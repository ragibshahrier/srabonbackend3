from django.urls import path
from .views import *

urlpatterns = [
    path('course/custom/new', CustomCourseView.as_view()),
    path('chat', ChatView.as_view()),
    path('login/', LoginView.as_view()),

    path('register/', RegisterView.as_view()),
    path('studentinfo/', StudentDetail.as_view()),
    path('addcourses/', AddCourseView.as_view()),
    path('courses/', CoursesView.as_view()),
    path('courses/<int:course_id>/', CoursesView.as_view()),

    path('chats/', ChatConvo.as_view()),
]
