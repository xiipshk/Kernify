"""Views for practice app."""
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView, View
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit

from ai.services import (
    AIServiceError,
    chat_completion,
    check_request_policy,
    detect_policy_risk,
    ensure_default_provider,
    policy_refusal,
    programming_only_prompt,
    record_usage,
    sanitize_output,
)
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


class TaskAIHelpAPIView(LoginRequiredMixin, View):
    """POST /practice/api/tasks/<slug>/ai-help/ — контекстная помощь ИИ по задаче."""

    MAX_CODE_LENGTH = 12000
    MAX_QUESTION_LENGTH = 2000
    MAX_HISTORY_MESSAGES = 10

    @method_decorator(ratelimit(key='user', rate='20/m', method='POST', block=True))
    def post(self, request, slug):
        task = get_object_or_404(
            PracticeTask.objects.select_related('topic__program__language'),
            slug=slug,
            status='published',
        )

        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except (ValueError, UnicodeDecodeError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not isinstance(payload, dict):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        mode = payload.get('mode') or 'question'
        if mode not in {'hint', 'review', 'question'}:
            mode = 'question'

        question = payload.get('question') or ''
        if not isinstance(question, str):
            return JsonResponse({'error': 'Invalid question'}, status=400)
        question = question.strip()
        if len(question) > self.MAX_QUESTION_LENGTH:
            return JsonResponse({'error': 'Question is too long'}, status=400)
        if mode == 'question' and not question:
            return JsonResponse({'error': 'Question is required'}, status=400)

        code = payload.get('code') or ''
        if not isinstance(code, str):
            return JsonResponse({'error': 'Invalid code'}, status=400)
        code = code[:self.MAX_CODE_LENGTH]

        history = self._clean_history(payload.get('history'))

        # Security: check the user's question and code for injection / data
        # exfiltration / internal-information requests before calling the model.
        risk = detect_policy_risk(code)
        if risk:
            return JsonResponse({
                'answer': policy_refusal(risk),
                'blocked': True,
                'reason': risk,
            })

        provider = ensure_default_provider()
        check = None
        if question:
            classification_context = [
                f'Практическая задача по программированию: {task.name}',
                f'Язык: {task.language.name} ({task.language.slug})',
                f'Текущий код ученика: {code[:800]}',
            ]
            classification_context += [
                f'{item["role"]}: {item["content"][:500]}'
                for item in history[-4:]
            ]
            try:
                check = check_request_policy(
                    question,
                    provider=provider,
                    context=classification_context,
                )
            except AIServiceError as exc:
                return JsonResponse({'error': str(exc)}, status=502)
            if not check['allowed']:
                record_usage(
                    request.user,
                    provider,
                    prompt_tokens=check['prompt_tokens'],
                    completion_tokens=check['completion_tokens'],
                    total_tokens=check['total_tokens'],
                )
                return JsonResponse({
                    'answer': policy_refusal(check['reason']),
                    'blocked': True,
                    'reason': check['reason'],
                })

        system_prompt = programming_only_prompt(
            'Ты — AI-наставник по практическим задачам на платформе Kernify. '
            'Твоя цель — помочь ученику самому найти и понять ошибку. Анализируй '
            'его код и объясняй, из-за чего код может не работать, на какие '
            'участки и случаи стоит обратить внимание. НЕ указывай точное место '
            'ошибки, НЕ говори, что именно исправить, и НЕ давай готовый код. '
            'Задавай наводящие вопросы и предлагай проверить гипотезы. Если '
            'ученик просит готовое решение, вежливо откажись и предложи разобрать '
            'задачу по шагам. Отвечай кратко, по делу и на языке пользователя.'
        )

        task_context = self._build_task_context(task)
        if mode == 'hint':
            instruction = (
                'Проанализируй текущий код ученика и подскажи, из-за чего он '
                'может не работать. Опиши возможные причины и области для '
                'проверки, но не называй конкретную ошибку и не говори, что '
                'именно исправить. Не давай готовый код.'
            )
            if question:
                instruction += f'\n\nДополнительный вопрос ученика: {question}'
        elif mode == 'review':
            instruction = (
                'Разбери текущий код ученика и предположи, из-за чего он может '
                'не проходить тесты. Опиши зоны риска и вопросы, которые стоит '
                'себе задать, но не указывай точное исправление и не давай '
                'готовый код.'
            )
            if question:
                instruction += f'\n\nДополнительный вопрос ученика: {question}'
        else:
            instruction = f'Вопрос ученика: {question}'

        user_parts = [f'Контекст задачи:\n{task_context}']
        if code.strip():
            user_parts.append(
                f'Текущий код ученика ({task.language.slug}):\n'
                f'```{task.language.slug}\n{code}\n```'
            )
        user_parts.append(instruction)
        user_content = '\n\n'.join(user_parts)

        messages = [{'role': 'system', 'content': system_prompt}]
        messages += history
        messages.append({'role': 'user', 'content': user_content})

        try:
            result = chat_completion(messages, provider=provider, temperature=0.4)
        except AIServiceError as exc:
            return JsonResponse({'error': str(exc)}, status=502)

        usage = check or {
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0,
        }
        record_usage(
            request.user,
            provider,
            prompt_tokens=result['prompt_tokens'] + usage['prompt_tokens'],
            completion_tokens=result['completion_tokens'] + usage['completion_tokens'],
            total_tokens=result['total_tokens'] + usage['total_tokens'],
        )

        return JsonResponse({
            'answer': sanitize_output(result['content']),
            'model': result['model'],
        })

    def _build_task_context(self, task):
        parts = [
            f'Название: {task.name}',
            f'Язык: {task.language.name} ({task.language.slug})',
            f'Тип задания: {task.get_task_type_display()}',
            f'Сложность: {task.difficulty_level}/5',
            f'Условие: {task.description[:4000]}',
        ]

        examples = []
        for index, case in enumerate((task.test_cases or [])[:3], start=1):
            if not isinstance(case, dict):
                continue
            examples.append(
                f'Пример {index}:\n'
                f'Ввод: {str(case.get("input", ""))[:500]}\n'
                f'Ожидаемый вывод: {str(case.get("expected_output", ""))[:500]}'
            )
        if examples:
            parts.append('Примеры:\n' + '\n\n'.join(examples))

        hint_texts = []
        for hint in (task.hints or [])[:5]:
            if isinstance(hint, dict):
                hint_texts.append(str(hint.get('text', ''))[:300])
            else:
                hint_texts.append(str(hint)[:300])
        hint_texts = [text for text in hint_texts if text]
        if hint_texts:
            parts.append(
                'Подсказки, которые уже доступны ученику (используй как ориентир, '
                'не пересказывай их целиком):\n- ' + '\n- '.join(hint_texts)
            )

        return '\n\n'.join(parts)

    def _clean_history(self, history):
        if not isinstance(history, list):
            return []
        cleaned = []
        for item in history[-self.MAX_HISTORY_MESSAGES:]:
            if not isinstance(item, dict):
                continue
            role = item.get('role')
            content = item.get('content')
            if role not in {'user', 'assistant'}:
                continue
            if not isinstance(content, str) or not content.strip():
                continue
            cleaned.append({'role': role, 'content': content[:4000]})
        return cleaned


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