from django.urls import path

from .views.resumes import ResumeApiView
from .views.render_resume import IndividualResumeApiView

from django.conf.urls.static import static
from django.conf import settings

static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = [
    path("", ResumeApiView.as_view()),
    path("id=<int:id>", IndividualResumeApiView.as_view())
]
