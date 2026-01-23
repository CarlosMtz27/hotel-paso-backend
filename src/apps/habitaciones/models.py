from django.db import models
from django.core.exceptions import ValidationError


class TipoHabitacion(models.Model):
    """
    Clasificación de habitaciones (Ej: Sencilla, Doble, Suite)
    """

    nombre = models.CharField(
        max_length=50,
        unique=True
    )

    descripcion = models.TextField(
        blank=True
    )

    activo = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.nombre


class Habitacion(models.Model):

    numero = models.PositiveIntegerField(
        unique=True
    )

    tipo = models.ForeignKey(
        TipoHabitacion,
        on_delete=models.PROTECT,
        related_name="habitaciones"
    )

    activa = models.BooleanField(
        default=True,
        help_text="Indica si la habitación está disponible para uso"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    # ==========================
    # Validaciones de dominio
    # ==========================
    def clean(self):
        if not self.tipo.activo:
            raise ValidationError(
                "No se puede asignar una habitación a un tipo inactivo"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        estado = "Activa" if self.activa else "Inactiva"
        return f"Habitación {self.numero} ({estado})"
