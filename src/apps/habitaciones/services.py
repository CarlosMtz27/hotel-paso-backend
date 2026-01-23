from django.core.exceptions import ValidationError
from .models import TipoHabitacion


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
