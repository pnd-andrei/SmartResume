from django.shortcuts import render
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from api.models.resume import Resume
from api.modules.template_paths import template_paths


class SearchDashboardApiView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        List all the resume items: by a description
        """

        resume_count = Resume.objects.count()

        return render(request, template_paths.get("search_dashboard"), {"count":resume_count})
