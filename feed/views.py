import json
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
import requests

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
from collections import Counter

import numpy as np
import re
import nltk
import difflib

MAX_RECOMMENDATIONS = 3


# Create your views here
class StudentViewset(CreateModelMixin,
                     GenericViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def create(self, request, *args, **kwargs):
        serializer = StudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Make the POST API call to a particular endpoint using the requests library
        url = 'https://api-68BE6A4A-0F0A-4D7A-B255-0A82A0F4D252.sendbird.com/v3/users'
        unique_id = str(request.data['user'])
        data = {
            "user_id": unique_id,
            "nickname": request.data['title'],
            "profile_url": "",
            "profile_file": ""
        }

        headers = {"Api-token": "2ff72c7d4712ab37955d9f2a391c57859f493c41",
                   "Content-Type": "application/json"
                   }
        res = requests.post(url, data=json.dumps(data), headers=headers)
        return Response({"response": serializer.data})


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


@api_view(['GET'])
def comment_on_post(request, pk):
    queryset = Comment.objects.filter(post_id=pk)
    serializer = CommentSerializer(queryset, many=True)
    return Response(serializer.data)


nltk.download('stopwords')


@api_view()
def recommendations(request):
    students = Student.objects.all()
    students_list = StudentSerializer(students, many=True)
    students_list = students_list.data

    stop_words = stopwords.words('english')
    stemmer = SnowballStemmer('english')
    text_cleaning_re = "@\S+|https?:\S+|http?:\S|[^A-Za-z0-9]+"

    def final_similarity(a: Student, b: Student):

        def sw(t):
            stem = False
            text = re.sub(text_cleaning_re, ' ', str(t).lower()).strip()
            tokens = []
            for token in text.split():
                if token not in stop_words:
                    if stem:
                        tokens.append(stemmer.stem(token))
                    else:
                        tokens.append(token)
            return (" ".join(tokens))

        def string_similarity(str1, str2):
            result = difflib.SequenceMatcher(a=str1.lower(), b=str2.lower())
            return result.ratio()

        AS = string_similarity(sw(a.about_me), sw(b['about_me']))

        def coml(a, b):
            a_vals = Counter(a)
            b_vals = Counter(b)

            # convert to word-vectors
            words = list(a_vals.keys() | b_vals.keys())
            a_vect = [a_vals.get(word, 0)
                      for word in words]        # [0, 0, 1, 1, 2, 1]
            b_vect = [b_vals.get(word, 0)
                      for word in words]        # [1, 1, 1, 0, 1, 0]

            # find cosine
            len_a = sum(av*av for av in a_vect) ** 0.5             # sqrt(7)
            len_b = sum(bv*bv for bv in b_vect) ** 0.5             # sqrt(4)
            dot = sum(av*bv for av, bv in zip(a_vect, b_vect))    # 3
            cosine = dot / (len_a * len_b)
            return cosine

        ss = coml(a.skills, b['skills'])
        final_sim = (1.2*AS + 0.8*ss)/2
        return final_sim

    # current user
    current_stud = Student.objects.get(user_id=request.user.id)
    res = []
    v = 0
    for i in students_list:
        stud: Student = dict(students_list[v])
        v += 1
        fs = final_similarity(current_stud, stud)
        res.append({'fs': fs,
                    'id': stud['user']})

    arr_new = sorted(res, key=lambda x: x['fs'], reverse=True)

    user_ids = []
    # todo insert user ids in
    for u in arr_new:
        if len(user_ids) < MAX_RECOMMENDATIONS and u['id'] not in user_ids and u['fs'] != 1:
            user_ids.append(u['id'])

    queryset = Student.objects.filter(user__in=user_ids)
    serializer = ProfileSerializer(queryset, many=True)
    return Response(serializer.data)
