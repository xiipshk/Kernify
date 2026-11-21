#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enhance lessons 15-33 with more detailed explanations."""

import json
import re
from pathlib import Path

# ============================================================
# MARKDOWN PROCESSING FUNCTIONS (copied from gen script)
# ============================================================

def extract_code_blocks(text):
    code_blocks = []
    placeholders = {}
    
    def protect_code(match):
        idx = len(code_blocks)
        lang = match.group(1) or 'csharp'
        code = match.group(2).rstrip()
        code_blocks.append({'type': 'code', 'language': lang, 'content': code})
        placeholder = f"{{{{CODE_BLOCK_{idx}}}}}"
        placeholders[placeholder] = idx
        return placeholder
    
    text = re.sub(r'```(\w*)\n(.*?)\n```', protect_code, text, flags=re.DOTALL)
    return text, code_blocks, placeholders


def markdown_to_html(text):
    if not text:
        return ""
    
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    text = re.sub(r'^\- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\n\1</ul>', text)
    text = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n)+', r'<ol>\n\1</ol>', text)
    
    def table_repl(match):
        lines = match.group(0).strip().split('\n')
        if len(lines) < 2:
            return match.group(0)
        headers = [h.strip() for h in lines[0].split('|') if h.strip()]
        rows = []
        for line in lines[2:]:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells:
                rows.append(cells)
        html = '<table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead><tbody>'
        for row in rows:
            html += '<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>'
        html += '</tbody></table>'
        return html
    text = re.sub(r'\|.*\|(\n\|[-:]+\|)+\n(\|.*\|\n?)+', table_repl, text)
    
    text = re.sub(r'\n\n+', '</p>\n<p>', text)
    text = '<p>' + text + '</p>'
    text = re.sub(r'<p>\s*</p>', '', text)
    text = re.sub(r'<p>(<h[1-6]>)', r'\1', text)
    text = re.sub(r'</h([1-6])></p>', r'</h\1>', text)
    text = re.sub(r'<p>(<ul>)', r'\1', text)
    text = re.sub(r'</ul></p>', r'</ul>', text)
    text = re.sub(r'<p>(<ol>)', r'\1', text)
    text = re.sub(r'</ol></p>', r'</ol>', text)
    text = re.sub(r'<p>(<table>)', r'\1', text)
    text = re.sub(r'</table></p>', r'</table>', text)
    
    return text


def process_markdown(md):
    text, code_blocks, placeholders = extract_code_blocks(md)
    html = markdown_to_html(text)
    
    for ph, idx in placeholders.items():
        html = html.replace(ph, f"[[CODE_BLOCK_{idx}]]")
    
    blocks = []
    parts = re.split(r'(<h[1-6]>.*?</h[1-6]>|<ul>.*?</ul>|<ol>.*?</ol>|<table>.*?</table>|<p>.*?</p>)', html, flags=re.DOTALL)
    
    def extract_code_markers(part):
        extracted = []
        remaining = part
        while True:
            m = re.search(r'\[\[CODE_BLOCK_(\d+)\]\]', remaining)
            if not m:
                break
            idx = int(m.group(1))
            extracted.append(code_blocks[idx])
            remaining = remaining[:m.start()] + remaining[m.end():]
        return extracted, remaining.strip()
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        code_markers, remaining = extract_code_markers(part)
        for cb in code_markers:
            blocks.append(cb)
        
        if not remaining:
            continue
        
        if remaining.startswith('<h'):
            level = int(remaining[2])
            content = re.sub(r'<h\d>(.*?)</h\d>', r'\1', remaining, flags=re.DOTALL)
            blocks.append({'type': 'heading', 'level': level, 'content': content.strip()})
        elif remaining.startswith('<ul>') or remaining.startswith('<ol>'):
            items = re.findall(r'<li>(.*?)</li>', remaining, flags=re.DOTALL)
            blocks.append({'type': 'list', 'items': [re.sub(r'<[^>]+>', '', i).strip() for i in items], 'ordered': remaining.startswith('<ol>')})
        elif remaining.startswith('<table>'):
            headers = re.findall(r'<th>(.*?)</th>', remaining)
            rows = []
            for tr in re.findall(r'<tr>(.*?)</tr>', remaining, flags=re.DOTALL):
                cells = re.findall(r'<td>(.*?)</td>', tr)
                if cells:
                    rows.append(cells)
            if headers:
                blocks.append({'type': 'table', 'headers': headers, 'rows': rows})
        elif remaining.startswith('<p>'):
            content = re.sub(r'<p>(.*?)</p>', r'\1', remaining, flags=re.DOTALL)
            content = re.sub(r'<[^>]+>', '', content).strip()
            if content:
                blocks.append({'type': 'text', 'content': content})
        elif remaining:
            content = re.sub(r'<[^>]+>', '', remaining).strip()
            if content:
                blocks.append({'type': 'text', 'content': content})
    
    return blocks

LESSON_ENHANCEMENTS = {}

# ============================================================
# LESSON 15: LINQ - DEEPENED
# ============================================================
LESSON_ENHANCEMENTS[15] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в LINQ: как это работает под капотом

### Query Syntax vs Method Syntax — детали компиляции

**Query Syntax** — это синтаксический сахар. Компилятор транслирует его в вызовы методов расширения (Method Syntax) перед генерацией IL.

```csharp
// Query Syntax
var query = from u in users
            where u.Age >= 18
            orderby u.Name
            select u.Name;

// Компилятор превращает в:
var query = users
    .Where(u => u.Age >= 18)
    .OrderBy(u => u.Name)
    .Select(u => u.Name);
```

**Важно**: Query Syntax не поддерживает все операторы (например, `Take`, `Skip`, `FirstOrDefault` с предикатом). Для них нужно комбинировать синтаксисы:

```csharp
// Комбинированный подход
var adults = (from u in users
              where u.Age >= 18
              select u)
             .Take(10)
             .ToList();
```

### 🔄 Отложенное выполнение (Deferred Execution) — механизм

LINQ использует **итераторы** (yield return) для реализации отложенного выполнения.

```csharp
// Упрощённая реализация Where внутри .NET
public static IEnumerable<T> Where<T>(this IEnumerable<T> source, Func<T, bool> predicate) {
    foreach (var item in source) {
        if (predicate(item)) yield return item; // Возвращает управление вызывающему коду
    }
}
```

**Последствия отложенного выполнения**:

```csharp
var nums = new List<int> { 1, 2, 3 };
var query = nums.Where(n => n > 1);  // Переменная query — это IEnumerable<int>, запрос НЕ выполнен

nums.Add(10);  // Изменяем исходную коллекцию ПОСЛЕ создания запроса

// Выполнение происходит ТОЛЬКО здесь:
foreach (var n in query) Console.WriteLine(n);  // Вывод: 2, 3, 10!

// Для немедленного выполнения используйте материализацию:
var list = query.ToList();  // Выполняет запрос СРАЗУ, сохраняет в новый List
var array = query.ToArray();  // То же самое, но в массив
var count = query.Count();  // Выполняет запрос для подсчёта
```

### 📊 Streaming vs Buffering операторы

| Категория | Операторы | Поведение | Память |
|---|---|---|---|
| **Streaming (ленивые)** | Where, Select, SelectMany | Обрабатывают по одному элементу | O(1) |
| **Buffering (жадные)** | OrderBy, GroupBy, Reverse, Distinct | Читают всю последовательность в память | O(n) |

```csharp
// Streaming: элементы передаются дальше сразу
var streaming = hugeCollection
    .Where(x => x.Active)
    .Select(x => x.Name);  // Память O(1)

// Buffering: нужен весь список для сортировки
var buffered = hugeCollection
    .OrderBy(x => x.Date)  // Читает ВСЁ в память!
    .Take(10);  // Только потом берёт первые 10
```

**Оптимизация**: ставьте `Where` ДО `OrderBy`!

```csharp
// ПЛОХО: сначала сортируем всё, потом фильтруем
var bad = hugeCollection.OrderBy(x => x.Date).Where(x => x.Active).Take(10);

// ХОРОШО: сначала фильтруем (streaming), потом сортируем малое количество
var good = hugeCollection.Where(x => x.Active).OrderBy(x => x.Date).Take(10);
```

### 🔗 Join vs GroupJoin — подробности

**Join (Inner Join)** — возвращает только пары с совпадением:

```csharp
var query = users.Join(orders,
    u => u.Id,        // outer key selector
    o => o.UserId,    // inner key selector
    (u, o) => new { u.Name, o.Amount });  // result selector

// Эквивалент SQL:
// SELECT u.Name, o.Amount FROM Users u INNER JOIN Orders o ON u.Id = o.UserId
```

**GroupJoin (Left Outer Join)** — сохраняет все левые элементы:

```csharp
var query = users.GroupJoin(orders,
    u => u.Id,
    o => o.UserId,
    (u, userOrders) => new { u.Name, Orders = userOrders });

// Результат для пользователя без заказов: { Name: "Bob", Orders: [] }
// Эквивалент SQL LEFT JOIN
```

**Zip** — поэлементное объединение (последовательности должны быть равной длины или Zip обрежет до меньшей):

```csharp
var names = new[] { "Alex", "Maria", "John" };
var ages = new[] { 25, 30 };
var zipped = names.Zip(ages, (n, a) => $"{n} ({a})");
// Результат: "Alex (25)", "Maria (30)" — John отброшен!
```

### ⚡ PLINQ — когда и как использовать

PLINQ (`AsParallel()`) параллелизирует выполнение запроса на несколько потоков.

```csharp
// CPU-bound работа — хорошо для PLINQ
var primes = Enumerable.Range(2, 1_000_000)
    .AsParallel()
    .Where(n => IsPrime(n))
    .ToList();

// Настройки параллелизма
var result = data.AsParallel()
    .WithDegreeOfParallelism(4)           // Макс 4 потока
    .WithExecutionMode(ParallelExecutionMode.ForceParallelism)  // Принудительно
    .WithMergeOptions(ParallelMergeOptions.NotBuffered)  // Streaming
    .Where(x => ExpensiveCheck(x))
    .ToList();
```

**Когда НЕ использовать PLINQ**:
- I/O-bound операции (HTTP, БД, файлы) — используйте `async/await` + `Task.WhenAll`
- Маленькие коллекции (накладные расходы > выгода)
- Запросы с побочными эффектами (не thread-safe)

### 🎯 IQueryable vs IEnumerable — провайдеры запросов

```csharp
// IEnumerable<T> — LINQ to Objects (выполняется в памяти)
IEnumerable<User> usersInMemory = GetUsers();
var filtered = usersInMemory.Where(u => u.Age > 18);  // Func<User, bool>

// IQueryable<T> — LINQ to SQL/EF Core (переводится в SQL)
IQueryable<User> usersInDb = dbContext.Users;
var filteredDb = usersInDb.Where(u => u.Age > 18);  // Expression<Func<User, bool>>

// Разница в сигнатуре:
// IEnumerable: Where(Func<T, bool>)
// IQueryable: Where(Expression<Func<T, bool>>)
```

**Expression Tree** — это дерево выражений, которое EF Core может проанализировать и перевести в SQL:

```csharp
// Это компилируется в Expression Tree, а не в делегат:
Expression<Func<User, bool>> predicate = u => u.Age > 18 && u.IsActive;

// EF Core анализирует дерево и генерирует:
// SELECT * FROM Users WHERE Age > 18 AND IsActive = 1

// Если передать Func — EF Core загрузит ВСЮ таблицу в память и отфильтрует там!
var bad = db.Users.Where(u => SomeComplexMethod(u));  // Func — клиентская фильтрация
var good = db.Users.Where(u => u.Age > 18);  // Expression — серверная фильтрация
```

### 🧠 Замыкания в LINQ — типичная ловушка

```csharp
// ПРОБЛЕМА: замыкание на переменной цикла
var queries = new List<Func<int, bool>>();
for (int i = 0; i < 10; i++) {
    queries.Add(x => x > i);  // Все замыкаются на ОДНОЙ переменной i!
}
// В конце цикла i = 10, все функции проверяют x > 10

// РЕШЕНИЕ: создавайте локальную копию
var queries = new List<Func<int, bool>>();
for (int i = 0; i < 10; i++) {
    int local = i;  // Копия для каждой итерации
    queries.Add(x => x > local);
}
```

### 📝 Практические паттерны LINQ

**Batch Processing (пакетная обработка)**:
```csharp
public static IEnumerable<IEnumerable<T>> Batch<T>(this IEnumerable<T> source, int size) {
    using var enumerator = source.GetEnumerator();
    while (enumerator.MoveNext()) {
        yield return YieldBatch(enumerator, size).ToList();
    }
}

IEnumerable<T> YieldBatch<T>(IEnumerator<T> enumerator, int size) {
    yield return enumerator.Current;
    for (int i = 1; i < size && enumerator.MoveNext(); i++) {
        yield return enumerator.Current;
    }
}

// Использование
foreach (var batch in hugeList.Batch(1000)) {
    await ProcessBatchAsync(batch);
}
```

**DistinctBy (до .NET 6)**:
```csharp
// .NET 6+: source.DistinctBy(x => x.Key)
// До .NET 6:
var distinct = source
    .GroupBy(x => x.Key)
    .Select(g => g.First());
```

**Pagination с Seek (Keyset Pagination)** — эффективнее OFFSET:
```csharp
// OFFSET pagination (медленно на больших страницах)
var page = query.Skip((pageNum - 1) * pageSize).Take(pageSize);

// Keyset Pagination (быстро, использует индекс)
var page = query
    .Where(x => x.Id > lastSeenId)  // Seek по индексу
    .OrderBy(x => x.Id)
    .Take(pageSize);
```

### 📌 Чек-лист производительности LINQ

