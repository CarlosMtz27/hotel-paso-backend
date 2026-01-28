from django.contrib import admin
from .models import MovimientoCaja


@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para MovimientoCaja.
    Se configura como una vista de solo lectura para auditoría, ya que los
    movimientos se crean automáticamente a través de otras acciones del sistema
    (ej. vender producto, iniciar estancia).
    """
    list_display = ('id', 'turno', 'tipo', 'monto', 'metodo_pago', 'estancia', 'producto')
    list_filter = ('tipo', 'metodo_pago', 'turno__usuario')
    search_fields = ('id', 'turno__id', 'turno__usuario__username', 'estancia__id')
    ordering = ('-fecha',)
    date_hierarchy = 'fecha'
    list_select_related = ('turno', 'turno__usuario', 'estancia', 'producto')

    # Hacemos todos los campos de solo lectura para preservar la integridad de los datos.
    readonly_fields = [f.name for f in MovimientoCaja._meta.get_fields()]

    def has_add_permission(self, request):
        # No permitir añadir desde el admin.
        return False

    def has_delete_permission(self, request, obj=None):
        # No permitir borrar para mantener el historial.
        return False