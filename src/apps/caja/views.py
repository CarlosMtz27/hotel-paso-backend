from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class MovimientoCajaCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(
            {"mensaje": "Movimiento creado"},
            status=status.HTTP_201_CREATED
        )
