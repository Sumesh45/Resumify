from django.db import models
from django.contrib.auth.models import User
from .validators import validate_file_size

class Resume_data(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.CharField(max_length=15)
    experience = models.IntegerField()
    skills = models.TextField()
    file = models.FileField(upload_to='resumes/', validators=[validate_file_size])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"
