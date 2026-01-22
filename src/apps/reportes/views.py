from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import reporte_turnos
from .serializers import ReporteTurnoSerializer
from .services_excel import exportar_turnos_excel



class ReporteTurnosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha_desde = request.query_params.get("fecha_desde")
        fecha_hasta = request.query_params.get("fecha_hasta")

        data = reporte_turnos(
            usuario=request.user,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

        serializer = ReporteTurnoSerializer(data, many=True)
        return Response(serializer.data)

class ReporteTurnosExcelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha_desde = request.query_params.get("fecha_desde")
        fecha_hasta = request.query_params.get("fecha_hasta")

        return exportar_turnos_excel(
            usuario=request.user,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )