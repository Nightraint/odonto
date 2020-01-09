from django.contrib.auth import update_session_auth_hash
from django import forms
from django.db import models
from .models import Obra_Social, Paciente, Norma_Trabajo, CustomUser, Odontologo, Ficha, Clinica, Telefono, Plan
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm,UserChangeForm,PasswordChangeForm
from django.forms import DateTimeField, EmailField
from .widgets import BootstrapDateTimePickerInput, BootstrapDatePickerInput
from django.forms import modelformset_factory
from django.forms.formsets import BaseFormSet

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
        widget=BootstrapDatePickerInput()
    )

    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(PacienteForm, self).__init__(*args, **kwargs)
        #self.fields['obras_sociales'].queryset = Obra_Social.objects.filter(clinica_id=clinica_id)
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
        self.fields['obra_social'].queryset = Obra_Social.objects.filter(clinica_id=clinica_id)
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
127244
##################### FICHAS #################### 

class FichaForm(forms.ModelForm):
    class Meta:
        model = Ficha
        exclude = ('clinica',)

    fecha = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'], 
        widget=BootstrapDateTimePickerInput()
    )

    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(FichaForm, self).__init__(*args, **kwargs)
        
        self.fields['odontologo'].queryset = Odontologo.objects.none()
        self.fields['obra_social'].queryset = Obra_Social.objects.none()
        self.fields['norma_trabajo'].queryset = Norma_Trabajo.objects.none()
        self.fields['paciente'].queryset = Paciente.objects.filter(clinica_id=clinica_id)

        self.fields['odontologo'].empty_label = 'Seleccionar'
        self.fields['obra_social'].empty_label = 'Seleccionar'
        self.fields['norma_trabajo'].empty_label = 'Seleccionar'
        self.fields['paciente'].empty_label = 'Seleccionar'

        if 'paciente' in self.data:
            try:
                paciente_id = int(self.data.get('paciente'))
                self.fields['odontologo'].queryset = Odontologo.objects.filter(paciente__id=paciente_id
                    ).order_by('nombre_apellido')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['odontologo'].queryset = self.instance.paciente.odontologos.order_by('nombre_apellido')

        if 'odontologo' in self.data:
            try:
                odontologo_id = int(self.data.get('odontologo'))
                self.fields['obra_social'].queryset = Obra_Social.objects.filter(plan__pacienteplan__paciente__id=paciente_id
                    ).filter(odontologo__id = odontologo_id
                    ).order_by('nombre')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['obra_social'].queryset = Obra_Social.objects.filter(plan__pacienteplan__paciente__id=self.instance.paciente.id
                ).filter(odontologo__id = self.instance.odontologo.id
                ).order_by('nombre')

        if 'obra_social' in self.data:
            try:
                obra_social_id = int(self.data.get('obra_social'))
                self.fields['norma_trabajo'].queryset = Norma_Trabajo.objects.filter(obra_social__id=obra_social_id
                    ).order_by('codigo')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            if self.instance.obra_social:
                self.fields['norma_trabajo'].queryset = Norma_Trabajo.objects.filter(obra_social=self.instance.obra_social
                ).order_by('codigo')
        
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

##################### PACIENTEPLAN #########################

class PacientePlanForm(forms.Form):
    obra_social = forms.ChoiceField(
        required = False,
        widget=forms.Select(attrs={
            'style' : 'width:200px;display:inline-block;margin-right:7px;',
            'onChange' : 'seleccionarObraSocial(this);',
        }))

    plan = forms.ChoiceField(
        required= False,
        widget=forms.Select(attrs={
            'style' : 'width:200px;display:inline-block;margin-right:7px;',
        }))

    nro_afiliado = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Nro. Afiliado',
            'style' : 'width:150px;display:inline-block;margin-right:7px;',
        }),
        required=False)

    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(PacientePlanForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['plan'].widget.attrs['class'] = 'form-control select_plan'
        self.fields['obra_social'].widget.attrs['class'] = 'form-control select_obra_social'
        self.fields['obra_social'].choices = [('','Seleccionar')] + [(o.id, str(o).upper()) for o in Obra_Social.objects.filter(clinica_id=clinica_id)]
        
        if self.initial:
            os = self.initial['obra_social']
            if os:
                self.fields['plan'].choices = [('','Seleccionar')] + [(p.id, str(p).upper()) for p in Plan.objects.filter(obra_social=os)]
                
class BasePacientePlanFormSet(BaseFormSet):
    def clean(self):
        pass

##################### IMAGENFICHA #########################

class ImagenFichaForm(forms.Form):
    imagen = forms.ImageField()

    def __init__(self, *args, **kwargs):
        #clinica_id = kwargs.pop('clinica_id')
        super(ImagenFichaForm, self).__init__(*args, **kwargs)
        self.fields['imagen'].widget.attrs['class'] = 'cargar_imagen'

class BaseImagenFichaFormSet(BaseFormSet):
    def clean(self):
        pass