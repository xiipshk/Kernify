"""
Генерация практических задач для всех тем сайта.

Использование:
    python manage.py generate_practice_tasks
    python manage.py generate_practice_tasks --topic python-1-1
    python manage.py generate_practice_tasks --per-topic 20
    python manage.py generate_practice_tasks --dry-run

Задачи строятся из общего банка классических упражнений (practice/task_bank.py),
подобранных под категорию темы. Для исполняемых языков (Python, C++, JavaScript,
Rust) идут проверяемые тесты и эталонные решения; для CSS — задания по стилям;
для C# — условия задач со стартовым шаблоном (C# пока не исполняется).
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from learning.models import Topic
from practice.models import PracticeTask
from practice.task_bank import EXERCISES, CSS_EXERCISES, CONCEPT_TASKS

RUNNABLE_LANGS = {'python', 'cpp', 'javascript', 'rust'}

# Ключевые слова -> категория упражнений.
KEYWORDS = [
    ('conditionals', ['услов', 'ветвлен', 'развилк', 'управление потоком']),
    ('loops', ['цикл', 'итерац', 'повтор']),
    ('strings', ['строк', 'текст']),
    ('collections', ['коллекц', 'массив', 'список', 'словар', 'множ', 'стек', 'очеред', 'set', 'dict']),
    ('functions', ['функц', 'метод', 'рекурси', 'замыкан', 'модул', 'файл', 'ошибк', 'исключен',
                   'тестирован', 'типизац', 'делегат', 'трейт', 'дженерик']),
    ('algorithms', ['алгоритм', 'сортиров', 'поиск', 'структур данных', 'дерев', 'граф', 'динамич',
                    'stl', 'итератор', 'производительн', 'оптимизац']),
    ('advanced', ['метакласс', 'декоратор', 'генератор', 'асинхрон', 'конкурент', 'многопоточ',
                  'макрос', 'unsafe', 'метапрограмм', 'devops', 'ci/cd', 'архитектур', 'микросервис',
                  'безопасн', 'профилир', 'abi', 'cargo', 'cmake', 'экосистем', 'внутреннее устройство',
                  'linq', 'async', 'own', 'владени']),
]


def classify_topic(topic_name: str) -> str:
    name = topic_name.lower()
    for category, words in KEYWORDS:
        if any(w in name for w in words):
            return category
    return 'basics'


def track_level(topic_slug: str) -> int:
    """Определяет уровень трека из slug вида python-2-3 -> 2."""
    parts = topic_slug.split('-')
    for part in parts:
        if part.isdigit() and 1 <= int(part) <= 3 and len(part) == 1:
            return int(part)
    return 1


def csharp_starter(statement: str) -> str:
    return (
        'using System;\n\n'
        'class Program\n'
        '{\n'
        '    static void Main()\n'
        '    {\n'
        f'        // {statement}\n'
        '    }\n'
        '}\n'
    )


# Заготовки стартового кода (решение — в поле solution, не показывается сразу).
STARTERS = {
    'python': '# Прочитайте входные данные и выведите результат\nimport sys\n\ndata = sys.stdin.read().split()\n# ваш код\n',
    'cpp': '#include <iostream>\n\nint main() {\n    // ваш код\n    return 0;\n}\n',
    'javascript': 'const fs = require("fs");\nconst data = fs.readFileSync(0, "utf8").trim();\n// ваш код\n',
    'rust': 'use std::io::{self, Read};\n\nfn main() {\n    let mut input = String::new();\n    io::stdin().read_to_string(&mut input).unwrap();\n    // ваш код\n}\n',
}

CSS_STARTER = '/* Напишите CSS-правило здесь */\n'


def pick_exercises(category: str, count: int, offset: int):
    """Подбирает count упражнений, начиная со сдвига offset (для разнообразия)."""
    primary = [e for e in EXERCISES if e['category'] == category]
    secondary = [e for e in EXERCISES if e['category'] != category]
    pool = primary + secondary
    if not pool:
        pool = EXERCISES[:]
    # ротация для разных тем
    offset = offset % len(pool)
    rotated = pool[offset:] + pool[:offset]
    return rotated[:count]


class Command(BaseCommand):
    help = 'Создаёт практические задачи для тем (20-30 на тему).'

    def add_arguments(self, parser):
        parser.add_argument('--per-topic', type=int, default=20, help='Задач на тему (по умолчанию 20)')
        parser.add_argument('--topic', type=str, default='', help='Сгенерировать только для одного slug темы')
        parser.add_argument('--dry-run', action='store_true', help='Только показать, что будет создано')

    def handle(self, *args, **options):
        per_topic = max(1, min(options['per_topic'], 30))
        only_slug = options['topic'].strip()
        dry_run = options['dry_run']

        topics = Topic.objects.filter(status='published').select_related('program__language').order_by('program__language__slug', 'order')
        if only_slug:
            topics = topics.filter(slug=only_slug)

        total_created = 0
        total_updated = 0
        topics_done = 0

        for topic in topics:
            lang = topic.program.language.slug
            n = per_topic

            if lang == 'css':
                created, updated = self._generate_css(topic, n, dry_run)
            elif lang == 'csharp':
                created, updated = self._generate_coding(topic, n, dry_run, csharp=True)
            else:
                created, updated = self._generate_coding(topic, n, dry_run, csharp=False)

            total_created += created
            total_updated += updated
            topics_done += 1

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY-RUN: изменения не сохранены.'))
        self.stdout.write(self.style.SUCCESS(
            f'Готово. Тем: {topics_done}, создано: {total_created}, обновлено: {total_updated}.'
        ))

    # ------------------------------------------------------------------
    def _save(self, topic, index, slug, defaults, dry_run):
        defaults = dict(defaults)
        defaults['order'] = index
        defaults['status'] = PracticeTask.PublishStatus.PUBLISHED
        defaults['published_at'] = timezone.now()
        if dry_run:
            return 0, 0
        _, created = PracticeTask.objects.update_or_create(
            topic=topic, slug=slug, defaults=defaults,
        )
        return (1, 0) if created else (0, 1)

    def _generate_coding(self, topic, count, dry_run, csharp=False):
        lang = topic.program.language.slug
        category = classify_topic(topic.name)
        level = track_level(topic.slug)
        offset = topic.order * 5

        created = updated = 0

        # Продвинутые/теоретические темы: половина — разбор кода (EXPLAIN),
        # половина — обычные кодинг-задачи, чтобы была и практика запуска.
        concept_count = count // 2 if category == 'advanced' and not csharp else 0
        if concept_count:
            concepts = CONCEPT_TASKS['advanced']
            for i in range(concept_count):
                title, statement = concepts[i % len(concepts)]
                slug = f'{topic.slug}-{slugify(title)[:40]}-{i + 1}'
                difficulty = min(5, 2 + level)
                c, u = self._save(topic, i + 1, slug, {
                    'language': topic.program.language,
                    'name': title,
                    'description': f'Тема «{topic.name}». {statement}',
                    'task_type': PracticeTask.TaskType.EXPLAIN,
                    'difficulty': difficulty,
                    'starter_code': '',
                    'solution': '',
                    'test_cases': [],
                    'hints': [f'Разберите пример по теме «{topic.name}».'],
                    'xp_reward': 10 + difficulty * 5,
                    'time_limit': 5,
                    'memory_limit': 128,
                }, dry_run)
                created += c; updated += u

        code_count = count - concept_count
        exercises = pick_exercises(category, code_count, offset)
        for j, ex in enumerate(exercises):
            i = concept_count + j
            difficulty = min(5, ex['difficulty'] + max(0, level - 1))
            if csharp:
                starter = csharp_starter(ex['statement'])
                solution = starter
            else:
                starter = STARTERS.get(lang, '')
                solution = ex['solutions'].get(lang, '')
            tests = [
                {'input': inp, 'expected_output': out, 'description': 'Пример'}
                for inp, out in ex['tests']
            ]

            slug = f'{topic.slug}-{ex["id"]}-{i + 1}'
            c, u = self._save(topic, i + 1, slug, {
                'language': topic.program.language,
                'name': ex['title'],
                'description': f'Тема «{topic.name}». {ex["statement"]}',
                'task_type': PracticeTask.TaskType.WRITE_CODE,
                'difficulty': difficulty,
                'starter_code': starter,
                'solution': solution,
                'test_cases': tests,
                'hints': [f'Задача по теме «{topic.name}».', 'Прочитайте входные данные и выведите результат.'],
                'xp_reward': 10 + difficulty * 5,
                'time_limit': 5,
                'memory_limit': 128,
            }, dry_run)
            created += c; updated += u
        return created, updated

    def _generate_css(self, topic, count, dry_run):
        created = updated = 0
        level = track_level(topic.slug)
        offset = (topic.order * 2) % len(CSS_EXERCISES)
        rotated = CSS_EXERCISES[offset:] + CSS_EXERCISES[:offset]

        for i in range(count):
            ex_id, title, statement, solution = rotated[i % len(rotated)]
            difficulty = min(5, 1 + (i % 3) + max(0, level - 1))
            slug = f'{topic.slug}-{ex_id}-{i + 1}'
            c, u = self._save(topic, i + 1, slug, {
                'language': topic.program.language,
                'name': title,
                'description': f'Тема «{topic.name}». {statement}',
                'task_type': PracticeTask.TaskType.WRITE_CODE,
                'difficulty': difficulty,
                'starter_code': CSS_STARTER,
                'solution': solution,
                'test_cases': [],
                'hints': [f'Задание по теме «{topic.name}».'],
                'xp_reward': 10 + difficulty * 5,
                'time_limit': 5,
                'memory_limit': 128,
            }, dry_run)
            created += c; updated += u
        return created, updated
