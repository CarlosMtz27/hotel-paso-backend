from django.contrib import admin
from .models import Estancia


@admin.register(Estancia)
class EstanciaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Estancia.
    Configurado como vista de solo lectura para auditoría. Las estancias
    se gestionan a través de la API para seguir la lógica de negocio.
    """
    list_display = ('id', 'habitacion', 'tarifa', 'activa', 'turno_inicio', 'turno_cierre', 'hora_salida_programada','hora_salida_real')
    list_filter = ('activa', 'habitacion__tipo', 'tarifa')
    search_fields = ('id', 'habitacion__numero')
    list_select_related = ('habitacion', 'tarifa', 'turno_inicio', 'turno_cierre', 'habitacion__tipo')

    fieldsets = (
        ('Estado Actual', {
            'fields': ('id', 'activa', 'habitacion', 'tarifa')
        }),
        ('Tiempos y Fechas', {
            'fields': ('hora_salida_programada', 'hora_salida_real')
        }),
        ('Turnos Asociados', {
            'fields': ('turno_inicio', 'turno_cierre')
        }),
    )

    # Hacemos todos los campos de solo lectura para preservar la integridad de los datos.
    readonly_fields = [f.name for f in Estancia._meta.get_fields()]

    def has_add_permission(self, request):
        # No permitir añadir desde el admin.
        return False

    def has_delete_permission(self, request, obj=None):
        # No permitir borrar para mantener el historial.
        return False