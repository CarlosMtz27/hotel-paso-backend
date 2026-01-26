# Define las rutas de la API para la aplicación 'caja'.

from django.urls import path
from .views import MovimientoCajaListCreateAPIView

urlpatterns = [
    # Endpoint para listar (GET) y crear (POST) movimientos de caja.
    path("movimientos/", MovimientoCajaListCreateAPIView.as_view(), name="movimientos-list-create"),
]
