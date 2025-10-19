from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import random
from datetime import timedelta

from sales.models import Sale, SaleItem
from products.models import Product  # Adjust import based on your project


class Command(BaseCommand):
    help = 'Create test sales data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of sales to create'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Spread sales across this many days'
        )

    def handle(self, *args, **options):
        count = options['count']
        days = options['days']

        # Get cashiers (non-admin users)
        cashiers = list(User.objects.filter(is_staff=False))
        if not cashiers:
            self.stdout.write(
                self.style.ERROR('No cashier users found. Please create some users first.')
            )
            return

        # Get products
        products = list(Product.objects.all())
        if not products:
            self.stdout.write(
                self.style.ERROR('No products found. Please create some products first.')
            )
            return

        self.stdout.write(f'Creating {count} test sales...')

        created_count = 0
        failed_count = 0

        for i in range(count):
            try:
                # Random date within the specified range
                days_ago = random.randint(0, days)
                sale_date = timezone.now() - timedelta(
                    days=days_ago,
                    hours=random.randint(8, 20),
                    minutes=random.randint(0, 59)
                )

                # Random cashier
                cashier = random.choice(cashiers)

                # Create sale with atomic transaction
                with transaction.atomic():
                    sale = Sale.objects.create(
                        sale_date=sale_date,
                        cashier=cashier,
                        total_amount=Decimal('0.00')
                    )

                    # Add 1-5 random items
                    num_items = random.randint(1, 5)
                    total_amount = Decimal('0.00')

                    for _ in range(num_items):
                        product = random.choice(products)
                        
                        # Check if product has stock
                        if product.quantity > 0:
                            # Random quantity (1 to min of 5 or available stock)
                            max_qty = min(5, product.quantity)
                            quantity = random.randint(1, max_qty)

                            # Use current product price
                            price_at_sale = product.price

                            # Create sale item
                            sale_item = SaleItem.objects.create(
                                sale=sale,
                                product=product,
                                quantity=quantity,
                                price_at_sale=price_at_sale
                            )

                            # Update product inventory
                            product.quantity -= quantity
                            product.save(update_fields=['quantity'])

                            # Add to total
                            total_amount += sale_item.subtotal

                    # Update sale total
                    sale.total_amount = total_amount
                    sale.save(update_fields=['total_amount'])

                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created sale {sale.transaction_id} - ${total_amount}'
                        )
                    )

            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Failed to create sale: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created {created_count} sales, {failed_count} failed.'
            )
        )