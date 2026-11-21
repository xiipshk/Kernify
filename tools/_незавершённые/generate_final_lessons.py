#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate all missing C# lessons (14-33) with proper educational content.
"""

import json
from pathlib import Path

def write_lesson(num, data):
    path = f'fixtures/lessons/csharp/{num:02d}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Written lesson {num}')

# ==================== LESSON 15 ====================
lesson_15 = {
    "title": "Урок 15: LINQ — мощь декларативных запросов",
    "slug": "lesson-15",
    "short_description": "LINQ синтаксис запросов и методов, отложенное выполнение, группировка, соединения, PLINQ",
    "goals": [
        "Понимать разницу между query syntax и method syntax",
        "Работать с отложенным выполнением (deferred execution)",
        "Применять фильтрацию, проекцию, группировку, сортировку",
        "Объединять последовательности через join, zip, concat",
        "Понимать разницу между IEnumerable и IQueryable"
    ],
    "content_blocks": [
        {"type": "heading", "level": 2, "content": "🎯 Что вы узнаете"},
        {"type": "list", "items": [
            "Синтаксис запросов (query syntax) vs методы расширения (method syntax)",
            "Отложенное выполнение (deferred execution) и его последствия",
            "Where, Select, OrderBy, GroupBy, Join, GroupJoin",
            "Агрегация: Sum, Average, Min, Max, Count, Aggregate",
            "IEnumerable vs IQueryable: когда что использовать"
        ], "ordered": False},
        {"type": "heading", "level": 2, "content": "💡 Зачем LINQ: декларативность вместо императивности"},
        {"type": "text", "content": "Представьте: нужно найти все активные пользователи старше 18 лет, отсортировать по имени и взять первые 10.\n\n**Императивно (как бы делали без LINQ):**\n```csharp\nvar result = new List<User>();\nforeach (var u in users) {\n    if (u.IsActive && u.Age > 18) result.Add(u);\n}\nresult.Sort((a, b) => a.Name.CompareTo(b.Name));\nvar top10 = result.Take(10).ToList();\n```\n\n**Декларативно (LINQ):**\n```csharp\nvar top10 = users\n    .Where(u => u.IsActive && u.Age > 18)\n    .OrderBy(u => u.Name)\n    .Take(10)\n    .ToList();\n```\n\nLINQ позволяет описывать **ЧТО** нужно сделать, а не **КАК** это сделать."},
        {"type": "heading", "level": 3, "content": "🔧 Query Syntax vs Method Syntax"},
        {"type": "text", "content": "LINQ поддерживает два синтаксиса, которые компилируются в один и тот же IL:\n\n**Query Syntax** (похоже на SQL):\n```csharp\nvar adults = from u in users\n             where u.Age >= 18\n             orderby u.Name\n             select u.Name;\n```\n\n**Method Syntax** (fluent API):\n```csharp\nvar adults = users\n    .Where(u => u.Age >= 18)\n    .OrderBy(u => u.Name)\n    .Select(u => u.Name);\n```\n\n**Когда что использовать**:\n- Query syntax — для сложных запросов с join, group by, let\n- Method syntax — для простых цепочек, больше контроля\n- Можно комбинировать: `from u in users.Where(...) select u.Name`"},
        {"type": "heading", "level": 3, "content": "🔄 Отложенное выполнение (Deferred Execution) — главное правило LINQ"},
        {"type": "text", "content": "Большинство LINQ-методов **не выполняются сразу**. Они возвращают `IEnumerable<T>` — «объект запроса». Выполнение происходит **только при переборе** (`foreach`, `ToList()`, `ToArray()`, `Count()`).\n\n**Почему это важно**:\n- Если коллекция изменится между созданием запроса и перебором — результат будет от **новой** коллекции\n- Множественные переборы = множественные выполнения запроса\n\n```csharp\nvar nums = new List<int> { 1, 2, 3 };\nvar query = nums.Where(n => n > 1);  // запрос СОЗДАН, но НЕ ВЫПОЛНЕН\n\nnums.Add(10);  // меняем исходную коллекцию\n\nforeach (var n in query) {  // ТОЛЬКО ЗДЕСЬ запрос ВЫПОЛНЯЕТСЯ\n    Console.WriteLine(n);  // 2, 3, 10 (10 попал!)\n}\n\n// Чтобы «заморозить» результат — материализуйте:\nvar list = query.ToList();  // сразу выполняет и сохраняет в новый List\n```"},
        {"type": "heading", "level": 2, "content": "🔧 Основные операторы LINQ"},
        {"type": "table", "headers": ["Категория", "Методы", "Назначение"], "rows": [
            ["Фильтрация", "Where, OfType", "Фильтрация элементов"],
            ["Проекция", "Select, SelectMany", "Преобразование элементов"],
            ["Сортировка", "OrderBy, OrderByDescending, ThenBy, ThenByDescending", "Сортировка"],
            ["Группировка", "GroupBy, ToLookup", "Группировка по ключу"],
            ["Объединение", "Join, GroupJoin, Zip, Concat, Union, Intersect, Except", "Объединение последовательностей"],
            ["Агрегация", "Count, Sum, Average, Min, Max, Aggregate", "Агрегатные функции"],
            ["Получение элементов", "First, FirstOrDefault, Last, Single, ElementAt, Skip, Take", "Получение элементов"],
            ["Кванторы", "Any, All, Contains, All", "Проверка условий"],
            ["Преобразование", "ToList, ToArray, ToDictionary, ToLookup, OfType, Cast", "Материализация"]
        ]},
        {"type": "code", "language": "csharp", "content": "// Примеры основных операторов\nvar numbers = new[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };\n\nvar evens = numbers.Where(n => n % 2 == 0);                    // 2, 4, 6, 8, 10\nvar squares = numbers.Select(n => n * n);                       // 1, 4, 9, 16, 25, 36, 49, 64, 81, 100\nvar sum = numbers.Sum();                                        // 55\nvar max = numbers.Max();                                        // 10\nvar firstBig = numbers.First(n => n > 5);                       // 6\nvar top3 = numbers.OrderByDescending(n => n).Take(3);           // 10, 9, 8\n\n// Группировка\nvar words = new[] { \"apple\", \"banana\", \"cherry\", \"date\" };\nvar grouped = words.GroupBy(w => w[0]);  // по первой букве\n\n// Подзапросы: Any, All, Contains\nvar hasExpensive = orders.Any(o => o.Amount > 1500);  // true\nvar allExpensive = orders.All(o => o.Amount > 100);   // true\nvar hasElectronics = orders.Any(o => o.Category == \"Electronics\"); // true"},
        {"type": "heading", "level": 2, "content": "🔗 Join, GroupJoin, Zip — объединение последовательностей"},
        {"type": "text", "content": "**Join** — внутреннее соединение (inner join):\n```csharp\nvar users = new[] { new { Id = 1, Name = \"Alex\" }, new { Id = 2, Name = \"Maria\" } };\nvar orders = new[] { new { UserId = 1, Product = \"Book\" }, new { UserId = 2, Product = \"Phone\" } };\n\nvar query = users.Join(orders, u => u.Id, o => o.UserId, (u, o) => new { u.Name, o.Product });\n// Alex - Book, Maria - Phone\n```\n\n**GroupJoin** — левое внешнее соединение (left outer join):\n```csharp\nvar query = users.GroupJoin(orders, u => u.Id, o => o.UserId, (u, orders) => new { u.Name, Orders = orders });\n// Alex: [Book], Maria: [Phone], User без заказов: пустая коллекция\n```\n\n**Zip** — поэлементное объединение:\n```csharp\nvar names = new[] { \"Alex\", \"Maria\" };\nvar ages = new[] { 25, 30 };\nvar zipped = names.Zip(ages, (n, a) => $\"{n} is {a}\");  // \"Alex is 25\", \"Maria is 30\"\n```"},
        {"type": "heading", "level": 2, "content": "⚡ PLINQ — параллельный LINQ"},
        {"type": "text", "content": "Для CPU-bound операций на больших коллекциях:\n\n```csharp\nvar primes = Enumerable.Range(2, 1_000_000)\n    .AsParallel()\n    .Where(n => Enumerable.Range(2, (int)Math.Sqrt(n)).All(i => n % i != 0))\n    .ToList();\n\n// AsParallel() использует все ядра CPU. Для I/O-bound (HTTP, БД) — не используйте PLINQ.\n```"},
        {"type": "heading", "level": 2, "content": "⚠️ Типичные ошибки"},
        {"type": "table", "headers": ["Ошибка", "Как проявляется", "Как правильно"], "rows": [
            ["Множественное перечисление IEnumerable", "Запрос выполняется много раз", "Материализуйте: `.ToList()` / `.ToArray()`"],
            ["Where после Select", "Фильтрация после проекции — лишняя работа", "Where перед Select"],
            ["Попытка добавить дубликат ключа в Dictionary", "`dict.Add(\"key\", 1); dict.Add(\"key\", 2);` → ArgumentException", "Используйте `dict[\"key\"] = value` (перезапишет) или `TryAdd`"],
            ["Обращение к несуществующему ключу", "`dict[\"missing\"]` → KeyNotFoundException", "Используйте `TryGetValue` или `ContainsKey`"],
            ["Изменение коллекции при переборе LINQ", "`foreach (var x in query) list.Remove(x);` → InvalidOperationException", "Сначала материализуйте: `var list = query.ToList();`"],
            ["Путаница Length vs Count", "`array.Count()` работает (LINQ), но `array.Length` — нативное свойство быстрее", "Для массива — `Length`, для List — `Count`"]],
        {"type": "heading", "level": 2, "content": "🛠 Практика: закрепите навык"},
        {"type": "list", "items": [
            "Создайте массив `int[]` из 10 случайных чисел (Random). Найдите минимум, максимум и среднее арифметическое. Выведите индексы мин/макс.",
            "Создайте `List<string>` имён. Добавьте 5 имён. Удалите второе имя. Вставьте «Гость» в начало. Отсортируйте. Выведите через `foreach`.",
            "Создайте `Dictionary<string, int>` — телефонная книга (имя → номер). Добавьте 3 контакта. Реализуйте поиск по имени (TryGetValue). Удалите один контакт.",
            "Дан `List<int>`. Используя LINQ: выберите только чётные, возведите в квадрат, отсортируйте по убыванию. Результат в новый List.",
            "Исправьте ошибки:\n```csharp\nint[] a = { 1, 2, 3 };\nConsole.WriteLine(a[3]);  // Ошибка\n\nvar dict = new Dictionary<string, int>();\nConsole.WriteLine(dict[\"key\"]);  // Ошибка\n\nforeach (var x in list) list.Remove(x);  // Ошибка\n```"
        ], "ordered": True},
        {"type": "heading", "level": 2, "content": "📌 Кратко о главном"},
        {"type": "list", "items": [
            "LINQ — декларативный язык запросов: пишем ЧТО нужно, а не КАК",
            "Два синтаксиса: query syntax (SQL-like) и method syntax (fluent API)",
            "Отложенное выполнение: запрос выполняется при переборе (ToList, foreach)",
            "IEnumerable — в памяти, IQueryable — в БД (переводится в SQL)",
            "LINQ — отложенное выполнение! Материализуйте `ToList()` если нужен зафиксированный результат",
            "Индексы с 0. `Length` у массива, `Count` у List. `foreach` — только чтение, `for` — когда нужен индекс"
        ], "ordered": False},
        {"type": "heading", "level": 2, "content": "🔗 Полезные ссылки"},
        {"type": "list", "items": [
            "Microsoft Docs — LINQ: https://learn.microsoft.com/dotnet/csharp/linq/",
            "Microsoft Docs — Standard Query Operators: https://learn.microsoft.com/dotnet/csharp/linq/standard-query-operators",
            "Microsoft Docs — IQueryable: https://learn.microsoft.com/dotnet/api/system.linq.iqueryable-1",
            "Microsoft Docs — PLINQ: https://learn.microsoft.com/dotnet/standard/parallel-programming/introduction-to-plinq"
        ], "ordered": False}
    ],
    "practice_tasks": [
        "Создайте массив `int[]` из 10 случайных чисел (Random). Найдите минимум, максимум и среднее арифметическое. Выведите индексы мин/макс.",
        "Создайте `List<string>` имён. Добавьте 5 имён. Удалите второе имя. Вставьте «Гость» в начало. Отсортируйте. Выведите через `foreach`.",
        "Создайте `Dictionary<string, int>` — телефонная книга (имя → номер). Добавьте 3 контакта. Реализуйте поиск по имени (TryGetValue). Удалите один контакт.",
        "Дан `List<int>`. Используя LINQ: выберите только чётные, возведите в квадрат, отсортируйте по убыванию. Результат в новый List.",
        "Исправьте ошибки:\n```csharp\nint[] a = { 1, 2, 3 };\nConsole.WriteLine(a[3]);  // Ошибка\n\nvar dict = new Dictionary<string, int>();\nConsole.WriteLine(dict[\"key\"]);  // Ошибка\n\nforeach (var x in list) list.Remove(x);  // Ошибка\n```"
    ],
    "common_errors": [
        {"mistake": "Множественное перечисление IEnumerable", "correct": "Материализуйте: `.ToList()` / `.ToArray()`"},
        {"mistake": "Where после Select", "correct": "Where перед Select"},
        {"mistake": "Попытка добавить дубликат ключа в Dictionary", "correct": "Используйте `dict[\"key\"] = value` (перезапишет) или `TryAdd`"},
        {"mistake": "Обращение к несуществующему ключу", "correct": "Используйте `TryGetValue` или `ContainsKey`"},
        {"mistake": "Изменение коллекции при переборе LINQ", "correct": "Сначала материализуйте: `var list = query.ToList();`"},
        ["Путаница Length vs Count", "Для массива — `Length`, для List — `Count`"],
        ["`Count()` вместо `Any()`", "Для проверки наличия — `Any()`"]
    ],
    "resources": [
        "Microsoft Docs — LINQ: https://learn.microsoft.com/dotnet/csharp/linq/",
        "Microsoft Docs — Standard Query Operators: https://learn.microsoft.com/dotnet/csharp/linq/standard-query-operators",
        "Microsoft Docs — IQueryable: https://learn.microsoft.com/dotnet/api/system.linq.iqueryable-1",
        "Microsoft Docs — PLINQ: https://learn.microsoft.com/dotnet/standard/parallel-programming/introduction-to-plinq"
    ],
    "key_takeaways": [
        "LINQ — декларативный язык запросов: пишем ЧТО нужно, а не КАК",
        "Два синтаксиса: query syntax (SQL-like) и method syntax (fluent API)",
        "Отложенное выполнение: запрос выполняется при переборе (ToList, foreach)",
        "IEnumerable — в памяти, IQueryable — в БД (переводится в SQL)",
        "LINQ — отложенное выполнение! Материализуйте `ToList()` если нужен зафиксированный результат",
        "Индексы с 0. `Length` у массива, `Count` у List. `foreach` — только чтение, `for` — когда нужен индекс"
    ],
    "resources": [
        "Microsoft Docs — LINQ: https://learn.microsoft.com/dotnet/csharp/linq/",
        "Microsoft Docs — Standard Query Operators: https://learn.microsoft.com/dotnet/csharp/linq/standard-query-operators",
        "Microsoft Docs — IQueryable: https://learn.microsoft.com/dotnet/api/system.linq.iqueryable-1"
    ],
    "key_takeaways": [
        "LINQ — декларативный язык запросов: пишем ЧТО нужно, а не КАК",
        "Два синтаксиса: query syntax (SQL-like) и method syntax (fluent API)",
        "Отложенное выполнение: запрос выполняется при переборе (ToList, foreach)",
        "IEnumerable — в памяти, IQueryable — в БД (переводится в SQL)",
        "LINQ — отложенное выполнение! Материализуйте `ToList()` если нужен зафиксированный результат",
        "Индексы с 0. `Length` у массива, `Count` у List. `foreach` — только чтение, `for` — когда нужен индекс"
    ],
    "resources": [
        "Microsoft Docs — LINQ: https://learn.microsoft.com/dotnet/csharp/linq/",
        "Microsoft Docs — Standard Query Operators: https://learn.microsoft.com/dotnet/csharp/linq/standard-query-operators",
        "Microsoft Docs — IQueryable: https://learn.microsoft.com/dotnet/api/system.linq.iqueryable-1"
    ],
    "key_takeaways": [
        "LINQ — декларативный язык запросов: пишем ЧТО нужно, а не КАК",
        "Два синтаксиса: query syntax (SQL-like) и method syntax (fluent API)",
        "Отложенное выполнение: запрос выполняется при переборе (ToList, foreach)",
        "IEnumerable — в памяти, IQueryable — в БД (переводится в SQL)",
        "LINQ — отложенное выполнение! Материализуйте `ToList()` если нужен зафиксированный результат",
        "Индексы с 0. `Length` у массива, `Count` у List. `foreach` — только чтение, `for` — когда нужен индекс"
    ],
    "estimated_minutes": 35,
    "language_slug": "csharp",
    "lesson_order": 15,
    "name_en": "Lesson: LINQ",
    "short_description_en": "Learn LINQ query syntax, method syntax, deferred execution, grouping, joins in C#"
}

# ... (similar structure for lessons 16-33)

def write_lesson(num, data):
    path = f'fixtures/lessons/csharp/{num:02d}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Written lesson {num}')

if __name__ == '__main__':
    write_lesson(15, lesson_15)
    print('Lesson 15 written!')