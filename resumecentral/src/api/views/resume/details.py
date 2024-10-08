from django.shortcuts import get_object_or_404, render
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from api.models.resume import Resume
from api.modules.template_paths import template_paths
from api.serializers.resume import ResumeSerializer



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
        description = next(value for key, value in resume_data_list if key == 'description').split(".pdf")[0]

        resource = resume_data.get("file_upload")
        resume_id = resume_data.get("id")

        context = {
            "resume_data": resume_data_list,
            "resource": resource,
            "id": resume_id,
            "description": description
        }

        return render(request, template_paths.get("resume_detail"), context)
