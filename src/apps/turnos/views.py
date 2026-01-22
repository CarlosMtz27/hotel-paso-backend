from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import InicioTurnoSerializer, CerrarTurnoSerializer
from .services import iniciar_turno
from .models import Turno
from rest_framework import status
from apps.turnos.services import cerrar_turno_service,obtener_resumen_turno


@method_decorator(csrf_exempt, name="dispatch")
class IniciarTurnoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InicioTurnoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        turno = iniciar_turno(
            usuario=request.user,
            **serializer.validated_data
        )

        return Response({
            "id": turno.id,
            "mensaje": "Turno iniciado correctamente",
            "fecha_inicio": turno.fecha_inicio,
        })


class CerrarTurnoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CerrarTurnoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            turno = Turno.objects.get(activo=True)
        except Turno.DoesNotExist:
            return Response(
                {"error": "No hay un turno activo"},
                status=status.HTTP_400_BAD_REQUEST
            )

        turno, sin_ingresos = cerrar_turno_service(
            turno=turno,
            efectivo_reportado=serializer.validated_data["efectivo_reportado"],
            sueldo=serializer.validated_data["sueldo"],
        )

        resumen = obtener_resumen_turno(turno=turno)

        return Response(
            {
                "mensaje": "Turno cerrado correctamente",
                "resumen": resumen,
                "sin_ingresos": sin_ingresos,
            },
        status=status.HTTP_200_OK
        )