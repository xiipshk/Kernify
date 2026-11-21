"""Склейка коротких абзацев с соседним текстом в пределах раздела."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from learning.models import Lesson, ProgrammingLanguage  # noqa: E402

MIN_LEN = 120
PREFIXES = ("Пример ожидаемого результата",)


def merge(blocks: list[dict]) -> tuple[list[dict], int]:
    """Склеивает короткие text-блоки с предыдущим абзацем раздела."""
    out: list[dict] = []
    merged = 0
    for block in blocks:
        kind = block.get("type")
        if kind == "heading":
            out.append(block)
            continue
        if kind != "text":
            out.append(block)
            continue

        content = (block.get("content") or "").strip()
        if len(content) >= MIN_LEN or content.startswith(PREFIXES):
            out.append(block)
            continue

        # ищем предыдущий text в том же разделе
        target = None
        for prev in reversed(out):
            if prev.get("type") == "heading":
                break
            if prev.get("type") == "text":
                target = prev
                break

        if target is None:
            out.append(block)
            continue

        prev_text = target["content"].rstrip()
        if prev_text.endswith((".", "!", "?", ":", "…")):
            joined = prev_text + " " + content
        else:
            joined = prev_text + ". " + content
        target["content"] = joined
        merged += 1
    return out, merged


def main(languages: list[str]) -> None:
    total = 0
    for slug in languages:
        lang = ProgrammingLanguage.objects.get(slug=slug)
        for lesson in Lesson.objects.filter(topic__program__language=lang):
            blocks = lesson.content or []
            if not isinstance(blocks, list):
                continue
            new_blocks, merged = merge(blocks)
            if merged:
                lesson.content = new_blocks
                lesson.save(update_fields=["content"])
                print(f"{lesson.slug}: склеено {merged}")
                total += merged
    print(f"всего склеено: {total}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["css"])
