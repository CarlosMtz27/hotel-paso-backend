from rest_framework import serializers
from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'precio',
            'activo',
            'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion']