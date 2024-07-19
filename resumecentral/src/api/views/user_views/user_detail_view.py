from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from api.models.api_user import ApiUser
from api.serializers.user_serializer import UserSerializer 
from django.shortcuts import get_object_or_404

class IndividualUserApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Retrieve and display the resume for the given id.
        """
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)



class TempValidationUserView(APIView):
    def get(self, request, temp, *args, **kwargs):
        """
        Retrieve and validate the user coresponding to the given temporary field.
        """
        if temp != "":
            user = get_object_or_404(ApiUser, temporary_field=temp)
            
            response_data = {
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
            }

            user.is_staff = True
            user.temporary_field = ""
            user.save()
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)