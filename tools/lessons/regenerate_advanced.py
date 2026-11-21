#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate advanced lessons (23-33) with proper content extraction."""

import json
import re
from pathlib import Path

def extract_code_blocks(text):
    """Extract code blocks from markdown text."""
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
    """Convert markdown to HTML."""
    if not text:
        return ""
    
    # Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Lists
    text = re.sub(r'^\- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\n\1</ul>', text)
    text = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n)+', r'<ol>\n\1</ol>', text)
    
    # Tables
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
    
    # Paragraphs
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
    """Process markdown into content blocks with proper code extraction."""
    # Step 1: Extract code blocks
    text, code_blocks, placeholders = extract_code_blocks(md)
    
    # Step 2: Convert markdown to HTML
    html = markdown_to_html(text)
    
    # Step 3: Restore code block placeholders
    for ph, idx in placeholders.items():
        html = html.replace(ph, f"[[CODE_BLOCK_{idx}]]")
    
    # Step 4: Split into blocks
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
        
        # Extract code markers
        code_markers, remaining = extract_code_markers(part)
        for cb in code_markers:
            blocks.append(cb)
        
        if not remaining:
            continue
        
        # Determine block type
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
# LESSON 23: Advanced Type System
# ============================================================
lesson_23_md = """## 🎯 Что вы узнаете
- Constraints: `class`, `struct`, `new()`, `notnull`, `unmanaged`, `Delegate`, `Enum`, `default`
- Covariance (`out`) и Contravariance (`in`) — когда и как использовать
- Pattern Matching: switch expressions, property patterns, list patterns, slice patterns
- Records: reference и struct, `with`-expressions, positional syntax, equality
- Modern C#: `required`, `init`, `file` types, Generic Math (`INumber<T>`)

## 🔧 Generics Constraints — полный обзор

В C# ограничения (constraints) позволяют сужать множество типов, которые можно подставить вместо параметра типа `T`. Это даёт доступ к членам этих типов внутри generic кода.

### Базовые ограничения

```csharp
// Ссылочный тип (class, interface, delegate, array)
where T : class

// Значимый тип (struct, enum, primitive) — НЕ nullable
where T : struct

// Публичный конструктор без параметров
where T : new()

// Не-nullable тип (reference или value type)
where T : notnull

// Unmanaged тип: примитивы, указатели, enum, struct без ref-полей
where T : unmanaged

// Базовый класс
where T : BaseClass

// Интерфейс
where T : IInterface

// Delegate (C# 7.3+)
where T : Delegate

// Enum (C# 7.3+)
where T : Enum

// Default constraint (C# 12+) — default(T) валиден
where T : default
```

### Комбинирование ограничений

```csharp
// Несколько ограничений
where T : class, IComparable<T>, new()

// Ограничение через другой type parameter
where T : U

// Пример: Repository с ограничениями
public class Repository<T> where T : class, IEntity, new() {
    public T Create() => new T(); // new() позволяет создавать экземпляры
    public int Compare(T x, T y) => x.CompareTo(y); // IComparable<T>
}
```

### Unmanaged constraint — для высокой производительности

Ограничение `unmanaged` гарантирует, что тип не содержит ссылок на управляемые объекты. Это критично для работы с нативной памятью, SIMD и interop.

```csharp
// Только примитивы, указатели, enums, structs без ref-полей
public static T[] AllocateArray<T>(int length) where T : unmanaged
    => new T[length]; // Гарантированно нет GC-ссылок внутри

public static void MemCopy<T>(T* src, T* dst, int count) where T : unmanaged
    => Buffer.MemoryCopy(src, dst, count * sizeof(T), count * sizeof(T));

// Пример: быстрая сериализация структур
public unsafe struct Vec3 { public float X, Y, Z; }
public static byte[] Serialize<T>(T[] data) where T : unmanaged {
    int size = data.Length * sizeof(T);
    var bytes = new byte[size];
    fixed (T* p = data)
        Buffer.MemoryCopy(p, bytes, size, size);
    return bytes;
}
```

### Delegate и Enum constraints

```csharp
// Delegate constraint — для работы с делегатами типобезопасно
public static Delegate CombineDelegates<T>(T first, T second) where T : Delegate
    => Delegate.Combine(first, second);

// Enum constraint — type-safe enum parsing
public static TEnum ParseEnum<TEnum>(string value, bool ignoreCase = false) where TEnum : Enum
    => (TEnum)Enum.Parse(typeof(TEnum), value, ignoreCase);

// Использование
var colors = ParseEnum<ConsoleColor>("Red"); // type-safe!
```

## 🔄 Covariance и Contravariance

Вариантность (variance) определяет, как соотносятся generic типы с разными аргументами типа.

### Covariance (`out`) — «выход» (возврат)

Ковариантность позволяет использовать более конкретный тип там, где ожидается более общий. Работает только для **выходных** позиций (возвращаемые значения, свойства только для чтения).

```csharp
// IEnumerable<out T> — ковариативен
IEnumerable<string> strings = new List<string>();
IEnumerable<object> objects = strings; // OK: string -> object

// Func<out TResult> — ковариативен по результату
Func<string> funcStr = () => "hello";
Func<object> funcObj = funcStr; // OK: возвращает string, ожидается object

// Свой интерфейс с out
public interface IReadOnlyRepository<out T> {
    T GetById(int id);           // OK: T в выходной позиции
    IEnumerable<T> GetAll();     // OK
    // void Add(T item);         // ОШИБКА: T во входной позиции
}
```

### Contravariance (`in`) — «вход» (параметр)

Контравариантность позволяет использовать более общий тип там, где ожидается более конкретный. Работает только для **входных** позиций (параметры методов, свойства только для записи).

```csharp
// IComparer<in T> — контравариативен
IComparer<object> objComparer = (a, b) => 0;
IComparer<string> strComparer = objComparer; // OK: object сравнивает всё, что string

// Action<in T> — контравариативен
Action<object> actObj = o => Console.WriteLine(o);
Action<string> actStr = actObj; // OK: принимает object, а string — это object

// Свой интерфейс с in
public interface IWriteOnlyRepository<in T> {
    void Add(T item);            // OK: T во входной позиции
    // T GetById(int id);        // ОШИБКА: T в выходной позиции
}
```

### Инвариантность — по умолчанию

По умолчанию generic типы инвариантны — нельзя присваивать `List<string>` в `List<object>`.

```csharp
// List<T> — инвариативен (имеет и входящие, и выходящие позиции)
List<string> strings = new();
List<object> objects = strings; // ОШИБКА компиляции!
// Потому что List<T> имеет Add(T) — вход, и T this[int] — выход
```

### Практический пример: Pipeline с вариантностью

```csharp
// Обработчик сообщений — контравариативен по типу сообщения
public interface IMessageHandler<in TMessage> {
    void Handle(TMessage message);
}

// Базовый обработчик для всех сообщений
public class LoggingHandler : IMessageHandler<object> {
    public void Handle(object msg) => Console.WriteLine($"Log: {msg}");
}

// Конкретный обработчик
public class EmailHandler : IMessageHandler<EmailMessage> {
    public void Handle(EmailMessage msg) => SendEmail(msg);
}

// Использование: LoggingHandler (object) можно использовать там, где нужен IMessageHandler<EmailMessage>
IMessageHandler<EmailMessage> handler = new LoggingHandler(); // OK благодаря in
handler.Handle(new EmailMessage()); // LoggingHandler.Handle(object) вызовется
```

## 🎯 Pattern Matching — современный синтаксис

Pattern matching в C# эволюционировал от простого `is` к мощным switch expressions.

### Switch Expressions (C# 8+)

```csharp
// Классический switch expression
string Describe(object obj) => obj switch {
    int i when i > 0 => $"Positive int: {i}",
    int i when i < 0 => $"Negative int: {i}",
    int _ => "Zero",
    string s when s.Length > 10 => $"Long string: {s.Length}",
    string s => $"Short string: {s}",
    null => "Null",
    _ => "Unknown"
};

// Выражение с типом и свойствами
object Process(IEnumerable<int> nums) => nums switch {
    [] => "Empty",
    [var single] => $"Single: {single}",
    [var first, var second, .. var rest] => $"First: {first}, Second: {second}, Rest: {rest.Count()}",
    [.. var all] when all.Count() > 100 => "Too many",
    _ => "Other"
};
```

### Property Patterns (C# 8+)

```csharp
var user = new User { Name = "Alex", Age = 25, Address: new Address { City: "Moscow" } };

// Проверка свойств
bool isAdultInMoscow = user is { Age: >= 18, Address: { City: "Moscow" } };

// В switch expression
string category = user switch {
    { Age: < 18 } => "Minor",
    { Age: >= 65 } => "Senior",
    { Name: "Admin" or "Root" } => "Privileged",
    { Address: { Country: "US" } } => "US User",
    _ => "Regular"
};

// Нested property patterns
var result = user switch {
    { Address: { City: { Length: > 10 } } } => "Long city name",
    { Address: { ZipCode: not null } } => "Has zip",
    _ => "No zip"
};
```

### List Patterns (C# 11+)

```csharp
int[] numbers = { 1, 2, 3, 4, 5 };

var result = numbers switch {
    [] => "Empty",
    [0, ..] => "Starts with zero",
    [.., 0] => "Ends with zero",
    [1, 2, 3, ..] => "Starts with 1,2,3",
    [var first, .. var middle, var last] => $"First: {first}, Last: {last}, Middle: {middle.Length}",
    [_, _, _, _, _] => "Exactly 5 elements",
    [>= 3 elements] => "3 or more",  // C# 12+
    _ => "Other"
};

// Slice patterns (C# 12+)
var slice = numbers[1..4]; // 2, 3, 4
var fromStart = numbers[..3]; // 1, 2, 3
var toEnd = numbers[2..]; // 3, 4, 5

// В pattern matching
var isPrefix = numbers is [1, 2, ..]; // true
```

## 📝 Records — неизменяемые данные

Records — это reference types (или value types) с value-семантикой сравнения и встроенной поддержкой `with`-expressions.

### Reference Record (class-based)

```csharp
public record User(string Name, string Email, int Age) {
    // Автоматически генерируется:
    // - Конструктор с параметрами
    // - Свойства init-only (Name, Email, Age)
    // - Equals/GetHashCode (по всем свойствам)
    // - ToString() с красивым выводом
    // - Deconstruct(out Name, out Email, out Age)
    // - Клонирование через with-expression
}

// Использование
var user1 = new User("Alex", "alex@test.com", 25);
var user2 = user1 with { Age = 26 }; // Копия с изменённым Age
// user1 == user2 -> false (разный Age)

// Positional records — деконструкция
public record Point(int X, int Y);
var p = new Point(10, 20);
var (x, y) = p; // x=10, y=20
Console.WriteLine(p); // Point { X = 10, Y = 20 }
```

### Record Struct (C# 10+) — value type record

```csharp
public readonly record struct Point3D(int X, int Y, int Z);

// Сравнение по значениям, без аллокаций на куче
var p1 = new Point3D(1, 2, 3);
var p2 = p1 with { Z = 4 }; // with-expression работает!
// p1.Equals(p2) -> false
```

### Records с методами и наследованием

```csharp
public abstract record Animal(string Name) {
    public virtual string Sound() => "...";
}

public record Dog(string Name, string Breed) : Animal(Name) {
    public override string Sound() => "Woof!";
    public void Fetch() => Console.WriteLine("Fetching!");
}

// Equality в Records — можно настроить
public record User(string Name, string Email) {
    // Сравнение только по Email
    protected virtual bool PrintMembers(StringBuilder builder) {
        builder.Append($"Email = {Email}");
        return true;
    }
}
```

## ⭐ Modern C# Features (C# 11-12)

### Required Properties (C# 11)

```csharp
public class User {
    public required string Name { get; init; }
    public required string Email { get; init; }
    public int Age { get; init; } // не required
}

// Использование — ОБЯЗАТЕЛЬНО передать required
var user = new User { Name = "Alex", Email = "a@b.com" }; // OK
// var bad = new User { Name = "Alex" }; // ОШИБКА компиляции: Email required
```

### Init-only Properties (C# 9)

```csharp
public class Config {
    public string ConnectionString { get; init; } // только в инициализаторе
    public int Timeout { get; init; }
}

var cfg = new Config { ConnectionString = "..." };
// cfg.ConnectionString = "new"; // ОШИБКА: нет set
```

### File-scoped Types (C# 11)

```csharp
// Видимы ТОЛЬКО в этом файле
file class InternalHelper { }
file struct InternalData { }
file interface IInternalService { }

// В другом файле — недоступны, не загрязняют namespace
```

### Generic Math — INumber<T> (C# 11, .NET 7+)

```csharp
// Математика для ЛЮБОГО числового типа
public static T Sum<T>(T a, T b) where T : INumber<T>
    => a + b;

public static T Average<T>(IEnumerable<T> values) where T : INumber<T> {
    T sum = T.Zero;
    int count = 0;
    foreach (var v in values) { sum += v; count++; }
    return count > 0 ? sum / T.CreateChecked(count) : T.Zero;
}

// Использование
int i = Sum(1, 2);        // 3
double d = Sum(1.5, 2.5); // 4.0
decimal m = Sum(1.1m, 2.2m); // 3.3
```

### Primary Constructors (C# 12) — для class/struct

```csharp
// Параметры конструктора становятся полями
public class User(string name, string email) {
    public string Name { get; } = name;
    public string Email { get; } = email;
    
    public void Print() => Console.WriteLine($"{Name} <{Email}>");
}

// Для record — уже было, теперь и для class/struct
public readonly struct Point(int X, int Y) {
    public int X { get; } = X;
    public int Y { get; } = Y;
}
```

### Collection Expressions (C# 12)

```csharp
// Единый синтаксис для всех коллекций
int[] arr = [1, 2, 3];
List<int> list = [1, 2, 3];
Span<int> span = [1, 2, 3];
ImmutableArray<int> imm = [1, 2, 3];

// Spread
int[] combined = [..arr, 4, 5, ..list];
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| `where T : class` для struct | struct не удовлетворяет | Используйте `where T : struct` или `where T : notnull` |
| Covariance на классе | Только интерфейсы/делегаты | Выносите в интерфейс с `out` |
| `with` на обычном классе | Только для records | Сделайте `record` или напишите метод копирования |
| `required` без инициализации | Ошибка компиляции | Всегда инициализируйте в object initializer |
| Pattern matching не покрывает все случаи | Предупреждение CS8509 | Добавьте `_ => ...` или используйте `switch` на sealed типах |
| `INumber<T>` на старых .NET | Требует .NET 7+ | Проверьте TFM: `<TargetFramework>net7.0</TargetFramework>` |

## 🛠 Практика

1. Напишите generic метод `Swap<T>(ref T a, ref T b) where T : unmanaged` используя `Unsafe.Swap`.
2. Создайте ковариантный интерфейс `IReadOnlyRepository<out T>` и контравариантный `IWriter<in T>`.
3. Реализуйте `Describe(object)` через switch expression с property patterns, list patterns, type patterns.
4. Сделайте `record User` с `required` полями, `with`-expression, деконструкцией.
5. Напишите generic `Clamp<T>(T value, T min, T max)` используя `IComparable<T>` и `INumber<T>`.

## 📌 Кратко

- **Constraints** — `class`, `struct`, `new()`, `notnull`, `unmanaged`, `Delegate`, `Enum`, `default`
- **Covariance (`out`)** — возвращаемые позиции: `IEnumerable<out T>`, `Func<out T>`
- **Contravariance (`in`)** — входные позиции: `IComparer<in T>`, `Action<in T>`
- **Pattern Matching** — switch expressions, property patterns, list patterns, slice patterns
- **Records** — неизменяемые, value equality, `with`-expressions, positional syntax, record struct
- **Modern** — `required`, `init`, `file` types, Generic Math (`INumber<T>`), primary constructors, collection expressions

## 🔗 Ссылки

- Generics Constraints: https://learn.microsoft.com/dotnet/csharp/programming-guide/generics/constraints-on-type-parameters
- Covariance/Contravariance: https://learn.microsoft.com/dotnet/csharp/programming-guide/concepts/covariance-contravariance/
- Pattern Matching: https://learn.microsoft.com/dotnet/csharp/pattern-matching
- Records: https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/record
- Generic Math: https://learn.microsoft.com/dotnet/api/system.numerics.inumber-1
"""

