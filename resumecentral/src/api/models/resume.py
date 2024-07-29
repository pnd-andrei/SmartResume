from django.db import models


class Resume(models.Model):
    description = models.CharField(max_length=1024, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, blank=True)
    file_upload = models.FileField()

    def __str__(self):
        return self.description
