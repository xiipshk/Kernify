#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rewrite all lessons in friendly CodeBasics/Hexlet/Stepik style:
- Start with concrete problem/scenario
- Show naive approach, then pain point
- Introduce concept as natural solution
- Line-by-line code explanations
- Visual diagrams (text-based)
- Friendly, conversational tone
- Practical exercise at the end
- Russian version = all Russian, English version = all English
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any

# Topic mapping per language
TOPIC_PATTERNS = {
    'python': {
        1: 'intro_setup',
        2: 'variables',
        3: 'operators',
        4: 'strings',
        5: 'conditionals',
        6: 'loops',
        7: 'lists',
        8: 'dicts',
        9: 'functions',
        10: 'modules',
        11: 'file_io',
        12: 'exceptions',
        13: 'oop_basics',
        14: 'oop_advanced',
        15: 'decorators',
        16: 'generators',
        17: 'context_managers',
        18: 'typing',
        19: 'async',
        20: 'testing',
        21: 'databases',
        22: 'web_basics',
        23: 'web_frameworks',
        23: 'advanced',
        24: 'advanced',
        25: 'advanced',
        26: 'advanced',
        27: 'advanced',
        28: 'advanced',
        29: 'advanced',
        30: 'advanced',
        31: 'advanced',
        32: 'advanced',
        33: 'capstone',
    },
    'javascript': {
        1: 'intro_setup',
        2: 'variables',
        3: 'types',
        4: 'operators',
        5: 'conditionals',
        6: 'loops',
        7: 'functions',
        8: 'objects',
        9: 'arrays',
        10: 'dom_basics',
        11: 'dom_advanced',
        12: 'events',
        13: 'async_basics',
        14: 'fetch_api',
        15: 'modules',
        16: 'tooling',
        17: 'testing',
        18: 'security',
        19: 'performance',
        20: 'react_basics',
        21: 'react_advanced',
        22: 'node_basics',
        23: 'node_advanced',
        24: 'typescript',
        25: 'advanced',
        26: 'advanced',
        27: 'advanced',
        28: 'advanced',
        29: 'capstone',
    },
    'cpp': {
        1: 'intro_setup',
        2: 'variables',
        3: 'types',
        4: 'operators',
        5: 'conditionals',
        6: 'loops',
        7: 'functions',
        8: 'arrays',
        9: 'pointers',
        10: 'strings',
        11: 'vectors',
        12: 'oop_basics',
        13: 'oop_advanced',
        14: 'templates',
        15: 'stl',
        16: 'exceptions',
        17: 'file_io',
        18: 'smart_pointers',
        19: 'move_semantics',
        20: 'concurrency',
        21: 'advanced',
        22: 'advanced',
        23: 'advanced',
        24: 'advanced',
        25: 'advanced',
        26: 'advanced',
        27: 'advanced',
        28: 'advanced',
        29: 'advanced',
        30: 'advanced',
        31: 'advanced',
        32: 'advanced',
        33: 'capstone',
    },
    'csharp': {
        1: 'intro_setup',
        2: 'variables',
        3: 'types',
        4: 'operators',
        5: 'conditionals',
        6: 'loops',
        7: 'methods',
        8: 'arrays',
        9: 'lists',
        10: 'oop_basics',
        11: 'inheritance',
        12: 'polymorphism',
        13: 'interfaces',
        14: 'generics',
        15: 'delegates',
        16: 'linq',
        17: 'exceptions',
        18: 'file_io',
        19: 'async',
        20: 'multithreading',
        21: 'dependency_injection',
        22: 'entity_framework',
        23: 'aspnet',
        24: 'testing',
        25: 'advanced',
        26: 'advanced',
        27: 'advanced',
        28: 'advanced',
        29: 'advanced',
        30: 'advanced',
        31: 'advanced',
        32: 'advanced',
        33: 'capstone',
    },
    'css': {
        1: 'intro_setup',
        2: 'selectors',
        3: 'box_model',
        4: 'flexbox',
        5: 'grid',
        6: 'positioning',
        7: 'typography',
        8: 'colors',
        9: 'responsive',
        10: 'animations',
        11: 'transforms',
        12: 'pseudo',
        13: 'forms',
        14: 'layouts',
        15: 'components',
        16: 'methodologies',
        17: 'preprocessors',
        18: 'architecture',
        19: 'performance',
        20: 'accessibility',
        21: 'i18n',
        22: 'custom_props',
        23: 'container_queries',
        24: 'advanced',
        25: 'advanced',
        26: 'advanced',
        27: 'advanced',
        28: 'advanced',
        29: 'advanced',
        30: 'advanced',
        31: 'advanced',
        32: 'capstone',
    },
    'rust': {
        1: 'intro_setup',
        2: 'variables',
        3: 'types',
        4: 'functions',
        5: 'control_flow',
        6: 'ownership',
        7: 'references',
        8: 'structs',
        9: 'enums',
        10: 'pattern_matching',
        11: 'error_handling',
        12: 'collections',
        13: 'generics',
        14: 'traits',
        15: 'lifetimes',
        16: 'smart_pointers',
        17: 'closures',
        18: 'iterators',
        19: 'modules',
        20: 'testing',
        21: 'file_io',
        22: 'concurrency',
        23: 'async',
        24: 'unsafe',
        25: 'macros',
        26: 'advanced',
        27: 'advanced',
        28: 'advanced',
        29: 'advanced',
        30: 'advanced',
        31: 'advanced',
        32: 'advanced',
        33: 'capstone',
    },
}

