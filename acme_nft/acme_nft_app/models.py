from sys import maxsize
from django.db import models
from enum import Enum

# Enum
class EntryType(Enum):
    cart = 'CART'
    order = 'ORDER'
    wishlist = 'WISHLIST'

class PaymentMethod(Enum):
    cash_on_delivery = 'CASH_ON_DELIVERY'
    card = 'CARD'

class Status(Enum):
    received = 'RECEIVED'
    sent = 'SENT'
    on_transit = 'ON_TRANSIT'
    delivered = 'DELIVERED'
    
class RarityType(models.TextChoices):
    common = 'COMMON'
    rare = 'RARE'
    epic = 'EPIC'
    legendary = 'LEGENDARY'
    mythic = 'MYTHIC'

# Models.

class User(models.Model):
    username = models.CharField(max_length=16, unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=40, blank=True)
    surname = models.CharField(max_length=60, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Address(models.Model):
    street_name = models.CharField(max_length=60)
    number = models.IntegerField()
    block = models.IntegerField(null=True)
    floor = models.IntegerField(null=True)
    door = models.CharField(max_length=1, blank=True)
    city = models.CharField(max_length=60)
    code_postal = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.street_name + ", " + str(self.number) + ", Bloque " + str(self.block) + ", " + str(self.floor) + "º " + self.door + ", " + self.city + ", " + str(self.code_postal)


class Complaint(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.title

class Author(models.Model):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
        
    name = models.CharField(max_length=60)
    collection = models.TextField()
    price = models.FloatField()
    stock = models.IntegerField()
    image_url = models.CharField(max_length=255, blank=True)
    offer_price = models.FloatField(blank=True, null=True)
    rarity = models.CharField(max_length=60, choices=[ (rarity, rarity.value) for rarity in RarityType], default=RarityType.common)
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING, null=True)
    
    def __str__(self):
        return self.name
class Opinion(models.Model):
    text = models.CharField(max_length=2000)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Order(models.Model):
    ref_code = models.CharField(max_length=60)
    payment_method = models.CharField(max_length=60, choices=[ (tag, tag.value) for tag in PaymentMethod])
    date = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=256)
    status = models.CharField(max_length=60, choices=[ (tag, tag.value) for tag in Status])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.ref_code

class ProductEntry(models.Model):
    quantity = models.IntegerField(null=True)
    entry_type = models.CharField(max_length=60, choices=[ (tag, tag.value) for tag in EntryType])
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'user_id: {self.user.id}, product_id: {self.product.id}, entry_type: {self.entry_type}'
