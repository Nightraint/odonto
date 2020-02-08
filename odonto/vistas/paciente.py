import django_filters
from django_filters.views import FilterView
from odonto.forms import (PacienteForm,
                        CustomFilterForm,
                        TelefonoForm,
                        BaseTelefonoFormSet,
                        EmailForm,
                        BaseEmailFormSet,
                        PacienteObraSocialForm,
                        BasePacienteObraSocialFormSet)
from odonto.models import (Paciente,
    Norma_Trabajo,
    Ficha,
    Telefono,
    Email,
    Plan,
    PacienteObraSocial,
    Consulta)
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
from django.forms.formsets import formset_factory
from django.shortcuts import redirect, render
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from functools import partial, wraps
from dateutil.relativedelta import relativedelta

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

    consulta = Consulta.objects.filter(ficha__paciente_id = id_paciente).filter(norma_trabajo_id = id_norma_trabajo).order_by('fecha').first()

    response_data = {}
    
    if consulta:
        fecha_ultima = consulta.fecha.replace(tzinfo=None)

        result = 'Se puede aplicar'
        aplicada_hace = ''

        if dias:
            cantidad = dias
            descripcion = 'días'
            diferencia = (fecha_ficha-fecha_ultima).days
            if (diferencia < dias):
                result = 'No se puede aplicar'
                if diferencia == 0:
                    aplicada_hace = 'menos de un dia'
                else:
                    aplicada_hace = '%s dias' % diferencia
        
        if meses:
            cantidad = meses
            descripcion = 'meses'
            
            diferencia = diff_month(fecha_ficha,fecha_ultima)
            if (diferencia < meses):
                result = 'No se puede aplicar'
                if diferencia == 0:
                    aplicada_hace = 'menos de un mes'
                else:
                    aplicada_hace = '%s meses' % diferencia
        
        if años:
            cantidad = años
            descripcion = 'años'
            diferencia = relativedelta(fecha_ficha, fecha_ultima).years
            if (diferencia < años):
                result = 'No se puede aplicar'
                if diferencia == 0:
                    aplicada_hace = 'menos de un año'
                else:
                    aplicada_hace = '% años' % diferencia

        response_data['result'] = result

        if aplicada_hace:
            response_data['message'] = 'Se puede aplicar cada <b>%s %s</b> y ya se ha aplicado hace <b>%s</b> para este paciente.' % (cantidad,descripcion,aplicada_hace)
            response_data['enlace'] = '/consulta/detalle/%s' % consulta.id
            
    response_data['norma_trabajo'] = '%s - %s' % (norma_trabajo.obra_social, norma_trabajo)
    return JsonResponse(response_data, safe=False)

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

@login_required
def editar(request, pk):
    TelefonoFormSet = formset_factory(TelefonoForm, formset=BaseTelefonoFormSet)
    EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet)
    PacienteObraSocialFormSet = formset_factory(wraps(PacienteObraSocialForm)(partial(PacienteObraSocialForm, clinica_id = request.user.clinica.id)), formset=BasePacienteObraSocialFormSet)
    
    instance = get_object_or_404(Paciente, pk=pk)

    if request.method == 'GET':
        paciente_form = PacienteForm(instance = instance,clinica_id = request.user.clinica.id)

        telefonos = Telefono.objects.filter(paciente = instance).order_by('id')
        telefonos_data = [{'descripcion': l.descripcion, 'telefono': l.telefono}
                            for l in telefonos]
        telefonos_formset = TelefonoFormSet(initial=telefonos_data,prefix='telefonos')

        emails = Email.objects.filter(paciente = instance).order_by('id')
        emails_data = [{'descripcion': l.descripcion, 'email': l.email}
                            for l in emails]
        emails_formset = EmailFormSet(initial=emails_data,prefix='emails')

        planes = PacienteObraSocial.objects.filter(paciente = instance).order_by('id')
        planes_data = [{'nro_afiliado': l.nro_afiliado,
                        'obra_social' : l.obra_social_id,
                        'plan' : l.plan_id}
                            for l in planes]
        obras_sociales_formset = PacienteObraSocialFormSet(initial=planes_data,prefix='obras_sociales')
    else:
        paciente_form = PacienteForm(request.POST,instance=instance,clinica_id = request.user.clinica.id)
        telefonos_formset = TelefonoFormSet(request.POST, prefix='telefonos')
        emails_formset = EmailFormSet(request.POST,prefix='emails')
        obras_sociales_formset = PacienteObraSocialFormSet(request.POST,prefix='obras_sociales')

        paciente_form.instance.clinica = request.user.clinica

        if paciente_form.is_valid() and telefonos_formset.is_valid() and emails_formset.is_valid() and obras_sociales_formset.is_valid():
            paciente_form.save()

            nuevos_telefonos = []
            for telefono_form in telefonos_formset:
                descripcion = telefono_form.cleaned_data.get('descripcion')
                telefono = telefono_form.cleaned_data.get('telefono')
                if telefono:
                    nuevos_telefonos.append(Telefono(descripcion=descripcion, telefono=telefono, paciente = instance))
            
            nuevos_emails = []
            for email_form in emails_formset:
                descripcion = email_form.cleaned_data.get('descripcion')
                email = email_form.cleaned_data.get('email')
                if email:
                    nuevos_emails.append(Email(descripcion=descripcion, email=email, paciente = instance))

            nuevos_planes = []
            for plan_form in obras_sociales_formset:
                plan = plan_form.cleaned_data.get('plan')
                nro_afiliado = plan_form.cleaned_data.get('nro_afiliado')
                obra_social = plan_form.cleaned_data.get('obra_social')
                if obra_social:
                    nuevos_planes.append(PacienteObraSocial(plan_id=plan,
                                                    paciente = instance,
                                                    nro_afiliado=nro_afiliado,
                                                    obra_social = obra_social))            
            try:
                with transaction.atomic():
                    Telefono.objects.filter(paciente=instance).delete()
                    Telefono.objects.bulk_create(nuevos_telefonos)

                    Email.objects.filter(paciente=instance).delete()
                    Email.objects.bulk_create(nuevos_emails)

                    PacienteObraSocial.objects.filter(paciente=instance).delete()
                    PacienteObraSocial.objects.bulk_create(nuevos_planes)

                    messages.success(request, 'Paciente actualizado.')
                    return redirect(reverse('paciente_index'))
            except IntegrityError: #If the transaction failed
                messages.error(request, 'Ocurrio un error guardando el paciente')
                return redirect(reverse('paciente_index'))
    context = {
        'paciente_form': paciente_form,
        'telefono_formset': telefonos_formset,
        'email_formset' : emails_formset,
        'obras_sociales_formset' : obras_sociales_formset,
        'funcion' : 'Editar'
    }
    return render(request, 'paciente/form.html', context)

