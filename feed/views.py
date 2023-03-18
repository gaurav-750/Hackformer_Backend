from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.generics import RetrieveAPIView, UpdateAPIView, CreateAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import User

from .models import Student, Post
from .serializers import ProfileSerializer, StudentSerializer, PostSerializer


# Create your views here
class StudentViewset(CreateModelMixin,
                     GenericViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentProfileView(RetrieveAPIView, UpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        username = self.kwargs.get('username')
        user = User.objects.get(username=username)
        student = Student.objects.select_related('user').get(
            user_id=user.id
        )
        return student


# todo Posts
class AllPost(ListAPIView, CreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        user = User.objects.get(id=self.request.user.id)
        student = Student.objects.get(user_id=user.id)
        return {
            "student_id": student.id
        }
