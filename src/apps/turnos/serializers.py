from rest_framework import serializers
from .models import Turno


class TurnoListSerializer(serializers.ModelSerializer):
    """
    Serializador de solo lectura para listar los turnos de forma resumida.
    Usado para el endpoint de listado y para devolver el objeto completo al crear.
    """
    usuario = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Turno
        fields = [
            'id', 'usuario', 'tipo_turno', 'fecha_inicio', 'fecha_fin',
            'activo', 'caja_inicial', 'efectivo_reportado', 'diferencia',
            'caja_final'
        ]


class InicioTurnoSerializer(serializers.ModelSerializer):
    """
    Serializador de escritura para validar los datos de entrada al iniciar un turno.
    """
    class Meta:
        model = Turno
        fields = [
            "tipo_turno",
            "caja_inicial",
        ]

    def validate_caja_inicial(self, value):
        """Valida que la caja inicial no sea negativa."""
        if value < 0:
            raise serializers.ValidationError("La caja inicial no puede ser negativa.")
        return value


class CerrarTurnoSerializer(serializers.Serializer):
    """
    Serializador de escritura para validar los datos de entrada al cerrar un turno.
    No está ligado a un modelo, solo define la estructura de la petición.
    """
    efectivo_reportado = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        error_messages={"min_value": "El efectivo reportado no puede ser negativo."}
    )
    sueldo = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        error_messages={"min_value": "El sueldo no puede ser negativo."}
    )