from django.urls import path
from authe.views import CreateUserView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("login/", LoginView.as_view(template_name="authe/login.html"), name="login"),
    path("create_user/", CreateUserView.as_view(), name="create_user"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]
