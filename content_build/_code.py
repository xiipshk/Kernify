"""Добавление блоков кода в урок перед указанным якорем."""

from __future__ import annotations

import sys
from textwrap import dedent

NL = chr(92) + "n"


def render(body: str) -> str:
    body = dedent(body).strip("\n")
    rendered = "\n".join(("            " + line) if line else "" for line in body.split("\n"))
    head = "        code(" + chr(10) + '            """' + chr(10)
    tail = chr(10) + '            """' + chr(10) + "        )," + chr(10)
    return head + rendered + tail


def main() -> None:
    path = sys.argv[1]
    pairs = sys.argv[2:]
    if len(pairs) % 2:
        raise SystemExit("нужны пары: якорь, код")
    src = open(path, encoding="utf-8").read()
    for anchor, body in zip(pairs[0::2], pairs[1::2]):
        if src.count(anchor) != 1:
            raise SystemExit(f"якорь найден {src.count(anchor)} раз: {anchor[:40]!r}")
        block = render(body)
        idx = src.index(anchor)
        start = src.rfind("\n", 0, idx) + 1
        src = src[:start] + block + src[start:]
    open(path, "w", encoding="utf-8").write(src)
    print(f"готово: {path}, размер {len(src)}")


if __name__ == "__main__":
    main()
