from rest_framework import serializers
from .models import TipoHabitacion, Habitacion


class TipoHabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoHabitacion
        fields = [
            "id",
            "nombre",
            "descripcion",
            "activo",
        ]

class HabitacionSerializer(serializers.ModelSerializer):
    tipo_nombre = serializers.CharField(
        source="tipo.nombre",
        read_only=True
    )

    class Meta:
        model = Habitacion
        fields = [
            "id",
            "numero",
            "tipo",
            "tipo_nombre",
            "activa",
            "fecha_creacion",
        ]