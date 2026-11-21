"""Views for practice app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView, View
from django.http import JsonResponse

from core.views import SlugDetailMixin
from practice.models import PracticeTask, PracticeSession
from practice.services import run_task_tests, save_submission, get_daily_challenge
from runner import code_runner


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

        # Ежедневный вызов — одна и та же задача в течение дня.
        daily = get_daily_challenge(timezone.localdate())

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
        topics = self.request.GET.getlist('topic')
        task_type = self.request.GET.get('type')
        difficulty = self.request.GET.get('difficulty')
        language = self.request.GET.get('language')

        if topics:
            queryset = queryset.filter(topic__slug__in=topics)
        if task_type:
            queryset = queryset.filter(task_type=task_type)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if language:
            queryset = queryset.filter(topic__program__language__slug=language)

        return queryset.order_by('topic', 'order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from learning.models import Topic, ProgrammingLanguage
        language = self.request.GET.get('language', '')
        topics = Topic.objects.filter(status='published').select_related('program__language')
        if language:
            topics = topics.filter(program__language__slug=language)
        context['topics'] = topics.order_by('program__language__order', 'order', 'name')
        context['languages'] = ProgrammingLanguage.objects.filter(status='published')
        context['task_types'] = PracticeTask.TaskType.choices
        context['difficulties'] = [(str(d), str(d)) for d in range(1, 6)]
        # Preserve selected filters for the template
        context['selected_topics'] = self.request.GET.getlist('topic')
        context['selected_type'] = self.request.GET.get('type', '')
        context['selected_difficulty'] = self.request.GET.get('difficulty', '')
        context['selected_language'] = language
        return context


class TaskDetailView(LoginRequiredMixin, SlugDetailMixin, DetailView):
    """Task detail view."""

    model = PracticeTask
    template_name = 'practice/task_detail.html'
    context_object_name = 'task'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return PracticeTask.objects.filter(status='published').select_related('topic__program__language')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object
        user = self.request.user

        # Get user's best session
        best_session = PracticeSession.objects.filter(
            user=user,
            task=task,
            status='passed'
        ).order_by('-xp_earned').first()

        context['best_session'] = best_session
        context['total_sessions'] = PracticeSession.objects.filter(user=user, task=task).count()
        return context


class TaskSolveView(LoginRequiredMixin, SlugDetailMixin, DetailView):
    """Task solving view (IDE)."""

    model = PracticeTask
    template_name = 'practice/task_solve.html'
    context_object_name = 'task'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return PracticeTask.objects.filter(status='published').select_related('topic__program__language')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object

        # Get existing session or create one - use get_or_create with select_for_update to avoid race conditions
        session, created = PracticeSession.objects.get_or_create(
            user=self.request.user,
            task=task,
            topic=task.topic,
            defaults={'status': 'pending', 'language': task.language.slug},
        )
        # Don't create new session on every GET - only if no pending/running session exists
        if not created and session.status not in ['pending', 'running']:
            # Create new session for new attempt
            session = PracticeSession.objects.create(
                user=self.request.user,
                task=task,
                topic=task.topic,
                status='pending',
            )
        context['session'] = session
        context['code_runner_enabled'] = code_runner.is_enabled()
        return context


class TaskSubmitView(LoginRequiredMixin, View):
    """Проверка решения по тестам задачи (обычная отправка формы)."""

    def post(self, request, slug):
        task = get_object_or_404(PracticeTask, slug=slug, status='published')
        code = request.POST.get('code', '')
        session_id = request.POST.get('session_id')
        # Язык решения всегда совпадает с языком задачи.
        language = task.language.slug

        session = get_object_or_404(PracticeSession, id=session_id, user=request.user, task=task)

        result = run_task_tests(task, code, language)
        save_submission(session, task, code, language, result)

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


COMPILER_LANGUAGES = [
    # (slug, отображаемое имя, стартовый код, можно ли запускать)
    ('python', 'Python', '# Напишите код на Python\nprint("Hello, Kernify!")\n', True),
    ('javascript', 'JavaScript', '// Напишите код на JavaScript\nconsole.log("Hello, Kernify!");\n', True),
    ('cpp', 'C++', '// Напишите код на C++\n#include <iostream>\n\nint main() {\n    std::cout << "Hello, Kernify!" << std::endl;\n    return 0;\n}\n', True),
    ('csharp', 'C#', '// Напишите код на C#\nusing System;\n\nclass Program\n{\n    static void Main()\n    {\n        Console.WriteLine("Hello, Kernify!");\n    }\n}\n', True),
    ('rust', 'Rust', '// Напишите код на Rust\nfn main() {\n    println!("Hello, Kernify!");\n}\n', True),
    ('css', 'CSS', '/* Напишите стили CSS */\nbody {\n    color: #6366f1;\n}\n', False),
]


class CompilerView(LoginRequiredMixin, TemplateView):
    """Свободный компилятор: редактор кода без привязки к задаче.

    Запуск кода выполняется в собственном Piston (см. ``CODE_RUNNER_ENABLED``).
    """

    template_name = 'practice/compiler.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        languages = [
            {'slug': slug, 'name': name, 'starter_code': starter, 'runnable': runnable}
            for slug, name, starter, runnable in COMPILER_LANGUAGES
        ]
        selected = self.request.GET.get('language', '')
        if selected not in {lang['slug'] for lang in languages}:
            selected = 'python'

        context.update({
            'languages': languages,
            'selected_language': selected,
            'selected_language_name': next(
                lang['name'] for lang in languages if lang['slug'] == selected
            ),
            'code_runner_enabled': code_runner.is_enabled(),
        })
        return context


class DailyChallengeView(LoginRequiredMixin, TemplateView):
    """Daily challenge view."""

    template_name = 'practice/daily.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()

        # Ежедневный вызов: одна задача на день (сохраняется в DailyChallenge).
        task = get_daily_challenge(today)
        context['task'] = task
        context['date'] = today
        return context


class TaskSubmitAPIView(LoginRequiredMixin, View):
    """AJAX endpoint for task submission."""

    def post(self, request, slug):
        import json
        from django.http import JsonResponse
        
        task = get_object_or_404(PracticeTask, slug=slug, status='published')

        # Parse JSON body
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            session_id = data.get('session_id')
            # Язык решения всегда совпадает с языком задачи (запрос игнорируется).
            language = task.language.slug
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not session_id:
            return JsonResponse({'error': 'session_id required'}, status=400)

        session = get_object_or_404(PracticeSession, id=session_id, user=request.user, task=task)

        result = run_task_tests(task, code, language)
        save_submission(session, task, code, language, result)

        return JsonResponse({
            'session_id': session.id,
            'status': session.status,
            'score': result['score'],
            'passed': result['passed'],
            'total': result['total'],
            'all_passed': result['all_passed'],
            'runnable': result['runnable'],
            'message': result['message'],
            'xp_earned': session.xp_earned,
            'test_results': result['tests'],
            'redirect_url': reverse('practice:session_result', kwargs={'pk': session.pk}),
        })