from django.urls import path

from api.views.register_views.resume_list_view import ResumeApiView
from api.views.register_views.resume_detail_view import IndividualResumeApiView

from django.conf.urls.static import static
from django.conf import settings

from api.views.register_views.resume_delete_view import DeleteResumeApiView
import api.views.auth_views.auth_view as auth_views

static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = [
    path("", ResumeApiView.as_view()),
    path("id=<int:id>", IndividualResumeApiView.as_view()),
    path("delete/id=<int:id>", DeleteResumeApiView.as_view()),
    path('register/', auth_views.register, name='register'),
    path('login/', auth_views.user_login, name='login'),
    path('logout/', auth_views.user_logout, name='logout'),
]
