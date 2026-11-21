#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rewrite all lessons in friendly CodeBasics/Hexlet/Stepik style - V3:
- Generic fallbacks for ALL topics
- Complete structure for every lesson
- Strict language separation
"""

import json
from pathlib import Path
from typing import Dict, List, Any

# Topic mapping per language
TOPIC_PATTERNS = {
    'python': {
        1: 'intro', 2: 'variables', 3: 'operators', 4: 'strings', 5: 'conditionals',
        6: 'loops', 7: 'lists', 8: 'dicts', 9: 'functions', 10: 'modules',
        11: 'file_io', 12: 'exceptions', 13: 'oop_basics', 14: 'oop_advanced',
        15: 'decorators', 16: 'generators', 17: 'context_managers', 18: 'typing',
        19: 'async', 20: 'testing', 21: 'databases', 22: 'web_basics', 23: 'web_frameworks',
        24: 'advanced', 25: 'advanced', 26: 'advanced', 27: 'advanced', 28: 'advanced',
        29: 'advanced', 30: 'advanced', 31: 'advanced', 32: 'advanced', 33: 'capstone',
    },
    'javascript': {
        1: 'intro', 2: 'variables', 3: 'types', 4: 'operators', 5: 'conditionals',
        6: 'loops', 7: 'functions', 8: 'objects', 9: 'arrays', 10: 'dom_basics',
        11: 'dom_advanced', 12: 'events', 13: 'async_basics', 14: 'fetch_api',
        15: 'modules', 16: 'tooling', 17: 'testing', 18: 'security', 19: 'performance',
        20: 'react_basics', 21: 'react_advanced', 22: 'node_basics', 23: 'node_advanced',
        24: 'typescript', 25: 'advanced', 26: 'advanced', 27: 'advanced', 28: 'advanced',
        29: 'capstone',
    },
    'cpp': {
        1: 'intro', 2: 'variables', 3: 'types', 4: 'operators', 5: 'conditionals',
        6: 'loops', 7: 'functions', 8: 'arrays', 9: 'pointers', 10: 'strings',
        11: 'vectors', 12: 'oop_basics', 13: 'oop_advanced', 14: 'templates',
        15: 'stl', 16: 'exceptions', 17: 'file_io', 18: 'smart_pointers',
        19: 'move_semantics', 20: 'concurrency', 21: 'advanced', 22: 'advanced',
        23: 'advanced', 24: 'advanced', 25: 'advanced', 26: 'advanced', 27: 'advanced',
        28: 'advanced', 29: 'advanced', 30: 'advanced', 31: 'advanced', 32: 'advanced',
        33: 'capstone',
    },
    'csharp': {
        1: 'intro', 2: 'variables', 3: 'types', 4: 'operators', 5: 'conditionals',
        6: 'loops', 7: 'methods', 8: 'arrays', 9: 'lists', 10: 'oop_basics',
        11: 'inheritance', 12: 'polymorphism', 13: 'interfaces', 14: 'generics',
        15: 'delegates', 16: 'linq', 17: 'exceptions', 18: 'file_io', 19: 'async',
        20: 'multithreading', 21: 'dependency_injection', 22: 'entity_framework',
        23: 'aspnet', 24: 'testing', 25: 'advanced', 26: 'advanced', 27: 'advanced',
        28: 'advanced', 29: 'advanced', 30: 'advanced', 31: 'advanced', 32: 'advanced',
        33: 'capstone',
    },
    'css': {
        1: 'intro', 2: 'selectors', 3: 'box_model', 4: 'flexbox', 5: 'grid',
        6: 'positioning', 7: 'typography', 8: 'colors', 9: 'responsive', 10: 'animations',
        11: 'transforms', 12: 'pseudo', 13: 'forms', 14: 'layouts', 15: 'components',
        16: 'methodologies', 17: 'preprocessors', 18: 'architecture', 19: 'performance',
        20: 'accessibility', 21: 'i18n', 22: 'custom_props', 23: 'container_queries',
        24: 'advanced', 25: 'advanced', 26: 'advanced', 27: 'advanced', 28: 'advanced',
        29: 'advanced', 30: 'advanced', 31: 'advanced', 32: 'capstone',
    },
    'rust': {
        1: 'intro', 2: 'variables', 3: 'types', 4: 'functions', 5: 'control_flow',
        6: 'ownership', 7: 'references', 8: 'structs', 9: 'enums', 10: 'pattern_matching',
        11: 'error_handling', 12: 'collections', 13: 'generics', 14: 'traits',
        15: 'lifetimes', 16: 'smart_pointers', 17: 'closures', 18: 'iterators',
        19: 'modules', 20: 'testing', 21: 'file_io', 22: 'concurrency', 23: 'async',
        24: 'unsafe', 25: 'macros', 26: 'advanced', 27: 'advanced', 28: 'advanced',
        29: 'advanced', 30: 'advanced', 31: 'advanced', 32: 'advanced', 33: 'capstone',
    },
}

# Friendly names for topics
TOPIC_DISPLAY = {
    'ru': {
        'intro': 'Начало работы', 'variables': 'Переменные', 'types': 'Типы данных',
        'operators': 'Операторы', 'strings': 'Строки', 'conditionals': 'Условия (if/else)',
        'loops': 'Циклы', 'functions': 'Функции', 'lists': 'Списки', 'arrays': 'Массивы',
        'dicts': 'Словари', 'objects': 'Объекты', 'methods': 'Методы',
        'modules': 'Модули', 'file_io': 'Файлы и ввод-вывод', 'exceptions': 'Исключения',
        'oop_basics': 'Основы ООП', 'oop_advanced': 'Продвинутое ООП',
        'inheritance': 'Наследование', 'polymorphism': 'Полиморфизм',
        'interfaces': 'Интерфейсы', 'generics': 'Дженерики (обобщения)',
        'delegates': 'Делегаты и события', 'linq': 'LINQ',
        'async': 'Асинхронность', 'async_basics': 'Основы асинхронности',
        'fetch_api': 'Fetch API', 'dom_basics': 'Основы DOM', 'dom_advanced': 'Продвинутый DOM',
        'events': 'События', 'react_basics': 'React основы', 'react_advanced': 'React продвинутый',
        'node_basics': 'Node.js основы', 'node_advanced': 'Node.js продвинутый',
        'typescript': 'TypeScript', 'pointers': 'Указатели', 'references': 'Ссылки',
        'vectors': 'Векторы (std::vector)', 'templates': 'Шаблоны (templates)',
        'stl': 'STL (стандартная библиотека)', 'smart_pointers': 'Умные указатели',
        'move_semantics': 'Move-семантика', 'concurrency': 'Параллелизм',
        'box_model': 'Блочная модель', 'flexbox': 'Flexbox', 'grid': 'CSS Grid',
        'positioning': 'Позиционирование', 'typography': 'Типографика',
        'colors': 'Цвета и фоны', 'responsive': 'Адаптивность',
        'animations': 'Анимации', 'transforms': 'Трансформации',
        'pseudo': 'Псевдоэлементы/классы', 'forms': 'Формы',
        'layouts': 'Макеты', 'components': 'Компоненты',
        'methodologies': 'Методологии (BEM, SMACSS)', 'preprocessors': 'Препроцессоры (Sass/Less)',
        'architecture': 'Архитектура CSS', 'performance': 'Производительность',
        'accessibility': 'Доступность (a11y)', 'i18n': 'Интернационализация',
        'custom_props': 'CSS-переменные', 'container_queries': 'Container Queries',
        'ownership': 'Владение (ownership)', 'structs': 'Структуры (struct)',
        'enums': 'Перечисления (enum)', 'pattern_matching': 'Сопоставление с образцом',
        'error_handling': 'Обработка ошибок', 'collections': 'Коллекции',
        'traits': 'Трейты (traits)', 'lifetimes': 'Время жизни (lifetimes)',
        'closures': 'Замыкания', 'iterators': 'Итераторы',
        'modules': 'Модули и крейты', 'testing': 'Тестирование',
        'file_io': 'Файлы и ввод-вывод', 'unsafe': 'Небезопасный Rust',
        'macros': 'Макросы', 'capstone': 'Итоговый проект',
        'advanced': 'Продвинутая тема', 'web_basics': 'Веб-основы', 'web_frameworks': 'Веб-фреймворки',
        'databases': 'Базы данных', 'dependency_injection': 'Dependency Injection',
        'entity_framework': 'Entity Framework', 'aspnet': 'ASP.NET Core',
        'multithreading': 'Многопоточность', 'decorators': 'Декораторы',
        'generators': 'Генераторы', 'context_managers': 'Контекстные менеджеры',
        'typing': 'Типизация (type hints)', 'testing': 'Тестирование',
    },
    'en': {
        'intro': 'Getting Started', 'variables': 'Variables', 'types': 'Data Types',
        'operators': 'Operators', 'strings': 'Strings', 'conditionals': 'Conditionals (if/else)',
        'loops': 'Loops', 'functions': 'Functions', 'lists': 'Lists', 'arrays': 'Arrays',
        'dicts': 'Dictionaries', 'objects': 'Objects', 'methods': 'Methods',
        'modules': 'Modules', 'file_io': 'File I/O', 'exceptions': 'Exceptions',
        'oop_basics': 'OOP Basics', 'oop_advanced': 'Advanced OOP',
        'inheritance': 'Inheritance', 'polymorphism': 'Polymorphism',
        'interfaces': 'Interfaces', 'generics': 'Generics',
        'delegates': 'Delegates & Events', 'linq': 'LINQ',
        'async': 'Async', 'async_basics': 'Async Basics',
        'fetch_api': 'Fetch API', 'dom_basics': 'DOM Basics', 'dom_advanced': 'Advanced DOM',
        'events': 'Events', 'react_basics': 'React Basics', 'react_advanced': 'Advanced React',
        'node_basics': 'Node.js Basics', 'node_advanced': 'Advanced Node.js',
        'typescript': 'TypeScript', 'pointers': 'Pointers', 'references': 'References',
        'vectors': 'Vectors (std::vector)', 'templates': 'Templates',
        'stl': 'STL', 'smart_pointers': 'Smart Pointers',
        'move_semantics': 'Move Semantics', 'concurrency': 'Concurrency',
        'box_model': 'Box Model', 'flexbox': 'Flexbox', 'grid': 'CSS Grid',
        'positioning': 'Positioning', 'typography': 'Typography',
        'colors': 'Colors & Backgrounds', 'responsive': 'Responsive Design',
        'animations': 'Animations', 'transforms': 'Transforms',
        'pseudo': 'Pseudo-elements/classes', 'forms': 'Forms',
        'layouts': 'Layouts', 'components': 'Components',
        'methodologies': 'Methodologies (BEM, SMACSS)', 'preprocessors': 'Preprocessors (Sass/Less)',
        'architecture': 'CSS Architecture', 'performance': 'Performance',
        'accessibility': 'Accessibility (a11y)', 'i18n': 'Internationalization',
        'custom_props': 'CSS Custom Properties', 'container_queries': 'Container Queries',
        'ownership': 'Ownership', 'structs': 'Structs', 'enums': 'Enums',
        'pattern_matching': 'Pattern Matching', 'error_handling': 'Error Handling',
        'collections': 'Collections', 'traits': 'Traits', 'lifetimes': 'Lifetimes',
        'closures': 'Closures', 'iterators': 'Iterators',
        'modules': 'Modules & Crates', 'testing': 'Testing',
        'file_io': 'File I/O', 'unsafe': 'Unsafe Rust',
        'macros': 'Macros', 'capstone': 'Capstone Project',
        'advanced': 'Advanced Topic', 'web_basics': 'Web Basics', 'web_frameworks': 'Web Frameworks',
        'databases': 'Databases', 'dependency_injection': 'Dependency Injection',
        'entity_framework': 'Entity Framework', 'aspnet': 'ASP.NET Core',
        'multithreading': 'Multithreading', 'decorators': 'Decorators',
        'generators': 'Generators', 'context_managers': 'Context Managers',
        'typing': 'Type Hints', 'testing': 'Testing',
    }
}

# Language-specific syntax
LANG_SYNTAX = {
    'python': {'decl': 'name = "value"', 'print': 'print(name)', 'comment': '# комментарий'},
    'javascript': {'decl': 'const name = "value";', 'print': 'console.log(name);', 'comment': '// комментарий'},
    'cpp': {'decl': 'std::string name = "value";', 'print': 'std::cout << name << std::endl;', 'comment': '// комментарий'},
    'csharp': {'decl': 'string name = "value"; // или: var name = "value";', 'print': 'Console.WriteLine(name);', 'comment': '// комментарий'},
    'rust': {'decl': 'let name = "value";', 'print': 'println!("{}", name);', 'comment': '// комментарий'},
    'css': {'decl': '--name: value; /* CSS-переменная */', 'print': '/* Использование: var(--name) */', 'comment': '/* комментарий */'},
}

# ============================================================
# SPECIFIC CONTENT for well-covered topics
# ============================================================
SPECIFIC_CONTENT = {
    'intro': {
        'python': {
            'ru': {
                'scenario': 'Добро пожаловать в мир Python! 🐍 Представьте: вы хотите научиться программировать, но не знаете, с чего начать. Хорошая новость — Python создан именно для того, чтобы быть понятным. Его код читается почти как обычный английский текст.',
                'pain_point': 'Многие новички думают, что программирование — это сложная магия. На самом деле это просто навык давать компьютеру чёткие инструкции. Как рецепт блюда: делай шаг 1, потом шаг 2, получится результат.',
                'solution': 'В этом уроке мы настроим окружение, напишем первую программу и поймём, как запускать код. К концу урока вы сможете писать и запускать свои скрипты.',
                'key_points': [
                    'Python устанавливается за пару минут',
                    'Код пишется в .py файлах или в интерактивном режиме (REPL)',
                    'print() — ваш главный друг для вывода результатов',
                    'Ошибки — это нормально, они помогают учиться',
                ],
            },
            'en': {
                'scenario': 'Welcome to Python! 🐍 Imagine you want to learn programming but don\'t know where to start. Good news — Python is designed to be readable. Its code reads almost like plain English.',
                'pain_point': 'Many beginners think programming is complex magic. Actually it\'s just the skill of giving computers clear instructions. Like a recipe: do step 1, then step 2, get the result.',
                'solution': 'In this lesson we\'ll set up the environment, write your first program, and understand how to run code. By the end you\'ll write and run your own scripts.',
                'key_points': [
                    'Python installs in minutes',
                    'Code goes in .py files or interactive mode (REPL)',
                    'print() is your best friend for output',
                    'Errors are normal — they help you learn',
                ],
            }
        },
        'javascript': {
            'ru': {
                'scenario': 'Привет! 🌐 JavaScript — единственный язык, который работает в каждом браузере. Если вы хотите делать интерактивные сайты — это ваш выбор. Код выполняется прямо здесь, в консоли.',
                'pain_point': 'Многие думают, что JS — это только для сайтов. На самом деле с Node.js он работает и на сервере, и в десктопных приложениях, и даже в микроконтроллерах.',
                'solution': 'Мы настроим окружение, откроем консоль браузера и напишем первые команды. К концу урока вы будете запускать JS-код самостоятельно.',
                'key_points': [
                    'JS работает в браузере без установки',
                    'Консоль разработчика (F12) — ваша песочница',
                    'console.log() — аналог print() для вывода',
                    'Ошибки в консоли — ваши подсказки',
                ],
            },
            'en': {
                'scenario': 'Hi! 🌐 JavaScript is the only language that runs in every browser. Want interactive websites? This is your choice. Code runs right here in the console.',
                'pain_point': 'Many think JS is only for websites. Actually with Node.js it runs on servers, desktop apps, and even microcontrollers.',
                'solution': 'We\'ll set up, open the browser console, and write first commands. By the end you\'ll run JS code on your own.',
                'key_points': [
                    'JS runs in browser without install',
                    'DevTools console (F12) is your sandbox',
                    'console.log() is like print() for output',
                    'Console errors are your hints',
                ],
            }
        },
    },
    'variables': {
        'python': {
            'ru': {
                'scenario': 'Представьте: нужно напечатать приветствие «Привет, друг!» несколько раз. Можно просто скопировать строку:',
                'naive_code': 'print("Привет, друг!")\nprint("Привет, друг!")\nprint("Привет, друг!")',
                'pain_point': 'Но что, если приветствие придётся изменить на «Привет, товарищ!»? Придётся искать и править каждое вхождение вручную. А если таких мест десятки? Это утомительно и чревато ошибками.',
                'solution': 'Есть способ проще — сохранить значение в переменной и использовать её везде:',
                'solution_code': 'greeting = "Привет, друг!"\n\nprint(greeting)\nprint(greeting)\nprint(greeting)',
                'explanation': 'В строке `greeting = "Привет, друг!"` мы создаём переменную с именем `greeting` и кладем в неё строку. Знак `=` — это оператор присваивания: он кладёт правое значение в левую переменную.',
                'visual': '┌──────────┐     ┌──────────────────┐\n│ greeting │ ──→ │ "Привет, друг!"  │\n└──────────┘     └──────────────────┘\n  переменная          значение',
                'how_it_works': 'Когда интерпретатор видит `print(greeting)`, он подставляет вместо имени переменной её значение:',
                'substitution': 'print(greeting)\n      │\n      ▼\nprint("Привет, друг!")',
                'key_points': [
                    'Переменная — это именованное хранилище для значения.',
                    'Присваивание `x = 5` кладёт значение 5 в переменную x.',
                    'Имена переменных: буквы, цифры, подчёркивание; не с цифры; регистр важен.',
                    'Переменную нужно создать перед использованием, иначе — NameError.',
                    'В `print(x)` подставляется значение, в `print("x")` — буква "x".',
                ],
            },
            'en': {
                'scenario': 'Imagine you need to print "Hello, friend!" multiple times. You could just copy the string:',
                'naive_code': 'print("Hello, friend!")\nprint("Hello, friend!")\nprint("Hello, friend!")',
                'pain_point': 'But what if you need to change it to "Hello, buddy!"? You\'d have to find and fix every occurrence manually. Dozens of them? Tedious and error-prone.',
                'solution': 'There\'s a simpler way — save the value in a variable and use it everywhere:',
                'solution_code': 'greeting = "Hello, friend!"\n\nprint(greeting)\nprint(greeting)\nprint(greeting)',
                'explanation': 'In `greeting = "Hello, friend!"` we create a variable named `greeting` and put the string into it. The `=` is assignment: it puts the right value into the left variable.',
                'visual': '┌──────────┐     ┌──────────────────┐\n│ greeting │ ──→ │ "Hello, friend!" │\n└──────────┘     └──────────────────┘\n  variable          value',
                'how_it_works': 'When the interpreter sees `print(greeting)`, it substitutes the variable name with its value:',
                'substitution': 'print(greeting)\n      │\n      ▼\nprint("Hello, friend!")',
                'key_points': [
                    'A variable is named storage for a value.',
                    'Assignment `x = 5` puts value 5 into variable x.',
                    'Variable names: letters, digits, underscore; not starting with digit; case-sensitive.',
                    'Variable must be created before use, otherwise NameError.',
                    'In `print(x)` value is substituted, in `print("x")` — literal "x".',
                ],
            }
        },
        'javascript': {
            'ru': {
                'scenario': 'Представьте: нужно вывести приветствие "Привет, друг!" несколько раз в консоль. Можно просто повторить строку:',
                'naive_code': 'console.log("Привет, друг!");\nconsole.log("Привет, друг!");\nconsole.log("Привет, друг!");',
                'pain_point': 'Но если текст изменится на "Привет, товарищ!", придётся править каждое место. В больших программах это неудобно и приводит к ошибкам.',
                'solution': 'Проще сохранить значение в переменной:',
                'solution_code': 'const greeting = "Привет, друг!";\n\nconsole.log(greeting);\nconsole.log(greeting);\nconsole.log(greeting);',
                'explanation': 'Строка `const greeting = "Привет, друг!";` создаёт константу (переменную, которую нельзя изменить) с именем `greeting` и присваивает ей строку. `const` — современный стандарт для значений, которые не меняются.',
                'visual': '┌──────────┐     ┌──────────────────┐\n│ greeting │ ──→ │ "Привет, друг!"  │\n└──────────┘     └──────────────────┘\n  константа         значение',
                'how_it_works': 'Когда JS видит `console.log(greeting)`, он подставляет значение переменной:',
                'substitution': 'console.log(greeting);\n           │\n           ▼\nconsole.log("Привет, друг!");',
                'key_points': [
                    'const — для значений, которые не меняются (по умолчанию используйте это)',
                    'let — если значение будет меняться позже',
                    'Имена: camelCase (myVariable), не с цифры, регистр важен',
                    'Сначала объявите, потом используйте — иначе ReferenceError',
                ],
            },
            'en': {
                'scenario': 'Imagine you need to log "Hello, friend!" multiple times. You could repeat the string:',
                'naive_code': 'console.log("Hello, friend!");\nconsole.log("Hello, friend!");\nconsole.log("Hello, friend!");',
                'pain_point': 'But if the text changes to "Hello, buddy!", you\'d have to fix every occurrence. In large programs this is inconvenient and error-prone.',
                'solution': 'It\'s simpler to save the value in a variable:',
                'solution_code': 'const greeting = "Hello, friend!";\n\nconsole.log(greeting);\nconsole.log(greeting);\nconsole.log(greeting);',
                'explanation': 'The line `const greeting = "Hello, friend!";` creates a constant (a variable that can\'t be reassigned) named `greeting` and assigns the string to it. `const` is the modern default for values that don\'t change.',
                'visual': '┌──────────┐     ┌──────────────────┐\n│ greeting │ ──→ │ "Hello, friend!" │\n└──────────┘     └──────────────────┘\n  constant          value',
                'how_it_works': 'When JS sees `console.log(greeting)`, it substitutes the variable value:',
                'substitution': 'console.log(greeting);\n           │\n           ▼\nconsole.log("Hello, friend!");',
                'key_points': [
                    'const — for values that don\'t change (use by default)',
                    'let — if value will change later',
                    'Names: camelCase (myVariable), not starting with digit, case-sensitive',
                    'Declare before use, otherwise ReferenceError',
                ],
            }
        },
        'cpp': {
            'ru': {
                'scenario': 'В C++ каждая переменная должна иметь тип. Это строже, чем в Python, но даёт контроль и производительность. Представьте: нужно хранить возраст пользователя.',
                'naive_code': '// Без переменной — неудобно\nstd::cout << "Возраст: 25" << std::endl;\nstd::cout << "Через год: 26" << std::endl;',
                'pain_point': 'Если возраст изменится, придётся править в нескольких местах. И компилятор не проверит, что мы складываем возраст со строкой.',
                'solution': 'Объявим переменную с типом:',
                'solution_code': 'int age = 25;  // int — целое число\n\nstd::cout << "Возраст: " << age << std::endl;\nstd::cout << "Через год: " << (age + 1) << std::endl;',
                'explanation': '`int age = 25;` говорит компилятору: "зарезервируй память под целое число, назови это место age, положи туда 25". Тип `int` гарантирует, что там будет только целое число.',
                'visual': '┌──────────┐     ┌───────┐\n│   age    │ ──→ │  25   │  (4 байта в памяти)\n└──────────┘     └───────┘\n  int переменная   значение',
                'how_it_works': 'Компилятор подставляет значение age там, где используется переменная:',
                'substitution': 'std::cout << age;\n                │\n                ▼\nstd::cout << 25;',
                'key_points': [
                    'В C++ тип указывается при объявлении: int, double, string, bool',
                    'int — целые числа, double — дробные, string — текст, bool — true/false',
                    'Имена: snake_case, не с цифры, регистр важен',
                    'Неинициализированная переменная — мусор в памяти (UB)!',
                ],
            },
            'en': {
                'scenario': 'In C++ every variable must have a type. Stricter than Python, but gives control and performance. Imagine storing user age.',
                'naive_code': '// Without variable — inconvenient\nstd::cout << "Age: 25" << std::endl;\nstd::cout << "Next year: 26" << std::endl;',
                'pain_point': 'If age changes, you\'d fix multiple places. Compiler won\'t check if you add age to a string.',
                'solution': 'Declare a variable with type:',
                'solution_code': 'int age = 25;  // int — integer\n\nstd::cout << "Age: " << age << std::endl;\nstd::cout << "Next year: " << (age + 1) << std::endl;',
                'explanation': '`int age = 25;` tells compiler: "reserve memory for integer, name it age, put 25 there". Type `int` guarantees only integers live there.',
                'visual': '┌──────────┐     ┌───────┐\n│   age    │ ──→ │  25   │  (4 bytes in memory)\n└──────────┘     └───────┘\n  int variable   value',
                'how_it_works': 'Compiler substitutes age value wherever variable is used:',
                'substitution': 'std::cout << age;\n                │\n                ▼\nstd::cout << 25;',
                'key_points': [
                    'In C++ type is declared: int, double, string, bool',
                    'int — integers, double — decimals, string — text, bool — true/false',
                    'Names: snake_case, not starting with digit, case-sensitive',
                    'Uninitialized variable = garbage memory (UB)!',
                ],
            }
        },
        'csharp': {
            'ru': {
                'scenario': 'В C# переменные имеют строгую типизацию, но компилятор умный — часто может догадаться за вас (var). Нужно сохранить имя пользователя.',
                'naive_code': 'Console.WriteLine("Имя: Алексей");\nConsole.WriteLine("Привет, Алексей");',
                'pain_point': 'Если имя изменится — правим везде. И нет проверки типов при конкатенации.',
                'solution': 'Используем переменную:',
                'solution_code': 'string name = "Алексей";  // или: var name = "Алексей";\n\nConsole.WriteLine($"Имя: {name}");\nConsole.WriteLine($"Привет, {name}");',
                'explanation': '`string name = "Алексей";` создаёт переменную типа string. `var` позволяет компилятору вывести тип самому (здесь тоже string). `$""` — интерполированные строки, удобнее конкатенации.',
                'visual': '┌──────────┐     ┌─────────────┐\n│   name   │ ──→ │ "Алексей"   │\n└──────────┘     └─────────────┘\n  string переменная  значение',
                'how_it_works': 'Компилятор подставляет значение:',
                'substitution': 'Console.WriteLine($"{name}");\n                  │\n                  ▼\nConsole.WriteLine("Алексей");',
                'key_points': [
                    'string, int, double, bool — основные типы',
                    'var — неявная типизация (тип выводится компилятором)',
                    'Имена: camelCase для локальных переменных',
                    'Переменная должна быть инициализирована перед использованием',
                ],
            },
            'en': {
                'scenario': 'In C# variables have static typing, but compiler is smart — often infers type for you (var). Need to store username.',
                'naive_code': 'Console.WriteLine("Name: Alex");\nConsole.WriteLine("Hello, Alex");',
                'pain_point': 'If name changes — fix everywhere. No type checking on concatenation.',
                'solution': 'Use a variable:',
                'solution_code': 'string name = "Alex";  // or: var name = "Alex";\n\nConsole.WriteLine($"Name: {name}");\nConsole.WriteLine($"Hello, {name}");',
                'explanation': '`string name = "Alex";` creates a string variable. `var` lets compiler infer type (also string here). `$""` — interpolated strings, cleaner than concatenation.',
                'visual': '┌──────────┐     ┌─────────────┐\n│   name   │ ──→ │ "Alex"      │\n└──────────┘     └─────────────┘\n  string variable  value',
                'how_it_works': 'Compiler substitutes value:',
                'substitution': 'Console.WriteLine($"{name}");\n                  │\n                  ▼\nConsole.WriteLine("Alex");',
                'key_points': [
                    'string, int, double, bool — main types',
                    'var — implicit typing (compiler infers type)',
                    'Names: camelCase for local variables',
                    'Variable must be initialized before use',
                ],
            }
        },
        'rust': {
            'ru': {
                'scenario': 'В Rust переменные по умолчанию неизменяемы (immutable). Это защита от ошибок. Нужно сохранить имя:',
                'naive_code': 'println!("Имя: Алексей");\nprintln!("Привет, Алексей");',
                'pain_point': 'Если имя изменится — правим везде. В Rust по умолчанию нельзя случайно изменить значение.',
                'solution': 'Создаём переменную (по умолчанию неизменяемую):',
                'solution_code': 'let name = "Алексей";  // неизменяемая\n\nprintln!("Имя: {}", name);\nprintln!("Привет, {}", name);',
                'explanation': '`let name = "Алексей";` создаёт неизменяемую переменную. Тип выводится автоматически (&str). Попытка изменить — ошибка компиляции. Для изменения нужен `mut`: `let mut name = "Алексей";`.',
                'visual': '┌──────────┐     ┌─────────────┐\n│   name   │ ──→ │ "Алексей"   │  (неизменяемо!)\n└──────────┘     └─────────────┘\n  let переменная  значение',
                'how_it_works': 'Компилятор подставляет значение:',
                'substitution': 'println!("{{}}", name);\n            │\n            ▼\nprintln!("Алексей");',
                'key_points': [
                    'let — по умолчанию неизменяемо (immutable)',
                    'let mut — явно разрешаем изменение',
                    'Тип выводится автоматически (type inference)',
                    'Имена: snake_case',
                    'Неинициализированные переменные — ошибка компиляции',
                ],
            },
            'en': {
                'scenario': 'In Rust variables are immutable by default. Safety by design. Need to store a name:',
                'naive_code': 'println!("Name: Alex");\nprintln!("Hello, Alex");',
                'pain_point': 'If name changes — fix everywhere. Rust prevents accidental mutation by default.',
                'solution': 'Create a variable (immutable by default):',
                'solution_code': 'let name = "Alex";  // immutable\n\nprintln!("Name: {}", name);\nprintln!("Hello, {}", name);',
                'explanation': '`let name = "Alex";` creates an immutable variable. Type inferred (&str). Mutation attempt = compile error. For mutability: `let mut name = "Alex";`.',
                'visual': '┌──────────┐     ┌─────────────┐\n│   name   │ ──→ │ "Alex"      │  (immutable!)\n└──────────┘     └─────────────┘\n  let variable  value',
                'how_it_works': 'Compiler substitutes value:',
                'substitution': 'println!("{{}}", name);\n            │\n            ▼\nprintln!("Alex");',
                'key_points': [
                    'let — immutable by default',
                    'let mut — explicitly allow mutation',
                    'Type inferred automatically (type inference)',
                    'Names: snake_case',
                    'Uninitialized variables = compile error',
                ],
            }
        },
    },
}

# ============================================================
# COMMON MISTAKES per topic
# ============================================================
COMMON_MISTAKES = {
    'variables': {
        'python': {'ru': [['Использование до присваивания', '`print(x)` → NameError', 'Сначала присвойте: `x = 10`'], ['Опечатка в имени', '`greeting = "Hi"`\n`print(greting)` → NameError', 'Проверяйте имена, используйте автодополнение'], ['Путаница: переменная vs строка', '`name = "Alex"`\n`print("name")` → выведет "name"', 'Переменная без кавычек: `print(name)`'], ['Присваивание вместо сравнения', '`if x = 5:` → SyntaxError', 'Сравнение: `if x == 5:`']], 'en': [['Using before assignment', '`print(x)` → NameError', 'Assign first: `x = 10`'], ['Typo in name', '`greeting = "Hi"`\n`print(greting)` → NameError', 'Check names, use autocomplete'], ['Variable vs string confusion', '`name = "Alex"`\n`print("name")` → prints "name"', 'Variable without quotes: `print(name)`'], ['Assignment instead of comparison', '`if x = 5:` → SyntaxError', 'Comparison: `if x == 5:`']]},
        'javascript': {'ru': [['Использование до объявления', '`console.log(x)` → ReferenceError', 'Сначала объявите: `const x = 10;`'], ['Опечатка в имени', '`const greeting = "Hi";`\n`console.log(greting);` → ReferenceError', 'Проверяйте имена'], ['const вместо let при изменении', '`const x = 5; x = 10;` → TypeError', 'Если меняется — используйте `let`']], 'en': [['Using before declaration', '`console.log(x)` → ReferenceError', 'Declare first: `const x = 10;`'], ['Typo in name', '`const greeting = "Hi";`\n`console.log(greting);` → ReferenceError', 'Check names'], ['const instead of let when mutating', '`const x = 5; x = 10;` → TypeError', 'If mutating — use `let`']]},
        'cpp': {'ru': [['Неинициализированная переменная', '`int x; std::cout << x;` → мусор (UB)', 'Всегда инициализируйте: `int x = 0;`'], ['Узкий тип для большого числа', '`int x = 3000000000;` → переполнение', 'Используйте `long long` или `int64_t`'], ['Сравнение float на равенство', '`float a = 0.1 + 0.2; a == 0.3` → false', 'Сравнивайте с epsilon: `abs(a - 0.3) < 1e-9`']], 'en': [['Uninitialized variable', '`int x; std::cout << x;` → garbage (UB)', 'Always initialize: `int x = 0;`'], ['Narrow type for large number', '`int x = 3000000000;` → overflow', 'Use `long long` or `int64_t`'], ['Float equality comparison', '`float a = 0.1 + 0.2; a == 0.3` → false', 'Compare with epsilon: `abs(a - 0.3) < 1e-9`']]},
        'csharp': {'ru': [['Использование до присваивания', '`int x; Console.WriteLine(x);` → ошибка компиляции', 'Присвойте значение: `int x = 0;`'], ['string vs String', '`String s = "hi";` работает, но `string` — предпочтительнее', 'Используйте `string` (alias)'], ['null для значимых типов', '`int x = null;` → ошибка', 'Используйте `int? x = null` (nullable)']], 'en': [['Using before assignment', '`int x; Console.WriteLine(x);` → compile error', 'Assign value: `int x = 0;`'], ['string vs String', '`String s = "hi";` works but `string` preferred', 'Use `string` (alias)'], ['null for value types', '`int x = null;` → error', 'Use `int? x = null` (nullable)']]},
        'rust': {'ru': [['Попытка изменить неизменяемую', '`let x = 5; x = 6;` → ошибка компиляции', 'Добавьте `mut`: `let mut x = 5;`'], ['Использование неинициализированной', '`let x: i32; println!("{}", x);` → ошибка компиляции', 'Всегда инициализируйте при объявлении'], ['Заимствование после перемещения', '`let s = String::new(); let t = s; println!("{}", s);` → ошибка', 'Клонируйте: `let t = s.clone();` или используйте ссылки']], 'en': [['Mutating immutable', '`let x = 5; x = 6;` → compile error', 'Add `mut`: `let mut x = 5;`'], ['Using uninitialized', '`let x: i32; println!("{}", x);` → compile error', 'Always initialize at declaration'], ['Use after move', '`let s = String::new(); let t = s; println!("{}", s);` → error', 'Clone: `let t = s.clone();` or use references']]},
    },
    'operators': {
        'python': {'ru': [['Деление `/` всегда даёт float', '`5 / 2` → `2.5` (не `2`)', 'Для целого: `5 // 2` → `2`'], ['Путаница `%` и `/`', '`%` — остаток, `/` — частное', '`7 % 3` → `1`, `7 / 3` → `2.33...`'], ['Приоритет операторов', '`2 + 3 * 4` → `14`, а не `20`', 'Скобки: `(2 + 3) * 4` → `20`']], 'en': [['Division `/` always returns float', '`5 / 2` → `2.5` (not `2`)', 'For integer: `5 // 2` → `2`'], ['Confusing `%` and `/`', '`%` — remainder, `/` — quotient', '`7 % 3` → `1`, `7 / 3` → `2.33...`'], ['Precedence surprise', '`2 + 3 * 4` → `14`, not `20`', 'Parentheses: `(2 + 3) * 4` → `20`']]},
    },
    'strings': {
        'python': {'ru': [['Попытка изменить символ в строке', '`s[0] = "A"` → TypeError', 'Строки неизменяемы! Создайте новую: `"A" + s[1:]`'], ['Забыли f перед строкой', '`name = "Alex"; print("{name}")` → выведет "{name}"', 'Нужен префикс f: `f"{name}"`'], ['Экранирование в путях Windows', '`path = "C:\\Users"` → ошибка', 'Raw-строка: `r"C:\\Users"` или `\\\\`']], 'en': [['Modifying string character', '`s[0] = "A"` → TypeError', 'Strings immutable! Create new: `"A" + s[1:]`'], ['Forgot f prefix', '`name = "Alex"; print("{name}")` → prints "{name}"', 'Need f prefix: `f"{name}"`'], ['Escaping in Windows paths', '`path = "C:\\Users"` → error', 'Raw string: `r"C:\\Users"` or `\\\\`']]},
    },
    'conditionals': {
        'python': {'ru': [['`=` вместо `==`', '`if x = 5:` → SyntaxError', 'Сравнение: `if x == 5:`'], ['Забыли `:` после условия', '`if x > 0` → SyntaxError', 'Всегда двоеточие: `if x > 0:`'], ['`and`/`or` возвращают не bool', '`"a" and "b"` → "b", а не True', 'Для bool оборачивайте: `bool("a" and "b")`']], 'en': [['`=` instead of `==`', '`if x = 5:` → SyntaxError', 'Comparison: `if x == 5:`'], ['Missing `:` after condition', '`if x > 0` → SyntaxError', 'Always colon: `if x > 0:`'], ['`and`/`or` return non-bool', '`"a" and "b"` → "b", not True', 'Wrap for bool: `bool("a" and "b")`']]},
    },
    'loops': {
        'python': {'ru': [['Бесконечный цикл без break', '`while True:` без выхода → зависание', 'Всегда предусматривайте выход'], ['Изменение коллекции во время итерации', '`for x in lst: lst.remove(x)` → пропуски', 'Итерируйте копию: `for x in lst[:]:`'], ['`range(len(lst))` вместо enumerate', 'Сложнее и читается хуже', 'Лучше: `for i, v in enumerate(lst):`']], 'en': [['Infinite loop without break', '`while True:` without exit → hang', 'Always provide exit'], ['Modifying collection during iteration', '`for x in lst: lst.remove(x)` → skips', 'Iterate copy: `for x in lst[:]:`'], ['`range(len(lst))` instead of enumerate', 'More complex, less readable', 'Better: `for i, v in enumerate(lst):`']]},
    },
    'functions': {
        'python': {'ru': [['Забыли return', '`def add(a, b): a + b` → возвращает None', 'Добавьте: `return a + b`'], ['Изменяемый аргумент по умолчанию', '`def f(x=[]): x.append(1)` → список общий для всех вызовов', '`def f(x=None): x = x or []`'], ['Путаница: параметры vs аргументы', 'Параметры — в определении, аргументы — при вызове', '`def f(param):` — параметр, `f(arg)` — аргумент']], 'en': [['Forgot return', '`def add(a, b): a + b` → returns None', 'Add: `return a + b`'], ['Mutable default argument', '`def f(x=[]): x.append(1)` → shared across calls', '`def f(x=None): x = x or []`'], ['Params vs args confusion', 'Params in definition, args at call site', '`def f(param):` param, `f(arg)` arg']]},
    },
    'lists': {
        'python': {'ru': [['Индекс за границами', '`lst[10]` для 3 элементов → IndexError', 'Проверяйте: `if i < len(lst):`'], ['`append` возвращает None', '`lst = lst.append(5)` → lst становится None', '`lst.append(5)` — меняет на месте, ничего не возвращает'], ['Копирование через присваивание', '`b = a` — это та же ссылка!', 'Копия: `b = a[:]` или `b = a.copy()`']], 'en': [['Index out of bounds', '`lst[10]` for 3 elements → IndexError', 'Check: `if i < len(lst):`'], ['`append` returns None', '`lst = lst.append(5)` → lst becomes None', '`lst.append(5)` — mutates in place, returns nothing'], ['Copy by assignment', '`b = a` — same reference!', 'Copy: `b = a[:]` or `b = a.copy()`']]},
    },
    'dicts': {
        'python': {'ru': [['KeyError при доступе', '`d["missing"]` → KeyError', 'Используйте `.get("missing", default)`'], ['Изменяемый ключ', '`d[[1,2]] = "oops"` → TypeError', 'Ключи должны быть неизменяемыми: строка, число, кортеж'], ['Перебор только ключей', '`for k in d:` — только ключи', 'Для пар: `for k, v in d.items():`']], 'en': [['KeyError on access', '`d["missing"]` → KeyError', 'Use `.get("missing", default)`'], ['Mutable key', '`d[[1,2]] = "oops"` → TypeError', 'Keys must be immutable: str, int, tuple'], ['Iterating keys only', '`for k in d:` — keys only', 'For pairs: `for k, v in d.items():`']]},
    },
}

# Generic fallbacks
GENERIC_MISTAKES = {
    'ru': [['Непонимание основной концепции', 'Код не работает или работает неправильно', 'Перечитайте урок, поэкспериментируйте в REPL'], ['Игнорирование best practices', 'Код работает, но трудно читать и поддерживать', 'Следуйте стилю (PEP 8 / Google Style / rustfmt)'], ['Копипаст без понимания', 'Ошибки в адаптированном коде', 'Пишите сами, разбирайте каждую строку']],
    'en': [['Not grasping core concept', 'Code fails or behaves unexpectedly', 'Re-read lesson, experiment in REPL'], ['Ignoring best practices', 'Code works but hard to read/maintain', 'Follow style guide (PEP 8 / Google Style / rustfmt)'], ['Copy-paste without understanding', 'Errors in adapted code', 'Write yourself, understand every line']],
}

GENERIC_PRACTICE = {
    'ru': ['Создайте простой пример, используя изученную тему.', 'Измените пример из урока — добавьте свою логику.', 'Найдите и исправьте ошибку в похожем коде.', 'Объясните другу (или ревью) как работает эта концепция своими словами.'],
    'en': ['Create a simple example using the learned concept.', 'Modify the lesson example — add your own logic.', 'Find and fix a bug in similar code.', 'Explain to a friend (or rubber duck) how this concept works in your own words.'],
}

GENERIC_LINKS = {
    'ru': ['Официальная документация по теме', 'Практическое руководство с примерами', 'Видео-туториал для визуального обучения'],
    'en': ['Official documentation for this topic', 'Practical guide with examples', 'Video tutorial for visual learning'],
}

GENERIC_TAKEAWAYS = {
    'ru': ['Главная идея темы понятна и применима на практике.', 'Знаете типичные ошибки и как их избежать.', 'Можете найти документацию и примеры самостоятельно.', 'Готовы переходить к следующей теме.'],
    'en': ['Core concept understood and applicable in practice.', 'Know common mistakes and how to avoid them.', 'Can find documentation and examples independently.', 'Ready to move to the next topic.'],
}

# ============================================================
# PRACTICE TASKS specific
# ============================================================
PRACTICE_TASKS = {
    'variables': {
        'python': {'ru': ['Создайте переменную `my_name` с вашим именем и выведите её на экран.', 'Создайте `age` (возраст) и `city` (город). Выведите: "Меня зовут {имя}, мне {возраст} лет, я живу в {город}".', 'Создайте `price = 100` и `quantity = 3`. Посчитайте общую стоимость в `total` и выведите.', 'Исправьте ошибку:\n```python\nname = "Анна"\nprint("name")  # должно вывести: Анна\n```'], 'en': ['Create variable `my_name` with your name and print it.', 'Create `age` and `city`. Print: "My name is {name}, I am {age} years old, I live in {city}".', 'Create `price = 100` and `quantity = 3`. Calculate total in `total` and print.', 'Fix the bug:\n```python\nname = "Anna"\nprint("name")  # should print: Anna\n```']},
        'javascript': {'ru': ['Создайте константу `myName` с вашим именем и выведите в консоль.', 'Создайте `age` и `city`. Выведите: `Меня зовут ${name}, мне ${age} лет`.', 'Создайте `price = 100`, `quantity = 3`. Посчитайте `total` и выведите.', 'Исправьте:\n```javascript\nconst name = "Анна";\nconsole.log("name"); // должно: Анна\n```'], 'en': ['Create constant `myName` with your name and log it.', 'Create `age` and `city`. Log: `My name is ${name}, I am ${age} years old`.', 'Create `price = 100`, `quantity = 3`. Calculate `total` and log.', 'Fix:\n```javascript\nconst name = "Anna";\nconsole.log("name"); // should: Anna\n```']},
    },
    'operators': {
        'python': {'ru': ['Посчитайте: `2 + 3 * 4`, `(2 + 3) * 4`, `2 ** 3`, `10 // 3`, `10 % 3`.', 'Дано `x = 7`, `y = 2`. Выведите: сумму, разность, произведение, частное, целое частное, остаток, степень.', 'Проверьте чётность чисел от 1 до 10 с помощью `% 2`.', 'Исправьте: `result = 5 / 2` должно дать целое число 2.'], 'en': ['Calculate: `2 + 3 * 4`, `(2 + 3) * 4`, `2 ** 3`, `10 // 3`, `10 % 3`.', 'Given `x = 7`, `y = 2`. Print: sum, difference, product, quotient, floor division, remainder, power.', 'Check parity of numbers 1-10 using `% 2`.', 'Fix: `result = 5 / 2` should give integer 2.']},
    },
    'strings': {
        'python': {'ru': ['Создайте f-строку: `f"Привет, {name}! Тебе {age} лет."` с вашими данными.', 'Дана строка `s = "  Python  "`. Выведите: `s.strip()`, `s.upper()`, `s.lower()`, `len(s)`.', 'Замените все "о" на "а" в строке `"хорошо"` методом `.replace()`.', 'Разбейте `"один,два,три"` по запятым в список через `.split(",")`.'], 'en': ['Create f-string: `f"Hello, {name}! You are {age}."` with your data.', 'Given `s = "  Python  "`. Print: `s.strip()`, `s.upper()`, `s.lower()`, `len(s)`.', 'Replace all "o" with "a" in `"good"` using `.replace()`.', 'Split `"one,two,three"` by commas into a list via `.split(",")`.']},
    },
    'conditionals': {
        'python': {'ru': ['Напишите программу: просит число, выводит "Положительное", "Отрицательное" или "Ноль".', 'Проверьте возраст: если >= 18 — "Совершеннолетний", иначе — "Несовершеннолетний".', 'Дано число. Выведите "Чётное" или "Нечётное" (подсказка: `% 2`).', 'Исправьте: `if x = 5:` → `if x == 5:`.'], 'en': ['Write program: asks number, prints "Positive", "Negative", or "Zero".', 'Check age: if >= 18 — "Adult", else — "Minor".', 'Given number. Print "Even" or "Odd" (hint: `% 2`).', 'Fix: `if x = 5:` → `if x == 5:`.']},
    },
    'loops': {
        'python': {'ru': ['Выведите числа от 1 до 10 через `for i in range(1, 11):`.', 'Дан список `["яблоко", "банан", "вишня"]`. Выведите каждый фрукт на новой строке.', 'Посчитайте сумму чисел от 1 до 100 (подсказка: `range(1, 101)`).', 'Найдите первое чётное число в списке `[1, 3, 5, 8, 9]` — используйте `break`.'], 'en': ['Print numbers 1 to 10 via `for i in range(1, 11):`.', 'Given list `["apple", "banana", "cherry"]`. Print each fruit on new line.', 'Sum numbers 1 to 100 (hint: `range(1, 101)`).', 'Find first even in `[1, 3, 5, 8, 9]` — use `break`.']},
    },
    'functions': {
        'python': {'ru': ['Создайте функцию `greet(name)`, которая возвращает `"Привет, {name}!"`.', 'Напишите `add(a, b)` — возвращает сумму. Проверьте: `add(2, 3)` → 5.', 'Сделайте параметр `name` опциональным со значением "Гость".', 'Исправьте: `def add(a, b): a + b` → добавьте `return`.'], 'en': ['Create `greet(name)` returning `"Hello, {name}!"`.', 'Write `add(a, b)` returning sum. Test: `add(2, 3)` → 5.', 'Make `name` optional with default "Guest".', 'Fix: `def add(a, b): a + b` → add `return`.']},
    },
    'lists': {
        'python': {'ru': ['Создайте список покупок из 5 элементов. Выведите первый и последний.', 'Добавьте "молоко" в конец списка. Удалите второй элемент.', 'Проверьте, есть ли "хлеб" в списке через `in`.', 'Создайте копию списка и измените копию — оригинал не должен измениться.'], 'en': ['Create shopping list of 5 items. Print first and last.', 'Append "milk" to end. Remove second element.', 'Check if "bread" in list via `in`.', 'Copy list, modify copy — original should stay unchanged.']},
    },
    'dicts': {
        'python': {'ru': ['Создайте словарь `user = {"name": "Алекс", "age": 25}`. Выведите имя.', 'Добавьте ключ "city" со значением "Москва". Увеличьте возраст на 1.', 'Проверьте наличие ключа "email" через `.get()` с дефолтом "не указан".', 'Переберите словарь: `for k, v in user.items(): print(k, v)`.'], 'en': ['Create `user = {"name": "Alex", "age": 25}`. Print name.', 'Add key "city" = "Moscow". Increment age by 1.', 'Check "email" key via `.get()` with default "not specified".', 'Iterate dict: `for k, v in user.items(): print(k, v)`.']},
    },
}

# ============================================================
# USEFUL LINKS specific
# ============================================================
USEFUL_LINKS = {
    'variables': {'ru': ['Python.org — Variables: https://docs.python.org/3/tutorial/introduction.html#variables', 'Real Python — Python Variables: https://realpython.com/python-variables/', 'PEP 8 — Naming Conventions: https://peps.python.org/pep-0008/#naming-conventions'], 'en': ['Python.org — Variables: https://docs.python.org/3/tutorial/introduction.html#variables', 'Real Python — Python Variables: https://realpython.com/python-variables/', 'PEP 8 — Naming Conventions: https://peps.python.org/pep-0008/#naming-conventions']},
    'operators': {'ru': ['Python.org — Operators: https://docs.python.org/3/reference/expressions.html#operator-precedence', 'Real Python — Operators: https://realpython.com/python-operators-expressions/', 'W3Schools — Python Operators: https://www.w3schools.com/python/python_operators.asp'], 'en': ['Python.org — Operators: https://docs.python.org/3/reference/expressions.html#operator-precedence', 'Real Python — Operators: https://realpython.com/python-operators-expressions/', 'W3Schools — Python Operators: https://www.w3schools.com/python/python_operators.asp']},
    'strings': {'ru': ['Python.org — Strings: https://docs.python.org/3/tutorial/introduction.html#strings', 'Real Python — String Formatting: https://realpython.com/python-string-formatting/', 'Python Docs — String Methods: https://docs.python.org/3/library/stdtypes.html#string-methods'], 'en': ['Python.org — Strings: https://docs.python.org/3/tutorial/introduction.html#strings', 'Real Python — String Formatting: https://realpython.com/python-string-formatting/', 'Python Docs — String Methods: https://docs.python.org/3/library/stdtypes.html#string-methods']},
    'conditionals': {'ru': ['Python.org — If Statements: https://docs.python.org/3/tutorial/controlflow.html#if-statements', 'Real Python — Conditional Logic: https://realpython.com/python-conditional-statements/', 'W3Schools — Python If Else: https://www.w3schools.com/python/python_conditions.asp'], 'en': ['Python.org — If Statements: https://docs.python.org/3/tutorial/controlflow.html#if-statements', 'Real Python — Conditional Logic: https://realpython.com/python-conditional-statements/', 'W3Schools — Python If Else: https://www.w3schools.com/python/python_conditions.asp']},
    'loops': {'ru': ['Python.org — For Loops: https://docs.python.org/3/tutorial/controlflow.html#for-statements', 'Real Python — Loops: https://realpython.com/python-for-loop/', 'W3Schools — Python For Loops: https://www.w3schools.com/python/python_for_loops.asp'], 'en': ['Python.org — For Loops: https://docs.python.org/3/tutorial/controlflow.html#for-statements', 'Real Python — Loops: https://realpython.com/python-for-loop/', 'W3Schools — Python For Loops: https://www.w3schools.com/python/python_for_loops.asp']},
    'functions': {'ru': ['Python.org — Functions: https://docs.python.org/3/tutorial/controlflow.html#defining-functions', 'Real Python — Defining Functions: https://realpython.com/defining-your-own-python-function/', 'W3Schools — Python Functions: https://www.w3schools.com/python/python_functions.asp'], 'en': ['Python.org — Functions: https://docs.python.org/3/tutorial/controlflow.html#defining-functions', 'Real Python — Defining Functions: https://realpython.com/defining-your-own-python-function/', 'W3Schools — Python Functions: https://www.w3schools.com/python/python_functions.asp']},
    'lists': {'ru': ['Python.org — Lists: https://docs.python.org/3/tutorial/introduction.html#lists', 'Real Python — Lists: https://realpython.com/python-lists-tuples/', 'W3Schools — Python Lists: https://www.w3schools.com/python/python_lists.asp'], 'en': ['Python.org — Lists: https://docs.python.org/3/tutorial/introduction.html#lists', 'Real Python — Lists: https://realpython.com/python-lists-tuples/', 'W3Schools — Python Lists: https://www.w3schools.com/python/python_lists.asp']},
    'dicts': {'ru': ['Python.org — Dictionaries: https://docs.python.org/3/tutorial/datastructures.html#dictionaries', 'Real Python — Dictionaries: https://realpython.com/python-dicts/', 'W3Schools — Python Dictionaries: https://www.w3schools.com/python/python_dictionaries.asp'], 'en': ['Python.org — Dictionaries: https://docs.python.org/3/tutorial/datastructures.html#dictionaries', 'Real Python — Dictionaries: https://realpython.com/python-dicts/', 'W3Schools — Python Dictionaries: https://www.w3schools.com/python/python_dictionaries.asp']},
}

# ============================================================
# KEY TAKEAWAYS specific
# ============================================================
KEY_TAKEAWAYS = {
    'variables': {'ru': ['Переменная — это именованное хранилище для значения.', 'Присваивание `x = 5` кладёт значение 5 в переменную x.', 'Имена переменных: буквы, цифры, подчёркивание; не с цифры; регистр важен.', 'Переменную нужно создать перед использованием, иначе — NameError.', 'В `print(x)` подставляется значение, в `print("x")` — буква "x".'], 'en': ['A variable is named storage for a value.', 'Assignment `x = 5` puts value 5 into variable x.', 'Variable names: letters, digits, underscore; not starting with digit; case-sensitive.', 'Variable must be created before use, otherwise NameError.', 'In `print(x)` value is substituted, in `print("x")` — literal "x".']},
    'operators': {'ru': ['Арифметика: `+ - * /` работает как в школе.', '`//` — целочисленное деление, `%` — остаток.', 'Приоритет: `**` > `* / // %` > `+ -`. Скобки меняют порядок.', '`/` всегда даёт float. Для int — используйте `//`.'], 'en': ['Arithmetic: `+ - * /` works like school math.', '`//` — floor division, `%` — remainder.', 'Precedence: `**` > `* / // %` > `+ -`. Parentheses change order.', '`/` always returns float. For int — use `//`.']},
    'strings': {'ru': ['Строки — неизменяемые последовательности символов.', 'f-строки (`f"..."`) — лучший способ форматирования (Python 3.6+).', 'Методы строк (.strip(), .upper(), .replace() и др.) создают НОВЫЕ строки.', 'Raw-строки (`r"..."`) отключают экранирование — удобно для путей и regex.'], 'en': ['Strings are immutable character sequences.', 'f-strings (`f"..."`) — best formatting (Python 3.6+).', 'String methods (.strip(), .upper(), .replace()) create NEW strings.', 'Raw strings (`r"..."`) disable escaping — handy for paths and regex.']},
    'conditionals': {'ru': ['`if` / `elif` / `else` — ветвление по условиям.', 'Сравнения (`==`, `!=`, `<`, `>`) возвращают True/False.', 'Логика: `and`, `or`, `not`. В Python они возвращают операнд, не обязательно bool.', 'Ошибка: `=` (присваивание) вместо `==` (сравнение).'], 'en': ['`if` / `elif` / `else` — conditional branching.', 'Comparisons (`==`, `!=`, `<`, `>`) return True/False.', 'Logic: `and`, `or`, `not`. In Python they return operand, not necessarily bool.', 'Mistake: `=` (assignment) instead of `==` (comparison).']},
    'loops': {'ru': ['`for x in collection:` — проходит по элементам (не по индексам!).', '`range(n)` — числа от 0 до n-1. `range(1, n+1)` — от 1 до n.', '`while condition:` — пока условие истинно. Нужен `break` для выхода.', '`else` у цикла — выполняется, если НЕ было `break`.'], 'en': ['`for x in collection:` — iterates elements (not indices!).', '`range(n)` — 0 to n-1. `range(1, n+1)` — 1 to n.', '`while condition:` — while truthy. Need `break` to exit.', 'Loop `else` — runs if NO `break` occurred.']},
    'functions': {'ru': ['`def name(params):` — создаёт функцию. `return` — возвращает результат.', 'Без `return` — возвращается `None`.', 'Параметры по умолчанию: `def f(x=10):`. Изменяемые дефолты — ловушка!', 'Именованные аргументы: `f(name="Alex")` — порядок не важен.'], 'en': ['`def name(params):` creates function. `return` sends result back.', 'No `return` — returns `None`.', 'Default params: `def f(x=10):`. Mutable defaults are a trap!', 'Named args: `f(name="Alex")` — order doesn\'t matter.']},
    'lists': {'ru': ['Списки — упорядоченные изменяемые коллекции. Индексы с 0.', '`append()`/`insert()`/`remove()` меняют список НА МЕСТЕ, возвращают None.', 'Срезы: `lst[1:4]` — с 1 по 3 включительно. `lst[:]` — копия.', '`in` проверяет наличие: `"a" in lst`. `len(lst)` — длина.'], 'en': ['Lists are ordered mutable collections. Indices start at 0.', '`append()`/`insert()`/`remove()` mutate IN PLACE, return None.', 'Slices: `lst[1:4]` — indices 1 to 3. `lst[:]` — copy.', '`in` checks membership: `"a" in lst`. `len(lst)` — length.']},
    'dicts': {'ru': ['Словари — пары "ключ: значение". Ключи уникальны и неизменяемы.', 'Доступ: `d[key]` (KeyError если нет) или `d.get(key, default)` (безопасно).', 'Перебор: `for k, v in d.items():`. Проверка: `key in d`.', 'Копия: `d.copy()` или `dict(d)`. Присваивание — та же ссылка!'], 'en': ['Dicts are "key: value" pairs. Keys unique and immutable.', 'Access: `d[key]` (KeyError if missing) or `d.get(key, default)` (safe).', 'Iterate: `for k, v in d.items():`. Check: `key in d`.', 'Copy: `d.copy()` or `dict(d)`. Assignment = same reference!']},
}

# Section templates
SECTION_TEMPLATES = {
    'ru': {
        'heading_objectives': '🎯 Что вы узнаете',
        'heading_intro': '💡 Зачем это нужно?',
        'heading_how_it_works': '🔍 Как это работает',
        'heading_key_points': '📋 Главные моменты',
        'heading_common_mistakes': '⚠️ Типичные ошибки',
        'heading_practice': '🛠 Практика',
        'heading_summary': '📌 Кратко о главном',
        'heading_useful': '🔗 Полезные ссылки',
    },
    'en': {
        'heading_objectives': '🎯 What You\'ll Learn',
        'heading_intro': '💡 Why This Matters',
        'heading_how_it_works': '🔍 How It Works',
        'heading_key_points': '📋 Key Points',
        'heading_common_mistakes': '⚠️ Common Mistakes',
        'heading_practice': '🛠 Practice',
        'heading_summary': '📌 Key Takeaways',
        'heading_useful': '🔗 Useful Links',
    }
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


def get_specific_content(topic: str, language: str, locale: str) -> Dict:
    return SPECIFIC_CONTENT.get(topic, {}).get(language, {}).get(locale, {})


def build_blocks_for_topic(topic: str, language: str, locale: str) -> List[Dict]:
    tpl = SECTION_TEMPLATES[locale]
    topic_display = TOPIC_DISPLAY[locale].get(topic, topic)
    syntax = LANG_SYNTAX.get(language, {})
    blocks = []
    
    specific = get_specific_content(topic, language, locale)
    has_specific = bool(specific)
    
    # 1. Objectives
    blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_objectives']})
    if has_specific and specific.get('key_points'):
        blocks.append({'type': 'list', 'items': specific['key_points'][:5], 'ordered': False})
    else:
        blocks.append({'type': 'list', 'items': [
            f'Понимать суть {topic_display.lower()}' if locale == 'ru' else f'Understand {topic_display.lower()}',
            'Уметь применять на практике' if locale == 'ru' else 'Apply in practice',
            'Избегать частые ошибки' if locale == 'ru' else 'Avoid common mistakes',
        ], 'ordered': False})
    
    # 2. Intro scenario
    blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_intro']})
    if has_specific:
        if specific.get('scenario'):
            blocks.append({'type': 'text', 'content': specific['scenario']})
        if specific.get('naive_code'):
            blocks.append({'type': 'code', 'language': language, 'content': specific['naive_code']})
        if specific.get('pain_point'):
            blocks.append({'type': 'text', 'content': specific['pain_point']})
        if specific.get('solution'):
            blocks.append({'type': 'text', 'content': specific['solution']})
        if specific.get('solution_code'):
            blocks.append({'type': 'code', 'language': language, 'content': specific['solution_code']})
    else:
        blocks.append({'type': 'text', 'content': f'Представьте, что вам нужно решить задачу, связанную с {topic_display.lower()}. Без знания этой темы код был бы громоздким и повторяющимся.' if locale == 'ru' else f'Imagine you need to solve a task related to {topic_display.lower()}. Without this concept, code would be bulky and repetitive.'})
        blocks.append({'type': 'text', 'content': f'Эта тема позволяет писать чистый, переиспользуемый и понятный код.' if locale == 'ru' else 'This concept lets you write clean, reusable, and readable code.'})
    
    # 3. How it works
    if has_specific and (specific.get('explanation') or specific.get('visual') or specific.get('how_it_works')):
        blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_how_it_works']})
        if specific.get('explanation'):
            blocks.append({'type': 'text', 'content': specific['explanation']})
        if specific.get('visual'):
            blocks.append({'type': 'text', 'content': f'**Схема:**\n```\n{specific["visual"]}\n```' if locale == 'ru' else f'**Diagram:**\n```\n{specific["visual"]}\n```'})
        if specific.get('how_it_works'):
            blocks.append({'type': 'text', 'content': specific['how_it_works']})
        if specific.get('substitution'):
            blocks.append({'type': 'code', 'language': language, 'content': specific['substitution']})
    else:
        blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_how_it_works']})
        blocks.append({'type': 'text', 'content': f'Когда вы используете {topic_display.lower()}, происходит следующее:' if locale == 'ru' else f'When you use {topic_display.lower()}, here\'s what happens:'})
        blocks.append({'type': 'text', 'content': f'1. Создаёте/объявляете сущность\n2. Работаете с ней по правилам языка\n3. Получаете результат' if locale == 'ru' else '1. Create/declare the entity\n2. Work with it per language rules\n3. Get result'})
        if syntax.get('decl'):
            blocks.append({'type': 'code', 'language': language, 'content': f'# Пример объявления\n{syntax["decl"]}\n\n# Использование\n{syntax["print"]}' if locale == 'ru' else f'// Declaration example\n{syntax["decl"]}\n\n// Usage\n{syntax["print"]}'})
    
    # 4. Key points
    key_points = specific.get('key_points') if has_specific else None
    if not key_points:
        key_points = [
            f'{topic_display} — фундаментальная концепция' if locale == 'ru' else f'{topic_display} is a fundamental concept',
            'Синтаксис прост, но мощи хватает на всё' if locale == 'ru' else 'Syntax is simple but powerful',
            'Практика — лучший способ закрепить' if locale == 'ru' else 'Practice is the best way to learn',
        ]
    blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_key_points']})
    blocks.append({'type': 'list', 'items': key_points, 'ordered': False})
    
    # 5. Common mistakes
    mistakes = COMMON_MISTAKES.get(topic, {}).get(language, {}).get(locale, GENERIC_MISTAKES.get(locale, GENERIC_MISTAKES['ru']))
    blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_common_mistakes']})
    blocks.append({'type': 'text', 'content': 'Вот самые частые ошибки и как их избежать:' if locale == 'ru' else 'Here are the most common mistakes and how to avoid them:'})
    blocks.append({'type': 'table', 'headers': ['Ошибка', 'Как проявляется', 'Как правильно'] if locale == 'ru' else ['Mistake', 'How It Shows', 'Correct Way'], 'rows': mistakes})
    
    # 6. Practice
    tasks = PRACTICE_TASKS.get(topic, {}).get(language, {}).get(locale, GENERIC_PRACTICE.get(locale, GENERIC_PRACTICE['ru']))
    blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_practice']})
    blocks.append({'type': 'text', 'content': 'Попробуйте сами — это лучший способ запомнить:' if locale == 'ru' else 'Try it yourself — that\'s the best way to learn:'})
    blocks.append({'type': 'list', 'items': tasks, 'ordered': True})
    
    # 7. Summary
    takeaways = KEY_TAKEAWAYS.get(topic, {}).get(locale, GENERIC_TAKEAWAYS.get(locale, GENERIC_TAKEAWAYS['ru']))
    blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_summary']})
    blocks.append({'type': 'list', 'items': takeaways, 'ordered': False})
    
    # 8. Useful links
    links = USEFUL_LINKS.get(topic, {}).get(locale, GENERIC_LINKS.get(locale, GENERIC_LINKS['ru']))
    blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_useful']})
    blocks.append({'type': 'list', 'items': links, 'ordered': False})
    
    return blocks


def build_lesson(data: Dict, language: str, lesson_num: int) -> Dict:
    topic = get_topic(language, lesson_num)
    
    data['content_blocks'] = build_blocks_for_topic(topic, language, 'ru')
    data['content_en'] = build_blocks_for_topic(topic, language, 'en')
    
    topic_display_ru = TOPIC_DISPLAY['ru'].get(topic, topic)
    topic_display_en = TOPIC_DISPLAY['en'].get(topic, topic)
    
    data['goals'] = [
        f'Понимать {topic_display_ru.lower()}',
        'Уметь применять на практике',
        'Распознавать и избегать частые ошибки',
    ]
    data['practice_tasks'] = PRACTICE_TASKS.get(topic, {}).get(language, {}).get('ru', GENERIC_PRACTICE.get('ru', GENERIC_PRACTICE['ru']))
    data['common_errors'] = [
        {'mistake': m[0], 'correct': m[2]} 
        for m in COMMON_MISTAKES.get(topic, {}).get(language, {}).get('ru', GENERIC_MISTAKES.get('ru', GENERIC_MISTAKES['ru']))
    ]
    data['resources'] = USEFUL_LINKS.get(topic, {}).get(language, {}).get('ru', GENERIC_LINKS.get('ru', GENERIC_LINKS['ru']))
    data['key_takeaways'] = KEY_TAKEAWAYS.get(topic, {}).get('ru', GENERIC_TAKEAWAYS.get('ru', GENERIC_TAKEAWAYS['ru']))
    
    data['name_en'] = f"Lesson: {topic_display_en}"
    data['short_description_en'] = f"Learn {topic_display_en.lower()} in {language.capitalize()}"
    
    total_chars = sum(len(json.dumps(b, ensure_ascii=False)) for b in data['content_blocks'])
    data['estimated_minutes'] = max(15, min(45, total_chars // 800))
    
    return data


def process_lesson(filepath: Path, language: str, lesson_num: int) -> Dict:
    data = load_lesson(filepath)
    data = build_lesson(data, language, lesson_num)
    return data


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Rewrite lessons in friendly style v3')
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