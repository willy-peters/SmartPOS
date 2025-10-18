from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    """
    Custom User model with role-based access control for SmartPOS system.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('cashier', 'Cashier'),
    ]
    
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'A user with this email already exists.',
        }
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='cashier',
        help_text='User role determines access permissions'
    )
    
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9]{3,30}$',
        message='Username must be 3-30 alphanumeric characters.',
    )
    
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': 'A user with this username already exists.',
        }
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'
    
    def is_cashier(self):
        """Check if user has cashier role."""
        return self.role == 'cashier'
