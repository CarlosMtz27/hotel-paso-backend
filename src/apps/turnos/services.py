from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from .models import Turno
from apps.caja.models import MovimientoCaja


@transaction.atomic
def iniciar_turno(*, usuario, tipo_turno, caja_inicial=0, sueldo=0):
    """
    Inicia un turno asegurando que solo exista uno activo.
    """

    if Turno.objects.filter(activo=True).exists():
        raise ValidationError("Ya existe un turno activo")

    turno = Turno.objects.create(
        usuario=usuario,
        tipo_turno=tipo_turno,
        caja_inicial=caja_inicial,
        sueldo=sueldo,
        activo=True,
    )

    return turno


@transaction.atomic
def cerrar_turno_service(
    *,
    turno: Turno,
    efectivo_reportado,
    sueldo
):
    """
    Cierra un turno calculando el efectivo esperado.
    """

    if not turno.activo:
        raise ValidationError("El turno ya está cerrado")

    total_efectivo = (
        MovimientoCaja.objects
        .filter(
            turno=turno,
            metodo_pago=MovimientoCaja.MetodoPago.EFECTIVO
        )
        .aggregate(total=Sum("monto"))["total"]
        or 0
    )

    #Calcular efectivo esperado
    efectivo_esperado = (
        turno.caja_inicial
        + total_efectivo
        - sueldo
    )

    #Cerrar turno usando el modelo
    turno.cerrar_turno(
        efectivo_esperado=efectivo_esperado,
        efectivo_reportado=efectivo_reportado,
        sueldo=sueldo
    )

    return turno
