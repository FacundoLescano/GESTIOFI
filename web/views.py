from .models import Sale, Product
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from authe.form import SaleForm

class getproductsView(LoginRequiredMixin, ListView):
    model = Product
    context_object_name = "Products"
    template_name = "web/getProducts.html"

    def get_queryset(self):
        return Product.objects.filter(empresa=self.request.user)
    
class CreateSaleView(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = "web/CreateSaleView.html"
    success_url = "/web/home/"

    def form_valid(self, form):
        form.instance.empresa = self.request.user
        return super().form_valid(form)