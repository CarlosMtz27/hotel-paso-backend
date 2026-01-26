# Define las rutas de la API para la aplicación 'productos'.

from django.urls import path
from .views import ProductoListAPIView, ProductoDetailAPIView

urlpatterns = [
    # Ejemplo: GET, POST /api/productos/
    path('', ProductoListAPIView.as_view(), name='productos_list'),
    # Ejemplo: GET, PUT, PATCH /api/productos/1/
    path('<int:pk>/', ProductoDetailAPIView.as_view(), name='productos_detail'),
]