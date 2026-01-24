from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from apps.turnos.models import Turno
from apps.estancias.services import abrir_estancia
from apps.estancias.serializers import (
    AbrirEstanciaSerializer,
    EstanciaDetalleSerializer,
)
from apps.estancias.services import cerrar_estancia
from apps.estancias.serializers import CerrarEstanciaSerializer
from apps.estancias.services import agregar_horas_extra
from apps.estancias.serializers import AgregarHorasExtraSerializer
from apps.estancias.services import agregar_horas_extra
from apps.estancias.serializers import AgregarHorasExtraSerializer



class AbrirEstanciaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AbrirEstanciaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            turno = Turno.objects.get(activo=True)
        except Turno.DoesNotExist:
            return Response(
                {"error": "No hay un turno activo"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            estancia = abrir_estancia(
                habitacion=serializer.validated_data["habitacion"],
                tarifa=serializer.validated_data["tarifa"],
                metodo_pago=serializer.validated_data["metodo_pago"],
                turno=turno,
            )
        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "mensaje": "Estancia abierta correctamente",
                "estancia": EstanciaDetalleSerializer(estancia).data,
            },
            status=status.HTTP_201_CREATED,
        )

class CerrarEstanciaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CerrarEstanciaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            turno = Turno.objects.get(activo=True)
        except Turno.DoesNotExist:
            return Response(
                {"error": "No hay un turno activo"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            estancia = cerrar_estancia(
                estancia=serializer.validated_data["estancia"],
                turno=turno,
                hora_salida_real=serializer.validated_data.get(
                    "hora_salida_real"
                ),
            )
        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "mensaje": "Estancia cerrada correctamente",
                "estancia": EstanciaDetalleSerializer(estancia).data,
            },
            status=status.HTTP_200_OK,
        )

class AgregarHorasExtraAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AgregarHorasExtraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            turno = Turno.objects.get(activo=True)
        except Turno.DoesNotExist:
            return Response(
                {"error": "No hay un turno activo"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            agregar_horas_extra(
                estancia=serializer.validated_data["estancia"],
                turno=turno,
                cantidad_horas=serializer.validated_data["cantidad_horas"],
                precio_hora=serializer.validated_data["precio_hora"],
                metodo_pago=serializer.validated_data["metodo_pago"],
            )
        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "mensaje": "Horas extra agregadas correctamente",
                "estancia": EstanciaDetalleSerializer(
                    serializer.validated_data["estancia"]
                ).data,
            },
            status=status.HTTP_200_OK,
        )
