from django.shortcuts import redirect, render
from api.modules.template_paths import template_paths

def error_403(request, exception=None):
    return render(request, template_paths.get("error_response"), {}, status=403)

def error_500(request):
    return render(request, template_paths.get("error_response"), status=500)