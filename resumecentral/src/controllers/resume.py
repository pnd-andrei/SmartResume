import django
import sys
import os


class ResumeController:
    def __init__(self) -> None:
        controller_dirname = os.path.dirname(os.path.abspath(__file__))
        source_dirname = os.path.dirname(controller_dirname)

        sys.path.append(source_dirname)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

        django.setup()


    def fetch_resumes(self):
        from api.models.resume import Resume 
        from api.serializers.resume import ResumeSerializer
        new_path = "new/fake/path"

        resumes = Resume.objects.all()
        serializer = ResumeSerializer(resumes, many=True)

        return serializer.data
    
    def fetch_pdfs(self):
        resumes = self.fetch_resumes()

        return ["media" + resume.get("file_upload") for resume in resumes]

