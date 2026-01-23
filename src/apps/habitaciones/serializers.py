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
            "fecha_creacion",
        ]

class HabitacionSerializer(serializers.ModelSerializer):
    tipo_habitacion_nombre = serializers.CharField(
        source="tipo_habitacion.nombre",
        read_only=True
    )

    class Meta:
        model = Habitacion
        fields = [
            "id",
            "numero",
            "tipo_habitacion",
            "tipo_habitacion_nombre",
            "activa",
            "fecha_creacion",
        ]