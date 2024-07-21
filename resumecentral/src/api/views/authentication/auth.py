from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from api.modules.template_paths import template_paths
import api.modules.mailer as mail_client
from api.forms.register import RegisterForm
from api.modules.hasher import compute_hash


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user_object = {
                "email": form.cleaned_data.get("email"),
                "username": form.cleaned_data.get("username"),
                "date_joined": form.cleaned_data.get("date_joined")
            }

            try:
                #generate temporary url
                hash_url = compute_hash(user_object)
                mail_client.send_verification_mail(user_object.get("email"), hash_url)

                if user_object.get("email").split("@")[1] != "computacenter.com":
                    raise ValueError("Invalid email domain")
                
                # Create the user instance but don"t save it to the database yet
                user = form.save(commit=False)
                
                # Update the temporary_field attribute with the hash_url
                user.temporary_field = hash_url
                
                # Now save the user instance
                user.save()
                
                login(request, user)
                return redirect("/user/")
            except ValueError as ve:
                form.add_error("email", str(ve))
            except Exception as e:
                form.add_error(None, str(e))

        return render(request, template_paths.get("auth_register"), {"form": form})
    else:
        form = RegisterForm()
    return render(request, template_paths.get("auth_register"), {"form": form})


def login(request):
    if request.user.is_authenticated:
        return redirect("/resumes")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/resumes")
            
        return redirect("/register")
    else:
        form = AuthenticationForm()
    return render(request, template_paths.get("auth_login"), {"form": form})

def logout(request):
    logout(request)
    return render(request, template_paths.get("auth_logout"))
