# Define las rutas de la API para la aplicación 'users'.

from django.urls import path
from .views import UserRegistrationAPIView, VistaLoginInvitado, LogoutAPIView, MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Rutas de autenticación JWT
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    # Rutas de gestión de usuarios
    # Endpoint para que un admin registre nuevos usuarios.
    path("register/", UserRegistrationAPIView.as_view(), name="register"),
    # Endpoint para el login de invitados.
    path("login-invitado/", VistaLoginInvitado.as_view(), name="login_invitado"),
]
