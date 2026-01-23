from django.core.exceptions import ValidationError
from .models import Tarifa


def crear_tarifa(
    *,
    nombre,
    horas,
    precio,
    tipo_habitacion,
    es_nocturna=False,
    hora_inicio_nocturna=None,
    hora_fin_nocturna=None,
):
    if not tipo_habitacion.activo:
        raise ValidationError("El tipo de habitación está inactivo")

    tarifa = Tarifa.objects.create(
        nombre=nombre,
        horas=horas,
        precio=precio,
        tipo_habitacion=tipo_habitacion,
        es_nocturna=es_nocturna,
        hora_inicio_nocturna=hora_inicio_nocturna,
        hora_fin_nocturna=hora_fin_nocturna,
    )

    return tarifa


def actualizar_tarifa(
    *,
    tarifa,
    nombre=None,
    horas=None,
    precio=None,
    activa=None
):
    if nombre is not None:
        tarifa.nombre = nombre

    if horas is not None:
        tarifa.horas = horas

    if precio is not None:
        tarifa.precio = precio

    if activa is not None:
        tarifa.activa = activa

    tarifa.full_clean()
    tarifa.save()

    return tarifa
