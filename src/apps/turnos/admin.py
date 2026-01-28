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
    list_select_related = ('usuario',)

    # Se define una vista de solo lectura para los turnos desde el admin.
    # Esto garantiza que los turnos solo se modifiquen a través de los
    # servicios de negocio (iniciar/cerrar turno), manteniendo la integridad de los datos.
    readonly_fields = (
        'id', 'usuario', 'tipo_turno', 'fecha_inicio', 'fecha_fin', 'activo',
        'sueldo', 'caja_inicial', 'efectivo_esperado', 'efectivo_reportado',
        'diferencia', 'caja_final'
    )

    fieldsets = (
        ('Información General', {
            'fields': ('id', 'usuario', 'tipo_turno', 'activo')
        }),
        ('Periodo', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Cierre de Caja (Contabilidad)', {
            'fields': (
                'caja_inicial', 'sueldo', 'efectivo_esperado',
                'efectivo_reportado', 'diferencia', 'caja_final'
            )
        }),
    )

    def has_add_permission(self, request):
        # Los turnos solo deben crearse a través de la API y los servicios.
        return False

    def has_delete_permission(self, request, obj=None):
        # Los turnos no se eliminan para mantener el historial.
        return False
