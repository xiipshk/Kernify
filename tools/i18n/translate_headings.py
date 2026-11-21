#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translate all English headings (level 2, 3, 4) in lesson content blocks to Russian.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any

# Comprehensive heading translations
HEADING_TRANSLATIONS = {
    # Common section headings
    'Lesson Objectives': 'Цели урока',
    'Lesson Summary': 'Ключевые выводы',
    'Key Takeaways': 'Ключевые выводы',
    'Key Points': 'Ключевые моменты',
    'Summary': 'Резюме',
    'Conclusion': 'Заключение',
    'Practice': 'Практические задания',
    'Practical Tasks': 'Практические задания',
    'Exercises': 'Упражнения',
    'Homework': 'Домашнее задание',
    'Common Mistakes': 'Типичные ошибки новичков',
    'Typical Errors': 'Типичные ошибки',
    'Common Errors': 'Частые ошибки',
    'Useful Resources': 'Полезные ресурсы',
    'Resources': 'Ресурсы',
    'Further Reading': 'Дополнительное чтение',
    'Security Questions': 'Вопросы по безопасности',
    'Security': 'Безопасность',
    'Reading': 'Чтение',
    'Key Implementations': 'Ключевые реализации',
    'Key Files': 'Ключевые файлы',
    'Key Advantage': 'Ключевое преимущество',
    'Key Values': 'Ключевые значения',
    'Keyboard Test': 'Тест клавиатуры',
    'Key Components': 'Ключевые компоненты',
    'Error Handling': 'Обработка ошибок',
    'Error Handling with async/await': 'Обработка ошибок с async/await',
    'Errors in asynchronous code': 'Ошибки в асинхронном коде',
    'Error codes vs Exceptions': 'Коды ошибок против исключений',
    'Reading IL': 'Чтение IL',
    'Reading attributes via Reflection': 'Чтение атрибутов через рефлексию',
    'Dictionary': 'Словарь',
    'SortedSet': 'Отсортированное множество',
    'Task 3: Error code hierarchy': 'Задача 3: Иерархия кодов ошибок',
    'Cache Locality is the Key to Performance': 'Локальность кэша — ключ к производительности',
    'Rules for Strict Aliasing': 'Правила строгого алиасинга',
    'API Design with Correct Resource Semantics': 'Проектирование API с правильной семантикой ресурсов',
    'std::expected (C++23) for Error Handling without Exceptions': 'std::expected (C++23) для обработки ошибок без исключений',
    'Resource Management (RAII)': 'Управление ресурсами (RAII)',
    'Key implementation points': 'Ключевые моменты реализации',
    'Keywords `final` and `override`': 'Ключевые слова `final` и `override`',
    'Key PEP to know': 'Ключевые PEP, которые нужно знать',
    'Key files to study': 'Ключевые файлы для изучения',
    'Content Security Policy': 'Content Security Policy (CSP)',
    'Dependency Security': 'Безопасность зависимостей',
    'Dependency Security (Supply Chain)': 'Безопасность цепочки поставок',
    'Web Vitals — Key Metrics': 'Web Vitals — ключевые метрики',
    'Security Fundamentals (OWASP Top 10 for Python)': 'Основы безопасности (OWASP Top 10 для Python)',
    'Problem: Resource Management': 'Проблема: управление ресурсами',
    'Mistakes are normal': 'Ошибки — это нормально',
    'SyntaxError — syntax error (code does not run)': 'SyntaxError — синтаксическая ошибка (код не запускается)',
    'NameError — access to a non-existent variable': 'NameError — доступ к несуществующей переменной',
    'TypeError — wrong type for operation': 'TypeError — неверный тип для операции',
    'ValueError — correct type, but invalid value': 'ValueError — правильный тип, но недопустимое значение',
    'IndexError / KeyError — collection out of bounds': 'IndexError / KeyError — выход за границы коллекции',
    'ZeroDivisionError — division by zero': 'ZeroDivisionError — деление на ноль',
    'Error handling (preliminary)': 'Обработка ошибок (введение)',
    '6. Error handling': '6. Обработка ошибок',
    '6. Security Fundamentals': '6. Основы безопасности',
    '7. Error handling': '7. Обработка ошибок',
    '5. Dependency Security': '5. Безопасность зависимостей',
    '5.4 SLO / SLI / Error Budgets': '5.4 SLO / SLI / Бюджеты ошибок',
    '1. Security': '1. Безопасность',
    '1.2 Content Security Policy (CSP)': '1.2 Content Security Policy (CSP)',
    '1.8 Dependency Security': '1.8 Безопасность зависимостей',
    '2.1 Web Vitals': '2.1 Web Vitals',
    '1.4 Security: context-sensitive output encoding': '1.4 Безопасность: контекстно-зависимое кодирование вывода',
    '1.5 Trusted Types (Modern Browser Security)': '1.5 Trusted Types (современная безопасность браузера)',
    '3.2 CORS': '3.2 CORS',
    '4. Content Security Policy': '4. Content Security Policy',
    '5. Dependency Security': '5. Безопасность зависимостей',
    '7. Header Security Checklist': '7. Чек-лист безопасности заголовков',
    '8. Browser vs Node.js Security Context': '8. Контекст безопасности браузера vs Node.js',
    '10. Security questions': '10. Вопросы по безопасности',
    '🎯 Lesson objectives': '🎯 Цели урока',
    'Lesson Ключевые выводы': 'Ключевые выводы урока',
    'Exercise 1: Creating a Project': 'Упражнение 1: Создание проекта',
    'Exercise 2: Experiment with errors': 'Упражнение 2: Эксперименты с ошибками',
    'Exercise 3: Parsing warnings': 'Упражнение 3: Разбор предупреждений',
    'Exercise 1: Variables and Mutability': 'Упражнение 1: Переменные и изменяемость',
    'Exercise 2: Tuples and Arrays': 'Упражнение 2: Кортежи и массивы',
    'Exercise 3: Constants and Types': 'Упражнение 3: Константы и типы',
    'Exercise 4: Numeric Literals': 'Упражнение 4: Числовые литералы',
    'Exercise 1: FizzBuzz': 'Упражнение 1: FizzBuzz',
    'Exercise 2: Searching an Array': 'Упражнение 2: Поиск в массиве',
    'Exercise 3: Nested Loops with Labels': 'Упражнение 3: Вложенные циклы с метками',
    'Exercise 4: `if` as an expression': 'Упражнение 4: `if` как выражение',
    'Exercise 1: Calculator with functions': 'Упражнение 1: Калькулятор с функциями',
    'Exercise 2: Closures and Iterators': 'Упражнение 2: Замыкания и итераторы',
    'Exercise 3: Higher Order Function': 'Упражнение 3: Функция высшего порядка',
    'Exercise 4: Divergent Function': 'Упражнение 4: Расходящаяся функция',
    'Exercise 1: Move vs Clone': 'Упражнение 1: Перемещение vs Клонирование',
    'Exercise 2: Borrowing Functions': 'Упражнение 2: Заимствование функций',
    'Exercise 3: Slicing': 'Упражнение 3: Срезы',
    'Exercise 4: Lifetime': 'Упражнение 4: Время жизни',
    'Exercise 1: Text Processing': 'Упражнение 1: Обработка текста',
    'Exercise 2: Removing duplicates while maintaining order': 'Упражнение 2: Удаление дубликатов с сохранением порядка',
    'Exercise 3: Grouping by Key': 'Упражнение 3: Группировка по ключу',
    'Exercise 4: Efficient String Concatenation': 'Упражнение 4: Эффективная конкатенация строк',
    'Operator `?`—Error Propagation': 'Оператор `?` — распространение ошибок',
    'Exercise 1: Geometric Shapes': 'Упражнение 1: Геометрические фигуры',
    'Exercise 2: Parsing Commands': 'Упражнение 2: Разбор команд',
    'Exercise 3: Option chains': 'Упражнение 3: Цепочки Option',
    'Implementation of `std::error::Error`': 'Реализация `std::error::Error`',
    '`thiserror` — for libraries (derive Error)': '`thiserror` — для библиотек (derive Error)',
    '6. Error Handling Strategies': '6. Стратегии обработки ошибок',
    'Exercise 1: Own error type with `thiserror`': 'Упражнение 1: Свой тип ошибки с `thiserror`',
    'Exercise 2: Error chain with context (`anyhow`)': 'Упражнение 2: Цепочка ошибок с контекстом (`anyhow`)',
    'Exercise 3: Result Combinators': 'Упражнение 3: Комбинаторы Result',
    'Exercise 1: Modular structure': 'Упражнение 1: Модульная структура',
    'Exercise 2: Cargo features': 'Упражнение 2: Фичи Cargo',
    'Exercise 3: Workspace': 'Упражнение 3: Рабочее пространство',
    'Exercise 1: Generic trait with associated type': 'Упражнение 1: Обобщённый трейт с ассоциированным типом',
    'Exercise 2: `impl Trait` in return type': 'Упражнение 2: `impl Trait` в типе возврата',
    'Exercise 3: Newtype for `Display`': 'Упражнение 3: Newtype для `Display`',
    'Exercise 1: Partial Move and ref': 'Упражнение 1: Частичное перемещение и ref',
    'Exercise 2: `mem::replace` for state machine': 'Упражнение 2: `mem::replace` для машины состояний',
    'Exercise 3: `Pin` for async state machine': 'Упражнение 3: `Pin` для асинхронной машины состояний',
    'Exercise 1: Newtype for Validation': 'Упражнение 1: Newtype для валидации',
    'Exercise 2: DST in trait objects': 'Упражнение 2: DST в трейт-объектах',
    'Exercise 3: PhantomData for FFI wrapper': 'Упражнение 3: PhantomData для FFI-обёртки',
    'Exercise 1: HRTB for callback with landing page': 'Упражнение 1: HRTB для колбэка с лендинг-страницей',
    'Exercise 2: Const generics for matrices': 'Упражнение 2: Const generics для матриц',
    'Exercise 3: Sealed trait for internal API': 'Упражнение 3: Sealed trait для внутреннего API',
    'Exercise 1: Custom iterator — Prime numbers': 'Упражнение 1: Пользовательский итератор — простые числа',
    'Exercise 2: Group by with itertools': 'Упражнение 2: Group by с itertools',
    'Exercise 3: Function Validator': 'Упражнение 3: Валидатор функций',
    'AppError — single error': 'AppError — единая ошибка',
    'Exercise 1: Implement OrderService': 'Упражнение 1: Реализация OrderService',
    'Exercise 2: Feature Flags': 'Упражнение 2: Флаги фич',
    'Exercise 1: Graph with Rc/Weak': 'Упражнение 1: Граф с Rc/Weak',
    'Exercise 2: Cache with Arc<RwLock>': 'Упражнение 2: Кэш с Arc<RwLock>',
    'Exercise 3: Copy-on-Write config': 'Упражнение 3: Copy-on-Write конфигурация',
    'Exercise 1: Testing the Calculator': 'Упражнение 1: Тестирование калькулятора',
    'Exercise 2: Property-based sorting test': 'Упражнение 2: Property-based тест сортировки',
    'Exercise 3: Mock test for a service': 'Упражнение 3: Mock-тест для сервиса',
    'Error Handling': 'Обработка ошибок',
    'Exercise 1: Config with TOML': 'Упражнение 1: Конфиг с TOML',
    'Exercise 2: HTTP client with retrays': 'Упражнение 2: HTTP-клиент с повторными попытками',
    'Exercise 3: Logger to file with rotation': 'Упражнение 3: Логгер в файл с ротацией',
    'Exercise 1: Pull workers with semaphore': 'Упражнение 1: Рабочие с семафором',
    'Exercise 2: Graceful shutdown': 'Упражнение 2: Graceful shutdown',
    'Exercise 3: Rate limiter with tokens': 'Упражнение 3: Rate limiter с токенами',
    'Exercise 1: Parallel MapReduce': 'Упражнение 1: Параллельный MapReduce',
    'Exercise 2: Thread pool with workers': 'Упражнение 2: Пул потоков с рабочими',
    'Exercise 3: Lock-free counter with batch processing': 'Упражнение 3: Lock-free счётчик с батчевой обработкой',
    '4. Errors (src/error.rs)': '4. Ошибки (src/error.rs)',
    'Exercise 1: Arena allocator': 'Упражнение 1: Аренда аллокатора',
    'Exercise 2: Intrusive linked list': 'Упражнение 2: Интрузивный связный список',
    'Exercise 3: Type-safe arena with `PhantomData`': 'Упражнение 3: Типобезопасная арена с `PhantomData`',
    'Exercise 1: GAT for cache with landing page': 'Упражнение 1: GAT для кэша с лендинг-страницей',
    'Exercise 2: Const generic matrix': 'Упражнение 2: Const generic матрица',
    'Exercise 3: HRTB for callbacks with borrowing': 'Упражнение 3: HRTB для колбэков с заимствованием',
    'Exercise 4: Sealed trait for internal API': 'Упражнение 4: Sealed trait для внутреннего API',
    'Exercise 1: Heterogeneous collection with Any': 'Упражнение 1: Гетерогенная коллекция с Any',
    'Exercise 2: Type-safe builder with PhantomData': 'Упражнение 2: Типобезопасный строитель с PhantomData',
    'Exercise 3: Function pointer table for plugins': 'Упражнение 3: Таблица указателей на функции для плагинов',
    'Exercise 1: Safe wrapper over C malloc/free': 'Упражнение 1: Безопасная обёртка над C malloc/free',
    'Exercise 2: Intrusive linked list with raw pointers': 'Упражнение 2: Интрузивный связный список с raw-указателями',
    'Exercise 3: FFI wrapper for a simple C library': 'Упражнение 3: FFI-обёртка для простой C-библиотеки',
    'Key Points': 'Ключевые моменты',
    'Exercise 1: Simple timer Future': 'Упражнение 1: Простой timer Future',
    'Exercise 2: Channel as Stream': 'Упражнение 2: Channel как Stream',
    'Exercise 3: Mini executor with Waker': 'Упражнение 3: Мини-исполнитель с Waker',
    'Exercise 1: Lock-free HashMap (simplified)': 'Упражнение 1: Lock-free HashMap (упрощённый)',
    'Exercise 2: MPSC with epoch reclamation': 'Упражнение 2: MPSC с epoch reclamation',
    'Exercise 3: Read-mostly cache with RCU': 'Упражнение 3: Read-mostly кэш с RCU',
    'Exercise 1: `bitflags!` analogue': 'Упражнение 1: Аналог `bitflags!`',
    'Exercise 2: Procedural derive for `Default`': 'Упражнение 2: Процедурный derive для `Default`',
    'Exercise 3: Function-like macro for asynchronous retry': 'Упражнение 3: Function-like макрос для асинхронного retry',
    'Exercise 1: FFI wrapper around the C library': 'Упражнение 1: FFI-обёртка вокруг C-библиотеки',
    'Exercise 2: `no_std` driver UART': 'Упражнение 2: `no_std` драйвер UART',
    'Exercise 3: Memory-mapped file with synchronization': 'Упражнение 3: Memory-mapped файл с синхронизацией',
    'Exercise 1: Setting up a workspace with features': 'Упражнение 1: Настройка workspace с фичами',
    'Exercise 2: Cross-compilation for embedded': 'Упражнение 2: Кросскомпиляция для embedded',
    'Exercise 3: Automating a Release with xtask': 'Упражнение 3: Автоматизация релиза с xtask',
    '2. Security guarantees': '2. Гарантии безопасности',
    'Key Features:': 'Ключевые особенности:',
    'Error: Unused variable': 'Ошибка: неиспользуемая переменная',
    'Error: Modifying an immutable variable': 'Ошибка: изменение неизменяемой переменной',
    'Error: Type mismatch': 'Ошибка: несоответствие типов',
    'Useful compiler flags': 'Полезные флаги компилятора',
    'Common compiler flags': 'Частые флаги компилятора',
    'Reading and writing elements': 'Чтение и запись элементов',
    '5. Keyword this': '5. Ключевое слово this',
    'Reading IL': 'Чтение IL',
    'Dictionary<TKey, TValue> — dictionary (hash table)': 'Dictionary<TKey, TValue> — словарь (хеш-таблица)',
    'Dictionary<TKey, TValue> — hash table': 'Dictionary<TKey, TValue> — хеш-таблица',
    'SortedSet<T> / SortedDictionary<TKey, TValue> — red-black tree': 'SortedSet<T> / SortedDictionary<TKey, TValue> — красно-чёрное дерево',
    '3. Error handling': '3. Обработка ошибок',
    '3. Dictionary<TKey, TValue> — dictionary': '3. Dictionary<TKey, TValue> — словарь',
    'Syntax and Key Points': 'Синтаксис и ключевые моменты',
    '5. Keyboard interaction': '5. Взаимодействие с клавиатурой',
    'Key values': 'Ключевые значения',
    'Key Advantage': 'Ключевое преимущество',
    '6. Key findings of the project': '6. Ключевые выводы проекта',
    '2. Keyboard focus and :focus-visible': '2. Фокус клавиатуры и :focus-visible',
    'Keyboard test': 'Тест клавиатуры',
    'Key Components': 'Ключевые компоненты',
    'Security questions': 'Вопросы по безопасности',
    'Further Reading': 'Дополнительное чтение',
    'Exercises': 'Упражнения',
    'Practice': 'Практические задания',
    'Practical Tasks': 'Практические задания',
    'Resources': 'Ресурсы',
    'Useful Resources': 'Полезные ресурсы',
    'Common Mistakes': 'Типичные ошибки',
    'Typical Errors': 'Типичные ошибки',
    'Summary': 'Резюме',
    'Key Takeaways': 'Ключевые выводы',
    'Lesson Objectives': 'Цели урока',
    'Lesson Summary': 'Ключевые выводы',
    'Homework': 'Домашнее задание',
    'Security': 'Безопасность',
    'Error Handling': 'Обработка ошибки',
    'Error codes vs Exceptions': 'Коды ошибок против исключений',
    'Reading attributes via Reflection': 'Чтение атрибутов через рефлексию',
    'Dictionary': 'Словарь',
    'Cache Locality is the Key to Performance': 'Локальность кэша — ключ к производительности',
    'Rules for Strict Aliasing': 'Правила строгого алиасинга',
    'API Design with Correct Resource Semantics': 'Проектирование API с правильной семантикой ресурсов',
    'std::expected (C++23) for Error Handling without Exceptions': 'std::expected (C++23) для обработки ошибок без исключений',
    'Resource Management (RAII)': 'Управление ресурсами (RAII)',
    'Key implementation points': 'Ключевые моменты реализации',
    'Keywords `final` and `override`': 'Ключевые слова `final` и `override`',
    'Key PEP to know': 'Ключевые PEP для изучения',
    'Key files to study': 'Ключевые файлы для изучения',
    'Content Security Policy': 'Content Security Policy (CSP)',
    'Dependency Security': 'Безопасность зависимостей',
    'Web Vitals — Key Metrics': 'Web Vitals — ключевые метрики',
    'Security Fundamentals (OWASP Top 10 for Python)': 'Основы безопасности (OWASP Top 10 для Python)',
    'Problem: Resource Management': 'Проблема: управление ресурсами',
    'Mistakes are normal': 'Ошибки — это нормально',
    'SyntaxError — syntax error (code does not run)': 'SyntaxError — синтаксическая ошибка (код не запускается)',
    'NameError — access to a non-existent variable': 'NameError — доступ к несуществующей переменной',
    'TypeError — wrong type for operation': 'TypeError — неверный тип для операции',
    'ValueError — correct type, but invalid value': 'ValueError — правильный тип, но недопустимое значение',
    'IndexError / KeyError — collection out of bounds': 'IndexError / KeyError — выход за границы коллекции',
    'ZeroDivisionError — division by zero': 'ZeroDivisionError — деление на ноль',
    'Error handling (preliminary)': 'Обработка ошибок (введение)',
    '6. Error handling': '6. Обработка ошибок',
    '6. Security Fundamentals': '6. Основы безопасности',
    '7. Error handling': '7. Обработка ошибок',
    '5. Dependency Security': '5. Безопасность зависимостей',
    '5.4 SLO / SLI / Error Budgets': '5.4 SLO / SLI / Бюджеты ошибок',
    '1. Security': '1. Безопасность',
    '1.2 Content Security Policy (CSP)': '1.2 Content Security Policy (CSP)',
    '1.8 Dependency Security': '1.8 Безопасность зависимостей',
    '2.1 Web Vitals': '2.1 Web Vitals',
    '1.4 Security: context-sensitive output encoding': '1.4 Безопасность: контекстно-зависимое кодирование вывода',
    '1.5 Trusted Types (Modern Browser Security)': '1.5 Trusted Types (современная безопасность браузера)',
    '3.2 CORS': '3.2 CORS',
    '4. Content Security Policy': '4. Content Security Policy',
    '5. Dependency Security': '5. Безопасность зависимостей',
    '7. Header Security Checklist': '7. Чек-лист безопасности заголовков',
    '8. Browser vs Node.js Security Context': '8. Контекст безопасности браузера vs Node.js',
    '10. Security questions': '10. Вопросы по безопасности',
    '🎯 Lesson objectives': '🎯 Цели урока',
    'Lesson Ключевые выводы': 'Ключевые выводы урока',
    'Exercise 1: Creating a Project': 'Упражнение 1: Создание проекта',
    'Exercise 2: Experiment with errors': 'Упражнение 2: Эксперименты с ошибками',
    'Exercise 3: Parsing warnings': 'Упражнение 3: Разбор предупреждений',
    'Exercise 1: Variables and Mutability': 'Упражнение 1: Переменные и изменяемость',
    'Exercise 2: Tuples and Arrays': 'Упражнение 2: Кортежи и массивы',
    'Exercise 3: Constants and Types': 'Упражнение 3: Константы и типы',
    'Exercise 4: Numeric Literals': 'Упражнение 4: Числовые литералы',
    'Exercise 1: FizzBuzz': 'Упражнение 1: FizzBuzz',
    'Exercise 2: Searching an Array': 'Упражнение 2: Поиск в массиве',
    'Exercise 3: Nested Loops with Labels': 'Упражнение 3: Вложенные циклы с метками',
    'Exercise 4: `if` as an expression': 'Упражнение 4: `if` как выражение',
    'Exercise 1: Calculator with functions': 'Упражнение 1: Калькулятор с функциями',
    'Exercise 2: Closures and Iterators': 'Упражнение 2: Замыкания и итераторы',
    'Exercise 3: Higher Order Function': 'Упражнение 3: Функция высшего порядка',
    'Exercise 4: Divergent Function': 'Упражнение 4: Расходящаяся функция',
    'Exercise 1: Move vs Clone': 'Упражнение 1: Перемещение vs Клонирование',
    'Exercise 2: Borrowing Functions': 'Упражнение 2: Заимствование функций',
    'Exercise 3: Slicing': 'Упражнение 3: Срезы',
    'Exercise 4: Lifetime': 'Упражнение 4: Время жизни',
    'Exercise 1: Text Processing': 'Упражнение 1: Обработка текста',
    'Exercise 2: Removing duplicates while maintaining order': 'Упражнение 2: Удаление дубликатов с сохранением порядка',
    'Exercise 3: Grouping by Key': 'Упражнение 3: Группировка по ключу',
    'Exercise 4: Efficient String Concatenation': 'Упражнение 4: Эффективная конкатенация строк',
    'Operator `?`—Error Propagation': 'Оператор `?` — распространение ошибок',
    'Exercise 1: Geometric Shapes': 'Упражнение 1: Геометрические фигуры',
    'Exercise 2: Parsing Commands': 'Упражнение 2: Разбор команд',
    'Exercise 3: Option chains': 'Упражнение 3: Цепочки Option',
    'Implementation of `std::error::Error`': 'Реализация `std::error::Error`',
    '`thiserror` — for libraries (derive Error)': '`thiserror` — для библиотек (derive Error)',
    '6. Error Handling Strategies': '6. Стратегии обработки ошибок',
    'Exercise 1: Own error type with `thiserror`': 'Упражнение 1: Свой тип ошибки с `thiserror`',
    'Exercise 2: Error chain with context (`anyhow`)': 'Упражнение 2: Цепочка ошибок с контекстом (`anyhow`)',
    'Exercise 3: Result Combinators': 'Упражнение 3: Комбинаторы Result',
    'Exercise 1: Modular structure': 'Упражнение 1: Модульная структура',
    'Exercise 2: Cargo features': 'Упражнение 2: Фичи Cargo',
    'Exercise 3: Workspace': 'Упражнение 3: Рабочее пространство',
    'Exercise 1: Generic trait with associated type': 'Упражнение 1: Обобщённый трейт с ассоциированным типом',
    'Exercise 2: `impl Trait` in return type': 'Упражнение 2: `impl Trait` в типе возврата',
    'Exercise 3: Newtype for `Display`': 'Упражнение 3: Newtype для `Display`',
    'Exercise 1: Partial Move and ref': 'Упражнение 1: Частичное перемещение и ref',
    'Exercise 2: `mem::replace` for state machine': 'Упражнение 2: `mem::replace` для машины состояний',
    'Exercise 3: `Pin` for async state machine': 'Упражнение 3: `Pin` для асинхронной машины состояний',
    'Exercise 1: Newtype for Validation': 'Упражнение 1: Newtype для валидации',
    'Exercise 2: DST in trait objects': 'Упражнение 2: DST в трейт-объектах',
    'Exercise 3: PhantomData for FFI wrapper': 'Упражнение 3: PhantomData для FFI-обёртки',
    'Exercise 1: HRTB for callback with landing page': 'Упражнение 1: HRTB для колбэка с лендинг-страницей',
    'Exercise 2: Const generics for matrices': 'Упражнение 2: Const generics для матриц',
    'Exercise 3: Sealed trait for internal API': 'Упражнение 3: Sealed trait для внутреннего API',
    'Exercise 1: Custom iterator — Prime numbers': 'Упражнение 1: Пользовательский итератор — простые числа',
    'Exercise 2: Group by with itertools': 'Упражнение 2: Group by с itertools',
    'Exercise 3: Function Validator': 'Упражнение 3: Валидатор функций',
    'AppError — single error': 'AppError — единая ошибка',
    'Exercise 1: Implement OrderService': 'Упражнение 1: Реализация OrderService',
    'Exercise 2: Feature Flags': 'Упражнение 2: Флаги фич',
    'Exercise 1: Graph with Rc/Weak': 'Упражнение 1: Граф с Rc/Weak',
    'Exercise 2: Cache with Arc<RwLock>': 'Упражнение 2: Кэш с Arc<RwLock>',
    'Exercise 3: Copy-on-Write config': 'Упражнение 3: Copy-on-Write конфигурация',
    'Exercise 1: Testing the Calculator': 'Упражнение 1: Тестирование калькулятора',
    'Exercise 2: Property-based sorting test': 'Упражнение 2: Property-based тест сортировки',
    'Exercise 3: Mock test for a service': 'Упражнение 3: Mock-тест для сервиса',
    'Error Handling': 'Обработка ошибок',
    'Exercise 1: Config with TOML': 'Упражнение 1: Конфиг с TOML',
    'Exercise 2: HTTP client with retrays': 'Упражнение 2: HTTP-клиент с повторными попытками',
    'Exercise 3: Logger to file with rotation': 'Упражнение 3: Логгер в файл с ротацией',
    'Exercise 1: Pull workers with semaphore': 'Упражнение 1: Рабочие с семафором',
    'Exercise 2: Graceful shutdown': 'Упражнение 2: Graceful shutdown',
    'Exercise 3: Rate limiter with tokens': 'Упражнение 3: Rate limiter с токенами',
    'Exercise 1: Parallel MapReduce': 'Упражнение 1: Параллельный MapReduce',
    'Exercise 2: Thread pool with workers': 'Упражнение 2: Пул потоков с рабочими',
    'Exercise 3: Lock-free counter with batch processing': 'Упражнение 3: Lock-free счётчик с батчевой обработкой',
    '4. Errors (src/error.rs)': '4. Ошибки (src/error.rs)',
    'Exercise 1: Arena allocator': 'Упражнение 1: Аренда аллокатора',
    'Exercise 2: Intrusive linked list': 'Упражнение 2: Интрузивный связный список',
    'Exercise 3: Type-safe arena with `PhantomData`': 'Упражнение 3: Типобезопасная арена с `PhantomData`',
    'Exercise 1: GAT for cache with landing page': 'Упражнение 1: GAT для кэша с лендинг-страницей',
    'Exercise 2: Const generic matrix': 'Упражнение 2: Const generic матрица',
    'Exercise 3: HRTB for callbacks with borrowing': 'Упражнение 3: HRTB для колбэков с заимствованием',
    'Exercise 4: Sealed trait for internal API': 'Упражнение 4: Sealed trait для внутреннего API',
    'Exercise 1: Heterogeneous collection with Any': 'Упражнение 1: Гетерогенная коллекция с Any',
    'Exercise 2: Type-safe builder with PhantomData': 'Упражнение 2: Типобезопасный строитель с PhantomData',
    'Exercise 3: Function pointer table for plugins': 'Упражнение 3: Таблица указателей на функции для плагинов',
    'Exercise 1: Safe wrapper over C malloc/free': 'Упражнение 1: Безопасная обёртка над C malloc/free',
    'Exercise 2: Intrusive linked list with raw pointers': 'Упражнение 2: Интрузивный связный список с raw-указателями',
    'Exercise 3: FFI wrapper for a simple C library': 'Упражнение 3: FFI-обёртка для простой C-библиотеки',
    'Key Points': 'Ключевые моменты',
    'Exercise 1: Simple timer Future': 'Упражнение 1: Простой timer Future',
    'Exercise 2: Channel as Stream': 'Упражнение 2: Channel как Stream',
    'Exercise 3: Mini executor with Waker': 'Упражнение 3: Мини-исполнитель с Waker',
    'Exercise 1: Lock-free HashMap (simplified)': 'Упражнение 1: Lock-free HashMap (упрощённый)',
    'Exercise 2: MPSC with epoch reclamation': 'Упражнение 2: MPSC с epoch reclamation',
    'Exercise 3: Read-mostly cache with RCU': 'Упражнение 3: Read-mostly кэш с RCU',
    'Exercise 1: `bitflags!` analogue': 'Упражнение 1: Аналог `bitflags!`',
    'Exercise 2: Procedural derive for `Default`': 'Упражнение 2: Процедурный derive для `Default`',
    'Exercise 3: Function-like macro for asynchronous retry': 'Упражнение 3: Function-like макрос для асинхронного retry',
    'Exercise 1: FFI wrapper around the C library': 'Упражнение 1: FFI-обёртка вокруг C-библиотеки',
    'Exercise 2: `no_std` driver UART': 'Упражнение 2: `no_std` драйвер UART',
    'Exercise 3: Memory-mapped file with synchronization': 'Упражнение 3: Memory-mapped файл с синхронизацией',
    'Exercise 1: Setting up a workspace with features': 'Упражнение 1: Настройка workspace с фичами',
    'Exercise 2: Cross-compilation for embedded': 'Упражнение 2: Кросскомпиляция для embedded',
    'Exercise 3: Automating a Release with xtask': 'Упражнение 3: Автоматизация релиза с xtask',
    '2. Security guarantees': '2. Гарантии безопасности',
    'Key Features:': 'Ключевые особенности:',
    'Error: Unused variable': 'Ошибка: неиспользуемая переменная',
    'Error: Modifying an immutable variable': 'Ошибка: изменение неизменяемой переменной',
    'Error: Type mismatch': 'Ошибка: несоответствие типов',
    'Useful compiler flags': 'Полезные флаги компилятора',
    'Common compiler flags': 'Частые флаги компилятора',
}

