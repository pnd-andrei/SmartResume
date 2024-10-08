from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from api.views.resume.delete import DeleteResumeApiView
from api.views.resume.details import IndividualResumeApiView
from api.views.resume.list import ResumeApiView
from api.views.search.dashboard import SearchDashboardApiView
from api.views.search.list import SearchResumesApiView
from api.views.resume.smart_detail import IndividualSmartResumeApiView
from api.views.enhance.list import EnhanceListApiView
from api.views.enhance.detail import EnhanceResumeApiView

static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# these url patterns are mapped to "resumes/<url_pattern>"
urlpatterns = [
    path("", ResumeApiView.as_view(), name="resume_list"),
    path("smart", IndividualSmartResumeApiView.as_view()),
    path("id=<int:id>", IndividualResumeApiView.as_view(), name="resume_detail"),
    path("delete/id=<int:id>", DeleteResumeApiView.as_view()),
    path("search/query/", SearchResumesApiView.as_view()),
    path("search/", SearchDashboardApiView.as_view()),
    path("enhance/", EnhanceListApiView.as_view()),
    path("enhance/query/", EnhanceResumeApiView.as_view()),
]
