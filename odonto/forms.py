from django.contrib.auth import update_session_auth_hash
from django import forms
from django.db import models
from .models import (Obra_Social,
                    Paciente,
                    Norma_Trabajo,
                    CustomUser,
                    Odontologo,
                    Ficha,
                    Clinica,
                    Telefono,
                    Plan,
                    Turno)
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm,UserChangeForm,PasswordChangeForm
from django.forms import DateTimeField, EmailField
from .widgets import BootstrapDateTimePickerInput, BootstrapDatePickerInput
from django.forms import modelformset_factory
from django.forms.formsets import BaseFormSet
from odonto.vistas.util import CustomErrorList
import math
import datetime

class MyModelChoiceField(forms.ModelChoiceField):
    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            value = self.queryset.get(**{key: value})
        except(ValueError, TypeError, self.queryset.model.DoesNotExist):
            pass
            #raise ValidationError(seld.error_messages['invalid_choice'], code='invalid_choice')
        return value

######################## LOGIN ##########################

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Usuario',
        }
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }
    ))

class PasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordForm, self).__init__(*args, **kwargs)

    old_password = forms.CharField(widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Contraseña anterior',
            }
        ),
        label='Contraseña anterior')
    new_password1 = forms.CharField(widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Contraseña nueva',
            }
        ),
        label='Contraseña nueva')
    new_password2 = forms.CharField(widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Repetir la contraseña nueva',
            }
        ),
        label='Repetir la contraseña nueva')

class UserRegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)

######################## OBRA SOCIAL ##########################

class Obra_SocialForm(forms.ModelForm):
    class Meta:
        model = Obra_Social
        exclude = ('clinica',)
    
    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(Obra_SocialForm, self).__init__(*args, **kwargs)
        
        for field in self.fields.values():
            if hasattr(field.widget,'input_type'):
                if field.widget.input_type != 'checkbox':
                    field.widget.attrs['class'] = 'form-control'
                else:
                    field.label_suffix = ''
                    field.widget.attrs['class'] = 'custom-control-input'
            else:
                field.widget.attrs['class'] = 'form-control'
    