def translate_headings(filepath: Path, dry_run: bool = False) -> Dict[str, Any]:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    blocks = data.get('content_blocks', [])
    changes = []
    
    for block in blocks:
        if block.get('type') == 'heading':
            content = block.get('content', '')
            original = content
            
            # Try exact match first
            if content in HEADING_TRANSLATIONS:
                content = HEADING_TRANSLATIONS[content]
            else:
                # Try partial matches for longer headings
                for eng, rus in HEADING_TRANSLATIONS.items():
                    if eng in content and rus not in content:
                        content = content.replace(eng, rus)
            
            if content != original:
                block['content'] = content
                changes.append(f'  Heading: "{original}" → "{content}"')
    
    # Also translate text block content that might contain English headings
    for block in blocks:
        if block.get('type') == 'text':
            content = block.get('content', '')
            original = content
            
            # Look for bold English headings in text
            for eng, rus in HEADING_TRANSLATIONS.items():
                # Match <strong>English</strong> or **English** patterns
                patterns = [
                    f'<strong>{re.escape(eng)}</strong>',
                    f'**{re.escape(eng)}**',
                    f'<b>{re.escape(eng)}</b>',
                ]
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        content = re.sub(pattern, f'<strong>{rus}</strong>', content, flags=re.IGNORECASE)
                        changes.append(f'  Text heading: "{eng}" → "{rus}"')
            
            if content != original:
                block['content'] = content
    
    # Also translate list items that start with English headings
    for block in blocks:
        if block.get('type') == 'list':
            items = block.get('items', [])
            for i, item in enumerate(items):
                original = item
                for eng, rus in HEADING_TRANSLATIONS.items():
                    if item.strip().startswith(eng) and rus not in item:
                        items[i] = item.replace(eng, rus, 1)
                        changes.append(f'  List item: "{eng}..." → "{rus}..."')
                        break
    
    data['content_blocks'] = blocks
    
    if not dry_run and changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
    
    return {
        'file': str(filepath),
        'changes': len(changes),
        'details': changes[:10]  # First 10 details
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Translate lesson headings to Russian')
    parser.add_argument('--lang', choices=['python', 'javascript', 'cpp', 'csharp', 'css', 'rust', 'all'], default='all')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    args = parser.parse_args()
    
    base_path = Path('fixtures/lessons')
    languages = ['python', 'javascript', 'cpp', 'csharp', 'css', 'rust'] if args.lang == 'all' else [args.lang]
    
    total_changes = 0
    for lang in languages:
        lang_path = base_path / lang
        if not lang_path.exists():
            continue
        
        files = sorted([f for f in lang_path.iterdir() if f.suffix == '.json'])
        print(f"\n=== Processing {lang.upper()} ({len(files)} lessons) ===")
        
        for filepath in files:
            result = translate_headings(filepath, args.dry_run)
            if result['changes'] > 0:
                print(f"  {filepath.name}: {result['changes']} heading translations")
                total_changes += result['changes']
                for detail in result['details'][:5]:
                    print(f"    {detail}")
                if len(result['details']) > 5:
                    print(f"    ... and {len(result['details']) - 5} more")
            else:
                print(f"  {filepath.name}: OK")
    
    print(f"\n=== Total heading translations: {total_changes} ===")


if __name__ == '__main__':
    main()