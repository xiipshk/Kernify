"""Admin configuration for ai app."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ai.models import AIProvider, AIChatSession, AIMessage, AIPromptTemplate, AIUsageStats


@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    """Admin for AIProvider."""

    list_display = ('name', 'provider_type', 'default_model', 'is_active', 'is_default', 'priority', 'requests_per_minute', 'tokens_per_minute')
    list_filter = ('provider_type', 'is_active', 'is_default')
    search_fields = ('name', 'default_model')
    ordering = ('-is_default', 'priority', 'name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'provider_type', 'model', 'api_key', 'base_url')}),
        (_('Status'), {'fields': ('is_active', 'is_default', 'priority')}),
        (_('Rate Limits'), {'fields': ('requests_per_minute', 'tokens_per_minute', 'default_temperature', 'default_max_tokens')}),
        (_('Capabilities'), {'fields': ('supports_streaming', 'supports_functions', 'supports_vision')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(AIPromptTemplate)
class AIPromptTemplateAdmin(admin.ModelAdmin):
    """Admin for AIPromptTemplate."""

    list_display = ('name', 'category', 'version', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category', 'system_prompt')
    raw_id_fields = ()
    ordering = ('category', 'name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'category', 'version', 'is_active')}),
        (_('Prompts'), {'fields': ('system_prompt', 'user_prompt_template', 'variables_schema')}),
        (_('Model Settings'), {'fields': ('default_temperature', 'default_max_tokens')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


class AIMessageInline(admin.TabularInline):
    """Inline for AI messages."""

    model = AIMessage
    extra = 0
    fields = ('role', 'content_short', 'tokens_used', 'created_at')
    readonly_fields = ('role', 'content_short', 'tokens_used', 'created_at')
    ordering = ('created_at',)
    can_delete = False

    def content_short(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_short.short_description = _('content')


@admin.register(AIChatSession)
class AIChatSessionAdmin(admin.ModelAdmin):
    """Admin for AIChatSession."""

    list_display = ('user', 'provider', 'title', 'topic', 'total_tokens_used', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'provider', 'topic', 'created_at')
    search_fields = ('user__email', 'user__username', 'title')
    raw_id_fields = ('user', 'provider', 'topic', 'lesson', 'practice_task')
    ordering = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at', 'total_tokens_used', 'total_cost')
    inlines = [AIMessageInline]

    fieldsets = (
        (None, {'fields': ('user', 'provider', 'title', 'topic', 'lesson', 'practice_task', 'is_active')}),
        (_('Context'), {'fields': ('system_prompt', 'model', 'temperature')}),
        (_('Statistics'), {'fields': ('total_tokens_used', 'total_cost')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at', 'closed_at')}),
    )


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    """Admin for AIMessage."""

    list_display = ('session', 'role', 'content_short', 'tokens_used', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('session__user__email', 'content')
    raw_id_fields = ('session',)
    ordering = ('session', 'created_at')
    readonly_fields = ('session', 'role', 'content', 'tokens_used', 'cost', 'tool_calls', 'tool_call_id', 'model', 'finish_reason', 'created_at')

    def content_short(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_short.short_description = _('content')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AIUsageStats)
class AIUsageStatsAdmin(admin.ModelAdmin):
    """Admin for AIUsageStats."""

    list_display = ('user', 'provider', 'date', 'requests_count', 'total_tokens', 'estimated_cost')
    list_filter = ('provider', 'date')
    search_fields = ('user__email', 'user__username')
    raw_id_fields = ('user', 'provider')
    ordering = ('-date', 'user')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('user', 'provider', 'date')}),
        (_('Usage'), {'fields': ('requests_count', 'input_tokens', 'output_tokens', 'total_tokens', 'estimated_cost')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False