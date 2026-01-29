from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from apps.estancias.models import Estancia
from .models import Turno
from apps.caja.models import MovimientoCaja


@transaction.atomic
def iniciar_turno(*, usuario, tipo_turno, caja_inicial=0):
    """
    Servicio de negocio para iniciar un nuevo turno.
    Valida permisos y la unicidad del turno activo.
    """

    # Regla: Solo puede existir un turno activo en todo el sistema a la vez.
    if Turno.objects.filter(activo=True).exists():
        raise ValidationError("Ya existe un turno activo")

    turno = Turno.objects.create(
        usuario=usuario,
        tipo_turno=tipo_turno,
        caja_inicial=caja_inicial,
        activo=True,
    )

    return turno


@transaction.atomic
def cerrar_turno_service(*, usuario, efectivo_reportado, sueldo):
    """
    Servicio de negocio para cerrar un turno.
    Orquesta las validaciones, el cálculo de totales y el cierre del turno.
    """
    try:
        # La responsabilidad de encontrar el turno activo ahora reside en el servicio.
        turno = Turno.objects.get(activo=True)
    except Turno.DoesNotExist:
        raise ValidationError("No hay un turno activo para cerrar.")

    # Regla: Un empleado solo puede cerrar el turno que él mismo abrió.
    if turno.usuario != usuario:
        raise ValidationError("Solo puedes cerrar tu propio turno.")

    # Regla: No se puede cerrar un turno que ya está cerrado.
    if not turno.activo:
        raise ValidationError("El turno ya está cerrado")

    # Calcula los totales de ingresos del turno desde los movimientos de caja.
    movimientos = MovimientoCaja.objects.filter(turno=turno)

    total_efectivo = (
        movimientos
        .filter(metodo_pago="EFECTIVO")
        .aggregate(total=Sum("monto"))["total"] or 0
    )

    total_transferencia = (
        movimientos
        .filter(metodo_pago="TRANSFERENCIA")
        .aggregate(total=Sum("monto"))["total"] or 0
    )

    total_ingresos = total_efectivo + total_transferencia

    # Bandera informativa para saber si el turno tuvo actividad económica.
    sin_ingresos = total_ingresos == 0

    # Fórmula contable para determinar el efectivo que debería haber en caja.
    efectivo_esperado_calculado = (
        turno.caja_inicial + total_efectivo - sueldo
    )

    # Se llama al método de negocio del modelo, que es el responsable de cambiar su estado.
    turno.cerrar_turno(
        efectivo_esperado=efectivo_esperado_calculado,
        efectivo_reportado=efectivo_reportado,
        sueldo=sueldo
    )

    return turno, sin_ingresos