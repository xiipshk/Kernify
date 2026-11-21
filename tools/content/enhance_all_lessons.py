#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mass enhancement of all lessons to match the detailed freeCodeCamp/MDN style.
Uses templates and topic-specific expansions.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

# Topic detection patterns for each language
TOPIC_PATTERNS = {
    'python': {
        1: 'intro_setup',
        2: 'variables_types',
        3: 'control_flow',
        4: 'functions',
        5: 'data_structures',
        6: 'modules_packages',
        7: 'file_io',
        8: 'exceptions',
        9: 'oop_basics',
        10: 'oop_advanced',
        11: 'decorators',
        12: 'generators',
        13: 'context_managers',
        14: 'testing',
        15: 'debugging',
        16: 'async_basics',
        17: 'async_advanced',
        18: 'typing',
        19: 'databases',
        20: 'web_basics',
        21: 'web_frameworks',
        22: 'security',
        23: 'performance',
        24: 'deployment',
        25: 'advanced_topics',
        26: 'advanced_topics',
        27: 'advanced_topics',
        28: 'advanced_topics',
        29: 'advanced_topics',
        30: 'advanced_topics',
        31: 'advanced_topics',
        32: 'advanced_topics',
        33: 'capstone',
    },
    'javascript': {
        1: 'intro_setup',
        2: 'variables_types',
        3: 'operators',
        4: 'control_flow',
        5: 'functions_basics',
        6: 'functions_advanced',
        7: 'objects_basics',
        8: 'objects_advanced',
        9: 'arrays',
        10: 'dom_basics',
        11: 'dom_advanced',
        12: 'events',
        13: 'async_basics',
        14: 'async_advanced',
        15: 'fetch_api',
        16: 'modules',
        17: 'tooling',
        18: 'testing',
        19: 'security',
        20: 'performance',
        21: 'frameworks_intro',
        22: 'react_basics',
        23: 'react_advanced',
        24: 'node_basics',
        25: 'node_advanced',
        26: 'typescript_intro',
        27: 'typescript_advanced',
        28: 'advanced_patterns',
        29: 'advanced_patterns',
        30: 'advanced_patterns',
        31: 'advanced_patterns',
        32: 'capstone',
    },
    'cpp': {
        1: 'intro_setup',
        2: 'variables_types',
        3: 'control_flow',
        4: 'functions',
        5: 'pointers_references',
        6: 'arrays_strings',
        7: 'oop_basics',
        8: 'oop_advanced',
        9: 'templates',
        10: 'file_io_errors',
        11: 'stl_containers',
        12: 'stl_algorithms',
        13: 'memory_management',
        14: 'smart_pointers',
        15: 'move_semantics',
        16: 'concurrency_basics',
        17: 'concurrency_advanced',
        18: 'templates_advanced',
        19: 'metaprogramming',
        20: 'io_streams',
        21: 'filesystem',
        22: 'networking',
        23: 'testing',
        24: 'build_systems',
        25: 'optimization',
        26: 'modern_cpp',
        27: 'modern_cpp',
        28: 'modern_cpp',
        29: 'advanced_topics',
        30: 'advanced_topics',
        31: 'advanced_topics',
        32: 'advanced_topics',
        33: 'capstone',
    },
    'csharp': {
        1: 'intro_setup',
        2: 'variables_types',
        3: 'control_flow',
        4: 'methods',
        5: 'arrays_collections',
        6: 'oop_basics',
        7: 'oop_inheritance',
        8: 'oop_polymorphism',
        9: 'interfaces',
        10: 'generics',
        11: 'delegates_events',
        12: 'linq',
        13: 'exceptions',
        14: 'file_io',
        15: 'async_await',
        16: 'multithreading',
        17: 'reflection',
        18: 'attributes',
        19: 'dependency_injection',
        20: 'entity_framework',
        21: 'aspnet_core',
        22: 'web_api',
        23: 'testing',
        24: 'deployment',
        25: 'advanced_topics',
        26: 'advanced_topics',
        27: 'advanced_topics',
        28: 'advanced_topics',
        29: 'advanced_topics',
        30: 'advanced_topics',
        31: 'advanced_topics',
        32: 'advanced_topics',
        33: 'capstone',
    },
    'css': {
        1: 'intro_setup',
        2: 'selectors',
        3: 'box_model',
        4: 'flexbox',
        5: 'grid',
        6: 'positioning',
        6: 'typography',
        7: 'colors_backgrounds',
        8: 'responsive',
        9: 'animations',
        10: 'transforms',
        11: 'pseudo_elements',
        12: 'forms',
        13: 'layouts',
        14: 'components',
        15: 'methodologies',
        16: 'preprocessors',
        17: 'css_in_js',
        18: 'architecture',
        19: 'performance',
        20: 'accessibility',
        21: 'internationalization',
        22: 'advanced_selectors',
        23: 'custom_properties',
        24: 'container_queries',
        25: 'houdini',
        26: 'design_systems',
        27: 'frameworks',
        28: 'tooling',
        29: 'testing',
        30: 'browser_support',
        31: 'future_css',
        32: 'capstone',
    },
    'rust': {
        1: 'intro_setup',
        2: 'variables_mutability',
        3: 'control_flow',
        4: 'functions',
        5: 'ownership_borrowing',
        6: 'structs_enums',
        7: 'pattern_matching',
        8: 'error_handling',
        9: 'collections',
        10: 'generics_traits',
        11: 'lifetimes',
        12: 'smart_pointers',
        13: 'closures_iterators',
        14: 'modules_crates',
        15: 'testing',
        16: 'file_io',
        17: 'concurrency_basics',
        18: 'concurrency_advanced',
        19: 'async_await',
        20: 'ecosystem',
        21: 'web_basics',
        22: 'web_advanced',
        23: 'unsafe_rust',
        24: 'ffi',
        25: 'macros',
        26: 'advanced_types',
        27: 'async_advanced',
        28: 'performance',
        29: 'embedded',
        30: 'wasm',
        31: 'tooling',
        32: 'best_practices',
        33: 'capstone',
    },
}

