from django.core.exceptions import ValidationError
from .models import Turno
from apps.caja.models import MovimientoCaja
from django.db.models import Sum
from django.utils import timezone


def iniciar_turno(*, usuario, tipo_turno, sueldo, caja_inicial):
    if Turno.objects.filter(usuario=usuario, activo=True).exists():
        raise ValidationError("El usuario ya tiene un turno activo")

    turno = Turno.objects.create(
        usuario=usuario,
        tipo_turno=tipo_turno,
        sueldo=sueldo,
        caja_inicial=caja_inicial,
    )

    return turno


def cerrar_turno(*, usuario, sueldo_reportado, efectivo_reportado):
    try:
        turno = Turno.objects.get(usuario=usuario, activo=True)
    except Turno.DoesNotExist:
        raise ValidationError("No tienes un turno activo")

    # Sumar solo efectivo
    total_efectivo = (
        MovimientoCaja.objects
        .filter(
            turno=turno,
            metodo_pago=MovimientoCaja.MetodoPago.EFECTIVO
        )
        .aggregate(total=Sum("monto"))["total"] or 0
    )

    efectivo_esperado = (
        turno.caja_inicial
        + total_efectivo
        - sueldo_reportado
    )

    diferencia = efectivo_reportado - efectivo_esperado

    turno.sueldo_reportado = sueldo_reportado
    turno.efectivo_reportado = efectivo_reportado
    turno.efectivo_esperado = efectivo_esperado
    turno.diferencia = diferencia
    turno.activo = False
    turno.fecha_fin = timezone.now()
    turno.save()

    return turno