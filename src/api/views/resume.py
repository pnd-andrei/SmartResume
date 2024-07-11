# Create your views here.

from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Resume
from ..serializers import ResumeSerializer


class ResumeApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        """
        List all the todo items for given requested user
        """

        resumes = Resume.objects
        print(resumes)

        if resumes:
            serializer = ResumeSerializer(resumes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)

    # 2. Create
    def post(self, request, *args, **kwargs):
        """
        Create the Todo with given todo data
        """

        data = {
            "description": request.data.get("description"),
            "processed": False,
            "timestamp": f"{datetime.now()}",
            "cv_url": request.data.get("cv_url"),
        }

        serializer = ResumeSerializer(data=data)

        if serializer.is_valid():
            print("save")
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
