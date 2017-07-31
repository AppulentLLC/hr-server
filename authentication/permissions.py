from rest_framework import permissions

class ManagerPermission(permissions.BasePermission):
    def is_manager(self, request):
        user = getattr(request, 'user', None)
        privileges = getattr(user, 'privileges', None)
        hr_role = privileges.hr_role
        if privileges and (privileges.is_global_admin or hr_role in ['m', 'a']):
            return True
        return False
            
        
class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of profile to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner() == request.user

class IsOwnerOrIsManager(ManagerPermission):
    def has_object_permission(self, request, view, obj):
        if self.is_manager(request):
            return True
        return obj.owner() == request.user
    
"""        
class IsSelfOrIsAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj == request.user or request.user.is_staff:
            return True
        if self.get_employee() is not None:
            return
"""

class IsManagerOrNotCreate(ManagerPermission):
    """
    Custom permission to only allow admin users to create a new object.
    """
    def has_permission(self, request, view):
        if self.is_manager(request):
            return True
        return view.action != 'create'

class IsManagerOrReadOnly(ManagerPermission):
    """
    The request is authenticated as a staff user, or is a read-only request.
    """

    def has_permission(self, request, view):
        if self.is_manager(request):
            return True
        return request.method in permissions.SAFE_METHODS

class IsNotDelete(permissions.BasePermission):
    """
    The request's method is not delete.
    """
    def has_permission(self, request, view):
        return request.method != 'DELETE'

class IsTerminal(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        privileges = getattr(user, 'privileges', None)
        if privileges and privileges.hr_role == 't':
            return True
        return False

class ReadOnly(ManagerPermission):
    """
    read-only request.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
        
"""            
class IsTerminalOrIsManager(ManagerPermission):
    def has_permission(self, request, view):
        if self.is_manager(request):
            return True
        terminal = getattr(request.user, 'terminal', None)
        return terminal is not None
"""
