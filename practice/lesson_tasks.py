"""
Задачи к уроку: подбор только из пройденного материала.

Уроки одного языка выстроены в цепочку (программа → тема → урок).
Задача допускается к уроку, если все навыки, нужные для её решения,
уже встречались в примерах кода этого урока или уроков до него.
"""
import json

from learning.skill_policy import (
    cumulative_skills_for_topic,
    detect_skills,
    lesson_skills,
    task_skills,
)
from practice.models import PracticeTask


def track_of(slug):
    """Уровень трека из slug (python-2-3 -> 2)."""
    parts = (slug or '').split('-')
    for part in parts[1:]:
        if part.isdigit() and len(part) == 1:
            return int(part)
    return 1


def lesson_sort_key(lesson):
    """Учебный порядок: трек (программа) -> тема -> урок."""
    return (
        track_of(lesson.topic.slug),
        lesson.topic.order or 0,
        lesson.order or 0,
        lesson.id or 0,
    )


def ordered_lessons(language):
    """Все опубликованные уроки языка в учебном порядке."""
    from learning.models import Lesson

    lessons = list(
        Lesson.objects
        .filter(topic__program__language=language, status='published')
        .select_related('topic', 'topic__program')
    )
    lessons.sort(key=lesson_sort_key)
    return lessons


def lesson_chain(lesson):
    """Уроки того же языка до текущего включительно (в учебном порядке)."""
    chain = []
    for item in ordered_lessons(lesson.topic.program.language):
        chain.append(item)
        if item.id == lesson.id:
            break
    return chain


def skills_before_lesson(lesson):
    """Навыки из этого урока И всех предыдущих уроков языка."""
    accumulated = set()
    for item in lesson_chain(lesson):
        accumulated |= lesson_skills(item)
    return accumulated


def lesson_tasks_for(lesson, limit=5, language_only=True):
    """Задачи, решаемые только пройденным материалом.

    ``language_only`` — брать задачи лишь того языка, который изучается.
    Теоретические задачи без тестов (разбор кода) практикой не считаются.
    """
    tasks = PracticeTask.objects.filter(status='published').exclude(test_cases=[]).select_related('language', 'topic')
    if language_only:
        tasks = tasks.filter(language=lesson.topic.program.language)
    else:
        tasks = tasks.filter(topic=lesson.topic)

    allowed_skills = skills_before_lesson(lesson)

    result = []
    seen_names = set()
    for task in tasks.order_by('difficulty', 'order', 'name'):
        # одна и та же задача бывает в нескольких темах — показываем один раз
        if task.name in seen_names:
            continue
        needed = task_skills(task)
        if needed <= allowed_skills:
            seen_names.add(task.name)
            result.append(task)
            if limit and len(result) >= limit:
                break
    return result


def lesson_tasks_report(lesson, limit=200):
    """Подробный отчёт: подходящие и отклонённые задачи с причинами."""
    tasks = PracticeTask.objects.filter(
        language=lesson.topic.program.language, status='published',
    ).exclude(test_cases=[]).order_by('difficulty', 'order', 'name')

    allowed_skills = skills_before_lesson(lesson)
    ok, rejected = [], []
    for task in tasks:
        missing = task_skills(task) - allowed_skills
        if missing:
            rejected.append((task, sorted(missing)))
        else:
            ok.append(task)
    return ok[:limit], rejected
