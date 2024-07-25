from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.modules.template_paths import template_paths
import asyncio
from resumecentral.src.controllers.ai import AIController


class SearchResumesApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        List all the resume items: by a description
        """
        description = request.GET.get("description")
        relevance = request.GET.get("relevance")

        sample_size = int(request.GET.get("sample_size"))

        chunk_size = 512

        #if request.GET.get("slider"):
            #slider = int(request.GET.get("slider"))
            #divider = pow(4,4-slider+1)
            #chunk_size = int(chunk_size / divider)

        results = []
        results = AIController.similarity_search(description,chunk_size)

        if relevance == "experience":
            results = asyncio.run(AIController.sort_retrieved_docs_by_experience(results))

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
