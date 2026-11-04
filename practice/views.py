"""Views for practice app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView, View
from django.http import Http404, JsonResponse

from practice.models import PracticeTask, PracticeSession


class PracticeIndexView(LoginRequiredMixin, TemplateView):
    """Practice index page."""

    template_name = 'practice/index.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Recommended tasks based on user's current learning
        from progress.models import UserProgress
        progress = UserProgress.objects.filter(user=user).select_related('language', 'current_topic')

        recommended = []
        for p in progress:
            if p.current_topic:
                tasks = PracticeTask.objects.filter(
                    topic=p.current_topic,
                    status='published'
                ).select_related('topic')[:3]
                recommended.extend(tasks)

        # Recent sessions
        recent = PracticeSession.objects.filter(user=user).select_related('task', 'task__topic')[:5]

        # Daily challenge
        daily = PracticeTask.objects.filter(status='published').order_by('?').first()

        context.update({
            'recommended_tasks': recommended[:6],
            'recent_sessions': recent,
            'daily_task': daily,
        })
        return context


class TaskListView(LoginRequiredMixin, ListView):
    """List of practice tasks."""

    model = PracticeTask
    template_name = 'practice/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        queryset = PracticeTask.objects.filter(status='published').select_related('topic__program__language')
        topic = self.request.GET.get('topic')
        task_type = self.request.GET.get('type')
        difficulty = self.request.GET.get('difficulty')

        if topic:
            queryset = queryset.filter(topic__slug=topic)
        if task_type:
            queryset = queryset.filter(task_type=task_type)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        return queryset.order_by('topic', 'order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from learning.models import Topic
        context['topics'] = Topic.objects.filter(status='published').select_related('program__language')
        context['task_types'] = PracticeTask.TaskType.choices
        context['difficulties'] = [(str(d), str(d)) for d in range(1, 6)]
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    """Task detail view."""

    model = PracticeTask
    template_name = 'practice/task_detail.html'
    context_object_name = 'task'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return PracticeTask.objects.filter(status='published').select_related('topic__program__language')

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        slug = self.kwargs.get(self.slug_url_kwarg)
        obj = queryset.filter(**{self.slug_field: slug}).first()
        if obj is None:
            raise Http404(_("No %(verbose_name)s found matching the query") % {
                'verbose_name': queryset.model._meta.verbose_name,
            })
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object
        user = self.request.user

        # Get user's best session
        best_session = PracticeSession.objects.filter(
            user=user,
            task=task,
            status='completed'
        ).order_by('-xp_earned').first()

        context['best_session'] = best_session
        context['total_sessions'] = PracticeSession.objects.filter(user=user, task=task).count()
        return context


class TaskSolveView(LoginRequiredMixin, DetailView):
    """Task solving view (IDE)."""

    model = PracticeTask
    template_name = 'practice/task_solve.html'
    context_object_name = 'task'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return PracticeTask.objects.filter(status='published').select_related('topic__program__language')

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        slug = self.kwargs.get(self.slug_url_kwarg)
        obj = queryset.filter(**{self.slug_field: slug}).first()
        if obj is None:
            raise Http404(_("No %(verbose_name)s found matching the query") % {
                'verbose_name': queryset.model._meta.verbose_name,
            })
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object

        # Create new session
        session = PracticeSession.objects.create(
            user=self.request.user,
            task=task,
            topic=task.topic,
            status='in_progress'
        )
        context['session'] = session
        return context


class TaskSubmitView(LoginRequiredMixin, View):
    """Submit task solution."""

    def post(self, request, slug):
        task = get_object_or_404(PracticeTask, slug=slug, status='published')
        code = request.POST.get('code', '')
        session_id = request.POST.get('session_id')

        session = get_object_or_404(PracticeSession, id=session_id, user=request.user, task=task)

        # Run tests (placeholder - would integrate with Piston API)
        # For now, mock test results
        test_results = [
            {'test_name': 'test_1', 'passed': True, 'input': 'input1', 'expected': 'output1', 'actual': 'output1'},
            {'test_name': 'test_2', 'passed': True, 'input': 'input2', 'expected': 'output2', 'actual': 'output2'},
        ]
        passed_count = sum(1 for t in test_results if t['passed'])
        score = int((passed_count / len(test_results)) * 100) if test_results else 0

        session.submitted_code = code
        session.test_results = test_results
        session.score = score
        session.attempts += 1
        session.status = 'completed' if score == 100 else 'failed'
        session.completed_at = timezone.now()

        if session.status == 'completed':
            session.xp_earned = task.xp_reward

        session.save()

        # Update user progress
        if session.status == 'completed':
            from progress.models import UserProgress
            from django.utils import timezone
            progress, _ = UserProgress.objects.get_or_create(
                user=request.user,
                language=task.topic.program.language
            )
            progress.total_xp += task.xp_reward
            progress.practice_solved += 1
            progress.last_activity_at = timezone.now()
            progress.save()

        return redirect('practice:session_result', pk=session.pk)


class SessionResultView(LoginRequiredMixin, DetailView):
    """Session result view."""

    model = PracticeSession
    template_name = 'practice/session_result.html'
    context_object_name = 'session'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return PracticeSession.objects.filter(user=self.request.user).select_related('task', 'task__topic__program__language')


class PracticeHistoryView(LoginRequiredMixin, ListView):
    """User's practice history."""

    model = PracticeSession
    template_name = 'practice/history.html'
    context_object_name = 'sessions'
    paginate_by = 20
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return PracticeSession.objects.filter(user=self.request.user).select_related('task', 'task__topic__program__language').order_by('-created_at')


class DailyChallengeView(LoginRequiredMixin, TemplateView):
    """Daily challenge view."""

    template_name = 'practice/daily.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get or create daily challenge
        from django.utils import timezone
        today = timezone.now().date()

        # Simple daily task selection
        task = PracticeTask.objects.filter(status='published').order_by('?').first()
        context['task'] = task
        context['date'] = today
        return context


from django.utils import timezone