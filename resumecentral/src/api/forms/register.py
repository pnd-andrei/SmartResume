from django import forms
from django.contrib.auth.forms import UserCreationForm

from api.models.user import ApiUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = ApiUser
        fields = ["username", "email", "password1", "password2"]
