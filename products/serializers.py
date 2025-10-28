from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model
    """
    is_low_stock = serializers.SerializerMethodField()
    is_out_of_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'sku',
            'category',
            'unit_price',
            'quantity_in_stock',
            'low_stock_threshold',
            'is_low_stock',
            'is_out_of_stock',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_low_stock(self, obj):
        """Check if product is low on stock"""
        return obj.is_low_stock()
    
    def get_is_out_of_stock(self, obj):
        """Check if product is out of stock"""
        return obj.quantity_in_stock == 0
    
    def validate_sku(self, value):
        """Ensure SKU is unique"""
        instance = self.instance
        if instance and instance.sku == value:
            return value
        
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError(
                f"Product with SKU '{value}' already exists"
            )
        return value
    
    def validate_unit_price(self, value):
        """Validate that unit price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than 0")
        return value
    
    def validate_quantity_in_stock(self, value):
        """Validate that quantity is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value
    
    def validate_low_stock_threshold(self, value):
        """Validate that threshold is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Low stock threshold cannot be negative")
        return value