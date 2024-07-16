# Create your views here.

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..forms.resume import ResumeForm
from ..models import Resume
from ..serializers import ResumeSerializer
from django.http import JsonResponse

class ResumeApiView(APIView):
    # 1. List all
    def get(self, request, *args, **kwargs):
        """
        List all the resume items
        """
        resumes = Resume.objects 

        if resumes:
            if request.GET.get("json") != None:
                data = list(resumes.values())
                return JsonResponse({'data': data})            
            else:
                serializer = ResumeSerializer(resumes, many=True)
                form = ResumeForm() #dynamic form

                entires = []
                
                for resume in serializer.data:
                    entry = (resume, resume.get('id'))
                    entires.append(entry)
                    
                return render(
                    request, "resume_list.html", {"form": form, "entries": entires}
                )

        return Response(status=status.HTTP_404_NOT_FOUND)

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
            
            instance.save()

            return Response(
                {"message": "Resume created successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
