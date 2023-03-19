from requests import Response
from rest_framework import serializers

from core.models import User
from .models import Comment, Post, Student


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['title', 'about_me', 'college_city', 'current_year', 'branch', 'skills',
                  'user', 'birth_date', 'phone', 'gender', 'college', 'isRestricted']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['user', 'title', 'phone', 'birth_date',
                  'college', 'college_city', 'skills', 'about_me']


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class SimpleProfileSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer()

    class Meta:
        model = Student
        fields = ['user', 'title']


class CommentSerializer(serializers.ModelSerializer):
    student = SimpleProfileSerializer()

    class Meta:
        model = Comment
        fields = ['student', 'post', 'content']


class PostSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField(
        method_name='get_comments_length')
    likes = serializers.SerializerMethodField(
        method_name='get_likes', read_only=True)
    student = SimpleProfileSerializer(read_only=True)
    isLikedByCurrentUser = serializers.SerializerMethodField(
        method_name='get_isLikedByCurrentUser')

    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'type',
                  'tags', 'created_at', 'likes', 'student',
                  'comments', 'isLikedByCurrentUser']

    def get_comments_length(self, post: Post):
        # todo return the number of comments on the post
        return Comment.objects.filter(post_id=post.id).count()

    def get_likes(self, post: Post):
        students = User.objects.filter(id__in=post.likes)
        serializer = SimpleUserSerializer(students, many=True)
        return serializer.data

    def get_isLikedByCurrentUser(self, post: Post):
        student_id = self.context['student_id']
        student: Student = Student.objects.get(id=student_id)

        return student.user.id in post.likes

    def create(self, validated_data):
        student_id = self.context['student_id']
        likes = []

        return Post.objects.create(
            likes=likes,
            student_id=student_id,  **validated_data
        )


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'post']

    def save(self, **kwargs):
        student_id = self.context['student_id']
        Comment.objects.create(
            student_id=student_id, **self.validated_data
        )
