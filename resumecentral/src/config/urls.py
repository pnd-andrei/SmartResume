"""
URL configuration for ResumeCentral-vPRO project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from api import urls as resume_urls
from django.contrib import admin
from django.urls import include, path

from django.http import HttpResponseForbidden
from django.views.static import serve as static_serve
from django.urls import re_path
from django.conf import settings


urlpatterns = [
    path("admin/", admin.site.urls),
    path("resumes/", include(resume_urls)),
]

def protected_media(request, path):
    print("request")
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You are not allowed to access this file")
    return static_serve(request, path, document_root=settings.MEDIA_ROOT)

#protected path
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', protected_media, name='protected_media')   
    ]