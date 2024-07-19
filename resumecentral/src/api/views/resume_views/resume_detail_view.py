from django.shortcuts import get_object_or_404, render
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from api.models.resume_model import Resume
from api.serializers.resume_serializer import ResumeSerializer


class IndividualResumeApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, id, *args, **kwargs):
        """
        Retrieve and display the resume for the given id.
        """
        resume = get_object_or_404(Resume, id=id)
        serializer = ResumeSerializer(resume)

        resume_data = serializer.data
        resume_data_list = [(key, value) for key, value in resume_data.items()]

        resource = resume_data.get("file_upload")
        resume_id = resume_data.get("id")

        context = {
            "resume_data": resume_data_list,
            "resource": resource,
            "id": resume_id,
        }

        return render(request, "resume_templates/resume_detail.html", context)