# Friendly intro scenarios for each topic
FRIENDLY_INTROS = {
    'variables': {
        'python': {
            'ru': {
                'scenario': 'Представьте, что вам нужно напечатать приветствие «Привет, друг!» на экране несколько раз. Можно просто скопировать строку:',
                'naive_code': 'print("Привет, друг!")\nprint("Привет, друг!")\nprint("Привет, друг!")',
                'pain_point': 'Но что, если приветствие придётся изменить на «Привет, товарищ!»? Придётся искать и править каждое вхождение вручную. А если таких мест десятки? Это утомительно и чревато ошибками.',
                'solution': 'Есть способ проще — сохранить значение в переменной и использовать её везде:',
                'solution_code': 'greeting = "Привет, друг!"\n\nprint(greeting)\nprint(greeting)\nprint(greeting)',
                'explanation': 'В строке `greeting = "Привет, друг!"` мы создаём переменную с именем `greeting` и кладем в неё строку. Знак `=` — это оператор присваивания: он кладёт правое значение в левую переменную.',
                'visual': '┌──────────┐     ┌──────────────────┐\n│ greeting │ ──→ │ "Привет, друг!"  │\n└──────────┘     └──────────────────┘\n  переменная          значение',
                'how_it_works': 'Когда интерпретатор видит `print(greeting)`, он подставляет вместо имени переменной её значение:',
                'substitution': 'print(greeting)\n      │\n      ▼\nprint("Привет, друг!")',
            },
            'en': {
                'scenario': 'Imagine you need to print the greeting "Hello, friend!" multiple times. You could just copy the string:',
                'naive_code': 'print("Hello, friend!")\nprint("Hello, friend!")\nprint("Hello, friend!")',
                'pain_point': 'But what if you need to change it to "Hello, buddy!"? You\'d have to find and fix every occurrence manually. And if there are dozens of them? That\'s tedious and error-prone.',
                'solution': 'There\'s a simpler way — save the value in a variable and use it everywhere:',
                'solution_code': 'greeting = "Hello, friend!"\n\nprint(greeting)\nprint(greeting)\nprint(greeting)',
                'explanation': 'In the line `greeting = "Hello, friend!"` we create a variable named `greeting` and put the string into it. The `=` sign is the assignment operator: it puts the right value into the left variable.',
                'visual': '┌──────────┐     ┌──────────────────┐\n│ greeting │ ──→ │ "Hello, friend!" │\n└──────────┘     └──────────────────┘\n  variable          value',
                'how_it_works': 'When the interpreter sees `print(greeting)`, it substitutes the variable name with its value:',
                'substitution': 'print(greeting)\n      │\n      ▼\nprint("Hello, friend!")',
            }
        },
        'javascript': {
            'ru': {
                'scenario': 'Представьте, что нужно вывести приветствие "Привет, друг!" несколько раз в консоль. Можно просто повторить строку:',
                'naive_code': 'console.log("Привет, друг!");\nconsole.log("Привет, друг!");\nconsole.log("Привет, друг!");',
                'pain_point': 'Но если текст изменится на "Привет, товарищ!", придётся править каждое место. В больших программах это неудобно и приводит к ошибкам.',
                'solution': 'Проще сохранить значение в переменной:',
                'solution_code': 'const greeting = "Привет, друг!";\n\nconsole.log(greeting);\nconsole.log(greeting);\nconsole.log(greeting);',
                'explanation': 'Строка `const greeting = "Привет, друг!";` создаёт константу (переменную, которую нельзя изменить) с именем `greeting` и присваивает ей строку.',
                'visual': '┌──────────┐     ┌──────────────────┐\n│ greeting │ ──→ │ "Привет, друг!"  │\n└──────────┘     └──────────────────┘\n  константа         значение',
            },
            'en': {
                'scenario': 'Imagine you need to log "Hello, friend!" multiple times. You could repeat the string:',
                'naive_code': 'console.log("Hello, friend!");\nconsole.log("Hello, friend!");\nconsole.log("Hello, friend!");',
                'pain_point': 'But if the text changes to "Hello, buddy!", you\'d have to fix every occurrence. In large programs this is inconvenient and error-prone.',
                'solution': 'It\'s simpler to save the value in a variable:',
                'solution_code': 'const greeting = "Hello, friend!";\n\nconsole.log(greeting);\nconsole.log(greeting);\nconsole.log(greeting);',
                'explanation': 'The line `const greeting = "Hello, friend!";` creates a constant (a variable that can\'t be reassigned) named `greeting` and assigns the string to it.',
                'visual': '┌──────────┐     ┌──────────────────┐\n│ greeting │ ──→ │ "Hello, friend!" │\n└──────────┘     └──────────────────┘\n  constant          value',
            }
        },
    },
    'operators': {
        'python': {
            'ru': {
                'scenario': 'В школе нас учили считать: 2 + 2 = 4. В Python математика работает так же, но есть нюансы, о которых стоит знать.',
            },
            'en': {
                'scenario': 'In school we learned 2 + 2 = 4. Python math works the same way, but there are nuances worth knowing.',
            }
        },
    },
    'conditionals': {
        'python': {
            'ru': {
                'scenario': 'В жизни мы постоянно принимаем решения: "Если дождь — возьму зонт, иначе — нет". В программах это работает так же: код должен вести себя по-разному в зависимости от условий.',
            },
            'en': {
                'scenario': 'In life we constantly make decisions: "If it rains — I\'ll take an umbrella, otherwise not." Programs work the same way: code must behave differently depending on conditions.',
            }
        },
    },
    'loops': {
        'python': {
            'ru': {
                'scenario': 'Представьте: нужно поздороваться с каждым другом из списка. Можно написать print пять раз, но если друзей станет сто? Циклы решают эту задачу — они повторяют действия автоматически.',
            },
            'en': {
                'scenario': 'Imagine you need to greet each friend in a list. You could write print five times, but what if you have a hundred friends? Loops solve this — they repeat actions automatically.',
            }
        },
    },
    'functions': {
        'python': {
            'ru': {
                'scenario': 'Вы замечали, что иногда пишете один и тот же код снова и снова? Функции позволяют упаковать повторяющуюся логику в один блок, дать ему имя и вызывать когда угодно. Это как рецепт: пишешь один раз — готовишь много раз.',
            },
            'en': {
                'scenario': 'Ever notice you write the same code over and over? Functions let you pack repeating logic into one block, give it a name, and call it anytime. Like a recipe: write once, cook many times.',
            }
        },
    },
    'lists': {
        'python': {
            'ru': {
                'scenario': 'У вас есть список покупок: хлеб, молоко, яйца. В Python такие наборы данных хранят в списках (list) — упорядоченных коллекциях, где каждый элемент имеет свой номер (индекс).',
            },
            'en': {
                'scenario': 'You have a shopping list: bread, milk, eggs. In Python such collections are stored in lists — ordered collections where each element has its own number (index).',
            }
        },
    },
    'strings': {
        'python': {
            'ru': {
                'scenario': 'Текст — это то, с чем программы работают постоянно: имена пользователей, сообщения, адреса сайтов. В Python текст хранят в строках (str) — неизменяемых последовательностях символов.',
            },
            'en': {
                'scenario': 'Text is what programs work with constantly: usernames, messages, website addresses. In Python text is stored in strings (str) — immutable sequences of characters.',
            }
        },
    },
}

