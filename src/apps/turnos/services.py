from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from .models import Turno
from apps.caja.models import MovimientoCaja


@transaction.atomic
def iniciar_turno(*, usuario, tipo_turno, caja_inicial=0, sueldo=0):
    """
    Inicia un turno asegurando que solo exista uno activo.
    """

    if Turno.objects.filter(activo=True).exists():
        raise ValidationError("Ya existe un turno activo")

    turno = Turno.objects.create(
        usuario=usuario,
        tipo_turno=tipo_turno,
        caja_inicial=caja_inicial,
        sueldo=sueldo,
        activo=True,
    )

    return turno


@transaction.atomic
def cerrar_turno_service(
    *,
    turno: Turno,
    efectivo_reportado,
    sueldo
):
    if not turno.activo:
        raise ValidationError("El turno ya está cerrado")

    total_efectivo = (
        MovimientoCaja.objects
        .filter(turno=turno, metodo_pago="EFECTIVO")
        .aggregate(total=Sum("monto"))["total"]
        or 0
    )

    total_movimientos = MovimientoCaja.objects.filter(turno=turno).count()
    sin_ingresos = total_movimientos == 0

    efectivo_esperado = (
        turno.caja_inicial
        + total_efectivo
        - sueldo
    )

    turno.cerrar_turno(
        efectivo_esperado=efectivo_esperado,
        efectivo_reportado=efectivo_reportado,
        sueldo=sueldo
    )

    return turno, sin_ingresos



def obtener_resumen_turno(*, turno):
    """
    Devuelve un resumen contable del turno.
    """

    movimientos = (
        MovimientoCaja.objects
        .filter(turno=turno)
        .values("metodo_pago")
        .annotate(total=Sum("monto"))
    )

    totales = {
        "EFECTIVO": 0,
        "TARJETA": 0,
        "TRANSFERENCIA": 0,
    }

    for m in movimientos:
        totales[m["metodo_pago"]] = m["total"]

    total_ingresos = sum(totales.values())

    return {
        "turno_id": turno.id,
        "fecha_inicio": turno.fecha_inicio,
        "fecha_fin": turno.fecha_fin,
        "caja_inicial": turno.caja_inicial,
        "total_efectivo": totales["EFECTIVO"],
        "total_tarjeta": totales["TARJETA"],
        "total_transferencia": totales["TRANSFERENCIA"],
        "total_ingresos": total_ingresos,
        "sueldo": turno.sueldo,
        "efectivo_esperado": turno.efectivo_esperado,
        "efectivo_reportado": turno.efectivo_reportado,
        "diferencia": turno.diferencia,
    }