from django.urls import path
from web.views import getproductsView, CreateSaleView, CreateProductView, DeleteProductView, MyaccountView, GeneratePDFView, DeleteSaleView, TotalSaleDayView, PageWelcome

urlpatterns = [
    path("welcome/", PageWelcome.as_view(), name="welcome"),
    path("home/", getproductsView.as_view(), name="home"),
    path("create_sale/", CreateSaleView.as_view(), name="create_sale"),
    path("create_product/", CreateProductView.as_view(), name="create_product"),
    path("delete_product/<int:pk>/", DeleteProductView.as_view(), name="delete_product"),
    path("my_account/", MyaccountView.as_view(), name="my_account"),
    path("generate_report/", GeneratePDFView.as_view(), name="generate_report"),
    path("delete_sale/<int:pk>/", DeleteSaleView.as_view(), name="delete_sale"),
    path("total_sales_day/", TotalSaleDayView.as_view(), name="total_sales_day"),
]