- [ ] `Where` перед `OrderBy` / `Select`
- [ ] `Select` только нужные колонки (особенно в EF Core)
- [ ] `AsNoTracking()` для read-only запросов в EF Core
- [ ] Избегайте `ToList()` в середине цепочки — ломает streaming
- [ ] Используйте `Any()` вместо `Count() > 0` для проверки существования
- [ ] `FirstOrDefault(predicate)` вместо `Where(predicate).FirstOrDefault()`
- [ ] Для пагинации — Keyset Pagination вместо OFFSET
- [ ] PLINQ только для CPU-bound на больших коллекциях
"""
}

# ============================================================
# LESSON 16: Collections - DEEPENED
# ============================================================
LESSON_ENHANCEMENTS[16] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в коллекции: внутреннее устройство и производительность

### 📦 List<T> — динамический массив

**Внутреннее устройство**: `List<T>` — обёртка над массивом `T[]` с автоматическим расширением.

```csharp
// Упрощённая логика Add
public void Add(T item) {
    if (_size == _items.Length) {
        // Удвоение capacity (amortized O(1))
        int newCapacity = _items.Length == 0 ? 4 : _items.Length * 2;
        Array.Resize(ref _items, newCapacity);
    }
    _items[_size++] = item;
}
```

**Capacity vs Count**:
- `Count` — количество элементов
- `Capacity` — выделенная память (всегда >= Count)
- При `Add` при превышении Capacity происходит реаллокация и копирование

```csharp
var list = new List<int>();
list.Capacity;  // 0
list.Add(1);    // Capacity = 4
list.Add(2);    // Capacity = 4
list.Add(3);    // Capacity = 4
list.Add(4);    // Capacity = 4
list.Add(5);    // Capacity = 8 (реаллокация!)

// Оптимизация: заранее известный размер
var list = new List<int>(10000);  // Capacity = 10000 сразу, никаких реаллокаций
```

**Insert/RemoveAt — O(n)**:
```csharp
// Insert в начало — сдвиг ВСЕХ элементов
list.Insert(0, value);  // O(n) — копирует n элементов

// RemoveAt — тоже O(n)
list.RemoveAt(0);  // O(n)

// Для частых вставок/удалений в начале — LinkedList или Queue
```

### 🗝 Dictionary<TKey, TValue> — хеш-таблица

**Внутреннее устройство**: массив "корзин" (buckets) + цепочки для разрешения коллизий.

```csharp
// Упрощённый алгоритм Get
public bool TryGetValue(TKey key, out TValue value) {
    int hash = key.GetHashCode() & 0x7FFFFFFF;  // Убираем знак
    int bucket = hash % _buckets.Length;
    
    for (int i = _buckets[bucket]; i >= 0; i = _entries[i].Next) {
        if (_entries[i].HashCode == hash && EqualityComparer<TKey>.Default.Equals(_entries[i].Key, key)) {
            value = _entries[i].Value;
            return true;
        }
    }
    value = default;
    return false;
}
```

**Важность GetHashCode() и Equals()**:

```csharp
// ПЛОХО: mutable ключ
var dict = new Dictionary<List<int>, string>();
var key = new List<int> { 1, 2 };
dict[key] = "value";
key.Add(3);  // Хеш изменился! Элемент "потерян" в словарь
dict[key];   // KeyNotFoundException

// ХОРОШО: immutable ключ (record, struct, string)
var dict = new Dictionary<Point, string>();  // Point — record struct
dict[new Point(1, 2)] = "value";  // Безопасно
```

**Load Factor и реаллокация**:
- Dictionary расширяется при достижении Load Factor (~75%)
- При реаллокации все элементы перехешируются — дорого!

```csharp
// Оптимизация: задайте Capacity заранее
var dict = new Dictionary<int, string>(10000);  // Избегает множественных реаллокаций
```

### 🔢 HashSet<T> — множество

**Основа**: та же хеш-таблица, что и Dictionary, но без Value.

```csharp
// Операции над множествами — O(n) где n — размер меньшего множества
var set1 = new HashSet<int> { 1, 2, 3, 4, 5 };
var set2 = new HashSet<int> { 4, 5, 6, 7 };

set1.UnionWith(set2);        // {1,2,3,4,5,6,7}
set1.IntersectWith(set2);    // {4,5}
set1.ExceptWith(set2);       // {1,2,3}
set1.SymmetricExceptWith(set2); // {1,2,3,6,7}
set1.IsSubsetOf(set2);       // false
set1.IsSupersetOf(set2);     // false
set1.Overlaps(set2);         // true
```

### 📋 Queue<T> и Stack<T>

**Queue<T>** — кольцевой буфер (circular buffer):

```csharp
// Внутренне: массив + head + tail индексы
// Enqueue — O(1) амортизированное
// Dequeue — O(1)

// Не используйте Queue для случайного доступа — только FIFO
```

**Stack<T>** — массив с указателем на вершину:

```csharp
// Push/Pop — O(1) амортизированное
// Идеален для: DFS, парсинг выражений, Undo/Redo
```

### 🔗 LinkedList<T> — двусвязный список

```csharp
// Когда использовать:
// - Частые Insert/Remove в СЕРЕДИНЕ (O(1) если есть узел)
// - Не нужен доступ по индексу
// - Нужно перемещать узлы между списками

var list = new LinkedList<int>();
list.AddLast(1);
var node = list.AddLast(2);
list.AddBefore(node, 0);  // O(1)
list.AddAfter(node, 3);   // O(1)
list.Remove(node);        // O(1)

// НЕ используйте для:
// - Случайного доступа (нет индексатора)
// - Малых данных (накладные расходы на узлы)
```

### ❄️ Immutable Collections — структуральное разделение

**Ключевая идея**: при изменении создаётся НОВАЯ коллекция, общая память со старой.

```csharp
using System.Collections.Immutable;

var list = ImmutableList.Create(1, 2, 3);
var list2 = list.Add(4);        // Новый список, старый неизменён
var list3 = list2.RemoveAt(0);  // Ещё один новый

// Память: общие узлы между list, list2, list3
// Сложность: O(log n) для Add/Remove (дерево с ветвлением 32)
```

**Производительность**:
| Операция | List<T> | ImmutableList<T> |
|---|---|---|
| Add в конец | O(1) амортиз. | O(log n) |
| Insert в середину | O(n) | O(log n) |
| Поиск по индексу | O(1) | O(log n) |
| Память при изменениях | O(n) копия | O(log n) новые узлы |

**Builder Pattern** для пакетных изменений:

```csharp
// ПЛОХО: много аллокаций
var immutable = ImmutableList.Create<int>();
for (int i = 0; i < 100000; i++) {
    immutable = immutable.Add(i);  // 100000 аллокаций!
}

// ХОРОШО: используйте Builder
var builder = ImmutableList.CreateBuilder<int>();
for (int i = 0; i < 100000; i++) {
    builder.Add(i);  // Мутирует внутренний массив
}
var immutable = builder.ToImmutable();  // Одно создание immutable структуры
```

### 🎯 Span<T>, Memory<T> — работа без аллокаций

**Span<T>** — ref struct (только стек), не может быть полем класса, не может быть в async:

```csharp
// Нулевые аллокации для срезов
ReadOnlySpan<char> span = "Hello World".AsSpan();
var slice = span.Slice(6, 5);  // "World" — НИКАКИХ АЛЛОКАЦИЙ!

// Парсинг без Substring
public static bool TryParseInt(ReadOnlySpan<char> span, out int value) {
    value = 0;
    foreach (var c in span) {
        if (c < '0' || c > '9') return false;
        value = value * 10 + (c - '0');
    }
    return true;
}
```

**Memory<T>** — может быть на куче, для async:

```csharp
Memory<byte> buffer = new byte[4096];
await stream.ReadAsync(buffer);  // Читает прямо в буфер, без копирования

// Memory<T> можно преобразовать в Span
Span<byte> span = buffer.Span;
```

**stackalloc** — стек для малых буферов:

```csharp
// Только для малых размеров (< ~1KB)
Span<byte> buffer = stackalloc byte[256];

// Для больших — ArrayPool
byte[] buffer = ArrayPool<byte>.Shared.Rent(65536);
try { /* работа */ } finally { ArrayPool<byte>.Shared.Return(buffer); }
```

### ⚡ Concurrent Collections — потокобезопасность

```csharp
using System.Collections.Concurrent;

// ConcurrentDictionary — тонкая блокировка (lock striping)
var dict = new ConcurrentDictionary<string, int>();
dict.GetOrAdd("key", k => ExpensiveCompute(k));  // Атомарно: Compute + Add
dict.TryUpdate("key", 42, 41);  // CAS: если 41, то ставим 42

// ConcurrentBag — неупорядоченная, для producer/consumer
var bag = new ConcurrentBag<int>();
bag.Add(1);  // Потокобезопасно

// ConcurrentQueue/Stack — lock-free (Interlocked)
var queue = new ConcurrentQueue<int>();
queue.Enqueue(1);
queue.TryDequeue(out var x);

// BlockingCollection — с ограничением и блокировкой
var blocking = new BlockingCollection<int>(boundedCapacity: 100);
blocking.Add(1);  // Блокирует если полная
blocking.Take();  // Блокирует если пуста
```

### 📊 Сводная таблица: что выбрать

| Сценарий | Коллекция | Обоснование |
|---|---|---|
| Обычный список, частый Add в конец | `List<T>` | O(1) амортиз., кэш-френдли |
| Частый Insert/Remove в середине | `LinkedList<T>` | O(1) с узлом |
| Поиск по ключу | `Dictionary<TKey, TValue>` | O(1) среднее |
| Уникальные значения, проверка вхождения | `HashSet<T>` | O(1) |
| FIFO очередь | `Queue<T>` | O(1) |
| LIFO стек | `Stack<T>` | O(1) |
| Потокобезопасный словарь | `ConcurrentDictionary` | Lock striping |
| Потокобезопасная очередь | `ConcurrentQueue` | Lock-free |
| Неизменяемые данные, функц. стиль | `ImmutableList<T>` | Структурное разделение |
| Парсинг, интероп, high-perf | `Span<T>/Memory<T>` | Нулевые аллокации |
| Многопоточный producer/consumer | `BlockingCollection` | Backpressure |

### 🛠 Практика: бенчмарки

```csharp
[MemoryDiagnoser]
public class CollectionBenchmarks {
    [Params(1000, 10000, 100000)]
    public int N { get; set; }
    
    [Benchmark]
    public void List_Add() {
        var list = new List<int>();
        for (int i = 0; i < N; i++) list.Add(i);
    }
    
    [Benchmark]
    public void List_Add_Preallocated() {
        var list = new List<int>(N);
        for (int i = 0; i < N; i++) list.Add(i);
    }
    
    [Benchmark]
    public void ImmutableList_Add() {
        var list = ImmutableList.Create<int>();
        for (int i = 0; i < N; i++) list = list.Add(i);
    }
    
    [Benchmark]
    public void ImmutableList_Builder() {
        var builder = ImmutableList.CreateBuilder<int>();
        for (int i = 0; i < N; i++) builder.Add(i);
        var _ = builder.ToImmutable();
    }
}
```

Ожидаемый результат: `List_Add_Preallocated` быстрее `List_Add` в 2-3 раза на больших N. `ImmutableList_Builder` в 10-100 раз быстрее `ImmutableList_Add`.
"""
}

# ============================================================
# LESSON 17: Async/Await - DEEPENED
# ============================================================
LESSON_ENHANCEMENTS[17] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в async/await: state machine, контекст, производительность

### 🧠 State Machine — как компилятор преобразует async метод

```csharp
// Исходный код
public async Task<string> DownloadAsync(string url) {
    using var client = new HttpClient();
    var data = await client.GetStringAsync(url);
    return Process(data);
}

// Компилятор генерирует структуру, реализующую IAsyncStateMachine:
[CompilerGenerated]
private struct <DownloadAsync>d__0 : IAsyncStateMachine {
    public int <>1__state;           // -1 = завершён, 0 = старт, 1 = после await
    public AsyncTaskMethodBuilder<string> <>t__builder;
    public string url;
    private HttpClient <client>5__1;
    private string <data>5__2;
    private TaskAwaiter<string> <>u__1;
    
    public void MoveNext() {
        int num = <>1__state;
        try {
            if (num == 0) {
                // Начало метода
                <client>5__1 = new HttpClient();
                <>u__1 = <client>5__1.GetStringAsync(url).GetAwaiter();
                if (!<>u__1.IsCompleted) {
                    <>1__state = 1;
                    <>t__builder.AwaitUnsafeOnCompleted(ref <>u__1, ref this);
                    return;  // Возврат управления! Метод НЕ блокирует поток.
                }
            } else if (num == 1) {
                // Продолжение после await
            }
            <>u__1 = default;
            <data>5__2 = <>u__1.GetResult();
            string result = Process(<data>5__2);
            <>t__builder.SetResult(result);
        } catch (Exception ex) {
            <>t__builder.SetException(ex);
        }
    }
}
```

**Ключевые моменты**:
- `await` — это **не блокировка**! Это регистрация продолжения и возврат управления вызывающему коду
- State machine хранит все локальные переменные как поля структуры
- `MoveNext()` вызывается при каждом завершении await'а

### ⚡ Task vs ValueTask — детальное сравнение

```csharp
// Task — класс (reference type), всегда аллоцируется (кроме кэшированных)
public Task<int> GetCached(int key) {
    if (_cache.TryGetValue(key, out var value))
        return Task.FromResult(value);  // Возвращает кэшированный Task<int> — новая аллокация!
    return FetchFromDbAsync(key);
}

// ValueTask — структура (value type), НЕ аллоцирует если результат уже есть
public ValueTask<int> GetCached(int key) {
    if (_cache.TryGetValue(key, out var value))
        return new ValueTask<int>(value);  // Ноль аллокаций!
    return new ValueTask<int>(FetchFromDbAsync(key));  // Асинхронный путь
}

// ВАЖНО: ValueTask можно await ТОЛЬКО ОДИН РАЗ!
var vt = GetCached(1);
await vt;  // OK
await vt;  // ИСКЛЮЧЕНИЕ! ValueTask уже потреблён.

// Правильно:
var result = await GetCached(1);  // await сразу, не сохранять ValueTask
```

**Когда что использовать**:
| Сценарий | Рекомендация |
|---|---|
| Результат часто уже доступен (кэш) | `ValueTask` |
| Всегда асинхронно (БД, HTTP) | `Task` |
| Горячий путь, миллионы вызовов/сек | `ValueTask` + `IValueTaskSource` |
| Нужно сохранить для повторного await | `Task` |

### 🛑 CancellationToken — правильная реализация

```csharp
public async Task ProcessAsync(CancellationToken ct = default) {
    for (int i = 0; i < 1000; i++) {
        // 1. Быстрая проверка (без аллокаций)
        ct.ThrowIfCancellationRequested();
        
        // 2. Передача вниз по цепочке
        await DoWorkAsync(i, ct);
    }
}

// В вызывающем коде:
using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
try {
    await ProcessAsync(cts.Token);
} catch (OperationCanceledException) {
    // Отменено по таймауту
}

// Связывание токенов (для составных операций):
var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(ct1, ct2, ct3);
await ProcessAsync(linkedCts.Token);
```

**Правила CancellationToken**:
1. Всегда принимайте `CancellationToken` в async методах (default = CancellationToken.None)
2. Проверяйте `ThrowIfCancellationRequested()` в циклах
3. Передавайте `ct` во все вложенные async вызовы
4. Используйте `CancellationTokenSource` для управления временем жизни

### 🔄 Параллелизм: WhenAll, WhenAny, Parallel.ForEachAsync

```csharp
// ПОСЛЕДОВАТЕЛЬНО (медленно):
foreach (var url in urls) {
    var data = await DownloadAsync(url);  // Ждёт завершения каждого
}

// ПАРАЛЛЕЛЬНО (быстро) — Task.WhenAll:
var tasks = urls.Select(DownloadAsync);
var results = await Task.WhenAll(tasks);  // Все запускаются сразу

// ОГРАНИЧЕННАЯ ПАРАЛЛЕЛЬНОСТЬ — Parallel.ForEachAsync (.NET 6+):
await Parallel.ForEachAsync(urls, new ParallelOptions { 
    MaxDegreeOfParallelism = 4 
}, async (url, ct) => {
    await DownloadAsync(url, ct);
});

// ТАЙМАУТЫ — Task.WhenAny:
var downloadTask = DownloadAsync(url);
var timeoutTask = Task.Delay(TimeSpan.FromSeconds(10));
var completed = await Task.WhenAny(downloadTask, timeoutTask);
if (completed == timeoutTask) throw new TimeoutException();
var data = await downloadTask;

// SEMAPHORE для ручного ограничения (старое API):
var sem = new SemaphoreSlim(4);
var tasks = urls.Select(async url => {
    await sem.WaitAsync(ct);
    try { return await DownloadAsync(url, ct); }
    finally { sem.Release(); }
});
await Task.WhenAll(tasks);
```

### 🌊 IAsyncEnumerable — асинхронные потоки

```csharp
// Producer — генерация данных по требованию
public async IAsyncEnumerable<int> GenerateAsync([EnumeratorCancellation] CancellationToken ct) {
    for (int i = 0; i < 100; i++) {
        await Task.Delay(10, ct);
        yield return i;
    }
}

// Consumer — асинхронное потребление
await foreach (var item in GenerateAsync(ct)) {
    Console.WriteLine(item);
}

// LINQ над IAsyncEnumerable (System.Linq.Async):
var evens = GenerateAsync(ct).Where(x => x % 2 == 0);
await foreach (var x in evens) { }

// Batch processing:
await foreach (var batch in GenerateAsync(ct).Chunk(10)) {
    await ProcessBatch(batch);
}
```

