from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from .models import Producto
from apps.core.permissions import IsAdminUser
from .serializers import ProductoSerializer
from .services import crear_producto, actualizar_producto


class ProductoListAPIView(APIView):
    """
    Maneja GET para listar todos los productos y POST para crear uno nuevo.
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request):
        productos = Producto.objects.all().order_by('nombre')
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            producto = crear_producto(**serializer.validated_data)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ProductoSerializer(producto).data, status=status.HTTP_201_CREATED)


class ProductoDetailAPIView(APIView):
    """
    Maneja GET (detalle) y PUT (actualizar) para un producto.
    """
    def get_permissions(self):
        if self.request.method == 'PUT':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request, pk):
        try:
            producto = Producto.objects.get(pk=pk)
            serializer = ProductoSerializer(producto)
            return Response(serializer.data)
        except Producto.DoesNotExist:
            return Response({"error": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            producto = Producto.objects.get(pk=pk)
        except Producto.DoesNotExist:
            return Response({"error": "Producto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        try:
            producto_actualizado = actualizar_producto(producto=producto, **request.data)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductoSerializer(producto_actualizado)
        return Response(serializer.data)
