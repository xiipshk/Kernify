# -*- coding: utf-8 -*-
"""Генерация английского контента: переводит все поля в *_en.

Считывает локализованные русские фикстуры, переводит:
  - lesson.name -> name_en
  - lesson.short_description -> short_description_en
  - lesson.content -> content_en
  - topic.name -> name_en
  - topic.description -> description_en
  - program.name -> name_en
  - program.description -> description_en

и записывает обратно в фикстуры (для переимпорта) или в БД напрямую.

Запуск::

    python localize_en.py            # отчёт
    python localize_en.py --apply    # записать в фикстуры
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

from translation_engine import Translator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(BASE_DIR, 'fixtures', 'lessons')

CYR = re.compile(r'[А-Яа-яЁё]')
CYR_WORD_RE = re.compile(r'[А-Яа-яЁё][А-Яа-яЁё\'\-]{1,}')
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]{1,}")

URL_RE = re.compile(r'https?://[^\s<>")\]]+')
TAG_RE = re.compile(r'<[^>]+>')

RESOURCE_RE = re.compile(r'^\s*\*\*[^*]+\*\*\s*[—–-]\s*(https?://|YouTube|$)', re.I)

KEYWORDS = {
    'if', 'else', 'elif', 'switch', 'case', 'default', 'while', 'do', 'for',
    'break', 'continue', 'return', 'goto', 'def', 'class', 'try', 'except',
    'finally', 'raise', 'yield', 'async', 'await', 'import', 'from', 'lambda',
    'with', 'as', 'pass', 'global', 'nonlocal', 'assert', 'del', 'in', 'is',
    'not', 'and', 'or', 'none', 'true', 'false', 'struct', 'enum', 'impl',
    'trait', 'fn', 'let', 'mut', 'pub', 'use', 'mod', 'match', 'unsafe',
    'where', 'void', 'int', 'char', 'float', 'double', 'bool', 'string',
    'public', 'private', 'protected', 'static', 'const', 'readonly', 'var',
    'new', 'override', 'virtual', 'abstract', 'sealed', 'partial', 'using',
    'namespace', 'get', 'set', 'record', 'dynamic', 'object', 'params', 'ref',
    'out', 'sizeof', 'typeof', 'nameof', 'foreach', 'throw', 'catch',
    'interface', 'extends', 'implements', 'function', 'this', 'super', 'null',
    'undefined', 'instanceof', 'delete', 'export', 'constructor', 'prototype',
    'extern', 'inline', 'register', 'volatile', 'signed', 'unsigned', 'long',
    'short', 'template', 'typename', 'operator', 'friend', 'explicit',
    'mutable', 'noexcept', 'constexpr', 'consteval', 'decltype', 'auto',
    'static_cast', 'dynamic_cast', 'const_cast', 'reinterpret_cast',
    'sizeof', 'alignof', 'co_await', 'co_yield', 'co_return', 'module',
    'export', 'defer', 'go', 'chan', 'select', 'range', 'fallthrough',
}


def looks_like_keyword_list(text: str) -> bool:
    parts = [p.strip() for p in re.split(r'[,/|]', text) if p.strip()]
    if len(parts) < 2:
        return False
    for part in parts:
        words = re.findall(r'[A-Za-z_][A-Za-z0-9_]*', part)
        if not words:
            return False
        if any(w.lower() not in KEYWORDS for w in words):
            return False
    return True


def strip_markup(text: str) -> str:
    text = TAG_RE.sub(' ', text)
    text = URL_RE.sub(' ', text)
    return text.replace('`', ' ')


def is_russian_prose(text: str) -> bool:
    """Похоже ли на русскую нарративную фразу (для перевода в EN)."""
    if not text or not CYR.search(text):
        return False
    if RESOURCE_RE.match(text.strip()):
        return False
    plain = strip_markup(text)
    words = WORD_RE.findall(plain) + CYR_WORD_RE.findall(plain)
    # Numbered headings like "5. Комментарии" have 1 word + number
    if len(words) == 1 and re.match(r'^\d+[\.\)]\s*\w+', plain.strip()):
        return True
    if len(words) < 2:
        return False
    return True


# --------------------------------------------------------------------- titles
TITLE_PREFIX_RE = re.compile(r'^(Урок|Lesson)\s*\d+(?:\.\d+)?\s*[:\-–—]?\s*', re.I)


def translate_title(title: str, tr: Translator) -> str:
    prefix = ''
    rest = title
    m = TITLE_PREFIX_RE.match(title)
    if m:
        prefix = title[:m.end()]
        rest = title[m.end():]
    if not rest.strip():
        return title

    segments = re.split(r'\s+—\s+', rest)
    segments = [s.strip() for s in segments if s.strip()]

    # "Семантика перемещения — Move Semantics" -> оставляем английский
    if len(segments) == 2 and CYR.search(segments[0]) and not CYR.search(segments[1]):
        return prefix + segments[1]

    new_segments = []
    for seg in segments:
        if not CYR.search(seg):
            new_segments.append(seg)
            continue
        if RESOURCE_RE.match(seg) or looks_like_keyword_list(seg):
            new_segments.append(seg)
            continue
        words = WORD_RE.findall(strip_markup(seg)) + CYR_WORD_RE.findall(strip_markup(seg))
        single_word = len(words) == 1
        if len(words) < 2 and not single_word:
            new_segments.append(seg)
            continue
        if single_word and not CYR.search(seg):
            new_segments.append(seg)
            continue
        translated = tr.translate(seg)
        new_segments.append(translated if translated.strip() else seg)

    if not new_segments:
        return title
    
    # Translate the "Урок X.Y:" prefix for EN
    if prefix:
        prefix = tr.translate(prefix).rstrip()
        # Ensure space after colon if there's more content
        if new_segments and not prefix.endswith(' '):
            prefix = prefix + ' '
    
    return prefix + ' — '.join(new_segments)


def translate_plain(text: str, tr: Translator) -> str:
    if not text or not CYR.search(text):
        return text
    if RESOURCE_RE.match(text.strip()):
        return text
    if len(WORD_RE.findall(strip_markup(text))) + len(CYR_WORD_RE.findall(strip_markup(text))) < 2:
        return text
    return tr.translate(text)


COMMENT_RE = re.compile(r'^(\s*)(#|//|/\*+|\*|<!--)\s?(.*)$')


def translate_code(code: str, tr: Translator) -> str:
    lines = code.split('\n')
    changed = False
    for idx, line in enumerate(lines):
        m = COMMENT_RE.match(line)
        if not m:
            continue
        indent, marker, body = m.groups()
        body_clean = body.replace('*/', '').replace('-->', '').strip()
        if body_clean and is_russian_prose(body_clean):
            translated = tr.translate(body_clean)
            if translated == body_clean:
                continue
            trailer = ''
            if body.rstrip().endswith('*/'):
                trailer = ' */'
            elif body.rstrip().endswith('-->'):
                trailer = ' -->'
            lines[idx] = f'{indent}{marker} {translated}{trailer}'
            changed = True
    return '\n'.join(lines) if changed else code


RESOURCE_WITH_DESC = re.compile(r'^(\s*\*\*[^*]+\*\*\s*[—–-]\s*https?://[^\s<>")\]]+)(\s*\([^)]+\))?\s*$')

def translate_block(block: dict, tr: Translator) -> bool:
    btype = block.get('type')
    changed = False
    if btype in ('heading', 'text', 'blockquote'):
        value = block.get('content') or ''
        if is_russian_prose(value):
            new = tr.translate(value)
            if new != value:
                block['content'] = new
                changed = True
    elif btype == 'list':
        items = block.get('items') or []
        for i, item in enumerate(items):
            if not isinstance(item, str):
                continue
            # Handle resource links with Russian descriptions in parentheses
            m = RESOURCE_WITH_DESC.match(item)
            if m:
                prefix, paren = m.group(1), m.group(2)
                if paren and CYR.search(paren):
                    translated_paren = tr.translate(paren)
                    if translated_paren != paren:
                        items[i] = prefix + translated_paren
                        changed = True
                continue
            if is_russian_prose(item):
                new = tr.translate(item)
                if new != item:
                    items[i] = new
                    changed = True
    elif btype == 'table':
        for key in ('headers',):
            values = block.get(key) or []
            for i, cell in enumerate(values):
                if isinstance(cell, str) and is_russian_prose(cell):
                    new = tr.translate(cell)
                    if new != cell:
                        values[i] = new
                        changed = True
        for row in block.get('rows') or []:
            for i, cell in enumerate(row):
                if isinstance(cell, str) and is_russian_prose(cell):
                    new = tr.translate(cell)
                    if new != cell:
                        row[i] = new
                        changed = True
    elif btype == 'code':
        code = block.get('content') or ''
        new_code = translate_code(code, tr)
        if new_code != code:
            block['content'] = new_code
            changed = True
    return changed


def translate_topic_name(name: str, tr: Translator) -> str:
    if not CYR.search(name):
        return name
    return tr.translate(name)


def process_file(data: dict, tr: Translator) -> bool:
    changed = False
    new_title = translate_title(data.get('title', ''), tr)
    if new_title != data.get('title'):
        data['title'] = new_title
        changed = True
    new_desc = translate_plain(data.get('short_description', ''), tr)
    if new_desc != data.get('short_description'):
        data['short_description'] = new_desc
        changed = True
    for block in data.get('content_blocks') or []:
        if translate_block(block, tr):
            changed = True
    return changed


def main() -> None:
    apply = '--apply' in sys.argv
    files = sorted(glob.glob(os.path.join(FIXTURES, '*', '*.json')))
    payloads = []
    for path in files:
        with open(path, encoding='utf-8') as fh:
            payloads.append((path, json.load(fh)))

    # Собираем все русские фрагменты.
    class Recorder:
        def __init__(self):
            self.texts = []
            self._seen = set()
        def translate(self, text):
            if text not in self._seen:
                self._seen.add(text)
                self.texts.append(text)
            return text

    recorder = Recorder()
    for _, data in payloads:
        process_file(data, recorder)
    print(f'Найдено русских фрагментов: {len(recorder.texts)}', flush=True)

    # Переводим батчами.
    tr = Translator('ru', 'en')
    translated = tr.translate_many(recorder.texts)
    mapping = dict(zip(recorder.texts, translated))
    print(f'Переведено: {len(mapping)} | запросов: {tr.requests} | из кэша: {tr.hits}', flush=True)

    # Применяем.
    class Applier:
        def __init__(self, mapping):
            self.mapping = mapping
            self.missed = []
        def translate(self, text):
            if text not in self.mapping:
                self.missed.append(text)
                return text
            return self.mapping[text]

    applier = Applier(mapping)
    changed_files = 0
    samples = []
    for path, data in payloads:
        before_title = data.get('title')
        if process_file(data, applier):
            changed_files += 1
            if before_title != data.get('title') and len(samples) < 40:
                samples.append((before_title, data.get('title')))
            if apply:
                with open(path, 'w', encoding='utf-8') as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=2)
                    fh.write('\n')
    print(f'Файлов изменено: {changed_files} из {len(files)}')
    if applier.missed:
        print(f'Не найдено в словаре: {len(applier.missed)}')
    print('\nПримеры заголовков:')
    for old, new in samples:
        print(f'  - {old[:95]}\n    → {new[:95]}')
    if not apply:
        print('\nЭто отчёт. Для записи запустите с --apply')


if __name__ == '__main__':
    main()