**Когда использовать**:
- Стриминг больших данных без загрузки в память
- Server-Sent Events, gRPC streaming
- Обработка чанков из БД

### ⚙️ ConfigureAwait и SynchronizationContext

```csharp
// По умолчанию: продолжение в ТОМ ЖЕ контексте (UI thread, ASP.NET classic)
await client.GetAsync(url);

// ConfigureAwait(false) — продолжение в ThreadPool, БЕЗ захвата контекста
await client.GetAsync(url).ConfigureAwait(false);
```

| Контекст | ConfigureAwait(true) | ConfigureAwait(false) |
|---|---|---|
| WPF/WinForms UI | Продолжение в UI потоке | В ThreadPool (может упасть при доступе к UI) |
| ASP.NET Core | Нет SynchronizationContext | Всегда в ThreadPool |
| Console/Worker | ThreadPool | ThreadPool |

**Правило**: в **библиотеках** всегда `.ConfigureAwait(false)`. В **UI коде** — `true` (по умолчанию).

### 🔒 Deadlocks — классическая проблема

```csharp
// DEADLOCK в WPF / старом ASP.NET:
public string GetData() => GetDataAsync().Result;  // Блокирует UI поток!
// async метод ждёт продолжение в UI потоке, но UI поток заблокирован .Result

// РЕШЕНИЯ:
// 1. Везде async:
public async Task<string> GetData() => await GetDataAsync();

// 2. ConfigureAwait(false) в библиотеках:
// В GetDataAsync:
await client.GetAsync(url).ConfigureAwait(false);

// 3. Task.Run для CPU-bound:
await Task.Run(() => HeavyCompute());
```

### ⚠️ Типичные ошибки и анти-паттерны

```csharp
// 1. async void (кроме event handlers) — исключения теряются!
async void Bad() { await Task.Delay(100); throw new Exception(); }
// Используйте async Task

// 2. .Result / .Wait() — deadlock
var data = client.GetStringAsync(url).Result;  // НИКОГДА!
// Всегда await

// 3. Забытый CancellationToken
await ProcessAsync();  // Нет возможности отменить
// Всегда: await ProcessAsync(ct);

// 4. Task.Run для I/O — лишний поток
await Task.Run(() => client.GetStringAsync(url));  // ПЛОХО!
// I/O не нужно в пуле потоков

// 5. foreach вместо await foreach
foreach (var item in asyncEnumerable) { }  // Не скомпилируется/не работает
// Всегда: await foreach

// 6. Множественный await ValueTask
var vt = GetValueAsync();
await vt;
await vt;  // Исключение!
// Правильно: var result = await vt;

// 7. Не проброс ct вниз
await ProcessAsync();  // ct потерян внутри
// await ProcessAsync(ct);
```

### 🛠 Практика: реализуйте правильные паттерны

1. **Retry с экспоненциальным backoff**:
```csharp
public async Task<T> RetryAsync<T>(Func<Task<T>> action, int maxRetries = 3, CancellationToken ct = default) {
    for (int i = 0; ; i++) {
        try { return await action(); }
        catch (Exception ex) when (i < maxRetries && IsTransient(ex)) {
            var delay = TimeSpan.FromSeconds(Math.Pow(2, i)) + TimeSpan.FromMilliseconds(Random.Shared.Next(100));
            await Task.Delay(delay, ct);
        }
    }
}
```

2. **Timeout wrapper**:
```csharp
public static async Task<T> WithTimeout<T>(this Task<T> task, TimeSpan timeout) {
    var completed = await Task.WhenAny(task, Task.Delay(timeout));
    if (completed == task) return await task;
    throw new TimeoutException();
}
```

3. **Bulkhead (ограничение параллелизма)**:
```csharp
public class Bulkhead {
    private readonly SemaphoreSlim _sem;
    public Bulkhead(int maxParallel) => _sem = new SemaphoreSlim(maxParallel);
    
    public async Task<T> ExecuteAsync<T>(Func<Task<T>> action) {
        await _sem.WaitAsync();
        try { return await action(); }
        finally { _sem.Release(); }
    }
}
```
"""
}

# Also add enhancements for lessons 18-33
LESSON_ENHANCEMENTS[18] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в CLR, GC, JIT

### ⚙️ Tiered Compilation (многоуровневая компиляция) — подробности

**.NET 7+** использует Tiered Compilation по умолчанию:

```
Tier 0 (быстрая компиляция):
- Без оптимизаций
- Быстрый старт приложения
- Использует интерпретатор или быстрый JIT
- Генерирует много инструкций, но работает "достаточно быстро"

Tier 1 (оптимизированная):
- Полные оптимизации (inlining, loop unrolling, vectorization)
- Компилируется в фоне для "горячих" методов
- Заменяет Tier 0 код на лету (OSR - On-Stack Replacement)
```

**OSR (On-Stack Replacement)** — уникальная технология .NET:
- Метод может быть заменён прямо во время выполнения
- Если метод долго выполняется в Tier 0, компилятор создаёт оптимизированную версию
- Переключение происходит в безопасной точке (loop header, method entry)

```xml
<!-- Отключение Tiered Compilation -->
<TieredCompilation>false</TieredCompilation>

<!-- Или для конкретного метода -->
[MethodImpl(MethodImplOptions.NoOptimization)]
public void NoOptMethod() { }
```

### 🏗 ReadyToRun (Crossgen2) — AOT-оптимизация

```xml
<PublishReadyToRun>true</PublishReadyToRun>
<PublishReadyToRunComposite>true</PublishReadyToRunComposite>
```

**Как работает**:
- При сборке генерируется нативный код для большинства методов
- При запуске JIT пропускает уже скомпилированные методы
- **Плюсы**: быстрее холодный старт, меньше работы JIT
- **Минусы**: больше размер сборки, не все методы совместимы (generic, рефлексия)

### 🎯 PGO — Profile-Guided Optimization

**Dynamic PGO (.NET 8+)** — рекомендуемый подход:
```xml
<TieredCompilation>true</TieredCompilation>
<TieredPGO>true</TieredPGO>
```

**Static PGO** — требует профилирования:
```bash
# 1. Инструментированная сборка
dotnet build -c Release /p:OptimizePGOInstrument=true

# 2. Запуск под нагрузкой (реальные сценарии!)
dotnet run --project MyApp

# 3. Оптимизированная сборка с профилем
dotnet build -c Release /p:OptimizePGOTrain=true
```

### 🗑 GC — поколения и эфимерный сегмент

```
┌─────────────────────────────────────────┐
│            Gen 2 (Large)                │  ← Долгоживущие объекты
│         (Full GC, редко)                │
├─────────────────────────────────────────┤
│            Gen 1 (Medium)               │  ← Выжили после Gen 0
│         (средний размер)                │
├─────────────────────────────────────────┤
│            Gen 0 (Small, ~256KB)        │  ← Новые объекты
│         (очень частый GC)               │
└─────────────────────────────────────────┘
```

**Large Object Heap (LOH)** — объекты ≥ 85,000 байт:
- Не компактируется (до .NET 5) → фрагментация
- Собирается ТОЛЬКО при Gen 2 (Full GC)
- .NET 5+: `GCSettings.LargeObjectHeapCompactionMode = CompactOnce`

**Pinned Object Heap (POH)** — .NET 5+:
- Объекты закреплённые через `fixed`, `GCHandle.Alloc(pinned)`
- Не двигаются при компактировке

### ⚙️ Режимы GC

| Режим | Workstation | Server |
|---|---|---|
| Потоки GC | 1 (или фоновый) | 1 на логический CPU |
| Память | Меньше | Больше (для throughput) |
| Latency | Низкая (для UI) | Выше, но выше throughput |
| Использование | Клиентские приложения | ASP.NET Core, gRPC, высоконагруженные сервисы |

```xml
<!-- Server GC для продакшена -->
<ServerGarbageCollection>true</ServerGarbageCollection>
<!-- Background GC включен по умолчанию -->
```

### 🔧 SafeHandle — правильный паттерн для unmanaged ресурсов

```csharp
// НЕПРАВИЛЬНО: IntPtr + финализатор
class BadWrapper {
    private IntPtr _handle;
    ~BadWrapper() => NativeMethods.Close(_handle);  // Негарантированно!
}

// ПРАВИЛЬНО: SafeHandle
public sealed class MySafeHandle : SafeHandleZeroOrMinusOneIsInvalid {
    private MySafeHandle() : base(true) { }  // ownsHandle = true
    
    public static MySafeHandle Create() {
        var handle = NativeMethods.Create();
        return new MySafeHandle { handle = handle };
    }
    
    protected override bool ReleaseHandle() 
        => NativeMethods.Close(handle);
}

// Использование — финализатор НЕ нужен!
public class Wrapper : IDisposable {
    private readonly MySafeHandle _handle = MySafeHandle.Create();
    public void Dispose() => _handle.Dispose();
}
```

**Почему SafeHandle лучше**:
- Наследуется от `CriticalFinalizerObject` — финализатор гарантированно выполнится
- Правильная семантика владения (`ownsHandle`)
- Защита от утечек при исключениях в конструкторе
"""
}

LESSON_ENHANCEMENTS[19] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в тестирование: продвинутые паттерны

### 🎭 Moq — продвинутое использование

**SetupSequence** — последовательные возвраты:
```csharp
mockRepo.SetupSequence(r => r.GetNextId())
    .Returns(1)
    .Returns(2)
    .Throws(new Exception("No more IDs"));
```

**Callback** — сложная логика:
```csharp
mockRepo.Setup(r => r.AddAsync(It.IsAny<User>(), It.IsAny<CancellationToken>()))
    .Callback<User, CancellationToken>((u, ct) => {
        u.Id = Interlocked.Increment(ref _lastId);  // Генерация ID
        _addedUsers.Add(u);  // Сохранение для проверки
    })
    .Returns(Task.CompletedTask);
```

**Verify с предикатами**:
```csharp
// Проверка аргументов
mock.Verify(r => r.Save(It.Is<User>(u => u.Age > 18 && u.Name.StartsWith("A"))), Times.Once);

// VerifyAll — все настройленные методы должны быть вызваны
var strictMock = new Mock<IService>(MockBehavior.Strict);
strictMock.VerifyAll();
```

### 🐳 Testcontainers — продвинутые сценарии

**Множественные контейнеры в одной сети**:
```csharp
var network = new NetworkBuilder().Build();
await network.CreateAsync();

var postgres = new PostgreSqlBuilder()
    .WithNetwork(network)
    .WithNetworkAliases("db")
    .Build();

var redis = new RedisBuilder()
    .WithNetwork(network)
    .WithNetworkAliases("cache")
    .Build();

await Task.WhenAll(postgres.StartAsync(), redis.StartAsync());
// Приложение подключается к "db" и "cache" по именам
```

**Кастомные образы и скрипты инициализации**:
```csharp
var customDb = new ContainerBuilder()
    .WithImage("my-custom-postgres:15")
    .WithResourceMapping(new FileInfo("./init.sql"), "/docker-entrypoint-initdb.d/init.sql")
    .WithEnvironment("POSTGRES_DB", "test")
    .Build();
```

### 📊 Покрытие кода — правильная интерпретация

```bash
# Запуск с покрытием
dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage

# Отчет
reportgenerator -reports:"./coverage/**/coverage.cobertura.xml" \
    -targetdir:"./coverage-report" -reporttypes:Html
```

**Метрики**:
- **Line Coverage** — % выполненных строк (может обманывать)
- **Branch Coverage** — % пройденных веток if/else (важнее!)
- **Method Coverage** — % вызванных методов

**Правильные цели**:
- Не 100% line coverage!
- 80%+ branch coverage для бизнес-логики
- 100% для критических путей (платежи, безопасность)

### 🔄 Property-Based Testing (FsCheck)

```csharp
// dotnet add package FsCheck.Xunit

[Property]
public void Reverse_ReversesList(int[] items) {
    var reversed = items.Reverse().ToArray();
    Assert.Equal(items, reversed.Reverse().ToArray());
}

[Property]
public void Sort_ProducesOrderedList(int[] items) {
    var sorted = items.OrderBy(x => x).ToArray();
    Assert.True(sorted.SequenceEqual(sorted.OrderBy(x => x)));
}

// FsCheck сам генерирует сотни случайных тест-кейсов
// включая edge cases: пустые массивы, null, дубликаты, Int32.MinValue/MaxValue
```

### 🎯 Contract Testing (Pact)

