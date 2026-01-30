from django.db import models
from django.core.exceptions import ValidationError


class TipoHabitacion(models.Model):
    """
    Representa una categoría o clasificación de habitaciones.
    Ejemplos: Sencilla, Doble, Suite, etc.
    """

    nombre = models.CharField(
        max_length=50,
        unique=True,
        help_text="Nombre único para el tipo de habitación (ej. 'Suite Presidencial')."
    )

    descripcion = models.TextField(
        blank=True,
        help_text="Descripción opcional de las características del tipo de habitación."
    )

    activo = models.BooleanField(
        default=True,
        help_text="Indica si este tipo de habitación está disponible para ser usado."
    )

    def __str__(self):
        """Representación en cadena para legibilidad en el admin y otras partes de Django."""
        return self.nombre


class Habitacion(models.Model):
    """
    Representa una habitación física individual en el hotel.
    Cada habitación tiene un número único y pertenece a un TipoHabitacion.
    """

    class Estado(models.TextChoices):
        DISPONIBLE = "DISPONIBLE", "Disponible"
        OCUPADA = "OCUPADA", "Ocupada"
        LIMPIEZA = "LIMPIEZA", "En Limpieza"
        MANTENIMIENTO = "MANTENIMIENTO", "En Mantenimiento"

    numero = models.PositiveIntegerField(
        unique=True,
        help_text="Número único que identifica la habitación."
    )

    tipo = models.ForeignKey(
        TipoHabitacion,
        on_delete=models.PROTECT,  # Evita borrar un tipo si tiene habitaciones asignadas.
        related_name="habitaciones"
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
        help_text="Estado operativo actual de la habitación."
    )

    activa = models.BooleanField(
        default=True,
        help_text="Indica si la habitación está operativa y puede ser asignada a una estancia."
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    # Métodos de Dominio y Validaciones
    def clean(self):
        """
        Aplica reglas de negocio a nivel de modelo antes de guardar.
        """
        # Regla: No se puede crear o asignar una habitación a un tipo que está inactivo.
        if not self.tipo.activo:
            raise ValidationError(
                "No se puede asignar una habitación a un tipo inactivo"
            )

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para asegurar que las validaciones del `clean`
        se ejecuten siempre antes de guardar.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Representación en cadena para legibilidad."""
        estado_str = "Inactiva" if not self.activa else self.get_estado_display()
        return f"Habitación {self.numero} ({estado_str})"
