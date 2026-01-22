from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import InicioTurnoSerializer
from .services import iniciar_turno
from .serializers import CierreTurnoSerializer
from .services import cerrar_turno


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


class CerrarTurnoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CierreTurnoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        turno = cerrar_turno(
            usuario=request.user,
            **serializer.validated_data
        )

        return Response({
            "mensaje": "Turno cerrado correctamente",
            "efectivo_esperado": turno.efectivo_esperado,
            "efectivo_reportado": turno.efectivo_reportado,
            "diferencia": turno.diferencia,
        })