# ============================================================
# LESSON 24: Language/Runtime Internals
# ============================================================
lesson_24_md = """## 🎯 Что вы узнаете
- IL (Intermediate Language): инструкции, стек, locals, branches
- Атрибуты: `[AttributeUsage]`, чтение через рефлексию, `CallerArgumentExpression`
- Source Generators: `ISourceGenerator`, `IncrementalGenerator`, генерация кода при компиляции
- Reflection: `Type`, `MethodInfo`, `PropertyInfo`, `Activator`, `MethodBase.GetCurrentMethod`
- Expression Trees: `Expression<TDelegate>`, компиляция в делегаты, visitor pattern
- DynamicMethod / ILGenerator: ручная генерация IL в runtime

## 📜 IL — Intermediate Language

### Пример C# и соответствующий IL

```csharp
public int Add(int a, int b) => a + b;
```

```il
.method public hidebysig instance int32 Add(int32 a, int32 b) cil managed
{
    .maxstack 2
    .locals init ([0] int32 V_0)
    
    IL_0000: ldarg.1      // загружает аргумент 1 (a)
    IL_0001: ldarg.2      // загружает аргумент 2 (b)
    IL_0002: add          // складывает два верхних значения стека
    IL_0003: stloc.0      // сохраняет в локальную переменную 0
    IL_0004: br.s IL_0006
    IL_0006: ldloc.0      // загружает локальную 0
    IL_0007: ret          // возвращает
}
```

### Основные IL инструкции

| Категория | Инструкции |
|---|---|
| **Стек** | `ldarg.0-3`, `ldarg.s`, `ldloc.0-3`, `ldloc.s`, `starg.s`, `stloc.s`, `dup`, `pop` |
| **Константы** | `ldc.i4.0-8`, `ldc.i4.s`, `ldc.i4`, `ldc.i8`, `ldc.r4`, `ldc.r8`, `ldstr` |
| **Арифметика** | `add`, `sub`, `mul`, `div`, `rem`, `neg`, `add.ovf` (с проверкой overflow) |
| **Логика** | `and`, `or`, `xor`, `not`, `shl`, `shr`, `ceq`, `cgt`, `clt`, `cgt.un` |
| **Ветвления** | `br`, `br.s`, `brtrue`, `brfalse`, `beq`, `bne`, `bgt`, `blt`, `ble`, `bge` |
| **Вызов** | `call`, `callvirt`, `newobj`, `ldftn`, `ldvirtftn` |
| **Возврат** | `ret` |
| **Исключения** | `throw`, `rethrow`, `leave`, `endfinally` |

### Просмотр IL

```bash
# dotnet-ildasm (установка: dotnet tool install -g ildasm)
ildasm MyAssembly.dll /out=MyAssembly.il

# Или онлайн: sharplab.io
```

## 🏷 Атрибуты — метаданные для кода

### Создание атрибута

```csharp
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method, AllowMultiple = true, Inherited = true)]
public class ValidateAttribute : Attribute {
    public string Rule { get; }
    public int MinLength { get; set; }
    
    public ValidateAttribute(string rule) => Rule = rule;
}

// Использование
[Validate("Email", MinLength = 5)]
[Validate("Required")]
public class User {
    [Validate("NotEmpty")]
    public string Name { get; set; }
}
```

### Чтение через рефлексию

```csharp
var type = typeof(User);

// Атрибуты класса
var classAttrs = type.GetCustomAttributes<ValidateAttribute>(inherit: true);
foreach (var attr in classAttrs)
    Console.WriteLine($"Class: {attr.Rule}, MinLength: {attr.MinLength}");

// Атрибуты свойств
var prop = type.GetProperty("Name");
var propAttrs = prop.GetCustomAttributes<ValidateAttribute>(false);
```

### Caller Attributes — автоматическая подстановка

```csharp
public void Log(string message,
    [CallerMemberName] string member = "",
    [CallerFilePath] string file = "",
    [CallerLineNumber] int line = 0,
    [CallerArgumentExpression("message")] string expr = "") {
    
    Console.WriteLine($"{file}:{line} [{member}] {expr} = {message}");
}

// Вызов
Log("User created"); 
// Program.cs:10 [Main] "User created" = User created
```

## ⚙️ Source Generators — генерация кода при компиляции

### Простой генератор (ISourceGenerator)

```csharp
[Generator]
public class AutoToStringGenerator : ISourceGenerator {
    public void Initialize(GeneratorInitializationContext context) {
        context.RegisterForSyntaxNotifications(() => new ClassSyntaxReceiver());
    }

    public void Execute(GeneratorExecutionContext context) {
        if (context.SyntaxContextReceiver is not ClassSyntaxReceiver receiver) return;
        
        foreach (var classDecl in receiver.Classes) {
            var className = classDecl.Identifier.Text;
            var properties = classDecl.Members
                .OfType<PropertyDeclarationSyntax>()
                .Select(p => p.Identifier.Text);
            
            var source = $@"
// <auto-generated/>
namespace {classDecl.GetNamespace()} {{
    partial class {className} {{
        public override string ToString() => 
            $\"{{GetType().Name}}: {{{string.Join(", ", properties.Select(p => $"{p} = {{{p}}}"))}}}\";
    }}
}}";
            
            context.AddSource($"{className}.ToString.g.cs", SourceText.From(source, Encoding.UTF8));
        }
    }
}

class ClassSyntaxReceiver : ISyntaxContextReceiver {
    public List<ClassDeclarationSyntax> Classes { get; } = new();
    
    public void OnVisitSyntaxNode(GeneratorSyntaxContext context) {
        if (context.Node is ClassDeclarationSyntax c && c.AttributeLists.Count > 0)
            Classes.Add(c);
    }
}
```

### Incremental Generator (современный, быстрый)

```csharp
[Generator(LanguageNames.CSharp)]
public class IncrementalGenerator : IIncrementalGenerator {
    public void Initialize(IncrementalGeneratorInitializationContext context) {
        var classes = context.SyntaxProvider
            .CreateSyntaxProvider(
                predicate: (node, _) => node is ClassDeclarationSyntax { AttributeLists.Count: > 0 },
                transform: (ctx, _) => (ClassDeclarationSyntax)ctx.Node)
            .Where(c => c.AttributeLists.Any(a => a.Attributes.Any(attr => attr.Name.ToString() == "GenerateToString")))
            .Collect();

        context.RegisterSourceOutput(classes, (ctx, classList) => {
            foreach (var classDecl in classList) {
                // генерация как выше
                ctx.AddSource($"{classDecl.Identifier}.ToString.g.cs", sourceText);
            }
        });
    }
}
```

### Использование в проекте

```xml
<!-- Генератор как отдельный проект -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.0</TargetFramework>
    <EnforceExtendedAnalyzerRules>true</EnforceExtendedAnalyzerRules>
    <IsRoslynComponent>true</IsRoslynComponent>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.CodeAnalysis.CSharp" Version="4.8.0" PrivateAssets="all" />
    <PackageReference Include="Microsoft.CodeAnalysis.Analyzers" Version="3.3.4" PrivateAssets="all" />
  </ItemGroup>
</Project>

<!-- В проекте-потребителе -->
<ProjectReference Include="..\MyGenerator\MyGenerator.csproj" 
                  OutputItemType="Analyzer" ReferenceOutputAssembly="false" />
```

### Применение

```csharp
// В коде пользователя
[GenerateToString]
public partial class User {
    public string Name { get; set; }
    public int Age { get; set; }
}

// Генератор создаст partial class с ToString()
// User.g.cs:
// partial class User { public override string ToString() => $"User: Name = {Name}, Age = {Age}"; }
```

## 🔍 Reflection — инспекция типов в runtime

### Основные операции

```csharp
Type t = typeof(User);
// или
Type t = user.GetType();

// Создание экземпляра
var user = (User)Activator.CreateInstance(typeof(User), "Alex", "a@b.com")!;
var user2 = Activator.CreateInstance<User>(); // нужен parameterless ctor

// Методы
var method = t.GetMethod("GetFullName", BindingFlags.Instance | BindingFlags.Public);
var result = method.Invoke(user, null);

// Свойства
var prop = t.GetProperty("Name");
prop.SetValue(user, "New Name");
var name = (string)prop.GetValue(user);

// Поля (включая private)
var field = t.GetField("_id", BindingFlags.Instance | BindingFlags.NonPublic);
field.SetValue(user, 42);

// Generic методы
var genericMethod = t.GetMethod("DoSomething").MakeGenericMethod(typeof(int));
genericMethod.Invoke(user, null);
```

### Performance: кэширование рефлексии

```csharp
// Медленно: typeof(T).GetProperty("Name") каждый раз
// Быстро: кэшируйте PropertyInfo в static readonly
private static readonly PropertyInfo NameProperty = typeof(User).GetProperty("Name")!;

public string GetNameFast(User u) => (string)NameProperty.GetValue(u)!;

// Для максимальной скорости — скомпилируйте в делегат
private static readonly Func<User, string> GetNameDelegate = 
    (Func<User, string>)Delegate.CreateDelegate(typeof(Func<User, string>), NameProperty.GetGetMethod()!);

public string GetNameFastest(User u) => GetNameDelegate(u);
```

## 🌳 Expression Trees — деревья выражений

### Создание и компиляция

```csharp
using System.Linq.Expressions;

// x => x.Age > 18
ParameterExpression param = Expression.Parameter(typeof(User), "x");
MemberExpression ageProp = Expression.Property(param, "Age");
ConstantExpression eighteen = Expression.Constant(18);
BinaryExpression greater = Expression.GreaterThan(ageProp, eighteen);

Expression<Func<User, bool>> lambda = Expression.Lambda<Func<User, bool>>(greater, param);
Func<User, bool> compiled = lambda.Compile();

var result = compiled(new User { Age = 20 }); // true
```

### Динамическое построение запросов

```csharp
public static IQueryable<T> ApplyFilters<T>(IQueryable<T> query, Dictionary<string, object> filters) {
    var param = Expression.Parameter(typeof(T), "x");
    Expression body = Expression.Constant(true);
    
    foreach (var (propName, value) in filters) {
        var prop = Expression.Property(param, propName);
        var constVal = Expression.Constant(value);
        var equal = Expression.Equal(prop, constVal);
        body = Expression.AndAlso(body, equal);
    }
    
    var lambda = Expression.Lambda<Func<T, bool>>(body, param);
    return query.Where(lambda);
}
```

### Expression Visitor — трансформация деревьев

```csharp
public class ParameterReplacer : ExpressionVisitor {
    private readonly ParameterExpression _oldParam;
    private readonly ParameterExpression _newParam;
    
    public ParameterReplacer(ParameterExpression oldParam, ParameterExpression newParam) {
        _oldParam = oldParam; _newParam = newParam;
    }
    
    protected override Expression VisitParameter(ParameterExpression node)
        => node == _oldParam ? _newParam : base.VisitParameter(node);
}

// Замена параметра в лямбде
var newParam = Expression.Parameter(typeof(User), "y");
var visitor = new ParameterReplacer(lambda.Parameters[0], newParam);
var newLambda = visitor.Visit(lambda);
```

## ⚡ DynamicMethod и ILGenerator — ручная генерация IL

### Быстрый доступ к свойству

```csharp
using System.Reflection.Emit;

public static Func<T, TProp> CreateFastGetter<T, TProp>(string propertyName) {
    var prop = typeof(T).GetProperty(propertyName)!;
    var getMethod = prop.GetGetMethod(true)!;
    
    var dm = new DynamicMethod(
        $"get_{propertyName}", 
        typeof(TProp), 
        new[] { typeof(T) }, 
        typeof(T), 
        skipVisibility: true);
    
    var il = dm.GetILGenerator();
    il.Emit(OpCodes.Ldarg_0);           // загружаем this
    il.Emit(OpCodes.Callvirt, getMethod); // вызываем getter
    il.Emit(OpCodes.Ret);               // возвращаем
    
    return (Func<T, TProp>)dm.CreateDelegate(typeof(Func<T, TProp>));
}

// Использование
var getName = CreateFastGetter<User, string>("Name");
var name = getName(user); // максимально быстро, без рефлексии
```

### Генерация всего метода

```csharp
public static Func<int, int, int> CreateAdder() {
    var dm = new DynamicMethod("Add", typeof(int), new[] { typeof(int), typeof(int) });
    var il = dm.GetILGenerator();
    
    il.Emit(OpCodes.Ldarg_0);
    il.Emit(OpCodes.Ldarg_1);
    il.Emit(OpCodes.Add);
    il.Emit(OpCodes.Ret);
    
    return (Func<int, int, int>)dm.CreateDelegate(typeof(Func<int, int, int>));
}
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Рефлексия в горячем пути | Медленно, аллокации | Кэшируйте MemberInfo, компилируйте в делегаты, используйте Source Generators |
| Source Generator не срабатывает | Не зарегистрирован / неправильный predicate | Проверьте `.csproj`: `OutputItemType="Analyzer" ReferenceOutputAssembly="false"` |
| `Expression.Compile()` каждый раз | Медленно | Кэшируйте скомпилированные делегаты |
| `DynamicMethod` без `skipVisibility: true` | Не видит private члены | Добавьте `skipVisibility: true` в конструктор |
| ILGenerator — неверный стек | InvalidProgramException при вызове | Проверяйте баланс стека: каждый `ldarg`/`ldloc` = `stloc`/`ret`/аргумент call |

## 🛠 Практика

1. Напишите консольную утилиту, которая через `ildasm` или `Mono.Cecil` выводит IL для заданного метода.
2. Создайте атрибут `[Cacheable]` и Source Generator, генерирующий обертку с кэшированием для помеченных методов.
3. Реализуйте `FastActivator.Create<T>()` через `DynamicMethod` — быстрее `Activator.CreateInstance`.
4. Постройте Expression Tree для динамического `OrderBy` по имени свойства строкой.
5. Напишите `ExpressionVisitor`, который заменяет все вызовы `DateTime.Now` на `DateTime.UtcNow`.

## 📌 Кратко

- **IL** — стековая байт-код, инструкции: ldarg, ldloc, call, br, ret. Смотрите через `ildasm` / sharplab.io
- **Attributes** — метаданные, `[AttributeUsage]`, чтение через `GetCustomAttributes`, `Caller*` атрибуты
- **Source Generators** — `IIncrementalGenerator`, генерация `.g.cs` при компиляции, работает в NativeAOT
- **Reflection** — `Type`, `MethodInfo`, `PropertyInfo`, `Activator`. Кэшируйте! Компилируйте в делегаты!
- **Expression Trees** — `Expression<TDelegate>`, `.Compile()`, Visitor pattern для трансформации
- **DynamicMethod/ILGenerator** — ручная IL генерация в runtime, максимальная скорость, `skipVisibility: true`

## 🔗 Ссылки

- IL Reference: https://learn.microsoft.com/dotnet/api/system.reflection.emit.opcodes
- Source Generators: https://learn.microsoft.com/dotnet/csharp/roslyn-sdk/source-generators-overview
- Expression Trees: https://learn.microsoft.com/dotnet/csharp/expression-trees
- DynamicMethod: https://learn.microsoft.com/dotnet/api/system.reflection.emit.dynamicmethod
- Reflection Performance: https://learn.microsoft.com/dotnet/framework/reflection-and-codedom/reflection-performance
"""

