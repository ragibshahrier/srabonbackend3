from django.db import models

# Create your models here.



from django.db import models
from django.contrib.auth.models import User
import hashlib
import uuid
import time

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    name = models.CharField(max_length=100,default='')
    email = models.EmailField(max_length=100,default='')
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=5)
    coursenumber = models.IntegerField(default=100)
    favsubjects = models.CharField(max_length=500, default='')


    def __str__(self):
        return f"{self.user.username}'s Profile"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    unique_id = models.CharField(max_length=32, unique=True, editable=False)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.unique_id:
            # Generate a unique id using timestamp and user id
            ts = int(time.time() * 1e6)  # microseconds for higher uniqueness
            self.unique_id = f"{self.user.id}_{ts}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Notification for {self.user.username} at {self.timestamp}"
