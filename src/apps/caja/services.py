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
    """
    NOTA: Esta función parece ser un remanente de una versión anterior y no se
    está utilizando actualmente en las vistas. La lógica de creación de movimientos
    se maneja a través de servicios más específicos como `vender_producto`,
    `abrir_estancia`, etc.
    """
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

    # Valida que el producto se pueda vender.
    if not producto.activo:
        raise ValidationError("El producto no está activo")

    monto_total = producto.precio * cantidad

    # Crea el registro contable en la base de datos.
    movimiento = MovimientoCaja.objects.create(
        turno=turno,
        tipo=MovimientoCaja.TipoMovimiento.PRODUCTO,
        monto=monto_total,
        metodo_pago=metodo_pago,
        producto_id=producto.id,
        estancia_id=estancia.id if estancia else None
    )

    # El método .save() del modelo llama a full_clean(), que ya valida
    # que el turno esté activo y que el monto sea positivo.

    # Devuelve el objeto creado para que la vista pueda serializarlo.
    return movimiento
