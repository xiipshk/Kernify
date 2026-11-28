"""Service layer for end-of-course tests."""

from django.utils.translation import gettext as _

from practice.assessment import level_for_score
from practice.course_assessment_models import CourseTestQuestion, CourseTestResult


def get_questions(program, limit=20):
    """Published questions of a course in a stable order."""
    return list(
        CourseTestQuestion.objects.filter(program=program)
        .select_related('topic')
        .order_by('order', 'difficulty', 'id')[:limit]
    )


def has_questions(program):
    return CourseTestQuestion.objects.filter(program=program).exists()


def questions_count(program):
    return CourseTestQuestion.objects.filter(program=program).count()


def _topic_ref(question):
    if question.topic_id and question.topic:
        return str(question.topic_id), question.topic.name
    if question.topic_label:
        return question.topic_label, question.topic_label
    label = _('Общее')
    return label, label


def evaluate(program, questions, answers, lang=None):
    """Check answers and build an unsaved :class:`CourseTestResult`."""
    breakdown = {}
    records = []
    details = []
    correct_count = 0

    for question in questions:
        raw = answers.get(str(question.pk))
        is_correct, user_display, correct_display = question.check_answer(raw, lang)

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
            'answer': raw,
            'correct': is_correct,
        })
        if isinstance(raw, (list, tuple, set)):
            answered = bool(raw)
        else:
            answered = bool(str(raw or '').strip())
        details.append({
            'question': question.localized('question', lang),
            'type': question.question_type,
            'topic': topic_name,
            'is_correct': is_correct,
            'answered': answered,
            'selected_text': user_display,
            'correct_text': correct_display,
            'explanation': question.localized('explanation', lang),
        })

    total = len(questions)
    score = round(correct_count * 100 / total) if total else 0

    result = CourseTestResult(
        program=program,
        total_questions=total,
        correct_answers=correct_count,
        score=score,
        level=level_for_score(score),
        topic_breakdown=breakdown,
        answers=records,
    )
    return result, details


def latest_result(user, program):
    if not user or not user.is_authenticated:
        return None
    return (
        CourseTestResult.objects.filter(user=user, program=program)
        .order_by('-created_at', '-id')
        .first()
    )


def topic_marks(user, program):
    """Map topic ids to 'known' / 'unknown' based on the latest course test."""
    result = latest_result(user, program)
    if result is None:
        return {}

    marks = {}
    for key, stats in (result.topic_breakdown or {}).items():
        total = stats.get('total', 0)
        if not total:
            continue
        marks[key] = 'known' if stats.get('correct', 0) == total else 'unknown'
    return marks
