"""Сверка манифеста и базы: чего нет на диске и что пусто в базе."""

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

from learning.models import Lesson, ProgrammingLanguage  # noqa: E402

INDEX = BASE_DIR / "content_build" / "lessons_index.json"


def status(language: str) -> dict:
    entries = [
        e
        for e in json.loads(INDEX.read_text(encoding="utf-8"))
        if e["language"] == language
    ]
    lang = ProgrammingLanguage.objects.get(slug=language)
    lessons = list(Lesson.objects.filter(topic__program__language=lang).select_related("topic"))
    by_slug = {x.slug: x for x in lessons}
    report = {"total": len(entries), "no_file": [], "empty_in_db": [], "ok": 0}
    for entry in entries:
        file_exists = os.path.exists(BASE_DIR / entry["file"])
        lesson = by_slug.get(entry["slug"])
        filled = bool(lesson and lesson.content)
        if file_exists and filled:
            report["ok"] += 1
            continue
        if not file_exists:
            report["no_file"].append(entry["lesson_name"])
        if not filled:
            report["empty_in_db"].append(entry["lesson_name"])
    return report


def main() -> None:
    for language in sys.argv[1:] or ["csharp", "javascript", "rust"]:
        rep = status(language)
        print(f"=== {language}: {rep['ok']}/{rep['total']} готово")
        if rep["no_file"]:
            print("  нет файла:", ", ".join(rep["no_file"]))
        if rep["empty_in_db"]:
            print("  пусто в базе:", ", ".join(rep["empty_in_db"]))


if __name__ == "__main__":
    main()
