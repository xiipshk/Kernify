"""Admin configuration for practice app."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from practice.models import PracticeTask, PracticeSession


@admin.register(PracticeTask)
class PracticeTaskAdmin(admin.ModelAdmin):
    """Admin for PracticeTask."""

    list_display = ('name', 'topic', 'language', 'slug', 'task_type', 'difficulty', 'order', 'xp_reward', 'time_limit', 'status', 'created_at')
    list_filter = ('task_type', 'difficulty', 'topic', 'language', 'status')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('topic', 'language')
    ordering = ('topic', 'order', 'difficulty', 'name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('topic', 'language', 'name', 'slug', 'description', 'task_type', 'difficulty')}),
        (_('Content'), {'fields': ('starter_code', 'solution', 'test_cases', 'hints')}),
        (_('Settings'), {'fields': ('order', 'xp_reward', 'time_limit', 'memory_limit', 'status')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    """Admin for PracticeSession."""

    list_display = ('user', 'task', 'topic', 'status', 'hints_used', 'attempts', 'time_spent', 'xp_earned', 'completed_at', 'created_at')
    list_filter = ('status', 'task', 'topic', 'created_at')
    search_fields = ('user__email', 'user__username', 'task__name')
    raw_id_fields = ('user', 'task', 'topic')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'test_results', 'ai_feedback', 'completed_at')

    fieldsets = (
        (None, {'fields': ('user', 'task', 'topic', 'status')}),
        (_('Submission'), {'fields': ('submitted_code', 'language')}),
        (_('Results'), {'fields': ('test_results', 'ai_feedback', 'hints_used', 'attempts', 'time_spent', 'xp_earned')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at', 'completed_at')}),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False