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

        # Overall stats - use aggregate instead of Python sum
        from django.db.models import Sum, Max
        totals = progress.aggregate(
            total_xp=Sum('total_xp'),
            total_lessons=Sum('lessons_completed'),
            total_topics=Sum('topics_completed'),
            total_exercises=Sum('practice_solved'),
            current_streak=Max('current_streak'),
            longest_streak=Max('longest_streak'),
        )

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
            'total_xp': totals['total_xp'] or 0,
            'total_lessons': totals['total_lessons'] or 0,
            'total_topics': totals['total_topics'] or 0,
            'total_exercises': totals['total_exercises'] or 0,
            'current_streak': totals['current_streak'] or 0,
            'longest_streak': totals['longest_streak'] or 0,
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
        from django.db.models import Count, Value, CharField
        from django.db.models.functions import TruncDate, Concat

        # Get last 365 days of activity
        end_date = date.today()
        start_date = end_date - timedelta(days=365)

        # Combine lesson completions and practice sessions using UNION
        from progress.models import LessonProgress
        from practice.models import PracticeSession

        # Lesson completions
        lesson_dates = LessonProgress.objects.filter(
            user=user,
            status=LessonProgress.ProgressStatus.COMPLETED,
            completed_at__date__gte=start_date,
            completed_at__date__lte=end_date
        ).annotate(
            d=TruncDate('completed_at')
        ).values('d').annotate(
            c=Count('id'),
            source=Value('lesson', output_field=CharField())
        )

        # Practice sessions
        practice_dates = PracticeSession.objects.filter(
            user=user,
            status='passed',
            completed_at__date__gte=start_date,
            completed_at__date__lte=end_date
        ).annotate(
            d=TruncDate('completed_at')
        ).values('d').annotate(
            c=Count('id'),
            source=Value('practice', output_field=CharField())
        )

        # Union the querysets and aggregate by date
        from django.db.models import Sum
        combined = lesson_dates.union(practice_dates).values('d').annotate(total=Sum('c'))

        # Build heatmap data: {date_string: count}
        heatmap = {}
        for item in combined:
            d = item['d']
            if d:
                heatmap[d.isoformat()] = item['total']

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
        from django.http import StreamingHttpResponse
        from progress.models import UserProgress, LessonProgress, TopicProgress
        from practice.models import PracticeSession

        user = request.user

        def generate_json():
            yield '{\n'
            
            # User progress
            yield '  "user_progress": [\n'
            first = True
            for obj in UserProgress.objects.filter(user=user).values().iterator(chunk_size=1000):
                if not first:
                    yield ',\n'
                yield '    ' + json.dumps(obj, default=str, ensure_ascii=False)
                first = False
            yield '\n  ],\n'
            
            # Lesson progress
            yield '  "lesson_progress": [\n'
            first = True
            for obj in LessonProgress.objects.filter(user=user).values().iterator(chunk_size=1000):
                if not first:
                    yield ',\n'
                yield '    ' + json.dumps(obj, default=str, ensure_ascii=False)
                first = False
            yield '\n  ],\n'
            
            # Topic progress
            yield '  "topic_progress": [\n'
            first = True
            for obj in TopicProgress.objects.filter(user=user).values().iterator(chunk_size=1000):
                if not first:
                    yield ',\n'
                yield '    ' + json.dumps(obj, default=str, ensure_ascii=False)
                first = False
            yield '\n  ],\n'
            
            # Practice sessions
            yield '  "practice_sessions": [\n'
            first = True
            for obj in PracticeSession.objects.filter(user=user).values().iterator(chunk_size=1000):
                if not first:
                    yield ',\n'
                yield '    ' + json.dumps(obj, default=str, ensure_ascii=False)
                first = False
            yield '\n  ]\n'
            yield '}'

        response = StreamingHttpResponse(generate_json(), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="progress_export_{user.username}.json"'
        return response