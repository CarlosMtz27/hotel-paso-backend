from rest_framework import serializers
from apps.estancias.models import Estancia
from apps.caja.models import MovimientoCaja
from apps.habitaciones.models import Habitacion
from apps.tarifas.models import Tarifa
from .models import Estancia


class EstanciaSerializer(serializers.ModelSerializer):
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

    habitacion_id = serializers.IntegerField()
    tarifa_id = serializers.IntegerField()
    metodo_pago = serializers.ChoiceField(
        choices=MovimientoCaja.MetodoPago.choices
    )

    def validate(self, data):
        try:
            data["habitacion"] = Habitacion.objects.get(
                id=data["habitacion_id"]
            )
        except Habitacion.DoesNotExist:
            raise serializers.ValidationError(
                {"habitacion_id": "Habitación no existe"}
            )

        try:
            data["tarifa"] = Tarifa.objects.get(
                id=data["tarifa_id"]
            )
        except Tarifa.DoesNotExist:
            raise serializers.ValidationError(
                {"tarifa_id": "Tarifa no existe"}
            )

        return data

class CerrarEstanciaSerializer(serializers.Serializer):

    estancia_id = serializers.IntegerField()
    hora_salida_real = serializers.DateTimeField(
        required=False,
        allow_null=True
    )

    def validate(self, data):
        try:
            data["estancia"] = Estancia.objects.get(
                id=data["estancia_id"]
            )
        except Estancia.DoesNotExist:
            raise serializers.ValidationError(
                {"estancia_id": "La estancia no existe"}
            )

        return data


class AgregarHorasExtraSerializer(serializers.Serializer):

    estancia_id = serializers.IntegerField()
    cantidad_horas = serializers.IntegerField(min_value=1)
    precio_hora = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    metodo_pago = serializers.ChoiceField(
        choices=MovimientoCaja.MetodoPago.choices
    )

    def validate(self, data):
        try:
            data["estancia"] = Estancia.objects.get(
                id=data["estancia_id"]
            )
        except Estancia.DoesNotExist:
            raise serializers.ValidationError(
                {"estancia_id": "La estancia no existe"}
            )

        if not data["estancia"].activa:
            raise serializers.ValidationError(
                "La estancia ya está cerrada"
            )

        return data

class EstanciaDetalleSerializer(serializers.ModelSerializer):

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
