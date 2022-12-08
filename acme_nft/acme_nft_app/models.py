from sys import maxsize

from django.contrib.auth.models import User
from django.db import models
from enum import Enum

from django.template.defaultfilters import register


# Enum
class EntryType(models.TextChoices):
    cart = 'CART'
    order = 'ORDER'
    wishlist = 'WISHLIST'

class PaymentMethod(models.TextChoices):
    transference = 'TRANSFERENCIA'
    card = 'TARJETA'

class Status(models.TextChoices):
    sent = 'ENVIADO'
    on_transit = 'EN TRÁNSITO'
    
class RarityType(models.TextChoices):
    common = 'COMMON'
    rare = 'RARE'
    epic = 'EPIC'
    legendary = 'LEGENDARY'
    mythic = 'MYTHIC'


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
        address = ""
        address+= self.street_name + ", " + str(self.number)+ " "
        if self.block:
            address+= ", Bloque " + str(self.block) + " "
        if self.floor:
            address += ", " + str(self.floor)  + "º "
        if self.door != "":
            address += self.door + " "
        return   address  + self.city + ", " + str(self.code_postal)


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
    showcase = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
        
class Comment(models.Model):
    text = models.CharField(max_length=2000)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

class Opinion(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.title

class Contact(models.Model):
    name = models.CharField(max_length=60)
    email = models.EmailField()
    subject = models.CharField(max_length=60)
    message = models.TextField()
    def __str__(self):
        return self.name


class Order(models.Model):
    ref_code = models.CharField(max_length=60)
    payment_method = models.CharField(max_length=60, choices=[ (tag, tag.value) for tag in PaymentMethod])
    date = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=256)
    status = models.CharField(max_length=60, choices=[ (tag, tag.value) for tag in Status])


    def total(self):
        total = 0
        for entry in self.productentry_set.all():

            if entry.product.offer_price:
                total += entry.product.offer_price * entry.quantity
            else:
                total += entry.product.price * entry.quantity

        return total

    def user(self):
        return self.productentry_set.first().user

    def __str__(self):
        return self.ref_code

class ProductEntry(models.Model):
    quantity = models.IntegerField(null=True)
    entry_type = models.CharField(max_length=60, choices=[ (tag, tag.value) for tag in EntryType])
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    def total(self):

        if self.product.offer_price:
            return self.product.offer_price * self.quantity


        return self.quantity * self.product.price
    
    def __str__(self):
        return f'user_id: {self.user.id}, product_id: {self.product.id}, entry_type: {self.entry_type}'

class ProfilePicture(models.Model):
    image = models.ImageField(upload_to='profile_pictures', default='static/images/profile.png')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
