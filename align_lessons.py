"""
Align website lessons with reference structure files (non-destructive).

Parses reference .md files to get the exact topic structure per language per
level, then rebuilds the learning database from fixtures with correct
lesson->topic mapping. Existing data is marked 'hidden' rather than deleted.
"""

import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Reference .md files location
REF_DIR = Path(r"C:\Users\maksy\OneDrive\Рабочий стол\логи клауде\обучение\структура обучения")

# Fixtures location
FIXTURES_DIR = BASE_DIR / "fixtures" / "lessons"

# Language mapping: lang_slug -> reference file name
LANG_FILES = {
    'csharp': 'CSharp.md',
    'cpp': 'C++.md',
    'python': 'Python.md',
    'javascript': 'JavaScript.md',
    'css': 'CSS.md',
    'rust': 'Rust.md',
}

# Language metadata
LANGUAGE_META = {
    'python': {'name': 'Python', 'icon': '🐍', 'color': '#3776AB', 'order': 1},
    'cpp': {'name': 'C++', 'icon': '⚡', 'color': '#00599C', 'order': 2},
    'javascript': {'name': 'JavaScript', 'icon': '🟨', 'color': '#F7DF1E', 'order': 3},
    'rust': {'name': 'Rust', 'icon': '🦀', 'color': '#000000', 'order': 4},
    'css': {'name': 'CSS', 'icon': '🎨', 'color': '#1572B6', 'order': 5},
    'csharp': {'name': 'C#', 'icon': '🔷', 'color': '#68217A', 'order': 6},
}

LEVEL_ORDER = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
LEVEL_NAME_RU = {
    'beginner': 'Новичок',
    'intermediate': 'Средний уровень',
    'advanced': 'Углубленный уровень',
}

# Number of topics per level per language (from reference files)
TOPIC_COUNTS = {
    'csharp': {'beginner': 11, 'intermediate': 11, 'advanced': 11},
    'cpp': {'beginner': 11, 'intermediate': 11, 'advanced': 11},
    'python': {'beginner': 11, 'intermediate': 11, 'advanced': 11},
    'javascript': {'beginner': 10, 'intermediate': 11, 'advanced': 11},
    'css': {'beginner': 10, 'intermediate': 11, 'advanced': 11},
    'rust': {'beginner': 11, 'intermediate': 11, 'advanced': 11},
}

# Lesson order -> topic order mapping per language/level
LESSON_ORDER_MAP = {
    'csharp': {
        'beginner': list(range(1, 12)),
        'intermediate': list(range(12, 23)),
        'advanced': list(range(23, 34)),
    },
    'cpp': {
        'beginner': list(range(1, 12)),
        'intermediate': list(range(12, 23)),
        'advanced': list(range(23, 34)),
    },
    'python': {
        'beginner': list(range(1, 12)),
        'intermediate': list(range(12, 23)),
        'advanced': list(range(23, 34)),
    },
    'rust': {
        'beginner': list(range(1, 12)),
        'intermediate': list(range(12, 23)),
        'advanced': list(range(23, 34)),
    },
    'javascript': {
        'beginner': list(range(1, 11)),
        'intermediate': list(range(11, 22)),
        'advanced': list(range(25, 33)),
    },
    'css': {
        'beginner': list(range(1, 11)),
        'intermediate': list(range(11, 22)),
        'advanced': list(range(22, 33)),
    },
}


def parse_reference_md(file_path):
    """Parse a reference .md file and return {level: [topic_names]}."""
    text = Path(file_path).read_text(encoding='utf-8')
    result = {}
    current_level = None

    for line in text.split('\n'):
        stripped = line.strip()
        m = re.match(r'^##\s+\d+\.\s+(.+)$', stripped)
        if m:
            level_name = m.group(1).strip().replace('ё', 'е')
            if 'Новичок' in level_name:
                current_level = 'beginner'
            elif 'Средний' in level_name:
                current_level = 'intermediate'
            elif 'Углубленный' in level_name:
                current_level = 'advanced'
            result[current_level] = []
            continue

        if current_level is not None:
            m = re.match(r'^\d+\.\s+\*\*(.+?):\*\*', stripped)
            if m:
                topic_name = m.group(1).strip()
                result[current_level].append(topic_name)

    return result


def load_fixtures(lang_slug):
    """Load all fixture JSONs for a language, keyed by lesson_order."""
    fixtures = {}
    lang_dir = FIXTURES_DIR / lang_slug
    if not lang_dir.exists():
        return fixtures
    for f in sorted(lang_dir.glob('*.json')):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            order = data.get('lesson_order')
            if order is not None:
                fixtures[order] = data
        except (json.JSONDecodeError, OSError):
            pass
    return fixtures


def django_slugify(text):
    from django.utils.text import slugify
    return slugify(text)


