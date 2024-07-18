from django.db import models
from django.contrib.auth.models import AbstractUser

class ApiUser(AbstractUser):
    temporary_field = models.CharField(max_length=100)
