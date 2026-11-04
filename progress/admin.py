"""Admin configuration for progress app."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from progress.models import (
    UserProgress,
    LessonProgress,
    TopicProgress,
    ErrorHistory,
    TestResult,
)


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    """Admin for UserProgress."""

    list_display = (
        'user', 'language', 'current_program', 'current_topic',
        'topics_completed', 'lessons_completed', 'practice_solved',
        'total_xp', 'last_activity_at',
    )
    list_filter = ('language', 'current_program', 'current_topic', 'current_lesson')
    search_fields = ('user__email', 'language__name', 'current_program__name')
    raw_id_fields = (
        'user', 'language', 'current_program', 'current_topic',
        'current_subtopic', 'current_lesson',
    )
    ordering = ('-last_activity_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_activity_at')

    fieldsets = (
        (None, {'fields': ('user', 'language')}),
        (_('Current progress'), {
            'fields': ('current_program', 'current_topic', 'current_subtopic', 'current_lesson'),
        }),
        (_('Statistics'), {
            'fields': ('topics_completed', 'lessons_completed', 'practice_solved', 'total_xp'),
        }),
        (_('Time tracking'), {'fields': ('total_time_spent', 'last_activity_at')}),
        (_('Streak'), {
            'fields': ('current_streak', 'longest_streak', 'last_streak_date'),
        }),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    """Admin for LessonProgress."""

    list_display = (
        'user', 'lesson', 'status', 'time_spent', 'review_count',
        'started_at', 'completed_at',
    )
    list_filter = ('status', 'lesson')
    search_fields = ('user__email', 'lesson__name', 'personal_notes')
    raw_id_fields = ('user', 'lesson')
    ordering = ('-updated_at',)
    readonly_fields = (
        'created_at', 'updated_at', 'started_at', 'completed_at',
        'last_reviewed_at', 'next_review_at',
    )

    fieldsets = (
        (None, {'fields': ('user', 'lesson', 'status')}),
        (_('Time tracking'), {
            'fields': ('time_spent', 'started_at', 'completed_at'),
        }),
        (_('Review'), {
            'fields': ('review_count', 'last_reviewed_at', 'next_review_at'),
        }),
        (_('Notes'), {'fields': ('personal_notes',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(TopicProgress)
class TopicProgressAdmin(admin.ModelAdmin):
    """Admin for TopicProgress."""

    list_display = (
        'user', 'topic', 'status', 'test_score',
        'lessons_completed', 'lessons_total', 'completed_at',
    )
    list_filter = ('status', 'topic')
    search_fields = ('user__email', 'topic__name')
    raw_id_fields = ('user', 'topic')
    ordering = ('topic__order',)
    readonly_fields = ('created_at', 'updated_at', 'completed_at')

    fieldsets = (
        (None, {'fields': ('user', 'topic', 'status')}),
        (_('Test score'), {'fields': ('test_score',)}),
        (_('Completion stats'), {
            'fields': ('lessons_total', 'lessons_completed', 'completed_at'),
        }),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ErrorHistory)
class ErrorHistoryAdmin(admin.ModelAdmin):
    """Admin for ErrorHistory."""

    list_display = (
        'user', 'topic', 'lesson', 'error_type', 'count',
        'is_resolved', 'last_seen',
    )
    list_filter = ('error_type', 'is_resolved', 'topic')
    search_fields = ('user__email', 'topic__name', 'error_description')
    raw_id_fields = ('user', 'topic', 'lesson', 'practice_task')
    ordering = ('-last_seen',)
    readonly_fields = ('created_at', 'updated_at', 'last_seen')

    fieldsets = (
        (None, {'fields': ('user', 'topic', 'lesson', 'practice_task')}),
        (_('Error details'), {
            'fields': ('error_type', 'error_description', 'user_code', 'correct_code'),
        }),
        (_('Spaced repetition'), {
            'fields': ('count', 'last_seen', 'next_review', 'interval_days', 'ease_factor'),
        }),
        (_('Resolution'), {
            'fields': ('is_resolved', 'resolved_at', 'resolution_note'),
        }),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    """Admin for TestResult."""

    list_display = (
        'user', 'topic', 'test_type', 'score', 'max_score',
        'questions_correct', 'questions_total', 'time_spent',
    )
    list_filter = ('test_type', 'topic')
    search_fields = ('user__email', 'topic__name', 'ai_feedback')
    raw_id_fields = ('user', 'topic')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('user', 'topic', 'test_type')}),
        (_('Score'), {
            'fields': ('score', 'max_score', 'questions_total', 'questions_correct', 'questions_partial'),
        }),
        (_('Details'), {'fields': ('answers', 'ai_feedback')}),
        (_('Time'), {'fields': ('time_spent',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
