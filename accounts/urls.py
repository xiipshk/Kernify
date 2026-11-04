"""URL configuration for accounts app."""
from django.urls import path
from django.contrib.auth.views import LogoutView

from accounts import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Dashboard (main cabinet)
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Profile management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/settings/', views.SettingsView.as_view(), name='settings'),

    # Password management
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # Email verification (stub)
    path('email/verify/', views.EmailVerifyView.as_view(), name='email_verify'),
    path('email/verify/<str:token>/', views.EmailVerifyConfirmView.as_view(), name='email_verify_confirm'),
    path('email/resend/', views.EmailResendView.as_view(), name='email_resend'),
]