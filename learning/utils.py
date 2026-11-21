"""Helpers shared by lesson import and admin tooling."""

import re

# Characters that are meaningful in URLs (or break Django's slug converter)
# but do appear in lesson titles such as "C#", "C++" or "Result, Option, ?".
SLUG_REPLACEMENTS = {
    '#': '-sharp',
    '+': '-plus',
    '&': '-and',
}

# Allowed slug characters: ASCII word chars, hyphen and the Cyrillic range
# used by the custom `unicode_slug` URL converter.
SLUG_ALLOWED_RE = re.compile(r'[^\w\u0400-\u04FF-]+')
SLUG_DASHES_RE = re.compile(r'-{2,}')


def make_url_slug(value, fallback='lesson'):
    """Normalize a title or slug so it survives a URL path.

    ``C#`` becomes ``c-sharp``, ``C++`` becomes ``c-plus-plus`` and commas,
    question marks and other unsafe characters collapse into dashes.
    """
    text = str(value or '').strip()
    for char, replacement in SLUG_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    text = SLUG_ALLOWED_RE.sub('-', text)
    text = SLUG_DASHES_RE.sub('-', text).strip('-')
    return text.lower() or fallback
