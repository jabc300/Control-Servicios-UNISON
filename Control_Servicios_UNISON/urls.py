from django.urls import path
from Control_Servicios_UNISON import views

urlpatterns = [
    # Áreas comunes de los usuarios
    path('', views.inicio, name="inicio"),
    path('registrarse/', views.registrarse, name="registrarse"),
    path('iniciar-sesion/', views.iniciar_sesion, name="iniciar-sesion"),
    path('cerrar-sesion/', views.cerrar_sesion, name="cerrar-sesion"),
    path('capacitarse/responder-FSI-02/', views.responder_fsi_02, name="responder-FSI-02"),
    path('responder-FSI-04/', views.responder_fsi_04, name="responder-FSI-04"),
    path('capacitarse/', views.capacitarse, name="capacitarse"),

    # Usuario que reserva turnos
    path('turno/', views.turno, name="turno"),
    path('solicitar-acceso/', views.solicitar_acceso, name="solicitar-acceso"),

    # Responsable del área
    path('administrar-area/', views.administrar_area, name="administrar-area"),

    # Brigadistas
    path('brigada/', views.brigada, name="brigada"),

    # Jefes de departamento
    path('registro-departamento/', views.registro_departamento, name="registro-departamento"),

    # Comisión de seguimiento
    path('divisiones/', views.divisiones, name="divisiones"),
    path('seguimiento/', views.seguimiento, name="seguimiento"),

    # Aceptar ingresos
    path('aceptar-jefatura/<str:pk>/', views.aceptar_jefatura, name="aceptar-jefatura"),
    path('aceptar-apertura/<str:pk>', views.aceptar_apertura, name="aceptar-apertura"),
    path('aceptar-turno/<str:pk>', views.aceptar_turno, name="aceptar-turno")

]