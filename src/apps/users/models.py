from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMINISTRADOR =  "ADMIN","Administrador"
        EMPLEADO = "EMPLEADO", "Empleado"
        INVITADO = "INVITADO", "Invitado"

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.EMPLEADO,
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.rol})"
