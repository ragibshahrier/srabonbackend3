from django.db import models

# Create your models here.



from django.db import models
from django.contrib.auth.models import User

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


