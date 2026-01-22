from django.db import models
from django.conf import settings
from django.utils import timezone

Usuario = settings.AUTH_USER_MODEL


class Turno(models.Model):

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["activo"],
                condition=models.Q(activo=True),
                name="unique_turno_activo"
            )
        ]
    class TipoTurno(models.TextChoices):
        DIA = "DIA", "Día"
        NOCHE = "NOCHE", "Noche"

    # ==========================
    # Relaciones
    # ==========================
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="turnos",
    )

    # ==========================
    # Datos del turno
    # ==========================
    tipo_turno = models.CharField(
        max_length=10,
        choices=TipoTurno.choices,
    )

    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    activo = models.BooleanField(default=True)

    # ==========================
    # Datos económicos
    # ==========================
    sueldo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Sueldo que el empleado toma al cerrar el turno",
    )

    caja_inicial = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Dinero con el que inicia la caja",
    )

    efectivo_esperado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Efectivo que debería haber en caja",
    )

    efectivo_reportado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Efectivo que el empleado dice haber contado",
    )

    diferencia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Diferencia entre efectivo esperado y reportado",
    )

    caja_final = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Efectivo final reportado en caja",
    )

    # ==========================
    # Métodos de dominio
    # ==========================
    def cerrar_turno(
        self,
        *,
        efectivo_esperado,
        efectivo_reportado,
        sueldo
    ):
        """
        Cierra el turno y deja registro contable completo.
        """
        self.efectivo_esperado = efectivo_esperado
        self.efectivo_reportado = efectivo_reportado
        self.sueldo = sueldo

        self.diferencia = efectivo_reportado - efectivo_esperado
        self.caja_final = efectivo_reportado

        self.fecha_fin = timezone.now()
        self.activo = False

        self.save()

    def __str__(self):
        estado = "Activo" if self.activo else "Cerrado"
        return f"Turno {self.id} - {self.usuario} ({estado})"
