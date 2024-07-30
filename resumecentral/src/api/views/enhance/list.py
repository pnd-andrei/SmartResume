from django.shortcuts import render
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from api.models.resume import Resume

from api.modules.template_paths import template_paths
from api.serializers.resume import ResumeSerializer


class EnhanceListApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        List all the resume items: by a description
        """
        resumes = Resume.objects.all()
        serializer = ResumeSerializer(resumes, many=True)

        entries = [
            (resume.get("id"), resume.get("file_upload"), resume.get("description"))
            for resume in serializer.data
        ]

        return render(request, template_paths.get("enhance_list"), {"entries": entries})
