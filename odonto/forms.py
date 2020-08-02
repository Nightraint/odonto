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
                    Turno,
                    Cuenta_Corriente)
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm,UserChangeForm,PasswordChangeForm
from django.forms import DateTimeField, EmailField
from .widgets import (BootstrapDateTimePickerInput
    ,BootstrapDatePickerInput
    ,XDSoftDateTimePickerInput)
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
        self.fields['obra_social'].empty_label = 'Haga click para seleccionar'
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

        self.fields['obras_sociales'].queryset = Obra_Social.objects.filter(clinica_id=clinica_id)
        self.fields['obras_sociales'].empty_label = 'Seleccionar obra social'

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

##################### VER TURNOS ################

class VerTurnosForm(forms.Form):
    odontologo = forms.ModelChoiceField(label='Odontologo',
        label_suffix=':',
        required=True,
        queryset=Odontologo.objects.none(),
        widget=forms.Select(attrs={
            'style' : 'max-width:880px;',
        }))

    class meta:
        fields = ('odontologo',)
        #exclude = ()
        # widgets = {
		# 	'mensaje': forms.Textarea(attrs={'rows':4, 'cols':15}),
		# }

    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(VerTurnosForm, self).__init__(*args, **kwargs)
        self.fields['odontologo'].queryset = Odontologo.objects.filter(clinica_id = clinica_id)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['odontologo'].empty_label = 'Seleccionar odontólogo'
    

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

    d11 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d12 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d13 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d14 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d15 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d16 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d17 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d18 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d21 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d22 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d23 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d24 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d25 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d26 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d27 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d28 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d31 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d32 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d33 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d34 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d35 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d36 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d37 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d38 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d41 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d42 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d43 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d44 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d45 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d46 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d47 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d48 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d51 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d52 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d53 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d54 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d55 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d61 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d62 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d63 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d64 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d65 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d71 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d72 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d73 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d74 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d75 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d81 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d82 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d83 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d84 = forms.CharField(widget=forms.HiddenInput(),required=False)
    d85 = forms.CharField(widget=forms.HiddenInput(),required=False)

    top11 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top12 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top13 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top14 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top15 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top16 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top17 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top18 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top21 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top22 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top23 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top24 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top25 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top26 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top27 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top28 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top31 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top32 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top33 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top34 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top35 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top36 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top37 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top38 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top41 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top42 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top43 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top44 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top45 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top46 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top47 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top48 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top51 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top52 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top53 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top54 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top55 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top61 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top62 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top63 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top64 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top65 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top71 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top72 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top73 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top74 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top75 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top81 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top82 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top83 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top84 = forms.CharField(widget=forms.HiddenInput(),required=False)
    top85 = forms.CharField(widget=forms.HiddenInput(),required=False)

    bot11 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot12 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot13 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot14 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot15 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot16 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot17 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot18 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot21 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot22 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot23 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot24 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot25 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot26 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot27 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot28 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot31 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot32 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot33 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot34 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot35 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot36 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot37 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot38 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot41 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot42 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot43 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot44 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot45 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot46 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot47 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot48 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot51 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot52 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot53 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot54 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot55 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot61 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot62 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot63 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot64 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot65 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot71 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot72 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot73 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot74 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot75 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot81 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot82 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot83 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot84 = forms.CharField(widget=forms.HiddenInput(),required=False)
    bot85 = forms.CharField(widget=forms.HiddenInput(),required=False)

    left11 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left12 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left13 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left14 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left15 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left16 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left17 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left18 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left21 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left22 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left23 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left24 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left25 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left26 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left27 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left28 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left31 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left32 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left33 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left34 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left35 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left36 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left37 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left38 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left41 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left42 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left43 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left44 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left45 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left46 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left47 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left48 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left51 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left52 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left53 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left54 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left55 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left61 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left62 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left63 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left64 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left65 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left71 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left72 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left73 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left74 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left75 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left81 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left82 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left83 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left84 = forms.CharField(widget=forms.HiddenInput(),required=False)
    left85 = forms.CharField(widget=forms.HiddenInput(),required=False)

    right11 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right12 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right13 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right14 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right15 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right16 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right17 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right18 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right21 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right22 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right23 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right24 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right25 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right26 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right27 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right28 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right31 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right32 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right33 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right34 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right35 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right36 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right37 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right38 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right41 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right42 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right43 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right44 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right45 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right46 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right47 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right48 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right51 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right52 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right53 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right54 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right55 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right61 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right62 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right63 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right64 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right65 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right71 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right72 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right73 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right74 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right75 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right81 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right82 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right83 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right84 = forms.CharField(widget=forms.HiddenInput(),required=False)
    right85 = forms.CharField(widget=forms.HiddenInput(),required=False)

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
        self.fields['plan'].queryset = Plan.objects.none()
        self.fields['paciente'].queryset = Paciente.objects.filter(clinica_id=clinica_id)

        self.fields['odontologo'].empty_label = 'Seleccionar odontólogo'
        self.fields['obra_social'].empty_label = 'Seleccionar obra social'
        self.fields['plan'].empty_label = 'Seleccionar plan'
        self.fields['paciente'].empty_label = 'Seleccionar paciente'

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
            if not field.widget.is_hidden:
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
                    }),
                    required=False)
    descripcion = forms.CharField(
                    widget=forms.TextInput(attrs={
                        'placeholder': 'Contacto',
                    }),
                    required=False)

    def __init__(self, *args, **kwargs):
        super(TelefonoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if visible.initial:
                visible.field.widget.attrs['readonly'] = True

class BaseTelefonoFormSet(BaseFormSet):
    def clean(self):
        pass

##################### EMAIL #########################

class EmailForm(forms.Form):
    email = forms.EmailField(
                    max_length=100,
                    widget=forms.TextInput(attrs={
                        'placeholder': 'Email',
                    }),
                    required=False)
    descripcion = forms.CharField(
                    widget=forms.TextInput(attrs={
                        'placeholder': 'Contacto',
                    }),
                    required=False)

    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if visible.initial:
                visible.field.widget.attrs['readonly'] = True

class BaseEmailFormSet(BaseFormSet):
    def clean(self):
        pass

##################### PLAN #########################

class PlanForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre del plan',
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
            'onChange' : 'seleccionarObraSocial($(this));',
        }))

    plan = MyModelChoiceField(
        required= False,
        empty_label= 'Seleccionar plan',
        queryset=Plan.objects.none(),
        widget=forms.Select(attrs={
        }))

    nro_afiliado = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Nro. Afiliado',
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
                    self.fields['plan'].widget.attrs['style'] = 'display:inline-block;'
                else:
                    self.fields['plan'].widget.attrs['style'] = 'display:none;'
            else:
                 self.fields['plan'].widget.attrs['style'] = 'display:none;'
        else:
             self.fields['plan'].widget.attrs['style'] = 'display:none;'

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
        self.fields['descripcion'].widget.attrs['class'] = 'form-control input-descripcion'
        self.fields['descripcion'].widget.attrs['placeholder'] = 'Descripción'
        self.fields['descripcion'].widget.attrs['style'] = 'margin-top:5px;'

