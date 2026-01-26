from rest_framework import serializers


class ReporteTurnoSerializer(serializers.Serializer):
    """
    Serializador de solo lectura para el reporte detallado por turno.
    Define la estructura de salida de los datos agregados por el servicio.
    """
    turno_id = serializers.IntegerField(source='id')
    empleado = serializers.CharField(source='usuario.username')
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


class ReporteEmpleadoSerializer(serializers.Serializer):
    """
    Serializador de solo lectura para el reporte agregado por empleado.
    Muestra los totales acumulados para cada empleado.
    """
    # `source` mapea el campo del modelo (`id`) al nombre deseado en la API (`empleado_id`).
    empleado_id = serializers.IntegerField(source='id')
    empleado = serializers.CharField(source='username')
    # `source` mapea el nombre del campo anotado en el queryset.
    turnos = serializers.IntegerField(source='turnos_count')
    turnos_sin_ingresos = serializers.IntegerField()
    total_efectivo = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_transferencia = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_tarjeta = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_ingresos = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_sueldos = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_diferencias = serializers.DecimalField(max_digits=12, decimal_places=2)
