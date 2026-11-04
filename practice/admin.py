"""Admin configuration for practice app."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from practice.models import (
    PracticeSession,
    PracticeTask,
)


@admin.register(PracticeTask)
class PracticeTaskAdmin(admin.ModelAdmin):
    """Admin for PracticeTask."""

    list_display = (
        'name', 'topic', 'language', 'slug', 'task_type',
        'difficulty', 'status', 'order', 'created_at',
    )
    list_filter = ('status', 'task_type', 'difficulty', 'topic', 'language')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('topic', 'language')
    ordering = ('topic', 'order', 'difficulty', 'name')
    readonly_fields = ('created_at', 'updated_at', 'published_at')

    fieldsets = (
        (None, {'fields': ('topic', 'language', 'name', 'slug', 'description')}),
        (_('Task'), {'fields': ('task_type', 'difficulty', 'order')}),
        (_('Code'), {'fields': ('starter_code', 'solution')}),
        (_('Tests & Hints'), {'fields': ('test_cases', 'hints')}),
        (_('Limits & Reward'), {'fields': ('time_limit', 'memory_limit', 'xp_reward')}),
        (_('Status'), {'fields': ('status', 'published_at')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    """Admin for PracticeSession."""

    list_display = (
        'user', 'task', 'topic', 'status', 'attempts',
        'xp_earned', 'completed_at', 'created_at',
    )
    list_filter = ('status', 'topic', 'created_at')
    search_fields = ('user__email', 'task__name', 'topic__name')
    raw_id_fields = ('user', 'task', 'topic')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'completed_at')

    fieldsets = (
        (None, {'fields': ('user', 'task', 'topic', 'language')}),
        (_('Submission'), {'fields': ('submitted_code', 'status')}),
        (_('Results'), {'fields': ('test_results', 'ai_feedback')}),
        (_('Progress'), {'fields': ('hints_used', 'attempts', 'time_spent', 'xp_earned')}),
        (_('Timestamps'), {'fields': ('completed_at', 'created_at', 'updated_at')}),
    )
