from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import TipoHabitacion, Habitacion


class TipoHabitacionSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo TipoHabitacion. Se usa para crear, listar y actualizar.
    """
    class Meta:
        model = TipoHabitacion
        fields = [
            "id",
            "nombre",
            "descripcion",
            "activo",
        ]
        extra_kwargs = {
            'nombre': {
                'validators': [
                    UniqueValidator(
                        queryset=TipoHabitacion.objects.all(),
                        message="Ya existe un tipo de habitación con ese nombre."
                    )
                ]
            }
        }

class HabitacionSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Habitacion.
    """
    # Campo de solo lectura para incluir el nombre del tipo de habitación en la respuesta,
    # lo que evita que el cliente tenga que hacer una petición extra.
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
        read_only_fields = ['id', 'fecha_creacion']
        extra_kwargs = {
            'numero': {
                'validators': [
                    UniqueValidator(
                        queryset=Habitacion.objects.all(),
                        message="Ya existe una habitación con ese número."
                    )
                ]
            }
        }

    def validate_tipo(self, value):
        """
        Valida que el tipo de habitación seleccionado esté activo.
        """
        if not value.activo:
            raise serializers.ValidationError("No se puede asignar una habitación a un tipo inactivo.")
        return value