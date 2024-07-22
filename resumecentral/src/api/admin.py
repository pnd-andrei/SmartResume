from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api.models.user import ApiUser

# Register model
admin.site.register(ApiUser, UserAdmin)
