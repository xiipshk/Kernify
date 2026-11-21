#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генерирует реальный учебный контент для уроков 12-33 (продвинутые темы C#).
"""

import json
from pathlib import Path

# Реальный контент для каждого продвинутого урока
ADVANCED_LESSONS = {
    12: {
        "title": "Урок 12: Система типов C# — value/reference типы, nullable, boxing/unboxing, record, immutability",
        "short_description": "value/reference типы, nullable, boxing/unboxing, record, struct, class, immutability",
        "goals": [
            "Понимать разницу между value type (struct) и reference type (class)",
            "Работать с nullable типами (T?) и операторами ?, ??, ??=",
            "Понимать boxing/unboxing и как их избегать",
            "Использовать record для неизменяемых данных",
            "Применять immutability паттерны"
        ],
        "content_blocks": [
            {"type": "heading", "level": 2, "content": "🎯 Что вы узнаете"},
            {"type": "list", "items": [
                "Разница между value type (struct) и reference type (class)",
                "Nullable типы (T?) и операторы ?, ??, ??=",
                "Boxing/unboxing: что это и как избежать",
                "Record (C# 9+) для неизменяемых данных",
                "Struct vs Class: когда что использовать",
                "Immutability паттерны"
            ], "ordered": False},
            {"type": "heading", "level": 2, "content": "💡 Value Type vs Reference Type: фундаментальное различие"},
            {"type": "text", "content": "В C# типы делятся на две фундаментальные категории: **value types** (значимые типы) и **reference types** (ссылочные типы). Это не просто теоретическое различие — оно влияет на производительность, потребление памяти и поведение кода."},
            {"type": "heading", "level": 3, "content": "Value Types (struct, enum, примитивы)"},
            {"type": "text", "content": "**Value types** хранят данные напрямую в переменной. При присваивании происходит **копирование** значения:\n\n```csharp\nstruct Point { public int X, Y; }\nPoint p1 = new Point { X = 1, Y = 2 };\nPoint p2 = p1;        // Копия!\np2.X = 100;\nConsole.WriteLine(p1.X); // 1 — оригинал не изменился\n```\n\n**Value types включают**: все примитивы (`int`, `double`, `bool`, `char`), `struct`, `enum`. Они хранятся в **стеке** (обычно), что делает доступ быстрым."},
            {"type": "heading", "level": 3, "content": "Reference Types (class, interface, delegate, array, string)"},
            {"type": "text", "content": "**Reference types** хранят **ссылку** на объект в куче (heap). Переменная содержит адрес объекта:\n\n```csharp\nclass Point { public int X, Y; }\nPoint p1 = new Point { X = 1, Y = 2 };\nPoint p2 = p1;        // Ссылка на ТОТ ЖЕ объект!\np2.X = 100;\nConsole.WriteLine(p1.X); // 100 — оригинал ИЗМЕНИЛСЯ!\n```\n\n**Reference types**: `class`, `interface`, `delegate`, `array`, `string`, `delegate`. Хранятся в **куче (heap)**, доступ через ссылку."},
            {"type": "heading", "level": 3, "content": "Практическое сравнение"},
            {"type": "table", "headers": ["Характеристика", "Value Type (struct)", "Reference Type (class)"], "rows": [
                ["Хранение", "Стек (обычно)", "Куча (heap)"],
                ["Присваивание", "Копия значения", "Копия ссылки"],
                "Равенство", "По значению (Value equality)", "По ссылке (Reference equality)"],
                ["Null", "Не может быть null (кроме Nullable)", "Может быть null"],
                "Наследование", "Не поддерживает наследование", "Поддерживает наследование"],
                "Производительность", "Быстрее (нет GC压力)", "GC pressure, но гибче"]
            ]},
            {"type": "heading", "level": 2, "content": "🔧 Nullable типы (T?) и операторы ?, ??, ??="},
            {"type": "text", "content": "По умолчанию **value types не могут быть null**. `Nullable<T>` (или сокращенно `T?`) решает эту проблему:\n\n```csharp\nint? x = null;        // OK\nint? y = 42;          // OK\nint z = x ?? 0;       // null-coalescing: если x null, то 0\nx ??= 10;             // null-coalescing assignment: если x null, присвоить 10\n\n// Операторы:\nConsole.WriteLine(x?.ToString());  // null-conditional: безопасный доступ\nint len = text?.Length ?? 0;       // комбинация ?. и ??\n```"},
            {"type": "heading", "level": 2, "content": "📦 Boxing и Unboxing: скрытые затраты"},
            {"type": "text", "content": "**Boxing** — упаковка value type в object (создание объекта в куче):\n\n```csharp\nint x = 42;\nobject o = x;        // Boxing: создается объект в куче, значение копируется\nint y = (int)o;      // Unboxing: проверка типа + копирование значения\n```\n\n**Проблемы**: аллокация в куче, нагрузка на GC, потеря производительности.\n\n**Как избежать**:\n- Используйте дженерики (`List<int>` вместо `ArrayList`)\n- Избегайте `object` для value types\n- Используйте `List<T>`, `Dictionary<TKey, TValue>` вместо нетипизированных коллекций"},
            {"type": "heading", "level": 2, "content": "📝 Record (C# 9+) — неизменяемые данные из коробки"},
            {"type": "text", "content": "**Record** — ссылочный тип с value-based equality, неизменяемостью и `with`-выражениями:\n\n```csharp\nrecord Person(string Name, int Age);\n\nvar p1 = new Person(\"Alex\", 25);\nvar p2 = new Person(\"Alex\", 25);\nConsole.WriteLine(p1 == p2);  // True — value-based equality!\n\n// with-expression: копия с изменениями\nvar older = p1 with { Age = 26 }; // p1 не изменился!\n\n// Positional records (короткий синтаксис)\nrecord Point(int X, int Y);\nvar p = new Point(1, 2);\nvar p2 = p with { X = 10 };\n```\n\n**Когда использовать record**: DTO, неизменяемые данные, сравнение по значению."},
            {"type": "heading", "level": 2, "content": "🧊 Immutability (неизменяемость) — лучшая практика"},
            {"type": "text", "content": "**Immutable объекты** — те, чье состояние не меняется после создания. Преимущества:\n- Потокобезопасность (thread-safe)\n- Предсказуемость кода\n- Легкое кэширование и мемоизация\n- Простота отладки\n\n**Паттерны**:\n```csharp\n// 1. Readonly поля + init-only свойства\nclass ImmutablePoint {\n    public int X { get; init; }\n    public int Y { get; init; }\n}\n\n// 2. Record (автоматически immutable)\nrecord Point(int X, int Y);\n\n// 3. Readonly struct (C# 7.2+)\nreadonly struct Point { public int X, Y; }\n```"},
            {"type": "heading", "level": 2, "content": "📋 Struct vs Class: чек-лист выбора"},
            {"type": "list", "items": [
                "✅ **struct**, если: маленький (< 16 байт), неизменяемый, часто создается/уничтожается, value-семантика",
                "✅ **class**, если: нужно наследование, ссылочная семантика, большой объект, идентичность важна",
                "❌ Избегайте struct, если: часто boxing, большие данные, нужна идентичность"
            ], "ordered": false},
            {"type": "heading", "level": 2, "content": "⚠️ Типичные ошибки новичков"},
            {"type": "table", "headers": ["Ошибка", "Как проявляется", "Как правильно"], "rows": [
                ["Struct с mutable полями", "Неожиданные изменения при копировании", "Делайте struct immutable (readonly/init)"],
                ["Сравнение классов через ==" , "Сравнивает ссылки, не значения", "Переопределите Equals/GetHashCode или используйте record"],
                ["Struct в List<T> с частыми изменениями", "Много копирований, медленно", "Используйте class или ImmutableArray"],
                ["struct в async/await", "Копирование на каждом await", "Лучше class для async состояния"],
                ["class вместо struct для маленьких DTO", "Лишний GC pressure", "Используйте readonly struct или record"]
            ]},
            {"type": "heading", "level": 2, "content": "🛠 Практика: закрепите навык"},
            {"type": "list", "items": [
                "Создайте `readonly struct Point3D` с X, Y, Z. Добавьте метод `DistanceTo(Point3D other)`.",
                "Создайте `record Person(string Name, int Age, Address Address)` с `record Address(string City, string Street)`. Проверьте equality и `with`.",
                "Рефакторинг: дан `class MutablePoint { public int X, Y; }`. Сделайте его immutable (readonly struct или record).",
                "Исправьте ошибки:\n```csharp\nstruct Point { public int X, Y; }\nvar p1 = new Point { X = 1, Y = 2 };\nvar p2 = p1; p2.X = 100; // p1.X изменилось? Почему?\n```"
            ], "ordered": true},
            {"type": "heading", "level": 2, "content": "📌 Кратко о главном"},
            {"type": "list", "items": [
                "struct — копируется по значению (стек), class — по ссылке (куча)",
                "T? / Nullable<T> позволяет value types быть null, операторы ?. ?? ??=",
                "Boxing (value→object) и Unboxing (object→value) — дорого, избегайте через generics",
                "Record (C# 9+) — immutable, value-equality, with-expressions из коробки",
                "Immutability — ключ к надежному, потокобезопасному коду. Используйте init, readonly, record, readonly struct",
                "struct для маленьких immutable данных, class для всего остального"
            ], "ordered": false},
            {"type": "heading", "level": 2, "content": "🔗 Полезные ссылки"},
            {"type": "list", "items": [
                "Microsoft Docs — Choosing between class and struct: https://learn.microsoft.com/dotnet/csharp/language-reference/value-types/choosing-class-struct",
                "Microsoft Docs — Nullable value types: https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/nullable-value-types",
                "Microsoft Docs — Record types: https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/record",
                "Microsoft Docs — Boxing and unboxing: https://learn.microsoft.com/dotnet/csharp/programming-guide/types/boxing-and-unboxing"
            ], "ordered": false}
        ],
        "practice_tasks": [
            "Создайте `readonly struct Point3D` с X, Y, Z. Добавьте метод `DistanceTo(Point3D other)`. Проверьте: `new Point3D(1,2,3).DistanceTo(new Point3D(4,5,6))`.",
            "Создайте `record Person(string Name, int Age, Address Address)` с `record Address(string City, string Street)`. Проверьте equality и `with`: `person with { Age = 26 }`.",
            "Создайте `record Transaction(int Id, DateTime Date, decimal Amount)` с `record Account(string Number, decimal Balance)`. Метод `Apply(Transaction t)` возвращает новый Account с обновленным балансом.",
            "Исправьте ошибки:\n```csharp\nstruct Point { public int X, Y; }\nvar p1 = new Point { X = 1, Y = 2 };\nvar p2 = p1; p2.X = 100; // p1.X изменилось? Почему?\n```"
        ],
        "common_errors": [
            {"mistake": "Mutable struct с публичными полями", "correct": "Делайте struct immutable (readonly/readonly struct / init / record)"},
            {"mistake": "Сравнение классов через ==", "correct": "Переопределяйте Equals/GetHashCode или используйте record"},
            {"mistake": "Boxing в цикле", "correct": "Используйте List<T> вместо ArrayList/List<object>"},
            {"mistake": "Struct в async/await с изменениями", "correct": "Лучше class для async состояния или immutable struct"},
            {"mistake": "Struct в List<T> с частыми изменениями", "correct": "Используйте class или ImmutableArray/ImmutableList"},
            {"mistake": "class вместо struct для маленьких DTO", "correct": "Используйте readonly struct или record для DTO"}
        ],
        "resources": [
            "Microsoft Docs — Choosing between class and struct: https://learn.microsoft.com/dotnet/csharp/language-reference/value-types/choosing-class-struct",
            "Microsoft Docs — Nullable value types: https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/nullable-value-types",
            "Microsoft Docs — Record types: https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/record",
            "Microsoft Docs — Boxing and unboxing: https://learn.microsoft.com/dotnet/csharp/programming-guide/types/boxing-and-unboxing",
            "Microsoft Docs — Records: https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/record"
        ],
        "key_takeaways": [
            "struct — копируется по значению (стек), class — по ссылке (куча)",
            "T? / Nullable<T> позволяет value types быть null, операторы ?. ?? ??=",
            "Boxing (value→object) и Unboxing (object→value) — дорого, избегайте через generics",
            "Record (C# 9+) — immutable, value-equality, with-expressions из коробки",
            "Immutability — ключ к надежному, потокобезопасному коду. init, readonly, record, readonly struct",
            "struct для маленьких immutable данных, class для всего остального"
        ],
        "estimated_minutes": 35,
        "language_slug": "csharp",
        "lesson_order": 12,
        "name_en": "Lesson: C# Type System Deep Dive",
        "short_description_en": "Value/reference types, nullable, boxing/unboxing, records, immutability"
    },
    # ... continue for other lessons
}

# I'll create the rest of the lessons similarly
# Let me create a comprehensive generator