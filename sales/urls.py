from django.urls import path
from . import views

urlpatterns = [
    # Sale management
    path('', views.sale_list, name='sale-list'),
    path('sales/new/', views.sale_create, name='sale-create'),
    path('sales/<int:pk>/update/', views.sale_update, name='sale-update'),
    path('sales/<int:pk>/delete/', views.sale_delete, name='sale-delete'),
    path('sales/create-multiple/', views.sale_create_multiple, name='sale-create-multiple'),
    path('sales/export/', views.sale_export, name='sale-export'),
]