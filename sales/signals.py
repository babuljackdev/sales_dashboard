from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Sale
from dashboard.consumers import trigger_dashboard_update

@receiver(post_save, sender=Sale)
def sale_saved_handler(sender, instance, created, **kwargs):
    """Handle sale create and update events"""
    trigger_dashboard_update()

@receiver(post_delete, sender=Sale)
def sale_deleted_handler(sender, instance, **kwargs):
    """Handle sale delete events"""
    trigger_dashboard_update() 