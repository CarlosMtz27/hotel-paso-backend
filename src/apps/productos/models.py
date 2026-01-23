from django.db import models
from django.core.exceptions import ValidationError


class Producto(models.Model):

    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    activo = models.BooleanField(
        default=True,
        help_text="Indica si el producto está disponible para la venta"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    # ==========================
    # Validaciones de dominio
    # ==========================
    def clean(self):
        if self.precio <= 0:
            raise ValidationError("El precio debe ser mayor a cero")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.nombre} - ${self.precio} ({estado})"
