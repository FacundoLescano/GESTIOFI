from django.db import models
from authe.models import Company

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    empresa = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Sale(models.Model):
    id_venta = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    products = models.ManyToManyField(Product, related_name='sales') 
    enterprise = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name