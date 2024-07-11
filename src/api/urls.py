from django.urls import path

from .views.resume import (
    ResumeApiView,
)

urlpatterns = [
    path('', ResumeApiView.as_view()),
]
