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


@transaction.atomic
def vender_producto(
    *,
    producto,
    cantidad,
    metodo_pago,
    turno,
    estancia=None
):
    """
    Registra la venta de un producto.
    Puede o no estar asociado a una estancia.
    """

    if not turno.activo:
        raise ValidationError("No hay un turno activo")

    if not producto.activo:
        raise ValidationError("El producto no está activo")

    if cantidad <= 0:
        raise ValidationError("Cantidad inválida")

    monto_total = producto.precio * cantidad

    MovimientoCaja.objects.create(
        turno=turno,
        tipo=MovimientoCaja.TipoMovimiento.PRODUCTO,
        monto=monto_total,
        metodo_pago=metodo_pago,
        producto_id=producto.id,
        estancia_id=estancia.id if estancia else None
    )

    return monto_total


