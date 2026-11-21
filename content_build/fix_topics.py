"""Починка структуры тем: одна тема на один урок.

В части программ тема создавалась под каждую запись каталога, и в одной
теме оказывались уроки разных уровней. Скрипт создаёт отдельные темы
с правильными именами и переносит в них уроки по слагу из манифеста.

Использование:
    python3 content_build/fix_topics.py csharp
    python3 content_build/fix_topics.py javascript
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from learning.models import CourseProgram, Lesson, ProgrammingLanguage, Topic  # noqa: E402

INDEX = BASE_DIR / "content_build" / "lessons_index.json"


def main() -> None:
    language_slug = sys.argv[1]
    language = ProgrammingLanguage.objects.get(slug=language_slug)
    entries = [
        e
        for e in json.loads(INDEX.read_text(encoding="utf-8"))
        if e["language"] == language_slug
    ]
    lessons = {x.slug: x for x in Lesson.objects.filter(topic__program__language=language)}
    moved = 0
    for entry in entries:
        program = CourseProgram.objects.get(language=language, order=entry["level"])
        topic = (
            Topic.objects.filter(program=program, order=entry["order"]).order_by("pk").first()
        )
        if topic is None:
            topic = Topic.objects.create(
                program=program,
                order=entry["order"],
                name=entry["title"],
                slug=f"{language.slug}-{program.order}-{entry['order']}",
                status=Topic.PublishStatus.PUBLISHED,
            )
        topic.name = entry["title"]
        topic.name_en = ""
        topic.description_en = ""
        topic.status = Topic.PublishStatus.PUBLISHED
        topic.is_deleted = False
        topic.save()

        lesson = lessons.get(entry["slug"])
        if lesson is not None and lesson.topic_id != topic.pk:
            lesson.topic = topic
            lesson.save(update_fields=["topic"])
            moved += 1
            print(f"перенесён: {entry['lesson_name']} → тема {entry['level']}.{entry['order']}")
    print(f"перенесено уроков: {moved}")


if __name__ == "__main__":
    main()
