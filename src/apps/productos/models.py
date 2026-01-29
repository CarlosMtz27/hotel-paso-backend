from django.db import models
from django.core.exceptions import ValidationError


class Producto(models.Model):
    """
    Representa un producto o servicio que se puede vender en el hotel.
    Ejemplos: Refresco, Papas Fritas, etc.
    """

    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre único del producto."
    )

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio de venta del producto."
    )

    activo = models.BooleanField(
        default=True,
        help_text="Indica si el producto está disponible para la venta"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    # Validaciones de dominio
    def clean(self):
        """
        Aplica reglas de negocio a nivel de modelo.
        - El precio no puede ser cero o negativo.
        """
        if self.precio <= 0:
            raise ValidationError("El precio debe ser mayor a cero")

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para asegurar que las validaciones del `clean`
        se ejecuten siempre antes de guardar.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Representación en cadena para legibilidad."""
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.nombre} - ${self.precio} ({estado})"
