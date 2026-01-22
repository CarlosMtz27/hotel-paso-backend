from django.urls import path
from .views import GraficaIngresosEmpleadosAPIView,ReporteTurnosAPIView, ReporteTurnosExcelAPIView,ReporteTurnosPDFAPIView, ResumenDiarioAPIView, ReportePorEmpleadoAPIView, ReporteDetalleEmpleadoAPIView, RankingEmpleadosAPIView

urlpatterns = [
    path("turnos/", ReporteTurnosAPIView.as_view()),
    path("turnos/excel/", ReporteTurnosExcelAPIView.as_view()),
    path("turnos/pdf/", ReporteTurnosPDFAPIView.as_view()),
    path("resumen/diario/", ResumenDiarioAPIView.as_view()),
    path("empleados/", ReportePorEmpleadoAPIView.as_view()),
    path("empleados/<int:empleado_id>/", ReporteDetalleEmpleadoAPIView.as_view()),
    path("empleados/ranking/", RankingEmpleadosAPIView.as_view()),
    path("empleados/grafica-ingresos/", GraficaIngresosEmpleadosAPIView.as_view()),


]