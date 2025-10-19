from rest_framework import serializers
from django.db import transaction
from .models import Sale, SaleItem
from products.models import Product  # Adjust import based on your project structure


class SaleItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual sale items with product details
    """
    product_id = serializers.IntegerField(write_only=True)
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
            'product_code',
            'quantity',
            'price_at_sale',
            'subtotal'
        ]
        read_only_fields = ['id', 'subtotal', 'product_name', 'product_code']
    
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
        read_only_fields = ['id', 'transaction_id', 'sale_date', 'total_amount']
    
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
        
        # Check stock availability for each item
        for item_data in items:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity')
            
            try:
                product = Product.objects.select_for_update().get(id=product_id)
                
                if product.stock_quantity < quantity:
                    raise serializers.ValidationError({
                        'items': f"Insufficient stock for {product.name}. "
                                f"Available: {product.stock_quantity}, Requested: {quantity}"
                    })
                
                # Validate price_at_sale if not provided, use current price
                if 'price_at_sale' not in item_data:
                    item_data['price_at_sale'] = product.selling_price
                
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
            
            # Validate stock again (in case of concurrent transactions)
            if product.stock_quantity < item_data['quantity']:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. "
                    f"Available: {product.stock_quantity}"
                )
            
            # Create sale item
            sale_item = SaleItem.objects.create(
                sale=sale,
                product=product,
                **item_data
            )
            
            # Update product inventory
            product.stock_quantity -= item_data['quantity']
            product.save(update_fields=['stock_quantity'])
            
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