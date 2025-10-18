# products/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from django.db.models import F
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsAdminOrReadOnly

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        """
        Admin sees all products.
        Cashiers see all products (read-only enforced by permissions).
        """
        return Product.objects.all()

    def create(self, request, *args, **kwargs):
        """Handle product creation with proper error handling"""
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {'error': 'Product with this SKU already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """Handle product update with proper error handling"""
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {'error': 'Product with this SKU already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def low_stock(self, request):
        """
        Get all products with low stock.
        Admin only endpoint.
        """
        # Check if user is admin
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filter products where quantity <= threshold
        low_stock_products = Product.objects.filter(
            quantity_in_stock__lte=F('low_stock_threshold')
        )
        
        serializer = self.get_serializer(low_stock_products, many=True)
        return Response({
            'count': low_stock_products.count(),
            'products': serializer.data
        })