from rest_framework import serializers
from .models import TipoHabitacion


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