######################## PACIENTE ##########################

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        exclude = ('clinica',)

    fecha_nacimiento = forms.DateTimeField(
        input_formats=['%d/%m/%Y'], 
        widget=BootstrapDatePickerInput(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(PacienteForm, self).__init__(*args, **kwargs)
        self.fields['odontologos'].queryset = Odontologo.objects.filter(clinica_id=clinica_id)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

################### NORMA TRABAJO ########################

class Norma_TrabajoForm(forms.ModelForm):
    class Meta:
        model = Norma_Trabajo
        exclude = ('clinica',)
    
    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(Norma_TrabajoForm, self).__init__(*args, **kwargs)

        if 'obra_social' in self.data and self.data.get('obra_social') != '':
            try:
                obra_social_seleccionada = self.data.get('obra_social')
                is_number = obra_social_seleccionada.isdigit()
                if not is_number: # Si la obra social no es numerica, es porque no es un id (entonces no existe, hay que agregarla)
                    os = Obra_Social()
                    os.nombre = obra_social_seleccionada
                    os.clinica_id = clinica_id
                    os.save()
                    self.data = self.data.copy()     # Copiamos la data porque no se puede modificar
                    self.data['obra_social'] = os.id # Seleccionamos el id de la nueva obra social
            except (ValueError, TypeError):
                pass

        self.fields['obra_social'].queryset = Obra_Social.objects.filter(clinica_id=clinica_id)
        self.fields['obra_social'].empty_label = 'Seleccionar obra social'
        self.fields['coseguro'].widget.attrs['style'] = 'width:150px;display:inline-block;'
        self.fields['bonos'].widget.attrs['style'] = 'width:150px;display:inline-block;'
        self.fields['dias'].widget.attrs['style'] = 'width:70px;display:inline-block;'
        self.fields['meses'].widget.attrs['style'] = 'width:70px;display:inline-block;'
        self.fields['años'].widget.attrs['style'] = 'width:70px;display:inline-block;'
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

##################### ODONTOLOGOS #################### 

class OdontologoForm(forms.ModelForm):
    class Meta:
        model = Odontologo
        exclude = ('clinica',)
    
    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(OdontologoForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

##################### TURNOS #################### 

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        exclude = ('clinica','todo_el_dia',)

    fecha_inicio = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=BootstrapDateTimePickerInput(attrs={
                    'placeholder': 'Fecha',
                },
                optional_class = '',)
    )

    fecha_fin = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=BootstrapDateTimePickerInput(attrs={
                    'placeholder': 'Fecha',
                },
                optional_class='')
    )

    observaciones = forms.CharField(
                widget=forms.Textarea(attrs={
                    'style' : 'height:100px;',
                }),
                required=False)
    
    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        fecha = kwargs.pop('fecha')
        kwargs.update({'error_class': CustomErrorList})
        super(TurnoForm, self).__init__(*args, **kwargs)

        if fecha:
            if len(fecha) == 10:
                date = datetime.datetime.strptime(fecha,'%Y-%m-%d')
                final_date = date
            else:
                date = datetime.datetime.strptime(fecha,'%Y-%m-%dT%H:%M:%S')
                minutes = datetime.timedelta(minutes = 30)
                final_date = date + minutes

            if date and not self.fields['fecha_inicio'].initial:
                self.fields['fecha_inicio'].initial = date.strftime('%d/%m/%Y %H:%M')

            if final_date and not self.fields['fecha_fin'].initial:
                self.fields['fecha_fin'].initial = final_date.strftime('%d/%m/%Y %H:%M')

        if 'paciente' in self.data and self.data.get('paciente') != '':
            try:
                paciente_seleccionado = self.data.get('paciente')
                is_number = paciente_seleccionado.isdigit()
                if not is_number: # Si el paciente no es numerico, es porque no es un id (entonces no existe, hay que agregarlo)
                    p = Paciente()
                    p.nombre_apellido = paciente_seleccionado
                    p.clinica_id = clinica_id
                    p.save()
                    self.data = self.data.copy() # Copiamos la data porque no se puede modificar
                    self.data['paciente'] = p.id # Seleccionamos el id del nuevo paciente
            except (ValueError, TypeError):
                pass

        if 'odontologo' in self.data and self.data.get('odontologo') != '':
            try:
                odontologo_seleccionado = self.data.get('odontologo')
                is_number = odontologo_seleccionado.isdigit()
                if not is_number: # Si el odontologo no es numerico, es porque no es un id (entonces no existe, hay que agregarlo)
                    o = Odontologo()
                    o.nombre_apellido = odontologo_seleccionado
                    o.clinica_id = clinica_id
                    o.save()
                    self.data = self.data.copy() # Copiamos la data porque no se puede modificar
                    self.data['odontologo'] = o.id # Seleccionamos el id del nuevo odontologo
            except (ValueError, TypeError):
                pass

        self.fields['odontologo'].queryset = Odontologo.objects.filter(clinica_id = clinica_id)
        self.fields['paciente'].queryset = Paciente.objects.filter(clinica_id=clinica_id)

        self.fields['odontologo'].required = True
        self.fields['paciente'].required = True

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

##################### FICHAS #################### 

class FichaForm(forms.ModelForm):
    class Meta:
        model = Ficha
        exclude = ('clinica',)

    fecha = forms.DateTimeField(
        input_formats=['%d/%m/%Y'], 
        widget=BootstrapDatePickerInput()
    )

    observaciones = forms.CharField(
                widget=forms.Textarea(attrs={
                    'style' : 'height:100px;',
                }),
                required=False)

    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(FichaForm, self).__init__(*args, **kwargs)

        if 'paciente' in self.data and self.data.get('paciente') != '':
            try:
                paciente_seleccionado = self.data.get('paciente')
                is_number = paciente_seleccionado.isdigit()
                if not is_number: # Si el paciente no es numerico, es porque no es un id (entonces no existe, hay que agregarlo)
                    p = Paciente()
                    p.nombre_apellido = paciente_seleccionado
                    p.clinica_id = clinica_id
                    p.save()
                    self.data = self.data.copy() # Copiamos la data porque no se puede modificar
                    self.data['paciente'] = p.id # Seleccionamos el id del nuevo paciente
            except (ValueError, TypeError):
                pass

        if 'odontologo' in self.data and self.data.get('odontologo') != '':
            try:
                odontologo_seleccionado = self.data.get('odontologo')
                is_number = odontologo_seleccionado.isdigit()
                if not is_number:
                    o = Odontologo()
                    o.nombre_apellido = odontologo_seleccionado
                    o.clinica_id = clinica_id
                    o.save()
                    self.data = self.data.copy()
                    self.data['odontologo'] = o.id
            except (ValueError, TypeError):
                pass

        if 'obra_social' in self.data and self.data.get('obra_social') != '':
            try:
                os_seleccionada = self.data.get('obra_social')
                is_number = os_seleccionada.isdigit()
                if not is_number:
                    os = Obra_Social()
                    os.nombre = os_seleccionada
                    os.clinica_id = clinica_id
                    os.save()
                    self.data = self.data.copy()
                    self.data['obra_social'] = os.id
            except (ValueError, TypeError):
                pass

        if 'plan' in self.data and self.data.get('plan') != '' and 'obra_social' in self.data:
            try:
                p_seleccionado = self.data.get('plan')
                is_number = p_seleccionado.isdigit()
                if not is_number:
                    plan = Plan()
                    plan.obra_social_id = self.data['obra_social']
                    plan.nombre = p_seleccionado
                    plan.clinica_id = clinica_id
                    plan.save()
                    self.data = self.data.copy()
                    self.data['plan'] = plan.id
            except (ValueError, TypeError):
                pass
        
        self.fields['odontologo'].queryset = Odontologo.objects.filter(clinica_id = clinica_id)
        self.fields['obra_social'].queryset = Obra_Social.objects.filter(clinica_id = clinica_id)
        #self.fields['norma_trabajo'].queryset = Norma_Trabajo.objects.none()
        self.fields['plan'].queryset = Plan.objects.none()
        self.fields['paciente'].queryset = Paciente.objects.filter(clinica_id=clinica_id)

        self.fields['odontologo'].empty_label = 'Seleccionar odontólogo'
        self.fields['obra_social'].empty_label = 'Seleccionar obra social'
        #self.fields['norma_trabajo'].empty_label = 'Seleccionar norma de trabajo'
        self.fields['plan'].empty_label = 'Seleccionar plan'
        self.fields['paciente'].empty_label = 'Seleccionar paciente'

        # if 'paciente' in self.data:
        #     try:
        #         paciente_id = int(self.data.get('paciente'))
        #         self.fields['odontologo'].queryset = Odontologo.objects.filter(paciente__id=paciente_id
        #             ).order_by('nombre_apellido')
        #     except (ValueError, TypeError):
        #         pass
        # elif self.instance.pk:
        #     self.fields['odontologo'].queryset = self.instance.paciente.odontologos.order_by('nombre_apellido')

        # if 'odontologo' in self.data:
        #     try:
        #         odontologo_id = int(self.data.get('odontologo'))
        #         self.fields['obra_social'].queryset = Obra_Social.objects.filter(pacienteobrasocial__paciente__id=paciente_id
        #             ).filter(odontologo__id = odontologo_id
        #             ).order_by('nombre')
        #     except (ValueError, TypeError):
        #         pass
        # elif self.instance.pk:
        #     self.fields['obra_social'].queryset = Obra_Social.objects.filter(pacienteobrasocial__paciente__id=self.instance.paciente.id
        #         ).filter(odontologo__id = self.instance.odontologo.id
        #         ).order_by('nombre')

        if 'obra_social' in self.data:
            try:
                obra_social_id = int(self.data.get('obra_social'))
                self.fields['plan'].queryset = Plan.objects.filter(obra_social__id=obra_social_id
                    ).order_by('nombre')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            if self.instance.obra_social:
                self.fields['plan'].queryset = Plan.objects.filter(obra_social=self.instance.obra_social
                ).order_by('nombre')
        
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

################### CUSTOM FILTER FORM ###############

class CustomFilterForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(CustomFilterForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
             field.widget.attrs['class'] = 'form-control'
             field.widget.attrs['placeholder'] = 'Ingrese su búsqueda...'

##################### VARIOS #########################

class ContactForm(forms.Form):
    nombre = forms.CharField(max_length=100,label='Nombre',label_suffix=':')
    mensaje = forms.CharField(label='Consulta',max_length=3000,label_suffix=':')
    mail = forms.EmailField(label='Correo electrónico',label_suffix=':')
    class meta:
        fields = ('nombre','mensaje','mail')
        #exclude = ()
        # widgets = {
		# 	'mensaje': forms.Textarea(attrs={'rows':4, 'cols':15}),
		# }
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

#################### CUSTOM USER ######################

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = '__all__'

##################### TELEFONO #########################

class TelefonoForm(forms.Form):
    telefono = forms.CharField(
                    max_length=100,
                    widget=forms.TextInput(attrs={
                        'placeholder': 'Número',
                        'style' : 'width:220px;display:inline-block;margin-right:7px;',
                    }),
                    required=False)
    descripcion = forms.CharField(
                    widget=forms.TextInput(attrs={
                        'placeholder': 'Contacto',
                        'style' : 'width:220px;display:inline-block;margin-right:7px;',
                    }),
                    required=False)

    def __init__(self, *args, **kwargs):
        super(TelefonoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class BaseTelefonoFormSet(BaseFormSet):
    def clean(self):
        pass

##################### EMAIL #########################

class EmailForm(forms.Form):
    email = forms.EmailField(
                    max_length=100,
                    widget=forms.TextInput(attrs={
                        'placeholder': 'Email',
                        'style' : 'width:220px;display:inline-block;margin-right:7px;',
                    }),
                    required=False)
    descripcion = forms.CharField(
                    widget=forms.TextInput(attrs={
                        'placeholder': 'Contacto',
                        'style' : 'width:220px;display:inline-block;margin-right:7px;',
                    }),
                    required=False)

    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class BaseEmailFormSet(BaseFormSet):
    def clean(self):
        pass

##################### PLAN #########################

class PlanForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre del plan',
            'style' : 'width:180px;display:inline-block;margin-right:7px;',
        }))

    VACIO = ''
    GRAVADO = 'GR'
    NO_GRAVADO = 'NG'
    EXENTO = 'EX'
    IVA = [
        (VACIO, 'Seleccione IVA'),
        (GRAVADO, 'Gravado'),
        (NO_GRAVADO, 'No gravado'),
        (EXENTO, 'Exento')
    ]

    iva = forms.ChoiceField(
        choices=IVA,
        required= False,
        widget=forms.Select(attrs={
            'style' : 'width:160px;display:inline-block;margin-right:7px;',
        }))
        
    paga_coseguro = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(PlanForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            #for field in self.fields.values():
            if hasattr(visible.field.widget,'input_type'):
                if visible.field.widget.input_type != 'checkbox':
                    visible.field.widget.attrs['class'] = 'form-control'
                else:
                    visible.field.label_suffix = ''
                    visible.field.widget.attrs['class'] = 'custom-control-input'
            else:
                visible.field.widget.attrs['class'] = 'form-control'

class BasePlanFormSet(BaseFormSet):
    def clean(self):
        pass

##################### PACIENTE OBRA SOCIAL #########################

class PacienteObraSocialForm(forms.Form):
    obra_social = forms.ModelChoiceField(
        required = False,
        empty_label= 'Seleccionar obra social',
        queryset=Obra_Social.objects.none(),
        widget=forms.Select(attrs={
            'style' : 'width:220px;margin-right:7px;display:inline-block;',
            'onChange' : 'seleccionarObraSocial(this);',
        }))

    plan = MyModelChoiceField(
        required= False,
        empty_label= 'Seleccionar plan',
        queryset=Plan.objects.none(),
        widget=forms.Select(attrs={
            'style' : 'width:150px;margin-right:7px;',
        }))

    nro_afiliado = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Nro. Afiliado',
            'style' : 'width:150px;display:inline-block;margin-right:7px;',
        }),
        required=False)

    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(PacienteObraSocialForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['plan'].widget.attrs['class'] = 'form-control select_plan'
        self.fields['obra_social'].widget.attrs['class'] = 'form-control select_obra_social'
        self.fields['obra_social'].queryset = Obra_Social.objects.filter(clinica_id = clinica_id)

        if self.initial:
            os = self.initial['obra_social']
            obra_social = Obra_Social.objects.get(pk=os)
            if obra_social:
                if obra_social.usa_planes:
                    self.fields['plan'].queryset = Plan.objects.filter(obra_social = os)
                    self.fields['plan'].widget.attrs['style'] += 'display:inline-block;'
                else:
                    self.fields['plan'].widget.attrs['style'] += 'display:none;'
            else:
                 self.fields['plan'].widget.attrs['style'] += 'display:none;'
        else:
             self.fields['plan'].widget.attrs['style'] += 'display:none;'

class BasePacienteObraSocialFormSet(BaseFormSet):
    def clean(self):
        pass

##################### IMAGENFICHA #########################

class ImagenFichaForm(forms.Form):
    imagen = forms.FileField(required=False)
    id_img = forms.IntegerField(required=False)
    filename = forms.CharField(required=False)
    descripcion = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        #clinica_id = kwargs.pop('clinica_id')
        super(ImagenFichaForm, self).__init__(*args, **kwargs)
        self.fields['imagen'].widget.attrs['class'] = 'cargar_imagen'
        self.fields['descripcion'].widget.attrs['class'] = 'form-control'
        self.fields['descripcion'].widget.attrs['placeholder'] = 'Descripción'
        self.fields['descripcion'].widget.attrs['style'] = 'margin-top:5px;'

class BaseImagenFichaFormSet(BaseFormSet):
    def clean(self):
        pass

##################### CONSULTA #########################

class ConsultaForm(forms.Form):
    fecha = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'], 
        widget=BootstrapDateTimePickerInput(attrs={
                    'placeholder': 'Fecha',
                },
                optional_class = 'fecha-consulta',)
    )
    
    norma_trabajo = MyModelChoiceField(
        required = False,
        empty_label= 'Seleccionar norma trabajo',
        queryset=Norma_Trabajo.objects.none(),
        widget=forms.Select(attrs={
            'onChange' : 'chequear(this);',
        }))

    nro_diente = forms.IntegerField(
                widget=forms.NumberInput(attrs={
                    'placeholder': 'Nro diente',
                }),
                required=False)

    detalle = forms.CharField(
                widget=forms.TextInput(attrs={
                    'placeholder': 'Detalle',
                    'style' : 'display:inline-block;margin-top:7px;',
                }),
                required=False)

    id_consulta = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(ConsultaForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control '
            if visible.name == 'norma_trabajo':
                visible.field.widget.attrs['class'] += 'select-norma-trabajo'

        if self.initial:
            nt = self.initial['norma_trabajo']
            if nt:
                norma_trabajo = Norma_Trabajo.objects.get(pk=nt)
                if norma_trabajo:
                    self.fields['norma_trabajo'].queryset = Norma_Trabajo.objects.filter(obra_social = norma_trabajo.obra_social)
            else:
                self.fields['norma_trabajo'].widget.attrs['style'] = 'display:none;'
        else:
            self.fields['norma_trabajo'].widget.attrs['style'] = 'display:none;'


class BaseConsultaFormSet(BaseFormSet):
    def clean(self):
        pass