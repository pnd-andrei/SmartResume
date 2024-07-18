# Create your views here.

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.forms.resume import ResumeForm
from api.models.resume_model import Resume
from api.serializers import ResumeSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated

class IndividualResumeApiView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id, *args, **kwargs):
        """
        List the resume for given id
        """
        user = self.request.user  # Access user through self.request
        resume = get_object_or_404(Resume, id=id) #returns 404 if not found

        serializer = ResumeSerializer(resume)
        resume_data_list = [(key, value) for key, value in serializer.data.items()]

        resource = serializer.data.get("file_upload")
        resume_id = serializer.data.get("id")

        return render(
            request, "resume_templates/resume_detail.html", { "resume_data": resume_data_list, "resource": resource, "id": resume_id}
        )
        