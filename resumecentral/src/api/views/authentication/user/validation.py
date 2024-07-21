from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models.user import ApiUser


class TempValidationUserView(APIView):
    def get(self, request, temp, *args, **kwargs):
        """
        Retrieve and validate the user coresponding to the given temporary field.
        """
        if temp != "":
            user = get_object_or_404(ApiUser, temporary_field=temp)

            user.is_staff = True
            user.temporary_field = ""
            user.save()
            
            response_data = {
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "temporary_field": user.temporary_field,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)