from rest_framework import serializers

from api.models.user import ApiUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiUser
        fields = "__all__"