```csharp
// Provider side (API)
var pact = Pact.ForProvider("MyAPI", config => {
    config.PactDirectory = @"./pacts";
});

pact.Given("user exists")
    .UponReceiving("a request for user")
    .With(new ProviderServiceRequest {
        Method = HttpVerb.Get,
        Path = "/api/users/1",
        Headers = new Dictionary<string, object> { { "Accept", "application/json" } }
    })
    .WillRespondWith(new ProviderServiceResponse {
        Status = 200,
        Headers = new Dictionary<string, object> { { "Content-Type", "application/json" } },
        Body = new { id = 1, name = "Alex" }
    });
pact.Verify();
```
"""
}

LESSON_ENHANCEMENTS[20] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в JSON, файлы, SQL

### 📄 System.Text.Json — Source Generators для AOT

```csharp
// Традиционный подход (рефлексия, не работает в NativeAOT)
var options = new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase };
var json = JsonSerializer.Serialize(user, options);

// Source Generator (compile-time, работает в NativeAOT)
[JsonSerializable(typeof(User))]
[JsonSerializable(typeof(List<User>))]
[JsonSourceGenerationOptions(PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase)]
internal partial class AppJsonContext : JsonSerializerContext { }

// Использование — БЕЗ рефлексии!
var json = JsonSerializer.Serialize(user, AppJsonContext.Default.User);
var user = JsonSerializer.Deserialize(json, AppJsonContext.Default.User);
```

**Плюсы Source Generator**:
- Работает в NativeAOT
- Никакой рефлексии в runtime
- Компилятор проверяет типы на этапе сборки
- Быстрее старт, меньше памяти

### 📁 Продвинутая работа с потоками

**PipeReader/Writer** — высокопроизводительные пайплайны:
```csharp
var pipe = new Pipe();

// Producer
_ = Task.Run(async () => {
    var writer = pipe.Writer;
    while (hasData) {
        var memory = writer.GetMemory(4096);
        var bytesRead = await source.ReadAsync(memory, ct);
        writer.Advance(bytesRead);
        await writer.FlushAsync(ct);
    }
    writer.Complete();
});

// Consumer
var reader = pipe.Reader;
while (true) {
    var result = await reader.ReadAsync(ct);
    var buffer = result.Buffer;
    
    while (TryParse(ref buffer, out var message)) {
        Process(message);
    }
    
    reader.AdvanceTo(buffer.Start, buffer.End);
    if (result.IsCompleted) break;
}
```

**ArrayPool для буферов**:
```csharp
// ПЛОХО: аллокация на каждой итерации
var buffer = new byte[4096];
await stream.ReadAsync(buffer);

// ХОРОШО: пулинг
byte[] buffer = ArrayPool<byte>.Shared.Rent(4096);
try {
    await stream.ReadAsync(buffer.AsMemory(0, 4096), ct);
} finally {
    ArrayPool<byte>.Shared.Return(buffer);
}
```

### 🗄 Dapper — продвинутые сценарии

**Multi-mapping (Join)**:
```csharp
var sql = @"
    SELECT u.*, p.* 
    FROM Users u 
    LEFT JOIN Posts p ON p.UserId = u.Id 
    WHERE u.Id = @id";

var userDict = new Dictionary<int, User>();
var user = await conn.Query<User, Post, User>(sql, 
    (u, p) => {
        if (!userDict.TryGetValue(u.Id, out var user)) {
            user = u;
            user.Posts = new List<Post>();
            userDict[u.Id] = user;
        }
        if (p != null) user.Posts.Add(p);
        return user;
    },
    new { id = 1 },
    splitOn: "Id");  // Колонка для разделения объектов

return userDict.Values.FirstOrDefault();
```

**Транзакции**:
```csharp
using var tx = await conn.BeginTransactionAsync();
try {
    await conn.ExecuteAsync("INSERT ...", params, tx);
    await conn.ExecuteAsync("UPDATE ...", params, tx);
    await tx.CommitAsync();
} catch {
    await tx.RollbackAsync();
    throw;
}
```

**Bulk Insert** (Dapper.Contrib или вручную):
```csharp
// Для больших объёмов — SqlBulkCopy
using var bulk = new SqlBulkCopy(conn) { DestinationTableName = "Users" };
bulk.ColumnMappings.Add("Id", "Id");
bulk.ColumnMappings.Add("Name", "Name");
await bulk.WriteToServerAsync(dataTable);
```

### 🏗 EF Core — продвинутые темы

**Split Query** — решение cartesian explosion:
```csharp
// ПРОБЛЕМА: Include создаёт огромный JOIN с дублированием
var users = await db.Users
    .Include(u => u.Posts)
    .Include(u => u.Comments)
    .ToListAsync();  // Users * Posts * Comments строк!

// РЕШЕНИЕ: Split Query — отдельные запросы
var users = await db.Users
    .Include(u => u.Posts)
    .Include(u => u.Comments)
    .AsSplitQuery()  // 3 отдельных запроса вместо 1 огромного
    .ToListAsync();
```

**Compiled Queries** — кэширование плана выполнения:
```csharp
private static readonly Func<AppDbContext, int, Task<User>> _getUserById =
    EF.CompileAsyncQuery((AppDbContext ctx, int id) => 
        ctx.Users.FirstOrDefault(u => u.Id == id));

// Использование — без перекомпиляции LINQ каждый раз
var user = await _getUserById(ctx, 123);
```

**Interceptors** — перехват команд:
```csharp
public class SoftDeleteInterceptor : SaveChangesInterceptor {
    public override InterceptionResult<int> SavingChanges(
        DbContextEventData eventData, InterceptionResult<int> result) {
        
        foreach (var entry in eventData.Context.ChangeTracker.Entries()
            .Where(e => e.State == EntityState.Deleted && e.Entity is ISoftDelete)) {
            
            entry.State = EntityState.Modified;
            entry.CurrentValues["IsDeleted"] = true;
            entry.CurrentValues["DeletedAt"] = DateTime.UtcNow;
        }
        return base.SavingChanges(eventData, result);
    }
}

// Регистрация
builder.Services.AddDbContext<AppDbContext>(options => 
    options.AddInterceptors(new SoftDeleteInterceptor()));
```

**Change Tracker** — отслеживание изменений:
```csharp
var user = await db.Users.FindAsync(1);
user.Name = "New Name";

// Что изменилось:
var entries = db.ChangeTracker.Entries()
    .Where(e => e.State == EntityState.Modified);

foreach (var entry in entries) {
    Console.WriteLine($"{entry.Entity.GetType().Name}: {entry.State}");
    foreach (var prop in entry.Properties.Where(p => p.IsModified)) {
        Console.WriteLine($"  {prop.Metadata.Name}: {prop.OriginalValue} -> {prop.CurrentValue}");
    }
}
```
"""
}

LESSON_ENHANCEMENTS[21] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в DI, Configuration, Logging

### ⚙️ DI — продвинутые сценарии регистрации

**Декоратор (Decorator Pattern)**:
```csharp
// Базовая реализация
services.AddScoped<IUserRepository, EfUserRepository>();

// Декоратор для кэширования
services.Decorate<IUserRepository, CachedUserRepositoryDecorator>();

// Реализация декоратора
public class CachedUserRepositoryDecorator : IUserRepository {
    private readonly IUserRepository _inner;
    private readonly IDistributedCache _cache;
    
    public async Task<User?> GetByIdAsync(UserId id, CancellationToken ct) {
        var cacheKey = $"user:{id}";
        var cached = await _cache.GetStringAsync(cacheKey, ct);
        if (cached != null) return JsonSerializer.Deserialize<User>(cached);
        
        var user = await _inner.GetByIdAsync(id, ct);
        if (user != null) {
            await _cache.SetStringAsync(cacheKey, JsonSerializer.Serialize(user), ct);
        }
        return user;
    }
}
```

**Открытые дженерики (Open Generics)**:
```csharp
// Регистрация для всех T
services.AddTransient(typeof(IRepository<>), typeof(EfRepository<>));
services.AddTransient(typeof(IValidator<>), typeof(FluentValidator<>));

// Использование
public class UserService {
    private readonly IRepository<User> _userRepo;  // Резолвится как EfRepository<User>
    private readonly IValidator<CreateUserCommand> _validator;
}
```

**Keyed Services (.NET 8+)**:
```csharp
// Регистрация с ключами
services.AddKeyedTransient<IPaymentProcessor, StripeProcessor>("stripe");
services.AddKeyedTransient<IPaymentProcessor, PayPalProcessor>("paypal");
services.AddKeyedTransient<IPaymentProcessor, CryptoProcessor>("crypto");

// Резолвиция по ключу
var processor = sp.GetRequiredKeyedService<IPaymentProcessor>("stripe");

// Или через атрибут
public class PaymentService([FromKeyedServices("stripe")] IPaymentProcessor processor) { }
```

### ⚙️ Configuration — продвинутые паттерны

**IOptionsMonitor — горячая перезагрузка**:
```csharp
public class JwtTokenService {
    private readonly JwtOptions _options;
    
    public JwtTokenService(IOptionsMonitor<JwtOptions> monitor) {
        _options = monitor.CurrentValue;
        monitor.OnChange(o => {
            _options = o;  // Реакция на изменение конфигурации!
            _key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(o.Key));
        });
    }
}
```

**Валидация конфигурации при старте**:
```csharp
builder.Services.AddOptions<JwtOptions>()
    .BindConfiguration("Jwt")
    .ValidateDataAnnotations()  // [Required], [MinLength] и т.д.
    .Validate(o => o.Key.Length >= 32, "Key must be at least 32 chars")
    .ValidateOnStart();  // Падает при старте если невалидно!
```

**Azure Key Vault интеграция**:
```csharp
builder.Configuration.AddAzureKeyVault(
    new Uri("https://myvault.vault.azure.net/"),
    new DefaultAzureCredential());  // Managed Identity, Azure CLI, Env Vars

// Секреты в KV: "Database--ConnectionString" → "Database:ConnectionString"
```

### 📝 Serilog — продвинутое логирование

**Кастомные Enrichers**:
```csharp
public class UserEnricher : ILogEventEnricher {
    private readonly IHttpContextAccessor _httpContext;
    
    public void Enrich(LogEvent logEvent, ILogEventPropertyFactory factory) {
        if (_httpContext.HttpContext?.User?.Identity?.IsAuthenticated == true) {
            var userId = _httpContext.HttpContext.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (userId != null) 
                logEvent.AddPropertyIfAbsent(factory.CreateProperty("UserId", userId));
        }
    }
}

// Регистрация
Log.Logger = new LoggerConfiguration()
    .Enrich.With<UserEnricher>()
    .CreateLogger();
```

**Destructuring — скрытие чувствительных данных**:
```csharp
.Destructure.ByTransforming<User>(u => new { 
    u.Id, u.Name, u.Email, 
    // НЕ логируем PasswordHash, CreditCard и т.д.
})
.Destructure.AsScalar<CreditCardNumber>()  // Не разбирать как объект
```

**Structured Logging в Seq/ELK**:
```csharp
// ХОРОШО — свойства для запросов
_logger.LogInformation("User {UserId} placed order {OrderId} for {Amount:C}", 
    userId, orderId, amount);

// В Seq: UserId == 123 AND Amount > 50
```
"""
}

LESSON_ENHANCEMENTS[22] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в архитектуру: Clean Architecture, DDD, CQRS

### 🏛 Clean Architecture — правила зависимостей

```
┌─────────────────────────────────────────┐
│            Domain (Enterprise)          │  ← Бизнес-логика, НИКАКИХ зависимостей
│  Entities, Value Objects, Events,       │
│  Repository Interfaces, Exceptions      │
├─────────────────────────────────────────┤
│         Application (Use Cases)         │  ← Use Cases, DTOs, Interfaces
│  Commands, Queries, Handlers,           │     Репозитории (интерфейсы!)
│  Validators, Mappers, Behaviors         │
├─────────────────────────────────────────┤
│           Infrastructure                │  ← Реализации: EF Core, HTTP, Email
│  DbContext, Repositories, Services,     │
│  Identity, Background Jobs, Config      │
├─────────────────────────────────────────┤
│          Presentation (API/UI)          │  ← Controllers, Views, gRPC, SignalR
│  Endpoints, DTOs, Mapping, Middleware   │
└─────────────────────────────────────────┘
```

**Dependency Rule**: зависимости ТОЛЬКО внутрь. Domain не знает ни о ком.

### 🎯 DDD — Aggregate Root и Domain Events

```csharp
// Aggregate Root — граница консистентности
public class Order : AggregateRoot<OrderId> {
    private readonly List<OrderItem> _items = new();
    public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly();
    public OrderStatus Status { get; private set; }
    
    public void AddItem(ProductId productId, int quantity, Money price) {
        if (Status != OrderStatus.Draft) 
            throw new InvalidOperationException("Cannot modify confirmed order");
        
        var existing = _items.FirstOrDefault(i => i.ProductId == productId);
        if (existing != null) existing.IncreaseQuantity(quantity);
        else _items.Add(new OrderItem(productId, quantity, price));
        
        AddDomainEvent(new OrderItemAddedEvent(Id, productId, quantity));
    }
    
    public void Confirm() {
        Status = OrderStatus.Confirmed;
        AddDomainEvent(new OrderConfirmedEvent(Id));
    }
}
```

**Domain Events — публикация после SaveChanges**:
```csharp
public class DomainEventDispatcher {
    private readonly IMediator _mediator;
    
    public async Task DispatchEventsAsync(DbContext ctx, CancellationToken ct) {
        var entities = ctx.ChangeTracker.Entries<IAggregateRoot>()
            .Select(e => e.Entity)
            .Where(e => e.DomainEvents.Any())
            .ToList();
        
        foreach (var entity in entities) {
            var events = entity.DomainEvents.ToList();
            entity.ClearDomainEvents();
            foreach (var @event in events) 
                await _mediator.Publish(@event, ct);
        }
    }
}

// В DbContext:
public override async Task<int> SaveChangesAsync(CancellationToken ct = default) {
    await _dispatcher.DispatchEventsAsync(this, ct);
    return await base.SaveChangesAsync(ct);
}
```

### ⚔️ CQRS с MediatR — Pipeline Behaviors

```csharp
// Validation Behavior (FluentValidation)
public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> 
    where TRequest : IRequest<TResponse> {
    
    private readonly IEnumerable<IValidator<TRequest>> _validators;
    
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct) {
        var context = new ValidationContext<TRequest>(request);
        var failures = _validators.Select(v => v.Validate(context))
            .SelectMany(r => r.Errors).Where(e => e != null).ToList();
        if (failures.Any()) throw new ValidationException(failures);
        return await next();
    }
}

// Transaction Behavior — только для команд
public class TransactionBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> {
    private readonly IUnitOfWork _uow;
    
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct) {
        if (request is ICommand) {
            await _uow.BeginTransactionAsync(ct);
            try {
                var response = await next();
                await _uow.CommitAsync(ct);
                return response;
            } catch {
                await _uow.RollbackAsync(ct);
                throw;
            }
        }
        return await next();
    }
}

// Регистрация (порядок важен!)
services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(typeof(Program).Assembly));
services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
services.AddTransient(typeof(IPipelineBehavior<,>), typeof(TransactionBehavior<,>));
services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
```

### 📜 Event Sourcing — события как источник истины

```csharp
// Aggregate хранит только события
public class Account : EventSourcedAggregate {
    public decimal Balance { get; private set; }
    public bool IsClosed { get; private set; }
    
    public void Deposit(decimal amount) {
        if (IsClosed) throw new InvalidOperationException("Account closed");
        Apply(new MoneyDepositedEvent(Id, amount));
    }
    
    protected override void When(object @event) {
        switch (@event) {
            case MoneyDepositedEvent e: Balance += e.Amount; break;
            case MoneyWithdrawnEvent e: Balance -= e.Amount; break;
            case AccountClosedEvent e: IsClosed = true; break;
        }
    }
}

// Event Store — только Append
public interface IEventStore {
    Task AppendAsync(AggregateId id, IEnumerable<IDomainEvent> events, int expectedVersion, CancellationToken ct);
    Task<IReadOnlyList<IDomainEvent>> GetEventsAsync(AggregateId id, CancellationToken ct);
}

// Projection (Read Model) — строятся из событий асинхронно
public class AccountBalanceProjection : 
    IEventHandler<MoneyDepositedEvent>, 
    IEventHandler<MoneyWithdrawnEvent> {
    
    private readonly IReadModelRepository<AccountBalanceView> _repo;
    
    public async Task Handle(MoneyDepositedEvent @event, CancellationToken ct) {
        var view = await _repo.GetAsync(@event.AccountId) ?? new AccountBalanceView(@event.AccountId);
        view.Balance += @event.Amount;
        await _repo.SaveAsync(view, ct);
    }
}
```
"""
}

LESSON_ENHANCEMENTS[23] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в систему типов: Constraints, Variance, Records

### 🔧 Generics Constraints — полная классификация

```csharp
// Основные
where T : class           // Ссылочный тип (class, interface, delegate, array)
where T : struct          // Значимый тип (НЕ nullable!)
where T : new()           // Публичный конструктор без параметров
where T : notnull         // Не-nullable (reference или value type)
where T : unmanaged       // Примитивы, указатели, enum, struct БЕЗ ref-полей
where T : Delegate        // Любой делегат (C# 7.3+)
where T : Enum            // Любой enum (C# 7.3+)
where T : BaseClass       // Наследник BaseClass
where T : IInterface      // Реализует интерфейс
where T : U               // T наследует от U (другой type parameter)

// Комбинации
where T : class, IComparable<T>, new()
where T : struct, INumber<T>

// Default constraint (C# 12+)
where T : default         // default(T) валиден (для unmanaged/struct)

// Примеры использования
public class Repository<T> where T : class, IEntity, new() { }
public unsafe void Copy<T>(T* src, T* dst, int count) where T : unmanaged { }
public TEnum ParseEnum<TEnum>(string s) where TEnum : Enum => Enum.Parse<TEnum>(s);
```

### 🔄 Covariance/Contravariance — детальные правила

**Covariance (`out`)** — только ВЫХОДНЫЕ позиции:
```csharp
// IEnumerable<out T> — можно: IEnumerable<string> → IEnumerable<object>
IEnumerable<string> strings = new List<string>();
IEnumerable<object> objects = strings;  // OK

// Func<out TResult> — ковариативен по результату
Func<string> funcStr = () => "hello";
Func<object> funcObj = funcStr;  // OK

// ПРАВИЛО: out — ТОЛЬКО в return type, property get
public interface IReadOnlyRepo<out T> {
    T GetById(int id);      // OK: T на выходе
    IEnumerable<T> GetAll(); // OK
    // void Add(T item);    // ОШИБКА: T на входе
}
```

