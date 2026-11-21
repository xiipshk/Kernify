"""Сводка готовности уроков.

Использование:
    python content_build/progress.py            # по всем языкам
    python content_build/progress.py python     # подробно по одному языку
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from content_build.validate_lessons import check, load_lesson, text_volume  # noqa: E402

INDEX_PATH = Path(__file__).resolve().parent / "lessons_index.json"


def main() -> None:
    entries = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    language_filter = sys.argv[1] if len(sys.argv) > 1 else None

    counts: dict[tuple[str, int], list[int]] = defaultdict(lambda: [0, 0])
    problems: list[tuple[str, str]] = []
    details: list[tuple[str, int, int, str, str, int, int]] = []

    for entry in entries:
        key = (entry["language"], entry["level"])
        counts[key][1] += 1
        path = BASE_DIR / entry["file"]
        if not path.exists():
            continue
        counts[key][0] += 1
        messages = check(path, entry)
        errors = [m for m in messages if m.startswith("ОШИБКА")]
        if errors:
            problems.append((entry["lesson_name"], "; ".join(errors)))
        try:
            data = load_lesson(path)
            details.append(
                (
                    entry["lesson_name"],
                    text_volume(data["content"]),
                    sum(1 for b in data["content"] if b["type"] == "code"),
                    entry["file"],
                    entry["language"],
                    entry["level"],
                    entry["order"],
                )
            )
        except Exception:  # noqa: BLE001
            pass

    done = sum(value[0] for value in counts.values())
    total = len(entries)
    print(f"Готово файлов: {done} из {total}")
    for (language, level), (ready, all_count) in sorted(counts.items()):
        bar = "#" * ready + "." * (all_count - ready)
        print(f"  {language:11} уровень {level}  {bar}  {ready}/{all_count}")

    if problems:
        print(f"\nФайлы с ошибками ({len(problems)}):")
        for name, error in problems:
            print(f"  {name}: {error}")

    if language_filter:
        print("\nДетали:")
        for name, chars, codes, _file, language, level, order in sorted(
            details,
            key=lambda item: (item[4], item[5], item[6]),
        ):
            if language != language_filter:
                continue
            print(
                f"  {name:60} {chars:6} знаков, {codes:3} блоков кода"
            )


if __name__ == "__main__":
    main()
