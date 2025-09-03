from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin


class Company(AbstractUser, PermissionsMixin): 
    username = models.CharField(max_length=100, unique=True)    
    email = models.EmailField()
    password = models.CharField(max_length=100)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class Branch(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    enterprise = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)    

    def __str__(self):
        return self.name