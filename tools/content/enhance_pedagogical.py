#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add pedagogical explanations: what examples show, where used, term definitions."""

import json
import re
from pathlib import Path

# Reuse markdown processing
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

PEDAGOGICAL_ENHANCEMENTS = {}

# ============================================================
# LESSON 15: LINQ - PEDAGOGICAL ENHANCEMENTS
# ============================================================
PEDAGOGICAL_ENHANCEMENTS[15] = """
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
"""

# ============================================================
# LESSON 16: Collections - PEDAGOGICAL
# ============================================================
PEDAGOGICAL_ENHANCEMENTS[16] = """
## 🎓 Педагогические дополнения к коллекциям

### 📖 Термин: **Амортизированная сложность O(1)**
> **Определение**: Операция в среднем занимает постоянное время, хотя отдельные вызовы могут быть медленнее. Для `List.Add`: обычно O(1), но когда массив переполняется — происходит реаллокация O(n), что в среднем даёт O(1).

### 📖 Термин: **Capacity vs Count**
> - **Count** — сколько элементов сейчас в коллекции
> - **Capacity** — сколько памяти выделено под капотом (всегда ≥ Count)
> - При превышении Capacity происходит реаллокация (создание нового массива + копирование)

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

**Где используется**: В высоконагруженных системах, парсерах больших файлов,.batch processing, когда известно приблизительное количество элементов.

### 📖 Термин: **Хеш-таблица (Hash Table)**
> **Определение**: Структура данных, хранящая пары ключ-значение в массиве «корзин» (buckets). Ключ преобразуется хеш-функцией в индекс корзины. Коллизии (разные ключи → одна корзина) решаются цепочками.

### 🎯 Что показывает пример с `GetHashCode`/`Equals`
```csharp
// ПЛОХО: mutable ключ
var dict = new Dictionary<List<int>, string>();
var key = new List<int> { 1, 2 };
dict[key] = "value";
key.Add(3);  // Хеш изменился! Элемент "потерян"
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
"""

# ============================================================
# LESSON 17: Async/Await - PEDAGOGICAL
# ============================================================
PEDAGOGICAL_ENHANCEMENTS[17] = """
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
5. **Task.WhenAll** для параллелизма, **WhenAny** для таймаутов
6. **IAsyncEnumerable** для стриминга больших данных
"""

# ============================================================
# LESSON 18: CLR/GC/JIT - PEDAGOGICAL
# ============================================================
PEDAGOGICAL_ENHANCEMENTS[18] = """
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
"""

# ============================================================
# LESSON 19: Testing - PEDAGOGICAL
# ============================================================
PEDAGOGICAL_ENHANCEMENTS[19] = """
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
"""

# ============================================================
# LESSON 20: JSON/Files/SQL - PEDAGOGICAL
# ============================================================
PEDAGOGICAL_ENHANCEMENTS[20] = """
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
"""

# I'll continue with more lessons but this is getting very long. Let me create a script to apply these.

# Write the script to apply pedagogical enhancements