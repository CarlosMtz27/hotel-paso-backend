from rest_framework.permissions import BasePermission

class EsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name="ADMIN").exists()


class EsEmpleado(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(
            name__in=["ADMIN", "EMPLEADO"]
        ).exists()
