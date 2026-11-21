"""Применить уроки из content_build/lessons к базе данных.

Использование:
    python content_build/apply_lesson.py content_build/lessons/python/01_vvedenie.py
    python content_build/apply_all.py                      # все готовые файлы
    python content_build/apply_all.py --language python    # только один язык
    python content_build/apply_all.py --language python --level 1
    python content_build/apply_all.py --dry-run
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.db import transaction  # noqa: E402

from learning.models import CourseProgram, Lesson, ProgrammingLanguage, Topic  # noqa: E402

INDEX_PATH = Path(__file__).resolve().parent / "lessons_index.json"


def load_lesson(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location("lesson_payload", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Не удалось загрузить файл: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LESSON


def apply(path: Path, *, verbose: bool = True) -> Lesson:
    """Записать один урок в базу и вернуть сохранённый объект."""
    path = Path(path).resolve()
    data = load_lesson(path)

    with transaction.atomic():
        language = ProgrammingLanguage.objects.get(slug=data["language"])
        program = CourseProgram.objects.get(
            language=language,
            order=data["program_order"],
        )

        lesson = None
        if data.get("legacy_lesson_id"):
            lesson = (
                Lesson.objects.filter(pk=data["legacy_lesson_id"])
                .select_related("topic")
                .first()
            )

        if lesson is not None:
            topic = lesson.topic
        else:
            topic = Topic.objects.filter(
                program=program,
                order=data["topic_order"],
            ).first()

        if topic is None:
            topic = Topic.objects.create(
                program=program,
                order=data["topic_order"],
                name=data["topic_name"],
                slug=f"{language.slug}-{program.order}-{data['topic_order']}",
                status=Topic.PublishStatus.PUBLISHED,
            )

        topic.name = data["topic_name"]
        topic.description = data.get("topic_description", "")
        topic.name_en = ""
        topic.description_en = ""
        topic.learning_objectives = data.get("learning_objectives", [])
        topic.difficulty = {
            1: "easy",
            2: "medium",
            3: "hard",
        }.get(program.order, "easy")
        topic.estimated_minutes = data.get("estimated_minutes", 30)
        topic.is_base_topic = data["topic_order"] == 1
        topic.status = Topic.PublishStatus.PUBLISHED
        topic.is_deleted = False
        topic.deleted_at = None
        topic.save()

        if lesson is None:
            lesson = Lesson.objects.filter(topic=topic, order=1).first()

        if lesson is None:
            lesson = Lesson(topic=topic, order=1, slug=data["slug"])

        lesson.topic = topic
        lesson.name = data["name"]
        lesson.slug = data["slug"]
        lesson.short_description = data.get("short_description", "")
        lesson.content = data["content"]
        lesson.name_en = ""
        lesson.short_description_en = ""
        lesson.content_en = []
        lesson.display_options = {}
        lesson.lesson_type = Lesson.LessonType.TEXT
        lesson.starter_code = data.get("starter_code", "")
        lesson.hints = data.get("hints", [])
        lesson.xp_reward = data.get("xp_reward", 10)
        lesson.difficulty = data.get("difficulty", "beginner")
        lesson.tags = data.get("tags", [])
        lesson.estimated_minutes = data.get("estimated_minutes", 30)
        lesson.status = Lesson.PublishStatus.PUBLISHED
        lesson.is_deleted = False
        lesson.deleted_at = None
        lesson.save()

        topic.update_counts()
        program.update_counts()
        language.update_counts()

    if verbose:
        chars = sum(
            len(str(block.get("content", ""))) for block in lesson.content
        )
        print(f"Готово: {lesson.name}")
        print(f"Урок: {lesson.slug} (id={lesson.pk})")
        print(f"Блоков: {len(lesson.content)}, текста: {chars}")

    return lesson


def apply_index_entry(entry: dict, *, verbose: bool = True) -> Lesson | None:
    path = BASE_DIR / entry["file"]
    if not path.exists():
        if verbose:
            print(f"Пропуск (нет файла): {entry['lesson_name']}")
        return None
    return apply(path, verbose=verbose)


def load_index() -> list[dict]:
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def main() -> None:
    args = sys.argv[1:]
    if args and not args[0].startswith("--"):
        for raw in args:
            apply(Path(raw))
        return

    dry_run = "--dry-run" in args
    language = None
    level = None
    if "--language" in args:
        language = args[args.index("--language") + 1]
    if "--level" in args:
        level = int(args[args.index("--level") + 1])

    entries = load_index()
    if language:
        entries = [e for e in entries if e["language"] == language]
    if level:
        entries = [e for e in entries if e["level"] == level]

    done = 0
    for entry in entries:
        path = BASE_DIR / entry["file"]
        if not path.exists():
            continue
        if dry_run:
            print(f"[dry-run] {entry['lesson_name']} <- {entry['file']}")
            continue
        apply(path)
        done += 1

    print(f"Применено уроков: {done}")


if __name__ == "__main__":
    main()
