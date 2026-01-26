# Define las rutas de la API para la aplicación 'habitaciones'.

from django.urls import path
from .views import (
    TipoHabitacionListAPIView,
    TipoHabitacionDetailAPIView,
    HabitacionListAPIView,
    HabitacionDetailAPIView
)

urlpatterns = [
    # --- TIPOS DE HABITACIÓN ---
    # Ejemplo: GET, POST /api/habitaciones/tipos/
    path('tipos/', TipoHabitacionListAPIView.as_view(), name='tipos_list'),

    # Ejemplo: GET, PUT /api/habitaciones/tipos/1/
    path('tipos/<int:pk>/', TipoHabitacionDetailAPIView.as_view(), name='tipos_detail'),

    # --- HABITACIONES ---
    # Ejemplo: GET, POST /api/habitaciones/
    path('', HabitacionListAPIView.as_view(), name='habitaciones_list'),

    # Ejemplo: GET, PUT /api/habitaciones/1/
    path('<int:pk>/', HabitacionDetailAPIView.as_view(), name='habitaciones_detail'),
]