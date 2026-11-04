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

    list_display = ('user', 'language', 'current_program', 'current_topic', 'lessons_completed', 'total_xp', 'current_streak', 'last_activity_at')
    list_filter = ('language', 'current_program', 'last_activity_at')
    search_fields = ('user__email', 'user__username', 'language__name')
    raw_id_fields = ('user', 'language', 'current_program', 'current_topic', 'current_subtopic', 'current_lesson')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-last_activity_at',)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    """Admin for LessonProgress."""

    list_display = ('user', 'lesson', 'status', 'time_spent', 'review_count', 'started_at', 'completed_at')
    list_filter = ('status', 'lesson__subtopic__topic', 'started_at', 'completed_at')
    search_fields = ('user__email', 'user__username', 'lesson__title')
    raw_id_fields = ('user', 'lesson')
    readonly_fields = ('created_at', 'updated_at', 'started_at', 'completed_at', 'last_reviewed_at', 'next_review_at')
    ordering = ('-updated_at',)


@admin.register(TopicProgress)
class TopicProgressAdmin(admin.ModelAdmin):
    """Admin for TopicProgress."""

    list_display = ('user', 'topic', 'status', 'test_score', 'lessons_total', 'lessons_completed', 'completion_percentage', 'completed_at')
    list_filter = ('status', 'topic__program', 'completed_at')
    search_fields = ('user__email', 'user__username', 'topic__name')
    raw_id_fields = ('user', 'topic')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    ordering = ('topic__order',)


@admin.register(ErrorHistory)
class ErrorHistoryAdmin(admin.ModelAdmin):
    """Admin for ErrorHistory."""

    list_display = ('user', 'topic', 'error_type', 'count', 'is_resolved', 'interval_days', 'ease_factor', 'next_review')
    list_filter = ('error_type', 'is_resolved', 'topic__program')
    search_fields = ('user__email', 'user__username', 'topic__name', 'error_description')
    raw_id_fields = ('user', 'topic', 'lesson', 'practice_task')
    readonly_fields = ('created_at', 'updated_at', 'last_seen')
    ordering = ('-last_seen',)


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    """Admin for TestResult."""

    list_display = ('user', 'topic', 'test_type', 'score', 'questions_total', 'questions_correct', 'passed', 'created_at')
    list_filter = ('test_type', 'topic__program', 'created_at')
    search_fields = ('user__email', 'user__username', 'topic__name')
    raw_id_fields = ('user', 'topic')
    readonly_fields = ('created_at', 'updated_at', 'passed')
    ordering = ('-created_at',)

    def passed(self, obj):
        return obj.passed
    passed.boolean = True
    passed.short_description = _('passed')