from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.habitaciones.models import Habitacion
from apps.tarifas.models import Tarifa
from apps.turnos.models import Turno


class Estancia(models.Model):
    """
    Representa la ocupación de una habitación por un cliente durante un
    período de tiempo determinado. Es el corazón operativo del hotel.
    """

    class Meta:
        constraints = [
            # Regla de negocio crítica: Una habitación no puede tener dos estancias activas al mismo tiempo.
            # Esta restricción a nivel de base de datos garantiza la integridad de los datos.
            models.UniqueConstraint(
                fields=["habitacion"],
                condition=models.Q(activa=True),
                name="unique_estancia_activa_por_habitacion"
            )
        ]
        permissions = [
            ("abrir_estancia", "Puede abrir una estancia"),
            ("cerrar_estancia", "Puede cerrar una estancia"),
            ("ver_estancias", "Puede ver estancias"),
        ]

    # ==========================
    # Relaciones
    # ==========================
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.PROTECT,  # Evita borrar una habitación si tiene estancias asociadas.
        related_name="estancias"
    )

    tarifa = models.ForeignKey(
        Tarifa,
        on_delete=models.PROTECT,  # Evita borrar una tarifa si está en uso.
        related_name="estancias"
    )

    turno_inicio = models.ForeignKey(
        Turno,
        on_delete=models.PROTECT,  # El turno donde se registró el inicio de la estancia.
        related_name="estancias_iniciadas"
    )

    turno_cierre = models.ForeignKey(
        Turno,
        on_delete=models.PROTECT,
        null=True,  # Puede ser nulo si la estancia aún está activa.
        blank=True,
        related_name="estancias_cerradas"  # El turno donde se registró el cierre.
    )

    # ==========================
    # Horarios
    # ==========================
    hora_entrada = models.DateTimeField(
        default=timezone.now,
        help_text="Hora en que el cliente ingresó a la habitación"
    )

    hora_salida_programada = models.DateTimeField(
        help_text="Hora calculada según tarifa y horas extra. Se actualiza si se agregan horas extras"
    )

    hora_salida_real = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Hora real en que el cliente salió"
    )

    # ==========================
    # Estado
    # ==========================
    activa = models.BooleanField(
        default=True,
        help_text="Indica si la estancia está actualmente en curso."
    )

    # ==========================
    # Dominio
    # ==========================
    def cerrar(self, *, turno_cierre, hora_salida_real):
        """
        Método de negocio para cerrar la estancia. Encapsula la lógica
        de cambiar el estado y registrar los datos de cierre.
        """
        if not self.activa:
            raise ValidationError("La estancia ya está cerrada")

        self.turno_cierre = turno_cierre
        self.hora_salida_real = hora_salida_real
        self.activa = False
        self.save(update_fields=['turno_cierre', 'hora_salida_real', 'activa'])

    def __str__(self):
        """Representación en cadena del objeto para legibilidad."""
        estado = "Activa" if self.activa else "Cerrada"
        return f"Habitación {self.habitacion.numero} - {estado}"
