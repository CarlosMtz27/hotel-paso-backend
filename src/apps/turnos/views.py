from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound

from .serializers import InicioTurnoSerializer, CerrarTurnoSerializer, TurnoListSerializer, TurnoResumenSerializer
from .services import iniciar_turno, cerrar_turno_service
from .models import Turno
from django.core.exceptions import ValidationError # Importar ValidationError de Django
from apps.core.permissions import IsAdminUser, IsEmpleado, IsOnlyInvitado


class TurnoListAPIView(generics.ListAPIView):
    """
    Endpoint de solo lectura para listar todos los turnos (históricos y activos).
    - `GET`: Solo los administradores pueden ver la lista de turnos.
    - Permite filtrar por: `usuario`, `activo`, `tipo_turno`.
    """
    # `select_related` optimiza la consulta para evitar N+1 queries al acceder a `usuario`.
    queryset = Turno.objects.select_related('usuario').order_by('-fecha_inicio')
    serializer_class = TurnoListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = {
        'usuario': ['exact'],
        'activo': ['exact'],
        'tipo_turno': ['exact'],
    }


@method_decorator(csrf_exempt, name="dispatch")
class IniciarTurnoView(APIView):
    """Endpoint para iniciar un nuevo turno."""
    # Permite a Admins, Empleados e Invitados iniciar un turno.
    permission_classes = [IsAuthenticated, (IsEmpleado | IsOnlyInvitado)]

    def post(self, request):
        """
        Maneja la petición POST para crear un turno.
        1. Valida los datos de entrada (tipo de turno, caja inicial).
        2. Llama al servicio de negocio `iniciar_turno`.
        3. Devuelve el objeto completo del turno recién creado.
        """
        serializer = InicioTurnoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Delega la lógica de creación a la capa de servicios.
            turno = iniciar_turno(
                usuario=request.user,
                **serializer.validated_data
            )
        except ValidationError as e:
            # Captura errores de negocio (ej. ya hay un turno activo).
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Devuelve el estado completo del turno creado.
        response_serializer = TurnoListSerializer(turno)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CerrarTurnoAPIView(APIView):
    """Endpoint para cerrar el turno activo."""
    # Permite a Admins, Empleados e Invitados cerrar un turno.
    permission_classes = [IsAuthenticated, (IsEmpleado | IsOnlyInvitado)]

    def post(self, request):
        """
        Maneja la petición POST para cerrar un turno.
        1. Valida los datos de entrada (efectivo reportado, sueldo).
        2. Llama al servicio de negocio `cerrar_turno_service`.
        3. Devuelve un resumen completo del turno cerrado.
        """
        serializer = CerrarTurnoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Delega la lógica de cierre a la capa de servicios.
            turno, sin_ingresos = cerrar_turno_service(
                usuario=request.user,
                efectivo_reportado=serializer.validated_data["efectivo_reportado"],
                sueldo=serializer.validated_data["sueldo"],
            )
        except ValidationError as e:
            # Captura errores de negocio (ej. no es el dueño del turno).
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Serializa el turno cerrado usando el serializador de resumen para una respuesta estructurada.
        resumen_serializer = TurnoResumenSerializer(turno)

        return Response(
            {
                "mensaje": "Turno cerrado correctamente",
                "resumen": resumen_serializer.data,
            },
            status=status.HTTP_200_OK
        )


class TurnoActivoAPIView(APIView):
    """
    Endpoint para obtener el turno activo.
    - `GET`: Devuelve el turno activo si existe, de lo contrario 404.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Busca y devuelve el turno activo.
        """
        # Buscamos todos los turnos activos
        turnos_activos = Turno.objects.filter(activo=True).select_related('usuario')

        if not turnos_activos.exists():
            raise NotFound(detail="No hay un turno activo.")

        # Prioridad: Devolver el turno del usuario actual si tiene uno
        turno_usuario = next((t for t in turnos_activos if t.usuario == request.user), None)

        if turno_usuario:
            serializer = TurnoListSerializer(turno_usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Si el usuario no tiene turno, pero hay otros activos, devolvemos el primero.
        serializer = TurnoListSerializer(turnos_activos.first())
        return Response(serializer.data, status=status.HTTP_200_OK)

