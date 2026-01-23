from django.core.exceptions import ValidationError
from django.db import transaction
from apps.turnos.models import Turno
from .models import MovimientoCaja


@transaction.atomic
def crear_movimiento_caja(
    *,
    usuario,
    monto,
    metodo_pago,
    descripcion=""
):
    # Buscar turno activo
    try:
        turno = Turno.objects.get(activo=True)
    except Turno.DoesNotExist:
        raise ValidationError("No hay un turno activo")

    #Crear movimiento
    movimiento = MovimientoCaja.objects.create(
    turno=turno,
    monto=monto,
    metodo_pago=metodo_pago,
)

    return movimiento
