"""Перестроить темы и уроки всех курсов по единому учебному плану.

Скрипт не создаёт новый контент: он переименовывает и переупорядочивает
существующие темы и уроки, очищает старые материалы и готовит места для
новых уроков. Идентификаторы сохраняются, поэтому прогресс пользователей
не теряется.

Использование:
    python content_build/rebuild_structure.py
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.db import transaction  # noqa: E402

from learning.models import CourseProgram, Lesson, ProgrammingLanguage, Topic  # noqa: E402
from content_build.curriculum import build_slots  # noqa: E402

TEMP_ORDER_BASE = 10000


def main() -> None:
    slots = build_slots()
    by_language: dict[str, list] = defaultdict(list)
    for slot in slots:
        by_language[slot.language].append(slot)

    with transaction.atomic():
        for language_slug, language_slots in by_language.items():
            language = ProgrammingLanguage.all_objects.get(slug=language_slug)
            programs = list(
                CourseProgram.all_objects.filter(language=language).order_by("order")
            )
            if len(programs) != 3:
                raise SystemExit(
                    f"{language_slug}: ожидалось 3 программы, найдено {len(programs)}"
                )

            topics = list(
                Topic.all_objects.filter(program__language=language)
                .select_related("program")
                .order_by("program__order", "order")
            )
            lessons = list(
                Lesson.all_objects.filter(topic__program__language=language)
                .select_related("topic")
                .order_by("topic__program__order", "topic__order", "order")
            )

            if len(topics) != len(language_slots):
                raise SystemExit(
                    f"{language_slug}: тем {len(topics)}, уроков в плане {len(language_slots)}"
                )
            if len(lessons) != len(language_slots):
                raise SystemExit(
                    f"{language_slug}: уроков {len(lessons)}, в плане {len(language_slots)}"
                )

            # Освобождаем уникальные пары (program, order) и (topic, order).
            for index, topic in enumerate(topics):
                topic.order = TEMP_ORDER_BASE + index
                topic.save(update_fields=["order", "updated_at"])
            for index, lesson in enumerate(lessons):
                lesson.order = TEMP_ORDER_BASE + index
                lesson.save(update_fields=["order", "updated_at"])

            for slot, topic, lesson in zip(language_slots, topics, lessons):
                program = programs[slot.level - 1]

                topic.program = program
                topic.order = slot.order
                topic.name = slot.topic_name
                topic.name_en = ""
                topic.slug = f"{slot.language}-{slot.level}-{slot.order}"
                topic.description = ""
                topic.description_en = ""
                topic.learning_objectives = []
                topic.difficulty = slot.topic_difficulty
                topic.estimated_minutes = slot.estimated_minutes
                topic.is_base_topic = slot.order == 1
                topic.status = Topic.PublishStatus.PUBLISHED
                topic.is_deleted = False
                topic.deleted_at = None
                topic.save()

                lesson.topic = topic
                lesson.order = 1
                lesson.name = slot.lesson_name
                lesson.name_en = ""
                lesson.slug = slot.slug
                lesson.short_description = ""
                lesson.short_description_en = ""
                lesson.content = []
                lesson.content_en = []
                lesson.display_options = {}
                lesson.lesson_type = Lesson.LessonType.TEXT
                lesson.starter_code = ""
                lesson.hints = []
                lesson.xp_reward = slot.xp_reward
                lesson.difficulty = slot.difficulty
                lesson.tags = []
                lesson.estimated_minutes = slot.estimated_minutes
                lesson.status = Lesson.PublishStatus.PUBLISHED
                lesson.is_deleted = False
                lesson.deleted_at = None
                lesson.save()

            for program in programs:
                program.update_counts()
            language.update_counts()

            print(
                f"{language.name}: {len(language_slots)} уроков, "
                f"{len(programs)} программы"
            )

    print("Структура перестроена.")


if __name__ == "__main__":
    main()
