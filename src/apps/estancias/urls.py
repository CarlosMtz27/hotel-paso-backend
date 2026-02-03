# Define las rutas de la API para la aplicación 'estancias'.

from django.urls import path
from .views import (
    AbrirEstanciaAPIView,
    CerrarEstanciaAPIView,
    AgregarHorasExtraAPIView,
    EstanciaListAPIView,
)

urlpatterns = [
    # Endpoint para listar todas las estancias.
    path("", EstanciaListAPIView.as_view(), name="estancias-list"),
    # Endpoint para abrir una nueva estancia.
    path("abrir/", AbrirEstanciaAPIView.as_view(), name="abrir-estancia"),
    # Endpoint para cerrar una estancia activa.
    path("cerrar/", CerrarEstanciaAPIView.as_view(), name="cerrar-estancia"),
    # Endpoint para agregar horas extra a una estancia.
    path("agregar-horas/", AgregarHorasExtraAPIView.as_view(), name="agregar-horas-extra"),
]