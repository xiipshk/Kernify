#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Translate lesson content blocks back to Russian (base fields)."""

import os
import re
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from learning.models import Lesson
from translation_engine import Translator

CYR = re.compile(r'[А-Яа-яЁё]')


def main():
    # Collect all English content blocks
    blocks_to_translate = []
    block_refs = []

    for l in Lesson.objects.select_related('topic__program__language'):
        for bi, b in enumerate(l.content):
            if not isinstance(b, dict):
                continue
            if b.get('type') in ('heading', 'text', 'blockquote'):
                val = b.get('content', '')
                if val and not CYR.search(val) and len(val) > 5:
                    blocks_to_translate.append(val)
                    block_refs.append((l, bi, 'content'))
            elif b.get('type') == 'list':
                for ii, item in enumerate(b.get('items') or []):
                    if isinstance(item, str) and not CYR.search(item) and len(item) > 5:
                        blocks_to_translate.append(item)
                        block_refs.append((l, bi, ('items', ii)))
            elif b.get('type') == 'table':
                for key in ('headers',):
                    for ii, cell in enumerate(b.get(key) or []):
                        if isinstance(cell, str) and not CYR.search(cell) and len(cell) > 5:
                            blocks_to_translate.append(cell)
                            block_refs.append((l, bi, (key, ii)))

    print(f'Found {len(blocks_to_translate)} English blocks')

    # Deduplicate
    unique_map = {}
    for i, text in enumerate(blocks_to_translate):
        if text not in unique_map:
            unique_map[text] = []
        unique_map[text].append(block_refs[i])

    unique_texts = list(unique_map.keys())
    print(f'Unique texts: {len(unique_texts)}')

    # Translate
    tr = Translator('en', 'ru')
    translated = tr.translate_many(unique_texts)
    mapping = dict(zip(unique_texts, translated))
    print(f'Translated. Requests: {tr.requests}, Cache: {tr.hits}')

    # Apply back
    updated = 0
    for l in Lesson.objects.select_related('topic__program__language'):
        content = l.content
        changed = False
        for bi, b in enumerate(content):
            if not isinstance(b, dict):
                continue
            if b.get('type') in ('heading', 'text', 'blockquote'):
                val = b.get('content', '')
                if val in mapping:
                    content[bi]['content'] = mapping[val]
                    changed = True
            elif b.get('type') == 'list':
                items = b.get('items') or []
                for ii, item in enumerate(items):
                    if isinstance(item, str) and item in mapping:
                        items[ii] = mapping[item]
                        changed = True
            elif b.get('type') == 'table':
                for key in ('headers',):
                    values = b.get(key) or []
                    for ii, cell in enumerate(values):
                        if isinstance(cell, str) and cell in mapping:
                            values[ii] = mapping[cell]
                            changed = True
        if changed:
            l.content = content
            l.save(update_fields=['content', 'updated_at'])
            updated += 1

    print(f'Updated {updated} lessons')


if __name__ == '__main__':
    main()