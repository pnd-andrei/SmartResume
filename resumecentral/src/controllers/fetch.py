import django
import sys
import os

controller_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(controller_dir)

sys.path.append(src_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from api.models.resume_model import Resume
from api.serializers.resume_serializer import ResumeSerializer


def fetch_resumes():
    resumes = Resume.objects.all()
    serializer = ResumeSerializer(resumes, many=True)

    return serializer.data


if __name__ == "__main__":
    print(fetch_resumes())
