from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


class EnhanceResumeApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        List all the resume items: by a description
        """
        description = request.GET.get("description")
        resume_id = request.GET.get("resume_id")
        print(description)
        print(resume_id)

        return Response(status=status.HTTP_400_BAD_REQUEST)
