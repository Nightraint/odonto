import django_filters
from django_filters.views import FilterView
from odonto.forms import (PacienteForm,CustomFilterForm,)
from odonto.models import Paciente, Norma_Trabajo, Ficha
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
from datetime import datetime
from django.db.models import Max

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
        kwargs.update({'error_class': CustomErrorList})
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
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

class PacienteEliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView): 
    model = Paciente 
    form = Paciente
    fields = "__all__"
    def get_success_url(self): 
        success_message = 'Paciente eliminado correctamente.'
        messages.success (self.request, (success_message))       
        return reverse('paciente_index')

@login_required
def chequear_norma(request):
    id_paciente = int(request.GET.get('paciente'))
    id_norma_trabajo = int(request.GET.get('norma_trabajo'))
    fecha = request.GET.get('fecha')

    fecha_ficha = datetime.strptime(fecha , '%d/%m/%Y %H:%M')
    
    paciente = Paciente.objects.get(pk = id_paciente)

    norma_trabajo = Norma_Trabajo.objects.get(pk = id_norma_trabajo)
    dias = norma_trabajo.dias
    meses = norma_trabajo.meses
    años = norma_trabajo.años

    ficha = Ficha.objects.filter(paciente_id = id_paciente).filter(norma_trabajo_id = id_norma_trabajo).order_by('fecha').first()

    response_data = {}
    
    if ficha:
        fecha_ultima = ficha.fecha.replace(tzinfo=None)
        diferencia = (fecha_ficha-fecha_ultima).days
        if (diferencia < norma_trabajo.dias):
            response_data['result'] = 'Advertencia'
            response_data['message'] = 'La norma de trabajo se puede aplicar cada <b>%s días</b> y ya se ha aplicado hace <b>%s días</b> para este paciente.' % (norma_trabajo.dias,diferencia)
            response_data['enlace'] = '/ficha/detalle/%s' % ficha.id
        else:
            response_data['result'] = 'OK'
            response_data['message'] = 'Se puede aplicar la norma de trabajo.'
    else:
        response_data['result'] = 'OK'
        response_data['message'] = 'Se puede aplicar la norma de trabajo.'

    return JsonResponse(response_data, safe=False)

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)