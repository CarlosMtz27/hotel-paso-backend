from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

# Imports de tus modelos y servicios
from .models import Habitacion, TipoHabitacion
from .serializers import HabitacionSerializer, TipoHabitacionSerializer
from apps.core.permissions import IsAdminUser

# ==========================================
#  VISTAS PARA TIPOS DE HABITACIÓN
# ==========================================

class TipoHabitacionListAPIView(generics.ListCreateAPIView):
    """
    Maneja las peticiones para la lista de Tipos de Habitación.
    - GET: Devuelve una lista de todos los tipos de habitación.
    - POST: Permite a un administrador crear un nuevo tipo de habitación.
    """
    queryset = TipoHabitacion.objects.all().order_by('nombre')
    serializer_class = TipoHabitacionSerializer
    filterset_fields = ['activo']

    def get_permissions(self):
        """Define permisos específicos por acción."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]


class TipoHabitacionDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    Maneja peticiones para un Tipo de Habitación específico.
    - GET: Devuelve los detalles de un tipo de habitación.
    - PUT/PATCH: Permite a un administrador actualizar un tipo de habitación.
    """
    queryset = TipoHabitacion.objects.all()
    serializer_class = TipoHabitacionSerializer

    def get_permissions(self):
        """Define permisos específicos por acción."""
        if self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]


# ==========================================
#  VISTAS PARA HABITACIONES
# ==========================================

class HabitacionListAPIView(generics.ListCreateAPIView):
    """
    Maneja las peticiones para la lista de Habitaciones.
    - GET: Devuelve una lista de todas las habitaciones.
    - POST: Permite a un administrador crear una nueva habitación.
    """
    queryset = Habitacion.objects.select_related('tipo').order_by('numero')
    serializer_class = HabitacionSerializer
    filterset_fields = ['activa', 'tipo']

    def get_permissions(self):
        """Define permisos específicos por acción."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]


class HabitacionDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    Maneja peticiones para una Habitación específica.
    - GET: Devuelve los detalles de una habitación.
    - PUT/PATCH: Permite a un administrador actualizar una habitación.
    """
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer

    def get_permissions(self):
        """Define permisos específicos por acción."""
        if self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]