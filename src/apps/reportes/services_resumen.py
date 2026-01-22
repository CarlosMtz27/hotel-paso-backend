from django.db.models import Sum
from django.utils import timezone
from apps.turnos.models import Turno
from apps.caja.models import MovimientoCaja


def resumen_diario(fecha=None):
    if fecha is None:
        fecha = timezone.now().date()

    turnos = Turno.objects.filter(
        fecha_inicio__date=fecha
    )

    total_efectivo = (
        MovimientoCaja.objects
        .filter(
            turno__in=turnos,
            metodo_pago="EFECTIVO"
        )
        .aggregate(total=Sum("monto"))["total"] or 0
    )

    total_transferencia = (
        MovimientoCaja.objects
        .filter(
            turno__in=turnos,
            metodo_pago="TRANSFERENCIA"
        )
        .aggregate(total=Sum("monto"))["total"] or 0
    )

    total_tarjeta = (
        MovimientoCaja.objects
        .filter(
            turno__in=turnos,
            metodo_pago="TARJETA"
        )
        .aggregate(total=Sum("monto"))["total"] or 0
    )

    total_sueldos = (
        turnos.aggregate(total=Sum("sueldo"))["total"] or 0
    )

    total_diferencias = (
        turnos.aggregate(total=Sum("diferencia"))["total"] or 0
    )

    return {
        "fecha": fecha,
        "turnos": turnos.count(),
        "turnos_sin_ingresos": turnos.filter(
            movimientos__isnull=True
        ).distinct().count(),
        "total_efectivo": total_efectivo,
        "total_transferencia": total_transferencia,
        "total_tarjeta": total_tarjeta,
        "total_ingresos": total_efectivo + total_transferencia + total_tarjeta,
        "total_sueldos": total_sueldos,
        "total_diferencias": total_diferencias,
    }
