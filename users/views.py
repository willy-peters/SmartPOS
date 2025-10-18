from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import (
    UserSerializer, 
    LoginSerializer, 
    RegisterSerializer
)
from .permissions import IsAdmin, IsAdminOrReadOnly, IsOwnerOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model with role-based access control.
    
    - Admin: Full CRUD access to all users
    - Cashier: Read-only access to user list, can update own profile
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        elif self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            permission_classes = [IsAdmin]
        elif self.action == 'me':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdmin]
        
        return [permission() for permission in permission_classes]
    
    def update(self, request, *args, **kwargs):
        """
        Update user with permission checks.
        """
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        
        # Check if cashier is trying to update someone else's profile
        if request.user.role == 'cashier' and instance.id != request.user.id:
            return Response(
                {"detail": "You do not have permission to update this user."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if admin is trying to demote themselves
        if (instance.id == request.user.id and 
            request.user.role == 'admin' and 
            request.data.get('role') == 'cashier'):
            return Response(
                {"detail": "Admin users cannot demote themselves."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partial update - calls update with partial=True.
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Prevent admin users from deleting their own account.
        """
        instance = self.get_object()
        
        if instance.id == request.user.id and request.user.role == 'admin':
            return Response(
                {"detail": "Admin users cannot delete their own account."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Get current user profile.
        GET /api/users/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint (Admin only).
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAdmin]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            {
                "message": "User created successfully.",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(generics.GenericAPIView):
    """
    User login endpoint.
    POST /api/auth/login/
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Login successful.",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        })


class LogoutView(generics.GenericAPIView):
    """
    User logout endpoint.
    POST /api/auth/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {"message": "Logout successful."},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"detail": "Invalid token or token already blacklisted."},
                status=status.HTTP_400_BAD_REQUEST
            )