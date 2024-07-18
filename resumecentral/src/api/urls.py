from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from api.views.register_views.resume_delete_view import DeleteResumeApiView
from api.views.register_views.resume_detail_view import IndividualResumeApiView
from api.views.register_views.resume_list_view import ResumeApiView

static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = [
    path("", ResumeApiView.as_view()),
    path("id=<int:id>", IndividualResumeApiView.as_view()),
    path("delete/id=<int:id>", DeleteResumeApiView.as_view()),
]
