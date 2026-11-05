"""
Learning content models: Languages, Programs, Topics, SubTopics, Lessons.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from core.models import (
    TimeStampedModel,
    OrderedModel,
    PublishedModel,
    SoftDeleteModel,
    OrderedTimeStampedModel,
    PublishedTimeStampedModel,
    PublishedManager,
    ActiveManager,
)


class ProgrammingLanguage(TimeStampedModel, OrderedModel, PublishedModel):
    """
    Programming languages available for learning.
    Managed by administrators.
    """

    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)

    # Icon and branding
    icon = models.CharField(_('icon'), max_length=50, blank=True, help_text=_('Icon class or emoji'))
    color = models.CharField(_('color'), max_length=7, blank=True, help_text=_('Hex color code'))
    logo = models.ImageField(_('logo'), upload_to='languages/', null=True, blank=True)

    # Version tracking
    version = models.CharField(_('version'), max_length=20, default='1.0')

    # Statistics (cached)
    programs_count = models.PositiveIntegerField(_('programs count'), default=0)
    topics_count = models.PositiveIntegerField(_('topics count'), default=0)
    lessons_count = models.PositiveIntegerField(_('lessons count'), default=0)

    objects = PublishedManager()
    all_objects = ActiveManager()

    class Meta:
        verbose_name = _('programming language')
        verbose_name_plural = _('programming languages')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def update_counts(self):
        """Update cached counts."""
        self.programs_count = self.programs.filter(status=self.PublishStatus.PUBLISHED).count()
        self.topics_count = Topic.objects.filter(program__language=self, status=Topic.PublishStatus.PUBLISHED).count()
        self.lessons_count = Lesson.objects.filter(subtopic__topic__program__language=self, status=Lesson.PublishStatus.PUBLISHED).count()
        self.save(update_fields=['programs_count', 'topics_count', 'lessons_count', 'updated_at'])


class CourseProgram(TimeStampedModel, OrderedModel, PublishedModel):
    """
    Learning programs/courses for a programming language.
    Example: "Python Basics", "Advanced Python", "Web Development with Python"
    """

    language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.CASCADE,
        related_name='programs',
        verbose_name=_('language'),
    )

    name = models.CharField(_('name'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200)
    description = models.TextField(_('description'), blank=True)

    # Prerequisites
    prerequisite_programs = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        verbose_name=_('prerequisite programs'),
        help_text=_('Programs that must be completed before this one'),
    )

    # Level and targeting
    class TargetLevel(models.TextChoices):
        BEGINNER = 'beginner', _('Beginner')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        ADVANCED = 'advanced', _('Advanced')
        ALL = 'all', _('All Levels')

    target_level = models.CharField(
        _('target level'),
        max_length=20,
        choices=TargetLevel.choices,
        default=TargetLevel.BEGINNER,
    )

    # Estimated duration
    estimated_hours = models.PositiveIntegerField(_('estimated hours'), default=0)

    # Statistics (cached)
    topics_count = models.PositiveIntegerField(_('topics count'), default=0)
    lessons_count = models.PositiveIntegerField(_('lessons count'), default=0)

    objects = PublishedManager()
    all_objects = ActiveManager()

    class Meta:
        verbose_name = _('course program')
        verbose_name_plural = _('course programs')
        ordering = ['language', 'order', 'name']
        constraints = [
            models.UniqueConstraint(fields=['language', 'slug'], name='unique_program_slug_per_language'),
        ]

    def __str__(self):
        return f"{self.language.name} - {self.name}"

    def update_counts(self):
        """Update cached counts."""
        self.topics_count = self.topics.filter(status=self.PublishStatus.PUBLISHED).count()
        self.lessons_count = Lesson.objects.filter(subtopic__topic__program=self, status=Lesson.PublishStatus.PUBLISHED).count()
        self.save(update_fields=['topics_count', 'lessons_count', 'updated_at'])


class Topic(TimeStampedModel, OrderedModel, PublishedModel):
    """
    Topics within a course program.
    Example: "Variables and Types", "Control Flow", "Functions"
    """

    program = models.ForeignKey(
        CourseProgram,
        on_delete=models.CASCADE,
        related_name='topics',
        verbose_name=_('program'),
    )

    name = models.CharField(_('name'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200)
    description = models.TextField(_('description'), blank=True)

    # Learning objectives
    learning_objectives = models.JSONField(
        _('learning objectives'),
        default=list,
        blank=True,
        help_text=_('List of learning objectives for this topic'),
    )

    # Prerequisites
    prerequisite_topics = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        verbose_name=_('prerequisite topics'),
    )

    # Difficulty
    class Difficulty(models.TextChoices):
        EASY = 'easy', _('Easy')
        MEDIUM = 'medium', _('Medium')
        HARD = 'hard', _('Hard')
        EXPERT = 'expert', _('Expert')

    difficulty = models.PositiveIntegerField(
        _('difficulty'),
        choices=Difficulty.choices,
        default=Difficulty.EASY,
    )

    # Estimated time
    estimated_minutes = models.PositiveIntegerField(_('estimated minutes'), default=30)

    # Base topic flag (critical for dependencies)
    is_base_topic = models.BooleanField(_('base topic'), default=False)

    # Statistics (cached)
    subtopics_count = models.PositiveIntegerField(_('subtopics count'), default=0)
    lessons_count = models.PositiveIntegerField(_('lessons count'), default=0)

    objects = PublishedManager()
    all_objects = ActiveManager()

    class Meta:
        verbose_name = _('topic')
        verbose_name_plural = _('topics')
        ordering = ['program', 'order', 'name']
        constraints = [
            models.UniqueConstraint(fields=['program', 'slug'], name='unique_topic_slug_per_program'),
            models.UniqueConstraint(fields=['program', 'order'], name='unique_topic_order_per_program'),
        ]

    def __str__(self):
        return f"{self.program.name} - {self.name}"

    def update_counts(self):
        """Update cached counts."""
        self.subtopics_count = self.subtopics.filter(status=self.PublishStatus.PUBLISHED).count()
        self.lessons_count = Lesson.objects.filter(subtopic__topic=self, status=Lesson.PublishStatus.PUBLISHED).count()
        self.save(update_fields=['subtopics_count', 'lessons_count', 'updated_at'])


class SubTopic(TimeStampedModel, OrderedModel, PublishedModel):
    """
    Sub-topics within a topic.
    More granular breakdown of content.
    """

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='subtopics',
        verbose_name=_('topic'),
    )

    name = models.CharField(_('name'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200)
    description = models.TextField(_('description'), blank=True)

    # Statistics (cached)
    lessons_count = models.PositiveIntegerField(_('lessons count'), default=0)

    objects = PublishedManager()
    all_objects = ActiveManager()

    class Meta:
        verbose_name = _('subtopic')
        verbose_name_plural = _('subtopics')
        ordering = ['topic', 'order', 'name']
        constraints = [
            models.UniqueConstraint(fields=['topic', 'slug'], name='unique_subtopic_slug_per_topic'),
            models.UniqueConstraint(fields=['topic', 'order'], name='unique_subtopic_order_per_topic'),
        ]

    def __str__(self):
        return f"{self.topic.name} - {self.name}"

    def update_counts(self):
        """Update cached counts."""
        self.lessons_count = self.lessons.filter(status=self.PublishStatus.PUBLISHED).count()
        self.save(update_fields=['lessons_count', 'updated_at'])


class Lesson(TimeStampedModel, OrderedModel, PublishedModel):
    """
    Individual lessons within a subtopic.
    Contains the actual learning content.
    """

    subtopic = models.ForeignKey(
        SubTopic,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_('subtopic'),
    )

    name = models.CharField(_('name'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200)
    short_description = models.TextField(_('short description'), blank=True)

    # Content - stored as JSON for flexibility and security
    # Structure: [{type: 'heading', level: 2, content: '...'}, {type: 'code', language: 'python', content: '...'}, ...]
    content = models.JSONField(
        _('content'),
        default=list,
        blank=True,
        help_text=_('Structured lesson content (blocks: heading, text, code, list, table, image, etc.)'),
    )

    class LessonType(models.TextChoices):
        TEXT = 'text', _('Text')
        CODE = 'code', _('Code')
        PRACTICE = 'practice', _('Practice')
        QUIZ = 'quiz', _('Quiz')
        PROJECT = 'project', _('Project')
        VIDEO = 'video', _('Video')

    class Difficulty(models.TextChoices):
        BEGINNER = 'beginner', _('Beginner')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        ADVANCED = 'advanced', _('Advanced')
        EXPERT = 'expert', _('Expert')

    lesson_type = models.CharField(
        _('lesson type'),
        max_length=20,
        choices=LessonType.choices,
        default=LessonType.TEXT,
    )
    starter_code = models.TextField(_('starter code'), blank=True)
    hints = models.JSONField(_('hints'), default=list, blank=True)
    xp_reward = models.PositiveIntegerField(_('XP reward'), default=10)
    difficulty = models.CharField(
        _('difficulty'),
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
    )
    tags = models.JSONField(_('tags'), default=list, blank=True)

    # Metadata
    estimated_minutes = models.PositiveIntegerField(_('estimated minutes'), default=15)

    # Author tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_lessons',
        verbose_name=_('created by'),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_lessons',
        verbose_name=_('updated by'),
    )

    # Version tracking for change history
    version = models.PositiveIntegerField(_('version'), default=1)
    change_log = models.TextField(_('change log'), blank=True)

    objects = PublishedManager()
    all_objects = ActiveManager()

    class Meta:
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')
        ordering = ['subtopic', 'order', 'name']
        constraints = [
            models.UniqueConstraint(fields=['subtopic', 'slug'], name='unique_lesson_slug_per_subtopic'),
            models.UniqueConstraint(fields=['subtopic', 'order'], name='unique_lesson_order_per_subtopic'),
        ]

    def __str__(self):
        return f"{self.subtopic.name} - {self.name}"

    def save(self, *args, **kwargs):
        # Increment version on update
        if self.pk:
            self.version += 1
        super().save(*args, **kwargs)

    def get_content_blocks(self):
        """Return content blocks with validation."""
        if not isinstance(self.content, list):
            return []
        return self.content


class LessonAttachment(TimeStampedModel, SoftDeleteModel):
    """
    Attachments for lessons (images, files, etc.).
    """

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('lesson'),
    )

    file = models.FileField(_('file'), upload_to='lesson_attachments/')
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    # File metadata
    file_size = models.PositiveIntegerField(_('file size (bytes)'), default=0)
    mime_type = models.CharField(_('MIME type'), max_length=100, blank=True)

    # Type classification
    class AttachmentType(models.TextChoices):
        IMAGE = 'image', _('Image')
        DOCUMENT = 'document', _('Document')
        CODE = 'code', _('Code File')
        ARCHIVE = 'archive', _('Archive')
        OTHER = 'other', _('Other')

    attachment_type = models.CharField(
        _('type'),
        max_length=20,
        choices=AttachmentType.choices,
        default=AttachmentType.OTHER,
    )

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = _('lesson attachment')
        verbose_name_plural = _('lesson attachments')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.lesson.name} - {self.name}"


class LessonVersion(TimeStampedModel):
    """
    Version history for lessons.
    Allows restoring previous versions.
    """

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name=_('lesson'),
    )

    version = models.PositiveIntegerField(_('version'))
    content = models.JSONField(_('content'))
    change_log = models.TextField(_('change log'), blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='lesson_versions',
        verbose_name=_('created by'),
    )

    class Meta:
        verbose_name = _('lesson version')
        verbose_name_plural = _('lesson versions')
        ordering = ['-version']
        constraints = [
            models.UniqueConstraint(fields=['lesson', 'version'], name='unique_lesson_version'),
        ]

    def __str__(self):
        return f"{self.lesson.name} v{self.version}"


# Signal handlers for updating cached counts
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver([post_save, post_delete], sender=CourseProgram)
def update_language_counts(sender, instance, **kwargs):
    if instance.language_id:
        instance.language.update_counts()


@receiver([post_save, post_delete], sender=Topic)
def update_program_counts(sender, instance, **kwargs):
    if instance.program_id:
        instance.program.update_counts()


@receiver([post_save, post_delete], sender=SubTopic)
def update_topic_counts(sender, instance, **kwargs):
    if instance.topic_id:
        instance.topic.update_counts()


@receiver([post_save, post_delete], sender=Lesson)
def update_subtopic_counts(sender, instance, **kwargs):
    if instance.subtopic_id:
        instance.subtopic.update_counts()