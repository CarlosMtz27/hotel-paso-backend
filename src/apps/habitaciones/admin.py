from django.contrib import admin
from .models import TipoHabitacion, Habitacion


@admin.register(TipoHabitacion)
class TipoHabitacionAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo TipoHabitacion."""
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Habitacion."""
    # Muestra campos clave en la lista de habitaciones.
    list_display = ('numero', 'tipo', 'estado', 'activa', 'fecha_creacion')
    # Permite editar el estado y si está activa directamente desde la lista.
    list_editable = ('estado', 'activa')
    # Permite filtrar por estado y por tipo de habitación.
    list_filter = ('estado', 'activa', 'tipo')
    # Permite buscar habitaciones por su número.
    search_fields = ('numero', 'tipo__nombre')
    ordering = ('numero',)
    date_hierarchy = 'fecha_creacion'
    list_select_related = ('tipo',)
    readonly_fields = ('fecha_creacion',)
