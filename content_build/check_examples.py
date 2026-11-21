"""Проверить примеры кода из уроков.

Запускает блоки кода в безопасном режиме (таймаут, временная папка) и
сообщает, какие примеры падают. Сравнение вывода нестрогое: показывается
фактический вывод рядом с ожидаемым блоком.

Использование:
    python content_build/check_examples.py --language python --level 1
    python content_build/check_examples.py path/to/lesson.py
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = Path(__file__).resolve().parent / "lessons_index.json"

SKIP_MARKERS = (
    "input(",
    "open(",
    "requests.",
    "asyncio.run",
    "while True",
    "time.sleep",
    "os.remove",
    "shutil.",
    "subprocess.",
    "socket.",
    "https://",
    "http://",
)


def load_lesson(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location("lesson_payload", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Не удалось загрузить файл: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LESSON


def runner_for(language: str) -> list[str] | None:
    language = language.lower()
    if language in {"python", "py"}:
        return [sys.executable]
    if language in {"javascript", "js"}:
        node = shutil.which("node")
        return [node] if node else None
    if language in {"bash", "shell", "sh"}:
        return ["bash"]
    return None


def run_snippet(command: list[str], source: str, suffix: str) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / f"snippet{suffix}"
        script.write_text(source, encoding="utf-8")
        try:
            result = subprocess.run(
                command + [str(script)],
                capture_output=True,
                text=True,
                timeout=8,
                cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return 124, "таймаут выполнения"
        return result.returncode, (result.stdout + result.stderr)[-2500:]


def check_lesson(path: Path) -> list[str]:
    data = load_lesson(path)
    blocks = data["content"]
    language = data["language"]
    problems: list[str] = []

    for index, block in enumerate(blocks):
        if block.get("type") != "code":
            continue
        block_language = str(block.get("language", "")).lower()
        if language == "python":
            if block_language not in {"python", "py"}:
                continue
        elif language == "javascript":
            if block_language not in {"javascript", "js"}:
                continue
        else:
            continue

        source = block["content"]
        if any(marker in source for marker in SKIP_MARKERS):
            continue
        if "# пропуск" in source or "# skip" in source:
            continue

        command = runner_for(block_language)
        if command is None:
            continue
        suffix = ".py" if block_language in {"python", "py"} else ".js"
        code, output = run_snippet(command, source, suffix)
        if code != 0:
            problems.append(
                f"блок {index}: код {code}\n--- код ---\n{source}\n--- вывод ---\n{output}"
            )

    return problems


def main() -> None:
    args = sys.argv[1:]
    paths: list[Path] = []
    if args and not args[0].startswith("--"):
        paths = [Path(raw).resolve() for raw in args]
    else:
        language = level = None
        if "--language" in args:
            language = args[args.index("--language") + 1]
        if "--level" in args:
            level = int(args[args.index("--level") + 1])
        for entry in json.loads(INDEX_PATH.read_text("utf-8")):
            if language and entry["language"] != language:
                continue
            if level and entry["level"] != level:
                continue
            path = BASE_DIR / entry["file"]
            if path.exists():
                paths.append(path)

    import os

    os.environ["PYTHONIOENCODING"] = "utf-8"

    total_problems = 0
    for path in sorted(paths):
        problems = check_lesson(path)
        if problems:
            total_problems += len(problems)
            print(f"\n=== {path.name}: {len(problems)} проблем(ы)")
            for problem in problems[:5]:
                print(problem)

    print(f"\nФайлов: {len(paths)}, проблемных примеров: {total_problems}")


if __name__ == "__main__":
    main()
