# Define las rutas de la API para la aplicación 'users'.

from django.urls import path
from .views import UserRegistrationAPIView, VistaLoginInvitado, LogoutAPIView

urlpatterns = [
    # El login de admin/empleado se maneja con JWT en /api/token/
    # Endpoint para que un admin registre nuevos usuarios.
    path("register/", UserRegistrationAPIView.as_view(), name="register"),
    # Endpoint para el login de invitados.
    path("login-invitado/", VistaLoginInvitado.as_view(), name="login_invitado"),
    # Endpoint para el logout (invalidar refresh token).
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
