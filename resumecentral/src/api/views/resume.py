# Create your views here.

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..forms.resume import ResumeForm
from ..models import Resume
from ..serializers import ResumeSerializer


class ResumeApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        """
        List all the resume items for given requested user
        """
        resumes = Resume.objects 

        if resumes:
            serializer = ResumeSerializer(resumes, many=True)
            form = ResumeForm()
            logs = []
            for obj in serializer.data:
                logobj = (
                     obj, obj.get('id')
                )
                logs.append(logobj)
                
            return render(
                request, "add_resume.html", {"form": form, "logs": logs}
            )

        return Response(status=status.HTTP_404_NOT_FOUND)

    # 2. Create
    def post(self, request, *args, **kwargs):
        form = ResumeForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save()  # Save form data and get the instance
            print(f"Resume saved: {instance}")  # Debug output
            return Response(
                {"message": "Resume created successfully"},
                status=status.HTTP_201_CREATED,
            )

        print(form.errors)  # Debug output for form errors
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
