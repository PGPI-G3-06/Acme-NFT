from django.urls import path
from . import views

app_name = "acme-nft"
urlpatterns = [
    path('', views.index, name="index"),
    path("order-by-collections/", views.index, name="order-by-collections"),
    path("order-by-author/", views.index, name="order-by-author"),
    # Product detail
    path('product/<int:product_id>', views.product_detail, name="product_detail"),
    # Login page
    path("signin", views.signin, name="signin"),
    path("signup", views.signup, name="signup"),
    path("login", views.login, name="login"),
    path("signout", views.signout, name="signout"),
    # cart
    path("cart/add/<int:product_id>", views.add_to_cart, name="add_to_cart"),
    # wishlist
    path("wishlist/add/<int:product_id>", views.add_to_wishlist, name="add_to_wishlist"),
    # comments
    path("comments/add/<int:product_id>", views.add_comment, name="add_comment"),
    # Others
    path("hello/<int:user_id>", views.hello, name="hello"),
    path("error", views.error, name="error"),
    path("profile", views.edit_user, name="profile"),
    path("show-address/<int:user_id>", views.show_adrress, name="show-address"),
    path("new-address", views.new_address, name="new-address"),
    path("delete-address/<int:address_id>", views.delete_address, name="delete-address"),
    path("update-address/<int:address_id>", views.update_address, name="update-address"),

]