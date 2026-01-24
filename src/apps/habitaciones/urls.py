from django.urls import path
from .views import (
    TipoHabitacionListAPIView,
    TipoHabitacionDetailAPIView,
    HabitacionListAPIView,
    HabitacionDetailAPIView
)

urlpatterns = [
    # --- TIPOS DE HABITACIÓN ---
    # http://localhost:8000/api/habitaciones/tipos/
    path('tipos/', TipoHabitacionListAPIView.as_view(), name='tipos_list'),

    # http://localhost:8000/api/habitaciones/tipos/1/
    path('tipos/<int:pk>/', TipoHabitacionDetailAPIView.as_view(), name='tipos_detail'),

    # --- HABITACIONES ---
    # http://localhost:8000/api/habitaciones/
    path('', HabitacionListAPIView.as_view(), name='habitaciones_list'),

    # http://localhost:8000/api/habitaciones/101/
    # Si usaste 'numero' como Primary Key manual, está bien. Si es ID autoincremental, es el ID.
    path('<int:pk>/', HabitacionDetailAPIView.as_view(), name='habitaciones_detail'),
]