from django import forms
from .models import Sale, Product, Salesperson

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer_name', 'salesperson', 'product', 'quantity', 'price_per_unit']
        widgets = {
            'date_of_sale': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