**Contravariance (`in`)** — только ВХОДНЫЕ позиции:
```csharp
// IComparer<in T> — можно: IComparer<object> → IComparer<string>
IComparer<object> objComparer = (a, b) => 0;
IComparer<string> strComparer = objComparer;  // OK

// Action<in T> — контравариативен
Action<object> actObj = o => Console.WriteLine(o);
Action<string> actStr = actObj;  // OK

// ПРАВИЛО: in — ТОЛЬКО в параметры, property set
public interface IWriter<in T> {
    void Write(T item);  // OK: T на входе
    // T Read();         // ОШИБКА: T на выходе
}
```

**Инвариантность** — по умолчанию (есть и входящие, и исходящие позиции):
```csharp
List<string> strings = new();
List<object> objects = strings;  // ОШИБКА!
// Потому что List<T> имеет Add(T) — вход, и T this[int] — выход
```

### 📝 Records — продвинутые возможности

**Equality и GetHashCode**:
```csharp
// По умолчанию — сравнение по ВСЕМ свойствам (value equality)
var r1 = new User("A", "a@b.com", 1);
var r2 = new User("A", "a@b.com", 1);
r1 == r2;  // true

// Настройка equality через PrintMembers
public record User(string Name, string Email) {
    protected virtual bool PrintMembers(StringBuilder builder) {
        builder.Append($"Email = {Email}");
        return true;  // Сравнение ТОЛЬКО по Email!
    }
}
```

**with-expressions и non-destructive mutation**:
```csharp
var user1 = new User("Alex", "alex@test.com", 25);
var user2 = user1 with { Age = 26 };  // Копия с изменением
var user3 = user1 with { Name = "Bob", Email = "bob@test.com" };  // Множественные изменения

// Positional records — деконструкция
public record Point(int X, int Y);
var p = new Point(10, 20);
var (x, y) = p;  // x=10, y=20
```

**Record Struct (C# 10+)** — value type:
```csharp
public readonly record struct Point3D(int X, int Y, int Z);
// Сравнение по значениям, НЕТ аллокаций на куче!
var p1 = new Point3D(1, 2, 3);
var p2 = p1 with { Z = 4 };  // Работает!
```

### 🎯 Pattern Matching — продвинутые паттерны

```csharp
// List Patterns (C# 11+)
int[] numbers = { 1, 2, 3, 4, 5 };
var result = numbers switch {
    [] => "Empty",
    [0, ..] => "Starts with zero",
    [.., 0] => "Ends with zero",
    [1, 2, 3, ..] => "Starts with 1,2,3",
    [var first, .. var middle, var last] => $"First: {first}, Last: {last}",
    [_, _, _, _, _] => "Exactly 5 elements",
    _ => "Other"
};

// Slice Patterns (C# 12+)
var slice = numbers[1..4];  // 2, 3, 4
var isPrefix = numbers is [1, 2, ..];  // true

// Property Patterns с and/or/not
var user = new User { Name = "Alex", Age = 25, Address: new Address { City: "Moscow" } };
var isAdultInMoscow = user is { Age: >= 18, Address: { City: "Moscow" } };

string category = user switch {
    { Age: < 18 } => "Minor",
    { Age: >= 65 } => "Senior",
    { Name: "Admin" or "Root" } => "Privileged",
    { Address: { Country: "US" } } => "US User",
    _ => "Regular"
};
```
"""
}

LESSON_ENHANCEMENTS[24] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в Internals: IL, Source Generators, Reflection

### 📜 IL — понимание сгенерированного кода

```csharp
// C# код
public int Add(int a, int b) => a + b;

// Соответствующий IL
.method public hidebysig instance int32 Add(int32 a, int32 b) cil managed {
    .maxstack 2
    .locals init ([0] int32 V_0)
    
    IL_0000: ldarg.1      // Загружает аргумент 1 (a)
    IL_0001: ldarg.2      // Загружает аргумент 2 (b)
    IL_0002: add          // Складывает два верхних значения стека
    IL_0003: stloc.0      // Сохраняет в локальную переменную 0
    IL_0004: br.s IL_0006
    IL_0006: ldloc.0      // Загружает локальную 0
    IL_0007: ret          // Возвращает
}
```

**Полезные инструменты**:
- `ildasm` / `dotnet-ildasm` — просмотр IL сборки
- [SharpLab.io](https://sharplab.io) — онлайн C# → IL / AST / JIT asm

### ⚙️ Source Generators — Incremental Generators (современный API)

```csharp
[Generator(LanguageNames.CSharp)]
public class AutoToStringGenerator : IIncrementalGenerator {
    public void Initialize(IncrementalGeneratorInitializationContext context) {
        // 1. Predicate — быстрый фильтр синтаксиса
        var classes = context.SyntaxProvider
            .CreateSyntaxProvider(
                predicate: (node, _) => node is ClassDeclarationSyntax { AttributeLists.Count: > 0 },
                transform: (ctx, _) => (ClassDeclarationSyntax)ctx.Node)
            .Where(c => c.AttributeLists.Any(a => 
                a.Attributes.Any(attr => attr.Name.ToString() == "GenerateToString")))
            .Collect();

        // 2. Генерация кода
        context.RegisterSourceOutput(classes, (ctx, classList) => {
            foreach (var classDecl in classList) {
                var props = classDecl.Members
                    .OfType<PropertyDeclarationSyntax>()
                    .Select(p => p.Identifier.Text);
                
                var source = $@"// <auto-generated/>
namespace {classDecl.GetNamespace()} {{
    partial class {classDecl.Identifier} {{
        public override string ToString() => 
            $\"{{GetType().Name}}: {{{string.Join(\", \", props.Select(p => $\"{p} = {{{p}}}\"))}}}\";
    }}
}}";
                ctx.AddSource($"{classDecl.Identifier}.ToString.g.cs", 
                    SourceText.From(source, Encoding.UTF8));
            }
        });
    }
}
```

**Ключевые отличия от ISourceGenerator**:
- `IIncrementalGenerator` — кэширует результаты, работает инкрементально
- `CreateSyntaxProvider` с predicate/transform — избегает лишнего парсинга
- `Collect()` — собирает все узлы перед генерацией
- Быстрее, меньше памяти, работает в NativeAOT

### 🔍 Reflection — оптимизация производительности

```csharp
// МЕДЛЕННО: рефлексия каждый раз
var prop = typeof(User).GetProperty("Name");
var value = prop.GetValue(user);

// БЫСТРО: кэширование PropertyInfo
private static readonly PropertyInfo NameProperty = typeof(User).GetProperty("Name")!;
var value = NameProperty.GetValue(user);

// ЕЩЁ БЫСТРО: делегат
private static readonly Func<User, string> GetNameDelegate = 
    (Func<User, string>)Delegate.CreateDelegate(typeof(Func<User, string>), NameProperty.GetGetMethod()!);
var value = GetNameDelegate(user);  // Прямой вызов, никакой рефлексии

// Для максимальной скорости — DynamicMethod / ILGenerator
```

### 🌳 Expression Trees — динамическое построение

```csharp
// Динамический OrderBy по имени свойства строкой
public static IQueryable<T> OrderByDynamic<T>(IQueryable<T> query, string propertyName) {
    var param = Expression.Parameter(typeof(T), "x");
    var prop = Expression.Property(param, propertyName);
    var lambda = Expression.Lambda(prop, param);
    
    var method = typeof(Queryable).GetMethods()
        .First(m => m.Name == "OrderBy" && m.GetParameters().Length == 2)
        .MakeGenericMethod(typeof(T), prop.Type);
    
    return (IQueryable<T>)method.Invoke(null, new object[] { query, lambda })!;
}

// Expression Visitor — трансформация
public class ParameterReplacer : ExpressionVisitor {
    private readonly ParameterExpression _old, _new;
    public ParameterReplacer(ParameterExpression oldP, ParameterExpression newP) {
        _old = oldP; _new = newP;
    }
    protected override Expression VisitParameter(ParameterExpression node)
        => node == _old ? _new : base.VisitParameter(node);
}
```

### ⚡ DynamicMethod / ILGenerator — ручная генерация

```csharp
public static Func<T, TProp> CreateFastGetter<T, TProp>(string propertyName) {
    var prop = typeof(T).GetProperty(propertyName)!;
    var getMethod = prop.GetGetMethod(true)!;
    
    var dm = new DynamicMethod(
        $"get_{propertyName}", 
        typeof(TProp), 
        new[] { typeof(T) }, 
        typeof(T), 
        skipVisibility: true);  // Доступ к private!
    
    var il = dm.GetILGenerator();
    il.Emit(OpCodes.Ldarg_0);           // Загружаем this
    il.Emit(OpCodes.Callvirt, getMethod); // Вызываем getter
    il.Emit(OpCodes.Ret);               // Возвращаем
    
    return (Func<T, TProp>)dm.CreateDelegate(typeof(Func<T, TProp>));
}
```
"""
}

LESSON_ENHANCEMENTS[25] = {
    "additional_content_md": """
## 🔍 Глубокое погружение: Extension Members, Operators, Pattern-based API

### 🔧 Extension Methods — продвинутые паттерны

**Generic Extensions с constraints**:
```csharp
public static class EnumerableExtensions {
    // Расширение только для IEnumerable<T>
    public static IEnumerable<T> DistinctBy<T, TKey>(
        this IEnumerable<T> source, 
        Func<T, TKey> keySelector) {
        var seen = new HashSet<TKey>();
        foreach (var item in source) {
            if (seen.Add(keySelector(item))) yield return item;
        }
    }
    
    // Chunk для .NET < 6
    public static IEnumerable<IEnumerable<T>> Chunk<T>(
        this IEnumerable<T> source, int size) {
        var chunk = new List<T>(size);
        foreach (var item in source) {
            chunk.Add(item);
            if (chunk.Count == size) {
                yield return chunk;
                chunk = new List<T>(size);
            }
        }
        if (chunk.Count > 0) yield return chunk;
    }
}
```

**Extension Properties (C# 12)** — только геттеры:
```csharp
public static class DateTimeExtensions {
    // На самом деле метод, но выглядит как свойство
    public static int WeekOfYear(this DateTime date) 
        => CultureInfo.CurrentCulture.Calendar.GetWeekOfYear(
            date, CalendarWeekRule.FirstFourDayWeek, DayOfWeek.Monday);
    
    public static bool IsWeekend(this DateTime date) 
        => date.DayOfWeek is DayOfWeek.Saturday or DayOfWeek.Sunday;
}
```

### ➕ Перегрузка операторов — полные правила

**Обязательные пары** (компилятор требует):
```csharp
// == и != — ОБЯЗАТЕЛЬНО вместе
public static bool operator ==(Vector2 a, Vector2 b) => a.X == b.X && a.Y == b.Y;
public static bool operator !=(Vector2 a, Vector2 b) => !(a == b);

// < и > — ОБЯЗАТЕЛЬНО вместе
public static bool operator <(Vector2 a, Vector2 b) => a.Length < b.Length;
public static bool operator >(Vector2 a, Vector2 b) => b < a;

// <= и >= — ОБЯЗАТЕЛЬНО вместе
public static bool operator <=(Vector2 a, Vector2 b) => !(b < a);
public static bool operator >=(Vector2 a, Vector2 b) => !(a < b);

// Equals и GetHashCode — ОБЯЗАТЕЛЬНЫ при ==/!=
public override bool Equals(object? obj) => obj is Vector2 v && this == v;
public override int GetHashCode() => HashCode.Combine(X, Y);
```

**true/false операторы** — для кастомных bool-like типов:
```csharp
public readonly struct Optional<T> {
    private readonly T _value;
    private readonly bool _hasValue;
    
    // Позволяет: if (optional) { ... }
    public static bool operator true(Optional<T> opt) => opt._hasValue;
    public static bool operator false(Optional<T> opt) => !opt._hasValue;
    
    // && и || — короткое замыкание
    public static Optional<T> operator &(Optional<T> a, Optional<T> b) 
        => a._hasValue ? b : a;
    public static Optional<T> operator |(Optional<T> a, Optional<T> b) 
        => a._hasValue ? a : b;
}
```

### 📇 Индексаторы — продвинутые сценарии

**Множественные индексаторы**:
```csharp
public class Matrix {
    private readonly double[,] _data;
    
    public Matrix(int rows, int cols) => _data = new double[rows, cols];
    
    // Два параметра
    public double this[int row, int col] {
        get => _data[row, col];
        set => _data[row, col] = value;
    }
    
    // Через Point
    public double this[Point p] {
        get => _data[p.X, p.Y];
        set => _data[p.X, p.Y] = value;
    }
}
```

**params индексатор (C# 12)**:
```csharp
public class MultiDimArray {
    private readonly Dictionary<string, object> _data = new();
    
    public object this[params int[] indices] {
        get => _data[string.Join(",", indices)];
        set => _data[string.Join(",", indices)] = value;
    }
}

var arr = new MultiDimArray();
arr[1, 2, 3] = "value";  // params int[]
```

**init-only setter (C# 9)**:
```csharp
public class Config {
    private string _value;
    public string Value { 
        get => _value; 
        init => _value = value ?? throw new ArgumentNullException(); 
    }
}
```

### 🎭 Pattern-based API — duck typing для языковых конструкций

**foreach — GetEnumerator**:
```csharp
public class NumberRange {
    private readonly int _start, _end;
    public NumberRange(int start, int end) { _start = start; _end = end; }
    
    public IEnumerator<int> GetEnumerator() {
        for (int i = _start; i <= _end; i++) yield return i;
    }
}

// Использование
foreach (var n in new NumberRange(1, 5)) Console.WriteLine(n);  // 1 2 3 4 5
```

**await — GetAwaiter**:
```csharp
public readonly struct LazyTaskAwaiter<T> : INotifyCompletion {
    private readonly Lazy<Task<T>> _task;
    public LazyTaskAwaiter(Lazy<Task<T>> task) => _task = task;
    public bool IsCompleted => _task.Value.IsCompleted;
    public T GetResult() => _task.Value.Result;
    public void OnCompleted(Action continuation) 
        => _task.Value.ContinueWith(_ => continuation());
}

public class LazyTask<T> {
    private readonly Lazy<Task<T>> _task;
    public LazyTask(Func<Task<T>> factory) => _task = new Lazy<Task<T>>(factory);
    
    public LazyTaskAwaiter<T> GetAwaiter() => new(_task);
}

// Использование
var lazy = new LazyTask<int>(async () => { await Task.Delay(100); return 42; });
var result = await lazy;  // Работает!
```

**using — Dispose / DisposeAsync**:
```csharp
public class ResourceHolder : IAsyncDisposable {
    public async ValueTask DisposeAsync() {
        await CleanupAsync();
    }
}

// using var — неявный using блок
using var resource = new ResourceHolder();  // Автоматический DisposeAsync()
```

**Деконструкция — Deconstruct**:
```csharp
public class Person {
    public string FirstName { get; }
    public string LastName { get; }
    public int Age { get; }
    
    public Person(string first, string last, int age) {
        FirstName = first; LastName = last; Age = age;
    }
    
    // Основной Deconstruct
    public void Deconstruct(out string firstName, out string lastName, out int age) {
        firstName = FirstName; lastName = LastName; age = Age;
    }
    
    // Альтернативный Deconstruct
    public void Deconstruct(out string fullName, out int age) {
        fullName = $"{FirstName} {LastName}"; age = Age;
    }
}

var person = new Person("Alex", "Smith", 30);
var (first, last, age) = person;
var (fullName, age2) = person;
```

**Collection Expressions (C# 12)**:
```csharp
// Любой тип с Add или Create/From
public class MyList<T> {
    private readonly List<T> _inner = new();
    public void Add(T item) => _inner.Add(item);
    public IEnumerator<T> GetEnumerator() => _inner.GetEnumerator();
}

// Использование
MyList<int> list = [1, 2, 3, 4, 5];  // Вызывает Add для каждого!
```
"""
}

