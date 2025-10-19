from rest_framework import permissions


class SalePermission(permissions.BasePermission):
    """
    Custom permission for sales:
    - Admins can view all sales
    - Cashiers can only view their own sales
    - All authenticated users can create sales
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view"""
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # All authenticated users can create sales (POST)
        if request.method == 'POST':
            return True
        
        # For list view (GET), all authenticated users can access
        # (filtering will be done in the viewset)
        if view.action == 'list':
            return True
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access specific sale object
        """
        # Admins/superusers can access any sale
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Cashiers can only access their own sales
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return obj.cashier == request.user
        
        # No one can update or delete sales
        return False