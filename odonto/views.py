from django.shortcuts import render
from django import forms
from django.db import models
from odonto.models import Obra_Social, Paciente, Norma_Trabajo, CustomUser, Odontologo, Ficha
from django.http import JsonResponse
from django.views import View
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse
from django.contrib.messages.views import SuccessMessageMixin 
from django.contrib.auth.mixins import LoginRequiredMixin
from odonto.forms import (Obra_SocialForm,
                            PacienteForm,
                            Norma_TrabajoForm,
                            ContactForm,
                            UserRegisterForm,
                            OdontologoForm,
                            FichaForm,
                            CustomFilterForm,)
from django.utils import timezone
from django.core.paginator import Paginator
from django_filters.views import FilterView
import django_filters
from django_filters.filterset import BaseFilterSet
from django.forms.utils import ErrorList
from odonto.vistas.util import CustomErrorList

#################### VARIOS ############################

class SignUpView(View):
    form_class = UserRegisterForm
    template_name = 'registration/sign_up.html'

    def get(self, request, *args, **kwargs):
            form = self.form_class()
            return render(request, self.template_name, {'form': form})
    def post(self, request, *args, **kwargs):
            form = self.form_class(request.POST)
            if form.is_valid():
                # <process form cleaned data>
                u = CustomUser.objects.create_user(
                        form.cleaned_data.get('username'),
                        '',# request.POST['email'],
                        form.cleaned_data.get('password1'),
                        is_active = True
                )
                # TODO Display message and redirect to login
                return HttpResponseRedirect('/login/?next=/')
            return render(request, self.template_name, {'form': form})

class ContactAjax(View):
    form_class = ContactForm
    template_name = "contacto.html"

    def get(self, *args, **kwargs):
        form = self.form_class()
        return render(self.request, self.template_name, {"contactForm": form})

    def post(self, *args, **kwargs):
        if self.request.method == "POST" and self.request.is_ajax():
            form = self.form_class(self.request.POST)
            form.save()
            return JsonResponse({"success":True}, status=200)
        return JsonResponse({"success":False}, status=400)

def index(request):
    return render(request, 'index.html',{})

@login_required
def obra_social_index(request):
    lista = Obra_Social.objects.order_by('id')[:6]
    context = {
        'lista': lista,
    }
    return render(request, 'obra_social/index.html',context)

def contacto(request):
    if request.method == "POST" and request.is_ajax():
        form = ContactForm(request.POST)
        #form.save()
        if form.is_valid():
            send_mail('Nueva consulta de ' + form.cleaned_data['nombre'],
                form.cleaned_data['mensaje'],
                'emilianorua@gmail.com',
                [form.cleaned_data['mail']],
                fail_silently=False,
                html_message=None)
            return JsonResponse({"success":True}, status=200)
        return JsonResponse({"success":False}, status=400)
    else:
	    #return JsonResponse({"success":False}, status=400)
        form = ContactForm()
        return render(request, "contacto.html", {"contactForm": form})
	