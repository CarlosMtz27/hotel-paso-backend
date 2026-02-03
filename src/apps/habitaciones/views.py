from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

# Imports de tus modelos y servicios
from .models import Habitacion, TipoHabitacion
from .serializers import HabitacionSerializer, TipoHabitacionSerializer
from apps.core.permissions import IsAdminUser, IsEmpleado, IsOnlyInvitado

#  VISTAS PARA TIPOS DE HABITACIÓN

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


class TipoHabitacionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Maneja peticiones para un Tipo de Habitación específico.
    - GET: Devuelve los detalles de un tipo de habitación.
    - PUT/PATCH: Permite a un administrador actualizar un tipo de habitación.
    - DELETE: Permite a un administrador eliminar un tipo de habitación.
    """
    queryset = TipoHabitacion.objects.all()
    serializer_class = TipoHabitacionSerializer

    def get_permissions(self):
        """Define permisos específicos por acción."""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]


class MarcarHabitacionDisponibleAPIView(APIView):
    """
    Endpoint para que un empleado o invitado marque una habitación como 'Disponible'.
    Típicamente se usa para cambiar el estado de 'En Limpieza' a 'Disponible'.
    """
    permission_classes = [IsAuthenticated, (IsEmpleado | IsOnlyInvitado)]
    serializer_class = HabitacionSerializer

    def post(self, request, pk=None):
        """
        Cambia el estado de la habitación especificada a 'DISPONIBLE'.
        """
        try:
            habitacion = Habitacion.objects.get(pk=pk)
        except Habitacion.DoesNotExist:
            return Response(
                {"error": "La habitación no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Regla de negocio: Solo permitir el cambio si la habitación está en limpieza o mantenimiento.
        if habitacion.estado not in [Habitacion.Estado.LIMPIEZA, Habitacion.Estado.MANTENIMIENTO]:
            return Response(
                {"error": f"No se puede marcar como disponible una habitación que está '{habitacion.get_estado_display()}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        habitacion.estado = Habitacion.Estado.DISPONIBLE
        habitacion.save(update_fields=['estado'])

        serializer = self.serializer_class(habitacion)
        return Response(serializer.data, status=status.HTTP_200_OK)


#  VISTAS PARA HABITACIONES

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


class HabitacionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Maneja peticiones para una Habitación específica.
    - GET: Devuelve los detalles de una habitación.
    - PUT/PATCH: Permite a un administrador actualizar una habitación.
    - DELETE: Permite a un administrador eliminar una habitación.
    """
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer

    def get_permissions(self):
        """Define permisos específicos por acción."""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]