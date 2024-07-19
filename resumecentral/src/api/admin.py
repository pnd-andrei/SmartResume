# api/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from api.models.api_user import ApiUser

# Register your models here.
admin.site.register(ApiUser, UserAdmin)
