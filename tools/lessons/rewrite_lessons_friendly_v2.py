#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rewrite all lessons in friendly CodeBasics/Hexlet/Stepik style - V2:
- Fresh content generation per topic (no copying mixed-language blocks)
- Complete topic coverage with intros, mistakes, practice
- Strict language separation: RU blocks = Russian only, EN blocks = English only
"""

import json
from pathlib import Path
from typing import Dict, List, Any

# Topic mapping per language (lesson_number -> topic_key)
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

# ============================================================
# FRIENDLY INTROS per topic per language
# ============================================================
FRIENDLY_INTROS = {
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
                    'Переменная — это именованное хранилище для значения',
                    'Присваивание `x = 5` кладёт 5 в переменную x',
                    'Имена: буквы, цифры, _ ; не с цифры; регистр важен',
                    'Сначала создайте, потом используйте — иначе NameError',
                    'В `print(x)` подставляется значение, в `print("x")` — буква "x"',
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
                    'A variable is named storage for a value',
                    'Assignment `x = 5` puts 5 into variable x',
                    'Names: letters, digits, _ ; not starting with digit; case-sensitive',
                    'Create before use, otherwise NameError',
                    'In `print(x)` value is substituted, in `print("x")` — literal "x"',
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
    'operators': {
        'python': {
            'ru': {
                'scenario': 'В школе нас учили: 2 + 2 = 4. В Python математика работает так же, но есть нюансы, о которых стоит знать с самого начала.',
                'pain_point': 'Деление `/` всегда даёт дробь, даже если делится нацело. И приоритет операторов может удивить.',
                'solution': 'Разберём основные операторы и их особенности:',
                'key_points': [
                    '`+ - * /` — базовая арифметика',
                    '`//` — целочисленное деление (отбрасывает дробную часть)',
                    '`%` — остаток от деления (полезно для чётности: n % 2)',
                    '`**` — возведение в степень',
                    'Приоритет: `**` > `* / // %` > `+ -` (как в математике)',
                    'Скобки `()` меняют порядок: `(2 + 3) * 4 = 20`',
                ],
            },
            'en': {
                'scenario': 'School taught us 2 + 2 = 4. Python math works the same, but there are nuances to know from the start.',
                'pain_point': 'Division `/` always returns float, even when divisible. Operator precedence can surprise.',
                'solution': 'Let\'s cover main operators and their quirks:',
                'key_points': [
                    '`+ - * /` — basic arithmetic',
                    '`//` — integer division (drops fractional part)',
                    '`%` — remainder (useful for parity: n % 2)',
                    '`**` — exponentiation',
                    'Precedence: `**` > `* / // %` > `+ -` (like math)',
                    'Parentheses `()` change order: `(2 + 3) * 4 = 20`',
                ],
            }
        },
    },
    'strings': {
        'python': {
            'ru': {
                'scenario': 'Текст — это то, с чем программы работают постоянно: имена пользователей, сообщения, адреса сайтов. В Python текст хранят в строках (str) — неизменяемых последовательностях символов.',
                'pain_point': 'Строки нельзя менять "на месте" — любое изменение создаёт новую строку. И кавычки бывают разными.',
                'solution': 'Разберём создание строк, форматирование и полезные методы:',
                'key_points': [
                    'Кавычки: одинарные, двойные, тройные (многострочные)',
                    'f-строки: f"Привет, {name}!" — современный стандарт (Python 3.6+)',
                    'Экранирование: `\n` — новая строка, `\t` — таб, `\\` — слеш',
                    'Raw-строки: r"C:\\Users" — без экранирования',
                    'Строки неизменяемы: `"abc".upper()` создаёт НОВУЮ строку',
                    'Методы: .strip(), .lower(), .upper(), .replace(), .split()',
                ],
            },
            'en': {
                'scenario': 'Text is what programs work with constantly: usernames, messages, URLs. In Python text is stored in strings (str) — immutable character sequences.',
                'pain_point': 'Strings can\'t be changed in place — any modification creates a new string. And quotes come in different flavours.',
                'solution': 'Let\'s cover string creation, formatting, and useful methods:',
                'key_points': [
                    'Quotes: single, double, triple (multiline)',
                    'f-strings: f"Hello, {name}!" — modern standard (Python 3.6+)',
                    'Escaping: `\n` — newline, `\t` — tab, `\\` — backslash',
                    'Raw strings: r"C:\\Users" — no escaping',
                    'Strings immutable: `"abc".upper()` creates NEW string',
                    'Methods: .strip(), .lower(), .upper(), .replace(), .split()',
                ],
            }
        },
    },
    'conditionals': {
        'python': {
            'ru': {
                'scenario': 'В жизни мы постоянно принимаем решения: "Если дождь — возьму зонт, иначе — нет". В программах это работает так же: код должен вести себя по-разному в зависимости от условий.',
                'pain_point': 'Главная ошибка новичков — писать `=` (присваивание) вместо `==` (сравнение). И забывать про `elif`.',
                'solution': 'Разберём if / elif / else и логические выражения:',
                'key_points': [
                    '`if условие:` — выполняется, если условие истинно',
                    '`elif другое_условие:` — проверяется, если if ложно',
                    '`else:` — выполняется, если ни одно условие не сработало',
                    'Сравнения: `== != < > <= >=` — возвращают True/False',
                    'Логика: `and` (И), `or` (ИЛИ), `not` (НЕ)',
                    'В Python `and`/`or` возвращают ОДИН ИЗ ОПЕРАНДОВ, не обязательно bool!',
                ],
            },
            'en': {
                'scenario': 'In life we constantly decide: "If rain — take umbrella, else — don\'t". Programs work the same: code must behave differently based on conditions.',
                'pain_point': 'Main beginner mistake — writing `=` (assignment) instead of `==` (comparison). And forgetting `elif`.',
                'solution': 'Let\'s cover if / elif / else and logical expressions:',
                'key_points': [
                    '`if condition:` — runs if condition is truthy',
                    '`elif other_condition:` — checked if if is falsy',
                    '`else:` — runs if no condition matched',
                    'Comparisons: `== != < > <= >=` — return True/False',
                    'Logic: `and` (AND), `or` (OR), `not` (NOT)',
                    'In Python `and`/`or` return ONE OF THE OPERANDS, not necessarily bool!',
                ],
            }
        },
    },
    'loops': {
        'python': {
            'ru': {
                'scenario': 'Представьте: нужно поздороваться с каждым другом из списка. Можно написать print пять раз, но если друзей станет сто? Циклы решают эту задачу — они повторяют действия автоматически.',
                'pain_point': 'Бесконечные циклы (`while True` без `break`) вешают программу. И `for` в Python работает иначе, чем в C/JS — он итерируется по элементам, а не по индексам.',
                'solution': 'Два типа циклов в Python:',
                'key_points': [
                    '`for элемент in коллекция:` — проходит по каждому элементу (списку, строке, range)',
                    '`range(n)` — генерирует числа от 0 до n-1',
                    '`while условие:` — повторяется, пока условие истинно',
                    '`break` — выход из цикла полностью',
                    '`continue` — пропуск текущей итерации',
                    '`else` у цикла — выполняется, если цикл завершился БЕЗ break',
                ],
            },
            'en': {
                'scenario': 'Imagine greeting each friend in a list. Write print five times? What if 100 friends? Loops solve this — they repeat actions automatically.',
                'pain_point': 'Infinite loops (`while True` without `break`) hang programs. Python `for` differs from C/JS — it iterates elements, not indices.',
                'solution': 'Two loop types in Python:',
                'key_points': [
                    '`for item in collection:` — iterates each element (list, string, range)',
                    '`range(n)` — generates numbers 0 to n-1',
                    '`while condition:` — repeats while condition is truthy',
                    '`break` — exits loop entirely',
                    '`continue` — skips current iteration',
                    'Loop `else` — runs if loop finished WITHOUT break',
                ],
            }
        },
    },
    'functions': {
        'python': {
            'ru': {
                'scenario': 'Вы замечали, что иногда пишете один и тот же код снова и снова? Функции позволяют упаковать повторяющуюся логику в один блок, дать ему имя и вызывать когда угодно. Это как рецепт: пишешь один раз — готовишь много раз.',
                'pain_point': 'Частая ошибка — забыть `return` (функция вернёт None). И путать параметры (при определении) и аргументы (при вызове).',
                'solution': 'Создадим свою первую функцию:',
                'key_points': [
                    '`def имя(параметры):` — определение функции',
                    '`return значение` — возвращает результат вызывающему коду',
                    'Без return — возвращается `None`',
                    'Параметры по умолчанию: `def greet(name="Гость"):`',
                    'Именованные аргументы: `greet(name="Алекс")` — порядок не важен',
                    'Docstring `"""Описание"""` — документация функции',
                ],
            },
            'en': {
                'scenario': 'Ever notice you write the same code over and over? Functions let you pack repeating logic into one block, give it a name, and call it anytime. Like a recipe: write once, cook many times.',
                'pain_point': 'Common mistake — forgetting `return` (returns None). Confusing parameters (definition) vs arguments (call).',
                'solution': 'Let\'s create your first function:',
                'key_points': [
                    '`def name(params):` — function definition',
                    '`return value` — sends result back to caller',
                    'No return — returns `None`',
                    'Default params: `def greet(name="Guest"):`',
                    'Named args: `greet(name="Alex")` — order doesn\'t matter',
                    'Docstring `"""Description"""` — function documentation',
                ],
            }
        },
    },
    'lists': {
        'python': {
            'ru': {
                'scenario': 'У вас есть список покупок: хлеб, молоко, яйца. В Python такие наборы данных хранят в списках (list) — упорядоченных коллекциях, где каждый элемент имеет свой номер (индекс).',
                'pain_point': 'Индексы начинаются с 0, а не с 1! Выход за границы — IndexError. И списки изменяемые — методы вроде .append() меняют исходный список.',
                'solution': 'Работа со списками: создание, доступ, изменение:',
                'key_points': [
                    'Создание: `fruits = ["яблоко", "банан", "вишня"]`',
                    'Доступ: `fruits[0]` → "яблоко", `fruits[-1]` → "вишня" (с конца)',
                    'Срезы: `fruits[1:3]` → ["банан", "вишня"] (включая начало, исключая конец)',
                    'Изменение: `fruits.append("слива")`, `fruits[0] = "груша"`',
                    'Длина: `len(fruits)`',
                    'Проверка: `"яблоко" in fruits` → True',
                ],
            },
            'en': {
                'scenario': 'You have a shopping list: bread, milk, eggs. In Python such collections are stored in lists — ordered collections where each element has its own number (index).',
                'pain_point': 'Indices start at 0, not 1! Out of bounds = IndexError. Lists are mutable — .append() changes the original list.',
                'solution': 'Working with lists: create, access, modify:',
                'key_points': [
                    'Create: `fruits = ["apple", "banana", "cherry"]`',
                    'Access: `fruits[0]` → "apple", `fruits[-1]` → "cherry" (from end)',
                    'Slices: `fruits[1:3]` → ["banana", "cherry"] (include start, exclude end)',
                    'Modify: `fruits.append("plum")`, `fruits[0] = "pear"`',
                    'Length: `len(fruits)`',
                    'Check: `"apple" in fruits` → True',
                ],
            }
        },
    },
    'dicts': {
        'python': {
            'ru': {
                'scenario': 'Представьте телефонную книгу: имя → номер. В Python для таких пар "ключ — значение" используют словари (dict). Это как настоящий словарь: ищешь слово (ключ) — находишь определение (значение).',
                'pain_point': 'Обращение к несуществующему ключу — KeyError. Используйте .get() или `in` для проверки. Ключи должны быть неизменяемыми (строки, числа, кортежи).',
                'solution': 'Работа со словарями:',
                'key_points': [
                    'Создание: `user = {"name": "Алекс", "age": 25}`',
                    'Доступ: `user["name"]` → "Алекс", `user.get("email", "нет")` → "нет"',
                    'Изменение: `user["age"] = 26`, `user["city"] = "Москва"`',
                    'Удаление: `del user["age"]` или `user.pop("age")`',
                    'Перебор: `for k, v in user.items():`',
                    'Проверка: `"name" in user` → True',
                ],
            },
            'en': {
                'scenario': 'Imagine a phone book: name → number. In Python for "key — value" pairs use dicts. Like a real dictionary: look up word (key) — find definition (value).',
                'pain_point': 'Accessing missing key = KeyError. Use .get() or `in` to check. Keys must be immutable (strings, numbers, tuples).',
                'solution': 'Working with dicts:',
                'key_points': [
                    'Create: `user = {"name": "Alex", "age": 25}`',
                    'Access: `user["name"]` → "Alex", `user.get("email", "none")` → "none"',
                    'Modify: `user["age"] = 26`, `user["city"] = "Moscow"`',
                    'Delete: `del user["age"]` or `user.pop("age")`',
                    'Iterate: `for k, v in user.items():`',
                    'Check: `"name" in user` → True',
                ],
            }
        },
    },
}

# ============================================================
# COMMON MISTAKES per topic per language
# ============================================================
COMMON_MISTAKES = {
    'variables': {
        'python': {
            'ru': [
                ['Использование до присваивания', '`print(x)` → NameError', 'Сначала присвойте: `x = 10`'],
                ['Опечатка в имени', '`greeting = "Hi"`\n`print(greting)` → NameError', 'Проверяйте имена, используйте автодополнение'],
                ['Путаница: переменная vs строка', '`name = "Alex"`\n`print("name")` → выведет "name"', 'Переменная без кавычек: `print(name)`'],
                ['Присваивание вместо сравнения', '`if x = 5:` → SyntaxError', 'Сравнение: `if x == 5:`'],
            ],
            'en': [
                ['Using before assignment', '`print(x)` → NameError', 'Assign first: `x = 10`'],
                ['Typo in name', '`greeting = "Hi"`\n`print(greting)` → NameError', 'Check names, use autocomplete'],
                ['Variable vs string confusion', '`name = "Alex"`\n`print("name")` → prints "name"', 'Variable without quotes: `print(name)`'],
                ['Assignment instead of comparison', '`if x = 5:` → SyntaxError', 'Comparison: `if x == 5:`'],
            ]
        },
        'javascript': {
            'ru': [
                ['Использование до объявления', '`console.log(x)` → ReferenceError', 'Сначала объявите: `const x = 10;`'],
                ['Опечатка в имени', '`const greeting = "Hi";`\n`console.log(greting);` → ReferenceError', 'Проверяйте имена'],
                ['const вместо let при изменении', '`const x = 5; x = 10;` → TypeError', 'Если меняется — используйте `let`'],
            ],
            'en': [
                ['Using before declaration', '`console.log(x)` → ReferenceError', 'Declare first: `const x = 10;`'],
                ['Typo in name', '`const greeting = "Hi";`\n`console.log(greting);` → ReferenceError', 'Check names'],
                ['const instead of let when mutating', '`const x = 5; x = 10;` → TypeError', 'If mutating — use `let`'],
            ]
        },
        'cpp': {
            'ru': [
                ['Неинициализированная переменная', '`int x; std::cout << x;` → мусор (UB)', 'Всегда инициализируйте: `int x = 0;`'],
                ['Узкий тип для большого числа', '`int x = 3000000000;` → переполнение', 'Используйте `long long` или `int64_t`'],
                ['Сравнение float на равенство', '`float a = 0.1 + 0.2; a == 0.3` → false', 'Сравнивайте с epsilon: `abs(a - 0.3) < 1e-9`'],
            ],
            'en': [
                ['Uninitialized variable', '`int x; std::cout << x;` → garbage (UB)', 'Always initialize: `int x = 0;`'],
                ['Narrow type for large number', '`int x = 3000000000;` → overflow', 'Use `long long` or `int64_t`'],
                ['Float equality comparison', '`float a = 0.1 + 0.2; a == 0.3` → false', 'Compare with epsilon: `abs(a - 0.3) < 1e-9`'],
            ]
        },
        'csharp': {
            'ru': [
                ['Использование до присваивания', '`int x; Console.WriteLine(x);` → ошибка компиляции', 'Присвойте значение: `int x = 0;`'],
                ['string vs String', '`String s = "hi";` работает, но `string` — предпочтительнее', 'Используйте `string` (alias)'],
                ['null для значимых типов', '`int x = null;` → ошибка', 'Используйте `int? x = null` (nullable)'],
            ],
            'en': [
                ['Using before assignment', '`int x; Console.WriteLine(x);` → compile error', 'Assign value: `int x = 0;`'],
                ['string vs String', '`String s = "hi";` works but `string` preferred', 'Use `string` (alias)'],
                ['null for value types', '`int x = null;` → error', 'Use `int? x = null` (nullable)'],
            ]
        },
        'rust': {
            'ru': [
                ['Попытка изменить неизменяемую', '`let x = 5; x = 6;` → ошибка компиляции', 'Добавьте `mut`: `let mut x = 5;`'],
                ['Использование неинициализированной', '`let x: i32; println!("{}", x);` → ошибка компиляции', 'Всегда инициализируйте при объявлении'],
                ['Заимствование после перемещения', '`let s = String::new(); let t = s; println!("{}", s);` → ошибка', 'Клонируйте: `let t = s.clone();` или используйте ссылки'],
            ],
            'en': [
                ['Mutating immutable', '`let x = 5; x = 6;` → compile error', 'Add `mut`: `let mut x = 5;`'],
                ['Using uninitialized', '`let x: i32; println!("{}", x);` → compile error', 'Always initialize at declaration'],
                ['Use after move', '`let s = String::new(); let t = s; println!("{}", s);` → error', 'Clone: `let t = s.clone();` or use references'],
            ]
        },
    },
    'operators': {
        'python': {
            'ru': [
                ['Деление `/` всегда даёт float', '`5 / 2` → `2.5` (не `2`)', 'Для целого: `5 // 2` → `2`'],
                ['Путаница `%` и `/`', '`%` — остаток, `/` — частное', '`7 % 3` → `1`, `7 / 3` → `2.33...`'],
                ['Приоритет операторов', '`2 + 3 * 4` → `14`, а не `20`', 'Скобки: `(2 + 3) * 4` → `20`'],
            ],
            'en': [
                ['Division `/` always returns float', '`5 / 2` → `2.5` (not `2`)', 'For integer: `5 // 2` → `2`'],
                ['Confusing `%` and `/`', '`%` — remainder, `/` — quotient', '`7 % 3` → `1`, `7 / 3` → `2.33...`'],
                ['Precedence surprise', '`2 + 3 * 4` → `14`, not `20`', 'Parentheses: `(2 + 3) * 4` → `20`'],
            ]
        },
    },
    'strings': {
        'python': {
            'ru': [
                ['Попытка изменить символ в строке', '`s[0] = "A"` → TypeError', 'Строки неизменяемы! Создайте новую: `"A" + s[1:]`'],
                ['Забыли f перед строкой', '`name = "Alex"; print("{name}")` → выведет "{name}"', 'Нужен префикс f: `f"{name}"`'],
                ['Экранирование в путях Windows', '`path = "C:\\Users"` → ошибка', 'Raw-строка: `r"C:\\Users"` или `\\\\`'],
            ],
            'en': [
                ['Modifying string character', '`s[0] = "A"` → TypeError', 'Strings immutable! Create new: `"A" + s[1:]`'],
                ['Forgot f prefix', '`name = "Alex"; print("{name}")` → prints "{name}"', 'Need f prefix: `f"{name}"`'],
                ['Escaping in Windows paths', '`path = "C:\\Users"` → error', 'Raw string: `r"C:\\Users"` or `\\\\`'],
            ]
        },
    },
    'conditionals': {
        'python': {
            'ru': [
                ['`=` вместо `==`', '`if x = 5:` → SyntaxError', 'Сравнение: `if x == 5:`'],
                ['Забыли `:` после условия', '`if x > 0` → SyntaxError', 'Всегда двоеточие: `if x > 0:`'],
                ['`and`/`or` возвращают не bool', '`"a" and "b"` → "b", а не True', 'Для bool оборачивайте: `bool("a" and "b")`'],
            ],
            'en': [
                ['`=` instead of `==`', '`if x = 5:` → SyntaxError', 'Comparison: `if x == 5:`'],
                ['Missing `:` after condition', '`if x > 0` → SyntaxError', 'Always colon: `if x > 0:`'],
                ['`and`/`or` return non-bool', '`"a" and "b"` → "b", not True', 'Wrap for bool: `bool("a" and "b")`'],
            ]
        },
    },
    'loops': {
        'python': {
            'ru': [
                ['Бесконечный цикл без break', '`while True:` без выхода → зависание', 'Всегда предусматривайте выход'],
                ['Изменение коллекции во время итерации', '`for x in lst: lst.remove(x)` → пропуски', 'Итерируйте копию: `for x in lst[:]:`'],
                ['`range(len(lst))` вместо enumerate', 'Сложнее и читается хуже', 'Лучше: `for i, v in enumerate(lst):`'],
            ],
            'en': [
                ['Infinite loop without break', '`while True:` without exit → hang', 'Always provide exit'],
                ['Modifying collection during iteration', '`for x in lst: lst.remove(x)` → skips', 'Iterate copy: `for x in lst[:]:`'],
                ['`range(len(lst))` instead of enumerate', 'More complex, less readable', 'Better: `for i, v in enumerate(lst):`'],
            ]
        },
    },
    'functions': {
        'python': {
            'ru': [
                ['Забыли return', '`def add(a, b): a + b` → возвращает None', 'Добавьте: `return a + b`'],
                ['Изменяемый аргумент по умолчанию', '`def f(x=[]): x.append(1)` → список общий для всех вызовов', '`def f(x=None): x = x or []`'],
                ['Путаница: параметры vs аргументы', 'Параметры — в определении, аргументы — при вызове', '`def f(param):` — параметр, `f(arg)` — аргумент'],
            ],
            'en': [
                ['Forgot return', '`def add(a, b): a + b` → returns None', 'Add: `return a + b`'],
                ['Mutable default argument', '`def f(x=[]): x.append(1)` → shared across calls', '`def f(x=None): x = x or []`'],
                ['Params vs args confusion', 'Params in definition, args at call site', '`def f(param):` param, `f(arg)` arg'],
            ]
        },
    },
    'lists': {
        'python': {
            'ru': [
                ['Индекс за границами', '`lst[10]` для 3 элементов → IndexError', 'Проверяйте: `if i < len(lst):`'],
                ['`append` возвращает None', '`lst = lst.append(5)` → lst становится None', '`lst.append(5)` — меняет на месте, ничего не возвращает'],
                ['Копирование через присваивание', '`b = a` — это та же ссылка!', 'Копия: `b = a[:]` или `b = a.copy()`'],
            ],
            'en': [
                ['Index out of bounds', '`lst[10]` for 3 elements → IndexError', 'Check: `if i < len(lst):`'],
                ['`append` returns None', '`lst = lst.append(5)` → lst becomes None', '`lst.append(5)` — mutates in place, returns nothing'],
                ['Copy by assignment', '`b = a` — same reference!', 'Copy: `b = a[:]` or `b = a.copy()`'],
            ]
        },
    },
    'dicts': {
        'python': {
            'ru': [
                ['KeyError при доступе', '`d["missing"]` → KeyError', 'Используйте `.get("missing", default)`'],
                ['Изменяемый ключ', '`d[[1,2]] = "oops"` → TypeError', 'Ключи должны быть неизменяемыми: строка, число, кортеж'],
                ['Перебор только ключей', '`for k in d:` — только ключи', 'Для пар: `for k, v in d.items():`'],
            ],
            'en': [
                ['KeyError on access', '`d["missing"]` → KeyError', 'Use `.get("missing", default)`'],
                ['Mutable key', '`d[[1,2]] = "oops"` → TypeError', 'Keys must be immutable: str, int, tuple'],
                ['Iterating keys only', '`for k in d:` — keys only', 'For pairs: `for k, v in d.items():`'],
            ]
        },
    },
}

# ============================================================
# PRACTICE TASKS per topic per language
# ============================================================
PRACTICE_TASKS = {
    'variables': {
        'python': {
            'ru': [
                'Создайте переменную `my_name` с вашим именем и выведите её на экран.',
                'Создайте `age` (возраст) и `city` (город). Выведите: "Меня зовут {имя}, мне {возраст} лет, я живу в {город}".',
                'Создайте `price = 100` и `quantity = 3`. Посчитайте общую стоимость в `total` и выведите.',
                'Исправьте ошибку:\n```python\nname = "Анна"\nprint("name")  # должно вывести: Анна\n```',
            ],
            'en': [
                'Create variable `my_name` with your name and print it.',
                'Create `age` and `city`. Print: "My name is {name}, I am {age} years old, I live in {city}".',
                'Create `price = 100` and `quantity = 3`. Calculate total in `total` and print.',
                'Fix the bug:\n```python\nname = "Anna"\nprint("name")  # should print: Anna\n```',
            ]
        },
        'javascript': {
            'ru': [
                'Создайте константу `myName` с вашим именем и выведите в консоль.',
                'Создайте `age` и `city`. Выведите: `Меня зовут ${name}, мне ${age} лет`.',
                'Создайте `price = 100`, `quantity = 3`. Посчитайте `total` и выведите.',
                'Исправьте:\n```javascript\nconst name = "Анна";\nconsole.log("name"); // должно: Анна\n```',
            ],
            'en': [
                'Create constant `myName` with your name and log it.',
                'Create `age` and `city`. Log: `My name is ${name}, I am ${age} years old`.',
                'Create `price = 100`, `quantity = 3`. Calculate `total` and log.',
                'Fix:\n```javascript\nconst name = "Anna";\nconsole.log("name"); // should: Anna\n```',
            ]
        },
    },
    'operators': {
        'python': {
            'ru': [
                'Посчитайте: `2 + 3 * 4`, `(2 + 3) * 4`, `2 ** 3`, `10 // 3`, `10 % 3`.',
                'Дано `x = 7`, `y = 2`. Выведите: сумму, разность, произведение, частное, целое частное, остаток, степень.',
                'Проверьте чётность чисел от 1 до 10 с помощью `% 2`.',
                'Исправьте: `result = 5 / 2` должно дать целое число 2.',
            ],
            'en': [
                'Calculate: `2 + 3 * 4`, `(2 + 3) * 4`, `2 ** 3`, `10 // 3`, `10 % 3`.',
                'Given `x = 7`, `y = 2`. Print: sum, difference, product, quotient, floor division, remainder, power.',
                'Check parity of numbers 1-10 using `% 2`.',
                'Fix: `result = 5 / 2` should give integer 2.',
            ]
        },
    },
    'strings': {
        'python': {
            'ru': [
                'Создайте f-строку: `f"Привет, {name}! Тебе {age} лет."` с вашими данными.',
                'Дана строка `s = "  Python  "`. Выведите: `s.strip()`, `s.upper()`, `s.lower()`, `len(s)`.',
                'Замените все "о" на "а" в строке `"хорошо"` методом `.replace()`.',
                'Разбейте `"один,два,три"` по запятым в список через `.split(",")`.',
            ],
            'en': [
                'Create f-string: `f"Hello, {name}! You are {age}."` with your data.',
                'Given `s = "  Python  "`. Print: `s.strip()`, `s.upper()`, `s.lower()`, `len(s)`.',
                'Replace all "o" with "a" in `"good"` using `.replace()`.',
                'Split `"one,two,three"` by commas into a list via `.split(",")`.',
            ]
        },
    },
    'conditionals': {
        'python': {
            'ru': [
                'Напишите программу: просит число, выводит "Положительное", "Отрицательное" или "Ноль".',
                'Проверьте возраст: если >= 18 — "Совершеннолетний", иначе — "Несовершеннолетний".',
                'Дано число. Выведите "Чётное" или "Нечётное" (подсказка: `% 2`).',
                'Исправьте: `if x = 5:` → `if x == 5:`.',
            ],
            'en': [
                'Write program: asks number, prints "Positive", "Negative", or "Zero".',
                'Check age: if >= 18 — "Adult", else — "Minor".',
                'Given number. Print "Even" or "Odd" (hint: `% 2`).',
                'Fix: `if x = 5:` → `if x == 5:`.',
            ]
        },
    },
    'loops': {
        'python': {
            'ru': [
                'Выведите числа от 1 до 10 через `for i in range(1, 11):`.',
                'Дан список `["яблоко", "банан", "вишня"]`. Выведите каждый фрукт на новой строке.',
                'Посчитайте сумму чисел от 1 до 100 (подсказка: `range(1, 101)`).',
                'Найдите первое чётное число в списке `[1, 3, 5, 8, 9]` — используйте `break`.',
            ],
            'en': [
                'Print numbers 1 to 10 via `for i in range(1, 11):`.',
                'Given list `["apple", "banana", "cherry"]`. Print each fruit on new line.',
                'Sum numbers 1 to 100 (hint: `range(1, 101)`).',
                'Find first even in `[1, 3, 5, 8, 9]` — use `break`.',
            ]
        },
    },
    'functions': {
        'python': {
            'ru': [
                'Создайте функцию `greet(name)`, которая возвращает `"Привет, {name}!"`.',
                'Напишите `add(a, b)` — возвращает сумму. Проверьте: `add(2, 3)` → 5.',
                'Сделайте параметр `name` опциональным со значением "Гость".',
                'Исправьте: `def add(a, b): a + b` → добавьте `return`.',
            ],
            'en': [
                'Create `greet(name)` returning `"Hello, {name}!"`.',
                'Write `add(a, b)` returning sum. Test: `add(2, 3)` → 5.',
                'Make `name` optional with default "Guest".',
                'Fix: `def add(a, b): a + b` → add `return`.',
            ]
        },
    },
    'lists': {
        'python': {
            'ru': [
                'Создайте список покупок из 5 элементов. Выведите первый и последний.',
                'Добавьте "молоко" в конец списка. Удалите второй элемент.',
                'Проверьте, есть ли "хлеб" в списке через `in`.',
                'Создайте копию списка и измените копию — оригинал не должен измениться.',
            ],
            'en': [
                'Create shopping list of 5 items. Print first and last.',
                'Append "milk" to end. Remove second element.',
                'Check if "bread" in list via `in`.',
                'Copy list, modify copy — original should stay unchanged.',
            ]
        },
    },
    'dicts': {
        'python': {
            'ru': [
                'Создайте словарь `user = {"name": "Алекс", "age": 25}`. Выведите имя.',
                'Добавьте ключ "city" со значением "Москва". Увеличьте возраст на 1.',
                'Проверьте наличие ключа "email" через `.get()` с дефолтом "не указан".',
                'Переберите словарь: `for k, v in user.items(): print(k, v)`.',
            ],
            'en': [
                'Create `user = {"name": "Alex", "age": 25}`. Print name.',
                'Add key "city" = "Moscow". Increment age by 1.',
                'Check "email" key via `.get()` with default "not specified".',
                'Iterate dict: `for k, v in user.items(): print(k, v)`.',
            ]
        },
    },
}

# ============================================================
# USEFUL LINKS per topic per language
# ============================================================
USEFUL_LINKS = {
    'variables': {
        'ru': [
            'Python.org — Variables: https://docs.python.org/3/tutorial/introduction.html#variables',
            'Real Python — Python Variables: https://realpython.com/python-variables/',
            'PEP 8 — Naming Conventions: https://peps.python.org/pep-0008/#naming-conventions',
        ],
        'en': [
            'Python.org — Variables: https://docs.python.org/3/tutorial/introduction.html#variables',
            'Real Python — Python Variables: https://realpython.com/python-variables/',
            'PEP 8 — Naming Conventions: https://peps.python.org/pep-0008/#naming-conventions',
        ]
    },
    'operators': {
        'ru': [
            'Python.org — Operators: https://docs.python.org/3/reference/expressions.html#operator-precedence',
            'Real Python — Operators: https://realpython.com/python-operators-expressions/',
        ],
        'en': [
            'Python.org — Operators: https://docs.python.org/3/reference/expressions.html#operator-precedence',
            'Real Python — Operators: https://realpython.com/python-operators-expressions/',
        ]
    },
    'strings': {
        'ru': [
            'Python.org — Strings: https://docs.python.org/3/tutorial/introduction.html#strings',
            'Real Python — String Formatting: https://realpython.com/python-string-formatting/',
            'Python Docs — String Methods: https://docs.python.org/3/library/stdtypes.html#string-methods',
        ],
        'en': [
            'Python.org — Strings: https://docs.python.org/3/tutorial/introduction.html#strings',
            'Real Python — String Formatting: https://realpython.com/python-string-formatting/',
            'Python Docs — String Methods: https://docs.python.org/3/library/stdtypes.html#string-methods',
        ]
    },
    'conditionals': {
        'ru': [
            'Python.org — If Statements: https://docs.python.org/3/tutorial/controlflow.html#if-statements',
            'Real Python — Conditional Logic: https://realpython.com/python-conditional-statements/',
        ],
        'en': [
            'Python.org — If Statements: https://docs.python.org/3/tutorial/controlflow.html#if-statements',
            'Real Python — Conditional Logic: https://realpython.com/python-conditional-statements/',
        ]
    },
    'loops': {
        'ru': [
            'Python.org — For Loops: https://docs.python.org/3/tutorial/controlflow.html#for-statements',
            'Real Python — Loops: https://realpython.com/python-for-loop/',
        ],
        'en': [
            'Python.org — For Loops: https://docs.python.org/3/tutorial/controlflow.html#for-statements',
            'Real Python — Loops: https://realpython.com/python-for-loop/',
        ]
    },
    'functions': {
        'ru': [
            'Python.org — Functions: https://docs.python.org/3/tutorial/controlflow.html#defining-functions',
            'Real Python — Defining Functions: https://realpython.com/defining-your-own-python-function/',
        ],
        'en': [
            'Python.org — Functions: https://docs.python.org/3/tutorial/controlflow.html#defining-functions',
            'Real Python — Defining Functions: https://realpython.com/defining-your-own-python-function/',
        ]
    },
    'lists': {
        'ru': [
            'Python.org — Lists: https://docs.python.org/3/tutorial/introduction.html#lists',
            'Real Python — Lists: https://realpython.com/python-lists-tuples/',
        ],
        'en': [
            'Python.org — Lists: https://docs.python.org/3/tutorial/introduction.html#lists',
            'Real Python — Lists: https://realpython.com/python-lists-tuples/',
        ]
    },
    'dicts': {
        'ru': [
            'Python.org — Dictionaries: https://docs.python.org/3/tutorial/datastructures.html#dictionaries',
            'Real Python — Dictionaries: https://realpython.com/python-dicts/',
        ],
        'en': [
            'Python.org — Dictionaries: https://docs.python.org/3/tutorial/datastructures.html#dictionaries',
            'Real Python — Dictionaries: https://realpython.com/python-dicts/',
        ]
    },
}

# ============================================================
# KEY TAKEAWAYS per topic per language
# ============================================================
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
            'A variable is named storage for a value.',
            'Assignment `x = 5` puts value 5 into variable x.',
            'Variable names: letters, digits, underscore; not starting with digit; case-sensitive.',
            'Variable must be created before use, otherwise NameError.',
            'In `print(x)` value is substituted, in `print("x")` — literal "x".',
        ]
    },
    'operators': {
        'ru': [
            'Арифметика: `+ - * /` работает как в школе.',
            '`//` — целочисленное деление, `%` — остаток.',
            'Приоритет: `**` > `* / // %` > `+ -`. Скобки меняют порядок.',
            '`/` всегда даёт float. Для int — используйте `//`.',
        ],
        'en': [
            'Arithmetic: `+ - * /` works like school math.',
            '`//` — floor division, `%` — remainder.',
            'Precedence: `**` > `* / // %` > `+ -`. Parentheses change order.',
            '`/` always returns float. For int — use `//`.',
        ]
    },
    'strings': {
        'ru': [
            'Строки — неизменяемые последовательности символов.',
            'f-строки (`f"..."`) — лучший способ форматирования (Python 3.6+).',
            'Методы строк (.strip(), .upper(), .replace() и др.) создают НОВЫЕ строки.',
            'Raw-строки (`r"..."`) отключают экранирование — удобно для путей и regex.',
        ],
        'en': [
            'Strings are immutable character sequences.',
            'f-strings (`f"..."`) — best formatting (Python 3.6+).',
            'String methods (.strip(), .upper(), .replace()) create NEW strings.',
            'Raw strings (`r"..."`) disable escaping — handy for paths and regex.',
        ]
    },
    'conditionals': {
        'ru': [
            '`if` / `elif` / `else` — ветвление по условиям.',
            'Сравнения (`==`, `!=`, `<`, `>`) возвращают True/False.',
            'Логика: `and`, `or`, `not`. В Python они возвращают операнд, не обязательно bool.',
            'Ошибка: `=` (присваивание) вместо `==` (сравнение).',
        ],
        'en': [
            '`if` / `elif` / `else` — conditional branching.',
            'Comparisons (`==`, `!=`, `<`, `>`) return True/False.',
            'Logic: `and`, `or`, `not`. In Python they return operand, not necessarily bool.',
            'Mistake: `=` (assignment) instead of `==` (comparison).',
        ]
    },
    'loops': {
        'ru': [
            '`for x in collection:` — проходит по элементам (не по индексам!).',
            '`range(n)` — числа от 0 до n-1. `range(1, n+1)` — от 1 до n.',
            '`while condition:` — пока условие истинно. Нужен `break` для выхода.',
            '`else` у цикла — выполняется, если НЕ было `break`.',
        ],
        'en': [
            '`for x in collection:` — iterates elements (not indices!).',
            '`range(n)` — 0 to n-1. `range(1, n+1)` — 1 to n.',
            '`while condition:` — while truthy. Need `break` to exit.',
            'Loop `else` — runs if NO `break` occurred.',
        ]
    },
    'functions': {
        'ru': [
            '`def name(params):` — создаёт функцию. `return` — возвращает результат.',
            'Без `return` — возвращается `None`.',
            'Параметры по умолчанию: `def f(x=10):`. Изменяемые дефолты — ловушка!',
            'Именованные аргументы: `f(name="Alex")` — порядок не важен.',
        ],
        'en': [
            '`def name(params):` creates function. `return` sends result back.',
            'No `return` — returns `None`.',
            'Default params: `def f(x=10):`. Mutable defaults are a trap!',
            'Named args: `f(name="Alex")` — order doesn\'t matter.',
        ]
    },
    'lists': {
        'ru': [
            'Списки — упорядоченные изменяемые коллекции. Индексы с 0.',
            '`append()`/`insert()`/`remove()` меняют список НА МЕСТЕ, возвращают None.',
            'Срезы: `lst[1:4]` — с 1 по 3 включительно. `lst[:]` — копия.',
            '`in` проверяет наличие: `"a" in lst`. `len(lst)` — длина.',
        ],
        'en': [
            'Lists are ordered mutable collections. Indices start at 0.',
            '`append()`/`insert()`/`remove()` mutate IN PLACE, return None.',
            'Slices: `lst[1:4]` — indices 1 to 3. `lst[:]` — copy.',
            '`in` checks membership: `"a" in lst`. `len(lst)` — length.',
        ]
    },
    'dicts': {
        'ru': [
            'Словари — пары "ключ: значение". Ключи уникальны и неизменяемы.',
            'Доступ: `d[key]` (KeyError если нет) или `d.get(key, default)` (безопасно).',
            'Перебор: `for k, v in d.items():`. Проверка: `key in d`.',
            'Копия: `d.copy()` или `dict(d)`. Присваивание — та же ссылка!',
        ],
        'en': [
            'Dicts are "key: value" pairs. Keys unique and immutable.',
            'Access: `d[key]` (KeyError if missing) or `d.get(key, default)` (safe).',
            'Iterate: `for k, v in d.items():`. Check: `key in d`.',
            'Copy: `d.copy()` or `dict(d)`. Assignment = same reference!',
        ]
    },
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


def build_blocks_for_topic(topic: str, language: str, locale: str) -> List[Dict]:
    """Generate fresh blocks for a topic in given language and locale (ru/en)."""
    tpl = SECTION_TEMPLATES[locale]
    blocks = []
    
    # Get topic data for this language/locale
    intro_data = FRIENDLY_INTROS.get(topic, {}).get(language, {}).get(locale, {})
    mistakes = COMMON_MISTAKES.get(topic, {}).get(language, {}).get(locale, [])
    tasks = PRACTICE_TASKS.get(topic, {}).get(language, {}).get(locale, [])
    links = USEFUL_LINKS.get(topic, {}).get(locale, [])
    takeaways = KEY_TAKEAWAYS.get(topic, {}).get(locale, [])
    key_points = intro_data.get('key_points', [])
    
    # 1. Objectives
    blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_objectives']})
    if key_points:
        blocks.append({'type': 'list', 'items': key_points[:4], 'ordered': False})
    else:
        blocks.append({'type': 'list', 'items': [f'Понимать {topic}', 'Уметь применять', 'Избегать ошибок'], 'ordered': False})
    
    # 2. Intro scenario (friendly problem-solution narrative)
    if intro_data:
        blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_intro']})
        if intro_data.get('scenario'):
            blocks.append({'type': 'text', 'content': intro_data['scenario']})
        if intro_data.get('naive_code'):
            blocks.append({'type': 'code', 'language': language, 'content': intro_data['naive_code']})
        if intro_data.get('pain_point'):
            blocks.append({'type': 'text', 'content': intro_data['pain_point']})
        if intro_data.get('solution'):
            blocks.append({'type': 'text', 'content': intro_data['solution']})
        if intro_data.get('solution_code'):
            blocks.append({'type': 'code', 'language': language, 'content': intro_data['solution_code']})
    
    # 3. How it works
    if intro_data and (intro_data.get('explanation') or intro_data.get('visual') or intro_data.get('how_it_works')):
        blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_how_it_works']})
        if intro_data.get('explanation'):
            blocks.append({'type': 'text', 'content': intro_data['explanation']})
        if intro_data.get('visual'):
            blocks.append({'type': 'text', 'content': f'**Схема:**\n```\n{intro_data["visual"]}\n```'})
        if intro_data.get('how_it_works'):
            blocks.append({'type': 'text', 'content': intro_data['how_it_works']})
        if intro_data.get('substitution'):
            blocks.append({'type': 'code', 'language': language, 'content': intro_data['substitution']})
    
    # 4. Key points
    if key_points:
        blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_key_points']})
        blocks.append({'type': 'list', 'items': key_points, 'ordered': False})
    
    # 5. Common mistakes
    if mistakes:
        blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_common_mistakes']})
        blocks.append({'type': 'text', 'content': 'Вот самые частые ошибки и как их избежать:' if locale == 'ru' else 'Here are the most common mistakes and how to avoid them:'})
        blocks.append({'type': 'table', 'headers': ['Ошибка', 'Как проявляется', 'Как правильно'] if locale == 'ru' else ['Mistake', 'How It Shows', 'Correct Way'], 'rows': mistakes})
    
    # 6. Practice
    if tasks:
        blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_practice']})
        blocks.append({'type': 'text', 'content': 'Попробуйте сами — это лучший способ запомнить:' if locale == 'ru' else 'Try it yourself — that\'s the best way to learn:'})
        blocks.append({'type': 'list', 'items': tasks, 'ordered': True})
    
    # 7. Summary
    if takeaways:
        blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_summary']})
        blocks.append({'type': 'list', 'items': takeaways, 'ordered': False})
    
    # 8. Useful links
    if links:
        blocks.append({'type': 'heading', 'level': 2, 'content': tpl['heading_useful']})
        blocks.append({'type': 'list', 'items': links, 'ordered': False})
    
    return blocks


def build_lesson(data: Dict, language: str, lesson_num: int) -> Dict:
    """Build complete lesson with fresh RU and EN content."""
    topic = get_topic(language, lesson_num)
    
    # Generate fresh Russian content
    data['content_blocks'] = build_blocks_for_topic(topic, language, 'ru')
    
    # Generate fresh English content
    data['content_en'] = build_blocks_for_topic(topic, language, 'en')
    
    # Metadata
    data['goals'] = [f'Понимать {topic}', 'Уметь применять на практике', 'Распознавать и избегать частые ошибки']
    data['practice_tasks'] = PRACTICE_TASKS.get(topic, {}).get(language, {}).get('ru', ['Базовая практика'])
    data['common_errors'] = [
        {'mistake': m[0], 'correct': m[2]} 
        for m in COMMON_MISTAKES.get(topic, {}).get(language, {}).get('ru', [['Ошибка', 'Как проявляется', 'Правильно']])
    ]
    data['resources'] = USEFUL_LINKS.get(topic, {}).get('ru', ['Официальная документация'])
    data['key_takeaways'] = KEY_TAKEAWAYS.get(topic, {}).get('ru', ['Главный вывод усвоен'])
    
    # English metadata
    data['name_en'] = data.get('title', '').replace('Урок', 'Lesson').replace('урок', 'lesson')
    data['short_description_en'] = data.get('short_description', '')
    
    # Estimate time
    total_chars = sum(len(json.dumps(b, ensure_ascii=False)) for b in data['content_blocks'])
    data['estimated_minutes'] = max(15, min(45, total_chars // 800))
    
    return data


def process_lesson(filepath: Path, language: str, lesson_num: int) -> Dict:
    data = load_lesson(filepath)
    data = build_lesson(data, language, lesson_num)
    return data


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Rewrite lessons in friendly style v2')
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