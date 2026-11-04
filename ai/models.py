"""
AI integration models: Abstract interfaces for future AI providers.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from core.models import TimeStampedModel


class AIProvider(TimeStampedModel):
    """
    Abstract AI provider configuration.
    Allows switching between different AI providers without code changes.
    """

    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)

    # Provider type
    class ProviderType(models.TextChoices):
        OPENAI = 'openai', _('OpenAI')
        ANTHROPIC = 'anthropic', _('Anthropic')
        LOCAL = 'local', _('Local Model')
        CUSTOM = 'custom', _('Custom API')

    provider_type = models.CharField(
        _('provider type'),
        max_length=20,
        choices=ProviderType.choices,
        default=ProviderType.OPENAI,
    )

    # API Configuration
    api_key = models.CharField(_('API key'), max_length=500, blank=True)
    base_url = models.URLField(_('base URL'), blank=True)
    default_model = models.CharField(_('default model'), max_length=100)

    # Model parameters
    default_temperature = models.FloatField(_('default temperature'), default=0.7)
    default_max_tokens = models.PositiveIntegerField(_('default max tokens'), default=4096)

    # Capabilities
    supports_streaming = models.BooleanField(_('supports streaming'), default=True)
    supports_functions = models.BooleanField(_('supports function calling'), default=False)
    supports_vision = models.BooleanField(_('supports vision'), default=False)

    # Rate limits
    requests_per_minute = models.PositiveIntegerField(_('requests per minute'), default=60)
    tokens_per_minute = models.PositiveIntegerField(_('tokens per minute'), default=100000)

    # Status
    is_active = models.BooleanField(_('active'), default=True)
    is_default = models.BooleanField(_('default'), default=False)

    # Priority (lower = higher priority)
    priority = models.PositiveIntegerField(_('priority'), default=100)

    objects = models.Manager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = _('AI provider')
        verbose_name_plural = _('AI providers')
        ordering = ['priority', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"

    def save(self, *args, **kwargs):
        # Ensure only one default provider
        if self.is_default:
            AIProvider.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class AIChatSession(TimeStampedModel):
    """
    AI chat session for a user on a specific topic/lesson.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_chat_sessions',
        verbose_name=_('user'),
    )

    provider = models.ForeignKey(
        AIProvider,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_sessions',
        verbose_name=_('provider'),
    )

    # Context
    topic = models.ForeignKey(
        'learning.Topic',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_chat_sessions',
        verbose_name=_('topic'),
    )
    lesson = models.ForeignKey(
        'learning.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_chat_sessions',
        verbose_name=_('lesson'),
    )
    practice_task = models.ForeignKey(
        'practice.PracticeTask',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_chat_sessions',
        verbose_name=_('practice task'),
    )

    # Session metadata
    title = models.CharField(_('title'), max_length=200, blank=True)
    system_prompt = models.TextField(_('system prompt'), blank=True)

    # Model used
    model = models.CharField(_('model'), max_length=100, blank=True)
    temperature = models.FloatField(_('temperature'), null=True, blank=True)

    # Token usage
    total_tokens_used = models.PositiveIntegerField(_('total tokens used'), default=0)
    total_cost = models.DecimalField(_('total cost (USD)'), max_digits=10, decimal_places=6, default=0)

    # Status
    is_active = models.BooleanField(_('active'), default=True)
    closed_at = models.DateTimeField(_('closed at'), null=True, blank=True)

    objects = models.Manager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = _('AI chat session')
        verbose_name_plural = _('AI chat sessions')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.email} - {self.title or 'AI Chat'}"


