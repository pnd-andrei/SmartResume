# Create your views here.

from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..forms.resume import ResumeForm
from ..models import Resume
from ..serializers import ResumeSerializer


class IndividualResumeApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        """
        List the resume for given id
        """
        resume = get_object_or_404(Resume, id=id)  # returns 404 if not found

        serializer = ResumeSerializer(resume)
        resume_data_list = [(key, value) for key, value in serializer.data.items()]

        resource = serializer.data.get("file_upload")

        return render(
            request,
            "resume_detail.html",
            {"resume_data": resume_data_list, "resource": resource},
        )
