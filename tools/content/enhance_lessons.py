#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to enhance lessons with missing standard sections and ensure Russian consistency.
Focuses on less detailed languages: C#, JavaScript (early), C++ (missing resources).
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

# Standard section templates in Russian
STANDARD_SECTIONS = {
    'objectives': {
        'heading': 'Цели урока',
        'level': 2,
        'content_template': 'lesson_objectives'
    },
    'common_errors': {
        'heading': 'Типичные ошибки новичков',
        'level': 2,
        'content_template': 'common_errors_table'
    },
    'practice': {
        'heading': 'Практические задания',
        'level': 2,
        'content_template': 'practice_tasks'
    },
    'resources': {
        'heading': 'Полезные ресурсы',
        'level': 2,
        'content_template': 'resources_list'
    },
    'key_takeaways': {
        'heading': 'Ключевые выводы',
        'level': 2,
        'content_template': 'key_takeaways_list'
    }
}

# Language-specific resource URLs
LANGUAGE_RESOURCES = {
    'csharp': {
        'base': 'https://learn.microsoft.com/ru-ru/dotnet/csharp/',
        'resources': [
            '**Microsoft C# Guide** — https://learn.microsoft.com/ru-ru/dotnet/csharp/',
            '**C# Language Reference** — https://learn.microsoft.com/ru-ru/dotnet/csharp/language-reference/',
            '**C# Coding Conventions** — https://learn.microsoft.com/ru-ru/dotnet/csharp/fundamentals/coding-style/coding-conventions',
            '**dotnet/csharplang repo** — https://github.com/dotnet/csharplang'
        ]
    },
    'javascript': {
        'base': 'https://developer.mozilla.org/ru/docs/Web/JavaScript/',
        'resources': [
            '**MDN JavaScript Guide** — https://developer.mozilla.org/ru/docs/Web/JavaScript/Guide',
            '**javascript.info** — https://javascript.info/',
            '**ECMAScript Specification** — https://tc39.es/ecma262/',
            '**Node.js Docs** — https://nodejs.org/ru/docs/'
        ]
    },
    'cpp': {
        'base': 'https://en.cppreference.com/w/',
        'resources': [
            '**cppreference.com** — https://en.cppreference.com/w/',
            '**C++ Core Guidelines** — https://isocpp.github.io/CppCoreGuidelines/',
            '**Modern C++ Tutorial** — https://changkun.de/modern-cpp/',
            '**Jason Turner C++ Weekly** — https://www.youtube.com/c/JasonTurnerCppWeekly'
        ]
    },
    'python': {
        'base': 'https://docs.python.org/3/',
        'resources': [
            '**Python Official Tutorial** — https://docs.python.org/3/tutorial/',
            '**Real Python** — https://realpython.com/',
            '**Python Docs** — https://docs.python.org/3/',
            '**Effective Python** — https://effectivepython.com/'
        ]
    },
    'rust': {
        'base': 'https://doc.rust-lang.org/',
        'resources': [
            '**The Rust Programming Language** — https://doc.rust-lang.org/book/',
            '**Rust by Example** — https://doc.rust-lang.org/rust-by-example/',
            '**Rust Reference** — https://doc.rust-lang.org/reference/',
            '**Rustlings Exercises** — https://github.com/rust-lang/rustlings'
        ]
    },
    'css': {
        'base': 'https://developer.mozilla.org/ru/docs/Web/CSS/',
        'resources': [
            '**MDN CSS Reference** — https://developer.mozilla.org/ru/docs/Web/CSS/Reference',
            '**web.dev Learn CSS** — https://web.dev/learn/css/',
            '**CSS-Tricks** — https://css-tricks.com/',
            '**Can I Use** — https://caniuse.com/'
        ]
    }
}

