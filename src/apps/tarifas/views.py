from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Tarifa
from .serializers import TarifaSerializer
from .services import crear_tarifa, actualizar_tarifa


class TarifaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tarifas = Tarifa.objects.all()
        serializer = TarifaSerializer(tarifas, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.rol != "ADMIN":
            return Response(
                {"error": "No tienes permisos"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TarifaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tarifa = crear_tarifa(**serializer.validated_data)

        return Response(
            TarifaSerializer(tarifa).data,
            status=status.HTTP_201_CREATED
        )

    def put(self, request, pk):
        if request.user.rol != "ADMIN":
            return Response(
                {"error": "No tienes permisos"},
                status=status.HTTP_403_FORBIDDEN
            )

        tarifa = Tarifa.objects.get(pk=pk)

        tarifa = actualizar_tarifa(
            tarifa=tarifa,
            **request.data
        )

        return Response(TarifaSerializer(tarifa).data)
