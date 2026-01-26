from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Tarifa
from .serializers import TarifaSerializer
from apps.core.permissions import IsAdminUser


class TarifaListCreateAPIView(generics.ListCreateAPIView):
    """
    Maneja GET para listar todas las tarifas y POST para crear una nueva.
    - `GET`: Cualquier usuario autenticado puede listar las tarifas.
    - `POST`: Solo los administradores pueden crear tarifas.
    """
    # `select_related` optimiza la consulta para evitar N+1 queries al acceder a `tipo_habitacion`.
    queryset = Tarifa.objects.select_related('tipo_habitacion').order_by('tipo_habitacion', 'precio')
    serializer_class = TarifaSerializer
    # Habilita el filtrado por estos campos a través de query params (ej. /api/tarifas/?activa=true).
    filterset_fields = [
        'activa',
        'es_nocturna',
        'tipo_habitacion'
    ]

    def get_permissions(self):
        """Define permisos específicos por acción."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]


class TarifaDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Maneja GET (detalle), PUT, PATCH (actualizar) y DELETE para una tarifa.
    - `GET`: Cualquier usuario autenticado puede ver el detalle.
    - `PUT`/`PATCH`/`DELETE`: Solo los administradores pueden modificar o eliminar.
    """
    queryset = Tarifa.objects.all()
    serializer_class = TarifaSerializer

    def get_permissions(self):
        """Define permisos específicos por acción."""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]
