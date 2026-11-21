"""Собрать Markdown-предпросмотр уроков из content_build/lessons.

Использование:
    python content_build/make_preview.py content_build/lessons/python/02_peremennye_i_tipy.py
    python content_build/make_preview.py --all
    python content_build/make_preview.py --all --language python
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PREVIEW_DIR = Path(__file__).resolve().parent / "preview"
INDEX_PATH = Path(__file__).resolve().parent / "lessons_index.json"


def load_lesson(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location("lesson_payload", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Не удалось загрузить файл: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LESSON


def render(data: dict) -> str:
    out = [f"# {data['name']}", "", data.get("short_description", ""), ""]

    for block in data["content"]:
        kind = block["type"]
        if kind == "heading":
            out += [("#" * block.get("level", 2)) + " " + block["content"], ""]
        elif kind == "text":
            out += [block["content"], ""]
        elif kind == "code":
            out += [f"```{block.get('language', 'text')}", block["content"], "```", ""]
        elif kind == "list":
            for index, item in enumerate(block["items"], 1):
                marker = f"{index}. " if block.get("ordered") else "- "
                out.append(marker + item)
            out.append("")
        elif kind == "table":
            out.append("| " + " | ".join(block["headers"]) + " |")
            out.append("|" + "|".join(["---"] * len(block["headers"])) + "|")
            for row in block["rows"]:
                out.append("| " + " | ".join(row) + " |")
            out.append("")
        elif kind == "callout":
            out += [f"> **{block.get('title', '')}**", f"> {block.get('content', '')}", ""]
        elif kind == "blockquote":
            out += ["> " + block.get("content", ""), ""]

    return "\n".join(out)


def write_preview(path: Path, data: dict) -> Path:
    output = PREVIEW_DIR / path.parent.name / (path.stem + ".md")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(data), encoding="utf-8")
    return output


def main() -> None:
    args = sys.argv[1:]
    if not args:
        raise SystemExit("Укажите путь к файлу урока или --all")

    if args[0] == "--all":
        language = None
        if "--language" in args:
            language = args[args.index("--language") + 1]
        entries = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        made = 0
        for entry in entries:
            if language and entry["language"] != language:
                continue
            path = BASE_DIR / entry["file"]
            if not path.exists():
                continue
            write_preview(path, load_lesson(path))
            made += 1
        print(f"Предпросмотров собрано: {made} -> {PREVIEW_DIR}")
        return

    path = Path(args[0]).resolve()
    data = load_lesson(path)
    print(write_preview(path, data))


if __name__ == "__main__":
    main()
