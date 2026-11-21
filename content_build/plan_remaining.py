"""Готовит задания для агентов-авторов уроков.

Использование:
    python3 content_build/plan_remaining.py <язык>

Печатает по одному уроку на строку в формате JSON, чтобы внешний
скрипт мог раздать их агентам.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
INDEX = BASE / "lessons_index.json"

HELPERS = {
    "css": "css_kit",
    "cpp": "lesson_kit",
    "python": "lesson_kit",
    "csharp": "lesson_kit",
    "javascript": "lesson_kit",
    "rust": "lesson_kit",
}


def main() -> None:
    language = sys.argv[1]
    entries = json.loads(INDEX.read_text(encoding="utf-8"))
    todo = [
        e
        for e in entries
        if e["language"] == language and not (BASE.parent / e["file"]).exists()
    ]
    print(json.dumps({"language": language, "helper": HELPERS.get(language, "lesson_kit"), "count": len(todo)}, ensure_ascii=False))
    for e in todo:
        print(json.dumps(e, ensure_ascii=False))


if __name__ == "__main__":
    main()
