from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from .models import Sale, SaleItem
from products.models import Product

User = get_user_model()


class SaleAPITestCase(TestCase):
    """Test cases for Sales API"""

    def setUp(self):
        """Set up test data"""
        # Create users
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.cashier1 = User.objects.create_user(
            username='cashier1',
            email='cashier1@test.com',
            password='cashier123'
        )
        self.cashier2 = User.objects.create_user(
            username='cashier2',
            email='cashier2@test.com',
            password='cashier123'
        )

        # Create products - adjusted to match your Product model
        # Assuming your Product has: name, selling_price, stock_quantity
        self.product1 = Product.objects.create(
            name='Test Laptop',
            description='Test laptop product',
            cost_price=Decimal('800.00'),
            selling_price=Decimal('999.99'),
            stock_quantity=10,
            low_stock_threshold=5
        )
        self.product2 = Product.objects.create(
            name='Test Mouse',
            description='Test mouse product',
            cost_price=Decimal('20.00'),
            selling_price=Decimal('29.99'),
            stock_quantity=50,
            low_stock_threshold=10
        )

        # Create API client
        self.client = APIClient()

    def test_create_sale_success(self):
        """Test successful sale creation"""
        self.client.force_authenticate(user=self.cashier1)

        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': 2,
                    'price_at_sale': '999.99'
                },
                {
                    'product_id': self.product2.id,
                    'quantity': 3,
                    'price_at_sale': '29.99'
                }
            ]
        }

        response = self.client.post('/api/sales/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        
        # Verify sale was created
        sale = Sale.objects.get(
            transaction_id=response.data['data']['transaction_id']
        )
        self.assertEqual(sale.cashier, self.cashier1)
        self.assertEqual(sale.items.count(), 2)
        self.assertEqual(
            sale.total_amount,
            Decimal('2089.95')  # (999.99 * 2) + (29.99 * 3)
        )

        # Verify inventory was updated
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock_quantity, 8)  # 10 - 2
        self.assertEqual(self.product2.stock_quantity, 47)  # 50 - 3

    def test_create_sale_insufficient_stock(self):
        """Test sale creation with insufficient stock"""
        self.client.force_authenticate(user=self.cashier1)

        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': 20,  # More than available (10)
                    'price_at_sale': '999.99'
                }
            ]
        }

        response = self.client.post('/api/sales/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify inventory wasn't changed
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock_quantity, 10)

    def test_create_sale_unauthenticated(self):
        """Test sale creation without authentication"""
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': 1,
                    'price_at_sale': '999.99'
                }
            ]
        }

        response = self.client.post('/api/sales/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_sales_as_admin(self):
        """Test admin can see all sales"""
        # Create sales by different cashiers
        sale1 = Sale.objects.create(
            cashier=self.cashier1,
            total_amount=Decimal('100.00')
        )
        sale2 = Sale.objects.create(
            cashier=self.cashier2,
            total_amount=Decimal('200.00')
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/sales/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_list_sales_as_cashier(self):
        """Test cashier can only see their own sales"""
        # Create sales by different cashiers
        sale1 = Sale.objects.create(
            cashier=self.cashier1,
            total_amount=Decimal('100.00')
        )
        sale2 = Sale.objects.create(
            cashier=self.cashier2,
            total_amount=Decimal('200.00')
        )

        self.client.force_authenticate(user=self.cashier1)
        response = self.client.get('/api/sales/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['data'][0]['transaction_id'],
            sale1.transaction_id
        )

    def test_retrieve_sale_as_owner(self):
        """Test cashier can retrieve their own sale"""
        sale = Sale.objects.create(
            cashier=self.cashier1,
            total_amount=Decimal('100.00')
        )

        self.client.force_authenticate(user=self.cashier1)
        response = self.client.get(f'/api/sales/{sale.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['data']['transaction_id'],
            sale.transaction_id
        )

    def test_retrieve_sale_as_non_owner(self):
        """Test cashier cannot retrieve another cashier's sale"""
        sale = Sale.objects.create(
            cashier=self.cashier1,
            total_amount=Decimal('100.00')
        )

        self.client.force_authenticate(user=self.cashier2)
        response = self.client.get(f'/api/sales/{sale.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_sale_not_allowed(self):
        """Test that sales cannot be updated"""
        sale = Sale.objects.create(
            cashier=self.cashier1,
            total_amount=Decimal('100.00')
        )

        self.client.force_authenticate(user=self.cashier1)
        response = self.client.put(
            f'/api/sales/{sale.id}/',
            {'total_amount': '200.00'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_sale_not_allowed(self):
        """Test that sales cannot be deleted"""
        sale = Sale.objects.create(
            cashier=self.cashier1,
            total_amount=Decimal('100.00')
        )

        self.client.force_authenticate(user=self.cashier1)
        response = self.client.delete(f'/api/sales/{sale.id}/')

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_filter_sales_by_date(self):
        """Test filtering sales by date range"""
        from django.utils import timezone
        from datetime import timedelta

        # Create sales on different dates
        old_date = timezone.now() - timedelta(days=10)
        recent_date = timezone.now() - timedelta(days=2)

        sale1 = Sale.objects.create(
            cashier=self.cashier1,
            total_amount=Decimal('100.00')
        )
        sale1.sale_date = old_date
        sale1.save()

        sale2 = Sale.objects.create(
            cashier=self.cashier1,
            total_amount=Decimal('200.00')
        )
        sale2.sale_date = recent_date
        sale2.save()

        self.client.force_authenticate(user=self.cashier1)
        
        # Filter for last 5 days
        start_date = (timezone.now() - timedelta(days=5)).isoformat()
        response = self.client.get(
            f'/api/sales/?start_date={start_date}'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_sales_statistics_as_admin(self):
        """Test statistics endpoint for admin"""
        Sale.objects.create(
            cashier=self.cashier1,
            total_amount=Decimal('100.00')
        )
        Sale.objects.create(
            cashier=self.cashier2,
            total_amount=Decimal('200.00')
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/sales/statistics/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['total_sales'], 2)
        self.assertEqual(
            float(response.data['data']['total_revenue']),
            300.00
        )

    def test_sales_statistics_as_cashier(self):
        """Test statistics endpoint denied for cashier"""
        self.client.force_authenticate(user=self.cashier1)
        response = self.client.get('/api/sales/statistics/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_auto_price_at_sale(self):
        """Test that price_at_sale defaults to current price"""
        self.client.force_authenticate(user=self.cashier1)

        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': 1
                    # No price_at_sale specified
                }
            ]
        }

        response = self.client.post('/api/sales/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        sale = Sale.objects.get(
            transaction_id=response.data['data']['transaction_id']
        )
        sale_item = sale.items.first()
        
        self.assertEqual(sale_item.price_at_sale, self.product1.selling_price)