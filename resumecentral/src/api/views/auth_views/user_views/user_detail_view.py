from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.user_serializer import UserSerializer


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
        requestData.pop('password', None)

        return Response(requestData, status=status.HTTP_200_OK)
