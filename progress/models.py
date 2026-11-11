"""
Progress models: UserProgress, LearningProgress, LessonProgress, ErrorHistory.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from core.models import TimeStampedModel, PublishedModel, PublishedManager, ActiveManager
from learning.models import ProgrammingLanguage, CourseProgram, Topic, Lesson


class UserProgress(TimeStampedModel):
    """
    User's overall progress in a programming language.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='language_progress',
        verbose_name=_('user'),
        db_index=True,
    )

    language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name=_('language'),
        db_index=True,
    )

    # Current program
    current_program = models.ForeignKey(
        CourseProgram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_users',
        verbose_name=_('current program'),
        db_index=True,
    )

    # Current topic/lesson
    current_topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_users',
        verbose_name=_('current topic'),
        db_index=True,
    )
    current_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_users',
        verbose_name=_('current lesson'),
        db_index=True,
    )

    # Overall statistics
    topics_completed = models.PositiveIntegerField(_('topics completed'), default=0)
    lessons_completed = models.PositiveIntegerField(_('lessons completed'), default=0)
    practice_solved = models.PositiveIntegerField(_('practice solved'), default=0)
    total_xp = models.PositiveIntegerField(_('total XP'), default=0)

    # Time tracking
    total_time_spent = models.PositiveIntegerField(_('total time spent (seconds)'), default=0)
    last_activity_at = models.DateTimeField(_('last activity'), null=True, blank=True)

    # Streak
    current_streak = models.PositiveIntegerField(_('current streak (days)'), default=0)
    longest_streak = models.PositiveIntegerField(_('longest streak (days)'), default=0)
    last_streak_date = models.DateField(_('last streak date'), null=True, blank=True)

    class Meta:
        verbose_name = _('user progress')
        verbose_name_plural = _('user progress')
        constraints = [
            models.UniqueConstraint(fields=['user', 'language'], name='unique_user_language_progress'),
        ]
        ordering = ['-last_activity_at']

    def __str__(self):
        return f"{self.user.email} - {self.language.name}"

    @property
    def completion_percentage(self):
        """Overall completion percentage for the language."""
        if not self.current_program:
            return 0
        total_lessons = self.current_program.lessons_count
        if total_lessons == 0:
            return 0
        return min(100, (self.lessons_completed / total_lessons) * 100)