# ... continue with other lessons ...

# Write lesson 23
lesson_23_data = {
    "title": "Урок 23: Продвинутая система типов — Generics constraints, Covariance/Contravariance, Pattern Matching, Records",
    "slug": "lesson-23",
    "short_description": "Ограничения дженериков, ковариантность/контравариантность, pattern matching, records, required, init, файл-скопе",
    "goals": [
        "Мастерски использовать constraints: where T : class, struct, new(), notnull, unmanaged, Delegate, Enum",
        "Понимать covariance (out) и contravariance (in) для интерфейсов и делегатов",
        "Писать сложные pattern matching: switch expressions, property patterns, list patterns",
        "Работать с records: with-expressions, positional records, record structs",
        "Использовать required, init, file-scoped types, generic math"
    ],
    "content_md": lesson_23_md,
    "practice_tasks": [
        "Напишите generic метод `Swap<T>(ref T a, ref T b) where T : unmanaged` используя `Unsafe.Swap`.",
        "Создайте ковариантный интерфейс `IReadOnlyRepository<out T>` и контравариантный `IWriter<in T>`.",
        "Реализуйте `Describe(object)` через switch expression с property patterns, list patterns, type patterns.",
        "Сделайте `record User` с `required` полями, `with`-expression, деконструкцией.",
        "Напишите generic `Clamp<T>(T value, T min, T max)` используя `IComparable<T>` и `INumber<T>`."
    ],
    "common_errors": [
        {"mistake": "`where T : class` для struct", "correct": "Используйте `where T : struct` или `where T : notnull`"},
        {"mistake": "Covariance на классе", "correct": "Только интерфейсы/делегаты — выносите в интерфейс с `out`"},
        {"mistake": "`with` на обычном классе", "correct": "Только для records — сделайте `record` или напишите метод копирования"},
        {"mistake": "`required` без инициализации", "correct": "Всегда инициализируйте в object initializer"},
        {"mistake": "Pattern matching не покрывает все случаи", "correct": "Добавьте `_ => ...` или используйте `switch` на sealed типах"},
        {"mistake": "`INumber<T>` на старых .NET", "correct": "Требует .NET 7+, проверьте TargetFramework"}
    ],
    "resources": [
        "Generics Constraints: https://learn.microsoft.com/dotnet/csharp/programming-guide/generics/constraints-on-type-parameters",
        "Covariance/Contravariance: https://learn.microsoft.com/dotnet/csharp/programming-guide/concepts/covariance-contravariance/",
        "Pattern Matching: https://learn.microsoft.com/dotnet/csharp/pattern-matching",
        "Records: https://learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/record",
        "Generic Math: https://learn.microsoft.com/dotnet/api/system.numerics.inumber-1"
    ],
    "key_takeaways": [
        "Constraints — class, struct, new(), notnull, unmanaged, Delegate, Enum, default",
        "Covariance (out) — возвращаемые позиции: IEnumerable<out T>, Func<out T>",
        "Contravariance (in) — входные позиции: IComparer<in T>, Action<in T>",
        "Pattern Matching — switch expressions, property patterns, list patterns, slice patterns",
        "Records — неизменяемые, value equality, with-expressions, positional syntax, record struct",
        "Modern — required, init, file types, Generic Math (INumber<T>), primary constructors, collection expressions"
    ],
    "estimated_minutes": 40,
    "language_slug": "csharp",
    "lesson_order": 23,
    "name_en": "Lesson: Advanced Type System",
    "short_description_en": "Generics constraints, covariance/contravariance, pattern matching, records, required, init, Generic Math"
}

