from rest_framework.permissions import BasePermission
from apps.users.models import Usuario


class IsAdminUser(BasePermission):
    """
    Permite el acceso solo a usuarios con el rol de Administrador.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.rol == Usuario.Rol.ADMINISTRADOR
        )


class IsEmpleado(BasePermission):
    """
    Permite el acceso a usuarios con rol de Administrador o Empleado.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.rol in [Usuario.Rol.ADMINISTRADOR, Usuario.Rol.EMPLEADO]
        )


# La clase `IsInvitado` fue eliminada porque era una reimplementación de la clase
# `IsAuthenticated` de Django REST Framework. Es mejor usar directamente
# `from rest_framework.permissions import IsAuthenticated` para mantener el
# código estándar y evitar confusiones, ya que el nombre `IsInvitado`
# sugería incorrectamente que solo permitía el acceso a invitados.


class IsOnlyInvitado(BasePermission):
    """
    Permite el acceso solo a usuarios con el rol de Invitado.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.rol == Usuario.Rol.INVITADO
        )
