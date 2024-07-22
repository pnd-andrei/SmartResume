import os
import sys

import django

controller_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(controller_dir)

sys.path.append(src_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from api.models.resume import Resume
from api.serializers.resume import ResumeSerializer


def fetch_resumes(url):
    resumes = Resume.objects.all()
    serializer = ResumeSerializer(resumes, many=True)

    return [[x.get("id") , url + "/media" + x.get("file_upload")] for x in serializer.data]
