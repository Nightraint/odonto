from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Obra_Social, Paciente, Norma_Trabajo, Odontologo, CustomUser, Clinica, Ficha, Turno, Tutorial, Cuenta_Corriente

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username','email',]
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ['clinica']}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ['clinica']}),
    )

admin.site.register(Cuenta_Corriente)
admin.site.register(Tutorial)
admin.site.register(Turno)
admin.site.register(Ficha)
admin.site.register(Obra_Social)
admin.site.register(Paciente)
admin.site.register(Norma_Trabajo)
admin.site.register(Odontologo)
admin.site.register(Clinica)
admin.site.register(CustomUser, CustomUserAdmin)

