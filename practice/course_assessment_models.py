"""
End-of-course tests: mixed theory questions and small practical tasks.

A course test may contain:
- single-choice theory questions;
- multiple-choice theory questions;
- short-answer theory questions;
- code-output tasks (run the snippet in your head and type the output).
"""

import re

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import (
    OrderedTimeStampedModel,
    PublishedSoftDeleteTimeStampedModel,
)
from learning.models import CourseProgram, Topic


def _normalize_text(value, *, collapse_spaces=True):
    text = str(value or '').replace('\r\n', '\n').replace('\r', '\n').strip()
    if collapse_spaces:
        return re.sub(r'\s+', ' ', text).strip().lower()
    return '\n'.join(line.rstrip() for line in text.split('\n')).strip()


class CourseTestQuestion(PublishedSoftDeleteTimeStampedModel, OrderedTimeStampedModel):
    """Question of the end-of-course test."""

    class QuestionType(models.TextChoices):
        SINGLE_CHOICE = 'single_choice', _('Single choice')
        MULTIPLE_CHOICE = 'multiple_choice', _('Multiple choice')
        SHORT_ANSWER = 'short_answer', _('Short answer')
        CODE_OUTPUT = 'code_output', _('Code output task')

    class SkillLevel(models.TextChoices):
        BEGINNER = 'beginner', _('Beginner')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        ADVANCED = 'advanced', _('Advanced')

    program = models.ForeignKey(
        CourseProgram,
        on_delete=models.CASCADE,
        related_name='test_questions',
        verbose_name=_('course program'),
        db_index=True,
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='course_test_questions',
        verbose_name=_('topic'),
    )
    topic_label = models.CharField(
        _('topic label'),
        max_length=120,
        blank=True,
        help_text=_('Used in the report when no topic is linked'),
    )

    question_type = models.CharField(
        _('question type'),
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE_CHOICE,
    )
    question = models.TextField(_('question'))
    question_en = models.TextField(_('question (English)'), blank=True)

    # For CODE_OUTPUT tasks: the snippet whose output the student must predict.
    code_snippet = models.TextField(_('code snippet'), blank=True)
    code_snippet_en = models.TextField(_('code snippet (English)'), blank=True)

    # For choice questions: [{"text": "...", "text_en": "...", "correct": true}, ...]
    options = models.JSONField(
        _('options'),
        default=list,
        blank=True,
        help_text=_(
            'Array of options: {"text": "...", "text_en": "...", "correct": true/false}'
        ),
    )

    # For SHORT_ANSWER / CODE_OUTPUT: accepted answers (case-insensitive for text).
    correct_answers = models.JSONField(
        _('correct answers'),
        default=list,
        blank=True,
        help_text=_('Array of accepted answers for short-answer and code-output tasks'),
    )

    explanation = models.TextField(_('explanation'), blank=True)
    explanation_en = models.TextField(_('explanation (English)'), blank=True)

    difficulty = models.PositiveIntegerField(_('difficulty'), default=1)
    skill_level = models.CharField(
        _('skill level'),
        max_length=20,
        choices=SkillLevel.choices,
        default=SkillLevel.BEGINNER,
    )

    class Meta:
        verbose_name = _('course test question')
        verbose_name_plural = _('course test questions')
        ordering = ['program', 'order', 'difficulty', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['program', 'order'],
                name='unique_course_test_question_order_per_program',
            ),
        ]

    def __str__(self):
        return f'{self.program}: {self.question[:60]}'

    def localized(self, field, lang):
        if (lang or '').startswith('en'):
            value = getattr(self, f'{field}_en', '') or ''
            if value:
                return value
        return getattr(self, field, '') or ''

    def get_options(self):
        if not isinstance(self.options, list):
            return []
        return [opt for opt in self.options if isinstance(opt, dict)]

    @staticmethod
    def _option_text(option, lang):
        if (lang or '').startswith('en') and option.get('text_en'):
            return option['text_en']
        return option.get('text', '')

    @property
    def correct_indices(self):
        return [
            index
            for index, option in enumerate(self.get_options())
            if option.get('correct')
        ]

    @property
    def correct_index(self):
        indices = self.correct_indices
        return indices[0] if len(indices) == 1 else None

    def to_payload(self, lang):
        """Browser-safe payload: correct answers and explanations are excluded."""
        return {
            'id': self.pk,
            'type': self.question_type,
            'question': self.localized('question', lang),
            'topic': self.topic_label or (
                self.topic.name if self.topic_id and self.topic else str(_('General'))
            ),
            'difficulty': self.difficulty,
            'code': self.localized('code_snippet', lang),
            'options': [
                {'text': self._option_text(option, lang)}
                for option in self.get_options()
            ],
        }

    def check_answer(self, raw, lang=None):
        """
        Check one answer.

        Returns ``(is_correct, user_display, correct_display)``.
        """
        if self.question_type in {
            self.QuestionType.SINGLE_CHOICE,
            self.QuestionType.MULTIPLE_CHOICE,
        }:
            return self._check_choice(raw, lang)
        return self._check_text(raw)

    def _check_choice(self, raw, lang):
        options = self.get_options()
        if self.question_type == self.QuestionType.SINGLE_CHOICE:
            selected = _parse_indices(raw, len(options))[:1]
            correct = self.correct_indices[:1]
        else:
            selected = sorted(set(_parse_indices(raw, len(options))))
            correct = sorted(set(self.correct_indices))

        user_text = ', '.join(
            self._option_text(options[index], lang)
            for index in selected
            if 0 <= index < len(options)
        )
        correct_text = ', '.join(
            self._option_text(options[index], lang)
            for index in correct
            if 0 <= index < len(options)
        )
        return bool(correct) and selected == correct, user_text, correct_text

    def _check_text(self, raw):
        answer = '' if raw is None else str(raw)
        accepted = [
            item for item in (self.correct_answers or [])
            if isinstance(item, (str, int, float))
        ]
        accepted = [str(item).strip() for item in accepted if str(item).strip()]
        correct_text = ' / '.join(accepted)

        if self.question_type == self.QuestionType.CODE_OUTPUT:
            normalized = _normalize_text(answer, collapse_spaces=False)
            accepted_normalized = {
                _normalize_text(item, collapse_spaces=False) for item in accepted
            }
        else:
            normalized = _normalize_text(answer)
            accepted_normalized = {_normalize_text(item) for item in accepted}

        is_correct = bool(normalized) and normalized in accepted_normalized
        return is_correct, answer.strip(), correct_text


