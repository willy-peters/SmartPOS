from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from decimal import Decimal
from datetime import datetime
# import pytz

from sales.models import Sale, SaleItem
from products.models import Product

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup test users and sales data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sales data before creating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing sales data...')
            Sale.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Sales data cleared!'))

        # Create users if they don't exist
        self.stdout.write('Creating test users...')
        
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@smartpos.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created admin user (ID: {admin.id})'))
        else:
            self.stdout.write(f'✓ Admin user already exists (ID: {admin.id})')

        cashier1, created = User.objects.get_or_create(
            username='cashier1',
            defaults={
                'email': 'john.doe@smartpos.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_staff': False,
                'is_active': True,
            }
        )
        if created:
            cashier1.set_password('cashier123')
            cashier1.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created cashier1 user (ID: {cashier1.id})'))
        else:
            self.stdout.write(f'✓ Cashier1 user already exists (ID: {cashier1.id})')

        cashier2, created = User.objects.get_or_create(
            username='cashier2',
            defaults={
                'email': 'jane.smith@smartpos.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'is_staff': False,
                'is_active': True,
            }
        )
        if created:
            cashier2.set_password('cashier123')
            cashier2.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created cashier2 user (ID: {cashier2.id})'))
        else:
            self.stdout.write(f'✓ Cashier2 user already exists (ID: {cashier2.id})')

        # Check if we have products
        products = Product.objects.all()[:5]
        if products.count() < 5:
            self.stdout.write(
                self.style.WARNING(
                    f'\nWarning: Only {products.count()} products found. '
                    'You need at least 5 products to create sample sales.'
                )
            )
            return

        self.stdout.write('\nCreating sample sales...')

        # Define sales data
        sales_data = [
            {
                'date': '2025-10-15T09:30:00Z',
                'cashier': cashier1,
                'transaction_id': 'TXN-A1B2C3D4E5F6',
                'items': [
                    {'product_index': 0, 'quantity': 2},
                    {'product_index': 1, 'quantity': 1},
                ]
            },
            {
                'date': '2025-10-15T14:45:00Z',
                'cashier': cashier2,
                'transaction_id': 'TXN-G7H8I9J0K1L2',
                'items': [
                    {'product_index': 2, 'quantity': 3},
                    {'product_index': 3, 'quantity': 2},
                ]
            },
            {
                'date': '2025-10-16T10:15:00Z',
                'cashier': cashier1,
                'transaction_id': 'TXN-M3N4O5P6Q7R8',
                'items': [
                    {'product_index': 4, 'quantity': 2},
                    {'product_index': 0, 'quantity': 1},
                ]
            },
            {
                'date': '2025-10-17T16:20:00Z',
                'cashier': cashier2,
                'transaction_id': 'TXN-S9T0U1V2W3X4',
                'items': [
                    {'product_index': 1, 'quantity': 2},
                    {'product_index': 3, 'quantity': 3},
                ]
            },
            {
                'date': '2025-10-18T11:00:00Z',
                'cashier': cashier1,
                'transaction_id': 'TXN-Y5Z6A7B8C9D0',
                'items': [
                    {'product_index': 0, 'quantity': 4},
                ]
            },
            {
                'date': '2025-10-18T15:30:00Z',
                'cashier': cashier2,
                'transaction_id': 'TXN-E1F2G3H4I5J6',
                'items': [
                    {'product_index': 2, 'quantity': 5},
                ]
            },
            {
                'date': '2025-10-19T08:45:00Z',
                'cashier': cashier1,
                'transaction_id': 'TXN-K7L8M9N0O1P2',
                'items': [
                    {'product_index': 3, 'quantity': 4},
                ]
            },
            {
                'date': '2025-10-19T12:20:00Z',
                'cashier': cashier2,
                'transaction_id': 'TXN-Q3R4S5T6U7V8',
                'items': [
                    {'product_index': 2, 'quantity': 3},
                ]
            },
        ]

        created_count = 0
        products_list = list(products)

        for sale_data in sales_data:
            try:
                with transaction.atomic():
                    # Check if sale already exists
                    if Sale.objects.filter(
                        transaction_id=sale_data['transaction_id']
                    ).exists():
                        self.stdout.write(
                            f'  ⊘ Sale {sale_data["transaction_id"]} already exists'
                        )
                        continue

                    # Parse date
                    sale_date = datetime.fromisoformat(
                        sale_data['date'].replace('Z', '+00:00')
                    )

                    # Create sale
                    sale = Sale.objects.create(
                        sale_date=sale_date,
                        cashier=sale_data['cashier'],
                        transaction_id=sale_data['transaction_id'],
                        total_amount=Decimal('0.00')
                    )

                    # Create sale items
                    total_amount = Decimal('0.00')
                    for item_data in sale_data['items']:
                        product = products_list[item_data['product_index']]
                        
                        # Check stock
                        if product.quantity < item_data['quantity']:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  ⚠ Insufficient stock for {product.name}. Skipping...'
                                )
                            )
                            continue

                        sale_item = SaleItem.objects.create(
                            sale=sale,
                            product=product,
                            quantity=item_data['quantity'],
                            price_at_sale=product.price
                        )

                        # Update inventory
                        product.quantity -= item_data['quantity']
                        product.save(update_fields=['quantity'])

                        total_amount += sale_item.subtotal

                    # Update sale total
                    sale.total_amount = total_amount
                    sale.save(update_fields=['total_amount'])

                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Created sale {sale.transaction_id} - ${total_amount}'
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error creating sale: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully created {created_count} sales!'
            )
        )
        
        # Display summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('LOGIN CREDENTIALS:')
        self.stdout.write('='*50)
        self.stdout.write(f'Admin    - Username: admin     Password: admin123')
        self.stdout.write(f'Cashier1 - Username: cashier1  Password: cashier123')
        self.stdout.write(f'Cashier2 - Username: cashier2  Password: cashier123')
        self.stdout.write('='*50)