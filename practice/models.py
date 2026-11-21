"""
Practice models: Tasks, Test Cases, Sessions.
"""

import json
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError

from core.models import TimeStampedModel, OrderedModel, PublishedModel, PublishedManager, ActiveManager, PublishedSoftDeleteTimeStampedModel
from learning.models import ProgrammingLanguage, Topic


class PracticeTask(PublishedSoftDeleteTimeStampedModel, OrderedModel):
    """
    Coding practice tasks.
    """

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='practice_tasks',
        verbose_name=_('topic'),
        db_index=True,
    )

    language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.CASCADE,
        related_name='practice_tasks',
        verbose_name=_('language'),
        db_index=True,
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

    # objects = PublishedManager()  # Now inherited from PublishedSoftDeleteTimeStampedModel
    # all_objects = ActiveManager()  # Now inherited from PublishedSoftDeleteTimeStampedModel

    class Meta:
        verbose_name = _('practice task')
        verbose_name_plural = _('practice tasks')
        ordering = ['topic', 'order', 'difficulty', 'name']
        constraints = [
            models.UniqueConstraint(fields=['topic', 'slug'], name='unique_task_slug_per_topic'),
        ]

    def __str__(self):
        return f"{self.topic.name} - {self.name}"

    @property
    def difficulty_level(self) -> int:
        """Сложность 1-5 (безопасно приводим к диапазону)."""
        try:
            level = int(self.difficulty)
        except (TypeError, ValueError):
            level = 1
        return max(1, min(5, level))

    @property
    def difficulty_stars(self) -> str:
        """Строка из 5 звёзд: заполненные ★ по сложности и пустые ☆."""
        level = self.difficulty_level
        return '★' * level + '☆' * (5 - level)

    @property
    def difficulty_stars_filled(self) -> str:
        return '★' * self.difficulty_level

    @property
    def difficulty_stars_empty(self) -> str:
        return '☆' * (5 - self.difficulty_level)

    @property
    def difficulty_color(self) -> str:
        """Цвет Bootstrap-бейджа для сложности."""
        return {1: 'success', 2: 'info', 3: 'warning', 4: 'danger', 5: 'primary'}.get(
            self.difficulty_level, 'secondary'
        )

    def clean(self):
        """Validate JSON fields."""
        super().clean()
        # Validate test_cases structure
        if self.test_cases:
            if not isinstance(self.test_cases, list):
                raise ValidationError({'test_cases': _('Test cases must be a list.')})
            for i, tc in enumerate(self.test_cases):
                if not isinstance(tc, dict):
                    raise ValidationError({'test_cases': _(f'Test case {i} must be an object.')})
                if 'input' not in tc or 'expected_output' not in tc:
                    raise ValidationError({'test_cases': _(f'Test case {i} must have "input" and "expected_output" fields.')})
        
        # Validate hints structure
        if self.hints:
            if not isinstance(self.hints, list):
                raise ValidationError({'hints': _('Hints must be a list.')})
            for i, hint in enumerate(self.hints):
                if not isinstance(hint, dict):
                    raise ValidationError({'hints': _(f'Hint {i} must be an object.')})
                if 'level' not in hint or 'text' not in hint:
                    raise ValidationError({'hints': _(f'Hint {i} must have "level" and "text" fields.')})

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
        db_index=True,
    )

    task = models.ForeignKey(
        PracticeTask,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name=_('task'),
        db_index=True,
    )

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='practice_sessions',
        verbose_name=_('topic'),
        db_index=True,
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

    @property
    def status_color(self):
        """Цвет Bootstrap для статуса сессии."""
        return {
            'passed': 'success',
            'failed': 'danger',
            'error': 'danger',
            'skipped': 'secondary',
            'running': 'info',
            'pending': 'warning',
        }.get(self.status, 'secondary')

class DailyChallenge(TimeStampedModel):
    """
    Ежедневный вызов: одна задача, выбранная на конкретную дату.
    """

    date = models.DateField(_('date'), unique=True, db_index=True)
    task = models.ForeignKey(
        PracticeTask,
        on_delete=models.CASCADE,
        related_name='daily_challenges',
        verbose_name=_('task'),
    )

    class Meta:
        verbose_name = _('daily challenge')
        verbose_name_plural = _('daily challenges')
        ordering = ['-date']

    def __str__(self):
        return f'{self.date}: {self.task.name}'
