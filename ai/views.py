"""Views for ai app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView, View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from ai.models import AIChatSession, AIMessage, AIProvider, AIPromptTemplate


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
        default_provider = AIProvider.objects.filter(is_default=True, is_active=True).first()

        chat = AIChatSession.objects.create(
            user=request.user,
            provider=default_provider,
            title=_('New Chat')
        )
        return redirect('ai:chat_detail', pk=chat.pk)


class ChatDetailView(LoginRequiredMixin, DetailView):
    """Chat detail view."""

    model = AIChatSession
    template_name = 'ai/chat_detail.html'
    context_object_name = 'chat'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return AIChatSession.objects.filter(user=self.request.user).prefetch_related('messages')

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
        # Placeholder for AI integration
        question = request.POST.get('question', '')
        context_code = request.POST.get('context_code', '')

        # Would integrate with AI provider here
        answer = _('AI integration coming soon. Your question: ') + question

        return JsonResponse({'answer': answer})


class CodeReviewView(LoginRequiredMixin, TemplateView):
    """Code review page."""

    template_name = 'ai/code_review.html'
    login_url = reverse_lazy('accounts:login')


class CodeReviewSubmitView(LoginRequiredMixin, View):
    """Submit code for review."""

    @method_decorator(ratelimit(key='user', rate='10/m', method='POST', block=True))
    def post(self, request):
        code = request.POST.get('code', '')
        language = request.POST.get('language', 'python')

        # Placeholder
        review = _('Code review coming soon.')

        return JsonResponse({'review': review})


class ExplainCodeView(LoginRequiredMixin, TemplateView):
    """Explain code page."""

    template_name = 'ai/explain.html'
    login_url = reverse_lazy('accounts:login')


class GenerateExerciseView(LoginRequiredMixin, TemplateView):
    """Generate exercise page."""

    template_name = 'ai/generate_exercise.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = AIProvider.objects.filter(is_active=True)
        return context


class UsageStatsView(LoginRequiredMixin, TemplateView):
    """AI usage statistics."""

    template_name = 'ai/usage.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        from types import SimpleNamespace

        context = super().get_context_data(**kwargs)
        context['usage'] = SimpleNamespace(
            total_requests=0,
            total_tokens=0,
            total_cost=0,
            errors_count=0,
            daily_stats=[],
        )
        return context