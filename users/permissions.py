from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permission class that allows only admin users.
    """
    message = "Only admin users can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


class IsCashier(permissions.BasePermission):
    """
    Permission class that allows only cashier users.
    """
    message = "Only cashier users can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'cashier'
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows full access to admins,
    and read-only access to cashiers.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow read operations for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow write operations only for admins
        return request.user.role == 'admin'
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admins
        return request.user.role == 'admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows users to edit their own profile
    or admins to edit any profile.
    """
    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.role == 'admin':
            return True
        
        # Users can only edit their own profile
        return obj.id == request.user.id