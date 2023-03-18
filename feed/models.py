from django.db import models

from django.conf import settings
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Student(models.Model):
    # 1-1 field (Student - User)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    title = models.CharField(max_length=55)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=255)
    gender = models.CharField(max_length=20)
    college = models.TextField()
    college_city = models.CharField(max_length=100)
    current_year = models.CharField(max_length=15)
    branch = models.CharField(max_length=100)
    about_me = models.TextField()
    skills = ArrayField(models.CharField(max_length=50))

    isRestricted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.first_name + ' ' + self.user.last_name


class Post(models.Model):
    TYPE_PROJECT = '1'
    TYPE_HACKATHON = '2'
    TYPE_CHOICES = [
        (TYPE_PROJECT, 'Project'),
        (TYPE_HACKATHON, 'Hackathon'),
    ]

    # 1 student -> many Posts
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(
        max_length=1, choices=TYPE_CHOICES, default=TYPE_PROJECT)
    tags = ArrayField(models.CharField(max_length=100))
    created_at = models.DateTimeField(auto_now_add=True)
    likes = ArrayField(models.BigIntegerField(
        blank=True, null=True), null=True, blank=True)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    # *1 post -> many comments
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    # *1 Student -> many comments
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self) -> str:
        return self.content
