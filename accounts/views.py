"""Views for accounts app."""
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView as BasePasswordChangeView
from django.contrib.auth.views import PasswordChangeDoneView as BasePasswordChangeDoneView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, UpdateView

from accounts.forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    UserProfileForm,
    UserSettingsForm,
)
from accounts.models import UserProfile, UserSettings


def user_progress_totals(user):
    """Aggregate XP and streak across all of a user's language progress records."""
    from progress.models import UserProgress
    progress = UserProgress.objects.filter(user=user).select_related('language')
    return {
        'total_xp': sum(p.total_xp for p in progress),
        'current_streak': max((p.current_streak for p in progress), default=0),
    }


class LoginView(SuccessMessageMixin, TemplateView):
    """Custom login view."""

    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    success_message = _('Welcome back, %(username)s!')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accounts:dashboard')
        return self.render_to_response(self.get_context_data(form=form))


class RegisterView(SuccessMessageMixin, CreateView):
    """User registration view."""

    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:dashboard')
    success_message = _('Account created successfully! Welcome to kernify!')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard / personal cabinet view."""

    template_name = 'accounts/dashboard.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get or create profile and settings
        profile, _ = UserProfile.objects.get_or_create(user=user)
        settings_obj, _ = UserSettings.objects.get_or_create(user=user)

        # Get progress data
        from progress.models import UserProgress
        progress = UserProgress.objects.filter(user=user).select_related('language')

        # Get recent activity
        from practice.models import PracticeSession
        recent_sessions = PracticeSession.objects.filter(user=user).select_related('task')[:5]

        # Get bookmarked lessons
        bookmarked_lessons = profile.bookmarked_lessons.prefetch_related('topic__program__language')[:5]

        # Get in-progress lessons
        from learning.models import Lesson, ProgrammingLanguage
        in_progress_lessons = Lesson.objects.filter(
            user_progress__user=user,
            user_progress__status='in_progress'
        ).select_related('topic__program__language')[:5]

        totals = user_progress_totals(user)
        context.update({
            'profile': profile,
            'settings': settings_obj,
            'progress': progress,
            'recent_sessions': recent_sessions,
            'bookmarked_lessons': bookmarked_lessons,
            'in_progress_lessons': in_progress_lessons,
            'total_xp': totals['total_xp'],
            'current_streak': totals['current_streak'],
            'languages': ProgrammingLanguage.objects.filter(status='published').order_by('order')[:6],
        })
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view."""

    template_name = 'accounts/profile.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        from progress.models import UserProgress
        progress = UserProgress.objects.filter(user=user).select_related('language')

        context.update({
            'profile': profile,
            'progress': progress,
            **user_progress_totals(user),
            'total_lessons': sum(p.lessons_completed for p in progress),
        })
        return context


class ProfileEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edit user profile."""

    template_name = 'accounts/profile_edit.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('accounts:profile')
    success_message = _('Profile updated successfully!')
    login_url = reverse_lazy('accounts:login')

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class SettingsView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """User settings view."""

    template_name = 'accounts/settings.html'
    form_class = UserSettingsForm
    success_url = reverse_lazy('accounts:settings')
    success_message = _('Settings saved successfully!')
    login_url = reverse_lazy('accounts:login')

    def get_object(self):
        settings_obj, _ = UserSettings.objects.get_or_create(user=self.request.user)
        return settings_obj

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class PasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, BasePasswordChangeView):
    """Change password view."""

    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:password_change_done')
    success_message = _('Password changed successfully!')
    login_url = reverse_lazy('accounts:login')


class PasswordChangeDoneView(LoginRequiredMixin, BasePasswordChangeDoneView):
    """Password change done view."""

    template_name = 'accounts/password_change_done.html'
    login_url = reverse_lazy('accounts:login')


class EmailVerifyView(LoginRequiredMixin, TemplateView):
    """Email verification view (stub)."""

    template_name = 'accounts/email_verify.html'
    login_url = reverse_lazy('accounts:login')


class EmailVerifyConfirmView(LoginRequiredMixin, TemplateView):
    """Email verification confirmation (stub)."""

    template_name = 'accounts/email_verify_confirm.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = kwargs.get('token')
        return context


class EmailResendView(LoginRequiredMixin, TemplateView):
    """Resend verification email (stub)."""

    template_name = 'accounts/email_resend.html'
    login_url = reverse_lazy('accounts:login')