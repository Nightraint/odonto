import django_filters
from django_filters.views import FilterView
from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from odonto.models import Tutorial
from datetime import datetime,timezone
from django.db.models import F
from odonto.vistas.util import CustomErrorList
from django.contrib.messages.views import SuccessMessageMixin 
from django.urls import reverse
from django.views.generic.edit import CreateView
from odonto.forms import (TurnoForm,CustomFilterForm)
from django.db import IntegrityError
from django.views.generic import ListView, DetailView 

class TutorialDetalle(LoginRequiredMixin,DetailView):
    model = Tutorial
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class TutorialListFilter(django_filters.FilterSet):
    filtro = django_filters.CharFilter(method='custom_filter')

    class Meta:
        form = CustomFilterForm
        model = Tutorial
        fields = {'filtro'}

    def custom_filter(self, queryset, name, value):
        return queryset.filter(
            titulo__icontains=value
            ) | queryset.filter(
                descripcion__icontains=value
            ) | queryset.filter(
                categoria__icontains=value
            )

class TutorialList(LoginRequiredMixin,FilterView):
    model = Tutorial
    paginate_by = 10
    context_object_name = 'object'
    filterset_class = TutorialListFilter

    def model_name(self):
        return "Tutoriales"
    
    def model_name_minuscula(self):
        return "tutoriales"

    def get_context_data(self, **kwargs):
        context = super(TutorialList, self).get_context_data(**kwargs)
        return context
    
    def get_queryset(self):
        return Tutorial.objects.all().order_by('titulo')