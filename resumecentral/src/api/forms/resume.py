from django import forms

from api.models.resume_model import Resume

# creating a form
class ResumeForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Resume
        fields = "__all__"
