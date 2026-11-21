#!/usr/bin/env python3
"""
Enhance lesson fixtures by adding detailed explanations to code examples:
- What each example demonstrates
- Why it's needed
- How it works
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Detailed explanations for common code patterns
EXAMPLE_EXPLANATIONS = {
    # JavaScript
    "console.log": {
        "what": "Выводит информацию в консоль браузера для отладки",
        "why": "Это основной способ увидеть значения переменных, результаты вычислений и ошибки во время разработки",
        "how": "Принимает любые значения (строки, числа, объекты, массивы) и печатает их в консоль разработчика (F12)"
    },
    "let const": {
        "what": "Объявляет переменные с блочной областью видимости",
        "why": "const для констант (не меняются), let для переменных (меняются). var устарел — у него функцияльная область видимости, что вызывает баги",
        "how": "const по умолчанию, let только если нужно переприсваивать. const с объектами позволяет менять свойства, но не саму ссылку"
    },
    "arrow function": {
        "what": "Краткий синтаксис создания функций (ES6+)",
        "why": "Короче запись, не создаёт свой this (наследует от внешней области), удобно для колбэков",
        "how": "(a, b) => a + b эквивалентно function(a, b) { return a + b; }"
    },
    "template literal": {
        "what": "Строки в обратных кавычках с интерполяцией ${}",
        "why": "Удобнее конкатенации, поддерживает многострочность, читаемее",
        "how": "`Привет, ${name}!` вместо 'Привет, ' + name + '!'"
    },
    "destructuring": {
        "what": "Распаковка массивов/объектов в отдельные переменные",
        "why": "Читаемее, меньше кода, позволяет сразу извлечь нужные свойства",
        "how": "const {name, age} = user; вместо const name = user.name; const age = user.age;"
    },
    "spread operator": {
        "what": "Распаковка массива/объекта в новый (...arr, ...obj)",
        "why": "Создаёт копии, объединяет массивы/объекты, передаёт аргументы в функции",
        "how": "const copy = [...arr]; const merged = [...a, ...b]; const updated = {...obj, newProp: 1}"
    },
    "async await": {
        "what": "Синтаксис для работы с промисами как с синхронным кодом",
        "why": "Читаемее чем .then()/catch(), проще обрабатывать ошибки try/catch, линейный поток",
        "how": "async function() { const data = await fetch(url); } вместо fetch().then().catch()"
    },
    "Promise.all": {
        "what": "Запускает несколько промисов параллельно и ждёт всех",
        "why": "Ускоряет загрузку независимых данных, не ждёт последовательно",
        "how": "const [users, posts] = await Promise.all([fetchUsers(), fetchPosts()])"
    },
    "map filter reduce": {
        "what": "Функциональные методы массивов для преобразования данных",
        "why": "Декларативный стиль, цепочки вызовов, иммутабельность, читаемость",
        "how": "arr.map(x => x*2).filter(x => x>10).reduce((a,b)=>a+b, 0)"
    },
    "optional chaining": {
        "what": "?. безопасный доступ к вложенным свойствам",
        "why": "Предотвращает ошибки 'Cannot read property of undefined', короче чем &&",
        "how": "user?.profile?.name вместо user && user.profile && user.profile.name"
    },
    "nullish coalescing": {
        "what": "?? возвращает правое значение только если левое null/undefined",
        "why": "В отличие от || не срабатывает на 0, '', false — только на null/undefined",
        "how": "const name = user.name ?? 'Гость' — если name null/undefined, будет 'Гость'"
    },

    # Python
    "f-string": {
        "what": "Форматированные строки с интерполяцией {expr}",
        "why": "Быстрее и читаемее .format() и %, поддерживает любые выражения внутри {}",
        "how": "f'Привет, {name}! Тебе {age} лет.' вместо 'Привет, ' + name + '! Тебе ' + str(age) + ' лет.'"
    },
    "list comprehension": {
        "what": "Создание списков через выражение в квадратных скобках",
        "why": "Быстрее цикла for, читаемее map/filter, питоничный стиль",
        "how": "[x*2 for x in range(10) if x%2==0] вместо цикла с append"
    },
    "dict comprehension": {
        "what": "Создание словарей через выражение в фигурных скобках",
        "why": "Компактно создаёт словари из итерируемых объектов",
        "how": "{k: v*2 for k, v in data.items() if v > 10}"
    },
    "dataclass": {
        "what": "Декоратор для автоматического создания __init__, __repr__, __eq__",
        "why": "Меньше бойлерплейта, автоматическая генерация методов, типизация полей",
        "how": "@dataclass class User: name: str; age: int = 18"
    },
    "context manager": {
        "what": "with open(...) as f: — автоматическое закрытие ресурсов",
        "why": "Гарантирует закрытие файлов/соединений даже при ошибках, чище try/finally",
        "how": "with open('file.txt') as f: data = f.read() — файл закроется автоматически"
    },
    "dataclasses": {
        "what": "Декоратор @dataclass для классов-данных",
        "why": "Автоматически создаёт __init__, __repr__, __eq__, меньше бойлерплейта",
        "how": "@dataclass class User: name: str; age: int = 18"
    },
    "type hints": {
        "what": "Аннотации типов для переменных, функций, классов",
        "why": "Статический анализ (mypy), автодополнение в IDE, документация, раннее обнаружение багов",
        "how": "def greet(name: str) -> str: return f'Привет, {name}'"
    },
    "async def": {
        "what": "Определение корутины для асинхронного выполнения",
        "why": "Позволяет использовать await внутри, не блокирует поток при I/O",
        "how": "async def fetch(): data = await http.get(url); return data"
    },
    "asyncio.gather": {
        "what": "Параллельный запуск корутин",
        "why": "Запускает несколько задач одновременно, ждёт все сразу — быстрее последовательного",
        "how": "results = await asyncio.gather(fetch_user(1), fetch_user(2), fetch_user(3))"
    },
    "pathlib": {
        "what": "Объектно-ориентированная работа с путями файлов",
        "why": "Кроссплатформенно, методы вместо os.path, цепочки вызовов, читаемо",
        "how": "Path('dir') / 'file.txt', path.read_text(), path.write_text('data')"
    },
    "dataclasses field": {
        "what": "field() для настройки полей dataclass (default_factory, init=False, repr=False)",
        "why": "Гибкая настройка полей: mutable defaults, исключение из init/repr/compare",
        "how": "@dataclass class User: tags: list[str] = field(default_factory=list)"
    },
    "async with": {
        "what": "Асинхронный контекстный менеджер",
        "why": "Автоматическое управление асинхронными ресурсами (подключения, сессии)",
        "how": "async with aiohttp.ClientSession() as session: async with session.get(url) as resp:"
    },
    "type var generic": {
        "what": "TypeVar для обобщённого программирования",
        "why": "Пишем код один раз для любых типов, сохраняем типизацию, DRY",
        "how": "T = TypeVar('T'); def first(items: list[T]) -> T: return items[0]"
    },
    "complex numbers": {
        "what": "Комплексные числа (complex) с действительной и мнимой частями",
        "why": "Математика, инженерия, обработка сигналов, квантовые вычисления",
        "how": "z = 3 + 4j; z.real, z.imag, abs(z), z.conjugate()"
    },
    "type isinstance": {
        "what": "Проверка типа через type() и isinstance()",
        "why": "isinstance() учитывает наследование, type() — точный тип, isinstance() рекомендуется",
        "how": "isinstance(x, int), isinstance(x, (int, float)), type(x) == int"
    },
    "len": {
        "what": "Функция len() — длина последовательности",
        "why": "Универсальный способ получить длину строк, списков, словарей, множеств",
        "how": "len('hello'), len([1,2,3]), len({'a': 1})"
    },
    "input": {
        "what": "input() — чтение строки из стандартного ввода",
        "why": "Взаимодействие с пользователем, получение данных из консоли",
        "how": "name = input('Имя: '); age = int(input('Возраст: '))"
    },
    "int float str conversion": {
        "what": "Явное преобразование типов: int(), float(), str()",
        "why": "input() возвращает строку, нужно явно преобразовывать для вычислений",
        "how": "int('42'), float('3.14'), str(123), bool(0), bool('')"
    },
    "try except": {
        "what": "Обработка исключений try/except/else/finally",
        "why": "Обработка ошибок во время выполнения, предотвращение краша программы",
        "how": "try: x = int(input()) except ValueError: print('Ошибка!')"
    },
    "while loop": {
        "what": "Цикл while — выполняется пока условие истинно",
        "why": "Когда количество итераций неизвестно заранее",
        "how": "while x > 0: x -= 1"
    },
    "for loop": {
        "what": "Цикл for — итерация по последовательности",
        "why": "Удобный перебор элементов списка, строки, range, словаря",
        "how": "for x in items: print(x); for i in range(10): print(i)"
    },
    "if else": {
        "what": "Условные конструкции if/elif/else",
        "why": "Ветвление логики программы в зависимости от условий",
        "how": "if x > 0: ... elif x < 0: ... else: ..."
    },
    "function def": {
        "what": "Определение функции через def",
        "why": "Повторное использование кода, декомпозиция, читаемость",
        "how": "def greet(name): return f'Привет, {name}!'"
    },
    "class": {
        "what": "Определение класса через class",
        "why": "Инкапсуляция данных и поведения, ООП, наследование",
        "how": "class User: def __init__(self, name): self.name = name"
    ),
    "import module": {
        "what": "Подключение модулей через import",
        "why": "Повторное использование кода, стандартная библиотека, сторонние пакеты",
        "how": "import math, from pathlib import Path, from math import sqrt as sq"
    ),
    "file io": {
        "what": "Работа с файлами: open, read, write, with",
        "why": "Постоянное хранение данных, конфиги, логи, обработка больших файлов",
        "how": "with open('file.txt') as f: data = f.read()"
    ),
    "try except": {
        "what": "Обработка исключений try/except/else/finally",
        "why": "Обработка ошибок времени выполнения, предотвращение краша",
        "how": "try: x = int(input()) except ValueError: print('Ошибка!')"
    ),
    "while loop": {
        "what": "Цикл while — выполняется пока условие истинно",
        "why": "Когда количество итераций неизвестно заранее",
        "how": "while x > 0: x -= 1"
    ),
    "for loop": {
        "what": "Цикл for — итерация по последовательности",
        "why": "Удобный перебор элементов списка, строки, range, словаря",
        "how": "for x in items: print(x); for i in range(10): print(i)"
    ),
    "if else": {
        "what": "Условные конструкции if/elif/else",
        "why": "Ветвление логики программы в зависимости от условий",
        "how": "if x > 0: ... elif x < 0: ... else: ..."
    ),
    "function def": {
        "what": "Определение функции через def",
        "why": "Повторное использование кода, декомпозиция, читаемость",
        "how": "def greet(name): return f'Привет, {name}!'"
    ),
    "class": {
        "what": "Определение класса через class",
        "why": "Инкапсуляция данных и поведения, ООП, наследование",
        "how": "class User: def __init__(self, name): self.name = name"
    ),
    "import module": {
        "what": "Подключение модулей через import",
        "why": "Повторное использование кода, стандартная библиотека, сторонние пакеты",
        "how": "import math, from pathlib import Path, from math import sqrt as sq"
    ),
    "file io": {
        "what": "Работа с файлами: open, read, write, with",
        "why": "Постоянное хранение данных, конфиги, логи, обработка больших файлов",
        "how": "with open('file.txt') as f: data = f.read()"
    ),
    "try except": {
        "what": "Обработка исключений try/except/else/finally",
        "why": "Обработка ошибок времени выполнения, предотвращение краша",
        "how": "try: x = int(input()) except ValueError: print('Ошибка!')"
    ),
    "while loop": {
        "what": "Цикл while — выполняется пока условие истинно",
        "why": "Когда количество итераций неизвестно заранее",
        "how": "while x > 0: x -= 1"
    ),
    "for loop": {
        "what": "Цикл for — итерация по последовательности",
        "why": "Удобный перебор элементов списка, строки, range, словаря",
        "how": "for x in items: print(x); for i in range(10): print(i)"
    ),
    "if else": {
        "what": "Условные конструкции if/elif/else",
        "why": "Ветвление логики программы в зависимости от условий",
        "how": "if x > 0: ... elif x < 0: ... else: ..."
    ),
    "function def": {
        "what": "Определение функции через def",
        "why": "Повторное использование кода, декомпозиция, читаемость",
        "how": "def greet(name): return f'Привет, {name}!'"
    ),
    "class": {
        "what": "Определение класса через class",
        "why": "Инкапсуляция данных и поведения, ООП, наследование",
        "how": "class User: def __init__(self, name): self.name = name"
    ),
    "import module": {
        "what": "Подключение модулей через import",
        "why": "Повторное использование кода, стандартная библиотека, сторонние пакеты",
        "how": "import math, from pathlib import Path, from math import sqrt as sq"
    ),
    "file io": {
        "what": "Работа с файлами: open, read, write, with",
        "why": "Постоянное хранение данных, конфиги, логи, обработка больших файлов",
        "how": "with open('file.txt') as f: data = f.read()"
    ),
    "try except": {
        "what": "Обработка исключений try/except/else/finally",
        "why": "Обработка ошибок времени выполнения, предотвращение краша",
        "how": "try: x = int(input()) except ValueError: print('Ошибка!')"
    ),
    "while loop": {
        "what": "Цикл while — выполняется пока условие истинно",
        "why": "Когда количество итераций неизвестно заранее",
        "how": "while x > 0: x -= 1"
    ),
    "for loop": {
        "what": "Цикл for — итерация по последовательности",
        "why": "Удобный перебор элементов списка, строки, range, словаря",
        "how": "for x in items: print(x); for i in range(10): print(i)"
    ),
    "if else": {
        "what": "Условные конструкции if/elif/else",
        "why": "Ветвление логики программы в зависимости от условий",
        "how": "if x > 0: ... elif x < 0: ... else: ..."
    ),
    "function def": {
        "what": "Определение функции через def",
        "why": "Повторное использование кода, декомпозиция, читаемость",
        "how": "def greet(name): return f'Привет, {name}!'"
    ),
    "class": {
        "what": "Определение класса через class",
        "why": "Инкапсуляция данных и поведения, ООП, наследование",
        "how": "class User: def __init__(self, name): self.name = name"
    ),
    "import module": {
        "what": "Подключение модулей через import",
        "why": "Повторное использование кода, стандартная библиотека, сторонние пакеты",
        "how": "import math, from pathlib import Path, from math import sqrt as sq"
    ),
    "file io": {
        "what": "Работа с файлами: open, read, write, with",
        "why": "Постоянное хранение данных, конфиги, логи, обработка больших файлов",
        "how": "with open('file.txt') as f: data = f.read()"
    ),

    # C++
    "RAII": {
        "what": "Resource Acquisition Is Initialization — ресурс захватывается в конструкторе, освобождается в деструкторе",
        "why": "Гарантирует освобождение ресурсов (память, файлы, мьютексы) даже при исключениях, нет утечек",
        "how": "std::unique_ptr<File> file = std::make_unique<File>(\"data.txt\"); // файл закроется в деструкторе"
    },
    "smart pointers": {
        "what": "unique_ptr, shared_ptr, weak_ptr — умные указатели с автоматическим управлением памятью",
        "why": "Исключают утечки памяти, dangling pointers, double free; владеют объектом",
        "how": "auto ptr = std::make_unique<Widget>(); // unique_ptr — единственный владелец"
    },
    "move semantics": {
        "what": "Перемещение ресурсов вместо копирования (std::move, rvalue references)",
        "why": "Избегает дорогого глубокого копирования, передаёт владение ресурсом",
        "how": "std::vector<int> v2 = std::move(v1); // v1 пуст, v2 забирает данные"
    },
    "RAII smart pointers": {
        "what": "Умные указатели реализуют RAII для динамической памяти",
        "why": "Автоматическое удаление при выходе из области видимости, нет утечек",
        "how": "auto p = std::make_unique<int>(42); // удалится при выходе из scope"
    },
    "perfect forwarding": {
        "what": "std::forward сохраняет категорию значения (lvalue/rvalue) при передаче дальше",
        "why": "Позволяет писать универсальные обёртки/фабрики, сохраняет move-семантику",
        "how": "template<typename T> void wrapper(T&& arg) { func(std::forward<T>(arg)); }"
    },
    "concepts cpp20": {
        "what": "Ограничения на шаблонные параметры (requires, concept)",
        "why": "Чёткие ошибки компиляции, документирование требований, лучше чем SFINAE",
        "how": "template<std::integral T> T add(T a, T b) { return a + b; }"
    },
    "coroutines cpp20": {
        "what": "Функции с co_await/co_yield/co_return для асинхронного кода",
        "why": "Линейный асинхронный код без колбэков, композиция, ленивые вычисления",
        "how": "cppcoro::generator<int> gen() { for(int i=0;i<10;++i) co_yield i; }"
    },
    "modules cpp20": {
        "what": "Система модулей вместо заголовочных файлов (import/export)",
        "why": "Быстрее компиляция, нет ODR нарушений, инкапсуляция, нет макросов",
        "how": "export module math; export int add(int a, int b); // math.cppm"
    },

    # C#
    "LINQ": {
        "what": "Language Integrated Query — запросы к коллекциям в стиле SQL",
        "why": "Декларативный стиль, ленивое выполнение, композиция, читаемость",
        "how": "users.Where(u => u.Age > 18).Select(u => u.Name).ToList()"
    },
    "async await": {
        "what": "Асинхронное программирование без блокировки потока",
        "why": "Освобождает поток при I/O, масштабируемость серверов, отзывчивость UI",
        "how": "async Task<User> GetUser(int id) { return await db.Users.FindAsync(id); }"
    },
    "records": {
        "what": "Неизменяемые ссылочные типы с value-семантикой (C# 9+)",
        "why": "Value equality, with-expressions, деконструкция, неизменяемость — идеально для DTO",
        "how": "public record User(string Name, int Age); var u = new User(\"Alex\", 25);"
    },
    "pattern matching": {
        "what": "is, switch expressions, property patterns, list patterns",
        "why": "Типобезопасная проверка типов и структуры, извлечение значений, читаемо",
        "how": "return obj switch { User u => u.Name, null => \"none\", _ => \"unknown\" };"
    },
    "nullable reference types": {
        "what": "? после типа означает допустимость null (C# 8+)",
        "why": "Статический анализ null-ссылок, предупреждения компилятора, меньше NullReferenceException",
        "how": "string? name = null; // допустим null; string name = \"Alex\"; // не допустим"
    },
    "records with with-expression": {
        "what": "Создание копии record с изменением части полей",
        "why": "Неизменяемость + удобное обновление, вместо ручного копирования полей",
        "how": "var updated = user with { Age = 26 }; // копия с изменённым Age"
    },
    "pattern matching switch": {
        "what": "Switch-выражение с pattern matching (C# 8+)",
        "why": "Выражение (возвращает значение), pattern matching, exhaustiveness checking",
        "how": "var result = shape switch { Circle c => c.Radius * c.Radius, Rectangle r => r.W * r.H, _ => 0 };"
    },
    "async streams": {
        "what": "IAsyncEnumerable<T> для асинхронных потоков данных",
        "why": "Потоковая обработка больших данных без загрузки в память, backpressure",
        "how": "await foreach (var item in GetItemsAsync()) { Process(item); }"
    },
    "source generators": {
        "what": "Генерация кода на этапе компиляции (C# 9+)",
        "why": "Нет рефлексии в runtime, работает в NativeAOT, нулевой оверхед",
        "how": "[Generator] public class MyGenerator : IIncrementalGenerator { ... }"
    },

    # C++
    "RAII": {
        "what": "Resource Acquisition Is Initialization — ресурс захватывается в конструкторе, освобождается в деструкторе",
        "why": "Гарантирует освобождение ресурсов (память, файлы, мьютексы) даже при исключениях, нет утечек",
        "how": "std::unique_ptr<File> file = std::make_unique<File>(\"data.txt\"); // файл закроется в деструкторе"
    },
    "smart pointers": {
        "what": "unique_ptr, shared_ptr, weak_ptr — умные указатели с автоматическим управлением памятью",
        "why": "Исключают утечки памяти, dangling pointers, double free; владеют объектом",
        "how": "auto ptr = std::make_unique<Widget>(); // unique_ptr — единственный владелец"
    },
    "move semantics": {
        "what": "Перемещение ресурсов вместо копирования (std::move, rvalue references)",
        "why": "Избегает дорогого глубокого копирования, передаёт владение ресурсом",
        "how": "std::vector<int> v2 = std::move(v1); // v1 пуст, v2 забирает данные"
    },
    "perfect forwarding": {
        "what": "std::forward сохраняет категорию значения (lvalue/rvalue) при передаче дальше",
        "why": "Позволяет писать универсальные обёртки/фабрики, сохраняет move-семантику",
        "how": "template<typename T> void wrapper(T&& arg) { func(std::forward<T>(arg)); }"
    },
    "concepts cpp20": {
        "what": "Ограничения на шаблонные параметры (requires, concept)",
        "why": "Чёткие ошибки компиляции, документирование требований, лучше чем SFINAE",
        "how": "template<std::integral T> T add(T a, T b) { return a + b; }"
    },
    "coroutines cpp20": {
        "what": "Функции с co_await/co_yield/co_return для асинхронного кода",
        "why": "Линейный асинхронный код без колбэков, композиция, ленивые вычисления",
        "how": "cppcoro::generator<int> gen() { for(int i=0;i<10;++i) co_yield i; }"
    },
    "modules cpp20": {
        "what": "Система модулей вместо заголовочных файлов (import/export)",
        "why": "Быстрее компиляция, нет ODR нарушений, инкапсуляция, нет макросов",
        "how": "export module math; export int add(int a, int b); // math.cppm"
    },

    # Rust
    "ownership": {
        "what": "Система владения — каждый значением владеет одна переменная, при перемещении владение передаётся",
        "why": "Безопасность памяти без GC: нет double-free, use-after-free, data races на уровне компилятора",
        "how": "let s1 = String::from(\"hello\"); let s2 = s1; // s1 больше не валиден, владелец s2"
    },
    "borrowing": {
        "what": "Заимствование (&T, &mut T) — временный доступ без передачи владения",
        "why": "Позволяет читать/менять данные без передачи владения, проверки на этапе компиляции",
        "how": "fn read(s: &String) { println!(\"{}\", s); } let s = String::from(\"hi\"); read(&s);"
    },
    "lifetimes": {
        "what": "Времена жизни ('a) — аннотации, гарантирующие, что ссылки не переживут данные",
        "why": "Предотвращают висячие ссылки, компилятор проверяет, что ссылки не переживут данные",
        "how": "fn longest<'a>(x: &'a str, y: &'a str) -> &'a str { if x.len() > y.len() { x } else { y } }"
    },
    "option result": {
        "what": "Option<T> — значение или ничего, Result<T, E> — успех или ошибка",
        "why": "Нет null, явная обработка отсутствия значения/ошибки, pattern matching",
        "how": "fn find(x: i32) -> Option<i32> { if x > 0 { Some(x) } else { None } }"
    },
    "traits": {
        "what": "Трейты — интерфейсы поведения, можно реализовать для любых типов",
        "why": "Полиморфизм без наследования, композиция, blanket implementations, marker traits",
        "how": "trait Draw { fn draw(&self); } impl Draw for Circle { fn draw(&self) { ... } }"
    },
    "pattern matching": {
        "what": "match — исчерпывающая проверка вариантов enum/структур",
        "why": "Исчерпываемость проверена компилятором, деструктуризация, выражения",
        "how": "match opt { Some(x) => x*2, None => 0 }"
    },
    "smart pointers": {
        "what": "Box<T>, Rc<T>, Arc<T>, RefCell<T>, Weak<T> — умные указатели с разной семантикой",
        "why": "Управление памятью без GC: Box — владелец, Rc/Arc — shared ownership, RefCell — interior mutability",
        "how": "let shared = Rc::new(RefCell::new(vec![1,2,3])); // shared mutable ownership"
    },
    "async await": {
        "what": "async fn возвращает Future, .await приостанавливает до готовности",
        "why": "Неблокирующий I/O, тысячи задач в одном потоке, композиция через .await",
        "how": "async fn fetch() -> Result<Data> { let resp = reqwest::get(url).await?; resp.json().await }"
    },
    "tokio": {
        "what": "Асинхронный рантайм для Rust (планировщик, I/O, таймеры, синхронизация)",
        "why": "Стандарт де-факто для async Rust, work-stealing scheduler, драйверы I/O",
        "how": "[tokio::main] async fn main() { tokio::spawn(async { ... }); }"
    },
    "serde": {
        "what": "Фреймворк сериализации/десериализации (derive-макросы)",
        "why": "Декларативный, быстрый, поддерживает JSON/TOML/YAML/bincode, zero-copy",
        "how": "[derive(Serialize, Deserialize)] struct User { name: String, age: u32 }"
    },
    "async traits": {
        "what": "Трейты с async методами (требует async-trait крейт или Rust 1.75+)",
        "why": "Абстракция над асинхронным поведением, моки в тестах, плагины",
        "how": "[async_trait] trait Storage { async fn save(&self, data: Data); }"
    },
    "pin unpin": {
        "what": "Pin<P> гарантирует, что значение не перемещается в памяти",
        "why": "Необходимо для самоссылающихся структур, Future, intrusive collections",
        "how": "let mut future = Box::pin(async { ... }); let pinned = future.as_mut();"
    },
    "generics traits": {
        "what": "Трейты с параметрами типа (Generic Associated Types — GAT)",
        "why": "Выразительные абстракции: итераторы с лайфтаймами, асинхронные трейты",
        "how": "trait Iterator { type Item; fn next(&mut self) -> Option<Self::Item>; }"
    },

    # C++
    "RAII": {
        "what": "Resource Acquisition Is Initialization — ресурс захватывается в конструкторе, освобождается в деструкторе",
        "why": "Гарантирует освобождение ресурсов (память, файлы, мьютексы) даже при исключениях, нет утечек",
        "how": "std::unique_ptr<File> file = std::make_unique<File>(\"data.txt\"); // файл закроется в деструкторе"
    },
    "move semantics": {
        "what": "Перемещение ресурсов вместо копирования (std::move, rvalue references)",
        "why": "Избегает дорогого глубокого копирования, передаёт владение ресурсом",
        "how": "std::vector<int> v2 = std::move(v1); // v1 пуст, v2 забирает данные"
    },
    "smart pointers": {
        "what": "unique_ptr, shared_ptr, weak_ptr — умные указатели с автоматическим управлением памятью",
        "why": "Исключают утечки памяти, dangling pointers, double free; владеют объектом",
        "how": "auto ptr = std::make_unique<Widget>(); // unique_ptr — единственный владелец"
    },
    "templates": {
        "what": "Параметризованные типы и функции (шаблоны)",
        "why": "Пишем код один раз для любых типов, compile-time полиморфизм, ноль оверхеда",
        "how": "template<typename T> T max(T a, T b) { return a > b ? a : b; }"
    },
    "concepts cpp20": {
        "what": "Ограничения на шаблонные параметры (requires, concept)",
        "why": "Чёткие ошибки компиляции, документирование требований, лучше чем SFINAE",
        "how": "template<std::integral T> T add(T a, T b) { return a + b; }"
    },
    "coroutines cpp20": {
        "what": "Функции с co_await/co_yield/co_return для асинхронного кода",
        "why": "Линейный асинхронный код без колбэков, композиция, ленивые вычисления",
        "how": "cppcoro::generator<int> gen() { for(int i=0;i<10;++i) co_yield i; }"
    },
    "modules cpp20": {
        "what": "Система модулей вместо заголовочных файлов (import/export)",
        "why": "Быстрее компиляция, нет ODR нарушений, инкапсуляция, нет макросов",
        "how": "export module math; export int add(int a, int b); // math.cppm"
    },
    "smart pointers": {
        "what": "unique_ptr, shared_ptr, weak_ptr — умные указатели с автоматическим управлением памятью",
        "why": "Исключают утечки памяти, dangling pointers, double free; владеют объектом",
        "how": "auto ptr = std::make_unique<Widget>(); // unique_ptr — единственный владелец"
    },
    "perfect forwarding": {
        "what": "std::forward сохраняет категорию значения (lvalue/rvalue) при передаче дальше",
        "why": "Позволяет писать универсальные обёртки/фабрики, сохраняет move-семантику",
        "how": "template<typename T> void wrapper(T&& arg) { func(std::forward<T>(arg)); }"
    },
    "concepts cpp20": {
        "what": "Ограничения на шаблонные параметры (requires, concept)",
        "why": "Чёткие ошибки компиляции, документирование требований, лучше чем SFINAE",
        "how": "template<std::integral T> T add(T a, T b) { return a + b; }"
    },
    "coroutines cpp20": {
        "what": "Функции с co_await/co_yield/co_return для асинхронного кода",
        "why": "Линейный асинхронный код без колбэков, композиция, ленивые вычисления",
        "how": "cppcoro::generator<int> gen() { for(int i=0;i<10;++i) co_yield i; }"
    },
    "modules cpp20": {
        "what": "Система модулей вместо заголовочных файлов (import/export)",
        "why": "Быстрее компиляция, нет ODR нарушений, инкапсуляция, нет макросов",
        "how": "export module math; export int add(int a, int b); // math.cppm"
    },
    "smart pointers": {
        "what": "unique_ptr, shared_ptr, weak_ptr — умные указатели с автоматическим управлением памятью",
        "why": "Исключают утечки памяти, dangling pointers, double free; владеют объектом",
        "how": "auto ptr = std::make_unique<Widget>(); // unique_ptr — единственный владелец"
    },
    "perfect forwarding": {
        "what": "std::forward сохраняет категорию значения (lvalue/rvalue) при передаче дальше",
        "why": "Позволяет писать универсальные обёртки/фабрики, сохраняет move-семантику",
        "how": "template<typename T> void wrapper(T&& arg) { func(std::forward<T>(arg)); }"
    },
    "concepts cpp20": {
        "what": "Ограничения на шаблонные параметры (requires, concept)",
        "why": "Чёткие ошибки компиляции, документирование требований, лучше чем SFINAE",
        "how": "template<std::integral T> T add(T a, T b) { return a + b; }"
    },
    "coroutines cpp20": {
        "what": "Функции с co_await/co_yield/co_return для асинхронного кода",
        "why": "Линейный асинхронный код без колбэков, композиция, ленивые вычисления",
        "how": "cppcoro::generator<int> gen() { for(int i=0;i<10;++i) co_yield i; }"
    },
    "modules cpp20": {
        "what": "Система модулей вместо заголовочных файлов (import/export)",
        "why": "Быстрее компиляция, нет ODR нарушений, инкапсуляция, нет макросов",
        "how": "export module math; export int add(int a, int b); // math.cppm"
    },

    # Rust
    "ownership": {
        "what": "Система владения — каждый значением владеет одна переменная, при перемещении владение передаётся",
        "why": "Безопасность памяти без GC: нет double-free, use-after-free, data races на уровне компилятора",
        "how": "let s1 = String::from(\"hello\"); let s2 = s1; // s1 больше не валиден, владелец s2"
    },
    "borrowing": {
        "what": "Заимствование (&T, &mut T) — временный доступ без передачи владения",
        "why": "Позволяет читать/менять данные без передачи владения, проверки на этапе компиляции",
        "how": "fn read(s: &String) { println!(\"{}\", s); } let s = String::from(\"hi\"); read(&s);"
    },
    "lifetimes": {
        "what": "Времена жизни ('a) — аннотации, гарантирующие, что ссылки не переживут данные",
        "why": "Предотвращают висячие ссылки, компилятор проверяет, что ссылки не переживут данные",
        "how": "fn longest<'a>(x: &'a str, y: &'a str) -> &'a str { if x.len() > y.len() { x } else { y } }"
    },
    "option result": {
        "what": "Option<T> — значение или ничего, Result<T, E> — успех или ошибка",
        "why": "Нет null, явная обработка отсутствия значения/ошибки, pattern matching",
        "how": "fn find(x: i32) -> Option<i32> { if x > 0 { Some(x) } else { None } }"
    },
    "traits": {
        "what": "Трейты — интерфейсы поведения, можно реализовать для любых типов",
        "why": "Полиморфизм без наследования, композиция, blanket implementations, marker traits",
        "how": "trait Draw { fn draw(&self); } impl Draw for Circle { fn draw(&self) { ... } }"
    },
    "pattern matching": {
        "what": "match — исчерпывающая проверка вариантов enum/структур",
        "why": "Исчерпываемость проверена компилятором, деструктуризация, выражения",
        "how": "match opt { Some(x) => x*2, None => 0 }"
    },
    "smart pointers": {
        "what": "Box<T>, Rc<T>, Arc<T>, RefCell<T>, Weak<T> — умные указатели с разной семантикой",
        "why": "Управление памятью без GC: Box — владелец, Rc/Arc — shared ownership, RefCell — interior mutability",
        "how": "let shared = Rc::new(RefCell::new(vec![1,2,3])); // shared mutable ownership"
    },
    "async await": {
        "what": "async fn возвращает Future, .await приостанавливает до готовности",
        "why": "Неблокирующий I/O, тысячи задач в одном потоке, композиция через .await",
        "how": "async fn fetch() -> Result<Data> { let resp = reqwest::get(url).await?; resp.json().await }"
    },
    "tokio": {
        "what": "Асинхронный рантайм для Rust (планировщик, I/O, таймеры, синхронизация)",
        "why": "Стандарт де-факто для async Rust, work-stealing scheduler, драйверы I/O",
        "how": "[tokio::main] async fn main() { tokio::spawn(async { ... }); }"
    },
    "serde": {
        "what": "Фреймворк сериализации/десериализации (derive-макросы)",
        "why": "Декларативный, быстрый, поддерживает JSON/TOML/YAML/bincode, zero-copy",
        "how": "[derive(Serialize, Deserialize)] struct User { name: String, age: u32 }"
    },
    "async traits": {
        "what": "Трейты с async методами (требует async-trait крейт или Rust 1.75+)",
        "why": "Абстракция над асинхронным поведением, моки в тестах, плагины",
        "how": "[async_trait] trait Storage { async fn save(&self, data: Data); }"
    },
    "pin unpin": {
        "what": "Pin<P> гарантирует, что значение не перемещается в памяти",
        "why": "Необходимо для самоссылающихся структур, Future, intrusive collections",
        "how": "let mut future = Box::pin(async { ... }); let pinned = future.as_mut();"
    },
    "generics traits": {
        "what": "Трейты с параметрами типа (Generic Associated Types — GAT)",
        "why": "Выразительные абстракции: итераторы с лайфтаймами, асинхронные трейты",
        "how": "trait Iterator { type Item; fn next(&mut self) -> Option<Self::Item>; }"
    },

    # C++
    "RAII": {
        "what": "Resource Acquisition Is Initialization — ресурс захватывается в конструкторе, освобождается в деструкторе",
        "why": "Гарантирует освобождение ресурсов (память, файлы, мьютексы) даже при исключениях, нет утечек",
        "how": "std::unique_ptr<File> file = std::make_unique<File>(\"data.txt\"); // файл закроется в деструкторе"
    },
    "move semantics": {
        "what": "Перемещение ресурсов вместо копирования (std::move, rvalue references)",
        "why": "Избегает дорогого глубокого копирования, передаёт владение ресурсом",
        "how": "std::vector<int> v2 = std::move(v1); // v1 пуст, v2 забирает данные"
    },
    "smart pointers": {
        "what": "unique_ptr, shared_ptr, weak_ptr — умные указатели с автоматическим управлением памятью",
        "why": "Исключают утечки памяти, dangling pointers, double free; владеют объектом",
        "how": "auto ptr = std::make_unique<Widget>(); // unique_ptr — единственный владелец"
    },
    "templates": {
        "what": "Параметризованные типы и функции (шаблоны)",
        "why": "Пишем код один раз для любых типов, compile-time полиморфизм, ноль оверхеда",
        "how": "template<typename T> T max(T a, T b) { return a > b ? a : b; }"
    },
    "concepts cpp20": {
        "what": "Ограничения на шаблонные параметры (requires, concept)",
        "why": "Чёткие ошибки компиляции, документирование требований, лучше чем SFINAE",
        "how": "template<std::integral T> T add(T a, T b) { return a + b; }"
    },
    "coroutines cpp20": {
        "what": "Функции с co_await/co_yield/co_return для асинхронного кода",
        "why": "Линейный асинхронный код без колбэков, композиция, ленивые вычисления",
        "how": "cppcoro::generator<int> gen() { for(int i=0;i<10;++i) co_yield i; }"
    },
    "modules cpp20": {
        "what": "Система модулей вместо заголовочных файлов (import/export)",
        "why": "Быстрее компиляция, нет ODR нарушений, инкапсуляция, нет макросов",
        "how": "export module math; export int add(int a, int b); // math.cppm"
    },
    "smart pointers": {
        "what": "unique_ptr, shared_ptr, weak_ptr — умные указатели с автоматическим управлением памятью",
        "why": "Исключают утечки памяти, dangling pointers, double free; владеют объектом",
        "how": "auto ptr = std::make_unique<Widget>(); // unique_ptr — единственный владелец"
    },
    "perfect forwarding": {
        "what": "std::forward сохраняет категорию значения (lvalue/rvalue) при передаче дальше",
        "why": "Позволяет писать универсальные обёртки/фабрики, сохраняет move-семантику",
        "how": "template<typename T> void wrapper(T&& arg) { func(std::forward<T>(arg)); }"
    },
    "concepts cpp20": {
        "what": "Ограничения на шаблонные параметры (requires, concept)",
        "why": "Чёткие ошибки компиляции, документирование требований, лучше чем SFINAE",
        "how": "template<std::integral T> T add(T a, T b) { return a + b; }"
    },
    "coroutines cpp20": {
        "what": "Функции с co_await/co_yield/co_return для асинхронного кода",
        "why": "Линейный асинхронный код без колбэков, композиция, ленивые вычисления",
        "how": "cppcoro::generator<int> gen() { for(int i=0;i<10;++i) co_yield i; }"
    },
    "modules cpp20": {
        "what": "Система модулей вместо заголовочных файлов (import/export)",
        "why": "Быстрее компиляция, нет ODR нарушений, инкапсуляция, нет макросов",
        "how": "export module math; export int add(int a, int b); // math.cppm"
    },
    "smart pointers": {
        "what": "unique_ptr, shared_ptr, weak_ptr — умные указатели с автоматическим управлением памятью",
        "why": "Исключают утечки памяти, dangling pointers, double free; владеют объектом",
        "how": "auto ptr = std::make_unique<Widget>(); // unique_ptr — единственный владелец"
    },
    "perfect forwarding": {
        "what": "std::forward сохраняет категорию значения (lvalue/rvalue) при передаче дальше",
        "why": "Позволяет писать универсальные обёртки/фабрики, сохраняет move-семантику",
        "how": "template<typename T> void wrapper(T&& arg) { func(std::forward<T>(arg)); }"
    },
    "concepts cpp20": {
        "what": "Ограничения на шаблонные параметры (requires, concept)",
        "why": "Чёткие ошибки компиляции, документирование требований, лучше чем SFINAE",
        "how": "template<std::integral T> T add(T a, T b) { return a + b; }"
    },
    "coroutines cpp20": {
        "what": "Функции с co_await/co_yield/co_return для асинхронного кода",
        "why": "Линейный асинхронный код без колбэков, композиция, ленивые вычисления",
        "how": "cppcoro::generator<int> gen() { for(int i=0;i<10;++i) co_yield i; }"
    },
    "modules cpp20": {
        "what": "Система модулей вместо заголовочных файлов (import/export)",
        "why": "Быстрее компиляция, нет ODR нарушений, инкапсуляция, нет макросов",
        "how": "export module math; export int add(int a, int b); // math.cppm"
    },
    "smart pointers": {
        "what": "unique_ptr, shared_ptr, weak_ptr — умные указатели с автоматическим управлением памятью",
        "why": "Исключают утечки памяти, dangling pointers, double free; владеют объектом",
        "how": "auto ptr = std::make_unique<Widget>(); // unique_ptr — единственный владелец"
    },
    "perfect forwarding": {
        "what": "std::forward сохраняет категорию значения (lvalue/rvalue) при передаче дальше",
        "why": "Позволяет писать универсальные обёртки/фабрики, сохраняет move-семантику",
        "how": "template<typename T> void wrapper(T&& arg) { func(std::forward<T>(arg)); }"
    },
    "concepts cpp20": {
        "what": "Ограничения на шаблонные параметры (requires, concept)",
        "why": "Чёткие ошибки компиляции, документирование требований, лучше чем SFINAE",
        "how": "template<std::integral T> T add(T a, T b) { return a + b; }"
    },
    "coroutines cpp20": {
        "what": "Функции с co_await/co_yield/co_return для асинхронного кода",
        "why": "Линейный асинхронный код без колбэков, композиция, ленивые вычисления",
        "how": "cppcoro::generator<int> gen() { for(int i=0;i<10;++i) co_yield i; }"
    },
    "modules cpp20": {
        "what": "Система модулей вместо заголовочных файлов (import/export)",
        "why": "Быстрее компиляция, нет ODR нарушений, инкапсуляция, нет макросов",
        "how": "export module math; export int add(int a, int b); // math.cppm"
    },
    "smart pointers": {
        "what": "unique_ptr, shared_ptr, weak_ptr — умные указатели с автоматическим управлением памятью",
        "why": "Исключают утечки памяти, dangling pointers, double free; владеют объектом",
        "how": "auto ptr = std::make_unique<Widget>(); // unique_ptr — единственный владелец"
    },
    "perfect forwarding": {
        "what": "std::forward сохраняет категорию значения (lvalue/rvalue) при передаче дальше",
        "why": "Позволяет писать универсальные обёртки/фабрики, сохраняет move-семантику",
        "how": "template<typename T> void wrapper(T&& arg) { func(std::forward<T>(arg)); }"
    },
    "concepts cpp20": {
        "what": "Ограничения на шаблонные параметры (requires, concept)",
        "why": "Чёткие ошибки компиляции, документирование требований, лучше чем SFINAE",
        "how": "template<std::integral T> T add(T a, T b) { return a + b; }"
    },
    "coroutines cpp20": {
        "what": "Функции с co_await/co_yield/co_return для асинхронного кода",
        "why": "Линейный асинхронный код без колбэков, композиция, ленивые вычисления",
        "how": "cppcoro::generator<int> gen() { for(int i=0;i<10;++i) co_yield i; }"
    },
    "modules cpp20": {
        "what": "Система модулей вместо заголовочных файлов (import/export)",
        "why": "Быстрее компиляция, нет ODR нарушений, инкапсуляция, нет макросов",
        "how": "export module math; export int add(int a, int b); // math.cppm"
    },
    "smart pointers": {
        "what": "unique_ptr, shared_ptr, weak_ptr — умные указатели с автоматическим управлением памятью",
        "why": "Исключают утечки памяти, dangling pointers, double free; владеют объектом",
        "how": "auto ptr = std::make_unique<Widget>(); // unique_ptr — единственный владелец"
    },
    "perfect forwarding": {
        "what": "std::forward сохраняет категорию значения (lvalue/rvalue) при передаче дальше",
        "why": "Позволяет писать универсальные обёртки/фабрики, сохраняет move-семантику",
        "how": "template<typename T> void wrapper(T&& arg) { func(std::forward<T>(arg)); }"
    },
    "concepts cpp20": {
        "what": "Ограничения на шаблонные параметры (requires, concept)",
        "why": "Чёткие ошибки компиляции, документирование требований, лучше чем SFINAE",
        "how": "template<std::integral T> T add(T a, T b) { return a + b; }"
    },
    "coroutines cpp20": {
        "what": "Функции с co_await/co_yield/co_return для асинхронного кода",
        "why": "Линейный асинхронный код без колбэков, композиция, ленивые вычисления",
        "how": "cppcoro::generator<int> gen() { for(int i=0;i<10;++i) co_yield i; }"
    },
    "modules cpp20": {
        "what": "Система модулей вместо заголовочных файлов (import/export)",
        "why": "Быстрее компиляция, нет ODR нарушений, инкапсуляция, нет макросов",
        "how": "export module math; export int add(int a, int b); // math.cppm"
    },
}

def find_code_blocks(blocks):
    """Find all code blocks in content_blocks"""
    code_blocks = []
    for i, block in enumerate(blocks):
        if block.get("type") == "code":
            code_blocks.append((i, block))
    return code_blocks

def get_code_language(block):
    return block.get("language", "")

def get_code_content(block):
    return block.get("content", "")

def detect_concept(code: str, language: str) -> str:
    """Detect which concept the code demonstrates"""
    code_lower = code.lower()
    lang = code.lower()
    
    # JavaScript patterns
    if "console.log" in code:
        return "console.log"
    if "let " in code or "const " in code:
        return "let const"
    if "=>" in code and "function" not in code:
        return "arrow function"
    if "`" in code and "${" in code:
        return "template literal"
    if "destructuring" in code_lower or ("{" in code and "}" in code and "=" in code and ("let " in code or "const " in code)):
        return "destructuring"
    if "..." in code:
        return "spread operator"
    if "async " in code and "await " in code:
        return "async await"
    if "Promise.all" in code:
        return "Promise.all"
    if ".map(" in code and ".filter(" in code or ".reduce(" in code:
        return "map filter reduce"
    if "?." in code:
        return "optional chaining"
    if "??" in code:
        return "nullish coalescing"
    
    # Python
    if "f\"" in code or "f'" in code:
        return "f-string"
    if "[" in code and "for " in code and "in " in code and "]" in code:
        return "list comprehension"
    if "{" in code and "for " in code and "in " in code and "}" in code and ":" in code:
        return "dict comprehension"
    if "@dataclass" in code:
        return "dataclass"
    if "with " in code and "open(" in code and "as " in code:
        return "context manager"
    if "@dataclass" in code:
        return "dataclasses"
    if "async def" in code:
        return "async def"
    if "asyncio.gather" in code:
        return "asyncio.gather"
    if "Path(" in code or "pathlib" in code:
        return "pathlib"
    if "field(" in code and "default_factory" in code:
        return "dataclasses field"
    if "async with" in code:
        return "async with"
    if "TypeVar" in code or "Generic[" in code:
        return "type var generic"
    
    # C#
    if "from " in code and "select " in code and "where " in code:
        return "LINQ"
    if "async " in code and "await " in code:
        return "async await"
    if "record " in code:
        return "records"
    if "switch " in code and "=>" in code:
        return "pattern matching switch"
    if "?" in code and "string?" in code:
        return "nullable reference types"
    if "with {" in code:
        return "records with with-expression"
    if "switch " in code and "=>" in code:
        return "pattern matching switch"
    if "IAsyncEnumerable" in code:
        return "async streams"
    if "[Generator]" in code or "IIncrementalGenerator" in code:
        return "source generators"
    
    # Rust
    if "let " in code and "String::from" in code:
        return "ownership"
    if "&" in code and "mut" in code:
        return "borrowing"
    if "'a" in code or "'static" in code:
        return "lifetimes"
    if "Option<" in code or "Result<" in code:
        return "option result"
    if "trait " in code and "fn " in code:
        return "traits"
    if "match " in code:
        return "pattern matching"
    if "Rc<" in code or "Arc<" in code or "Box<" in code or "RefCell" in code:
        return "smart pointers"
    if "async " in code and ".await" in code:
        return "async await"
    if "tokio" in code:
        return "tokio"
    if "serde" in code or "Serialize" in code or "Deserialize" in code:
        return "serde"
    if "async_trait" in code or "async_trait" in code:
        return "async traits"
    if "Pin<" in code or "Unpin" in code:
        return "pin unpin"
    if "type Item" in code or "Generic" in code:
        return "generics traits"
    
    # C++
    if "std::unique_ptr" in code or "std::make_unique" in code or "std::shared_ptr" in code:
        return "smart pointers"
    if "std::move" in code or "std::forward" in code:
        return "move semantics"
    if "template<" in code or "typename " in code:
        return "templates"
    if "concept " in code or "requires " in code:
        return "concepts cpp20"
    if "co_await" in code or "co_yield" in code or "co_return" in code:
        return "coroutines cpp20"
    if "module " in code or "import " in code or "export " in code:
        return "modules cpp20"
    if "std::move" in code or "std::forward" in code:
        return "perfect forwarding"
    if "concept " in code or "requires " in code:
        return "concepts cpp20"
    if "co_await" in code or "co_yield" in code or "co_return" in code:
        return "coroutines cpp20"
    if "module " in code or "import " in code or "export " in code:
        return "modules cpp20"
    if "std::move" in code or "std::forward" in code:
        return "perfect forwarding"
    if "concept " in code or "requires " in code:
        return "concepts cpp20"
    if "co_await" in code or "co_yield" in code or "co_return" in code:
        return "coroutines cpp20"
    if "module " in code or "import " in code or "export " in code:
        return "modules cpp20"
    
    # Rust specific
    if "let " in code and "String::from" in code:
        return "ownership"
    if "&" in code and "mut" in code:
        return "borrowing"
    if "'a" in code or "'static" in code:
        return "lifetimes"
    if "Option<" in code or "Result<" in code:
        return "option result"
    if "trait " in code and "fn " in code:
        return "traits"
    if "match " in code:
        return "pattern matching"
    if "Rc<" in code or "Arc<" in code or "Box<" in code or "RefCell" in code:
        return "smart pointers"
    if "async " in code and ".await" in code:
        return "async await"
    if "tokio" in code:
        return "tokio"
    if "serde" in code or "Serialize" in code or "Deserialize" in code:
        return "serde"
    if "async_trait" in code or "async_trait" in code:
        return "async traits"
    if "Pin<" in code or "Unpin" in code:
        return "pin unpin"
    if "type Item" in code or "Generic" in code:
        return "generics traits"
    
    return ""

def enhance_code_block(block: Dict) -> Dict:
    """Add explanation to a code block"""
    code = block.get("content", "")
    language = block.get("language", "")
    
    if not code.strip():
        return block
    
    concept = detect_concept(code, language)
    if concept and concept in EXAMPLE_EXPLANATIONS:
        explanation = EXAMPLE_EXPLANATIONS[concept]
        
        # Add explanation as a text block before the code
        explanation_block = {
            "type": "text",
            "content": f"> 💡 **Пример: {concept}**\n\n**Что делает:** {explanation['what']}\n\n**Зачем нужно:** {explanation['why']}\n\n**Как работает:** {explanation['how']}"
        }
        
        # We'll return the explanation to be inserted before this block
        return {"explanation": explanation_block, "original": block}
    
    return block

def enhance_lesson_file(filepath: Path):
    """Enhance a single lesson JSON file with example explanations"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lesson = json.load(f)
    
    content_blocks = lesson.get("content_blocks", [])
    new_blocks = []
    
    i = 0
    while i < len(content_blocks):
        block = content_blocks[i]
        
        if block.get("type") == "code":
            # Check if previous block is already an explanation for this code
            has_explanation = False
            if new_blocks and new_blocks[-1].get("type") == "text":
                prev_content = new_blocks[-1].get("content", "")
                if "Пример:" in prev_content and ("Что делает:" in prev_content or "Зачем нужно:" in prev_content):
                    has_explanation = True
            
            if not has_explanation:
                # Add explanation before this code block
                block_copy = content_blocks[i].copy()
                code = block.get("content", "")
                language = block.get("language", "")
                concept = detect_concept(code, "")
                
                if concept and concept in EXAMPLE_EXPLANATIONS:
                    explanation = EXAMPLE_EXPLANATIONS[concept]
                    explanation_block = {
                        "type": "text",
                        "content": f"> 💡 **Пример: {concept}**\n\n**Что делает:** {EXAMPLE_EXPLANATIONS[concept]['what']}\n\n**Зачем нужно:** {EXAMPLE_EXPLANATIONS[concept]['why']}\n\n**Как работает:** {EXAMPLE_EXPLANATIONS[concept]['how']}"
                    }
                    new_blocks.append(explanation_block)
            
            new_blocks.append(block)
        else:
            new_blocks.append(block)
        
        i += 1
    
    lesson["content_blocks"] = new_blocks
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)

def process_all_lessons():
    base_path = Path("/Users/xiip.shk/работа/Kernify/fixtures/lessons")
    
    for lang_dir in ["javascript", "python", "rust", "csharp", "cpp", "css"]:
        lang_path = Path(f"/Users/xiip.shk/работа/Kernify/fixtures/lessons/{lang_dir}")
        if not lang_path.exists():
            continue
        
        lesson_files = sorted(lang_path.glob("*.json"))
        print(f"Processing {lang_dir} ({len(lesson_files)} lessons)...")
        
        for lf in lesson_files:
            try:
                enhance_lesson_file(lf)
            except Exception as e:
                print(f"  Error processing {lf.name}: {e}")

if __name__ == "__main__":
    process_all_lessons()
    print("Done!")