"""URL configuration for learning app."""
from django.urls import path

from learning import views

app_name = 'learning'

urlpatterns = [
    # Learning index
    path('', views.LearningIndexView.as_view(), name='index'),

    # My courses
    path('my-courses/', views.MyCoursesView.as_view(), name='my_courses'),

    # Course enrollment
    path('programs/<slug:slug>/enroll/', views.EnrollView.as_view(), name='enroll'),

    # Lesson learning
    path('lessons/<slug:slug>/learn/', views.LessonLearnView.as_view(), name='lesson_learn'),

    # Lesson complete
    path('lessons/<slug:slug>/complete/', views.LessonCompleteView.as_view(), name='lesson_complete'),

    # Bookmark lesson
    path('lessons/<slug:slug>/bookmark/', views.BookmarkLessonView.as_view(), name='bookmark_lesson'),

    # Notes
    path('lessons/<slug:slug>/notes/', views.LessonNotesView.as_view(), name='lesson_notes'),
    path('notes/', views.UserNotesView.as_view(), name='user_notes'),
]