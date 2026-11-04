"""Views for progress app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView

from datetime import timedelta

from learning.models import CourseProgram, ProgrammingLanguage, Topic
from progress.models import ErrorHistory, TestResult, UserProgress


class ProgressDashboardView(LoginRequiredMixin, TemplateView):
    """Progress dashboard."""

    template_name = 'progress/dashboard.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        progress = UserProgress.objects.filter(user=user).select_related('language')

        # Overall stats
        total_xp = sum(p.total_xp for p in progress)
        total_lessons = sum(p.lessons_completed for p in progress)
        total_topics = sum(p.topics_completed for p in progress)
        total_exercises = sum(p.practice_solved for p in progress)
        current_streak = max((p.current_streak for p in progress), default=0)
        longest_streak = max((p.longest_streak for p in progress), default=0)

        # Recent activity
        from practice.models import PracticeSession
        recent_sessions = PracticeSession.objects.filter(user=user).select_related('task')[:10]

        # Error review due
        due_errors = ErrorHistory.objects.filter(
            user=user,
            is_resolved=False,
            next_review__lte=timezone.now().date()
        ).select_related('lesson')[:5]

        context.update({
            'progress': progress,
            'total_xp': total_xp,
            'total_lessons': total_lessons,
            'total_topics': total_topics,
            'total_exercises': total_exercises,
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'recent_sessions': recent_sessions,
            'due_errors': due_errors,
        })
        return context


class LanguageProgressView(LoginRequiredMixin, DetailView):
    """Language-specific progress."""

    model = ProgrammingLanguage
    template_name = 'progress/language_progress.html'
    context_object_name = 'language'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        language = self.object

        progress = get_object_or_404(UserProgress, user=user, language=language)

        # Topic progress
        topic_progress = TopicProgress.objects.filter(user=user, topic__program__language=language).select_related('topic').order_by('-updated_at')

        # Recent lessons
        from progress.models import LessonProgress
        recent_lessons = LessonProgress.objects.filter(
            user=user,
            lesson__subtopic__topic__program__language=language
        ).select_related('lesson', 'lesson__subtopic__topic').order_by('-updated_at')[:10]

        context.update({
            'progress': progress,
            'topic_progress': topic_progress,
            'recent_lessons': recent_lessons,
        })
        return context


class TopicProgressView(LoginRequiredMixin, DetailView):
    """Topic progress detail."""

    model = Topic
    template_name = 'progress/topic_progress.html'
    context_object_name = 'topic'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return Topic.objects.filter(status='published').select_related('program__language')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        topic = self.object

        topic_progress = get_object_or_404(
            topic.user_progress, user=user
        )

        # Lesson progress
        from progress.models import LessonProgress
        lessons = LessonProgress.objects.filter(
            user=user,
            lesson__subtopic__topic=topic
        ).select_related('lesson', 'lesson__subtopic').order_by('lesson__order')

        context.update({
            'topic_progress': topic_progress,
            'lessons': lessons,
        })
        return context


class AchievementsView(LoginRequiredMixin, TemplateView):
    """Achievements page."""

    template_name = 'progress/achievements.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Placeholder for achievements
        context['achievements'] = []
        return context


class StatisticsView(LoginRequiredMixin, TemplateView):
    """Detailed statistics."""

    template_name = 'progress/statistics.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        from practice.models import PracticeSession
        from django.db.models import Count, Avg, Sum
        from django.db.models.functions import TruncDate
        from django.utils import timezone
        from datetime import timedelta

        # Last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)

        sessions = PracticeSession.objects.filter(user=user, created_at__gte=thirty_days_ago)

        stats = sessions.aggregate(
            total=Count('id'),
            total_xp=Sum('xp_earned'),
        )

        # Daily stats for chart
        daily = sessions.annotate(date=TruncDate('created_at')).values('date').annotate(
            count=Count('id'),
            xp=Sum('xp_earned')
        ).order_by('date')

        context.update({
            'stats': stats,
            'daily_stats': list(daily),
        })
        return context


class ErrorReviewView(LoginRequiredMixin, ListView):
    """Error review (SM-2)."""

    model = ErrorHistory
    template_name = 'progress/error_review.html'
    context_object_name = 'errors'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return ErrorHistory.objects.filter(
            user=self.request.user,
            is_resolved=False
        ).select_related('lesson', 'lesson__subtopic__topic').order_by('next_review')


class ErrorReviewSubmitView(LoginRequiredMixin, TemplateView):
    """Submit error review."""

    def post(self, request, pk):
        error = get_object_or_404(ErrorHistory, pk=pk, user=request.user)
        quality = int(request.POST.get('quality', 0))

        # SM-2 algorithm
        error.ease_factor = max(1.3, error.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

        if quality >= 3:
            if error.count == 0:
                error.interval_days = 1
            elif error.count == 1:
                error.interval_days = 6
            else:
                error.interval_days = int(error.interval_days * error.ease_factor)
            error.count += 1
        else:
            error.count = 0
            error.interval_days = 1

        error.next_review = timezone.now() + timedelta(days=error.interval_days)

        if quality >= 4 and error.count >= 3:
            error.is_resolved = True
            error.resolved_at = timezone.now()

        error.save()

        return redirect('progress:error_review')


class HeatmapView(LoginRequiredMixin, TemplateView):
    """Activity heatmap."""

    template_name = 'progress/heatmap.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Placeholder
        context['heatmap_data'] = {}
        return context


class ExportProgressView(LoginRequiredMixin, TemplateView):
    """Export progress data."""

    template_name = 'progress/export.html'
    login_url = reverse_lazy('accounts:login')