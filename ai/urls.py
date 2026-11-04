"""URL configuration for ai app."""
from django.urls import path

from ai import views

app_name = 'ai'

urlpatterns = [
    # AI Chat
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('chat/new/', views.NewChatView.as_view(), name='new_chat'),
    path('chat/<int:pk>/', views.ChatDetailView.as_view(), name='chat_detail'),
    path('chat/<int:pk>/delete/', views.ChatDeleteView.as_view(), name='chat_delete'),

    # AI Assistant (context-aware)
    path('assistant/', views.AssistantView.as_view(), name='assistant'),
    path('assistant/ask/', views.AskAssistantView.as_view(), name='ask_assistant'),

    # AI Code Review
    path('code-review/', views.CodeReviewView.as_view(), name='code_review'),
    path('code-review/submit/', views.CodeReviewSubmitView.as_view(), name='code_review_submit'),

    # AI Explain Code
    path('explain/', views.ExplainCodeView.as_view(), name='explain_code'),

    # AI Generate Exercise
    path('generate-exercise/', views.GenerateExerciseView.as_view(), name='generate_exercise'),

    # Usage stats
    path('usage/', views.UsageStatsView.as_view(), name='usage_stats'),
]