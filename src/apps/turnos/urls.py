from django.urls import path
from .views import IniciarTurnoView
from .views import CerrarTurnoView


urlpatterns = [
    path("iniciar/", IniciarTurnoView.as_view()),
    path("cerrar/", CerrarTurnoView.as_view()),

]
