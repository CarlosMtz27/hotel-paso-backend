from django.db.models import Sum
from apps.turnos.models import Turno
from apps.caja.models import MovimientoCaja


def reporte_turnos(*, usuario, fecha_desde=None, fecha_hasta=None):
    # ADMIN ve todo, EMPLEADO solo sus turnos
    if usuario.is_staff:
        turnos = Turno.objects.all()
    else:
        turnos = Turno.objects.filter(usuario=usuario)

    # Filtros por fecha
    if fecha_desde:
        turnos = turnos.filter(fecha_inicio__date__gte=fecha_desde)

    if fecha_hasta:
        turnos = turnos.filter(fecha_inicio__date__lte=fecha_hasta)

    turnos = turnos.order_by("-fecha_inicio")

    reporte = []

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
            total_efectivo +
            total_transferencia +
            total_tarjeta
        )

        reporte.append({
            "turno_id": turno.id,
            "empleado": str(turno.usuario),
            "tipo_turno": turno.tipo_turno,
            "fecha_inicio": turno.fecha_inicio,
            "fecha_fin": turno.fecha_fin,
            "caja_inicial": turno.caja_inicial,
            "total_efectivo": total_efectivo,
            "total_transferencia": total_transferencia,
            "total_tarjeta": total_tarjeta,
            "total_ingresos": total_ingresos,
            "sueldo": turno.sueldo,
            "efectivo_esperado": turno.efectivo_esperado,
            "efectivo_reportado": turno.efectivo_reportado,
            "diferencia": turno.diferencia,
            "sin_ingresos": not movimientos.exists(),
        })

    return reporte




