from django.db import models

class Resume(models.Model):
    resume = models.CharField(max_length = 20000)
    timestamp = models.DateTimeField(auto_now_add = True, auto_now = False, blank = True)
    processed = models.BooleanField(default = False, blank = True)

    def __str__(self):
        return self.resume