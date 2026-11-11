"""Views for progress app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView

from datetime import timedelta

from learning.models import CourseProgram, ProgrammingLanguage, Topic
from progress.models import ErrorHistory, TestResult, TopicProgress, UserProgress


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
            next_review__lte=timezone.now()
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
            lesson__topic__program__language=language
        ).select_related('lesson', 'lesson__topic').order_by('-updated_at')[:10]

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
            lesson__topic=topic
        ).select_related('lesson', 'lesson__topic').order_by('lesson__order')

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
        ).select_related('lesson', 'lesson__topic').order_by('next_review')


class ErrorReviewSubmitView(LoginRequiredMixin, TemplateView):
    """Submit error review."""

    def post(self, request, pk):
        error = get_object_or_404(ErrorHistory, pk=pk, user=request.user)
        try:
            quality = int(request.POST.get('quality', 0))
        except (ValueError, TypeError):
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest(_('Invalid quality value'))
        if quality < 0 or quality > 5:
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest(_('Quality must be between 0 and 5'))

        # Use model's SM-2 implementation (avoids duplication)
        error.schedule_next_review(quality)

        if quality >= 4 and error.count >= 3:
            error.is_resolved = True
            error.resolved_at = timezone.now()
            error.save(update_fields=['is_resolved', 'resolved_at', 'updated_at'])

        return redirect('progress:error_review')


class HeatmapView(LoginRequiredMixin, TemplateView):
    """Activity heatmap."""

    template_name = 'progress/heatmap.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        from datetime import date, timedelta
        from django.db.models import Count
        from django.db.models.functions import TruncDate

        # Get last 365 days of activity
        end_date = date.today()
        start_date = end_date - timedelta(days=365)

        # Combine lesson completions and practice sessions
        from progress.models import LessonProgress
        from practice.models import PracticeSession

        lesson_dates = LessonProgress.objects.filter(
            user=user,
            status=LessonProgress.ProgressStatus.COMPLETED,
            completed_at__date__gte=start_date,
            completed_at__date__lte=end_date
        ).annotate(d=TruncDate('completed_at')).values('d').annotate(c=Count('id'))

        practice_dates = PracticeSession.objects.filter(
            user=user,
            status='passed',
            completed_at__date__gte=start_date,
            completed_at__date__lte=end_date
        ).annotate(d=TruncDate('completed_at')).values('d').annotate(c=Count('id'))

        # Build heatmap data: {date_string: count}
        heatmap = {}
        for item in lesson_dates:
            d = item['d']
            if d:
                heatmap[d.isoformat()] = heatmap.get(d.isoformat(), 0) + item['c']
        for item in practice_dates:
            d = item['d']
            if d:
                heatmap[d.isoformat()] = heatmap.get(d.isoformat(), 0) + item['c']

        context['heatmap_data'] = heatmap
        context['start_date'] = start_date.isoformat()
        context['end_date'] = end_date.isoformat()
        return context


class ExportProgressView(LoginRequiredMixin, TemplateView):
    """Export progress data."""

    template_name = 'progress/export.html'
    login_url = reverse_lazy('accounts:login')

    def get(self, request, *args, **kwargs):
        import json
        from django.http import HttpResponse
        from progress.models import UserProgress, LessonProgress, TopicProgress
        from practice.models import PracticeSession

        user = request.user

        data = {
            'user_progress': list(UserProgress.objects.filter(user=user).values()),
            'lesson_progress': list(LessonProgress.objects.filter(user=user).values()),
            'topic_progress': list(TopicProgress.objects.filter(user=user).values()),
            'practice_sessions': list(PracticeSession.objects.filter(user=user).values()),
        }

        response = HttpResponse(json.dumps(data, default=str, ensure_ascii=False, indent=2),
                                content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="progress_export_{user.username}.json"'
        return response