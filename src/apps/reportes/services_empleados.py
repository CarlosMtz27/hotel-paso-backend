from django.db.models import Sum, Q, Count, Value, DecimalField
from django.db.models.functions import Coalesce
from apps.turnos.models import Turno
from apps.caja.models import MovimientoCaja
from django.contrib.auth import get_user_model

User = get_user_model()


def _get_empleado_report_queryset():
    """
    Queryset base y reutilizable para los reportes de empleados.
    Calcula todos los totales por empleado usando la potencia de la base de datos.
    """
    return User.objects.filter(rol=User.Rol.EMPLEADO).annotate(
        turnos_count=Count('turnos', distinct=True),
        total_efectivo=Coalesce(Sum('turnos__movimientos__monto', filter=Q(turnos__movimientos__metodo_pago='EFECTIVO')), Value(0), output_field=DecimalField()),
        total_transferencia=Coalesce(Sum('turnos__movimientos__monto', filter=Q(turnos__movimientos__metodo_pago='TRANSFERENCIA')), Value(0), output_field=DecimalField()),
        total_tarjeta=Coalesce(Sum('turnos__movimientos__monto', filter=Q(turnos__movimientos__metodo_pago='TARJETA')), Value(0), output_field=DecimalField()),
        total_ingresos=Coalesce(Sum('turnos__movimientos__monto'), Value(0), output_field=DecimalField()),
        total_sueldos=Coalesce(Sum('turnos__sueldo'), Value(0), output_field=DecimalField()),
        total_diferencias=Coalesce(Sum('turnos__diferencia'), Value(0), output_field=DecimalField()),
        turnos_sin_ingresos=Count('turnos', filter=Q(turnos__movimientos__isnull=True))
    )


def reporte_por_empleado():
    """
    Devuelve un resumen de ventas y caja por empleado, ordenado por nombre.
    """
    return _get_empleado_report_queryset().order_by('username')


def reporte_detalle_empleado(*, empleado_id):
    """
    Devuelve el detalle de turnos de un empleado.
    Este servicio ya era eficiente, solo se añaden comentarios.
    """

    turnos = (
        Turno.objects
        .filter(usuario_id=empleado_id)
        .order_by("-fecha_inicio")
    )

    detalle = []

    # Aquí el bucle es aceptable porque el número de turnos por empleado es manejable.
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
    """
    Devuelve un ranking de empleados ordenado por ingresos totales de forma descendente.
    Reutiliza el queryset base para máxima eficiencia.
    """
    return _get_empleado_report_queryset().order_by('-total_ingresos')


def grafica_ingresos_por_empleado():
    """
    Prepara los datos para ser consumidos directamente por una librería de gráficas.
    """
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
