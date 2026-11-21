"""Запуск агентов-авторов: один процесс на один урок.

Использование:
    python3 content_build/run_agents.py csharp 4
    python3 content_build/run_agents.py rust 3 --only 1_1,1_2

Каждый агент получает prompt из content_build/agent_prompt.md
с подставленными данными урока и пишет файл урока,
затем сам прогоняет валидатор и применяет урок к базе.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parent
LOG_DIR = BASE / "agent_logs"
PROMPT = BASE / "agent_prompt.md"

HELPERS = {
    "css": "css_kit",
    "cpp": "lesson_kit",
    "python": "lesson_kit",
    "csharp": "lesson_kit",
    "javascript": "lesson_kit",
    "rust": "lesson_kit",
}

PROGRAM_NAMES = {
    "csharp": {1: "C# — Начинающий", 2: "C# — Средний", 3: "C# — Продвинутый"},
    "javascript": {1: "JavaScript — Начинающий", 2: "JavaScript — Средний", 3: "JavaScript — Продвинутый"},
    "rust": {1: "Rust — Начинающий", 2: "Rust — Средний", 3: "Rust — Продвинутый"},
}


def plan(language: str) -> list[dict]:
    out = subprocess.run(
        [sys.executable, str(BASE / "plan_remaining.py"), language],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip().splitlines()
    return [json.loads(line) for line in out[1:]]


def build_prompt(entry: dict, helper: str) -> str:
    template = PROMPT.read_text(encoding="utf-8")
    program = PROGRAM_NAMES.get(entry["language"], {}).get(entry["level"], entry["language"])
    return (
        template.replace("{{LANGUAGE}}", entry["language"])
        .replace("{{HELPER}}", helper)
        .replace("{{PROGRAM}}", program)
        .replace("{{LEVEL}}", str(entry["level"]))
        .replace("{{ORDER}}", str(entry["order"]))
        .replace("{{LESSON_NAME}}", entry["lesson_name"])
        .replace("{{SLUG}}", entry["slug"])
        .replace("{{SOURCE}}", entry["source"])
        .replace("{{FILE}}", entry["file"])
        .replace("{{DIFFICULTY}}", entry["difficulty"])
        .replace("{{MINUTES}}", str(entry["estimated_minutes"]))
        .replace("{{XP}}", str(entry["xp_reward"]))
    )


def main() -> None:
    language = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))

    entries = plan(language)
    if only:
        entries = [e for e in entries if f"{e['level']}_{e['order']}" in only]
    entries = entries[:limit]

    LOG_DIR.mkdir(exist_ok=True)
    helper = HELPERS.get(language, "lesson_kit")
    for entry in entries:
        key = f"{entry['level']}_{entry['order']}"
        prompt = build_prompt(entry, helper)
        prompt_dir = LOG_DIR / "prompts"
        prompt_dir.mkdir(exist_ok=True)
        prompt_path = prompt_dir / f"{language}_{key}.md"
        prompt_path.write_text(prompt, encoding="utf-8")

        log_path = LOG_DIR / f"{language}_{key}.log"
        log = log_path.open("w", encoding="utf-8")
        cmd = [
            "opencode",
            "run",
            "-m",
            os.environ.get("KERNIFY_AGENT_MODEL", "starimg/deepseek-v4.1-flash-1017"),
            "--agent",
            "build",
            "--title",
            f"{language} {key}",
            prompt,
        ]
        proc = subprocess.Popen(cmd, cwd=str(REPO), stdout=log, stderr=subprocess.STDOUT)
        print(f"запущен {language} {key} → pid {proc.pid}, лог {log_path}")


if __name__ == "__main__":
    main()
