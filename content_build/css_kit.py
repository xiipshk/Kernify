"""Общие помощники для уроков CSS."""

from __future__ import annotations

from textwrap import dedent

WIDTH = 74


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


def css(source: str) -> dict:
    return {"type": "code", "language": "css", "content": code(source)}


def html(source: str) -> dict:
    return {"type": "code", "language": "html", "content": code(source)}


def result(source: str) -> dict:
    return {"type": "code", "language": "text", "content": code(source)}
