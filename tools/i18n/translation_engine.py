# -*- coding: utf-8 -*-
"""Движок машинного перевода для контента уроков.

Использует публичный эндпоинт Google (`clients5.google.com/translate_a/t`,
режим расширения Chrome) — он принимает несколько `q` за раз и возвращает
массив переводов, что даёт точное соответствие строк.

Результаты кэшируются на диск, код и ссылки защищаются от перевода.

Использование::

    from translation_engine import Translator
    tr = Translator('ru', 'en')
    print(tr.translate_many(['Привет', 'Мир']))
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, 'translations')

ENDPOINT = 'https://clients5.google.com/translate_a/t'

CODE_RE = re.compile(r'`([^`]+)`')
URL_RE = re.compile(r'https?://[^\s<>")\]]+')
PLACEHOLDER_RE = re.compile(r'⟦([KUVHКk])(\d+)⟧')
# Google occasionally transliterates the Latin placeholder kind into Cyrillic
# (K -> К).  Normalise it back before restoring protected fragments.
PLACEHOLDER_KIND = {'К': 'K', 'k': 'K'}
HTML_TAG_ANY_RE = re.compile(r'</?[A-Za-z][^<>]{0,300}>')

# Технические токены, которые нельзя переводить: селекторы, флаги,
# обобщённые типы, camelCase/snake_case, имена файлов, вызовы функций.
VERBATIM_RE = re.compile(r"""
      \b[A-Za-z][A-Za-z0-9_]*<[^<>\n]{1,80}>
    | :[a-z][a-z-]*
    | (?<![\w-])--[a-z][A-Za-z0-9-]*
    | \b[a-z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*
    | \b[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+
    | \b[A-Z]{2,}[0-9]*\b
    | \b[A-Za-z0-9_]+\.(?:js|jsx|ts|tsx|py|rs|cs|cpp|hpp|hxx|h|c|css|scss|sass|html|json|yaml|yml|toml|sh|md|txt|config|ini|xml|sql|lock|webp|png|svg)\b
    | \b[A-Za-z_][A-Za-z0-9_]*\(\)
    | (?<![A-Za-z0-9_])[A-Z]\#
""", re.X)

# Названия продуктов и терминов, которые переводить нельзя.
PROTECT_TERMS = [
    'ASP.NET Core', 'ASP.NET', 'EF Core', '.NET Core', '.NET',
    'placement new', 'happens-before', 'lock-free', 'wait-free',
    'WebAssembly', 'GitHub Actions', 'Node.js', 'TypeScript', 'JavaScript',
    'PostgreSQL', 'Kubernetes', 'Docker Compose', 'Common Lisp', 'Objective-C',
    'Clean Architecture', 'Event Loop', 'Event-Driven', 'Zero-Copy',
]
PROTECT_TERM_RE = re.compile(
    r'(?<![A-Za-z0-9_])(' 
    + '|'.join(re.escape(t) for t in sorted(PROTECT_TERMS, key=len, reverse=True))
    + r')(?![A-Za-z0-9_])'
)
HTML_TAG_RE = re.compile(
    r'</?(?:p|div|span|strong|em|b|i|u|s|code|pre|ul|ol|li|br|hr|'
    r'h[1-6]|table|thead|tbody|tr|td|th|blockquote|a|img|sup|sub)\b[^>]*>',
    re.I,
)


class TranslationError(RuntimeError):
    pass


class Translator:
    """Пакетный переводчик с дисковым кэшем и ограничением частоты запросов."""

    def __init__(self, src: str, dst: str, batch_strings: int = 30,
                 batch_chars: int = 3000, timeout: int = 40,
                 min_interval: float = 0.25):
        self.src = src
        self.dst = dst
        self.batch_strings = batch_strings
        self.batch_chars = batch_chars
        self.timeout = timeout
        self.min_interval = min_interval
        self._last_request = 0.0
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.cache_path = os.path.join(CACHE_DIR, f'cache_{src}_{dst}.json')
        self.cache: dict[str, str] = {}
        self._dirty = 0
        self.requests = 0
        self.hits = 0
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, encoding='utf-8') as fh:
                    self.cache = json.load(fh)
            except (OSError, ValueError):
                self.cache = {}

    # ------------------------------------------------------------------ cache
    @staticmethod
    def _key(src: str, dst: str, text: str) -> str:
        return hashlib.sha1(f'{src}\x00{dst}\x00{text}'.encode('utf-8')).hexdigest()

    def save(self) -> None:
        if not self._dirty:
            return
        tmp = self.cache_path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as fh:
            json.dump(self.cache, fh, ensure_ascii=False)
        os.replace(tmp, self.cache_path)
        self._dirty = 0

    # --------------------------------------------------------------- protect
    @staticmethod
    def _protect(text: str):
        saved: list[tuple[str, str]] = []

        def _add(kind: str, value: str) -> str:
            saved.append((kind, value))
            return f'⟦{kind}{len(saved) - 1}⟧'

        # 1) HTML-теги — как есть, чтобы не ломать разметку.
        text = HTML_TAG_ANY_RE.sub(lambda m: _add('H', m.group(0)), text)
        # 2) inline-код в бэктиках
        text = CODE_RE.sub(lambda m: _add('K', m.group(1)), text)
        # 3) ссылки
        text = URL_RE.sub(lambda m: _add('U', m.group(0)), text)
        # 4) названия продуктов/термины
        text = PROTECT_TERM_RE.sub(lambda m: _add('V', m.group(0)), text)
        # 5) прочие технические токены
        text = VERBATIM_RE.sub(lambda m: _add('V', m.group(0)), text)
        return text, saved

    @staticmethod
    def _restore(text: str, saved, html_mode: bool) -> str:
        def _value(kind: str, idx: int):
            if idx >= len(saved):
                return None
            value = saved[idx][1]
            if kind == 'K':
                return f'<code>{value}</code>' if html_mode else f'`{value}`'
            return value

        def _repl(m):
            kind = PLACEHOLDER_KIND.get(m.group(1), m.group(1))
            value = _value(kind, int(m.group(2)))
            return m.group(0) if value is None else value

        text = PLACEHOLDER_RE.sub(_repl, text)
        return text

    # --------------------------------------------------------------- request
    def _throttle(self) -> None:
        wait = self.min_interval - (time.time() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.time()

    def _request(self, texts: list[str]) -> list[str]:
        pairs = [('client', 'dict-chrome-ex'), ('sl', self.src), ('tl', self.dst)]
        pairs += [('q', t) for t in texts]
        url = ENDPOINT + '?' + urllib.parse.urlencode(pairs)
        req = urllib.request.Request(url, headers={
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/122.0 Safari/537.36'),
            'Accept': '*/*',
        })
        last = None
        for attempt in range(6):
            self._throttle()
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode('utf-8')
                data = json.loads(raw)
                self.requests += 1
                self._last_request = time.time()
                if isinstance(data, str):
                    data = [data]
                return [d if isinstance(d, str) else '' for d in data]
            except Exception as exc:  # noqa: BLE001 - сеть бывает любой
                last = exc
                time.sleep(min(45, 3 * (attempt + 1)))
        raise TranslationError(f'перевод не удался: {last}')

    # -------------------------------------------------------------- translate
    @staticmethod
    def _fix(translated: str, original: str) -> str:
        if ' — ' in original and ' - ' in translated and ' — ' not in translated:
            translated = translated.replace(' - ', ' — ')
        return translated.strip('\n')

    def _translate_batch(self, texts: list[str]) -> list[str]:
        protected = []
        for text in texts:
            p, saved = self._protect(text)
            protected.append([p, saved])

        pieces = [p for p, _ in protected]
        raw = self._request(pieces)
        if len(raw) != len(texts):
            # Эндпоинт схлопнул массив — переводим по одной строке.
            raw = [self._request([p])[0] for p in pieces]

        result = []
        for idx, (part, (p, saved)) in enumerate(zip(raw, protected)):
            html_mode = bool(HTML_TAG_RE.search(texts[idx]))
            text = self._restore(part, saved, html_mode)
            fixed = self._fix(text, texts[idx])
            result.append(fixed if fixed.strip() else texts[idx])
        return result

    def translate_many(self, texts: list[str]) -> list[str]:
        out: list = [None] * len(texts)
        pending: list[tuple[int, str]] = []

        for idx, text in enumerate(texts):
            if not text or not text.strip():
                out[idx] = text
                continue
            key = self._key(self.src, self.dst, text)
            cached = self.cache.get(key)
            if cached is not None:
                out[idx] = cached
                self.hits += 1
            else:
                pending.append((idx, text))

        batches: list[list[tuple[int, str]]] = []
        batch: list[tuple[int, str]] = []
        chars = 0
        for item in pending:
            size = len(item[1])
            if batch and (len(batch) >= self.batch_strings or chars + size > self.batch_chars):
                batches.append(batch)
                batch, chars = [], 0
            batch.append(item)
            chars += size
        if batch:
            batches.append(batch)

        for bi, current in enumerate(batches, 1):
            translations = self._translate_batch([t for _, t in current])
            for (idx, src_text), translated in zip(current, translations):
                out[idx] = translated
                self.cache[self._key(self.src, self.dst, src_text)] = translated
                self._dirty += 1
            if bi % 5 == 0:
                self.save()
                print(f'    … {bi}/{len(batches)} пакетов, запросов={self.requests}',
                      flush=True)

        self.save()
        return [t if t is not None else '' for t in out]

    def translate(self, text: str) -> str:
        return self.translate_many([text])[0]
