from django.db import models
from django.utils import timezone
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)

class Product(models.Model):
    """
    Product model representing items available for sale.
    
    Attributes:
        name (str): The name of the product
        description (str): Detailed description of the product
        stock_level (int): Current quantity in stock
        price (float): Unit price of the product
        created_at (datetime): Timestamp when product was created
        updated_at (datetime): Timestamp when product was last updated
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    stock_level = models.IntegerField(default=0)
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Salesperson(models.Model):
    """
    Salesperson model representing sales team members.
    
    Attributes:
        name (str): Full name of the salesperson
        email (str): Unique email address
        phone (str): Contact phone number
        created_at (datetime): Timestamp when record was created
    """
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Sale(models.Model):
    """
    Sale model representing individual sales transactions.
    
    Attributes:
        customer_name (str): Name of the customer
        salesperson (Salesperson): Reference to the salesperson who made the sale
        product (Product): Reference to the product sold
        quantity (int): Number of units sold
        price_per_unit (float): Price per unit at time of sale
        total_price (float): Total price of the sale
        date_of_sale (datetime): When the sale occurred
        created_at (datetime): Timestamp when record was created
    """
    customer_name = models.CharField(max_length=200)
    salesperson = models.ForeignKey(Salesperson, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_per_unit = models.FloatField()
    total_price = models.FloatField()
    date_of_sale = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Override save method to calculate total price and adjust product stock before saving."""
        # Get the current product instance
        product_instance = self.product
        
        # If the sale is being created
        if self.pk is None:
            product_instance.stock_level -= self.quantity
        else:
            # If the sale is being updated, adjust stock based on the difference
            previous_sale = Sale.objects.get(pk=self.pk)
            quantity_difference = self.quantity - previous_sale.quantity
            product_instance.stock_level -= quantity_difference
        
        # Save the product instance to update stock level
        product_instance.save()
        
        # Calculate total price
        self.total_price = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale to {self.customer_name} by {self.salesperson.name}"

    @classmethod
    def get_monthly_revenue(cls):
        """Calculate total revenue for the current month."""
        current_month = timezone.now().month
        return cls.objects.filter(
            date_of_sale__month=current_month
        ).aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0

    @classmethod
    def get_monthly_sales_count(cls):
        """Get total number of sales for the current month."""
        current_month = timezone.now().month
        return cls.objects.filter(date_of_sale__month=current_month).count()

    class Meta:
        ordering = ['-date_of_sale']

# Signal handlers
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from dashboard.consumers import trigger_dashboard_update

@receiver(post_save, sender=Sale)
def sale_saved_handler(sender, instance, created, **kwargs):
    """
    Signal handler for sale creation and updates.
    Triggers dashboard update when a sale is created or modified.
    """
    try:
        trigger_dashboard_update()
    except Exception as e:
        logger.error(f"Error triggering dashboard update on sale save: {e}")

@receiver(post_delete, sender=Sale)
def sale_deleted_handler(sender, instance, **kwargs):
    """
    Signal handler for sale deletion.
    Triggers dashboard update when a sale is deleted.
    """
    try:
        trigger_dashboard_update()
    except Exception as e:
        logger.error(f"Error triggering dashboard update on sale deletion: {e}")
