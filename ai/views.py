"""Views for ai app."""
import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django_ratelimit.decorators import ratelimit

from ai.models import AIChatSession, AIMessage, AIProvider, AIPromptTemplate
from ai.services import (
    DEFAULT_SYSTEM_PROMPT,
    MAX_HISTORY_MESSAGES,
    MAX_MESSAGE_LENGTH,
    AIServiceError,
    chat_completion,
    check_request_policy,
    detect_policy_risk,
    ensure_default_provider,
    get_provider,
    policy_refusal,
    programming_only_prompt,
    record_usage,
    sanitize_output,
)

logger = logging.getLogger(__name__)


class ChatView(LoginRequiredMixin, ListView):
    """AI Chat list."""

    model = AIChatSession
    template_name = 'ai/chat.html'
    context_object_name = 'chats'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return AIChatSession.objects.filter(user=self.request.user).order_by('-updated_at')


class NewChatView(LoginRequiredMixin, View):
    """Create new chat session."""

    def get(self, request):
        default_provider = ensure_default_provider()

        chat = AIChatSession.objects.create(
            user=request.user,
            provider=default_provider,
            title=_('New Chat')
        )
        # Redirect to chat detail - title will be auto-generated from first message
        return redirect('ai:chat_detail', pk=chat.pk)


