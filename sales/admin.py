from django.contrib import admin

from .models import Product, Salesperson, Sale

admin.site.register(Product)
admin.site.register(Salesperson)
admin.site.register(Sale) 