from django.contrib import admin
from .models import TipoHabitacion, Habitacion


@admin.register(TipoHabitacion)
class TipoHabitacionAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo TipoHabitacion."""
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Habitacion."""
    # Muestra campos clave en la lista de habitaciones.
    list_display = ('numero', 'tipo', 'activa')
    # Permite filtrar por estado y por tipo de habitación.
    list_filter = ('activa', 'tipo')
    # Permite buscar habitaciones por su número.
    search_fields = ('numero',)
