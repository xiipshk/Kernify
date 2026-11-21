"""Быстрая накачка объёма урока CSS.

Добавляет блоки text перед указанными заголовками из встроенного словаря,
где ключ — начало текста заголовка.
"""

from __future__ import annotations

import sys

WIDTH = 74
NL = chr(92) + "n"


def render_text(body: str) -> str:
    body = " ".join(body.split())
    lines: list[str] = []
    current = ""
    for word in body.split(" "):
        cand = (current + " " + word).strip()
        if len(cand) > WIDTH:
            lines.append(current)
            current = word
        else:
            current = cand
    lines.append(current)

    parts = []
    last = len(lines) - 1
    for i, line in enumerate(lines):
        esc = line.replace("\\", "\\\\").replace('"', '\\"')
        suffix = NL if i < last else ""
        parts.append('            "' + esc + suffix + '"')
    return "        text(\n" + "\n".join(parts) + ",\n        ),\n"


def main() -> None:
    path = sys.argv[1]
    pairs = sys.argv[2:]
    if len(pairs) % 2:
        raise SystemExit("нужны пары: якорь, текст")

    src = open(path, encoding="utf-8").read()
    for anchor, body in zip(pairs[0::2], pairs[1::2]):
        if src.count(anchor) != 1:
            raise SystemExit(f"якорь найден {src.count(anchor)} раз: {anchor[:50]!r}")
        block = render_text(body)
        idx = src.index(anchor)
        start = src.rfind("\n", 0, idx) + 1
        src = src[:start] + block + src[start:]

    open(path, "w", encoding="utf-8").write(src)
    print(f"готово: {path}, размер {len(src)}")


if __name__ == "__main__":
    main()
