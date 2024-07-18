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

import config.auth_views.auth_view as auth_views


#add in robots.txt dissalow media scanning

urlpatterns = [
    path("admin/", admin.site.urls),
    path("resumes/", include(resume_urls)),
    path('register/', auth_views.register, name='register'),
    path('login/', auth_views.user_login, name='login'),
    path('logout/', auth_views.user_logout, name='logout'),
]