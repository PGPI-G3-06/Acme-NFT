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

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff')
    inlines = [AddressInline, ComplaintInline]


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
    inlines = [OpinionInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(ProductEntry)