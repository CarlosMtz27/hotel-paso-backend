from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario


def login_invitado_service(*, nombre: str):
    """
    Servicio de negocio para manejar el login de un invitado.
    1. Crea un usuario 'INVITADO' con un nombre de usuario único.
    2. Genera tokens JWT para este usuario.
    3. Devuelve el usuario y los tokens.
    """
    # Creamos un nombre de usuario único para evitar colisiones en la base de datos.
    username = f"invitado_{nombre.lower().replace(' ', '_')}_{Usuario.objects.count()}"

    usuario = Usuario.objects.create(
        username=username,
        first_name=nombre,
        rol=Usuario.Rol.INVITADO,
        password=make_password(None),  # Los invitados no tienen contraseña para iniciar sesión.
    )

    # Generamos tokens JWT para el nuevo usuario invitado
    refresh = RefreshToken.for_user(usuario)
    tokens = {"refresh": str(refresh), "access": str(refresh.access_token)}

    return usuario, tokens