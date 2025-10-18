from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User

class UserModelTest(TestCase):
    """Test User model."""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        self.cashier = User.objects.create_user(
            username='cashier1',
            email='cashier@test.com',
            password='testpass123',
            role='cashier'
        )
    
    def test_user_creation(self):
        """Test user is created correctly."""
        self.assertEqual(self.admin.username, 'admin1')
        self.assertEqual(self.admin.role, 'admin')
        self.assertTrue(self.admin.is_admin())
        self.assertFalse(self.admin.is_cashier())
    
    def test_cashier_role(self):
        """Test cashier role methods."""
        self.assertTrue(self.cashier.is_cashier())
        self.assertFalse(self.cashier.is_admin())
    
    def test_default_role(self):
        """Test default role is cashier."""
        user = User.objects.create_user(
            username='test1',
            email='test@test.com',
            password='testpass123'
        )
        self.assertEqual(user.role, 'cashier')


class AuthenticationTest(APITestCase):
    """Test authentication endpoints."""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        self.cashier = User.objects.create_user(
            username='cashier1',
            email='cashier@test.com',
            password='testpass123',
            role='cashier'
        )
        
        self.client = APIClient()
    
    def test_login_success(self):
        """Test successful login."""
        url = reverse('login')
        data = {
            'username': 'admin1',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        url = reverse('login')
        data = {
            'username': 'admin1',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_register_as_admin(self):
        """Test admin can register new users."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'role': 'cashier'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_register_as_cashier_fails(self):
        """Test cashier cannot register new users."""
        self.client.force_authenticate(user=self.cashier)
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'role': 'cashier'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserPermissionsTest(APITestCase):
    """Test role-based permissions."""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        self.cashier = User.objects.create_user(
            username='cashier1',
            email='cashier@test.com',
            password='testpass123',
            role='cashier'
        )
        
        self.client = APIClient()
    
    def test_admin_can_list_users(self):
        """Test admin can list all users."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_cashier_can_list_users(self):
        """Test cashier can list users (read-only)."""
        self.client.force_authenticate(user=self.cashier)
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_cashier_can_view_own_profile(self):
        """Test cashier can view their own profile."""
        self.client.force_authenticate(user=self.cashier)
        url = reverse('user-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'cashier1')
    
    def test_cashier_can_update_own_profile(self):
        """Test cashier can update their own profile."""
        self.client.force_authenticate(user=self.cashier)
        url = reverse('user-detail', kwargs={'pk': self.cashier.id})
        data = {'first_name': 'Updated'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cashier.refresh_from_db()
        self.assertEqual(self.cashier.first_name, 'Updated')
    
    def test_cashier_cannot_update_other_profile(self):
        """Test cashier cannot update other user's profile."""
        self.client.force_authenticate(user=self.cashier)
        url = reverse('user-detail', kwargs={'pk': self.cashier.id})
        data = {'first_name': 'Hacked'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_cannot_demote_self(self):
        """Test admin cannot demote themselves."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-detail', kwargs={'pk': self.cashier.id})
        data = {'role': 'cashier'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_admin_cannot_delete_self(self):
        """Test admin cannot delete their own account."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-detail', kwargs={'pk': self.cashier.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cashier_cannot_delete_users(self):
        """Test cashier cannot delete users."""
        self.client.force_authenticate(user=self.cashier)
        url = reverse('user-detail', kwargs={'pk': self.cashier.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)