class LessonProgress(TimeStampedModel):
    """
    User's progress on a specific lesson.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        verbose_name=_('user'),
        db_index=True,
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name=_('lesson'),
        db_index=True,
    )

    # Status
    class ProgressStatus(models.TextChoices):
        NOT_STARTED = 'not_started', _('Not Started')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        SKIPPED = 'skipped', _('Skipped')

    status = models.CharField(
        _('status'),
        max_length=20,
        choices=ProgressStatus.choices,
        default=ProgressStatus.NOT_STARTED,
    )

    # Time tracking
    time_spent = models.PositiveIntegerField(_('time spent (seconds)'), default=0)
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)

    # Score (0-100)
    score = models.PositiveIntegerField(_('score'), default=0)

    # Review
    review_count = models.PositiveIntegerField(_('review count'), default=0)
    last_reviewed_at = models.DateTimeField(_('last reviewed'), null=True, blank=True)
    next_review_at = models.DateTimeField(_('next review'), null=True, blank=True)

    # Notes
    personal_notes = models.TextField(_('personal notes'), blank=True)

    class Meta:
        verbose_name = _('lesson progress')
        verbose_name_plural = _('lesson progress')
        constraints = [
            models.UniqueConstraint(fields=['user', 'lesson'], name='unique_user_lesson_progress'),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.email} - {self.lesson.name} ({self.status})"

    def mark_completed(self):
        """Mark lesson as completed."""
        from django.utils import timezone
        self.status = self.ProgressStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def mark_in_progress(self):
        """Mark lesson as in progress."""
        from django.utils import timezone
        if self.status == self.ProgressStatus.NOT_STARTED:
            self.status = self.ProgressStatus.IN_PROGRESS
            self.started_at = timezone.now()
            self.save(update_fields=['status', 'started_at', 'updated_at'])


class TopicProgress(TimeStampedModel):
    """
    User's progress on a topic (aggregated from lessons).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='topic_progress',
        verbose_name=_('user'),
        db_index=True,
    )

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name=_('topic'),
        db_index=True,
    )

    # Status (based on entrance test and lesson completion)
    class TopicStatus(models.TextChoices):
        UNTESTED = 'untested', _('Untested')
        NOT_MASTERED = 'not_mastered', _('Not Mastered')
        PARTIAL = 'partial', _('Partial')
        MASTERED = 'mastered', _('Mastered')

    status = models.CharField(
        _('status'),
        max_length=20,
        choices=TopicStatus.choices,
        default=TopicStatus.UNTESTED,
    )

    # Test score (0-100)
    test_score = models.PositiveIntegerField(_('test score'), default=0)

    # Completion stats
    lessons_total = models.PositiveIntegerField(_('lessons total'), default=0)
    lessons_completed = models.PositiveIntegerField(_('lessons completed'), default=0)

    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)

    class Meta:
        verbose_name = _('topic progress')
        verbose_name_plural = _('topic progress')
        constraints = [
            models.UniqueConstraint(fields=['user', 'topic'], name='unique_user_topic_progress'),
        ]
        ordering = ['topic__order']

    def __str__(self):
        return f"{self.user.email} - {self.topic.name} ({self.status})"

    @property
    def completion_percentage(self):
        """Topic completion percentage."""
        if self.lessons_total == 0:
            return 0
        return min(100, (self.lessons_completed / self.lessons_total) * 100)

    def update_status(self):
        """Update status based on completion and test score."""
        # Check MASTERED first (highest bar)
        if self.test_score >= 70 and self.completion_percentage >= 80:
            self.status = self.TopicStatus.MASTERED
        # Check NOT_MASTERED: took test but scored < 30 AND no lessons completed
        elif self.test_score > 0 and self.test_score < 30 and self.completion_percentage == 0:
            self.status = self.TopicStatus.NOT_MASTERED
        # Check PARTIAL: either passed test with 30-69, or completed some lessons
        elif self.test_score >= 30 or self.completion_percentage > 0:
            self.status = self.TopicStatus.PARTIAL
        # Default: never took test, no completion
        else:
            self.status = self.TopicStatus.UNTESTED
        self.save(update_fields=['status', 'updated_at'])


