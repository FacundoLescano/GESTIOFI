from django.shortcuts import render
from django.http import HttpResponse
from .models import Company, Branch
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .form import CompanyCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password

class CreateUserView(CreateView):
    model = Company
    form_class = CompanyCreationForm
    template_name = "authe/CreateUserView.html"
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Encriptar la contraseña antes de guardar el objeto
        user = form.save(commit=False)
        user.password = make_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)