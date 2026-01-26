from django.contrib import admin
from .models import Turno


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    """
    Configuración personalizada para el modelo Turno en el admin de Django.
    Mejora la visualización y la capacidad de auditoría.
    """
    list_display = (
        'id', 'usuario', 'tipo_turno', 'fecha_inicio', 'fecha_fin', 'activo',
        'caja_inicial', 'efectivo_reportado', 'diferencia'
    )
    list_filter = ('activo', 'tipo_turno', 'usuario')
    search_fields = ('usuario__username', 'id')
    ordering = ('-fecha_inicio',)
    date_hierarchy = 'fecha_inicio'

    # Hacer que los campos calculados sean de solo lectura para evitar inconsistencias.
    readonly_fields = (
        'fecha_inicio', 'fecha_fin', 'efectivo_esperado', 'diferencia', 'caja_final'
    )

    def has_add_permission(self, request):
        # Los turnos solo deben crearse a través de la API y los servicios.
        return False

    def has_delete_permission(self, request, obj=None):
        # Los turnos no se eliminan para mantener el historial.
        return False
