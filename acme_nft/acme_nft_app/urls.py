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
    path("cart", views.cart_view, name="cart"),
    path("cart/update-quantity/<int:product_id>", views.edit_amount_cart, name="update_quantity"),
    path("cart/delete/<int:product_id>", views.delete_from_cart, name="delete_from_cart"),
    path("cart/resume", views.resume_cart_view, name="resume_cart"),
    path("cart/add-address", views.add_address_in_cart, name="add_address_in_cart"),
    path("cart/resueme/pay", views.payment, name="payment"),

    # Wishlist
    path("wishlist/add/<int:product_id>", views.add_to_wishlist, name="add_to_wishlist"),
    
    # Comments
    path("comments/add/<int:product_id>", views.add_comment, name="add_comment"),
    
    # Address
    path("address/show/<int:user_id>", views.show_adrress, name="show_address"),
    path("address/new", views.new_address, name="new_address"),
    path("address/delete/<int:address_id>", views.delete_address, name="delete_address"),
    path("address/update/<int:address_id>", views.update_address, name="update_address"),
   

    # Customer Service
    path("customerservice", views.customer_service, name="customerservice"),
    path("complaint", views.complaint, name="complaint"),
    path("opinion", views.opinion, name="opinion"),
    path("opinions", views.opinions, name="opinions"),

    # Orders
    path("orders", views.orders, name="orders"),
    path("order/<int:order_id>", views.order, name="order"),
    
    # Others
    path("hello/<int:user_id>", views.hello, name="hello"),
    path("error", views.error, name="error"),
    path("profile", views.edit_user, name="profile"),

    # Admin
    path("admins/products", views.AdminListProducts.as_view(), name="admin"),
    path("admins/products/<int:product_id>",views.update_product, name="admin_detail"),
    path("admins/products/new", views.create_product, name="admin_new_product"),


]

