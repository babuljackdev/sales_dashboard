from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField, Q, DateField, Min
from django.db.models.functions import ExtractWeek, ExtractDay, ExtractMonth, ExtractYear
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from sales.models import Sale, Product, Salesperson
from .forms import ProductForm, SalespersonForm
import logging

logger = logging.getLogger(__name__)

def dashboard(request):
    """
    Main dashboard view displaying sales metrics and analytics.
    """
    try:
        context = get_dashboard_context()
        return render(request, 'dashboard/dashboard.html', context)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        messages.error(request, "An error occurred while loading the dashboard.")
        return redirect('sale-list')

def dashboard_data(request):
    """API endpoint for real-time dashboard updates"""
    return JsonResponse(get_dashboard_context())

def dashboard_chart_data(request):
    """
    API endpoint for chart data.
    Provides time-series data for sales trends and revenue by salesperson.
    """
    try:
        time_range = request.GET.get('timeRange', 'daily')
        today = timezone.now()
        
        # Adjust the date range based on time_range
        if time_range == 'weekly':
            start_date = today - timedelta(weeks=8)  # Show last 8 weeks
        elif time_range == 'monthly':
            start_date = today - timedelta(days=180)  # Show last 6 months
        else:
            start_date = today - timedelta(days=30)  # Show last 30 days
        
        # Get sales trends based on time range
        sales_trends = get_sales_trends(start_date, time_range)
        
        # Get revenue by salesperson for the entire period
        revenue_by_salesperson = Sale.objects.filter(
            date_of_sale__gte=start_date
        ).values('salesperson__name').annotate(
            total_revenue=Sum(F('quantity') * F('price_per_unit'))
        ).order_by('-total_revenue')
        
        return JsonResponse({
            'sales_trends': list(sales_trends),
            'revenue_by_salesperson': list(revenue_by_salesperson)
        })
    except Exception as e:
        logger.error(f"Error fetching chart data: {e}")
        return JsonResponse({'error': 'Failed to load chart data'}, status=500)

