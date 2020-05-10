from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from odonto.models import Turno
from datetime import datetime,timezone
from django.db.models import F
from odonto.vistas.util import CustomErrorList
from django.contrib.messages.views import SuccessMessageMixin 
from django.urls import reverse
from django.views.generic.edit import CreateView
from odonto.forms import (TurnoForm)

class TurnoCrear(LoginRequiredMixin, SuccessMessageMixin, CreateView): 
    model = Turno
    form_class = TurnoForm
    success_message = 'Turno creado correctamente!'
 
    #def get_success_url(self):        
        #return reverse('turno_index')
    #    return JsonResponse({'success':'true'})

    def get_context_data(self, **kwargs):
        context = super(TurnoCrear, self).get_context_data(**kwargs)
        context['funcion'] = 'Agregar'
        return context
    
    def form_valid(self, form):
        form.instance.clinica = self.request.user.clinica
        self.object = form.save()
        return HttpResponse({'success':'true'}, content_type="application/json")
    
    def get_form_kwargs(self):
        kwargs = super(TurnoCrear, self).get_form_kwargs()
        fecha = ''
        if self.request.GET:
            fecha = self.request.GET['fecha']
        kwargs.update({'fecha': fecha})
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

@login_required
def crear(request):
    if request.method == 'GET':
        form = TurnoForm(clinica_id = request.user.clinica.id, fecha = request.GET['fecha'])
    else:
        form = TurnoForm(request.POST,clinica_id = request.user.clinica.id, fecha ='')
        instance = form.instance

        form.instance.clinica = request.user.clinica

        if form.is_valid():
            form.save()
            return JsonResponse({'success':'true'})
    context = {
        'form': form,
        'funcion' : 'Agregar',
    }
    return render(request, 'turno/form.html', context)

@login_required
def index(request):
    today = datetime.now(timezone.utc)
    prueba = today.strftime('%Y-%m-%dT%H:%M:%S %p')
    formatedDay = today.strftime('%Y-%m-%d')

    context = {
        'today': formatedDay,
        'prueba':prueba
    }
    return render(request, 'turno/index.html',context)

@login_required
def get_all(request):
    turnos = Turno.objects.filter(clinica = request.user.clinica
        ).values('id',
        ).annotate(title = F('paciente__nombre_apellido')
        ).annotate(start = F('fecha_inicio')
        ).annotate(end = F('fecha_fin')
        ).annotate(wsp = F('paciente__whatsapp')) # or simply .values() to get all fields

    p_list = list(turnos)  # important: convert the QuerySet to a list object

    return JsonResponse(p_list, safe=False)