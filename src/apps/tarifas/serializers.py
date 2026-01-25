from rest_framework import serializers
from .models import Tarifa
from rest_framework.validators import UniqueTogetherValidator


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
        read_only_fields = ["id", "fecha_creacion"]
        validators = [
            UniqueTogetherValidator(
                queryset=Tarifa.objects.all(),
                fields=['nombre', 'tipo_habitacion'],
                message="Ya existe una tarifa con este nombre para el tipo de habitación seleccionado."
            )
        ]

    def validate_horas(self, value):
        """Valida que las horas sean mayores a cero."""
        if value <= 0:
            raise serializers.ValidationError("Las horas de la tarifa deben ser mayores a cero.")
        return value

    def validate(self, data):
        """
        Validaciones a nivel de objeto.
        - Valida la lógica de las tarifas nocturnas.
        """
        es_nocturna = data.get('es_nocturna', self.instance.es_nocturna if self.instance else False)
        hora_inicio = data.get('hora_inicio_nocturna', getattr(self.instance, 'hora_inicio_nocturna', None))
        hora_fin = data.get('hora_fin_nocturna', getattr(self.instance, 'hora_fin_nocturna', None))

        if es_nocturna:
            if not hora_inicio or not hora_fin:
                raise serializers.ValidationError("Las tarifas nocturnas deben tener una hora de inicio y fin.")
        else:
            if hora_inicio or hora_fin:
                raise serializers.ValidationError("Solo las tarifas nocturnas pueden tener un horario definido.")

        return data
