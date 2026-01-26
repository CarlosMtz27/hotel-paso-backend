from django.db.models import Sum, Q, Value, Case, When, BooleanField, DecimalField
from django.db.models.functions import Coalesce
from apps.turnos.models import Turno
from apps.users.models import Usuario


def reporte_turnos(*, usuario, fecha_desde=None, fecha_hasta=None):
    """
    Genera un reporte detallado de turnos con sus totales financieros.
    - Si el usuario es ADMIN, ve todos los turnos.
    - Si es EMPLEADO, solo ve sus propios turnos.
    Utiliza `annotate` para calcular los totales de forma eficiente en la base de datos.
    """
    # Regla de negocio: Un admin ve todo, un empleado solo lo suyo.
    if usuario.rol == Usuario.Rol.ADMINISTRADOR:
        turnos = Turno.objects.all()
    else:
        turnos = Turno.objects.filter(usuario=usuario)

    # Aplica filtros de fecha si se proporcionan.
    if fecha_desde:
        turnos = turnos.filter(fecha_inicio__date__gte=fecha_desde)

    if fecha_hasta:
        turnos = turnos.filter(fecha_inicio__date__lte=fecha_hasta)

    # Anotamos los cálculos directamente en el queryset.
    # `Coalesce` se usa para reemplazar los `None` por `0` cuando no hay movimientos.
    turnos = turnos.annotate(
        total_efectivo=Coalesce(Sum('movimientos__monto', filter=Q(movimientos__metodo_pago='EFECTIVO')), Value(0), output_field=DecimalField()),
        total_transferencia=Coalesce(Sum('movimientos__monto', filter=Q(movimientos__metodo_pago='TRANSFERENCIA')), Value(0), output_field=DecimalField()),
        total_tarjeta=Coalesce(Sum('movimientos__monto', filter=Q(movimientos__metodo_pago='TARJETA')), Value(0), output_field=DecimalField()),
        total_ingresos=Coalesce(Sum('movimientos__monto'), Value(0), output_field=DecimalField()),
        # `Case` y `When` para determinar si un turno no tuvo movimientos.
        sin_ingresos=Case(
            When(movimientos__isnull=True, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    ).select_related('usuario').order_by('-fecha_inicio')

    # El serializador se encargará de convertir este queryset enriquecido a formato JSON.
    return turnos
