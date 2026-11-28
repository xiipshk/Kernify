"""URL configuration for practice app."""
from django.urls import path

from practice import assessment_views, course_assessment_views, views

app_name = 'practice'

urlpatterns = [
    # Тест-диагностика по языку (вкладка «Тест»)
    path('assessment/<slug:slug>/', assessment_views.LanguageAssessmentView.as_view(), name='language_assessment'),
    path('assessment/<slug:slug>/results/<int:pk>/', assessment_views.AssessmentResultDetailView.as_view(), name='assessment_result'),

    # Тест после курса (CourseProgram)
    path('course-test/<slug:slug>/', course_assessment_views.CourseTestView.as_view(), name='course_test'),
    path('course-test/<slug:slug>/results/<int:pk>/', course_assessment_views.CourseTestResultDetailView.as_view(), name='course_test_result'),

    # Practice index
    path('', views.PracticeIndexView.as_view(), name='index'),

    # Task list
    path('tasks/', views.TaskListView.as_view(), name='task_list'),

    # Task detail
    path('tasks/<slug:slug>/', views.TaskDetailView.as_view(), name='task_detail'),

    # Task solve (IDE)
    path('tasks/<slug:slug>/solve/', views.TaskSolveView.as_view(), name='task_solve'),

    # Task submit (form)
    path('tasks/<slug:slug>/submit/', views.TaskSubmitView.as_view(), name='task_submit'),

    # Task submit (AJAX/API)
    path('api/tasks/<slug:slug>/submit/', views.TaskSubmitAPIView.as_view(), name='task_submit_api'),

    # AI help while solving a task
    path('api/tasks/<slug:slug>/ai-help/', views.TaskAIHelpAPIView.as_view(), name='task_ai_help_api'),

    # Task results
    path('sessions/<int:pk>/', views.SessionResultView.as_view(), name='session_result'),

    # My practice history
    path('history/', views.PracticeHistoryView.as_view(), name='history'),

    # Standalone code compiler (no task needed)
    path('compiler/', views.CompilerView.as_view(), name='compiler'),

    # Daily challenge
    path('daily/', views.DailyChallengeView.as_view(), name='daily'),
]