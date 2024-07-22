from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.modules.template_paths import template_paths

from resumecentral.src.controllers.ai import AIController


class SearchResumesApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        List all the resume items: by a description
        """
        description = request.GET.get("description")
        sample_size = int(request.GET.get("sample_size"))

        results = AIController.similarity_search(description,sample_size)

        if description and sample_size:
            entries = [
                (
                    {
                        "id": resume.metadata.get("id"),
                        "file_upload": resume.metadata.get("source"), 
                        "precision": resume.metadata.get("score")
                    },
                    resume.metadata.get("id"),
                )
                for resume in results[:sample_size]
            ]

            return render(
                request,
                template_paths.get("search_list"),
                {
                    "entries": entries,
                    "description": description,
                    "sample_size": sample_size,
                },
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)
