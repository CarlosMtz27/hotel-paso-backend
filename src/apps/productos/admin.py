from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    Configuración personalizada para el modelo Producto en el admin de Django.
    Mejora la visualización y la capacidad de auditoría.
    """
    list_display = ('nombre', 'precio', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    ordering = ('nombre',)
