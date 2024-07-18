# Create your views here.

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.forms.resume import ResumeForm
from api.models.resume_model import Resume
from api.serializers import ResumeSerializer
from django.http import JsonResponse

import string
import secrets
from django.core.files.base import ContentFile
from rest_framework.permissions import IsAuthenticated


class ResumeApiView(APIView):
    permission_classes = [IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        """
        List all the resume items
        """
        resumes = Resume.objects.all() 

        if not resumes.exists():
            #return Response(status=status.HTTP_404_NOT_FOUND)
            pass

        if request.GET.get("json") is not None:
            data = list(resumes.values())
            return JsonResponse({'data': data})

        serializer = ResumeSerializer(resumes, many=True)
        form = ResumeForm()  # dynamic form
        entries = [(resume, resume.get('id')) for resume in serializer.data]

        return render(request, "resume_templates/resume_list.html", {"form": form, "entries": entries})

    # 2. Create
    def post(self, request, *args, **kwargs):
        form = ResumeForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)  # get instance but do not commit to db yet

            file_upload = form.cleaned_data.get("file_upload")

            # pdf checks
            if not file_upload.name.endswith('.pdf'):
                return Response("Uploaded file must be a pdf", status=status.HTTP_400_BAD_REQUEST)
            if file_upload.content_type != 'application/pdf':
                return Response("Uploaded file must be a pdf", status=status.HTTP_400_BAD_REQUEST)

            # Generate a random filename
            characters = string.ascii_letters + string.digits
            random_filename = ''.join(secrets.choice(characters) for _ in range(32)) + f"_{file_upload.name}.pdf"

            # Save the file with the new name
            instance.file_upload.save(random_filename, ContentFile(file_upload.read()))

            instance.save()

            return Response(
                {"message": "Resume created successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    