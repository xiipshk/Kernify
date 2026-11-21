#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate advanced lessons (25-33) with proper content extraction."""

import json
import re
from pathlib import Path

# Reuse the markdown processing functions from the previous script
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


def write_lesson(num, data):
    path = f'fixtures/lessons/csharp/{num:02d}.json'
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Written lesson {num:02d}: {data["title"][:60]}...')


# ============================================================
# LESSON 25: Extension Members, Operators, Indexers
# ============================================================
lesson_25_md = """## 🎯 Что вы узнаете
- Extension methods: синтаксис, приоритет, generic extensions
- Extension properties (C# 12) — расширение типов свойствами
- Перегрузка операторов: арифметические, сравнения, приведения, логические
- Индексаторы: `this[]`, несколько параметров, `params`
- Pattern-based API: `GetEnumerator` (foreach), `GetAwaiter` (await), `Dispose` (using), `Deconstruct` (деконструкция)

## 🔧 Extension Methods — расширение типов

### Базовый синтаксис

```csharp
public static class StringExtensions {
    // this string — расширяемый тип
    public static bool IsNullOrEmpty(this string s) => string.IsNullOrEmpty(s);
    
    // Generic extension
    public static TResult Pipe<T, TResult>(this T value, Func<T, TResult> func) => func(value);
    
    // Несколько параметров
    public static string Repeat(this string s, int count, string separator = "") 
        => string.Join(separator, Enumerable.Repeat(s, count));
}
```

### Использование

```csharp
"hello".IsNullOrEmpty();           // false
"hello".Pipe(s => s.ToUpper());    // "HELLO"
"ha".Repeat(3, " ");               // "ha ha ha"
```

### Приоритет и конфликты

```csharp
// Instance method ПОБЕЖДАЕТ extension method
class MyList : List<int> {
    public int Count() => 999; // переопределяет List.Count
}

var list = new MyList();
list.Count(); // 999 (instance method), не Enumerable.Count()
```

### Extension Properties (C# 12)

```csharp
// Только геттеры!
public static class DateTimeExtensions {
    public static int WeekOfYear(this DateTime date) 
        => CultureInfo.CurrentCulture.Calendar.GetWeekOfYear(date, CalendarWeekRule.FirstFourDayWeek, DayOfWeek.Monday);
    
    // Можно с параметрами (на самом деле метод, но выглядит как свойство)
    public static bool IsWeekend(this DateTime date) 
        => date.DayOfWeek is DayOfWeek.Saturday or DayOfWeek.Sunday;
}
```

## ➕ Перегрузка операторов

### Арифметические

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
    public static Vector2 operator /(Vector2 v, double scalar) => new(v.X / scalar, v.Y / scalar);
    
    // Унарные
    public static Vector2 operator -(Vector2 v) => new(-v.X, -v.Y);
    public static Vector2 operator ++(Vector2 v) => v + new Vector2(1, 1);
    public static Vector2 operator --(Vector2 v) => v - new Vector2(1, 1);
}
```

### Сравнения

```csharp
// Обязательно парно: == и !=, < и >, <= и >=
public static bool operator ==(Vector2 a, Vector2 b) => a.X == b.X && a.Y == b.Y;
public static bool operator !=(Vector2 a, Vector2 b) => !(a == b);

// Для IComparable
public static bool operator <(Vector2 a, Vector2 b) => a.Length < b.Length;
public static bool operator >(Vector2 a, Vector2 b) => b < a;
public static bool operator <=(Vector2 a, Vector2 b) => !(b < a);
public static bool operator >=(Vector2 a, Vector2 b) => !(a < b);

// Equals и GetHashCode ДОЛЖНЫ быть переопределены при ==/!=
public override bool Equals(object? obj) => obj is Vector2 v && this == v;
public override int GetHashCode() => HashCode.Combine(X, Y);
```

### Неявные и явные преобразования

```csharp
public readonly struct Temperature {
    public double Celsius { get; }
    public Temperature(double celsius) => Celsius = celsius;
    
    // Implicit — безопасное, без потери данных
    public static implicit operator Temperature(double celsius) => new(celsius);
    public static implicit operator double(Temperature t) => t.Celsius;
    
    // Explicit — может терять данные или выбрасывать исключение
    public static explicit operator Temperature(Fahrenheit f) => new((f.Value - 32) * 5 / 9);
    public static explicit operator Fahrenheit(Temperature t) => new(t.Celsius * 9 / 5 + 32);
}

// Использование
Temperature t = 25.0;           // implicit double -> Temperature
double c = t;                   // implicit Temperature -> double
Fahrenheit f = (Fahrenheit)t;   // explicit cast required
```

### Логические операторы (для nullable bool / custom types)

```csharp
// true/false операторы — для использования в if, &&, ||
public readonly struct Optional<T> {
    private readonly T _value;
    private readonly bool _hasValue;
    
    public static bool operator true(Optional<T> opt) => opt._hasValue;
    public static bool operator false(Optional<T> opt) => !opt._hasValue;
    
    // && и || — короткое замыкание
    public static Optional<T> operator &(Optional<T> a, Optional<T> b) 
        => a._hasValue ? b : a;
    public static Optional<T> operator |(Optional<T> a, Optional<T> b) 
        => a._hasValue ? a : b;
}
```

## 📇 Индексаторы

### Базовый индексатор

```csharp
public class Matrix {
    private readonly double[,] _data;
    
    public Matrix(int rows, int cols) => _data = new double[rows, cols];
    
    // Два параметра
    public double this[int row, int col] {
        get => _data[row, col];
        set => _data[row, col] = value;
    }
    
    // Можно несколько индексаторов с разными сигнатурами
    public double this[Point p] {
        get => _data[p.X, p.Y];
        set => _data[p.X, p.Y] = value;
    }
}

var m = new Matrix(3, 3);
m[1, 2] = 5.0;
var val = m[1, 2];
```

### Индексатор с params (C# 12)

```csharp
public class MultiDimArray {
    private readonly Dictionary<string, object> _data = new();
    
    public object this[params int[] indices] {
        get => _data[string.Join(",", indices)];
        set => _data[string.Join(",", indices)] = value;
    }
}

var arr = new MultiDimArray();
arr[1, 2, 3] = "value"; // params int[]
```

### Индексатор только для чтения / только для записи

```csharp
public class ReadOnlyCollection<T> {
    private readonly T[] _items;
    
    // Только get
    public T this[int index] => _items[index];
    
    // init-only setter (C# 9)
    public T this[int index] { get => _items[index]; init => _items[index] = value; }
}
```

## 🎭 Pattern-based API — duck typing для языковых конструкций

### foreach — GetEnumerator

```csharp
// Любой тип с GetEnumerator() возвращающим IEnumerator<T> работает в foreach
public class NumberRange {
    private readonly int _start, _end;
    
    public NumberRange(int start, int end) { _start = start; _end = end; }
    
    public IEnumerator<int> GetEnumerator() {
        for (int i = _start; i <= _end; i++) yield return i;
    }
}

// Использование
foreach (var n in new NumberRange(1, 5)) Console.WriteLine(n); // 1 2 3 4 5
```

### await — GetAwaiter

```csharp
// Любой тип с GetAwaiter() возвращающим INotifyCompletion/ICriticalNotifyCompletion
public readonly struct ValueTaskAwaiter<T> : INotifyCompletion {
    private readonly ValueTask<T> _task;
    
    public ValueTaskAwaiter(ValueTask<T> task) => _task = task;
    public bool IsCompleted => _task.IsCompleted;
    public T GetResult() => _task.Result;
    public void OnCompleted(Action continuation) => _task.AsTask().ContinueWith(_ => continuation());
}

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
var result = await lazy; // работает!
```

### using / using var — Dispose / DisposeAsync

```csharp
// IDisposable / IAsyncDisposable — для using
public class ResourceHolder : IDisposable, IAsyncDisposable {
    private bool _disposed;
    
    public void Dispose() {
        if (_disposed) return;
        // cleanup
        _disposed = true;
    }
    
    public async ValueTask DisposeAsync() {
        if (_disposed) return;
        await CleanupAsync();
        _disposed = true;
    }
}

// using var — неявный using блок
using var resource = new ResourceHolder();
// автоматически Dispose() в конце scope
```

### Деконструкция — Deconstruct

```csharp
// Позволяет: var (x, y) = point;
public readonly record struct Point(int X, int Y) {
    // Автоматически для records
}

// Для обычных классов/структур
public class Person {
    public string FirstName { get; }
    public string LastName { get; }
    public int Age { get; }
    
    public Person(string first, string last, int age) {
        FirstName = first; LastName = last; Age = age;
    }
    
    public void Deconstruct(out string firstName, out string lastName, out int age) {
        firstName = FirstName; lastName = LastName; age = Age;
    }
    
    // Можно несколько Deconstruct с разным числом параметров
    public void Deconstruct(out string fullName, out int age) {
        fullName = $"{FirstName} {LastName}"; age = Age;
    }
}

var person = new Person("Alex", "Smith", 30);
var (first, last, age) = person;
var (fullName, age2) = person;
```

### Collection Expressions (C# 12) — pattern-based для создания

```csharp
// Любой тип с Add или Create/From методом
public class MyList<T> {
    private readonly List<T> _inner = new();
    
    public void Add(T item) => _inner.Add(item);
    public IEnumerator<T> GetEnumerator() => _inner.GetEnumerator();
}

// Использование collection expression
MyList<int> list = [1, 2, 3, 4, 5]; // вызывает Add для каждого
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Extension method не находится | Не в scope (нет using namespace) | Добавьте `using` namespace с extension class |
| `==` без `Equals`/`GetHashCode` | Нарушение контракта | Всегда переопределяйте `Equals` и `GetHashCode` при `==`/`!=` |
| `implicit` с потерей данных | Баги при неявном преобразовании | Используйте `explicit` если есть потеря данных/исключения |
| Индексатор с `params` и обычный | Двусмысленность | Избегайте конфликтов сигнатур |
| `GetAwaiter` не возвращает `INotifyCompletion` | Не работает `await` | Реализуйте `INotifyCompletion` или `ICriticalNotifyCompletion` |
| `Deconstruct` с `out` параметрами не по порядку | Неудобно использовать | Сохраняйте порядок свойств |

## 🛠 Практика

1. Напишите extension methods для `IEnumerable<T>`: `Chunk(int size)`, `Batch(int size)`, `DistinctBy<TKey>(selector)`.
2. Реализуйте структуру `Money` с перегруженными `+`, `-`, `*`, `/`, `==`, `!=`, implicit от `decimal`.
3. Создайте класс `Grid<T>` с индексатором `this[int x, int y]` и `this[Point p]`.
4. Сделайте тип `RetryPolicy`, который можно `await`ить (реализуйте `GetAwaiter`).
5. Реализуйте `Deconstruct` для класса `Order` с вариантами: `(id, customer, total)`, `(id, items, total)`.

## 📌 Кратко

- **Extension methods** — `static` класс, `this Type`, instance methods побеждают
- **Extension properties (C# 12)** — только get, на самом деле методы
- **Operators** — `+ - * / % == != < > <= >= true false & | ^ ~ ++ --`, пары обязательны
- **Conversions** — `implicit` (безопасно), `explicit` (может терять/бросать)
- **Indexers** — `this[params]`, несколько сигнатур, `init` setter
- **Pattern API** — `GetEnumerator` (foreach), `GetAwaiter` (await), `Dispose` (using), `Deconstruct` (деконструкция)

## 🔗 Ссылки

- Extension Methods: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/extension-methods
- Operator Overloading: https://learn.microsoft.com/dotnet/csharp/language-reference/operators/operator-overloading
- Indexers: https://learn.microsoft.com/dotnet/csharp/programming-guide/indexers/
- Pattern-based API: https://learn.microsoft.com/dotnet/csharp/language-reference/proposals/csharp-12.0/collection-expressions
"""

