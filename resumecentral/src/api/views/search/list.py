from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from api.models.resume import Resume
from api.serializers.resume import ResumeSerializer

from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api.modules.template_paths import template_paths

class SearchResumesApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        List all the resume items: by a description
        """
        description = request.GET.get("description")
        sample_size = request.GET.get("sample_size")

        if description and sample_size:
            resumes = Resume.objects.all()

            if request.GET.get("json") is not None:
                data = list(resumes.values())
                return JsonResponse({"data": data})

            serializer = ResumeSerializer(resumes, many=True)

            entries = [(
                {
                    "id": resume.get("id"), 
                    "file_upload": resume.get("file_upload")
                }, 
            
                resume.get("id")) for resume in serializer.data
            ]   
            
            print(entries)

            return render(
                request,
                template_paths.get("search_list"),
                {"entries": entries, "description": description, "sample_size": sample_size},
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)

