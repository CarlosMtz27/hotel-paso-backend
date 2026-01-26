from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from apps.turnos.models import Turno
from apps.estancias.services import abrir_estancia
from apps.estancias.services import cerrar_estancia
from apps.estancias.services import agregar_horas_extra
from apps.estancias.serializers import (
    AbrirEstanciaSerializer,
    CerrarEstanciaSerializer,
    AgregarHorasExtraSerializer,
    EstanciaDetalleSerializer,
)


class ActiveTurnoRequiredMixin:
    """
    Mixin que verifica la existencia de un turno activo antes de procesar la petición.
    Si no hay un turno activo, corta el flujo y devuelve un error 400.
    """
    def dispatch(self, request, *args, **kwargs):
        try:
            self.turno_activo = Turno.objects.get(activo=True)
        except Turno.DoesNotExist:
            return Response({"error": "No hay un turno activo"}, status=status.HTTP_400_BAD_REQUEST)
        return super().dispatch(request, *args, **kwargs)

class AbrirEstanciaAPIView(ActiveTurnoRequiredMixin, APIView):
    """Endpoint para abrir una nueva estancia."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Maneja la petición POST para crear una estancia.
        1. Valida los datos de entrada.
        2. Verifica que haya un turno activo.
        3. Llama al servicio de negocio `abrir_estancia`.
        4. Devuelve el objeto de la estancia recién creada.
        """
        serializer = AbrirEstanciaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Delega la creación y la lógica de negocio a la capa de servicios.
            estancia = abrir_estancia(
                habitacion=serializer.validated_data["habitacion_id"],
                tarifa=serializer.validated_data["tarifa_id"],
                metodo_pago=serializer.validated_data["metodo_pago"],
                # El mixin ya ha cargado el turno activo en self.turno_activo
                turno=self.turno_activo,
            )
        except ValidationError as e:
            # Captura errores de validación de la capa de servicios o modelos.
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Devuelve el estado completo de la estancia creada.
        return Response(EstanciaDetalleSerializer(estancia).data, status=status.HTTP_201_CREATED)

class CerrarEstanciaAPIView(ActiveTurnoRequiredMixin, APIView):
    """Endpoint para cerrar una estancia activa."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Maneja la petición POST para cerrar una estancia.
        """
        serializer = CerrarEstanciaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            estancia = cerrar_estancia(
                estancia=serializer.validated_data["estancia_id"],
                turno=self.turno_activo,
                hora_salida_real=serializer.validated_data.get(
                    "hora_salida_real"
                ),
            )
        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Devuelve el estado completo de la estancia cerrada.
        return Response(EstanciaDetalleSerializer(estancia).data, status=status.HTTP_200_OK)

class AgregarHorasExtraAPIView(ActiveTurnoRequiredMixin, APIView):
    """Endpoint para agregar horas extra a una estancia."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Maneja la petición POST para agregar horas y registrar el cobro.
        """
        serializer = AgregarHorasExtraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # El servicio ahora devuelve la estancia actualizada.
            estancia_actualizada = agregar_horas_extra(
                estancia=serializer.validated_data["estancia_id"],
                turno=self.turno_activo,
                cantidad_horas=serializer.validated_data["cantidad_horas"],
                precio_hora=serializer.validated_data["precio_hora"],
                metodo_pago=serializer.validated_data["metodo_pago"],
            )
        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Devuelve el estado completo y actualizado de la estancia.
        return Response(EstanciaDetalleSerializer(estancia_actualizada).data, status=status.HTTP_200_OK)
