import django_filters
from django_filters.views import FilterView
from odonto.forms import (FichaForm,CustomFilterForm,ImagenFichaForm,BaseImagenFichaFormSet)
from odonto.models import Ficha, Imagen
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

    if request.method == 'GET':
        ficha_form = FichaForm(clinica_id = request.user.clinica.id)
        imagenes_formset = ImagenFichaFormSet(prefix='imagenes')
    else:
        imagenes_formset = ImagenFichaFormSet(request.POST,request.FILES,prefix='imagenes')

        ficha_form = FichaForm(request.POST,clinica_id = request.user.clinica.id)
        instance = ficha_form.instance

        ficha_form.instance.clinica = request.user.clinica

        if ficha_form.is_valid() and imagenes_formset.is_valid():
            ficha_form.save()
            
            nuevas_imagenes = []
        for imagen_form in imagenes_formset:
            ficha = ficha_form.instance
            imagen = imagen_form.cleaned_data.get('imagen')
            if imagen:
                nuevas_imagenes.append(Imagen(ficha=ficha,
                    imagen= imagen))
        try:
            with transaction.atomic():
                Imagen.objects.bulk_create(nuevas_imagenes)
                messages.success(request, 'Ficha creada correctamente')
                return redirect(reverse('ficha_index'))
        except IntegrityError:
            messages.error(request, 'Ocurrio un error guardando la ficha')
            return redirect(reverse('ficha_index'))

    context = {
        'ficha_form': ficha_form,
        'imagenes_formset': imagenes_formset,
    }
    return render(request, 'ficha/form.html', context)

@login_required
def editar(request,pk):
    ImagenFichaFormSet = formset_factory(ImagenFichaForm, formset=BaseImagenFichaFormSet)
    instance = get_object_or_404(Ficha, pk=pk)
    if request.method == 'GET':
        ficha_form = FichaForm(instance=instance,clinica_id = request.user.clinica.id)
        
        imagenes = Imagen.objects.filter(ficha = instance).order_by('id')
        imagenes_data = [{'imagen': i.imagen, }
                            for i in imagenes]
        imagenes_formset = ImagenFichaFormSet(prefix='imagenes',initial=imagenes_data)
    else:
        imagenes_formset = ImagenFichaFormSet(request.POST,request.FILES,prefix='imagenes')

        ficha_form = FichaForm(request.POST,clinica_id = request.user.clinica.id)
        instance = ficha_form.instance

        ficha_form.instance.clinica = request.user.clinica

        if ficha_form.is_valid() and imagenes_formset.is_valid():
            ficha_form.save()
            
            nuevas_imagenes = []
        for imagen_form in imagenes_formset:
            ficha = ficha_form.instance
            imagen = imagen_form.cleaned_data.get('imagen')
            if imagen:
                nuevas_imagenes.append(Imagen(ficha=ficha,
                    imagen= imagen))
        try:
            with transaction.atomic():
                Imagen.objects.bulk_create(nuevas_imagenes)
                messages.success(request, 'Ficha creada correctamente')
                return redirect(reverse('ficha_index'))
        except IntegrityError:
            messages.error(request, 'Ocurrio un error guardando la ficha')
            return redirect(reverse('ficha_index'))

    context = {
        'ficha_form': ficha_form,
        'imagenes_formset': imagenes_formset,
    }
    return render(request, 'ficha/form.html', context)