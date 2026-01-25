from django.urls import path
from .views import ProductoListAPIView, ProductoDetailAPIView

urlpatterns = [
    # http://localhost:8000/api/productos/
    path('', ProductoListAPIView.as_view(), name='productos_list'),
    # http://localhost:8000/api/productos/1/
    path('<int:pk>/', ProductoDetailAPIView.as_view(), name='productos_detail'),
]