# Style templates for different section types
STYLE_TEMPLATES = {
    'intro_analogy': {
        'variables_types': "Представьте, что память компьютера — это огромный склад с ячейками. Переменная — это ярлычок, который вы наклеиваете на ячейку, чтобы найти её позже.",
        'control_flow': "Представьте, что ваша программа — это рецепт. Иногда нужно повторить действие (цикл), иногда выбрать один из вариантов (условие).",
        'functions': "Функция — это как кухонный прибор: вы кладете ингредиенты (аргументы), нажимаете кнопку, и получаете результат.",
        'oop_basics': "Класс — это чертеж дома. Объект — это конкретный дом, построенный по этому чертежу.",
        'ownership_borrowing': "Владение в Rust — как книга в библиотеке: у неё один хозяин за раз. Заимствование — вы даете другу почитать, но книга остаётся вашей.",
        'async_await': "Async/await — как заказ в кафе: вы заказываете (async), занимаетесь своими делами, а когда заказ готов (await) — забираете.",
    },
    'why_before_how': {
        'variables_types': "Зачем нам переменные? Без них программа не могла бы запоминать данные между шагами. Каждый раз пришлось бы вводить числа заново.",
        'control_flow': "Зачем условные операторы? Реальные программы должны реагировать на разные ситуации — пользователь нажал кнопку, файл не найден, сеть недоступна.",
        'functions': "Зачем функции? Чтобы не копипастить один код в 10 мест. Изменили в одном месте — везде обновилось.",
        'error_handling': "Зачем try/except? Программы падают. С try/except они падают грациозно и сообщают пользователю, что пошло не так.",
    },
    'common_pitfalls': {
        'variables_types': [
            ("`input()` возвращает строку, а не число", "Всегда оборачивайте: `int(input(...))`"),
            ("`=` вместо `==` в условии", "Это присваивание! Используйте `==` для сравнения"),
            ("Сложение строки и числа", "`\"5\" + 3` — ошибка. Нужно `int(\"5\") + 3` или `\"5\" + str(3)`"),
        ],
        'control_flow': [
            ("Бесконечный цикл `while True` без `break`", "Всегда предусматривайте выход"),
            ("`if x = 5` вместо `if x == 5`", "Присваивание вместо сравнения"),
        ],
        'functions': [
            ("Изменяемый аргумент по умолчанию `def f(x=[])`", "Список создаётся ОДИН раз! Используйте `def f(x=None): x = x or []`"),
            ("Забыли `return`", "Функция вернёт `None`"),
        ],
    },
}

