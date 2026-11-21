#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add pedagogical explanations to lessons 15-33: what examples show, where used, term definitions."""

import json
import re
from pathlib import Path

# ============================================================
# MARKDOWN PROCESSING FUNCTIONS
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


# ============================================================
# PEDAGOGICAL ENHANCEMENTS FOR LESSONS 15-33
# Each lesson gets additional markdown with:
# - "🎯 Что показывает этот пример" after code blocks
# - "📍 Где это используется в реальных проектах" sections
# - "📖 Термин: ..." definitions right after first use
# ============================================================

PEDAGOGICAL = {
    15: """
## 🎓 Педагогические дополнения к LINQ

### 📖 Термин: **Отложенное выполнение (Deferred Execution)**
> **Определение**: Запрос LINQ не выполняется в момент создания, а только когда вы начинаете перебирать результаты (через `foreach`, `ToList()`, `ToArray()`, `Count()` и т.д.).
> 
> **Почему это важно**: Это позволяет строить запросы поэтапно, комбинировать их, и выполнять только когда нужны данные. Но это также значит, что если исходная коллекция изменится между созданием запроса и его выполнением — результат будет от новой коллекции.

### 📖 Термин: **Streaming (потоковые) операторы**
> **Определение**: Операторы, которые обрабатывают элементы по одному и сразу передают дальше (`Where`, `Select`, `SelectMany`). Они не накапливают все элементы в памяти.
> 
> **Пример**: `Where` — как только нашёл подходящий элемент, сразу отдаёт его дальше.

### 📖 Термин: **Buffering (буферизующие) операторы**
> **Определение**: Операторы, которым нужны ВСЕ элементы сразу для работы (`OrderBy`, `GroupBy`, `Reverse`, `Distinct`). Они читают всю последовательность в память.
> 
> **Пример**: `OrderBy` не может отдать первый элемент, пока не прочитает все и не отсортирует.

### 🎯 Что показывает пример с `Where` перед `OrderBy`
```csharp
// ПЛОХО: сначала сортируем ВСЁ, потом фильтруем
var bad = hugeCollection.OrderBy(x => x.Date).Where(x => x.Active).Take(10);

// ХОРОШО: сначала фильтруем (streaming), потом сортируем малое количество
var good = hugeCollection.Where(x => x.Active).OrderBy(x => x.Date).Take(10);
```
**Что демонстрирует**: Разницу в производительности на порядки. В первом случае сортируем миллионы элементов, во втором — только тысячи отфильтрованных.

**Где используется**: В любых запросах к большим коллекциям, базам данных, логам, телеметрии.

### 🎯 Что показывает пример с `IQueryable` vs `IEnumerable`
```csharp
// IEnumerable — выполняется В ПАМЯТИ (клиентская фильтрация)
var usersInMemory = GetUsers();
var filtered = usersInMemory.Where(u => u.Age > 18);  // Func<User, bool>

// IQueryable — переводится в SQL (серверная фильтрация)
var usersInDb = dbContext.Users;
var filteredDb = usersInDb.Where(u => u.Age > 18);  // Expression<Func<User, bool>>
```
**Что демонстрирует**: Как один и тот же синтаксис `Where` работает по-разному в зависимости от типа коллекции.

**Где используется**: В Entity Framework Core, LINQ to SQL, любых ORM. Критично для производительности — неверный выбор загрузит всю таблицу в память.

### 📖 Термин: **Expression Tree (дерево выражений)**
> **Определение**: Структура данных, представляющая код в виде дерева объектов, которую можно проанализировать, изменить и скомпилировать. Используется EF Core для перевода C# кода в SQL.

### 🎯 Что показывает пример с замыканием в цикле
```csharp
// ПРОБЛЕМА: все функции замыкаются на ОДНОЙ переменной i
for (int i = 0; i < 10; i++) {
    queries.Add(x => x > i);  // В конце i = 10!
}

// РЕШЕНИЕ: локальная копия
for (int i = 0; i < 10; i++) {
    int local = i;  // Копия для каждой итерации
    queries.Add(x => x > local);
}
```
**Что демонстрирует**: Классическую ловушку замыканий — переменная цикла захватывается по ссылке, а не по значению.

**Где используется**: В любом коде с лямбдами в циклах: фильтры, колбэки, динамическое построение запросов.

---

### 📍 Резюме: где применяется LINQ в реальных проектах
- **Фильтрация/проекция данных** из БД (EF Core), API ответов, конфигов
- **ETL пайплайны** — трансформация данных между системами
- **Аналитика/отчёты** — группировки, агрегации, joins
- **In-memory обработка** — кэши, очереди, кэширование
""",

    16: """
## 🎓 Педагогические дополнения к коллекциям

### 📖 Термин: **Амортизированная сложность O(1)**
> **Определение**: Операция в среднем занимает постоянное время, хотя отдельные вызовы могут быть медленнее. Для `List.Add`: обычно O(1), но когда массив переполняется — происходит реаллокация O(n), что в среднем даёт O(1).

### 📖 Термин: **Capacity vs Count**
> - **Count** — сколько элементов сейчас в коллекции
> - **Capacity** — сколько памяти выделено под капотом (всегда ≥ Count)
> - При `Add` при превышении Capacity происходит реаллокация (создание нового массива + копирование)

### 🎯 Что показывает пример с `Capacity`
```csharp
var list = new List<int>();
list.Add(1);    // Capacity = 4 (первая аллокация)
list.Add(2);    // Capacity = 4
list.Add(3);    // Capacity = 4
list.Add(4);    // Capacity = 4
list.Add(5);    // Capacity = 8 — РЕАЛЛОКАЦИЯ! Копирование 4 элементов

// Оптимизация: задайте Capacity заранее
var list = new List<int>(10000);  // Никаких реаллокаций при 10000 Add
```
**Что демонстрирует**: Как избежать лишних аллокаций и копирований.

**Где используется**: В высоконагруженных системах, парсерах больших файлов, batch processing, когда известно приблизительное количество элементов.

### 📖 Термин: **Хеш-таблица (Hash Table)**
> **Определение**: Структура данных, хранящая пары ключ-значение в массиве «корзин» (buckets). Ключ преобразуется хеш-функцией в индекс корзины. Коллизии (разные ключи → одна корзина) решаются цепочками.

### 🎯 Что показывает пример с `GetHashCode`/`Equals`
```csharp
// ПЛОХО: mutable ключ
var dict = new Dictionary<List<int>, string>();
var key = new List<int> { 1, 2 };
dict[key] = "value";
key.Add(3);  // Хеш изменился! Элемент "потерян" в словарь
dict[key];   // KeyNotFoundException

// ХОРОШО: immutable ключ (record, struct)
var dict = new Dictionary<Point, string>();  // Point — record struct
dict[new Point(1, 2)] = "value";  // Безопасно
```
**Что демонстрирует**: Почему ключи словаря должны быть неизменяемыми.

**Где используется**: В любых словарях, кэшах, индексах, где ключи — объекты.

### 🎯 Что показывает пример с `ImmutableList` + `Builder`
```csharp
// ПЛОХО: 100000 аллокаций!
var immutable = ImmutableList.Create<int>();
for (int i = 0; i < 100000; i++) {
    immutable = immutable.Add(i);  // Каждый раз новый объект!
}

// ХОРОШО: Builder pattern
var builder = ImmutableList.CreateBuilder<int>();
for (int i = 0; i < 100000; i++) {
    builder.Add(i);  // Мутирует внутренний массив
}
var immutable = builder.ToImmutable();  // Одно создание
```
**Что демонстрирует**: Паттерн Builder для пакетных изменений immutable коллекций.

**Где используется**: Функциональное программирование, потокобезопасные кэши, конфигурации, event sourcing.

### 📖 Термин: **Ref struct (ref-структура)**
> **Определение**: Структура, которая может жить ТОЛЬКО в стеке, не может быть полем класса, захвачена в замыкании, использована в `async` методах. Примеры: `Span<T>`, `Memory<T>` (Memory — не ref struct, но связан).

### 🎯 Что показывает пример с `Span<T>` парсингом
```csharp
// ПАРСИНГ БЕЗ АЛЛОКАЦИЙ
public static bool TryParseInt(ReadOnlySpan<char> span, out int value) {
    value = 0;
    foreach (var c in span) {
        if (c < '0' || c > '9') return false;
        value = value * 10 + (c - '0');
    }
    return true;
}

// Использование — никаких Substring!
ReadOnlySpan<char> input = "12345".AsSpan();
TryParseInt(input, out int val);  // 0 аллокаций!
```
**Что демонстрирует**: Парсинг без создания промежуточных строк.

**Где используется**: Парсеры CSV/JSON/логов, сетевые протоколы, высоконагруженные парсеры.

### 📖 Термин: **Lock striping (полосатые блокировки)**
> **Определение**: Техника в `ConcurrentDictionary` — вместо одной глобальной блокировки используется массив блокировок (обычно 32-64), каждая защищает свою часть корзин. Это позволяет параллельно работать с разными ключами.

---

### 📍 Резюме: выбор коллекции
| Задача | Коллекция | Почему |
|--------|-----------|--------|
| Обычный список, Add в конец | `List<T>` | O(1) амортиз., кэш-френдли |
| Частый Insert/Remove в середине | `LinkedList<T>` | O(1) если есть узел |
| Поиск по ключу | `Dictionary<TKey, TValue>` | O(1) среднее |
| Уникальные значения, проверка вхождения | `HashSet<T>` | O(1) |
| FIFO очередь | `Queue<T>` | O(1) |
| LIFO стек | `Stack<T>` | O(1) |
| Потокобезопасный словарь | `ConcurrentDictionary` | Lock striping |
| Неизменяемые данные | `ImmutableList<T>` | Структурное разделение |
| Парсинг, high-perf | `Span<T>/Memory<T>` | 0 аллокаций |
""",

    17: """
## 🎓 Педагогические дополнения к Async/Await

### 📖 Термин: **State Machine (машина состояний)**
> **Определение**: Структура, которую компилятор генерирует для каждого `async` метода. Она хранит все локальные переменные как поля и имеет метод `MoveNext()`, который выполняется по частям — до первого `await`, потом после каждого `await`.

### 🎯 Что показывает пример State Machine
```csharp
// Исходный код
public async Task<string> DownloadAsync(string url) {
    using var client = new HttpClient();
    var data = await client.GetStringAsync(url);
    return Process(data);
}

// Компилятор генерирует структуру:
struct <DownloadAsync>d__0 : IAsyncStateMachine {
    int <>1__state;  // -1=завершён, 0=старт, 1=после await
    // Все локальные переменные становятся полями:
    HttpClient <client>5__1;
    string <data>5__2;
    TaskAwaiter<string> <>u__1;
    
    void MoveNext() {
        // Выполняется кусками: до await, после await...
    }
}
```
**Что демонстрирует**: `await` НЕ блокирует поток! Он регистрирует продолжение и возвращает управление.

**Где используется**: В понимании того, почему async код не блокирует UI/потоки, почему локальные переменные выживают между await.

### 📖 Термин: **ValueTask** 
> **Определение**: Структура (value type), которая может представлять либо уже готовый результат (без аллокации), либо асинхронную операцию. В отличие от `Task` (класс), не аллоцирует память при синхронном завершении.

### 🎯 Что показывает пример Task vs ValueTask
```csharp
// Task — класс, всегда аллоцируется (кроме кэшированных)
Task<int> GetCached(int key) {
    if (_cache.TryGetValue(key, out var value))
        return Task.FromResult(value);  // Новая аллокация!
    return FetchFromDbAsync(key);
}

// ValueTask — структура, 0 аллокаций если результат есть
ValueTask<int> GetCached(int key) {
    if (_cache.TryGetValue(key, out var value))
        return new ValueTask<int>(value);  // 0 аллокаций!
    return new ValueTask<int>(FetchFromDbAsync(key));
}

// ВАЖНО: ValueTask можно await ТОЛЬКО ОДИН РАЗ!
var vt = GetCached(1);
await vt;  // OK
await vt;  // ИСКЛЮЧЕНИЕ! Уже потреблён.
```
**Что демонстрирует**: Разницу в аллокациях и ограничение однократного await.

**Где используется**: `ValueTask` — в горячих путях (кэши, миллионы вызовов/сек), `Task` — везде остальное.

### 📖 Термин: **CancellationToken**
> **Определение**: Токен отмены, позволяющий внешнему коду попросить операцию завершиться досрочно. Не принудительно убивает поток — это кооперативная отмена (операция сама проверяет токен).

### 🎯 Что показывает пример с CancellationToken
```csharp
public async Task ProcessAsync(CancellationToken ct = default) {
    for (int i = 0; i < 1000; i++) {
        ct.ThrowIfCancellationRequested();  // Быстрая проверка
        await DoWorkAsync(i, ct);  // Передача дальше
    }
}

// Использование:
using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
await ProcessAsync(cts.Token);  // Отменится через 5 сек
```
**Что демонстрирует**: Кооперативную отмену — операция сама решает, когда проверить токен.

**Где используется**: Во всех долгих операциях: HTTP запросы, БД, файловый ввод-вывод, вычисления.

### 📖 Термин: **SynchronizationContext**
> **Определение**: Абстракция, управляющая тем, ГДЕ выполняется продолжение после `await`. В UI (WPF/WinForms) — возвращает в UI поток. В ASP.NET Core — нет (продолжение в пуле потоков).

### 🎯 Что показывает пример ConfigureAwait
```csharp
// По умолчанию: продолжение в ТОМ ЖЕ контексте
await client.GetAsync(url);

// ConfigureAwait(false) — продолжение в ThreadPool
await client.GetAsync(url).ConfigureAwait(false);
```
**Что демонстрирует**: Как избежать захвата UI контекста в библиотеках.

**Где используется**: В библиотеках (всегда `ConfigureAwait(false)`), в UI коде — по умолчанию.

### 📖 Термин: **Deadlock (взаимная блокировка)**
> **Определение**: Ситуация, когда поток А ждёт поток Б, а поток Б ждёт поток А. В async: UI поток блокируется на `.Result`, а продолжение `await` пытается вернуться в UI поток.

### 🎯 Что показывает пример Deadlock
```csharp
// DEADLOCK в WPF/старом ASP.NET:
public string GetData() => GetDataAsync().Result;  // Блокирует UI поток!
// async метод ждёт продолжение в UI потоке, но UI поток заблокирован .Result

// РЕШЕНИЯ:
// 1. Везде async:
public async Task<string> GetData() => await GetDataAsync();

// 2. ConfigureAwait(false) в библиотеках
await client.GetAsync(url).ConfigureAwait(false);
```
**Что демонстрирует**: Классическую проблему синхронного ожидания async кода.

**Где используется**: При миграции синхронного кода на async, в legacy проектах.

---

### 📍 Резюме: лучшие практики async/await
1. **Везде async** — не используйте `.Result`/`.Wait()`
2. **CancellationToken везде** — передавайте вниз по стеку
3. **ConfigureAwait(false)** в библиотеках
4. **ValueTask** для горячих путей с кэшем
4. **Task.WhenAll** для параллелизма, **WhenAny** для таймаутов
5. **IAsyncEnumerable** для стриминга больших данных
""",

    18: """
## 🎓 Педагогические дополнения к CLR/GC/JIT

### 📖 Термин: **JIT (Just-In-Time) компиляция**
> **Определение**: Компиляция IL (промежуточного кода) в нативный машинный код прямо перед выполнением метода. Позволяет оптимизировать под конкретный процессор и среду выполнения.

### 📖 Термин: **Tiered Compilation (многоуровневая компиляция)**
> **Определение**: Стратегия .NET 7+, где методы компилируются в два этапа:
> - **Tier 0**: Быстрая компиляция БЕЗ оптимизаций для быстрого старта
> - **Tier 1**: Полная оптимизация (инлайнинг, векторизация) для горячих методов в фоне
> - **OSR (On-Stack Replacement)**: Замена кода метода прямо во время выполнения

### 🎯 Что показывает пример Tiered Compilation
```xml
<!-- Отключение -->
<TieredCompilation>false</TieredCompilation>

<!-- Для конкретного метода -->
[MethodImpl(MethodImplOptions.NoOptimization)]
public void NoOptMethod() { }
```
**Что демонстрирует**: Как управлять балансом старт/производительность.

**Где используется**: В диагностике проблем старта, профилировании, специальных случаях (криптография, где оптимизации могут сломать константное время).

### 📖 Термин: **ReadyToRun (Crossgen2)**
> **Определение**: AOT-компиляция при публикации — нативный код генерируется заранее, JIT пропускает эти методы при запуске.

### 🎯 Что показывает пример ReadyToRun
```xml
<PublishReadyToRun>true</PublishReadyToRun>
<PublishReadyToRunComposite>true</PublishReadyToRunComposite>
```
**Что демонстрирует**: Трейдофф: быстрее старт, больше размер, не все методы совместимы.

**Где используется**: В продакшене для ускорения холодного старта (serverless, контейнеры).

### 📖 Термин: **PGO (Profile-Guided Optimization)**
> **Определение**: Оптимизация на основе профиля реального запуска. JIT собирает статистику какие методы горячие, какие ветки частые, и перекомпилирует с учётом этого.

### 🎯 Что показывает пример Dynamic PGO
```xml
<TieredCompilation>true</TieredCompilation>
<TieredPGO>true</TieredPGO>
```
**Что демонстрирует**: Самый простой способ получить 10-20% прирост производительности в .NET 8+.

**Где используется**: В продакшене везде, где важна производительность.

### 📖 Термин: **Поколения GC (Generations)**
> **Определение**: Разделение кучи на возрастные группы:
> - **Gen 0**: Новые объекты (малые, ~256 KB), частый GC
> - **Gen 1**: Выжили после Gen 0 (буфер)
> - **Gen 2**: Долгоживущие объекты, редкий Full GC

### 🎯 Что показывает пример с LOH
```csharp
// НЕ в LOH (80 KB)
var small = new double[10000];  // 80,000 байт

// В LOH (88 KB)
var large = new double[11000];  // 88,000 байт
```
**Что демонстрирует**: Порог 85 KB для попадания в Large Object Heap.

**Где используется**: При работе с большими массивами, изображениями, сериализацией — чтобы избежать фрагментации LOH.

### 📖 Термин: **Large Object Heap (LOH)**
> **Определение**: Отдельная куча для объектов ≥ 85,000 байт. Не компактируется (до .NET 5), собирается только при Full GC (Gen 2).

### 🎯 Что показывает пример с ArrayPool
```csharp
// ПЛОХО: LOH фрагментация
for (int i = 0; i < 1000; i++) {
    var buffer = new byte[100000];  // Каждый раз в LOH!
}

// ХОРОШО: пулинг
var buffer = ArrayPool<byte>.Shared.Rent(100000);
try { /* работа */ } 
finally { ArrayPool<byte>.Shared.Return(buffer); }
```
**Что демонстрирует**: Как избежать фрагментации LOH через пулинг.

**Где используется**: Сетевые буферы, парсинг больших файлов, обработка изображений, сериализация.

### 📖 Термин: **SafeHandle**
> **Определение**: Базовый класс для безопасной обёртки нативных дескрипторов (файлы, сокеты, дескрипторы БД). Наследуется от `CriticalFinalizerObject` — гарантирует вызов финализатора даже при аварийном завершении.

### 🎯 Что показывает пример SafeHandle
```csharp
// ПРАВИЛЬНО: SafeHandle
public sealed class MySafeHandle : SafeHandleZeroOrMinusOneIsInvalid {
    private MySafeHandle() : base(true) { }  // ownsHandle = true
    protected override bool ReleaseHandle() => NativeMethods.Close(handle);
}

// Использование — финализатор НЕ нужен!
public class Wrapper : IDisposable {
    private readonly MySafeHandle _handle = MySafeHandle.Create();
    public void Dispose() => _handle.Dispose();
}
```
**Что демонстрирует**: Правильный паттерн для unmanaged ресурсов вместо `IntPtr` + финализатора.

**Где используется**: В любой интероп-обёртке: файлы, сокеты, БД, Win32 API, COM.

### 📖 Термин: **CriticalFinalizerObject**
> **Определение**: Базовый класс, финализаторы которого гарантированно выполняются даже при `Environment.FailFast`, выгрузке AppDomain, аварийном завершении процесса.

---

### 📍 Резюме: диагностика производительности
| Инструмент | Для чего |
|------------|----------|
| `dotnet-counters` | Real-time метрики (GC, ThreadPool, JIT) |
| `dotnet-trace` | ETW трассировка, анализ в PerfView/Speedscope |
| `dotnet-gcdump` | Снимок кучи, кто держит память |
| `PerfView` | Глубокий анализ: CPU стеки, GC паузы, аллокации |
""",

    19: """
## 🎓 Педагогические дополнения к тестированию

### 📖 Термин: **AAA Pattern (Arrange-Act-Assert)**
> **Определение**: Структура теста в три фазы:
> 1. **Arrange** — подготовка данных, моков, среды
> 2. **Act** — вызов тестируемого метода
> 3. **Assert** — проверка результата

### 🎯 Что показывает пример с Moq SetupSequence
```csharp
mockRepo.SetupSequence(r => r.GetNextId())
    .Returns(1)
    .Returns(2)
    .Throws(new Exception("No more IDs"));
```
**Что демонстрирует**: Как задать последовательные возвраты для последовательных вызовов.

**Где используется**: Тестирование генераторов ID, итераторов, состояний.

### 🎯 Что показывает пример с Callback
```csharp
mockRepo.Setup(r => r.AddAsync(It.IsAny<User>(), It.IsAny<CancellationToken>()))
    .Callback<User, CancellationToken>((u, ct) => {
        u.Id = Interlocked.Increment(ref _lastId);  // Генерация ID
        _addedUsers.Add(u);  // Сохранение для проверки
    })
    .Returns(Task.CompletedTask);
```
**Что демонстрирует**: Как выполнить сложную логику внутри мока (генерация ID, сохранение для проверки).

**Где используется**: Когда мок должен вести себя как настоящий репозиторий (генерация ID, валидация, побочные эффекты).

### 📖 Термин: **Property-Based Testing (PBT)**
> **Определение**: Подход, где вы описываете свойства (инварианты), которые должны выполняться для ВСЕХ возможных входов, а фреймворк (FsCheck) сам генерирует сотни случайных тест-кейсов включая edge cases.

### 🎯 Что показывает пример Property-Based Testing
```csharp
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
```
**Что демонстрирует**: Как протестировать алгоритмы на всех возможных входах (пустые массивы, дубликаты, Int32.MinValue/MaxValue, null).

**Где используется**: Тестирование алгоритмов сортировки, парсеров, математических функций, сериализации.

### 📖 Термин: **Contract Testing (Pact)**
> **Определение**: Подход к тестированию микросервисов, где consumer и provider договариваются о контракте (API), и тесты проверяют соответствие контракту независимо.

### 🎯 Что показывает пример Contract Testing
```csharp
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
        Body = new { id = 1, name = "Alex" }
    });
pact.Verify();
```
**Что демонстрирует**: Как гарантировать совместимость API между сервисами без поднятия всей среды.

**Где используется**: Микросервисная архитектура, API версионирование, consumer-driven contracts.

### 📖 Термин: **Branch Coverage (покрытие веток)**
> **Определение**: Процент пройденных веток условий (if/else, switch, ?:). Важнее Line Coverage, так как показывает, проверены ли оба исхода условий.

### 🎯 Что показывает пример целей покрытия
```bash
# Line Coverage — может быть 100%, но if (x > 0) проверен только для x > 0
# Branch Coverage — проверяет и x > 0, и x <= 0

# Правильные цели:
# - 80%+ branch coverage для бизнес-логики
# - 100% для критических путей (платежи, безопасность)
```
**Что демонстрирует**: Почему Line Coverage обманчива и какие цели ставить.

**Где используется**: В CI/CD пайплайнах, настройке порогов качества.

---

### 📍 Резюме: пирамида тестирования
```
        /\
       /  \     E2E (Playwright) — немного, медленные, дорогие
      /____\
     /      \   Integration (Testcontainers) — средне
    /________\
   /          \  Unit (xUnit, Moq) — много, быстрые, дешёвые
  /____________\
```

**Где что тестировать**:
- **Unit**: чистая логика, валидаторы, мапперы, утилиты (моки для зависимостей)
- **Integration**: репозитории (Testcontainers БД), API endpoints, SignalR хабы
- **E2E**: критичные пользовательские сценарии (логин, заказ, оплата)
""",

    20: """
## 🎓 Педагогические дополнения к JSON/Files/SQL

### 📖 Термин: **Source Generator (генератор исходного кода)**
> **Определение**: Компонент, работающий на этапе компиляции, анализирующий код и генерирующий дополнительные `.cs` файлы. Работает в NativeAOT, не использует рефлексию в runtime.

### 🎯 Что показывает пример Source Generator для JSON
```csharp
// Традиционный подход (рефлексия — не работает в NativeAOT)
var json = JsonSerializer.Serialize(user, options);

// Source Generator (compile-time, работает в NativeAOT)
[JsonSerializable(typeof(User))]
[JsonSerializable(typeof(List<User>))]
[JsonSourceGenerationOptions(PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase)]
internal partial class AppJsonContext : JsonSerializerContext { }

// Использование — БЕЗ рефлексии!
var json = JsonSerializer.Serialize(user, AppJsonContext.Default.User);
```
**Что демонстрирует**: Как избавиться от рефлексии при сериализации.

**Где используется**: NativeAOT приложения, высоконагруженные API, мобильные приложения (iOS/Android с .NET).

### 📖 Термин: **PipeReader / PipeWriter**
> **Определение**: Высокопроизводительные API для работы с потоками данных без лишних копирований. Реализуют паттерн producer/consumer с буферизацией.

### 🎯 Что показывает пример PipeReader
```csharp
var pipe = new Pipe();

// Producer — пишет данные
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

// Consumer — читает и парсит
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
**Что демонстрирует**: Zero-copy парсинг потоков данных.

**Где используется**: Парсинг больших HTTP ответов, стриминг файлов, gRPC streaming, реализация протоколов.

### 📖 Термин: **ArrayPool**
> **Определение**: Пул массивов для повторного использования, снижающий нагрузку на GC. Особенно важен для больших буферов, которые иначе попали бы в LOH.

### 🎯 Что показывает пример с ArrayPool
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
**Что демонстрирует**: Как избежать аллокаций при работе с потоками.

**Где используется**: Сетевые серверы, парсинг больших файлов, обработка изображений, любой высоконагруженный I/O.

### 📖 Термин: **Split Query (EF Core)**
> **Определение**: Режим, при котором EF Core вместо одного огромного JOIN с дублированием данных выполняет несколько отдельных запросов и собирает результат в памяти.

### 🎯 Что показывает пример Split Query
```csharp
// ПРОБЛЕМА: Include создаёт огромный JOIN
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
**Что демонстрирует**: Решение проблемы "cartesian explosion" при eager loading.

**Где используется**: При загрузке сущностей с множественными коллекциями (один-ко-многим во множестве).

### 📖 Термин: **Compiled Queries (EF Core)**
> **Определение**: Предварительно скомпилированные LINQ запросы, план выполнения которых кэшируется, избегая перекомпиляции при каждом вызове.

### 🎯 Что показывает пример Compiled Queries
```csharp
private static readonly Func<AppDbContext, int, Task<User>> _getUserById =
    EF.CompileAsyncQuery((AppDbContext ctx, int id) => 
        ctx.Users.FirstOrDefault(u => u.Id == id));

// Использование — без перекомпиляции LINQ каждый раз
var user = await _getUserById(ctx, 123);
```
**Что демонстрирует**: Как убрать накладные расходы на парсинг LINQ при частых вызовах.

**Где используется**: Горячие пути: частые поиски по ID, простые фильтры в высоконагруженных API.

### 📖 Термин: **Interceptors (EF Core)**
> **Определение**: Механизм перехвата операций EF Core (SaveChanges, команды БД) для внедрения логики: мягкое удаление, аудит, шифрование.

### 🎯 Что показывает пример Soft Delete Interceptor
```csharp
public class SoftDeleteInterceptor : SaveChangesInterceptor {
    public override InterceptionResult<int> SavingChanges(
        DbContextEventData eventData, InterceptionResult<int> result) {
        
        foreach (var entry in eventData.Context.ChangeTracker.Entries()
            .Where(e => e.State == EntityState.Deleted && e.Entity is ISoftDelete)) {
            
            entry.State = EntityState.Modified;  // Не удаляем, а помечаем
            entry.CurrentValues["IsDeleted"] = true;
            entry.CurrentValues["DeletedAt"] = DateTime.UtcNow;
        }
        return base.SavingChanges(eventData, result);
    }
}
```
**Что демонстрирует**: Как реализовать мягкое удаление прозрачно для бизнес-логики.

**Где используется**: Многотенантные системы, аудит, GDPR compliance, архивирование.

### 📖 Термин: **Change Tracker (EF Core)**
> **Определение**: Механизм отслеживания изменений сущностей: какие свойства изменились, исходные и текущие значения, состояние (Added/Modified/Deleted).

---

### 📍 Резюме: выбор подхода к данным
| Сценарий | Рекомендация |
|----------|--------------|
| Простые CRUD, высокая нагрузка | Dapper |
| Сложная бизнес-логика, отношения | EF Core |
| Аналитические запросы | ADO.NET / Dapper |
| Прототипирование | EF Core (InMemory для тестов) |
| Bulk operations | Dapper + SqlBulkCopy / EF Core BulkExtensions |
""",

    21: """
## 🎓 Педагогические дополнения к DI, Configuration, Logging

### 📖 Термин: **Dependency Injection (DI) — Внедрение зависимостей**
> **Определение**: Паттерн, где зависимости класса предоставляются извне (через конструктор), а не создаются внутри класса. Это обеспечивает слабую связанность и тестируемость.

### 📖 Термин: **Декоратор (Decorator Pattern) в DI**
> **Определение**: Паттерн, где класс-обёртка добавляет функциональность к существующему сервису, не меняя его код. Реализует тот же интерфейс и делегирует вызовы внутреннему объекту.

### 🎯 Что показывает пример с декоратором
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
**Что демонстрирует**: Как добавить кэширование/логирование/метрики без изменения основного репозитория.

**Где используется**: Кэширование, логирование запросов, метрики, retry policies, авторизация.

### 📖 Термин: **Открытые дженерики (Open Generics)**
> **Определение**: Регистрация обобщённого типа без указания конкретного типа параметра. Контейнер сам подставит нужный тип при резолвинге.

### 🎯 Что показывает пример с открытыми дженериками
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
**Что демонстрирует**: Как избежать повторной регистрации для каждого типа сущности.

**Где используется**: Репозитории, валидаторы, обработчики команд/запросов, мапперы.

### 📖 Термин: **Keyed Services (.NET 8+)**
> **Определение**: Регистрация нескольких реализаций одного интерфейса с уникальными ключами, позволяющая резолвить нужную по ключу.

### 🎯 Что показывает пример с Keyed Services
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
**Что демонстрирует**: Как выбирать реализацию в runtime по ключу.

**Где используется**: Платежные шлюзы, провайдеры уведомлений (Email/SMS/Push), хранилища (S3/Azure/GCS), стратегии экспорта.

### 📖 Термин: **IOptionsMonitor — горячая перезагрузка конфигурации**
> **Определение**: Сервис, который отслеживает изменения в конфигурации и уведомляет подписчиков через callback `OnChange`.

### 🎯 Что показывает пример с IOptionsMonitor
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
**Что демонстрирует**: Как реагировать на изменение конфигурации без перезапуска приложения.

**Где используется**: Ротация секретов, feature flags, динамические настройки率限制, секреты в Key Vault.

### 📖 Термин: **IOptionsSnapshot — на запрос**
> **Определение**: Перечитывает конфигурацию на каждый запрос (scoped). Полезно для per-request конфигурации.

### 📖 Термин: **IOptions — синглтон**
> **Определение**: Читает конфигурацию один раз при старте. Кэширует значение навсегда.

---

### 📝 Serilog — продвинутое логирование

### 📖 Термин: **Enricher (обогатитель)**
> **Определение**: Компонент, добавляющий дополнительные свойства к каждому лог-событию автоматически.

### 🎯 Что показывает пример с кастомным Enricher
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
**Что демонстрирует**: Как автоматически добавлять UserId/TraceId к ВСЕМ логам в контексте запроса.

**Где используется**: Корреляция логов, аудит, отладка распределённых систем.

### 📖 Термин: **Destructuring (деструктуризация)**
> **Определение**: Сериализация сложного объекта в структурированный лог (JSON) вместо вызова `ToString()`.

### 🎯 Что показывает пример с Destructuring
```csharp
// ПЛОХО — ToString()
_logger.LogInformation("User: {User}", user);  // User: User { Name = Alex }

// ХОРОШО — @ для деструктуризации
_logger.LogInformation("User: {@User}", user);  // User: { Name: "Alex", Email: "a@b.com" }

// Настройка — скрыть секреты
.Destructure.ByTransforming<User>(u => new { u.Id, u.Name, u.Email })  // скрыть PasswordHash
.Destructure.AsScalar<CreditCardNumber>()  // не разбирать, как есть
```
**Что демонстрирует**: Как логировать объекты структурированно и безопасно.

**Где используется**: Аудит, отладка, SIEM/ELK/Seq анализ.

---

### 📝 Валидация конфигурации при старте
```csharp
builder.Services.AddOptions<JwtOptions>()
    .BindConfiguration("Jwt")
    .ValidateDataAnnotations()  // [Required], [MinLength] и т.д.
    .Validate(o => o.Key.Length >= 32, "Key must be at least 32 chars")
    .ValidateOnStart();  // Падает при старте если невалидно!
```
**Что демонстрирует**: Fail-fast — падение при старте вместо ошибок в runtime.

**Где используется**: Валидация критических настроек (секреты, connection strings, URLs).
""",

    22: """
## 🎓 Педагогические дополнения к архитектуре

### 📖 Термин: **Clean Architecture (Чистая архитектура)**
> **Определение**: Архитектурный стиль, где зависимости направлены ТОЛЬКО внутрь. Внутренние слои не знают о внешних. Бизнес-логика изолирована от фреймворков, БД, UI.

### 🎯 Что показывает схема слоёв
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
**Что демонстрирует**: Правило зависимостей — только внутрь. Domain не знает ни о ком.

**Где используется**: В 엔терпрайз приложениях, долгосрочных проектах, где важна поддерживаемость.

### 📖 Термин: **Aggregate Root (Корень агрегата)**
> **Определение**: Сущность, которая является точкой входа в агрегат (группу связанных объектов). Контролирует инварианты внутри агрегата. Все изменения проходят через него.

### 🎯 Что показывает пример Aggregate Root
```csharp
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
**Что демонстрирует**: Инкапсуляция бизнес-логики внутри агрегата, защита инвариантов, генерация Domain Events.

**Где используется**: В DDD проектах, где важна согласованность бизнес-данных.

### 📖 Термин: **Domain Events (События домена)**
> **Определение**: События, происходящие внутри домена, которые заинтересованные стороны (другие агрегаты, внешние системы) могут обработать. Публикуются после успешного сохранения.

### 🎯 Что показывает пример Domain Event Dispatcher
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
```
**Что демонстрирует**: Публикация доменных событий ПОСЛЕ успешного сохранения в БД (в той же транзакции).

**Где используется**: Интеграция с внешними системами, отправка уведомлений, обновление read models, аудит.

### 📖 Термин: **CQRS (Command Query Responsibility Segregation)**
> **Определение**: Паттерн разделения операций чтения (Queries) и записи (Commands) на разные модели. Команды меняют состояние, запросы только читают.

### 🎯 Что показывает пример CQRS с MediatR
```csharp
// Command — изменяет состояние
public record CreateTaskCommand(string Title, string Description, Guid ProjectId) : IRequest<TaskId>;

public class CreateTaskHandler : IRequestHandler<CreateTaskCommand, TaskId> {
    private readonly ITaskRepository _repo;
    private readonly IUnitOfWork _uow;
    
    public async Task<TaskId> Handle(CreateTaskCommand cmd, CancellationToken ct) {
        var task = Task.Create(TaskId.New(), cmd.Title, cmd.Description, 
            new ProjectId(cmd.ProjectId), _currentUser.UserId!);
        await _repo.AddAsync(task, ct);
        await _uow.SaveChangesAsync(ct);
        return task.Id;
    }
}

// Query — только чтение
public record GetTaskQuery(TaskId Id) : IRequest<TaskDto?>;

public class GetTaskHandler : IRequestHandler<GetTaskQuery, TaskDto?> {
    private readonly ITaskReadRepository _repo;
    
    public async Task<TaskDto?> Handle(GetTaskQuery query, CancellationToken ct) {
        var task = await _repo.GetByIdAsync(query.Id, ct);
        return task == null ? null : _mapper.Map<TaskDto>(task);
    }
}
```
**Что демонстрирует**: Разделение записи и чтения, разные модели для разных нужд.

**Где используется**: Сложные домены, высоконагруженные системы, когда читать и писать нужно по-разному.

### 📖 Термин: **Pipeline Behaviors (MediatR)**
> **Определение**: Middleware для MediatR, выполняемое до/после каждого запроса/команды. Используется для cross-cutting concerns: валидация, логирование, транзакции.

### 🎯 Что показывает пример Pipeline Behaviors
```csharp
// Validation Behavior (FluentValidation)
public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> {
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct) {
        var failures = _validators.Select(v => v.Validate(new ValidationContext<TRequest>(request)))
            .SelectMany(r => r.Errors).Where(e => e != null).ToList();
        if (failures.Any()) throw new ValidationException(failures);
        return await next();
    }
}

// Transaction Behavior — только для команд
public class TransactionBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> {
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
```
**Что демонстрирует**: Cross-cutting concerns (валидация, транзакции, логирование) без загрязнения хендлеров.

**Где используется**: Валидация (FluentValidation), транзакции, логирование, метрики, кэширование, авторизация.

### 📖 Термин: **Event Sourcing (Хранилище событий)**
> **Определение**: Паттерн, где состояние агрегата восстанавливается из последовательности событий (Event Log), а не хранится напрямую. События — единственный источник истины.

### 🎯 Что показывает пример Event Sourcing
```csharp
// Aggregate хранит только события
public class Account : EventSourcedAggregate {
    public decimal Balance { get; private set; }
    public bool IsClosed { get; private set; }
    
    public void Deposit(decimal amount) {
        if (IsClosed) throw new InvalidOperationException("Closed");
        Apply(new MoneyDeposited(Id, amount));
    }
    
    protected override void When(object @event) {
        switch (@event) {
            case MoneyDeposited e: Balance += e.Amount; break;
            case MoneyWithdrawn e: Balance -= e.Amount; break;
            case AccountClosed e: IsClosed = true; break;
        }
    }
}
```
**Что демонстрирует**: Состояние вычисляется из истории событий. Полная аудит-трасса из коробки.

**Где используется**: Финансы, аудит, сложные бизнес-процессы, где важна история изменений.

---

### 📍 Резюме: когда что применять
| Паттерн | Когда применять |
|---------|-----------------|
| Clean Architecture | Всегда для энтерпрайз приложений |
| DDD / Aggregate Root | Сложная бизнес-логика, инварианты |
| CQRS | Разные модели для чтения/записи, высокая нагрузка |
| Event Sourcing | Аудит обязателен, сложные бизнес-процессы |
| Pipeline Behaviors | Cross-cutting concerns (валидация, транзакции, логирование) |
""",

    23: """
## 🎓 Педагогические дополнения к системе типов

### 📖 Термин: **Generics Constraints (Ограничения обобщений)**
> **Определение**: Ограничения на параметр типа `T`, которые говорят компилятору, какие операции допустимы с `T` внутри generic кода.

### 🎯 Что показывает таблица constraints
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
```
**Что демонстрирует**: Как сузить множество допустимых типов и получить доступ к их членам.

**Где используется**: В generic репозиториях, алгоритмах, библиотеках, где нужны гарантии о типах.

### 📖 Термин: **Covariance (Ковариантность) / `out`**
> **Определение**: Возможность использовать более конкретный тип там, где ожидается более общий. Работает только для ВЫХОДНЫХ позиций (возвращаемые значения, property get).

### 🎯 Что показывает пример ковариантности
```csharp
// IEnumerable<out T> — можно: IEnumerable<string> → IEnumerable<object>
IEnumerable<string> strings = new List<string>();
IEnumerable<object> objects = strings;  // OK

// Func<out TResult> — ковариативен по результату
Func<string> funcStr = () => "hello";
Func<object> funcObj = funcStr;  // OK

// Свой интерфейс с out
public interface IReadOnlyRepo<out T> {
    T GetById(int id);      // OK: T на выходе
    // void Add(T item);    // ОШИБКА: T на входе
}
```
**Что демонстрирует**: Как безопасно присваивать более конкретные коллекции переменным более общих типов.

**Где используется**: `IEnumerable<T>`, `IReadOnlyList<T>`, `Func<TResult>`, любые read-only интерфейсы.

### 📖 Термин: **Contravariance (Контравариантность) / `in`**
> **Определение**: Возможность использовать более общий тип там, где ожидается более конкретный. Работает только для ВХОДНЫХ позиций (параметры методов, property set).

### 🎯 Что показывает пример контравариантности
```csharp
// IComparer<in T> — можно: IComparer<object> → IComparer<string>
IComparer<object> objComparer = (a, b) => 0;
IComparer<string> strComparer = objComparer;  // OK

// Action<in T> — контравариативен
Action<object> actObj = o => Console.WriteLine(o);
Action<string> actStr = actObj;  // OK

// Свой интерфейс с in
public interface IWriter<in T> {
    void Write(T item);  // OK: T на входе
    // T Read();         // ОШИБКА: T на выходе
}
```
**Что демонстрирует**: Как использовать более общий обработчик для конкретных типов.

**Где используется**: `IComparer<T>`, `Action<T>`, `IObserver<T>`, любые write-only интерфейсы.

### 📖 Термин: **Pattern Matching (Сопоставление с образцом)**
> **Определение**: Синтаксис для проверки структуры данных и извлечения значений. Включает type patterns, property patterns, list patterns, slice patterns.

### 🎯 Что показывает пример List Patterns (C# 11+)
```csharp
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
```
**Что демонстрирует**: Декларативное разбор массивов/списков без ручных индексов.

**Где используется**: Парсинг протоколов, разбор команд, валидация структур данных.

### 📖 Термин: **Records (Записи)**
> **Определение**: Reference type (или value type в C# 10+) с value-семантикой сравнения, невидимостью по умолчанию, встроенным `with`-expression для невидимых изменений.

### 🎯 Что показывает пример Records
```csharp
public record User(string Name, string Email, int Age) {
    // Автоматически: конструктор, init-свойства, Equals/GetHashCode, ToString, Deconstruct
}

var user1 = new User("Alex", "alex@test.com", 25);
var user2 = user1 with { Age = 26 };  // Копия с изменением
// user1 == user2 -> false (разный Age)

// Positional records — деконструкция
public record Point(int X, int Y);
var p = new Point(10, 20);
var (x, y) = p;  // x=10, y=20
Console.WriteLine(p); // Point { X = 10, Y = 20 }
```
**Что демонстрирует**: Невидимые данные с value equality и удобным копированием.

**Где используется**: DTO, Value Objects, команды/запросы в CQRS, immutable данные.

---

### 📍 Резюме: что выбрать
| Задача | Решение |
|--------|---------|
| Ограничить T для доступа к членам | Constraints (`where T : ...`) |
| Read-only коллекция/интерфейс | `out` (covariance) |
| Write-only интерфейс/обработчик | `in` (contravariance) |
| Разбор структуры данных | Pattern matching (switch, is, list patterns) |
| Невидимые данные с value equality | `record` / `record struct` |
""",

    24: """
## 🎓 Педагогические дополнения к Internals

### 📖 Термин: **IL (Intermediate Language)**
> **Определение**: Промежуточный язык .NET — стековый байт-код, в который компилируется C# код. JIT компилирует IL в нативный код при выполнении.

### 🎯 Что показывает пример IL
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
**Что демонстрирует**: Стековую природу IL — загрузка аргументов, операции над стеком, сохранение в локальные переменные.

**Где используется**: Отладка оптимизаций, понимание производительности, реверс-инжиниринг, написание IL вручную.

### 📖 Термин: **Source Generators (Генераторы исходного кода)**
> **Определение**: Компоненты, работающие на этапе компиляции, анализирующие синтаксис и генерирующие дополнительные `.cs` файлы. Работают в NativeAOT, не используют рефлексию.

### 🎯 Что показывает пример Incremental Generator
```csharp
[Generator(LanguageNames.CSharp)]
public class AutoToStringGenerator : IIncrementalGenerator {
    public void Initialize(IncrementalGeneratorInitializationContext context) {
        var classes = context.SyntaxProvider
            .CreateSyntaxProvider(
                predicate: (node, _) => node is ClassDeclarationSyntax { AttributeLists.Count: > 0 },
                transform: (ctx, _) => (ClassDeclarationSyntax)ctx.Node)
            .Where(c => c.AttributeLists.Any(a => 
                a.Attributes.Any(attr => attr.Name.ToString() == "GenerateToString")))
            .Collect();

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
**Что демонстрирует**: Генерация кода на этапе компиляции без рефлексии.

**Где используется**: Автогенерация ToString, клонирование, маппинг, сериализация, валидация, gRPC/GraphQL код.

### 📖 Термин: **Incremental Generator**
> **Определение**: Современный API Source Generators, который кэширует результаты и работает инкрементально (перегенерация только изменённого). Быстрее и эффективнее старого `ISourceGenerator`.

### 📖 Термин: **Reflection (Рефлексия)**
> **Определение**: Механизм инспекции типов, членов, атрибутов в runtime. Позволяет динамически создавать объекты, вызывать методы, читать/писать свойства.

### 🎯 Что показывает пример оптимизации рефлексии
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
```
**Что демонстрирует**: Накладные расходы рефлексии и как их устранить.

**Где используется**: В горячих путях, сериализаторах, мапперах, DI контейнерах, ORM.

### 📖 Термин: **Expression Trees (Деревья выражений)**
> **Определение**: Структура данных, представляющая код в виде дерева объектов (`Expression<TDelegate>`). Можно анализировать, трансформировать и компилировать в делегаты.

### 🎯 Что показывает пример Expression Trees
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
```
**Что демонстрирует**: Динамическое построение LINQ запросов по строкам.

**Где используется**: Динамическая сортировка/фильтрация в API, построение предикатов по конфигу, LINQ providers.

### 📖 Термин: **DynamicMethod / ILGenerator**
> **Определение**: Ручная генерация IL кода в runtime для создания делегатов с максимальной производительностью.

### 🎯 Что показывает пример DynamicMethod
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
**Что демонстрирует**: Ручную генерацию IL для максимальной скорости доступа к свойствам.

**Где используется**: Высокопроизводительные сериализаторы, мапперы, ORM, DI контейнеры.

---

### 📍 Резюме: инструменты интроспекции
| Инструмент | Для чего | Производительность |
|------------|----------|-------------------|
| Reflection | Динамический доступ к типам | Медленно (кэшируйте!) |
| Expression Trees | Динамическое построение кода | Среднее (кэшируйте делегаты) |
| DynamicMethod/ILGenerator | Максимальная скорость, ручной IL | Максимальная |
| Source Generators | Генерация кода на этапе компиляции | Нулевая в runtime |
""",

    25: """
## 🎓 Педагогические дополнения к Extension Members, Operators, Indexers

### 📖 Термин: **Extension Methods (Методы расширения)**
> **Определение**: Статические методы в статическом классе, которые вызываются так, будто это методы экземпляра расширяемого типа. Первый параметр помечается `this`.

### 🎯 Что показывает пример Extension Methods
```csharp
public static class StringExtensions {
    public static bool IsNullOrEmpty(this string s) => string.IsNullOrEmpty(s);
    
    // Generic extension
    public static TResult Pipe<T, TResult>(this T value, Func<T, TResult> func) => func(value);
    
    // Несколько параметров
    public static string Repeat(this string s, int count, string separator = "") 
        => string.Join(separator, Enumerable.Repeat(s, count));
}
```
**Что демонстрирует**: Как добавить методы к типам, которые вы не контролируете (BCL, сторонние библиотеки).

**Где используется**: Fluent API, pipelines, утилиты для BCL типов (string, IEnumerable, DateTime), DSL.

### 📖 Термин: **Extension Properties (C# 12)**
> **Определение**: Только геттеры, синтаксически выглядят как свойства, но на самом деле являются методами расширения.

### 🎯 Что показывает пример Extension Properties
```csharp
public static class DateTimeExtensions {
    public static int WeekOfYear(this DateTime date) 
        => CultureInfo.CurrentCulture.Calendar.GetWeekOfYear(date, CalendarWeekRule.FirstFourDayWeek, DayOfWeek.Monday);
    
    public static bool IsWeekend(this DateTime date) 
        => date.DayOfWeek is DayOfWeek.Saturday or DayOfWeek.Sunday;
}
```
**Что демонстрирует**: Синтаксический сахар для читаемых вызовов.

**Где используется**: Вычисляемые свойства для BCL типов, Domain-specific helpers.

### 📖 Термин: **Operator Overloading (Перегрузка операторов)**
> **Определение**: Возможность определить поведение операторов (`+`, `-`, `==`, `!=`, `<`, `>`, `implicit`, `explicit` и др.) для своих типов.

### 🎯 Что показывает пример перегрузки операторов
```csharp
public readonly struct Vector2 {
    public double X { get; }
    public double Y { get; }
    
    public Vector2(double x, double y) { X = x; Y = y; }
    
    // Бинарные
    public static Vector2 operator +(Vector2 a, Vector2 b) => new(a.X + b.X, a.Y + b.Y);
    public static Vector2 operator -(Vector2 a, Vector2 b) => new(a.X - b.X, a.Y - b.Y);
    public static Vector2 operator *(Vector2 v, double scalar) => new(v.X * scalar, v.Y * scalar);
    public static Vector2 operator *(double scalar, Vector2 v) => v * scalar; // симметрично
    
    // Унарные
    public static Vector2 operator -(Vector2 v) => new(-v.X, -v.Y);
    
    // Сравнения — ОБЯЗАТЕЛЬНО ПАРНО!
    public static bool operator ==(Vector2 a, Vector2 b) => a.X == b.X && a.Y == b.Y;
    public static bool operator !=(Vector2 a, Vector2 b) => !(a == b);
    
    // Equals/GetHashCode — ОБЯЗАТЕЛЬНЫ при ==/!=
    public override bool Equals(object? obj) => obj is Vector2 v && this == v;
    public override int GetHashCode() => HashCode.Combine(X, Y);
}
```
**Что демонстрирует**: Правила перегрузки (обязательные пары, Equals/GetHashCode).

**Где используется**: Математические типы (Vector, Matrix, Complex), Money, DateTime-like типы, единицы измерения.

### 📖 Термин: **Implicit / Explicit Conversions**
> **Определение**: Неявное (`implicit`) — безопасное, без потери данных, вызывается автоматически. Явное (`explicit`) — может терять данные или выбрасывать исключение, требует каста.

### 🎯 Что показывает пример конверсий
```csharp
public readonly struct Temperature {
    public double Celsius { get; }
    public Temperature(double celsius) => Celsius = celsius;
    
    // Implicit — безопасное
    public static implicit operator Temperature(double celsius) => new(celsius);
    public static implicit operator double(Temperature t) => t.Celsius;
    
    // Explicit — может терять данные
    public static explicit operator Temperature(Fahrenheit f) => new((f.Value - 32) * 5 / 9);
    public static explicit operator Fahrenheit(Temperature t) => new(t.Celsius * 9 / 5 + 32);
}
```
**Что демонстрирует**: Разницу между безопасным автоматическим приведением и явным кастом.

**Где используется**: Единицы измерения (Temperature, Length, Weight), Money (валюты), обёртки примитивов.

### 📖 Термин: **Pattern-based API (Duck typing для языковых конструкций)**
> **Определение**: C# позволяет использовать любые типы в языковых конструкциях (`foreach`, `await`, `using`, деконструкция), если они имеют нужные методы (`GetEnumerator`, `GetAwaiter`, `Dispose`, `Deconstruct`), не требуя интерфейсов.

### 🎯 Что показывает пример await с GetAwaiter
```csharp
// Тип, который можно await'ить
public class LazyTask<T> {
    private readonly Func<Task<T>> _factory;
    private Task<T>? _task;
    
    public LazyTask(Func<Task<T>> factory) => _factory = factory;
    
    public ValueTaskAwaiter<T> GetAwaiter() {
        _task ??= _factory();
        return new ValueTaskAwaiter<T>(new ValueTask<T>(_task));
    }
}

// Использование
var lazy = new LazyTask<int>(async () => { await Task.Delay(100); return 42; });
var result = await lazy;  // Работает!
```
**Что демонстрирует**: Как сделать любой тип awaitable без наследования от Task.

**Где используется**: Lazy initialization, retry policies, polling, pooling, кастомные асинхронные примитивы.

### 📖 Термин: **Deconstruct (Деконструкция)**
> **Определение**: Метод `Deconstruct` с `out` параметрами, позволяющий разобрать объект на части: `var (x, y) = point;`.

---

### 📍 Резюме: когда что применять
| Паттерн | Когда применять |
|---------|-----------------|
| Extension Methods | Добавить поведение к чужим типам, Fluent API |
| Extension Properties (C# 12) | Вычисляемые свойства для чужих типов |
| Operators | Математические/доменные типы, единицы измерения |
| Conversions | Единицы измерения, Money, обёртки примитивов |
| Indexers | Матрицы, гриды, многомерные данные, конфиги |
| GetAwaiter | Lazy tasks, retry policies, pooling |
| Deconstruct | Value Objects, DTOs, tuples-like типы |
""",

    26: """
## 🎓 Педагогические дополнения к GC

### 📖 Термин: **Generational GC (Поколенческий сборщик мусора)**
> **Определение**: GC делит кучу на поколения по возрасту объектов. Новые объекты создаются в Gen 0, выжившие перемещаются в Gen 1, потом в Gen 2. Молодые объекты умирают быстро — их сборка дешёвая.

### 🎯 Что показывает схема поколений
```
┌─────────────────────────────────────────────┐
│            Gen 2 (Large)                    │  ← Долгоживущие, редкий Full GC
├─────────────────────────────────────────────┤
│            Gen 1 (Medium)                   │  ← Выжили после Gen 0
├─────────────────────────────────────────────┤
│            Gen 0 (Small, ~256KB)            │  ← Новые объекты, частый GC
└─────────────────────────────────────────────┘
```
**Что демонстрирует**: Гипотезу поколений — большинство объектов умирает молодыми.

**Где используется**: Понимание профиля аллокаций, оптимизация GC давления.

### 📖 Термин: **Large Object Heap (LOH)**
> **Определение**: Отдельная куча для объектов ≥ 85,000 байт. Не компактируется (до .NET 5), собирается только при Full GC (Gen 2).

### 🎯 Что показывает пример с LOH
```csharp
// НЕ в LOH (80 KB)
var small = new double[10000];  // 10000 * 8 = 80,000 байт

// В LOH (88 KB)
var large = new double[11000];  // 11000 * 8 = 88,000 байт
```
**Что демонстрирует**: Порог 85 KB и последствия попадания в LOH (нет компактировки, фрагментация).

**Где используется**: При работе с большими массивами, изображениями, большими строками, сериализацией.

### 🎯 Что показывает пример с ArrayPool
```csharp
// ПЛОХО: LOH фрагментация
for (int i = 0; i < 1000; i++) {
    var buffer = new byte[100000];  // Каждый раз в LOH!
}

// ХОРОШО: пулинг
var buffer = ArrayPool<byte>.Shared.Rent(100000);
try { /* работа */ } 
finally { ArrayPool<byte>.Shared.Return(buffer); }
```
**Что демонстрирует**: Как избежать фрагментации LOH через пулинг.

**Где используется**: Сетевые буферы, парсинг больших файлов, обработка изображений, сериализация.

### 📖 Термин: **Pinned Object Heap (POH) — .NET 5+**
> **Определение**: Отдельная куча для объектов, закреплённых в памяти через `fixed` или `GCHandle.Alloc(pinned)`. Не двигаются при компактировке.

### 🎯 Что показывает пример GCHandle
```csharp
// Pinned — закрепляет в памяти, GC не двигает
var handle = GCHandle.Alloc(obj, GCHandleType.Pinned);
IntPtr ptr = handle.AddrOfPinnedObject(); // указатель для native кода
// NativeWrite(ptr, 1024);
handle.Free(); // ОБЯЗАТЕЛЬНО Free!

// Weak — слабая ссылка
var weak = GCHandle.Alloc(obj, GCHandleType.Weak);
bool isAlive = weak.IsAllocated; // false если собран
```
**Что демонстрирует**: Работу с закреплёнными объектами для interop и слабыми ссылками.

**Где используется**: Interop с нативным кодом, работа с неуправляемой памятью, слабые кэши.

### 📖 Термин: **WeakReference / ConditionalWeakTable**
> **Определение**: Слабая ссылка не препятствует GC собирать объект. `ConditionalWeakTable` — словарь с слабыми ключами (ephemerons), значение живет пока жив ключ.

### 🎯 Что показывает пример ConditionalWeakTable
```csharp
// Ключ не удерживается сильно, значение удерживается пока жив ключ
var table = new ConditionalWeakTable<object, string>();

var key = new object();
table.Add(key, "associated data");

// key можно использовать как "аттачмент" к любому объекту
// Когда key соберется GC — запись исчезнет автоматически
```
**Что демонстрирует**: Привязку метаданных к чужим объектам без утечек памяти.

**Где используется**: Расширение чужих объектов данными, кэши с автоматическим очищением, аттачменты к объектам.

### 📖 Термин: **Ephemeron (Эфимерон)**
> **Определение**: Пара (ключ, значение), где значение достижимо ТОЛЬКО если достижим ключ. GC видит: если ключ мертв → значение тоже мертво (даже если на значение есть ссылки из других мест).

---

### 📍 Резюме: диагностика GC
| Инструмент | Для чего |
|------------|----------|
| `GC.GetTotalMemory()` | Текущая выделенная память |
| `GC.CollectionCount(gen)` | Количество сборок по поколениям |
| `dotnet-counters` | Real-time метрики GC |
| `dotnet-gcdump` | Снимок кучи для анализа |
| `dotnet-trace` | ETW трассировка GC событий |
| `PerfView` | Глубокий анализ GC/CPU/Memory |
""",

    27: """
## 🎓 Педагогические дополнения к Networking

### 📖 Термин: **IHttpClientFactory**
> **Определение**: Фабрика для создания `HttpClient` с правильным управлением жизненным циклом, пулингом соединений, обработкой DNS изменений.

### 🎯 Что показывает пример неправильного HttpClient
```csharp
// НЕ ДЕЛАЙТЕ ТАК — утечка сокетов (TIME_WAIT)
using var client = new HttpClient();
var result = await client.GetStringAsync(url);
```
**Что демонстрирует**: Проблему исчерпания сокетов при частом создании HttpClient.

**Где используется**: В legacy коде, который нужно рефакторить.

### 📖 Термин: **Polly — Resilience Policies**
> **Определение**: Библиотека для реализации паттернов устойчивости: Retry, Circuit Breaker, Timeout, Bulkhead, Fallback.

### 🎯 Что показывает пример PolicyWrap
```csharp
// ПРАВИЛЬНЫЙ ПОРЯДОК: Timeout → Bulkhead → CircuitBreaker → Retry → Fallback
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
**Что демонстрирует**: Правильный порядок политик (внутреннее → внешнее) и комбинирование.

**Где используется**: Во всех исходящих HTTP/gRPC вызовах для устойчивости.

### 📖 Термин: **Jitter (дрожание)**
> **Определение**: Случайная добавка к задержке retry, чтобы предотвратить "thundering herd" (стадный эффект) — одновременный перезапрос множества клиентов после сбоя.

### 🎯 Что показывает пример с Jitter
```csharp
// Decorrelated Jitter (рекомендует AWS)
WaitAndRetryAsync(3, retryAttempt => 
    TimeSpan.FromSeconds(Math.Min(30, Math.Pow(2, retryAttempt))) + 
    TimeSpan.FromMilliseconds(Random.Shared.Next(0, 1000)))
```
**Что демонстрирует**: Как разбросать ретраи во времени.

**Где используется**: Во всех retry политиках для распределённых систем.

### 📖 Термин: **gRPC Interceptors**
> **Определение**: Middleware для gRPC, перехватывающие вызовы для логирования, метрик, авторизации, трассировки.

### 🎯 Что показывает пример Logging Interceptor
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
```
**Что демонстрирует**: Cross-cutting concerns для gRPC без загрязнения бизнес-логики.

**Где используется**: Логирование, метрики, трассировка, авторизация, валидация в gRPC.

### 📖 Термин: **SignalR Hub**
> **Определение**: Серверная точка входа для real-time коммуникации. Управляет подключениями, группами, рассылкой сообщений.

### 🎯 Что показывает пример SignalR Hub
```csharp
[Authorize]
public class TaskHub : Hub {
    public async Task JoinProject(string projectId) 
        => await Groups.AddToGroupAsync(Context.ConnectionId, $"project-{projectId}");
    
    public async Task LeaveProject(string projectId) 
        => await Groups.RemoveFromGroupAsync(Context.ConnectionId, $"project-{projectId}");
}
```
**Что демонстрирует**: Группировка подключений по проектам для таргетированной рассылки.

**Где используется**: Чат, уведомления, коллаборативное редактирование, дашборды, real-time обновления.

### 📖 Термин: **Rate Limiting (Ограничение частоты)**
> **Определение**: Защита от перегрузки, ограничивающая количество запросов за единицу времени.

### 🎯 Что показывает пример Token Bucket
```csharp
options.AddTokenBucketLimiter("api", opts => {
    opts.TokenLimit = 100;           // Макс токенов
    opts.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
    opts.QueueLimit = 10;            // Очередь ожидания
    opts.ReplenishmentPeriod = TimeSpan.FromSeconds(10);
    opts.TokensPerPeriod = 20;       // 20 токенов каждые 10 сек
});
```
**Что демонстрирует**: Алгоритм "ведро с жетонами" для burst трафика.

**Где используется**: Публичные API, авторизация, защита от DDoS, справедливое использование ресурсов.

---

### 📍 Резюме: выбор подхода
| Задача | Решение |
|--------|---------|
| Исходящие HTTP вызовы | IHttpClientFactory + Polly |
| gRPC сервисы | protobuf, interceptors, code-first |
| Real-time уведомления | SignalR + Redis backplane |
| Ограничение нагрузки | Rate Limiting (Token Bucket / Sliding Window) |
| IPC | Named Pipes / Unix Domain Sockets |
""",

    28: """
## 🎓 Педагогические дополнения к Security

### 📖 Термин: **JWT (JSON Web Token)**
> **Определение**: Компактный, URL-safe токен для передачи claims между сторонами. Состоит из Header.Payload.Signature, подписанного секретом или приватным ключом.

### 🎯 Что показывает пример JWT с Refresh Token Rotation
```csharp
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
```
**Что демонстрирует**: Ротация refresh токенов — старый отзывается, выдаются новые пары (безопаснее).

**Где используется**: В системах аутентификации с долгосрочными сессиями.

### 📖 Термин: **Resource-based Authorization (RBAC на уровне ресурса)**
> **Определение**: Авторизация, принимающая решение на основе конкретного ресурса (документа, заказа) и прав пользователя на нём.

### 🎯 Что показывает пример Resource-based Auth
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
**Что демонстрирует**: Авторизация на уровне конкретного экземпляра ресурса.

**Где используется**: Многотенантные системы, документы с владельцами, проекты с участниками.

### 📖 Термин: **AES-GCM (Galois/Counter Mode)**
> **Определение**: Аутентифицированное шифрование — одновременно обеспечивает конфиденциальность (шифрование) и целостность (аутентификация) данных.

### 🎯 Что показывает пример AES-GCM
```csharp
public static (byte[] ciphertext, byte[] nonce, byte[] tag) Encrypt(byte[] plaintext, byte[] key) {
    var nonce = RandomNumberGenerator.GetBytes(12);  // 96-bit nonce для GCM
    var tag = new byte[16];
    var ciphertext = new byte[plaintext.Length];
    
    using var aes = new AesGcm(key);
    aes.Encrypt(nonce, plaintext, ciphertext, tag);
    return (ciphertext, nonce, tag);
}
```
**Что демонстрирует**: Современное аутентифицированное шифрование (confidentiality + integrity).

**Где используется**: Шифрование PII, токенов, конфиденциальных данных в БД/передаче.

### 📖 Термин: **Data Protection API (ASP.NET Core)**
> **Определение**: Встроенный механизм защиты данных (шифрование/подпись) с управлением ключами, ротацией, purpose chains.

### 🎯 Что показывает пример Data Protection
```csharp
builder.Services.AddDataProtection()
    .PersistKeysToFileSystem(new DirectoryInfo("/app/keys"))
    .SetApplicationName("MyApp")
    .SetDefaultKeyLifetime(TimeSpan.FromDays(90))
    .ProtectKeysWithDpapi();  // Windows: DPAPI

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
**Что демонстрирует**: Безопасная защита токенов/данных с ротацией ключей и purpose isolation.

**Где используется**: CSRF токены, password reset токены, email confirmation, защита PII.

### 📖 Термин: **Security Headers (HTTP заголовки безопасности)**
> **Определение**: HTTP заголовки, указывающие браузеру политики безопасности: CSP, HSTS, X-Frame-Options и др.

---

### 📍 Резюме: чек-лист безопасности
- [ ] HTTPS везде (HSTS)
- [ ] JWT с коротким TTL + Refresh Tokens
- [ ] Аутентификация: MFA, lockout, password hashing (Argon2)
- [ ] Авторизация: Policies + Resource-based
- [ ] Криптография: AES-GCM, Argon2, Data Protection API
- [ ] Headers: CSP, HSTS, X-Frame-Options, Referrer-Policy
- [ ] CSRF: Anti-forgery tokens / SameSite=Strict
- [ ] Secrets: User Secrets (dev), Key Vault (prod), НЕ в коде!
""",

    29: """
## 🎓 Педагогические дополнения к Observability

### 📖 Термин: **Structured Logging (Структурированное логирование)**
> **Определение**: Логирование в формате ключ-значение (JSON), где каждое поле отдельно, что позволяет запрашивать/фильтровать логи в Seq/ELK/Grafana.

### 🎯 Что показывает пример структурированного логирования
```csharp
// ПЛОХО — строка, нельзя фильтровать
_logger.LogInformation("User 123 placed order 456 for $99.99");

// ХОРОШО — свойства для запросов в Seq/ELK
_logger.LogInformation("User {UserId} placed order {OrderId} for {Amount:C}", 123, 456, 99.99m);
```
**Что демонстрирует**: Разницу между неструктурированными и структурированными логами.

**Где используется**: Во всех продакшен-логах для наблюдаемости.

### 📖 Термин: **Enrichment (Обогащение логов)**
> **Определение**: Автоматическое добавление контекстных свойств (ThreadId, MachineName, CorrelationId, UserId) ко ВСЕМ логам в области видимости.

### 🎯 Что показывает пример Enrichment
```csharp
// Добавить свойства к ВСЕМ логам в scope
using (LogContext.PushProperty("CorrelationId", correlationId))
using (LogContext.PushProperty("UserId", userId)) {
    _logger.LogInformation("Processing order"); // автоматически имеет CorrelationId, UserId
}
```
**Что демонстрирует**: Как автоматически добавлять контекст без ручного добавления в каждый лог.

**Где используется**: Распределённые системы, микросервисы, request tracing.

### 📖 Термин: **OpenTelemetry**
> **Определение**: Единый стандарт для метрик, трассировки и логов. Независим от вендора, экспортирует в Prometheus, Jaeger, Zipkin, Grafana и др.

### 📖 Термин: **Activity / ActivitySource**
> **Определение**: Единица работы в распределённой трассировке. `ActivitySource` создаёт `Activity` (spans), которые формируют trace.

### 🎯 Что показывает пример ActivitySource
```csharp
public static class AppActivitySource {
    public static readonly ActivitySource Source = new("MyApp.Activities");
}

public class OrderService {
    public async Task<Order> CreateOrderAsync(CreateOrderDto dto) {
        using var activity = AppActivitySource.Source.StartActivity("CreateOrder", ActivityKind.Internal);
        activity?.SetTag("customer.id", dto.CustomerId);
        activity?.SetTag("items.count", dto.Items.Count);
        
        var order = await _repo.CreateAsync(dto);
        activity?.SetTag("order.id", order.Id);
        activity?.SetStatus(ActivityStatusCode.Ok);
        return order;
    }
}
```
**Что демонстрирует**: Создание кастомных spans для бизнес-операций.

**Где используется**: Трассировка бизнес-операций, измерение latency, debug распределённых систем.

### 📖 Термин: **W3C TraceContext**
> **Определение**: Стандарт заголовков для передачи trace контекста между сервисами: `traceparent`, `tracestate`, `baggage`.

### 🎯 Что показывает пример корреляции логов
```csharp
// Serilog + OpenTelemetry = TraceId/SpanId в логах
.Enrich.WithProperty("TraceId", () => Activity.Current?.TraceId.ToString() ?? "none")
.Enrich.WithProperty("SpanId", () => Activity.Current?.SpanId.ToString() ?? "none")
```
**Что демонстрирует**: Автоматическое добавление TraceId/SpanId в логи для корреляции с трассировкой.

**Где используется**: Всякая распределённая система для end-to-end observability.

### 📖 Термин: **Baggage**
> **Определение**: Пользовательские пары ключ-значение, передающиеся через trace контекст (W3C Baggage header) для распространения контекста.

---

### 📍 Резюме: стек Observability
| Уровень | Инструменты | Что даёт |
|---------|-------------|----------|
| Logs | Serilog + Seq/ELK | Что произошло, детали ошибок |
| Metrics | OpenTelemetry + Prometheus/Grafana | Состояние системы, тренды, алерты |
| Traces | ActivitySource + Jaeger/Zipkin | Где время, bottlenecks, ошибки |
| Profiling | dotnet-trace, PerfView, BenchmarkDotNet | CPU/память/GC глубокий анализ |
""",

    30: """
## 🎓 Педагогические дополнения к Cloud Native

### 📖 Термин: **Multi-stage Docker Build**
> **Определение**: Dockerfile с несколькими этапами (FROM), где ранние этапы (build) не попадают в итоговый образ. Итоговый образ содержит только runtime артефакты.

### 🎯 Что показывает пример Multi-stage Dockerfile
```dockerfile
# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY *.sln .
COPY src/*/*.csproj ./src/
RUN dotnet restore
COPY . .
RUN dotnet publish src/MyApp.Api/MyApp.Api.csproj -c Release -o /app/publish --no-restore

# Stage 2: Runtime (distroless)
FROM mcr.microsoft.com/dotnet/aspnet:8.0-distroless AS runtime
WORKDIR /app
USER 65532:65532
COPY --from=build --chown=65532:65532 /app/publish .
ENTRYPOINT ["dotnet", "MyApp.Api.dll"]
```
**Что демонстрирует**: Разделение build-time и runtime зависимостей, минимальный итоговый образ.

**Где используется**: Во всех продакшен Docker образах.

### 📖 Термин: **Layer Caching (Кэширование слоёв)**
> **Определение**: Docker кэширует каждый слой. Если файлы не изменились — слой берётся из кэша. Порядок инструкций критичен.

### 🎯 Что показывает пример порядка COPY
```dockerfile
# ПЛОХО — копируем всё, потом restore (инвалидирует кэш при любом изменении кода)
COPY . .
RUN dotnet restore

# ХОРОШО — сначала csproj, restore, потом код
COPY *.sln .
COPY src/*/*.csproj ./src/
RUN dotnet restore
COPY . .
RUN dotnet publish ...
```
**Что демонстрирует**: Как максимально использовать кэш Docker.

**Где используется**: Во всех Dockerfile для ускорения CI/CD.

### 📖 Термин: **Distroless**
> **Определение**: Минимальные базовые образы без shell, пакетного менеджера, лишних утилит. Только runtime и зависимости.

### 🎯 Что показывает сравнение базовых образов
| Base Image | Размер | Безопасность | Shell | Package Manager |
|---|---|---|---|---|
| `aspnet:8.0` (Debian) | ~100 MB | Стандарт | bash | apt |
| `aspnet:8.0-alpine` | ~30 MB | Меньше | sh | apk |
| `aspnet:8.0-distroless` | ~25 MB | Минимальная | **нет** | **нет** |

**Что демонстрирует**: Трейдофф между размером/безопасностью и отладкой.

**Где используется**: Продакшен — distroless, дев/стейджинг — alpine для отладки.

### 📖 Термин: **Helm (Package Manager для Kubernetes)**
> **Определение**: Менеджер пакетов для K8s, управляющий чартами (шаблоны манифестов + values).

### 🎯 Что показывает пример Helm Chart
```yaml
# values.yaml
replicaCount: 3
image:
  repository: myregistry/myapp
  tag: "1.2.3"
ingress:
  enabled: true
  hosts:
  - host: myapp.example.com
    paths: ["/"]
```
**Что демонстрирует**: Параметризация манифестов через values файлы.

**Где используется**: Управление релизами, окружениями (dev/staging/prod), зависимостями.

### 📖 Термин: **Kustomize (Native K8s Customization)**
> **Определение**: Нативный K8s инструмент для кастомизации манифестов без шаблонов — через базовые ресурсы + оверлеи (overlays) + патчи.

### 🎯 Что показывает пример Kustomize
```yaml
# base/kustomization.yaml
resources:
- deployment.yaml
- service.yaml

# overlays/prod/kustomization.yaml
bases:
- ../../base
patches:
- path: replica-patch.yaml
images:
- name: myregistry/myapp
  newTag: v1.2.3
```
**Что демонстрирует**: Нативный K8s способ управления окружениями без Helm.

**Где используется**: Когда нужен нативный K8s подход, GitOps, простые кастомизации.

### 📖 Термин: **Service Mesh (Istio/Linkerd)**
> **Определение**: Инфраструктурный слой для управления межсервисным трафиком: mTLS, traffic splitting, observability, security policies.

### 🎯 Что показывает пример Istio VirtualService
```yaml
# Canary Deployment — 10% трафика на v2
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
**Что демонстрирует**: Traffic splitting для canary/blue-green деплоев без изменения кода.

**Где используется**: Canary deployments, A/B тестирование, миграции, feature flags.

### 📖 Термин: **GitOps (ArgoCD/Flux)**
> **Определение**: Подход к CD, где желаемое состояние кластера описано в Git, и оператор (ArgoCD/Flux) непрерывно синхронизирует кластер с Git.

---

### 📍 Резюме: Cloud Native чек-лист
- [ ] Multi-stage Dockerfile + distroless + non-root
- [ ] K8s: Deployment, Service, Ingress, ConfigMap/Secret, HPA, PDB
- [ ] Probes: liveness/readiness/startup
- [ ] Helm: charts, values, dependencies
- [ ] Service Mesh: mTLS, traffic splitting, observability
- [ ] CI/CD: GitHub Actions (test/build/push) + ArgoCD (GitOps deploy)
- [ ] Observability: Serilog, OpenTelemetry, Prometheus/Grafana
""",

    31: """
## 🎓 Педагогические дополнения к Производительности

### 📖 Термин: **BenchmarkDotNet**
> **Определение**: Библиотека для наукоёмких микробенчмарков: прогрев, статистика, анализ памяти, дизассемблирование, сравнение рантаймов.

### 🎯 Что показывает пример BenchmarkDotNet
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
```
**Что демонстрирует**: Научное измерение производительности с памятью и асм кодом.

**Где используется**: В разработке высокопроизводительных библиотек, сравнении алгоритмов, регрессионном тестировании производительности.

### 📖 Термин: **SIMD (Single Instruction Multiple Data)**
> **Определение**: Параллельная обработка нескольких данных одной инструкцией. В .NET: `Vector<T>` (переносимо), `HardwareIntrinsics` (AVX2/SSE/NEON).

### 🎯 Что показывает пример SIMD
```csharp
// Vector<T> — переносимая абстракция
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
**Что демонстрирует**: Векторизацию циклов для ускорения математических операций.

**Где используется**: Математика, обработка сигналов, ML, обработка изображений, физика, криптография.

### 📖 Термин: **PGO (Profile-Guided Optimization)**
> **Определение**: Оптимизация на основе профиля реального запуска. JIT перекомпилирует горячие методы с учётом собранной статистики.

### 🎯 Что показывает пример Dynamic PGO
```xml
<TieredCompilation>true</TieredCompilation>
<TieredPGO>true</TieredPGO>
```
**Что демонстрирует**: Автоматическую оптимизацию горячих путей на основе реального профиля.

**Где используется**: В .NET 8+ продакшене для автоматического ускорения горячих путей.

### 📖 Термин: **NativeAOT**
> **Определение**: Компиляция в полностью нативный бинарь без JIT, рефлексии, динамической загрузки сборок.

### 🎯 Что показывает пример NativeAOT
```xml
<PublishAot>true</PublishAot>
<StripSymbols>true</StripSymbols>
<IlcOptimizationPreference>Speed</IlcOptimizationPreference>
```
**Что демонстрирует**: Полностью нативный бинарь без JIT.

**Где используется**: CLI инструменты, Serverless (cold start), Edge/IoT, Security-critical.

### 📖 Термин: **Span<T> / Memory<T>**
> **Определение**: Типы для работы с непрерывными областями памяти без аллокаций и копирований. `Span<T>` — ref struct (только стек), `Memory<T>` — может быть на куче.

### 🎯 Что показывает пример Span парсинга
```csharp
// ПАРСИНГ БЕЗ АЛЛОКАЦИЙ
public static bool TryParseInt(ReadOnlySpan<char> span, out int value) {
    value = 0;
    foreach (var c in span) {
        if (c < '0' || c > '9') return false;
        value = value * 10 + (c - '0');
    }
    return true;
}
```
**Что демонстрирует**: Работу с памятью без аллокаций.

**Где используется**: Парсинг, сериализация, сетевые протоколы, высоконагруженные пути.

---

### 📍 Резюме: чек-лист оптимизации
1. **Измеряй** — BenchmarkDotNet с MemoryDiagnoser
2. **Избегай аллокаций** — Span, ArrayPool, stackalloc, ObjectPool
3. **Векторизуй** — Vector<T> / HardwareIntrinsics (с fallback!)
4. **PGO** — `<TieredPGO>true</TieredPGO>`
5. **Профилируй** — dotnet-trace + PerfView/Speedscope
6. **NativeAOT** — для cold start критических сценариев
""",

    32: """
## 🎓 Педагогические дополнения к Advanced Patterns

### 📖 Термин: **Functional C# (Функциональный C#)**
> **Определение**: Стиль программирования с невидимыми данными, композицией функций, избеганием исключений для управления потоком (Railway-oriented programming).

### 📖 Термин: **Result<T> / Option<T>**
> **Определение**: Типы для представления успеха/ошибки (`Result<T>`) или наличия/отсутствия значения (`Option<T>`) вместо null и исключений.

### 🎯 Что показывает пример Railway-oriented programming
```csharp
// Вместо try/catch — цепочка Result
public Result<Order> PlaceOrder(PlaceOrderCommand cmd) =>
    ValidateCommand(cmd)
    .Bind(CheckInventory)
    .Bind(ReserveItems)
    .Bind(CalculateTotal)
    .Bind(ProcessPayment)
    .Bind(CreateOrder)
    .Bind(SendConfirmation);
```
**Что демонстрирует**: Композицию операций без исключений — каждый шаг возвращает `Result`, ошибка прерывает цепочку.

**Где используется**: Бизнес-логика, валидация, пайплайны обработки, где важна явная обработка ошибок.

### 📖 Термин: **Rx.NET (Reactive Extensions)**
> **Определение**: Библиотека для реактивного программирования: `IObservable<T>` (push-последовательности), операторы, schedulers, backpressure.

### 🎯 Что показывает пример Rx.NET Pipeline
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
**Что демонстрирует**: Декларативную обработку потоков данных с операторами.

**Где используется**: Event streams, UI события, телеметрия, стриминг данных, real-time обновления.

### 📖 Термин: **Actor Model (Акторная модель)**
> **Определение**: Модель конкурентности, где "акторы" — изолированные единицы состояния и поведения, общающиеся только через асинхронные сообщения.

### 🎯 Что показывает пример Akka.NET Actor
```csharp
public class OrderActor : ReceiveActor {
    private OrderState _state = new();
    
    public OrderActor() {
        Command<PlaceOrder>(Handle);
        Command<GetOrder>(cmd => Sender.Tell(_state));
        
        // Persistence (Event Sourcing)
        Recover<OrderPlaced>(e => _state = _state.Apply(e));
    }
}
```
**Что демонстрирует**: Инкапсуляция состояния в акторе, обработка команд, persistence.

**Где используется**: Высоконагруженные системы, distributed systems, gaming, financial trading.

### 📖 Термин: **Orleans — Virtual Actors (Grains)**
> **Определение**: Реализация акторной модели с виртуальными акторами (Grains) — акторы создаются/активируются по требованию, имеют устойчивое состояние.

### 🎯 Что показывает пример Orleans Grain
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
**Что демонстрирует**: Виртуальные акторы с автоматическим управлением жизненным циклом и персистентностью.

**Где используется**: Распределённые системы, корзины покупок, сессии пользователей, IoT устройства.

### 📖 Термин: **Circuit Breaker**
> **Определение**: Паттерн, предотвращающий каскадные сбои: при превышении порога ошибок "размыкает цепь" и быстро проваливает запросы, давая сервису время восстановиться.

### 🎯 Что показывает пример Circuit Breaker
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
**Что демонстрирует**: Защиту от каскадных сбоев в распределённых системах.

**Где используется**: Внешние API вызовы, БД, микросервисы — везде, где зависимость может упасть.

### 📖 Термин: **Saga Pattern**
> **Определение**: Паттерн распределённой транзакции: последовательность локальных транзакций с компенсацией при ошибке (обратный порядок).

### 🎯 Что показывает пример Saga
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
**Что демонстрирует**: Реализацию распределённой транзакции с компенсацией.

**Где используется**: Микросервисы, заказ-оплата-уведомление, любые распределённые бизнес-процессы.

### 📖 Термин: **Event Sourcing**
> **Определение**: Паттерн, где состояние агрегата восстанавливается из последовательности событий (Event Log), а не хранится напрямую.

---

### 📍 Резюме: когда что применять
| Паттерн | Когда применять |
|---------|-----------------|
| Functional C# / Result/Option | Бизнес-логика, валидация, pipeline'ы |
| Rx.NET | Event streams, UI, телеметрия, real-time |
| Akka.NET | Классические акторы, сложное состояние, clustering |
| Orleans | Виртуальные акторы, простое масштабирование, persistence |
| Circuit Breaker | Внешние зависимости, защита от каскадных сбоев |
| Saga | Распределённые транзакции, микросервисы |
| Event Sourcing | Аудит обязателен, сложные бизнес-процессы |
""",

    33: """
## 🎓 Педагогические дополнения к Финальному проекту

### 📖 Термин: **Clean Architecture в действии**
> **Определение**: Практическое применение чистой архитектуры в полном стеке: Domain → Application → Infrastructure → API/Client.

### 🎯 Что показывает структура решения
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
│   └── Configuration/           # Options classes, DI registration
│
├── TaskManager.Api/             # Presentation Layer
│   ├── Endpoints/               # Minimal API (MapGroup)
│   ├── Hubs/                    # TaskHub (SignalR)
│   ├── Middleware/              # ExceptionHandling, RateLimiting
│   └── Program.cs               # Composition Root
│
├── TaskManager.Client/          # Blazor WebAssembly
│   ├── Pages/                   # Tasks.razor, Projects.razor
│   ├── Components/              # TaskCard, TaskForm
│   ├── Services/                # ApiClient, SignalRClient, AuthStateProvider
│   └── State/                   # Flux/Redux state management
```
**Что демонстрирует**: Реальную структуру Clean Architecture проекта.

**Где используется**: В качестве шаблона для новых проектов, референс-архитектура.

### 🎯 Что показывает Domain Aggregate с Domain Events
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
}
```
**Что демонстрирует**: Инкапсуляцию бизнес-логики, генерацию Domain Events при изменении состояния.

**Где используется**: В Domain слое любого DDD проекта.

### 🎯 Что показывает Outbox Pattern
```csharp
public override async Task<int> SaveChangesAsync(CancellationToken ct = default) {
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
```
**Что демонстрирует**: Надёжную публикацию Domain Events в той же транзакции, что и бизнес-данные.

**Где используется**: В EF Core проектах с Domain Events для гарантированной доставки.

### 🎯 Что показывает CQRS + MediatR
```csharp
// Command
public record CreateTaskCommand(string Title, string Description, Guid ProjectId) : IRequest<TaskId>;

public class CreateTaskHandler : IRequestHandler<CreateTaskCommand, TaskId> {
    public async Task<TaskId> Handle(CreateTaskCommand cmd, CancellationToken ct) {
        var task = Task.Create(TaskId.New(), cmd.Title, cmd.Description, new ProjectId(cmd.ProjectId), _currentUser.UserId!);
        await _repo.AddAsync(task, ct);
        await _uow.SaveChangesAsync(ct);
        return task.Id;
    }
}

// Pipeline Behavior — Validation
public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> {
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct) {
        var failures = _validators.Select(v => v.Validate(new ValidationContext<TRequest>(request)))
            .SelectMany(r => r.Errors).Where(e => e != null).ToList();
        if (failures.Any()) throw new ValidationException(failures);
        return await next();
    }
}
```
**Что демонстрирует**: Разделение команд/запросов, pipeline behaviors для cross-cutting concerns.

**Где используется**: В Application слое CQRS архитектуры.

### 🎯 Что показывает SignalR Real-time
```csharp
[Authorize]
public class TaskHub : Hub {
    public async Task JoinProject(string projectId) 
        => await Groups.AddToGroupAsync(Context.ConnectionId, $"project-{projectId}");
}

public class SignalRNotificationService : INotificationService {
    public async Task NotifyTaskCreated(TaskDto task) 
        => await _hub.Clients.Group($"project-{task.ProjectId}").SendAsync("TaskCreated", task);
}
```
**Что демонстрирует**: Real-time уведомления через группы проектов.

**Где используется**: Коллаборативные приложения, дашборды, чаты, real-time обновления.

### 🎯 Что показывает Blazor Client с SignalR
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
**Что демонстрирует**: Blazor WASM клиент с автоматической переподключением и JWT в query string.

**Где используется**: Blazor WASM приложения с real-time обновлениями.

### 🎯 Что показывает Testcontainers Integration Tests
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
**Что демонстрирует**: Интеграционные тесты с реальной БД (Testcontainers) и полным стеком приложения.

**Где используется**: В CI/CD пайплайнах для проверки интеграции.

### 🎯 Что показывает Docker Multi-stage + Distroless
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
**Что демонстрирует**: Production-ready Dockerfile: multi-stage, distroless, non-root, health check.

**Где используется**: Во всех продакшен Docker образах.

### 🎯 Что показывает Helm + K8s
```yaml
# values.yaml
replicaCount: 3
image:
  repository: ghcr.io/myorg/taskmanager
  tag: "1.0.0"
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
**Что демонстрирует**: Production-ready Helm chart с зависимостями и автоскейлингом.

**Где используется**: В Kubernetes продакшене с Helm.

### 🎯 Что показывает CI/CD Pipeline
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
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
**Что демонстрирует**: GitHub Actions pipeline: test → build → docker push → ArgoCD deploy.

**Где используется**: В GitOps CI/CD пайплайнах.

---

### 🎉 Итоговый чек-лист готовности
- [ ] Clean Architecture: 4 слоя, зависимости внутрь
- [ ] DDD: Aggregates, Value Objects, Domain Events, Repository pattern
- [ ] CQRS + MediatR: Commands/Queries, Pipeline Behaviors (Validation, Transaction, Logging)
- [ ] EF Core: Outbox Pattern для надёжности Domain Events, миграции
- [ ] SignalR: real-time уведомления, Groups для проектов, JWT в query string для WebSockets
- [ ] Blazor WASM: SignalR клиент, автоматическое переподключение, state management
- [ ] Testing: Unit (Moq), Integration (Testcontainers), E2E (Playwright)
- [ ] Docker: Multi-stage, Distroless, Non-root, Health Checks, Layer Caching
- [ ] K8s/Helm: Deployment, Service, Ingress, HPA, PDB, ConfigMap/Secret, dependencies
- [ ] CI/CD: GitHub Actions (test, build, push), ArgoCD (GitOps), semver tags
- [ ] Observability: Serilog, OpenTelemetry, Prometheus/Grafana, Jaeger/Zipkin
""",
}

# ============================================================
# APPLY ENHANCEMENTS
# ============================================================

def apply_pedagogical():
    for i in range(15, 34):
        path = f'fixtures/lessons/csharp/{i:02d}.json'
        if not Path(path).exists():
            print(f"Lesson {i:02d}: File not found")
            continue
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if i in PEDAGOGICAL:
            enhancement = PEDAGOGICAL[i]
            blocks = process_markdown(enhancement)
            data['content_blocks'].extend(blocks)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write('\n')
            
            print(f"Enhanced lesson {i:02d} with {len(blocks)} pedagogical blocks")
        else:
            print(f"Lesson {i:02d}: No pedagogical content defined")

    print("Pedagogical enhancement complete!")

if __name__ == '__main__':
    apply_pedagogical()