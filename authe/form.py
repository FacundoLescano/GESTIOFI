from typing import Required
from django import forms
from django.forms import widgets
from .models import Company
from web.models import Sale
from web.models import Product

class CompanyCreationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'formcontrollocura'}
        )
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'formcontrollocura'}
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={'class': 'formcontrollocura'}
        )
    )
    cuit = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'formcontrollocura'}
        )
    )
    city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={'class': 'formcontrollocura'}
        )
    )
    class Meta:
        model = Company
        fields = ['username', 'email', 'password', 'cuit', 'city']


class SaleForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True)
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(), 
        required=True,
        label="Select Products")
    enterprise = forms.ModelChoiceField(queryset=Company.objects.all(), required=True)
    total = forms.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        model = Sale
        fields = ['name', 'products', 'enterprise', 'total']
        

class ProductForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True)
    category = forms.CharField(max_length=50, required=False)
    price = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    stock = forms.IntegerField(min_value=0, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)
    empresa = forms.ModelChoiceField(queryset=Company.objects.all(), required=True)
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'description', 'category', 'empresa']