LESSON_ENHANCEMENTS[26] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в GC: поколения, LOH, POH, диагностика

### 🗑 Детальная карта памяти

```
Small Object Heap (SOH)                    Large Object Heap (LOH)
┌─────────────────────────────┐           ┌─────────────────────────────┐
│ Gen 0  (~256 KB, частый GC) │           │   Объекты ≥ 85,000 байт     │
│ Gen 1  (~2 MB)              │           │   Массивы, длинные строки   │
│ Gen 2  (неограничен)        │           │   НЕ компактируется*        │
└─────────────────────────────┘           └─────────────────────────────┘
         ↑                                             ↑
    Компактируется                                .NET 5+: CompactOnce

Pinned Object Heap (POH) — .NET 5+
- Объекты через fixed, GCHandle.Alloc(pinned)
- Не двигаются при компактировке
```

### 📊 Эфимерный сегмент (Gen 0, 1) — как работает аллокация

```
Allocation Pointer (NextObjPtr) ──────────►
┌─────────────────────────────────────────────────────────┐
│  Свободная память                                        │
├─────────────────────────────────────────────────────────┤
│  Gen 0 (новые объекты)  ← Allocation Pointer            │
├─────────────────────────────────────────────────────────┤
│  Gen 1 (выжившие)                                       │
├─────────────────────────────────────────────────────────┤
│  Gen 2 (долгоживущие)                                   │
└─────────────────────────────────────────────────────────┘
```

**Быстрая аллокация** (bump pointer):
```csharp
// Очень быстро — просто сдвиг указателя!
// Thread-local allocation contexts (TLA) для многопоточности
var obj = new MyClass();  // ~1-2 нс в Gen 0
```

**Когда происходит Gen 0 GC**:
- Allocation pointer достигает конца Gen 0 сегмента
- Очень быстро (микросекунды), миллионы раз в секунду

### 📦 Large Object Heap (LOH) — детали

**Порог**: 85,000 байт (85 KB)
```csharp
// НЕ в LOH (80 KB)
var small = new double[10000];  // 10000 * 8 = 80,000 байт

// В LOH (88 KB)
var large = new double[11000];  // 11000 * 8 = 88,000 байт
```

**Проблемы LOH**:
1. **Не компактируется** (до .NET 5) → фрагментация
2. **Собирается только при Full GC** (Gen 2)
3. **OutOfMemoryException** при фрагментации даже при свободной памяти

**Решения**:
```csharp
// .NET 5+ — разовая компактировка
GCSettings.LargeObjectHeapCompactionMode = GCLargeObjectHeapCompactionMode.CompactOnce;
await GC.CollectAsync(2, GCCollectionMode.Forced, blocking: true);

// Пулинг для избежания LOH
var buffer = ArrayPool<byte>.Shared.Rent(100000);
try { /* работа */ } 
finally { ArrayPool<byte>.Shared.Return(buffer); }
```

### 📌 Pinned Object Heap (POH) — .NET 5+

```csharp
// Автоматически попадает в POH
fixed (byte* ptr = buffer) { /* ... */ }

// Или вручную
var handle = GCHandle.Alloc(obj, GCHandleType.Pinned);
try { NativeWrite(handle.AddrOfPinnedObject(), size); }
finally { handle.Free(); }  // КРИТИЧНО освободить!

// ПРОБЛЕМА: слишком много pinned объектов → фрагментация SOH/LOH
// РЕШЕНИЕ: минимизируйте время закрепления, используйте ArrayPool
```

### ⚙️ Режимы GC — детальное сравнение

| Параметр | Workstation | Server |
|---|---|---|
| GC Threads | 1 (или 1 фоновый) | 1 на логический CPU |
| Segments | Меньше | Больше (для throughput) |
| Latency | Низкая (для UI) | Выше, но выше throughput |
| Background GC | Опционально | По умолчанию включен |

```xml
<!-- Server GC для ASP.NET Core / высоконагруженных сервисов -->
<ServerGarbageCollection>true</ServerGarbageCollection>
```

### 📊 Диагностика — программный доступ

```csharp
// Память
long total = GC.GetTotalMemory(false);  // Без принудительной сборки
long totalForced = GC.GetTotalMemory(true);  // С Full GC

// Счётчики сборок
int gen0 = GC.CollectionCount(0);
int gen1 = GC.CollectionCount(1);
int gen2 = GC.CollectionCount(2);

// Уведомление о приближающемся Full GC
GC.RegisterForFullGCNotification(10, 10);  // % Gen 2, % LOH
Task.Run(async () => {
    while (true) {
        var status = GC.WaitForFullGCApproach();
        if (status == GCNotificationStatus.Succeeded) {
            // Подготовка: сбросить кэши, освободить память
            await PrepareForFullGCAsync();
        }
        await Task.Delay(1000);
    }
});
```

### 🔧 dotnet-counters / dotnet-trace / PerfView

```bash
# Real-time метрики
dotnet-counters monitor -p <PID> --counters System.Runtime.GC

# ETW трассировка
dotnet-trace collect -p <PID> --providers Microsoft-Windows-DotNETRuntime:4:5 -o trace.nettrace
dotnet-trace convert trace.nettrace --format speedscope  # Открыть в speedscope.app

# PerfView — глубокий анализ
# GC Stats: паузы, поколения, причины
# CPU Stacks: где тратится время
# Memory: кто аллоцирует, GC Roots
```

### ⚠️ Типичные ошибки и анти-паттерны

```csharp
// 1. GC.Collect() в продакшене — НИКОГДА!
GC.Collect();  // Нарушает поколенческую логику, вызывает Full GC

// 2. Финализатор без GC.SuppressFinalize
~MyClass() { _handle.Dispose(); }  // Double dispose, лишняя работа GC
// Правильно:
public void Dispose() {
    _handle.Dispose();
    GC.SuppressFinalize(this);
}

// 3. Большие массивы в цикле без пула
for (int i = 0; i < 1000; i++) {
    var buffer = new byte[100000];  // LOH фрагментация!
}
// Правильно:
var buffer = ArrayPool<byte>.Shared.Rent(100000);
try { /* работа */ } finally { ArrayPool<byte>.Shared.Return(buffer); }

// 4. GCHandle без Free()
var handle = GCHandle.Alloc(obj, GCHandleType.Pinned);
// ... работа ...
handle.Free();  // ОБЯЗАТЕЛЬНО! Иначе утечка pinned памяти

// 5. finalizer без SafeHandle
class Bad {
    private IntPtr _handle = NativeOpen();
    ~Bad() { NativeClose(_handle); }  // Негарантированно!
}
// Правильно: SafeHandle
```
"""
}

LESSON_ENHANCEMENTS[27] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в Networking: HttpClient, gRPC, SignalR

### 🌐 HttpClient — продвинутая настройка

**PooledConnectionLifetime** — критично для DNS изменений:
```csharp
services.AddHttpClient<ApiClient>().ConfigurePrimaryHttpMessageHandler(() => 
    new HttpClientHandler {
        PooledConnectionLifetime = TimeSpan.FromMinutes(5),  // Переподключение каждые 5 мин
        MaxConnectionsPerServer = 100,  // .NET 6+
        AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate,
        UseCookies = false,
    });
```

**SocketsHttpHandler** — низкоуровневый контроль:
```csharp
var handler = new SocketsHttpHandler {
    PooledConnectionLifetime = TimeSpan.FromMinutes(5),
    MaxConnectionsPerServer = 100,
    EnableMultipleHttp2Connections = true,
    ConnectTimeout = TimeSpan.FromSeconds(10),
    Expect100Continue = false,
};
services.AddHttpClient<ApiClient>().ConfigurePrimaryHttpMessageHandler(() => handler);
```

### 🛡 Polly — продвинутые политики

**PolicyWrap — правильный порядок** (внутреннее → внешнее):
```csharp
// ВНУТРИ → НАРУЖУ: Timeout → Bulkhead → CircuitBreaker → Retry → Fallback
var wrapper = Policy.WrapAsync(
    Policy.TimeoutAsync<HttpResponseMessage>(TimeSpan.FromSeconds(10)),           // 1. Timeout
    Policy.BulkheadAsync<HttpResponseMessage>(10, 20),                           // 2. Bulkhead
    HttpPolicyExtensions.HandleTransientHttpError()
        .CircuitBreakerAsync(5, TimeSpan.FromSeconds(30)),                       // 3. Circuit Breaker
    HttpPolicyExtensions.HandleTransientHttpError()
        .WaitAndRetryAsync(3, i => TimeSpan.FromSeconds(Math.Pow(2, i)) + 
            TimeSpan.FromMilliseconds(Random.Shared.Next(100))),                 // 4. Retry + Jitter
    Policy<HttpResponseMessage>.Handle<HttpRequestException>()
        .FallbackAsync(new HttpResponseMessage(HttpStatusCode.ServiceUnavailable)) // 5. Fallback
);
```

**Jitter** — критично для предотвращения thundering herd:
```csharp
// Decorrelated Jitter (рекомендует AWS)
WaitAndRetryAsync(3, retryAttempt => 
    TimeSpan.FromSeconds(Math.Min(30, Math.Pow(2, retryAttempt))) + 
    TimeSpan.FromMilliseconds(Random.Shared.Next(0, 1000)))
```

**Hedging** — параллельные запросы с отменой:
```csharp
var policy = Policy.Handle<HttpRequestException>()
    .OrResult(r => r.StatusCode == HttpStatusCode.RequestTimeout)
    .AdvancedRetryPolicy(3, (attempt, outcome, ctx) => {
        // Запускаем несколько параллельно, принимаем первый успешный
        return new RetryResult(TimeSpan.FromMilliseconds(100), true);
    });
```

### 🔧 gRPC — продвинутые сценарии

**Interceptors** — cross-cutting:
```csharp
public class LoggingInterceptor : Interceptor {
    public override async Task<TResponse> UnaryServerHandler<TRequest, TResponse>(
        TRequest request, ServerCallContext context, 
        UnaryServerMethod<TRequest, TResponse> continuation) {
        
        var stopwatch = Stopwatch.StartNew();
        _logger.LogInformation("gRPC {Method} started", context.Method);
        try {
            return await continuation(request, context);
        } finally {
            stopwatch.Stop();
            _logger.LogInformation("gRPC {Method} completed in {Elapsed}ms", 
                context.Method, stopwatch.ElapsedMilliseconds);
        }
    }
}

// Регистрация
builder.Services.AddGrpc(options => {
    options.Interceptors.Add<LoggingInterceptor>();
});
```

**Deadline Propagation** — передача таймаута:
```csharp
// Клиент передаёт deadline
var call = client.SayHelloAsync(request, deadline: DateTime.UtcNow.AddSeconds(5));

// Сервер проверяет
public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context) {
    if (context.Deadline < DateTime.UtcNow) 
        throw new RpcException(new Status(StatusCode.DeadlineExceeded, "Deadline exceeded"));
    // ...
}
```

**Code-first gRPC (.NET 7+)** — без .proto:
```csharp
[ProtoContract]
public class HelloRequest { [ProtoMember(1)] public string Name { get; set; } }

[ProtoContract]
public class HelloReply { [ProtoMember(1)] public string Message { get; set; } }

[GrpcService]
public interface IGreeter {
    Task<HelloReply> SayHello(HelloRequest request);
}

// Регистрация
builder.Services.AddCodeFirstGrpc();
```

### 🔌 SignalR — масштабирование

**Redis Backplane** — масштабирование на несколько инстансов:
```csharp
builder.Services.AddSignalR()
    .AddStackExchangeRedis("localhost:6379", options => {
        options.Configuration.ChannelPrefix = "myapp";
    });

// Теперь сообщения доставляются на ВСЕ инстансы
await _hub.Clients.All.SendAsync("Message", data);
```

**User Groups** — персональные уведомления:
```csharp
public class NotificationHub : Hub {
    public async Task JoinUserGroup(string userId) 
        => await Groups.AddToGroupAsync(Context.ConnectionId, $"user:{userId}");
    
    public async Task LeaveUserGroup(string userId) 
        => await Groups.RemoveFromGroupAsync(Context.ConnectionId, $"user:{userId}");
}

// Отправка конкретному пользователю
await _hub.Clients.Group($"user:{userId}").SendAsync("Notification", data);
```

**Streaming** — передача больших данных:
```csharp
public async Task DownloadFile(string fileId, IAsyncEnumerable<byte[]> stream) {
    await foreach (var chunk in stream) {
        await Clients.Caller.SendAsync("FileChunk", chunk);
    }
}
```

### 🚦 Rate Limiting — продвинутые алгоритмы

**Token Bucket** — для burst трафика:
```csharp
options.AddTokenBucketLimiter("api", opts => {
    opts.TokenLimit = 100;           // Макс токенов
    opts.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
    opts.QueueLimit = 10;            // Очередь ожидания
    opts.ReplenishmentPeriod = TimeSpan.FromSeconds(10);
    opts.TokensPerPeriod = 20;       // 20 токенов каждые 10 сек
});
```

**Sliding Window Log** — точный контроль:
```csharp
// Хранит timestamps каждого запроса
// Точнее Fixed/Sliding Window, но больше памяти
```

**Distributed Rate Limiting (Redis)**:
```csharp
// Lua скрипт для атомарности
var luaScript = @"
    local current = redis.call('INCR', KEYS[1])
    if current == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
    return current
";
var count = (long)await redis.EvalAsync(luaScript, new RedisKey[] { key }, new RedisValue[] { windowSeconds });
if (count > limit) throw new RateLimitExceededException();
```
"""
}

LESSON_ENHANCEMENTS[28] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в Security: JWT, OAuth2, Crypto, Data Protection

### 🔐 JWT — продвинутые сценарии

**Refresh Tokens с ротацией**:
```csharp
public class TokenService {
    public async Task<TokenResponse> RefreshAsync(string refreshToken, string ipAddress) {
        var stored = await _repo.GetRefreshTokenAsync(refreshToken);
        if (stored == null || stored.IsRevoked || stored.Expires < DateTime.UtcNow)
            throw new SecurityTokenException("Invalid refresh token");
        
        // Ротация: старый refresh token отзывается, выдаются новые
        await _repo.RevokeAsync(refreshToken, ipAddress, "Replaced by new token");
        
        var newAccessToken = GenerateAccessToken(user);
        var newRefreshToken = GenerateRefreshToken(user, ipAddress);
        await _repo.SaveAsync(newRefreshToken);
        
        return new TokenResponse(newAccessToken, newRefreshToken.Token);
    }
}
```

**JWT в Query String для SignalR/WebSockets**:
```csharp
options.Events = new JwtBearerEvents {
    OnMessageReceived = context => {
        var accessToken = context.Request.Query["access_token"];
        var path = context.HttpContext.Request.Path;
        if (!string.IsNullOrEmpty(accessToken) && path.StartsWithSegments("/hubs")) {
            context.Token = accessToken;  // Чтение токена из query string
        }
        return Task.CompletedTask;
    }
};
```

### 🛡 Authorization — Resource-based

```csharp
// Требование
public class DocumentOwnerRequirement : IAuthorizationRequirement { }

// Обработчик
public class DocumentOwnerHandler : AuthorizationHandler<DocumentOwnerRequirement, Document> {
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context, 
        DocumentOwnerRequirement requirement, 
        Document resource) {
        
        if (resource.OwnerId == GetUserId(context.User)) 
            context.Succeed(requirement);
        return Task.CompletedTask;
    }
}

// Использование
[HttpGet("{id}")]
public async Task<IActionResult> Get(int id) {
    var doc = await _repo.GetAsync(id);
    var auth = await _authorizationService.AuthorizeAsync(User, doc, "DocumentOwner");
    if (!auth.Succeeded) return Forbid();
    return Ok(doc);
}
```

