from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.template.response import TemplateResponse
from rest_framework.views import APIView

from api.serializers.user import UserSerializer
from api.modules.template_paths import template_paths


class IndividualUserApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Retrieve and display the resume for the given id.
        """
        user = request.user
        serializer = UserSerializer(user)
        requestData = serializer.data

        # Remove the password field from the serialized data
        requestData.pop("password", None)

        return TemplateResponse(
            request,
            template_paths.get("response"),
            {"entries": requestData},
            status=status.HTTP_200_OK,
        )
