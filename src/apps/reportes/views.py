from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import reporte_turnos
from .serializers import ReporteTurnoSerializer


class ReporteTurnosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = reporte_turnos(usuario=request.user)

        serializer = ReporteTurnoSerializer(data, many=True)
        return Response(serializer.data)
