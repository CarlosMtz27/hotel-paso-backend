from rest_framework import serializers
from .models import Turno
from django.db.models import Sum
from apps.caja.models import MovimientoCaja
from apps.estancias.models import Estancia
from apps.users.serializers import UserSerializer




class TurnoListSerializer(serializers.ModelSerializer):
    """
    Serializador de solo lectura para listar los turnos de forma resumida.
    Usado para el endpoint de listado y para devolver el objeto completo al crear.
    """
    usuario = UserSerializer(read_only=True)

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


class TurnoResumenSerializer(serializers.ModelSerializer):
    """
    Serializador de solo lectura para presentar un resumen completo de un turno cerrado.
    Calcula todos los totales y contadores relacionados con el turno.
    """
    usuario = serializers.CharField(source='usuario.username', read_only=True)

    # Campos calculados para el resumen financiero
    total_efectivo = serializers.SerializerMethodField()
    total_transferencia = serializers.SerializerMethodField()
    total_tarjeta = serializers.SerializerMethodField()
    total_ingresos = serializers.SerializerMethodField()
    sin_ingresos = serializers.SerializerMethodField()

    # Campos calculados para el resumen operativo (estancias)
    estancias = serializers.SerializerMethodField()

    class Meta:
        model = Turno
        fields = [
            'id', 'usuario', 'tipo_turno', 'fecha_inicio', 'fecha_fin',
            'caja_inicial', 'sueldo', 'efectivo_esperado', 'efectivo_reportado', 'diferencia',
            'total_efectivo', 'total_transferencia', 'total_tarjeta', 'total_ingresos',
            'sin_ingresos', 'estancias'
        ]

    def get_totales_movimientos(self, obj):
        """
        Método auxiliar para evitar recalcular los totales.
        Se ejecuta una vez y almacena los resultados en el contexto del serializador.
        """
        if not hasattr(self, '_totales_movimientos'):
            movimientos = MovimientoCaja.objects.filter(turno=obj).values('metodo_pago').annotate(total=Sum('monto'))
            self._totales_movimientos = {m['metodo_pago']: m['total'] for m in movimientos}
        return self._totales_movimientos

    def get_total_efectivo(self, obj):
        return self.get_totales_movimientos(obj).get('EFECTIVO', 0)

    def get_total_transferencia(self, obj):
        return self.get_totales_movimientos(obj).get('TRANSFERENCIA', 0)

    def get_total_tarjeta(self, obj):
        # Se asume que 'TARJETA' es un método de pago válido, como en los reportes.
        return self.get_totales_movimientos(obj).get('TARJETA', 0)

    def get_total_ingresos(self, obj):
        totales = self.get_totales_movimientos(obj)
        return sum(totales.values())

    def get_sin_ingresos(self, obj):
        return self.get_total_ingresos(obj) == 0

    def get_estancias(self, obj):
        """
        Calcula un resumen de la actividad de estancias durante el turno.
        """
        if not hasattr(self, '_resumen_estancias'):
            self._resumen_estancias = {
                "iniciadas": Estancia.objects.filter(turno_inicio=obj).count(),
                "cerradas": Estancia.objects.filter(turno_cierre=obj).count(),
                # Nota: Este valor es el estado actual, no al momento del cierre.
                # Para un valor histórico exacto, se necesitaría un snapshot o una lógica más compleja.
                "activas_al_cierre": Estancia.objects.filter(activa=True).count()
            }
        return self._resumen_estancias