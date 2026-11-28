"""Фильтры для Bootstrap-бейджей: безопасный цвет по значению (не по переводу)."""
from django import template

register = template.Library()

# Значение поля -> цвет Bootstrap. Ключи — «сырые» значения choices.
COLORS = {
    # сложность темы/урока
    'easy': 'success', 'beginner': 'success',
    'medium': 'warning', 'intermediate': 'info',
    'hard': 'danger', 'advanced': 'warning',
    'expert': 'danger', 'all': 'secondary',
    # тип урока
    'text': 'secondary', 'code': 'info', 'practice': 'primary',
    'quiz': 'warning', 'project': 'danger', 'video': 'dark',
    # тип задачи
    'write_code': 'primary', 'fix_bug': 'danger', 'explain': 'info',
    'improve': 'warning', 'complete': 'success', 'debug': 'secondary',
    # прочее
    'published': 'success', 'draft': 'secondary', 'hidden': 'warning', 'archived': 'dark',
    # статусы сессии/прогресса
    'passed': 'success', 'failed': 'danger', 'pending': 'warning',
    'running': 'info', 'skipped': 'secondary', 'error': 'danger',
}


@register.filter
def badge_color(value):
    """Возвращает цвет Bootstrap ('success', 'info', ...) для значения."""
    key = str(value).lower() if value is not None else ''
    return COLORS.get(key, 'secondary')


# Пометки тем по итогам теста знаний
TOPIC_MARK_COLORS = {'known': 'success', 'unknown': 'danger'}


@register.filter
def topic_mark(marks, key):
    """Пометка темы ('known' / 'unknown') по словарю из вьюхи."""
    if not marks:
        return ''
    return marks.get(key) or marks.get(str(key), '')


@register.filter
def topic_mark_color(mark):
    """Цвет бейджа для пометки темы."""
    return TOPIC_MARK_COLORS.get(mark, 'secondary')
