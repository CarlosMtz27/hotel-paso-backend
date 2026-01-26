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
    Servicio de negocio para abrir una nueva estancia.
    Orquesta la creación de la Estancia y su correspondiente MovimientoCaja inicial.
    Se ejecuta dentro de una transacción para garantizar la atomicidad.
    """

    # Regla: No se puede operar sin un turno activo.
    if not turno.activo:
        raise ValidationError("No hay un turno activo")

    # Regla: La habitación debe estar disponible para ser ocupada.
    if not habitacion.activa:
        raise ValidationError("La habitación no está activa")

    # Regla: La habitación no debe tener otra estancia activa.
    # Aunque hay una restricción en la BD, esta validación provee un mensaje de error más amigable.
    if Estancia.objects.filter(habitacion=habitacion, activa=True).exists():
        raise ValidationError("La habitación ya está ocupada")

    # Regla: La tarifa seleccionada debe estar activa.
    if not tarifa.activa:
        raise ValidationError("La tarifa no está activa")

    hora_entrada = timezone.now()
    # Regla: La hora de salida se calcula automáticamente y no es manipulable por el usuario.
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

    # Regla: El cobro de la tarifa base se registra inmediatamente en la caja.
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
    Servicio de negocio para cerrar una estancia.
    """

    # Regla: No se puede cerrar una estancia que ya está cerrada.
    if not estancia.activa:
        raise ValidationError("La estancia ya está cerrada")

    # Regla: La operación debe realizarse dentro de un turno activo.
    if not turno.activo:
        raise ValidationError("No hay un turno activo")

    # Delega la lógica de cambio de estado al método de dominio del modelo.
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
    """
    Servicio de negocio para agregar horas extra a una estancia activa.
    """

    # Regla: La operación debe realizarse dentro de un turno activo.
    if not turno.activo:
        raise ValidationError("No hay un turno activo")

    # Regla: No se pueden agregar horas a una estancia ya cerrada.
    if not estancia.activa:
        raise ValidationError("La estancia ya está cerrada")

    # Regla: La cantidad de horas debe ser un número positivo.
    if cantidad_horas <= 0:
        raise ValidationError("Horas extra inválidas")

    precio_total = cantidad_horas * precio_hora

    # Actualiza la hora de salida programada.
    estancia.hora_salida_programada += timezone.timedelta(hours=cantidad_horas)
    estancia.save(update_fields=['hora_salida_programada'])

    # Registra el ingreso correspondiente en la caja.
    MovimientoCaja.objects.create(
        turno=turno,
        tipo="EXTRA",
        monto=precio_total,
        metodo_pago=metodo_pago,
        estancia_id=estancia.id
    )

    return estancia