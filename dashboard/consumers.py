import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import datetime, timedelta
from sales.models import Sale, Product
from dashboard.views import calculate_percentage_change

logger = logging.getLogger(__name__)

class DashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time dashboard updates.
    
    Handles WebSocket connections for the dashboard, providing real-time
    updates of sales metrics, top products, and inventory status.
    """

    async def connect(self):
        """
        Handle WebSocket connection.
        Adds the client to the dashboard_updates group and sends initial data.
        """
        try:
            await self.channel_layer.group_add("dashboard_updates", self.channel_name)
            await self.accept()
            await self.send_dashboard_data()
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {e}")
            await self.close()

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        Removes the client from the dashboard_updates group.
        """
        try:
            await self.channel_layer.group_discard("dashboard_updates", self.channel_name)
        except Exception as e:
            logger.error(f"Error in WebSocket disconnection: {e}")

    async def dashboard_update(self, event):
        """
        Handle dashboard update events.
        Fetches fresh dashboard data and sends it to the WebSocket.
        """
        try:
            data = await self.get_dashboard_data()
            await self.send(text_data=json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending dashboard update: {e}")
            await self.send(text_data=json.dumps({
                'error': 'Failed to update dashboard data'
            }))

    async def send_dashboard_data(self):
        """Send current dashboard data to the WebSocket."""
        try:
            data = await self.get_dashboard_data()
            await self.send(text_data=json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending initial dashboard data: {e}")
            await self.send(text_data=json.dumps({
                'error': 'Failed to load dashboard data'
            }))

    @database_sync_to_async
    def get_dashboard_data(self):
        """
        Fetch and calculate all dashboard metrics.
        
        Returns:
            dict: Dashboard data including:
                - Total revenue and revenue change
                - Total sales and sales change
                - Top product details
                - Top selling products list
                - Low stock products list
        """
        try:
            today = timezone.now()
            start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_month_start = (start_of_month - timedelta(days=1)).replace(day=1)
            
            # Calculate current month metrics
            current_month_sales = Sale.objects.filter(date_of_sale__gte=start_of_month)
            current_month_revenue = current_month_sales.aggregate(
                total=Sum(F('quantity') * F('price_per_unit'))
            )['total'] or 0
            
            # Calculate last month metrics for comparison
            last_month_sales = Sale.objects.filter(
                date_of_sale__gte=last_month_start,
                date_of_sale__lt=start_of_month
            )
            last_month_revenue = last_month_sales.aggregate(
                total=Sum(F('quantity') * F('price_per_unit'))
            )['total'] or 0
            
            # Calculate percentage changes
            revenue_change = calculate_percentage_change(current_month_revenue, last_month_revenue)
            sales_change = calculate_percentage_change(
                current_month_sales.count(),
                last_month_sales.count()
            )
            
            # Get top product with serializable data
            top_product_query = Product.objects.annotate(
                total_quantity=Sum('sale__quantity'),
                revenue=Sum(F('sale__quantity') * F('sale__price_per_unit'))
            ).filter(
                sale__date_of_sale__gte=start_of_month
            ).order_by('-total_quantity').first()

            top_product = {
                'name': top_product_query.name if top_product_query else '',
                'total_quantity': getattr(top_product_query, 'total_quantity', 0) or 0,
                'revenue': float(getattr(top_product_query, 'revenue', 0) or 0)
            } if top_product_query else None
            
            # Get top selling products with serializable data
            top_products_query = Product.objects.annotate(
                total_quantity=Sum('sale__quantity'),
                revenue=Sum(F('sale__quantity') * F('sale__price_per_unit'))
            ).order_by('-total_quantity')[:5]

            top_products = [{
                'name': p.name,
                'total_quantity': p.total_quantity or 0,
                'revenue': float(p.revenue or 0),
                'stock_level': p.stock_level
            } for p in top_products_query]
            
            # Get low stock products with serializable data
            low_stock_query = Product.objects.filter(stock_level__lte=5).order_by('stock_level')
            low_stock_products = [{
                'name': p.name,
                'stock_level': p.stock_level
            } for p in low_stock_query]
            
            return {
                'total_revenue': float(current_month_revenue),
                'revenue_change': revenue_change,
                'total_sales': current_month_sales.count(),
                'sales_change': sales_change,
                'top_product': top_product,
                'top_products': top_products,
                'low_stock_products': low_stock_products,
                'low_stock_count': len(low_stock_products)
            }
        except Exception as e:
            logger.error(f"Error calculating dashboard data: {e}")
            return {
                'error': 'Failed to calculate dashboard metrics',
                'total_revenue': 0,
                'revenue_change': 0,
                'total_sales': 0,
                'sales_change': 0,
                'top_product': None,
                'top_products': [],
                'low_stock_products': [],
                'low_stock_count': 0
            }

def trigger_dashboard_update():
    """
    Utility function to trigger dashboard update from anywhere in the application.
    Sends update signal to all connected clients.
    """
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "dashboard_updates",
            {
                "type": "dashboard_update",
                "data": None  # Data will be fetched by each consumer
            }
        )
    except Exception as e:
        logger.error(f"Error triggering dashboard update: {e}")
        raise 