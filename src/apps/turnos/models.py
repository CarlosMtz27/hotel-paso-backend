from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

Usuario = settings.AUTH_USER_MODEL


class Turno(models.Model):
    """
    Representa un período de trabajo de un empleado, durante el cual se
    registran todas las operaciones monetarias. Es la unidad contable principal.
    """

    class Meta:
        permissions = [
            ("abrir_turno", "Puede abrir turno"),
            ("cerrar_turno", "Puede cerrar turno"),
            ("ver_turnos", "Puede ver turnos"),
        ]

    class TipoTurno(models.TextChoices):
        """Define si el turno es de día o de noche."""
        DIA = "DIA", "Día"
        NOCHE = "NOCHE", "Noche"

    # ==========================
    # Relaciones
    # ==========================
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,  # Un turno siempre debe tener un usuario asociado.
        related_name="turnos",
        help_text="Empleado responsable del turno."
    )

    # ==========================
    # Datos del turno
    # ==========================
    tipo_turno = models.CharField(
        max_length=10,
        choices=TipoTurno.choices,
        help_text="Indica si el turno es de día o de noche."
    )

    fecha_inicio = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se inició el turno."
    )
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora en que se cerró el turno. Nulo si está activo."
    )

    activo = models.BooleanField(
        default=True,
        help_text="Indica si el turno está actualmente en curso."
    )

    # ==========================
    # Datos económicos
    # ==========================
    sueldo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Sueldo que el empleado reporta haber tomado al cerrar el turno.",
    )

    caja_inicial = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Dinero con el que el empleado inicia la caja.",
    )

    efectivo_esperado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cálculo del efectivo que debería haber en caja al cierre.",
    )

    efectivo_reportado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Efectivo que el empleado contó físicamente al cierre.",
    )

    diferencia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Diferencia entre el efectivo esperado y el reportado.",
    )

    caja_final = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Efectivo final en caja después de tomar el sueldo (es igual al efectivo reportado).",
    )

    # ==========================
    # Métodos de dominio
    # ==========================
    def clean(self):
        """Aplica validaciones de negocio a nivel de modelo."""
        if self.caja_inicial < 0:
            raise ValidationError("La caja inicial no puede ser negativa.")

    def save(self, *args, **kwargs):
        """Asegura que las validaciones se ejecuten antes de guardar."""
        self.full_clean()
        super().save(*args, **kwargs)

    def cerrar_turno(
        self,
        *,
        efectivo_esperado,
        efectivo_reportado,
        sueldo
    ):
        """
        Método de negocio para cerrar el turno.
        Calcula los totales, actualiza el estado y guarda los cambios.
        """
        if not self.activo:
            raise ValidationError("El turno ya está cerrado.")
        
        # Las validaciones específicas del cierre ahora viven dentro de este método.
        if efectivo_reportado is None or efectivo_reportado < 0:
            raise ValidationError("El efectivo reportado no puede ser negativo.")
        
        if sueldo < 0:
            raise ValidationError("El sueldo no puede ser negativo.")

        self.efectivo_esperado = efectivo_esperado
        self.efectivo_reportado = efectivo_reportado
        self.sueldo = sueldo

        self.diferencia = self.efectivo_reportado - self.efectivo_esperado
        self.caja_final = self.efectivo_reportado

        self.fecha_fin = timezone.now()
        self.activo = False

        # Usar update_fields es más eficiente y previene efectos secundarios.
        self.save(update_fields=[
            'efectivo_esperado', 'efectivo_reportado', 'sueldo',
            'diferencia', 'caja_final', 'fecha_fin', 'activo'
        ])

    def __str__(self):
        """Representación en cadena para legibilidad."""
        estado = "Activo" if self.activo else "Cerrado"
        return f"Turno #{self.id} - {self.usuario} ({self.tipo_turno}) [{estado}]"
