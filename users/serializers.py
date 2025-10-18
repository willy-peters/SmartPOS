from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with role-based field access.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password', 
                  'first_name', 'last_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate_email(self, value):
        """Ensure email is unique."""
        user = self.context.get('request').user if self.context.get('request') else None
        if self.instance:
            # Updating existing user
            if User.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        else:
            # Creating new user
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_role(self, value):
        """Validate role is either admin or cashier."""
        if value not in ['admin', 'cashier']:
            raise serializers.ValidationError("Role must be either 'admin' or 'cashier'.")
        return value
    
    def validate(self, attrs):
        """
        Prevent admin users from demoting themselves.
        """
        request = self.context.get('request')
        if request and self.instance:
            # Check if admin is trying to change their own role
            if (self.instance.id == request.user.id and 
                self.instance.role == 'admin' and 
                attrs.get('role') != 'admin'):
                raise serializers.ValidationError(
                    {"role": "Admin users cannot demote themselves."}
                )
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password."""
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update user with optional password change."""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration (admin only).
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 
                  'role', 'first_name', 'last_name']
    
    def validate(self, attrs):
        """Validate password confirmation matches."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password_confirm": "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        """Create new user."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
