"""Перезапуск оставшихся уроков Rust порциями.

Для каждого урока из очереди запускает `opencode`-подобный агент нельзя,
поэтому скрипт печатает готовые задания в файлы: prompt-ы читает
человек (или сессия) и раздаёт их агентам порциями.

Использование:
    python3 content_build/queue_rust.py 10
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

from learning.models import Lesson, ProgrammingLanguage  # noqa: E402

INDEX = BASE_DIR / "content_build" / "lessons_index.json"
PROGRAM = {
    1: "Rust — Начинающий",
    2: "Rust — Средний",
    3: "Rust — Продвинутый",
}


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    language_slug = sys.argv[2] if len(sys.argv) > 2 else "rust"
    language = ProgrammingLanguage.objects.get(slug=language_slug)
    filled = {x.slug: bool(x.content) for x in Lesson.objects.filter(topic__program__language=language)}
    entries = [
        e
        for e in json.loads(INDEX.read_text(encoding="utf-8"))
        if e["language"] == language_slug and not filled.get(e["slug"])
    ]
    out = BASE_DIR / "content_build" / "queue"
    out.mkdir(exist_ok=True)
    for entry in entries[:limit]:
        key = f"{entry['level']}_{entry['order']}"
        prompt = f"""Author ONE Kernify lesson. Read the brief /Users/xiip.shk/работа/Kernify/content_build/agent_prompt.md and follow it exactly with these values: LANGUAGE={language_slug}, HELPER=lesson_kit, PROGRAM={PROGRAM[entry['level']]}, LEVEL={entry['level']}, ORDER={entry['order']}, LESSON_NAME="{entry['lesson_name']}", SLUG={entry['slug']}, SOURCE="{entry['source']}", FILE={entry['file']}, DIFFICULTY={entry['difficulty']}, MINUTES={entry['estimated_minutes']}, XP={entry['xp_reward']}. Structure reference: /Users/xiip.shk/работа/Kernify/content_build/lessons/cpp/1_3.py (copy helper functions verbatim). The lesson already exists in the database as an EMPTY record with exactly this name and slug — do not rename it and do not touch the index file. Work inside /Users/xiip.shk/работа/Kernify only. Validate from /Users/xiip.shk/работа: `python3 Kernify/content_build/validate_lessons.py Kernify/{entry['file']}` until 0 errors, then `cd /Users/xiip.shk/работа/Kernify && python3 content_build/apply_lesson.py {entry['file']}`. Reply: lesson name, text chars, code count, validator result.
"""
        (out / f"{language_slug}_{key}.txt").write_text(prompt, encoding="utf-8")
        print(f"{language_slug} {key}: {entry['lesson_name']}")
    print(f"в очереди: {len(entries)}")


if __name__ == "__main__":
    main()
