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

    # Regla: El usuario debe tener el permiso específico para abrir turnos.
    if not usuario.has_perm("turnos.abrir_turno"):
        raise ValidationError("No tienes permiso para abrir turno")

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

    # Regla: El usuario debe tener el permiso específico para cerrar turnos.
    if not usuario.has_perm("turnos.cerrar_turno"):
        raise ValidationError("No tienes permiso para cerrar turno")

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


def obtener_resumen_turno(*, turno):
    """
    Devuelve un diccionario con el resumen contable y operativo del turno.
    Esta función es de solo lectura y se usa para generar reportes.
    """

    # ==========================
    # INGRESOS (solo caja)
    # ==========================
    movimientos = (
        MovimientoCaja.objects
        .filter(turno=turno)
        .values("metodo_pago")
        .annotate(total=Sum("monto"))
    )

    totales = {
        "EFECTIVO": 0,
        "TRANSFERENCIA": 0,
    }

    for m in movimientos:
        totales[m["metodo_pago"]] = m["total"]

    total_ingresos = sum(totales.values())

    # ==========================
    # ESTANCIAS (informativo)
    # ==========================
    # Cuenta cuántas estancias se abrieron durante este turno.
    estancias_iniciadas = Estancia.objects.filter(
        turno_inicio=turno
    ).count()

    # Cuenta cuántas estancias se cerraron durante este turno.
    estancias_cerradas = Estancia.objects.filter(
        turno_cierre=turno
    ).count()

    # Cuenta cuántas estancias quedaron activas en el sistema al momento del cierre.
    estancias_activas = Estancia.objects.filter(
        activa=True
    ).count()

    # ==========================
    # RESPUESTA
    # ==========================
    return {
        "turno_id": turno.id,
        "fecha_inicio": turno.fecha_inicio,
        "fecha_fin": turno.fecha_fin,
        "usuario": str(turno.usuario),
        "tipo_turno": turno.tipo_turno,

        # caja
        "caja_inicial": turno.caja_inicial,
        "total_efectivo": totales["EFECTIVO"],
        "total_transferencia": totales["TRANSFERENCIA"],
        "total_ingresos": total_ingresos,
        "sueldo": turno.sueldo,
        "efectivo_esperado": turno.efectivo_esperado,
        "efectivo_reportado": turno.efectivo_reportado,
        "diferencia": turno.diferencia,

        # control
        "sin_ingresos": total_ingresos == 0,

        # estancias (operativo)
        "estancias": {
            "iniciadas": estancias_iniciadas,
            "cerradas": estancias_cerradas,
            "activas_al_cierre": estancias_activas,
        },
    }