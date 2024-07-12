from django import forms

from .models import Resume


# creating a form
class ResumeForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Resume
        fields = "__all__"
