# products/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category', 'unit_price',
            'quantity_in_stock', 'low_stock_threshold',
            'is_low_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_unit_price(self, value):
        """Ensure unit price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero")
        return value

    def validate_quantity_in_stock(self, value):
        """Ensure quantity is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Quantity in stock cannot be negative")
        return value

    def validate_low_stock_threshold(self, value):
        """Ensure threshold is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Low stock threshold cannot be negative")
        return value

    def validate_sku(self, value):
        """Ensure SKU is uppercase and stripped of whitespace"""
        return value.strip().upper()

    def validate(self, attrs):
        """Additional cross-field validation"""
        sku = attrs.get('sku', '')
        if self.instance:
            # Update operation - check for duplicate SKU
            if Product.objects.exclude(id=self.instance.id).filter(sku=sku).exists():
                raise serializers.ValidationError({
                    'sku': 'Product with this SKU already exists'
                })
        return attrs