# Common mistakes templates per language/topic
COMMON_MISTAKES_TEMPLATES = {
    'csharp': {
        'variables': [
            ('`var x;` без инициализации', '`var x = 42;` — `var` требует инициализации'),
            ('`int x = 3.14;` — неявное приведение double к int', '`int x = (int)3.14;` или `int x = 3;`'),
            ('`decimal d = 1.5;` без суффикса M', '`decimal d = 1.5M;` — обязателен суффикс'),
            ('`string s = null; s.Length` — NullReferenceException', 'Использовать `string? s = null; s?.Length` или проверку на null'),
            ('`const` для значений, известных только во время выполнения', 'Использовать `readonly` для полей, инициализируемых в конструкторе'),
        ],
        'control_flow': [
            ('`if (x = 5)` — присваивание вместо сравнения', '`if (x == 5)` — двойное равно для сравнения'),
            ('`switch` без `break` — fall-through', 'Всегда добавлять `break` или использовать `switch` выражения (C# 8+)'),
            ('`for (int i = 0; i <= arr.Length; i++)` — выход за границы', '`for (int i = 0; i < arr.Length; i++)` — строго меньше'),
        ],
        'oop': [
            ('Наследование вместо композиции', '"Has-a" вместо "Is-a": используйте композицию, когда объект *содержит* другой'),
            ('`virtual` без `override` в потомке', 'Всегда используйте `override` для переопределения виртуальных методов'),
            ('Публичные поля вместо свойств', 'Используйте свойства (`public int Age { get; set; }`) для инкапсуляции'),
        ],
        'collections': [
            ('Изменение коллекции во время `foreach`', 'Используйте `for` или создайте копию: `foreach (var x in list.ToList())`'),
            ('`List<T>` для частых вставок/удалений в начале', 'Используйте `LinkedList<T>` или `Queue<T>`/`Stack<T>`'),
        ],
        'async': [
            ('`.Result` или `.Wait()` — блокировка потока', 'Используйте `await` для асинхронного ожидания'),
            ('`async void` методы (кроме event handlers)', 'Возвращайте `Task` или `Task<T>` для обработки ошибок'),
        ]
    },
    'javascript': {
        'variables': [
            ('`var` в современном коде', 'Используйте `const` по умолчанию, `let` если нужно переназначение'),
            ('`const obj = {}; obj = {};` — ошибка переназначения', '`const` защищает ссылку, не содержимое: `obj.prop = "new"` — OK'),
            ('`let x;` — undefined, но `const x;` — ошибка', '`const` требует инициализацию при объявлении'),
        ],
        'types': [
            ('`typeof null === "object"` — баг JS', 'Проверяйте: `value === null` или `value == null`'),
            ('`[] == ![]` → true — приведение типов', 'Используйте строгое сравнение `===` и `!==`'),
            ('`parseInt("08")` → 0 (в старых версиях — октальная)', 'Всегда указывайте основание: `parseInt("08", 10)`'),
        ],
        'functions': [
            ('Стрелочная функция не имеет `this`', 'Для методов объектов используйте обычные функции или `bind`'),
            ('`forEach` не ждёт `await`', 'Используйте `for...of` с `await` или `Promise.all(map(...))`'),
        ]
    },
    'cpp': {
        'basics': [
            ('`using namespace std;` в заголовочных файлах', 'Загрязняет глобальное пространство имён — только в .cpp'),
            ('`void main()`', '`int main()` — стандарт требует возврат int'),
            ('Забытый `#include <...>`', 'Всегда подключайте нужные заголовки перед использованием'),
        ],
        'memory': [
            ('Утечка памяти: `new` без `delete`', 'Используйте умные указатели `std::unique_ptr`, `std::shared_ptr`'),
            ('Доступ к удалённой памяти (use-after-free)', 'RAII и умные указатели предотвращают это автоматически'),
            ('Двойное освобождение (double free)', 'Умные указатели гарантируют единственное освобождение'),
        ],
        'templates': [
            ('Код шаблонов в .cpp файле', 'Реализация шаблонов должна быть в заголовочном файле'),
            ('`std::vector<T>` — копирование при передаче по значению', 'Передавайте по константной ссылке: `const std::vector<T>&`'),
        ]
    }
}

