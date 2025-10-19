import django_filters
from .models import Sale


class SaleFilter(django_filters.FilterSet):
    """
    Filter for sales with date range and other criteria
    """
    # Date range filters
    start_date = django_filters.DateTimeFilter(
        field_name='sale_date',
        lookup_expr='gte',
        label='Start Date'
    )
    end_date = django_filters.DateTimeFilter(
        field_name='sale_date',
        lookup_expr='lte',
        label='End Date'
    )
    
    # Date filter (exact date)
    date = django_filters.DateFilter(
        field_name='sale_date__date',
        label='Exact Date'
    )
    
    # Transaction ID search
    transaction_id = django_filters.CharFilter(
        field_name='transaction_id',
        lookup_expr='icontains',
        label='Transaction ID'
    )
    
    # Cashier filter (for admins)
    cashier = django_filters.NumberFilter(
        field_name='cashier__id',
        label='Cashier ID'
    )
    
    cashier_username = django_filters.CharFilter(
        field_name='cashier__username',
        lookup_expr='icontains',
        label='Cashier Username'
    )
    
    # Amount range filters
    min_amount = django_filters.NumberFilter(
        field_name='total_amount',
        lookup_expr='gte',
        label='Minimum Amount'
    )
    max_amount = django_filters.NumberFilter(
        field_name='total_amount',
        lookup_expr='lte',
        label='Maximum Amount'
    )
    
    class Meta:
        model = Sale
        fields = [
            'start_date',
            'end_date',
            'date',
            'transaction_id',
            'cashier',
            'cashier_username',
            'min_amount',
            'max_amount'
        ]