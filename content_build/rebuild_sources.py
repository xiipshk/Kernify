"""Восстановление исходника урока из базы (обратная генерация)."""

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

HELPERS = '''from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\\n")


def text(content: str) -> dict:
    return {"type": "text", "content": content.strip()}


def heading(content: str, level: int = 2) -> dict:
    return {"type": "heading", "level": level, "content": content.strip()}


def bullets(*items: str, ordered: bool = False) -> dict:
    return {"type": "list", "ordered": ordered, "items": list(items)}


def numbered(*items: str) -> dict:
    return bullets(*items, ordered=True)


def table(headers: list[str], rows: list[list[str]]) -> dict:
    return {"type": "table", "headers": headers, "rows": rows}


def callout(style: str, title: str, content: str) -> dict:
    return {"type": "callout", "style": style, "title": title, "content": content}


def example(language: str, source: str) -> dict:
    return {"type": "code", "language": language, "content": code(source)}
'''


def literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_block(block: dict) -> str:
    kind = block.get("type")
    if kind == "text":
        return f"        text({literal(block.get('content', ''))}),"
    if kind == "heading":
        level = block.get("level", 2)
        if level == 2:
            return f"        heading({literal(block.get('content', ''))}),"
        return f"        heading({literal(block.get('content', ''))}, {level}),"
    if kind == "list":
        items = ",\n".join(f"            {literal(i)}" for i in block.get("items", []))
        fn = "numbered" if block.get("ordered") else "bullets"
        return f"        {fn}(\n{items},\n        ),"
    if kind == "table":
        headers = ", ".join(literal(h) for h in block.get("headers", []))
        rows = ",\n".join(
            "            [" + ", ".join(literal(c) for c in row) + "]" for row in block.get("rows", [])
        )
        return f"        table(\n            [{headers}],\n            [\n{rows},\n            ],\n        ),"
    if kind == "callout":
        return (
            "        callout(\n"
            f"            {literal(block.get('style', 'info'))},\n"
            f"            {literal(block.get('title', ''))},\n"
            f"            {literal(block.get('content', ''))},\n"
            "        ),"
        )
    if kind == "code":
        return (
            "        example(\n"
            f"            {literal(block.get('language', 'text'))},\n"
            f"            {literal(block.get('content', ''))},\n"
            "        ),"
        )
    raise ValueError(f"неизвестный тип блока: {kind}")


def main() -> None:
    language_slug = sys.argv[1]
    only = set(sys.argv[2:])
    language = ProgrammingLanguage.objects.get(slug=language_slug)
    entries = [
        e
        for e in json.loads(INDEX.read_text(encoding="utf-8"))
        if e["language"] == language_slug
    ]
    lessons = {x.slug: x for x in Lesson.objects.filter(topic__program__language=language)}
    for entry in entries:
        key = f"{entry['level']}_{entry['order']}"
        if only and key not in only:
            continue
        path = BASE_DIR / entry["file"]
        if path.exists():
            continue
        lesson = lessons.get(entry["slug"])
        if lesson is None or not lesson.content:
            print(f"пропуск (нет содержимого): {entry['lesson_name']}")
            continue

        content = ",\n".join(render_block(b) for b in lesson.content)
        source = f'''"""Урок {entry['order']} курса {language_slug}: восстановлен из базы."""

{HELPERS}
LESSON = {{
    "language": {literal(language_slug)},
    "program_order": {entry['level']},
    "topic_order": {entry['order']},
    "name": {literal(lesson.name)},
    "slug": {literal(lesson.slug)},
    "short_description": {literal(lesson.short_description or '')},
    "topic_name": {literal(lesson.topic.name)},
    "topic_description": {literal(lesson.topic.description or '')},
    "learning_objectives": {json.dumps(lesson.topic.learning_objectives or [], ensure_ascii=False)},
    "estimated_minutes": {lesson.estimated_minutes},
    "xp_reward": {lesson.xp_reward},
    "difficulty": {literal(lesson.difficulty)},
    "tags": {json.dumps(lesson.tags or [], ensure_ascii=False)},
    "starter_code": {literal(lesson.starter_code or '')},
    "hints": {json.dumps(lesson.hints or [], ensure_ascii=False, indent=8)},
    "content": [
{content}
    ],
}}
'''
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        print(f"восстановлен: {path}")


if __name__ == "__main__":
    main()