# Section templates in friendly style
SECTION_TEMPLATES = {
    'ru': {
        'heading_objectives': '🎯 Что вы узнаете',
        'heading_how_it_works': '🔍 Как это работает',
        'heading_rules': '📋 Правила и нюансы',
        'heading_examples': '💡 Примеры',
        'heading_common_mistakes': '⚠️ Типичные ошибки',
        'heading_practice': '🛠 Практика',
        'heading_summary': '📌 Кратко о главном',
        'heading_useful': '🔗 Полезные ссылки',
    },
    'en': {
        'heading_objectives': '🎯 What You\'ll Learn',
        'heading_how_it_works': '🔍 How It Works',
        'heading_rules': '📋 Rules & Nuances',
        'heading_examples': '💡 Examples',
        'heading_common_mistakes': '⚠️ Common Mistakes',
        'heading_practice': '🛠 Practice',
        'heading_summary': '📌 Key Takeaways',
        'heading_useful': '🔗 Useful Links',
    }
}

# Common mistakes per topic (friendly table format)
COMMON_MISTAKES = {
    'variables': {
        'ru': [
            ['Использование переменной до присваивания', '`print(x)` → NameError', 'Сначала присвойте: `x = 10`'],
            ['Опечатка в имени переменной', '`greeting = "Hi"`\n`print(greting)` → NameError', 'Проверяйте имена, используйте автодополнение'],
            ['Путаница между переменной и строкой', '`name = "Alex"`\n`print("name")` → выведет "name"', 'Переменная без кавычек: `print(name)`'],
            ['Присваивание вместо сравнения', '`if x = 5:` → SyntaxError', 'Сравнение: `if x == 5:`'],
        ],
        'en': [
            ['Using variable before assignment', '`print(x)` → NameError', 'Assign first: `x = 10`'],
            ['Typo in variable name', '`greeting = "Hi"`\n`print(greting)` → NameError', 'Check names, use autocomplete'],
            ['Confusing variable with string', '`name = "Alex"`\n`print("name")` → prints "name"', 'Variable without quotes: `print(name)`'],
            ['Assignment instead of comparison', '`if x = 5:` → SyntaxError', 'Comparison: `if x == 5:`'],
        ]
    },
    'operators': {
        'ru': [
            ['Деление `/` всегда даёт float', '`5 / 2` → `2.5` (не `2`)', 'Для целого: `5 // 2` → `2`'],
            ['Путаница `%` и `/`', '`%` — остаток, `/` — частное', '`7 % 3` → `1`, `7 / 3` → `2.33...`'],
            ['Странности с приоритетом', '`2 + 3 * 4` → `14`, а не `20`', 'Скобки помогают: `(2 + 3) * 4` → `20`'],
        ],
        'en': [
            ['Division `/` always returns float', '`5 / 2` → `2.5` (not `2`)', 'For integer: `5 // 2` → `2`'],
            ['Confusing `%` and `/`', '`%` — remainder, `/` — quotient', '`7 % 3` → `1`, `7 / 3` → `2.33...`'],
            ['Precedence surprises', '`2 + 3 * 4` → `14`, not `20`', 'Parentheses help: `(2 + 3) * 4` → `20`'],
        ]
    },
}

