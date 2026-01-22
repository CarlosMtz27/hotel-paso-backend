from django.db import models
from django.utils import timezone
from apps.turnos.models import Turno


class Estancia(models.Model):
    class MetodoPago(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"

    turno = models.ForeignKey(
        Turno,
        on_delete=models.PROTECT,
        related_name="estancias",
    )

    habitacion = models.PositiveIntegerField()

    hora_entrada = models.DateTimeField(default=timezone.now)

    horas_base = models.PositiveIntegerField()
    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    metodo_pago = models.CharField(
        max_length=20,
        choices=MetodoPago.choices,
    )

    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"Habitación {self.habitacion} - Turno {self.turno.id}"
