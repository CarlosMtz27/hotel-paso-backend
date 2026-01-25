from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Permite el acceso solo a usuarios con rol de Administrador.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol == 'ADMIN')

class EsEmpleado(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(
            name__in=["ADMIN", "EMPLEADO"]
        ).exists()
