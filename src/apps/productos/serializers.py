from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Producto.
    Maneja la validación (precio > 0, nombre único) y la conversión
    de datos entre el formato de la API y los objetos de Django.
    """

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'precio',
            'stock',
            'activo',
            'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion']
        extra_kwargs = {
            'nombre': {
                'validators': [
                    UniqueValidator(
                        queryset=Producto.objects.all(),
                        message="Ya existe un producto con ese nombre."
                    )
                ]
            },
            'stock': {'min_value': 0},
        }

    def validate_precio(self, value):
        """Valida que el precio sea mayor a cero."""
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a cero.")
        return value