### 🔒 Криптография — правильные алгоритмы

**AES-GCM (аутентифицированное шифрование)** — .NET 6+:
```csharp
public static (byte[] ciphertext, byte[] nonce, byte[] tag) Encrypt(byte[] plaintext, byte[] key) {
    var nonce = RandomNumberGenerator.GetBytes(12);  // 96-bit nonce для GCM
    var tag = new byte[16];
    var ciphertext = new byte[plaintext.Length];
    
    using var aes = new AesGcm(key);
    aes.Encrypt(nonce, plaintext, ciphertext, tag);
    return (ciphertext, nonce, tag);
}

public static byte[] Decrypt(byte[] ciphertext, byte[] nonce, byte[] tag, byte[] key) {
    var plaintext = new byte[ciphertext.Length];
    using var aes = new AesGcm(key);
    aes.Decrypt(nonce, ciphertext, tag, plaintext);
    return plaintext;
}
```

**PBKDF2 / Argon2 для паролей**:
```csharp
// .NET встроенный (ASP.NET Core Identity использует PBKDF2)
var hashed = new PasswordHasher<User>().HashPassword(user, password);
var result = new PasswordHasher<User>().VerifyHashedPassword(user, hashed, input);

// Argon2 (рекомендуется для новых проектов)
using Konscious.Security.Cryptography.Argon2;
var argon2 = new Argon2id(Encoding.UTF8.GetBytes(password)) {
    Salt = salt,
    DegreeOfParallelism = 8,
    Iterations = 4,
    MemorySize = 1024 * 1024  // 1 GB
};
var hash = argon2.GetBytes(32);
```

**Data Protection API** — защита токенов:
```csharp
builder.Services.AddDataProtection()
    .PersistKeysToFileSystem(new DirectoryInfo("/app/keys"))
    .SetApplicationName("MyApp")
    .SetDefaultKeyLifetime(TimeSpan.FromDays(90))
    .ProtectKeysWithDpapi();  // Windows DPAPI

// Использование
public class TokenProtector {
    private readonly IDataProtector _protector;
    public TokenProtector(IDataProtectionProvider provider) {
        _protector = provider.CreateProtector("MyApp.Tokens.v1");  // Purpose chain
    }
    public string Protect(string data) => _protector.Protect(data);
    public string Unprotect(string data) => _protector.Unprotect(data);
}
```

### 🌐 Security Headers Middleware

```csharp
app.Use(async (context, next) => {
    context.Response.Headers["X-Content-Type-Options"] = "nosniff";
    context.Response.Headers["X-Frame-Options"] = "DENY";
    context.Response.Headers["X-XSS-Protection"] = "1; mode=block";
    context.Response.Headers["Referrer-Policy"] = "strict-origin-when-cross-origin";
    context.Response.Headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()";
    context.Response.Headers["Content-Security-Policy"] = 
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self'; " +
        "img-src 'self' data:; font-src 'self'; connect-src 'self'; " +
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'";
    context.Response.Headers["Strict-Transport-Security"] = 
        "max-age=31536000; includeSubDomains; preload";
    await next();
});
```
"""
}

LESSON_ENHANCEMENTS[29] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в Observability: OpenTelemetry, Profiling

### 📊 OpenTelemetry Metrics — кастомные метрики

```csharp
public class OrderMetrics {
    private readonly Counter<long> _ordersCreated;
    private readonly Histogram<double> _orderValue;
    private readonly UpDownCounter<long> _activeOrders;
    
    public OrderMetrics(IMeterFactory meterFactory) {
        var meter = meterFactory.Create("MyApp.Metrics");
        _ordersCreated = meter.CreateCounter<long>("orders.created.total", "orders", "Total orders");
        _orderValue = meter.CreateHistogram<double>("order.value", "USD", "Order value distribution");
        _activeOrders = meter.CreateUpDownCounter<long>("orders.active", "orders", "Active orders");
    }
    
    public void OrderCreated(decimal value) {
        _ordersCreated.Add(1);
        _orderValue.Record((double)value);
        _activeOrders.Add(1);
    }
}
```

**Cardinality Rules** — критично для Prometheus:
```csharp
// ПЛОХО — unbounded labels (Prometheus OOM!)
meter.CreateCounter("requests", "requests").Add(1, 
    new("user_id", userId),  // 10000+ уникальных значений!
    new("request_id", Guid.NewGuid()));

// ХОРОШО — bounded labels
meter.CreateCounter("requests", "requests").Add(1,
    new("method", method),      // GET, POST, PUT, DELETE
    new("endpoint", endpoint),  // /api/users, /api/orders
    new("status", status));     // 200, 404, 500
```

### 🔍 Distributed Tracing — ActivitySource

```csharp
public static class AppActivitySource {
    public static readonly ActivitySource Source = new("MyApp.Activities");
}

public class OrderService {
    public async Task<Order> CreateOrderAsync(CreateOrderDto dto) {
        using var activity = AppActivitySource.Source.StartActivity("CreateOrder", ActivityKind.Internal);
        activity?.SetTag("customer.id", dto.CustomerId);
        activity?.SetTag("items.count", dto.Items.Count);
        
        // Baggage — передача через контекст
        Baggage.Current.SetBaggage("user.id", dto.CustomerId.ToString());
        
        var order = await _repo.CreateAsync(dto);
        activity?.SetTag("order.id", order.Id);
        activity?.SetStatus(ActivityStatusCode.Ok);
        return order;
    }
}
```

**W3C TraceContext Propagation**:
```http
# Автоматически добавляются/читаются
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
tracestate: vendor=value
baggage: user.id=123,correlation.id=abc
```

### ⚡ Профилирование — dotnet-trace, PerfView, BenchmarkDotNet

**BenchmarkDotNet — правильные бенчмарки**:
```csharp
[MemoryDiagnoser]
[DisassemblyDiagnoser(exportHtml: true, exportDiff: true)]
[SimpleJob(RuntimeMoniker.Net80)]
[SimpleJob(RuntimeMoniker.Net90)]
public class StringBenchmarks {
    private const int N = 1000;
    
    [Benchmark(Baseline = true)]
    public string StringBuilder() {
        var sb = new StringBuilder();
        for (int i = 0; i < N; i++) sb.Append(i);
        return sb.ToString();
    }
    
    [Benchmark]
    public string StringConcat() {
        string s = "";
        for (int i = 0; i < N; i++) s += i;
        return s;
    }
}

// Запуск
BenchmarkRunner.Run<StringBenchmarks>();
```

**dotnet-trace — ETW профилирование**:
```bash
# Сборка с символами
dotnet publish -c Release -p:DebugType=portable -p:DebugSymbols=true

# Сбор трассировки
dotnet-trace collect --process-id <PID> \
  --providers Microsoft-Windows-DotNETRuntime:4:5 \
  --providers Microsoft-DotNETCore-SampleProfiler:4:5 \
  -o trace.nettrace

# Конвертация для Speedscope
dotnet-trace convert trace.nettrace --format speedscope
# Открыть в https://speedscope.app
```

**PerfView — глубокий анализ**:
- GC Stats: паузы, поколения, причины GC
- CPU Stacks: где тратится время (JIT, GC, ваш код)
- Memory: аллокации по типам/стекам, GC Roots
- File I/O, Network, Lock Contention
"""
}

LESSON_ENHANCEMENTS[30] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в Cloud Native: Docker, Kubernetes, Service Mesh

### 🐳 Docker — продвинутая оптимизация

**Multi-stage с кэшированием NuGet**:
```dockerfile
# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# 1. Копируем ТОЛЬКО csproj файлы для кэширования restore
COPY *.sln .
COPY src/*/*.csproj ./src/
RUN dotnet restore

# 2. Копируем исходный код и билдим
COPY . .
RUN dotnet publish src/MyApp.Api/MyApp.Api.csproj -c Release -o /app/publish --no-restore

# Stage 2: Runtime (Distroless)
FROM mcr.microsoft.com/dotnet/aspnet:8.0-distroless AS runtime
WORKDIR /app
USER 65532:65532
COPY --from=build --chown=65532:65532 /app/publish .
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
ENTRYPOINT ["dotnet", "MyApp.Api.dll"]
```

**.dockerignore — критично для скорости**:
```dockerignore
**/bin
**/obj
**/.git
**/.vs
**/.idea
**/*.md
**/Dockerfile*
**/docker-compose*
**/tests
**/TestResults
```

### ☸️ Kubernetes — продвинутые манифесты

**HPA с кастомными метриками**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

**PodDisruptionBudget** — доступность при обновлениях:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: myapp
```

### ⛵ Helm — продвинутые чарты

**Values с condition**:
```yaml
# values.yaml
postgresql:
  enabled: true
  auth:
    database: myapp

redis:
  enabled: false  # Можно включить в values-prod.yaml
```

**Chart.yaml с зависимостями**:
```yaml
dependencies:
- name: postgresql
  version: "12.x.x"
  repository: "https://charts.bitnami.com/bitnami"
  condition: postgresql.enabled
```

### 🕸 Service Mesh — Istio

**mTLS и Traffic Splitting**:
```yaml
# DestinationRule
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL  # mTLS

---
# VirtualService — Canary Deployment
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts: [myapp]
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: myapp
        subset: v2
      weight: 100
  - route:
    - destination:
        host: myapp
        subset: v1
      weight: 100
```

### 🔄 CI/CD — GitHub Actions + ArgoCD

**Multi-arch build**:
```yaml
- name: Build and Push
  uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}/api:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**ArgoCD Application**:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myapp-config
    targetRevision: HEAD
    path: overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```
"""
}

LESSON_ENHANCEMENTS[31] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в производительность: SIMD, PGO, NativeAOT

### ⚡ SIMD — Hardware Intrinsics

**Vector<T> — переносимая абстракция**:
```csharp
// Сумма массива
public static float SumVector(float[] data) {
    Vector<float> sum = Vector<float>.Zero;
    int i = 0;
    for (; i <= data.Length - Vector<float>.Count; i += Vector<float>.Count) {
        var v = new Vector<float>(data, i);
        sum += v;
    }
    // Хвост
    float scalarSum = 0;
    for (; i < data.Length; i++) scalarSum += data[i];
    return Vector.Sum(sum) + scalarSum;
}
```

**AVX2 — прямые инструкции**:
```csharp
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;

public static float SumAvx2(float[] data) {
    if (!Avx2.IsSupported) return SumVector(data);  // Fallback!
    
    Vector256<float> sum = Vector256<float>.Zero;
    int i = 0;
    for (; i <= data.Length - 8; i += 8) {
        sum = Avx2.Add(sum, Avx2.LoadVector256(data.AsSpan(i)));
    }
    
    // Horizontal add
    var sum128 = Avx.Add(sum.GetLower(), sum.GetUpper());
    sum128 = Avx.Add(sum128, Avx2.Permute(sum128, 0b11101110));
    sum128 = Avx.Add(sum128, Avx.Permute(sum128, 0b01010101));
    return sum128.GetElement(0);
}
```

**Arm64 NEON**:
```csharp
using System.Runtime.Intrinsics.Arm;

public static float SumNeon(float[] data) {
    if (!AdvSimd.IsSupported) return SumVector(data);
    Vector128<float> sum = Vector128<float>.Zero;
    for (int i = 0; i <= data.Length - 4; i += 4) {
        sum = AdvSimd.Add(sum, AdvSimd.LoadVector128(data.AsSpan(i)));
    }
    // Horizontal add...
    return sum.GetElement(0);
}
```

**Проверка поддержки**:
```csharp
// Всегда проверяйте!
if (Avx2.IsSupported) { /* AVX2 код */ }
else if (Sse.IsSupported) { /* SSE код */ }
else { /* Скалярный fallback */ }
```

### 🎯 PGO — Profile-Guided Optimization

**Dynamic PGO (.NET 8+)** — просто включите:
```xml
<PropertyGroup>
  <TieredCompilation>true</TieredCompilation>
  <TieredPGO>true</TieredPGO>
</PropertyGroup>
```

**Static PGO** — требует профилирования:
```bash
# 1. Инструментированная сборка
dotnet build -c Release /p:OptimizePGOInstrument=true

# 2. Запуск под РЕАЛЬНОЙ нагрузкой
dotnet run --project MyApp

# 3. Оптимизированная сборка
dotnet build -c Release /p:OptimizePGOTrain=true
```

### 🚀 NativeAOT — нативный бинарь

```xml
<PropertyGroup>
  <PublishAot>true</PublishAot>
  <StripSymbols>true</StripSymbols>
  <IlcGenerateStackTraceData>false</IlcGenerateStackTraceData>
  <IlcOptimizationPreference>Speed</IlcOptimizationPreference>
</PropertyGroup>

# Публикация
dotnet publish -c Release -r linux-x64 --self-contained true
```

**Ограничения NativeAOT**:
- Нет рефлексии (System.Reflection)
- Нет динамической загрузки сборок (Assembly.Load)
- Нет JIT компиляции
- Нет динамического кода (Expression.Compile, DynamicMethod)
- Больше размер бинаря

**Когда использовать**:
- CLI инструменты (быстрый старт)
- Serverless / AWS Lambda (cold start)
- Edge / IoT устройства
- Security-critical (меньше attack surface)

### 📊 BenchmarkDotNet — правильные бенчмарки

```csharp
[MemoryDiagnoser]
[DisassemblyDiagnoser(exportHtml: true, exportDiff: true)]
[SimpleJob(RuntimeMoniker.Net80)]
[SimpleJob(RuntimeMoniker.Net90)]
public class StringBenchmarks {
    private const int N = 1000;
    
    [Benchmark(Baseline = true)]
    public string StringBuilder() {
        var sb = new StringBuilder();
        for (int i = 0; i < N; i++) sb.Append(i);
        return sb.ToString();
    }
    
    [Benchmark]
    public string StringConcat() {
        string s = "";
        for (int i = 0; i < N; i++) s += i;
        return s;
    }
    
    [GlobalSetup]
    public void Setup() { /* прогрев */ }
}

BenchmarkRunner.Run<StringBenchmarks>();
```

**Анализ результатов**:
```
| Method         | Mean      | Gen0   | Allocated |
|---------------|-----------|--------|-----------|
| StringBuilder | 45.2 us   | 3.5 KB | 14 KB     |
| StringConcat  | 1,250 us  | 150 KB | 600 KB    |
```
"""
}

LESSON_ENHANCEMENTS[32] = {
    "additional_content_md": """
## 🔍 Глубокое погружение в продвинутые паттерны: Functional C#, Rx.NET, Actors

### 🧮 Functional C# — Railway-oriented programming

```csharp
// Result<T> — успех или ошибка
public readonly struct Result<T> {
    private readonly T _value;
    private readonly Error _error;
    private readonly bool _isSuccess;
    
    public static Result<T> Success(T value) => new(value);
    public static Result<T> Failure(Error error) => new(error);
    
    public bool IsSuccess => _isSuccess;
    public T Value => _isSuccess ? _value : throw new InvalidOperationException();
    public Error Error => !_isSuccess ? _error : throw new InvalidOperationException();
    
    // Map — трансформация при успехе
    public Result<TResult> Map<TResult>(Func<T, TResult> mapper)
        => _isSuccess ? Result<TResult>.Success(mapper(_value)) : Result<TResult>.Failure(_error);
    
    // Bind / FlatMap — цепочка
    public Result<TResult> Bind<TResult>(Func<T, Result<TResult>> binder)
        => _isSuccess ? binder(_value) : Result<TResult>.Failure(_error);
    
    // Match — pattern matching
    public TResult Match<TResult>(Func<T, TResult> success, Func<Error, TResult> failure)
        => _isSuccess ? success(_value) : failure(_error);
}

