from django.db.models import Sum
from apps.turnos.models import Turno
from apps.caja.models import MovimientoCaja
from django.contrib.auth import get_user_model



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


def reporte_detalle_empleado(*, empleado_id):
    """
    Devuelve el detalle de turnos de un empleado
    """

    turnos = (
        Turno.objects
        .filter(usuario_id=empleado_id)
        .order_by("-fecha_inicio")
    )

    detalle = []

    for turno in turnos:
        movimientos = MovimientoCaja.objects.filter(turno=turno)

        total_efectivo = movimientos.filter(
            metodo_pago="EFECTIVO"
        ).aggregate(total=Sum("monto"))["total"] or 0

        total_transferencia = movimientos.filter(
            metodo_pago="TRANSFERENCIA"
        ).aggregate(total=Sum("monto"))["total"] or 0

        total_tarjeta = movimientos.filter(
            metodo_pago="TARJETA"
        ).aggregate(total=Sum("monto"))["total"] or 0

        total_ingresos = (
            total_efectivo + total_transferencia + total_tarjeta
        )

        detalle.append({
            "turno_id": turno.id,
            "tipo_turno": turno.tipo_turno,
            "fecha_inicio": turno.fecha_inicio,
            "fecha_fin": turno.fecha_fin,
            "caja_inicial": float(turno.caja_inicial),
            "total_efectivo": float(total_efectivo),
            "total_transferencia": float(total_transferencia),
            "total_tarjeta": float(total_tarjeta),
            "total_ingresos": float(total_ingresos),
            "sueldo": float(turno.sueldo),
            "efectivo_esperado": float(turno.efectivo_esperado or 0),
            "efectivo_reportado": float(turno.efectivo_reportado or 0),
            "diferencia": float(turno.diferencia or 0),
            "sin_ingresos": movimientos.count() == 0,
            "activo": turno.activo,
        })

    return detalle


def ranking_empleados():
    User = get_user_model()
    empleados = User.objects.all()

    ranking = []

    for empleado in empleados:
        turnos = Turno.objects.filter(usuario=empleado)

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

        total_ingresos = (
            total_efectivo + total_transferencia + total_tarjeta
        )

        turnos_sin_ingresos = turnos.filter(
            id__in=[
                t.id for t in turnos
                if not MovimientoCaja.objects.filter(turno=t).exists()
            ]
        ).count()

        ranking.append({
            "empleado_id": empleado.id,
            "empleado": str(empleado),
            "turnos": turnos.count(),
            "total_ingresos": float(total_ingresos),
            "total_efectivo": float(total_efectivo),
            "total_transferencia": float(total_transferencia),
            "total_tarjeta": float(total_tarjeta),
            "turnos_sin_ingresos": turnos_sin_ingresos,
        })

    # ordenar por ingresos
    ranking.sort(key=lambda x: x["total_ingresos"], reverse=True)

    return ranking


def grafica_ingresos_por_empleado():
    ranking = ranking_empleados()

    return {
        "labels": [r["empleado"] for r in ranking],
        "datasets": [
            {
                "label": "Ingresos Totales",
                "data": [r["total_ingresos"] for r in ranking],
            }
        ]
    }
