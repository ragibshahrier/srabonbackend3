from django.urls import path
from .views import *

urlpatterns = [
    path('course/custom/new', CustomCourseView.as_view()),
    path('chat', ChatView.as_view()),

    path('getserverinfo/', Getserverinfo.as_view()),
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('studentinfo/', StudentDetail.as_view()),
    path('addcourses/', AddCourseView.as_view()),
    path('courses/', CoursesView.as_view()),
    path('courses/<str:course_id>/', CoursesView.as_view()),

    path('chats/', ChatConvo.as_view()),

    path('score/', ScoreView.as_view()),
    path('leaderboard/', AllStudentsProfileView.as_view()),
    path('coursecontent/<str:course_id>/<str:lang>/', CourseContentView.as_view()),
    path('personal-course-stats/<str:course_id>/', PersonalCourseStatsView.as_view()),

    path('notifications/<str:arg>/', NotificationView.as_view()),

    path('add-from-explorer/', AddFromExplorerView.as_view()),
    path('explorer-courses/', ExplorerCoursesView.as_view()),
    path('course-access/<str:access>/', CourseAccessView.as_view()),

    path('grammarhelper/', GrammarHelperView.as_view()),
]