// Railway-oriented validation
public Result<Order> PlaceOrder(PlaceOrderCommand cmd) =>
    ValidateCommand(cmd)
    .Bind(CheckInventory)
    .Bind(ReserveItems)
    .Bind(CalculateTotal)
    .Bind(ProcessPayment)
    .Bind(CreateOrder)
    .Bind(SendConfirmation);
```

### 🔄 Rx.NET — Reactive Extensions

**IObservable<T> — push-базированные последовательности**:
```csharp
var observable = Observable.Create<int>(observer => {
    for (int i = 0; i < 10; i++) {
        observer.OnNext(i);
        Thread.Sleep(100);
    }
    observer.OnCompleted();
    return Disposable.Empty;
});

var subscription = observable
    .Where(x => x % 2 == 0)
    .Buffer(TimeSpan.FromSeconds(1))
    .Select(batch => batch.Average())
    .Subscribe(avg => Console.WriteLine($"Avg: {avg}"));

subscription.Dispose();  // Всегда Dispose!
```

**Backpressure** — контроль скорости:
```csharp
// Producer быстрее Consumer
var fast = Observable.Interval(TimeSpan.FromMilliseconds(10));
var slow = fast
    .Buffer(TimeSpan.FromSeconds(1))
    .Select(batch => batch.Average())
    .ObserveOn(TaskPoolScheduler.Default)
    .Subscribe(Process);
```

### 🎭 Actor Model — Akka.NET и Orleans

**Akka.NET — классическая модель**:
```csharp
public class OrderActor : ReceiveActor {
    private OrderState _state = new();
    
    public OrderActor() {
        Command<PlaceOrder>(Handle);
        Command<GetOrder>(cmd => Sender.Tell(_state));
        
        // Persistence (Event Sourcing)
        Recover<OrderPlaced>(e => _state = _state.Apply(e));
    }
    
    private void Handle(PlaceOrder cmd) {
        var evt = new OrderPlaced(cmd.OrderId, cmd.Items, DateTime.UtcNow);
        Persist(evt, e => {
            _state = _state.Apply(e);
            Sender.Tell(new OrderConfirmed(cmd.OrderId));
        });
    }
}

// Supervision — отказоустойчивость
protected override SupervisorStrategy SupervisorStrategy()
    => new OneForOneStrategy(
        maxNrOfRetries: 3,
        withinTimeRange: TimeSpan.FromMinutes(1),
        localOnlyDecider: ex => ex switch {
            SqlException => Directive.Restart,
            ArgumentException => Directive.Stop,
            _ => Directive.Escalate
        });
```

**Orleans — Virtual Actors (Grains)**:
```csharp
public interface IOrderGrain : IGrainWithIntegerKey {
    Task<OrderResult> PlaceOrder(PlaceOrderCommand cmd);
    Task<OrderState> GetOrder();
}

public class OrderGrain : Grain, IOrderGrain {
    private readonly IPersistentState<OrderState> _state;
    
    public OrderGrain([PersistentState("order", "storage")] IPersistentState<OrderState> state) {
        _state = state;
    }
    
    public async Task<OrderResult> PlaceOrder(PlaceOrderCommand cmd) {
        _state.State = _state.State.Apply(new OrderPlaced(cmd.OrderId, cmd.Items));
        await _state.WriteStateAsync();
        return OrderResult.Success(cmd.OrderId);
    }
}
```

### 🔄 Продвинутые паттерны надежности

**Circuit Breaker**:
```csharp
public class CircuitBreaker {
    private int _failures;
    private CircuitState _state = CircuitState.Closed;
    
    public async Task<T> ExecuteAsync<T>(Func<Task<T>> action) {
        if (_state == CircuitState.Open) {
            if (DateTime.UtcNow - _lastFailure > _timeout) _state = CircuitState.HalfOpen;
            else throw new CircuitBreakerOpenException();
        }
        try {
            var result = await action();
            OnSuccess(); return result;
        } catch { OnFailure(); throw; }
    }
}
```

**Saga — распределенная транзакция**:
```csharp
public async Task ExecuteAsync(CreateOrderSagaData data) {
    var compensations = new Stack<Func<Task>>();
    try {
        await _inventory.ReserveAsync(data.Items);
        compensations.Push(() => _inventory.ReleaseAsync(data.Items));
        
        await _payment.ChargeAsync(data.PaymentInfo);
        compensations.Push(() => _payment.RefundAsync(data.PaymentInfo));
        
        await _order.CreateAsync(data);
    } catch {
        while (compensations.Count > 0) 
            await compensations.Pop()();  // Compensate в обратном порядке
        throw;
    }
}
```

**Event Sourcing**:
```csharp
public class Account : EventSourcedAggregate {
    public decimal Balance { get; private set; }
    
    public void Deposit(decimal amount) => Apply(new MoneyDeposited(Id, amount));
    
    protected override void When(object @event) {
        switch (@event) {
            case MoneyDeposited e: Balance += e.Amount; break;
            case MoneyWithdrawn e: Balance -= e.Amount; break;
        }
    }
}
```
"""
}

LESSON_ENHANCEMENTS[33] = {
    "additional_content_md": """
## 🔍 Финальный проект — глубокий разбор архитектуры

### 🏗 Clean Architecture — детальная структура

```
src/
├── TaskManager.Domain/          # Domain Layer
│   ├── Entities/                # Task, User, Project (Aggregate Roots)
│   ├── ValueObjects/            # TaskId, UserId, Email, TaskStatus
│   ├── Events/                  # Domain Events: TaskCreated, TaskAssigned
│   ├── Repositories/            # Interfaces: ITaskRepository
│   └── Exceptions/              # Domain Exceptions
│
├── TaskManager.Application/     # Application Layer
│   ├── Commands/                # CreateTask, AssignTask, CompleteTask
│   ├── Queries/                 # GetTask, GetTasks, GetProject
│   ├── Handlers/                # MediatR Handlers
│   ├── Validators/              # FluentValidation
│   ├── DTOs/                    # TaskDto, ProjectDto, UserDto
│   ├── Mappers/                 # Mapster profiles
│   ├── Behaviors/               # Pipeline: Validation, Transaction, Logging
│   └── Interfaces/              # IEmailService, INotificationService
│
├── TaskManager.Infrastructure/  # Infrastructure Layer
│   ├── Persistence/             # EF Core DbContext, Migrations, Repositories
│   ├── Services/                # EmailService, SignalRNotificationService
│   ├── Identity/                # JWT TokenService, RefreshTokenService
│   ├── BackgroundJobs/          # Hangfire: Reminders, Cleanup
│   └── Configuration/           # Options, DI Registration
│
├── TaskManager.Api/             # Presentation Layer
│   ├── Endpoints/               # Minimal API (MapGroup)
│   ├── Hubs/                    # TaskHub (SignalR)
│   ├── Middleware/              # ExceptionHandling, RateLimiting
│   ├── Program.cs               # Composition Root
│   └── appsettings.json
│
├── TaskManager.Client/          # Blazor WebAssembly
│   ├── Pages/                   # Tasks.razor, Projects.razor
│   ├── Components/              # TaskCard, TaskForm
│   ├── Services/                # ApiClient, SignalRClient, AuthStateProvider
│   └── State/                   # Flux/Redux state management
│
└── Tests/
    ├── Unit/                    # xUnit, Moq, FluentAssertions
    ├── Integration/             # Testcontainers, WebApplicationFactory
    └── E2E/                     # Playwright
```

### 🎯 Domain — Aggregate с Domain Events

```csharp
public class Task : AggregateRoot<TaskId> {
    public string Title { get; private set; }
    public TaskStatus Status { get; private set; }
    public UserId? AssigneeId { get; private set; }
    public ProjectId ProjectId { get; private set; }
    
    public static Task Create(TaskId id, string title, ProjectId projectId, UserId creatorId) {
        var task = new Task { Id = id, Title = title, ProjectId = projectId, Status = TaskStatus.Backlog };
        task.AddDomainEvent(new TaskCreatedEvent(task.Id, task.Title, projectId, creatorId));
        return task;
    }
    
    public void Assign(UserId userId) {
        if (Status == TaskStatus.Done) throw new InvalidOperationException("Cannot assign completed task");
        AssigneeId = userId;
        AddDomainEvent(new TaskAssignedEvent(Id, userId));
    }
    
    public void Complete() {
        if (Status != TaskStatus.InReview) throw new InvalidOperationException("Must be in review");
        Status = TaskStatus.Done;
        AddDomainEvent(new TaskCompletedEvent(Id));
    }
}
```

### ⚔️ Application — CQRS + MediatR

```csharp
// Command
public record CreateTaskCommand(string Title, string Description, Guid ProjectId) : IRequest<TaskId>;

public class CreateTaskHandler : IRequestHandler<CreateTaskCommand, TaskId> {
    private readonly ITaskRepository _repo;
    private readonly IUnitOfWork _uow;
    private readonly ICurrentUserService _currentUser;
    
    public async Task<TaskId> Handle(CreateTaskCommand cmd, CancellationToken ct) {
        var task = Task.Create(TaskId.New(), cmd.Title, cmd.Description, new ProjectId(cmd.ProjectId), _currentUser.UserId!);
        await _repo.AddAsync(task, ct);
        await _uow.SaveChangesAsync(ct);
        return task.Id;
    }
}

// Pipeline Behaviors
public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> {
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct) {
        var failures = _validators.Select(v => v.Validate(new ValidationContext<TRequest>(request)))
            .SelectMany(r => r.Errors).Where(e => e != null).ToList();
        if (failures.Any()) throw new ValidationException(failures);
        return await next();
    }
}
```

### 🗄 Infrastructure — EF Core + Outbox Pattern

```csharp
public class AppDbContext : DbContext {
    public DbSet<Task> Tasks => Set<Task>();
    
    protected override void OnModelCreating(ModelBuilder model) {
        model.Entity<OutboxMessage>(e => {
            e.HasKey(m => m.Id);
            e.Property(m => m.Type).HasMaxLength(200);
            e.Property(m => m.Content).HasColumnType("jsonb");
        });
    }
    
    public override async Task<int> SaveChangesAsync(CancellationToken ct = default) {
        // Dispatch Domain Events -> Outbox
        var entities = ChangeTracker.Entries<IAggregateRoot>()
            .Select(e => e.Entity).Where(e => e.DomainEvents.Any()).ToList();
        
        foreach (var entity in entities) {
            foreach (var domainEvent in entity.DomainEvents) {
                OutboxMessages.Add(new OutboxMessage {
                    Id = Guid.NewGuid(),
                    Type = domainEvent.GetType().AssemblyQualifiedName!,
                    Content = JsonSerializer.Serialize(domainEvent),
                    CreatedAt = DateTime.UtcNow
                });
            }
            entity.ClearDomainEvents();
        }
        return await base.SaveChangesAsync(ct);
    }
}
```

### 🔌 SignalR — Real-time

```csharp
[Authorize]
public class TaskHub : Hub {
    public async Task JoinProject(string projectId) 
        => await Groups.AddToGroupAsync(Context.ConnectionId, $"project-{projectId}");
}

public class SignalRNotificationService : INotificationService {
    private readonly IHubContext<TaskHub> _hub;
    
    public async Task NotifyTaskCreated(TaskDto task) 
        => await _hub.Clients.Group($"project-{task.ProjectId}").SendAsync("TaskCreated", task);
}
```

### 🌐 API — Minimal API

```csharp
var api = app.MapGroup("/api").RequireAuthorization();

api.MapGet("/tasks", async (ISender sender, Guid projectId) => 
    Results.Ok(await sender.Send(new GetTasksQuery(projectId))));

api.MapPost("/tasks", async (ISender sender, CreateTaskCommand cmd) => 
    Results.Created($"/api/tasks/{await sender.Send(cmd)}", null));

api.MapPut("/tasks/{id}/assign", async (ISender sender, Guid id, AssignTaskCommand cmd) => {
    await sender.Send(cmd with { TaskId = new TaskId(id) });
    return Results.NoContent();
});
```

### 🌐 Blazor Client — SignalR Integration

```csharp
public class TaskSignalRService {
    private HubConnection? _connection;
    public event Action<TaskDto>? OnTaskCreated;
    
    public async Task StartAsync(string token) {
        _connection = new HubConnectionBuilder()
            .WithUrl("https://api/hubs/tasks", options => {
                options.AccessTokenProvider = () => Task.FromResult(token)!;
            })
            .WithAutomaticReconnect()
            .Build();
        
        _connection.On<TaskDto>("TaskCreated", dto => OnTaskCreated?.Invoke(dto));
        await _connection.StartAsync();
    }
}
```

### 🧪 Tests — Testcontainers

```csharp
public class TasksApiTests : IClassFixture<DatabaseFixture> {
    private readonly HttpClient _client;
    
    public TasksApiTests(DatabaseFixture fixture) {
        _fixture = fixture;
        var factory = new WebApplicationFactory<Program>()
            .WithWebHostBuilder(builder => {
                builder.ConfigureServices(services => {
                    services.RemoveAll<DbContextOptions<AppDbContext>>();
                    services.AddDbContext<AppDbContext>(opt => 
                        opt.UseNpgsql(_fixture.ConnectionString));
                });
            });
        _client = factory.CreateClient();
    }
    
    [Fact]
    public async Task CreateTask_ReturnsCreated() {
        var token = await GetAuthTokenAsync();
        _client.DefaultRequestHeaders.Authorization = new("Bearer", token);
        
        var response = await _client.PostAsJsonAsync("/api/tasks", new {
            Title = "Test Task", ProjectId = _fixture.TestProjectId
        });
        response.StatusCode.Should().Be(HttpStatusCode.Created);
    }
}
```

### 🐳 Docker — Multi-stage Distroless

```dockerfile
# Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY *.sln .
COPY src/*/*.csproj ./src/
RUN dotnet restore
COPY . .
RUN dotnet publish src/TaskManager.Api/TaskManager.Api.csproj -c Release -o /app/publish --no-restore

# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0-distroless AS runtime
WORKDIR /app
USER 65532:65532
COPY --from=build --chown=65532:65532 /app/publish .
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
ENTRYPOINT ["dotnet", "TaskManager.Api.dll"]
```

### ⛵ Helm — Production Values

```yaml
replicaCount: 3
image:
  repository: ghcr.io/myorg/taskmanager
  tag: "1.0.0"
service:
  type: ClusterIP
  port: 80
ingress:
  enabled: true
  hosts:
  - host: tasks.example.com
    paths: ["/"]
  tls:
  - secretName: tasks-tls
    hosts: [tasks.example.com]
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
postgresql:
  enabled: true
redis:
  enabled: true
```

### 🔄 CI/CD — GitHub Actions + ArgoCD

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-dotnet@v4
    - run: dotnet test --no-build -c Release
  
  docker:
    needs: test
    steps:
    - uses: docker/build-push-action@v5
      with:
        push: true
        tags: ghcr.io/${{ github.repository }}/api:${{ github.sha }}
  
  deploy:
    needs: docker
    if: github.ref == 'refs/heads/main'
    run: |
      kubectl set image deployment/taskmanager-api taskmanager-api=ghcr.io/...:${{ github.sha }}
      kubectl rollout status deployment/taskmanager-api --timeout=300s
```
"""
}

# Apply enhancements to all lessons 15-33
for i in range(15, 34):
    path = f'fixtures/lessons/csharp/{i:02d}.json'
    if not Path(path).exists():
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if i in LESSON_ENHANCEMENTS:
        enhancement = LESSON_ENHANCEMENTS[i]["additional_content_md"]
        blocks = process_markdown(enhancement)
        data['content_blocks'].extend(blocks)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
        
        print(f"Enhanced lesson {i:02d} with {len(blocks)} additional blocks")

print("Enhancement complete!")