# ============================================================
# LESSON 26: GC, Generations, Finalizers, IDisposable
# ============================================================
lesson_26_md = """## 🎯 Что вы узнаете
- Поколения GC: Gen 0, 1, 2, LOH, POH, эфимерный сегмент
- Режимы GC: Workstation vs Server, Background vs Foreground
- Финализаторы, IDisposable, SafeHandle, CriticalFinalizerObject
- WeakReference, WeakReference<T>, ConditionalWeakTable, GCHandle
- Диагностика: GC.GetTotalMemory, GC.CollectionCount, dotnet-counters, EventPipe

## 🗑 Поколенческий GC — как это работает

### Эфимерный сегмент (Gen 0, 1)

```
┌─────────────────────────────────────────────┐
│              Gen 2 (Large)                  │  ← Долгоживущие, редкий Full GC
├─────────────────────────────────────────────┤
│              Gen 1 (Medium)                 │  ← Выжили после Gen 0
├─────────────────────────────────────────────┤
│              Gen 0 (Small, ~256KB)          │  ← Новые объекты, частый GC
└─────────────────────────────────────────────┘
```

- **Gen 0**: новые объекты, малые, собирается очень часто (миллионы раз в секунду)
- **Gen 1**: буфер между Gen 0 и Gen 2, объекты пережившие 1 сборку Gen 0
- **Gen 2**: долгоживущие объекты, собирается при Full GC (редко)

### Large Object Heap (LOH)

- Объекты **≥ 85,000 байт** (85 KB)
- Массивы: `double[10000]` ≈ 80 KB (не в LOH), `double[11000]` ≈ 88 KB (в LOH)
- **Не компактируется** (до .NET 5) — фрагментация
- .NET 5+: `GCSettings.LargeObjectHeapCompactionMode = GCLargeObjectHeapCompactionMode.CompactOnce`
- Собирается **только при Gen 2 (Full GC)**

### Pinned Object Heap (POH) — .NET 5+

- Объекты, закрепленные через `fixed`, `GCHandle.Alloc(obj, GCHandleType.Pinned)`
- Не двигаются при компактировке
- Отдельная куча, уменьшает фрагментацию основной кучи

### Карта памяти (упрощенно)

```
Small Object Heap (SOH)          Large Object Heap (LOH)
┌─────────────────────┐          ┌─────────────────────┐
│ Gen 0  (256 KB)     │          │   ≥ 85 KB objects   │
│ Gen 1  (2 MB)       │          │   Arrays, strings   │
│ Gen 2  (unlimited)  │          │   No compaction*    │
└─────────────────────┘          └─────────────────────┘
         ↑                                 ↑
    Compaction                        .NET 5+: CompactOnce
```

## ⚙️ Режимы GC

### Workstation GC (default для клиентских)

```xml
<ServerGarbageCollection>false</ServerGarbageCollection>
<ConcurrentGarbageCollection>true</ConcurrentGarbageCollection> <!-- Background GC -->
```
- Один GC поток (или конкурентный фоновый)
- Низкая задержка, подходит для UI приложений

### Server GC (для серверов, высокой нагрузки)

```xml
<ServerGarbageCollection>true</ServerGarbageCollection>
<!-- Background GC по умолчанию включен -->
```
- **Один GC поток на логический процессор**
- Параллельная сборка, выше throughput
- Больше памяти под кучу
- **Рекомендуется для ASP.NET Core, gRPC сервисов**

### Background vs Foreground GC

| Режим | Описание |
|---|---|
| **Background (Concurrent)** | Сборка Gen 0/1 параллельно с выполнением кода (меньше пауз) |
| **Foreground (Blocking)** | Полная остановка всех потоков (Stop-the-world) для Gen 2/LOH |

## ♻️ IDisposable и Finalization — правильный паттерн

### Полный паттерн Dispose

```csharp
public sealed class ResourceHolder : IDisposable {
    private readonly SafeFileHandle _handle; // SafeHandle — правильный wrapper
    private bool _disposed;
    
    public ResourceHolder(string path) {
        _handle = File.OpenHandle(path, FileMode.Open);
    }
    
    public void Dispose() {
        Dispose(true);
        GC.SuppressFinalize(this); // Не вызывать финализатор
    }
    
    // Virtual для наследования
    protected virtual void Dispose(bool disposing) {
        if (_disposed) return;
        
        if (disposing) {
            // Освобождаем MANAGED ресурсы (другие IDisposable)
            _handle?.Dispose();
        }
        
        // Освобождаем UNMANAGED ресурсы (только если НЕ используете SafeHandle)
        // _handle = null; // SafeHandle сам сделает это в своем финализаторе
        
        _disposed = true;
    }
    
    // Финализатор НУЖЕН ТОЛЬКО если есть unmanaged ресурсы БЕЗ SafeHandle
    // ~ResourceHolder() => Dispose(false);
}
```

### SafeHandle — правильный способ для unmanaged

```csharp
// Вместо IntPtr + ручной финализатор
public sealed class MySafeHandle : SafeHandleZeroOrMinusOneIsInvalid {
    private MySafeHandle() : base(true) { } // ownsHandle = true
    
    // Фабричный метод
    public static MySafeHandle Create() {
        var handle = NativeMethods.CreateResource();
        return new MySafeHandle { handle = handle };
    }
    
    protected override bool ReleaseHandle() {
        return NativeMethods.CloseHandle(handle);
    }
}

// Использование
public class Wrapper : IDisposable {
    private readonly MySafeHandle _handle;
    
    public Wrapper() => _handle = MySafeHandle.Create();
    
    public void Dispose() => _handle?.Dispose(); // SafeHandle вызовет ReleaseHandle
    // Финализатор НЕ НУЖЕН! SafeHandle имеет CriticalFinalizerObject
}
```

### CriticalFinalizerObject — гарантированный финализатор

- `SafeHandle`, `CriticalHandle` наследуются от `CriticalFinalizerObject`
- Их финализаторы выполняются **даже при выгрузке AppDomain / быстром завершении процесса**
- Обычные финализаторы могут не выполниться при `Environment.FailFast` или rude AppDomain unload

## 🔗 WeakReference — слабые ссылки

### WeakReference / WeakReference<T>

```csharp
// Слабая ссылка — не препятствует GC
var strong = new BigObject();
var weak = new WeakReference<BigObject>(strong);

strong = null;
GC.Collect();
GC.WaitForPendingFinalizers();

if (weak.TryGetTarget(out var obj)) {
    // объект еще жив
} else {
    // объект собран GC
}
```

### ConditionalWeakTable<TKey, TValue> — таблица с слабыми ключами

```csharp
// Ключ не удерживается сильно, значение удерживается пока жив ключ
var table = new ConditionalWeakTable<object, string>();

var key = new object();
table.Add(key, "associated data");

// key можно использовать как "аттачмент" к любому объекту
// Когда key соберется GC — запись исчезнет автоматически

// Паттерн: расширение чужих классов данными
public static class ObjectExtensions {
    private static readonly ConditionalWeakTable<object, Dictionary<string, object>> _attachments = new();
    
    public static void SetAttachment(this object obj, string key, object value) {
        var dict = _attachments.GetValue(obj, _ => new Dictionary<string, object>());
        dict[key] = value;
    }
    
    public static T GetAttachment<T>(this object obj, string key) {
        if (_attachments.TryGetValue(obj, out var dict) && dict.TryGetValue(key, out var val))
            return (T)val;
        return default;
    }
}
```

### Ephemeron — как это работает внутри

- `ConditionalWeakTable` использует **ephemerons** (эфимероны)
- Ephemeron — это пара (ключ, значение), где значение достижимо ТОЛЬКО если достижим ключ
- GC видит: если ключ мертв → значение тоже мертво (даже если на значение есть ссылки из других мест)

## 📌 GCHandle — pinning и interop

### Типы GCHandle

```csharp
var obj = new byte[1024];

// Normal — обычная сильная ссылка (как объект)
var h1 = GCHandle.Alloc(obj, GCHandleType.Normal);
var target = h1.Target; // object
h1.Free();

// Pinned — закрепляет в памяти, GC не двигает
var h2 = GCHandle.Alloc(obj, GCHandleType.Pinned);
IntPtr ptr = h2.AddrOfPinnedObject(); // указатель для native кода
// NativeWrite(ptr, 1024);
h2.Free(); // ОБЯЗАТЕЛЬНО Free!

// Weak — слабая ссылка
var h3 = GCHandle.Alloc(obj, GCHandleType.Weak);
bool isAlive = h3.IsAllocated; // false если собран
h3.Free();

// WeakTrackResurrection — слабая, отслеживает реанимацию в финализаторе
var h4 = GCHandle.Alloc(obj, GCHandleType.WeakTrackResurrection);
```

### Использование с unmanaged кодом

```csharp
public unsafe void WriteToNative(byte[] buffer) {
    var handle = GCHandle.Alloc(buffer, GCHandleType.Pinned);
    try {
        byte* ptr = (byte*)handle.AddrOfPinnedObject();
        NativeApi.Write(ptr, buffer.Length);
    } finally {
        handle.Free(); // Критично освободить!
    }
}

// Для строк (без копирования)
public unsafe void WriteString(string s) {
    fixed (char* ptr = s) { // string уже pinned в .NET
        NativeApi.WriteUtf16(ptr, s.Length);
    }
}
```

## 📊 Мониторинг и диагностика GC

### Программный доступ

```csharp
// Общая выделенная память
long totalMemory = GC.GetTotalMemory(forceFullCollection: false);

// Количество сборок по поколениям
int gen0 = GC.CollectionCount(0);
int gen1 = GC.CollectionCount(1);
int gen2 = GC.CollectionCount(2);

// Максимальное поколение (обычно 2)
int maxGen = GC.MaxGeneration;

// Уведомление о приближающемся GC
GC.RegisterForFullGCNotification(10, 10); // проценты Gen 2 и LOH
Task.Run(async () => {
    while (true) {
        var status = GC.WaitForFullGCApproach();
        if (status == GCNotificationStatus.Succeeded) {
            // Подготовка к Full GC: сбросить кэши, освободить память
            await PrepareForFullGCAsync();
        }
        await Task.Delay(1000);
    }
});
```

### dotnet-counters (real-time)

```bash
dotnet-counters monitor --process-id <PID> --counters System.Runtime.GC
# Показывает: Gen 0/1/2 GCs, Heap Size, Allocation Rate, LOH Size, Time in GC
```

### EventPipe / dotnet-trace

```bash
dotnet-trace collect --process-id <PID> --providers Microsoft-Windows-DotNETRuntime:4:5
# Детальные события: GCStart, GCEnd, GCAllocationTick, GCHeapSurvivalAndMovement
```

### PerfView — глубокий анализ

- Загрузка `.etl` файла
- GC Stats: паузы, поколения, причины GC
- Heap Dump: кто держит память, GC Roots
- Allocation Stacks: где аллоцируется больше всего

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| `GC.Collect()` в продакшене | Нарушает поколенческую логику, вызывает Full GC | Никогда не вызывайте вручную (кроме тестов) |
| Финализатор без `GC.SuppressFinalize` | Double dispose, лишняя работа GC | Всегда `GC.SuppressFinalize(this)` в `Dispose()` |
| `IDisposable` без `virtual Dispose(bool)` | Наследники не могут расширить cleanup | Делайте `protected virtual void Dispose(bool)` |
| Unmanaged ресурсы без `SafeHandle` | Утечки, сложные финализаторы | Всегда `SafeHandle` / `CriticalHandle` |
| `GCHandle` без `Free()` | Утечка pinned памяти, фрагментация | Всегда `try/finally` с `handle.Free()` |
| Большие массивы в цикле без пула | LOH фрагментация, частые Full GC | `ArrayPool<T>.Shared.Rent/Return` |
| `WeakReference` к value type | Боксинг, не работает как ожидается | Используйте `WeakReference<T>` где T : class |

## 🛠 Практика

1. Реализуйте класс с `SafeHandle` для обертки нативного дескриптора (например, файл/сокет).
2. Создайте кэш на `ConditionalWeakTable` для привязки метаданных к объектам без утечек.
3. Напишите бенчмарк: `new byte[100000]` в цикле vs `ArrayPool<byte>.Shared.Rent`. Сравните Gen 2 GC count.
4. Используйте `dotnet-counters` под нагрузкой. Найдите: Allocation Rate, % Time in GC, Gen 2 GC frequency.
5. Исправьте:
```csharp
class Bad {
    private IntPtr _handle = NativeOpen();
    ~Bad() { NativeClose(_handle); } // Ошибка: нет SafeHandle, нет Dispose
}
```

## 📌 Кратко

- **GC** — поколенческий: Gen 0/1 (эфимерные), Gen 2 (долгоживущие), LOH (≥85KB), POH (pinned)
- **Режимы** — Workstation (клиент) vs Server (сервер, 1 поток на CPU), Background (concurrent)
- **IDisposable** — `Dispose(bool)`, `GC.SuppressFinalize`, `SafeHandle` для unmanaged
- **Finalizer** — только если есть unmanaged БЕЗ SafeHandle; `CriticalFinalizerObject` гарантирует выполнение
- **WeakReference** — не удерживает объект; `ConditionalWeakTable` — ephemerons для аттачментов
- **GCHandle** — `Pinned` для interop, обязательный `Free()`
- **Диагностика** — `GC.GetTotalMemory`, `dotnet-counters`, `dotnet-trace`, PerfView

## 🔗 Ссылки

- GC Fundamentals: https://learn.microsoft.com/dotnet/standard/garbage-collection/fundamentals
- IDisposable: https://learn.microsoft.com/dotnet/standard/garbage-collection/implementing-dispose
- SafeHandle: https://learn.microsoft.com/dotnet/api/system.runtime.interopservices.safehandle
- WeakReference: https://learn.microsoft.com/dotnet/api/system.weakreference-1
- ConditionalWeakTable: https://learn.microsoft.com/dotnet/api/system.runtime.compilerservices.conditionalweaktable-2
- GCHandle: https://learn.microsoft.com/dotnet/api/system.runtime.interopservices.gchandle
"""

