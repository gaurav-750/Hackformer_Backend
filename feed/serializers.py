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
        fields = ['user_id', 'birth_date', 'phone', 'gender', 'college']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['user', 'phone', 'birth_date',
                  'college', 'college_city', 'skills', 'about_me']


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class SimpleProfileSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer()

    class Meta:
        model = Student
        fields = ['user']


class CommentSerializer(serializers.ModelSerializer):
    student = SimpleProfileSerializer()

    class Meta:
        model = Comment
        fields = ['student', 'post', 'content']


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    likes = serializers.SerializerMethodField(
        method_name='get_likes', read_only=True)
    student = SimpleProfileSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'type',
                  'tags', 'created_at', 'likes', 'student', 'comments']

    def get_likes(self, post: Post):
        students = User.objects.filter(id__in=post.likes)
        serializer = SimpleUserSerializer(students, many=True)
        return serializer.data

    def create(self, validated_data):
        student_id = self.context['student_id']
        likes = []

        return Post.objects.create(
            likes=likes,
            student_id=student_id,  **validated_data
        )
