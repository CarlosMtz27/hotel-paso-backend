from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from .models import MovimientoCaja
from .serializers import MovimientoCajaSerializer, CrearVentaProductoSerializer
from .services import vender_producto
from apps.core.permissions import IsAdminUser, IsEmpleado, IsOnlyInvitado
from apps.turnos.models import Turno


class MovimientoCajaListCreateAPIView(generics.ListCreateAPIView):
    """
    - GET: Lista todos los movimientos de caja. (Cualquier usuario autenticado)
    - POST: Registra la venta de un producto. (Admins, Empleados e Invitados)
    """
    queryset = MovimientoCaja.objects.select_related('turno', 'estancia', 'producto').order_by('-fecha')
    filterset_fields = ['turno', 'tipo', 'metodo_pago', 'estancia']

    def get_serializer_class(self):
        """
        Determina qué serializador usar según el método de la petición.
        - POST (crear): Usa un serializador específico para validar la entrada.
        - GET (listar): Usa un serializador detallado para mostrar la salida.
        """
        if self.request.method == 'POST':
            return CrearVentaProductoSerializer
        return MovimientoCajaSerializer

    def get_permissions(self):
        """
        Define permisos específicos por acción.
        - GET (listar): Cualquier usuario autenticado puede ver el historial de caja.
        - POST (crear): Administradores, Empleados e Invitados pueden registrar una venta.
        """
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        
        # Para POST, se permite a cualquier usuario con rol (Admin, Empleado, Invitado).
        # IsEmpleado cubre a Admins y Empleados. IsOnlyInvitado cubre a los invitados.
        return [IsAuthenticated(), (IsEmpleado | IsOnlyInvitado)()]

    def create(self, request, *args, **kwargs):
        """
        Procesa la petición POST para registrar una nueva venta de producto.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Regla de negocio: Toda venta debe ocurrir dentro de un turno activo.
            turno_activo = Turno.objects.get(activo=True)
        except Turno.DoesNotExist:
            return Response({"error": "No hay un turno activo para registrar la venta."}, status=status.HTTP_400_BAD_REQUEST)

        # Mapea los nombres de campo del serializador a los que espera la función de servicio.
        # Esto desacopla la API de la lógica de negocio interna.
        service_data = serializer.validated_data.copy()
        service_data['producto'] = service_data.pop('producto_id')
        if 'estancia_id' in service_data:
            service_data['estancia'] = service_data.pop('estancia_id')

        try:
            # Delega la lógica de creación a la capa de servicios.
            movimiento = vender_producto(
                turno=turno_activo,
                **service_data
            )
            # Devuelve el objeto completo del movimiento recién creado.
            response_serializer = MovimientoCajaSerializer(movimiento)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
