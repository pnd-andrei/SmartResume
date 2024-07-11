# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Resume
from ..serializers import ResumeSerializer
from ..forms import ResumeForm
from datetime import datetime
from django.shortcuts import render, redirect

class ResumeApiView(APIView):
    # add permission to check if user is authenticated
    #permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request, *args, **kwargs):
        '''
        List all the resume items for given requested user
        '''        
        resumes = Resume.objects 

        if resumes:
            serializer = ResumeSerializer(resumes, many=True)
            form = ResumeForm()
            return render(request, 'add_resume.html', {'form': form, 'logs': serializer.data})

        return Response(status=status.HTTP_404_NOT_FOUND)

    # 2. Create
    def post(self, request, *args, **kwargs):
        form = ResumeForm(request.POST, request.FILES)
        
        if form.is_valid():
            instance = form.save()  # Save form data and get the instance
            print(f"Resume saved: {instance}")  # Debug output
            return Response({'message': 'Resume created successfully'}, status=status.HTTP_201_CREATED)
        
        print(form.errors)  # Debug output for form errors
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