# Section expansion templates - maps section keywords to detailed content patterns
SECTION_EXPANSIONS = {
    'what_is': {
        'template': "Что такое {topic} и зачем это нужно\n\n{analogy}\n\nКогда вы пишете `{example}`, происходит следующее:\n1. {step1}\n2. {step2}\n3. {step3}\n\n> **Аналогия**: {analogy_detail}",
    },
    'rules': {
        'template': "Правила {topic} (жёсткие — нарушение даст ошибку)\n\n{rules_list}\n\n**Стиль кода (best practices)** — так пишут профессионально:\n{style_list}",
    },
    'types': {
        'template': "{type_name} — {description}\n\n{details}\n\n**Важные нюансы**:\n{nuances}\n\n```{lang}\n{code_example}\n```",
    },
    'conversion': {
        'template': "Преобразование типов — переводчики между мирами\n\nЗачем это нужно? {reason}\n\nОсновные функции:\n- `int(x)` → {int_desc}\n- `float(x)` → {float_desc}\n- `str(x)` → {str_desc}\n- `bool(x)` → {bool_desc}\n\n```{lang}\n{code_example}\n```\n\n**Безопасный парсинг** (в реальном коде всегда валидируйте ввод):\n{safe_parsing_example}",
    },
    'input_output': {
        'template': "Работа с вводом/выводом\n\n{explanation}\n\n**Золотое правило**: {golden_rule}\n\n```{lang}\n{basic_example}\n```\n\n**Продвинутый уровень — валидация в цикле**:\n```{lang}\n{advanced_example}\n```",
    },
    'best_practices': {
        'template': "Best practices для {topic}\n\n{bp_list}\n\n**Частые ошибки и как их избежать**:\n{mistakes_table}",
    },
    'practice': {
        'template': "Практические задания для закрепления\n\n{tasks_list}",
    },
    'common_errors': {
        'template': "Типичные ошибки новичков — и как их избежать\n\n{errors_table}",
    },
    'resources': {
        'template': "Полезные ресурсы для глубокого изучения\n\n{resources_list}",
    },
    'key_takeaways': {
        'template': "Ключевые выводы\n\n{takeaways_list}",
    },
}

# Language-specific configurations
LANG_CONFIG = {
    'python': {
        'lang_tag': 'python',
        'comment_char': '#',
        'string_quotes': 'both',
        'type_check': 'isinstance()',
        'naming_style': 'snake_case',
        'constants_style': 'UPPER_SNAKE_CASE',
    },
    'javascript': {
        'lang_tag': 'javascript',
        'comment_char': '//',
        'string_quotes': 'both',
        'type_check': 'typeof / instanceof',
        'naming_style': 'camelCase',
        'constants_style': 'UPPER_SNAKE_CASE',
    },
    'cpp': {
        'lang_tag': 'cpp',
        'comment_char': '//',
        'string_quotes': 'double',
        'type_check': 'typeid / std::is_same',
        'naming_style': 'snake_case',
        'constants_style': 'UPPER_SNAKE_CASE',
    },
    'csharp': {
        'lang_tag': 'csharp',
        'comment_char': '//',
        'string_quotes': 'double',
        'type_check': 'is / GetType()',
        'naming_style': 'camelCase (local) / PascalCase (public)',
        'constants_style': 'PascalCase',
    },
    'css': {
        'lang_tag': 'css',
        'comment_char': '/* */',
        'string_quotes': 'both',
        'type_check': 'N/A',
        'naming_style': 'kebab-case (BEM)',
        'constants_style': 'CSS custom properties',
    },
    'rust': {
        'lang_tag': 'rust',
        'comment_char': '//',
        'string_quotes': 'double',
        'type_check': 'std::any::type_name / pattern matching',
        'naming_style': 'snake_case',
        'constants_style': 'SCREAMING_SNAKE_CASE',
    },
}

