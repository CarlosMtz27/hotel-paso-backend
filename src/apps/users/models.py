from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado que extiende el `AbstractUser` de Django.
    Añade un campo `rol` para manejar los permisos a nivel de aplicación y
    un campo `activo` para desactivar usuarios sin borrarlos.
    """
    class Rol(models.TextChoices):
        """Define los roles disponibles en el sistema."""
        ADMINISTRADOR = "ADMIN", "Administrador"
        EMPLEADO = "EMPLEADO", "Empleado"
        INVITADO = "INVITADO", "Invitado"

    # Rol del sistema (fuente de verdad para permisos)
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.EMPLEADO,
        help_text="Rol del usuario dentro del sistema, determina sus permisos."
    )

    # Permite desactivar usuarios sin borrarlos
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el usuario puede iniciar sesión. Desmarcar en lugar de borrar."
    )

    def es_admin(self):
        """Método de conveniencia para verificar si el usuario es administrador."""
        return self.rol == self.Rol.ADMINISTRADOR

    def es_empleado(self):
        """Método de conveniencia para verificar si el usuario es empleado."""
        return self.rol == self.Rol.EMPLEADO

    def __str__(self):
        """Representación en cadena para legibilidad."""
        nombre = self.get_full_name()
        return f"{nombre or self.username} ({self.rol})"
