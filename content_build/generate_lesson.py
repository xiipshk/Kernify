#!/usr/bin/env python3
"""
Генератор уроков Kernify v2 — улучшенная версия.

Стратегия:
1. Исходник парсится в структурированные секции
2. Каждая секция превращается в: заголовок + объясняющий текст + код + вывод + анализ
3. Добавляются callout'ы, таблицы, практические советы
4. Генерация starter_code и hints на основе контента
"""

from __future__ import annotations

import re
import json
from pathlib import Path
from textwrap import dedent
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SourceSection:
    level: int
    title: str
    raw_content: str
    code_blocks: list[tuple[str, str]] = field(default_factory=list)
    text_parts: list[str] = field(default_factory=list)


@dataclass
class LessonMeta:
    language: str
    program_order: int
    topic_order: int
    name: str
    slug: str
    short_description: str
    topic_name: str
    topic_description: str
    learning_objectives: list[str]
    estimated_minutes: int
    xp_reward: int
    difficulty: str
    tags: list[str]
    starter_code: str = ""
    hints: list[str] = field(default_factory=list)


def parse_source_file(path: Path) -> tuple[str, list[SourceSection]]:
    text = path.read_text(encoding="utf-8")
    
    title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    lesson_title = title_match.group(1).strip() if title_match else "Урок"
    
    # Ищем секции: ## Заголовок или ### Подзаголовок
    # Паттерн захватывает заголовок и всё до следующего заголовка
    section_pattern = re.compile(
        r'^(#{2,3})\s+(.+?)\n(.*?)(?=\n#{2,3}\s|\Z)',
        re.MULTILINE | re.DOTALL
    )
    
    sections = []
    for match in section_pattern.finditer(text):
        level = len(match.group(1))
        title = match.group(2).strip()
        content = match.group(3).strip()
        
        # Извлекаем код-блоки
        code_blocks = []
        code_pattern = re.compile(r'```(\w*)\n(.*?)\n```', re.DOTALL)
        for code_match in code_pattern.finditer(content):
            lang = code_match.group(1).strip() or "python"
            code = code_match.group(2).strip()
            code_blocks.append((lang, code))
        
        # Удаляем код-блоки из текста, оставляем только поясняющий текст
        text_only = re.sub(r'```\w*\n.*?\n```', '', content, flags=re.DOTALL)
        # Разбиваем на абзацы
        text_parts = [p.strip() for p in re.split(r'\n\s*\n', text_only) if p.strip()]
        
        sections.append(SourceSection(
            level=level,
            title=title,
            raw_content=content,
            code_blocks=code_blocks,
            text_parts=text_parts
        ))
    
    lesson_title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    lesson_title = lesson_title_match.group(1).strip() if lesson_title_match else "Урок"
    
    return lesson_title, sections


def extract_objectives(text: str) -> list[str]:
    match = re.search(r'## Цели урока\n(.*?)(?=\n##|\n---|\Z)', text, re.DOTALL)
    if not match:
        return []
    objectives = []
    for line in match.group(1).split('\n'):
        line = line.strip()
        if line.startswith('-'):
            objectives.append(line[1:].strip())
    return objectives