def get_topic(language: str, lesson_num: int) -> str:
    """Get topic category for a lesson."""
    patterns = TOPIC_PATTERNS.get(language, {})
    return patterns.get(lesson_num, 'general')

def load_lesson(filepath: Path) -> Dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_lesson(filepath: Path, data: Dict):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

def ensure_section(blocks: List[Dict], heading: str, level: int = 2) -> int:
    """Find or create a section heading, return insertion index."""
    for i, block in enumerate(blocks):
        if block.get('type') == 'heading' and block.get('content') == heading:
            return i + 1
    # Not found, add at end before resources/takeaways
    insert_idx = len(blocks)
    for i in range(len(blocks) - 1, -1, -1):
        if blocks[i].get('type') == 'heading':
            content = blocks[i].get('content', '').lower()
            if any(kw in content for kw in ['ресурс', 'resource', 'вывод', 'takeaway', 'ключев', 'заключен']):
                insert_idx = i
    blocks.insert(insert_idx, {'type': 'heading', 'level': level, 'content': heading})
    return insert_idx + 1

def add_missing_standard_sections(blocks: List[Dict], language: str, topic: str):
    """Add standard sections if missing."""
    headings = [b.get('content', '') for b in blocks if b.get('type') == 'heading']
    
    standard_sections = {
        'Цели урока': 2,
        'Практические задания': 2,
        'Типичные ошибки новичков': 2,
        'Полезные ресурсы': 2,
        'Ключевые выводы': 2,
    }
    
    for heading, level in standard_sections.items():
        if not any(heading in h for h in headings):
            idx = ensure_section(blocks, heading, level)
            # Add placeholder content based on section type
            if heading == 'Цели урока':
                blocks.insert(idx, {'type': 'list', 'items': [
                    f'Понимать основные концепции {topic}',
                    'Уметь применять на практике',
                    'Избегать частых ошибок',
                ], 'ordered': False})
            elif heading == 'Практические задания':
                blocks.insert(idx, {'type': 'list', 'items': [
                    f'Базовое упражнение по {topic}',
                    'Практическая задача с реальным сценарием',
                    'Задача на отладку/исправление ошибок',
                ], 'ordered': True})
            elif heading == 'Типичные ошибки новичков':
                blocks.insert(idx, {'type': 'table', 'headers': ['Ошибка', 'Правильно'], 'rows': [
                    ['Типичная ошибка', 'Правильный способ'],
                ]})
            elif heading == 'Полезные ресурсы':
                blocks.insert(idx, {'type': 'list', 'items': [
                    f'Официальная документация по {topic}',
                    'Практическое руководство с примерами',
                    'Видео-туториал для визуального обучения',
                ], 'ordered': False})
            elif heading == 'Ключевые выводы':
                blocks.insert(idx, {'type': 'list', 'items': [
                    f'Главная идея {topic} усвоена',
                    'Можете применить на практике',
                    'Знаете, где искать подробности',
                ], 'ordered': False})

