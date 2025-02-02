from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta, datetime
import csv
import logging

from .models import Sale, Salesperson, Product
from .forms import SaleForm

logger = logging.getLogger(__name__)

def sale_list(request):
    """
    View for displaying sales with search, filtering, and pagination functionality.
    
    Supports:
    - Search by customer name, product name, or salesperson name
    - Filter by salesperson
    - Filter by date range
    - Pagination (10 items per page)
    """
    try:
        # Get all sales
        sales_queryset = Sale.objects.all().order_by('-date_of_sale')
        
        # Search functionality
        search_query = request.GET.get('search')
        if search_query:
            sales_queryset = sales_queryset.filter(
                Q(customer_name__icontains=search_query) |
                Q(product__name__icontains=search_query) |
                Q(salesperson__name__icontains=search_query)
            )
        
        # Filter by salesperson
        salesperson_id = request.GET.get('salesperson')
        if salesperson_id:
            sales_queryset = sales_queryset.filter(salesperson_id=salesperson_id)
        
        # Filter by date range
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        if date_from:
            sales_queryset = sales_queryset.filter(date_of_sale__gte=date_from)
        if date_to:
            sales_queryset = sales_queryset.filter(date_of_sale__lte=date_to)
        
        # Pagination
        paginator = Paginator(sales_queryset, 10)
        page = request.GET.get('page')
        sales = paginator.get_page(page)
        
        context = {
            'sales': sales,
            'salespeople': Salesperson.objects.all(),
        }
        return render(request, 'sales/sale_list.html', context)
    except Exception as e:
        logger.error(f"Error in sale_list view: {e}")
        messages.error(request, "An error occurred while loading the sales list.")
        return redirect('dashboard')

def sale_create(request):
    """
    View for creating a new sale.
    Handles both GET (form display) and POST (form submission) requests.
    """
    try:
        if request.method == 'POST':
            form = SaleForm(request.POST)
            if form.is_valid():
                sale = form.save(commit=False)
                sale.save()
                messages.success(request, 'Sale created successfully!')
                return redirect('sale-list')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = SaleForm()
            products = Product.objects.all()
            form.fields['product'].queryset = products
            form.fields['product'].choices = [(p.id, f"{p.name} (${p.price})") for p in products]

        return render(request, 'sales/sale_form.html', {'form': form})
    except Exception as e:
        logger.error(f"Error in sale_create view: {e}")
        messages.error(request, "An error occurred while creating the sale.")
        return redirect('sale-list')

def sale_update(request, pk):
    """
    View for updating an existing sale.
    Handles both GET (form display) and POST (form submission) requests.
    """
    try:
        sale = get_object_or_404(Sale, pk=pk)
        products = Product.objects.all()
        if request.method == 'POST':
            form = SaleForm(request.POST, instance=sale)
            if form.is_valid():
                product_id = form.cleaned_data['product'].id
                quantity = form.cleaned_data['quantity']
                product = Product.objects.get(pk=product_id)
                if product.stock_level < quantity:
                    messages.error(request, f"Insufficient stock for {product.name}. Available stock: {product.stock_level}")
                    return render(request, 'sales/sale_form.html', locals())
                form.save()
                messages.success(request, 'Sale updated successfully!')
                return redirect('sale-list')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = SaleForm(instance=sale)
            
        return render(request, 'sales/sale_form.html', locals())
    except Exception as e:
        logger.error(f"Error in sale_update view: {e}")
        messages.error(request, "An error occurred while updating the sale.")
        return redirect('sale-list')

def sale_delete(request, pk):
    """
    View for deleting an existing sale.
    Requires confirmation via POST request.
    """
    try:
        sale = get_object_or_404(Sale, pk=pk)
        if request.method == 'POST':
            sale.delete()
            messages.success(request, 'Sale deleted successfully!')
            return redirect('sale-list')
        return render(request, 'sales/sale_confirm_delete.html', {'sale': sale})
    except Exception as e:
        logger.error(f"Error in sale_delete view: {e}")
        messages.error(request, "An error occurred while deleting the sale.")
        return redirect('sale-list')

def sale_create_multiple(request):
    """
    View for creating multiple sales at once.
    Handles bulk sale creation for a single customer.
    """
    try:
        if request.method == 'POST':
            customer_name = request.POST.get('customer_name')
            salesperson_id = request.POST.get('salesperson')
            products = request.POST.getlist('products[]')
            quantities = request.POST.getlist('quantities[]')
            prices = request.POST.getlist('prices[]')
            
            for product_id, quantity in zip(products, quantities):
                product = Product.objects.get(pk=product_id)
                if product.stock_level < int(quantity):
                    messages.error(request, f"Insufficient stock for {product.name}. Available stock: {product.stock_level}")
                    return render(request, 'sales/sale_create_multiple.html', locals())
            
            for product, quantity, price in zip(products, quantities, prices):
                Sale.objects.create(
                    customer_name=customer_name,
                    salesperson_id=int(salesperson_id),
                    product_id=int(product),
                    quantity=int(quantity),
                    price_per_unit=float(price),
                    date_of_sale=timezone.now()
                )
            
            messages.success(request, 'Sales created successfully!')
            return redirect('sale-list')
        
        context = {
            'salespeople': Salesperson.objects.all(),
            'products': Product.objects.all(),
        }
        return render(request, 'sales/sale_create_multiple.html', context)
    except Exception as e:
        logger.error(f"Error in sale_create_multiple view: {e}")
        messages.error(request, "An error occurred while creating multiple sales.")
        return redirect('sale-list')

def sale_export(request):
    """
    View for exporting sales data to CSV format.
    Applies the same filters as the sale list view.
    """
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="sales_export_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Customer', 'Salesperson', 'Product', 'Quantity', 'Price/Unit', 'Total', 'Date'])
        
        # Get filtered queryset
        sales_queryset = Sale.objects.all().order_by('-date_of_sale')
        
        # Apply filters if present
        search_query = request.GET.get('search')
        if search_query:
            sales_queryset = sales_queryset.filter(
                Q(customer_name__icontains=search_query) |
                Q(product__name__icontains=search_query) |
                Q(salesperson__name__icontains=search_query)
            )
        
        salesperson_id = request.GET.get('salesperson')
        if salesperson_id:
            sales_queryset = sales_queryset.filter(salesperson_id=salesperson_id)
        
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        if date_from:
            sales_queryset = sales_queryset.filter(date_of_sale__gte=date_from)
        if date_to:
            sales_queryset = sales_queryset.filter(date_of_sale__lte=date_to)
        
        for sale in sales_queryset:
            writer.writerow([
                sale.customer_name,
                sale.salesperson.name,
                sale.product.name,
                sale.quantity,
                sale.price_per_unit,
                sale.total_price,
                sale.date_of_sale.strftime("%Y-%m-%d")
            ])
        
        return response
    except Exception as e:
        logger.error(f"Error in sale_export view: {e}")
        messages.error(request, "An error occurred while exporting sales data.")
        return redirect('sale-list')