def _parse_indices(raw, options_count):
    if raw is None:
        return []
    if isinstance(raw, (list, tuple, set)):
        values = raw
    elif isinstance(raw, str):
        values = [part for part in re.split(r'[,;\s]+', raw) if part]
    else:
        values = [raw]

    indices = []
    for value in values:
        try:
            index = int(value)
        except (TypeError, ValueError):
            continue
        if 0 <= index < options_count:
            indices.append(index)
    return indices


class CourseTestResult(models.Model):
    """Saved result of an end-of-course test."""

    class Level(models.TextChoices):
        BEGINNER = 'beginner', _('Beginner')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        ADVANCED = 'advanced', _('Advanced')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_test_results',
        verbose_name=_('user'),
        db_index=True,
    )
    program = models.ForeignKey(
        CourseProgram,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name=_('course program'),
        db_index=True,
    )

    total_questions = models.PositiveIntegerField(_('total questions'), default=0)
    correct_answers = models.PositiveIntegerField(_('correct answers'), default=0)
    score = models.PositiveIntegerField(_('score (%)'), default=0)
    level = models.CharField(
        _('level'),
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER,
    )

    # {"<topic_key>": {"name": "...", "total": 3, "correct": 2}, ...}
    topic_breakdown = models.JSONField(_('topic breakdown'), default=dict)
    answers = models.JSONField(_('answers'), default=list)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _('course test result')
        verbose_name_plural = _('course test results')
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['user', 'program', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user} — {self.program.name}: {self.score}%'

    @property
    def incorrect_answers(self):
        return max(self.total_questions - self.correct_answers, 0)

    @property
    def wrong_topics(self):
        return [
            {'slug': key, **stats}
            for key, stats in (self.topic_breakdown or {}).items()
            if stats.get('correct', 0) < stats.get('total', 0)
        ]

    @property
    def strong_topics(self):
        return [
            {'slug': key, **stats}
            for key, stats in (self.topic_breakdown or {}).items()
            if stats.get('total', 0) and stats.get('correct', 0) == stats.get('total', 0)
        ]
