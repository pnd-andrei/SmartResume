import os

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.forms.resume import Resume
from api.serializers.resume import ResumeSerializer


class DeleteResumeApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, id, *args, **kwargs):
        """
        Delete the resume for given id
        """
        resume = get_object_or_404(Resume, id=id)

        serializer = ResumeSerializer(resume)
        file_upload = serializer.data.get("file_upload")

        try:
            resume.delete()
            if file_upload:
                file_path = "media" + file_upload
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as ex:
            print(ex)
            return Response(
                {"error": "An error occurred while deleting the resume."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return redirect(reverse("resume_list"))
