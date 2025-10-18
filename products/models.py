# products/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    category = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    quantity_in_stock = models.IntegerField(
        validators=[MinValueValidator(0)],
        db_index=True
    )
    low_stock_threshold = models.IntegerField(
        default=5,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['category']),
            models.Index(fields=['quantity_in_stock']),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def is_low_stock(self):
        """Check if product stock is below threshold"""
        return self.quantity_in_stock <= self.low_stock_threshold

    def decrease_stock(self, quantity):
        """
        Decrease stock by given quantity.
        Raises ValidationError if insufficient stock.
        """
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")
        
        if self.quantity_in_stock < quantity:
            raise ValidationError(
                f"Insufficient stock. Available: {self.quantity_in_stock}, "
                f"Requested: {quantity}"
            )
        
        self.quantity_in_stock -= quantity
        self.save(update_fields=['quantity_in_stock', 'updated_at'])

    def increase_stock(self, quantity):
        """Increase stock by given quantity"""
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")
        
        self.quantity_in_stock += quantity
        self.save(update_fields=['quantity_in_stock', 'updated_at'])