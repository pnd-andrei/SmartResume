from rest_framework import serializers

from api.models.resume import Resume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = "__all__"
