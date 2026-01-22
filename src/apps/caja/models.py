from django.db import models
from apps.turnos.models import Turno


class MovimientoCaja(models.Model):

    class TipoMovimiento(models.TextChoices):
        ESTANCIA = "ESTANCIA", "Estancia"
        EXTRA = "EXTRA", "Hora extra"
        PRODUCTO = "PRODUCTO", "Producto"

    class MetodoPago(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"

    turno = models.ForeignKey(
        Turno,
        on_delete=models.PROTECT,
        related_name="movimientos"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TipoMovimiento.choices
    )

    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    metodo_pago = models.CharField(
        max_length=20,
        choices=MetodoPago.choices
    )

    fecha = models.DateTimeField(auto_now_add=True)

    # referencias opcionales (se usarán después)
    estancia_id = models.IntegerField(null=True, blank=True)
    producto_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} - ${self.monto} ({self.metodo_pago})"
