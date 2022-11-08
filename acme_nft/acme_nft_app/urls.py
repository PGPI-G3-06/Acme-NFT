from django.urls import path
from . import views

app_name = "acme-nft"
urlpatterns = [
    path('', views.index, name="index"), 
    # Product detail
    path('product/<int:product_id>', views.product_detail, name="product_detail"),
    # Login page
    path("login-page", views.login_page, name="login_page"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    # wishlist
    path("wishlist/add/<int:product_id>", views.add_to_wishlist, name="add_to_wishlist"),
    # Others
    path("hello/<int:user_id>", views.hello, name="hello"),
    path("error", views.error, name="error"),
]