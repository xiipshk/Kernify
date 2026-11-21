"""Общие помощники для файлов уроков."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


def text(content: str) -> dict:
    return {"type": "text", "content": content.strip()}


def heading(content: str, level: int = 2) -> dict:
    return {"type": "heading", "level": level, "content": content.strip()}


def bullets(*items: str, ordered: bool = False) -> dict:
    return {"type": "list", "ordered": ordered, "items": list(items)}


def numbered(*items: str) -> dict:
    return bullets(*items, ordered=True)


def table(headers: list[str], rows: list[list[str]]) -> dict:
    return {"type": "table", "headers": headers, "rows": rows}


def callout(style: str, title: str, content: str) -> dict:
    return {"type": "callout", "style": style, "title": title, "content": content}


def example(language: str, source: str) -> dict:
    return {"type": "code", "language": language, "content": code(source)}


# Готовые блоки, повторяющиеся в каждом уроке.

def check_yourself(questions: tuple[str, ...], answers: tuple[str, ...]) -> list[dict]:
    assert len(questions) == len(answers)
    return [
        heading("Проверьте себя"),
        numbered(*questions),
        heading("Ответы", 3),
        numbered(*answers),
    ]


def outro(
    summary: tuple[str, ...],
    next_text: str,
    resources: tuple[str, ...],
) -> list[dict]:
    return [
        heading("Итоги"),
        bullets(*summary),
        heading("Что дальше"),
        text(next_text),
        heading("Если хотите углубиться"),
        bullets(*resources),
    ]


def signature(name: str, level: int, order: int, title: str, slug: str) -> dict:
    """Каркас урока в формате эталонных уроков."""
    return {
        "language": "python",
        "program_order": level,
        "topic_order": order,
        "name": f"{level}.{order}. {title}",
        "slug": slug,
    }
