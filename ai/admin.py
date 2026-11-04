"""Admin configuration for ai app."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ai.models import (
    AIProvider,
    AIChatSession,
    AIMessage,
    AIPromptTemplate,
    AIUsageStats,
)


class AIMessageInline(admin.TabularInline):
    """Inline for AI messages within a chat session."""

    model = AIMessage
    extra = 0
    fields = ('role', 'content', 'tokens_used', 'cost', 'model', 'finish_reason', 'created_at')
    readonly_fields = ('role', 'content', 'tokens_used', 'cost', 'model', 'finish_reason', 'created_at')
    ordering = ('-created_at',)
    can_delete = False


@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    """Admin for AIProvider."""

    list_display = ('name', 'slug', 'provider_type', 'default_model', 'is_active', 'is_default', 'priority', 'created_at')
    list_filter = ('provider_type', 'is_active', 'is_default')
    search_fields = ('name', 'slug', 'default_model')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('priority', 'name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'provider_type', 'default_model')}),
        (_('API Configuration'), {'fields': ('api_key', 'base_url')}),
        (_('Model Parameters'), {'fields': ('default_temperature', 'default_max_tokens')}),
        (_('Capabilities'), {'fields': ('supports_streaming', 'supports_functions', 'supports_vision')}),
        (_('Rate Limits'), {'fields': ('requests_per_minute', 'tokens_per_minute')}),
        (_('Status'), {'fields': ('is_active', 'is_default', 'priority')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(AIChatSession)
class AIChatSessionAdmin(admin.ModelAdmin):
    """Admin for AIChatSession."""

    list_display = ('user', 'provider', 'title', 'model', 'total_tokens_used', 'total_cost', 'is_active', 'closed_at', 'created_at')
    list_filter = ('is_active', 'provider', 'model')
    search_fields = ('user__email', 'title', 'model')
    raw_id_fields = ('user', 'provider', 'topic', 'lesson', 'practice_task')
    ordering = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at', 'total_tokens_used', 'total_cost')
    inlines = [AIMessageInline]

    fieldsets = (
        (None, {'fields': ('user', 'provider', 'title', 'system_prompt')}),
        (_('Context'), {'fields': ('topic', 'lesson', 'practice_task')}),
        (_('Model'), {'fields': ('model', 'temperature')}),
        (_('Usage'), {'fields': ('total_tokens_used', 'total_cost')}),
        (_('Status'), {'fields': ('is_active', 'closed_at')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    """Admin for AIMessage."""

    list_display = ('session', 'role', 'tokens_used', 'cost', 'model', 'finish_reason', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('session__title', 'content', 'model', 'finish_reason')
    raw_id_fields = ('session',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('session', 'role', 'content')}),
        (_('Metadata'), {'fields': ('tokens_used', 'cost', 'model', 'finish_reason')}),
        (_('Tool Calls'), {'fields': ('tool_calls', 'tool_call_id')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(AIPromptTemplate)
class AIPromptTemplateAdmin(admin.ModelAdmin):
    """Admin for AIPromptTemplate."""

    list_display = ('name', 'slug', 'category', 'default_temperature', 'default_max_tokens', 'version', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('category', 'name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'category')}),
        (_('Template'), {'fields': ('system_prompt', 'user_prompt_template')}),
        (_('Parameters'), {'fields': ('default_temperature', 'default_max_tokens', 'variables_schema')}),
        (_('Versioning'), {'fields': ('version', 'is_active')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(AIUsageStats)
class AIUsageStatsAdmin(admin.ModelAdmin):
    """Admin for AIUsageStats."""

    list_display = ('user', 'provider', 'date', 'requests_count', 'input_tokens', 'output_tokens', 'total_tokens', 'estimated_cost')
    list_filter = ('provider', 'date')
    search_fields = ('user__email', 'provider__name')
    raw_id_fields = ('user', 'provider')
    ordering = ('-date',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('user', 'provider', 'date')}),
        (_('Usage'), {'fields': ('requests_count', 'input_tokens', 'output_tokens', 'total_tokens', 'estimated_cost')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
