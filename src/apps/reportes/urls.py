from django.urls import path
from .views import GraficaIngresosEmpleadosAPIView,ReporteTurnosAPIView, ReporteTurnosExcelAPIView,ReporteTurnosPDFAPIView, ResumenDiarioAPIView, ReportePorEmpleadoAPIView, ReporteDetalleEmpleadoAPIView, RankingEmpleadosAPIView

urlpatterns = [
    path("turnos/", ReporteTurnosAPIView.as_view(), name="reporte-turnos"),
    path("turnos/excel/", ReporteTurnosExcelAPIView.as_view(), name="reporte-turnos-excel"),
    path("turnos/pdf/", ReporteTurnosPDFAPIView.as_view(), name="reporte-turnos-pdf"),
    path("resumen/diario/", ResumenDiarioAPIView.as_view(), name="resumen-diario"),
    path("empleados/", ReportePorEmpleadoAPIView.as_view(), name="reporte-empleados"),
    path("empleados/<int:empleado_id>/", ReporteDetalleEmpleadoAPIView.as_view(), name="reporte-detalle-empleado"),
    path("empleados/ranking/", RankingEmpleadosAPIView.as_view(), name="ranking-empleados"),
    path("empleados/grafica-ingresos/", GraficaIngresosEmpleadosAPIView.as_view(), name="grafica-ingresos-empleados"),


]