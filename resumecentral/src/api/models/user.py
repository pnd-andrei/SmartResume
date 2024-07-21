from django.contrib.auth.models import AbstractUser
from django.db import models


class ApiUser(AbstractUser):
    email = models.EmailField(unique=True) #make mail unique
    temporary_field = models.CharField(max_length=100)
