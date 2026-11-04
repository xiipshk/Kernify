"""
Practice models: Tasks, Test Cases, Sessions.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from core.models import TimeStampedModel, OrderedModel, PublishedModel, PublishedManager, ActiveManager
from learning.models import ProgrammingLanguage, Topic


class PracticeTask(TimeStampedModel, OrderedModel, PublishedModel):
    """
    Coding practice tasks.
    """

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='practice_tasks',
        verbose_name=_('topic'),
    )

    language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.CASCADE,
        related_name='practice_tasks',
        verbose_name=_('language'),
    )

    name = models.CharField(_('name'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200)
    description = models.TextField(_('description'))

    # Task type
    class TaskType(models.TextChoices):
        WRITE_CODE = 'write_code', _('Write Code')
        FIX_BUG = 'fix_bug', _('Fix Bug')
        EXPLAIN = 'explain', _('Explain Code')
        IMPROVE = 'improve', _('Improve Code')
        COMPLETE = 'complete', _('Complete Code')
        DEBUG = 'debug', _('Debug Code')

    task_type = models.CharField(
        _('task type'),
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.WRITE_CODE,
    )

    # Difficulty (1-5)
    difficulty = models.PositiveIntegerField(_('difficulty'), default=1)

    # Starter code and solution
    starter_code = models.TextField(_('starter code'), blank=True)
    solution = models.TextField(_('solution'), blank=True)

    # Test cases (JSON array)
    # Structure: [{"input": "...", "expected_output": "...", "description": "..."}, ...]
    test_cases = models.JSONField(
        _('test cases'),
        default=list,
        help_text=_('Array of test cases with input, expected output, and description'),
    )

    # Hints (JSON array)
    # Structure: [{"level": 1, "text": "..."}, {"level": 2, "text": "..."}]
    hints = models.JSONField(
        _('hints'),
        default=list,
        blank=True,
        help_text=_('Progressive hints for the task'),
    )

    # XP reward
    xp_reward = models.PositiveIntegerField(_('XP reward'), default=10)

    # Time limit for execution (seconds)
    time_limit = models.PositiveIntegerField(_('time limit (seconds)'), default=5)
    memory_limit = models.PositiveIntegerField(_('memory limit (MB)'), default=128)

    objects = PublishedManager()
    all_objects = ActiveManager()

    class Meta:
        verbose_name = _('practice task')
        verbose_name_plural = _('practice tasks')
        ordering = ['topic', 'order', 'difficulty', 'name']
        constraints = [
            models.UniqueConstraint(fields=['topic', 'slug'], name='unique_task_slug_per_topic'),
        ]

    def __str__(self):
        return f"{self.topic.name} - {self.name}"

    def get_test_cases(self):
        """Return validated test cases."""
        if not isinstance(self.test_cases, list):
            return []
        return self.test_cases

    def get_hints(self):
        """Return validated hints sorted by level."""
        if not isinstance(self.hints, list):
            return []
        return sorted(self.hints, key=lambda h: h.get('level', 0))


class PracticeSession(TimeStampedModel):
    """
    User's attempt at a practice task.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='practice_sessions',
        verbose_name=_('user'),
    )

    task = models.ForeignKey(
        PracticeTask,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name=_('task'),
    )

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='practice_sessions',
        verbose_name=_('topic'),
    )

    # Submitted code
    submitted_code = models.TextField(_('submitted code'), blank=True)
    language = models.CharField(_('language'), max_length=50)

    # Status
    class SessionStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        RUNNING = 'running', _('Running')
        PASSED = 'passed', _('Passed')
        FAILED = 'failed', _('Failed')
        ERROR = 'error', _('Error')
        SKIPPED = 'skipped', _('Skipped')

    status = models.CharField(
        _('status'),
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.PENDING,
    )

    # Test results (JSON)
    # Structure: [{"test_case": 1, "passed": true, "output": "...", "error": null}, ...]
    test_results = models.JSONField(_('test results'), default=list, blank=True)

    # AI feedback
    ai_feedback = models.TextField(_('AI feedback'), blank=True)

    # Progress tracking
    hints_used = models.PositiveIntegerField(_('hints used'), default=0)
    attempts = models.PositiveIntegerField(_('attempts'), default=1)
    time_spent = models.PositiveIntegerField(_('time spent (seconds)'), default=0)
    xp_earned = models.PositiveIntegerField(_('XP earned'), default=0)

    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)

    class Meta:
        verbose_name = _('practice session')
        verbose_name_plural = _('practice sessions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.task.name} ({self.status})"

    @property
    def passed_tests_count(self):
        """Count of passed test cases."""
        if not isinstance(self.test_results, list):
            return 0
        return sum(1 for r in self.test_results if r.get('passed'))

    @property
    def total_tests_count(self):
        """Total number of test cases."""
        if not isinstance(self.test_results, list):
            return 0
        return len(self.test_results)

    @property
    def success_rate(self):
        """Success rate as percentage."""
        total = self.total_tests_count
        if total == 0:
            return 0
        return (self.passed_tests_count / total) * 100