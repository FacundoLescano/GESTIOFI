from django import forms
from .models import Company
from web.models import Sale

class CompanyCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    class Meta:
        model = Company
        fields = ['username', 'email', 'password']


class SaleForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True)
    products = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple, required=True)
    enterprise = forms.CharField(max_length=100, required=True)
    class Meta:
        model = Sale
        fields = ['name', 'products', 'enterprise']