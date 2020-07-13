import django_filters
from django_filters.views import FilterView
from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from odonto.models import Cuenta_Corriente, Paciente
from datetime import datetime,timezone
from django.db.models import F
from odonto.vistas.util import CustomErrorList
from django.contrib.messages.views import SuccessMessageMixin 
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from odonto.forms import (Cuenta_CorrienteForm, CustomFilterForm, )
from django.db import IntegrityError

class Cuenta_CorrienteListFilter(django_filters.FilterSet):
    filtro = django_filters.CharFilter(method='custom_filter')

    class Meta:
        form = CustomFilterForm
        model = Cuenta_Corriente
        fields = {'filtro'}

    def custom_filter(self, queryset, name, value):
         return queryset.filter(
             fecha__icontains=value
         )| queryset.filter(
             paciente__nombre_apellido__icontains=value
         ) | queryset.filter(
             importe__icontains=value
         ) | queryset.filter(
             ingreso_egreso__icontains=value
         )

class Cuenta_CorrienteList(LoginRequiredMixin,FilterView):
    model = Cuenta_Corriente
    paginate_by = 10
    context_object_name = 'object'
    filterset_class = Cuenta_CorrienteListFilter

    def model_name(self):
        return "Movimientos"
    
    def model_name_minuscula(self):
        return "movimientos"

    def get_context_data(self, **kwargs):
        context = super(Cuenta_CorrienteList, self).get_context_data(**kwargs)
        #Para agregar variables 
        return context

    def get_queryset(self):
        return Cuenta_Corriente.objects.filter(paciente__clinica=self.request.user.clinica).order_by('-id')

class Cuenta_CorrienteCrear(LoginRequiredMixin, SuccessMessageMixin, CreateView): 
    model = Cuenta_Corriente
    form_class = Cuenta_CorrienteForm
    success_message = 'Movimiento creado correctamente!'

    def get_success_url(self):        
        return reverse('cuenta_corriente_index')

    def get_context_data(self, **kwargs):
        context = super(Cuenta_CorrienteCrear, self).get_context_data(**kwargs)
        context['funcion'] = 'Agregar'
        return context
    
    def form_valid(self, form):
        form.instance.clinica = self.request.user.clinica
        try:
            return super(Cuenta_CorrienteCrear, self).form_valid(form)
        except IntegrityError as e:
            form.add_error(NON_FIELD_ERRORS,'Ya existe una norma de trabajo con el codigo ingresado.')
            return self.form_invalid(form)
    
    def get_form_kwargs(self):
        kwargs = super(Cuenta_CorrienteCrear, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

class Cuenta_CorrienteEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView): 
    model = Cuenta_Corriente
    form_class = Cuenta_CorrienteForm
    success_message = 'Movimiento modificado correctamente!'
 
    def get_success_url(self):        
        return reverse('cuenta_corriente_index')
    
    def get_context_data(self, **kwargs):
        context = super(Cuenta_CorrienteEditar, self).get_context_data(**kwargs)
        context['funcion']='Editar'
        return context

    def get_form_kwargs(self):
        kwargs = super(Cuenta_CorrienteEditar, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs
