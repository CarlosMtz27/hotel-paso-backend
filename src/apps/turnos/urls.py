# Define las rutas de la API para la aplicación 'turnos'.

from django.urls import path
from .views import IniciarTurnoView, CerrarTurnoAPIView, TurnoListAPIView


urlpatterns = [
    # Endpoint para que los administradores listen todos los turnos.
    path("", TurnoListAPIView.as_view(), name="turnos-list"),
    # Endpoint para que un empleado inicie su turno.
    path("iniciar/", IniciarTurnoView.as_view(), name="iniciar-turno"),
    # Endpoint para que un empleado cierre su turno.
    path("cerrar/", CerrarTurnoAPIView.as_view(), name="cerrar-turno"),

]
