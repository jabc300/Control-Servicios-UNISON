from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group

from .decorators import para_no_autenticados, usuarios_admitidos
from .formularios import *


# Create your views here.
def inicio(request):
    if request.user.is_authenticated:
        # Todos tienen un grupo por defecto al crearse
        grupo = request.user.groups.all()[0].name
        if grupo == 'Entrenamiento':
            incumbencia = 'capacitarse'

        elif grupo == 'Jefes de Departamento':
            incumbencia = 'registro-departamento'

        elif grupo == 'Responsables':
            incumbencia = 'administrar-area'

        elif grupo == 'Brigada':
            incumbencia = 'brigada'

        elif grupo == 'Comisión':
            incumbencia = 'seguimiento'

        # Aquí actúa el grupo Capacitados
        else:
            if request.user.usuariobase.rol != 'SIN_ELEGIR':
                incumbencia = 'turno'
            else:
                incumbencia = 'solicitar-acceso'

    else:
        incumbencia = 'iniciar-sesion'

    return redirect(incumbencia)

@para_no_autenticados
def registrarse(request):
    formulario = FormularioRegistro(request.POST)
    messages.success(request, 'Su cuenta se ha creado, complete los cursos y elija un rol.')
    if formulario.is_valid():
        formulario.save()

        return redirect('iniciar-sesion')

    context = {'formulario': formulario}
    return render(request, 'registrarse.html', context)


@para_no_autenticados
def iniciar_sesion(request):
    if request.method == 'POST':
        expediente = request.POST.get('expediente')
        contrasena = request.POST.get('contrasena')
        usuario = authenticate(request, username=expediente, password=contrasena)

        if usuario is not None:
            login(request, usuario)
            return redirect('inicio')
        else:
            messages.info(request, 'Esa combinación de expediente y contraseña no está en el sistema.')

    context = {}

    return render(request, 'iniciar-sesion.html', context)


def cerrar_sesion(request):
    logout(request)
    return redirect('iniciar-sesion')


@usuarios_admitidos(roles_admitidos=['Responsables'])
def administrar_area(request):
    context = {'solicitudes': SolicitudTurno.objects.filter(area_solici=request.user.responsabilidadarea.area_trabajo),
               'turnos': request.user.responsabilidadarea.area_trabajo.turnoasignado_set.all()}
    return render(request, 'administrar-area.html', context)


@usuarios_admitidos(roles_admitidos=['Brigada'])
def brigada(request):
    return render(request, 'brigada.html')


@usuarios_admitidos(roles_admitidos=['Jefes de Departamento'])
def registro_departamento(request):
    formulario = RegistrarArea(request.POST)
    departamento = request.user.jefaturadepartamento.departamento

    if request.method == 'POST':
        if formulario.is_valid():
            nueva_area = AreaTrabajo.objects.create(nombre=formulario.cleaned_data['nombre'], departamento=departamento, direccion=formulario.cleaned_data['direccion'], espacio_m2=formulario.cleaned_data['espacio_m2'], capacidad=formulario.cleaned_data['espacio_m2']/1.8)
            nueva_area.save()
            return redirect('registro-departamento')

    context = {'nombre_depto': departamento.nombre, 'division': departamento.division.nombre, 'areas': departamento.areatrabajo_set.all(), 'formulario': formulario}
    return render(request, 'registro-departamento.html', context)


@usuarios_admitidos(roles_admitidos=['Capacitados'])
def turno(request):
    return render(request, 'turno.html')


@usuarios_admitidos(roles_admitidos=['Capacitados'])
def solicitar_acceso(request):
    # Jefes de departamento
    if request.user.usuariobase.rol == 'JD':
        formulario = SolicitarJefatura(request.POST)
        if request.method == 'POST':
            if formulario.is_valid():
                nueva_jefatura = SolicitudJefatura.objects.create(jefe=request.user, division=formulario.cleaned_data['division'], nombre_depto=formulario.cleaned_data['nombre_depto'])
                nueva_jefatura.save()
                return redirect('inicio')

    # Responsables de área
    elif request.user.usuariobase.rol == 'RA':
        formulario = SolicitarApertura(request.POST)
        if request.method == 'POST':
            if formulario.is_valid():
                nueva_responsabilidad = SolicitudApertura.objects.create(responsable=request.user, area_solici=formulario.cleaned_data['area_solici'])
                nueva_responsabilidad.save()
                return redirect('inicio')

    # Usuarios que piden acceso
    elif request.user.usuariobase.rol == 'IN' or request.user.usuariobase.rol == 'AL' or request.user.usuariobase.rol == 'EM':
        formulario = SolicitarTurno(request.POST)
        if request.method == 'POST':
            if formulario.is_valid():
                nuevo_turno = SolicitudTurno.objects.create(usuario=request.user, area_solici=formulario.cleaned_data['area_solici'])
                nuevo_turno.save()
                return redirect('inicio')

    # Usuario aún sin rol definido
    else:
        formulario = EleccionRol(request.POST)
        if request.method == 'POST':
            if formulario.is_valid():
                request.user.usuariobase.rol = formulario.cleaned_data['rol']
                request.user.usuariobase.save()
                return redirect('solicitar-acceso')


    return render(request, 'solicitar-acceso.html', {'formulario':formulario})


