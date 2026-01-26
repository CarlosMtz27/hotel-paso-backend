from django.db import models
from django.core.exceptions import ValidationError

from apps.turnos.models import Turno
from apps.estancias.models import Estancia
from apps.productos.models import Producto


class MovimientoCaja(models.Model):
    """
    Representa una única transacción de dinero en el sistema.
    Es la fuente de verdad para todos los ingresos. Cada movimiento está
    anclado a un turno específico.
    """

    class TipoMovimiento(models.TextChoices):
        """Define el origen o la razón del movimiento de dinero."""
        ESTANCIA = "ESTANCIA", "Estancia"
        EXTRA = "EXTRA", "Hora extra"
        PRODUCTO = "PRODUCTO", "Producto"

    class MetodoPago(models.TextChoices):
        """Define cómo se realizó el pago."""
        EFECTIVO = "EFECTIVO", "Efectivo"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"

    # ==========================
    # Relaciones
    # ==========================
    turno = models.ForeignKey(
        Turno,
        on_delete=models.PROTECT,  # Evita borrar un turno si tiene movimientos.
        related_name="movimientos"
    )

    estancia = models.ForeignKey(
        Estancia,
        on_delete=models.PROTECT,
        null=True,  # Puede ser nulo (ej. venta directa de producto).
        blank=True, # Requerido para el admin de Django.
        related_name="movimientos"
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        null=True,  # Puede ser nulo (ej. cobro de estancia).
        blank=True, # Requerido para el admin de Django.
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
        """
        Aplica las reglas de negocio a nivel de modelo antes de guardar.
        Este método es llamado automáticamente por `full_clean`.
        """
        # Regla: El monto de un movimiento siempre debe ser positivo.
        if self.monto <= 0:
            raise ValidationError("El monto debe ser mayor a cero")

        # Regla: No se pueden registrar movimientos en un turno que ya ha sido cerrado.
        # Esto asegura la integridad contable de cada turno.
        if not self.turno.activo:
            raise ValidationError("No se pueden registrar movimientos en un turno cerrado")

        # Regla: Si el movimiento es por una estancia o una hora extra,
        # debe estar obligatoriamente asociado a una estancia.
        if self.tipo in [self.TipoMovimiento.ESTANCIA, self.TipoMovimiento.EXTRA]:
            if not self.estancia:
                raise ValidationError("Este movimiento requiere una estancia")

        # Regla: Si el movimiento es por la venta de un producto,
        # debe estar obligatoriamente asociado a un producto.
        if self.tipo == self.TipoMovimiento.PRODUCTO:
            if not self.producto:
                raise ValidationError("Este movimiento requiere un producto")

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para asegurar que las validaciones del `clean`
        se ejecuten siempre antes de guardar el objeto en la base de datos.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo} - ${self.monto} ({self.metodo_pago})"
