import django_filters
from django_filters.views import FilterView
from odonto.forms import (PacienteForm,
                        CustomFilterForm,
                        TelefonoForm,
                        BaseTelefonoFormSet,
                        EmailForm,
                        BaseEmailFormSet,
                        PacientePlanForm,
                        BasePacientePlanFormSet)
from odonto.models import (Paciente,
    Norma_Trabajo,
    Ficha,
    Telefono,
    Email,
    Plan,
    PacientePlan)
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

@login_required
def editar(request, pk):
    TelefonoFormSet = formset_factory(TelefonoForm, formset=BaseTelefonoFormSet)
    EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet)
    PacientePlanFormSet = formset_factory(wraps(PacientePlanForm)(partial(PacientePlanForm, clinica_id = request.user.clinica.id)), formset=BasePacientePlanFormSet)
    instance = get_object_or_404(Paciente, pk=pk)

    if request.method == 'GET':
        paciente_form = PacienteForm(instance = instance,clinica_id = request.user.clinica.id)

        telefonos = Telefono.objects.filter(paciente = instance).order_by('id')
        telefonos_data = [{'descripcion': l.descripcion, 'telefono': l.telefono}
                            for l in telefonos]
        telefonos_formset = TelefonoFormSet(initial=telefonos_data)

        emails = Email.objects.filter(paciente = instance).order_by('id')
        emails_data = [{'descripcion': l.descripcion, 'email': l.email}
                            for l in emails]
        emails_formset = EmailFormSet(initial=emails_data)

        planes = PacientePlan.objects.filter(paciente = instance).order_by('id')
        planes_data = [{'nro_afiliado': l.nro_afiliado,
                        'obra_social' : l.plan.obra_social_id,
                        'plan' : l.plan_id}
                            for l in planes]
        paciente_planes_formset = PacientePlanFormSet(initial=planes_data,prefix='paciente_planes')
    else:
        paciente_form = PacienteForm(request.POST,instance=instance,clinica_id = request.user.clinica.id)
        telefonos_formset = TelefonoFormSet(request.POST)
        emails_formset = EmailFormSet(request.POST)
        paciente_planes_formset = PacientePlanFormSet(request.POST,prefix='paciente_planes')

        paciente_form.instance.clinica = request.user.clinica

        if paciente_form.is_valid() and telefonos_formset.is_valid() and emails_formset.is_valid():
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
            for plan_form in paciente_planes_formset:
                plan = plan_form.cleaned_data.get('plan')
                nro_afiliado = plan_form.cleaned_data.get('nro_afiliado')
                if plan:
                    nuevos_planes.append(PacientePlan(plan_id=plan,paciente = instance,nro_afiliado=nro_afiliado))
            
            try:
                with transaction.atomic():
                    Telefono.objects.filter(paciente=instance).delete()
                    Telefono.objects.bulk_create(nuevos_telefonos)

                    Email.objects.filter(paciente=instance).delete()
                    Email.objects.bulk_create(nuevos_emails)

                    messages.success(request, 'Paciente actualizado.')
                    return redirect(reverse('paciente_index'))
            except IntegrityError: #If the transaction failed
                messages.error(request, 'Ocurrio un error guardando el paciente')
                return redirect(reverse('paciente_index'))
    context = {
        'paciente_form': paciente_form,
        'telefono_formset': telefonos_formset,
        'email_formset' : emails_formset,
        'paciente_planes_formset' : paciente_planes_formset
    }
    return render(request, 'paciente/form.html', context)

@login_required
def crear(request):
    TelefonoFormSet = formset_factory(TelefonoForm, formset=BaseTelefonoFormSet)
    EmailFormSet = formset_factory(EmailForm, formset=BaseEmailFormSet)
    PacientePlanFormSet = formset_factory(wraps(PacientePlanForm)(partial(PacientePlanForm, clinica_id = request.user.clinica.id)), formset=BasePacientePlanFormSet)

    if request.method == 'GET':
        paciente_form = PacienteForm(clinica_id = request.user.clinica.id)
        telefonos_formset = TelefonoFormSet(prefix='telefonos')
        emails_formset = EmailFormSet(prefix='emails')
        paciente_planes_formset = PacientePlanFormSet(prefix='paciente_planes')
    else:
        telefonos_formset = TelefonoFormSet(request.POST,prefix='telefonos')
        emails_formset = EmailFormSet(request.POST,prefix='emails')
        paciente_planes_formset = PacientePlanFormSet(request.POST,prefix='paciente_planes')

        paciente_form = PacienteForm(request.POST,clinica_id = request.user.clinica.id)
        instance = paciente_form.instance

        paciente_form.instance.clinica = request.user.clinica

        if paciente_form.is_valid() and telefonos_formset.is_valid() and emails_formset.is_valid() and paciente_planes_formset.is_valid:
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
            for plan_form in paciente_planes_formset:
                plan = plan_form.cleaned_data.get('plan')
                nro_afiliado = plan_form.cleaned_data.get('nro_afiliado')
                if plan:
                    nuevos_planes.append(PacientePlan(plan_id=plan,paciente = instance,nro_afiliado=nro_afiliado))
            
            try:
                with transaction.atomic():
                    Telefono.objects.bulk_create(nuevos_telefonos)
                    Email.objects.bulk_create(nuevos_emails)
                    PacientePlan.objects.bulk_create(nuevos_planes)
                    messages.success(request, 'Paciente creado correctamente')
                    return redirect(reverse('paciente_index'))
            except IntegrityError:
                messages.error(request, 'Ocurrio un error guardando el paciente')
                return redirect(reverse('paciente_index'))

    context = {
        'paciente_form': paciente_form,
        'telefono_formset': telefonos_formset,
        'email_formset' : emails_formset,
        'paciente_planes_formset' : paciente_planes_formset,
    }
    return render(request, 'paciente/form.html', context)