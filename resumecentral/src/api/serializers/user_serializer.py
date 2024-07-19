from rest_framework import serializers
from api.models.api_user import ApiUser
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiUser
        fields = "__all__"

