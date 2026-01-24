from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from apps.estancias.models import Estancia
from .models import Turno
from apps.caja.models import MovimientoCaja


@transaction.atomic
def iniciar_turno(*, usuario, tipo_turno, caja_inicial=0):

    if not usuario.has_perm("turnos.abrir_turno"):
        raise ValidationError("No tienes permiso para abrir turno")

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
def cerrar_turno_service(*, turno, usuario, efectivo_reportado, sueldo):

    if not usuario.has_perm("turnos.cerrar_turno"):
        raise ValidationError("No tienes permiso para cerrar turno")

    if not turno.activo:
        raise ValidationError("El turno ya está cerrado")

    if efectivo_reportado is None or efectivo_reportado < 0:
        raise ValidationError("Efectivo reportado inválido")

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

    # solo informativo
    sin_ingresos = total_ingresos == 0

    turno.sueldo = sueldo
    turno.efectivo_reportado = efectivo_reportado
    turno.efectivo_esperado = (
        turno.caja_inicial + total_efectivo - sueldo
    )
    turno.diferencia = (
        efectivo_reportado - turno.efectivo_esperado
    )

    turno.activo = False
    turno.fecha_fin = timezone.now()
    turno.caja_final = efectivo_reportado
    turno.save()

    return turno, sin_ingresos


def obtener_resumen_turno(*, turno):
    """
    Devuelve resumen contable y operativo del turno.
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
    estancias_iniciadas = Estancia.objects.filter(
        turno_inicio=turno
    ).count()

    estancias_cerradas = Estancia.objects.filter(
        turno_cierre=turno
    ).count()

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
        "sueldo": turno.sueldo_reportado,
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