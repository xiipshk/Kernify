"""URL configuration for practice app."""
from django.urls import path

from practice import views

app_name = 'practice'

urlpatterns = [
    # Practice index
    path('', views.PracticeIndexView.as_view(), name='index'),

    # Task list
    path('tasks/', views.TaskListView.as_view(), name='task_list'),

    # Task detail
    path('tasks/<slug:slug>/', views.TaskDetailView.as_view(), name='task_detail'),

    # Task solve (IDE)
    path('tasks/<slug:slug>/solve/', views.TaskSolveView.as_view(), name='task_solve'),

    # Task submit
    path('tasks/<slug:slug>/submit/', views.TaskSubmitView.as_view(), name='task_submit'),

    # Task results
    path('sessions/<int:pk>/', views.SessionResultView.as_view(), name='session_result'),

    # My practice history
    path('history/', views.PracticeHistoryView.as_view(), name='history'),

    # Daily challenge
    path('daily/', views.DailyChallengeView.as_view(), name='daily'),
]