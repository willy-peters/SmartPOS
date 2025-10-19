from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Sale, SaleItem
from .serializers import SaleSerializer, SaleListSerializer
from .permissions import SalePermission
from .filters import SaleFilter


class SaleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sales transactions
    
    Endpoints:
    - GET /api/sales/ - List sales (filtered by user role)
    - POST /api/sales/ - Create new sale
    - GET /api/sales/{id}/ - Retrieve specific sale
    - GET /api/sales/statistics/ - Get sales statistics
    """
    permission_classes = [IsAuthenticated, SalePermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SaleFilter
    
    def get_queryset(self):
        """
        Return queryset based on user role:
        - Admins see all sales
        - Cashiers see only their own sales
        """
        user = self.request.user
        
        if user.is_staff or user.is_superuser:
            # Admins see all sales
            queryset = Sale.objects.all()
        else:
            # Cashiers see only their own sales
            queryset = Sale.objects.filter(cashier=user)
        
        # Optimize queries
        queryset = queryset.select_related('cashier').prefetch_related(
            'items__product'
        )
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'list':
            return SaleListSerializer
        return SaleSerializer
    
    def perform_create(self, serializer):
        """Set the cashier to the current user"""
        serializer.save(cashier=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new sale with enhanced error handling
        """
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            return Response(
                {
                    'status': 'success',
                    'message': 'Sale created successfully',
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
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific sale"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    def list(self, request, *args, **kwargs):
        """List sales with pagination"""
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
    
    def update(self, request, *args, **kwargs):
        """Prevent updating sales"""
        return Response(
            {
                'status': 'error',
                'message': 'Sales cannot be modified after creation'
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        """Prevent partial updating sales"""
        return Response(
            {
                'status': 'error',
                'message': 'Sales cannot be modified after creation'
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        """Prevent deleting sales"""
        return Response(
            {
                'status': 'error',
                'message': 'Sales cannot be deleted. Please process a refund instead.'
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get sales statistics
        Available for admins only
        """
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {
                    'status': 'error',
                    'message': 'Only admins can view statistics'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Calculate statistics
        sales = Sale.objects.filter(sale_date__gte=start_date)
        
        statistics = {
            'total_sales': sales.count(),
            'total_revenue': sales.aggregate(
                total=Sum('total_amount')
            )['total'] or 0,
            'total_items_sold': SaleItem.objects.filter(
                sale__sale_date__gte=start_date
            ).aggregate(
                total=Sum('quantity')
            )['total'] or 0,
            'average_sale_value': sales.aggregate(
                avg=Sum('total_amount')
            )['avg'] or 0,
            'top_cashiers': list(
                sales.values('cashier__username', 'cashier__first_name', 'cashier__last_name')
                .annotate(
                    total_sales=Count('id'),
                    total_revenue=Sum('total_amount')
                )
                .order_by('-total_revenue')[:5]
            ),
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': timezone.now().isoformat()
        }
        
        # Calculate average if there are sales
        if statistics['total_sales'] > 0:
            statistics['average_sale_value'] = (
                statistics['total_revenue'] / statistics['total_sales']
            )
        
        return Response({
            'status': 'success',
            'data': statistics
        })
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's sales for the current user"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            sale_date__date=today
        )
        
        serializer = self.get_serializer(queryset, many=True)
        total = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        
        return Response({
            'status': 'success',
            'data': {
                'sales': serializer.data,
                'count': queryset.count(),
                'total_amount': total,
                'date': today.isoformat()
            }
        })