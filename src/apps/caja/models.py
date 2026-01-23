from django.db import models
from django.core.exceptions import ValidationError

from apps.turnos.models import Turno
from apps.estancias.models import Estancia
from apps.productos.models import Producto


class MovimientoCaja(models.Model):

    class TipoMovimiento(models.TextChoices):
        ESTANCIA = "ESTANCIA", "Estancia"
        EXTRA = "EXTRA", "Hora extra"
        PRODUCTO = "PRODUCTO", "Producto"

    class MetodoPago(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"

    # ==========================
    # Relaciones
    # ==========================
    turno = models.ForeignKey(
        Turno,
        on_delete=models.PROTECT,
        related_name="movimientos"
    )

    estancia = models.ForeignKey(
        Estancia,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimientos"
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimientos"
    )

    # ==========================
    # Datos del movimiento
    # ==========================
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

    # ==========================
    # Validaciones de dominio
    # ==========================
    def clean(self):
        if self.monto <= 0:
            raise ValidationError("El monto debe ser mayor a cero")

        if not self.turno.activo:
            raise ValidationError("No se pueden registrar movimientos en un turno cerrado")

        if self.tipo in [self.TipoMovimiento.ESTANCIA, self.TipoMovimiento.EXTRA]:
            if not self.estancia:
                raise ValidationError("Este movimiento requiere una estancia")

        if self.tipo == self.TipoMovimiento.PRODUCTO:
            if not self.producto:
                raise ValidationError("Este movimiento requiere un producto")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo} - ${self.monto} ({self.metodo_pago})"
