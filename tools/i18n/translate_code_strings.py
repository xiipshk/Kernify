#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Translate Russian string literals in code blocks to English."""

import os
import re
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from learning.models import Lesson
from translation_engine import Translator

CYR = re.compile(r'[А-Яа-яЁё]')
STRING_RE = re.compile(r'(["\'])([^"\']*[А-Яа-яЁё][^"\']*)\1')


def translate_strings_in_code(code: str, tr: Translator) -> str:
    def repl(m):
        quote, content = m.groups()
        if CYR.search(content):
            translated = tr.translate(content)
            return f'{quote}{translated}{quote}'
        return m.group(0)

    return STRING_RE.sub(repl, code)


def main():
    tr = Translator('ru', 'en')
    updated = 0

    for l in Lesson.objects.all():
        content_en = l.content_en
        changed = False
        for bi, b in enumerate(content_en):
            if isinstance(b, dict) and b.get('type') == 'code':
                new_code = translate_strings_in_code(b.get('content', ''), tr)
                if new_code != b.get('content', ''):
                    content_en[bi]['content'] = new_code
                    changed = True
        if changed:
            l.content_en = content_en
            l.save(update_fields=['content_en', 'updated_at'])
            updated += 1

    print(f'Updated {updated} lessons')
    print(f'Requests: {tr.requests}, Cache: {tr.hits}')


if __name__ == '__main__':
    main()