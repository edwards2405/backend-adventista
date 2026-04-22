from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permite el acceso solo a los usuarios con rol 'superadmin' o is_superuser.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        return request.user.role and request.user.role.nombre_rol == 'superadmin'


class IsDoctor(permissions.BasePermission):
    """
    Permite el acceso solo a los usuarios con rol 'medico' o 'superadmin'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser or (request.user.role and request.user.role.nombre_rol == 'superadmin'):
            return True
            
        return request.user.role and request.user.role.nombre_rol == 'medico'


class IsReceptionist(permissions.BasePermission):
    """
    Permite el acceso solo a los usuarios con rol 'recepcion' o 'superadmin'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser or (request.user.role and request.user.role.nombre_rol == 'superadmin'):
            return True
            
        return request.user.role and request.user.role.nombre_rol == 'recepcion'