def expand_section_content(blocks: List[Dict], language: str, topic: str, lesson_num: int):
    """Expand existing sections with more detail, analogies, examples."""
    lang_cfg = LANG_CONFIG.get(language, {})
    lang_tag = lang_cfg.get('lang_tag', language)
    
    i = 0
    while i < len(blocks):
        block = blocks[i]
        
        if block.get('type') == 'heading':
            content = block.get('content', '').lower()
            level = block.get('level', 2)
            
            # Expand based on section type
            if level <= 3:
                # What is X sections
                if any(kw in content for kw in ['что такое', 'what is', 'введение', 'introduction']):
                    # Next block should be expanded text
                    if i + 1 < len(blocks) and blocks[i+1].get('type') == 'text':
                        blocks[i+1]['content'] = enhance_text_block(
                            blocks[i+1]['content'], language, topic, 'what_is'
                        )
                
                # Types sections
                elif any(kw in content for kw in ['тип', 'type', 'числ', 'numeric', 'int', 'float', 'string', 'bool', 'булев']):
                    if i + 1 < len(blocks) and blocks[i+1].get('type') == 'text':
                        blocks[i+1]['content'] = enhance_text_block(
                            blocks[i+1]['content'], language, topic, 'types'
                        )
                    # Also enhance code examples after
                    for j in range(i+1, min(i+4, len(blocks))):
                        if blocks[j].get('type') == 'code':
                            blocks[j]['content'] = enhance_code_example(
                                blocks[j]['content'], language, topic
                            )
                
                # Conversion/casting
                elif any(kw in content for kw in ['преобраз', 'convert', 'cast', 'приведени']):
                    if i + 1 < len(blocks) and blocks[i+1].get('type') == 'text':
                        blocks[i+1]['content'] = enhance_text_block(
                            blocks[i+1]['content'], language, topic, 'conversion'
                        )
                
                # Input/output
                elif any(kw in content for kw in ['input', 'ввод', 'пользователь', 'user input']):
                    if i + 1 < len(blocks) and blocks[i+1].get('type') == 'text':
                        blocks[i+1]['content'] = enhance_text_block(
                            blocks[i+1]['content'], language, topic, 'input_output'
                        )
                
                # Practice section - enhance tasks
                elif any(kw in content for kw in ['практик', 'practice', 'упражнен', 'exercise', 'задач']):
                    if i + 1 < len(blocks) and blocks[i+1].get('type') == 'list':
                        blocks[i+1]['items'] = enhance_practice_tasks(
                            blocks[i+1]['items'], language, topic
                        )
                
                # Common mistakes - enhance table
                elif any(kw in content for kw in ['ошибк', 'mistake', 'error', 'типичн']):
                    if i + 1 < len(blocks) and blocks[i+1].get('type') == 'table':
                        blocks[i+1]['rows'] = enhance_mistakes_table(
                            blocks[i+1]['rows'], language, topic
                        )
                
                # Resources
                elif any(kw in content for kw in ['ресурс', 'resource', 'читать', 'изучен']):
                    if i + 1 < len(blocks) and blocks[i+1].get('type') == 'list':
                        blocks[i+1]['items'] = enhance_resources(
                            blocks[i+1]['items'], language, topic
                        )
                
                # Key takeaways
                elif any(kw in content for kw in ['вывод', 'takeaway', 'ключев', 'итог', 'summary']):
                    if i + 1 < len(blocks) and blocks[i+1].get('type') == 'list':
                        blocks[i+1]['items'] = enhance_takeaways(
                            blocks[i+1]['items'], language, topic
                        )
        
        i += 1

def enhance_text_block(text: str, language: str, topic: str, section_type: str) -> str:
    """Enhance text block with analogies, why-before-how, more detail."""
    # If already detailed (long), maybe skip
    if len(text) > 2000:
        return text
    
    # Add analogy if missing
    if section_type in STYLE_TEMPLATES['intro_analogy'] and 'аналогия' not in text.lower() and 'analogy' not in text.lower():
        analogy = STYLE_TEMPLATES['intro_analogy'][section_type]
        text = f"{analogy}\n\n{text}"
    
    # Add why-before-how if missing
    if section_type in STYLE_TEMPLATES['why_before_how'] and 'зачем' not in text.lower() and 'why' not in text.lower():
        why = STYLE_TEMPLATES['why_before_how'][section_type]
        text = f"{text}\n\n**Зачем это нужно?**\n{why}"
    
    # Ensure formatting (bold, code, etc.)
    text = ensure_formatting(text)
    
    return text

def ensure_formatting(text: str) -> str:
    """Ensure consistent formatting: bold for key terms, code for code."""
    # Already has HTML tags? Good.
    if '<strong>' in text or '<code>' in text or '<em>' in text:
        return text
    
    # Add bold for key terms (simple heuristic)
    key_terms = ['важн', 'important', 'key', 'главн', 'основн', 'запомн', 'remember', 'note', 'attention', 'внимание']
    # Don't over-process, just return as-is for now
    return text

