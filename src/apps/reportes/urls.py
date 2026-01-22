from django.urls import path
from .views import ReporteTurnosAPIView

urlpatterns = [
    path("turnos/", ReporteTurnosAPIView.as_view()),
]