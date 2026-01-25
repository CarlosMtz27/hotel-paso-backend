from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

# Imports de tus modelos y servicios
from .models import Habitacion, TipoHabitacion
from .serializers import HabitacionSerializer, TipoHabitacionSerializer
from .services import crear_habitacion, actualizar_habitacion, crear_tipo_habitacion, actualizar_tipo_habitacion
from apps.core.permissions import IsAdminUser

# ==========================================
#  VISTAS PARA TIPOS DE HABITACIÓN
# ==========================================

class TipoHabitacionListAPIView(APIView):
    """Maneja GET (lista) y POST (crear)"""
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request):
        tipos = TipoHabitacion.objects.filter(activo=True).order_by('nombre')
        serializer = TipoHabitacionSerializer(tipos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TipoHabitacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            tipo = crear_tipo_habitacion(**serializer.validated_data)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TipoHabitacionSerializer(tipo).data, status=status.HTTP_201_CREATED)


class TipoHabitacionDetailAPIView(APIView):
    """Maneja PUT (actualizar) y GET (uno solo - opcional)"""
    def get_permissions(self):
        if self.request.method == 'PUT':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request, pk):
        try:
            tipo = TipoHabitacion.objects.get(pk=pk)
            serializer = TipoHabitacionSerializer(tipo)
            return Response(serializer.data)
        except TipoHabitacion.DoesNotExist:
            return Response({"error": "No encontrado"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            tipo = TipoHabitacion.objects.get(pk=pk)
        except TipoHabitacion.DoesNotExist:
            return Response({"error": "No encontrado"}, status=status.HTTP_404_NOT_FOUND)

        try:
            tipo = actualizar_tipo_habitacion(tipo_habitacion=tipo, **request.data)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TipoHabitacionSerializer(tipo).data)


# ==========================================
#  VISTAS PARA HABITACIONES
# ==========================================

class HabitacionListAPIView(APIView):
    """Maneja GET (lista) y POST (crear)"""
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request):
        # Filtramos para mostrar solo habitaciones activas y de tipos activos
        habitaciones = Habitacion.objects.filter(activa=True, tipo__activo=True).select_related('tipo').order_by('numero')
        serializer = HabitacionSerializer(habitaciones, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = HabitacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            habitacion = crear_habitacion(
                numero=serializer.validated_data["numero"],
                tipo=serializer.validated_data["tipo"]
            )
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(HabitacionSerializer(habitacion).data, status=status.HTTP_201_CREATED)


class HabitacionDetailAPIView(APIView):
    """Maneja GET (detalle) y PUT (actualizar)"""
    def get_permissions(self):
        if self.request.method == 'PUT':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request, pk):
        try:
            habitacion = Habitacion.objects.get(pk=pk)
            serializer = HabitacionSerializer(habitacion)
            return Response(serializer.data)
        except Habitacion.DoesNotExist:
             return Response({"error": "Habitación no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            habitacion = Habitacion.objects.get(pk=pk)
        except Habitacion.DoesNotExist:
             return Response({"error": "Habitación no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        try:
            habitacion = actualizar_habitacion(habitacion=habitacion, **request.data)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(HabitacionSerializer(habitacion).data)