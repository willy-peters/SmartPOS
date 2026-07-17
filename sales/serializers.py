from rest_framework import serializers
from django.db import transaction
from .models import Sale, SaleItem
from products.models import Product  # Adjust import based on your project structure
from django.core.exceptions import ValidationError


class SaleItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual sale items with product details
    """
    product_id = serializers.IntegerField()
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = SaleItem
        fields = [
            'id',
            'product_id',
            'product_name',
            'quantity',
            'price_at_sale',
            'subtotal'
        ]
        read_only_fields = ['id', 'subtotal', 'product_name', 'price_at_sale']
    
    def validate_product_id(self, value):
        """Validate that product exists"""
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError(f"Product with id {value} does not exist")
        return value


class SaleSerializer(serializers.ModelSerializer):
    """
    Serializer for complete sales with nested items
    """
    items = SaleItemSerializer(many=True)
    cashier_username = serializers.CharField(source='cashier.username', read_only=True)
    cashier_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Sale
        fields = [
            'id',
            'transaction_id',
            'sale_date',
            'cashier',
            'cashier_username',
            'cashier_name',
            'total_amount',
            'items'
        ]
        read_only_fields = ['id', 'transaction_id', 'sale_date', 'total_amount', 'cashier']
    
    def get_cashier_name(self, obj):
        """Get cashier's full name"""
        return f"{obj.cashier.first_name} {obj.cashier.last_name}".strip() or obj.cashier.username
    
    def validate_items(self, items):
        """Validate that items list is not empty"""
        if not items:
            raise serializers.ValidationError("Sale must contain at least one item")
        
        if len(items) > 100:
            raise serializers.ValidationError("Sale cannot contain more than 100 items")
        
        return items
    
    def validate(self, data):
        """Validate stock availability for all items"""
        items = data.get('items', [])
        
        # Aggregate quantities by product_id to correctly check combined request stock
        product_quantities = {}
        for item_data in items:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 0)
            product_quantities[product_id] = product_quantities.get(product_id, 0) + quantity
            
        # Check stock availability and set price_at_sale
        for item_data in items:
            product_id = item_data.get('product_id')
            total_requested = product_quantities.get(product_id, 0)
            
            try:
                product = Product.objects.get(id=product_id)
                
                if product.quantity_in_stock < total_requested:
                    raise serializers.ValidationError({
                        'items': f"Insufficient stock for {product.name}. "
                                f"Available: {product.quantity_in_stock}, Total Requested: {total_requested}"
                    })
                
                # Force price_at_sale to be the current product unit_price
                item_data['price_at_sale'] = product.unit_price
                
            except Product.DoesNotExist:
                raise serializers.ValidationError({
                    'items': f"Product with id {product_id} does not exist"
                })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create sale with items and update inventory atomically
        """
        items_data = validated_data.pop('items')
        
        # Create the sale instance
        sale = Sale.objects.create(**validated_data)
        
        total_amount = 0
        
        # Create sale items and update inventory
        for item_data in items_data:
            product_id = item_data.pop('product_id')
            product = Product.objects.select_for_update().get(id=product_id)
            
            # Decrease stock using helper method
            try:
                product.decrease_stock(item_data.get('quantity', 0))
            except ValidationError as e:
                raise serializers.ValidationError({
                    'items': str(e)
                })
            
            # Force final price_at_sale under database lock
            item_data['price_at_sale'] = product.unit_price
            
            # Create sale item
            sale_item = SaleItem.objects.create(
                sale=sale,
                product=product,
                **item_data
            )
            
            # Calculate running total
            total_amount += sale_item.subtotal
        
        # Update sale total amount
        sale.total_amount = total_amount
        sale.save(update_fields=['total_amount'])
        
        return sale
    
    def update(self, instance, validated_data):
        """
        Prevent updating sales after creation
        """
        raise serializers.ValidationError(
            "Sales cannot be modified after creation. Please create a new sale or process a refund."
        )


class SaleListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing sales
    """
    cashier_username = serializers.CharField(source='cashier.username', read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id',
            'transaction_id',
            'sale_date',
            'cashier_username',
            'total_amount',
            'items_count'
        ]