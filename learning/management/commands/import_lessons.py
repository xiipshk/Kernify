"""
Import lessons from parsed JSON fixtures into Django models.

Usage:
    python manage.py import_lessons --fixtures-dir fixtures
    python manage.py import_lessons --fixtures-dir fixtures --language python
    python manage.py import_lessons --fixtures-dir fixtures --dry-run
    python manage.py import_lessons --fixtures-dir fixtures --clear
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify as django_slugify

from learning.models import (
    ProgrammingLanguage,
    CourseProgram,
    Topic,
    SubTopic,
    Lesson,
)

logger = logging.getLogger(__name__)

# Lesson order range -> (target_level, level_display_name)
LEVEL_RANGES = [
    (1, 11, CourseProgram.TargetLevel.BEGINNER, 'Новичок'),
    (12, 22, CourseProgram.TargetLevel.INTERMEDIATE, 'Средний уровень'),
    (23, 33, CourseProgram.TargetLevel.ADVANCED, 'Углубленный уровень'),
]

LEVEL_PROGRAM_ORDER = {
    CourseProgram.TargetLevel.BEGINNER: 1,
    CourseProgram.TargetLevel.INTERMEDIATE: 2,
    CourseProgram.TargetLevel.ADVANCED: 3,
}

# Per-language metadata
LANGUAGE_META = {
    'python': {'name': 'Python', 'icon': '🐍', 'color': '#3776AB', 'order': 1},
    'cpp': {'name': 'C++', 'icon': '⚡', 'color': '#00599C', 'order': 2},
    'javascript': {'name': 'JavaScript', 'icon': '🟨', 'color': '#F7DF1E', 'order': 3},
    'rust': {'name': 'Rust', 'icon': '🦀', 'color': '#000000', 'order': 4},
    'css': {'name': 'CSS', 'icon': '🎨', 'color': '#1572B6', 'order': 5},
    'csharp': {'name': 'C#', 'icon': '🔷', 'color': '#68217A', 'order': 6},
}


class Command(BaseCommand):
    help = 'Import courses, topics, subtopics and lessons from parsed JSON fixtures.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixtures-dir',
            type=str,
            default='fixtures',
            help='Directory containing fixtures/lessons/<lang>/*.json',
        )
        parser.add_argument(
            '--language',
            type=str,
            default=None,
            help='Import only this language slug (python, cpp, javascript, rust, css, csharp)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse and validate without writing to the database',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing learning data before import',
        )

    def handle(self, *args, **options):
        fixtures_dir = Path(options['fixtures_dir'])
        if not fixtures_dir.is_absolute():
            fixtures_dir = Path(__file__).resolve().parent.parent.parent.parent / fixtures_dir

        language_slug = options.get('language')
        dry_run = options.get('dry_run')
        clear = options.get('clear')

        if clear and not dry_run:
            self.stdout.write('Clearing existing learning data...')
            ProgrammingLanguage.objects.all().delete()  # cascades to programs/topics/subtopics/lessons

        if not fixtures_dir.exists():
            self.stderr.write(self.style.ERROR(f'Fixtures directory not found: {fixtures_dir}'))
            return

        lessons_dir = fixtures_dir / 'lessons'
        if not lessons_dir.exists():
            self.stderr.write(self.style.ERROR(f'Lessons directory not found: {lessons_dir}'))
            return

        language_dirs = sorted([d for d in lessons_dir.iterdir() if d.is_dir()])
        if language_slug:
            language_dirs = [d for d in language_dirs if d.name == language_slug]

        if not language_dirs:
            self.stderr.write(self.style.WARNING('No language directories found.'))
            return

        total_lessons = 0
        for lang_dir in language_dirs:
            lang_slug = lang_dir.name
            self.stdout.write(f'\n=== Importing {lang_slug} ===')
            count = self.import_language(lang_slug, lang_dir, dry_run)
            total_lessons += count
            self.stdout.write(f'  {count} lesson(s) processed for {lang_slug}')

        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: {total_lessons} lesson(s) processed')
        )
        if dry_run:
            self.stdout.write(self.style.WARNING('(dry run — no changes persisted)'))

    def import_language(self, lang_slug, lang_dir, dry_run):
        meta = LANGUAGE_META.get(
            lang_slug,
            {'name': lang_slug.title(), 'icon': '', 'color': '', 'order': 99},
        )

        if dry_run:
            self.stdout.write(f'  [dry-run] language: {meta["name"]}')
        else:
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

        # Load all lesson JSONs for this language
        lesson_files = sorted(lang_dir.glob('*.json'))
        lessons_data = []
        for lf in lesson_files:
            try:
                with open(lf, encoding='utf-8') as f:
                    data = json.load(f)
                data['_file'] = lf.name
                lessons_data.append(data)
            except (json.JSONDecodeError, OSError) as exc:
                self.stderr.write(
                    self.style.WARNING(f'  Skip {lf.name}: {exc}')
                )

        # Sort by lesson order
        lessons_data.sort(key=lambda d: d.get('lesson_order', 999))

        count = 0
        for data in lessons_data:
            try:
                if dry_run:
                    lesson_order = data.get('lesson_order', 0)
                    program_level, topic_order = self._map_order_to_program(lesson_order)
                    self.stdout.write(
                        f'  [dry-run] lesson {lesson_order}: {data.get("title", "")[:60]} '
                        f'-> {program_level} / topic {topic_order}'
                    )
                    count += 1
                    continue

                self._import_one_lesson(language, data)
                count += 1
            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(
                        f'  Failed {data.get("_file", "?")}: {exc}'
                    )
                )

        if not dry_run:
            language.update_counts()

        return count

    def _map_order_to_program(self, lesson_order):
        """Map a lesson order (1-33) to (target_level, topic_order_within_program)."""
        for start, end, level, _ in LEVEL_RANGES:
            if start <= lesson_order <= end:
                topic_order = ((lesson_order - start) % 11) + 1
                return level, topic_order
        # Fallback: advanced
        return CourseProgram.TargetLevel.ADVANCED, ((lesson_order - 1) % 11) + 1

    def _import_one_lesson(self, language, data):
        lesson_order = data.get('lesson_order', 0)
        program_level, topic_order = self._map_order_to_program(lesson_order)

        # Get or create program
        program = self._get_or_create_program(language, program_level)

        # Extract topic name from lesson title
        topic_name = self._extract_topic_name(data.get('title', ''))
        topic_slug = f'{django_slugify(topic_name) or "topic"}-{topic_order}'

        # Get or create topic (one topic per lesson order within program)
        # Use get_or_create to avoid overwriting existing topic data when
        # multiple lessons share the same topic_order
        topic, created = Topic.all_objects.get_or_create(
            program=program,
            order=topic_order,
            defaults={
                'name': topic_name,
                'slug': topic_slug,
                'description': data.get('short_description', ''),
                'difficulty': 1,
                'estimated_minutes': 30,
                'is_base_topic': topic_order == 1,
                'status': Topic.PublishStatus.PUBLISHED,
            },
        )

        # Get or create subtopic (one subtopic per topic)
        subtopic, _ = SubTopic.all_objects.update_or_create(
            topic=topic,
            order=1,
            defaults={
                'name': 'Основной материал',
                'slug': f'subtopic-{topic_order}',
                'description': '',
                'status': SubTopic.PublishStatus.PUBLISHED,
            },
        )

        # Create lesson
        content_blocks = data.get('content_blocks', [])
        estimated = data.get('estimated_minutes', 15)
        lesson_slug = data.get('slug') or django_slugify(data.get('title', 'lesson')) or 'lesson'

        change_log_parts = [f'Imported from {data.get("_file", "")}']
        if data.get('goals'):
            change_log_parts.append(f'{len(data["goals"])} goals')
        if data.get('practice_tasks'):
            change_log_parts.append(f'{len(data["practice_tasks"])} practice tasks')

        lesson, _ = Lesson.all_objects.update_or_create(
            subtopic=subtopic,
            order=lesson_order,
            defaults={
                'name': data.get('title', 'Untitled'),
                'slug': lesson_slug,
                'short_description': data.get('short_description', ''),
                'content': content_blocks,
                'estimated_minutes': estimated,
                'version': 1,
                'change_log': '; '.join(change_log_parts),
                'status': Lesson.PublishStatus.PUBLISHED,
            },
        )

        return lesson

    def _get_or_create_program(self, language, target_level):
        level_name = dict(CourseProgram.TargetLevel.choices).get(target_level, target_level)
        program_slug = f'{language.slug}-{target_level}'

        program, _ = CourseProgram.all_objects.update_or_create(
            language=language,
            slug=program_slug,
            defaults={
                'name': f'{language.name} — {level_name}',
                'description': f'Курс {language.name} для уровня {level_name}.',
                'target_level': target_level,
                'order': LEVEL_PROGRAM_ORDER[target_level],
                'estimated_hours': 40,
                'status': CourseProgram.PublishStatus.PUBLISHED,
            },
        )
        return program

    def _extract_topic_name(self, title):
        """Extract topic name from lesson title: 'Урок 1.2: Введение — описание'"""
        name = title
        # Strip lesson number prefix: 'Урок 1.2:' or 'Урок 1:'
        name = re.sub(r'^Урок\s*\d+(?:\.\d+)?\s*[:\—-]\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^Урок\s*\d+(?:\.\d+)?\s*', '', name, flags=re.IGNORECASE)
        # Take part before em-dash or hyphen
        if '—' in name:
            name = name.split('—', 1)[0].strip()
        elif '-' in name:
            name = name.split('-', 1)[0].strip()
        return name.strip() or 'Тема'