# Practice tasks per topic
PRACTICE_TASKS = {
    'variables': {
        'ru': [
            'Создайте переменную `my_name` с вашим именем и выведите её на экран.',
            'Создайте переменную `age` с вашим возрастом и переменную `city` с городом. Выведите: "Меня зовут {имя}, мне {возраст} лет, я живу в {город}".',
            'Создайте переменную `price = 100` и `quantity = 3`. Посчитайте общую стоимость и сохраните в `total`.',
            'Исправьте ошибку в коде:\n```python\nname = "Анна"\nprint("name")  # должно вывести: Анна\n```',
        ],
        'en': [
            'Create a variable `my_name` with your name and print it.',
            'Create `age` with your age and `city` with your city. Print: "My name is {name}, I am {age} years old, I live in {city}".',
            'Create `price = 100` and `quantity = 3`. Calculate total and save to `total`.',
            'Fix the bug:\n```python\nname = "Anna"\nprint("name")  # should print: Anna\n```',
        ]
    },
}

# Useful links per topic
USEFUL_LINKS = {
    'variables': {
        'ru': [
            'Python.org — Variables and Assignment: https://docs.python.org/3/tutorial/introduction.html#variables',
            'Real Python — Python Variables: https://realpython.com/python-variables/',
            'PEP 8 — Naming Conventions: https://peps.python.org/pep-0008/#naming-conventions',
        ],
        'en': [
            'Python.org — Variables and Assignment: https://docs.python.org/3/tutorial/introduction.html#variables',
            'Real Python — Python Variables: https://realpython.com/python-variables/',
            'PEP 8 — Naming Conventions: https://peps.python.org/pep-0008/#naming-conventions',
        ]
    },
}

