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

from django.contrib import admin
from django.urls import include, path

import api.views.authentication.auth as auth_views
import api.views.authentication.user.validation as temp_validation_views
import api.views.authentication.user.detail as user_views
from api import urls as resume_urls

# add in robots.txt dissalow media scanning

urlpatterns = [
    path("admin/", admin.site.urls),
    path("resumes/", include(resume_urls)),
    path('register/', auth_views.user_register, name='register'),
    path('login/', auth_views.user_login, name='login'),
    path('logout/', auth_views.user_logout, name='logout'),
    path('validate/<str:temp>', temp_validation_views.TempValidationUserView.as_view()),
    path('user/', user_views.IndividualUserApiView.as_view()),
]