# Write lessons 25 and 26
lesson_25_data = {
    "title": "Урок 25: Extension members, операторы, индексаторы, неявные преобразования, pattern-based API",
    "slug": "lesson-25",
    "short_description": "Extension methods/properties, перегрузка операторов, неявные/явные преобразования, индексаторы, pattern-based API (foreach, await, using)",
    "goals": [
        "Писать extension methods и extension properties (C# 12)",
        "Перегружать операторы: +, -, ==, !=, <, >, true, false, implicit, explicit",
        "Создавать индексаторы с параметрами",
        "Реализовывать pattern-based API: GetEnumerator, GetAwaiter, Dispose, Deconstruct",
        "Понимать, как работает foreach, await, using, switch под капотом"
    ],
    "content_md": lesson_25_md,
    "practice_tasks": [
        "Напишите extension methods для `IEnumerable<T>`: `Chunk(int size)`, `Batch(int size)`, `DistinctBy<TKey>(selector)`.",
        "Реализуйте структуру `Money` с перегруженными `+`, `-`, `*`, `/`, `==`, `!=`, implicit от `decimal`.",
        "Создайте класс `Grid<T>` с индексатором `this[int x, int y]` и `this[Point p]`.",
        "Сделайте тип `RetryPolicy`, который можно `await`ить (реализуйте `GetAwaiter`).",
        "Реализуйте `Deconstruct` для класса `Order` с вариантами: `(id, customer, total)`, `(id, items, total)`."
    ],
    "common_errors": [
        {"mistake": "Extension method не находится", "correct": "Добавьте `using` namespace с extension class"},
        {"mistake": "`==` без `Equals`/`GetHashCode`", "correct": "Всегда переопределяйте `Equals` и `GetHashCode` при `==`/`!=`"},
        {"mistake": "`implicit` с потерей данных", "correct": "Используйте `explicit` если есть потеря данных/исключения"},
        {"mistake": "Индексатор с `params` и обычный", "correct": "Избегайте конфликтов сигнатур"},
        {"mistake": "`GetAwaiter` не возвращает `INotifyCompletion`", "correct": "Реализуйте `INotifyCompletion` или `ICriticalNotifyCompletion`"},
        {"mistake": "`Deconstruct` с `out` параметрами не по порядку", "correct": "Сохраняйте порядок свойств"}
    ],
    "resources": [
        "Extension Methods: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/extension-methods",
        "Operator Overloading: https://learn.microsoft.com/dotnet/csharp/language-reference/operators/operator-overloading",
        "Indexers: https://learn.microsoft.com/dotnet/csharp/programming-guide/indexers/",
        "Pattern-based API: https://learn.microsoft.com/dotnet/csharp/language-reference/proposals/csharp-12.0/collection-expressions"
    ],
    "key_takeaways": [
        "Extension methods — static класс, this Type, instance methods побеждают",
        "Extension properties (C# 12) — только get, на самом деле методы",
        "Operators — + - * / % == != < > <= >= true false & | ^ ~ ++ --, пары обязательны",
        "Conversions — implicit (безопасно), explicit (может терять/бросать)",
        "Indexers — this[params], несколько сигнатур, init setter",
        "Pattern API — GetEnumerator (foreach), GetAwaiter (await), Dispose (using), Deconstruct (деконструкция)"
    ],
    "estimated_minutes": 35,
    "language_slug": "csharp",
    "lesson_order": 25,
    "name_en": "Lesson: Extension Members, Operators, Indexers",
    "short_description_en": "Extension methods/properties, operator overloading, conversions, indexers, pattern-based API"
}

