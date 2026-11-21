"""Добавление блоков в урок (text и код)."""

from __future__ import annotations

import sys
from textwrap import dedent

WIDTH = 74
NL = chr(92) + "n"  # последовательность \n для исходника


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


def render_code(body: str) -> str:
    body = dedent(body).strip("\n")
    rendered = "\n".join(("            " + line) if line else "" for line in body.split("\n"))
    return (
        "        code(\n"
        '            """\n'
        + rendered
        + "\n"
        '            """\n'
        "        ),\n"
    )


def main() -> None:
    path = sys.argv[1]
    args = sys.argv[2:]
    if len(args) % 3:
        raise SystemExit("нужны тройки: якорь, вид, содержимое")

    src = open(path, encoding="utf-8").read()
    for anchor, kind, body in zip(*[iter(args)] * 3):
        if src.count(anchor) != 1:
            raise SystemExit(f"якорь найден {src.count(anchor)} раз")
        block = render_text(body) if kind == "text" else render_code(body)
        idx = src.index(anchor)
        start = src.rfind("\n", 0, idx) + 1
        src = src[:start] + block + src[start:]

    open(path, "w", encoding="utf-8").write(src)
    print(f"готово: {path}, размер {len(src)}")


if __name__ == "__main__":
    main()
