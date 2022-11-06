from django.urls import path
from . import views

app_name = "acme-nft"
urlpatterns = [
    path('', views.index, name="index"),
    path("login-page", views.login_page, name="login_page"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("hello/<int:user_id>", views.hello, name="hello"),
    path("error", views.error, name="error"),
    path("profile", views.edit_user, name="profile"),
]