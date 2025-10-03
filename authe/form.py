from typing import Required
from django import forms
from django.forms import widgets
from .models import Company
from web.models import Sale, Product, SaleProduct
from django.forms import inlineformset_factory

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


class SaleForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'sale-name-input',
            'placeholder': 'Nombre'
        })
    )
    enterprise = forms.ModelChoiceField(
        queryset=Company.objects.all(), 
        required=True,
        widget=forms.Select(attrs={
            'class': 'sale-enterprise-select',
            'placeholder': 'Empresa'
        })
    )
    total = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False, 
        initial=0.00,
        widget=forms.NumberInput(attrs={
            'class': 'sale-total-input',
            'readonly': True
        })
    )
    
    class Meta:
        model = Sale
        fields = ['name', 'enterprise', 'total'] 

class SaleProductForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=True,
        widget=forms.Select(attrs={
            'class': 'sale-product-select',
            'placeholder': 'Seleccionar producto'
        })
    )
    quantity = forms.IntegerField(
        required=True,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'sale-quantity-input',
            'placeholder': 'Cantidad',
            'min': '1'
        })
    )
    
    class Meta:
        model = SaleProduct
        fields = ['product', 'quantity']
        
SaleProductFormSet= inlineformset_factory(
    Sale, 
    SaleProduct,
    form=SaleProductForm,
    fields=('product', 'quantity'), 
    extra=5, 
    max_num=None, 
    can_delete=False)