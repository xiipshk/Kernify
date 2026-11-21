# -*- coding: utf-8 -*-
"""Локализация русской версии: убираем английскую прозу из фикстур.

Переводит (en → ru) только *нарративные* английские фрагменты:
заголовки-описания, абзацы, пункты списков, ячейки таблиц, комментарии
в коде. Технические идентификаторы, имена API и названия книг/ссылок
остаются как есть.

Запуск::

    python localize_ru.py            # отчёт без изменений
    python localize_ru.py --apply    # записать изменения в фикстуры
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
URL_RE = re.compile(r'https?://[^\s<>")\]]+')
TAG_RE = re.compile(r'<[^>]+>')
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]{1,}")

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'of', 'with', 'without', 'for', 'to', 'in',
    'on', 'at', 'by', 'from', 'into', 'onto', 'over', 'under', 'between',
    'through', 'during', 'before', 'after', 'above', 'below', 'per', 'via',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'has', 'have', 'had',
    'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should', 'must',
    'may', 'might', 'shall', 'this', 'that', 'these', 'those', 'it', 'its',
    'they', 'them', 'their', 'we', 'our', 'you', 'your', 'he', 'she', 'his',
    'her', 'i', 'as', 'if', 'then', 'than', 'so', 'such', 'not', 'no', 'nor',
    'but', 'also', 'only', 'more', 'most', 'less', 'least', 'each', 'every',
    'all', 'any', 'some', 'other', 'another', 'both', 'either', 'neither',
    'when', 'where', 'which', 'who', 'whom', 'whose', 'why', 'how', 'what',
    'while', 'because', 'since', 'until', 'unless', 'though', 'although',
    'there', 'here', 'now', 'always', 'never', 'often', 'usually', 'still',
    'just', 'very', 'too', 'much', 'many', 'few', 'several', 'own', 'same',
    'up', 'down', 'out', 'off', 'again', 'once', 'about', 'against', 'among',
    'within', 'upon', 'whether', 'however', 'therefore', 'thus', 'instead',
    'otherwise', 'yet', 'already', 'else', 'let', 'lets', "let's",
    'make', 'makes', 'made', 'use', 'uses', 'used', 'using', 'get', 'gets',
    'got', 'need', 'needs', 'want', 'wants', 'ensure', 'ensures', 'allow',
    'allows', 'avoid', 'avoids', 'keep', 'keeps', 'provide', 'provides',
    'consider', 'prefer', 'see', 'look', 'take', 'takes', 'give', 'gives',
}

PROSE_WORDS = {
    'overview', 'strategy', 'strategies', 'testing', 'tests', 'setup',
    'performance', 'security', 'architecture', 'architectural', 'guide',
    'introduction', 'intro', 'basics', 'basic', 'advanced', 'patterns',
    'pattern', 'practices', 'practice', 'principles', 'principle', 'example',
    'examples', 'summary', 'comparison', 'compare', 'integration', 'deployment',
    'configuration', 'structure', 'management', 'implementation', 'fundamentals',
    'essentials', 'approach', 'notes', 'note', 'best', 'trade-offs',
    'trade-off', 'checklist', 'pitfalls', 'antipatterns', 'refactoring',
    'observability', 'monitoring', 'optimization', 'optimizing', 'debugging',
    'migration', 'versioning', 'documentation', 'automation', 'tooling',
    'ecosystem', 'internals', 'concurrency', 'memory', 'resource', 'resources',
    'lifetime', 'constraints', 'semantics', 'model', 'models', 'design',
    'workflow', 'pipeline', 'pipelines', 'quality', 'reliability',
    'engineering', 'development', 'production', 'environment', 'process',
    'lifecycle', 'lifecycles', 'serialization', 'deserialization',
    'communication', 'networking', 'background', 'services', 'libraries',
    'library', 'frameworks', 'framework', 'algorithms', 'algorithm',
    'choosing', 'right', 'moving', 'heavy', 'work', 'worker', 'workers',
    'modules', 'module', 'safety', 'diagnostics', 'profiling', 'tracing',
    'logging', 'metrics', 'scaling', 'deploying', 'building', 'package',
    'packages', 'interop', 'bindings', 'layout', 'styling', 'responsive',
    'preprocessor', 'preprocessors', 'animation', 'animations', 'transitions',
    'typography', 'accessibility', 'selectors', 'specificity', 'cascade',
    'refactor', 'mocking', 'benchmarking', 'benchmarks', 'profiler', 'leaks',
    'garbage', 'collection', 'diagrams', 'diagram', 'schema', 'schemas',
    'queries', 'query', 'transactions', 'indexes', 'indexing', 'caching',
    'cache', 'queues', 'queue', 'streams', 'buffers', 'threads', 'processes',
    'tasks', 'scheduling', 'scheduler', 'event', 'events', 'driven', 'protocols',
    'protocol', 'authentication', 'authorization', 'encryption',
    'vulnerabilities', 'attacks', 'threats', 'remediation', 'hardening',
    'compliance', 'audit', 'auditing', 'mistakes', 'errors', 'exceptions',
    'handling', 'recovery', 'retries', 'timeouts', 'capacity', 'throughput',
    'latency', 'maintenance', 'legacy', 'modularity', 'coupling', 'cohesion',
    'boundaries', 'layers', 'layer', 'domain', 'infrastructure',
    'application', 'presentation', 'persistence', 'mapping', 'orm', 'proxy',
    'gateway', 'routing', 'middleware', 'static', 'dynamic', 'runtime',
    'build', 'compilation', 'linking', 'loading', 'loader', 'linker',
    'compiler', 'virtual', 'machine', 'bytecode', 'instructions', 'registers',
    'stack', 'heap', 'pointers', 'pointer', 'references', 'reference',
    'ownership', 'borrowing', 'lifetimes', 'traits', 'generics', 'macros',
    'metaprogramming', 'reflection', 'attributes', 'annotations', 'decorators',
    'closures', 'scopes', 'hoisting', 'context', 'execution', 'promises',
    'callbacks', 'asynchronous', 'synchronous', 'parallelism', 'multithreading',
    'coroutines', 'generators', 'iterators', 'iterables', 'collections',
    'containers', 'tuples', 'dictionaries', 'sets', 'arrays', 'strings',
    'numbers', 'booleans', 'operators', 'conditions', 'loops', 'functions',
    'methods', 'classes', 'objects', 'inheritance', 'polymorphism',
    'encapsulation', 'abstraction', 'interfaces', 'contracts', 'dependencies',
    'injection', 'container', 'registry', 'factory', 'singleton', 'observer',
    'decorator', 'adapter', 'facade', 'command', 'builder', 'prototype',
    'mediator', 'memento', 'state', 'template', 'visitor', 'chain',
    'responsibility', 'repository', 'unit', 'service', 'microservices',
    'monolith', 'distributed', 'cluster', 'clustering', 'replication',
    'sharding', 'consistency', 'availability', 'partitioning', 'fault',
    'tolerance', 'telemetry', 'instrumentation', 'alerting', 'dashboards',
    'installation', 'installing', 'running', 'launching', 'comments',
    'variables', 'types', 'typing', 'conversions', 'conversion', 'input',
    'output', 'files', 'file', 'project', 'projects', 'exercise', 'exercises',
    'task', 'solution', 'solutions', 'step', 'steps', 'part', 'parts',
    'chapter', 'chapters', 'section', 'sections', 'demo', 'demos', 'tutorial',
    'tutorials', 'course', 'lesson', 'lessons', 'topics', 'topic',
}

RESOURCE_RE = re.compile(r'^\s*\*\*[^*]+\*\*\s*[—–-]\s*(https?://|YouTube|$)', re.I)

# Ключевые слова языков программирования: списки ключевых слов не переводим.
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
    """`if, switch, while, for` — это перечисление ключевых слов, не проза."""
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


class RecordingTranslator:
    """Собирает строки вместо перевода (первый проход)."""

    def __init__(self):
        self.texts: list[str] = []
        self._seen: set[str] = set()

    def translate(self, text: str) -> str:
        if text not in self._seen:
            self._seen.add(text)
            self.texts.append(text)
        return text


class DictTranslator:
    """Отдаёт готовый перевод из словаря (второй проход)."""

    def __init__(self, mapping: dict[str, str]):
        self.mapping = mapping
        self.missed: list[str] = []

    def translate(self, text: str) -> str:
        if text not in self.mapping:
            self.missed.append(text)
            return text
        return self.mapping[text]


def strip_markup(text: str) -> str:
    text = TAG_RE.sub(' ', text)
    text = URL_RE.sub(' ', text)
    return text.replace('`', ' ')


def is_english_prose(text: str) -> bool:
    if not text or CYR.search(text):
        return False
    if RESOURCE_RE.match(text.strip()):
        return False
    plain = strip_markup(text)
    words = WORD_RE.findall(plain)
    if len(words) < 2:
        return False
    if re.search(r'\bvs\b', plain, re.I):
        return False
    if looks_like_keyword_list(plain):
        return False
    low = [w.lower() for w in words]
    stop = sum(1 for w in low if w in STOPWORDS)
    prose = sum(1 for w in low if w in PROSE_WORDS)
    if prose:
        return True
    if stop >= 2:
        return True
    if stop == 1 and len(words) >= 4:
        return True
    return False


def has_cyr(text: str) -> bool:
    return bool(CYR.search(text or ''))


TITLE_PREFIX_RE = re.compile(r'^(Урок|Lesson)\s*\d+(?:\.\d+)?\s*[:\-–—]?\s*', re.I)


def localize_title(title: str, tr) -> str:
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

    # "Move Semantics — семантика перемещения": вторая часть уже русский
    # перевод первой — оставляем только её.
    if len(segments) == 2 and not has_cyr(segments[0]) and has_cyr(segments[1]):
        second = segments[1]
        second = second[:1].upper() + second[1:]
        return prefix + second

    new_segments = []
    for seg in segments:
        m2 = re.match(r'^([A-Za-z][^()]*?)\s*\(([^()]*[А-Яа-яЁё][^()]*)\)\s*$', seg)
        if m2 and not has_cyr(m2.group(1)):
            new_segments.append(m2.group(2).strip())
            continue
        if has_cyr(seg):
            new_segments.append(seg)
            continue
        if RESOURCE_RE.match(seg) or looks_like_keyword_list(seg):
            new_segments.append(seg)
            continue
        words = WORD_RE.findall(strip_markup(seg))
        single_word = len(words) == 1 and words[0].lower() in PROSE_WORDS
        if len(words) < 2 and not single_word:
            new_segments.append(seg)
            continue
        translated = tr.translate(seg)
        new_segments.append(translated if translated.strip() else seg)

    if not new_segments:
        return title
    return prefix + ' — '.join(new_segments)


def localize_plain(text: str, tr) -> str:
    if not text or has_cyr(text):
        return text
    if RESOURCE_RE.match(text.strip()):
        return text
    if len(WORD_RE.findall(strip_markup(text))) < 2:
        return text
    return tr.translate(text)


COMMENT_RE = re.compile(r'^(\s*)(#|//|/\*+|\*|<!--)\s?(.*)$')


def localize_code(code: str, tr) -> str:
    lines = code.split('\n')
    changed = False
    for idx, line in enumerate(lines):
        m = COMMENT_RE.match(line)
        if not m:
            continue
        indent, marker, body = m.groups()
        body_clean = body.replace('*/', '').replace('-->', '').strip()
        if body_clean and is_english_prose(body_clean):
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


def localize_block(block: dict, tr) -> bool:
    btype = block.get('type')
    changed = False
    if btype in ('heading', 'text', 'blockquote'):
        value = block.get('content') or ''
        if is_english_prose(value):
            new = tr.translate(value)
            if new != value:
                block['content'] = new
                changed = True
    elif btype == 'list':
        items = block.get('items') or []
        for i, item in enumerate(items):
            if isinstance(item, str) and is_english_prose(item):
                new = tr.translate(item)
                if new != item:
                    items[i] = new
                    changed = True
    elif btype == 'table':
        for key in ('headers',):
            values = block.get(key) or []
            for i, cell in enumerate(values):
                if isinstance(cell, str) and is_english_prose(cell):
                    new = tr.translate(cell)
                    if new != cell:
                        values[i] = new
                        changed = True
        for row in block.get('rows') or []:
            for i, cell in enumerate(row):
                if isinstance(cell, str) and is_english_prose(cell):
                    new = tr.translate(cell)
                    if new != cell:
                        row[i] = new
                        changed = True
    elif btype == 'code':
        code = block.get('content') or ''
        new_code = localize_code(code, tr)
        if new_code != code:
            block['content'] = new_code
            changed = True
    return changed


def process_file(data: dict, tr) -> bool:
    changed = False
    new_title = localize_title(data.get('title', ''), tr)
    if new_title != data.get('title'):
        data['title'] = new_title
        changed = True
    new_desc = localize_plain(data.get('short_description', ''), tr)
    if new_desc != data.get('short_description'):
        data['short_description'] = new_desc
        changed = True
    for block in data.get('content_blocks') or []:
        if localize_block(block, tr):
            changed = True
    return changed


def main() -> None:
    apply = '--apply' in sys.argv
    files = sorted(glob.glob(os.path.join(FIXTURES, '*', '*.json')))
    payloads = []
    for path in files:
        with open(path, encoding='utf-8') as fh:
            payloads.append((path, json.load(fh)))

    # Проход 1: собрать все английские фрагменты.
    recorder = RecordingTranslator()
    for _, data in payloads:
        process_file(data, recorder)
    print(f'Найдено английских фрагментов: {len(recorder.texts)}', flush=True)

    # Перевод одним заходом (с кэшем на диске).
    tr = Translator('en', 'ru')
    translated = tr.translate_many(recorder.texts)
    mapping = dict(zip(recorder.texts, translated))
    print(f'Переведено: {len(mapping)} | запросов: {tr.requests} | из кэша: {tr.hits}',
          flush=True)

    # Проход 2: применить.
    applier = DictTranslator(mapping)
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
        for t in applier.missed[:5]:
            print('   ', t[:100])
    print('\nПримеры заголовков:')
    for old, new in samples:
        print(f'  - {old[:95]}\n    → {new[:95]}')
    if not apply:
        print('\nЭто отчёт. Для записи запустите с --apply')


if __name__ == '__main__':
    main()
