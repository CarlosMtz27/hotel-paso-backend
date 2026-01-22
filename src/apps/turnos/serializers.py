from rest_framework import serializers
from .models import Turno

class InicioTurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turno
        fields = [
            "tipo_turno",
            "sueldo",
            "caja_inicial",
        ]


class CierreTurnoSerializer(serializers.Serializer):
    sueldo_reportado = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    efectivo_reportado = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )
