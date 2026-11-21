"""URL configuration for progress app."""
from django.urls import path

from progress import views

app_name = 'progress'

urlpatterns = [
    # Progress dashboard
    path('', views.ProgressDashboardView.as_view(), name='dashboard'),

    # Language progress
    path('language/<slug:slug>/', views.LanguageProgressView.as_view(), name='language_progress'),

    # Topic progress
    path('topic/<slug:slug>/', views.TopicProgressView.as_view(), name='topic_progress'),

    # Achievements
    path('achievements/', views.AchievementsView.as_view(), name='achievements'),

    # Statistics
    path('stats/', views.StatisticsView.as_view(), name='statistics'),

    # Error review (SM-2)
    path('errors/', views.ErrorReviewView.as_view(), name='error_review'),
    path('errors/<int:pk>/review/', views.ErrorReviewSubmitView.as_view(), name='error_review_submit'),

    # Heatmap / calendar
    path('heatmap/', views.HeatmapView.as_view(), name='heatmap'),

    # Export data
    path('export/', views.ExportProgressView.as_view(), name='export'),
]