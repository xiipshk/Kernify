"""
Custom template filters for programming language display names and colors.
"""

import html
import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

INLINE_CODE_RE = re.compile(r'`([^`\n]+)`')
BOLD_RE = re.compile(r'\*\*(.+?)\*\*', re.S)
ITALIC_RE = re.compile(r'(^|[\s(])\*([^*\n]+)\*(?=[\s).,!?:;]|$)')
LINK_RE = re.compile(r'\[([^\]]+)\]\((https?://[^)\s]+)\)')

# Tags that are allowed to stay as real HTML in lesson prose. Everything else
# that looks like `<...>` is escaped, so text such as `<class 'int'>` is shown
# to the reader instead of being swallowed by the browser.
ALLOWED_TAG_RE = re.compile(
    r'</?(?:a|b|i|em|strong|code|pre|br|p|div|span|ul|ol|li|h[1-6]|blockquote|'
    r'table|thead|tbody|tr|th|td|img|hr|small|mark|sup|sub|kbd|figure|figcaption)\b[^>]*>',
    re.I,
)

# Block-level HTML means the author wrote raw HTML on purpose: leave it alone.
BLOCK_HTML_RE = re.compile(r'<(p|div|ul|ol|table|blockquote|pre|figure|h[1-6])\b', re.I)

PLACEHOLDER = '\x00{}\x00'


def _escape_unknown_tags(text: str) -> str:
    """Escape `<`/`>` that do not belong to a whitelisted HTML tag."""
    text = html.unescape(str(text))
    kept = []

    def _stash(match):
        kept.append(match.group(0))
        return PLACEHOLDER.format(len(kept) - 1)

    text = ALLOWED_TAG_RE.sub(_stash, text)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return re.sub(r'\x00(\d+)\x00', lambda m: kept[int(m.group(1))], text)


def _md_inline_html(text: str) -> str:
    """Convert inline Markdown (code, bold, italic, links) in an escaped line."""
    codes = []

    def _stash_code(match):
        codes.append(match.group(1))
        return PLACEHOLDER.format(len(codes) - 1)

    text = INLINE_CODE_RE.sub(_stash_code, text)
    text = BOLD_RE.sub(lambda m: f'<strong>{m.group(1)}</strong>', text)
    text = ITALIC_RE.sub(lambda m: f'{m.group(1)}<em>{m.group(2)}</em>', text)
    text = LINK_RE.sub(
        lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>',
        text,
    )
    # Restore inline code last so markdown inside `code` stays literal.
    return re.sub(
        r'\x00(\d+)\x00',
        lambda m: f'<code>{codes[int(m.group(1))]}</code>',
        text,
    )


@register.filter
def md_inline(value):
    """Render inline Markdown: ``code``, **bold**, *italic* and [links](url)."""
    if value is None:
        return ''
    return mark_safe(_md_inline_html(_escape_unknown_tags(value)))


@register.filter
def rich_text(value):
    """Render a prose block: paragraphs, line breaks and inline Markdown.

    Raw HTML is preserved when the block clearly contains block-level markup
    (for example an authored ``<div>`` or ``<table>``). Otherwise the text is
    escaped and converted to paragraphs, which keeps characters like ``<`` in
    code snippets visible.
    """
    if value is None:
        return ''

    text = str(value)
    if not text.strip():
        return ''

    if BLOCK_HTML_RE.search(text) and '```' not in text:
        return mark_safe(text)

    paragraphs = re.split(r'\n\s*\n', text.strip())
    rendered = []
    for paragraph in paragraphs:
        lines = paragraph.split('\n')
        escaped_lines = [_md_inline_html(_escape_unknown_tags(line)) for line in lines]
        rendered.append('<p>' + '<br>'.join(escaped_lines) + '</p>')
    return mark_safe(''.join(rendered))

# Friendly display names for language slugs
LANGUAGE_NAMES = {
    'bash': 'Bash',
    'shell': 'Bash',
    'sh': 'Bash',
    'python': 'Python',
    'javascript': 'JavaScript',
    'js': 'JavaScript',
    'typescript': 'TypeScript',
    'ts': 'TypeScript',
    'cpp': 'C++',
    'c++': 'C++',
    'cxx': 'C++',
    'cc': 'C++',
    'csharp': 'C#',
    'c#': 'C#',
    'cs': 'C#',
    'rust': 'Rust',
    'rs': 'Rust',
    'css': 'CSS',
    'html': 'HTML',
    'htm': 'HTML',
    'sql': 'SQL',
    'json': 'JSON',
    'xml': 'XML',
    'yaml': 'YAML',
    'yml': 'YAML',
    'toml': 'TOML',
    'ini': 'INI',
    'text': 'Text',
    'txt': 'Text',
}

# Accent colors for each language (used for code block borders and labels)
LANGUAGE_COLORS = {
    'bash': '#4EAA25',
    'shell': '#4EAA25',
    'sh': '#4EAA25',
    'python': '#3776AB',
    'javascript': '#F7DF1E',
    'js': '#F7DF1E',
    'typescript': '#3178C6',
    'ts': '#3178C6',
    'cpp': '#00599C',
    'c++': '#00599C',
    'cxx': '#00599C',
    'cc': '#00599C',
    'csharp': '#68217A',
    'c#': '#68217A',
    'cs': '#68217A',
    'rust': '#DEA584',
    'rs': '#DEA584',
    'css': '#1572B6',
    'html': '#E34F26',
    'htm': '#E34F26',
    'sql': '#E38C00',
    'json': '#292929',
    'xml': '#0060AC',
    'yaml': '#00395E',
    'yml': '#00395E',
    'toml': '#6D8086',
    'ini': '#00395E',
}


@register.filter
def language_name(value):
    """Convert a language slug to a friendly display name."""
    if not value:
        return 'Python'
    return LANGUAGE_NAMES.get(str(value).lower(), str(value).title())


@register.filter
def language_color(value):
    """Convert a language slug to its accent color hex code."""
    if not value:
        return '#6366f1'
    return LANGUAGE_COLORS.get(str(value).lower(), '#6366f1')
