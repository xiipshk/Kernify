"""
Diagnostic assessment (knowledge test): questions and user results.

Модели для теста-диагностики по языку программирования: вопросы с вариантами
ответов и результаты прохождения. Тест нужен, чтобы понять, что ученик уже
знает, и показать пробелы по темам.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import (
    OrderedTimeStampedModel,
    PublishedSoftDeleteTimeStampedModel,
)
from learning.models import ProgrammingLanguage, Topic


class AssessmentQuestion(PublishedSoftDeleteTimeStampedModel, OrderedTimeStampedModel):
    """
    Вопрос теста-диагностики по языку.

    Легко расширяется: можно добавить вопросы к новой теме, поменять тему
    вопроса админке — отчёт пересчитает пробелы автоматически.
    """

    class SkillLevel(models.TextChoices):
        BEGINNER = 'beginner', _('Beginner')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        ADVANCED = 'advanced', _('Advanced')

    language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.CASCADE,
        related_name='assessment_questions',
        verbose_name=_('language'),
        db_index=True,
    )

    # Тема, к которой относится вопрос (для анализа пробелов)
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assessment_questions',
        verbose_name=_('topic'),
    )

    # Человекочитаемый тег темы — используется, если topic не задан
    topic_label = models.CharField(
        _('topic label'),
        max_length=120,
        blank=True,
        help_text=_('Короткое название темы для отчёта, если тема не привязана'),
    )

    question = models.TextField(_('question'))
    question_en = models.TextField(_('question (English)'), blank=True)

    # Варианты ответов: [{"text": "...", "text_en": "...", "correct": true}, ...]
    options = models.JSONField(
        _('options'),
        default=list,
        help_text=_('Array of options: {"text": "...", "text_en": "...", "correct": true/false}'),
    )

    explanation = models.TextField(
        _('explanation'),
        blank=True,
        help_text=_('Пояснение к правильному ответу'),
    )
    explanation_en = models.TextField(_('explanation (English)'), blank=True)

    difficulty = models.PositiveIntegerField(_('difficulty'), default=1)
    skill_level = models.CharField(
        _('skill level'),
        max_length=20,
        choices=SkillLevel.choices,
        default=SkillLevel.BEGINNER,
    )

    class Meta:
        verbose_name = _('assessment question')
        verbose_name_plural = _('assessment questions')
        # Уникальный порядок вопросов внутри языка
        ordering = ['language', 'order', 'difficulty', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['language', 'order'], name='unique_assessment_question_order_per_language'
            ),
        ]

    def __str__(self):
        return f"{self.language.name}: {self.question[:60]}"

    @property
    def correct_index(self):
        """Индекс правильного варианта или None, если данные повреждены."""
        for i, option in enumerate(self.get_options()):
            if option.get('correct'):
                return i
        return None

    def get_options(self):
        if not isinstance(self.options, list):
            return []
        return [opt for opt in self.options if isinstance(opt, dict)]

    def localized(self, field, lang):
        """Значение поля с учётом языка: `field_en` для английского."""
        if (lang or '').startswith('en'):
            value = getattr(self, f'{field}_en', '') or ''
            if value:
                return value
        return getattr(self, field, '')

    def to_payload(self, lang):
        """
        Безопасное представление вопроса для браузера.

        Правильный ответ и пояснение НЕ включаются — их проверяет сервер.
        """
        return {
            'id': self.pk,
            'question': self.localized('question', lang),
            'topic': self.topic_label,
            'difficulty': self.difficulty,
            'options': [
                {'text': self._option_text(opt, lang)}
                for opt in self.get_options()
            ],
        }

    @staticmethod
    def _option_text(option, lang):
        if (lang or '').startswith('en') and option.get('text_en'):
            return option['text_en']
        return option.get('text', '')

    def check_answer(self, answer_index):
        """Проверяет индекс ответа, возвращает (is_correct, correct_index)."""
        correct = self.correct_index
        try:
            answer_index = int(answer_index)
        except (TypeError, ValueError):
            answer_index = -1
        return answer_index == correct, correct


class AssessmentResult(models.Model):
    """Результат прохождения теста пользователем."""

    class Level(models.TextChoices):
        BEGINNER = 'beginner', _('Beginner')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        ADVANCED = 'advanced', _('Advanced')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessment_results',
        verbose_name=_('user'),
        db_index=True,
    )
    language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.CASCADE,
        related_name='assessment_results',
        verbose_name=_('language'),
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

    # По темам: {"Тема": {"total": 3, "correct": 2}, ...}
    topic_breakdown = models.JSONField(_('topic breakdown'), default=dict)

    # Ответы: [{"id": 1, "answer": 2, "correct": true, "correct_index": 2}, ...]
    answers = models.JSONField(_('answers'), default=list)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _('assessment result')
        verbose_name_plural = _('assessment results')
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['user', 'language', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user} — {self.language.name}: {self.score}%"

    @property
    def incorrect_answers(self):
        return max(self.total_questions - self.correct_answers, 0)

    @property
    def wrong_topics(self):
        """Темы, где есть ошибки."""
        return [
            {'slug': slug, **stats}
            for slug, stats in (self.topic_breakdown or {}).items()
            if stats.get('correct', 0) < stats.get('total', 0)
        ]

    @property
    def strong_topics(self):
        """Темы без ошибок."""
        return [
            {'slug': slug, **stats}
            for slug, stats in (self.topic_breakdown or {}).items()
            if stats.get('total', 0) and stats.get('correct', 0) == stats.get('total', 0)
        ]
