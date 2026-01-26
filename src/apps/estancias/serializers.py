from rest_framework import serializers
from apps.estancias.models import Estancia
from apps.caja.models import MovimientoCaja
from apps.habitaciones.models import Habitacion
from apps.tarifas.models import Tarifa
from .models import Estancia


class EstanciaSerializer(serializers.ModelSerializer):
    """
    Serializador de solo lectura para listar estancias.
    Proporciona campos adicionales para una visualización más rica.
    NOTA: Este serializador parece ser un remanente y no se usa en las vistas actuales.
    `EstanciaDetalleSerializer` cumple una función similar y más completa.
    """
    habitacion_numero = serializers.IntegerField(
        source="habitacion.numero",
        read_only=True
    )
    tarifa_nombre = serializers.CharField(
        source="tarifa.nombre",
        read_only=True
    )
    turno_inicio_id = serializers.IntegerField(
        source="turno_inicio.id",
        read_only=True
    )
    turno_cierre_id = serializers.IntegerField(
        source="turno_cierre.id",
        read_only=True
    )

    class Meta:
        model = Estancia
        fields = [
            "id",
            "habitacion",
            "habitacion_numero",
            "tarifa",
            "tarifa_nombre",
            "hora_entrada",
            "hora_salida_programada",
            "hora_salida_real",
            "activa",
            "turno_inicio_id",
            "turno_cierre_id",
        ]

class AbrirEstanciaSerializer(serializers.Serializer):
    """
    Serializador de escritura para validar los datos de entrada al abrir una estancia.
    No está ligado a un modelo, solo define la estructura de la petición.
    """
    habitacion_id = serializers.PrimaryKeyRelatedField(
        queryset=Habitacion.objects.all(), source='habitacion'
    )
    tarifa_id = serializers.PrimaryKeyRelatedField(
        queryset=Tarifa.objects.all(), source='tarifa'
    )
    metodo_pago = serializers.ChoiceField(
        choices=MovimientoCaja.MetodoPago.choices
    )

class CerrarEstanciaSerializer(serializers.Serializer):
    """
    Serializador de escritura para validar los datos de entrada al cerrar una estancia.
    """
    estancia_id = serializers.PrimaryKeyRelatedField(
        queryset=Estancia.objects.all(), source='estancia'
    )
    # La hora de salida es opcional; si no se provee, el servicio usará la hora actual.
    hora_salida_real = serializers.DateTimeField(
        required=False,
        allow_null=True
    )


class AgregarHorasExtraSerializer(serializers.Serializer):
    """
    Serializador de escritura para validar los datos al agregar horas extra a una estancia.
    """
    estancia_id = serializers.PrimaryKeyRelatedField(
        queryset=Estancia.objects.all(), source='estancia'
    )
    cantidad_horas = serializers.IntegerField(min_value=1)
    precio_hora = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    metodo_pago = serializers.ChoiceField(
        choices=MovimientoCaja.MetodoPago.choices
    )

    def validate(self, data):
        """Valida que la estancia exista y esté activa."""
        estancia = data['estancia']
        # Regla de negocio: No se pueden agregar horas a una estancia ya cerrada.
        if not estancia.activa:
            raise serializers.ValidationError(
                {"estancia_id": "La estancia ya está cerrada"}
            )

        return data

class EstanciaDetalleSerializer(serializers.ModelSerializer):
    """
    Serializador de solo lectura para devolver el estado completo y actualizado
    de una estancia después de una operación (abrir, cerrar, etc.).
    """
    # Usamos  `StringRelatedField` para una respuesta más legible y amigable para el frontend.
    habitacion = serializers.StringRelatedField()
    tarifa = serializers.StringRelatedField()
    turno_inicio = serializers.StringRelatedField()
    turno_cierre = serializers.StringRelatedField()

    class Meta:
        model = Estancia
        fields = [
            "id",
            "habitacion",
            "tarifa",
            "hora_entrada",
            "hora_salida_programada",
            "hora_salida_real",
            "activa",
            "turno_inicio",
            "turno_cierre",
        ]
