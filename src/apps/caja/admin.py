from django.contrib import admin
from .models import MovimientoCaja


@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):
    """
    Configuración personalizada para el modelo MovimientoCaja en el admin de Django.
    Mejora la visualización y la capacidad de auditoría.
    """
    list_display = ('id', 'fecha', 'turno', 'tipo', 'monto', 'metodo_pago', 'estancia', 'producto')
    list_filter = ('tipo', 'metodo_pago', 'turno__usuario')
    search_fields = ('turno__id', 'estancia__id', 'producto__nombre')
    ordering = ('-fecha',)
    date_hierarchy = 'fecha'

    def has_add_permission(self, request):
        # Los movimientos solo deben crearse a través de la lógica de negocio (API, servicios).
        return False

    def has_change_permission(self, request, obj=None):
        # Los movimientos son inmutables.
        return False

    def has_delete_permission(self, request, obj=None):
        # Los movimientos no se deben eliminar.
        return False