# Practice task templates per language
PRACTICE_TEMPLATES = {
    'csharp': {
        'variables': [
            'Объявите переменные всех базовых типов (`int`, `double`, `decimal`, `bool`, `char`, `string`) и выведите их с `GetType()`',
            'Создайте `decimal` для цены товара, `int` для количества, вычислите сумму с точностью до копейки',
            'Поэкспериментируйте с `int.Parse`, `TryParse`, `Convert.ToInt32` на некорректных строках',
            'Напишите программу: запрашивает имя и возраст, выводит «Привет, {name}! Через 10 лет вам будет {age+10}»',
            'Используя `checked`, вызовите переполнение `int` и перехватите `OverflowException`',
        ],
        'control_flow': [
            'Напишите программу "FizzBuzz": числа от 1 до 100, кратные 3 — "Fizz", 5 — "Buzz", 3 и 5 — "FizzBuzz"',
            'Реализуйте калькулятор через `switch` выражение (C# 8+): два числа и оператор (+, -, *, /)',
            'Найдите сумму чётных чисел от 1 до N с помощью `for` и `while` — сравните производительность',
        ],
        'oop': [
            'Создайте базовый класс `Animal` с абстрактным методом `Speak()`, наследников `Dog`, `Cat`, `Bird`',
            'Реализуйте интерфейс `IComparable<T>` для класса `Student` (сравнение по GPA)',
            'Создайте класс `BankAccount` с свойствами `Balance` (только чтение снаружи), методами `Deposit`, `Withdraw`',
        ],
        'collections': [
            'Заполните `List<int>` числами 1..100, удалите все нечётные, выведите результат',
            'Создайте `Dictionary<string, int>` для подсчёта слов в тексте',
            'Используйте `HashSet<int>` для удаления дубликатов из массива',
        ]
    },
    'javascript': {
        'variables': [
            'Создайте переменные всех примитивных типов, проверьте `typeof`',
            'Поэкспериментируйте с шаблонными строками: интерполяция, многострочность',
            'Проверьте: `[] == ![]`, `[] == false`, `[] == true`, `{} == {}`',
            'Найдите 5 способов преобразовать строку в число',
            'Создайте объект, скопируйте его spread-оператором, измените копию, проверьте оригинал',
        ],
        'functions': [
            'Напишите функцию `sum(...args)`, принимающую любое количество аргументов и возвращающую сумму',
            'Создайте замыкание: функция-счётчик, увеличивающая значение при каждом вызове',
            'Реализуйте `debounce` и `throttle` для ограничения частоты вызовов',
        ],
        'async': [
            'Напишите функцию `fetchWithTimeout(url, ms)`, отменяющая запрос через `ms` миллисекунд',
            'Последовательно загрузите 3 URL через `fetch`, соберите результаты в массив',
            'Параллельно загрузите 5 URL с `Promise.all`, обработайте ошибки через `Promise.allSettled`',
        ]
    }
}

def get_lesson_topic_from_filename(filename: str, language: str) -> str:
    """Determine lesson topic category from filename/number."""
    num = int(filename.split('.')[0])
    
    if language == 'csharp':
        if num <= 2: return 'variables'
        elif num <= 5: return 'control_flow'
        elif num <= 11: return 'oop'
        elif num <= 16: return 'collections'
        elif num <= 22: return 'async'
        else: return 'advanced'
    elif language == 'javascript':
        if num <= 2: return 'variables'
        elif num <= 6: return 'types'
        elif num <= 12: return 'functions'
        elif num <= 18: return 'async'
        elif num <= 24: return 'dom'
        else: return 'advanced'
    elif language == 'cpp':
        if num <= 3: return 'basics'
        elif num <= 10: return 'memory'
        elif num <= 20: return 'templates'
        else: return 'advanced'
    return 'general'

