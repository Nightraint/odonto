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
from . import settings
from .vistas import paciente, odontologo, norma_trabajo, ficha, obra_social, plan, turno, tutorial, cuenta_corriente, views
from django.contrib.auth import views as auth_views
from odonto.forms import UserLoginForm, PasswordForm
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('ficha/crear', ficha.crear, name='crear'),
    path('ficha/eliminar/<int:pk>', ficha.FichaEliminar.as_view(), name='eliminar'),
    path('ficha/editar/<int:pk>', ficha.editar, name='editar'),
    path('ficha/detalle/<int:pk>', ficha.FichaDetalle.as_view(template_name = "ficha/detail.html"), name='detalle'),
    path('ficha/', ficha.FichaList.as_view(template_name='ficha/list.html'), name='ficha_index'),
    path('ficha/odontograma/', ficha.odontograma, name='ficha_odontograma'),

    path('odontologo/crear', odontologo.OdontologoCrear.as_view(template_name = "odontologo/form.html"), name='crear'),
    path('odontologo/eliminar/<int:pk>', odontologo.OdontologoEliminar.as_view(), name='eliminar'),
    path('odontologo/editar/<int:pk>', odontologo.OdontologoEditar.as_view(template_name = "odontologo/form.html"), name='editar'),
    path('odontologo/detalle/<int:pk>', odontologo.OdontologoDetalle.as_view(template_name = "odontologo/detail.html"), name='detalle'),
    path('odontologo/', odontologo.OdontologoList.as_view(template_name='odontologo/list.html'), name='odontologo_index'),
    path(r'odontologo/get_for_select/', odontologo.get_for_select, name='get_for_select'),

    path('obra_social/crear', obra_social.crear , name='crear'),
    path('obra_social/eliminar/<int:pk>', obra_social.ObraSocialEliminar.as_view(), name='eliminar'),
    path('obra_social/editar/<int:pk>', obra_social.editar, name='editar'),
    path('obra_social/detalle/<int:pk>', obra_social.Obras_Sociales_Detalle.as_view(template_name = "obra_social/detail.html"), name='detalle'),
    path('obra_social/', obra_social.Obra_SocialList.as_view(template_name='obra_social/list.html'), name='obra_social_index'),
    path(r'obra_social/get_for_select/', obra_social.get_for_select, name='get_for_select'),
    path('obra_social/<int:pk>', obra_social.get, name='get'),

    path('cuenta_corriente/crear', cuenta_corriente.Cuenta_CorrienteCrear.as_view(template_name = "cuenta_corriente/form.html") , name='cuenta_corriente_crear'),
    path('cuenta_corriente/eliminar/<int:pk>', cuenta_corriente.Cuenta_CorrienteEliminar.as_view(), name='eliminar'),
    path('cuenta_corriente/editar/<int:pk>', cuenta_corriente.Cuenta_CorrienteEditar.as_view(template_name = "cuenta_corriente/form.html") , name='cuenta_corriente_editar'),
    path('cuenta_corriente/', cuenta_corriente.Cuenta_CorrienteList.as_view(template_name='cuenta_corriente/list.html'), name='cuenta_corriente_index'),

    path(r'plan/get_for_select/', plan.get_for_select, name='get_for_select'),

    path('paciente/crear', paciente.crear , name='crear'),
    path('paciente/eliminar/<int:pk>', paciente.PacienteEliminar.as_view(), name='eliminar'),
    path('paciente/editar/<int:pk>', paciente.editar, name='editar'),
    path('paciente/detalle/<int:pk>', paciente.PacienteDetalle.as_view(template_name = "paciente/detail.html"), name='detalle'),
    path('paciente/', paciente.PacienteList.as_view(template_name='paciente/list.html'), name='paciente_index'),
    path(r'paciente/chequear_norma/', paciente.chequear_norma, name='chequear_norma'),

    path('norma_trabajo/crear', norma_trabajo.Norma_TrabajoCrear.as_view(template_name = "norma_trabajo/form.html"), name='crear'),
    path('norma_trabajo/eliminar/<int:pk>', norma_trabajo.Norma_TrabajoEliminar.as_view(), name='eliminar'),
    path('norma_trabajo/editar/<int:pk>', norma_trabajo.Norma_TrabajoEditar.as_view(template_name = "norma_trabajo/form.html"), name='editar'),
    path('norma_trabajo/detalle/<int:pk>', norma_trabajo.Norma_TrabajoDetalle.as_view(template_name = "norma_trabajo/detail.html"), name='detalle'),
    path('norma_trabajo/', norma_trabajo.Norma_TrabajoList.as_view(template_name='norma_trabajo/list.html'), name='norma_trabajo_index'),
    path(r'norma_trabajo/get_for_select/', norma_trabajo.get_for_select, name='get_for_select'),

    #path('turno/crear', turno.TurnoCrear.as_view(template_name="turno/form.html"), name='crear'),
    path('turno/crear', turno.crear, name='crear'),
    path('turno/', turno.index, name='turno_index'),
    path('turno/get_all', turno.get_all, name='get_all'),
    path('turno/eliminar/<int:pk>', turno.eliminar, name='eliminar_turno'),
    path('turno/actualizar/<int:pk>/', turno.actualizar, name='actualizar_turno'),
    path('turno/cancelar/', turno.cancelar, name='cancelar_turno'),

    path('tutoriales/', tutorial.TutorialList.as_view(template_name="tutorial/list.html"), name='tutorial_index'),
    path('tutoriales/<int:pk>', tutorial.TutorialDetalle.as_view(template_name="tutorial/detail.html"), name='tutorial_detail'),

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
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)