def clean_markdown(text: str) -> str:
    """Очищает markdown, оставляя чистый текст."""
    text = re.sub(r'```\w*\n.*?\n```', '', text, flags=re.DOTALL)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'#{2,3}\s+.+?\n', '', text)
    text = re.sub(r'---+', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def build_objectives_from_sections(sections: list[SourceSection], fallback: list[str]) -> list[str]:
    """Строит цели обучения из заголовков разделов уровня 2."""
    objectives = []
    for section in sections:
        if section.level == 2:
            title = re.sub(r'^\d+\.\s*', '', section.title)
            # Убираем технические слова
            title = re.sub(r'^(Зачем|Что такое|Как|Основы|Базовый|Практические)\s+', '', title, flags=re.IGNORECASE)
            if title and len(title) > 3:
                objectives.append(f"Понимать и применять {title.lower()}")
    if objectives:
        return objectives[:6]
    return fallback[:6]


def generate_starter_code(sections: list[SourceSection], topic: str) -> str:
    """Генерирует стартовый код на основе первых примеров."""
    # Ищем первый простой код-блок
    for section in sections:
        for lang, code in section.code_blocks:
            if lang in ("python", "py") and len(code) < 500:
                # Проверяем, что это не фрагмент, а полноценный пример
                if "async def" in code or "def " in code or "import" in code:
                    lines = code.strip().split('\n')
                    if len(lines) >= 3 and len(lines) <= 20:
                        return code
    # Фоллбэк
    return f"# Пример кода для {topic}\n# TODO: добавьте стартовый пример"


def generate_hints(sections: list[SourceSection]) -> list[str]:
    """Генерирует подсказки на основе контента."""
    hints = []
    
    # Ищем ключевые темы для подсказок
    content_all = " ".join(s.raw_content for s in sections).lower()
    
    if "asyncio.run" in content_all:
        hints.append("asyncio.run() — главный вход в асинхронный код (Python 3.7+).")
    if "await" in content_all:
        hints.append("await работает только внутри async функций.")
    if "asyncio.gather" in content_all:
        hints.append("gather запускает задачи параллельно и ждёт все результаты.")
    if "asyncio.lock" in content_all or "asyncio.Lock" in content_all:
        hints.append("async with lock — безопасный способ захвата, автоматическое освобождение.")
    if "asyncio.semaphore" in content_all or "asyncio.Semaphore" in content_all:
        hints.append("Semaphore ограничивает параллелизм: async with semaphore.")
    if "aiohttp" in content_all:
        hints.append("ClientSession создавайте один раз, reuse connections.")
    if "asyncio.timeout" in content_all or "wait_for" in content_all:
        hints.append("wait_for оборачивает корутину с таймаутом, timeout (3.11+) — контекстный менеджер.")
    
    # Общие
    hints.append("Корутину нужно await'ить или передать в gather/create_task, иначе не выполнится.")
    hints.append("Для CPU-bound задач используйте run_in_executor с ProcessPoolExecutor.")
    
    return hints[:5]


def section_to_blocks(section: SourceSection, prev_section: Optional[SourceSection]) -> list[dict]:
    """Конвертирует секцию в блоки урока."""
    blocks = []
    
    # Заголовок
    h_level = 2 if section.level == 2 else 3
    blocks.append({"type": "heading", "level": h_level, "content": section.title})
    
    # Поясняющий текст
    for text_part in section.text_parts:
        if len(text_part) > 30:  # пропускаем слишком короткие фрагменты
            blocks.append({"type": "text", "content": text_part})
    
    # Код-блоки с пояснениями
    for i, (lang, code) in enumerate(section.code_blocks):
        if not code.strip():
            continue
        
        # Добавляем код
        blocks.append({"type": "code", "language": lang, "content": code})
        
        # Добавляем заглушку для вывода (позже заменим на реальный при необходимости)
        # Определяем, нужен ли вывод
        needs_output = any(kw in code for kw in ["print(", "return ", "await ", "asyncio.run"])
        if needs_output:
            blocks.append({"type": "code", "language": "text", "content": "# вывод примера"})
        
        # После некоторых код-блоков добавляем пояснение
        if i == 0 and section.code_blocks:
            # После первого примера в секции добавляем анализ
            blocks.append({"type": "text", "content": "Этот пример демонстрирует ключевую идею раздела. Обратите внимание на структуру кода и используемые примитивы."})
    
    # Добавляем callout для важных моментов
    if section.level == 2 and section.code_blocks:
        key_terms = {
            "asyncio.run": ("info", "Точка входа", "asyncio.run() создаёт event loop, запускает корутину и закрывает loop. В 3.12+ loop создаётся автоматически."),
            "await": ("info", "Приостановка", "await отдаёт управление event loop'у, позволяя другим задачам выполняться."),
            "asyncio.gather": ("success", "Параллелизм", "gather запускает все переданные корутины одновременно и собирает результаты в список."),
            "asyncio.Lock": ("warning", "Синхронизация", "Lock гарантирует, что критическая секция выполняется только одной задачей за раз."),
            "asyncio.Semaphore": ("info", "Ограничение", "Semaphore(n) позволяет не более n задачам одновременно находиться в секции."),
            "asyncio.Event": ("info", "Сигналы", "Event — простой способ уведомить задачи о наступлении события."),
            "asyncio.Queue": ("info", "Передача данных", "Queue безопасна для передачи данных между producer и consumer задачами."),
            "asyncio.wait_for": ("warning", "Таймауты", "wait_for отменяет задачу по таймауту, поднимая TimeoutError."),
            "aiohttp.ClientSession": ("success", "HTTP клиент", "Создавайте сессию один раз и переиспользуйте для множества запросов."),
        }
        
        content_lower = section.raw_content.lower()
        for term, (style, title, desc) in key_terms.items():
            if term.lower() in content_lower:
                blocks.append({
                    "type": "callout",
                    "style": style,
                    "title": title,
                    "content": desc
                })
                break  # только один callout на секцию
    
    return blocks


def build_intro(topic_name: str, sections: list[SourceSection]) -> str:
    """Строит введение: 2 абзаца."""
    # Находим первый содержательный текст
    first_text = ""
    for section in sections:
        if section.level == 2 and section.text_parts:
            first_text = section.text_parts[0]
            break
    
    if not first_text:
        first_text = f"{topic_name} — важная тема для современного Python."
    
    para1 = f"{topic_name} позволяет писать эффективный неблокирующий код. " \
            f"Вместо ожидания ввода-вывода программа переключается на другие задачи, " \
            f"что критично для высоконагруженных сервисов, ботов и парсеров."
    
    para2 = f"В этом уроке мы пройдём от основ event loop и корутин до " \
            f"продвинутых паттернов: синхронизация, таймауты, работа с HTTP через aiohttp. " \
            f"Каждый пример запускается и демонстрирует реальное поведение."
    
    return f"{para1}\n\n{para2}"


def build_ending(topic_name: str, sections: list[SourceSection]) -> list[dict]:
    """Строит завершающие разделы с учетом контента урока."""
    blocks = []
    
    # Типичные ошибки — генерируем из контента
    blocks.append({"type": "heading", "level": 2, "content": "Типичные ошибки"})
    
    error_rows = [
        ["Вызов корутины без await", "Корутина не выполняется, программа молчит.", "Всегда await'ьте или передавайте в gather/create_task."],
        ["Блокирующий код в async", "Весь event loop блокируется, параллелизм теряется.", "Выносите в to_thread или run_in_executor."],
        ["Создание новой сессии на запрос", "Потеря пула соединений, медленнее.", "Один ClientSession на приложение."],
        ["Забытый task.cancel()", "Задача висит в памяти, утечка.", "Всегда await task после cancel."],
        ["Глобальные переменные вместо Lock", "Гонка данных, непредсказуемые баги.", "asyncio.Lock для критических секций."],
    ]
    
    blocks.append({
        "type": "table",
        "headers": ["Ошибка", "Что происходит", "Как правильно"],
        "rows": error_rows
    })
    
    # Практика
    blocks.append({"type": "heading", "level": 2, "content": "Практика"})
    blocks.append({
        "type": "text",
        "content": "Выполните задания по порядку. Каждое закрепляет конкретный навык."
    })
    blocks.append({
        "type": "list",
        "ordered": True,
        "items": [
            "Напишите асинхронную функцию, которая параллельно скачивает 3 URL через aiohttp и возвращает сумму длин ответов.",
            "Реализуйте ограниченный пул работников: Semaphore(3) + Queue задач. Запустите 10 задач, убедитесь, что одновременно работает не более 3.",
            "Напишите функцию с таймаутом: если операция не завершилась за 2 секунды — вернуть значение по умолчанию.",
            "Создайте producer-consumer паттерн: одна задача кладёт числа в Queue, три задачи забирают и обрабатывают.",
            "Добавьте graceful shutdown: при Ctrl+C корректно завершайте все задачи и закрывайте aiohttp сессию."
        ]
    })
    
    # Проверьте себя
    blocks.append({"type": "heading", "level": 2, "content": "Проверьте себя"})
    blocks.append({
        "type": "list",
        "ordered": True,
        "items": [
            "Чем корутина отличается от обычной функции?",
            "Зачем нужен asyncio.run() и можно ли вызывать его несколько раз?",
            "В чём разница между gather, wait и as_completed?",
            "Почему await time.sleep() блокирует event loop, а await asyncio.sleep() — нет?",
            "Как корректно обработать CancelledError при отмене задачи?"
        ]
    })
    blocks.append({"type": "heading", "level": 3, "content": "Ответы"})
    blocks.append({
        "type": "list",
        "ordered": True,
        "items": [
            "Корутина (async def) возвращает объект-корутину, которая выполняется только при await. Обычная функция выполняется сразу.",
            "asyncio.run() создаёт новый event loop, запускает корутину и закрывает loop. Нельзя вложить один run в другой — используйте create_task.",
            "gather ждёт все и возвращает список результатов. wait возвращает done/pending множества. as_completed — итератор по завершающимся задачам.",
            "time.sleep() блокирует весь поток (и event loop). asyncio.sleep() отдаёт управление loop'у, позволяя другим задачам работать.",
            "Обязательно перехватывайте CancelledError, делайте cleanup и делайте raise, иначе задача не отменится."
        ]
    })
    
    # Итоги
    blocks.append({"type": "heading", "level": 2, "content": "Итоги"})
    blocks.append({
        "type": "list",
        "ordered": False,
        "items": [
            "async/await — синтаксис для неблокирующего кода, event loop управляет выполнением.",
            "Корутины запускаются через asyncio.run() или create_task().",
            "gather / wait / as_completed — инструменты параллелизма.",
            "Lock, Semaphore, Event, Queue — примитивы синхронизации для задач.",
            "wait_for / timeout — защита от зависаний.",
            "to_thread / run_in_executor — мост к блокирующему и CPU-bound коду.",
            "aiohttp — стандарт асинхронного HTTP, ClientSession переиспользуйте."
        ]
    })
    
    # Что дальше
    blocks.append({"type": "heading", "level": 2, "content": "Что дальше"})
    blocks.append({
        "type": "text",
        "content": "Асинхронность — основа современных высоконагруженных сервисов. " \
        "Следующий урок про работу с данными: базы, ORM, миграции и кэширование — " \
        "там эти навыки пригодятся для асинхронных драйверов БД."
    })
    
    # Если хотите углубиться
    blocks.append({"type": "heading", "level": 2, "content": "Если хотите углубиться"})
    blocks.append({
        "type": "list",
        "ordered": False,
        "items": [
            "Официальная документация asyncio: docs.python.org/3/library/asyncio.html",
            "Real Python: Async IO in Python — подробный туториал.",
            "aiohttp документация: docs.aiohttp.org — клиент и сервер.",
            "PEP 3156: корутины и event loop — историческое обоснование."
        ]
    })
    
    return blocks


def generate_lesson_file(meta: LessonMeta, sections: list[SourceSection]) -> str:
    """Генерирует полный .py файл урока."""
    
    # Цели обучения
    objectives = meta.learning_objectives or build_objectives_from_sections(sections, [
        "Понимать event loop и корутины",
        "Писать async/await код",
        "Запускать задачи параллельно через gather",
        "Синхронизировать через Lock, Semaphore, Event, Queue",
        "Работать с таймаутами и отменой задач",
        "Делать HTTP-запросы через aiohttp"
    ])
    
    # Starter code и hints
    starter_code = meta.starter_code or generate_starter_code(sections, meta.topic_name)
    hints = meta.hints if meta.hints else generate_hints(sections)
    
    # Строим контент
    content_blocks = []
    
    # Введение
    intro = build_intro(meta.topic_name, sections)
    content_blocks.append({"type": "text", "content": intro})
    
    # "Чему вы научитесь"
    content_blocks.append({"type": "heading", "level": 2, "content": "Чему вы научитесь"})
    content_blocks.append({
        "type": "list",
        "ordered": False,
        "items": [f"{obj};" for obj in objectives]
    })
    
    # Основные секции
    for i, section in enumerate(sections):
        prev = sections[i-1] if i > 0 else None
        content_blocks.extend(section_to_blocks(section, prev))
    
    # Завершающие разделы
    content_blocks.extend(build_ending(meta.topic_name, sections))
    
    # Рендерим Python код
    return render_lesson_python(meta, content_blocks, starter_code, hints, objectives)


def render_lesson_python(meta: LessonMeta, content_blocks: list[dict], starter_code: str, hints: list[str], objectives: list[str]) -> str:
    """Рендерит полный Python файл урока."""
    
    def render_block(block: dict) -> str:
        if block["type"] == "text":
            return '        {"type": "text", "content": ' + json.dumps(block["content"], ensure_ascii=False) + '},'
        elif block["type"] == "heading":
            return '        {"type": "heading", "level": ' + str(block["level"]) + ', "content": ' + json.dumps(block["content"], ensure_ascii=False) + '},'
        elif block["type"] == "code":
            return '        {"type": "code", "language": ' + json.dumps(block["language"]) + ', "content": ' + json.dumps(block["content"], ensure_ascii=False) + '},'
        elif block["type"] == "list":
            items = ", ".join(json.dumps(item, ensure_ascii=False) for item in block["items"])
            ordered = "True" if block.get("ordered") else "False"
            return '        {"type": "list", "ordered": ' + ordered + ', "items": [' + items + ']},'
        elif block["type"] == "table":
            headers = ", ".join(json.dumps(h, ensure_ascii=False) for h in block["headers"])
            rows = ",\n            ".join(
                "[" + ", ".join(json.dumps(c, ensure_ascii=False) for c in row) + "]"
                for row in block["rows"]
            )
            return '        {"type": "table", "headers": [' + headers + '], "rows": [\n            ' + rows + '\n        ]},'
        elif block["type"] == "callout":
            style = json.dumps(block["style"])
            title = json.dumps(block["title"])
            content = json.dumps(block["content"])
            return '        {"type": "callout", "style": ' + style + ', "title": ' + title + ', "content": ' + content + '},'
        return ""
    
    content_str = "\n".join(render_block(b) for b in content_blocks)
    
    starter_json = json.dumps(starter_code, ensure_ascii=False)
    hints_str = ", ".join(json.dumps(h, ensure_ascii=False) for h in hints)
    tags_str = ", ".join(json.dumps(t, ensure_ascii=False) for t in meta.tags)
    objectives_str = ", ".join(json.dumps(o, ensure_ascii=False) for o in objectives)
    
    # Строим шаблон
    header = '"""Урок ' + meta.name + ' курса ' + meta.language.upper() + '."""\n\nfrom textwrap import dedent\n\n\ndef code(text: str) -> str:\n    return dedent(text).strip("\\n")\n\n\nLESSON = {\n'
    
    fields = [
        '    "language": ' + json.dumps(meta.language),
        '    "program_order": ' + str(meta.program_order),
        '    "topic_order": ' + str(meta.topic_order),
        '    "name": ' + json.dumps(meta.name),
        '    "slug": ' + json.dumps(meta.slug),
        '    "short_description": ' + json.dumps(meta.short_description, ensure_ascii=False),
        '    "topic_name": ' + json.dumps(meta.topic_name, ensure_ascii=False),
        '    "topic_description": ' + json.dumps(meta.topic_description, ensure_ascii=False),
        '    "learning_objectives": [' + objectives_str + ']',
        '    "estimated_minutes": ' + str(meta.estimated_minutes),
        '    "xp_reward": ' + str(meta.xp_reward),
        '    "difficulty": ' + json.dumps(meta.difficulty),
        '    "tags": [' + tags_str + ']',
        '    "starter_code": code(' + json.dumps(starter_code, ensure_ascii=False) + ')',
        '    "hints": [' + hints_str + ']',
        '    "content": [\n' + content_str + '\n    ]\n}'
    ]
    
    return header + ',\n'.join(fields) + '\n'


def main():
    source_path = Path("/Users/xiip.shk/работа/Kernify-lesson/обучение питон/19_Асинхронность.txt")
    output_path = Path("/Users/xiip.shk/работа/Kernify/content_build/lessons/python/2_8.py")
    
    source_text = source_path.read_text(encoding="utf-8")
    lesson_title, sections = parse_source_file(source_path)
    
    objectives = extract_objectives(source_text)
    
    meta = LessonMeta(
        language="python",
        program_order=2,
        topic_order=8,
        name="2.8. Асинхронность",
        slug="python-2-8-асинхронность",
        short_description="Event loop, async/await, задачи, синхронизация, aiohttp и таймауты.",
        topic_name="Асинхронность",
        topic_description="Как писать неблокирующий код с async/await, управлять задачами, синхронизировать доступ и делать HTTP-запросы через aiohttp.",
        learning_objectives=objectives if objectives else [],
        estimated_minutes=40,
        xp_reward=15,
        difficulty="intermediate",
        tags=["python", "asyncio", "асинхронность", "async", "await", "aiohttp"]
    )
    
    lesson_code = generate_lesson_file(meta, sections)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(lesson_code, encoding="utf-8")
    print(f"Сгенерирован: {output_path}")
    print(f"Секций: {len(sections)}")
    print(f"Код-блоков в исходнике: {sum(len(s.code_blocks) for s in sections)}")


if __name__ == "__main__":
    main()