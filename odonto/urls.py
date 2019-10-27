"""odonto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django import views
from . import views
from .vistas import paciente, odontologo, norma_trabajo, ficha, obra_social
from django.contrib.auth import views as auth_views
from odonto.forms import UserLoginForm, PasswordForm

urlpatterns = [
    path('ficha/crear', ficha.FichaCrear.as_view(template_name = "ficha/ficha_form.html"), name='crear'),
    path('ficha/eliminar/<int:pk>', ficha.FichaEliminar.as_view(), name='eliminar'),
    path('ficha/editar/<int:pk>', ficha.FichaEditar.as_view(template_name = "ficha/ficha_form.html"), name='editar'),
    path('ficha/detalle/<int:pk>', ficha.FichaDetalle.as_view(template_name = "ficha/ficha_detail.html"), name='detalle'),
    path('ficha/', ficha.FichaList.as_view(template_name='ficha/ficha_list.html'), name='ficha_index'),

    path('odontologo/crear', odontologo.OdontologoCrear.as_view(template_name = "odontologo/odontologo_form.html"), name='crear'),
    path('odontologo/eliminar/<int:pk>', odontologo.OdontologoEliminar.as_view(), name='eliminar'),
    path('odontologo/editar/<int:pk>', odontologo.OdontologoEditar.as_view(template_name = "odontologo/odontologo_form.html"), name='editar'),
    path('odontologo/detalle/<int:pk>', odontologo.OdontologoDetalle.as_view(template_name = "odontologo/odontologo_detail.html"), name='detalle'),
    path('odontologo/', odontologo.OdontologoList.as_view(template_name='odontologo/odontologo_list.html'), name='odontologo_index'),
    path(r'odontologo/get_for_select/', odontologo.get_for_select, name='get_for_select'),

    path('obra_social/crear', obra_social.ObraSocialCrear.as_view(template_name = "obra_social/obra_social_form.html"), name='crear'),
    path('obra_social/eliminar/<int:pk>', obra_social.ObraSocialEliminar.as_view(), name='eliminar'),
    path('obra_social/editar/<int:pk>', obra_social.ObraSocialEditar.as_view(template_name = "obra_social/obra_social_form.html"), name='editar'),
    path('obra_social/detalle/<int:pk>', obra_social.Obras_Sociales_Detalle.as_view(template_name = "obra_social/obra_social_detail.html"), name='detalle'),
    path('obra_social/', obra_social.Obra_SocialList.as_view(template_name='obra_social/obra_social_list.html'), name='obra_social_index'),
    path(r'obra_social/get_for_select/', obra_social.get_for_select, name='get_for_select'),

    path('paciente/crear', paciente.PacienteCrear.as_view(template_name = "paciente/paciente_form.html"), name='crear'),
    path('paciente/eliminar/<int:pk>', paciente.PacienteEliminar.as_view(), name='eliminar'),
    path('paciente/editar/<int:pk>', paciente.PacienteEditar.as_view(template_name = "paciente/paciente_form.html"), name='editar'),
    path('paciente/detalle/<int:pk>', paciente.PacienteDetalle.as_view(template_name = "paciente/paciente_detail.html"), name='detalle'),
    path('paciente/', paciente.PacienteList.as_view(template_name='paciente/paciente_list.html'), name='paciente_index'),
    path(r'paciente/chequear_norma/', paciente.chequear_norma, name='chequear_norma'),

    path('norma_trabajo/crear', norma_trabajo.Norma_TrabajoCrear.as_view(template_name = "norma_trabajo/norma_trabajo_form.html"), name='crear'),
    path('norma_trabajo/eliminar/<int:pk>', norma_trabajo.Norma_TrabajoEliminar.as_view(), name='eliminar'),
    path('norma_trabajo/editar/<int:pk>', norma_trabajo.Norma_TrabajoEditar.as_view(template_name = "norma_trabajo/norma_trabajo_form.html"), name='editar'),
    path('norma_trabajo/detalle/<int:pk>', norma_trabajo.Norma_TrabajoDetalle.as_view(template_name = "norma_trabajo/norma_trabajo_detail.html"), name='detalle'),
    path('norma_trabajo/', norma_trabajo.Norma_TrabajoList.as_view(template_name='norma_trabajo/norma_trabajo_list.html'), name='norma_trabajo_index'),
    path(r'norma_trabajo/get_for_select/', norma_trabajo.get_for_select, name='get_for_select'),

    path('',TemplateView.as_view(template_name='index.html'), name='index'),
    path('admin/', admin.site.urls),
    path('contacto/',views.contacto,name='contacto'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/',auth_views.LoginView.as_view(authentication_form=UserLoginForm),name='login'),
    path('register/',views.SignUpView.as_view(),name='register'),
    path('changepassword/', auth_views.PasswordChangeView.as_view(form_class=PasswordForm,
                                                                template_name = 'registration/password_change.html',
                                                                success_url = '/'),name='changepassword')
]
