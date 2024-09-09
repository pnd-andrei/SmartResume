import secrets
import string

from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.forms.resume import ResumeForm
from api.models.resume import Resume
from api.modules.template_paths import template_paths
from api.serializers.resume import ResumeSerializer
from django.template.response import TemplateResponse


class ResumeApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        List all the resume items.
        """
        resumes = Resume.objects.all()

        if request.GET.get("json") is not None:
            data = list(resumes.values())
            return JsonResponse({"data": data})

        serializer = ResumeSerializer(resumes, many=True)

        form = ResumeForm()  # Dynamic form

        entries = [(resume, resume.get("id")) for resume in serializer.data]

        return render(
            request,
            template_paths.get("resume_list"),
            {"form": form, "entries": entries},
        )

    def post(self, request, *args, **kwargs):
        """
        Create a new resume entry.
        """
        form = ResumeForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(
                commit=False
            )  # Get instance but do not commit to db yet

            file_upload = form.cleaned_data.get("file_upload")

            # PDF checks
            if (
                not file_upload.name.endswith(".pdf")
                or file_upload.content_type != "application/pdf"
            ):
                return Response(
                    "Uploaded file must be a PDF", status=status.HTTP_400_BAD_REQUEST
                )

            # Generate a random filename
            characters = string.ascii_letters + string.digits
            random_filename = (
                "".join(secrets.choice(characters) for _ in range(32))
                + f"_{file_upload.name}"
            )

            # Save the file with the new name
            instance.file_upload.save(random_filename, ContentFile(file_upload.read()))

            instance.save()

            return TemplateResponse(
                request,
                template_paths.get("response"),
                {"entries": {"Response": "Resume added sucessfully"}},
                status=status.HTTP_200_OK,
            )

        return Response(
            form.errors,
            template_name=template_paths.get("response"),
            status=status.HTTP_400_BAD_REQUEST,
        )