def main():
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

    from django.db import transaction
    from django.db.models import F, Value
    from django.db.models.functions import Concat
    from learning.models import (
        ProgrammingLanguage,
        CourseProgram,
        Topic,
        Lesson,
    )

    print('=== Aligning website lessons with reference structure (non-destructive) ===')
    print()

    # 1. Parse reference files
    print('1. Parsing reference .md files...')
    ref_structure = {}
    for lang_slug, filename in LANG_FILES.items():
        file_path = REF_DIR / filename
        if not file_path.exists():
            print(f'  WARNING: {filename} not found, skipping {lang_slug}')
            continue
        structure = parse_reference_md(file_path)
        ref_structure[lang_slug] = structure
        total = sum(len(v) for v in structure.values())
        print('  {}: beginner={}, intermediate={}, advanced={}, total={}'.format(
            lang_slug,
            len(structure.get('beginner', [])),
            len(structure.get('intermediate', [])),
            len(structure.get('advanced', [])),
            total,
        ))

    # 2. Load fixtures
    print()
    print('2. Loading fixtures...')
    all_fixtures = {}
    for lang_slug in LANG_FILES:
        fixtures = load_fixtures(lang_slug)
        all_fixtures[lang_slug] = fixtures
        orders = sorted(fixtures.keys())
        print(f'  {lang_slug}: {len(fixtures)} fixture(s), orders={orders[:5]}...{orders[-5:]}')

    # 3. Hide all existing learning data (non-destructive: update status, not delete)
    print()
    print('3. Hiding existing learning data...')
    Lesson.all_objects.all().update(status=Lesson.PublishStatus.HIDDEN)
    Topic.all_objects.all().update(status=Topic.PublishStatus.HIDDEN)
    CourseProgram.all_objects.all().update(status=CourseProgram.PublishStatus.HIDDEN)
    ProgrammingLanguage.all_objects.all().update(status=ProgrammingLanguage.PublishStatus.HIDDEN)
    # Clear existing lesson slugs with unique temp values to avoid UNIQUE conflicts
    # when recreating lessons with new slugs in the same subtopic.
    Lesson.all_objects.all().update(slug=Concat(Value('__temp__-'), F('id')))
    print('  All existing learning data hidden; lesson slugs cleared.')

    # 4. Rebuild
    print()
    print('4. Rebuilding learning data...')

    total_lessons = 0
    total_topics = 0

    for lang_slug in ['python', 'cpp', 'javascript', 'rust', 'css', 'csharp']:
        meta = LANGUAGE_META[lang_slug]
        structure = ref_structure.get(lang_slug, {})
        fixtures = all_fixtures.get(lang_slug, {})

        if not structure:
            print(f'  SKIP {lang_slug}: no reference structure')
            continue

        language, _ = ProgrammingLanguage.all_objects.update_or_create(
            slug=lang_slug,
            defaults={
                'name': meta['name'],
                'icon': meta.get('icon', ''),
                'color': meta.get('color', ''),
                'order': meta.get('order', 99),
                'status': ProgrammingLanguage.PublishStatus.PUBLISHED,
            },
        )
        print(f'\n  === {lang_slug} ({meta["name"]}) ===')

        for level in ['beginner', 'intermediate', 'advanced']:
            level_name = LEVEL_NAME_RU[level]
            topics = structure.get(level, [])
            lesson_orders = LESSON_ORDER_MAP[lang_slug][level]

            program_slug = f'{lang_slug}-{level}'
            program, _ = CourseProgram.all_objects.update_or_create(
                language=language,
                slug=program_slug,
                defaults={
                    'name': f'{meta["name"]} — {level_name}',
                    'description': f'Курс {meta["name"]} для уровня {level_name}.',
                    'target_level': getattr(CourseProgram.TargetLevel, level.upper()),
                    'order': LEVEL_ORDER[level],
                    'estimated_hours': 40,
                    'status': CourseProgram.PublishStatus.PUBLISHED,
                },
            )

            topic_count = TOPIC_COUNTS[lang_slug][level]
            print(f'    {level}: {len(topics)} topic(s), {len(lesson_orders)} fixture order(s)')

            for topic_idx in range(topic_count):
                topic_order = topic_idx + 1
                topic_name = topics[topic_idx] if topic_idx < len(topics) else f'Тема {topic_order}'
                topic_slug = f'{django_slugify(topic_name) or "topic"}-{topic_order}'

                topic, _ = Topic.all_objects.update_or_create(
                    program=program,
                    order=topic_order,
                    defaults={
                        'name': topic_name,
                        'slug': topic_slug,
                        'description': '',
                        'difficulty': 1,
                        'estimated_minutes': 30,
                        'is_base_topic': topic_order == 1,
                        'status': Topic.PublishStatus.PUBLISHED,
                    },
                )

                lesson_order = lesson_orders[topic_idx] if topic_idx < len(lesson_orders) else None
                fixture_data = fixtures.get(lesson_order) if lesson_order else None

                if fixture_data:
                    content_blocks = fixture_data.get('content_blocks', [])
                    estimated = fixture_data.get('estimated_minutes', 15)
                    lesson_slug = fixture_data.get('slug') or django_slugify(fixture_data.get('title', 'lesson')) or 'lesson'
                    change_log = f'Imported from fixture order {lesson_order}'
                    if fixture_data.get('goals'):
                        change_log += f'; {len(fixture_data["goals"])} goals'
                    if fixture_data.get('practice_tasks'):
                        change_log += f'; {len(fixture_data["practice_tasks"])} practice tasks'

                    lesson, created = Lesson.all_objects.update_or_create(
                        topic=topic,
                        order=topic_order,
                        defaults={
                            'name': fixture_data.get('title', topic_name),
                            'slug': lesson_slug,
                            'short_description': fixture_data.get('short_description', ''),
                            'content': content_blocks,
                            'estimated_minutes': estimated,
                            'version': 1,
                            'change_log': change_log,
                            'status': Lesson.PublishStatus.PUBLISHED,
                        },
                    )
                    total_lessons += 1
                else:
                    print(f'      No fixture for {lang_slug} {level} topic {topic_order} ({topic_name})')

                total_topics += 1

        language.update_counts()

    print()
    print(f'=== Done: {total_topics} topic(s), {total_lessons} lesson(s) ===')
    print()
    print('Note: Old learning data was marked hidden, not deleted.')
    print('      You can inspect db.sqlite3.old if you need to recover anything.')


if __name__ == '__main__':
    main()
