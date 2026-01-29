from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Producto
from apps.core.permissions import IsAdminUser
from .serializers import ProductoSerializer


class ProductoListAPIView(generics.ListCreateAPIView):
    """
    Maneja GET para listar todos los productos y POST para crear uno nuevo.
    - `GET`: Cualquier usuario autenticado puede listar los productos.
    - `POST`: Solo los administradores pueden crear productos.
    """
    queryset = Producto.objects.all().order_by('nombre')
    serializer_class = ProductoSerializer
    filterset_fields = ['activo']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]


class ProductoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Maneja GET (detalle), PUT/PATCH (actualizar) y DELETE para un producto.
    - `GET`: Cualquier usuario autenticado puede ver el detalle.
    - `PUT`/`PATCH`/`DELETE`: Solo los administradores pueden actualizar o eliminar.
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]
