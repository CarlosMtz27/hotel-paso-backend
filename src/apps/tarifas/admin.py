from django.contrib import admin
from .models import Tarifa


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    """
    Configuración personalizada para el modelo Tarifa en el admin de Django.
    """
    list_display = ('nombre', 'tipo_habitacion', 'precio', 'horas', 'es_nocturna', 'activa')
    list_filter = ('activa', 'es_nocturna', 'tipo_habitacion')
    search_fields = ('nombre', 'tipo_habitacion__nombre')
    ordering = ('tipo_habitacion', 'precio',)
