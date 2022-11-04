from sys import maxsize
from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=16, unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=40, blank=True)
    surname = models.CharField(max_length=60, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username