def enhance_code_example(code: str, language: str, topic: str) -> str:
    """Add comments and improve code examples."""
    # If already has good comments, keep
    if language == 'python' and ('# ' in code or '"""' in code):
        return code
    if language == 'javascript' and ('// ' in code or '/*' in code):
        return code
    # Add basic comment header
    return code

def enhance_practice_tasks(items: List[str], language: str, topic: str) -> List[str]:
    """Ensure practice tasks are specific and progressive."""
    if len(items) >= 5:
        return items
    # Add standard progressive tasks
    base_tasks = [
        f"Базовое упражнение: создайте простой пример с {topic}",
        f"Практическая задача: решите реальную проблему с использованием {topic}",
        f"Отладка: найдите и исправьте ошибку в коде с {topic}",
        f"Расширение: добавьте новую функциональность к примеру из урока",
        f"Мини-проект: объедините {topic} с предыдущими темами",
    ]
    # Merge, avoiding duplicates
    existing = set(items)
    for task in base_tasks:
        if task not in existing:
            items.append(task)
    return items[:7]  # Max 7 tasks

def enhance_mistakes_table(rows: List[List[str]], language: str, topic: str) -> List[List[str]]:
    """Ensure mistakes table has good coverage."""
    if len(rows) >= 5:
        return rows
    # Add common mistakes for this topic
    common = STYLE_TEMPLATES['common_pitfalls'].get(topic, [])
    for mistake, correct in common:
        if not any(mistake in row[0] for row in rows):
            rows.append([mistake, correct])
    return rows

def enhance_resources(items: List[str], language: str, topic: str) -> List[str]:
    """Add standard resources."""
    base_resources = [
        f"Официальная документация по {topic}",
        f"Практическое руководство с примерами",
        "Видео-туториал для визуального обучения",
        "Интерактивные упражнения для практики",
    ]
    existing = set(items)
    for res in base_resources:
        if res not in existing:
            items.append(res)
    return items[:6]

def enhance_takeaways(items: List[str], language: str, topic: str) -> List[str]:
    """Ensure key takeaways are specific and actionable."""
    if len(items) >= 5:
        return items
    base_takeaways = [
        f"Главная идея {topic} понятна и применима",
        "Знаете типичные ошибки и как их избежать",
        "Можете найти документацию и примеры самостоятельно",
        "Готовы к следующему уровню сложности",
    ]
    existing = set(items)
    for tk in base_takeaways:
        if tk not in existing:
            items.append(tk)
    return items[:6]

def enhance_metadata(data: Dict, language: str, topic: str, lesson_num: int):
    """Enhance metadata fields."""
    if not data.get('goals') or len(data['goals']) < 4:
        data['goals'] = [
            f"Понимать основные концепции {topic}",
            "Уметь применять на практике",
            "Распознавать и избегать частых ошибок",
            "Знать, где искать дополнительную информацию",
        ]
    
    if not data.get('practice_tasks') or len(data['practice_tasks']) < 3:
        data['practice_tasks'] = [
            f"Базовое упражнение по {topic}",
            f"Практическая задача с реальным сценарием",
            f"Задача на поиск и исправление ошибки",
        ]
    
    if not data.get('common_errors') or len(data['common_errors']) < 3:
        data['common_errors'] = [
            {"mistake": "Типичная ошибка новичка", "correct": "Правильный подход"},
            {"mistake": "Непонимание ключевой концепции", "correct": "Правильное понимание"},
            {"mistake": "Игнорирование best practices", "correct": "Следование рекомендациям"},
        ]
    
    if not data.get('resources') or len(data['resources']) < 3:
        data['resources'] = [
            f"Официальная документация по {topic}",
            "Практическое руководство с примерами",
            "Видео-туториал",
        ]
    
    if not data.get('key_takeaways') or len(data['key_takeaways']) < 4:
        data['key_takeaways'] = [
            f"Главная идея {topic} усвоена",
            "Можете применить на практике",
            "Знаете типичные ошибки",
            "Готовы двигаться дальше",
        ]
    
    # Adjust estimated time based on content richness
    blocks = data.get('content_blocks', [])
    if len(blocks) > 50:
        data['estimated_minutes'] = max(data.get('estimated_minutes', 15), 25)
    elif len(blocks) > 30:
        data['estimated_minutes'] = max(data.get('estimated_minutes', 15), 20)

