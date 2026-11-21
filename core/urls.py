"""URL configuration for core app."""
from django.urls import path
from django.views.generic import TemplateView

from core import views

app_name = 'core'

urlpatterns = [
    # Home page
    path('', views.HomeView.as_view(), name='home'),

    # About page
    path('about/', TemplateView.as_view(template_name='core/about.html'), name='about'),

    # Contact page
    path('contact/', TemplateView.as_view(template_name='core/contact.html'), name='contact'),

    # Languages overview
    path('languages/', views.LanguagesView.as_view(), name='languages'),

    # Language detail
    path('languages/<slug:slug>/', views.LanguageDetailView.as_view(), name='language_detail'),

    # Course program detail
    path('programs/<slug:slug>/', views.ProgramDetailView.as_view(), name='program_detail'),

    # Topic detail
    path('topics/<slug:slug>/', views.TopicDetailView.as_view(), name='topic_detail'),

    # Lesson detail
    path('lessons/<slug:slug>/', views.LessonDetailView.as_view(), name='lesson_detail'),
]