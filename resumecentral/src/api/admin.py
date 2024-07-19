from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api.models.api_user import ApiUser

# Register model
admin.site.register(ApiUser, UserAdmin)
