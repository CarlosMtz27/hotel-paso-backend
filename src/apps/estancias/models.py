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
    # Estado de la estancia
    # ==========================
    hora_entrada = models.DateTimeField(
        default=timezone.now
    )

    hora_salida = models.DateTimeField(
        null=True,
        blank=True
    )

    activa = models.BooleanField(
        default=True
    )

    # ==========================
    # Validaciones de dominio
    # ==========================
    def clean(self):
        if not self.habitacion.activa:
            raise ValidationError("La habitación no está activa")

        if not self.turno_inicio.activo:
            raise ValidationError("El turno de inicio no está activo")

        if not self.tarifa.activa:
            raise ValidationError("La tarifa está inactiva")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # ==========================
    # Métodos de dominio
    # ==========================
    def cerrar(self, *, turno_cierre):
        if not self.activa:
            raise ValidationError("La estancia ya está cerrada")

        if not turno_cierre.activo:
            raise ValidationError("El turno de cierre no está activo")

        self.hora_salida = timezone.now()
        self.turno_cierre = turno_cierre
        self.activa = False
        self.save()

    def __str__(self):
        estado = "Activa" if self.activa else "Cerrada"
        return f"Habitación {self.habitacion.numero} - {estado}"
