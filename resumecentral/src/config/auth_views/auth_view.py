from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from api.forms.register_form import RegisterForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/resumes')
        return redirect('/register')
    else:
        form = RegisterForm()
    return render(request, 'auth_templates/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/resumes')
            
        return redirect('/register')
    else:
        form = AuthenticationForm()
    return render(request, 'auth_templates/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return render(request, 'auth_templates/logout.html')
