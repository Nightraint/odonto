import django_filters
from django_filters.views import FilterView
from odonto.forms import (FichaForm,
    CustomFilterForm,
    ImagenFichaForm,
    BaseImagenFichaFormSet,
    ConsultaForm,
    BaseConsultaFormSet,
    CtaCteForm,
    BaseCtaCteFormSet
    )
from odonto.models import Ficha, Imagen, Consulta, Cuenta_Corriente
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin 
from django.urls import reverse
from odonto.vistas.util import CustomErrorList
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render
from functools import partial, wraps

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
 
    def get_context_data(self, **kwargs):
        context = super(FichaCrear, self).get_context_data(**kwargs)
        ImagenFichaFormSet = formset_factory(ImagenFichaForm, formset=BaseImagenFichaFormSet)
        context['imagenes_formset'] = ImagenFichaFormSet(prefix='imagenes')
        return context
    
    def post(self, request, *args, **kwargs):
        ImagenFichaFormSet = formset_factory(ImagenFichaForm, formset=BaseImagenFichaFormSet)
        imagenes_formset = ImagenFichaFormSet(request.POST,request.FILES,prefix='imagenes')

        ficha_form = FichaForm(request.POST,clinica_id = request.user.clinica.id)
        
        if imagenes_formset.is_valid() and ficha_form.is_valid():
            return self.form_valid(ficha_form,imagenes_formset)

    def form_valid(self, form, imagenes_formset):
        form.instance.clinica = self.request.user.clinica
        ImagenFichaFormSet = formset_factory(ImagenFichaForm, formset=BaseImagenFichaFormSet)
        self.object = form.save()

        nuevas_imagenes = []
        for imagen_form in imagenes_formset:
            ficha = self.object
            imagen = imagen_form.cleaned_data.get('imagen')
            if imagen:
                nuevas_imagenes.append(Imagen(ficha=ficha,
                    imagen= imagen))
        try:
            with transaction.atomic():
                Imagen.objects.bulk_create(nuevas_imagenes)
                messages.success(self.request, 'Ficha creada correctamente')
                return redirect(reverse('ficha_index'))
        except IntegrityError:
            messages.error(self.request, 'Ocurrio un error guardando la ficha')
            return redirect(reverse('ficha_index'))
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super(FichaCrear, self).get_form_kwargs()
        kwargs.update({'clinica_id': self.request.user.clinica.id})
        kwargs.update({'error_class': CustomErrorList})
        return kwargs
    
    def get_success_url(self):        
        return reverse('ficha_index')

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

