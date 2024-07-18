from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from api.serializers.user_serializer import UserSerializer 


class IndividualUserApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve and display the resume for the given id.
        """
        user = request.user
        serializer = UserSerializer(user)
        print(serializer)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