def get_dashboard_context():
    """
    Helper function to get dashboard context data.
    
    Returns:
        dict: Dashboard metrics including revenue, sales, top products, and inventory status
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
        logger.error(f"Error getting dashboard context: {e}")
        return {
            'error': 'Failed to load dashboard metrics',
            'total_revenue': 0,
            'revenue_change': 0,
            'total_sales': 0,
            'sales_change': 0,
            'top_product': None,
            'top_products': [],
            'low_stock_products': [],
            'low_stock_count': 0
        }

def get_sales_trends(start_date, time_range='daily'):
    """
    Helper function to get sales trends data.
    
    Args:
        start_date (datetime): Start date for the trend data
        time_range (str): Time grouping - 'daily', 'weekly', or 'monthly'
    
    Returns:
        list: Time series data with dates and revenue
    """
    try:
        sales = Sale.objects.filter(date_of_sale__gte=start_date)
        
        if time_range == 'weekly':
            # Group by week using proper database functions
            sales = sales.annotate(
                week=ExtractWeek('date_of_sale'),
                year=ExtractYear('date_of_sale')
            ).values('year', 'week').annotate(
                daily_revenue=Sum(F('quantity') * F('price_per_unit')),
                week_start=Min('date_of_sale__date')
            ).order_by('year', 'week')
            
            return [{
                'date': item['week_start'].isoformat(),
                'daily_revenue': float(item['daily_revenue'] or 0)
            } for item in sales]
            
        elif time_range == 'monthly':
            # Group by month using proper database functions
            sales = sales.annotate(
                month=ExtractMonth('date_of_sale'),
                year=ExtractYear('date_of_sale')
            ).values('year', 'month').annotate(
                daily_revenue=Sum(F('quantity') * F('price_per_unit')),
                month_start=Min('date_of_sale__date')
            ).order_by('year', 'month')
            
            return [{
                'date': item['month_start'].isoformat(),
                'daily_revenue': float(item['daily_revenue'] or 0)
            } for item in sales]
            
        else:
            # Daily data
            sales = sales.values('date_of_sale__date').annotate(
                daily_revenue=Sum(F('quantity') * F('price_per_unit'))
            ).order_by('date_of_sale__date')
            
            return [{
                'date': item['date_of_sale__date'].isoformat(),
                'daily_revenue': float(item['daily_revenue'] or 0)
            } for item in sales]
    except Exception as e:
        logger.error(f"Error getting sales trends: {e}")
        return []

def calculate_percentage_change(current, previous):
    """
    Helper function to calculate percentage change between two values.
    
    Args:
        current (float): Current value
        previous (float): Previous value
    
    Returns:
        float: Percentage change, rounded to 1 decimal place
    """
    if not previous:
        return 100 if current else 0
    return round(((current - previous) / previous) * 100, 1)

class ProductListView(ListView):
    """List view for displaying all products."""
    model = Product
    template_name = 'dashboard/product_list.html'
    context_object_name = 'products'
    ordering = ['-created_at']

def product_create(request):
    """View for creating a new product."""
    try:
        if request.method == 'POST':
            form = ProductForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product created successfully!')
                return redirect('product-list')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = ProductForm()
        return render(request, 'dashboard/product_form.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in product_create view: {e}")
        messages.error(request, "An error occurred while creating the product.")
        return redirect('product-list')

def product_update(request, pk):
    """View for updating an existing product."""
    try:
        product = get_object_or_404(Product, pk=pk)
        if request.method == 'POST':
            form = ProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product updated successfully!')
                return redirect('product-list')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = ProductForm(instance=product)
        return render(request, 'dashboard/product_form.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in product_update view: {e}")
        messages.error(request, "An error occurred while updating the product.")
        return redirect('product-list')

def product_delete(request, pk):
    """View for deleting an existing product."""
    try:
        product = get_object_or_404(Product, pk=pk)
        if request.method == 'POST':
            product.delete()
            messages.success(request, 'Product deleted successfully!')
            return redirect('product-list')
        return render(request, 'dashboard/product_confirm_delete.html', {'product': product})
    except Exception as e:
        logger.error(f"Error in product_delete view: {e}")
        messages.error(request, "An error occurred while deleting the product.")
        return redirect('product-list')

class SalespersonListView(ListView):
    """List view for displaying all salespeople."""
    model = Salesperson
    template_name = 'dashboard/salesperson_list.html'
    context_object_name = 'salespeople'
    ordering = ['-created_at']

def salesperson_create(request):
    """View for creating a new salesperson."""
    try:
        if request.method == 'POST':
            form = SalespersonForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Salesperson created successfully!')
                return redirect('salesperson-list')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = SalespersonForm()
        return render(request, 'dashboard/salesperson_form.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in salesperson_create view: {e}")
        messages.error(request, "An error occurred while creating the salesperson.")
        return redirect('salesperson-list')

def salesperson_update(request, pk):
    """View for updating an existing salesperson."""
    try:
        salesperson = get_object_or_404(Salesperson, pk=pk)
        if request.method == 'POST':
            form = SalespersonForm(request.POST, instance=salesperson)
            if form.is_valid():
                form.save()
                messages.success(request, 'Salesperson updated successfully!')
                return redirect('salesperson-list')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = SalespersonForm(instance=salesperson)
        return render(request, 'dashboard/salesperson_form.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in salesperson_update view: {e}")
        messages.error(request, "An error occurred while updating the salesperson.")
        return redirect('salesperson-list')

def salesperson_delete(request, pk):
    """View for deleting an existing salesperson."""
    try:
        salesperson = get_object_or_404(Salesperson, pk=pk)
        if request.method == 'POST':
            salesperson.delete()
            messages.success(request, 'Salesperson deleted successfully!')
            return redirect('salesperson-list')
        return render(request, 'dashboard/salesperson_confirm_delete.html', {'salesperson': salesperson})
    except Exception as e:
        logger.error(f"Error in salesperson_delete view: {e}")
        messages.error(request, "An error occurred while deleting the salesperson.")
        return redirect('salesperson-list')

def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        sale.delete()  # Signal will handle the dashboard update
        messages.success(request, 'Sale deleted successfully!')
        return redirect('sale-list')
    return render(request, 'dashboard/sale_confirm_delete.html', {'sale': sale}) 