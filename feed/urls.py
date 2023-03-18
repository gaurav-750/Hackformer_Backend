from django.urls import path, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('student', views.StudentViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('student/<str:username>',
         views.StudentProfileView.as_view(), name='student-profile'),
]