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
    path("show-address/<int:user_id>", views.show_adrress, name="show-address"),
    path("new-address", views.new_address, name="new-address"),
    path("delete-address/<int:address_id>", views.delete_address, name="delete-address"),
    path("update-address/<int:address_id>", views.update_address, name="update-address"),



]