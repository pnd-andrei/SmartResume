from django import forms

from api.models.resume_model import Resume


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = "__all__"
