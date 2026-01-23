from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Habitacion
from .serializers import HabitacionSerializer
from .services import crear_habitacion, actualizar_habitacion
from .models import TipoHabitacion
from .serializers import TipoHabitacionSerializer
from .services import crear_tipo_habitacion, actualizar_tipo_habitacion


class TipoHabitacionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipos = TipoHabitacion.objects.all()
        serializer = TipoHabitacionSerializer(tipos, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.rol != "ADMIN":
            return Response(
                {"error": "No tienes permisos"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TipoHabitacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tipo = crear_tipo_habitacion(**serializer.validated_data)

        return Response(
            TipoHabitacionSerializer(tipo).data,
            status=status.HTTP_201_CREATED
        )

    def put(self, request, pk):
        if request.user.rol != "ADMIN":
            return Response(
                {"error": "No tienes permisos"},
                status=status.HTTP_403_FORBIDDEN
            )

        tipo = TipoHabitacion.objects.get(pk=pk)

        tipo = actualizar_tipo_habitacion(
            tipo_habitacion=tipo,
            **request.data
        )

        return Response(TipoHabitacionSerializer(tipo).data)


class HabitacionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        habitaciones = Habitacion.objects.all()
        serializer = HabitacionSerializer(habitaciones, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.rol != "ADMIN":
            return Response(
                {"error": "No tienes permisos"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = HabitacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        habitacion = crear_habitacion(
            numero=serializer.validated_data["numero"],
            tipo_habitacion=serializer.validated_data["tipo_habitacion"]
        )

        return Response(
            HabitacionSerializer(habitacion).data,
            status=status.HTTP_201_CREATED
        )

    def put(self, request, pk):
        if request.user.rol != "ADMIN":
            return Response(
                {"error": "No tienes permisos"},
                status=status.HTTP_403_FORBIDDEN
            )

        habitacion = Habitacion.objects.get(pk=pk)

        habitacion = actualizar_habitacion(
            habitacion=habitacion,
            **request.data
        )

        return Response(HabitacionSerializer(habitacion).data)