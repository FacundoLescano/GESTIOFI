from django.urls import path
from web.views import getproductsView, CreateSaleView

urlpatterns = [
    path("home/", getproductsView.as_view(), name="home"),
    path("create_sale/", CreateSaleView.as_view(), name="create_sale"),
]