class AIMessage(TimeStampedModel):
    """
    Individual message in an AI chat session.
    """

    session = models.ForeignKey(
        AIChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('session'),
    )

    # Role
    class Role(models.TextChoices):
        SYSTEM = 'system', _('System')
        USER = 'user', _('User')
        ASSISTANT = 'assistant', _('Assistant')
        TOOL = 'tool', _('Tool')

    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Role.choices,
    )

    content = models.TextField(_('content'))

    # Metadata
    tokens_used = models.PositiveIntegerField(_('tokens used'), default=0)
    cost = models.DecimalField(_('cost (USD)'), max_digits=10, decimal_places=6, default=0)

    # Tool calls (for function calling)
    tool_calls = models.JSONField(_('tool calls'), default=list, blank=True)
    tool_call_id = models.CharField(_('tool call ID'), max_length=100, blank=True)

    # Model response metadata
    model = models.CharField(_('model'), max_length=100, blank=True)
    finish_reason = models.CharField(_('finish reason'), max_length=50, blank=True)

    class Meta:
        verbose_name = _('AI message')
        verbose_name_plural = _('AI messages')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.session} - {self.get_role_display()}"


class AIPromptTemplate(TimeStampedModel):
    """
    Reusable prompt templates for different AI tasks.
    """

    name = models.CharField(_('name'), max_length=200, unique=True)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    description = models.TextField(_('description'), blank=True)

    # Category
    class Category(models.TextChoices):
        EXPLAIN = 'explain', _('Explain Concept')
        DEBUG = 'debug', _('Debug Code')
        HINT = 'hint', _('Generate Hint')
        SOLUTION = 'solution', _('Explain Solution')
        GENERATE_TASK = 'generate_task', _('Generate Task')
        GENERATE_TEST = 'generate_test', _('Generate Test')
        FEEDBACK = 'feedback', _('Generate Feedback')
        ADAPT = 'adapt', _('Adapt Content')
        CUSTOM = 'custom', _('Custom')

    category = models.CharField(
        _('category'),
        max_length=20,
        choices=Category.choices,
        default=Category.CUSTOM,
    )

    # Template
    system_prompt = models.TextField(_('system prompt'))
    user_prompt_template = models.TextField(
        _('user prompt template'),
        help_text=_('Use {variable} placeholders for dynamic content'),
    )

    # Parameters
    default_temperature = models.FloatField(_('default temperature'), default=0.7)
    default_max_tokens = models.PositiveIntegerField(_('default max tokens'), default=2048)

    # Variables (JSON schema for validation)
    variables_schema = models.JSONField(
        _('variables schema'),
        default=dict,
        blank=True,
        help_text=_('JSON schema for template variables'),
    )

    # Versioning
    version = models.PositiveIntegerField(_('version'), default=1)
    is_active = models.BooleanField(_('active'), default=True)

    objects = models.Manager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = _('AI prompt template')
        verbose_name_plural = _('AI prompt templates')
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

    def render(self, variables):
        """Render template with variables."""
        prompt = self.user_prompt_template
        for key, value in variables.items():
            prompt = prompt.replace(f'{{{key}}}', str(value))
        return prompt


class AIUsageStats(TimeStampedModel):
    """
    Track AI usage for billing and limits.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_usage_stats',
        verbose_name=_('user'),
    )

    provider = models.ForeignKey(
        AIProvider,
        on_delete=models.CASCADE,
        related_name='usage_stats',
        verbose_name=_('provider'),
    )

    # Period
    date = models.DateField(_('date'))

    # Usage
    requests_count = models.PositiveIntegerField(_('requests count'), default=0)
    input_tokens = models.PositiveIntegerField(_('input tokens'), default=0)
    output_tokens = models.PositiveIntegerField(_('output tokens'), default=0)
    total_tokens = models.PositiveIntegerField(_('total tokens'), default=0)
    estimated_cost = models.DecimalField(_('estimated cost (USD)'), max_digits=10, decimal_places=6, default=0)

    class Meta:
        verbose_name = _('AI usage stats')
        verbose_name_plural = _('AI usage stats')
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['user', 'provider', 'date'], name='unique_user_provider_date'),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.provider.name} - {self.date}"