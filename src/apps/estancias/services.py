from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

from apps.estancias.models import Estancia
from apps.turnos.models import Turno
from apps.caja.models import MovimientoCaja


@transaction.atomic
def abrir_estancia(
    *,
    habitacion,
    tarifa,
    metodo_pago,
    turno
):
    """
    Abre una estancia y registra el cobro base en caja.
    """

    if not turno.activo:
        raise ValidationError("No hay un turno activo")

    if not habitacion.activa:
        raise ValidationError("La habitación no está activa")

    if Estancia.objects.filter(habitacion=habitacion, activa=True).exists():
        raise ValidationError("La habitación ya está ocupada")

    if not tarifa.activa:
        raise ValidationError("La tarifa no está activa")

    hora_entrada = timezone.now()
    hora_salida_programada = hora_entrada + timezone.timedelta(
        hours=tarifa.horas
    )

    estancia = Estancia.objects.create(
        habitacion=habitacion,
        tarifa=tarifa,
        turno_inicio=turno,
        hora_entrada=hora_entrada,
        hora_salida_programada=hora_salida_programada,
        activa=True,
    )

    # Movimiento de caja por la estancia base
    MovimientoCaja.objects.create(
        turno=turno,
        tipo=MovimientoCaja.TipoMovimiento.ESTANCIA,
        monto=tarifa.precio,
        metodo_pago=metodo_pago,
        estancia_id=estancia.id,
    )

    return estancia


@transaction.atomic
def cerrar_estancia(
    *,
    estancia,
    turno,
    hora_salida_real=None
):
    """
    Cierra una estancia sin recalcular montos.
    """

    if not estancia.activa:
        raise ValidationError("La estancia ya está cerrada")

    if not turno.activo:
        raise ValidationError("No hay un turno activo")

    if estancia.turno_inicio != turno:
        raise ValidationError("La estancia pertenece a otro turno")

    estancia.cerrar(
        turno_cierre=turno,
        hora_salida_real=hora_salida_real or timezone.now()
    )

    return estancia


@transaction.atomic
def agregar_horas_extra(
    *,
    estancia,
    turno,
    cantidad_horas,
    precio_hora,
    metodo_pago
):
    

    if not turno.activo:
        raise ValidationError("No hay un turno activo")

    if not estancia.activa:
        raise ValidationError("La estancia ya está cerrada")

    if cantidad_horas <= 0:
        raise ValidationError("Horas extra inválidas")

    precio_total = cantidad_horas * precio_hora

    # extender salida programada
    estancia.hora_salida_programada += timedelta(hours=cantidad_horas)
    estancia.save()

    # registrar ingreso en caja
    MovimientoCaja.objects.create(
        turno=turno,
        tipo="EXTRA",
        monto=precio_total,
        metodo_pago=metodo_pago,
        estancia_id=estancia.id
    )