from django.urls import path

from .views.resume_list_view import ResumeApiView
from .views.resume_detail_view import IndividualResumeApiView

from django.conf.urls.static import static
from django.conf import settings

from .views.resume_delete_view import DeleteResumeApiView

static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = [
    path("", ResumeApiView.as_view()),
    path("id=<int:id>", IndividualResumeApiView.as_view()),
    path("delete/id=<int:id>", DeleteResumeApiView.as_view())
]
