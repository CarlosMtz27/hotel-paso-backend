# Define las rutas de la API para la aplicación 'users'.

from django.urls import path
from .views import (
    CurrentUserAPIView, LogoutAPIView, MyTokenObtainPairView,
    UserRegistrationAPIView, VistaLoginInvitado,
    UserListAPIView, UserDetailAPIView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Rutas de autenticación JWT
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("user/", CurrentUserAPIView.as_view(), name="current_user"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    # Rutas de gestión de usuarios
    # Endpoint para que un admin registre nuevos usuarios.
    path("register/", UserRegistrationAPIView.as_view(), name="register"),
    # Endpoint para el login de invitados.
    path("login-invitado/", VistaLoginInvitado.as_view(), name="login_invitado"),
    # Endpoints de gestión de usuarios (Admin)
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailAPIView.as_view(), name="user-detail"),
]
