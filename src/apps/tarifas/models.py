from django.db import models
from django.core.exceptions import ValidationError
from apps.habitaciones.models import TipoHabitacion


class Tarifa(models.Model):

    class Meta:
        constraints = [
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
        decimal_places=2
    )

    es_nocturna = models.BooleanField(
        default=False
    )

    hora_inicio_nocturna = models.TimeField(
        null=True,
        blank=True
    )

    hora_fin_nocturna = models.TimeField(
        null=True,
        blank=True
    )

    tipo_habitacion = models.ForeignKey(
        TipoHabitacion,
        on_delete=models.PROTECT,
        related_name="tarifas"
    )

    activa = models.BooleanField(
        default=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    # ==========================
    # Validaciones de dominio
    # ==========================
    def clean(self):
        if self.horas <= 0:
            raise ValidationError(
                "Las horas de la tarifa deben ser mayores a cero"
            )

        if self.es_nocturna:
            if not self.hora_inicio_nocturna or not self.hora_fin_nocturna:
                raise ValidationError(
                    "Las tarifas nocturnas deben tener horario definido"
                )
        else:
            if self.hora_inicio_nocturna or self.hora_fin_nocturna:
                raise ValidationError(
                    "Las tarifas diurnas no deben tener horario nocturno"
                )

        if not self.tipo_habitacion.activa:
            raise ValidationError(
                "No se puede asignar una tarifa a un tipo de habitación inactivo"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        tipo = "Nocturna" if self.es_nocturna else "Diurna"
        return f"{self.nombre} - {self.tipo_habitacion} ({tipo})"