@login_required
def crear(request):
    TelefonoFormSet = formset_factory(TelefonoForm, formset=BaseTelefonoFormSet)
    EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet)
    PacienteObraSocialFormSet = formset_factory(wraps(PacienteObraSocialForm)(partial(PacienteObraSocialForm, clinica_id = request.user.clinica.id)), formset=BasePacienteObraSocialFormSet)

    if request.method == 'GET':
        paciente_form = PacienteForm(clinica_id = request.user.clinica.id)
        telefonos_formset = TelefonoFormSet(prefix='telefonos')
        emails_formset = EmailFormSet(prefix='emails')
        obras_sociales_formset = PacienteObraSocialFormSet(prefix='obras_sociales')
    else:
        telefonos_formset = TelefonoFormSet(request.POST,prefix='telefonos')
        emails_formset = EmailFormSet(request.POST,prefix='emails')
        obras_sociales_formset = PacienteObraSocialFormSet(request.POST,prefix='obras_sociales')

        # TODO: Agregar la opcion seleccionada en las opciones del select

        paciente_form = PacienteForm(request.POST,clinica_id = request.user.clinica.id)
        instance = paciente_form.instance

        paciente_form.instance.clinica = request.user.clinica

        if paciente_form.is_valid() and telefonos_formset.is_valid() and emails_formset.is_valid() and obras_sociales_formset.is_valid():
            paciente_form.save()

            nuevos_telefonos = []
            for telefono_form in telefonos_formset:
                descripcion = telefono_form.cleaned_data.get('descripcion')
                telefono = telefono_form.cleaned_data.get('telefono')
                if telefono:
                    nuevos_telefonos.append(Telefono(descripcion=descripcion, telefono=telefono, paciente = instance))
            
            nuevos_emails = []
            for email_form in emails_formset:
                descripcion = email_form.cleaned_data.get('descripcion')
                email = email_form.cleaned_data.get('email')
                if email:
                    nuevos_emails.append(Email(descripcion=descripcion, email=email, paciente = instance))
            
            nuevos_planes = []
            for plan_form in obras_sociales_formset:
                plan = plan_form.cleaned_data.get('plan')
                nro_afiliado = plan_form.cleaned_data.get('nro_afiliado')
                obra_social = plan_form.cleaned_data.get('obra_social')
                if obra_social:
                    nuevos_planes.append(PacienteObraSocial(plan_id=plan,
                                                    paciente = instance,
                                                    nro_afiliado=nro_afiliado,
                                                    obra_social = obra_social))
            
            try:
                with transaction.atomic():
                    Telefono.objects.bulk_create(nuevos_telefonos)
                    Email.objects.bulk_create(nuevos_emails)
                    PacienteObraSocial.objects.bulk_create(nuevos_planes)
                    messages.success(request, 'Paciente creado correctamente')
                    return redirect(reverse('paciente_index'))
            except IntegrityError:
                messages.error(request, 'Ocurrio un error guardando el paciente')
                return redirect(reverse('paciente_index'))

    context = {
        'paciente_form': paciente_form,
        'telefono_formset': telefonos_formset,
        'email_formset' : emails_formset,
        'obras_sociales_formset' : obras_sociales_formset,
        'funcion' : 'Agregar'
    }
    return render(request, 'paciente/form.html', context)