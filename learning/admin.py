"""Admin configuration for learning app."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from learning.models import (
    ProgrammingLanguage,
    CourseProgram,
    Topic,
    Lesson,
    LessonAttachment,
    LessonVersion,
)


class LessonAttachmentInline(admin.TabularInline):
    """Inline for lesson attachments."""

    model = LessonAttachment
    extra = 1
    fields = ('file', 'name', 'attachment_type', 'description', 'file_size', 'mime_type')
    ordering = ('-created_at',)


class LessonVersionInline(admin.TabularInline):
    """Inline for lesson versions."""

    model = LessonVersion
    extra = 0
    fields = ('version', 'created_by', 'change_log', 'created_at')
    readonly_fields = ('version', 'created_by', 'change_log', 'content', 'created_at')
    ordering = ('-version',)
    can_delete = False


@admin.register(ProgrammingLanguage)
class ProgrammingLanguageAdmin(admin.ModelAdmin):
    """Admin for ProgrammingLanguage."""

    list_display = ('name', 'slug', 'icon', 'color', 'order', 'status', 'programs_count', 'topics_count', 'lessons_count', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    readonly_fields = ('created_at', 'updated_at', 'programs_count', 'topics_count', 'lessons_count')

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'icon', 'color', 'logo', 'order')}),
        (_('Status'), {'fields': ('status', 'version')}),
        (_('Statistics'), {'fields': ('programs_count', 'topics_count', 'lessons_count')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(CourseProgram)
class CourseProgramAdmin(admin.ModelAdmin):
    """Admin for CourseProgram."""

    list_display = ('name', 'language', 'slug', 'status', 'target_level', 'order', 'topics_count', 'lessons_count', 'estimated_hours', 'created_at')
    list_filter = ('status', 'target_level', 'language')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('language',)
    ordering = ('language', 'order', 'name')
    readonly_fields = ('created_at', 'updated_at', 'topics_count', 'lessons_count')
    filter_horizontal = ('prerequisite_programs',)

    fieldsets = (
        (None, {'fields': ('language', 'name', 'slug', 'description')}),
        (_('Status & Level'), {'fields': ('status', 'target_level', 'estimated_hours', 'order')}),
        (_('Prerequisites'), {'fields': ('prerequisite_programs',)}),
        (_('Statistics'), {'fields': ('topics_count', 'lessons_count')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Admin for Topic."""

    list_display = ('name', 'program', 'slug', 'status', 'difficulty', 'order', 'is_base_topic', 'lessons_count', 'estimated_minutes')
    list_filter = ('status', 'difficulty', 'program', 'is_base_topic')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('program',)
    ordering = ('program', 'order', 'name')
    readonly_fields = ('created_at', 'updated_at', 'lessons_count')
    filter_horizontal = ('prerequisite_topics',)

    fieldsets = (
        (None, {'fields': ('program', 'name', 'slug', 'description', 'learning_objectives')}),
        (_('Status & Difficulty'), {'fields': ('status', 'difficulty', 'estimated_minutes', 'order', 'is_base_topic')}),
        (_('Prerequisites'), {'fields': ('prerequisite_topics',)}),
        (_('Statistics'), {'fields': ('lessons_count',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin for Lesson."""

    list_display = ('name', 'topic', 'slug', 'status', 'order', 'estimated_minutes', 'version', 'created_at')
    list_filter = ('status', 'topic')
    search_fields = ('name', 'slug', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('topic', 'created_by', 'updated_by')
    ordering = ('topic', 'order', 'name')
    readonly_fields = ('created_at', 'updated_at', 'version', 'content')
    filter_horizontal = ()
    inlines = [LessonAttachmentInline, LessonVersionInline]

    fieldsets = (
        (None, {'fields': ('topic', 'name', 'slug', 'short_description')}),
        (_('Content'), {'fields': ('content',)}),
        (_('Status & Order'), {'fields': ('status', 'order', 'estimated_minutes')}),
        (_('Authorship'), {'fields': ('created_by', 'updated_by', 'version', 'change_log')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(LessonAttachment)
class LessonAttachmentAdmin(admin.ModelAdmin):
    """Admin for LessonAttachment."""

    list_display = ('name', 'lesson', 'attachment_type', 'file_size', 'created_at')
    list_filter = ('attachment_type',)
    search_fields = ('name', 'lesson__name')
    raw_id_fields = ('lesson',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'file_size', 'mime_type')


@admin.register(LessonVersion)
class LessonVersionAdmin(admin.ModelAdmin):
    """Admin for LessonVersion."""

    list_display = ('lesson', 'version', 'created_by', 'change_log', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('lesson__name', 'created_by__email', 'change_log')
    raw_id_fields = ('lesson', 'created_by')
    ordering = ('-lesson', '-version')
    readonly_fields = ('lesson', 'version', 'created_by', 'change_log', 'content', 'created_at')
    can_delete = False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False