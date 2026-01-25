from django.urls import path
from .views import UserRegistrationAPIView, VistaLoginInvitado, LogoutAPIView

urlpatterns = [
    # El login de admin/empleado se maneja con JWT en /api/auth/login/
    path("register/", UserRegistrationAPIView.as_view(), name="register"),
    path("login-invitado/", VistaLoginInvitado.as_view(), name="login_invitado"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