def generate_objectives(language: str, topic: str, lesson_data: Dict) -> List[str]:
    """Generate learning objectives based on lesson content."""
    objectives_map = {
        'csharp': {
            'variables': [
                'Понимать объявление переменных: явные типы и `var`',
                'Знать типы значений (int, double, decimal, bool, char) и их особенности',
                'Уметь преобразовывать типы: неявные, явные, Parse/TryParse, checked',
                'Работать с nullable типами и операторами `??`, `?.`',
            ],
            'control_flow': [
                'Использовать условные операторы: `if`, `else if`, `switch` выражения',
                'Работать с циклами: `for`, `foreach`, `while`, `do-while`',
                'Применять `break`, `continue`, `return` для управления потоком',
            ],
            'oop': [
                'Создавать классы, структуры, записи (records)',
                'Реализовывать наследование, полиморфизм, абстрактные классы',
                'Использовать интерфейсы, свойства, индексаторы, операторы',
                'Понимать инкапсуляцию: модификаторы доступа, readonly, init',
            ],
            'collections': [
                'Работать с List, Dictionary, HashSet, Queue, Stack',
                'Использовать LINQ для фильтрации, проекции, группировки',
                'Понимать разницу между массивами и коллекциями',
            ],
            'async': [
                'Писать асинхронные методы с `async`/`await`',
                'Работать с `Task`, `Task<T>`, `ValueTask`',
                'Использовать `Task.WhenAll`, `WhenAny`, `Parallel.ForEachAsync`',
                'Обрабатывать отмену через `CancellationToken`',
            ]
        },
        'javascript': {
            'variables': [
                'Понимать `let`, `const`, `var` и области видимости',
                'Знать все 8 примитивных типов (включая `bigint`, `symbol`)',
                'Работать с приведением типов: явным и неявным',
                'Использовать `??`, `?.`, `??=` для работы с null/undefined',
            ],
            'types': [
                'Работать со строками: шаблонные строки, методы ES2023+',
                'Понимать числа: `number`, `bigint`, специальные значения',
                'Использовать `Array`, `Map`, `Set`, `WeakMap`, `WeakSet`',
            ],
            'functions': [
                'Создавать функции: объявления, выражения, стрелочные',
                'Работать с замыканиями, `this`, `bind`, `call`, `apply`',
                'Понимать параметры по умолчанию, rest, spread',
            ],
            'async': [
                'Использовать `Promise`, `async`/`await`, `try/catch`',
                'Работать с `fetch`, `AbortController`, таймаутами',
                'Применять `Promise.all`, `allSettled`, `race`, `any`',
            ]
        }
    }
    
    lang_map = objectives_map.get(language, {})
    return lang_map.get(topic, [
        'Понимать основные концепции урока',
        'Уметь применять изученные конструкции на практике',
        'Избегать типичных ошибок новичков',
    ])

def generate_key_takeaways(language: str, topic: str) -> List[str]:
    """Generate key takeaways for a lesson."""
    takeaways_map = {
        'csharp': {
            'variables': [
                '`var` — не "вариантный" тип, а вывод типа компилятором (требует инициализации)',
                '`decimal` — для денег, `double` — для научных вычислений, `float` — редко',
                '`int.Parse` бросает исключение, `TryParse` — безопасный способ',
                'Nullable типы (`int?`) позволяют value types быть null, `??` — coalescing',
            ],
            'control_flow': [
                '`switch` выражения (C# 8+) — выразительные и безопасные (нет fall-through)',
                '`foreach` — только для чтения, для изменения используйте `for` или `ToList()`',
                '`break` прерывает цикл, `continue` — переход к следующей итерации',
            ],
            'oop': [
                'Класс — ссылочный тип, структура — значимый (value type)',
                '`record` (C# 9+) — неизменяемые типы данных с value-семантикой',
                'Интерфейсы определяют контракт, реализация — в классах',
                'Композиция (`has-a`) часто лучше наследования (`is-a`)',
            ]
        },
        'javascript': {
            'variables': [
                '`const` по умолчанию, `let` при необходимости, `var` — никогда',
                '`typeof null === "object"` — известный баг, проверяйте `value === null`',
                'Приведение типов неожиданно: используйте `===` и `Number()`/`String()` явно',
                '`??` — только для null/undefined, `||` — для любого falsy',
            ],
            'functions': [
                'Стрелочные функции не имеют своего `this` — берут из лексического окружения',
                'Замыкание — функция + её лексическое окружение',
                '`async` функция всегда возвращает `Promise`',
            ]
        }
    }
    
    lang_map = takeaways_map.get(language, {})
    return lang_map.get(topic, [
        'Основные концепции усвоены',
        'Можно применить на практике',
    ])

def has_section(blocks: List[Dict], section_heading: str) -> bool:
    """Check if a section with given heading exists."""
    for block in blocks:
        if block.get('type') == 'heading' and section_heading in block.get('content', ''):
            return True
    return False

def find_section_end(blocks: List[Dict], start_idx: int) -> int:
    """Find the index where the next section starts."""
    for i in range(start_idx + 1, len(blocks)):
        if blocks[i].get('type') == 'heading' and blocks[i].get('level', 3) <= 2:
            return i
    return len(blocks)

