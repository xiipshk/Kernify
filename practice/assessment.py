"""Сервис проверки теста-диагностики (практика/оценка знаний)."""
import random

from django.utils.translation import gettext as _

from practice.models import AssessmentQuestion, AssessmentResult


# Пороги уровней (проценты правильных ответов)
LEVEL_RULES = (
    (80, AssessmentResult.Level.ADVANCED),
    (50, AssessmentResult.Level.INTERMEDIATE),
)


def level_for_score(score):
    """Уровень по проценту правильных ответов."""
    for threshold, level in LEVEL_RULES:
        if score >= threshold:
            return level
    return AssessmentResult.Level.BEGINNER


def get_questions(language, limit=20):
    """Опубликованные вопросы языка, перемешанные, не больше ``limit``."""
    questions = list(
        AssessmentQuestion.objects.filter(
            language=language,
            status=AssessmentQuestion.PublishStatus.PUBLISHED,
        ).select_related('topic')
    )
    random.shuffle(questions)
    return questions[:limit]


def _topic_ref(question):
    """Ключ и название темы вопроса.

    Ключ — id темы, если вопрос привязан к теме (slug уникален только внутри
    программы, поэтому id надёжнее). Иначе используем текстовую метку.
    """
    if question.topic_id and question.topic:
        return str(question.topic_id), question.topic.name
    if question.topic_label:
        return question.topic_label, question.topic_label
    label = _('Общее')
    return label, label


def _parse_index(raw, options_count):
    try:
        index = int(raw)
    except (TypeError, ValueError):
        return None
    return index if 0 <= index < options_count else None


def evaluate(language, questions, answers):
    """
    Проверяет ответы и сохраняет результат.

    ``answers`` — словарь вида {"<question_id>": index}.
    Возвращает (result, details). ``result.user`` заполняет вызывающий код.
    """
    breakdown = {}
    records = []
    details = []
    correct_count = 0

    for question in questions:
        raw = answers.get(str(question.pk))
        options = question.get_options()
        selected_index = _parse_index(raw, len(options))
        correct_index = question.correct_index
        is_correct = selected_index is not None and selected_index == correct_index

        topic_key, topic_name = _topic_ref(question)
        stats = breakdown.setdefault(
            topic_key, {'name': topic_name, 'total': 0, 'correct': 0}
        )
        stats['total'] += 1
        if is_correct:
            stats['correct'] += 1
            correct_count += 1

        records.append({
            'id': question.pk,
            'answer': selected_index,
            'correct_index': correct_index,
            'correct': is_correct,
        })
        details.append({
            'question': question.question,
            'topic': topic_name,
            'is_correct': is_correct,
            'answered': selected_index is not None,
            'selected_text': (
                AssessmentQuestion._option_text(options[selected_index], None)
                if selected_index is not None else ''
            ),
            'correct_text': (
                AssessmentQuestion._option_text(options[correct_index], None)
                if correct_index is not None else ''
            ),
            'explanation': question.explanation,
        })

    total = len(questions)
    score = round(correct_count * 100 / total) if total else 0

    result = AssessmentResult(
        language=language,
        total_questions=total,
        correct_answers=correct_count,
        score=score,
        level=level_for_score(score),
        topic_breakdown=breakdown,
        answers=records,
    )
    return result, details


def latest_result(user, language):
    """Последний результат теста пользователя по языку."""
    if not user or not user.is_authenticated:
        return None
    return (
        AssessmentResult.objects.filter(user=user, language=language)
        .order_by('-created_at', '-id')
        .first()
    )


def topic_marks(user, language):
    """
    Пометки тем по последнему тесту: {id темы (строка): 'known' | 'unknown'}.

    Ключ — id темы (см. ``_topic_ref``). Темы, по которым не было
    вопросов, в словарь не попадают.
    """
    result = latest_result(user, language)
    if result is None:
        return {}

    marks = {}
    for key, stats in (result.topic_breakdown or {}).items():
        total = stats.get('total', 0)
        if not total:
            continue
        marks[key] = 'known' if stats.get('correct', 0) == total else 'unknown'
    return marks
