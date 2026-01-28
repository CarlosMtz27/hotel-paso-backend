from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Solo ADMIN"""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == "ADMIN"
        )


class IsEmpleado(BasePermission):
    """ADMIN o EMPLEADO"""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol in ["ADMIN", "EMPLEADO"]
        )


class IsInvitado(BasePermission):
    """Cualquier usuario autenticado (ADMIN / EMPLEADO / INVITADO)"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOnlyInvitado(BasePermission):
    """Solo INVITADO"""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.rol == "INVITADO"
        )
