from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.habitaciones.models import Habitacion
from apps.tarifas.models import Tarifa
from apps.turnos.models import Turno


class Estancia(models.Model):

    class Meta:
        constraints = [
            # Una habitación solo puede tener una estancia activa
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
        on_delete=models.PROTECT,
        related_name="estancias"
    )

    tarifa = models.ForeignKey(
        Tarifa,
        on_delete=models.PROTECT,
        related_name="estancias"
    )

    turno_inicio = models.ForeignKey(
        Turno,
        on_delete=models.PROTECT,
        related_name="estancias_iniciadas"
    )

    turno_cierre = models.ForeignKey(
        Turno,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="estancias_cerradas"
    )

    # ==========================
    # Horarios
    # ==========================
    hora_entrada = models.DateTimeField(default=timezone.now)

    hora_salida_programada = models.DateTimeField(
        help_text="Hora calculada según tarifa y horas extra"
    )

    hora_salida_real = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Hora real en que el cliente salió"
    )

    # ==========================
    # Estado
    # ==========================
    activa = models.BooleanField(default=True)

    # ==========================
    # Dominio
    # ==========================
    def cerrar(self, *, turno_cierre, hora_salida_real):
        if not self.activa:
            raise ValidationError("La estancia ya está cerrada")

        self.turno_cierre = turno_cierre
        self.hora_salida_real = hora_salida_real
        self.activa = False
        self.save()

    def __str__(self):
        estado = "Activa" if self.activa else "Cerrada"
        return f"Habitación {self.habitacion.numero} - {estado}"
