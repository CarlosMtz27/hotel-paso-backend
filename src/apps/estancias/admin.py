from django.contrib import admin
from .models import Estancia


@admin.register(Estancia)
class EstanciaAdmin(admin.ModelAdmin):
    """
    Configuración personalizada para el modelo Estancia en el admin de Django.
    Mejora la visualización y la capacidad de auditoría.
    """
    list_display = ('id', 'habitacion', 'tarifa', 'hora_entrada', 'hora_salida_programada', 'hora_salida_real', 'activa', 'turno_inicio', 'turno_cierre')
    list_filter = ('activa', 'habitacion__tipo', 'turno_inicio__usuario')
    search_fields = ('habitacion__numero',)
    ordering = ('-hora_entrada',)
    date_hierarchy = 'hora_entrada'

    # Se recomienda hacer los campos de solo lectura para evitar modificaciones
    # accidentales que no pasen por la lógica de negocio de los servicios.
    readonly_fields = ('hora_entrada', 'hora_salida_programada', 'hora_salida_real', 'turno_inicio', 'turno_cierre')

    def has_add_permission(self, request):
        # Las estancias solo deben crearse a través de la API y los servicios.
        return False

    def has_delete_permission(self, request, obj=None):
        # Las estancias no se eliminan, solo se cierran.
        return False