class ChatDetailView(LoginRequiredMixin, DetailView):
    """Chat detail view."""

    model = AIChatSession
    template_name = 'ai/chat_detail.html'
    context_object_name = 'chat'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return AIChatSession.objects.filter(user=self.request.user).prefetch_related(
            models.Prefetch('messages', queryset=AIMessage.objects.order_by('created_at'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chat = self.object
        context['chats'] = AIChatSession.objects.filter(user=self.request.user).order_by('-updated_at')
        context['providers'] = AIProvider.objects.filter(is_active=True)
        context['templates'] = AIPromptTemplate.objects.filter(is_active=True)
        return context


class ChatDeleteView(LoginRequiredMixin, View):
    """Delete chat session."""

    def post(self, request, pk):
        chat = get_object_or_404(AIChatSession, pk=pk, user=request.user)
        chat.delete()
        return redirect('ai:chat')


class AssistantView(LoginRequiredMixin, TemplateView):
    """AI Assistant page."""

    template_name = 'ai/assistant.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = AIProvider.objects.filter(is_active=True)
        return context


class AskAssistantView(LoginRequiredMixin, View):
    """Ask AI assistant (AJAX)."""

    @method_decorator(ratelimit(key='user', rate='30/m', method='POST', block=True))
    def post(self, request):
        question = (request.POST.get('question') or '').strip()
        context_code = (request.POST.get('context_code') or '').strip()
        language = (request.POST.get('language') or 'python').strip() or 'python'

        if not question:
            return JsonResponse({'error': _('Please enter a question.')}, status=400)
        if len(question) > MAX_MESSAGE_LENGTH:
            return JsonResponse({'error': _('Your question is too long.')}, status=400)

        user_content = question
        if context_code:
            user_content += (
                f'\n\nКод ({language}):\n```{language}\n{context_code}\n```'
            )

        provider = get_provider(request.POST.get('provider')) or ensure_default_provider()

        check = None
        if context_code:
            risk = detect_policy_risk(f'{question}\n{context_code}')
            if risk:
                return JsonResponse({
                    'answer': policy_refusal(risk),
                    'blocked': True,
                    'reason': risk,
                })
        else:
            try:
                check = check_request_policy(question, provider=provider)
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

        messages = [
            {'role': 'system', 'content': programming_only_prompt(DEFAULT_SYSTEM_PROMPT)},
            {'role': 'user', 'content': user_content},
        ]

        try:
            result = chat_completion(messages, provider=provider)
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
            'usage': {
                'prompt_tokens': result['prompt_tokens'],
                'completion_tokens': result['completion_tokens'],
                'total_tokens': result['total_tokens'],
            },
        })


class ChatMessageAPIView(View):
    """POST /api/ai/chat/ — send a message to the AI chat and persist both replies."""

    @method_decorator(ratelimit(key='user', rate='30/m', method='POST', block=True))
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': _('Authentication required.')}, status=401)

        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except (ValueError, UnicodeDecodeError):
            return JsonResponse({'error': _('Invalid request body.')}, status=400)

        if not isinstance(payload, dict):
            return JsonResponse({'error': _('Invalid request body.')}, status=400)

        try:
            chat_id = int(payload.get('chat_id'))
        except (TypeError, ValueError):
            return JsonResponse({'error': _('Chat is required.')}, status=400)

        message = payload.get('message')
        if not isinstance(message, str) or not message.strip():
            return JsonResponse({'error': _('Message cannot be empty.')}, status=400)
        message = message.strip()
        if len(message) > MAX_MESSAGE_LENGTH:
            return JsonResponse({'error': _('Message is too long.')}, status=400)

        chat = get_object_or_404(AIChatSession, pk=chat_id, user=request.user)

        provider = get_provider(payload.get('provider_id')) or ensure_default_provider()
        chat.provider = provider

        history = list(
            chat.messages.filter(
                role__in=[AIMessage.Role.USER, AIMessage.Role.ASSISTANT]
            ).order_by('-created_at')[:MAX_HISTORY_MESSAGES]
        )[::-1]
        classification_context = [
            f'{item.role}: {item.content}' for item in history[-6:]
        ]

        try:
            check = check_request_policy(
                message, provider=provider, context=classification_context
            )
        except AIServiceError as exc:
            return JsonResponse({'error': str(exc)}, status=502)

        # Set a readable title from the first user message.
        if not chat.title.strip() or chat.title in ('New Chat', 'Новый чат'):
            chat.title = message[:60]

        AIMessage.objects.create(
            session=chat,
            role=AIMessage.Role.USER,
            content=message,
        )

        if not check['allowed']:
            refusal = policy_refusal(check['reason'])
            record_usage(
                request.user,
                provider,
                prompt_tokens=check['prompt_tokens'],
                completion_tokens=check['completion_tokens'],
                total_tokens=check['total_tokens'],
            )
            assistant_message = AIMessage.objects.create(
                session=chat,
                role=AIMessage.Role.ASSISTANT,
                content=refusal,
                finish_reason=f'blocked:{check["reason"]}',
            )
            chat.total_tokens_used = F('total_tokens_used') + check['total_tokens']
            chat.save(update_fields=[
                'title', 'provider', 'total_tokens_used', 'updated_at',
            ])
            return JsonResponse({
                'answer': refusal,
                'blocked': True,
                'reason': check['reason'],
                'message_id': assistant_message.pk,
            })

        messages = [
            {
                'role': 'system',
                'content': programming_only_prompt(
                    chat.system_prompt or DEFAULT_SYSTEM_PROMPT
                ),
            },
        ]
        messages += [
            {'role': item.role, 'content': item.content}
            for item in history
        ]
        messages.append({'role': 'user', 'content': message})

        try:
            result = chat_completion(messages, provider=provider)
        except AIServiceError as exc:
            chat.save(update_fields=['title', 'provider', 'updated_at'])
            return JsonResponse({'error': str(exc)}, status=502)

        assistant_message = AIMessage.objects.create(
            session=chat,
            role=AIMessage.Role.ASSISTANT,
            content=sanitize_output(result['content']),
            tokens_used=result['total_tokens'],
            model=result['model'],
            finish_reason=result['finish_reason'],
        )

        chat.model = result['model']
        chat.total_tokens_used = (
            F('total_tokens_used') + result['total_tokens'] + check['total_tokens']
        )
        chat.save(update_fields=['title', 'provider', 'model', 'total_tokens_used', 'updated_at'])

        record_usage(
            request.user,
            provider,
            prompt_tokens=result['prompt_tokens'] + check['prompt_tokens'],
            completion_tokens=result['completion_tokens'] + check['completion_tokens'],
            total_tokens=result['total_tokens'] + check['total_tokens'],
        )

        return JsonResponse({
            'answer': sanitize_output(result['content']),
            'message_id': assistant_message.pk,
            'model': result['model'],
            'usage': {
                'prompt_tokens': result['prompt_tokens'],
                'completion_tokens': result['completion_tokens'],
                'total_tokens': result['total_tokens'],
            },
        })


class CodeReviewView(LoginRequiredMixin, TemplateView):
    """Code review page."""

    template_name = 'ai/code_review.html'
    login_url = reverse_lazy('accounts:login')


class CodeReviewSubmitView(LoginRequiredMixin, View):
    """Submit code for review."""

    @method_decorator(ratelimit(key='user', rate='10/m', method='POST', block=True))
    def post(self, request):
        code = (request.POST.get('code') or '').strip()
        language = (request.POST.get('language') or 'python').strip() or 'python'
        focus = (request.POST.get('focus') or 'general').strip() or 'general'

        if not code:
            return JsonResponse({'error': _('Please provide code to review.')}, status=400)
        if len(code) > 20000:
            return JsonResponse({'error': _('Code is too long.')}, status=400)

        risk = detect_policy_risk(code)
        if risk:
            return JsonResponse({
                'review': policy_refusal(risk),
                'blocked': True,
                'reason': risk,
            })

        focus_prompts = {
            'general': 'общее качество кода, читаемость и логику',
            'performance': 'производительность и сложность алгоритмов',
            'security': 'безопасность и потенциальные уязвимости',
            'style': 'стиль кода, именование и соответствие best practices',
            'bugs': 'поиск багов, крайних случаев и логических ошибок',
        }
        focus_text = focus_prompts.get(focus, focus_prompts['general'])

        system_prompt = programming_only_prompt((
            'Ты — опытный senior-разработчик и наставник. Проведи код-ревью кода '
            'ученика. Сосредоточься на: {focus}. Отвечай структурированно, '
            'используй заголовки и маркированные списки. Если код корректен, '
            'скажи об этом прямо. Не переписывай весь код без необходимости — '
            'показывай только важные фрагменты. Отвечай на языке пользователя.'
        ).format(focus=focus_text))

        messages = [
            {'role': 'system', 'content': system_prompt},
            {
                'role': 'user',
                'content': f'Проверь этот код ({language}):\n```{language}\n{code}\n```',
            },
        ]

        provider = get_provider(request.POST.get('provider')) or ensure_default_provider()
        try:
            result = chat_completion(messages, provider=provider, temperature=0.3)
        except AIServiceError as exc:
            return JsonResponse({'error': str(exc)}, status=502)

        record_usage(
            request.user,
            provider,
            prompt_tokens=result['prompt_tokens'],
            completion_tokens=result['completion_tokens'],
            total_tokens=result['total_tokens'],
        )
        return JsonResponse({
            'review': sanitize_output(result['content']),
            'model': result['model'],
        })


class ExplainCodeView(LoginRequiredMixin, TemplateView):
    """Explain code page."""

    template_name = 'ai/explain.html'
    login_url = reverse_lazy('accounts:login')


class ExplainCodeSubmitView(LoginRequiredMixin, View):
    """Explain a code snippet with the AI provider (AJAX)."""

    @method_decorator(ratelimit(key='user', rate='20/m', method='POST', block=True))
    def post(self, request):
        code = (request.POST.get('code') or '').strip()
        language = (request.POST.get('language') or 'python').strip() or 'python'
        detail = (request.POST.get('detail') or 'beginner').strip() or 'beginner'

        if not code:
            return JsonResponse({'error': _('Please provide code to explain.')}, status=400)
        if len(code) > 20000:
            return JsonResponse({'error': _('Code is too long.')}, status=400)

        risk = detect_policy_risk(code)
        if risk:
            return JsonResponse({
                'explanation': policy_refusal(risk),
                'blocked': True,
                'reason': risk,
            })

        detail_prompts = {
            'beginner': 'объясняй простыми словами, как новичку, без сложных терминов',
            'intermediate': 'объясняй для разработчика со средним опытом',
            'advanced': 'объясняй технически подробно, включая нюансы реализации',
        }
        detail_text = detail_prompts.get(detail, detail_prompts['beginner'])

        system_prompt = programming_only_prompt((
            'Ты — преподаватель программирования на платформе Kernify. '
            'Объясни, что делает код: сначала общий смысл, затем разбери '
            'ключевые строки и конструкции. {detail}. Отвечай на языке '
            'пользователя, структурируй ответ.'
        ).format(detail=detail_text[0].upper() + detail_text[1:]))

        messages = [
            {'role': 'system', 'content': system_prompt},
            {
                'role': 'user',
                'content': f'Объясни этот код ({language}):\n```{language}\n{code}\n```',
            },
        ]

        provider = get_provider(request.POST.get('provider')) or ensure_default_provider()
        try:
            result = chat_completion(messages, provider=provider, temperature=0.4)
        except AIServiceError as exc:
            return JsonResponse({'error': str(exc)}, status=502)

        record_usage(
            request.user,
            provider,
            prompt_tokens=result['prompt_tokens'],
            completion_tokens=result['completion_tokens'],
            total_tokens=result['total_tokens'],
        )
        return JsonResponse({
            'explanation': sanitize_output(result['content']),
            'model': result['model'],
        })


class GenerateExerciseView(LoginRequiredMixin, TemplateView):
    """Generate exercise page."""

    template_name = 'ai/generate_exercise.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = AIProvider.objects.filter(is_active=True)
        return context


class GenerateExerciseSubmitView(LoginRequiredMixin, View):
    """Generate a practice exercise with the AI provider (AJAX)."""

    @method_decorator(ratelimit(key='user', rate='10/m', method='POST', block=True))
    def post(self, request):
        topic = (request.POST.get('topic') or '').strip()
        language = (request.POST.get('language') or 'python').strip() or 'python'
        difficulty = (request.POST.get('difficulty') or 'easy').strip() or 'easy'
        exercise_type = (request.POST.get('type') or 'coding').strip() or 'coding'

        if not topic:
            return JsonResponse({'error': _('Please provide a topic.')}, status=400)
        if len(topic) > 500:
            return JsonResponse({'error': _('Topic is too long.')}, status=400)

        difficulty_labels = {
            'easy': 'лёгкий (для новичков)',
            'medium': 'средний',
            'hard': 'сложный',
            'expert': 'экспертный',
        }
        type_labels = {
            'coding': 'задача на написание кода',
            'quiz': 'вопрос с вариантами ответа',
            'debugging': 'задача на поиск и исправление ошибок',
            'completion': 'задача на дополнение кода',
        }

        system_prompt = programming_only_prompt((
            'Ты — методист образовательной платформы Kernify. Составь учебное '
            'задание по программированию. Требования: понятное условие, формат '
            'ввода/вывода, 2–3 примера, ограничения, подсказки (не раскрывающие '
            'решение сразу), starter-код и тест-кейсы. В конце приведи решение '
            'в свёрнутом виде под заголовком «Решение». Отвечай на русском языке '
            'в структурированном Markdown.'
        ))
        user_prompt = (
            f'Тема: {topic}\n'
            f'Язык программирования: {language}\n'
            f'Сложность: {difficulty_labels.get(difficulty, difficulty)}\n'
            f'Тип задания: {type_labels.get(exercise_type, exercise_type)}'
        )

        provider = get_provider(request.POST.get('provider')) or ensure_default_provider()

        try:
            check = check_request_policy(topic, provider=provider)
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
                'exercise': policy_refusal(check['reason']),
                'blocked': True,
                'reason': check['reason'],
            })

        try:
            result = chat_completion(
                [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
                provider=provider,
                temperature=0.8,
            )
        except AIServiceError as exc:
            return JsonResponse({'error': str(exc)}, status=502)

        record_usage(
            request.user,
            provider,
            prompt_tokens=result['prompt_tokens'] + check['prompt_tokens'],
            completion_tokens=result['completion_tokens'] + check['completion_tokens'],
            total_tokens=result['total_tokens'] + check['total_tokens'],
        )
        return JsonResponse({
            'exercise': sanitize_output(result['content']),
            'model': result['model'],
        })


class UsageStatsView(LoginRequiredMixin, TemplateView):
    """AI usage statistics."""

    template_name = 'ai/usage.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        from types import SimpleNamespace
        from django.db.models import Sum
        from ai.models import AIUsageStats

        context = super().get_context_data(**kwargs)
        
        # Aggregate usage stats from database
        stats = AIUsageStats.objects.filter(user=self.request.user).aggregate(
            total_requests=Sum('requests_count'),
            total_tokens=Sum('total_tokens'),
            total_cost=Sum('estimated_cost'),
        )
        
        daily_stats = AIUsageStats.objects.filter(user=self.request.user).order_by('-date')[:30]
        
        context['usage'] = SimpleNamespace(
            total_requests=stats['total_requests'] or 0,
            total_tokens=stats['total_tokens'] or 0,
            total_cost=stats['total_cost'] or 0,
            errors_count=0,  # Would need error tracking model
            daily_stats=daily_stats,
        )
        return context
