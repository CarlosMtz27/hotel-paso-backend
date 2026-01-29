from django.db.models import Sum, Q, Count, Value, DecimalField, Case, When, BooleanField
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
    Devuelve el detalle de turnos de un empleado, calculado eficientemente
    con una única consulta a la base de datos.
    """
    turnos = (
        Turno.objects
        .filter(usuario_id=empleado_id)
        .annotate(
            total_efectivo=Coalesce(Sum('movimientos__monto', filter=Q(movimientos__metodo_pago='EFECTIVO')), Value(0), output_field=DecimalField()),
            total_transferencia=Coalesce(Sum('movimientos__monto', filter=Q(movimientos__metodo_pago='TRANSFERENCIA')), Value(0), output_field=DecimalField()),
            total_tarjeta=Coalesce(Sum('movimientos__monto', filter=Q(movimientos__metodo_pago='TARJETA')), Value(0), output_field=DecimalField()),
            total_ingresos=Coalesce(Sum('movimientos__monto'), Value(0), output_field=DecimalField()),
            sin_ingresos=Case(
                When(movimientos__isnull=True, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        .order_by("-fecha_inicio")
    )
    return turnos


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
    # Se evalúa el queryset una sola vez para mejorar el rendimiento.
    ranking_data = list(ranking_empleados().values('username', 'total_ingresos'))

    return {
        "labels": [r["username"] for r in ranking_data],
        "datasets": [
            {
                "label": "Ingresos Totales",
                "data": [r["total_ingresos"] for r in ranking_data],
            }
        ]
    }
