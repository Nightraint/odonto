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
from odonto.forms import (ObraSocialForm,
                            PacienteForm,
                            Norma_TrabajoForm,
                            ContactForm,
                            ObraSocialFilterForm,
                            UserRegisterForm,
                            OdontologoForm,
                            FichaForm,
                            CustomFilterForm,)
from django.utils import timezone
from django.core.paginator import Paginator
from django_filters.views import FilterView
import django_filters
from django_filters.filterset import BaseFilterSet
################### FICHA ##################

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
        #return HttpResponseRedirect(self.get_success_url())
    
    def get_form_kwargs(self):
        kwargs = super(FichaCrear, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
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
        return kwargs

class FichaEliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView): 
    model = Ficha 
    form = Ficha
    fields = "__all__"
    def get_success_url(self): 
        success_message = 'Ficha eliminada correctamente.'
        messages.success (self.request, (success_message))       
        return reverse('ficha_index')

################### ODONTOLOGO ##################

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
        return kwargs

class OdontologoEliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView): 
    model = Odontologo 
    form = Odontologo
    fields = "__all__"
    def get_success_url(self): 
        success_message = 'Odontologo eliminado correctamente.'
        messages.success (self.request, (success_message))       
        return reverse('odontologo_index')

##################### OBRA SOCIAL #######################

class Obra_Social_Filter(django_filters.FilterSet):
    class Meta:
        form = ObraSocialFilterForm
        model = Obra_Social
        fields = {'nombre':['contains']}

class Obra_SocialList(LoginRequiredMixin,FilterView):
    model = Obra_Social
    paginate_by = 10
    context_object_name = 'obras_sociales'
    filterset_class = Obra_Social_Filter

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
    form_class = ObraSocialForm
    success_message = 'Obra social creada correctamente!'
 
    def get_success_url(self):        
        return reverse('obra_social_index')
    
    def form_valid(self, form):
        form.instance.clinica = self.request.user.clinica
        self.object = form.save()
        return super().form_valid(form)
        #return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(ObraSocialCrear, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        return kwargs

class ObraSocialEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView): 
    model = Obra_Social
    form_class = ObraSocialForm
    success_message = 'Obra social modificada correctamente!'
 
    def get_success_url(self):        
        return reverse('obra_social_index')
    
    def get_form_kwargs(self):
        kwargs = super(ObraSocialEditar, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        return kwargs

class ObraSocialEliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView): 
    model = Obra_Social 
    form = Obra_Social
    fields = "__all__"
    def get_success_url(self): 
        success_message = 'Obra social eliminada correctamente.'
        messages.success (self.request, (success_message))       
        return reverse('obra_social_index')

############### PACIENTES ######################

class PacienteListFilter(django_filters.FilterSet):
    filtro = django_filters.CharFilter(method='custom_filter')

    class Meta:
        form = CustomFilterForm
        model = Paciente
        fields = {'filtro'}

    def custom_filter(self, queryset, name, value):
         return queryset.filter(
             nombre_apellido__icontains=value
         ) | queryset.filter(
             odontologos__nombre_apellido__icontains=value
         ) | queryset.filter(
             obras_sociales__nombre__icontains=value
         ) | queryset.filter(
             dni__icontains=value
         ) | queryset.filter(
             domicilio__icontains=value
         ) | queryset.filter(
             telefono__icontains=value
         )

class PacienteList(LoginRequiredMixin,FilterView):
    model = Paciente
    paginate_by = 10
    context_object_name = 'paciente'
    filterset_class = PacienteListFilter
    ordering = ['nombre_apellido']

    def model_name(self):
        return "Pacientes"
    
    def model_name_minuscula(self):
        return "pacientes"

    def get_context_data(self, **kwargs):
        context = super(PacienteList, self).get_context_data(**kwargs)
        #Para agregar variables 
        return context
    
    def get_queryset(self):
        return Paciente.objects.filter(clinica=self.request.user.clinica)

class PacienteDetalle(LoginRequiredMixin,DetailView):
    model = Paciente
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class PacienteCrear(LoginRequiredMixin, SuccessMessageMixin, CreateView): 
    model = Paciente
    form_class = PacienteForm
    success_message = 'Paciente creado correctamente!'
 
    def get_success_url(self):        
        return reverse('paciente_index')
    
    def form_valid(self, form):
        form.instance.clinica = self.request.user.clinica
        self.object = form.save()
        return super().form_valid(form)
        #return HttpResponseRedirect(self.get_success_url())
    
    def get_form_kwargs(self):
        kwargs = super(PacienteCrear, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        return kwargs

class PacienteEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView): 
    model = Paciente
    form_class = PacienteForm
    success_message = 'Paciente modificado correctamente!'
 
    def get_success_url(self):        
        return reverse('paciente_index')

    def get_form_kwargs(self):
        kwargs = super(PacienteEditar, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        return kwargs

class PacienteEliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView): 
    model = Paciente 
    form = Paciente
    fields = "__all__"
    def get_success_url(self): 
        success_message = 'Paciente eliminado correctamente.'
        messages.success (self.request, (success_message))       
        return reverse('paciente_index')

############### NORMAS DE TRABAJO #####################

class NormaTrabajoListFilter(django_filters.FilterSet):
    filtro = django_filters.CharFilter(method='custom_filter')

    class Meta:
        form = CustomFilterForm
        model = Paciente
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
        return kwargs

class Norma_TrabajoEliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView): 
    model = Norma_Trabajo 
    form = Norma_Trabajo
    fields = "__all__"
    def get_success_url(self): 
        success_message = 'Norma de trabajo eliminada correctamente.'
        messages.success (self.request, (success_message))       
        return reverse('norma_trabajo_index')


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
	