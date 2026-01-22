from django.urls import path
from .views import ReporteTurnosAPIView, ReporteTurnosExcelAPIView,ReporteTurnosPDFAPIView, ResumenDiarioAPIView, ReportePorEmpleadoAPIView

urlpatterns = [
    path("turnos/", ReporteTurnosAPIView.as_view()),
    path("turnos/excel/", ReporteTurnosExcelAPIView.as_view()),
    path("turnos/pdf/", ReporteTurnosPDFAPIView.as_view()),
    path("resumen/diario/", ResumenDiarioAPIView.as_view()),
    path("empleados/", ReportePorEmpleadoAPIView.as_view()),


]