from django.urls import path
from .views import VistaLogin,VistaLoginInvitado

urlpatterns = [
    path("login/", VistaLogin.as_view()),
    path("login-invitado/", VistaLoginInvitado.as_view()),

]