@login_required
def crear(request):
    ImagenFichaFormSet = formset_factory(ImagenFichaForm, formset=BaseImagenFichaFormSet)
    ConsultaFormSet = formset_factory(wraps(ConsultaForm)(partial(ConsultaForm, clinica_id = request.user.clinica.id)), formset=BaseConsultaFormSet)
    CtaCteFormFormSet = formset_factory(CtaCteForm, formset=BaseCtaCteFormSet)

    if request.method == 'GET':
        ficha_form = FichaForm(clinica_id = request.user.clinica.id)
        imagenes_formset = ImagenFichaFormSet(prefix='imagenes')
        consultas_formset = ConsultaFormSet(prefix='consultas')
        ctacte_formset = CtaCteFormFormSet(prefix='cta_cte')
    else:
        imagenes_formset = ImagenFichaFormSet(request.POST, request.FILES, prefix='imagenes')
        consultas_formset = ConsultaFormSet(request.POST, prefix='consultas')
        ctacte_formset = CtaCteFormFormSet(request.POST, prefix='cta_cte')
        ficha_form = FichaForm(request.POST,clinica_id = request.user.clinica.id)
        instance = ficha_form.instance

        ficha_form.instance.clinica = request.user.clinica

        if (ficha_form.is_valid() and
            imagenes_formset.is_valid() and
            consultas_formset.is_valid() and
            ctacte_formset.is_valid()):

            ficha_form.save()
            
            nuevas_consultas = []
            for form in consultas_formset:
                fecha = form.cleaned_data.get('fecha')
                obra_social = form.cleaned_data.get('obra_social')
                norma_trabajo = form.cleaned_data.get('norma_trabajo')
                detalle = form.cleaned_data.get('detalle')
                nro_diente = form.cleaned_data.get('nro_diente')
                if detalle or norma_trabajo:
                    nuevas_consultas.append(Consulta(ficha=instance,
                        norma_trabajo_id = norma_trabajo,
                        detalle = detalle,
                        fecha = fecha,
                        nro_diente= nro_diente,))

            nuevas_imagenes = []
            for imagen_form in imagenes_formset:
                imagen = imagen_form.cleaned_data.get('imagen')
                descripcion = imagen_form.cleaned_data.get('descripcion')
                if imagen:
                    nuevas_imagenes.append(Imagen(ficha=instance,
                        imagen= imagen,
                        descripcion = descripcion))

            nuevas_cta_cte = []
            for form in ctacte_formset:
                fecha = form.cleaned_data.get('fecha')
                concepto = form.cleaned_data.get('concepto')
                ingreso_egreso = form.cleaned_data.get('ingreso_egreso')
                importe = form.cleaned_data.get('importe')
                if importe:
                    nuevas_cta_cte.append(Cuenta_Corriente(paciente=instance.paciente,
                        fecha= fecha,
                        concepto = concepto,
                        ingreso_egreso = ingreso_egreso,
                        importe = importe))

            try:
                with transaction.atomic():
                    Consulta.objects.bulk_create(nuevas_consultas)
                    Imagen.objects.bulk_create(nuevas_imagenes)
                    Cuenta_Corriente.objects.bulk_create(nuevas_cta_cte)
                    messages.success(request, 'Ficha creada correctamente')
                    return redirect(reverse('ficha_index'))
            except IntegrityError:
                messages.error(request, 'Ocurrio un error guardando la ficha')
                return redirect(reverse('ficha_index'))

    context = {
        'ficha_form': ficha_form,
        'imagenes_formset': imagenes_formset,
        'consultas_formset': consultas_formset,
        'ctacte_formset': ctacte_formset,
        'funcion' : 'Agregar',
    }
    return render(request, 'ficha/form_v2.html', context)

