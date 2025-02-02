from django import forms
from sales.models import Sale, Product, Salesperson

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'stock_level', 'price']

class SalespersonForm(forms.ModelForm):
    class Meta:
        model = Salesperson
        fields = ['name', 'email', 'phone'] 