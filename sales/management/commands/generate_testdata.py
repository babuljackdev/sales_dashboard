from django.core.management.base import BaseCommand
from django.utils import timezone
from sales.models import Product, Salesperson, Sale
from decimal import Decimal
import random
from datetime import datetime, timedelta
import pytz

class Command(BaseCommand):
    help = 'Generate test data for the sales dashboard'

    def generate_products(self):
        # List of sample product names and categories
        products = [
            "Professional Laptop", "Wireless Mouse", "Mechanical Keyboard", "4K Monitor",
            "USB-C Hub", "Wireless Headphones", "Webcam Pro", "External SSD",
            "Gaming Chair", "Standing Desk", "Desk Lamp", "Wireless Charger",
            "Bluetooth Speaker", "Tablet Pro", "Smartwatch", "Fitness Tracker",
            "Noise-Canceling Earbuds", "Power Bank", "Graphics Tablet", "Portable Monitor",
            "Router Pro", "Security Camera", "Smart Speaker", "Wireless Printer",
            "External GPU", "VR Headset", "Streaming Mic", "Ergonomic Mouse",
            "Mechanical Numpad", "Desk Mat"
        ]

        for name in products:
            price = round(random.uniform(50, 1000), 2)
            stock = random.randint(10, 100)
            Product.objects.create(
                name=name,
                description=f"High-quality {name.lower()} for professional use",
                price=Decimal(str(price)),
                stock_level=stock
            )
        
        return len(products)

    def generate_salespeople(self):
        # List of sample names
        first_names = ["John", "Emma", "Michael", "Sarah", "David", "Lisa", "James", "Emily", "Robert", "Jessica"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

        for i in range(10):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            email = f"{name.lower().replace(' ', '.')}@example.com"
            phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            
            Salesperson.objects.create(
                name=name,
                email=email,
                phone=phone
            )
        
        return 10

    def generate_sales(self):
        products = list(Product.objects.all())
        salespeople = list(Salesperson.objects.all())
        
        # List of sample customer names
        customer_first_names = ["Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", "George", "Hannah", "Ian", "Julia"]
        customer_last_names = ["Anderson", "Baker", "Clark", "Davis", "Edwards", "Fisher", "Green", "Harris", "Irwin", "Jackson"]
        
        # Generate sales for the past 7 months
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7*30)  # Approximately 7 months
        
        total_sales = 0
        current_date = start_date
        
        while current_date <= end_date:
            # Generate random number of sales for this day (2-5 sales per day)
            daily_sales = random.randint(2, 5)
            
            for _ in range(daily_sales):
                product = random.choice(products)
                salesperson = random.choice(salespeople)
                quantity = random.randint(1, 5)
                customer_name = f"{random.choice(customer_first_names)} {random.choice(customer_last_names)}"
                
                # Create the sale
                Sale.objects.create(
                    customer_name=customer_name,
                    product=product,
                    salesperson=salesperson,
                    quantity=quantity,
                    price_per_unit=product.price,
                    date_of_sale=current_date
                )
                total_sales += 1
            
            current_date += timedelta(days=1)
        
        return total_sales

    def handle(self, *args, **kwargs):
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Sale.objects.all().delete()
        Product.objects.all().delete()
        Salesperson.objects.all().delete()

        # Generate new data
        self.stdout.write('Generating products...')
        products_count = self.generate_products()
        self.stdout.write(f'Created {products_count} products')

        self.stdout.write('Generating salespeople...')
        salespeople_count = self.generate_salespeople()
        self.stdout.write(f'Created {salespeople_count} salespeople')

        self.stdout.write('Generating sales...')
        sales_count = self.generate_sales()
        self.stdout.write(f'Created {sales_count} sales')

        self.stdout.write(self.style.SUCCESS('Successfully generated test data')) 