from django.contrib import admin
from django.contrib.auth.models import User

# Register your models here.

from .models import *


class AddressInline(admin.StackedInline):
    model = Address
    extra = 1

class ComplaintInline(admin.TabularInline):
    model = Complaint
    extra = 1

class ProfilePictureInline(admin.TabularInline):
    model = ProfilePicture
    extra = 1

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff')
    inlines = [AddressInline, ComplaintInline, ProfilePictureInline]


class ProductInline(admin.StackedInline):
    model = Product
    extra = 1


class AuthorAdmin(admin.ModelAdmin):
    inlines = [ProductInline]

class OpinionInline(admin.StackedInline):
    model = Opinion
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'price', 'rarity')
    search_fields = ['name', 'author__name']
    inlines = [OpinionInline]

class ProductEntryAdmin(admin.ModelAdmin):
    list_display = ('product_display','stock_display','quantity', 'entry_type')

    def product_display(self, obj) -> str:
        return str(obj.product.id) + ' - ' + str(obj.product.name)

    def stock_display(self, obj) -> str:
        return obj.product.stock

    stock_display.short_description = 'Stock'


class OrderAdmin(admin.ModelAdmin):
    list_display = ('ref_code', 'payment_method', 'date', 'status')
    search_fields = ['ref_code', 'status']


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ProductEntry,ProductEntryAdmin)