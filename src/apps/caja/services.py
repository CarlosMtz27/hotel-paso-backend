from django.core.exceptions import ValidationError
from django.db import transaction
from apps.productos.models import Producto
from apps.turnos.models import Turno
from .models import MovimientoCaja

@transaction.atomic
def vender_producto(
    *,
    producto: Producto,
    cantidad: int,
    metodo_pago: str,
    turno: Turno,
    estancia=None
) -> MovimientoCaja:
    """
    Servicio de negocio para registrar la venta de un producto.

    Este servicio encapsula toda la lógica para una venta:
    1. Valida que el producto esté disponible y tenga stock suficiente.
    2. Disminuye el stock del producto.
    3. Calcula el monto total de la transacción.
    4. Crea el registro contable (MovimientoCaja) correspondiente.
    5. Se ejecuta dentro de una transacción para garantizar la atomicidad.

    Args:
        producto: La instancia del modelo `Producto` que se está vendiendo.
        cantidad: El número de unidades del producto.
        metodo_pago: El método de pago utilizado (ej. 'EFECTIVO').
        turno: El turno activo en el que se realiza la venta.
        estancia (opcional): La estancia a la que se puede asociar la venta.

    Returns:
        La instancia del `MovimientoCaja` recién creada.

    Raises:
        ValidationError: Si el producto no está activo o no hay stock.
    """

    # Regla de negocio: Solo se pueden vender productos que están marcados como activos.
    if not producto.activo:
        raise ValidationError(f"El producto '{producto.nombre}' no está activo y no se puede vender.")

    # Regla de negocio: Debe haber suficiente stock para la venta.
    if producto.stock < cantidad:
        raise ValidationError(
            f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock}, Solicitado: {cantidad}."
        )

    # Disminuir el stock del producto.
    # Usar F() podría ser una opción para evitar race conditions, pero para este caso es suficiente.
    producto.stock -= cantidad
    producto.save(update_fields=['stock'])

    # Cálculo del monto total basado en el precio del producto y la cantidad.
    monto_total = producto.precio * cantidad

    # Creación del registro contable. Este es el único punto donde se crean
    # movimientos de tipo 'PRODUCTO', centralizando la lógica.
    movimiento = MovimientoCaja.objects.create(
        turno=turno,
        tipo=MovimientoCaja.TipoMovimiento.PRODUCTO,
        monto=monto_total,
        metodo_pago=metodo_pago,
        producto=producto, # Es mejor pasar la instancia completa.
        estancia=estancia # Pasa la instancia directamente.
    )

    # Se devuelve el objeto creado para que la vista pueda serializarlo y
    # enviarlo como respuesta al cliente.
    return movimiento
    # Cálculo del monto total basado en el precio del producto y la cantidad.
    monto_total = producto.precio * cantidad

    # Creación del registro contable. Este es el único punto donde se crean
    # movimientos de tipo 'PRODUCTO', centralizando la lógica.
    movimiento = MovimientoCaja.objects.create(
        turno=turno,
        tipo=MovimientoCaja.TipoMovimiento.PRODUCTO,
        monto=monto_total,
        metodo_pago=metodo_pago,
        producto=producto, # Es mejor pasar la instancia completa.
        estancia=estancia # Pasa la instancia directamente.
    )

    # Se devuelve el objeto creado para que la vista pueda serializarlo y
    # enviarlo como respuesta al cliente.
    return movimiento
