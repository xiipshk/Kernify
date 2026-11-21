# -*- coding: utf-8 -*-
"""Общий применитель контента к пустым code-блокам фикстур.

Используется частичными скриптами fill_part_*.py:

    from fill_common import apply_fill
    FILL = { 'python/01.json': { 38: "..." }, ... }
    apply_fill(FILL)

Каждый блок проверяется: тип code, язык совпадает с ожидаемым (не проверяем —
просто code), content пуст. Уже заполненные блоки пропускаются, поэтому
повторный запуск безопасен.
"""

import json
import os
import sys
import textwrap

BASE = 'fixtures/lessons'


def apply_fill(fill, allow_overwrite=False, languages=None):
    languages = languages or {}
    filled = 0
    skipped = []
    errors = []
    for rel, blocks_map in fill.items():
        path = os.path.join(BASE, rel)
        if not os.path.exists(path):
            errors.append(f'{rel}: файл не найден')
            continue
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            errors.append(f'{rel}: битый JSON ({exc})')
            continue
        blocks = data.get('content_blocks', [])
        for idx, content in blocks_map.items():
            if idx >= len(blocks):
                errors.append(f'{rel}#{idx}: индекс вне диапазона ({len(blocks)})')
                continue
            block = blocks[idx]
            if block.get('type') != 'code':
                errors.append(f'{rel}#{idx}: тип {block.get("type")!r}, ожидался code')
                continue
            if str(block.get('content', '') or '').strip() and not allow_overwrite:
                skipped.append(f'{rel}#{idx}')
                continue
            block['content'] = textwrap.dedent(content).strip('\n')
            new_lang = languages.get((rel, idx))
            if new_lang:
                block['language'] = new_lang
            filled += 1
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')

    print(f'Заполнено блоков: {filled}')
    if skipped:
        print(f'Пропущено уже заполненных: {len(skipped)}')
    if errors:
        print('Ошибки:')
        for e in errors:
            print('  -', e)
        sys.exit(1)
