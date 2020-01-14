import django_filters
from django_filters.views import FilterView
from odonto.forms import (Obra_SocialForm,CustomFilterForm,PlanForm,BasePlanFormSet)
from odonto.models import Obra_Social, Plan
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin 
from django.urls import reverse
from odonto.vistas.util import CustomErrorList
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import F
from django.forms.formsets import formset_factory
from django.shortcuts import redirect, render
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.core import serializers

class Obra_SocialListFilter(django_filters.FilterSet):
    filtro = django_filters.CharFilter(method='custom_filter')

    class Meta:
        form = CustomFilterForm
        model = Obra_Social
        fields = {'filtro'}

    def custom_filter(self, queryset, name, value):
         return queryset.filter(
             nombre__icontains=value
         )

class Obra_SocialList(LoginRequiredMixin,FilterView):
    model = Obra_Social
    paginate_by = 10
    context_object_name = 'obras_sociales'
    filterset_class = Obra_SocialListFilter

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
    form_class = Obra_SocialForm
    success_message = 'Obra social creada correctamente!'
 
    def get_success_url(self):        
        return reverse('obra_social_index')
    
    def form_valid(self, form):
        form.instance.clinica = self.request.user.clinica
        try:
            return super(ObraSocialCrear, self).form_valid(form)
        except IntegrityError as e:
            form.add_error(None,'Ya existe una obra social con el codigo ingresado.')
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(ObraSocialCrear, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

class ObraSocialEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView): 
    model = Obra_Social
    form_class = Obra_SocialForm
    success_message = 'Obra social modificada correctamente!'
 
    def get_success_url(self):        
        return reverse('obra_social_index')
    
    def get_form_kwargs(self):
        kwargs = super(ObraSocialEditar, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs

class ObraSocialEliminar(LoginRequiredMixin, SuccessMessageMixin, DeleteView): 
    model = Obra_Social 
    form = Obra_Social
    fields = "__all__"
    def get_success_url(self): 
        success_message = 'Obra social eliminada correctamente.'
        messages.success (self.request, (success_message))       
        return reverse('obra_social_index')

@login_required
def get_for_select(request):
    paciente = int(request.GET.get('paciente'))
    odontologo = int(request.GET.get('odontologo'))
    obras_sociales = Obra_Social.objects.filter(clinica = request.user.clinica
        ).filter(pacienteobrasocial__paciente__id = paciente
        ).filter(odontologo__id = odontologo
        ).values('id', 'nombre', 'usa_planes',
        ).annotate(descrip = F('nombre')) # or simply .values() to get all fields
    count = obras_sociales.count()
    os_list = list(obras_sociales)  # important: convert the QuerySet to a list object
    return JsonResponse(os_list, safe=False)

@login_required
def get(request, pk):
    obra_social = Obra_Social.objects.filter(clinica = request.user.clinica
        ).filter(id = pk)
    data = serializers.serialize('json', obra_social)
    #obra_social_object = json.loads(data) #Inverso
    return HttpResponse(data)

@login_required
def editar(request, pk):
    PlanFormSet = formset_factory(PlanForm, formset=BasePlanFormSet)
    instance = get_object_or_404(Obra_Social, pk=pk)
    if request.method == 'GET':
        obra_social_form = Obra_SocialForm(instance = instance,clinica_id = request.user.clinica.id)
        planes = Plan.objects.filter(obra_social = instance).order_by('id')
        planes_data = [{'nombre': p.nombre, 'iva' : p.iva, 'paga_coseguro': p.paga_coseguro}
                            for p in planes]
        planes_formset = PlanFormSet(initial=planes_data)
    else:
        obra_social_form = Obra_SocialForm(request.POST,instance=instance,clinica_id = request.user.clinica.id)
        planes_formset = PlanFormSet(request.POST)

        obra_social_form.instance.clinica = request.user.clinica

        if obra_social_form.is_valid() and planes_formset.is_valid():
            obra_social_form.save()
            nuevos_planes = []
            if instance.usa_planes:
                for plan_form in planes_formset:
                    nombre = plan_form.cleaned_data.get('nombre')
                    iva = plan_form.cleaned_data.get('iva')
                    if obra_social_form.cleaned_data.get('usa_coseguro'):
                        paga_coseguro = plan_form.cleaned_data.get('paga_coseguro')
                    else:
                        paga_coseguro = False
                    if nombre:
                        nuevos_planes.append(Plan(nombre=nombre,
                            iva= iva,
                            paga_coseguro = paga_coseguro,
                            obra_social = instance))
            try:
                with transaction.atomic():
                    Plan.objects.filter(obra_social=instance).delete()
                    Plan.objects.bulk_create(nuevos_planes)

                    messages.success(request, 'Obra social actualizada.')
                    return redirect(reverse('obra_social_index'))
            except IntegrityError:
                messages.error(request, 'Ocurrio un error guardando la obra social')
                return redirect(reverse('obra_social_index'))
    context = {
        'obra_social_form': obra_social_form,
        'planes_formset': planes_formset,
        'funcion' : 'Editar',
    }
    return render(request, 'obra_social/form.html', context)

@login_required
def crear(request):
    PlanFormSet = formset_factory(PlanForm, formset=BasePlanFormSet)

    if request.method == 'GET':
        obra_social_form = Obra_SocialForm(clinica_id = request.user.clinica.id)
        planes_formset = PlanFormSet(prefix='planes')
    else:
        planes_formset = PlanFormSet(request.POST,prefix='planes')

        obra_social_form = Obra_SocialForm(request.POST,clinica_id = request.user.clinica.id)
        instance = obra_social_form.instance

        obra_social_form.instance.clinica = request.user.clinica

        if obra_social_form.is_valid() and planes_formset.is_valid():
            obra_social_form.save()
            
            nuevos_planes = []
            if instance.usa_planes:
                for plan_form in planes_formset:
                    nombre = plan_form.cleaned_data.get('nombre')
                    iva = plan_form.cleaned_data.get('iva')
                    paga_coseguro = plan_form.cleaned_data.get('paga_coseguro')
                    if nombre:
                        nuevos_planes.append(Plan(nombre=nombre,
                            iva= iva,
                            paga_coseguro = paga_coseguro,
                            obra_social = instance))
           
            try:
                with transaction.atomic():
                    Plan.objects.bulk_create(nuevos_planes)
                    messages.success(request, 'Obra social creada correctamente')
                    return redirect(reverse('obra_social_index'))
            except IntegrityError:
                messages.error(request, 'Ocurrio un error guardando la obra social')
                return redirect(reverse('obra_social_index'))

    context = {
        'obra_social_form': obra_social_form,
        'planes_formset': planes_formset,
        'funcion' : 'Agregar',
    }
    return render(request, 'obra_social/form.html', context)