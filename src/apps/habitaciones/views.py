from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Imports de tus modelos y servicios
from .models import Habitacion, TipoHabitacion
from .serializers import HabitacionSerializer, TipoHabitacionSerializer
from .services import crear_habitacion, actualizar_habitacion, crear_tipo_habitacion, actualizar_tipo_habitacion

# ==========================================
#  VISTAS PARA TIPOS DE HABITACIÓN
# ==========================================

class TipoHabitacionListAPIView(APIView):
    """Maneja GET (lista) y POST (crear)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tipos = TipoHabitacion.objects.all()
        serializer = TipoHabitacionSerializer(tipos, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.rol != "ADMIN":
            return Response({"error": "No tienes permisos"}, status=status.HTTP_403_FORBIDDEN)

        serializer = TipoHabitacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Nota: Usamos ** para desempaquetar el diccionario validado
        tipo = crear_tipo_habitacion(**serializer.validated_data)
        return Response(TipoHabitacionSerializer(tipo).data, status=status.HTTP_201_CREATED)


class TipoHabitacionDetailAPIView(APIView):
    """Maneja PUT (actualizar) y GET (uno solo - opcional)"""
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if request.user.rol != "ADMIN":
            return Response({"error": "No tienes permisos"}, status=status.HTTP_403_FORBIDDEN)

        try:
            tipo = TipoHabitacion.objects.get(pk=pk)
        except TipoHabitacion.DoesNotExist:
            return Response({"error": "No encontrado"}, status=status.HTTP_404_NOT_FOUND)

        tipo = actualizar_tipo_habitacion(tipo_habitacion=tipo, **request.data)
        return Response(TipoHabitacionSerializer(tipo).data)


# ==========================================
#  VISTAS PARA HABITACIONES
# ==========================================

class HabitacionListAPIView(APIView):
    """Maneja GET (lista) y POST (crear)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        habitaciones = Habitacion.objects.all()
        serializer = HabitacionSerializer(habitaciones, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.rol != "ADMIN":
            return Response({"error": "No tienes permisos"}, status=status.HTTP_403_FORBIDDEN)

        serializer = HabitacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        
        habitacion = crear_habitacion(
            numero=serializer.validated_data["numero"],
            tipo_habitacion=serializer.validated_data["tipo_habitacion"] 
        )
        return Response(HabitacionSerializer(habitacion).data, status=status.HTTP_201_CREATED)


class HabitacionDetailAPIView(APIView):
    """Maneja PUT (actualizar)"""
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if request.user.rol != "ADMIN":
            return Response({"error": "No tienes permisos"}, status=status.HTTP_403_FORBIDDEN)

        try:
            habitacion = Habitacion.objects.get(pk=pk)
        except Habitacion.DoesNotExist:
             return Response({"error": "No encontrado"}, status=status.HTTP_404_NOT_FOUND)

        habitacion = actualizar_habitacion(habitacion=habitacion, **request.data)
        return Response(HabitacionSerializer(habitacion).data)