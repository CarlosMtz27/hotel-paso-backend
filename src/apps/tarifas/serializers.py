from rest_framework import serializers
from .models import Tarifa


class TarifaSerializer(serializers.ModelSerializer):
    tipo_habitacion_nombre = serializers.CharField(
        source="tipo_habitacion.nombre",
        read_only=True
    )

    class Meta:
        model = Tarifa
        fields = [
            "id",
            "nombre",
            "horas",
            "precio",
            "es_nocturna",
            "hora_inicio_nocturna",
            "hora_fin_nocturna",
            "tipo_habitacion",
            "tipo_habitacion_nombre",
            "activa",
            "fecha_creacion",
        ]
