"""
Сервисы практики: реальная проверка решений по тестам задачи.

Код пользователя прогоняется через раннер (runner/code_runner.py) на каждом
тест-кейсе из ``task.test_cases``; результат сравнивается с эталоном.
"""
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from practice.models import PracticeSession
from runner import code_runner

# Ограничение числа тестов на одну отправку (чтобы не ждать слишком долго).
MAX_TESTS_PER_SUBMIT = 10


def normalize_test_cases(task):
    """Приводит test_cases к единому виду."""
    cases = []
    for tc in (task.test_cases or []):
        if not isinstance(tc, dict):
            continue
        cases.append({
            'input': tc.get('input', '') or '',
            'expected_output': tc.get('expected_output', tc.get('expected', '')) or '',
            'description': tc.get('description', '') or '',
        })
    return cases


def run_task_tests(task, code, language):
    """Прогоняет код по тестам задачи.

    Возвращает словарь с результатами каждого теста, счётом и флагом успеха.
    """
    lang = (language or task.language.slug or '').lower()
    cases = normalize_test_cases(task)

    result = {
        'language': lang,
        'total': len(cases),
        'tests': [],
        'passed': 0,
        'score': 0,
        'all_passed': False,
        'runnable': False,
        'message': '',
    }

    if not cases:
        result['message'] = 'Для этой задачи нет автоматических тестов.'
        return result
    if not (code or '').strip():
        result['message'] = 'Пустое решение.'
        return result
    if not code_runner.supports_language(lang):
        result['message'] = f'Автоматическая проверка для языка «{lang}» недоступна.'
        return result
    if not code_runner.is_enabled():
        result['message'] = 'Запуск кода временно недоступен.'
        return result

    tests = []
    passed = 0
    for index, tc in enumerate(cases[:MAX_TESTS_PER_SUBMIT], start=1):
        run = code_runner.run_code(code, lang, stdin=tc['input'])
        actual = (run.output or '').strip()
        expected = tc['expected_output'].strip()
        ok = bool(run.success) and actual == expected
        if ok:
            passed += 1
        tests.append({
            'test_name': f'Тест {index}',
            'test_case': index,
            'passed': ok,
            'input': tc['input'],
            'expected': expected,
            'actual': actual,
            'error_message': '' if run.success else (run.error or ''),
            'description': tc['description'],
        })

    total = len(tests)
    result.update({
        'tests': tests,
        'passed': passed,
        'total': total,
        'score': int(passed / total * 100) if total else 0,
        'all_passed': total > 0 and passed == total,
        'runnable': True,
    })
    return result


def save_submission(session, task, code, language, result):
    """Сохраняет попытку и начисляет XP при полном успехе (один раз за задачу)."""
    session.submitted_code = code or ''
    session.language = (language or task.language.slug or '')[:50]
    session.test_results = result.get('tests', [])
    session.attempts = (session.attempts or 0) + 1
    session.completed_at = timezone.now()

    previously_passed = PracticeSession.objects.filter(
        user=session.user, task=task, status='passed',
    ).exclude(pk=session.pk).exists()

    if result.get('runnable'):
        session.status = 'passed' if result.get('all_passed') else 'failed'
    else:
        # Нет исполняемых тестов (например, CSS/C#) — оставляем на ручную проверку.
        session.status = 'pending'

    grant_xp = session.status == 'passed' and not previously_passed
    session.xp_earned = task.xp_reward if grant_xp else 0
    session.save()

    if grant_xp:
        _award_xp(session, task)


def _award_xp(session, task):
    """Начисляет XP в прогресс пользователя (атомарно)."""
    from progress.models import UserProgress

    with transaction.atomic():
        progress = UserProgress.objects.select_for_update().filter(
            user=session.user,
            language=task.topic.program.language,
        ).first()
        if progress:
            UserProgress.objects.filter(pk=progress.pk).update(
                total_xp=F('total_xp') + task.xp_reward,
                practice_solved=F('practice_solved') + 1,
                last_activity_at=timezone.now(),
            )


# ---------------------------------------------------------------------------
# Ежедневный вызов
# ---------------------------------------------------------------------------

RECENT_DAYS = 30  # не повторять задачу последние N дней
PREFERRED_LANGUAGES = {'python', 'cpp', 'javascript', 'rust', 'csharp'}


def pick_daily_task(date, language=None):
    """Выбирает случайную проверяемую задачу для ежедневного вызова.

    Предпочитает задачи с тестами на исполняемых языках и не повторяет
    задачи из последних ``RECENT_DAYS`` дней.
    """
    import random

    from practice.models import DailyChallenge, PracticeTask

    qs = PracticeTask.objects.filter(status='published').exclude(test_cases=[])
    if language:
        qs = qs.filter(language__slug=language)

    # Не повторяем недавние задачи.
    used_ids = set(
        DailyChallenge.objects.filter(
            date__gte=date - timezone.timedelta(days=RECENT_DAYS),
            date__lt=date,
        ).values_list('task_id', flat=True)
    )
    candidates = list(qs.exclude(id__in=used_ids).values_list('id', flat=True))
    if not candidates:
        # Если все недавно использованы — берём из всего пула.
        candidates = list(qs.values_list('id', flat=True))
    if not candidates:
        # Совсем нет задач с тестами — берём любую опубликованную.
        candidates = list(
            PracticeTask.objects.filter(status='published').values_list('id', flat=True)
        )
    if not candidates:
        return None

    # Стабильный выбор в рамках дня (даже при гонке запросов).
    rng = random.Random(date.toordinal())
    task_id = rng.choice(sorted(candidates))
    return PracticeTask.objects.filter(id=task_id).first()


def get_daily_challenge(date, language=None):
    """Возвращает задачу ежедневного вызова на дату, создавая при необходимости."""
    from practice.models import DailyChallenge

    obj = DailyChallenge.objects.filter(date=date).select_related('task').first()
    if obj:
        return obj.task

    task = pick_daily_task(date, language=language)
    if not task:
        return None

    obj, _ = DailyChallenge.objects.get_or_create(date=date, defaults={'task': task})
    return obj.task