# Key takeaways per topic
KEY_TAKEAWAYS = {
    'variables': {
        'ru': [
            'Переменная — это именованное хранилище для значения.',
            'Присваивание `x = 5` кладёт значение 5 в переменную x.',
            'Имена переменных: буквы, цифры, подчёркивание; не с цифры; регистр важен.',
            'Переменную нужно создать перед использованием, иначе — NameError.',
            'В `print(x)` подставляется значение, в `print("x")` — буква "x".',
        ],
        'en': [
            'A variable is a named storage for a value.',
            'Assignment `x = 5` puts value 5 into variable x.',
            'Variable names: letters, digits, underscore; not starting with digit; case-sensitive.',
            'Variable must be created before use, otherwise NameError.',
            'In `print(x)` value is substituted, in `print("x")` — literal "x".',
        ]
    },
}


def get_topic(language: str, lesson_num: int) -> str:
    patterns = TOPIC_PATTERNS.get(language, {})
    return patterns.get(lesson_num, 'general')


def load_lesson(filepath: Path) -> Dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_lesson(filepath: Path, data: Dict):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def build_friendly_lesson(data: Dict, language: str, lesson_num: int) -> Dict:
    """Rebuild lesson in friendly CodeBasics/Hexlet style."""
    topic = get_topic(language, lesson_num)
    tpl = SECTION_TEMPLATES['ru']  # Russian version is primary
    
    # Get intro for this topic/language
    intro_data = FRIENDLY_INTROS.get(topic, {}).get(language, {}).get('ru', {})
    
    blocks = []
    
    # 1. Friendly Objectives
    blocks.append({
        'type': 'heading',
        'level': 2,
        'content': tpl['heading_objectives']
    })
    blocks.append({
        'type': 'list',
        'items': data.get('goals', [
            f'Понимать основы {topic}',
            'Уметь применять на практике',
            'Избегать частых ошибок',
        ]),
        'ordered': False
    })
    
    # 2. Problem Scenario (friendly intro)
    if intro_data:
        blocks.append({
            'type': 'heading',
            'level': 2,
            'content': f'1. {intro_data.get("scenario", "Введение")[:60]}...'
        })
        blocks.append({
            'type': 'text',
            'content': intro_data.get('scenario', '')
        })
        
        if intro_data.get('naive_code'):
            blocks.append({
                'type': 'code',
                'language': language,
                'content': intro_data['naive_code']
            })
        
        if intro_data.get('pain_point'):
            blocks.append({
                'type': 'text',
                'content': intro_data['pain_point']
            })
        
        if intro_data.get('solution'):
            blocks.append({
                'type': 'text',
                'content': intro_data['solution']
            })
        
        if intro_data.get('solution_code'):
            blocks.append({
                'type': 'code',
                'language': language,
                'content': intro_data['solution_code']
            })
        
        if intro_data.get('explanation'):
            blocks.append({
                'type': 'heading',
                'level': 3,
                'content': 'Что здесь происходит?'
            })
            blocks.append({
                'type': 'text',
                'content': intro_data['explanation']
            })
        
        if intro_data.get('visual'):
            blocks.append({
                'type': 'text',
                'content': f'**Схема переменной:**\n```\n{intro_data["visual"]}\n```'
            })
        
        if intro_data.get('how_it_works'):
            blocks.append({
                'type': 'text',
                'content': intro_data['how_it_works']
            })
        
        if intro_data.get('substitution'):
            blocks.append({
                'type': 'code',
                'language': language,
                'content': intro_data['substitution']
            })
    
    # 3. Main content from existing blocks (enhanced)
    existing_blocks = data.get('content_blocks', [])
    for block in existing_blocks:
        btype = block.get('type')
        if btype == 'heading':
            # Skip duplicate objectives headings
            content = block.get('content', '')
            if any(kw in content.lower() for kw in ['цели', 'objective', 'what you']):
                continue
            # Make heading friendlier
            new_content = content
            if content.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                pass  # Keep numbered sections
            blocks.append(block)
        elif btype in ('text', 'code', 'table', 'list'):
            blocks.append(block)
    
    # 4. Common Mistakes (friendly table)
    mistakes = COMMON_MISTAKES.get(topic, {}).get('ru', [])
    if mistakes:
        blocks.append({
            'type': 'heading',
            'level': 2,
            'content': tpl['heading_common_mistakes']
        })
        blocks.append({
            'type': 'text',
            'content': 'Вот самые частые ошибки новичков и как их избежать:'
        })
        blocks.append({
            'type': 'table',
            'headers': ['Ошибка', 'Как проявляется', 'Как правильно'],
            'rows': mistakes
        })
    
    # 5. Practice
    tasks = PRACTICE_TASKS.get(topic, {}).get('ru', [])
    if tasks:
        blocks.append({
            'type': 'heading',
            'level': 2,
            'content': tpl['heading_practice']
        })
        blocks.append({
            'type': 'text',
            'content': 'Попробуйте сами — это лучший способ запомнить:'
        })
        blocks.append({
            'type': 'list',
            'items': tasks,
            'ordered': True
        })
    
    # 6. Summary
    takeaways = KEY_TAKEAWAYS.get(topic, {}).get('ru', data.get('key_takeaways', []))
    if takeaways:
        blocks.append({
            'type': 'heading',
            'level': 2,
            'content': tpl['heading_summary']
        })
        blocks.append({
            'type': 'list',
            'items': takeaways,
            'ordered': False
        })
    
    # 7. Useful links
    links = USEFUL_LINKS.get(topic, {}).get('ru', data.get('resources', []))
    if links:
        blocks.append({
            'type': 'heading',
            'level': 2,
            'content': tpl['heading_useful']
        })
        blocks.append({
            'type': 'list',
            'items': links,
            'ordered': False
        })
    
    # Update data
    data['content_blocks'] = blocks
    
    # Ensure metadata
    data['goals'] = data.get('goals', [f'Понимать {topic}', 'Уметь применять', 'Избегать ошибок'])
    data['practice_tasks'] = tasks or data.get('practice_tasks', ['Базовая практика'])
    data['common_errors'] = [
        {'mistake': m[0], 'correct': m[2]} for m in mistakes
    ] or data.get('common_errors', [{'mistake': 'Ошибка', 'correct': 'Правильно'}])
    data['resources'] = links or data.get('resources', ['Официальная документация'])
    data['key_takeaways'] = takeaways or data.get('key_takeaways', ['Главный вывод'])
    
    # Estimate time based on content size
    total_chars = sum(len(json.dumps(b, ensure_ascii=False)) for b in blocks)
    data['estimated_minutes'] = max(15, min(45, total_chars // 800))
    
    return data


def build_english_version(data: Dict, language: str, lesson_num: int) -> Dict:
    """Build English version (content_en) matching Russian structure."""
    topic = get_topic(language, lesson_num)
    tpl = SECTION_TEMPLATES['en']
    
    intro_data = FRIENDLY_INTROS.get(topic, {}).get(language, {}).get('en', {})
    
    blocks = []
    
    # 1. Objectives
    blocks.append({
        'type': 'heading',
        'level': 2,
        'content': tpl['heading_objectives']
    })
    blocks.append({
        'type': 'list',
        'items': [
            f'Understand {topic} fundamentals',
            'Apply in practice',
            'Avoid common mistakes',
        ],
        'ordered': False
    })
    
    # 2. Problem Scenario
    if intro_data:
        blocks.append({
            'type': 'heading',
            'level': 2,
            'content': f'1. {intro_data.get("scenario", "Introduction")[:60]}...'
        })
        blocks.append({
            'type': 'text',
            'content': intro_data.get('scenario', '')
        })
        
        if intro_data.get('naive_code'):
            blocks.append({
                'type': 'code',
                'language': language,
                'content': intro_data['naive_code']
            })
        
        if intro_data.get('pain_point'):
            blocks.append({
                'type': 'text',
                'content': intro_data['pain_point']
            })
        
        if intro_data.get('solution'):
            blocks.append({
                'type': 'text',
                'content': intro_data['solution']
            })
        
        if intro_data.get('solution_code'):
            blocks.append({
                'type': 'code',
                'language': language,
                'content': intro_data['solution_code']
            })
        
        if intro_data.get('explanation'):
            blocks.append({
                'type': 'heading',
                'level': 3,
                'content': 'What Happens Here?'
            })
            blocks.append({
                'type': 'text',
                'content': intro_data['explanation']
            })
        
        if intro_data.get('visual'):
            blocks.append({
                'type': 'text',
                'content': f'**Variable Diagram:**\n```\n{intro_data["visual"]}\n```'
            })
        
        if intro_data.get('how_it_works'):
            blocks.append({
                'type': 'text',
                'content': intro_data['how_it_works']
            })
        
        if intro_data.get('substitution'):
            blocks.append({
                'type': 'code',
                'language': language,
                'content': intro_data['substitution']
            })
    
    # 3. Existing content translated (simplified - in real use would translate)
    existing_blocks = data.get('content_blocks', [])
    for block in existing_blocks:
        btype = block.get('type')
        if btype == 'heading':
            content = block.get('content', '')
            if any(kw in content.lower() for kw in ['цели', 'objective', 'what you']):
                continue
            # Translate heading roughly
            new_content = content
            trans = {
                'Что такое': 'What is',
                'Как это работает': 'How It Works',
                'Правила': 'Rules',
                'Примеры': 'Examples',
                'Ошибки': 'Mistakes',
                'Практика': 'Practice',
                'Кратко': 'Summary',
                'Полезные': 'Useful',
            }
            for ru, en in trans.items():
                if ru in new_content:
                    new_content = new_content.replace(ru, en)
            blocks.append({'type': 'heading', 'level': block.get('level', 2), 'content': new_content})
        elif btype in ('text', 'code', 'table', 'list'):
            # For code/table keep as-is, for text would need translation
            blocks.append(block)
    
    # 4. Common Mistakes
    mistakes = COMMON_MISTAKES.get(topic, {}).get('en', [])
    if mistakes:
        blocks.append({
            'type': 'heading',
            'level': 2,
            'content': tpl['heading_common_mistakes']
        })
        blocks.append({
            'type': 'text',
            'content': 'Here are the most common beginner mistakes and how to avoid them:'
        })
        blocks.append({
            'type': 'table',
            'headers': ['Mistake', 'How It Shows', 'Correct Way'],
            'rows': mistakes
        })
    
    # 5. Practice
    tasks = PRACTICE_TASKS.get(topic, {}).get('en', [])
    if tasks:
        blocks.append({
            'type': 'heading',
            'level': 2,
            'content': tpl['heading_practice']
        })
        blocks.append({
            'type': 'text',
            'content': 'Try it yourself — that\'s the best way to learn:'
        })
        blocks.append({
            'type': 'list',
            'items': tasks,
            'ordered': True
        })
    
    # 6. Summary
    takeaways = KEY_TAKEAWAYS.get(topic, {}).get('en', [])
    if takeaways:
        blocks.append({
            'type': 'heading',
            'level': 2,
            'content': tpl['heading_summary']
        })
        blocks.append({
            'type': 'list',
            'items': takeaways,
            'ordered': False
        })
    
    # 7. Useful links
    links = USEFUL_LINKS.get(topic, {}).get('en', [])
    if links:
        blocks.append({
            'type': 'heading',
            'level': 2,
            'content': tpl['heading_useful']
        })
        blocks.append({
            'type': 'list',
            'items': links,
            'ordered': False
        })
    
    return {
        'content_en': blocks,
        'name_en': data.get('title', '').replace('Урок', 'Lesson'),
        'short_description_en': data.get('short_description', ''),
    }


def process_lesson(filepath: Path, language: str, lesson_num: int) -> Dict:
    data = load_lesson(filepath)
    
    # Build friendly Russian version
    data = build_friendly_lesson(data, language, lesson_num)
    
    # Build English version
    en_data = build_english_version(data, language, lesson_num)
    data.update(en_data)
    
    return data


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Rewrite lessons in friendly style')
    parser.add_argument('--lang', choices=['python', 'javascript', 'cpp', 'csharp', 'css', 'rust', 'all'], default='all')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--lesson', type=str)
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
                print(f"✅ Rewritten {filepath}")
            else:
                print(f"Would rewrite {filepath}")
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
                    print(f"  Would rewrite {filepath.name}")
            except Exception as e:
                print(f"  ❌ {filepath.name}: {e}")


if __name__ == '__main__':
    main()