def enhance_lesson(filepath: Path, language: str, dry_run: bool = False) -> Dict[str, Any]:
    """Enhance a single lesson file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    blocks = data.get('content_blocks', [])
    filename = filepath.name
    topic = get_lesson_topic_from_filename(filename, language)
    
    changes = []
    
    # 1. Ensure "Цели урока" section exists (after first heading)
    if not has_section(blocks, 'Цели урока') and not has_section(blocks, 'Lesson Objectives'):
        objectives = generate_objectives(language, topic, data)
        # Find first heading (usually lesson title or "Lesson Objectives")
        insert_idx = 1
        for i, block in enumerate(blocks):
            if block.get('type') == 'heading' and block.get('level') == 2:
                insert_idx = i + 1
                break
        
        new_blocks = [
            {'type': 'heading', 'level': 2, 'content': 'Цели урока'},
            {'type': 'list', 'items': objectives, 'ordered': False}
        ]
        blocks[insert_idx:insert_idx] = new_blocks
        changes.append('Added "Цели урока" section')
    
    # 2. Ensure "Типичные ошибки новичков" section exists (before practice/resources)
    if not has_section(blocks, 'Типичные ошибки') and not has_section(blocks, 'Common mistakes'):
        mistakes = COMMON_MISTAKES_TEMPLATES.get(language, {}).get(topic, [])
        if mistakes:
            # Find good insertion point - before practice or resources or at end
            insert_idx = len(blocks)
            for i, block in enumerate(blocks):
                if block.get('type') == 'heading':
                    content = block.get('content', '').lower()
                    if any(kw in content for kw in ['практик', 'practice', 'ресурс', 'resource', 'полезн', 'домашн', 'homework']):
                        insert_idx = i
                        break
            
            new_blocks = [
                {'type': 'heading', 'level': 2, 'content': 'Типичные ошибки новичков'},
                {'type': 'table', 'headers': ['Ошибка', 'Правильно'], 'rows': mistakes}
            ]
            blocks[insert_idx:insert_idx] = new_blocks
            changes.append('Added "Типичные ошибки новичков" section')
    
    # 3. Ensure "Практические задания" section exists
    if not has_section(blocks, 'Практические задания') and not has_section(blocks, 'Practice'):
        practice_tasks = PRACTICE_TEMPLATES.get(language, {}).get(topic, [])
        if practice_tasks:
            insert_idx = len(blocks)
            for i, block in enumerate(blocks):
                if block.get('type') == 'heading':
                    content = block.get('content', '').lower()
                    if any(kw in content for kw in ['ресурс', 'resource', 'полезн', 'домашн', 'homework', 'ключев', 'takeaway']):
                        insert_idx = i
                        break
            
            new_blocks = [
                {'type': 'heading', 'level': 2, 'content': 'Практические задания'},
                {'type': 'list', 'items': practice_tasks, 'ordered': True}
            ]
            blocks[insert_idx:insert_idx] = new_blocks
            changes.append('Added "Практические задания" section')
    
    # 4. Ensure "Полезные ресурсы" section exists
    if not has_section(blocks, 'Полезные ресурсы') and not has_section(blocks, 'Useful resources') and not has_section(blocks, 'Resources'):
        resources = LANGUAGE_RESOURCES.get(language, {}).get('resources', [])
        if resources:
            insert_idx = len(blocks)
            for i, block in enumerate(blocks):
                if block.get('type') == 'heading':
                    content = block.get('content', '').lower()
                    if any(kw in content for kw in ['ключев', 'takeaway', 'итог', 'summary']):
                        insert_idx = i
                        break
            
            new_blocks = [
                {'type': 'heading', 'level': 2, 'content': 'Полезные ресурсы'},
                {'type': 'list', 'items': resources, 'ordered': False}
            ]
            blocks[insert_idx:insert_idx] = new_blocks
            changes.append('Added "Полезные ресурсы" section')
    
    # 5. Ensure "Ключевые выводы" section exists
    if not has_section(blocks, 'Ключевые выводы') and not has_section(blocks, 'Key takeaways') and not has_section(blocks, 'Lesson Summary'):
        takeaways = generate_key_takeaways(language, topic)
        if takeaways:
            insert_idx = len(blocks)
            
            new_blocks = [
                {'type': 'heading', 'level': 2, 'content': 'Ключевые выводы'},
                {'type': 'list', 'items': takeaways, 'ordered': False}
            ]
            blocks[insert_idx:insert_idx] = new_blocks
            changes.append('Added "Ключевые выводы" section')
    
    # 6. Ensure Russian consistency: replace English headings with Russian
    heading_replacements = {
        'Lesson Objectives': 'Цели урока',
        'Lesson Summary': 'Ключевые выводы',
        'Key Takeaways': 'Ключевые выводы',
        'Practice': 'Практические задания',
        'Practical Tasks': 'Практические задания',
        'Common Mistakes': 'Типичные ошибки новичков',
        'Typical Errors': 'Типичные ошибки новичков',
        'Useful Resources': 'Полезные ресурсы',
        'Resources': 'Полезные ресурсы',
        'Further Reading': 'Полезные ресурсы',
        'Security Questions': 'Контрольные вопросы',
        'Homework': 'Домашнее задание',
        'Exercises': 'Практические задания',
        'Summary': 'Ключевые выводы',
        'Conclusion': 'Заключение',
    }
    
    for block in blocks:
        if block.get('type') == 'heading':
            content = block.get('content', '')
            for eng, rus in heading_replacements.items():
                if eng.lower() in content.lower() and rus not in content:
                    block['content'] = content.replace(eng, rus)
                    changes.append(f'Translated heading: "{eng}" → "{rus}"')
    
    # 7. Update metadata fields
    if not data.get('goals'):
        data['goals'] = generate_objectives(language, topic, data)
        changes.append('Added goals metadata')
    
    if not data.get('common_errors'):
        mistakes = COMMON_MISTAKES_TEMPLATES.get(language, {}).get(topic, [])
        if mistakes:
            data['common_errors'] = [{'mistake': m[0], 'correct': m[1]} for m in mistakes]
            changes.append('Added common_errors metadata')
    
    if not data.get('practice_tasks'):
        practice_tasks = PRACTICE_TEMPLATES.get(language, {}).get(topic, [])
        if practice_tasks:
            data['practice_tasks'] = practice_tasks
            changes.append('Added practice_tasks metadata')
    
    if not data.get('resources'):
        resources = LANGUAGE_RESOURCES.get(language, {}).get('resources', [])
        if resources:
            data['resources'] = resources
            changes.append('Added resources metadata')
    
    if not data.get('key_takeaways'):
        takeaways = generate_key_takeaways(language, topic)
        if takeaways:
            data['key_takeaways'] = takeaways
            changes.append('Added key_takeaways metadata')
    
    # Update content_blocks
    data['content_blocks'] = blocks
    
    if not dry_run and changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
    
    return {
        'file': str(filepath),
        'changes': changes,
        'blocks_count': len(blocks),
        'topic': topic
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Enhance lessons with missing sections')
    parser.add_argument('--lang', choices=['csharp', 'javascript', 'cpp', 'python', 'rust', 'css', 'all'], default='csharp')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--lesson', type=str, help='Specific lesson file (e.g., csharp/01.json)')
    args = parser.parse_args()
    
    base_path = Path('fixtures/lessons')
    
    if args.lesson:
        filepath = base_path / args.lesson
        if filepath.exists():
            result = enhance_lesson(filepath, args.lesson.split('/')[0], args.dry_run)
            print(f"\n{result['file']}:")
            for change in result['changes']:
                print(f"  + {change}")
            if not result['changes']:
                print("  No changes needed")
        else:
            print(f"File not found: {filepath}")
        return
    
    languages = ['csharp', 'javascript', 'cpp', 'python', 'rust', 'css'] if args.lang == 'all' else [args.lang]
    
    total_changes = 0
    for lang in languages:
        lang_path = base_path / lang
        if not lang_path.exists():
            print(f"Language directory not found: {lang_path}")
            continue
        
        files = sorted([f for f in lang_path.iterdir() if f.suffix == '.json'])
        print(f"\n=== Processing {lang.upper()} ({len(files)} lessons) ===")
        
        for filepath in files:
            result = enhance_lesson(filepath, lang, args.dry_run)
            if result['changes']:
                print(f"  {filepath.name}: {len(result['changes'])} changes")
                total_changes += len(result['changes'])
                for change in result['changes']:
                    print(f"    + {change}")
            else:
                print(f"  {filepath.name}: OK (no changes needed)")
    
    print(f"\n=== Total changes: {total_changes} ===")


if __name__ == '__main__':
    main()