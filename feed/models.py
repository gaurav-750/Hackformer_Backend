from django.db import models

from django.conf import settings
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Student(models.Model):
    # 1-1 field (Student - User)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=255)
    gender = models.CharField(max_length=15)
    college = models.TextField()
    college_city = models.CharField(max_length=100)
    current_year = models.CharField(max_length=15)
    branch = models.CharField(max_length=100)
    about_me = models.TextField()
    skills = ArrayField(models.CharField(max_length=50))