class ErrorHistory(TimeStampedModel):
    """
    Track user errors for spaced repetition.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='error_history',
        verbose_name=_('user'),
        db_index=True,
    )

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='error_history',
        verbose_name=_('topic'),
        db_index=True,
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='error_history',
        verbose_name=_('lesson'),
        db_index=True,
    )

    practice_task = models.ForeignKey(
        'practice.PracticeTask',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='error_history',
        verbose_name=_('practice task'),
        db_index=True,
    )

    # Error details
    class ErrorType(models.TextChoices):
        SYNTAX = 'syntax', _('Syntax Error')
        LOGIC = 'logic', _('Logic Error')
        CONCEPT = 'concept', _('Conceptual Misunderstanding')
        RUNTIME = 'runtime', _('Runtime Error')
        PERFORMANCE = 'performance', _('Performance Issue')
        STYLE = 'style', _('Code Style')
        OTHER = 'other', _('Other')

    error_type = models.CharField(
        _('error type'),
        max_length=20,
        choices=ErrorType.choices,
        default=ErrorType.OTHER,
    )

    error_description = models.TextField(_('error description'))
    user_code = models.TextField(_('user code'), blank=True)
    correct_code = models.TextField(_('correct code'), blank=True)

    # Spaced repetition
    count = models.PositiveIntegerField(_('occurrence count'), default=1)
    last_seen = models.DateTimeField(_('last seen'), auto_now=True)
    next_review = models.DateTimeField(_('next review'), null=True, blank=True)
    interval_days = models.PositiveIntegerField(_('interval (days)'), default=1)
    ease_factor = models.FloatField(_('ease factor'), default=2.5)

    # Resolution
    is_resolved = models.BooleanField(_('resolved'), default=False)
    resolved_at = models.DateTimeField(_('resolved at'), null=True, blank=True)
    resolution_note = models.TextField(_('resolution note'), blank=True)

    class Meta:
        verbose_name = _('error history')
        verbose_name_plural = _('error history')
        ordering = ['-last_seen']

    def __str__(self):
        return f"{self.user.email} - {self.error_type} in {self.topic.name}"

    def schedule_next_review(self, quality=3):
        """
        Schedule next review using SM-2 algorithm.
        quality: 0-5 (0 = complete blackout, 5 = perfect response)
        
        Standard SM-2 algorithm:
        - repetition (count) starts at 1
        - If quality >= 3:
            - If count == 1: interval = 1
            - If count == 2: interval = 6
            - Else: interval = previous_interval * ease_factor (rounded)
            - ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            - ease_factor = max(1.3, ease_factor)
        - If quality < 3:
            - count = 1 (reset)
            - interval = 1
            - ease_factor = max(1.3, ease_factor - 0.2)
        """
        from django.utils import timezone
        from datetime import timedelta

        if quality >= 3:
            # Successful recall
            if self.count == 1:
                self.interval_days = 1
            elif self.count == 2:
                self.interval_days = 6
            else:
                # Use previous interval * ease_factor, rounded
                self.interval_days = int(round(self.interval_days * self.ease_factor))

            # Update ease factor per SM-2 formula
            # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
            q = quality
            self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
            self.count += 1
        else:
            # Failed recall - reset to first repetition
            self.count = 1
            self.interval_days = 1
            self.ease_factor = max(1.3, self.ease_factor - 0.2)

        self.next_review = timezone.now() + timedelta(days=self.interval_days)
        self.save(update_fields=['count', 'interval_days', 'ease_factor', 'next_review', 'updated_at'])

    def mark_resolved(self, note=''):
        """Mark error as resolved."""
        from django.utils import timezone
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolution_note = note
        self.save(update_fields=['is_resolved', 'resolved_at', 'resolution_note', 'updated_at'])


class TestResult(TimeStampedModel):
    """
    Results of entrance/final tests for topics.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name=_('user'),
    )

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name=_('topic'),
    )

    # Test type
    class TestType(models.TextChoices):
        ENTRANCE = 'entrance', _('Entrance Test')
        FINAL = 'final', _('Final Test')
        PRACTICE = 'practice', _('Practice Test')

    test_type = models.CharField(
        _('test type'),
        max_length=20,
        choices=TestType.choices,
        default=TestType.ENTRANCE,
    )

    # Score
    score = models.PositiveIntegerField(_('score'), default=0)  # 0-100
    max_score = models.PositiveIntegerField(_('max score'), default=100)

    # Details
    questions_total = models.PositiveIntegerField(_('questions total'), default=0)
    questions_correct = models.PositiveIntegerField(_('questions correct'), default=0)
    questions_partial = models.PositiveIntegerField(_('questions partial'), default=0)

    # Answers (JSON)
    # Structure: [{"question_id": 1, "answer": "...", "score": 2, "feedback": "..."}, ...]
    answers = models.JSONField(_('answers'), default=list, blank=True)

    # AI feedback
    ai_feedback = models.TextField(_('AI feedback'), blank=True)

    # Time
    time_spent = models.PositiveIntegerField(_('time spent (seconds)'), default=0)

    class Meta:
        verbose_name = _('test result')
        verbose_name_plural = _('test results')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.topic.name} ({self.test_type}: {self.score}%)"

    @property
    def passed(self):
        return self.score >= 70