from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.modules.template_paths import template_paths
import asyncio
from resumecentral.src.controllers.ai_search import AISearch

def transform_special_chars_to_codes(input_string):
    # Initialize an empty list to store transformed characters
    transformed_string = []

    for char in input_string:
        # Check if the character is a special character
        if not char.isalnum() and not char.isspace():
            # Transform the special character to its Unicode code point
            transformed_char = f"\\u{ord(char):04x}"
            transformed_string.append(transformed_char)
        else:
            transformed_string.append(char)

    # Join the list into a single string and return it
    return ''.join(transformed_string)

class SearchResumesApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        List all the resume items: by a description
        """
        description = request.GET.get("description")

        sample_size = int(request.GET.get("sample_size"))

        relevance = request.GET.get("relevance")

        chunk_size = 250

        if request.GET.get("slider"):
            slider = int(request.GET.get("slider"))
            divider = pow(2, 4 - slider)
            chunk_size = int(chunk_size * divider)

        results = []
        results = AISearch.similarity_search(description, chunk_size)

        if relevance == "experience":
            results = asyncio.run(AISearch.sort_retrieved_docs_by_experience(results))

        if description and sample_size:
            entries = [
                (
                    {
                        "id": resume.metadata.get("id"),
                        "description": resume.metadata.get("description"),
                        "file_upload": resume.metadata.get("source").split('/static/')[-1],
                        "precision": resume.metadata.get("score"),
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
                    "description": transform_special_chars_to_codes(input_string=description),
                    "ui_description": description,
                    "sample_size": sample_size,
                },
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)
