import django_filters
from django_filters.views import FilterView
from odonto.forms import (FichaForm,CustomFilterForm,)
from odonto.models import Ficha
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin 
from django.urls import reverse
from odonto.vistas.util import CustomErrorList

class FichaListFilter(django_filters.FilterSet):
    filtro = django_filters.CharFilter(method='custom_filter')

    class Meta:
        form = CustomFilterForm
        model = Ficha
        fields = {'filtro'}

    def custom_filter(self, queryset, name, value):
         return queryset.filter(
             detalle__icontains=value
         ) | queryset.filter(
             paciente__nombre_apellido__icontains=value
         ) | queryset.filter(
             odontologo__nombre_apellido__icontains=value
         ) | queryset.filter(
             obra_social__nombre__icontains=value
         )

class FichaList(LoginRequiredMixin,FilterView):
    model = Ficha
    paginate_by = 10
    context_object_name = 'ficha'
    filterset_class = FichaListFilter

    def model_name(self):
        return "Fichas"
    
    def model_name_minuscula(self):
        return "fichas"

    def get_context_data(self, **kwargs):
        context = super(FichaList, self).get_context_data(**kwargs)
        #Para agregar variables 
        return context

    def get_queryset(self):
        return Ficha.objects.filter(clinica=self.request.user.clinica)

class FichaDetalle(LoginRequiredMixin,DetailView):
    model = Ficha
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class FichaCrear(LoginRequiredMixin, SuccessMessageMixin, CreateView): 
    model = Ficha
    form_class = FichaForm
    success_message = 'Ficha creada correctamente!'
 
    def get_success_url(self):        
        return reverse('ficha_index')
    
    def form_valid(self, form):
        form.instance.clinica = self.request.user.clinica
        self.object = form.save()
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super(FichaCrear, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

class FichaEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView): 
    model = Ficha
    form_class = FichaForm
    success_message = 'Ficha modificada correctamente!'
 
    def get_success_url(self):        
        return reverse('ficha_index')
    
    def get_form_kwargs(self):
        kwargs = super(FichaEditar, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

class FichaEliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView): 
    model = Ficha 
    form = Ficha
    fields = "__all__"
    def get_success_url(self): 
        success_message = 'Ficha eliminada correctamente.'
        messages.success (self.request, (success_message))       
        return reverse('ficha_index')