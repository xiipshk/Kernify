"""API URLs for the ai app (mounted under /api/ai/, no locale prefix)."""
from django.urls import path

from ai import views

app_name = 'ai_api'

urlpatterns = [
    path('chat/', views.ChatMessageAPIView.as_view(), name='chat_message'),
]
