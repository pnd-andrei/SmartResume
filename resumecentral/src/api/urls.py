from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views.resume_detail_view import IndividualResumeApiView
from .views.resume_list_view import ResumeApiView

static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# these url patterns are mapped to "resumes/<url_pattern>"
urlpatterns = [
    path("", ResumeApiView.as_view()),
    path("id=<int:id>", IndividualResumeApiView.as_view()),
]
