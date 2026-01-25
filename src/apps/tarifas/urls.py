from django.urls import path
from .views import TarifaListCreateAPIView, TarifaDetailAPIView

urlpatterns = [
    path('', TarifaListCreateAPIView.as_view(), name='tarifas_list_create'),
    path(
        '<int:pk>/',
        TarifaDetailAPIView.as_view(),
        name='tarifas_detail'
    ),
]