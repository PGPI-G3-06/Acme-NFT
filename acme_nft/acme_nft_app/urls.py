from django.urls import path
from . import views

app_name = "acme-nft"
urlpatterns = [
    path('', views.index, name="index"), 
    # Product detail
    path('product/<int:product_id>', views.product_detail, name="product_detail"),
    # Login page
    path("signin", views.signin, name="signin"),
    path("signup", views.signup, name="signup"),
    path("login", views.login, name="login"),
    path("signout", views.signout, name="signout"),
    # Cart
    path("cart/add/<int:product_id>", views.add_to_cart, name="add_to_cart"),
    # Wishlist
    path("wishlist/add/<int:product_id>", views.add_to_wishlist, name="add_to_wishlist"),
    # Comments
    path("comments/add/<int:product_id>", views.add_comment, name="add_comment"),
    # Address
    path("address/show/<int:user_id>", views.show_adrress, name="show_address"),
    path("address/new", views.new_address, name="new_address"),
    path("address/delete/<int:address_id>", views.delete_address, name="delete_address"),
    path("address/update/<int:address_id>", views.update_address, name="update_address"),
    # Others
    path("hello/<int:user_id>", views.hello, name="hello"),
    path("error", views.error, name="error"),
    path("profile", views.edit_user, name="profile"),
]