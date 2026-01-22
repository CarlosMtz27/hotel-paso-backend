from django.urls import path
from .views import MovimientoCajaCreateAPIView

urlpatterns = [
    path("movimientos/", MovimientoCajaCreateAPIView.as_view()),
]
