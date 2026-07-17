# products/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsAdminOrReadOnly  # Import your custom permission


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products
    
    Endpoints:
    - GET /api/products/ - List all products
    - POST /api/products/ - Create new product (admin only)
    - GET /api/products/{id}/ - Retrieve specific product
    - PUT /api/products/{id}/ - Update product (admin only)
    - PATCH /api/products/{id}/ - Partial update (admin only)
    - DELETE /api/products/{id}/ - Delete product (admin only)
    - GET /api/products/low-stock/ - Get low stock products
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]  # Use custom permission
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'sku']
    search_fields = ['name', 'sku', 'category']
    ordering_fields = ['name', 'unit_price', 'quantity_in_stock', 'created_at']
    ordering = ['-created_at']
    
    # REMOVE get_permissions() method - not needed with custom permission
    
    def list(self, request, *args, **kwargs):
        """List all products"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'count': queryset.count(),
            'data': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific product"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """Create a new product"""
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            return Response(
                {
                    'status': 'success',
                    'message': 'Product created successfully',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """Update a product"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response({
                'status': 'success',
                'message': 'Product updated successfully',
                'data': serializer.data
            })
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def partial_update(self, request, *args, **kwargs):
        """Partially update a product"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a product"""
        instance = self.get_object()
        
        # Check if product has been sold
        if hasattr(instance, 'sale_items') and instance.sale_items.exists():
            return Response(
                {
                    'status': 'error',
                    'message': 'Cannot delete product that has been sold. Consider marking it as inactive instead.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(
            {
                'status': 'success',
                'message': 'Product deleted successfully'
            },
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """
        Get products with low stock
        Returns products where quantity_in_stock <= low_stock_threshold
        
        Query params:
        - threshold: Override default threshold (optional)
        """
        # Get custom threshold from query params if provided
        custom_threshold = request.query_params.get('threshold')
        
        if custom_threshold:
            try:
                threshold = int(custom_threshold)
                queryset = Product.objects.filter(
                    quantity_in_stock__lte=threshold
                )
            except ValueError:
                return Response(
                    {
                        'status': 'error',
                        'message': 'Invalid threshold value. Must be an integer.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Use each product's own low_stock_threshold
            queryset = Product.objects.filter(
                quantity_in_stock__lte=F('low_stock_threshold')
            )
        
        # Order by most critical (lowest stock first)
        queryset = queryset.order_by('quantity_in_stock')
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'status': 'success',
            'count': queryset.count(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='out-of-stock')
    def out_of_stock(self, request):
        """Get products that are completely out of stock"""
        queryset = Product.objects.filter(quantity_in_stock=0).order_by('name')
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'status': 'success',
            'count': queryset.count(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get list of all product categories"""
        categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')
        
        return Response({
            'status': 'success',
            'count': len(categories),
            'data': list(categories)
        })