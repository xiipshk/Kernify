"""Создание уроков из манифеста в новых пустых программах.

Исправляет ситуацию, когда `apply_lesson.py` находит урок в чужой
программе по имени и перезаписывает его вместо создания в нужной.

Использование:
    python3 content_build/create_missing_lessons.py csharp
    python3 content_build/create_missing_lessons.py javascript
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

from learning.models import (  # noqa: E402
    CourseProgram,
    Lesson,
    ProgrammingLanguage,
    Topic,
)

INDEX = BASE_DIR / "content_build" / "lessons_index.json"


def main() -> None:
    language_slug = sys.argv[1]
    language = ProgrammingLanguage.objects.get(slug=language_slug)
    entries = [
        e
        for e in json.loads(INDEX.read_text(encoding="utf-8"))
        if e["language"] == language_slug
    ]
    created = 0
    for entry in entries:
        program = CourseProgram.objects.get(language=language, order=entry["level"])
        topic, _ = Topic.objects.get_or_create(
            program=program,
            order=entry["order"],
            defaults={
                "name": entry["title"],
                "slug": f"{language.slug}-{program.order}-{entry['order']}",
                "status": Topic.PublishStatus.PUBLISHED,
            },
        )
        lesson = Lesson.objects.filter(topic=topic, order=1).first()
        if lesson is None:
            Lesson.objects.create(
                topic=topic,
                order=1,
                name=entry["lesson_name"],
                slug=entry["slug"],
                short_description="",
                content=[],
                status=Lesson.PublishStatus.DRAFT,
            )
            created += 1
            print(f"создан: {language_slug} {entry['level']}.{entry['order']} {entry['lesson_name']}")
        elif lesson.slug != entry["slug"]:
            lesson.slug = entry["slug"]
            lesson.save(update_fields=["slug"])
            print(f"исправлен slug: {entry['lesson_name']}")
    print(f"итого создано: {created}")


if __name__ == "__main__":
    main()
