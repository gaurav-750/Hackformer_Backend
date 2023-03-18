from django.urls import path, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('student', views.StudentViewset)
router.register('comment', views.CommentView)

urlpatterns = [
    path('', include(router.urls)),
    path('student/<str:username>/',
         views.StudentProfileView.as_view(), name='student-profile'),
    path('post/', views.AllPost.as_view(), name='all-posts'),
    path('post/like/', views.like_post),
    path('post/comment/<int:pk>/', views.comment_on_post),
    path('student/recommendations/', views.recommendations),
]
