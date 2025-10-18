# products/admin.py
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'unit_price', 'quantity_in_stock', 'is_low_stock', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'sku', 'category']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def is_low_stock(self, obj):
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'