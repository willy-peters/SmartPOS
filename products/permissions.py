from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Anyone authenticated can read (GET, HEAD, OPTIONS)
    - Only admins can create/update/delete
    """
    
    def has_permission(self, request, view):
        print(f"=== Permission Check ===")
        print(f"User: {request.user}")
        print(f"Authenticated: {request.user.is_authenticated}")
        print(f"Method: {request.method}")
        print(f"Action: {getattr(view, 'action', 'N/A')}")
        print(f"Is staff: {request.user.is_staff}")
        print(f"Is superuser: {request.user.is_superuser}")
        print(f"=======================")
        
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            print("DENIED: User not authenticated")
            return False
        
        # Allow safe methods (GET, HEAD, OPTIONS) for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            print("ALLOWED: Safe method")
            return True
        
        # Check if user is admin for unsafe methods
        is_admin = request.user.is_staff or request.user.is_superuser
        print(f"Admin check result: {is_admin}")
        return is_admin