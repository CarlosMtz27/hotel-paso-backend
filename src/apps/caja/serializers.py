from rest_framework import serializers
from .models import MovimientoCaja
from apps.productos.models import Producto
from apps.estancias.models import Estancia


class MovimientoCajaSerializer(serializers.ModelSerializer):
    """
    Serializador de solo lectura para listar y detallar movimientos de caja.
    Usa `StringRelatedField` para mostrar una representación legible de los
    objetos relacionados en lugar de solo sus IDs.
    """
    turno = serializers.StringRelatedField()
    estancia = serializers.StringRelatedField()
    producto = serializers.StringRelatedField()

    class Meta:
        model = MovimientoCaja
        fields = '__all__'  # Muestra todos los campos del modelo.


class CrearVentaProductoSerializer(serializers.Serializer):
    """
    Serializador de escritura para validar los datos de entrada al registrar
    la venta de un producto. No está ligado a un modelo directamente, solo
    define los campos esperados en la petición POST.
    """
    # Valida que el producto exista y esté activo.
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.filter(activo=True)
    )
    # Valida que la cantidad sea un entero positivo.
    cantidad = serializers.IntegerField(min_value=1)
    # Valida que el método de pago sea uno de los permitidos.
    metodo_pago = serializers.ChoiceField(choices=MovimientoCaja.MetodoPago.choices)
    # Permite asociar la venta a una estancia activa, pero no es obligatorio.
    estancia_id = serializers.PrimaryKeyRelatedField(
        queryset=Estancia.objects.filter(activa=True),
        required=False,
        allow_null=True
    )