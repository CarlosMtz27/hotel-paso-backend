from django.contrib import admin
from .models import Tarifa


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    """
    Configuración personalizada para el modelo Tarifa en el admin de Django.
    """
    list_display = ('nombre', 'tipo_habitacion', 'precio', 'horas', 'es_nocturna', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'es_nocturna', 'tipo_habitacion')
    search_fields = ('nombre', 'tipo_habitacion__nombre')
    ordering = ('-fecha_creacion', 'tipo_habitacion', 'precio',)
    date_hierarchy = 'fecha_creacion'
    list_select_related = ('tipo_habitacion',)
    readonly_fields = ('fecha_creacion',)

    fieldsets = (
        (None, {
            'fields': ('nombre', 'tipo_habitacion', 'activa')
        }),
        ('Detalles de Precio y Duración', {
            'fields': ('precio', 'horas')
        }),
        ('Tarifa Nocturna (Opcional)', {
            'classes': ('collapse',),
            'fields': ('es_nocturna', 'hora_inicio_nocturna', 'hora_fin_nocturna'),
            'description': 'Marque esta opción y defina el horario solo si la tarifa es exclusivamente para la noche.'
        }),
    )
