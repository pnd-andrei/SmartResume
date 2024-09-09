from django import forms
from django.contrib.auth.forms import UserCreationForm
from api.models.user import ApiUser

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Only computacenter emails'}))

    class Meta:
        model = ApiUser
        fields = ["username", "email", "password1", "password2"]
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.help_text = None
