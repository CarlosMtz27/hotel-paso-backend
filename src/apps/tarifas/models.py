from django.db import models
from django.core.exceptions import ValidationError
from apps.habitaciones.models import TipoHabitacion


class Tarifa(models.Model):
    """
    Representa una opción de precio y tiempo para un tipo de habitación.
    Ej: "3 horas para Habitación Sencilla", "Noche completa para Suite".
    """

    class Meta:
        constraints = [
            # Regla: No puede haber dos tarifas con el mismo nombre para el mismo tipo de habitación.
            models.UniqueConstraint(
                fields=["nombre", "tipo_habitacion"],
                name="unique_tarifa_por_tipo_habitacion"
            )
        ]
        permissions = [
            ("crear_tarifa", "Puede crear tarifas"),
            ("editar_tarifa", "Puede editar tarifas"),
            ("ver_tarifas", "Puede ver tarifas"),
            ("desactivar_tarifa", "Puede desactivar tarifas"),
        ]

    nombre = models.CharField(
        max_length=100,
        help_text="Ej: 3 horas, 6 horas, Noche completa"
    )

    horas = models.PositiveIntegerField(
        help_text="Duración base de la tarifa en horas"
    )

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Costo de la tarifa."
    )

    es_nocturna = models.BooleanField(
        default=False,
        help_text="Indica si esta tarifa aplica solo en un horario nocturno específico."
    )

    hora_inicio_nocturna = models.TimeField(
        null=True,
        blank=True,
        help_text="Hora de inicio si la tarifa es nocturna (ej. 21:00)."
    )

    hora_fin_nocturna = models.TimeField(
        null=True,
        blank=True,
        help_text="Hora de fin si la tarifa es nocturna (ej. 10:00)."
    )

    tipo_habitacion = models.ForeignKey(
        TipoHabitacion,
        on_delete=models.PROTECT, # Evita borrar un tipo de habitación si tiene tarifas.
        related_name="tarifas"
    )

    activa = models.BooleanField(
        default=True,
        help_text="Indica si la tarifa está disponible para ser usada en nuevas estancias."
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    # Validaciones de dominio
    def clean(self):
        """
        Aplica reglas de negocio a nivel de modelo antes de guardar.
        """
        # Regla: El precio debe ser un valor positivo.
        if self.precio <= 0:
            raise ValidationError("El precio debe ser mayor a cero.")

        # Regla: La duración en horas debe ser positiva.
        if self.horas <= 0:
            raise ValidationError(
                "Las horas de la tarifa deben ser mayores a cero"
            )

        # Regla: Si una tarifa es nocturna, debe tener un horario definido.
        if self.es_nocturna:
            if not self.hora_inicio_nocturna or not self.hora_fin_nocturna:
                raise ValidationError(
                    "Las tarifas nocturnas deben tener horario definido"
                )
        # Regla: Si una tarifa no es nocturna, no debe tener horario.
        else:
            if self.hora_inicio_nocturna or self.hora_fin_nocturna:
                raise ValidationError(
                    "Las tarifas diurnas no deben tener horario nocturno"
                )

        # Regla: No se puede asociar una tarifa a un tipo de habitación inactivo.
        if not self.tipo_habitacion.activo:
            raise ValidationError(
                "No se puede asignar una tarifa a un tipo de habitación inactivo"
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
        tipo = "Nocturna" if self.es_nocturna else "Diurna"
        return f"{self.nombre} - {self.tipo_habitacion} ({tipo})"
