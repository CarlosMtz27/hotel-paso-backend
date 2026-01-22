from django.urls import path
from .views import IniciarTurnoView
from .views import CerrarTurnoAPIView


urlpatterns = [
    path("iniciar/", IniciarTurnoView.as_view()),
    path("cerrar/", CerrarTurnoAPIView.as_view(), name="cerrar-turno"),

]
