import django_filters
from django_filters.views import FilterView
from odonto.forms import (Norma_TrabajoForm,CustomFilterForm,)
from odonto.models import Norma_Trabajo
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
from django.db.models import Value
from django.db.models.functions import Concat
from django.db.models import CharField

class NormaTrabajoListFilter(django_filters.FilterSet):
    filtro = django_filters.CharFilter(method='custom_filter')

    class Meta:
        form = CustomFilterForm
        model = Norma_Trabajo
        fields = {'filtro'}

    def custom_filter(self, queryset, name, value):
         return queryset.filter(
             codigo__icontains=value
         )| queryset.filter(
             descripcion__icontains=value
         ) | queryset.filter(
             obra_social__nombre__icontains=value
         )

class Norma_TrabajoList(LoginRequiredMixin,FilterView):
    model = Norma_Trabajo
    paginate_by = 10
    context_object_name = 'normas_trabajo'
    filterset_class = NormaTrabajoListFilter

    def model_name(self):
        return "Normas de trabajo"
    
    def model_name_minuscula(self):
        return "normas de trabajo"

    def get_context_data(self, **kwargs):
        context = super(Norma_TrabajoList, self).get_context_data(**kwargs)
        #Para agregar variables 
        return context

    def get_queryset(self):
        return Norma_Trabajo.objects.filter(clinica=self.request.user.clinica)

class Norma_TrabajoDetalle(LoginRequiredMixin,DetailView):
    model = Norma_Trabajo
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class Norma_TrabajoCrear(LoginRequiredMixin, SuccessMessageMixin, CreateView): 
    model = Norma_Trabajo
    form_class = Norma_TrabajoForm
    success_message = 'Paciente creado correctamente!'
 
    def get_success_url(self):        
        return reverse('norma_trabajo_index')
    
    def form_valid(self, form):
        form.instance.clinica = self.request.user.clinica
        self.object = form.save()
        return super().form_valid(form)
        #return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(Norma_TrabajoCrear, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

class Norma_TrabajoEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView): 
    model = Norma_Trabajo
    form_class = Norma_TrabajoForm
    success_message = 'Norma de trabajo modificada correctamente!'
 
    def get_success_url(self):        
        return reverse('norma_trabajo_index')

    def get_form_kwargs(self):
        kwargs = super(Norma_TrabajoEditar, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

class Norma_TrabajoEliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView): 
    model = Norma_Trabajo 
    form = Norma_Trabajo
    fields = "__all__"
    def get_success_url(self): 
        success_message = 'Norma de trabajo eliminada correctamente.'
        messages.success (self.request, (success_message))       
        return reverse('norma_trabajo_index')

@login_required
def get_for_select(request):
    obra_social = int(request.GET.get('obra_social'))
    normas_trabajo = Norma_Trabajo.objects.filter(clinica = request.user.clinica
        ).filter(obra_social__id = obra_social
        ).values('id', 'codigo', 'descripcion'
        ).annotate(descrip = Concat('codigo', Value(' - '), 'descripcion',output_field=CharField())) # or simply .values() to get all fields
    nt_list = list(normas_trabajo)  # important: convert the QuerySet to a list object
    return JsonResponse(nt_list, safe=False)