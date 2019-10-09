import django_filters
from django_filters.views import FilterView
from odonto.forms import (OdontologoForm,CustomFilterForm,)
from odonto.models import Odontologo
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin 
from django.urls import reverse
from odonto.vistas.util import CustomErrorList
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

class OdontologoListFilter(django_filters.FilterSet):
    filtro = django_filters.CharFilter(method='custom_filter')

    class Meta:
        form = CustomFilterForm
        model = Odontologo
        fields = {'filtro'}

    def custom_filter(self, queryset, name, value):
         return queryset.filter(
             nombre_apellido__icontains=value
         ) | queryset.filter(
             matricula__icontains=value
         )

class OdontologoList(LoginRequiredMixin,FilterView):
    model = Odontologo
    paginate_by = 10
    context_object_name = 'odontologo'
    filterset_class = OdontologoListFilter

    def model_name(self):
        return "Odontólogos"
    
    def model_name_minuscula(self):
        return "odontólogos"

    def get_context_data(self, **kwargs):
        context = super(OdontologoList, self).get_context_data(**kwargs)
        #Para agregar variables 
        return context

    def get_queryset(self):
        return Odontologo.objects.filter(clinica=self.request.user.clinica)

class OdontologoDetalle(LoginRequiredMixin,DetailView):
    model = Odontologo
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class OdontologoCrear(LoginRequiredMixin, SuccessMessageMixin, CreateView): 
    model = Odontologo
    form_class = OdontologoForm
    success_message = 'Odontologo creado correctamente!'
 
    def get_success_url(self):        
        return reverse('odontologo_index')
    
    def form_valid(self, form):
        form.instance.clinica = self.request.user.clinica
        self.object = form.save()
        return super().form_valid(form)
        #return HttpResponseRedirect(self.get_success_url())
    
    def get_form_kwargs(self):
        kwargs = super(OdontologoCrear, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

class OdontologoEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView): 
    model = Odontologo
    form_class = OdontologoForm
    success_message = 'Odontologo modificado correctamente!'
 
    def get_success_url(self):        
        return reverse('odontologo_index')

    def get_form_kwargs(self):
        kwargs = super(OdontologoEditar, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

class OdontologoEliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView): 
    model = Odontologo 
    form = Odontologo
    fields = "__all__"
    def get_success_url(self): 
        success_message = 'Odontologo eliminado correctamente.'
        messages.success (self.request, (success_message))       
        return reverse('odontologo_index')

@login_required
def get_odontologos(request):
    paciente = int(request.GET.get('paciente'))
    odoo = Odontologo.objects.filter(paciente__id = paciente)
    odontologos = Odontologo.objects.filter(clinica = request.user.clinica).filter(paciente__id = paciente).values('id', 'nombre_apellido') # or simply .values() to get all fields
    odo_list = list(odontologos)  # important: convert the QuerySet to a list object
    return JsonResponse(odo_list, safe=False)
