from django.urls import path
from .views import ReporteTurnosAPIView, ReporteTurnosExcelAPIView

urlpatterns = [
    path("turnos/", ReporteTurnosAPIView.as_view()),
    path("turnos/excel/", ReporteTurnosExcelAPIView.as_view()),
]