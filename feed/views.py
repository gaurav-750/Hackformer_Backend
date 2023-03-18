from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, \
    CreateAPIView, ListAPIView, DestroyAPIView, \
    RetrieveDestroyAPIView, ListCreateAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, \
    UpdateModelMixin, DestroyModelMixin,  RetrieveModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import User

from .models import Comment, Student, Post
from .serializers import CommentSerializer, CreateCommentSerializer, ProfileSerializer, StudentSerializer, PostSerializer


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


# todo Like/Dislike a post:
@api_view(['POST'])
def like_post(request):
    post_id = request.data['post_id']
    post = Post.objects.get(id=post_id)
    user_id = request.user.id

    if user_id not in post.likes:
        post.likes.append(user_id)
    else:
        post.likes.remove(user_id)
    post.save()

    return Response({
        "message": "ok"
    })


# todo Comment
class CommentView(ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Comment.objects.all()
    serializer_class = CreateCommentSerializer

    def get_serializer_context(self):
        user = self.request.user
        student = Student.objects.get(user_id=user.id)
        return {
            'student_id': student.id
        }
