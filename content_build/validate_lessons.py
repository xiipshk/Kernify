"""Проверить файлы уроков перед публикацией.

Использование:
    python content_build/validate_lessons.py                 # все готовые файлы
    python content_build/validate_lessons.py --language python --level 1
    python content_build/validate_lessons.py path/to/file.py

Проверяет структуру LESSON, соответствие учебному плану, допустимые блоки,
объём текста, количество примеров кода и отсутствие мусора вроде эмодзи.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

INDEX_PATH = Path(__file__).resolve().parent / "lessons_index.json"

BLOCK_TYPES = {
    "text",
    "heading",
    "code",
    "list",
    "table",
    "callout",
    "blockquote",
    "image",
    "video",
    "divider",
}

TEXT_BLOCKS = {"text", "heading", "callout", "blockquote"}
CALLOUT_STYLES = {"info", "warning", "success", "danger", "error"}

REQUIRED_KEYS = {
    "language",
    "program_order",
    "topic_order",
    "name",
    "slug",
    "short_description",
    "topic_name",
    "topic_description",
    "learning_objectives",
    "estimated_minutes",
    "xp_reward",
    "difficulty",
    "tags",
    "content",
}

MIN_CHARS = 12_000
MAX_CHARS = 19_000
MIN_CODE = 8
MAX_CODE = 40

EMOJI_RE = re.compile(
    "[" "\U0001f300-\U0001faff" "\U00002600-\U000027bf" "\U0001f1e6-\U0001f1ff" "]"
)
PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|FIXME|XXX|Lorem ipsum)\b", re.IGNORECASE)
STYLE_BAD_PHRASES = [
    "давайте разберёмся",
    "в этом уроке мы рассмотрим",
    "как вы уже знаете",
    "очевидно, что",
    "просто запомните",
]


def load_lesson(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location("lesson_payload", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Не удалось загрузить файл: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LESSON


def text_volume(blocks: list[dict]) -> int:
    total = 0
    for block in blocks:
        kind = block.get("type")
        if kind in TEXT_BLOCKS:
            total += len(str(block.get("content", "")))
        elif kind == "list":
            total += sum(len(str(item)) for item in block.get("items", []))
        elif kind == "table":
            total += sum(len(str(cell)) for cell in block.get("headers", []))
            for row in block.get("rows", []):
                total += sum(len(str(cell)) for cell in row)
    return total


def check(path: Path, entry: dict | None) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        data = load_lesson(path)
    except Exception as exc:  # noqa: BLE001
        return [f"не удалось загрузить: {exc}"]

    missing = REQUIRED_KEYS - data.keys()
    if missing:
        errors.append(f"нет ключей: {', '.join(sorted(missing))}")
        return errors

    if entry:
        if data["language"] != entry["language"]:
            errors.append(f"язык {data['language']} != {entry['language']}")
        if data["program_order"] != entry["level"]:
            errors.append(f"уровень {data['program_order']} != {entry['level']}")
        if data["topic_order"] != entry["order"]:
            errors.append(f"порядок {data['topic_order']} != {entry['order']}")
        if data["name"] != entry["lesson_name"]:
            errors.append(f"название «{data['name']}» != «{entry['lesson_name']}»")
        if data["slug"] != entry["slug"]:
            errors.append(f"slug «{data['slug']}» != «{entry['slug']}»")

    blocks = data["content"]
    if not isinstance(blocks, list) or len(blocks) < 30:
        errors.append(f"блоков мало: {len(blocks) if isinstance(blocks, list) else '—'}")
        return errors

    for index, block in enumerate(blocks):
        if not isinstance(block, dict) or "type" not in block:
            errors.append(f"блок {index}: нет поля type")
            continue
        kind = block["type"]
        if kind not in BLOCK_TYPES:
            errors.append(f"блок {index}: неизвестный тип {kind}")
            continue
        if kind == "heading":
            level = block.get("level", 2)
            if level not in (2, 3):
                errors.append(f"блок {index}: уровень заголовка {level}")
            if not str(block.get("content", "")).strip():
                errors.append(f"блок {index}: пустой заголовок")
        elif kind in {"text", "blockquote"}:
            if not str(block.get("content", "")).strip():
                errors.append(f"блок {index}: пустой текст")
        elif kind == "code":
            if not str(block.get("content", "")).strip():
                errors.append(f"блок {index}: пустой код")
            if not block.get("language"):
                errors.append(f"блок {index}: нет языка кода")
        elif kind == "list":
            items = block.get("items") or []
            if not items:
                errors.append(f"блок {index}: пустой список")
            if any(not str(item).strip() for item in items):
                errors.append(f"блок {index}: пустой пункт списка")
        elif kind == "table":
            headers = block.get("headers") or []
            rows = block.get("rows") or []
            if not headers or not rows:
                errors.append(f"блок {index}: пустая таблица")
            for row in rows:
                if len(row) != len(headers):
                    errors.append(
                        f"блок {index}: строка таблицы из {len(row)} ячеек "
                        f"при {len(headers)} заголовках"
                    )
                    break
        elif kind == "callout":
            style = block.get("style")
            if style not in CALLOUT_STYLES:
                errors.append(f"блок {index}: стиль врезки {style}")
            if not str(block.get("title", "")).strip():
                errors.append(f"блок {index}: врезка без заголовка")
            if not str(block.get("content", "")).strip():
                errors.append(f"блок {index}: врезка без текста")

    chars = text_volume(blocks)
    if chars < MIN_CHARS:
        errors.append(f"мало текста: {chars} знаков (нужно {MIN_CHARS}+)")
    elif chars > MAX_CHARS:
        warnings.append(f"много текста: {chars} знаков (желательно до {MAX_CHARS})")

    code_count = sum(1 for block in blocks if block.get("type") == "code")
    if code_count < MIN_CODE:
        errors.append(f"мало примеров кода: {code_count} (нужно {MIN_CODE}+)")
    elif code_count > MAX_CODE:
        warnings.append(f"много примеров кода: {code_count} (желательно до {MAX_CODE})")

    raw = json.dumps(data, ensure_ascii=False)
    if EMOJI_RE.search(raw):
        errors.append("в тексте есть эмодзи")
    if PLACEHOLDER_RE.search(raw):
        errors.append("в тексте есть заглушка (TODO/FIXME/...)")

    lowered = raw.lower()
    for phrase in STYLE_BAD_PHRASES:
        if phrase in lowered:
            warnings.append(f"стилевая фраза: «{phrase}»")

    headings = [
        block["content"] for block in blocks if block.get("type") == "heading"
    ]
    joined = " | ".join(headings).lower()
    for required in ("чему вы научитесь", "итог", "практика"):
        if required not in joined:
            warnings.append(f"нет раздела «{required}»")

    if not data.get("short_description", "").strip():
        errors.append("пустое short_description")
    if len(data.get("learning_objectives") or []) < 3:
        warnings.append("меньше трёх учебных целей")
    if not (data.get("hints") or []):
        warnings.append("нет подсказок (hints)")
    if not str(data.get("starter_code", "")).strip():
        warnings.append("нет starter_code")

    # Следы старого английского контента.
    for key in ("name_en", "short_description_en", "content_en"):
        if key in data and data[key]:
            warnings.append(f"заполнено английское поле {key}")

    return [f"ОШИБКА: {error}" for error in errors] + [
        f"предупреждение: {warning}" for warning in warnings
    ]


def main() -> None:
    args = sys.argv[1:]
    index = {entry["file"]: entry for entry in json.loads(INDEX_PATH.read_text("utf-8"))}

    paths: list[Path] = []
    if args and not args[0].startswith("--"):
        paths = [Path(raw).resolve() for raw in args]
    else:
        language = level = None
        if "--language" in args:
            language = args[args.index("--language") + 1]
        if "--level" in args:
            level = int(args[args.index("--level") + 1])
        for entry in index.values():
            if language and entry["language"] != language:
                continue
            if level and entry["level"] != level:
                continue
            path = BASE_DIR / entry["file"]
            if path.exists():
                paths.append(path)

    failed = 0
    checked = 0
    for path in sorted(paths):
        rel = str(path.relative_to(BASE_DIR)) if path.is_relative_to(BASE_DIR) else str(path)
        messages = check(path, index.get(rel))
        checked += 1
        problems = [m for m in messages if m.startswith("ОШИБКА")]
        if problems:
            failed += 1
            print(f"\n{rel}")
            for message in messages:
                print(f"  {message}")
        elif messages:
            print(f"\n{rel}")
            for message in messages:
                print(f"  {message}")

    print(f"\nПроверено файлов: {checked}, с ошибками: {failed}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
