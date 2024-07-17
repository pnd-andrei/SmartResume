# Create your views here.

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.forms.resume import ResumeForm
from api.forms.resume import Resume
from api.serializers import ResumeSerializer
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

import os

class DeleteResumeApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        """
        List the resume for given id
        """
        resume = get_object_or_404(Resume, id=id) #returns 404 if not found
        serializer = ResumeSerializer(resume)
        file_upload = (serializer.data.get("file_upload"))

        try:
            resume.delete()
            os.remove("media" + file_upload)
        except Exception as ex:
            print(ex)

        return redirect('/resumes')
        