# Define las rutas de la API para la aplicación 'tarifas'.

from django.urls import path
from .views import TarifaListCreateAPIView, TarifaDetailAPIView

urlpatterns = [
    # Ejemplo: GET, POST /api/tarifas/
    path('', TarifaListCreateAPIView.as_view(), name='tarifas_list_create'),
    # Ejemplo: GET, PUT, PATCH, DELETE /api/tarifas/1/
    path(
        '<int:pk>/',
        TarifaDetailAPIView.as_view(),
        name='tarifas_detail'
    ),
]