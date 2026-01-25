from django.core.exceptions import ValidationError
from .models import Habitacion, TipoHabitacion


def crear_tipo_habitacion(*, nombre, descripcion=""):
    if TipoHabitacion.objects.filter(nombre=nombre).exists():
        raise ValidationError("Ya existe un tipo de habitación con ese nombre")

    return TipoHabitacion.objects.create(
        nombre=nombre,
        descripcion=descripcion
    )


def actualizar_tipo_habitacion(*, tipo_habitacion, nombre=None, descripcion=None, activo=None):
    if nombre and nombre != tipo_habitacion.nombre:
        if TipoHabitacion.objects.filter(nombre=nombre).exists():
            raise ValidationError("Ya existe un tipo de habitación con ese nombre")
        tipo_habitacion.nombre = nombre

    if descripcion is not None:
        tipo_habitacion.descripcion = descripcion

    if activo is not None:
        tipo_habitacion.activo = activo

    tipo_habitacion.full_clean()
    tipo_habitacion.save()

    return tipo_habitacion


def crear_habitacion(*, numero, tipo):
    if Habitacion.objects.filter(numero=numero).exists():
        raise ValidationError("Ya existe una habitación con ese número")

    if not tipo.activo:
        raise ValidationError("El tipo de habitación está inactivo")

    return Habitacion.objects.create(
        numero=numero,
        tipo=tipo
    )


def actualizar_habitacion(*, habitacion, numero=None, tipo=None, activa=None):
    if numero and numero != habitacion.numero:
        if Habitacion.objects.filter(numero=numero).exists():
            raise ValidationError("Ya existe una habitación con ese número")
        habitacion.numero = numero

    if tipo:
        if not tipo.activo:
            raise ValidationError("El tipo de habitación está inactivo")
        habitacion.tipo = tipo

    if activa is not None:
        habitacion.activa = activa

    habitacion.full_clean()
    habitacion.save()

    return habitacion