lesson_26_data = {
    "title": "Урок 26: GC, поколения, финализаторы, IDisposable, SafeHandle, WeakReference — глубокое погружение",
    "slug": "lesson-26",
    "short_description": "Детальный разбор GC: поколения, LOH, POH, режимы, финализаторы, IDisposable pattern, SafeHandle, WeakReference, ConditionalWeakTable, GCHandle",
    "goals": [
        "Понимать поколенческий GC: Gen 0, 1, 2, LOH, POH, эфимерный сегмент",
        "Различать Workstation vs Server GC, Background vs Foreground",
        "Правильно реализовывать IDisposable и финализаторы с SafeHandle",
        "Работать с WeakReference, WeakReference<T>, ConditionalWeakTable",
        "Использовать GCHandle для pinning и interop"
    ],
    "content_md": lesson_26_md,
    "practice_tasks": [
        "Реализуйте класс с `SafeHandle` для обертки нативного дескриптора (например, файл/сокет).",
        "Создайте кэш на `ConditionalWeakTable` для привязки метаданных к объектам без утечек.",
        "Напишите бенчмарк: `new byte[100000]` в цикле vs `ArrayPool<byte>.Shared.Rent`. Сравните Gen 2 GC count.",
        "Используйте `dotnet-counters` под нагрузкой. Найдите: Allocation Rate, % Time in GC, Gen 2 GC frequency.",
        "Исправьте:\n```csharp\nclass Bad {\n    private IntPtr _handle = NativeOpen();\n    ~Bad() { NativeClose(_handle); } // Ошибка: нет SafeHandle, нет Dispose\n}\n```"
    ],
    "common_errors": [
        {"mistake": "`GC.Collect()` в продакшене", "correct": "Никогда не вызывайте вручную (кроме тестов)"},
        {"mistake": "Финализатор без `GC.SuppressFinalize`", "correct": "Всегда `GC.SuppressFinalize(this)` в `Dispose()`"},
        {"mistake": "`IDisposable` без `virtual Dispose(bool)`", "correct": "Наследники не могут расширить cleanup — делайте `protected virtual void Dispose(bool)`"},
        {"mistake": "Unmanaged ресурсы без `SafeHandle`", "correct": "Всегда `SafeHandle` / `CriticalHandle`"},
        {"mistake": "`GCHandle` без `Free()`", "correct": "Всегда `try/finally` с `handle.Free()`"},
        {"mistake": "Большие массивы в цикле без пула", "correct": "`ArrayPool<T>.Shared.Rent/Return`"},
        {"mistake": "`WeakReference` к value type", "correct": "Используйте `WeakReference<T>` где T : class"}
    ],
    "resources": [
        "GC Fundamentals: https://learn.microsoft.com/dotnet/standard/garbage-collection/fundamentals",
        "IDisposable: https://learn.microsoft.com/dotnet/standard/garbage-collection/implementing-dispose",
        "SafeHandle: https://learn.microsoft.com/dotnet/api/system.runtime.interopservices.safehandle",
        "WeakReference: https://learn.microsoft.com/dotnet/api/system.weakreference-1",
        "ConditionalWeakTable: https://learn.microsoft.com/dotnet/api/system.runtime.compilerservices.conditionalweaktable-2",
        "GCHandle: https://learn.microsoft.com/dotnet/api/system.runtime.interopservices.gchandle"
    ],
    "key_takeaways": [
        "GC — поколенческий: Gen 0/1 (эфимерные), Gen 2 (долгоживущие), LOH (≥85KB), POH (pinned)",
        "Режимы — Workstation (клиент) vs Server (сервер, 1 поток на CPU), Background (concurrent)",
        "IDisposable — Dispose(bool), GC.SuppressFinalize, SafeHandle для unmanaged",
        "Finalizer — только если есть unmanaged БЕЗ SafeHandle; CriticalFinalizerObject гарантирует выполнение",
        "WeakReference — не удерживает объект; ConditionalWeakTable — ephemerons для аттачментов",
        "GCHandle — Pinned для interop, обязательный Free()",
        "Диагностика — GC.GetTotalMemory, dotnet-counters, dotnet-trace, PerfView"
    ],
    "estimated_minutes": 45,
    "language_slug": "csharp",
    "lesson_order": 26,
    "name_en": "Lesson: GC, Generations, Finalizers, IDisposable",
    "short_description_en": "Deep dive into GC generations, LOH, POH, finalizers, IDisposable, SafeHandle, WeakReference"
}

write_lesson(25, lesson_25_data)
write_lesson(26, lesson_26_data)

print("Lessons 25-26 written!")