#!/usr/bin/env python3
"""Extract all translatable strings from Django templates and Python files."""
import re
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
TEMPLATES_DIR = PROJECT_DIR / "templates"

# Collect all unique translatable strings
strings = set()

# Pattern for {% trans "..." %} and {% trans '...' %}
trans_pattern = re.compile(r'\{%\s+trans\s+["\'](.*?)["\']\s+%\}')

# Pattern for {% blocktrans %}...{% endblocktrans %}
blocktrans_pattern = re.compile(
    r'\{%\s+blocktrans\b[^%]*%\}(.*?)\{%\s+endblocktrans\s+%\}',
    re.DOTALL
)

# Pattern for _("...") and _('...') in Python files
gettext_pattern = re.compile(r'_\(["\'](.*?)["\']\)')

# Pattern for gettext_lazy("...") and gettext_lazy('...')
gettext_lazy_pattern = re.compile(r'gettext_lazy\(["\'](.*?)["\']\)')

# Pattern for ngettext_lazy
ngettext_pattern = re.compile(r'ngettext_lazy\(["\'](.*?)["\']\s*,\s*["\'](.*?)["\']\)')

# Walk through all template files
for html_file in TEMPLATES_DIR.rglob("*.html"):
    content = html_file.read_text(encoding="utf-8")

    for m in trans_pattern.finditer(content):
        strings.add(m.group(1))

    for m in blocktrans_pattern.finditer(content):
        # blocktrans content may have multiple lines, extract text between tags
        block_content = m.group(1)
        # Find individual trans-like strings within blocktrans
        for inner in trans_pattern.finditer(block_content):
            strings.add(inner.group(1))

# Walk through all Python files
for py_file in PROJECT_DIR.rglob("*.py"):
    # Skip migrations, venv, etc.
    if any(part in py_file.parts for part in ['migrations', 'venv', '.venv', '__pycache__', 'node_modules']):
        continue
    content = py_file.read_text(encoding="utf-8")

    for m in gettext_pattern.finditer(content):
        strings.add(m.group(1))

    for m in gettext_lazy_pattern.finditer(content):
        strings.add(m.group(1))

    for m in ngettext_pattern.finditer(content):
        strings.add(m.group(1))
        strings.add(m.group(2))

# Sort and output
sorted_strings = sorted(strings)
print(f"Found {len(sorted_strings)} unique translatable strings:\n")
for s in sorted_strings:
    print(f'msgid "{s}"')
    print(f'msgstr ""')
    print()