class BaseImagenFichaFormSet(BaseFormSet):
    def clean(self):
        pass

##################### CONSULTA #########################

class ConsultaForm(forms.Form):
    fecha = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'], 
        required=False,
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
                    'style' : 'display:inline-block;',
                }),
                required=False)

    id_consulta = forms.IntegerField(required=False)

    descripcion_norma_trabajo = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(ConsultaForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control '
            if visible.name == 'norma_trabajo':
                visible.field.widget.attrs['class'] += 'select-norma-trabajo'
            if visible.name == 'detalle':
                visible.field.widget.attrs['class'] += 'input-detalle'

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

##################### CUENTA CORRIENTE #########################

class Cuenta_CorrienteForm(forms.ModelForm):
    class Meta:
        model = Cuenta_Corriente
        exclude = ()

    fecha = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'], 
        required=False,
        widget=BootstrapDateTimePickerInput(attrs={
                    'placeholder': 'Fecha',
                },
                optional_class = 'fecha-consulta',)
    )

    concepto = forms.CharField(
            widget=forms.Textarea(attrs={
                'style' : 'height:100px;',
            }),
            required=False)

  
    def __init__(self, *args, **kwargs):
        clinica_id = kwargs.pop('clinica_id')
        super(Cuenta_CorrienteForm, self).__init__(*args, **kwargs)

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

        self.fields['paciente'].queryset = Paciente.objects.filter(clinica_id=clinica_id)
        self.fields['paciente'].required = True

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'