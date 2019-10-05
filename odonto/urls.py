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
from django.contrib.auth import views as auth_views
from odonto.forms import UserLoginForm, PasswordForm

urlpatterns = [
    path('ficha/crear', views.FichaCrear.as_view(template_name = "ficha/ficha_form.html"), name='crear'),
    path('ficha/eliminar/<int:pk>', views.FichaEliminar.as_view(), name='eliminar'),
    path('ficha/editar/<int:pk>', views.FichaEditar.as_view(template_name = "ficha/ficha_form.html"), name='editar'),
    path('ficha/detalle/<int:pk>', views.FichaDetalle.as_view(template_name = "ficha/ficha_detail.html"), name='detalle'),
    path('ficha/', views.FichaList.as_view(template_name='ficha/ficha_list.html'), name='ficha_index'),

    path('odontologo/crear', views.OdontologoCrear.as_view(template_name = "odontologo/odontologo_form.html"), name='crear'),
    path('odontologo/eliminar/<int:pk>', views.OdontologoEliminar.as_view(), name='eliminar'),
    path('odontologo/editar/<int:pk>', views.OdontologoEditar.as_view(template_name = "odontologo/odontologo_form.html"), name='editar'),
    path('odontologo/detalle/<int:pk>', views.OdontologoDetalle.as_view(template_name = "odontologo/odontologo_detail.html"), name='detalle'),
    path('odontologo/', views.OdontologoList.as_view(template_name='odontologo/odontologo_list.html'), name='odontologo_index'),

    path('obra_social/crear', views.ObraSocialCrear.as_view(template_name = "obra_social/obra_social_form.html"), name='crear'),
    path('obra_social/eliminar/<int:pk>', views.ObraSocialEliminar.as_view(), name='eliminar'),
    path('obra_social/editar/<int:pk>', views.ObraSocialEditar.as_view(template_name = "obra_social/obra_social_form.html"), name='editar'),
    path('obra_social/detalle/<int:pk>', views.Obras_Sociales_Detalle.as_view(template_name = "obra_social/obra_social_detail.html"), name='detalle'),
    path('obra_social/', views.Obra_SocialList.as_view(template_name='obra_social/obra_social_list.html'), name='obra_social_index'),

    path('paciente/crear', views.PacienteCrear.as_view(template_name = "paciente/paciente_form.html"), name='crear'),
    path('paciente/eliminar/<int:pk>', views.PacienteEliminar.as_view(), name='eliminar'),
    path('paciente/editar/<int:pk>', views.PacienteEditar.as_view(template_name = "paciente/paciente_form.html"), name='editar'),
    path('paciente/detalle/<int:pk>', views.PacienteDetalle.as_view(template_name = "paciente/paciente_detail.html"), name='detalle'),
    path('paciente/', views.PacienteList.as_view(template_name='paciente/paciente_list.html'), name='paciente_index'),
    
    path('norma_trabajo/crear', views.Norma_TrabajoCrear.as_view(template_name = "norma_trabajo/norma_trabajo_form.html"), name='crear'),
    path('norma_trabajo/eliminar/<int:pk>', views.Norma_TrabajoEliminar.as_view(), name='eliminar'),
    path('norma_trabajo/editar/<int:pk>', views.Norma_TrabajoEditar.as_view(template_name = "norma_trabajo/norma_trabajo_form.html"), name='editar'),
    path('norma_trabajo/detalle/<int:pk>', views.Norma_TrabajoDetalle.as_view(template_name = "norma_trabajo/norma_trabajo_detail.html"), name='detalle'),
    path('norma_trabajo/', views.Norma_TrabajoList.as_view(template_name='norma_trabajo/norma_trabajo_list.html'), name='norma_trabajo_index'),

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