@usuarios_admitidos(roles_admitidos=['Comisión'])
def seguimiento(request):
    context = {'solic_jefaturas': SolicitudJefatura.objects.all(), 'solic_aperturas': SolicitudApertura.objects.all()}
    return render(request, 'seguimiento.html', context)


@usuarios_admitidos(roles_admitidos=['Entrenamiento'])
def responder_fsi_02(request):
    formulario = Fsi_02(request.POST)
    if request.method == 'POST':
        if formulario.is_valid():
            for respuesta in formulario:
                if respuesta is False:
                    messages.info(request, 'Lamentablemente, no cumple con los requisitos para volver en esta etapa.')
                    return redirect('capacitarse')

            request.user.usuariobase.fsi_02 = True
            request.user.usuariobase.save()
            messages.success(request, 'Ha completado el formato FSI-02.')

            return redirect('capacitarse')

    context = {'formulario': formulario}
    return render(request, 'responder-FSI-02.html', context)


@usuarios_admitidos(roles_admitidos=['Entrenamiento'])
def responder_fsi_04(request):
    return None


@usuarios_admitidos(roles_admitidos=['Entrenamiento'])
def capacitarse(request):
    if request.user.usuariobase.fsi_02:
        grupo = Group.objects.get(name='Entrenamiento')
        request.user.groups.remove(grupo)
        grupo = Group.objects.get(name='Capacitados')
        request.user.groups.add(grupo)
        return redirect('inicio')

    return render(request, 'capacitarse.html')


@usuarios_admitidos(roles_admitidos=['Comisión'])
def divisiones(request):
    return None


@usuarios_admitidos(roles_admitidos=['Comisión'])
def aceptar_jefatura(request, pk):
    solicitud = SolicitudJefatura.objects.get(id=pk)

    nuevo_depto = Departamento.objects.create(nombre=solicitud.nombre_depto, division=solicitud.division)
    nuevo_depto.save()
    nueva_jefatura = JefaturaDepartamento.objects.create(usuario=solicitud.jefe, departamento=nuevo_depto)
    nueva_jefatura.save()

    solicitud.jefe.groups.add(Group.objects.get(name='Jefes de Departamento'))
    solicitud.jefe.groups.remove(Group.objects.get(name='Capacitados'))

    solicitud.delete()

    return render(request, 'aceptar-jefatura.html')


def aceptar_apertura(request, pk):
    solicitud = SolicitudApertura.objects.get(id=pk)

    nueva_responsabilidad = ResponsabilidadArea.objects.create(usuario=solicitud.responsable, area_trabajo=solicitud.area_solici)
    nueva_responsabilidad.save()

    solicitud.responsable.groups.add(Group.objects.get(name='Responsables'))
    solicitud.responsable.groups.remove(Group.objects.get(name="Capacitados"))
    solicitud.area_solici.autorizada = True
    solicitud.area_solici.usuarios += 1
    if solicitud.area_solici.usuarios == solicitud.area_solici.capacidad:
        solicitud.area_solici.disponibles = False

    solicitud.area_solici.save()
    solicitud.delete()

    return redirect(seguimiento)

def aceptar_turno(request, pk):
    solicitud = SolicitudTurno.objects.get(id=pk)

    nuevo_turno = TurnoAsignado.objects.create(usuario=solicitud.usuario, area_trabajo=solicitud.area_solici)
    nuevo_turno.save()

    solicitud.area_solici.usuarios += 1
    if solicitud.area_solici.usuarios >= solicitud.area_solici.capacidad:
        solicitud.area_solici.disponibles = False

    solicitud.area_solici.save()
    solicitud.delete()

    return redirect(administrar_area)