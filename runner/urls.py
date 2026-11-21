"""URL configuration for the code runner app."""
from django.urls import path

from runner import views

app_name = 'runner'

urlpatterns = [
    path('code/run/', views.RunCodeView.as_view(), name='code_run'),
]
