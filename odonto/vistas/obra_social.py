import django_filters
from django_filters.views import FilterView
from odonto.forms import (Obra_SocialForm,CustomFilterForm,)
from odonto.models import Obra_Social
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
from django.db.models import F
from django.db import IntegrityError

class Obra_SocialListFilter(django_filters.FilterSet):
    filtro = django_filters.CharFilter(method='custom_filter')

    class Meta:
        form = CustomFilterForm
        model = Obra_Social
        fields = {'filtro'}

    def custom_filter(self, queryset, name, value):
         return queryset.filter(
             nombre__icontains=value
         )

class Obra_SocialList(LoginRequiredMixin,FilterView):
    model = Obra_Social
    paginate_by = 10
    context_object_name = 'obras_sociales'
    filterset_class = Obra_SocialListFilter

    def model_name(self):
        return "Obras sociales"
    
    def model_name_minuscula(self):
        return "obras sociales"

    def get_context_data(self, **kwargs):
        context = super(Obra_SocialList, self).get_context_data(**kwargs)
        #Para agregar variables 
        return context
    
    def get_queryset(self):
        return Obra_Social.objects.filter(clinica=self.request.user.clinica)

class Obras_Sociales_Detalle(LoginRequiredMixin,DetailView):
    model = Obra_Social
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class ObraSocialCrear(LoginRequiredMixin, SuccessMessageMixin, CreateView): 
    model = Obra_Social
    form_class = Obra_SocialForm
    success_message = 'Obra social creada correctamente!'
 
    def get_success_url(self):        
        return reverse('obra_social_index')
    
    def form_valid(self, form):
        form.instance.clinica = self.request.user.clinica
        try:
            return super(ObraSocialCrear, self).form_valid(form)
        except IntegrityError as e:
            form.add_error(None,'Ya existe una obra social con el codigo ingresado.')
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(ObraSocialCrear, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

class ObraSocialEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView): 
    model = Obra_Social
    form_class = Obra_SocialForm
    success_message = 'Obra social modificada correctamente!'
 
    def get_success_url(self):        
        return reverse('obra_social_index')
    
    def get_form_kwargs(self):
        kwargs = super(ObraSocialEditar, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

class ObraSocialEliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView): 
    model = Obra_Social 
    form = Obra_Social
    fields = "__all__"
    def get_success_url(self): 
        success_message = 'Obra social eliminada correctamente.'
        messages.success (self.request, (success_message))       
        return reverse('obra_social_index')

@login_required
def get_for_select(request):
    paciente = int(request.GET.get('paciente'))
    odontologo = int(request.GET.get('odontologo'))
    obras_sociales = Obra_Social.objects.filter(clinica = request.user.clinica
        ).filter(paciente__id = paciente
        ).filter(odontologo__id = odontologo
        ).values('id', 'nombre'
        ).annotate(descrip = F('nombre')) # or simply .values() to get all fields
    os_list = list(obras_sociales)  # important: convert the QuerySet to a list object
    return JsonResponse(os_list, safe=False)