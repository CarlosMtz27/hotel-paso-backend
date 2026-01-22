from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import reporte_turnos
from .serializers import ReporteTurnoSerializer
from .services_excel import exportar_turnos_excel
from django.http import FileResponse
from .services_pdf import generar_pdf_turnos
from .services_resumen import resumen_diario
from .services_empleados import reporte_por_empleado



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
    

class ReporteTurnosPDFAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha_desde = request.query_params.get("fecha_desde")
        fecha_hasta = request.query_params.get("fecha_hasta")

        buffer = generar_pdf_turnos(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )

        return FileResponse(
            buffer,
            as_attachment=True,
            filename="reporte_turnos.pdf",
            content_type="application/pdf"
        )
    
class ResumenDiarioAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha = request.query_params.get("fecha")
        resumen = resumen_diario(fecha)
        return Response(resumen)
    

class ReportePorEmpleadoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reporte = reporte_por_empleado()
        return Response(reporte)