@login_required
def editar(request,pk):
    ImagenFichaFormSet = formset_factory(ImagenFichaForm, formset=BaseImagenFichaFormSet)
    ConsultaFormSet = formset_factory(wraps(ConsultaForm)(partial(ConsultaForm, clinica_id = request.user.clinica.id)), formset=BaseConsultaFormSet)
    CtaCteFormFormSet = formset_factory(CtaCteForm, formset=BaseCtaCteFormSet)

    instance = get_object_or_404(Ficha, pk=pk)

    if request.method == 'GET':
        ficha_form = FichaForm(instance=instance,clinica_id = request.user.clinica.id)
        
        imagenes = Imagen.objects.filter(ficha = instance).order_by('id')
        imagenes_data = [{'imagen': i.imagen,
                          'id_img': i.id,
                          'filename': i.filename(),
                          'descripcion': i.descripcion}
                            for i in imagenes]
        imagenes_formset = ImagenFichaFormSet(prefix='imagenes',initial=imagenes_data)

        consultas = Consulta.objects.filter(ficha = instance).order_by('id')
        consultas_data = [{'fecha': c.fecha,
                           'detalle': c.detalle,
                           'norma_trabajo' : c.norma_trabajo_id,
                           'id_consulta': c.id,
                           'nro_diente': c.nro_diente,
                           'descripcion_norma_trabajo': c.norma_trabajo}
                            for c in consultas]
        consultas_formset = ConsultaFormSet(prefix='consultas', initial=consultas_data)

        ctactes = Cuenta_Corriente.objects.filter(paciente = instance.paciente).order_by('id')
        ctacte_data = [{'fecha': c.fecha,
                           'concepto': c.concepto,
                           'ingreso_egreso' : c.ingreso_egreso,
                           'id_cta_cte': c.id,
                           'importe': c.importe}
                            for c in ctactes]
        ctacte_formset = CtaCteFormFormSet(prefix='cta_cte', initial=ctacte_data)
    else:
        imagenes_formset = ImagenFichaFormSet(request.POST,request.FILES or None,prefix='imagenes')
        consultas_formset = ConsultaFormSet(request.POST,prefix='consultas')
        ctacte_formset = CtaCteFormFormSet(request.POST,prefix='cta_cte')
        
        ficha_form = FichaForm(request.POST, request.FILES,instance=instance,clinica_id = request.user.clinica.id)
        instance = ficha_form.instance

        ficha_form.instance.clinica = request.user.clinica

        if (ficha_form.is_valid() and
            imagenes_formset.is_valid() and
            consultas_formset.is_valid()and
            ctacte_formset.is_valid()):

            ficha_form.save()

            nuevas_consultas = []
            id_consultas = []
            for form in consultas_formset:
                fecha = form.cleaned_data.get('fecha')
                norma_trabajo = form.cleaned_data.get('norma_trabajo')
                detalle = form.cleaned_data.get('detalle')
                id_consulta = form.cleaned_data.get('id_consulta')
                nro_diente = form.cleaned_data.get('nro_diente')
                if (detalle or norma_trabajo) and not id_consulta:
                    nuevas_consultas.append(Consulta(ficha=instance,
                        norma_trabajo_id = norma_trabajo,
                        detalle = detalle,
                        fecha = fecha,
                        nro_diente = nro_diente))
                elif id_consulta:
                        id_consultas.append(id_consulta)
                        cons = Consulta.objects.get(pk=id_consulta)
                        cons.detalle = detalle
                        cons.save()
            
            nuevas_imagenes = []
            id_existentes = []
            for imagen_form in imagenes_formset:
                imagen = imagen_form.cleaned_data.get('imagen')
                id_img = imagen_form.cleaned_data.get('id_img')
                descripcion = imagen_form.cleaned_data.get('descripcion')
                if imagen and not id_img:
                    nuevas_imagenes.append(Imagen(ficha=instance,
                        imagen= imagen,
                        descripcion = descripcion))
                elif id_img:
                        id_existentes.append(id_img)
                        img = Imagen.objects.get(pk=id_img)
                        img.descripcion = descripcion
                        img.save()

            nuevas_cta_cte = []
            id_ctactes = []
            for form in ctacte_formset:
                fecha = form.cleaned_data.get('fecha')
                concepto = form.cleaned_data.get('concepto')
                ingreso_egreso = form.cleaned_data.get('ingreso_egreso')
                importe = form.cleaned_data.get('importe')
                id_cta_cte = form.cleaned_data.get('id_cta_cte')
                if importe and not id_cta_cte:
                    nuevas_cta_cte.append(Cuenta_Corriente(paciente=instance.paciente,
                        fecha= fecha,
                        concepto = concepto,
                        ingreso_egreso = ingreso_egreso,
                        importe = importe))
                elif id_cta_cte:
                    id_ctactes.append(id_cta_cte)

            try:
                with transaction.atomic():
                    Imagen.objects.filter(ficha=instance).exclude(id__in=id_existentes).delete()
                    Imagen.objects.bulk_create(nuevas_imagenes)
                    #Consulta.objects.filter(ficha=instance).exclude(id__in=id_consultas).delete()
                    Consulta.objects.bulk_create(nuevas_consultas)
                    Cuenta_Corriente.objects.filter(paciente=instance.paciente).exclude(id__in=id_ctactes).delete()
                    Cuenta_Corriente.objects.bulk_create(nuevas_cta_cte)
                    messages.success(request, 'Ficha modificada correctamente')
                    return redirect(reverse('ficha_index'))
            except IntegrityError:
                messages.error(request, 'Ocurrio un error guardando la ficha')
                return redirect(reverse('ficha_index'))

    context = {
        'ficha_form': ficha_form,
        'imagenes_formset': imagenes_formset,
        'consultas_formset': consultas_formset,
        'ctacte_formset': ctacte_formset,
        'funcion' : 'Editar',
    }
    return render(request, 'ficha/form_v2.html', context)

@login_required
def odontograma(request):
    
    context = {
    }

    return render(request, 'ficha/odontograma.html', context)