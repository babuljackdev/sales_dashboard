from django.urls import path
from . import views

urlpatterns = [
    # Dashboard views
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/api/chart-data/', views.dashboard_chart_data, name='dashboard-chart-data'),
    
    # Product management
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/new/', views.product_create, name='product-create'),
    path('products/<int:pk>/update/', views.product_update, name='product-update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product-delete'),
    
    # Salesperson management
    path('salespeople/', views.SalespersonListView.as_view(), name='salesperson-list'),
    path('salespeople/new/', views.salesperson_create, name='salesperson-create'),
    path('salespeople/<int:pk>/update/', views.salesperson_update, name='salesperson-update'),
    path('salespeople/<int:pk>/delete/', views.salesperson_delete, name='salesperson-delete'),
] 