lesson_24_data = {
    "title": "Урок 24: Внутренности языка и рантайма — IL, Attributes, Source Generators, Reflection, Expression Trees",
    "slug": "lesson-24",
    "short_description": "IL код, атрибуты, Source Generators, рефлексия, Expression Trees, DynamicMethod, компиляция в runtime",
    "goals": [
        "Читать и понимать IL инструкции",
        "Создавать кастомные атрибуты и читать их через рефлексию",
        "Писать Source Generators для генерации кода на этапе компиляции",
        "Работать с Expression Trees для динамического кода",
        "Использовать DynamicMethod и ILGenerator для высокой производительности"
    ],
    "content_md": lesson_24_md,
    "practice_tasks": [
        "Напишите консольную утилиту, которая через `ildasm` или `Mono.Cecil` выводит IL для заданного метода.",
        "Создайте атрибут `[Cacheable]` и Source Generator, генерирующий обертку с кэшированием для помеченных методов.",
        "Реализуйте `FastActivator.Create<T>()` через `DynamicMethod` — быстрее `Activator.CreateInstance`.",
        "Постройте Expression Tree для динамического `OrderBy` по имени свойства строкой.",
        "Напишите `ExpressionVisitor`, который заменяет все вызовы `DateTime.Now` на `DateTime.UtcNow`."
    ],
    "common_errors": [
        {"mistake": "Рефлексия в горячем пути", "correct": "Кэшируйте MemberInfo, компилируйте в делегаты, используйте Source Generators"},
        {"mistake": "Source Generator не срабатывает", "correct": "Проверьте .csproj: OutputItemType=\"Analyzer\" ReferenceOutputAssembly=\"false\""},
        {"mistake": "`Expression.Compile()` каждый раз", "correct": "Кэшируйте скомпилированные делегаты"},
        {"mistake": "`DynamicMethod` без `skipVisibility: true`", "correct": "Добавьте `skipVisibility: true` в конструктор"},
        {"mistake": "ILGenerator — неверный стек", "correct": "Проверяйте баланс стека: каждый ldarg/ldloc = stloc/ret/аргумент call"}
    ],
    "resources": [
        "IL Reference: https://learn.microsoft.com/dotnet/api/system.reflection.emit.opcodes",
        "Source Generators: https://learn.microsoft.com/dotnet/csharp/roslyn-sdk/source-generators-overview",
        "Expression Trees: https://learn.microsoft.com/dotnet/csharp/expression-trees",
        "DynamicMethod: https://learn.microsoft.com/dotnet/api/system.reflection.emit.dynamicmethod",
        "Reflection Performance: https://learn.microsoft.com/dotnet/framework/reflection-and-codedom/reflection-performance"
    ],
    "key_takeaways": [
        "IL — стековая байт-код, инструкции: ldarg, ldloc, call, br, ret. Смотрите через ildasm / sharplab.io",
        "Attributes — метаданные, [AttributeUsage], чтение через GetCustomAttributes, Caller* атрибуты",
        "Source Generators — IIncrementalGenerator, генерация .g.cs при компиляции, работает в NativeAOT",
        "Reflection — Type, MethodInfo, PropertyInfo, Activator. Кэшируйте! Компилируйте в делегаты!",
        "Expression Trees — Expression<TDelegate>, .Compile(), Visitor pattern для трансформации",
        "DynamicMethod/ILGenerator — ручная IL генерация в runtime, максимальная скорость, skipVisibility: true"
    ],
    "estimated_minutes": 45,
    "language_slug": "csharp",
    "lesson_order": 24,
    "name_en": "Lesson: Language/Runtime Internals",
    "short_description_en": "IL, Attributes, Source Generators, Reflection, Expression Trees, DynamicMethod"
}

# Write lessons
write_lesson(23, lesson_23_data)
write_lesson(24, lesson_24_data)

print("Lessons 23-24 written!")