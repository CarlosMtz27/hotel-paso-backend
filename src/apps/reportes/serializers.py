from rest_framework import serializers


class ReporteTurnoSerializer(serializers.Serializer):
    turno_id = serializers.IntegerField()
    empleado = serializers.CharField()
    tipo_turno = serializers.CharField()
    fecha_inicio = serializers.DateTimeField()
    fecha_fin = serializers.DateTimeField(allow_null=True)

    caja_inicial = serializers.DecimalField(max_digits=10, decimal_places=2)

    total_efectivo = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_transferencia = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_tarjeta = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_ingresos = serializers.DecimalField(max_digits=10, decimal_places=2)

    sueldo = serializers.DecimalField(max_digits=10, decimal_places=2)

    efectivo_esperado = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True
    )
    efectivo_reportado = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True
    )
    diferencia = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True
    )

    sin_ingresos = serializers.BooleanField()
