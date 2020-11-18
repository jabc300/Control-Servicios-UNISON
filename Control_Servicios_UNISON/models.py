from django.contrib.auth.models import User
from django.db import models


# Create your models here.

# DEFINICIÓN DE LOS USUARIOS

class UsuarioBase(models.Model):
    usuario = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

    BRIGADISTA = 'BR'
    JEFE_DEPTO = 'JD'
    RESPONSABL = 'RA'
    INVESTIGAD = 'IN'
    ALUMNO = 'AL'
    EMPLEADO = 'EM'
    QUIMICO = 'QU'
    SIN_ELEGIR = 'NA'
    ROLES_ELEGIBLES = [
        (SIN_ELEGIR, 'No elegido'),
        (BRIGADISTA, 'Brigadista'),
        (JEFE_DEPTO, 'Jefe de departamento'),
        (RESPONSABL, 'Responsable'),
        (INVESTIGAD, 'Investigador'),
        (ALUMNO, 'Alumno'),
        (EMPLEADO, 'Empleado'),
        (QUIMICO, 'Químico'),
    ]

    rol = models.CharField(
        max_length=2,
        choices=ROLES_ELEGIBLES,
        default=SIN_ELEGIR,
    )
    REQUIRED_FIELDS = []

    fsi_02 = models.BooleanField()
    fsi_04 = models.BooleanField()
    capacitacion = models.BooleanField()


# ----------------------------------------------------------------------------------------------------------------------
# Elementos específicos de cada rol:
# Una vez autorizado, el usuario estándar se expande con información específica con la que trabajará.

# Brigadista asignado a una división
class AsignacionBrigada(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    division = models.ForeignKey('Division', on_delete=models.CASCADE)


# Químico activo para recibir información y enviar resultados
class QuimicoActivo(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)


# Asignación de un área de la que será responsable
class ResponsabilidadArea(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    area_trabajo = models.ForeignKey('AreaTrabajo', on_delete=models.CASCADE)


# Vinculación con un departamento específico
class JefaturaDepartamento(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE)


# Información sobre el turno actual
class TurnoAsignado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    area_trabajo = models.ForeignKey('AreaTrabajo', on_delete=models.CASCADE)
    # horario


# ----------------------------------------------------------------------------------------------------------------------
# Estructura de los espacios
class Division(models.Model):
    nombre = models.CharField(max_length=100)


class Departamento(models.Model):
    nombre = models.CharField(max_length=100)
    division = models.ForeignKey('Division', on_delete=models.CASCADE)


class AreaTrabajo(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE)
    direccion = models.CharField(max_length=500)  # Cambiar por maps: https://pypi.org/project/django-google-maps/
    espacio_m2 = models.IntegerField()
    capacidad = models.IntegerField()
    autorizada = models.BooleanField(default=False)
    ultima_rev = models.DateTimeField(null=True)


# ----------------------------------------------------------------------------------------------------------------------
# Reportes de control
class InspeccionSanitaria(models.Model):
    brigadista = models.ForeignKey('AsignacionBrigada', on_delete=models.CASCADE)
    area_revisada = models.ForeignKey('AreaTrabajo', on_delete=models.CASCADE)
    fecha = models.DateTimeField(null=True)
    riesgo = models.IntegerField()  # Determina la prioridad para la comisión. Entre menos, mejor.


class PruebaCovidPositivo(models.Model):
    quimico = models.ForeignKey('QuimicoActivo', on_delete=models.PROTECT)
    paciente = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_aplicacion = models.DateTimeField(null=True)
    fecha_entrega = models.DateTimeField(null=True)