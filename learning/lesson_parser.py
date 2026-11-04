"""
Lesson text-file parser for RTK Django integration.

Parses lesson text files (UTF-8, Markdown-like) from all 6 programming
language courses into structured content blocks suitable for the
``Lesson.content`` JSONField.

Supported block types: ``heading``, ``text``, ``code``, ``list``,
``table``, ``callout``, ``blockquote``.

Special sections extracted into dedicated fields:
    * ``## Цели урока``              -> goals
    * ``## Практические задания``    -> practice_tasks
    * ``## Типичные ошибки новичков`` -> common_errors
    * ``## Полезные ресурсы``        -> resources
    * ``## Ключевые выводы``         -> key_takeaways
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Map fenced-code language aliases -> Prism.js language identifiers.
CODE_LANGUAGE_ALIASES = {
    'py': 'python',
    'python': 'python',
    'cpp': 'cpp',
    'c++': 'cpp',
    'cxx': 'cpp',
    'cc': 'cpp',
    'css': 'css',
    'rs': 'rust',
    'rust': 'rust',
    'js': 'javascript',
    'javascript': 'javascript',
    'ts': 'typescript',
    'typescript': 'typescript',
    'c#': 'csharp',
    'csharp': 'csharp',
    'cs': 'csharp',
    'bash': 'bash',
    'shell': 'bash',
    'sh': 'bash',
    'html': 'html',
    'htm': 'html',
    'xml': 'xml',
    'json': 'json',
    'sql': 'sql',
    'yaml': 'yaml',
    'yml': 'yaml',
    'toml': 'toml',
    'ini': 'ini',
    'text': 'text',
    'txt': 'text',
}

# Section title patterns (Russian) -> internal section key.
SECTION_PATTERNS = {
    r'цели\s+урока': 'goals',
    r'практические\s+задания': 'practice',
    r'типичные\s+ошибки': 'errors',
    r'полезные\s+ресурсы': 'resources',
    r'ключевые\s+выводы': 'takeaways',
}


def slugify(text: str) -> str:
    """Create a URL-friendly slug from a lesson title."""
    # Strip lesson-number prefix: "Урок 1.2:", "Урок 1:", etc.
    text = re.sub(r'^Урок\s*\d+(?:\.\d+)?\s*[:\—-]\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^Урок\s*\d+(?:\.\d+)?\s*', '', text, flags=re.IGNORECASE)
    # Transliterate Cyrillic -> Latin.
    trans = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
        'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'a', 'Б': 'b', 'В': 'v', 'Г': 'g', 'Д': 'd', 'Е': 'e', 'Ё': 'e',
        'Ж': 'zh', 'З': 'z', 'И': 'i', 'Й': 'y', 'К': 'k', 'Л': 'l', 'М': 'm',
        'Н': 'n', 'О': 'o', 'П': 'p', 'Р': 'r', 'С': 's', 'Т': 't', 'У': 'u',
        'Ф': 'f', 'Х': 'h', 'Ц': 'ts', 'Ч': 'ch', 'Ш': 'sh', 'Щ': 'sch', 'Ъ': '',
        'Ы': 'y', 'Ь': '', 'Э': 'e', 'Ю': 'yu', 'Я': 'ya',
    }
    text = ''.join(trans.get(c, c) for c in text)
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-') or 'lesson'


def normalize_code_language(raw: str) -> str:
    """Map a fenced-code language tag to a Prism identifier."""
    key = raw.strip().lower()
    return CODE_LANGUAGE_ALIASES.get(key, key or 'text')


def identify_section(title: str) -> str | None:
    """Return the internal section key for a heading title, or ``None``."""
    lowered = title.lower()
    for pattern, key in SECTION_PATTERNS.items():
        if re.search(pattern, lowered):
            return key
    return None


def inline_to_html(text: str) -> str:
    """Convert basic Markdown inline formatting to HTML."""
    # Code spans first (protect contents from other conversions).
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Bold.
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    # Italic.
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    return text


def parse_bullet_list(lines: list[str], start: int) -> tuple[list[str], int]:
    """Parse a list (- item or 1. item) starting at ``start``."""
    items: list[str] = []
    ordered = False
    i = start
    while i < len(lines):
        stripped = lines[i].strip()
        m = re.match(r'^(\d+\.\s|[-*]\s)(.+)$', stripped)
        if not m:
            break
        if m.group(1).endswith('.'):
            ordered = True
        items.append(m.group(2).strip())
        i += 1
    return items, i


def parse_table(lines: list[str], start: int) -> dict[str, Any] | None:
    """Parse a GitHub-flavoured table starting at ``start`` (the `|` line)."""
    if start >= len(lines) or not lines[start].strip().startswith('|'):
        return None
    headers: list[str] = []
    rows: list[list[str]] = []
    i = start
    while i < len(lines) and lines[i].strip().startswith('|'):
        cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
        # Skip the separator row (|---|---|).
        if all(set(c) <= set('-: ') and c.strip() for c in cells):
            i += 1
            continue
        if not headers:
            headers = cells
        else:
            rows.append(cells)
        i += 1
    return {
        'block': {
            'type': 'table',
            'headers': headers,
            'rows': rows,
        },
        'next_i': i,
    }


def parse_regular_section(lines: list[str], blocks: list[dict[str, Any]]) -> int:
    """Parse a regular content section (heading + body) into ``blocks``.

    Returns the index of the first unparsed line.
    """
    i = 0
    n = len(lines)
    # First non-empty line should be a heading.
    while i < n and not lines[i].strip():
        i += 1
    if i < n:
        m = re.match(r'^(#{2,4})\s+(.+)$', lines[i].strip())
        if m:
            level = len(m.group(1))
            blocks.append({
                'type': 'heading',
                'level': level,
                'content': m.group(2).strip(),
            })
            i += 1
    # Body: paragraphs, code blocks, lists, tables, blockquotes.
    while i < n:
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped == '---':
            i += 1
            continue
        # Nested heading -> end of section.
        if re.match(r'^#{1,4}\s+', stripped):
            break
        # Code block.
        mcode = re.match(r'^```(\w*)', stripped)
        if mcode:
            lang = normalize_code_language(mcode.group(1))
            code_lines: list[str] = []
            i += 1
            while i < n and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1  # skip closing ```
            blocks.append({
                'type': 'code',
                'language': lang,
                'content': '\n'.join(code_lines),
            })
            continue
        # Table.
        if stripped.startswith('|'):
            tbl = parse_table(lines, i)
            if tbl:
                blocks.append(tbl['block'])
                i = tbl['next_i']
                continue
        # Blockquote.
        if stripped.startswith('> '):
            bq: list[str] = []
            while i < n and lines[i].strip().startswith('> '):
                bq.append(lines[i].strip()[2:].strip())
                i += 1
            blocks.append({
                'type': 'blockquote',
                'content': '\n'.join(bq),
            })
            continue
        # List.
        if re.match(r'^(\d+\.\s|[-*]\s)', stripped):
            items, i = parse_bullet_list(lines, i)
            blocks.append({
                'type': 'list',
                'items': items,
                'ordered': bool(re.match(r'^\d+\.\s', lines[i - len(items)].strip()) if i - len(items) >= 0 else False),
            })
            continue
        # Paragraph.
        para: list[str] = [stripped]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt or nxt == '---' or re.match(r'^#{1,4}\s+', nxt)
                    or nxt.startswith('```') or nxt.startswith('|')
                    or nxt.startswith('> ') or re.match(r'^(\d+\.\s|[-*]\s)', nxt)):
                break
            para.append(nxt)
            i += 1
        blocks.append({
            'type': 'text',
            'content': inline_to_html(' '.join(para)),
        })
    return i


def parse_lesson_file(file_path: str | Path) -> dict[str, Any]:
    """Parse a single lesson text file into a structured dict.

    Returns a dict with keys:
        title, slug, short_description, goals, content_blocks,
        practice_tasks, common_errors, resources, key_takeaways,
        estimated_minutes
    """
    path = Path(file_path)
    raw = path.read_text(encoding='utf-8')
    # Split into chunks separated by horizontal rules.
    chunks = re.split(r'\n\s*---\s*\n', raw)

    result: dict[str, Any] = {
        'title': '',
        'slug': '',
        'short_description': '',
        'goals': [],
        'content_blocks': [],
        'practice_tasks': [],
        'common_errors': [],
        'resources': [],
        'key_takeaways': [],
        'estimated_minutes': 15,
    }

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.split('\n')

        # Collect all heading positions within this chunk so we can process
        # multiple sections that may sit between two '---' separators
        # (e.g. title + "## Цели урока" in the first chunk).
        headings: list[tuple[int, int, str]] = []  # (line_index, level, title)
        for idx, line in enumerate(lines):
            stripped = line.strip()
            m1 = re.match(r'^#\s+(.+)$', stripped)
            m2 = re.match(r'^##\s+(.+)$', stripped)
            m3 = re.match(r'^###\s+(.+)$', stripped)
            m4 = re.match(r'^####\s+(.+)$', stripped)
            if m1:
                headings.append((idx, 1, m1.group(1).strip()))
            elif m2:
                headings.append((idx, 2, m2.group(1).strip()))
            elif m3:
                headings.append((idx, 3, m3.group(1).strip()))
            elif m4:
                headings.append((idx, 4, m4.group(1).strip()))

        if not headings:
            continue

        # Process each heading together with the body lines that follow it
        # (up to the next heading or end of chunk).
        for h_idx, (pos, level, title) in enumerate(headings):
            body_start = pos + 1
            body_end = headings[h_idx + 1][0] if h_idx + 1 < len(headings) else len(lines)
            body_lines = lines[body_start:body_end]

            if level == 1 and not result['title']:
                # Lesson title: # Урок N[.N]: ...
                result['title'] = title
                result['slug'] = slugify(title)
                if '—' in title:
                    result['short_description'] = title.split('—', 1)[1].strip()
                elif '-' in title:
                    result['short_description'] = title.split('-', 1)[1].strip()
                # Body of the title chunk (if any) becomes intro text.
                intro = '\n'.join(body_lines).strip()
                if intro:
                    result['content_blocks'].append({
                        'type': 'text',
                        'content': inline_to_html(intro),
                    })
                continue

            if level == 2:
                section_key = identify_section(title)
                if section_key == 'goals':
                    goals, _ = parse_bullet_list(body_lines, 0)
                    result['goals'] = goals
                    result['content_blocks'].append({
                        'type': 'heading', 'level': 2, 'content': title,
                    })
                    if goals:
                        result['content_blocks'].append({
                            'type': 'list', 'items': goals, 'ordered': False,
                        })
                elif section_key == 'practice':
                    tasks, _ = parse_bullet_list(body_lines, 0)
                    result['practice_tasks'] = tasks
                    result['content_blocks'].append({
                        'type': 'heading', 'level': 2, 'content': title,
                    })
                    if tasks:
                        result['content_blocks'].append({
                            'type': 'list', 'items': tasks, 'ordered': True,
                        })
                elif section_key == 'resources':
                    resources, _ = parse_bullet_list(body_lines, 0)
                    result['resources'] = resources
                    result['content_blocks'].append({
                        'type': 'heading', 'level': 2, 'content': title,
                    })
                    if resources:
                        result['content_blocks'].append({
                            'type': 'list', 'items': resources, 'ordered': False,
                        })
                elif section_key == 'takeaways':
                    takeaways, _ = parse_bullet_list(body_lines, 0)
                    result['key_takeaways'] = takeaways
                    result['content_blocks'].append({
                        'type': 'heading', 'level': 2, 'content': title,
                    })
                    if takeaways:
                        result['content_blocks'].append({
                            'type': 'list', 'items': takeaways, 'ordered': False,
                        })
                elif section_key == 'errors':
                    errors: list[dict[str, str]] = []
                    ii = 0
                    while ii < len(body_lines):
                        if body_lines[ii].strip().startswith('|'):
                            tbl = parse_table(body_lines, ii)
                            if tbl:
                                blk = tbl['block']
                                for row in blk['rows']:
                                    if len(row) >= 2:
                                        errors.append({
                                            'mistake': row[0],
                                            'correct': row[1],
                                        })
                                ii = tbl['next_i']
                                continue
                        ii += 1
                    result['common_errors'] = errors
                    result['content_blocks'].append({
                        'type': 'heading', 'level': 2, 'content': title,
                    })
                    if errors:
                        result['content_blocks'].append({
                            'type': 'table',
                            'headers': ['Ошибка', 'Правильно'],
                            'rows': [[e['mistake'], e['correct']] for e in errors],
                        })
                else:
                    # Regular numbered/unnumbered content section.
                    section_lines = ['## ' + title] + body_lines
                    parse_regular_section(section_lines, result['content_blocks'])
                continue

            # Level 3/4 heading inside content -> parse as a regular section.
            section_lines = ('#' * level) + ' ' + title
            parse_regular_section([section_lines] + body_lines, result['content_blocks'])

    return result


def lesson_summary(parsed: dict[str, Any]) -> dict[str, Any]:
    """Return a lightweight summary of a parsed lesson (for verification)."""
    return {
        'title': parsed.get('title'),
        'slug': parsed.get('slug'),
        'blocks': len(parsed.get('content_blocks', [])),
        'goals': len(parsed.get('goals', [])),
        'practice_tasks': len(parsed.get('practice_tasks', [])),
        'resources': len(parsed.get('resources', [])),
        'common_errors': len(parsed.get('common_errors', [])),
        'key_takeaways': len(parsed.get('key_takeaways', [])),
        'has_code': any(b.get('type') == 'code' for b in parsed.get('content_blocks', [])),
    }
