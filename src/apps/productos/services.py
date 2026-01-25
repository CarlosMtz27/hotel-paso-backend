from django.core.exceptions import ValidationError
from .models import Producto


def crear_producto(*, nombre: str, precio: float):
    """
    Crea un nuevo producto.
    Valida que el nombre no esté duplicado.
    """
    if Producto.objects.filter(nombre=nombre).exists():
        raise ValidationError("Ya existe un producto con ese nombre.")

    producto = Producto(nombre=nombre, precio=precio)
    producto.full_clean()  # Esto llamará al clean() del modelo para validar el precio
    producto.save()
    return producto


def actualizar_producto(*, producto: Producto, nombre: str = None, precio: float = None, activo: bool = None):
    """
    Actualiza un producto existente.
    """
    if nombre and nombre != producto.nombre:
        if Producto.objects.filter(nombre=nombre).exclude(pk=producto.pk).exists():
            raise ValidationError("Ya existe otro producto con ese nombre.")
        producto.nombre = nombre

    if precio is not None:
        producto.precio = precio

    if activo is not None:
        producto.activo = activo

    producto.full_clean()
    producto.save()
    return producto