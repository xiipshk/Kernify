"""Admin configuration for learning app."""
import json

from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django_json_widget.widgets import JSONEditorWidget

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

    def has_add_permission(self, request, obj=None):
        return False


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


LESSON_BLOCK_TYPES = {
    'heading',
    'text',
    'code',
    'list',
    'table',
    'callout',
    'blockquote',
    'image',
    'video',
    'divider',
}

CALLOUT_STYLES = {'info', 'success', 'warning', 'danger'}


def _as_text(value, limit=200000):
    """Coerce an arbitrary JSON value to a length-limited string."""
    if value is None:
        return ''
    if not isinstance(value, str):
        value = str(value)
    return value[:limit]


def _as_string_list(value, item_limit=20000):
    """Coerce a JSON value to a list of strings (accepts newline-separated text)."""
    if isinstance(value, str):
        value = value.split('\n')
    if not isinstance(value, (list, tuple)):
        return []
    return [_as_text(item, item_limit) for item in value]


def _as_int(value, default, minimum, maximum):
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(minimum, min(maximum, number))


def _as_float(value, default, minimum, maximum):
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return round(max(minimum, min(maximum, number)), 2)


def _clean_block(block):
    """Validate and normalize one lesson content block.

    Unknown block types are preserved as-is: this keeps content created by
    future block types from being destroyed by an older editor build.
    """
    if not isinstance(block, dict):
        return None

    block_type = block.get('type')
    if block_type not in LESSON_BLOCK_TYPES:
        return block

    clean = {'type': block_type}

    if block_type == 'heading':
        clean['level'] = _as_int(block.get('level'), 2, 1, 6)
        clean['content'] = _as_text(block.get('content'), 1000)

    elif block_type == 'text':
        clean['content'] = _as_text(block.get('content'))

    elif block_type == 'code':
        language = _as_text(block.get('language'), 32).strip().lower()
        clean['language'] = language or 'text'
        clean['content'] = _as_text(block.get('content'))

    elif block_type == 'list':
        clean['ordered'] = bool(block.get('ordered'))
        clean['items'] = _as_string_list(block.get('items'))

    elif block_type == 'table':
        rows = []
        if isinstance(block.get('rows'), list):
            for row in block.get('rows'):
                if isinstance(row, (list, tuple)):
                    rows.append([_as_text(cell, 5000) for cell in row])
        clean['headers'] = _as_string_list(block.get('headers'), 5000)
        clean['rows'] = rows
        if 'content' in block:
            clean['content'] = _as_text(block.get('content'), 1000)

    elif block_type == 'callout':
        style = block.get('style') or 'info'
        clean['style'] = style if style in CALLOUT_STYLES else 'info'
        clean['title'] = _as_text(block.get('title'), 300)
        clean['content'] = _as_text(block.get('content'))

    elif block_type == 'blockquote':
        clean['content'] = _as_text(block.get('content'))

    elif block_type == 'image':
        clean['url'] = _as_text(block.get('url'), 2000).strip()
        clean['alt'] = _as_text(block.get('alt'), 500)
        clean['caption'] = _as_text(block.get('caption'), 500)

    elif block_type == 'video':
        clean['url'] = _as_text(block.get('url'), 2000).strip()

    return clean


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin for Lesson."""

    change_form_template = 'admin/learning/lesson/change_form.html'

    list_display = ('name', 'topic', 'slug', 'status', 'order', 'estimated_minutes', 'version', 'editor_link', 'created_at')
    list_filter = ('status', 'topic')
    search_fields = ('name', 'slug', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('topic', 'created_by', 'updated_by')
    ordering = ('topic', 'order', 'name')
    readonly_fields = ('created_at', 'updated_at', 'version')
    filter_horizontal = ()
    inlines = [LessonAttachmentInline, LessonVersionInline]

    fieldsets = (
        (None, {'fields': ('topic', 'name', 'slug', 'short_description')}),
        (_('Content'), {'fields': ('content',)}),
        (_('Status & Order'), {'fields': ('status', 'order', 'estimated_minutes')}),
        (_('Authorship'), {'fields': ('created_by', 'updated_by', 'version', 'change_log')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            kwargs['widget'] = JSONEditorWidget(mode='code', options={'mode': 'code'})
        return super().formfield_for_dbfield(db_field, **kwargs)

    # ------------------------------------------------------------------
    # Visual editor
    # ------------------------------------------------------------------

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                '<path:object_id>/editor/',
                self.admin_site.admin_view(self.editor_view),
                name='learning_lesson_editor',
            ),
            path(
                '<path:object_id>/editor/save/',
                self.admin_site.admin_view(self.editor_save_view),
                name='learning_lesson_editor_save',
            ),
        ]
        return custom + urls

    def editor_link(self, obj):
        """List-column shortcut to the visual editor."""
        if not getattr(obj, 'pk', None):
            return ''
        url = reverse('admin:learning_lesson_editor', args=[obj.pk])
        return format_html(
            '<a class="button" style="padding:2px 8px;" href="{}">Редактор</a>',
            url,
        )

    editor_link.short_description = 'Редактор'

    @method_decorator(never_cache)
    def editor_view(self, request, object_id):
        """Full-page block editor for a single lesson."""
        lesson = get_object_or_404(self.get_queryset(request), pk=object_id)
        if not self.has_view_or_change_permission(request, lesson):
            raise PermissionDenied

        blocks = lesson.content if isinstance(lesson.content, list) else []
        payload = {
            'id': lesson.pk,
            'name': lesson.name,
            'slug': lesson.slug,
            'short_description': lesson.short_description,
            'status': lesson.status,
            'difficulty': lesson.difficulty,
            'lesson_type': lesson.lesson_type,
            'xp_reward': lesson.xp_reward,
            'estimated_minutes': lesson.estimated_minutes,
            'content': blocks,
            'display': lesson.get_display_options(),
            'version': lesson.version,
            'choices': {
                'status': [
                    (value, str(label))
                    for value, label in Lesson._meta.get_field('status').choices
                ],
                'difficulty': [
                    (value, str(label)) for value, label in Lesson.Difficulty.choices
                ],
                'lesson_type': [
                    (value, str(label)) for value, label in Lesson.LessonType.choices
                ],
                'font': [
                    ('sans', 'Без засечек — Inter / системный'),
                    ('serif', 'С засечками — Georgia'),
                    ('mono', 'Моноширинный — JetBrains Mono'),
                    ('humanist', 'Гуманистический — Verdana'),
                    ('rounded', 'Округлый — SF Pro Rounded'),
                ],
            },
        }

        context = {
            **self.admin_site.each_context(request),
            'title': f'Редактор урока: {lesson.name}',
            'lesson': lesson,
            'original': lesson,
            'opts': self.model._meta,
            'editor_payload': payload,
            'save_url': reverse('admin:learning_lesson_editor_save', args=[lesson.pk]),
            'lesson_url': reverse('learning:lesson_learn', kwargs={'slug': lesson.slug}),
            'change_url': reverse('admin:learning_lesson_change', args=[lesson.pk]),
            'can_change': self.has_change_permission(request, lesson),
        }
        return TemplateResponse(request, 'admin/learning/lesson/editor.html', context)

    def editor_save_view(self, request, object_id):
        """JSON endpoint that persists the editor state."""
        if request.method != 'POST':
            return JsonResponse({'ok': False, 'error': 'Метод не поддерживается'}, status=405)

        lesson = get_object_or_404(self.get_queryset(request), pk=object_id)
        if not self.has_change_permission(request, lesson):
            return JsonResponse({'ok': False, 'error': 'Нет прав на изменение урока'}, status=403)

        try:
            data = json.loads(request.body.decode('utf-8') or '{}')
        except (ValueError, UnicodeDecodeError):
            return JsonResponse({'ok': False, 'error': 'Некорректный JSON'}, status=400)

        if not isinstance(data, dict):
            return JsonResponse({'ok': False, 'error': 'Некорректные данные'}, status=400)

        raw_blocks = data.get('content')
        if not isinstance(raw_blocks, list):
            return JsonResponse({'ok': False, 'error': 'Содержимое урока должно быть списком блоков'}, status=400)

        blocks = []
        for raw_block in raw_blocks[:2000]:
            clean_block = _clean_block(raw_block)
            if clean_block is not None:
                blocks.append(clean_block)

        meta = data.get('meta') if isinstance(data.get('meta'), dict) else {}

        name = _as_text(meta.get('name'), 200).strip()
        if not name:
            return JsonResponse({'ok': False, 'error': 'Название урока не может быть пустым'}, status=400)

        status_values = {choice[0] for choice in Lesson._meta.get_field('status').choices}
        status = meta.get('status') if meta.get('status') in status_values else lesson.status

        difficulty_values = {choice[0] for choice in Lesson.Difficulty.choices}
        difficulty = meta.get('difficulty') if meta.get('difficulty') in difficulty_values else lesson.difficulty

        lesson_type_values = {choice[0] for choice in Lesson.LessonType.choices}
        lesson_type = meta.get('lesson_type') if meta.get('lesson_type') in lesson_type_values else lesson.lesson_type

        xp_reward = _as_int(meta.get('xp_reward'), lesson.xp_reward, 0, 10000)
        estimated_minutes = _as_int(meta.get('estimated_minutes'), lesson.estimated_minutes, 1, 600)
        short_description = _as_text(meta.get('short_description'), 1000).strip()

        raw_display = data.get('display') if isinstance(data.get('display'), dict) else {}
        display = dict(lesson.get_display_options())
        if raw_display.get('font') in Lesson.FONT_STACKS:
            display['font'] = raw_display['font']
        display['size'] = _as_int(raw_display.get('size'), display.get('size', 17), 12, 28)
        display['line_height'] = _as_float(
            raw_display.get('line_height'), display.get('line_height', 1.7), 1.2, 2.4
        )
        display['width'] = _as_int(raw_display.get('width'), display.get('width', 68), 40, 120)

        content_changed = lesson.content != blocks
        if content_changed:
            # Keep a snapshot of the previous text so it can be restored.
            LessonVersion.objects.update_or_create(
                lesson=lesson,
                version=lesson.version,
                defaults={
                    'content': lesson.content,
                    'change_log': 'Снимок перед сохранением в визуальном редакторе',
                    'created_by': request.user,
                },
            )

        lesson.name = name
        lesson.short_description = short_description
        lesson.status = status
        lesson.difficulty = difficulty
        lesson.lesson_type = lesson_type
        lesson.xp_reward = xp_reward
        lesson.estimated_minutes = estimated_minutes
        lesson.content = blocks
        lesson.display_options = display
        lesson.updated_by = request.user
        if not lesson.created_by_id:
            lesson.created_by = request.user
        lesson.change_log = 'Сохранено в визуальном редакторе ' + timezone.localtime().strftime('%d.%m.%Y %H:%M')
        lesson.save()

        return JsonResponse({
            'ok': True,
            'version': lesson.version,
            'blocks': len(blocks),
            'saved_at': timezone.localtime().strftime('%H:%M:%S'),
        })


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