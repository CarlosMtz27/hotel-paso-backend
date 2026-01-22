from django.db.models import Sum
from apps.turnos.models import Turno
from apps.caja.models import MovimientoCaja


def reporte_por_empleado():
    """
    Devuelve un resumen de ventas y caja por empleado
    """

    empleados = (
        Turno.objects
        .select_related("usuario")
        .values("usuario_id", "usuario__username")
        .distinct()
    )

    reporte = []

    for emp in empleados:
        turnos = Turno.objects.filter(usuario_id=emp["usuario_id"])

        movimientos = MovimientoCaja.objects.filter(turno__in=turnos)

        total_efectivo = movimientos.filter(
            metodo_pago="EFECTIVO"
        ).aggregate(total=Sum("monto"))["total"] or 0

        total_transferencia = movimientos.filter(
            metodo_pago="TRANSFERENCIA"
        ).aggregate(total=Sum("monto"))["total"] or 0

        total_tarjeta = movimientos.filter(
            metodo_pago="TARJETA"
        ).aggregate(total=Sum("monto"))["total"] or 0

        total_sueldos = (
            turnos.aggregate(total=Sum("sueldo"))["total"] or 0
        )

        total_diferencias = (
            turnos.aggregate(total=Sum("diferencia"))["total"] or 0
        )

        turnos_sin_ingresos = turnos.filter(
            movimientos__isnull=True
        ).distinct().count()

        reporte.append({
            "empleado_id": emp["usuario_id"],
            "empleado": emp["usuario__username"],
            "turnos": turnos.count(),
            "turnos_sin_ingresos": turnos_sin_ingresos,
            "total_efectivo": total_efectivo,
            "total_transferencia": total_transferencia,
            "total_tarjeta": total_tarjeta,
            "total_ingresos": (
                total_efectivo + total_transferencia + total_tarjeta
            ),
            "total_sueldos": total_sueldos,
            "total_diferencias": total_diferencias,
        })

    return reporte
