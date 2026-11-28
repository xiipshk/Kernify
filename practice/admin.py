"""Admin configuration for practice app."""
from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget

from practice.models import (
    AssessmentQuestion,
    AssessmentResult,
    CourseTestQuestion,
    CourseTestResult,
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

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('test_cases', 'hints'):
            kwargs['widget'] = JSONEditorWidget(mode='code', options={'mode': 'code'})
        return super().formfield_for_dbfield(db_field, **kwargs)


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


# --- Тест-диагностика по языку ---

@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    """Admin for AssessmentQuestion."""

    list_display = ('question_preview', 'language', 'topic_label', 'topic', 'difficulty', 'skill_level', 'order', 'status')
    list_filter = ('language', 'skill_level', 'difficulty', 'status')
    search_fields = ('question', 'topic_label', 'topic__name')
    raw_id_fields = ('topic',)
    ordering = ('language', 'order')
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    formfield_overrides = {
        models.JSONField: {
            'widget': JSONEditorWidget(mode='tree', height='240px', width='100%')
        },
    }

    fieldsets = (
        (None, {'fields': ('language', 'topic', 'topic_label', 'order', 'status')}),
        (_('Question'), {'fields': ('question', 'question_en')}),
        (_('Options'), {
            'fields': ('options',),
            'description': _('JSON: [{"text": "...", "text_en": "...", "correct": true}, ...]. '
                             'Ровно один вариант должен иметь "correct": true.'),
        }),
        (_('Explanation'), {'fields': ('explanation', 'explanation_en')}),
        (_('Difficulty'), {'fields': ('difficulty', 'skill_level')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at', 'published_at')}),
    )

    @admin.display(description=_('question'))
    def question_preview(self, obj):
        return obj.question[:80]

    def get_prepopulated_fields(self, request, obj=None):
        return {}


# --- Тест после курса ---

@admin.register(CourseTestQuestion)
class CourseTestQuestionAdmin(admin.ModelAdmin):
    """Admin for end-of-course test questions."""

    list_display = (
        'question_preview', 'program', 'question_type', 'topic_label', 'topic',
        'difficulty', 'skill_level', 'order', 'status',
    )
    list_filter = ('program', 'question_type', 'skill_level', 'difficulty', 'status')
    search_fields = ('question', 'topic_label', 'topic__name', 'program__name')
    raw_id_fields = ('topic',)
    ordering = ('program', 'order')
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    formfield_overrides = {
        models.JSONField: {
            'widget': JSONEditorWidget(mode='tree', height='240px', width='100%')
        },
    }

    fieldsets = (
        (None, {'fields': ('program', 'topic', 'topic_label', 'question_type', 'order', 'status')}),
        (_('Question'), {'fields': ('question', 'question_en')}),
        (_('Code output task'), {
            'fields': ('code_snippet', 'code_snippet_en'),
            'description': _('Shown above the answer field for code-output tasks.'),
        }),
        (_('Options'), {
            'fields': ('options',),
            'description': _(
                'JSON for choice questions: [{"text": "...", "text_en": "...", "correct": true}, ...]. '
                'For multiple choice, multiple options may have "correct": true.'
            ),
        }),
        (_('Accepted answers'), {
            'fields': ('correct_answers',),
            'description': _(
                'JSON array of accepted answers for short-answer and code-output tasks, '
                'e.g. ["42", "42.0"].'
            ),
        }),
        (_('Explanation'), {'fields': ('explanation', 'explanation_en')}),
        (_('Difficulty'), {'fields': ('difficulty', 'skill_level')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at', 'published_at')}),
    )

    @admin.display(description=_('question'))
    def question_preview(self, obj):
        return obj.question[:80]


@admin.register(CourseTestResult)
class CourseTestResultAdmin(admin.ModelAdmin):
    """Admin for saved end-of-course test results."""

    list_display = (
        'user', 'program', 'score', 'level', 'correct_answers',
        'total_questions', 'created_at',
    )
    list_filter = ('program', 'level', 'created_at')
    search_fields = ('user__email', 'program__name')
    raw_id_fields = ('user', 'program')
    ordering = ('-created_at',)
    readonly_fields = (
        'user', 'program', 'total_questions', 'correct_answers', 'score',
        'level', 'topic_breakdown', 'answers', 'created_at',
    )
