from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Sale(models.Model):
    """
    Represents a complete sales transaction
    """
    sale_date = models.DateTimeField(auto_now_add=True, db_index=True)
    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Changed from User to settings.AUTH_USER_MODEL
        on_delete=models.PROTECT,
        related_name='sales'
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    transaction_id = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True,
        db_index=True
    )
    
    class Meta:
        ordering = ['-sale_date']
        indexes = [
            models.Index(fields=['-sale_date', 'cashier']),
        ]
    
    def __str__(self):
        return f"Sale {self.transaction_id} - {self.sale_date.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        """Generate unique transaction ID if not provided"""
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_transaction_id():
        """Generate a unique transaction ID"""
        return f"TXN-{uuid.uuid4().hex[:12].upper()}"


class SaleItem(models.Model):
    """
    Represents individual items within a sale transaction
    """
    sale = models.ForeignKey(
        Sale, 
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='sale_items'
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    price_at_sale = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Price of the product at the time of sale"
    )
    
    class Meta:
        ordering = ['id']
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name='positive_quantity'
            ),
            models.CheckConstraint(
                check=models.Q(price_at_sale__gt=0),
                name='positive_price'
            ),
        ]
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} @ {self.price_at_sale}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.quantity * self.price_at_sale