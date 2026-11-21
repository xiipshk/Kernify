"""URL configuration for learning app."""
from django.urls import path, register_converter
from django.utils.text import slugify

from learning import views

app_name = 'learning'


class UnicodeSlugConverter:
    """Custom path converter that supports Unicode slugs (including Cyrillic)."""
    
    # Use explicit Unicode character ranges to ensure matching works
    # Includes: ASCII word chars + Cyrillic + other Unicode letters
    regex = r'[-\w\u0400-\u04FF]+'  # \w + Cyrillic range
    
    def to_python(self, value):
        return value
    
    def to_url(self, value):
        return value


register_converter(UnicodeSlugConverter, 'unicode_slug')

urlpatterns = [
    # Learning index
    path('', views.LearningIndexView.as_view(), name='index'),

    # My courses
    path('my-courses/', views.MyCoursesView.as_view(), name='my_courses'),

    # Course enrollment
    path('programs/<unicode_slug:slug>/enroll/', views.EnrollView.as_view(), name='enroll'),

    # Lesson learning
    path('lessons/<unicode_slug:slug>/learn/', views.LessonLearnView.as_view(), name='lesson_learn'),

    # Lesson complete
    path('lessons/<unicode_slug:slug>/complete/', views.LessonCompleteView.as_view(), name='lesson_complete'),

    # Lesson next (complete + award XP + go to next lesson)
    path('lessons/<unicode_slug:slug>/next/', views.LessonNextView.as_view(), name='lesson_next'),

    # Bookmark lesson
    path('lessons/<unicode_slug:slug>/bookmark/', views.BookmarkLessonView.as_view(), name='bookmark_lesson'),

    # Notes
    path('lessons/<unicode_slug:slug>/notes/', views.LessonNotesView.as_view(), name='lesson_notes'),
    path('notes/', views.UserNotesView.as_view(), name='user_notes'),
]