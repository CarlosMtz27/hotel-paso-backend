from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario


@admin.register(Usuario)
class UserAdmin(BaseUserAdmin):
    """
    Configuración personalizada para el modelo Usuario en el admin de Django.
    Extiende el UserAdmin base para añadir nuestros campos personalizados.
    """
    # Campos a mostrar en la lista de usuarios.
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff', 'activo', 'date_joined', 'last_login')
    # Filtros disponibles en la barra lateral.
    list_filter = ('rol', 'is_staff', 'is_superuser', 'activo', 'groups')
    # Campos por los que se puede buscar.
    search_fields = ('username', 'first_name', 'last_name', 'email')
    # Orden por defecto.
    ordering = ('-date_joined',)
    date_hierarchy = 'date_joined'
    # Añade el campo 'rol' y 'activo' a los fieldsets para poder editarlos.
    fieldsets = BaseUserAdmin.fieldsets + (('Campos Personalizados', {'fields': ('rol', 'activo')}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (('Campos Personalizados', {'fields': ('rol',)}),)
