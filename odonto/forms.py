from django.contrib.auth import update_session_auth_hash
from django import forms
from .models import Obra_Social, Paciente, Norma_Trabajo, CustomUser, Odontologo, Ficha, Clinica
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm,UserChangeForm,PasswordChangeForm
from django.forms import DateTimeField
from .widgets import BootstrapDateTimePickerInput

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
            field.widget.attrs['class'] = 'form-control'
    
######################## PACIENTE ##########################

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        exclude = ('clinica',)

    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(PacienteForm, self).__init__(*args, **kwargs)
        self.fields['obras_sociales'].queryset = Obra_Social.objects.filter(clinica_id=clinica_id)
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
        #self.fields['obra_social'].queryset = Obra_Social.objects.filter(clinica_id=clinica_id)
        #self.fields['odontologo'].queryset = Odontologo.objects.filter(clinica_id=clinica_id)
        #self.fields['norma_trabajo'].queryset = Norma_Trabajo.objects.filter(clinica_id=clinica_id)
        self.fields['odontologo'].queryset = Odontologo.objects.none()
        self.fields['obra_social'].queryset = Obra_Social.objects.none()
        self.fields['norma_trabajo'].queryset = Norma_Trabajo.objects.none()

        if 'paciente' in self.data:
            try:
                paciente_id = int(self.data.get('paciente'))
                self.fields['odontologo'].queryset = Odontologo.objects.filter(paciente__id=paciente_id).order_by('nombre_apellido')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['odontologo'].queryset = self.instance.paciente.odontologos.order_by('nombre_apellido')

        self.fields['paciente'].queryset = Paciente.objects.filter(clinica_id=clinica_id)
        
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