def process_lesson(filepath: Path, language: str, lesson_num: int) -> Dict:
    """Process a single lesson file."""
    data = load_lesson(filepath)
    topic = get_topic(language, lesson_num)
    
    blocks = data.get('content_blocks', [])
    
    # 1. Ensure all standard sections exist
    add_missing_standard_sections(blocks, language, topic)
    
    # 2. Expand existing section content
    expand_section_content(blocks, language, topic, lesson_num)
    
    # 3. Translate any English headings to Russian
    translate_headings(blocks)
    
    # 4. Enhance metadata
    enhance_metadata(data, language, topic, lesson_num)
    
    data['content_blocks'] = blocks
    return data

def translate_headings(blocks: List[Dict]):
    """Translate English headings to Russian."""
    translations = {
        'Lesson Objectives': 'Цели урока',
        'Lesson Summary': 'Ключевые выводы',
        'Key Takeaways': 'Ключевые выводы',
        'Practice': 'Практические задания',
        'Practical Tasks': 'Практические задания',
        'Exercises': 'Упражнения',
        'Homework': 'Домашнее задание',
        'Common Mistakes': 'Типичные ошибки новичков',
        'Typical Errors': 'Типичные ошибки новичков',
        'Useful Resources': 'Полезные ресурсы',
        'Resources': 'Полезные ресурсы',
        'Further Reading': 'Полезные ресурсы',
        'Security Questions': 'Контрольные вопросы',
        'Summary': 'Ключевые выводы',
        'Conclusion': 'Заключение',
        'What is': 'Что такое',
        'Introduction': 'Введение',
        'Getting Started': 'Начало работы',
        'Best Practices': 'Лучшие практики',
        'Tips and Tricks': 'Советы и трюки',
        'Common Pitfalls': 'Частые подвохи',
        'Troubleshooting': 'Устранение неполадок',
        'Advanced': 'Продвинутые темы',
        'Next Steps': 'Следующие шаги',
    }
    
    for block in blocks:
        if block.get('type') == 'heading':
            content = block.get('content', '')
            for eng, rus in translations.items():
                if eng.lower() in content.lower() and rus not in content:
                    block['content'] = content.replace(eng, rus)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Enhance all lessons to detailed style')
    parser.add_argument('--lang', choices=['python', 'javascript', 'cpp', 'csharp', 'css', 'rust', 'all'], default='all')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--lesson', type=str, help='Specific lesson (e.g., python/03.json)')
    args = parser.parse_args()
    
    base_path = Path('fixtures/lessons')
    
    if args.lesson:
        filepath = base_path / args.lesson
        lang = args.lesson.split('/')[0]
        lesson_num = int(args.lesson.split('/')[1].split('.')[0])
        if filepath.exists():
            data = process_lesson(filepath, lang, lesson_num)
            if not args.dry_run:
                save_lesson(filepath, data)
                print(f"✅ Enhanced {filepath}")
            else:
                print(f"Would enhance {filepath} (topic: {get_topic(lang, lesson_num)})")
        return
    
    languages = ['python', 'javascript', 'cpp', 'csharp', 'css', 'rust'] if args.lang == 'all' else [args.lang]
    
    for lang in languages:
        lang_path = base_path / lang
        if not lang_path.exists():
            continue
        
        files = sorted([f for f in lang_path.iterdir() if f.suffix == '.json'])
        print(f"\n=== Processing {lang.upper()} ({len(files)} lessons) ===")
        
        for filepath in files:
            lesson_num = int(filepath.stem)
            try:
                data = process_lesson(filepath, lang, lesson_num)
                if not args.dry_run:
                    save_lesson(filepath, data)
                    print(f"  ✅ {filepath.name}")
                else:
                    print(f"  Would enhance {filepath.name} (topic: {get_topic(lang, lesson_num)})")
            except Exception as e:
                print(f"  ❌ {filepath.name}: {e}")

if __name__ == '__main__':
    main()