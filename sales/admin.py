from django.contrib import admin
from django.utils.html import format_html
from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    """Inline display of sale items within sale admin"""
    model = SaleItem
    extra = 0
    readonly_fields = ['subtotal_display']
    fields = ['product', 'quantity', 'price_at_sale', 'subtotal_display']
    
    def subtotal_display(self, obj):
        """Display subtotal for the item"""
        if obj.id:
            return f"${obj.subtotal:.2f}"
        return "-"
    subtotal_display.short_description = 'Subtotal'
    
    def has_add_permission(self, request, obj=None):
        """Prevent adding items after sale creation"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting items after sale creation"""
        return False


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """Admin interface for sales"""
    list_display = [
        'transaction_id',
        'sale_date',
        'cashier',
        'total_amount_display',
        'items_count',
        'status_badge'
    ]
    list_filter = ['sale_date', 'cashier']
    search_fields = ['transaction_id', 'cashier__username', 'cashier__first_name', 'cashier__last_name']
    readonly_fields = [
        'transaction_id',
        'sale_date',
        'total_amount',
        'items_summary'
    ]
    inlines = [SaleItemInline]
    date_hierarchy = 'sale_date'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('transaction_id', 'sale_date')
        }),
        ('Sale Details', {
            'fields': ('cashier', 'total_amount', 'items_summary')
        }),
    )
    
    def total_amount_display(self, obj):
        """Format total amount as currency"""
        return f"${obj.total_amount:.2f}"
    total_amount_display.short_description = 'Total Amount'
    total_amount_display.admin_order_field = 'total_amount'
    
    def items_count(self, obj):
        """Display number of items in sale"""
        return obj.items.count()
    items_count.short_description = 'Items'
    
    def status_badge(self, obj):
        """Display status badge"""
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">COMPLETED</span>'
        )
    status_badge.short_description = 'Status'
    
    def items_summary(self, obj):
        """Display summary of items in the sale"""
        if obj.id:
            items = obj.items.all()
            summary = "<ul style='margin: 0; padding-left: 20px;'>"
            for item in items:
                summary += f"<li>{item.product.name} x {item.quantity} @ ${item.price_at_sale} = ${item.subtotal}</li>"
            summary += "</ul>"
            return format_html(summary)
        return "-"
    items_summary.short_description = 'Items Summary'
    
    def has_add_permission(self, request):
        """Sales should be created through API, not admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing sales"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting sales"""
        return False


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    """Admin interface for sale items"""
    list_display = [
        'id',
        'sale',
        'product',
        'quantity',
        'price_at_sale',
        'subtotal_display'
    ]
    list_filter = ['sale__sale_date', 'product']
    search_fields = ['sale__transaction_id', 'product__name', 'product__code']
    readonly_fields = ['sale', 'product', 'quantity', 'price_at_sale', 'subtotal_display']
    
    def subtotal_display(self, obj):
        """Display subtotal"""
        return f"${obj.subtotal:.2f}"
    subtotal_display.short_description = 'Subtotal'
    
    def has_add_permission(self, request):
        """Prevent adding sale items directly"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing sale items"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting sale items"""
        return False