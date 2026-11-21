#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate lessons 14-33 with full Russian educational content."""

import json
import re
from pathlib import Path

# ---------- Markdown -> HTML + code extraction ----------
def markdown_to_blocks(text: str):
    """Convert markdown text to list of blocks (heading/text/code/table/list)."""
    if not text:
        return []
    
    # First, extract code blocks
    code_blocks = []
    placeholder_map = {}
    
    def protect_code(match):
        idx = len(code_blocks)
        lang = match.group(1) or 'csharp'
        code = match.group(2).rstrip()
        code_blocks.append({'type': 'code', 'language': lang, 'content': code})
        placeholder = f"{{{{CODE_BLOCK_{idx}}}}}"
        placeholder_map[placeholder] = idx
        return placeholder
    
    text = re.sub(r'```(\w*)\n(.*?)\n```', protect_code, text, flags=re.DOTALL)
    
    # Process markdown
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
    
    # Tables (simple)
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
    
    # Now split into blocks by HTML tags
    blocks = []
    for ph, idx in placeholder_map.items():
        text = text.replace(ph, f"[[CODE_BLOCK_{idx}]]")
    
    # Split by block tags
    parts = re.split(r'(<h[1-6]>.*?</h[1-6]>|<ul>.*?</ul>|<ol>.*?</ol>|<table>.*?</table>|<p>.*?</p>)', text, flags=re.DOTALL)
    
    def extract_code_markers(part):
        """Recursively extract code block markers from a part."""
        extracted = []
        remaining = part
        
        # Check for standalone markers
        while True:
            m = re.search(r'\[\[CODE_BLOCK_(\d+)\]\]', remaining)
            if not m:
                break
            idx = int(m.group(1))
            extracted.append(code_blocks[idx])
            # Remove this marker
            remaining = remaining[:m.start()] + remaining[m.end():]
        
        return extracted, remaining.strip()
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Extract any code markers from this part (including nested)
        code_markers, remaining = extract_code_markers(part)
        for cb in code_markers:
            blocks.append(cb)
        
        if not remaining:
            continue
        
        # Determine block type from remaining content
        if remaining.startswith('<h'):
            level = int(remaining[2])
            content = re.sub(r'<h\d>(.*?)</h\d>', r'\1', remaining, flags=re.DOTALL)
            blocks.append({'type': 'heading', 'level': level, 'content': content.strip()})
        elif remaining.startswith('<ul>') or remaining.startswith('<ol>'):
            items = re.findall(r'<li>(.*?)</li>', remaining, flags=re.DOTALL)
            blocks.append({'type': 'list', 'items': [i.strip() for i in items], 'ordered': remaining.startswith('<ol>')})
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
            content = content.strip()
            if content:
                blocks.append({'type': 'text', 'content': content})
        elif remaining:
            # Any other remaining content as text
            blocks.append({'type': 'text', 'content': remaining})
    
    return blocks


def write_lesson(num, data):
    path = f'fixtures/lessons/csharp/{num:02d}.json'
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Written lesson {num:02d}: {data["title"][:60]}...')


# ============================================================
# LESSON CONTENT DEFINITIONS (raw markdown)
# ============================================================

LESSONS = {}

# ----- 14: Delegates & Events -----
LESSONS[14] = {
    "title": "Урок 14: Делегаты и события — инверсия управления",
    "slug": "lesson-14",
    "short_description": "Делегаты, multicast, события, event pattern, EventHandler, слабые события, async события, pattern matching с делегатами",
    "goals": [
        "Понимать, что такое делегат и как он отличается от интерфейса",
        "Работать с multicast делегатами и цепочками вызовов",
        "Правильно объявлять и поднимать события (event pattern)",
        "Работать с EventHandler<TEventArgs> и кастомными EventArgs",
        "Понимать проблему утечек памяти и слабые события",
        "Работать с async событиями и pattern matching для делегатов"
    ],
    "content_md": """## 🎯 Что вы узнаете
- Что такое делегат: типобезопасный указатель на метод
- Multicast делегаты: комбинирование нескольких методов
- События (event): инкапсуляция делегатов, паттерн publisher/subscriber
- EventHandler<TEventArgs>: стандартный паттерн событий
- Слабые события (WeakEventManager): предотвращение утечек памяти
- Async события: асинхронные обработчики, Task-based подход

## 💡 Зачем нужны делегаты: инверсия управления

Представьте: вы пишете сортировку. Алгоритм один, но критерий сравнения разный — по возрастанию, убыванию, по длине строки, по дате. Без делегатов пришлось бы писать отдельный метод для каждого случая или использовать if/else.

С делегатом:

```csharp
// Делегат — тип, описывающий сигнатуру метода
public delegate int Comparison<T>(T x, T y);

// Сортировка принимает делегат как параметр
public static void Sort<T>(T[] array, Comparison<T> comparison) { }

// Использование: передаем ЛЮБОЙ подходящий метод
Sort(numbers, (a, b) => a - b);           // по возрастанию
Sort(numbers, (a, b) => b - a);           // по убыванию
Sort(words, (a, b) => a.Length - b.Length); // по длине
```

**Делегат** — это тип, который представляет ссылку на метод с определенной сигнатурой. Это **инверсия управления**: алгоритм не знает, *как* сравнивать, он *делегирует* это решение вызывающему коду.

### 🎯 Делегаты vs Интерфейсы: когда что использовать

| Аспект | Делегат | Интерфейс |
|---|---|---|
| Назначение | Один метод (действие) | Контракт (несколько методов/свойств) |
| Состояние | Нет (stateless) | Может иметь состояние |
| Множественность | Multicast (список методов) | Одна реализация на класс |
| Использование | Callback, стратегия одного действия | Контракт поведения, DI |
| Анонимность | Лямбды, анонимные методы | Требует класса |

**Правило**: если нужно **один метод** как параметр/возврат — **делегат**. Если **контракт с состоянием/несколькими методами** — **интерфейс**.

### 🔗 Multicast делегаты: цепочка вызовов

Делегаты в C# **мультикаст** — могут хранить список методов. При вызове выполняются **все** по порядку добавления.

```csharp
public delegate void Notification(string message);

Notification notify = null;
notify += EmailNotify;    // добавили
notify += SmsNotify;      // добавили
notify += PushNotify;     // добавили

notify("Hello!");  // Вызовет ВСЕ три метода по порядку

notify -= SmsNotify;  // убрали SMS
```

**Важно**: возвращаемое значение — только от **последнего** метода в цепочке. Если методы возвращают значения — используйте `GetInvocationList()` и вызывайте вручную.

```csharp
public delegate int Operation(int a, int b);

Operation ops = null;
ops += (a, b) => a + b;
ops += (a, b) => a - b;
ops += (a, b) => a * b;

int result = ops(10, 5);  // result = 50 (только последнее: 10 * 5)

// Чтобы получить все результаты:
var results = ops.GetInvocationList()
    .Cast<Operation>()
    .Select(d => d(10, 5))
    .ToList();  // [15, 5, 50]
```

### 📢 События (event): инкапсуляция multicast делегата

**Событие** — это обертка над делегатом, которая:
- Позволяет **только добавлять/удалять** обработчики (`+=`, `-=`)
- **Запрещает** прямой вызов и присваивание (`=`)
- Обеспечивает **инкапсуляцию**: класс сам решает, когда поднимать событие

**Паттерн события (Event Pattern)**:
1. Делегат-тип для обработчика (обычно `EventHandler<TEventArgs>`)
2. Событие с ключевым словом `event`
3. Защищенный виртуальный метод `OnEventName` для подъема
4. Проверка на `null` перед вызовом (или `?.Invoke`)

```csharp
// Стандартный паттерн события
public class Timer {
    // 1. Делегат (обычно EventHandler<T>)
    public event EventHandler<TickEventArgs> Tick;

    // 2. Метод подъема (protected virtual для наследования)
    protected virtual void OnTick(TickEventArgs e) {
        // Thread-safe вызов: копируем делегат, проверяем на null
        Tick?.Invoke(this, e);
    }

    public void Start() {
        while (true) {
            Thread.Sleep(1000);
            OnTick(new TickEventArgs(DateTime.Now));
        }
    }
}

public class TickEventArgs : EventArgs {
    public DateTime Time { get; }
    public TickEventArgs(DateTime time) => Time = time;
}

// Использование
timer.Tick += (sender, e) => Console.WriteLine($"Tick at {e.Time}");
timer.Tick += LogToFile;  // второй обработчик
```

### 📦 EventHandler<TEventArgs> — стандартный паттерн

В BCL есть готовый делегат: `EventHandler<TEventArgs>` где `TEventArgs : EventArgs`.

Сигнатура: `void Handler(object sender, TEventArgs e)`
- `sender` — объект, поднявший событие
- `e` — данные события (наследник `EventArgs`)

**Правила хорошего тона**:
- Наследуйте аргументы от `EventArgs`
- Имя класса аргументов: `<EventName>EventArgs`
- Свойства только для чтения (`get;`) — данные события не меняются
- Для отменяемых событий используйте `CancelEventArgs`

```csharp
// Стандартные EventArgs
public class UserRegisteredEventArgs : EventArgs {
    public User User { get; }
    public DateTime RegisteredAt { get; }
    public UserRegisteredEventArgs(User user) {
        User = user;
        RegisteredAt = DateTime.UtcNow;
    }
}

// Отменяемое событие
public class UserRegisteringEventArgs : CancelEventArgs {
    public User User { get; }
    public UserRegisteringEventArgs(User user) => User = user;
}

// Использование
public class UserService {
    public event EventHandler<UserRegisteringEventArgs> UserRegistering;
    public event EventHandler<UserRegisteredEventArgs> UserRegistered;

    public void Register(User user) {
        var args = new UserRegisteringEventArgs(user);
        OnUserRegistering(args);
        
        if (!args.Cancel) {
            // регистрация...
            OnUserRegistered(new UserRegisteredEventArgs(user));
        }
    }

    protected virtual void OnUserRegistering(UserRegisteringEventArgs e) =>
        UserRegistering?.Invoke(this, e);
    protected virtual void OnUserRegistered(UserRegisteredEventArgs e) =>
        UserRegistered?.Invoke(this, e);
}
```

### 🔌 Слабые события (Weak Events): решение утечек памяти

**Проблема**: подписчик на событие создает сильную ссылку от издателя к подписчику. Если подписчик не отписался (`-=`), GC не может его собрать — **утечка памяти**.

**Решения**:
1. **Всегда отписывайтесь** в `Dispose` / деструкторе / `Unloaded`
2. **WeakEventManager** (WPF) — слабая ссылка на обработчик
3. **Слабые делегаты** вручную через `WeakReference`
4. **События как интерфейсы** — `IObservable<T>` / `IObserver<T>` (Rx.NET)

```csharp
// Ручная реализация слабого события через WeakReference
public class WeakEvent<TEventArgs> where TEventArgs : EventArgs {
    private readonly List<WeakReference<EventHandler<TEventArgs>>> _handlers = new();

    public void Add(EventHandler<TEventArgs> handler) {
        _handlers.Add(new WeakReference<EventHandler<TEventArgs>>(handler));
    }

    public void Remove(EventHandler<TEventArgs> handler) {
        _handlers.RemoveAll(wr => !wr.TryGetTarget(out var h) || h == handler);
    }

    public void Invoke(object sender, TEventArgs e) {
        var dead = new List<WeakReference<EventHandler<TEventArgs>>>();
        foreach (var wr in _handlers) {
            if (wr.TryGetTarget(out var handler)) {
                handler(sender, e);
            } else {
                dead.Add(wr);
            }
        }
        foreach (var d in dead) _handlers.Remove(d);
    }
}
```

### ⚡ Async события: асинхронные обработчики

Стандартный `EventHandler` синхронен. Для async обработчиков нужен другой подход:

```csharp
public delegate Task AsyncEventHandler<TEventArgs>(object sender, TEventArgs e);

public event AsyncEventHandler<UserRegisteredEventArgs> UserRegisteredAsync;

protected virtual async Task OnUserRegisteredAsync(UserRegisteredEventArgs e) {
    var handlers = UserRegisteredAsync?.GetInvocationList();
    if (handlers != null) {
        var tasks = handlers.Cast<AsyncEventHandler<UserRegisteredEventArgs>>()
            .Select(h => h(this, e));
        await Task.WhenAll(tasks);  // параллельное выполнение
    }
}
```

**Важно**: исключения в одном обработчике не должны ломать остальные — используйте `Task.WhenAll` с try/catch внутри.

```csharp
public class AsyncEvent<TEventArgs> where TEventArgs : EventArgs {
    private readonly List<Func<object, TEventArgs, Task>> _handlers = new();

    public void Add(Func<object, TEventArgs, Task> handler) => _handlers.Add(handler);
    public void Remove(Func<object, TEventArgs, Task> handler) => _handlers.Remove(handler);

    public async Task InvokeAsync(object sender, TEventArgs e) {
        var tasks = _handlers.Select(h => SafeInvoke(h, sender, e)).ToList();
        await Task.WhenAll(tasks);
    }

    private async Task SafeInvoke(Func<object, TEventArgs, Task> handler, object sender, TEventArgs e) {
        try { await handler(sender, e); }
        catch (Exception ex) { /* log, не прерываем остальные */ }
    }
}
```

### 🔍 Pattern Matching с делегатами

C# 7+ позволяет использовать pattern matching для работы с делегатами:

```csharp
Delegate d = SomeMethod;

// Type pattern
if (d is Action<int> a) { a(42); }
else if (d is Func<int, int> f) { var r = f(5); }

// Switch expression (C# 8+)
string description = d switch {
    Action => "Action (void)",
    Func<int, int> => "Func<int, int>",
    Action<int, string> => "Action<int, string>",
    null => "Null delegate",
    _ => "Other delegate"
};

// Property pattern (C# 8+)
if (d is { Method: { Name: "Callback" } }) { }

// Null-coalescing для делегата
var handler = onClick ??= () => Console.WriteLine("Default");
```

## ⚠️ Типичные ошибки новичков

| Ошибка | Как проявляется | Как правильно |
|---|---|---|
| Вызов события без проверки на null | `Tick(this, e);` — NullReferenceException если нет подписчиков | Используйте `Tick?.Invoke(this, e);` или `EventHandler` с `?.Invoke` |
| Прямое присваивание события | `Click = Handler;` — ошибка компиляции (event не позволяет =) | Только `+=` и `-=` для событий |
| Забыли отписаться от события | Утечка памяти: подписчик живёт вечно | Реализуйте `IDisposable` и делайте `-=` в `Dispose()` |
| Возврат значения в multicast делегате | Возвращается только результат последнего метода | Используйте `GetInvocationList()` для сбора всех результатов |
| Блокировка в обработчике события | Deadlock: событие поднимается под локом, обработчик ждет тот же лок | Не поднимайте события под локом. Используйте `Task.Run` или асинхронные события |
| Использование event для публичного API вместо делегата | Нужно передать callback в метод — событие не подходит | Для callback используйте `Func/Action/Delegate`, не `event` |
| Асинхронный void в обработчике | `async void Handler()` — исключения теряются, порядок не гарантирован | Используйте `async Task` и асинхронные события (`Task`-based) |

## 🛠 Практика: закрепите навык

1. Создайте класс `EventBus` с методами `Subscribe<T>(Action<T>)`, `Publish<T>(T event)`. Реализуйте как синхронную, так и асинхронную версию.
2. Создайте класс `Observable<T>` с событием `ValueChanged` (oldValue, newValue). Реализуйте привязку: `binding.Bind(textBox, "Text", viewModel, "Name")`.
3. Реализуйте слабое событие `WeakEvent<T>` с `WeakReference`. Проверьте: подписчик собирается GC после потери сильных ссылок.
4. Исправьте ошибки:
```csharp
class Button {
    public event Action Click;  // Ошибка: нет EventArgs
    public void OnClick() => Click();  // Ошибка: нет ?.Invoke
}

class Form {
    public event EventHandler<EventArgs> Load;
    protected void OnLoad() { Load(this, EventArgs.Empty); }  // Ошибка: нет ?.Invoke
}
```

## 📌 Кратко о главном

- Делегат — типобезопасный указатель на метод. `Func<T, TResult>`, `Action<T>`, `Predicate<T>` — готовые делегаты.
- Multicast: `+=` добавляет, `-=` удаляет. Вызов — все методы по порядку. Возврат — только последний.
- Событие (`event`) — инкапсуляция делегата. Только `+=`/`-=`, вызов через `?.Invoke`.
- Паттерн события: `EventHandler<TEventArgs>`, `EventArgs`, `OnEventName`, `?.Invoke`.
- Async события: `Task`-based делегаты, `Task.WhenAll`, обработка ошибок в каждом обработчике.
- Утечки памяти: всегда отписывайтесь (`-=`), используйте `WeakEventManager` или `WeakReference`.
- Pattern matching: `is Action<int>`, `switch` на делегатах, property patterns.

## 🔗 Полезные ссылки

- Microsoft Docs — Delegates: https://learn.microsoft.com/dotnet/csharp/programming-guide/delegates/
- Microsoft Docs — Events: https://learn.microsoft.com/dotnet/csharp/programming-guide/events/
- Microsoft Docs — Weak Events: https://learn.microsoft.com/dotnet/desktop/wpf/advanced/weak-event-patterns
- Microsoft Docs — Async Events: https://learn.microsoft.com/dotnet/standard/events/
- Stephen Cleary — Async Events: https://blog.stephencleary.com/2013/02/async-events.html
""",
    "practice_tasks": [
        "Создайте класс `EventBus` с методами `Subscribe<T>(Action<T>)`, `Publish<T>(T event)`. Реализуйте как синхронную, так и асинхронную версию.",
        "Создайте класс `Observable<T>` с событием `ValueChanged` (oldValue, newValue). Реализуйте привязку: `binding.Bind(textBox, \"Text\", viewModel, \"Name\")`.",
        "Реализуйте слабое событие `WeakEvent<T>` с `WeakReference`. Проверьте: подписчик собирается GC после потери сильных ссылок.",
        "Исправьте ошибки:\n```csharp\nclass Button {\n    public event Action Click;  // Ошибка: нет EventArgs\n    public void OnClick() => Click();  // Ошибка: нет ?.Invoke\n}\n\nclass Form {\n    public event EventHandler<EventArgs> Load;\n    protected void OnLoad() { Load(this, EventArgs.Empty); }  // Ошибка: нет ?.Invoke\n}\n```"
    ],
    "common_errors": [
        {"mistake": "Вызов события без проверки на null", "correct": "Используйте `Tick?.Invoke(this, e);` или `EventHandler` с `?.Invoke`"},
        {"mistake": "Прямое присваивание события", "correct": "Только `+=` и `-=` для событий"},
        {"mistake": "Забыли отписаться от события", "correct": "Реализуйте `IDisposable` и делайте `-=` в `Dispose()`"},
        {"mistake": "Возврат значения в multicast делегате", "correct": "Используйте `GetInvocationList()` для сбора всех результатов"},
        {"mistake": "Блокировка в обработчике события", "correct": "Не поднимайте события под локом. Используйте `Task.Run` или асинхронные события"},
        {"mistake": "Использование event для публичного API вместо делегата", "correct": "Для callback используйте `Func/Action/Delegate`, не `event`"},
        {"mistake": "Асинхронный void в обработчике", "correct": "Используйте `async Task` и асинхронные события (`Task`-based)"}
    ],
    "resources": [
        "Microsoft Docs — Delegates: https://learn.microsoft.com/dotnet/csharp/programming-guide/delegates/",
        "Microsoft Docs — Events: https://learn.microsoft.com/dotnet/csharp/programming-guide/events/",
        "Microsoft Docs — Weak Events: https://learn.microsoft.com/dotnet/desktop/wpf/advanced/weak-event-patterns",
        "Microsoft Docs — Async Events: https://learn.microsoft.com/dotnet/standard/events/",
        "Stephen Cleary — Async Events: https://blog.stephencleary.com/2013/02/async-events.html"
    ],
    "key_takeaways": [
        "Делегат — типобезопасный указатель на метод. `Func<T, TResult>`, `Action<T>`, `Predicate<T>` — готовые делегаты.",
        "Multicast: `+=` добавляет, `-=` удаляет. Вызов — все методы по порядку. Возврат — только последний.",
        "Событие (`event`) — инкапсуляция делегата. Только `+=`/`-=`, вызов через `?.Invoke`.",
        "Паттерн события: `EventHandler<TEventArgs>`, `EventArgs`, `OnEventName`, `?.Invoke`.",
        "Async события: `Task`-based делегаты, `Task.WhenAll`, обработка ошибок в каждом обработчике.",
        "Утечки памяти: всегда отписывайтесь (`-=`), используйте `WeakEventManager` или `WeakReference`.",
        "Pattern matching: `is Action<int>`, `switch` на делегатах, property patterns."
    ],
    "estimated_minutes": 35,
    "language_slug": "csharp",
    "lesson_order": 14,
    "name_en": "Lesson: Delegates and Events",
    "short_description_en": "Learn delegates, multicast, events, async events in C#"
}

# ----- 15: LINQ -----
LESSONS[15] = {
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
    "content_md": """## 🎯 Что вы узнаете
- Синтаксис запросов (query syntax) vs методы расширения (method syntax)
- Отложенное выполнение (deferred execution) и его последствия
- Where, Select, OrderBy, GroupBy, Join, GroupJoin
- Агрегация: Sum, Average, Min, Max, Count, Aggregate
- IEnumerable vs IQueryable: когда что использовать

## 💡 Зачем LINQ: декларативность вместо императивности

Представьте: нужно найти все активные пользователи старше 18 лет, отсортировать по имени и взять первые 10.

**Императивно (как бы делали без LINQ):**
```csharp
var result = new List<User>();
foreach (var u in users) {
    if (u.IsActive && u.Age > 18) result.Add(u);
}
result.Sort((a, b) => a.Name.CompareTo(b.Name));
var top10 = result.Take(10).ToList();
```

**Декларативно (LINQ):**
```csharp
var top10 = users
    .Where(u => u.IsActive && u.Age > 18)
    .OrderBy(u => u.Name)
    .Take(10)
    .ToList();
```

LINQ позволяет описывать **ЧТО** нужно сделать, а не **КАК** это сделать.

### 🔧 Query Syntax vs Method Syntax

LINQ поддерживает два синтаксиса, которые компилируются в один и тот же IL:

**Query Syntax** (похоже на SQL):
```csharp
var adults = from u in users
             where u.Age >= 18
             orderby u.Name
             select u.Name;
```

**Method Syntax** (fluent API):
```csharp
var adults = users
    .Where(u => u.Age >= 18)
    .OrderBy(u => u.Name)
    .Select(u => u.Name);
```

**Когда что использовать**:
- Query syntax — для сложных запросов с join, group by, let
- Method syntax — для простых цепочек, больше контроля
- Можно комбинировать: `from u in users.Where(...) select u.Name`

### 🔄 Отложенное выполнение (Deferred Execution) — главное правило LINQ

Большинство LINQ-методов **не выполняются сразу**. Они возвращают `IEnumerable<T>` — «объект запроса». Выполнение происходит **только при переборе** (`foreach`, `ToList()`, `ToArray()`, `Count()`).

**Почему это важно**:
- Если коллекция изменится между созданием запроса и перебором — результат будет от **новой** коллекции
- Множественные переборы = множественные выполнения запроса

```csharp
var nums = new List<int> { 1, 2, 3 };
var query = nums.Where(n => n > 1);  // запрос СОЗДАН, но НЕ ВЫПОЛНЕН

nums.Add(10);  // меняем исходную коллекцию

foreach (var n in query) {  // ТОЛЬКО ЗДЕСЬ запрос ВЫПОЛНЯЕТСЯ
    Console.WriteLine(n);  // 2, 3, 10 (10 попал!)
}

// Чтобы «заморозить» результат — материализуйте:
var list = query.ToList();  // сразу выполняет и сохраняет в новый List
```

### 🔧 Основные операторы LINQ

| Категория | Методы | Назначение |
|---|---|---|
| Фильтрация | Where, OfType | Фильтрация элементов |
| Проекция | Select, SelectMany | Преобразование элементов |
| Сортировка | OrderBy, OrderByDescending, ThenBy, ThenByDescending | Сортировка |
| Группировка | GroupBy, ToLookup | Группировка по ключу |
| Объединение | Join, GroupJoin, Zip, Concat, Union, Intersect, Except | Объединение последовательностей |
| Агрегация | Count, Sum, Average, Min, Max, Aggregate | Агрегатные функции |
| Получение элементов | First, FirstOrDefault, Last, Single, ElementAt, Skip, Take | Получение элементов |
| Кванторы | Any, All, Contains | Проверка условий |
| Преобразование | ToList, ToArray, ToDictionary, ToLookup, OfType, Cast | Материализация |

```csharp
// Примеры основных операторов
var numbers = new[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };

var evens = numbers.Where(n => n % 2 == 0);                    // 2, 4, 6, 8, 10
var squares = numbers.Select(n => n * n);                       // 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
var sum = numbers.Sum();                                        // 55
var max = numbers.Max();                                        // 10
var firstBig = numbers.First(n => n > 5);                       // 6
var top3 = numbers.OrderByDescending(n => n).Take(3);           // 10, 9, 8

// Группировка
var words = new[] { "apple", "banana", "cherry", "date" };
var grouped = words.GroupBy(w => w[0]);  // по первой букве

// Подзапросы: Any, All, Contains
var hasExpensive = orders.Any(o => o.Amount > 1500);  // true
var allExpensive = orders.All(o => o.Amount > 100);   // true
var hasElectronics = orders.Any(o => o.Category == "Electronics"); // true
```

### 🔗 Join, GroupJoin, Zip — объединение последовательностей

**Join** — внутреннее соединение (inner join):
```csharp
var users = new[] { new { Id = 1, Name = "Alex" }, new { Id = 2, Name = "Maria" } };
var orders = new[] { new { UserId = 1, Product = "Book" }, new { UserId = 2, Product = "Phone" } };

var query = users.Join(orders, u => u.Id, o => o.UserId, (u, o) => new { u.Name, o.Product });
// Alex - Book, Maria - Phone
```

**GroupJoin** — левое внешнее соединение (left outer join):
```csharp
var query = users.GroupJoin(orders, u => u.Id, o => o.UserId, (u, orders) => new { u.Name, Orders = orders });
// Alex: [Book], Maria: [Phone], User без заказов: пустая коллекция
```

**Zip** — поэлементное объединение:
```csharp
var names = new[] { "Alex", "Maria" };
var ages = new[] { 25, 30 };
var zipped = names.Zip(ages, (n, a) => $"{n} is {a}");  // "Alex is 25", "Maria is 30"
```

### ⚡ PLINQ — параллельный LINQ

Для CPU-bound операций на больших коллекциях:

```csharp
var primes = Enumerable.Range(2, 1_000_000)
    .AsParallel()
    .Where(n => Enumerable.Range(2, (int)Math.Sqrt(n)).All(i => n % i != 0))
    .ToList();

// AsParallel() использует все ядра CPU. Для I/O-bound (HTTP, БД) — не используйте PLINQ.
```

## ⚠️ Типичные ошибки

| Ошибка | Как проявляется | Как правильно |
|---|---|---|
| Множественное перечисление IEnumerable | Запрос выполняется много раз | Материализуйте: `.ToList()` / `.ToArray()` |
| Where после Select | Фильтрация после проекции — лишняя работа | Where перед Select |
| Попытка добавить дубликат ключа в Dictionary | `dict.Add("key", 1); dict.Add("key", 2);` → ArgumentException | Используйте `dict["key"] = value` (перезапишет) или `TryAdd` |
| Обращение к несуществующему ключу | `dict["missing"]` → KeyNotFoundException | Используйте `TryGetValue` или `ContainsKey` |
| Изменение коллекции при переборе LINQ | `foreach (var x in query) list.Remove(x);` → InvalidOperationException | Сначала материализуйте: `var list = query.ToList();` |
| Путаница Length vs Count | `array.Count()` работает (LINQ), но `array.Length` — нативное свойство быстрее | Для массива — `Length`, для List — `Count` |

## 🛠 Практика: закрепите навык

1. Создайте массив `int[]` из 10 случайных чисел (Random). Найдите минимум, максимум и среднее арифметическое. Выведите индексы мин/макс.
2. Создайте `List<string>` имён. Добавьте 5 имён. Удалите второе имя. Вставьте «Гость» в начало. Отсортируйте. Выведите через `foreach`.
3. Создайте `Dictionary<string, int>` — телефонная книга (имя → номер). Добавьте 3 контакта. Реализуйте поиск по имени (TryGetValue). Удалите один контакт.
4. Дан `List<int>`. Используя LINQ: выберите только чётные, возведите в квадрат, отсортируйте по убыванию. Результат в новый List.
5. Исправьте ошибки:
```csharp
int[] a = { 1, 2, 3 };
Console.WriteLine(a[3]);  // Ошибка

var dict = new Dictionary<string, int>();
Console.WriteLine(dict["key"]);  // Ошибка

foreach (var x in list) list.Remove(x);  // Ошибка
```

## 📌 Кратко о главном

- LINQ — декларативный язык запросов: пишем ЧТО нужно, а не КАК
- Два синтаксиса: query syntax (SQL-like) и method syntax (fluent API)
- Отложенное выполнение: запрос выполняется при переборе (ToList, foreach)
- IEnumerable — в памяти, IQueryable — в БД (переводится в SQL)
- LINQ — отложенное выполнение! Материализуйте `ToList()` если нужен зафиксированный результат
- Индексы с 0. `Length` у массива, `Count` у List. `foreach` — только чтение, `for` — когда нужен индекс

## 🔗 Полезные ссылки

- Microsoft Docs — LINQ: https://learn.microsoft.com/dotnet/csharp/linq/
- Microsoft Docs — Standard Query Operators: https://learn.microsoft.com/dotnet/csharp/linq/standard-query-operators
- Microsoft Docs — IQueryable: https://learn.microsoft.com/dotnet/api/system.linq.iqueryable-1
- Microsoft Docs — PLINQ: https://learn.microsoft.com/dotnet/standard/parallel-programming/introduction-to-plinq
""",
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
        {"mistake": "Путаница Length vs Count", "correct": "Для массива — `Length`, для List — `Count`"},
        {"mistake": "`Count()` вместо `Any()`", "correct": "Для проверки наличия — `Any()`"}
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
    "estimated_minutes": 35,
    "language_slug": "csharp",
    "lesson_order": 15,
    "name_en": "Lesson: LINQ",
    "short_description_en": "Learn LINQ query syntax, method syntax, deferred execution, grouping, joins in C#"
}

# ----- 16: Collections Deep Dive -----
LESSONS[16] = {
    "title": "Урок 16: Коллекции — List, Dictionary, HashSet, Queue, Stack, Immutable",
    "slug": "lesson-16",
    "short_description": "Глубинный разбор коллекций: производительность, выбор правильной структуры, неизменяемые коллекции",
    "goals": [
        "Выбирать правильную коллекцию под задачу",
        "Понимать сложность операций O(1), O(n), O(log n)",
        "Работать с Immutable коллекциями для потокобезопасности",
        "Использовать Span/Memory для нулевых аллокаций"
    ],
    "content_md": """## 🎯 Что вы узнаете
- List<T>, Dictionary<TKey,TValue>, HashSet<T>, Queue<T>, Stack<T>, LinkedList<T>
- Сложность операций: когда O(1), когда O(n), когда O(log n)
- Immutable коллекции: ImmutableList, ImmutableDictionary, ImmutableArray
- Span<T>, Memory<T>, ReadOnlySpan<T> — работа без аллокаций
- Concurrent коллекции для многопоточности

## 📦 List<T> — динамический массив

```csharp
var list = new List<int> { 1, 2, 3 };
list.Add(4);           // O(1) амортизированное
list.Insert(0, 0);     // O(n) — сдвиг всех элементов
list.RemoveAt(0);      // O(n)
var x = list[0];       // O(1) — доступ по индексу
list.Sort();           // O(n log n)
```

**Когда использовать**: последовательный доступ, нужны индексы, частое добавление в конец.

## 🗝 Dictionary<TKey,TValue> — хеш-таблица

```csharp
var dict = new Dictionary<string, int>();
dict["key"] = 42;              // O(1) среднее
dict.TryGetValue("key", out var v); // O(1) безопасное чтение
dict.ContainsKey("key");       // O(1)
dict.Remove("key");            // O(1)
```

**Когда использовать**: быстрый поиск по ключу, уникальные ключи.

**Важно**: `GetHashCode()` и `Equals()` должны быть согласованы для ключей!

## 🔢 HashSet<T> — множество уникальных значений

```csharp
var set = new HashSet<int> { 1, 2, 3 };
set.Add(2);                    // false, уже есть
set.UnionWith(new[] { 3, 4 }); // {1,2,3,4}
set.IntersectWith(new[] { 2, 5 }); // {2}
set.ExceptWith(new[] { 1 });   // {2}
set.IsSubsetOf(new[] { 1,2,3 }); // true
```

**Когда использовать**: проверка принадлежности, операции над множествами, уникальность.

## 📋 Queue<T> и Stack<T>

```csharp
// FIFO — очередь
var q = new Queue<int>();
q.Enqueue(1); q.Enqueue(2);
var first = q.Dequeue(); // 1

// LIFO — стек
var s = new Stack<int>();
s.Push(1); s.Push(2);
var top = s.Pop(); // 2
```

**Queue**: BFS, пулы задач, обработка запросов.
**Stack**: DFS, парсинг, отмена действий (undo).

## 🔗 LinkedList<T> — двусвязный список

```csharp
var ll = new LinkedList<int>();
ll.AddLast(1);
var node = ll.AddLast(2);
ll.AddBefore(node, 0);  // O(1) если есть узел
ll.Remove(node);        // O(1)
```

**Когда использовать**: частые вставки/удаления в середине, итерация без индексов.

## ❄️ Immutable коллекции (System.Collections.Immutable)

```csharp
using System.Collections.Immutable;

var list = ImmutableList.Create(1, 2, 3);
var list2 = list.Add(4);           // новый список, старый неизменен
var list3 = list2.RemoveAt(0);     // еще один новый список

// Структурное разделение — эффективно по памяти!
// Потокобезопасны по дизайну
```

| Mutable | Immutable |
|---|---|
| List<T> | ImmutableList<T> |
| Dictionary<K,V> | ImmutableDictionary<K,V> |
| HashSet<T> | ImmutableHashSet<T> |
| Array | ImmutableArray<T> |
| Queue<T> | ImmutableQueue<T> |
| Stack<T> | ImmutableStack<T> |

## 🎯 Span<T> и Memory<T> — нулевые аллокации

```csharp
// Span — только стек, не может быть полем класса
ReadOnlySpan<char> span = "hello".AsSpan();
var sub = span.Slice(1, 3); // "ell" — никаких аллокаций!

// Memory — может быть на куче, для async
Memory<byte> buffer = new byte[1024];
await stream.ReadAsync(buffer); // без копирования

// Stackalloc для совсем маленьких буферов
Span<byte> small = stackalloc byte[256];
```

**Когда использовать**: парсинг, сериализация, работа с буферами, высокая производительность.

## ⚡ Concurrent коллекции (System.Collections.Concurrent)

```csharp
var dict = new ConcurrentDictionary<string, int>();
dict.GetOrAdd("key", k => ExpensiveCompute(k)); // атомарно
dict.TryUpdate("key", 42, 41);                  // CAS

var bag = new ConcurrentBag<int>();
bag.Add(1); // потокобезопасно

var queue = new ConcurrentQueue<int>();
queue.Enqueue(1);
queue.TryDequeue(out var x);
```

## 📊 Сводная таблица выбора

| Задача | Коллекция | Сложность |
|---|---|---|
| Список с индексами, добавление в конец | List<T> | O(1) add, O(1) index |
| Поиск по ключу | Dictionary<K,V> | O(1) |
| Уникальные значения, проверка вхождения | HashSet<T> | O(1) |
| FIFO очередь | Queue<T> | O(1) |
| LIFO стек | Stack<T> | O(1) |
| Вставки в середию | LinkedList<T> | O(1) с узлом |
| Потокобезопасность без локов | Immutable* | O(log n) |
| Многопоточный доступ с локами | Concurrent* | O(1) амортизированное |
| Парсинг без аллокаций | Span<T>/Memory<T> | O(1) slice |

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| `List.Contains()` в цикле | O(n²) на больших данных | Используйте HashSet для проверки вхождения |
| Dictionary с mutable ключом | Ключ изменился — элемент потерян | Ключи должны быть immutable |
| foreach по Dictionary — изменение | InvalidOperationException | Собирайте ключи в List сначала |
| List.Insert(0, x) в цикле | O(n²) | Используйте LinkedList или добавление в конец + Reverse |
| ImmutableList в цикле Add | Много аллокаций | Накапливайте в Builder: `list.ToBuilder()` |

## 🛠 Практика

1. Реализуйте LRU кэш на `Dictionary` + `LinkedList` (O(1) get/put).
2. Дан большой `List<int>` (1 млн). Найдите пересечение с другим списком быстрее всего.
3. Сравните производительность: `List.Add` vs `ImmutableList.Add` в цикле 100к итераций.
4. Напишите парсер CSV строки используя только `Span<char>` без аллокаций.
5. Исправьте:
```csharp
var dict = new Dictionary<List<int>, string>(); // Ошибка: List не может быть ключом
var list = new List<int>();
for (int i = 0; i < 10000; i++) list.Insert(0, i); // Очень медленно
```

## 📌 Кратко

- **List** — default choice для списков
- **Dictionary** — default для ключ-значение
- **HashSet** — для уникальности и проверки вхождения
- **Immutable*** — для потокобезопасности и функционального стиля
- **Span/Memory** — для высокой производительности без GC
- **Concurrent*** — для простой многопоточности

## 🔗 Ссылки

- Microsoft Docs — Collections: https://learn.microsoft.com/dotnet/standard/collections/
- Immutable Collections: https://learn.microsoft.com/dotnet/standard/collections/immutable
- Span/Memory: https://learn.microsoft.com/dotnet/standard/memory-and-spans/
""",
    "practice_tasks": [
        "Реализуйте LRU кэш на `Dictionary` + `LinkedList` (O(1) get/put).",
        "Дан большой `List<int>` (1 млн). Найдите пересечение с другим списком быстрее всего.",
        "Сравните производительность: `List.Add` vs `ImmutableList.Add` в цикле 100к итераций.",
        "Напишите парсер CSV строки используя только `Span<char>` без аллокаций.",
        "Исправьте:\n```csharp\nvar dict = new Dictionary<List<int>, string>(); // Ошибка: List не может быть ключом\nvar list = new List<int>();\nfor (int i = 0; i < 10000; i++) list.Insert(0, i); // Очень медленно\n```"
    ],
    "common_errors": [
        {"mistake": "`List.Contains()` в цикле", "correct": "Используйте HashSet для проверки вхождения"},
        {"mistake": "Dictionary с mutable ключом", "correct": "Ключи должны быть immutable"},
        {"mistake": "foreach по Dictionary — изменение", "correct": "Собирайте ключи в List сначала"},
        {"mistake": "List.Insert(0, x) в цикле", "correct": "Используйте LinkedList или добавление в конец + Reverse"},
        {"mistake": "ImmutableList в цикле Add", "correct": "Накапливайте в Builder: `list.ToBuilder()`"}
    ],
    "resources": [
        "Microsoft Docs — Collections: https://learn.microsoft.com/dotnet/standard/collections/",
        "Immutable Collections: https://learn.microsoft.com/dotnet/standard/collections/immutable",
        "Span/Memory: https://learn.microsoft.com/dotnet/standard/memory-and-spans/"
    ],
    "key_takeaways": [
        "List — default choice для списков",
        "Dictionary — default для ключ-значение",
        "HashSet — для уникальности и проверки вхождения",
        "Immutable* — для потокобезопасности и функционального стиля",
        "Span/Memory — для высокой производительности без GC",
        "Concurrent* — для простой многопоточности"
    ],
    "estimated_minutes": 30,
    "language_slug": "csharp",
    "lesson_order": 16,
    "name_en": "Lesson: Collections Deep Dive",
    "short_description_en": "Deep dive into List, Dictionary, HashSet, Immutable collections, Span/Memory"
}

# ----- 17: Async/Await -----
LESSONS[17] = {
    "title": "Урок 17: Асинхронность — Task, async/await, CancellationToken, ValueTask, IAsyncEnumerable",
    "slug": "lesson-17",
    "short_description": "Полное руководство по async/await: Task, ValueTask, CancellationToken, параллелизм, IAsyncEnumerable, ошибки",
    "goals": [
        "Понимать как работает async/await под капотом (state machine)",
        "Правильно использовать CancellationToken для отмены",
        "Выбирать между Task и ValueTask",
        "Работать с IAsyncEnumerable для стриминга",
        "Избегать deadlocks и типичных ошибок async"
    ],
    "content_md": """## 🎯 Что вы узнаете
- Task, Task<T>, ValueTask, ValueTask<T> — когда что использовать
- async/await — как это работает (state machine)
- CancellationToken — кооперативная отмена
- Task.Run, Task.WhenAll, Task.WhenAny, Parallel.ForEachAsync
- IAsyncEnumerable — асинхронные потоки данных
- ConfigureAwait, SynchronizationContext, deadlocks

## 🧠 Как работает async/await: State Machine

```csharp
public async Task<string> DownloadAsync(string url) {
    using var client = new HttpClient();
    var data = await client.GetStringAsync(url); // await — точка приостановки
    return Process(data);
}
```

Компилятор превращает это в **state machine** (структуру, реализующую `IAsyncStateMachine`):
- Состояние 0: старт, вызов `GetStringAsync`
- Состояние 1: продолжение после `await`, вызов `Process`
- Состояние -1: завершено

**Важно**: `await` не блокирует поток! Он регистрирует продолжение и возвращает управление вызывающему коду.

## ⚡ Task vs ValueTask

| Аспект | Task | ValueTask |
|---|---|---|
| Тип | Класс (reference type) | Структура (value type) |
| Аллокация | Всегда (кроме кэшированных) | Нет, если синхронно завершен |
| Использование | Асинхронные операции, долгие | Горячие пути, часто синхронные |
| Повторное ожидание | Можноawait много раз | **Только один раз!** |

```csharp
// ValueTask — для кэшированных/быстрых результатов
public ValueTask<int> GetCachedAsync(int key) {
    if (_cache.TryGetValue(key, out var value))
        return new ValueTask<int>(value); // синхронно, без аллокации
    return new ValueTask<int>(FetchFromDbAsync(key)); // асинхронно
}

// НЕЛЬЗЯ:
var vt = GetCachedAsync(1);
await vt;
await vt; // Исключение! ValueTask можно await только один раз
```

## 🛑 CancellationToken — кооперативная отмена

```csharp
public async Task ProcessAsync(CancellationToken ct = default) {
    for (int i = 0; i < 1000; i++) {
        ct.ThrowIfCancellationRequested(); // бросает OperationCanceledException
        await DoWorkAsync(i, ct);          // передаем дальше
    }
}

// Использование
using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
try {
    await ProcessAsync(cts.Token);
} catch (OperationCanceledException) {
    // отменено по таймауту
}
```

**Правила**:
- Всегда принимайте `CancellationToken` в async методах
- Проверяйте `ct.ThrowIfCancellationRequested()` в циклах
- Передавайте `ct` вниз по цепочке вызовов
- Используйте `CancellationTokenSource` для управления

## 🔄 Параллелизм: WhenAll, WhenAny, Parallel.ForEachAsync

```csharp
// Все одновременно — быстрее
var tasks = urls.Select(u => DownloadAsync(u));
var results = await Task.WhenAll(tasks); // ждет все

// Первая завершенная — для таймаутов, спекулятивного выполнения
var winner = await Task.WhenAny(tasks);

// Ограниченная параллельность (max 4 одновременно)
await Parallel.ForEachAsync(urls, new ParallelOptions { MaxDegreeOfParallelism = 4 },
    async (url, ct) => await DownloadAsync(url, ct));
```

**SemaphoreSlim** — для ручного ограничения:
```csharp
var sem = new SemaphoreSlim(4);
var tasks = urls.Select(async url => {
    await sem.WaitAsync(ct);
    try { return await DownloadAsync(url, ct); }
    finally { sem.Release(); }
});
await Task.WhenAll(tasks);
```

## 🌊 IAsyncEnumerable — асинхронные потоки

```csharp
// Producer
public async IAsyncEnumerable<int> GenerateAsync([EnumeratorCancellation] CancellationToken ct) {
    for (int i = 0; i < 100; i++) {
        await Task.Delay(10, ct);
        yield return i;
    }
}

// Consumer
await foreach (var item in GenerateAsync(ct)) {
    Console.WriteLine(item);
}

// LINQ над IAsyncEnumerable (System.Linq.Async)
var evens = GenerateAsync(ct).Where(x => x % 2 == 0);
await foreach (var x in evens) { }
```

**Когда использовать**: стриминг больших данных, чанки из БД, Server-Sent Events, gRPC streaming.

## ⚙️ ConfigureAwait и SynchronizationContext

```csharp
// По умолчанию: продолжение в том же контексте (UI thread, ASP.NET request context)
await client.GetAsync(url);

// ConfigureAwait(false) — продолжение в ThreadPool, без захвата контекста
await client.GetAsync(url).ConfigureAwait(false);
```

| Контекст | ConfigureAwait(true) | ConfigureAwait(false) |
|---|---|---|
| WPF/WinForms UI | Продолжение в UI потоке | В ThreadPool (может упасть при доступе к UI) |
| ASP.NET Core | Нет SynchronizationContext | Всегда в ThreadPool |
| Консоль/Worker | ThreadPool | ThreadPool |

**Правило**: в библиотеках **всегда** используйте `.ConfigureAwait(false)`. В UI коде — `true` (по умолчанию).

## 🔒 Deadlocks и как их избегать

**Классический deadlock** (WPF/старое ASP.NET):
```csharp
// НЕ ДЕЛАЙТЕ ТАК:
public string GetData() => GetDataAsync().Result; // Блокирует UI поток!
// async метод ждет продолжение в UI потоке, но UI поток заблокирован .Result
```

**Решения**:
1. **Везде async**: `public async Task<string> GetData() => await GetDataAsync();`
2. **ConfigureAwait(false)** в библиотеках
3. **Task.Run** для CPU-bound: `await Task.Run(() => HeavyCompute());`

## 🎯 ValueTask и IValueTaskSource — для высокой производительности

```csharp
// Продвинутый: пулинг ValueTask через IValueTaskSource
public class PooledTaskSource : IValueTaskSource<int> {
    // Реализация пулинга для избегания аллокаций в горячих путях
}
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| `async void` (кроме event handlers) | Исключения теряются, нельзя await | Используйте `async Task` |
| `.Result` / `.Wait()` | Deadlock в UI/ASP.NET классик | Везде `await` |
| Забыли CancellationToken | Невозможно отменить долгую операцию | Всегда добавляйте `CancellationToken` |
| `Task.Run` для I/O | Лишний поток, не нужно | `Task.Run` только для CPU-bound |
| `foreach` вместо `await foreach` | Не работает с IAsyncEnumerable | Используйте `await foreach` |
| Множественный await ValueTask | Исключение | Сохраняйте результат: `var result = await vt;` |
| Не передают ct вниз | Отмена не доходит до внутренних вызовов | Всегда пробрасывайте `ct` |

## 🛠 Практика

1. Реализуйте `RetryPolicy` с экспоненциальным backoff и `CancellationToken`.
2. Напишите загрузку файлов с ограничением параллелизма (SemaphoreSlim).
3. Создайте `IAsyncEnumerable` чтение больших CSV файлов чанками.
4. Исправьте deadlock:
```csharp
// В WPF приложении:
public string GetText() => DownloadAsync().Result; // Deadlock!
// Исправьте
```
5. Реализуйте `TimeoutAfter` extension: `await DownloadAsync().TimeoutAfter(TimeSpan.FromSeconds(5))`.

## 📌 Кратко

- **async/await** — синтаксический сахар над state machine, не блокирует потоки
- **Task** — для асинхронных операций, **ValueTask** — для горячих путей (один await!)
- **CancellationToken** — обязателен во всех async методах
- **Task.WhenAll** — параллелизм, **WhenAny** — таймауты/первый успех
- **IAsyncEnumerable** — стриминг данных без буферизации
- **ConfigureAwait(false)** — в библиотеках всегда
- **Никаких `.Result` / `.Wait()`** — только `await`

## 🔗 Ссылки

- Stephen Cleary — Async/Await: https://blog.stephencleary.com/
- Microsoft Docs — Async: https://learn.microsoft.com/dotnet/csharp/async
- IAsyncEnumerable: https://learn.microsoft.com/dotnet/csharp/async#iasyncenumerable
- ConfigureAwait: https://learn.microsoft.com/dotnet/api/system.threading.tasks.task.configureawait
""",
    "practice_tasks": [
        "Реализуйте `RetryPolicy` с экспоненциальным backoff и `CancellationToken`.",
        "Напишите загрузку файлов с ограничением параллелизма (SemaphoreSlim).",
        "Создайте `IAsyncEnumerable` чтение больших CSV файлов чанками.",
        "Исправьте deadlock:\n```csharp\n// В WPF приложении:\npublic string GetText() => DownloadAsync().Result; // Deadlock!\n// Исправьте\n```",
        "Реализуйте `TimeoutAfter` extension: `await DownloadAsync().TimeoutAfter(TimeSpan.FromSeconds(5))`."
    ],
    "common_errors": [
        {"mistake": "`async void` (кроме event handlers)", "correct": "Используйте `async Task`"},
        {"mistake": "`.Result` / `.Wait()`", "correct": "Везде `await`"},
        {"mistake": "Забыли CancellationToken", "correct": "Всегда добавляйте `CancellationToken`"},
        {"mistake": "`Task.Run` для I/O", "correct": "`Task.Run` только для CPU-bound"},
        {"mistake": "`foreach` вместо `await foreach`", "correct": "Используйте `await foreach`"},
        {"mistake": "Множественный await ValueTask", "correct": "Сохраняйте результат: `var result = await vt;`"},
        {"mistake": "Не передают ct вниз", "correct": "Всегда пробрасывайте `ct`"}
    ],
    "resources": [
        "Stephen Cleary — Async/Await: https://blog.stephencleary.com/",
        "Microsoft Docs — Async: https://learn.microsoft.com/dotnet/csharp/async",
        "IAsyncEnumerable: https://learn.microsoft.com/dotnet/csharp/async#iasyncenumerable",
        "ConfigureAwait: https://learn.microsoft.com/dotnet/api/system.threading.tasks.task.configureawait"
    ],
    "key_takeaways": [
        "async/await — синтаксический сахар над state machine, не блокирует потоки",
        "Task — для асинхронных операций, ValueTask — для горячих путей (один await!)",
        "CancellationToken — обязателен во всех async методах",
        "Task.WhenAll — параллелизм, WhenAny — таймауты/первый успех",
        "IAsyncEnumerable — стриминг данных без буферизации",
        "ConfigureAwait(false) — в библиотеках всегда",
        "Никаких .Result / .Wait() — только await"
    ],
    "estimated_minutes": 40,
    "language_slug": "csharp",
    "lesson_order": 17,
    "name_en": "Lesson: Async/Await Deep Dive",
    "short_description_en": "Complete guide to Task, async/await, CancellationToken, ValueTask, IAsyncEnumerable"
}

# ----- 18: CLR, GC, Memory -----
LESSONS[18] = {
    "title": "Урок 18: CLR, JIT, GC, управляемая память — под капотом .NET",
    "slug": "lesson-18",
    "short_description": "CLR, JIT компиляция, поколения GC, Large Object Heap, финализаторы, IDisposable, Span, unsafe",
    "goals": [
        "Понимать как работает JIT и tiered compilation",
        "Знать поколения GC (Gen 0, 1, 2) и LOH",
        "Правильно реализовывать IDisposable и финализаторы",
        "Работать с unsafe кодом, Span, Memory, stackalloc",
        "Диагностировать утечки памяти и производительность GC"
    ],
    "content_md": """## 🎯 Что вы узнаете
- CLR архитектура: JIT, AOT (NativeAOT), tiered compilation
- GC: поколения (Gen 0, 1, 2), Large Object Heap (LOH), Pinned Object Heap
- Финализаторы, IDisposable, SafeHandle, CriticalFinalizerObject
- Утечки памяти: event handlers, static поля, кэши, неправильный Dispose
- Unsafe код: pointers, stackalloc, Span<T>, Memory<T>, fixed
- Профилирование: dotnet-counters, dotnet-gcdump, PerfView

## ⚙️ CLR и JIT компиляция

### Компиляция
```
C# код → Roslyn → IL (Intermediate Language) → JIT → Native Code
```

### Tiered Compilation (многоуровневая)
- **Tier 0** — быстрая компиляция без оптимизаций, для быстрого старта
- **Tier 1** — оптимизированная версия для горячих методов
- **OSR (On-Stack Replacement)** — замена метода прямо во время выполнения

```csharp
// Можно отключить: <TieredCompilation>false</TieredCompilation>
// Или для конкретного метода:
[MethodImpl(MethodImplOptions.NoOptimization)]
public void NoOpt() { }
```

### ReadyToRun / NativeAOT
- **ReadyToRun** — предварительно скомпилированные сборки (больше размер, быстрее старт)
- **NativeAOT** — полностью нативный бинарь без JIT (маленький, быстрый старт, нет рефлексии)

## 🗑 Garbage Collector — поколенческая модель

### Поколения
| Поколение | Описание | Размер | Частота сборки |
|---|---|---|---|
| **Gen 0** | Новые объекты, короткоживущие | ~256 KB | Часто (млн раз/сек) |
| **Gen 1** | Выжившие после Gen 0 | ~2 MB | Реже |
| **Gen 2** | Долгоживущие объекты | Неограничен | Редко (Full GC) |

### Large Object Heap (LOH)
- Объекты **≥ 85,000 байт** (массивы, большие строки)
- Не компактируется (фрагментация)
- Собирается только при Full GC (Gen 2)
- .NET 5+: `GCSettings.LargeObjectHeapCompactionMode = CompactOnce`

### Pinned Object Heap (.NET 5+)
- Закрепленные объекты (`fixed`, `GCHandle.Alloc(pinned)`)
- Не двигаются при компактировке

### Режимы GC
```xml
<!-- Workstation (default для клиентских) -->
<ServerGarbageCollection>false</ServerGarbageCollection>
<ConcurrentGarbageCollection>true</ConcurrentGarbageCollection>

<!-- Server GC (для серверов, многопоточных приложений) -->
<ServerGarbageCollection>true</ServerGarbageCollection>
<!-- Background GC по умолчанию включен -->
```

## ♻️ IDisposable и Finalization

### Паттерн Dispose (Full)
```csharp
public class ResourceHolder : IDisposable {
    private SafeFileHandle _handle; // SafeHandle — правильный wrapper для unmanaged
    private bool _disposed;

    public ResourceHolder() {
        _handle = File.OpenHandle("file.txt", FileMode.Open);
    }

    public void Dispose() {
        Dispose(true);
        GC.SuppressFinalize(this); // не вызывать финализатор
    }

    protected virtual void Dispose(bool disposing) {
        if (_disposed) return;
        if (disposing) {
            // Освобождаем managed ресурсы
            _handle?.Dispose();
        }
        // Освобождаем unmanaged ресурсы (есть только в SafeHandle)
        _disposed = true;
    }

    // Финализатор ТОЛЬКО если есть unmanaged ресурсы БЕЗ SafeHandle
    ~ResourceHolder() => Dispose(false);
}
```

### SafeHandle — правильный способ
```csharp
// Вместо IntPtr + финализатор — используйте SafeHandle
public sealed class MySafeHandle : SafeHandleZeroOrMinusOneIsInvalid {
    private MySafeHandle() : base(true) { } // owns handle
    protected override bool ReleaseHandle() {
        NativeMethods.CloseHandle(handle);
        return true;
    }
}
```

**Правила**:
- Всегда используйте `SafeHandle` для unmanaged ресурсов
- Финализатор (`~Class`) нужен **только** если есть unmanaged ресурсы БЕЗ SafeHandle
- `GC.SuppressFinalize(this)` в `Dispose()`
- `Dispose(bool disposing)` — virtual для наследования

## 🔍 Диагностика памяти

### dotnet-counters (real-time)
```bash
dotnet-counters monitor --process-id <PID> --counters System.Runtime.GC
# Gen 0/1/2 collections, heap size, allocation rate
```

### dotnet-gcdump (heap snapshot)
```bash
dotnet-gcdump collect --process-id <PID>
dotnet-gcdump report <file>.gcdump --type-stat
# Анализ: кто держит память, пути к GC roots
```

### PerfView / dotnet-trace
```bash
dotnet-trace collect --process-id <PID> --providers Microsoft-Windows-DotNETRuntime
# Детальные ETW события GC, JIT, ThreadPool
```

### GC.GetTotalMemory / GC.CollectionCount
```csharp
long mem = GC.GetTotalMemory(false); // без принудительной сборки
int gen2 = GC.CollectionCount(2);
```

## ⚡ Unsafe, Pointers, Span, stackalloc

### fixed и pinning
```csharp
byte[] buffer = new byte[1024];
fixed (byte* p = buffer) {
    // p закреплен, GC не двигает buffer
    NativeWrite(p, 1024);
}
// после блока buffer снова может двигаться
```

### stackalloc — стек, без GC
```csharp
// Маленькие буферы на стеке
Span<byte> buffer = stackalloc byte[256];
// Для больших — только если точно знаете размер стека (обычно 1MB)
```

### Span<T> / Memory<T>
```csharp
// Span — только стек, ref struct
ReadOnlySpan<char> span = "hello".AsSpan();
var slice = span.Slice(1, 3); // никаких аллокаций!

// Memory — может быть на куче, для async
Memory<byte> mem = new byte[1024];
await stream.ReadAsync(mem); // без копирования

// MemoryMarshal — низкоуровневые преобразования
Span<byte> bytes = MemoryMarshal.AsBytes(span);
```

## 💡 Типичные утечки памяти

| Источник | Почему утекает | Решение |
|---|---|---|
| События (`+=` без `-=`) | Издатель держит подписчика | `IDisposable` с `-=`, WeakEventManager |
| Static поля / кэши | Живут до конца AppDomain | `WeakReference`, `MemoryCache` с лимитами |
| Незакрытые `IDisposable` | Финализатор не успевает / не вызывается | `using` / `await using` везде |
| Зарегистрированные коллбеки в DI | Singleton держит Scoped | Проверяйте lifetime в DI |
| Большие объекты в LOH | Фрагментация, редкий GC | `ArrayPool<T>`, `MemoryPool<T>`, pooling |

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| `GC.Collect()` в продакшене | Нарушает поколенческую логику, тормозит | Не вызывайте вручную (кроме тестов) |
| Финализатор без `GC.SuppressFinalize` | Double dispose, лишняя работа GC | Всегда `GC.SuppressFinalize(this)` в `Dispose()` |
| `fixed` на больших массивах | Фрагментирует кучу, блокирует GC | Используйте `ArrayPool`, `MemoryPool`, `GCHandle` аккуратно |
| `stackalloc` больших буферов | StackOverflow | `stackalloc` только для малых (< ~1KB) |
| Забыли `Dispose` на `FileStream` / `DbContext` | Утечка дескрипторов, блокировки файлов | Всегда `using` / `await using` |
| `byte[]` в цикле без пула | LOH фрагментация, Gen 2 GC | `ArrayPool<byte>.Shared.Rent/Return` |

## 🛠 Практика

1. Найдите утечку: создайте класс с событием, подпишитесь, «забудьте» отписаться. Проверьте через `dotnet-gcdump`.
2. Реализуйте пул `byte[]` через `ArrayPool<byte>`. Сравните аллокации с `new byte[]`.
3. Напишите `struct` с `IDisposable` (ref struct не может реализовывать интерфейсы — почему?).
4. Исправьте:
```csharp
class Bad {
    private FileStream _fs = File.OpenRead("x.txt");
    ~Bad() { _fs.Dispose(); } // Ошибка: финализатор может не вызвать Dispose
}
```
5. Профилируйте: `dotnet-counters monitor -p <pid> System.Runtime.GC` под нагрузкой.

## 📌 Кратко

- **JIT** — компилирует IL в нативный код; Tiered Compilation = быстрый старт + оптимизации
- **GC** — поколенческий (Gen 0/1/2), LOH для ≥85KB, компактирует (кроме LOH)
- **IDisposable** — паттерн с `Dispose(bool)`, `GC.SuppressFinalize`, `SafeHandle` для unmanaged
- **Unsafe** — `fixed`, `stackalloc`, `Span`/`Memory` для производительности без GC
- **Диагностика** — `dotnet-counters`, `dotnet-gcdump`, `dotnet-trace`, PerfView
- **Утечки** — события, статика, незакрытые Dispose, LOH фрагментация

## 🔗 Ссылки

- GC Fundamentals: https://learn.microsoft.com/dotnet/standard/garbage-collection/fundamentals
- IDisposable: https://learn.microsoft.com/dotnet/standard/garbage-collection/implementing-dispose
- Span/Memory: https://learn.microsoft.com/dotnet/standard/memory-and-spans/
- NativeAOT: https://learn.microsoft.com/dotnet/core/deploying/native-aot/
- PerfView: https://github.com/microsoft/perfview
""",
    "practice_tasks": [
        "Найдите утечку: создайте класс с событием, подпишитесь, «забудьте» отписаться. Проверьте через `dotnet-gcdump`.",
        "Реализуйте пул `byte[]` через `ArrayPool<byte>`. Сравните аллокации с `new byte[]`.",
        "Напишите `struct` с `IDisposable` (ref struct не может реализовывать интерфейсы — почему?).",
        "Исправьте:\n```csharp\nclass Bad {\n    private FileStream _fs = File.OpenRead(\"x.txt\");\n    ~Bad() { _fs.Dispose(); } // Ошибка: финализатор может не вызвать Dispose\n}\n```",
        "Профилируйте: `dotnet-counters monitor -p <pid> System.Runtime.GC` под нагрузкой."
    ],
    "common_errors": [
        {"mistake": "`GC.Collect()` в продакшене", "correct": "Не вызывайте вручную (кроме тестов)"},
        {"mistake": "Финализатор без `GC.SuppressFinalize`", "correct": "Всегда `GC.SuppressFinalize(this)` в `Dispose()`"},
        {"mistake": "`fixed` на больших массивах", "correct": "Используйте `ArrayPool`, `MemoryPool`, `GCHandle` аккуратно"},
        {"mistake": "`stackalloc` больших буферов", "correct": "`stackalloc` только для малых (< ~1KB)"},
        {"mistake": "Забыли `Dispose` на `FileStream` / `DbContext`", "correct": "Всегда `using` / `await using`"},
        {"mistake": "`byte[]` в цикле без пула", "correct": "`ArrayPool<byte>.Shared.Rent/Return`"}
    ],
    "resources": [
        "GC Fundamentals: https://learn.microsoft.com/dotnet/standard/garbage-collection/fundamentals",
        "IDisposable: https://learn.microsoft.com/dotnet/standard/garbage-collection/implementing-dispose",
        "Span/Memory: https://learn.microsoft.com/dotnet/standard/memory-and-spans/",
        "NativeAOT: https://learn.microsoft.com/dotnet/core/deploying/native-aot/",
        "PerfView: https://github.com/microsoft/perfview"
    ],
    "key_takeaways": [
        "JIT — компилирует IL в нативный код; Tiered Compilation = быстрый старт + оптимизации",
        "GC — поколенческий (Gen 0/1/2), LOH для ≥85KB, компактирует (кроме LOH)",
        "IDisposable — паттерн с Dispose(bool), GC.SuppressFinalize, SafeHandle для unmanaged",
        "Unsafe — fixed, stackalloc, Span/Memory для производительности без GC",
        "Диагностика — dotnet-counters, dotnet-gcdump, dotnet-trace, PerfView",
        "Утечки — события, статика, незакрытые Dispose, LOH фрагментация"
    ],
    "estimated_minutes": 40,
    "language_slug": "csharp",
    "lesson_order": 18,
    "name_en": "Lesson: CLR, GC, Memory Internals",
    "short_description_en": "CLR, JIT, GC generations, LOH, IDisposable, unsafe, Span, memory diagnostics"
}

# ----- 19: Testing -----
LESSONS[19] = {
    "title": "Урок 19: Тестирование — xUnit, NUnit, Moq, FluentAssertions, интеграционные тесты, Testcontainers",
    "slug": "lesson-19",
    "short_description": "Unit тесты, моки, интеграционные тесты, Testcontainers, покрытие кода, TDD, свойства хороших тестов",
    "goals": [
        "Писать unit тесты на xUnit/NUnit с FluentAssertions",
        "Использовать Moq для моков и стабов",
        "Писать интеграционные тесты с Testcontainers (БД, Redis, Kafka)",
        "Понимать TDD цикл: Red-Green-Refactor",
        "Измерять и улучшать покрытие кода"
    ],
    "content_md": """## 🎯 Что вы узнаете
- xUnit vs NUnit vs MSTest — выбор фреймворка
- AAA паттерн: Arrange, Act, Assert
- FluentAssertions — читаемые ассерты
- Moq — моки, стабы, верификация вызовов
- Интеграционные тесты с Testcontainers
- TDD, покрытие кода (coverlet), свойства хороших тестов (FIRST)

## 🧪 xUnit — современный стандарт

```csharp
public class CalculatorTests {
    [Fact]
    public void Add_TwoNumbers_ReturnsSum() {
        // Arrange
        var calc = new Calculator();
        
        // Act
        var result = calc.Add(2, 3);
        
        // Assert
        result.Should().Be(5);
    }

    [Theory]
    [InlineData(1, 2, 3)]
    [InlineData(-1, 1, 0)]
    [InlineData(0, 0, 0)]
    public void Add_VariousInputs_ReturnsExpected(int a, int b, int expected) {
        new Calculator().Add(a, b).Should().Be(expected);
    }
}
```

**xUnit особенности**:
- Нет `[SetUp]`/`[TearDown]` — используйте конструктор и `IDisposable`/`IAsyncDisposable`
- `[Fact]` — одиночный тест, `[Theory]` + `[InlineData]` — параметризованные
- Параллельный запуск по умолчанию

## 📖 FluentAssertions — читаемые проверки

```csharp
// Коллекции
list.Should().HaveCount(3).And.ContainInOrder(1, 2, 3);
list.Should().BeEquivalentTo(new[] { 1, 2, 3 }); // порядок не важен

// Строки
str.Should().StartWith("error").And.Contain("code").And.EndWith(".");

// Исключения
action.Should().Throw<ArgumentException>()
    .WithMessage("*invalid*")
    .Where(e => e.ParamName == "id");

// Асинхронные
await func.Should().ThrowAsync<TimeoutException>();

// Объекты
user.Should().BeEquivalentTo(expected, opts => opts.Excluding(u => u.PasswordHash));
```

## 🎭 Moq — моки и стабы

```csharp
var mockRepo = new Mock<IUserRepository>();

// Setup (стаб) — возвращает значение
mockRepo.Setup(r => r.GetByIdAsync(1, It.IsAny<CancellationToken>()))
        .ReturnsAsync(new User { Id = 1, Name = "Alex" });

// Callback — для сложной логики
mockRepo.Setup(r => r.AddAsync(It.IsAny<User>(), It.IsAny<CancellationToken>()))
        .Callback<User, CancellationToken>((u, ct) => u.Id = 42)
        .Returns(Task.CompletedTask);

// Verify — проверка вызовов
mockRepo.Verify(r => r.GetByIdAsync(1, It.IsAny<CancellationToken>()), Times.Once);
mockRepo.Verify(r => r.DeleteAsync(It.IsAny<int>(), It.IsAny<CancellationToken>()), Times.Never);

// Strict mock — падает на неожиданных вызовах
var strictMock = new Mock<IService>(MockBehavior.Strict);
```

**Moq советы**:
- `It.Is<T>(x => x.Id > 0)` — предикат
- `It.IsAny<T>()` — любой
- `It.IsInRange<T>(min, max, Range.Inclusive)` — диапазон
- `ReturnsAsync` для `Task<T>`, `Returns` для синхронных
- `Verifiable()` + `VerifyAll()` — для обязательных вызовов

## 🐳 Testcontainers — реальные БД в тестах

```csharp
// PostgreSQL контейнер
var postgres = new PostgreSqlBuilder()
    .WithDatabase("testdb")
    .WithUsername("test")
    .WithPassword("test")
    .Build();

await postgres.StartAsync();

var connStr = postgres.GetConnectionString();
// используйте для EF Core DbContext, Dapper и т.д.

// Автоочистка
await postgres.DisposeAsync();
```

```csharp
// В xUnit — IAsyncLifetime для общих контейнеров
public class DatabaseFixture : IAsyncLifetime {
    public PostgreSqlContainer Container { get; private set; }
    public string ConnectionString => Container.GetConnectionString();

    public async Task InitializeAsync() {
        Container = new PostgreSqlBuilder().Build();
        await Container.StartAsync();
        // Миграции
        await RunMigrationsAsync(ConnectionString);
    }

    public async Task DisposeAsync() => await Container.DisposeAsync();
}

// Использование
public class UserRepositoryTests : IClassFixture<DatabaseFixture> {
    private readonly DatabaseFixture _fixture;
    public UserRepositoryTests(DatabaseFixture fixture) => _fixture = fixture;
    
    [Fact]
    public async Task Add_User_Persists() {
        var repo = new UserRepository(_fixture.ConnectionString);
        await repo.AddAsync(new User { Name = "Test" });
        // ...
    }
}
```

**Доступные контейнеры**: PostgreSQL, MySQL, SQL Server, MongoDB, Redis, Kafka, RabbitMQ, Elasticsearch, LocalStack (AWS), Azurite (Azure), MinIO (S3).

## 🔄 Интеграционные тесты ASP.NET Core

```csharp
public class ApiTests : IClassFixture<WebApplicationFactory<Program>> {
    private readonly HttpClient _client;

    public ApiTests(WebApplicationFactory<Program> factory) {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetUsers_ReturnsOk() {
        var response = await _client.GetAsync("/api/users");
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }
}

// С переопределением конфигурации (Testcontainers БД)
var factory = new WebApplicationFactory<Program>()
    .WithWebHostBuilder(builder => {
        builder.ConfigureServices(services => {
            // Заменяем DbContext на тестовый с InMemory или Testcontainers
            services.RemoveAll<DbContextOptions<AppDbContext>>();
            services.AddDbContext<AppDbContext>(opt => 
                opt.UseNpgsql(_fixture.ConnectionString));
        });
    });
```

## 🔴🟢🔵 TDD: Red-Green-Refactor

1. **Red** — пишете падающий тест
2. **Green** — минимальный код для прохождения
3. **Refactor** — улучшаете код, тесты зеленые

```csharp
// Red: тест для несуществующего метода
[Fact]
public void CalculateDiscount_VipCustomer_Applies20Percent() {
    var svc = new DiscountService();
    svc.Calculate(new Customer { Type = CustomerType.Vip }, 100)
       .Should().Be(80);
}

// Green: минимальная реализация
public decimal Calculate(Customer c, decimal amount) =>
    c.Type == CustomerType.Vip ? amount * 0.8m : amount;

// Refactor: выносим стратегии, добавляем тесты на границы
```

## 📊 Покрытие кода (Code Coverage)

```bash
# Установка
dotnet tool install --global coverlet.console
dotnet tool install --global dotnet-reportgenerator-globaltool

# Запуск с покрытием
dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage

# Отчет HTML
reportgenerator -reports:"./coverage/**/coverage.cobertura.xml" -targetdir:"./coverage-report" -reporttypes:Html
```

**Метрики**:
- **Line coverage** — % выполненных строк
- **Branch coverage** — % пройденных веток (if/else)
- **Method coverage** — % вызванных методов

**Цель**: не 100%, а **смысловое покрытие** бизнес-логики.

## ✅ Свойства хороших тестов: FIRST

| Принцип | Описание |
|---|---|
| **Fast** | Быстрые (< 100ms unit, < 1s integration) |
| **Independent** | Не зависят друг от друга, порядок не важен |
| **Repeatable** | Детерминированные, проходят всегда одинаково |
| **Self-validating** | Падают/проходят сами, не требуют ручной проверки |
| **Timely** | Пишутся до или сразу после кода (TDD) |

**Анти-паттерны**:
- Тесты, зависящие от времени/даты/погоды/внешнего API
- Тесты, делящие состояние (static поля,シングleton БД)
- Тесты с `Thread.Sleep` вместо правильных ожиданий
- Один тест проверяет всё — разделяйте!

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Тестируете реализацию, не поведение | Рефакторинг ломает тесты | Тестируйте публичный API, поведение |
| Моки возвращают null | NullReference в коде | Всегда `Setup` для используемых методов |
| `Thread.Sleep` в тестах | Медленные, флаaky тесты | Используйте `WaitFor` с условием или виртуальное время |
| Общее состояние между тестами | Порядок влияет на результат | `IClassFixture`/`CollectionFixture`, изоляция |
| Тесты только happy path | Баги на граничных случаях | Тестируйте ошибки, null, пустые коллекции |
| Слишком много моков | Тест не проверяет реальную логику | Используйте реальные объекты где возможно |

## 🛠 Практика

1. Напишите unit тесты для `Calculator` с xUnit + FluentAssertions (Fact, Theory, исключения).
2. Замокайте `IEmailService` в тесте регистрации пользователя. Проверьте, что `SendWelcomeEmail` вызван ровно 1 раз.
3. Поднимите PostgreSQL в Testcontainers, запустите миграции EF Core, протестируйте `UserRepository`.
4. Напишите интеграционный тест ASP.NET Core endpoint с `WebApplicationFactory`.
5. Настройте `coverlet` + `reportgenerator` в CI. Поставьте порог покрытия 80% для бизнес-слоя.

## 📌 Кратко

- **xUnit** — дефолт для .NET, параллельный, конструктор вместо SetUp
- **FluentAssertions** — `Should().Be()`, читаемые ошибки
- **Moq** — `Setup`, `Verify`, `Callback`, `MockBehavior.Strict`
- **Testcontainers** — реальные БД/сервисы в Docker для интеграционных тестов
- **TDD** — Red → Green → Refactor
- **Coverage** — coverlet + reportgenerator, цель — смысловое покрытие
- **FIRST** — Fast, Independent, Repeatable, Self-validating, Timely

## 🔗 Ссылки

- xUnit: https://xunit.net/
- FluentAssertions: https://fluentassertions.com/
- Moq: https://github.com/moq/moq4
- Testcontainers: https://dotnet.testcontainers.org/
- TDD: https://learn.microsoft.com/dotnet/core/testing/tdd
""",
    "practice_tasks": [
        "Напишите unit тесты для `Calculator` с xUnit + FluentAssertions (Fact, Theory, исключения).",
        "Замокайте `IEmailService` в тесте регистрации пользователя. Проверьте, что `SendWelcomeEmail` вызван ровно 1 раз.",
        "Поднимите PostgreSQL в Testcontainers, запустите миграции EF Core, протестируйте `UserRepository`.",
        "Напишите интеграционный тест ASP.NET Core endpoint с `WebApplicationFactory`.",
        "Настройте `coverlet` + `reportgenerator` в CI. Поставьте порог покрытия 80% для бизнес-слоя."
    ],
    "common_errors": [
        {"mistake": "Тестируете реализацию, не поведение", "correct": "Тестируйте публичный API, поведение"},
        {"mistake": "Моки возвращают null", "correct": "Всегда `Setup` для используемых методов"},
        {"mistake": "`Thread.Sleep` в тестах", "correct": "Используйте `WaitFor` с условием или виртуальное время"},
        {"mistake": "Общее состояние между тестами", "correct": "`IClassFixture`/`CollectionFixture`, изоляция"},
        {"mistake": "Тесты только happy path", "correct": "Тестируйте ошибки, null, пустые коллекции"},
        {"mistake": "Слишком много моков", "correct": "Используйте реальные объекты где возможно"}
    ],
    "resources": [
        "xUnit: https://xunit.net/",
        "FluentAssertions: https://fluentassertions.com/",
        "Moq: https://github.com/moq/moq4",
        "Testcontainers: https://dotnet.testcontainers.org/",
        "TDD: https://learn.microsoft.com/dotnet/core/testing/tdd"
    ],
    "key_takeaways": [
        "xUnit — дефолт для .NET, параллельный, конструктор вместо SetUp",
        "FluentAssertions — Should().Be(), читаемые ошибки",
        "Moq — Setup, Verify, Callback, MockBehavior.Strict",
        "Testcontainers — реальные БД/сервисы в Docker для интеграционных тестов",
        "TDD — Red → Green → Refactor",
        "Coverage — coverlet + reportgenerator, цель — смысловое покрытие",
        "FIRST — Fast, Independent, Repeatable, Self-validating, Timely"
    ],
    "estimated_minutes": 45,
    "language_slug": "csharp",
    "lesson_order": 19,
    "name_en": "Lesson: Testing",
    "short_description_en": "Unit tests, mocking, integration tests, Testcontainers, TDD, code coverage"
}

# ----- 20: JSON, Files, Streams, SQL -----
LESSONS[20] = {
    "title": "Урок 20: JSON, файлы/потоки, SQL — работа с данными",
    "slug": "lesson-20",
    "short_description": "System.Text.Json, сериализация, файлы/потоки, ADO.NET, Dapper, EF Core основы, миграции",
    "goals": [
        "Сериализовать/десериализовать JSON с System.Text.Json",
        "Работать с файлами, потоками, StreamReader/Writer, PipeReader",
        "Использовать ADO.NET и Dapper для прямого SQL",
        "Понимать EF Core: DbContext, миграции, LINQ-to-SQL",
        "Выбирать правильный подход для сценария"
    ],
    "content_md": """## 🎯 Что вы узнаете
- System.Text.Json: опции, полиморфизм, кастомные конвертеры, Source Generator
- Файлы и потоки: FileStream, StreamReader/Writer, PipeReader, асинхронность
- ADO.NET: SqlConnection, SqlCommand, DataReader, параметры
- Dapper: микро-ORM, быстрый маппинг, мультимаппинг
- EF Core: DbContext, конфигурация, миграции, отслеживание изменений, LINQ

## 📄 System.Text.Json — современный JSON в .NET

### Базовая сериализация
```csharp
var user = new User { Id = 1, Name = "Alex", Email = "alex@example.com" };

// Сериализация
string json = JsonSerializer.Serialize(user);
// {"Id":1,"Name":"Alex","Email":"alex@example.com"}

// Десериализация
var user2 = JsonSerializer.Deserialize<User>(json);
```

### JsonSerializerOptions
```csharp
var options = new JsonSerializerOptions {
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase, // camelCase
    WriteIndented = true,                              //pretty print
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull, // игнорировать null
    Converters = { new JsonStringEnumConverter() },   // enum как строки
    ReferenceHandler = ReferenceHandler.Preserve,     // циклы ссылок
    NumberHandling = JsonNumberHandling.WriteAsString // большие числа как строки
};

string json = JsonSerializer.Serialize(user, options);
```

### Полиморфизм и $type
```csharp
[JsonPolymorphic(TypeDiscriminatorPropertyName = "$type")]
[JsonDerivedType(typeof(AdminUser), "admin")]
[JsonDerivedType(typeof(RegularUser), "regular")]
public abstract class User { public int Id { get; set; } }

public class AdminUser : User { public string[] Permissions { get; set; } }
public class RegularUser : User { public DateTime LastLogin { get; set; } }

// Сериализует с $type, десериализует в правильный тип
```

### Source Generator (AOT, производительность)
```csharp
[JsonSerializable(typeof(User))]
[JsonSerializable(typeof(List<User>))]
internal partial class AppJsonContext : JsonSerializerContext { }

// Использование — без рефлексии, работает в NativeAOT
string json = JsonSerializer.Serialize(user, AppJsonContext.Default.User);
```

### Кастомный конвертер
```csharp
public class DateOnlyConverter : JsonConverter<DateOnly> {
    public override DateOnly Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        => DateOnly.Parse(reader.GetString()!);

    public override void Write(Utf8JsonWriter writer, DateOnly value, JsonSerializerOptions options)
        => writer.WriteStringValue(value.ToString("yyyy-MM-dd"));
}

// Регистрация
options.Converters.Add(new DateOnlyConverter());
```

## 📁 Файлы и потоки

### FileStream — низкоуровневый
```csharp
// Чтение
await using var fs = new FileStream("data.bin", FileMode.Open, FileAccess.Read, FileShare.Read, bufferSize: 4096, useAsync: true);
var buffer = new byte[1024];
int read;
while ((read = await fs.ReadAsync(buffer)) > 0) {
    Process(buffer.AsSpan(0, read));
}

// Запись
await using var fs = new FileStream("out.bin", FileMode.Create, FileAccess.Write, FileShare.None, bufferSize: 4096, useAsync: true);
await fs.WriteAsync(data);
```

### StreamReader/Writer — текст
```csharp
// Чтение строк
await using var reader = new StreamReader("file.txt", Encoding.UTF8);
string line;
while ((line = await reader.ReadLineAsync()) != null) { }

// Запись
await using var writer = new StreamWriter("out.txt", append: false, Encoding.UTF8);
await writer.WriteLineAsync("Hello");
```

### PipeReader/Writer — высокопроизводительные пайплайны
```csharp
// Для высоконагруженного парсинга без аллокаций
var pipe = new Pipe();
_ = FillPipeAsync(pipe.Writer); // producer

var reader = pipe.Reader;
while (true) {
    var result = await reader.ReadAsync();
    var buffer = result.Buffer;
    
    // Парсим из buffer (ReadOnlySequence<byte>)
    Process(buffer);
    
    reader.AdvanceTo(buffer.End);
    if (result.IsCompleted) break;
}
```

### File API удобные методы
```csharp
// Простые сценарии
string text = await File.ReadAllTextAsync("file.txt");
await File.WriteAllTextAsync("file.txt", "content");
var lines = await File.ReadAllLinesAsync("file.txt");
await File.AppendAllLinesAsync("file.txt", new[] { "line1", "line2" });

// Временные файлы
string tempPath = Path.GetTempFileName();
```

## 🗄 ADO.NET — прямой доступ к БД

```csharp
await using var conn = new SqlConnection(connStr);
await conn.OpenAsync();

await using var cmd = new SqlCommand("SELECT Id, Name FROM Users WHERE Age > @age", conn);
cmd.Parameters.AddWithValue("@age", 18);

await using var reader = await cmd.ExecuteReaderAsync();
while (await reader.ReadAsync()) {
    int id = reader.GetInt32(0);
    string name = reader.GetString(1);
    // или reader["Name"] как object
}

// ExecuteScalar — одно значение
int count = (int)await cmd.ExecuteScalarAsync();

// ExecuteNonQuery — INSERT/UPDATE/DELETE
await using var insertCmd = new SqlCommand("INSERT INTO Users (Name) VALUES (@name)", conn);
insertCmd.Parameters.AddWithValue("@name", "New User");
int rows = await insertCmd.ExecuteNonQueryAsync();
```

**Важно**: всегда параметризуйте запросы — защита от SQL Injection!

## 🐟 Dapper — микро-ORM

```csharp
using Dapper;

await using var conn = new SqlConnection(connStr);

// Простой запрос
var users = await conn.QueryAsync<User>("SELECT * FROM Users WHERE Age > @age", new { age = 18 });

// Один объект
var user = await conn.QueryFirstOrDefaultAsync<User>("SELECT * FROM Users WHERE Id = @id", new { id = 1 });

// Параметры из объекта
await conn.ExecuteAsync("INSERT INTO Users (Name, Email) VALUES (@Name, @Email)", new { Name = "Alex", Email = "a@b.com" });

// Мультимаппинг (Join)
var sql = @"
    SELECT u.*, p.* 
    FROM Users u 
    LEFT JOIN Posts p ON p.UserId = u.Id 
    WHERE u.Id = @id";
var user = await conn.QueryAsync<User, Post, User>(sql, 
    (u, p) => { u.Posts ??= new(); u.Posts.Add(p); return u; },
    new { id = 1 },
    splitOn: "Id"); // колонка для разделения

// Транзакции
await using var tx = await conn.BeginTransactionAsync();
await conn.ExecuteAsync("...", params, tx);
await tx.CommitAsync();
```

## 🏗 EF Core — полноценный ORM

### DbContext и сущности
```csharp
public class AppDbContext : DbContext {
    public DbSet<User> Users => Set<User>();
    public DbSet<Post> Posts => Set<Post>();

    protected override void OnConfiguring(DbContextOptionsBuilder options)
        => options.UseNpgsql("Host=localhost;Database=mydb;Username=...");

    protected override void OnModelCreating(ModelBuilder model) {
        model.Entity<User>(e => {
            e.HasKey(u => u.Id);
            e.Property(u => u.Email).HasMaxLength(256).IsRequired();
            e.HasIndex(u => u.Email).IsUnique();
            e.HasMany(u => u.Posts).WithOne(p => p.User).HasForeignKey(p => p.UserId);
        });
    }
}
```

### Основные операции
```csharp
await using var db = new AppDbContext();

// Добавление
db.Users.Add(new User { Name = "Alex", Email = "a@b.com" });
await db.SaveChangesAsync();

// Чтение с трэкингом (по умолчанию)
var user = await db.Users.FindAsync(1);
user.Name = "New Name";
await db.SaveChangesAsync(); // UPDATE автоматически

// AsNoTracking — только чтение, быстрее
var users = await db.Users.AsNoTracking().Where(u => u.Age > 18).ToListAsync();

// Include — жадная загрузка
var userWithPosts = await db.Users.Include(u => u.Posts).FirstAsync(u => u.Id == 1);

// Select — проекция (только нужные колонки)
var names = await db.Users.Where(u => u.Age > 18).Select(u => u.Name).ToListAsync();

// Raw SQL
var users = await db.Users.FromSqlRaw("SELECT * FROM Users WHERE Age > {0}", 18).ToListAsync();
await db.Database.ExecuteSqlRawAsync("UPDATE Users SET Name = {0} WHERE Id = {1}", "New", 1);
```

### Миграции
```bash
# Создание
dotnet ef migrations add InitialCreate

# Применение
dotnet ef database update

# Откат
dotnet ef database update PreviousMigration

# Скрипт для продакшена
dotnet ef migrations script -o migration.sql
```

### Отслеживание изменений (Change Tracker)
```csharp
var user = await db.Users.FindAsync(1);
user.Name = "Changed";

// Что изменилось
var entries = db.ChangeTracker.Entries()
    .Where(e => e.State == EntityState.Modified);

foreach (var entry in entries) {
    Console.WriteLine($"{entry.Entity.GetType().Name}: {entry.State}");
    foreach (var prop in entry.Properties.Where(p => p.IsModified)) {
        Console.WriteLine($"  {prop.Metadata.Name}: {prop.OriginalValue} -> {prop.CurrentValue}");
    }
}
```

### Конкурентность (Optimistic Concurrency)
```csharp
public class User {
    public int Id { get; set; }
    public string Name { get; set; }
    [ConcurrencyCheck]
    public int Version { get; set; } // или [Timestamp] byte[] RowVersion
}

// При SaveChanges — DbUpdateConcurrencyException если Version изменился
```

## ⚡ Выбор подхода

| Сценарий | Рекомендация |
|---|---|
| Простые CRUD, производительность критична | Dapper |
| Сложная бизнес-логика, отношения, миграции | EF Core |
| Аналитические запросы, сырые SQL | ADO.NET / Dapper |
| Прототипирование, малые проекты | EF Core (InMemory для тестов) |
| Высокая нагрузка, bulk operations | Dapper + SqlBulkCopy / EF Core BulkExtensions |

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| N+1 проблема в EF Core | Загрузка коллекций в цикле | `Include`, `Select`, `SplitQuery` |
| Отсутствие `AsNoTracking` для чтения | Лишнее отслеживание, память | Всегда `AsNoTracking()` для read-only |
| JSON циклические ссылки | StackOverflow / бесконечная рекурсия | `ReferenceHandler.Preserve` или `[JsonIgnore]` |
| Конкатенация SQL строк | SQL Injection | Всегда параметры: `@param` |
| `File.ReadAllText` на больших файлах | OOM, блокировка | `StreamReader` / `PipeReader` построчно |
| Забыли `await using` / `Dispose` | Утечка дескрипторов, блокировки файлов | Всегда `await using` для асинхронных |

## 🛠 Практика

1. Сериализуйте объект с вложенными типами в JSON с `CamelCase`, `WriteIndented`, игнорируя null.
2. Напишите асинхронный парсер большего CSV (100MB) через `PipeReader` без загрузки в память.
3. Реализуйте репозиторий пользователей на Dapper с CRUD и транзакциями.
4. Создайте EF Core модель: User —< Post —< Comment. Напишите миграцию. Запросите пользователей с постами (Include) и только имена (Select).
5. Исправьте N+1:
```csharp
var users = db.Users.ToList();
foreach (var u in users) Console.WriteLine(u.Posts.Count); // N+1!
```

## 📌 Кратко

- **System.Text.Json** — быстрый, нативный, Source Generator для AOT
- **Потоки** — `FileStream` (байты), `StreamReader/Writer` (текст), `PipeReader` (high-perf)
- **ADO.NET** — база, полный контроль, параметры обязательны
- **Dapper** — быстрый маппинг, минимальные накладные расходы
- **EF Core** — полноценный ORM, миграции, LINQ, Change Tracker, N+1 проблема
- **Выбор** — Dapper для производительности/простых, EF Core для сложной логики

## 🔗 Ссылки

- System.Text.Json: https://learn.microsoft.com/dotnet/standard/serialization/system-text-json/
- Dapper: https://github.com/DapperLib/Dapper
- EF Core: https://learn.microsoft.com/ef/core/
- EF Core Performance: https://learn.microsoft.com/ef/core/performance/
""",
    "practice_tasks": [
        "Сериализуйте объект с вложенными типами в JSON с `CamelCase`, `WriteIndented`, игнорируя null.",
        "Напишите асинхронный парсер большего CSV (100MB) через `PipeReader` без загрузки в память.",
        "Реализуйте репозиторий пользователей на Dapper с CRUD и транзакциями.",
        "Создайте EF Core модель: User —< Post —< Comment. Напишите миграцию. Запросите пользователей с постами (Include) и только имена (Select).",
        "Исправьте N+1:\n```csharp\nvar users = db.Users.ToList();\nforeach (var u in users) Console.WriteLine(u.Posts.Count); // N+1!\n```"
    ],
    "common_errors": [
        {"mistake": "N+1 проблема в EF Core", "correct": "`Include`, `Select`, `SplitQuery`"},
        {"mistake": "Отсутствие `AsNoTracking` для чтения", "correct": "Всегда `AsNoTracking()` для read-only"},
        {"mistake": "JSON циклические ссылки", "correct": "`ReferenceHandler.Preserve` или `[JsonIgnore]`"},
        {"mistake": "Конкатенация SQL строк", "correct": "Всегда параметры: `@param`"},
        {"mistake": "`File.ReadAllText` на больших файлах", "correct": "`StreamReader` / `PipeReader` построчно"},
        {"mistake": "Забыли `await using` / `Dispose`", "correct": "Всегда `await using` для асинхронных"}
    ],
    "resources": [
        "System.Text.Json: https://learn.microsoft.com/dotnet/standard/serialization/system-text-json/",
        "Dapper: https://github.com/DapperLib/Dapper",
        "EF Core: https://learn.microsoft.com/ef/core/",
        "EF Core Performance: https://learn.microsoft.com/ef/core/performance/"
    ],
    "key_takeaways": [
        "System.Text.Json — быстрый, нативный, Source Generator для AOT",
        "Потоки — FileStream (байты), StreamReader/Writer (текст), PipeReader (high-perf)",
        "ADO.NET — база, полный контроль, параметры обязательны",
        "Dapper — быстрый маппинг, минимальные накладные расходы",
        "EF Core — полноценный ORM, миграции, LINQ, Change Tracker, N+1 проблема",
        "Выбор — Dapper для производительности/простых, EF Core для сложной логики"
    ],
    "estimated_minutes": 45,
    "language_slug": "csharp",
    "lesson_order": 20,
    "name_en": "Lesson: JSON, Files, Streams, SQL",
    "short_description_en": "System.Text.Json, files/streams, ADO.NET, Dapper, EF Core basics"
}

# ----- 21: Configuration, Logging, DI -----
LESSONS[21] = {
    "title": "Урок 21: Конфигурация, логирование, Dependency Injection — инфраструктура приложения",
    "slug": "lesson-21",
    "short_description": "IConfiguration, appsettings.json, переменные окружения, User Secrets, ILogger, Serilog, DI контейнер, жизненные циклы",
    "goals": [
        "Настраивать конфигурацию из множества источников",
        "Использовать User Secrets и Azure Key Vault для секретов",
        "Настраивать структурированное логирование с Serilog",
        "Понимать DI: Transient, Scoped, Singleton,_factory",
        "Регистрировать сервисы: по типу, фабрика, декоратор, open generics"
    ],
    "content_md": """## 🎯 Что вы узнаете
- IConfiguration: провайдеры, приоритеты, биндинг в объекты
- appsettings.json, appsettings.{Environment}.json, Environment Variables, User Secrets, Azure Key Vault
- ILogger, LogLevel, структурированное логирование, Serilog, Seq, ELK
- DI контейнер: Transient, Scoped, Singleton, регистрация, декораторы, المفتوحة generics
- IOptions, IOptionsMonitor, IOptionsSnapshot — паттерны опций

## ⚙️ Конфигурация — IConfiguration

### Источники и приоритет (последний побеждает)
```csharp
var config = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
    .AddJsonFile($"appsettings.{Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT")}.json", optional: true)
    .AddEnvironmentVariables(prefix: "MYAPP_")     // MYAPP_CONNECTIONSTRINGS__DB=...
    .AddUserSecrets<Program>()                     // dev: dotnet user-secrets set "Key" "Value"
    .AddAzureKeyVault(new Uri("https://myvault.vault.azure.net/"), new DefaultAzureCredential()) // prod
    .AddCommandLine(args)                          // --Key=Value
    .Build();
```

### Биндинг в строго типизированные объекты
```csharp
// appsettings.json
{
  "Database": {
    "ConnectionString": "Server=...;Database=...",
    "MaxPoolSize": 100,
    "EnableRetry": true
  },
  "Cache": { "Redis": { "Host": "localhost", "Port": 6379 } }
}

// Классы
public class DatabaseOptions {
    public string ConnectionString { get; set; }
    public int MaxPoolSize { get; set; }
    public bool EnableRetry { get; set; }
}

// Регистрация
services.Configure<DatabaseOptions>(config.GetSection("Database"));

// Использование через IOptions
public class UserService {
    private readonly DatabaseOptions _dbOptions;
    public UserService(IOptions<DatabaseOptions> options) => _dbOptions = options.Value;
}
```

### IOptions паттерны
| Интерфейс | Когда использовать | Особенности |
|---|---|---|
| `IOptions<TOptions>` | Singleton, читается один раз при старте | Кэшируется, не обновляется |
| `IOptionsSnapshot<TOptions>` | Scoped, перечитывается на каждый запрос | Для per-request конфигурации |
| `IOptionsMonitor<TOptions>` | Singleton, подписка на изменения | `OnChange(callback)`, `CurrentValue` |

```csharp
// Горячая перезагрузка
services.Configure<DatabaseOptions>(config.GetSection("Database"));

public class DbService {
    private readonly DatabaseOptions _options;
    public DbService(IOptionsMonitor<DatabaseOptions> monitor) {
        _options = monitor.CurrentValue;
        monitor.OnChange(o => _options = o); // реакция на изменения
    }
}
```

## 🔐 Секреты: User Secrets и Key Vault

### User Secrets (только Development)
```bash
dotnet user-secrets init
dotnet user-secrets set "Database:ConnectionString" "Server=dev;Database=mydb;..."
dotnet user-secrets list
```
Хранится в `%APPDATA%\\Microsoft\\UserSecrets\\<id>\\secrets.json` (Windows) или `~/.microsoft/usersecrets/<id>/secrets.json` (Linux/Mac).

### Azure Key Vault (Production)
```csharp
// В Program.cs
builder.Configuration.AddAzureKeyVault(
    new Uri("https://myapp.vault.azure.net/"),
    new DefaultAzureCredential()); // Managed Identity, Azure CLI, Env Vars
```
Секреты в KV: `Database--ConnectionString` → `Database:ConnectionString` в конфигурации.

## 📝 Логирование — ILogger и Serilog

### Встроенное логирование
```csharp
public class UserService {
    private readonly ILogger<UserService> _logger;
    public UserService(ILogger<UserService> logger) => _logger = logger;

    public void CreateUser(string name) {
        _logger.LogInformation("Creating user {Name}", name); // структурированное!
        _logger.LogDebug("Debug details for {Name}", name);
        _logger.LogWarning("User {Name} already exists", name);
        _logger.LogError(ex, "Failed to create user {Name}", name);
    }
}
```

**Уровни**: Trace < Debug < Information < Warning < Error < Critical < None

### Настройка в Program.cs
```csharp
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.AddDebug();
builder.Logging.AddFilter("Microsoft", LogLevel.Warning); // меньше шума от фреймворка
builder.Logging.AddFilter("System", LogLevel.Warning);
```

### Serilog — структурированные логи, sinks, enrichment
```bash
dotnet add package Serilog.AspNetCore
dotnet add package Serilog.Sinks.Console
dotnet add package Serilog.Sinks.Seq
dotnet add package Serilog.Sinks.File
```

```csharp
// Program.cs
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
    .Enrich.FromLogContext()
    .Enrich.WithProperty("Application", "MyApp")
    .Enrich.WithThreadId()
    .Enrich.WithMachineName()
    .WriteTo.Console(outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj} {Properties:j}{NewLine}{Exception}")
    .WriteTo.Seq("http://localhost:5341") // UI для логов
    .WriteTo.File("logs/app-.txt", rollingInterval: RollingInterval.Day, retainedFileCountLimit: 30)
    .CreateLogger();

builder.Host.UseSerilog();
```

**Структурированные свойства** (для запросов в Seq/ELK):
```csharp
_logger.LogInformation("Order {OrderId} placed by {UserId} for {Amount:C}", orderId, userId, amount);
// В Seq можно фильтровать: OrderId == "123" AND Amount > 100
```

### Log Scopes — корреляция
```csharp
using (_logger.BeginScope("OrderId={OrderId}", orderId)) {
    _logger.LogInformation("Processing payment");
    _logger.LogInformation("Sending confirmation");
}
// Все логи в scope автоматически имеют OrderId
```

## 💉 Dependency Injection — жизненные циклы

### Регистрация
```csharp
var services = new ServiceCollection();

// Transient — новый экземпляр КАЖДЫЙ раз
services.AddTransient<IEmailSender, SmtpEmailSender>();

// Scoped — один экземпляр НА ЗАПРОС (в ASP.NET Core)
services.AddScoped<IUserRepository, EfUserRepository>();

// Singleton — один экземпляр НА ВСЁ ПРИЛОЖЕНИЕ
services.AddSingleton<ICache, MemoryCache>();

// По фабрике
services.AddTransient<Func<EmailType, IEmailSender>>(sp => type => type switch {
    EmailType.Smtp => sp.GetRequiredService<SmtpEmailSender>(),
    EmailType.SendGrid => sp.GetRequiredService<SendGridEmailSender>(),
    _ => throw new ArgumentException()
});

// Декоратор (обертка)
services.Decorate<IUserRepository, CachingUserRepositoryDecorator>();

// Открытые дженерики
services.AddTransient(typeof(IRepository<>), typeof(EfRepository<>));
```

### Жизненные циклы — схема
```
Transient:  A -> [New]    B -> [New]    C -> [New]
Scoped:     Request 1: [Shared]        Request 2: [Shared]
Singleton:  App Start: [Single Instance Forever]
```

### Captive Dependency — ловушка!
```csharp
// ОШИБКА: Singleton зависит от Scoped!
services.AddSingleton<SingletonService>();
services.AddScoped<ScopedService>();

public class SingletonService {
    public SingletonService(ScopedService scoped) { } // BAD! Scoped заперт в Singleton
}
```
**Решение**: не инжектируйте Scoped в Singleton. Используйте `IServiceScopeFactory` для создания scope вручную.

### IServiceProvider / IServiceScopeFactory
```csharp
// Ручная резолвиция (в BackgroundService, SignalR Hubs, Middleware)
public class MyBackgroundService : BackgroundService {
    private readonly IServiceScopeFactory _scopeFactory;
    public MyBackgroundService(IServiceScopeFactory scopeFactory) => _scopeFactory = scopeFactory;

    protected override async Task ExecuteAsync(CancellationToken ct) {
        while (!ct.IsCancellationRequested) {
            using var scope = _scopeFactory.CreateScope();
            var repo = scope.ServiceProvider.GetRequiredService<IUserRepository>();
            await repo.CleanupAsync();
            await Task.Delay(TimeSpan.FromHours(1), ct);
        }
    }
}
```

### Keyed Services (.NET 8+)
```csharp
services.AddKeyedTransient<IPaymentProcessor, StripeProcessor>("stripe");
services.AddKeyedTransient<IPaymentProcessor, PayPalProcessor>("paypal");

// Резолвиция
var processor = sp.GetRequiredKeyedService<IPaymentProcessor>("stripe");
// или через атрибут
public class PaymentService([FromKeyedServices("stripe")] IPaymentProcessor processor) { }
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Singleton зависит от Scoped | Captive dependency, баги | Не инжектируйте Scoped в Singleton; используйте IServiceScopeFactory |
| Scoped зависит от Transient | OK (Transient создается внутри Scoped) | Нормально |
| Transient зависит от Scoped | OK | Нормально |
| Конфигурация не перечитывается | IOptions кэширует | Используйте IOptionsMonitor + OnChange |
| Секреты в appsettings.json | Утечка в Git | User Secrets (dev), Key Vault (prod) |
| Логи не структурированы | Нельзя запрашивать в Seq/ELK | Используйте `{Property}` синтаксис, Serilog |
| `ILogger<T>` в статическом классе | Нельзя инжектировать | Передавайте ILogger как параметр или используйте статический Log.Logger (Serilog) |

## 🛠 Практика

1. Настройте `ConfigurationBuilder` с appsettings.json, appsettings.Development.json, Environment Variables, User Secrets.
2. Создайте класс `JwtOptions` с биндингом из секции "Jwt". Используйте `IOptionsMonitor` для горячего обновления ключа.
3. Настройте Serilog: Console + Seq + File (rolling). Добавьте enrichment: ThreadId, MachineName, CorrelationId.
4. Зарегистрируйте сервисы: `IEmailSender` (Transient), `IUserRepository` (Scoped), `ICache` (Singleton). Добавьте декоратор для кэширования репозитория.
5. Исправьте captive dependency:
```csharp
services.AddSingleton<BackgroundWorker>();
services.AddScoped<DbContext>();
// BackgroundWorker инжектирует DbContext — ОШИБКА!
```

## 📌 Кратко

- **IConfiguration** — цепочка провайдеров, последний побеждает, биндинг в POCO
- **Секреты** — User Secrets (dev), Azure Key Vault (prod), НИКОГДА в Git
- **ILogger** — структурированное: `LogInformation("User {Id} logged in", id)`
- **Serilog** — sinks (Console, Seq, File), enrichment, scopes для корреляции
- **DI** — Transient (каждый раз), Scoped (на запрос), Singleton (на приложение)
- **Captive Dependency** — не кладите Scoped в Singleton!
- **IOptionsMonitor** — для реакции на изменения конфигурации

## 🔗 Ссылки

- Configuration: https://learn.microsoft.com/dotnet/core/extensions/configuration
- User Secrets: https://learn.microsoft.com/dotnet/core/extensions/user-secrets
- Logging: https://learn.microsoft.com/dotnet/core/extensions/logging
- Serilog: https://serilog.net/
- DI: https://learn.microsoft.com/dotnet/core/extensions/dependency-injection
- Keyed Services: https://learn.microsoft.com/dotnet/core/extensions/dependency-injection#keyed-services
""",
    "practice_tasks": [
        "Настройте `ConfigurationBuilder` с appsettings.json, appsettings.Development.json, Environment Variables, User Secrets.",
        "Создайте класс `JwtOptions` с биндингом из секции \"Jwt\". Используйте `IOptionsMonitor` для горячего обновления ключа.",
        "Настройте Serilog: Console + Seq + File (rolling). Добавьте enrichment: ThreadId, MachineName, CorrelationId.",
        "Зарегистрируйте сервисы: `IEmailSender` (Transient), `IUserRepository` (Scoped), `ICache` (Singleton). Добавьте декоратор для кэширования репозитория.",
        "Исправьте captive dependency:\n```csharp\nservices.AddSingleton<BackgroundWorker>();\nservices.AddScoped<DbContext>();\n// BackgroundWorker инжектирует DbContext — ОШИБКА!\n```"
    ],
    "common_errors": [
        {"mistake": "Singleton зависит от Scoped", "correct": "Не инжектируйте Scoped в Singleton; используйте IServiceScopeFactory"},
        {"mistake": "Scoped зависит от Transient", "correct": "OK (Transient создается внутри Scoped)"},
        {"mistake": "Transient зависит от Scoped", "correct": "OK"},
        {"mistake": "Конфигурация не перечитывается", "correct": "Используйте IOptionsMonitor + OnChange"},
        {"mistake": "Секреты в appsettings.json", "correct": "User Secrets (dev), Key Vault (prod)"},
        {"mistake": "Логи не структурированы", "correct": "Используйте `{Property}` синтаксис, Serilog"},
        {"mistake": "`ILogger<T>` в статическом классе", "correct": "Передавайте ILogger как параметр или используйте статический Log.Logger (Serilog)"}
    ],
    "resources": [
        "Configuration: https://learn.microsoft.com/dotnet/core/extensions/configuration",
        "User Secrets: https://learn.microsoft.com/dotnet/core/extensions/user-secrets",
        "Logging: https://learn.microsoft.com/dotnet/core/extensions/logging",
        "Serilog: https://serilog.net/",
        "DI: https://learn.microsoft.com/dotnet/core/extensions/dependency-injection",
        "Keyed Services: https://learn.microsoft.com/dotnet/core/extensions/dependency-injection#keyed-services"
    ],
    "key_takeaways": [
        "IConfiguration — цепочка провайдеров, последний побеждает, биндинг в POCO",
        "Секреты — User Secrets (dev), Azure Key Vault (prod), НИКОГДА в Git",
        "ILogger — структурированное: LogInformation(\"User {Id} logged in\", id)",
        "Serilog — sinks (Console, Seq, File), enrichment, scopes для корреляции",
        "DI — Transient (каждый раз), Scoped (на запрос), Singleton (на приложение)",
        "Captive Dependency — не кладите Scoped в Singleton!",
        "IOptionsMonitor — для реакции на изменения конфигурации"
    ],
    "estimated_minutes": 40,
    "language_slug": "csharp",
    "lesson_order": 21,
    "name_en": "Lesson: Configuration, Logging, DI",
    "short_description_en": "IConfiguration, appsettings, User Secrets, Serilog, DI lifecycles, IOptions"
}

# ----- 22: Architecture — Clean, DDD, CQRS -----
LESSONS[22] = {
    "title": "Урок 22: Архитектура — Clean Architecture, DDD, CQRS, MediatR, модульность",
    "slug": "lesson-22",
    "short_description": "Clean Architecture слои, Domain-Driven Design, CQRS с MediatR, Event Sourcing основы, модульные монолиты",
    "goals": [
        "Понимать Clean Architecture: слои, правила зависимостей",
        "Применять DDD: Entities, Value Objects, Aggregates, Domain Events, Repositories",
        "Реализовывать CQRS с MediatR: Commands, Queries, Handlers, Pipeline Behaviors",
        "Знать основы Event Sourcing и когда это нужно",
        "Проектировать модульные монолиты"
    ],
    "content_md": """## 🎯 Что вы узнаете
- Clean Architecture: 4 слоя, Dependency Rule, независимость от фреймворков
- DDD: Entity, Value Object, Aggregate Root, Domain Event, Repository, Factory
- CQRS: разделение чтения/записи, MediatR, Pipeline Behaviors (валидация, логирование, транзакции)
- Event Sourcing: события как источник истины, проекции
- Модульные монолиты: вертикальные срезы, изоляция модулей

## 🏛 Clean Architecture

### Слои (внутренний -> внешний)
```
┌─────────────────────────────────────┐
│        Domain (Enterprise)          │  ← Бизнес-логика, никаких зависимостей
│  Entities, Value Objects, Events    │
├─────────────────────────────────────┤
│      Application (Use Cases)        │  ← Use Cases, Interfaces, DTOs
│  Commands, Queries, Handlers,       │     Репозитории (интерфейсы)
│  Validators, Mappers                │
├─────────────────────────────────────┤
│       Infrastructure                │  ← Реализации: EF Core, HTTP, Email
│  DbContext, Repositories, Services  │
├─────────────────────────────────────┤
│        Presentation (API/UI)        │  ← Controllers, Views, gRPC, SignalR
│  Endpoints, DTOs, Mapping           │
└─────────────────────────────────────┘
```

### Dependency Rule
**Зависимости направлены ТОЛЬКО внутрь**. Внутренние слои не знают о внешних.
- Domain не ссылается ни на что
- Application ссылается только на Domain
- Infrastructure ссылается на Application + Domain
- Presentation ссылается на Application + Domain

### Реализация через интерфейсы (Inversion of Control)
```csharp
// Domain
public interface IUserRepository {
    Task<User?> GetByIdAsync(UserId id, CancellationToken ct);
    Task AddAsync(User user, CancellationToken ct);
}

// Application
public class UserService {
    private readonly IUserRepository _repo;
    public UserService(IUserRepository repo) => _repo = repo;
}

// Infrastructure
public class EfUserRepository : IUserRepository {
    private readonly AppDbContext _db;
    public EfUserRepository(AppDbContext db) => _db = db;
    // реализация через EF Core
}
```

## 🎯 Domain-Driven Design (DDD)

### Entity — идентичность
```csharp
public abstract class Entity<TId> where TId : notnull {
    public TId Id { get; protected set; }
    protected Entity(TId id) => Id = id;
    
    public override bool Equals(object? obj) 
        => obj is Entity<TId> other && Id.Equals(other.Id);
    public override int GetHashCode() => Id.GetHashCode();
}

public class User : Entity<UserId> {
    public string Name { get; private set; }
    public Email Email { get; private set; } // Value Object
    
    private User() { } // для EF Core
    
    public static User Create(UserId id, string name, Email email) {
        var user = new User(id) { Name = name, Email = email };
        user.AddDomainEvent(new UserCreatedEvent(user.Id));
        return user;
    }
    
    public void ChangeName(string newName) {
        Name = newName;
        AddDomainEvent(new UserNameChangedEvent(Id, newName));
    }
}
```

### Value Object — равенство по значениям
```csharp
public record Email(string Value) : IEquatable<Email> {
    public static implicit operator string(Email e) => e.Value;
    public static implicit operator Email(string s) => new(s);
    
    public Email {
        if (string.IsNullOrWhiteSpace(Value) || !Value.Contains("@"))
            throw new ArgumentException("Invalid email");
    }
}

// Или struct для производительности
public readonly struct Money : IEquatable<Money> {
    public decimal Amount { get; }
    public string Currency { get; }
    public Money(decimal amount, string currency) { Amount = amount; Currency = currency; }
    public bool Equals(Money other) => Amount == other.Amount && Currency == other.Currency;
}
```

### Aggregate Root — границы консистентности
```csharp
public class Order : Entity<OrderId> {
    private readonly List<OrderItem> _items = new();
    public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly();
    public OrderStatus Status { get; private set; }
    
    public void AddItem(ProductId productId, int quantity, Money price) {
        if (Status != OrderStatus.Draft) 
            throw new InvalidOperationException("Cannot modify confirmed order");
        
        var item = _items.FirstOrDefault(i => i.ProductId == productId);
        if (item != null) item.IncreaseQuantity(quantity);
        else _items.Add(new OrderItem(productId, quantity, price));
        
        AddDomainEvent(new OrderItemAddedEvent(Id, productId, quantity));
    }
    
    public void Confirm() {
        Status = OrderStatus.Confirmed;
        AddDomainEvent(new OrderConfirmedEvent(Id));
    }
}
```

### Domain Events — события внутри домена
```csharp
public abstract class Entity<TId> {
    private readonly List<IDomainEvent> _domainEvents = new();
    public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();
    
    protected void AddDomainEvent(IDomainEvent @event) => _domainEvents.Add(@event);
    public void ClearDomainEvents() => _domainEvents.Clear();
}

// Публикация после SaveChanges
public class DomainEventDispatcher {
    private readonly IMediator _mediator;
    public async Task DispatchEventsAsync(DbContext ctx, CancellationToken ct) {
        var entities = ctx.ChangeTracker.Entries<Entity>()
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

### Repository — абстракция персистентности
```csharp
// В Domain
public interface IUserRepository {
    Task<User?> GetByIdAsync(UserId id, CancellationToken ct);
    Task AddAsync(User user, CancellationToken ct);
    // НЕТ Update/Delete — Aggregate Root сам управляет состоянием
}

// В Infrastructure
public class EfUserRepository : IUserRepository {
    private readonly AppDbContext _db;
    public async Task<User?> GetByIdAsync(UserId id, CancellationToken ct)
        => await _db.Users.FindAsync(new object[] { id.Value }, ct);
    
    public async Task AddAsync(User user, CancellationToken ct)
        => await _db.Users.AddAsync(user, ct);
}
```

## ⚔️ CQRS с MediatR

### Команда (Command) — изменяет состояние
```csharp
public record CreateUserCommand(string Name, string Email) : IRequest<UserId>;

public class CreateUserHandler : IRequestHandler<CreateUserCommand, UserId> {
    private readonly IUserRepository _repo;
    private readonly IUnitOfWork _uow;
    
    public CreateUserHandler(IUserRepository repo, IUnitOfWork uow) {
        _repo = repo; _uow = uow;
    }
    
    public async Task<UserId> Handle(CreateUserCommand cmd, CancellationToken ct) {
        var email = new Email(cmd.Email);
        var user = User.Create(UserId.New(), cmd.Name, email);
        await _repo.AddAsync(user, ct);
        await _uow.SaveChangesAsync(ct);
        return user.Id;
    }
}
```

### Запрос (Query) — только чтение
```csharp
public record GetUserQuery(UserId Id) : IRequest<UserDto?>;

public class GetUserHandler : IRequestHandler<GetUserQuery, UserDto?> {
    private readonly IReadOnlyUserRepository _repo; // отдельный репозиторий для чтения
    
    public async Task<UserDto?> Handle(GetUserQuery query, CancellationToken ct) {
        var user = await _repo.GetByIdAsync(query.Id, ct);
        return user == null ? null : new UserDto(user.Id.Value, user.Name, user.Email.Value);
    }
}
```

### Pipeline Behaviors — cross-cutting concerns
```csharp
// Валидация (FluentValidation)
public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> 
    where TRequest : IRequest<TResponse> {
    private readonly IEnumerable<IValidator<TRequest>> _validators;
    
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct) {
        var context = new ValidationContext<TRequest>(request);
        var failures = _validators.Select(v => v.Validate(context))
            .SelectMany(r => r.Errors)
            .Where(e => e != null)
            .ToList();
        
        if (failures.Any())
            throw new ValidationException(failures);
        
        return await next();
    }
}

// Логирование
public class LoggingBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> {
    private readonly ILogger<LoggingBehavior<TRequest, TResponse>> _logger;
    
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct) {
        _logger.LogInformation("Handling {RequestName}", typeof(TRequest).Name);
        var response = await next();
        _logger.LogInformation("Handled {RequestName}", typeof(TRequest).Name);
        return response;
    }
}

// Транзакция
public class TransactionBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> {
    private readonly IUnitOfWork _uow;
    
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct) {
        if (request is ICommand) { // только для команд
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

// Регистрация
services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(typeof(Program).Assembly));
services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
services.AddTransient(typeof(IPipelineBehavior<,>), typeof(TransactionBehavior<,>));
```

## 📜 Event Sourcing — события как источник истины

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

// Event Store — только Append, никогда Update/Delete
public interface IEventStore {
    Task AppendAsync(AggregateId id, IEnumerable<IDomainEvent> events, int expectedVersion, CancellationToken ct);
    Task<IReadOnlyList<IDomainEvent>> GetEventsAsync(AggregateId id, CancellationToken ct);
}

// Проекции (Read Models) — строятся из событий асинхронно
public class AccountBalanceProjection : IEventHandler<MoneyDepositedEvent>, IEventHandler<MoneyWithdrawnEvent> {
    private readonly IReadModelRepository<AccountBalanceView> _repo;
    
    public async Task Handle(MoneyDepositedEvent @event, CancellationToken ct) {
        var view = await _repo.GetAsync(@event.AccountId) ?? new AccountBalanceView(@event.AccountId);
        view.Balance += @event.Amount;
        await _repo.SaveAsync(view, ct);
    }
}
```

**Когда использовать Event Sourcing**:
- Аудит обязателен (финансы, медицина)
- Сложная бизнес-логика с историей
- Нужен time-travel / debug по событиям
- CQRS read models обновляются из событий

## 🧩 Модульные монолиты (Modular Monolith)

```csharp
// Каждый модуль — независимый вертикальный срез
src/
├── Modules/
│   ├── Users/
│   │   ├── Domain/
│   │   ├── Application/
│   │   ├── Infrastructure/
│   │   ├── Api/
│   │   └── UsersModule.cs (IModule)
│   ├── Orders/
│   └── Payments/
├── BuildingBlocks/ (shared kernel: MediatR, EF Core base, etc.)
└── Host/ (ASP.NET Core startup, DI registration)

// Регистрация модулей
public interface IModule {
    void RegisterModule(WebApplicationBuilder builder);
    void MapEndpoints(WebApplication app);
}

public class UsersModule : IModule {
    public void RegisterModule(WebApplicationBuilder builder) {
        builder.Services.AddMediatR(typeof(UsersModule).Assembly);
        builder.Services.AddDbContext<UsersDbContext>(...);
        // внутренние сервисы модуля
    }
    public void MapEndpoints(WebApplication app) {
        app.MapGroup("/api/users").MapUsersEndpoints();
    }
}

// В Program.cs
var modules = new IModule[] { new UsersModule(), new OrdersModule() };
foreach (var m in modules) m.RegisterModule(builder);
var app = builder.Build();
foreach (var m in modules) m.MapEndpoints(app);
```

**Преимущества**:
- Изоляция: модули не знают друг о друге (общаются через MediatR/Events)
- Независимое развертывание в будущем (микросервисы)
- Четкие границы, низкая связанность

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Анемичная доменная модель | Логика в сервисах, Entity = DTO | Переносите логику в Entity/Aggregate, используйте фабричные методы |
| Репозиторий возвращает IQueryable | Утекает детали БД в Application | Репозиторий возвращает материализованные коллекции |
| Команды и запросы в одном обработчике | Нарушение CQRS | Разделяйте: IRequest<T> для команд, IRequest<T> для запросов |
| Слишком много слоев для простого CRUD | Over-engineering | Для CRUD — Minimal API + EF Core прямо в контроллере |
| Domain Events не публикуются | Интеграционные события не работают | Dispatch в SaveChanges через DomainEventDispatcher |

## 🛠 Практика

1. Создайте Clean Architecture решение: 4 проекта (Domain, Application, Infrastructure, Api). Настройте зависимости.
2. Реализуйте Aggregate `Order` с Value Object `Money`, Domain Events, методы `AddItem`, `Confirm`.
3. Напишите `CreateOrderCommand` и `GetOrderQuery` с MediatR. Добавьте `ValidationBehavior` (FluentValidation).
4. Реализуйте `DomainEventDispatcher`, публикующий события после `SaveChangesAsync`.
5. Создайте модульный монолит с модулями `Users` и `Orders`. Общение через MediatR.

## 📌 Кратко

- **Clean Architecture** — 4 слоя, зависимости только внутрь, интерфейсы в Application
- **DDD** — Entity (Id), Value Object (равенство по значению), Aggregate Root (консистентность), Domain Events
- **CQRS** — Commands (write) / Queries (read), MediatR, Pipeline Behaviors для cross-cutting
- **Event Sourcing** — события как log, проекции для чтения, аудит из коробки
- **Modular Monolith** — вертикальные срезы, изоляция, путь к микросервисам

## 🔗 Ссылки

- Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- DDD Reference: https://domainlanguage.com/ddd/
- MediatR: https://github.com/jbogard/MediatR
- Event Sourcing: https://martinfowler.com/eaaDev/EventSourcing.html
- Modular Monolith: https://www.kamilgrzybek.com/design/modular-monolith-primer/
""",
    "practice_tasks": [
        "Создайте Clean Architecture решение: 4 проекта (Domain, Application, Infrastructure, Api). Настройте зависимости.",
        "Реализуйте Aggregate `Order` с Value Object `Money`, Domain Events, методы `AddItem`, `Confirm`.",
        "Напишите `CreateOrderCommand` и `GetOrderQuery` с MediatR. Добавьте `ValidationBehavior` (FluentValidation).",
        "Реализуйте `DomainEventDispatcher`, публикующий события после `SaveChangesAsync`.",
        "Создайте модульный монолит с модулями `Users` и `Orders`. Общение через MediatR."
    ],
    "common_errors": [
        {"mistake": "Анемичная доменная модель", "correct": "Переносите логику в Entity/Aggregate, используйте фабричные методы"},
        {"mistake": "Репозиторий возвращает IQueryable", "correct": "Репозиторий возвращает материализованные коллекции"},
        {"mistake": "Команды и запросы в одном обработчике", "correct": "Разделяйте: IRequest<T> для команд, IRequest<T> для запросов"},
        {"mistake": "Слишком много слоев для простого CRUD", "correct": "Для CRUD — Minimal API + EF Core прямо в контроллере"},
        {"mistake": "Domain Events не публикуются", "correct": "Dispatch в SaveChanges через DomainEventDispatcher"}
    ],
    "resources": [
        "Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html",
        "DDD Reference: https://domainlanguage.com/ddd/",
        "MediatR: https://github.com/jbogard/MediatR",
        "Event Sourcing: https://martinfowler.com/eaaDev/EventSourcing.html",
        "Modular Monolith: https://www.kamilgrzybek.com/design/modular-monolith-primer/"
    ],
    "key_takeaways": [
        "Clean Architecture — 4 слоя, зависимости только внутрь, интерфейсы в Application",
        "DDD — Entity (Id), Value Object (равенство по значению), Aggregate Root (консистентность), Domain Events",
        "CQRS — Commands (write) / Queries (read), MediatR, Pipeline Behaviors для cross-cutting",
        "Event Sourcing — события как log, проекции для чтения, аудит из коробки",
        "Modular Monolith — вертикальные срезы, изоляция, путь к микросервисам"
    ],
    "estimated_minutes": 50,
    "language_slug": "csharp",
    "lesson_order": 22,
    "name_en": "Lesson: Architecture — Clean, DDD, CQRS",
    "short_description_en": "Clean Architecture layers, DDD, CQRS with MediatR, Event Sourcing, Modular Monolith"
}

# ----- 23: Advanced Type System -----
LESSONS[23] = {
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
    "content_md": """## 🎯 Что вы узнаете
- Constraints: `class`, `struct`, `new()`, `notnull`, `unmanaged`, `Delegate`, `Enum`, `default`
- Covariance (`out`) и Contravariance (`in`) — когда и как использовать
- Pattern Matching: switch expressions, property patterns, list patterns, slice patterns
- Records: reference и struct, `with`-expressions, positional syntax, equality
- Modern C#: `required`, `init`, `file` types, Generic Math (`INumber<T>`)

## 🔧 Generics Constraints — полный обзор

```csharp
// Базовые
where T : class           // ссылочный тип
where T : struct          // значимый тип (не nullable)
where T : new()           // публичный конструктор без параметров
where T : notnull         // не-nullable (reference или value)
where T : unmanaged       // примитивы, указатели, structs без реф-полей
where T : Delegate        // любой делегат (C# 7.3+)
where T : Enum            // любой enum (C# 7.3+)
where T : BaseClass       // наследник BaseClass
where T : IInterface      // реализует интерфейс
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

### Unmanaged constraint — для высокой производительности
```csharp
// Только примитивы, указатели, enums, structs без реф-полей
public static T[] AllocateArray<T>(int length) where T : unmanaged
    => new T[length]; // гарантированно нет GC-ссылок внутри

public static void MemCopy<T>(T* src, T* dst, int count) where T : unmanaged
    => Buffer.MemoryCopy(src, dst, count * sizeof(T), count * sizeof(T));
```

## 🔄 Covariance и Contravariance

### Covariance (`out`) — «выход» (возврат)
```csharp
// IEnumerable<out T> — можно присваивать IEnumerable<Derived> -> IEnumerable<Base>
IEnumerable<string> strings = new List<string>(); // OK
IEnumerable<object> objects = strings;            // OK: string -> object

// Delegate covariance
Func<string> funcStr = () => "hello";
Func<object> funcObj = funcStr; // OK: возвращает string, а ожидается object
```

**Правило**: `out` — только в **возвращаемых** позициях (return type, property get).

### Contravariance (`in`) — «вход» (параметр)
```csharp
// IComparer<in T> — можно присваивать IComparer<Base> -> IComparer<Derived>
IComparer<object> objComparer = (a, b) => 0;
IComparer<string> strComparer = objComparer; // OK: object сравнивает всё, что string

// Delegate contravariance
Action<object> actObj = o => Console.WriteLine(o);
Action<string> actStr = actObj; // OK: принимает object, а string — это object
```

**Правило**: `in` — только в **входных** позициях (parameters, property set).

### Инвариантность — по умолчанию
```csharp
// List<T> — инвариантен
List<string> strings = new();
List<object> objects = strings; // ОШИБКА!
// Потому что List<T> имеет Add(T) — вход, и T this[int] — выход
```

### Свои вариантные интерфейсы
```csharp
// Только для интерфейсов и делегатов!
public interface IReadOnlyRepository<out T> {
    T GetById(int id);           // OK: out
    // void Add(T item);         // ОШИБКА: in позиция
}

public interface IWriteOnlyRepository<in T> {
    void Add(T item);            // OK: in
    // T GetById(int id);        // ОШИБКА: out позиция
}

public interface IRepository<T> : IReadOnlyRepository<T>, IWriteOnlyRepository<T> { }
// IRepository<T> — инвариантен
```

## 🎯 Pattern Matching — современный синтаксис

### Switch Expressions (C# 8+)
```csharp
string Describe(object obj) => obj switch {
    int i when i > 0 => $"Positive int: {i}",
    int i when i < 0 => $"Negative int: {i}",
    int _ => "Zero",
    string s when s.Length > 10 => $"Long string: {s.Length}",
    string s => $"Short string: {s}",
    null => "Null",
    _ => "Unknown"
};

// Выражение с типом
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

bool isAdultInMoscow = user is { Age: >= 18, Address: { City: "Moscow" } };

string category = user switch {
    { Age: < 18 } => "Minor",
    { Age: >= 65 } => "Senior",
    { Name: "Admin" or "Root" } => "Privileged",
    { Address: { Country: "US" } } => "US User",
    _ => "Regular"
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
    _ => "Other"
};
```

### Slice Patterns (C# 12+)
```csharp
// Работает с Span, массивами, List
var slice = numbers[1..4]; // 2, 3, 4
var fromStart = numbers[..3]; // 1, 2, 3
var toEnd = numbers[2..]; // 3, 4, 5

// В pattern matching
var isPrefix = numbers is [1, 2, ..]; // true
```

## 📝 Records — неизменяемые данные

### Reference Record (class-based)
```csharp
public record User(string Name, string Email, int Age) {
    // Автоматически: конструктор, свойства init, Equals/GetHashCode, ToString, Deconstruct
    // Инициализация только через конструктор или object initializer с init
}

// with-expression — копия с изменениями
var user1 = new User("Alex", "alex@test.com", 25);
var user2 = user1 with { Age = 26 }; // Name и Email скопированы
// user1 == user2 -> false (разный Age)
```

### Positional Records — деконструкция
```csharp
public record Point(int X, int Y);

var p = new Point(10, 20);
var (x, y) = p; // деконструкция
Console.WriteLine(p); // Point { X = 10, Y = 20 }
```

### Record Struct (C# 10+) — value type record
```csharp
public readonly record struct Point3D(int X, int Y, int Z);

// Сравнение по значениям, без аллокаций на куче
// with-expression тоже работает
var p1 = new Point3D(1, 2, 3);
var p2 = p1 with { Z = 4 };
```

### Record с методами и наследованием
```csharp
public abstract record Animal(string Name) {
    public virtual string Sound() => "...";
}

public record Dog(string Name, string Breed) : Animal(Name) {
    public override string Sound() => "Woof!";
    public void Fetch() => Console.WriteLine("Fetching!");
}
```

### Equality в Records
```csharp
// По умолчанию — сравнение по ВСЕМ свойствам (value equality)
var r1 = new User("A", "a@b.com", 1);
var r2 = new User("A", "a@b.com", 1);
r1 == r2; // true

// Можно переопределить
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
""",
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

# ----- 24: Language/Runtime Internals -----
LESSONS[24] = {
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
    "content_md": """## 🎯 Что вы узнаете
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

# или в Visual Studio: Debug -> Windows -> Disassembly
# или онлайн: sharplab.io
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
<ProjectReference Include="..\\MyGenerator\\MyGenerator.csproj" 
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
""",
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

# ----- 25: Extension Members, Operators, Indexers -----
LESSONS[25] = {
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
    "content_md": """## 🎯 Что вы узнаете
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
""",
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

# ----- 26: GC, Generations, Finalizers, IDisposable -----
LESSONS[26] = {
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
    "content_md": """## 🎯 Что вы узнаете
- Поколения GC: Gen 0, 1, 2 — эфимерные и долгоживущие
- Large Object Heap (LOH) и Pinned Object Heap (POH)
- Режимы GC: Workstation/Server, Concurrent/Background
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
""",
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

# ----- 27: Networking, HTTP, gRPC -----
LESSONS[27] = {
    "title": "Урок 27: Сетевое программирование — HttpClient, Sockets, gRPC, WebSockets, SignalR",
    "slug": "lesson-27",
    "short_description": "HttpClient, IHttpClientFactory, Polly, Sockets, Named Pipes, gRPC, WebSockets, SignalR, Rate Limiting",
    "goals": [
        "Правильно использовать HttpClient через IHttpClientFactory",
        "Настраивать Polly политики: Retry, Circuit Breaker, Timeout, Bulkhead",
        "Работать с гRPC: protobuf, code-first, contract-first, streaming",
        "Использовать WebSockets и SignalR для real-time",
        "Применять Rate Limiting и throttling"
    ],
    "content_md": """## 🎯 Что вы узнаете
- HttpClient: пулинг соединений, IHttpClientFactory, жизненный цикл
- Polly: Retry, Circuit Breaker, Timeout, Bulkhead, Fallback
- gRPC: protobuf, unary/streaming, interceptors, code-first
- WebSockets: System.Net.WebSockets, SignalR
- Rate Limiting: Fixed Window, Sliding Window, Token Bucket
- Named Pipes, Unix Domain Sockets для IPC

## 🌐 HttpClient — правильное использование

### Проблема: HttpClient exhaustion
```csharp
// НЕ ДЕЛАЙТЕ ТАК — утечка сокетов (TIME_WAIT)
using var client = new HttpClient();
var result = await client.GetStringAsync(url);
```

### Правильно: IHttpClientFactory
```csharp
// Program.cs
builder.Services.AddHttpClient<GitHubClient>(client => {
    client.BaseAddress = new Uri("https://api.github.com/");
    client.DefaultRequestHeaders.UserAgent.ParseAdd("MyApp/1.0");
    client.Timeout = TimeSpan.FromSeconds(30);
});

// Использование
public class GitHubClient {
    private readonly HttpClient _client;
    public GitHubClient(HttpClient client) => _client = client;
    
    public async Task<User> GetUserAsync(string login) {
        var response = await _client.GetAsync($"users/{login}");
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<User>();
    }
}
```

### Типы регистрации
```csharp
// Typed Client (рекомендуется)
services.AddHttpClient<GitHubClient>();

// Named Client
services.AddHttpClient("github", c => c.BaseAddress = new Uri("https://api.github.com/"));

// В коде
var client = factory.CreateClient("github");

// Default Client
services.AddHttpClient(); // без имени
var client = factory.CreateClient(); // использует default
```

### HttpClientHandler настройка
```csharp
services.AddHttpClient<ApiClient>().ConfigurePrimaryHttpMessageHandler(() => 
    new HttpClientHandler {
        AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate,
        UseCookies = false,
        AllowAutoRedirect = true,
        MaxConnectionsPerServer = 100, // .NET 6+
        PooledConnectionLifetime = TimeSpan.FromMinutes(5), // DNS refresh
        ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true // только для dev!
    });
```

## 🛡 Polly — Resilience Policies

### Установка
```bash
dotnet add package Microsoft.Extensions.Http.Polly
dotnet add package Polly.Extensions.Http
```

### Основные политики
```csharp
services.AddHttpClient<ApiClient>()
    .AddPolicyHandler(GetRetryPolicy())
    .AddPolicyHandler(GetCircuitBreakerPolicy())
    .AddPolicyHandler(GetTimeoutPolicy());

// Retry с экспоненциальным backoff + jitter
static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy() 
    => HttpPolicyExtensions
        .HandleTransientHttpError() // 5xx, 408, HttpRequestException
        .OrResult(r => r.StatusCode == System.Net.HttpStatusCode.TooManyRequests) // 429
        .WaitAndRetryAsync(
            retryCount: 3,
            sleepDurationProvider: attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt)) 
                + TimeSpan.FromMilliseconds(Random.Shared.Next(0, 100)), // jitter
            onRetry: (outcome, timespan, attempt, ctx) => {
                Log.Warning("Retry {Attempt} after {Delay}: {Reason}", attempt, timespan, outcome.Exception?.Message ?? outcome.Result?.StatusCode.ToString());
            });

// Circuit Breaker — останавливает вызовы при множественных ошибках
static IAsyncPolicy<HttpResponseMessage> GetCircuitBreakerPolicy()
    => HttpPolicyExtensions
        .HandleTransientHttpError()
        .CircuitBreakerAsync(
            handledEventsAllowedBeforeBreaking: 5,
            durationOfBreak: TimeSpan.FromSeconds(30),
            onBreak: (ex, ts) => Log.Error("Circuit opened for {Duration}", ts),
            onReset: () => Log.Information("Circuit closed"),
            onHalfOpen: () => Log.Information("Circuit half-open"));

// Timeout
static IAsyncPolicy<HttpResponseMessage> GetTimeoutPolicy()
    => Policy.TimeoutAsync<HttpResponseMessage>(TimeSpan.FromSeconds(10));

// Bulkhead — ограничение параллелизма
static IAsyncPolicy<HttpResponseMessage> GetBulkheadPolicy()
    => Policy.BulkheadAsync<HttpResponseMessage>(
        maxParallelization: 10,
        maxQueuingActions: 20,
        onBulkheadRejectedAsync: ctx => {
            Log.Warning("Bulkhead rejected");
            return Task.CompletedTask;
        });

// Fallback — возврат дефолтного значения при ошибке
static IAsyncPolicy<HttpResponseMessage> GetFallbackPolicy()
    => Policy<HttpResponseMessage>
        .Handle<HttpRequestException>()
        .FallbackAsync(new HttpResponseMessage(HttpStatusCode.ServiceUnavailable) {
            Content = new StringContent("{\"error\":\"Service unavailable\"}", Encoding.UTF8, "application/json")
        });
```

### PolicyWrap — комбинирование
```csharp
// Порядок важен: Timeout → Bulkhead → CircuitBreaker → Retry → Fallback
var wrapper = Policy.WrapAsync(
    GetTimeoutPolicy(),
    GetBulkheadPolicy(),
    GetCircuitBreakerPolicy(),
    GetRetryPolicy(),
    GetFallbackPolicy()
);

services.AddHttpClient<ApiClient>().AddPolicyHandler(wrapper);
```

## 🔧 gRPC — высокопроизводительный RPC

### Protobuf определение
```protobuf
// greet.proto
syntax = "proto3";

package Greet;

service Greeter {
    rpc SayHello (HelloRequest) returns (HelloReply);           // Unary
    rpc SayHellos (HelloRequest) returns (stream HelloReply);   // Server streaming
    rpc SayHelloStream (stream HelloRequest) returns (HelloReply); // Client streaming
    rpc SayHelloBidi (stream HelloRequest) returns (stream HelloReply); // Bidi streaming
}

message HelloRequest {
    string name = 1;
}

message HelloReply {
    string message = 1;
}
```

### Server (ASP.NET Core)
```csharp
// Program.cs
builder.Services.AddGrpc();

app.MapGrpcService<GreeterService>();

// Service
public class GreeterService : Greeter.GreeterBase {
    public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context) {
        return Task.FromResult(new HelloReply { Message = $"Hello, {request.Name}!" });
    }
    
    // Server streaming
    public override async Task SayHellos(HelloRequest request, IServerStreamWriter<HelloReply> responseStream, ServerCallContext context) {
        for (int i = 0; i < 5; i++) {
            await responseStream.WriteAsync(new HelloReply { Message = $"Hello {i}, {request.Name}!" });
            await Task.Delay(100);
        }
    }
}
```

### Client
```csharp
var channel = GrpcChannel.ForAddress("https://localhost:5001");
var client = new Greeter.GreeterClient(channel);

// Unary
var reply = await client.SayHelloAsync(new HelloRequest { Name = "Alex" });

// Server streaming
using var call = client.SayHellos(new HelloRequest { Name = "Alex" });
await foreach (var msg in call.ResponseStream.ReadAllAsync()) {
    Console.WriteLine(msg.Message);
}

// Client streaming
using var call = client.SayHelloStream();
await call.RequestStream.WriteAsync(new HelloRequest { Name = "A" });
await call.RequestStream.WriteAsync(new HelloRequest { Name = "B" });
await call.RequestStream.CompleteAsync();
var reply = await call.ResponseAsync;

// Bidi streaming
using var call = client.SayHelloBidi();
var writeTask = WriteRequests(call.RequestStream);
var readTask = ReadResponses(call.ResponseStream);
await Task.WhenAll(writeTask, readTask);
```

### Code-first gRPC (без .proto)
```csharp
// .NET 7+: атрибуты вместо .proto
[ProtoContract]
public class HelloRequest {
    [ProtoMember(1)] public string Name { get; set; }
}

[ProtoContract]
public class HelloReply {
    [ProtoMember(1)] public string Message { get; set; }
}

[GrpcService]
public interface IGreeter {
    Task<HelloReply> SayHello(HelloRequest request);
}

// Реализация
public class GreeterService : IGreeter { ... }

// Регистрация
builder.Services.AddCodeFirstGrpc(options => {
    options.ResponseCompressionLevel = System.IO.Compression.CompressionLevel.Optimal;
});
```

### Interceptors — cross-cutting
```csharp
public class LoggingInterceptor : Interceptor {
    private readonly ILogger<LoggingInterceptor> _logger;
    
    public override async Task<TResponse> UnaryServerHandler<TRequest, TResponse>(
        TRequest request, ServerCallContext context, UnaryServerMethod<TRequest, TResponse> continuation) {
        _logger.LogInformation("gRPC {Method} called", context.Method);
        var stopwatch = Stopwatch.StartNew();
        try {
            return await continuation(request, context);
        } finally {
            stopwatch.Stop();
            _logger.LogInformation("gRPC {Method} completed in {Elapsed}ms", context.Method, stopwatch.ElapsedMilliseconds);
        }
    }
}

// Регистрация
builder.Services.AddGrpc(options => {
    options.Interceptors.Add<LoggingInterceptor>();
});
```

## 🔌 WebSockets и SignalR

### Низкоуровневые WebSockets
```csharp
// Server (ASP.NET Core)
app.UseWebSockets();

app.Map("/ws", async context => {
    if (!context.WebSockets.IsWebSocketRequest) {
        context.Response.StatusCode = 400;
        return;
    }
    
    using var ws = await context.WebSockets.AcceptWebSocketAsync();
    var buffer = new byte[4096];
    
    while (ws.State == WebSocketState.Open) {
        var result = await ws.ReceiveAsync(buffer, CancellationToken.None);
        if (result.MessageType == WebSocketMessageType.Close) {
            await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closed", CancellationToken.None);
            break;
        }
        
        // Echo
        await ws.SendAsync(buffer.AsMemory(0, result.Count), result.MessageType, result.EndOfMessage, CancellationToken.None);
    }
});

// Client
using var ws = new ClientWebSocket();
await ws.ConnectAsync(new Uri("wss://localhost/ws"), CancellationToken.None);
await ws.SendAsync(Encoding.UTF8.GetBytes("Hello"), WebSocketMessageType.Text, true, CancellationToken.None);
var buffer = new byte[4096];
var result = await ws.ReceiveAsync(buffer, CancellationToken.None);
```

### SignalR — абстракция над WebSockets
```bash
dotnet add package Microsoft.AspNetCore.SignalR
dotnet add package Microsoft.AspNetCore.SignalR.Client
```

```csharp
// Hub
public class ChatHub : Hub {
    public async Task SendMessage(string user, string message) {
        await Clients.All.SendAsync("ReceiveMessage", user, message);
    }
    
    public async Task SendToGroup(string group, string message) {
        await Clients.Group(group).SendAsync("ReceiveMessage", Context.UserIdentifier, message);
    }
    
    public override async Task OnConnectedAsync() {
        await Groups.AddToGroupAsync(Context.ConnectionId, "default");
        await base.OnConnectedAsync();
    }
}

// Регистрация
builder.Services.AddSignalR();
app.MapHub<ChatHub>("/chathub");

// Client (JS или C#)
var connection = new HubConnectionBuilder()
    .WithUrl("https://localhost/chathub")
    .WithAutomaticReconnect()
    .Build();

connection.On<string, string>("ReceiveMessage", (user, msg) => Console.WriteLine($"{user}: {msg}"));

await connection.StartAsync();
await connection.InvokeAsync("SendMessage", "Alex", "Hello SignalR!");
```

## 🚦 Rate Limiting — ограничение запросов

### Встроенный Rate Limiter (.NET 7+)
```csharp
builder.Services.AddRateLimiter(options => {
    // Fixed Window — простое окно
    options.AddFixedWindowLimiter("fixed", opts => {
        opts.PermitLimit = 100;
        opts.Window = TimeSpan.FromMinutes(1);
        opts.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        opts.QueueLimit = 10;
    });
    
    // Sliding Window — скользящее окно (гладче)
    options.AddSlidingWindowLimiter("sliding", opts => {
        opts.PermitLimit = 100;
        opts.Window = TimeSpan.FromMinutes(1);
        opts.SegmentsPerWindow = 10;
        opts.QueueLimit = 10;
    });
    
    // Token Bucket — для burst трафика
    options.AddTokenBucketLimiter("token", opts => {
        opts.TokenLimit = 100;
        opts.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        opts.QueueLimit = 10;
        opts.ReplenishmentPeriod = TimeSpan.FromSeconds(10);
        opts.TokensPerPeriod = 20;
    });
    
    // Concurrency — ограничение одновременных запросов
    options.AddConcurrencyLimiter("concurrency", opts => {
        opts.PermitLimit = 10;
        opts.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        opts.QueueLimit = 5;
    });
    
    // Глобальная политика отказа
    options.OnRejected = (context, token) => {
        context.HttpContext.Response.StatusCode = StatusCodes.Status429TooManyRequests;
        return ValueTask.CompletedTask;
    };
});

// Использование
app.UseRateLimiter();

app.MapGet("/api/data", () => "OK").RequireRateLimiting("sliding");

// Или через атрибут
[EnableRateLimiting("fixed")]
public class MyController : ControllerBase { }
```

### Распределенное Rate Limiting (Redis)
```csharp
// Используйте DistributedRateLimiter из Microsoft.Extensions.RateLimiting.Redis
// или реализуйте через Redis Lua скрипты для атомарности
```

## 📡 IPC: Named Pipes, Unix Domain Sockets

### Named Pipes (Windows/Linux)
```csharp
// Server
var server = new NamedPipeServerStream("mypipe", PipeDirection.InOut, 4);
await server.WaitForConnectionAsync();
using var reader = new StreamReader(server);
using var writer = new StreamWriter(server) { AutoFlush = true };

var msg = await reader.ReadLineAsync();
await writer.WriteLineAsync($"Echo: {msg}");

// Client
var client = new NamedPipeClientStream(".", "mypipe", PipeDirection.InOut);
await client.ConnectAsync(1000);
using var reader = new StreamReader(client);
using var writer = new StreamWriter(client) { AutoFlush = true };

await writer.WriteLineAsync("Hello");
var response = await reader.ReadLineAsync();
```

### Unix Domain Sockets (Linux, высокопроизводительный IPC)
```csharp
// .NET 6+
var listener = new UnixDomainSocketEndPoint("/tmp/mysocket");
var server = new Socket(AddressFamily.Unix, SocketType.Stream, ProtocolType.Unspecified);
server.Bind(listener);
server.Listen(10);

var client = await server.AcceptAsync();
// общение через SendAsync/ReceiveAsync
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| `new HttpClient()` в методе | Socket exhaustion, TIME_WAIT | `IHttpClientFactory`, `AddHttpClient` |
| Отсутствие Timeout | Зависшие запросы вечно | Всегда `Timeout` в HttpClient или Polly Timeout |
| Retry без jitter | Thundering herd при восстановлении | Добавляйте `Random.Next()` к задержке |
| Circuit Breaker не сбрасывается | Сервис не восстанавливается | Проверьте `onReset`, логируйте состояние |
| gRPC без `Grpc.Net.Client` | Не работает в браузере/HTTP/1.1 | Используйте `Grpc.Net.Client` + `Grpc.AspNetCore` |
| WebSockets без отмены | Утечки при разрыве | Всегда передавайте `CancellationToken` |
| Rate Limiter без `QueueLimit` | Неограниченная очередь = OOM | Всегда ставьте `QueueLimit` |

## 🛠 Практика

1. Настройте `IHttpClientFactory` с Typed Client, Polly Retry (3 раза, экспоненциальный backoff + jitter), Circuit Breaker, Timeout.
2. Создайте gRPC сервис с unary, server streaming, client streaming, bidi методами. Протестируйте клиент.
3. Реализуйте SignalR Hub для чата с комнатами (Groups). Напишите C# клиент.
4. Настройте Rate Limiting: Sliding Window 100 req/min, Token Bucket для burst.
5. Напишите Named Pipe сервер и клиент для IPC между двумя процессами.

## 📌 Кратко

- **HttpClient** — только через `IHttpClientFactory` (Typed/Named/Default), пулинг, DNS refresh
- **Polly** — Retry (backoff + jitter), Circuit Breaker, Timeout, Bulkhead, Fallback, PolicyWrap
- **gRPC** — protobuf, 4 типа RPC, interceptors, code-first (.NET 7+)
- **WebSockets/SignalR** — SignalR проще, авто-переподключение, Groups
- **Rate Limiting** — Fixed/Sliding Window, Token Bucket, Concurrency, всегда QueueLimit
- **IPC** — Named Pipes (cross-platform), Unix Domain Sockets (Linux, fast)

## 🔗 Ссылки

- HttpClient: https://learn.microsoft.com/dotnet/architecture/microservices/implement-resilient-applications/use-httpclientfactory-to-implement-resilient-http-requests
- Polly: https://github.com/App-vNext/Polly
- gRPC: https://learn.microsoft.com/aspnet/core/grpc/
- SignalR: https://learn.microsoft.com/aspnet/core/signalr/
- Rate Limiting: https://learn.microsoft.com/dotnet/core/extensions/rate-limiting
""",
    "practice_tasks": [
        "Настройте `IHttpClientFactory` с Typed Client, Polly Retry (3 раза, экспоненциальный backoff + jitter), Circuit Breaker, Timeout.",
        "Создайте gRPC сервис с unary, server streaming, client streaming, bidi методами. Протестируйте клиент.",
        "Реализуйте SignalR Hub для чата с комнатами (Groups). Напишите C# клиент.",
        "Настройте Rate Limiting: Sliding Window 100 req/min, Token Bucket для burst.",
        "Напишите Named Pipe сервер и клиент для IPC между двумя процессами."
    ],
    "common_errors": [
        {"mistake": "`new HttpClient()` в методе", "correct": "`IHttpClientFactory`, `AddHttpClient`"},
        {"mistake": "Отсутствие Timeout", "correct": "Всегда `Timeout` в HttpClient или Polly Timeout"},
        {"mistake": "Retry без jitter", "correct": "Добавляйте `Random.Next()` к задержке"},
        {"mistake": "Circuit Breaker не сбрасывается", "correct": "Проверьте `onReset`, логируйте состояние"},
        {"mistake": "gRPC без `Grpc.Net.Client`", "correct": "Используйте `Grpc.Net.Client` + `Grpc.AspNetCore`"},
        {"mistake": "WebSockets без отмены", "correct": "Всегда передавайте `CancellationToken`"},
        {"mistake": "Rate Limiter без `QueueLimit`", "correct": "Всегда ставьте `QueueLimit`"}
    ],
    "resources": [
        "HttpClient: https://learn.microsoft.com/dotnet/architecture/microservices/implement-resilient-applications/use-httpclientfactory-to-implement-resilient-http-requests",
        "Polly: https://github.com/App-vNext/Polly",
        "gRPC: https://learn.microsoft.com/aspnet/core/grpc/",
        "SignalR: https://learn.microsoft.com/aspnet/core/signalr/",
        "Rate Limiting: https://learn.microsoft.com/dotnet/core/extensions/rate-limiting"
    ],
    "key_takeaways": [
        "HttpClient — только через IHttpClientFactory (Typed/Named/Default), пулинг, DNS refresh",
        "Polly — Retry (backoff + jitter), Circuit Breaker, Timeout, Bulkhead, Fallback, PolicyWrap",
        "gRPC — protobuf, 4 типа RPC, interceptors, code-first (.NET 7+)",
        "WebSockets/SignalR — SignalR проще, авто-переподключение, Groups",
        "Rate Limiting — Fixed/Sliding Window, Token Bucket, Concurrency, всегда QueueLimit",
        "IPC — Named Pipes (cross-platform), Unix Domain Sockets (Linux, fast)"
    ],
    "estimated_minutes": 50,
    "language_slug": "csharp",
    "lesson_order": 27,
    "name_en": "Lesson: Networking, HTTP, gRPC",
    "short_description_en": "HttpClient, IHttpClientFactory, Polly, gRPC, WebSockets, SignalR, Rate Limiting"
}

# ----- 28: Security — Auth, AuthZ, Crypto -----
LESSONS[28] = {
    "title": "Урок 28: Безопасность — Authentication, Authorization, JWT, OAuth2, OpenID Connect, Crypto, Data Protection",
    "slug": "lesson-28",
    "short_description": "ASP.NET Core Identity, JWT, OAuth2/OIDC, Policies, Claims, Crypto, Data Protection API, Anti-forgery, Rate Limiting",
    "goals": [
        "Настроить аутентификацию: Cookie, JWT, OAuth2, OpenID Connect, Azure AD, IdentityServer",
        "Реализовать авторизацию: Policies, Requirements, Handlers, Claims-based, Resource-based",
        "Работать с криптографией: AES, RSA, HMAC, Hashing, PBKDF2, Data Protection API",
        "Защитить от CSRF, XSS, Clickjacking, Open Redirect",
        "Применять Rate Limiting, IP filtering, Security Headers"
    ],
    "content_md": """## 🎯 Что вы узнаете
- Аутентификация: Cookie, JWT Bearer, OAuth2, OpenID Connect, Azure AD, IdentityServer
- Авторизация: `[Authorize]`, Policies, Requirements/Handlers, Claims, Resource-based
- Криптография: `Aes`, `RSA`, `HMACSHA256`, `Rfc2898DeriveBytes` (PBKDF2), `Argon2`
- Data Protection API: защита данных, ключи, purpose chains
- Безопасность веба: CSRF, XSS, CSP, HSTS, Anti-forgery, Secure Headers

## 🔐 Аутентификация в ASP.NET Core

### Cookie Authentication (традиционная)
```csharp
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options => {
        options.LoginPath = "/Account/Login";
        options.LogoutPath = "/Account/Logout";
        options.AccessDeniedPath = "/Account/AccessDenied";
        options.ExpireTimeSpan = TimeSpan.FromHours(8);
        options.SlidingExpiration = true;
        options.Cookie.HttpOnly = true;
        options.Cookie.SecurePolicy = CookieSecurePolicy.Always; // только HTTPS
        options.Cookie.SameSite = SameSiteMode.Strict; // CSRF защита
    });
```

### JWT Bearer (Stateless, для API)
```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => {
        options.TokenValidationParameters = new TokenValidationParameters {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = "myapp",
            ValidAudience = "myapp-client",
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes("super-secret-key-min-256-bits!")),
            ClockSkew = TimeSpan.FromMinutes(1)
        };
        
        // Для SignalR / WebSockets — чтение токена из query string
        options.Events = new JwtBearerEvents {
            OnMessageReceived = context => {
                var accessToken = context.Request.Query["access_token"];
                var path = context.HttpContext.Request.Path;
                if (!string.IsNullOrEmpty(accessToken) && path.StartsWithSegments("/hubs")) {
                    context.Token = accessToken;
                }
                return Task.CompletedTask;
            }
        };
    });
```

### Генерация JWT
```csharp
public class JwtTokenService {
    private readonly IConfiguration _config;
    
    public string GenerateToken(User user, IEnumerable<string> roles) {
        var claims = new List<Claim> {
            new(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
            new(JwtRegisteredClaimNames.Email, user.Email),
            new(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new(ClaimTypes.Name, user.UserName)
        };
        claims.AddRange(roles.Select(r => new Claim(ClaimTypes.Role, r)));
        
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_config["Jwt:Key"]!));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);
        
        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddHours(1),
            signingCredentials: creds
        );
        
        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
```

### OAuth2 / OpenID Connect (Google, GitHub, Azure AD)
```csharp
builder.Services.AddAuthentication()
    .AddCookie()
    .AddGoogle(options => {
        options.ClientId = config["Google:ClientId"];
        options.ClientSecret = config["Google:ClientSecret"];
        options.Scope.Add("email");
        options.Scope.Add("profile");
    })
    .AddMicrosoftIdentityWebApp(config.GetSection("AzureAd")); // Azure AD

// Или через IdentityServer / Duende
builder.Services.AddAuthentication("Bearer")
    .AddIdentityServerAuthentication("Bearer", options => {
        options.Authority = "https://identityserver";
        options.ApiName = "myapi";
    });
```

### ASP.NET Core Identity (User Management)
```csharp
builder.Services.AddDbContext<AppDbContext>(opt => opt.UseNpgsql(connStr));
builder.Services.AddIdentity<User, Role>(options => {
    options.Password.RequireDigit = true;
    options.Password.RequiredLength = 8;
    options.Password.RequireNonAlphanumeric = true;
    options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);
    options.Lockout.MaxFailedAccessAttempts = 5;
    options.User.RequireUniqueEmail = true;
    options.SignIn.RequireConfirmedEmail = true;
})
.AddEntityFrameworkStores<AppDbContext>()
.AddDefaultTokenProviders(); // Email confirmation, password reset

// Использование
public class AccountController : ControllerBase {
    private readonly UserManager<User> _userManager;
    private readonly SignInManager<User> _signInManager;
    
    [HttpPost("register")]
    public async Task<IActionResult> Register(RegisterDto dto) {
        var user = new User { UserName = dto.Email, Email = dto.Email };
        var result = await _userManager.CreateAsync(user, dto.Password);
        if (!result.Succeeded) return BadRequest(result.Errors);
        
        await _userManager.AddToRoleAsync(user, "User");
        // Send confirmation email...
        return Ok();
    }
    
    [HttpPost("login")]
    public async Task<IActionResult> Login(LoginDto dto) {
        var result = await _signInManager.PasswordSignInAsync(dto.Email, dto.Password, dto.RememberMe, lockoutOnFailure: true);
        if (result.Succeeded) return Ok();
        if (result.IsLockedOut) return StatusCode(429, "Account locked");
        return Unauthorized();
    }
}
```

## 🛡 Авторизация — Policies и Requirements

### Простая авторизация
```csharp
[Authorize] // Требует аутентификацию
[Authorize(Roles = "Admin,Manager")] // Роли
[Authorize(Policy = "RequireAdminRole")] // Политика
```

### Политики (Policies)
```csharp
builder.Services.AddAuthorization(options => {
    // Простая политика по роли
    options.AddPolicy("RequireAdminRole", policy => 
        policy.RequireRole("Admin"));
    
    // По claim
    options.AddPolicy("CanDeleteUsers", policy =>
        policy.RequireClaim("permission", "users.delete"));
    
    // Несколько требований (И)
    options.AddPolicy("SeniorAdmin", policy =>
        policy.RequireRole("Admin")
              .RequireClaim("department", "IT")
              .RequireAssertion(ctx => ctx.User.HasClaim(c => c.Type == "security_level" && int.Parse(c.Value) >= 5)));
    
    // Кастомное требование
    options.AddPolicy("MinimumAge", policy =>
        policy.Requirements.Add(new MinimumAgeRequirement(18)));
});

// Регистрация обработчика
builder.Services.AddScoped<IAuthorizationHandler, MinimumAgeHandler>();
```

### Кастомные Requirements и Handlers
```csharp
// Требование
public class MinimumAgeRequirement : IAuthorizationRequirement {
    public int MinimumAge { get; }
    public MinimumAgeRequirement(int minimumAge) => MinimumAge = minimumAge;
}

// Обработчик
public class MinimumAgeHandler : AuthorizationHandler<MinimumAgeRequirement> {
    protected override Task HandleRequirementAsync(AuthorizationHandlerContext context, MinimumAgeRequirement requirement) {
        var dobClaim = context.User.FindFirst(ClaimTypes.DateOfBirth);
        if (dobClaim != null && DateTime.TryParse(dobClaim.Value, out var dob)) {
            var age = DateTime.Today.Year - dob.Year;
            if (dob > DateTime.Today.AddYears(-age)) age--;
            if (age >= requirement.MinimumAge) context.Succeed(requirement);
        }
        return Task.CompletedTask;
    }
}

// Resource-based authorization (на уровне объекта)
public class DocumentAuthorizationHandler : AuthorizationHandler<OperationAuthorizationRequirement, Document> {
    protected override Task HandleRequirementAsync(AuthorizationHandlerContext context, OperationAuthorizationRequirement requirement, Document resource) {
        if (requirement.Name == "Read" && resource.IsPublic) context.Succeed(requirement);
        if (requirement.Name == "Edit" && resource.OwnerId == GetUserId(context.User)) context.Succeed(requirement);
        if (requirement.Name == "Delete" && context.User.IsInRole("Admin")) context.Succeed(requirement);
        return Task.CompletedTask;
    }
}

// Использование
[HttpGet("{id}")]
public async Task<IActionResult> GetDocument(int id) {
    var doc = await _repo.GetAsync(id);
    var authResult = await _authorizationService.AuthorizeAsync(User, doc, "Read");
    if (!authResult.Succeeded) return Forbid();
    return Ok(doc);
}
```

## 🔒 Криптография — правильное использование

### Симметричное шифрование (AES-GCM) — .NET 6+
```csharp
// AES-GCM — аутентифицированное шифрование (confidentiality + integrity)
public static class AesGcmHelper {
    public static (byte[] ciphertext, byte[] nonce, byte[] tag) Encrypt(byte[] plaintext, byte[] key, byte[]? associatedData = null) {
        var nonce = RandomNumberGenerator.GetBytes(12); // 96-bit nonce для GCM
        var tag = new byte[16];
        var ciphertext = new byte[plaintext.Length];
        
        using var aes = new AesGcm(key);
        aes.Encrypt(nonce, plaintext, ciphertext, tag, associatedData);
        
        return (ciphertext, nonce, tag);
    }
    
    public static byte[] Decrypt(byte[] ciphertext, byte[] nonce, byte[] tag, byte[] key, byte[]? associatedData = null) {
        var plaintext = new byte[ciphertext.Length];
        using var aes = new AesGcm(key);
        aes.Decrypt(nonce, ciphertext, tag, plaintext, associatedData);
        return plaintext;
    }
}

// Использование
var key = RandomNumberGenerator.GetBytes(32); // 256-bit key
var (cipher, nonce, tag) = AesGcmHelper.Encrypt(Encoding.UTF8.GetBytes("secret"), key);
var plain = AesGcmHelper.Decrypt(cipher, nonce, tag, key);
```

### Асимметричное шифрование (RSA)
```csharp
// Генерация ключей
using var rsa = RSA.Create(2048);
var publicKey = rsa.ExportSubjectPublicKeyInfoPem();
var privateKey = rsa.ExportPkcs8PrivateKeyPem();

// Шифрование (малые данные, обычно hybrid: RSA для ключа + AES для данных)
public static byte[] EncryptRsa(byte[] data, string publicKeyPem) {
    using var rsa = RSA.Create();
    rsa.ImportFromPem(publicKeyPem);
    return rsa.Encrypt(data, RSAEncryptionPadding.OaepSHA256);
}

public static byte[] DecryptRsa(byte[] data, string privateKeyPem) {
    using var rsa = RSA.Create();
    rsa.ImportFromPem(privateKeyPem);
    return rsa.Decrypt(data, RSAEncryptionPadding.OaepSHA256);
}
```

### Подписание и верификация (RSA/ECDSA)
```csharp
// Подписание
public static byte[] SignData(byte[] data, string privateKeyPem) {
    using var rsa = RSA.Create();
    rsa.ImportFromPem(privateKeyPem);
    return rsa.SignData(data, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
}

// Верификация
public static bool VerifySignature(byte[] data, byte[] signature, string publicKeyPem) {
    using var rsa = RSA.Create();
    rsa.ImportFromPem(publicKeyPem);
    return rsa.VerifyData(data, signature, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
}
```

### Хеширование паролей — PBKDF2 / Argon2
```csharp
// .NET встроенный PBKDF2 (ASP.NET Core Identity использует это)
public static string HashPassword(string password) {
    // Identity использует PBKDF2 с HMACSHA256, 100000 итераций
    return new PasswordHasher<object>().HashPassword(null!, password);
}

public static bool VerifyPassword(string hashed, string password) {
    var result = new PasswordHasher<object>().VerifyHashedPassword(null!, hashed, password);
    return result == PasswordVerificationResult.Success;
}

// Argon2 (рекомендуется для новых проектов) — требует пакет Konscious.Security.Cryptography.Argon2
// dotnet add package Konscious.Security.Cryptography.Argon2
```

### HMAC — целостность и аутентичность
```csharp
public static string ComputeHmacSha256(string data, string key) {
    var keyBytes = Encoding.UTF8.GetBytes(key);
    var dataBytes = Encoding.UTF8.GetBytes(data);
    
    using var hmac = new HMACSHA256(keyBytes);
    var hash = hmac.ComputeHash(dataBytes);
    return Convert.ToBase64String(hash);
}

public static bool VerifyHmac(string data, string key, string expectedHmac) {
    var actual = ComputeHmacSha256(data, key);
    // Constant-time comparison!
    return CryptographicOperations.FixedTimeEquals(
        Encoding.UTF8.GetBytes(actual), 
        Encoding.UTF8.GetBytes(expectedHmac));
}
```

## 🛡 Data Protection API — защита данных в ASP.NET Core

### Настройка
```csharp
builder.Services.AddDataProtection()
    .PersistKeysToFileSystem(new DirectoryInfo("/app/keys")) // или Azure Blob, Redis
    .SetApplicationName("MyApp")
    .SetDefaultKeyLifetime(TimeSpan.FromDays(90))
    .ProtectKeysWithDpapi(); // Windows: DPAPI, Linux: нет (или Azure Key Vault)
```

### Использование
```csharp
public class TokenProtector {
    private readonly IDataProtector _protector;
    
    public TokenProtector(IDataProtectionProvider provider) {
        _protector = provider.CreateProtector("MyApp.Tokens.v1"); // purpose chain
    }
    
    public string Protect(string data) => _protector.Protect(data);
    public string Unprotect(string protectedData) => _protector.Unprotect(protectedData);
    
    // С ограничением по времени
    public string ProtectWithExpiry(string data, TimeSpan lifetime) 
        => _protector.ToTimeLimitedDataProtector().Protect(data, lifetime);
    
    public string UnprotectWithExpiry(string protectedData) 
        => _protector.ToTimeLimitedDataProtector().Unprotect(protectedData);
}
```

**Применения**: CSRF токены, password reset токены, email confirmation, шифрование query string параметров.

## 🌐 Веб-безопасность — заголовки и защита

### Security Headers Middleware
```csharp
app.Use(async (context, next) => {
    context.Response.Headers["X-Content-Type-Options"] = "nosniff";
    context.Response.Headers["X-Frame-Options"] = "DENY";
    context.Response.Headers["X-XSS-Protection"] = "1; mode=block";
    context.Response.Headers["Referrer-Policy"] = "strict-origin-when-cross-origin";
    context.Response.Headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()";
    context.Response.Headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'";
    context.Response.Headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload";
    await next();
});
```

### Anti-forgery (CSRF защита)
```csharp
// Автоматически для Razor Pages / MVC с Form
builder.Services.AddAntiforgery(options => {
    options.HeaderName = "X-CSRF-TOKEN";
    options.Cookie.Name = "__RequestVerificationToken";
    options.Cookie.HttpOnly = true;
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
    options.Cookie.SameSite = SameSiteMode.Strict;
});

// В контроллере
[HttpPost]
[ValidateAntiForgeryToken] // или [AutoValidateAntiforgeryToken] для всех unsafe методов
public IActionResult Submit(FormModel model) { ... }

// Для SPA (React/Vue) — чтение токена из cookie и отправка в заголовке
```

### Защита от Open Redirect
```csharp
[HttpGet("login")]
public IActionResult Login(string returnUrl) {
    if (!Url.IsLocalUrl(returnUrl)) returnUrl = "/"; // Только локальные URL!
    return View(new LoginViewModel { ReturnUrl = returnUrl });
}
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Хранение паролей в открытом виде | Утечка → компромисс всех аккаунтов | Всегда `PasswordHasher` / Argon2 |
| Секретный ключ JWT в коде / Git | Компрометация токенов | User Secrets / Key Vault / Environment Variables |
| Отсутствие `ValidateLifetime` в JWT | Токены никогда не истекают | Всегда `ValidateLifetime = true`, `ClockSkew` минимальный |
| `SameSite=Lax` для auth cookie | CSRF уязвимость | `SameSite=Strict` или `Lax` + Anti-forgery |
| Отсутствие CSP | XSS уязвимости | Настройте `Content-Security-Policy` |
| Ручная криптография (AES без GCM) | Нет integrity, уязвимости padding oracle | Используйте `AesGcm` / `ChaCha20Poly1305` |
| `FixedTimeEquals` не используется | Timing attacks на HMAC/токены | Всегда `CryptographicOperations.FixedTimeEquals` |

## 🛠 Практика

1. Настройте JWT аутентификацию с Refresh Tokens (хранить в HttpOnly cookie, access token в памяти).
2. Реализуйте Policy-based авторизацию: `CanEditDocument` с Resource-based handler.
3. Зашифруйте чувствительные данные (PII) через Data Protection API с purpose chain.
4. Настройте Security Headers middleware: CSP, HSTS, X-Frame-Options, Permissions-Policy.
5. Реализуйте HMAC подпись для вебхуков (проверка `X-Signature` заголовка).

## 📌 Кратко

- **AuthN**: Cookie (web), JWT (API), OAuth2/OIDC (Google, Azure AD), Identity (user mgmt)
- **AuthZ**: `[Authorize]`, Policies (Role, Claim, Custom Requirement), Resource-based
- **Crypto**: AES-GCM (симметричное), RSA/OAEP (асимметричное), PBKDF2/Argon2 (пароли), HMAC (integrity)
- **Data Protection** — ключи, purpose chains, time-limited, для токенов/CSRF/PII
- **Web Security**: CSP, HSTS, Anti-forgery, SameSite, Secure Headers, Open Redirect protection

## 🔗 Ссылки

- ASP.NET Core Auth: https://learn.microsoft.com/aspnet/core/security/authentication/
- Authorization: https://learn.microsoft.com/aspnet/core/security/authorization/
- Data Protection: https://learn.microsoft.com/aspnet/core/security/data-protection/
- Cryptography: https://learn.microsoft.com/dotnet/standard/security/
- OWASP: https://owasp.org/www-project-top-ten/
""",
    "practice_tasks": [
        "Настройте JWT аутентификацию с Refresh Tokens (хранить в HttpOnly cookie, access token в памяти).",
        "Реализуйте Policy-based авторизацию: `CanEditDocument` с Resource-based handler.",
        "Зашифруйте чувствительные данные (PII) через Data Protection API с purpose chain.",
        "Настройте Security Headers middleware: CSP, HSTS, X-Frame-Options, Permissions-Policy.",
        "Реализуйте HMAC подпись для вебхуков (проверка `X-Signature` заголовка)."
    ],
    "common_errors": [
        {"mistake": "Хранение паролей в открытом виде", "correct": "Всегда PasswordHasher / Argon2"},
        {"mistake": "Секретный ключ JWT в коде / Git", "correct": "User Secrets / Key Vault / Environment Variables"},
        {"mistake": "Отсутствие `ValidateLifetime` в JWT", "correct": "Всегда `ValidateLifetime = true`, `ClockSkew` минимальный"},
        {"mistake": "`SameSite=Lax` для auth cookie", "correct": "`SameSite=Strict` или `Lax` + Anti-forgery"},
        {"mistake": "Отсутствие CSP", "correct": "Настройте `Content-Security-Policy`"},
        {"mistake": "Ручная криптография (AES без GCM)", "correct": "Используйте `AesGcm` / `ChaCha20Poly1305`"},
        {"mistake": "`FixedTimeEquals` не используется", "correct": "Всегда `CryptographicOperations.FixedTimeEquals`"}
    ],
    "resources": [
        "ASP.NET Core Auth: https://learn.microsoft.com/aspnet/core/security/authentication/",
        "Authorization: https://learn.microsoft.com/aspnet/core/security/authorization/",
        "Data Protection: https://learn.microsoft.com/aspnet/core/security/data-protection/",
        "Cryptography: https://learn.microsoft.com/dotnet/standard/security/",
        "OWASP: https://owasp.org/www-project-top-ten/"
    ],
    "key_takeaways": [
        "AuthN: Cookie (web), JWT (API), OAuth2/OIDC (Google, Azure AD), Identity (user mgmt)",
        "AuthZ: [Authorize], Policies (Role, Claim, Custom Requirement), Resource-based",
        "Crypto: AES-GCM (симметричное), RSA/OAEP (асимметричное), PBKDF2/Argon2 (пароли), HMAC (integrity)",
        "Data Protection — ключи, purpose chains, time-limited, для токенов/CSRF/PII",
        "Web Security: CSP, HSTS, Anti-forgery, SameSite, Secure Headers, Open Redirect protection"
    ],
    "estimated_minutes": 55,
    "language_slug": "csharp",
    "lesson_order": 28,
    "name_en": "Lesson: Security — Auth, AuthZ, Crypto",
    "short_description_en": "Authentication, Authorization, JWT, OAuth2, OpenID Connect, Crypto, Data Protection"
}

# ----- 29: Observability — Logging, Metrics, Tracing -----
LESSONS[29] = {
    "title": "Урок 29: Observability — структурированное логирование, метрики, распределенное трассирование, профилирование",
    "slug": "lesson-29",
    "short_description": "Serilog, Seq, OpenTelemetry, метрики (Prometheus/Grafana), распределенное трассирование (Jaeger/Zipkin), профилирование",
    "goals": [
        "Настроить структурированное логирование с Serilog: sinks, enrichment, levels",
        "Экспортировать метрики в Prometheus/Grafana через OpenTelemetry",
        "Реализовать распределенное трассирование: Activity, W3C TraceContext, Jaeger/Zipkin",
        "Использовать ActivitySource и ActivityListener для кастомных spans",
        "Профилировать приложение: dotnet-trace, PerfView, BenchmarkDotNet"
    ],
    "content_md": """## 🎯 Что вы узнаете
- Serilog: structured logging, sinks (Console, Seq, File, Elasticsearch), enrichment, log levels
- OpenTelemetry: metrics, traces, logs — единый стандарт
- Prometheus + Grafana: метрики, дашборды, алерты
- Distributed Tracing: Activity, ActivitySource, W3C TraceContext, Jaeger, Zipkin
- Профилирование: dotnet-trace, PerfView, BenchmarkDotNet, dotnet-counters

## 📝 Структурированное логирование — Serilog

### Базовая настройка
```csharp
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
    .MinimumLevel.Override("System", LogEventLevel.Warning)
    .Enrich.FromLogContext()           // свойства из LogContext.PushProperty
    .Enrich.WithProperty("App", "MyApp")
    .Enrich.WithThreadId()
    .Enrich.WithMachineName()
    .Enrich.WithProcessId()
    .Enrich.WithEnvironmentName()
    .WriteTo.Console(
        outputTemplate: "[{Timestamp:HH:mm:ss.fff} {Level:u3}] {Message:lj} {Properties:j}{NewLine}{Exception}")
    .WriteTo.Seq("http://seq:5341")    // UI для поиска/анализа логов
    .WriteTo.File("logs/app-.txt", 
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 30,
        outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{Level:u3}] {Message:lj} {Properties:j}{NewLine}{Exception}")
    .CreateLogger();

builder.Host.UseSerilog();
```

### Структурированные сообщения (ключ к поиску!)
```csharp
// ПЛОХО — строка, нельзя фильтровать
_logger.LogInformation("User 123 placed order 456 for $99.99");

// ХОРОШО — свойства для запросов в Seq/ELK
_logger.LogInformation("User {UserId} placed order {OrderId} for {Amount:C}", 123, 456, 99.99m);

// В Seq можно: UserId == 123 AND Amount > 50
```

### Enrichment — контекст
```csharp
// Добавить свойства к ВСЕМ логам в scope
using (LogContext.PushProperty("CorrelationId", correlationId))
using (LogContext.PushProperty("UserId", userId)) {
    _logger.LogInformation("Processing order"); // автоматически имеет CorrelationId, UserId
}

// Кастомный enricher
public class UserEnricher : ILogEventEnricher {
    private readonly IHttpContextAccessor _httpContext;
    public void Enrich(LogEvent logEvent, ILogEventPropertyFactory factory) {
        if (_httpContext.HttpContext?.User?.Identity?.IsAuthenticated == true) {
            var userId = _httpContext.HttpContext.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (userId != null) logEvent.AddPropertyIfAbsent(factory.CreateProperty("UserId", userId));
        }
    }
}

// Регистрация
.Enrich.With<UserEnricher>()
```

### Destructuring — сериализация объектов
```csharp
// По умолчанию ToString() — неинформативно
_logger.LogInformation("User: {@User}", user); // @ — сериализовать как JSON

// Настройка
.Destructure.ByTransforming<User>(u => new { u.Id, u.Name, u.Email }) // скрыть PasswordHash
.Destructure.AsScalar<CreditCardNumber>() // не разбирать, как есть
```

## 📊 Метрики — OpenTelemetry + Prometheus

### Настройка OpenTelemetry Metrics
```bash
dotnet add package OpenTelemetry.Exporter.Prometheus
dotnet add package OpenTelemetry.Extensions.Hosting
```

```csharp
builder.Services.AddOpenTelemetry()
    .WithMetrics(builder => builder
        .AddRuntimeInstrumentation()           // GC, ThreadPool, JIT метрики
        .AddAspNetCoreInstrumentation()        // HTTP запросы: duration, status codes
        .AddHttpClientInstrumentation()        // исходящие HTTP
        .AddEntityFrameworkCoreInstrumentation() // EF Core queries
        .AddMeter("MyApp.Metrics")             // кастомные метрики
        .AddPrometheusExporter());             // /metrics endpoint
```

### Кастомные метрики
```csharp
public class OrderMetrics {
    private readonly Counter<long> _ordersCreated;
    private readonly Histogram<double> _orderValue;
    private readonly UpDownCounter<long> _activeOrders;
    
    public OrderMetrics(IMeterFactory meterFactory) {
        var meter = meterFactory.Create("MyApp.Metrics");
        _ordersCreated = meter.CreateCounter<long>("orders.created.total", "orders", "Total orders created");
        _orderValue = meter.CreateHistogram<double>("order.value", "USD", "Order value distribution");
        _activeOrders = meter.CreateUpDownCounter<long>("orders.active", "orders", "Currently active orders");
    }
    
    public void OrderCreated(decimal value) {
        _ordersCreated.Add(1);
        _orderValue.Record((double)value);
        _activeOrders.Add(1);
    }
    
    public void OrderCompleted() => _activeOrders.Add(-1);
}
```

### Prometheus + Grafana
```yaml
# docker-compose.yml
prometheus:
  image: prom/prometheus
  volumes: ["./prometheus.yml:/etc/prometheus/prometheus.yml"]
  ports: ["9090:9090"]

grafana:
  image: grafana/grafana
  ports: ["3000:3000"]
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes: ["./grafana/dashboards:/etc/grafana/provisioning/dashboards"]
```

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'myapp'
    static_configs:
      - targets: ['host.docker.internal:5000'] # или k8s service discovery
```

## 🔍 Распределенное трассирование — OpenTelemetry Traces

### Настройка
```bash
dotnet add package OpenTelemetry.Exporter.Jaeger
dotnet add package OpenTelemetry.Exporter.Zipkin
dotnet add package OpenTelemetry.Instrumentation.AspNetCore
dotnet add package OpenTelemetry.Instrumentation.Http
dotnet add package OpenTelemetry.Instrumentation.EntityFrameworkCore
```

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(builder => builder
        .AddAspNetCoreInstrumentation(options => {
            options.Filter = ctx => !ctx.Request.Path.StartsWithSegments("/health");
            options.EnrichWithHttpRequest = (activity, request) => {
                activity.SetTag("http.request.body", GetRequestBody(request));
            };
        })
        .AddHttpClientInstrumentation(options => {
            options.EnrichWithHttpRequestMessage = (activity, request) => {
                activity.SetTag("http.client", request.RequestUri?.Host);
            };
        })
        .AddEntityFrameworkCoreInstrumentation(options => {
            options.SetDbStatementForText = true; // SQL в spans
        })
        .AddSource("MyApp.Activities")           // кастомные ActivitySource
        .AddJaegerExporter(options => {
            options.AgentHost = "jaeger";
            options.AgentPort = 6831;
        })
        .AddZipkinExporter(options => {
            options.Endpoint = new Uri("http://zipkin:9411/api/v2/spans");
        })
        .SetResourceBuilder(ResourceBuilder.CreateDefault()
            .AddService("MyApp")));
```

### ActivitySource — кастомные spans
```csharp
public static class AppActivitySource {
    public static readonly ActivitySource Source = new("MyApp.Activities");
}

public class OrderService {
    public async Task<Order> CreateOrderAsync(CreateOrderDto dto) {
        using var activity = AppActivitySource.Source.StartActivity("CreateOrder", ActivityKind.Internal);
        activity?.SetTag("customer.id", dto.CustomerId);
        activity?.SetTag("items.count", dto.Items.Count);
        
        // baggage — передается через контекст (W3C TraceContext)
        Baggage.Current.SetBaggage("user.id", dto.CustomerId.ToString());
        
        var order = await _repo.CreateAsync(dto);
        
        activity?.SetTag("order.id", order.Id);
        activity?.SetStatus(ActivityStatusCode.Ok);
        return order;
    }
}
```

### Context Propagation — W3C TraceContext
```http
# Заголовки автоматически добавляются/читаются
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
tracestate: vendor=value
baggage: user.id=123,correlation.id=abc
```

### Correlation в логах
```csharp
// Serilog + OpenTelemetry = TraceId/SpanId в логах
.Enrich.WithProperty("TraceId", () => Activity.Current?.TraceId.ToString() ?? "none")
.Enrich.WithProperty("SpanId", () => Activity.Current?.SpanId.ToString() ?? "none")
```

## ⚡ Профилирование и бенчмарки

### dotnet-trace — ETW трассировка
```bash
# Сбор трассировки
dotnet-trace collect --process-id <PID> \
  --providers Microsoft-Windows-DotNETRuntime:4:5 \
  --providers Microsoft-Windows-DotNETRuntime:4:5:EventStack \
  --providers Microsoft-DotNETCore-SampleProfiler:4:5 \
  -o trace.nettrace

# Анализ в PerfView или Speedscope
dotnet-trace convert trace.nettrace --format speedscope
```

### dotnet-counters — real-time метрики
```bash
dotnet-counters monitor --process-id <PID> \
  --counters System.Runtime.GC \
  --counters System.Runtime.Threading \
  --counters Microsoft.AspNetCore.Hosting
```

### BenchmarkDotNet — микробенчмарки
```bash
dotnet add package BenchmarkDotNet
```

```csharp
[MemoryDiagnoser]
[SimpleJob(RuntimeMoniker.Net80)]
public class StringConcatBenchmarks {
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
    
    [Benchmark]
    public string StringInterpolation() {
        string s = "";
        for (int i = 0; i < N; i++) s = $"{s}{i}";
        return s;
    }
}

// Запуск
BenchmarkRunner.Run<StringConcatBenchmarks>();
```

### PerfView — глубокий анализ
- Открытие `.nettrace` / `.etl`
- GC Stats: паузы, поколения, причины
- CPU Stacks: где тратится время (JIT, GC, ваш код)
- Memory: кто аллоцирует, GC Roots
- File I/O, Network, Lock Contention

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Логи не структурированы | Нельзя запрашивать/фильтровать в Seq | Используйте `{Property}` синтаксис, `@` для объектов |
| Отсутствие CorrelationId | Невозможно проследить запрос через сервисы | Добавляйте `TraceId`/`CorrelationId` в LogContext |
| Метрики без лейблов (high cardinality) | Prometheus OOM | Не добавляйте unbounded лейблы (userId, requestId) |
| Трассировка не включена для всех вызовов | Разрывы в trace | Включите instrumentation для HttpClient, EF Core, gRPC |
| Benchmark без `[MemoryDiagnoser]` | Не видно аллокации | Всегда добавляйте MemoryDiagnoser |
| `dotnet-trace` без символов | Нечитаемые стеки | Собирайте с `dotnet publish -c Release -p:DebugType=portable` |

## 🛠 Практика

1. Настройте Serilog: Console + Seq + File (rolling). Добавьте enrichment: ThreadId, MachineName, CorrelationId из Activity.
2. Добавьте OpenTelemetry Metrics: Runtime, AspNetCore, HttpClient, EF Core. Экспорт в Prometheus. Создайте Grafana дашборд.
3. Включите Distributed Tracing: Jaeger/Zipkin экспортер. Добавьте кастомный `ActivitySource` для бизнес-операций.
4. Напишите BenchmarkDotNet тест: сравните `StringBuilder` vs `string.Concat` vs `List<string>.Join`.
5. Профилируйте приложение под нагрузкой: `dotnet-trace collect`, анализ в PerfView / Speedscope.

## 📌 Кратко

- **Serilog** — structured logging, sinks, enrichment, `@` для объектов, LogContext для correlation
- **OpenTelemetry Metrics** — Runtime, AspNetCore, HttpClient, EF Core, custom meters → Prometheus/Grafana
- **Distributed Tracing** — ActivitySource, W3C TraceContext, Jaeger/Zipkin, baggage для propagation
- **Profiling** — dotnet-trace (ETW), dotnet-counters (real-time), BenchmarkDotNet (micro), PerfView (deep)

## 🔗 Ссылки

- Serilog: https://serilog.net/
- OpenTelemetry .NET: https://github.com/open-telemetry/opentelemetry-dotnet
- Prometheus: https://prometheus.io/
- Grafana: https://grafana.com/
- Jaeger: https://www.jaegertracing.io/
- BenchmarkDotNet: https://benchmarkdotnet.org/
- PerfView: https://github.com/microsoft/perfview
""",
    "practice_tasks": [
        "Настройте Serilog: Console + Seq + File (rolling). Добавьте enrichment: ThreadId, MachineName, CorrelationId из Activity.",
        "Добавьте OpenTelemetry Metrics: Runtime, AspNetCore, HttpClient, EF Core. Экспорт в Prometheus. Создайте Grafana дашборд.",
        "Включите Distributed Tracing: Jaeger/Zipkin экспортер. Добавьте кастомный `ActivitySource` для бизнес-операций.",
        "Напишите BenchmarkDotNet тест: сравните `StringBuilder` vs `string.Concat` vs `List<string>.Join`.",
        "Профилируйте приложение под нагрузкой: `dotnet-trace collect`, анализ в PerfView / Speedscope."
    ],
    "common_errors": [
        {"mistake": "Логи не структурированы", "correct": "Используйте `{Property}` синтаксис, `@` для объектов"},
        {"mistake": "Отсутствие CorrelationId", "correct": "Добавляйте `TraceId`/`CorrelationId` в LogContext"},
        {"mistake": "Метрики без лейблов (high cardinality)", "correct": "Не добавляйте unbounded лейблы (userId, requestId)"},
        {"mistake": "Трассировка не включена для всех вызовов", "correct": "Включите instrumentation для HttpClient, EF Core, gRPC"},
        {"mistake": "Benchmark без `[MemoryDiagnoser]`", "correct": "Всегда добавляйте MemoryDiagnoser"},
        {"mistake": "`dotnet-trace` без символов", "correct": "Собирайте с `dotnet publish -c Release -p:DebugType=portable`"}
    ],
    "resources": [
        "Serilog: https://serilog.net/",
        "OpenTelemetry .NET: https://github.com/open-telemetry/opentelemetry-dotnet",
        "Prometheus: https://prometheus.io/",
        "Grafana: https://grafana.com/",
        "Jaeger: https://www.jaegertracing.io/",
        "BenchmarkDotNet: https://benchmarkdotnet.org/",
        "PerfView: https://github.com/microsoft/perfview"
    ],
    "key_takeaways": [
        "Serilog — structured logging, sinks, enrichment, @ для объектов, LogContext для correlation",
        "OpenTelemetry Metrics — Runtime, AspNetCore, HttpClient, EF Core, custom meters → Prometheus/Grafana",
        "Distributed Tracing — ActivitySource, W3C TraceContext, Jaeger/Zipkin, baggage для propagation",
        "Profiling — dotnet-trace (ETW), dotnet-counters (real-time), BenchmarkDotNet (micro), PerfView (deep)"
    ],
    "estimated_minutes": 50,
    "language_slug": "csharp",
    "lesson_order": 29,
    "name_en": "Lesson: Observability",
    "short_description_en": "Structured logging, metrics, distributed tracing, profiling with OpenTelemetry"
}

# ----- 30: Cloud Native — Docker, Kubernetes, Cloud -----
LESSONS[30] = {
    "title": "Урок 30: Cloud Native — Docker, Kubernetes, Cloud Run, сервис-меш, CI/CD",
    "slug": "lesson-30",
    "short_description": "Dockerfile оптимизация, multi-stage builds, Kubernetes манифесты, Helm, Kustomize, Service Mesh (Istio/Linkerd), CI/CD pipelines",
    "goals": [
        "Писать оптимальные Dockerfile: multi-stage, layer caching, non-root, distroless",
        "Развертывать в Kubernetes: Deployments, Services, Ingress, ConfigMaps, Secrets, HPA",
        "Использовать Helm и Kustomize для управления конфигурациями",
        "Понимать Service Mesh: Istio, Linkerd — mTLS, traffic splitting, observability",
        "Настраивать CI/CD: GitHub Actions, GitLab CI, ArgoCD, Flux"
    ],
    "content_md": """## 🎯 Что вы узнаете
- Docker: multi-stage builds, layer caching, .dockerignore, distroless, non-root, security
- Kubernetes: Pods, Deployments, Services, Ingress, ConfigMaps, Secrets, HPA, VPA, PDB
- Helm: charts, values, dependencies,リリース
- Kustomize: base/overlays, patches, generators
- Service Mesh: Istio/Linkerd — mTLS, traffic management, observability
- CI/CD: GitHub Actions, ArgoCD, Flux, продвинутые стратегии деплоя

## 🐳 Docker — оптимальные образы

### Multi-stage Build
```dockerfile
# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Кэшируем restore — копируем сначала csproj
COPY *.sln .
COPY src/*/*.csproj ./src/
RUN dotnet restore

# Копируем остальное и билдим
COPY . .
RUN dotnet publish src/MyApp.Api/MyApp.Api.csproj -c Release -o /app/publish --no-restore

# Stage 2: Runtime (distroless — минимальный, без shell, package manager)
FROM mcr.microsoft.com/dotnet/aspnet:8.0-distroless AS runtime
WORKDIR /app

# Non-root user (UID 65532 в distroless)
USER 65532:65532

COPY --from=build --chown=65532:65532 /app/publish .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["dotnet", "MyApp.Api.dll"]
```

### .dockerignore — критично для скорости
```dockerignore
# Исключаем из контекста сборки
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

### Layer Caching — порядок важен
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

### Distroless vs Alpine vs Debian
| Base Image | Размер | Безопасность | Shell | Package Manager |
|---|---|---|---|---|
| `mcr.microsoft.com/dotnet/aspnet:8.0` (Debian) | ~100 MB | Стандарт | bash | apt |
| `mcr.microsoft.com/dotnet/aspnet:8.0-alpine` | ~30 MB | Меньше атакующих поверхностей | sh | apk |
| `mcr.microsoft.com/dotnet/aspnet:8.0-distroless` | ~25 MB | Минимальная (нет shell, нет пакетов) | **нет** | **нет** |

**Рекомендация**: distroless для продакшена (безопасность), alpine если нужен shell для отладки.

## ☸️ Kubernetes — манифесты

### Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels: { app: myapp }
spec:
  replicas: 3
  selector:
    matchLabels: { app: myapp }
  template:
    metadata:
      labels: { app: myapp }
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 65532
        fsGroup: 65532
      containers:
      - name: myapp
        image: myregistry/myapp:v1.2.3
        ports:
        - containerPort: 8080
          name: http
        envFrom:
        - configMapRef: { name: myapp-config }
        - secretRef: { name: myapp-secrets }
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet: { path: /health/live, port: 8080 }
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet: { path: /health/ready, port: 8080 }
          initialDelaySeconds: 5
          periodSeconds: 5
        startupProbe:
          httpGet: { path: /health/startup, port: 8080 }
          failureThreshold: 30
          periodSeconds: 10
```

### Service
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  labels: { app: myapp }
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
    name: http
  selector:
    app: myapp
```

### Ingress
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts: [myapp.example.com]
    secretName: myapp-tls
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp
            port: { number: 80 }
```

### ConfigMap и Secret
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  ASPNETCORE_ENVIRONMENT: "Production"
  Logging__LogLevel__Default: "Information"
  FeatureFlags__NewUi: "true"

---
# secret.yaml (значения в base64!)
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
type: Opaque
data:
  ConnectionStrings__Default: cG9zdGdyZXNxbDovLz... # base64
  Jwt__Key: c3VwZXItc2VjcmV0LWtleS1taW4tMjU2LWJpdHMh
```

### HPA (Horizontal Pod Autoscaler)
```yaml
# hpa.yaml
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

### PodDisruptionBudget — доступность при обновлениях
```yaml
# pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 2 # или maxUnavailable: 1
  selector:
    matchLabels:
      app: myapp
```

## ⛵ Helm — пакетный менеджер K8s

### Структура чарта
```
myapp/
├── Chart.yaml          # метаданные
├── values.yaml         # дефолтные значения
├── values-prod.yaml    # прод значения
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── hpa.yaml
    ├── configmap.yaml
    ├── secret.yaml
    └── _helpers.tpl    # хелперы
```

### Chart.yaml
```yaml
apiVersion: v2
name: myapp
description: My Application Helm Chart
type: application
version: 1.2.3
appVersion: "1.2.3"
dependencies:
- name: postgresql
  version: "12.x.x"
  repository: "https://charts.bitnami.com/bitnami"
  condition: postgresql.enabled
```

### Values.yaml
```yaml
replicaCount: 3
image:
  repository: myregistry/myapp
  tag: "1.2.3"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  hosts:
  - host: myapp.example.com
    paths: ["/"]
  tls:
  - secretName: myapp-tls
    hosts: [myapp.example.com]

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
  maxReplicas: 50
  targetCPUUtilizationPercentage: 70

postgresql:
  enabled: true
  auth:
    database: myapp
```

### Команды
```bash
# Установка
helm install myapp ./myapp -n production --create-namespace -f values-prod.yaml

# Обновление
helm upgrade myapp ./myapp -n production -f values-prod.yaml

# Откат
helm rollback myapp 1 -n production

# Шаблонизация (для проверки)
helm template myapp ./myapp -f values-prod.yaml
```

## 🎨 Kustomize — нативный K8s способ

### Структура
```
base/
├── deployment.yaml
├── service.yaml
├── kustomization.yaml
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   └── replica-patch.yaml
    ├── staging/
    │   ├── kustomization.yaml
    │   └── replica-patch.yaml
    └── prod/
        ├── kustomization.yaml
        ├── replica-patch.yaml
        └── resources-patch.yaml
```

### base/kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
commonLabels:
  app: myapp
  managed-by: kustomize
```

### overlays/prod/kustomization.yaml
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
- ../../base
patches:
- path: replica-patch.yaml
- path: resources-patch.yaml
images:
- name: myregistry/myapp
  newTag: v1.2.3
configMapGenerator:
- name: myapp-config
  behavior: merge
  literals:
  - ASPNETCORE_ENVIRONMENT=Production
  - FeatureFlags__NewUi=true
secretGenerator:
- name: myapp-secrets
  literals:
  - ConnectionStrings__Default=postgresql://...
```

### Применение
```bash
kubectl apply -k overlays/prod
```

## 🕸 Service Mesh — Istio / Linkerd

### Зачем Service Mesh
- **mTLS** — автоматическое шифрование между сервисами
- **Traffic Management** — canary, blue-green, mirroring, retries, timeouts
- **Observability** — автоматические метрики, трассировка, access logs
- **Security** — авторизация, JWT валидация, rate limiting

### Istio — пример
```yaml
# DestinationRule — настройки трафика
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
    loadBalancer:
      simple: LEAST_REQUEST
    tls:
      mode: ISTIO_MUTUAL # mTLS

---
# VirtualService — маршрутизация
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

---
# AuthorizationPolicy — RBAC
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: myapp-authz
spec:
  selector:
    matchLabels:
      app: myapp
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

### Linkerd — легкий альтернативный
```bash
# Установка
linkerd install | kubectl apply -f -

# Автоматическое mTLS — просто добавьте аннотацию
kubectl annotate deploy myapp linkerd.io/inject=enabled
```

## 🔄 CI/CD — GitHub Actions, ArgoCD, Flux

### GitHub Actions — Build & Deploy
```yaml
# .github/workflows/ci-cd.yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=sha,prefix=
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/myapp myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        kubectl rollout status deployment/myapp --timeout=300s
```

### ArgoCD — GitOps Continuous Delivery
```yaml
# Application.yaml
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
      allowEmpty: false
    syncOptions:
    - CreateNamespace=true
    - PrunePropagationPolicy=foreground
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### Flux — альтернативный GitOps
```bash
# Установка
flux bootstrap github \
  --owner=myorg \
  --repository=myapp-config \
  --branch=main \
  --path=clusters/prod \
  --personal
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| `latest` тег в проде | Непредсказуемые деплои, кэш | Всегда конкретные теги: semver, git sha |
| Отсутствие `resources.requests/limits` | OOM Kill, нестабильность, неэффективность | Всегда ставьте requests и limits |
| Отсутствие `liveness/readiness` probes | Kubernetes не знает, жив ли под | Добавляйте health endpoints |
| Запуск от root в контейнере | Безопасность | `USER 65532:65532` в Dockerfile |
| Secrets в Git / Helm values.yaml | Утечка | Sealed Secrets, External Secrets Operator, Vault |
| Отсутствие PDB | Downtime при node drain/update | Добавьте PodDisruptionBudget |
| Неправильный порядок слоев в Dockerfile | Медленные сборки | COPY csproj → restore → COPY . → publish |

## 🛠 Практика

1. Напишите оптимальный multi-stage Dockerfile для ASP.NET Core приложения с distroless базой, non-root пользователем, health check.
2. Создайте K8s манифесты: Deployment, Service, Ingress, ConfigMap, Secret, HPA, PDB.
3. Создайте Helm чарт с зависимостью от PostgreSQL (Bitnami). Настройте values-prod.yaml.
4. Настройте Kustomize: base + overlays для dev/staging/prod с разными replicaCount и ресурсами.
5. Настройте GitHub Actions pipeline: build multi-arch image, push to GHCR, deploy через kubectl/ArgoCD.

## 📌 Кратко

- **Docker**: multi-stage, layer caching (csproj first), distroless, non-root, .dockerignore, health checks
- **K8s**: Deployment, Service, Ingress, ConfigMap/Secret, HPA, VPA, PDB, probes, resources
- **Helm**: charts, values, dependencies, template functions, release management
- **Kustomize**: base/overlays, patches, generators, нативный K8s
- **Service Mesh**: Istio/Linkerd — mTLS, traffic splitting, observability, security policies
- **CI/CD**: GitHub Actions (build/push), ArgoCD/Flux (GitOps), semver tags, security scanning

## 🔗 Ссылки

- Docker Best Practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Kubernetes: https://kubernetes.io/docs/home/
- Helm: https://helm.sh/docs/
- Kustomize: https://kustomize.io/
- Istio: https://istio.io/latest/docs/
- Linkerd: https://linkerd.io/
- ArgoCD: https://argo-cd.readthedocs.io/
- Flux: https://fluxcd.io/
""",
    "practice_tasks": [
        "Напишите оптимальный multi-stage Dockerfile для ASP.NET Core приложения с distroless базой, non-root пользователем, health check.",
        "Создайте K8s манифесты: Deployment, Service, Ingress, ConfigMap, Secret, HPA, PDB.",
        "Создайте Helm чарт с зависимостью от PostgreSQL (Bitnami). Настройте values-prod.yaml.",
        "Настройте Kustomize: base + overlays для dev/staging/prod с разными replicaCount и ресурсами.",
        "Настройте GitHub Actions pipeline: build multi-arch image, push to GHCR, deploy через kubectl/ArgoCD."
    ],
    "common_errors": [
        {"mistake": "`latest` тег в проде", "correct": "Всегда конкретные теги: semver, git sha"},
        {"mistake": "Отсутствие `resources.requests/limits`", "correct": "Всегда ставьте requests и limits"},
        {"mistake": "Отсутствие `liveness/readiness` probes", "correct": "Добавляйте health endpoints"},
        {"mistake": "Запуск от root в контейнере", "correct": "`USER 65532:65532` в Dockerfile"},
        {"mistake": "Secrets в Git / Helm values.yaml", "correct": "Sealed Secrets, External Secrets Operator, Vault"},
        {"mistake": "Отсутствие PDB", "correct": "Добавьте PodDisruptionBudget"},
        {"mistake": "Неправильный порядок слоев в Dockerfile", "correct": "COPY csproj → restore → COPY . → publish"}
    ],
    "resources": [
        "Docker Best Practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/",
        "Kubernetes: https://kubernetes.io/docs/home/",
        "Helm: https://helm.sh/docs/",
        "Kustomize: https://kustomize.io/",
        "Istio: https://istio.io/latest/docs/",
        "Linkerd: https://linkerd.io/",
        "ArgoCD: https://argo-cd.readthedocs.io/",
        "Flux: https://fluxcd.io/"
    ],
    "key_takeaways": [
        "Docker: multi-stage, layer caching (csproj first), distroless, non-root, .dockerignore, health checks",
        "K8s: Deployment, Service, Ingress, ConfigMap/Secret, HPA, VPA, PDB, probes, resources",
        "Helm: charts, values, dependencies, template functions, release management",
        "Kustomize: base/overlays, patches, generators, нативный K8s",
        "Service Mesh: Istio/Linkerd — mTLS, traffic splitting, observability, security policies",
        "CI/CD: GitHub Actions (build/push), ArgoCD/Flux (GitOps), semver tags, security scanning"
    ],
    "estimated_minutes": 60,
    "language_slug": "csharp",
    "lesson_order": 30,
    "name_en": "Lesson: Cloud Native — Docker, K8s, Cloud",
    "short_description_en": "Dockerfile optimization, Kubernetes manifests, Helm, Kustomize, Service Mesh, CI/CD"
}

# ----- 31: Performance — Profiling, Benchmarks, Optimizations -----
LESSONS[31] = {
    "title": "Урок 31: Производительность — профилирование, бенчмарки, оптимизации, Span, ArrayPool, SIMD",
    "slug": "lesson-31",
    "short_description": "BenchmarkDotNet, профилирование (dotnet-trace, PerfView), Span/Memory, ArrayPool, SIMD, Vector<T>, PGO, NativeAOT",
    "goals": [
        "Писать правильные бенчмарки с BenchmarkDotNet: MemoryDiagnoser, DisassemblyDiagnoser",
        "Профилировать CPU и память: dotnet-trace, PerfView, dotnet-counters, EventPipe",
        "Использовать Span/Memory, ArrayPool, Stackalloc для снижения аллокаций",
        "Применять SIMD: Vector<T>, HardwareIntrinsics (AVX2, SSE), System.Numerics",
        "Понимать PGO (Profile-Guided Optimization), NativeAOT, Tiered Compilation, ReadyToRun"
    ],
    "content_md": """## 🎯 Что вы узнаете
- BenchmarkDotNet: настройка, MemoryDiagnoser, DisassemblyDiagnoser, TailCallDiagnoser
- Профилирование: dotnet-trace, PerfView, dotnet-counters, EventPipe, sampling vs instrumentation
- Низкоуровневые оптимизации: Span/Memory, ArrayPool, stackalloc, object pooling
- SIMD: Vector<T>, HardwareIntrinsics (AVX2, SSE, Arm64), System.Numerics
- Продвинутые: PGO, NativeAOT, ReadyToRun, Tiered Compilation, Dynamic PGO

## 📊 BenchmarkDotNet — наука о измерении

### Базовый бенчмарк
```bash
dotnet add package BenchmarkDotNet
```

```csharp
[MemoryDiagnoser]           // аллокации, GC
[DisassemblyDiagnoser]      // asm код (требует `dotnet build -c Release`)
[SimpleJob(RuntimeMoniker.Net80)]
[SimpleJob(RuntimeMoniker.Net90)] // сравнение версий
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
    
    [Benchmark]
    public string ListJoin() {
        var list = new List<string>(N);
        for (int i = 0; i < N; i++) list.Add(i.ToString());
        return string.Join("", list);
    }
    
    [GlobalSetup]
    public void Setup() { /* инициализация данных */ }
    
    [GlobalCleanup]
    public void Cleanup() { /* очистка */ }
}

// Запуск
BenchmarkRunner.Run<StringBenchmarks>();
```

### Параметризованные бенчмарки
```csharp
[Params(100, 1000, 10000)]
public int N { get; set; }

[Benchmark]
public void Test() { /* использует N */ }
```

### Диагностика
```csharp
[MemoryDiagnoser]           // Gen 0/1/2, Allocated Bytes
[DisassemblyDiagnoser(exportHtml: true, exportDiff: true)] // asm + diff
[ThreadingDiagnoser]        // lock contention
[EventPipeProfiler]         // EventPipe events
[NativeMemoryProfiler]      // нативная память (Windows)
```

### Анализ результатов
```
| Method         | N    | Mean      | Error    | StdDev   | Gen0   | Allocated |
|---------------|------|-----------|----------|----------|--------|-----------|
| StringBuilder | 1000 | 45.2 us   | 0.9 us   | 0.8 us   | 3.5 KB | 14 KB     |
| StringConcat  | 1000 | 1,250 us  | 25 us    | 22 us    | 150 KB | 600 KB    |
| ListJoin      | 1000 | 62.1 us   | 1.2 us   | 1.1 us   | 5.2 KB | 20 KB     |
```

## 🔍 Профилирование — инструменты

### dotnet-trace (ETW)
```bash
# Сборка с символами
dotnet publish -c Release -p:DebugType=portable -p:DebugSymbols=true

# Сбор трассировки
dotnet-trace collect --process-id <PID> \
  --providers Microsoft-Windows-DotNETRuntime:4:5 \
  --providers Microsoft-DotNETCore-SampleProfiler:4:5 \
  -o trace.nettrace

# Конвертация для Speedscope (веб-визуализатор)
dotnet-trace convert trace.nettrace --format speedscope
# Открыть в https://speedscope.app
```

### dotnet-counters (real-time)
```bash
dotnet-counters monitor --process-id <PID> \
  --counters System.Runtime.GC \
  --counters System.Runtime.Threading \
  --counters System.Runtime.Jit \
  --counters Microsoft.AspNetCore.Hosting
```

### PerfView — глубокий анализ
- Открытие `.nettrace` / `.etl`
- **GC Stats**: паузы, поколения, причины GC (Allocation, OutOfMemory, Induced)
- **CPU Stacks**: где тратится время (JIT, GC, ваш код, .NET libs)
- **Memory**: аллокации по типам/стекам, GC Roots
- **File I/O / Network / Lock Contention**

### Sampling vs Instrumentation
| Режим | Накладные расходы | Детализация |
|---|---|---|
| **Sampling** (default) | Низкие (~1-5%) | Статистическая, не видит быстрые методы |
| **Instrumentation** | Высокие | Точное время каждого вызова, счетчики |

```bash
# Instrumentation
dotnet-trace collect -p <PID> --providers Microsoft-DotNETCore-SampleProfiler:4:5:EventStack
```

## 🚀 Span, Memory, ArrayPool — снижение аллокаций

### Span<T> / Memory<T>
```csharp
// Парсинг без аллокаций подстрок
public static bool TryParseInt(ReadOnlySpan<char> span, out int value) {
    value = 0;
    bool negative = false;
    int start = 0;
    
    if (span[0] == '-') { negative = true; start = 1; }
    else if (span[0] == '+') { start = 1; }
    
    for (int i = start; i < span.Length; i++) {
        char c = span[i];
        if (c < '0' || c > '9') return false;
        value = value * 10 + (c - '0');
    }
    
    if (negative) value = -value;
    return true;
}

// Использование
ReadOnlySpan<char> input = "12345".AsSpan();
TryParseInt(input, out int val); // никаких аллокаций!

// Slice без копирования
var slice = input.Slice(1, 3); // "234"
```

### ArrayPool<T> — пулинг массивов
```csharp
// Вместо new byte[100000] в цикле
public async Task ProcessStreamAsync(Stream stream) {
    byte[] buffer = ArrayPool<byte>.Shared.Rent(65536);
    try {
        while (true) {
            int read = await stream.ReadAsync(buffer);
            if (read == 0) break;
            Process(buffer.AsSpan(0, read));
        }
    } finally {
        ArrayPool<byte>.Shared.Return(buffer, clearArray: true);
    }
}

// Для строк — StringBuilder не нужен, используйте ArrayPool<char>
var chars = ArrayPool<char>.Shared.Rent(1024);
// ... заполнение ...
var result = new string(chars, 0, length);
ArrayPool<char>.Shared.Return(chars);
```

### stackalloc — стек для малых буферов
```csharp
// Только для малых размеров (< ~1KB), иначе StackOverflow
public unsafe void ProcessSmall(int count) {
    if (count <= 256) {
        byte* buffer = stackalloc byte[count];
        // заполнение...
        NativeProcess(buffer, count);
    } else {
        byte[] buffer = ArrayPool<byte>.Shared.Rent(count);
        try { fixed (byte* ptr = buffer) NativeProcess(ptr, count); }
        finally { ArrayPool<byte>.Shared.Return(buffer); }
    }
}
```

### Object Pooling — для сложных объектов
```csharp
// Microsoft.Extensions.ObjectPool
public class StringBuilderPool : IPooledObjectPolicy<StringBuilder> {
    public StringBuilder Create() => new StringBuilder(256);
    public bool Return(StringBuilder obj) { obj.Clear(); return true; }
}

// Регистрация
services.AddSingleton<ObjectPool<StringBuilder>>(sp => 
    new DefaultObjectPool<StringBuilder>(new StringBuilderPool(), maximumRetained: 100));

// Использование
public class MyService {
    private readonly ObjectPool<StringBuilder> _pool;
    public MyService(ObjectPool<StringBuilder> pool) => _pool = pool;
    
    public string BuildString() {
        var sb = _pool.Get();
        try {
            sb.Append("data");
            return sb.ToString();
        } finally {
            _pool.Return(sb);
        }
    }
}
```

## ⚡ SIMD — Single Instruction Multiple Data

### Vector<T> — абстракция над SIMD
```csharp
using System.Numerics;

// Сумма массива
public static float SumVector(float[] data) {
    Vector<float> sum = Vector<float>.Zero;
    int i = 0;
    
    // Vector<float>.Count = 8 (AVX2) или 4 (SSE)
    for (; i <= data.Length - Vector<float>.Count; i += Vector<float>.Count) {
        var v = new Vector<float>(data, i);
        sum += v;
    }
    
    // Хвост
    float scalarSum = 0;
    for (; i < data.Length; i++) scalarSum += data[i];
    
    return Vector.Sum(sum) + scalarSum;
}

// Умножение матриц (упрощенно)
public static void Multiply(Vector<float> a, Vector<float> b, Vector<float> result) {
    result = a * b; // поэлементное умножение
}
```

### HardwareIntrinsics — прямой доступ к инструкциям
```csharp
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;

// AVX2 — 256-bit регистры (8 x float, 4 x double)
public static float SumAvx2(float[] data) {
    if (!Avx2.IsSupported) return SumVector(data); // fallback
    
    Vector256<float> sum = Vector256<float>.Zero;
    int i = 0;
    for (; i <= data.Length - 8; i += 8) {
        sum = Avx2.Add(sum, Avx2.LoadVector256(data.AsSpan(i)));
    }
    
    // Horizontal add
    var sum128 = Avx.Add(sum.GetLower(), sum.GetUpper());
    sum128 = Avx.Add(sum128, Avx2.Permute(sum128, 0b11101110)); // shuffle
    sum128 = Avx.Add(sum128, Avx.Permute(sum128, 0b01010101));
    return sum128.GetElement(0);
}

// SSE — 128-bit (4 x float)
public static float SumSse(float[] data) {
    if (!Sse.IsSupported) return SumScalar(data);
    // аналогично...
}
```

### Arm64 AdvSimd (NEON)
```csharp
using System.Runtime.Intrinsics.Arm;

public static float SumNeon(float[] data) {
    if (!AdvSimd.IsSupported) return SumScalar(data);
    // Vector128<float> = 4 float
    Vector128<float> sum = Vector128<float>.Zero;
    for (int i = 0; i <= data.Length - 4; i += 4) {
        sum = AdvSimd.Add(sum, AdvSimd.LoadVector128(data.AsSpan(i)));
    }
    // horizontal add...
}
```

### System.Numerics — математика для SIMD
```csharp
using System.Numerics;

Vector3 a = new(1, 2, 3);
Vector3 b = new(4, 5, 6);
Vector3 c = a + b;           // (5, 7, 9)
Vector3 d = a * b;           // (4, 10, 18)
float dot = Vector3.Dot(a, b); // 32
Vector3 cross = Vector3.Cross(a, b);
float len = a.Length();
```

## 🎯 Продвинутые оптимизации

### PGO — Profile-Guided Optimization (.NET 8+)
```xml
<!-- Dynamic PGO (рекомендуется) -->
<PropertyGroup>
  <TieredCompilation>true</TieredCompilation>
  <TieredPGO>true</TieredPGO>
</PropertyGroup>

<!-- Static PGO — требует профилирования -->
<!-- 1. dotnet build -c Release /p:OptimizePGOInstrument=true -->
<!-- 2. Запуск приложения под нагрузкой -->
<!-- 3. dotnet build -c Release /p:OptimizePGOTrain=true -->
```

### NativeAOT — нативный бинарь
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
**Ограничения**: нет рефлексии, нет динамической загрузки сборок, нет JIT, больше бинарь.

### ReadyToRun (Crossgen2)
```xml
<PropertyGroup>
  <PublishReadyToRun>true</PublishReadyToRun>
  <PublishReadyToRunComposite>true</PublishReadyToRunComposite> # composite images
</PropertyGroup>
```
**Плюсы**: быстрее старт, меньше JIT. **Минусы**: больше размер, не все сборки совместимы.

### Tiered Compilation
```xml
<PropertyGroup>
  <TieredCompilation>true</TieredCompilation>
  <TieredPGO>true</TieredPGO> <!-- Dynamic PGO -->
</PropertyGroup>
```
- Tier 0: быстрая компиляция без оптимизаций
- Tier 1: оптимизированная для горячих методов
- OSR: замена метода на лету

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Бенчмарк без `[MemoryDiagnoser]` | Не видно аллокации/GC | Всегда добавляйте |
| `DateTime.Now` в бенчмарке | Низкое разрешение, системные вызовы | Используйте `Stopwatch` |
| JIT не прогрет | Первые итерации медленные | `[GlobalSetup]` с прогревом, `IterationSetup` |
| Dead code elimination | JIT выкидывает неиспользуемый код | `return` результат, `GC.KeepAlive` |
| SIMD без fallback | Падение на старых CPU | Проверяйте `Avx2.IsSupported`, `Sse.IsSupported` |
| `stackalloc` большого буфера | StackOverflow | Только < 1KB, иначе `ArrayPool` |
| PGO без нагрузочного теста | Профиль нерепрезентативен | Запускайте реальные сценарии |

## 🛠 Практика

1. Напишите BenchmarkDotNet тест: сравните `List<T>.Add` vs `ArrayPool` + `List<T>` с заранее выделенным массивом.
2. Профилируйте приложение под нагрузкой: `dotnet-trace collect`, найдите топ-5 горячих методов в PerfView/Speedscope.
3. Оптимизируйте парсинг CSV: замените `string.Split` на `Span<char>` парсинг без аллокаций.
4. Реализуйте сумму массива через `Vector<T>` и `Avx2` с fallback на скалярный код.
5. Настройте Dynamic PGO: `<TieredPGO>true</TieredPGO>`. Сравьте производительность до/после.

## 📌 Кратко

- **BenchmarkDotNet**: MemoryDiagnoser, DisassemblyDiagnoser, Params, Baseline, правильный анализ результатов
- **Профилирование**: dotnet-trace (ETW), PerfView (deep), dotnet-counters (real-time), Speedscope (визуализация)
- **Низкие аллокации**: Span/Memory, ArrayPool, stackalloc (<1KB), ObjectPool
- **SIMD**: Vector<T> (переносимо), HardwareIntrinsics (AVX2/SSE/NEON), System.Numerics
- **Продвинутые**: Dynamic PGO, NativeAOT, ReadyToRun, Tiered Compilation

## 🔗 Ссылки

- BenchmarkDotNet: https://benchmarkdotnet.org/
- Span/Memory: https://learn.microsoft.com/dotnet/standard/memory-and-spans/
- SIMD: https://learn.microsoft.com/dotnet/api/system.runtime.intrinsics
- PGO: https://learn.microsoft.com/dotnet/core/deploying/profile-guided-optimization
- NativeAOT: https://learn.microsoft.com/dotnet/core/deploying/native-aot/
- PerfView: https://github.com/microsoft/perfview
""",
    "practice_tasks": [
        "Напишите BenchmarkDotNet тест: сравните `List<T>.Add` vs `ArrayPool` + `List<T>` с заранее выделенным массивом.",
        "Профилируйте приложение под нагрузкой: `dotnet-trace collect`, найдите топ-5 горячих методов в PerfView/Speedscope.",
        "Оптимизируйте парсинг CSV: замените `string.Split` на `Span<char>` парсинг без аллокаций.",
        "Реализуйте сумму массива через `Vector<T>` и `Avx2` с fallback на скалярный код.",
        "Настройте Dynamic PGO: `<TieredPGO>true</TieredPGO>`. Сравните производительность до/после."
    ],
    "common_errors": [
        {"mistake": "Бенчмарк без `[MemoryDiagnoser]`", "correct": "Всегда добавляйте"},
        {"mistake": "`DateTime.Now` в бенчмарке", "correct": "Используйте `Stopwatch`"},
        {"mistake": "JIT не прогрет", "correct": "`[GlobalSetup]` с прогревом, `IterationSetup`"},
        {"mistake": "Dead code elimination", "correct": "`return` результат, `GC.KeepAlive`"},
        {"mistake": "SIMD без fallback", "correct": "Проверяйте `Avx2.IsSupported`, `Sse.IsSupported`"},
        {"mistake": "`stackalloc` большого буфера", "correct": "Только < 1KB, иначе `ArrayPool`"},
        {"mistake": "PGO без нагрузочного теста", "correct": "Запускайте реальные сценарии"}
    ],
    "resources": [
        "BenchmarkDotNet: https://benchmarkdotnet.org/",
        "Span/Memory: https://learn.microsoft.com/dotnet/standard/memory-and-spans/",
        "SIMD: https://learn.microsoft.com/dotnet/api/system.runtime.intrinsics",
        "PGO: https://learn.microsoft.com/dotnet/core/deploying/profile-guided-optimization",
        "NativeAOT: https://learn.microsoft.com/dotnet/core/deploying/native-aot/",
        "PerfView: https://github.com/microsoft/perfview"
    ],
    "key_takeaways": [
        "BenchmarkDotNet: MemoryDiagnoser, DisassemblyDiagnoser, Params, Baseline, правильный анализ результатов",
        "Профилирование: dotnet-trace (ETW), PerfView (deep), dotnet-counters (real-time), Speedscope (визуализация)",
        "Низкие аллокации: Span/Memory, ArrayPool, stackalloc (<1KB), ObjectPool",
        "SIMD: Vector<T> (переносимо), HardwareIntrinsics (AVX2/SSE/NEON), System.Numerics",
        "Продвинутые: Dynamic PGO, NativeAOT, ReadyToRun, Tiered Compilation"
    ],
    "estimated_minutes": 55,
    "language_slug": "csharp",
    "lesson_order": 31,
    "name_en": "Lesson: Performance — Profiling, Benchmarks, SIMD",
    "short_description_en": "BenchmarkDotNet, profiling, Span/Memory, ArrayPool, SIMD, PGO, NativeAOT"
}

# ----- 32: Advanced Patterns — Functional, Reactive, Actors -----
LESSONS[32] = {
    "title": "Урок 32: Продвинутые паттерны — Функциональное программирование, Reactive (Rx.NET), Actor Model (Akka.NET/Orleans)",
    "slug": "lesson-32",
    "short_description": "Functional C#: Result, Option, Railway-oriented, Rx.NET: IObservable, operators, schedulers, Akka.NET/Orleans actors",
    "goals": [
        "Писать функциональный C#: Result<T>, Option<T>, Railway-oriented programming",
        "Работать с Rx.NET: IObservable, operators (Select, Where, Merge, CombineLatest), schedulers",
        "Понимать Actor Model: Akka.NET и Orleans — actors, persistence, clustering",
        "Применять паттерны: Circuit Breaker, Retry, Bulkhead, Saga, Event Sourcing"
    ],
    "content_md": """## 🎯 Что вы узнаете
- Функциональный C#: `Result<T>`, `Option<T>`, `Either<L,R>`, Railway-oriented programming
- Rx.NET (Reactive Extensions): `IObservable<T>`, операторы, schedulers, backpressure
- Actor Model: Akka.NET — actors, supervision, persistence, clustering; Orleans — virtual actors, grains
- Продвинутые паттерны: Circuit Breaker, Retry, Bulkhead, Saga, Event Sourcing, CQRS

## 🧮 Функциональный C# — Result, Option, Railway

### Option<T> — отсутствие значения вместо null
```csharp
// Реализация (или используйте LanguageExt, OneOf, Functional.Maybe)
public readonly struct Option<T> {
    private readonly T _value;
    private readonly bool _hasValue;
    
    private Option(T value) { _value = value; _hasValue = true; }
    public static Option<T> Some(T value) => new(value);
    public static Option<T> None => default;
    
    public bool IsSome => _hasValue;
    public bool IsNone => !_hasValue;
    
    public T Value => _hasValue ? _value : throw new InvalidOperationException("Option is None");
    public T ValueOrDefault() => _hasValue ? _value : default!;
    public T ValueOr(T defaultValue) => _hasValue ? _value : defaultValue;
    
    // Map — трансформация если есть значение
    public Option<TResult> Map<TResult>(Func<T, TResult> mapper) 
        => _hasValue ? Option<TResult>.Some(mapper(_value)) : Option<TResult>.None;
    
    // Bind / FlatMap — цепочка Option
    public Option<TResult> Bind<TResult>(Func<T, Option<TResult>> binder)
        => _hasValue ? binder(_value) : Option<TResult>.None;
    
    // Match — pattern matching
    public TResult Match<TResult>(Func<T, TResult> some, Func<TResult> none)
        => _hasValue ? some(_value) : none();
}

// Использование
Option<User> FindUser(int id) => id > 0 ? Option<User>.Some(new User(id)) : Option<User>.None;

var name = FindUser(1)
    .Map(u => u.Name)
    .Bind(n => n.Length > 3 ? Option<string>.Some(n.ToUpper()) : Option<string>.None)
    .ValueOrDefault("UNKNOWN");
```

### Result<T> — успех или ошибка
```csharp
public readonly struct Result<T> {
    private readonly T _value;
    private readonly Error _error;
    private readonly bool _isSuccess;
    
    private Result(T value) { _value = value; _isSuccess = true; }
    private Result(Error error) { _error = error; _isSuccess = false; }
    
    public static Result<T> Success(T value) => new(value);
    public static Result<T> Failure(Error error) => new(error);
    
    public bool IsSuccess => _isSuccess;
    public bool IsFailure => !_isSuccess;
    public T Value => _isSuccess ? _value : throw new InvalidOperationException();
    public Error Error => !_isSuccess ? _error : throw new InvalidOperationException();
    
    public Result<TResult> Map<TResult>(Func<T, TResult> mapper)
        => _isSuccess ? Result<TResult>.Success(mapper(_value)) : Result<TResult>.Failure(_error);
    
    public Result<TResult> Bind<TResult>(Func<T, Result<TResult>> binder)
        => _isSuccess ? binder(_value) : Result<TResult>.Failure(_error);
    
    public TResult Match<TResult>(Func<T, TResult> success, Func<Error, TResult> failure)
        => _isSuccess ? success(_value) : failure(_error);
}

public readonly record struct Error(string Code, string Message);
```

### Railway-oriented programming — цепочка без исключений
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

// Каждый шаг: Result<T> -> Result<U>
private Result<ValidatedCommand> ValidateCommand(PlaceOrderCommand cmd) {
    if (cmd.Items.Count == 0) return Result<ValidatedCommand>.Failure(new Error("EMPTY_ORDER", "Order must have items"));
    if (cmd.CustomerId <= 0) return Result<ValidatedCommand>.Failure(new Error("INVALID_CUSTOMER", "Invalid customer"));
    return Result<ValidatedCommand>.Success(new ValidatedCommand(cmd));
}

private Result<InventoryCheck> CheckInventory(ValidatedCommand cmd) {
    // ...
}
```

### LanguageExt — библиотека для функционального C#
```bash
dotnet add package LanguageExt.Core
```

```csharp
using LanguageExt;
using static LanguageExt.Prelude;

// Option
Option<int> some = Some(42);
Option<int> none = None;
var result = some.Map(x => x * 2).Bind(x => x > 50 ? Some(x) : None);

// Either<L, R> — Left (error) / Right (success)
Either<Error, User> GetUser(int id) => id > 0 
    ? Right(new User(id)) 
    : Left(Error.New("NOT_FOUND", "User not found"));

// Try — безопасное выполнение
Try<Option<User>> tryGet = () => _repo.GetByIdAsync(id);
var user = await tryGet.Match(
    Succ: u => u,
    Fail: ex => None
);
```

## 🔄 Rx.NET — Reactive Extensions

### IObservable<T> — push-базированные последовательности
```bash
dotnet add package System.Reactive
dotnet add package System.Reactive.Linq
```

```csharp
// Создание Observable
var observable = Observable.Create<int>(observer => {
    for (int i = 0; i < 10; i++) {
        observer.OnNext(i);
        Thread.Sleep(100);
    }
    observer.OnCompleted();
    return Disposable.Empty;
});

// Подписка
var subscription = observable.Subscribe(
    onNext: x => Console.WriteLine($"Received: {x}"),
    onError: ex => Console.Error.WriteLine($"Error: {ex}"),
    onCompleted: () => Console.WriteLine("Done")
);

// Отмена подписки
subscription.Dispose();
```

### Основные операторы
```csharp
// Трансформация
source.Select(x => x * 2)
source.SelectMany(x => Observable.Range(0, x)) // flatten

// Фильтрация
source.Where(x => x % 2 == 0)
source.OfType<string>()
source.Distinct()
source.DistinctUntilChanged()

// Комбинирование
Observable.Merge(source1, source2)           // объединение
Observable.Concat(source1, source2)          // последовательно
Observable.Zip(source1, source2, (a, b) => a + b) // попарно
Observable.CombineLatest(source1, source2, (a, b) => a + b) // последние значения
Observable.Amb(source1, source2)             // первый emit

// Временные
source.Throttle(TimeSpan.FromMilliseconds(300))  // debounce
source.Sample(TimeSpan.FromSeconds(1))           // последнее за период
source.Buffer(TimeSpan.FromSeconds(5))           // батчинг
source.Window(TimeSpan.FromSeconds(10))          // окна

// Обработка ошибок
source.Catch(Observable.Return(defaultValue))    // fallback
source.Retry(3)                                  // повторить 3 раза
source.RetryWhen(errors => errors.DelaySubscription(TimeSpan.FromSeconds(1)))
source.OnErrorResumeNext(fallbackObservable)     // продолжить с другого
```

### Schedulers — управление потоками
```csharp
// ThreadPool (default для подписок)
Observable.Start(() => HeavyCompute(), Scheduler.Default)

// UI Thread (WPF/WinForms/MAUI)
Observable.Start(() => HeavyCompute())
    .ObserveOnDispatcher() // или ObserveOn(SynchronizationContextScheduler.Current)

// Новый поток
Observable.Start(() => HeavyCompute(), Scheduler.NewThread)

// TaskPoolScheduler — для async
Observable.FromAsync(async () => await FetchAsync())
    .SubscribeOn(TaskPoolScheduler.Default);
```

### Backpressure — контроль скорости
```csharp
// Producer быстрее Consumer — буферизация/отбрасывание
var fastProducer = Observable.Interval(TimeSpan.FromMilliseconds(10));
var slowConsumer = fastProducer
    .Buffer(TimeSpan.FromSeconds(1)) // батчинг
    .Select(batch => batch.Average())
    .ObserveOn(TaskPoolScheduler.Default) // обработка в пуле
    .Subscribe(avg => Process(avg));

// Или Reactive Streams (IAsyncEnumerable) для нативного backpressure
```

## 🎭 Actor Model — Akka.NET и Orleans

### Akka.NET — классическая модель акторов
```bash
dotnet add package Akka
dotnet add package Akka.Hosting
dotnet add package Akka.Persistence.SqlServer
```

```csharp
// Actor
public class OrderActor : ReceiveActor {
    private OrderState _state = new();
    
    public OrderActor() {
        Command<PlaceOrder>(cmd => Handle(cmd));
        Command<GetOrder>(cmd => Sender.Tell(_state));
        
        // Persistence
        Recover<OrderPlaced>(e => _state = _state.Apply(e));
    }
    
    private void Handle(PlaceOrder cmd) {
        if (_state.Status != OrderStatus.Draft) {
            Sender.Tell(new OrderRejected("Invalid state"));
            return;
        }
        
        var evt = new OrderPlaced(cmd.OrderId, cmd.Items, DateTime.UtcNow);
        Persist(evt, e => {
            _state = _state.Apply(e);
            Sender.Tell(new OrderConfirmed(cmd.OrderId));
        });
    }
}

// Actor System
var system = ActorSystem.Create("OrderSystem");
var orderActor = system.ActorOf(Props.Create(() => new OrderActor()), "order-1");

// Использование
orderActor.Tell(new PlaceOrder(orderId, items));
var response = await orderActor.Ask<OrderConfirmed>(TimeSpan.FromSeconds(5));
```

### Supervision — отказоустойчивость
```csharp
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

### Orleans — Virtual Actors (Grains)
```bash
dotnet add package Microsoft.Orleans.Core
dotnet add package Microsoft.Orleans.Persistence.AdoNet
dotnet add package Microsoft.Orleans.Clustering.AdoNet
```

```csharp
// Grain Interface
public interface IOrderGrain : IGrainWithIntegerKey {
    Task<OrderResult> PlaceOrder(PlaceOrderCommand cmd);
    Task<OrderState> GetOrder();
}

// Grain Implementation
public class OrderGrain : Grain, IOrderGrain {
    private readonly IPersistentState<OrderState> _state;
    
    public OrderGrain([PersistentState("order", "storage")] IPersistentState<OrderState> state) {
        _state = state;
    }
    
    public async Task<OrderResult> PlaceOrder(PlaceOrderCommand cmd) {
        if (_state.State.Status != OrderStatus.Draft)
            return OrderResult.Failed("Invalid state");
        
        _state.State = _state.State.Apply(new OrderPlaced(cmd.OrderId, cmd.Items));
        await _state.WriteStateAsync();
        return OrderResult.Success(cmd.OrderId);
    }
    
    public Task<OrderState> GetOrder() => Task.FromResult(_state.State);
}

// Client
var client = new ClientBuilder()
    .UseLocalhostClustering()
    .AddAdoNetGrainStorage("storage", opts => opts.ConnectionString = connStr)
    .Build();
await client.Connect();

var grain = client.GetGrain<IOrderGrain>(orderId);
var result = await grain.PlaceOrder(cmd);
```

### Orleans — Clustering, Streams, Reminders
```csharp
// Stream — для event-driven
public interface IOrderEvents : IGrainWithIntegerKey {
    Task Subscribe(IAsyncObserver<OrderEvent> observer);
}

// Reminder — надежные таймеры (выживают перезапускам)
public class OrderGrain : Grain, IOrderGrain {
    public async Task SetReminder(string name, TimeSpan dueTime) {
        await RegisterOrUpdateReminder(name, dueTime, TimeSpan.Zero);
    }
    
    public Task ReceiveReminder(string name, TickStatus status) {
        // обработка
        return Task.CompletedTask;
    }
}
```

## 🔄 Продвинутые паттерны

### Circuit Breaker
```csharp
public class CircuitBreaker {
    private int _failures;
    private DateTime _lastFailure;
    private CircuitState _state = CircuitState.Closed;
    private readonly int _threshold;
    private readonly TimeSpan _timeout;
    
    public async Task<T> ExecuteAsync<T>(Func<Task<T>> action) {
        if (_state == CircuitState.Open) {
            if (DateTime.UtcNow - _lastFailure > _timeout) _state = CircuitState.HalfOpen;
            else throw new CircuitBreakerOpenException();
        }
        
        try {
            var result = await action();
            OnSuccess();
            return result;
        } catch {
            OnFailure();
            throw;
        }
    }
    
    private void OnSuccess() {
        _failures = 0;
        _state = CircuitState.Closed;
    }
    
    private void OnFailure() {
        _failures++;
        _lastFailure = DateTime.UtcNow;
        if (_failures >= _threshold) _state = CircuitState.Open;
    }
}
```

### Saga — распределенная транзакция
```csharp
public class OrderSaga {
    private readonly IServiceProvider _services;
    
    public async Task ExecuteAsync(CreateOrderSagaData data) {
        var steps = new List<Func<Task>>();
        var compensations = new Stack<Func<Task>>();
        
        try {
            // Step 1: Reserve Inventory
            await _inventory.ReserveAsync(data.Items);
            compensations.Push(() => _inventory.ReleaseAsync(data.Items));
            
            // Step 2: Charge Payment
            await _payment.ChargeAsync(data.PaymentInfo);
            compensations.Push(() => _payment.RefundAsync(data.PaymentInfo));
            
            // Step 3: Create Order
            var order = await _order.CreateAsync(data);
            compensations.Push(() => _order.CancelAsync(order.Id));
            
            // Step 4: Send Notification
            await _notification.SendAsync(data.CustomerId, "Order created");
        } catch {
            // Compensate in reverse order
            while (compensations.Count > 0) {
                try { await compensations.Pop()(); } catch { /* log */ }
            }
            throw;
        }
    }
}
```

### Event Sourcing — события как источник истины
```csharp
// Aggregate
public class Account : EventSourcedAggregate {
    public decimal Balance { get; private set; }
    public bool IsClosed { get; private set; }
    
    public void Deposit(decimal amount) {
        if (IsClosed) throw new InvalidOperationException("Closed");
        Apply(new MoneyDeposited(Id, amount));
    }
    
    public void Withdraw(decimal amount) {
        if (Balance < amount) throw new InvalidOperationException("Insufficient funds");
        Apply(new MoneyWithdrawn(Id, amount));
    }
    
    protected override void When(object @event) {
        switch (@event) {
            case MoneyDeposited e: Balance += e.Amount; break;
            case MoneyWithdrawn e: Balance -= e.Amount; break;
            case AccountClosed e: IsClosed = true; break;
        }
    }
}

// Event Store
public interface IEventStore {
    Task AppendAsync(AggregateId id, IEnumerable<IDomainEvent> events, int expectedVersion);
    Task<IReadOnlyList<IDomainEvent>> GetEventsAsync(AggregateId id);
}

// Projection (Read Model)
public class AccountBalanceProjection : 
    IEventHandler<MoneyDeposited>, 
    IEventHandler<MoneyWithdrawn> {
    
    private readonly IReadModelRepository<AccountBalanceView> _repo;
    
    public async Task Handle(MoneyDeposited @event, CancellationToken ct) {
        var view = await _repo.GetAsync(@event.AccountId) ?? new AccountBalanceView(@event.AccountId);
        view.Balance += @event.Amount;
        await _repo.SaveAsync(view, ct);
    }
}
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Исключения для управления потоком | Медленно, трудно отлаживать | `Result<T>`, `Option<T>`, Railway-oriented |
| `Subscribe` без `Dispose` | Утечки памяти, лишние подписки | Всегда `using subscription = obs.Subscribe(...)` |
| Blocking в Rx (`Wait`, `FirstAsync().Wait()`) | Deadlock, потеря reactivity | Используйте `await observable.FirstAsync()` |
| Акторы с блокирующим кодом | Забивают dispatcher | `PipeTo`, `Ask`, асинхронные методы в акторах |
| Orleans Grain делает много работы | Один grain = single-threaded | Декомпозиция на гранулярные grains |
| Saga без идемпотентности | Повторные ретраи = дубликаты | Все шаги идемпотентны (проверка по correlationId) |

## 🛠 Практика

1. Реализуйте `Result<T>` и `Option<T>` с `Map`, `Bind`, `Match`. Напишите валидацию заказа в railway-стиле.
2. Создайте Rx.NET pipeline: генерация чисел → фильтрация чётных → батчинг по 5 → вывод среднего каждую секунду.
3. Напишите Akka.NET актор для управления состоянием заказа с Persistence (Event Sourcing).
4. Создайте Orleans Grain для корзины покупок с персистентным состоянием и reminders для abandoned cart.
5. Реализуйте Circuit Breaker и Saga для распределенного заказа (Inventory → Payment → Notification).

## 📌 Кратко

- **Functional C#**: `Result<T>`, `Option<T>`, `Either<L,R>`, Railway-oriented — нет исключений, композиция
- **Rx.NET**: `IObservable<T>`, операторы (Select, Where, Merge, CombineLatest, Throttle), Schedulers, Backpressure
- **Akka.NET**: Actors, Supervision, Persistence, Clustering — классическая модель акторов
- **Orleans**: Virtual Actors (Grains), Persistence, Streams, Reminders, Clustering — проще, масштабируемее
- **Patterns**: Circuit Breaker, Retry, Bulkhead, Saga, Event Sourcing — надежность в распределенных системах

## 🔗 Ссылки

- LanguageExt: https://github.com/louthy/language-ext
- Rx.NET: https://github.com/dotnet/reactive
- Akka.NET: https://getakka.net/
- Orleans: https://dotnet.github.io/orleans/
- Enterprise Integration Patterns: https://www.enterpriseintegrationpatterns.com/
""",
    "practice_tasks": [
        "Реализуйте `Result<T>` и `Option<T>` с `Map`, `Bind`, `Match`. Напишите валидацию заказа в railway-стиле.",
        "Создайте Rx.NET pipeline: генерация чисел → фильтрация чётных → батчинг по 5 → вывод среднего каждую секунду.",
        "Напишите Akka.NET актор для управления состоянием заказа с Persistence (Event Sourcing).",
        "Создайте Orleans Grain для корзины покупок с персистентным состоянием и reminders для abandoned cart.",
        "Реализуйте Circuit Breaker и Saga для распределенного заказа (Inventory → Payment → Notification)."
    ],
    "common_errors": [
        {"mistake": "Исключения для управления потоком", "correct": "Result<T>, Option<T>, Railway-oriented"},
        {"mistake": "`Subscribe` без `Dispose`", "correct": "Всегда `using subscription = obs.Subscribe(...)`"},
        {"mistake": "Blocking в Rx (`Wait`, `FirstAsync().Wait()`)", "correct": "Используйте `await observable.FirstAsync()`"},
        {"mistake": "Акторы с блокирующим кодом", "correct": "PipeTo, Ask, асинхронные методы в акторах"},
        {"mistake": "Orleans Grain делает много работы", "correct": "Декомпозиция на гранулярные grains"},
        {"mistake": "Saga без идемпотентности", "correct": "Все шаги идемпотентны (проверка по correlationId)"}
    ],
    "resources": [
        "LanguageExt: https://github.com/louthy/language-ext",
        "Rx.NET: https://github.com/dotnet/reactive",
        "Akka.NET: https://getakka.net/",
        "Orleans: https://dotnet.github.io/orleans/",
        "Enterprise Integration Patterns: https://www.enterpriseintegrationpatterns.com/"
    ],
    "key_takeaways": [
        "Functional C#: Result<T>, Option<T>, Either<L,R>, Railway-oriented — нет исключений, композиция",
        "Rx.NET: IObservable<T>, операторы (Select, Where, Merge, CombineLatest, Throttle), Schedulers, Backpressure",
        "Akka.NET: Actors, Supervision, Persistence, Clustering — классическая модель акторов",
        "Orleans: Virtual Actors (Grains), Persistence, Streams, Reminders, Clustering — проще, масштабируемее",
        "Patterns: Circuit Breaker, Retry, Bulkhead, Saga, Event Sourcing — надежность в распределенных системах"
    ],
    "estimated_minutes": 60,
    "language_slug": "csharp",
    "lesson_order": 32,
    "name_en": "Lesson: Advanced Patterns — Functional, Reactive, Actors",
    "short_description_en": "Functional C#, Result/Option, Rx.NET, Akka.NET, Orleans, Circuit Breaker, Saga"
}

# ----- 33: Final Project — Full Stack Application -----
LESSONS[33] = {
    "title": "Урок 33: Финальный проект — Full Stack приложение: API, Blazor, SignalR, Tests, CI/CD, Deploy",
    "slug": "lesson-33",
    "short_description": "Сборка полного приложения: Clean Architecture, ASP.NET Core API, Blazor WASM, SignalR, xUnit/Integration tests, Docker, Kubernetes, GitHub Actions, ArgoCD",
    "goals": [
        "Создать Clean Architecture решение с 4 слоями",
        "Реализовать ASP.NET Core Minimal API с CQRS (MediatR), EF Core, JWT Auth",
        "Построить Blazor WebAssembly клиент с авторизацией, SignalR real-time",
        "Написать Unit тесты (xUnit, Moq, FluentAssertions) и Integration тесты (Testcontainers)",
        "Настроить Docker multi-stage, Kubernetes манифесты, Helm чарт",
        "Настроить CI/CD: GitHub Actions → Build → Test → Docker → Deploy (ArgoCD)"
    ],
    "content_md": """## 🎯 Финальный проект: Task Manager Full Stack

Мы соберем всё изученное в одно приложение: **Task Manager** — управление задачами с real-time обновлениями.

### Архитектура решения
```
src/
├── TaskManager.Domain/          # Domain Layer
│   ├── Entities/                # Task, User, Project (Aggregate Roots)
│   ├── ValueObjects/            # TaskId, UserId, Email, TaskStatus
│   ├── Events/                  # Domain Events: TaskCreated, TaskAssigned, TaskCompleted
│   ├── Repositories/            # Interfaces: ITaskRepository, IUserRepository
│   └── Exceptions/              # Domain Exceptions
│
├── TaskManager.Application/     # Application Layer
│   ├── Commands/                # CreateTask, AssignTask, CompleteTask, CreateProject
│   ├── Queries/                 # GetTask, GetTasks, GetProject, GetUserTasks
│   ├── Handlers/                # Command/Query Handlers
│   ├── Validators/              # FluentValidation validators
│   ├── DTOs/                    # TaskDto, ProjectDto, UserDto
│   ├── Mappers/                 # Mapster/MapsterMapper profiles
│   ├── Behaviors/               # MediatR Pipeline: Validation, Logging, Transaction
│   └── Interfaces/              # IEmailService, INotificationService
│
├── TaskManager.Infrastructure/  # Infrastructure Layer
│   ├── Persistence/             # EF Core DbContext, Migrations, Repositories
│   ├── Services/                # EmailService, SignalRNotificationService
│   ├── Identity/                # JWT TokenService, RefreshTokenService
│   ├── BackgroundJobs/          # Hangfire/Quartz: Reminders, Cleanup
│   └── Configuration/           # Options classes, DI registration
│
├── TaskManager.Api/             # Presentation Layer (ASP.NET Core)
│   ├── Endpoints/               # Minimal API endpoints (MapGroup)
│   ├── Hubs/                    # TaskHub (SignalR)
│   ├── Middleware/              # ExceptionHandling, RequestLogging, RateLimiting
│   ├── Filters/                 # ValidationFilter, AuthorizationFilter
│   ├── Program.cs               # Composition Root
│   └── appsettings.json
│
├── TaskManager.Client/          # Blazor WebAssembly
│   ├── Pages/                   # Tasks.razor, Projects.razor, Login.razor
│   ├── Components/              # TaskCard, TaskForm, ProjectSelector
│   ├── Services/                # ApiClient, SignalRClient, AuthStateProvider
│   ├── State/                   # Flux/Redux-like state management
│   └── wwwroot/
│
├── TaskManager.Tests.Unit/      # Unit Tests
│   ├── Domain/                  # Entity, ValueObject, DomainEvent tests
│   ├── Application/             # Handler, Validator tests (Moq)
│   └── Infrastructure/          # Repository, Service tests
│
├── TaskManager.Tests.Integration/ # Integration Tests
│   ├── Api/                     # Endpoint tests (WebApplicationFactory)
│   ├── Persistence/             # Repository tests (Testcontainers PostgreSQL)
│   └── SignalR/                 # Hub tests
│
└── TaskManager.Tests.E2E/       # E2E Tests (Playwright)
    └── specs/
```

## 1️⃣ Domain Layer — ЧЯС (Clean Architecture)

### Value Objects
```csharp
// TaskId — strongly typed ID
public readonly record struct TaskId(Guid Value) {
    public static TaskId New() => new(Guid.NewGuid());
    public static implicit operator Guid(TaskId id) => id.Value;
    public static implicit operator TaskId(Guid guid) => new(guid);
    public override string ToString() => Value.ToString();
}

// Email — валидация в конструкторе
public readonly record struct Email(string Value) {
    public Email {
        if (string.IsNullOrWhiteSpace(Value) || !Value.Contains("@"))
            throw new ArgumentException("Invalid email format", nameof(Value));
    }
    public static implicit operator string(Email e) => e.Value;
    public static implicit operator Email(string s) => new(s);
}

// TaskStatus — enum-like с поведением
public enum TaskStatus {
    Backlog = 1,
    InProgress = 2,
    InReview = 3,
    Done = 4,
    Archived = 5
}
```

### Aggregate Root — Task
```csharp
public class Task : AggregateRoot<TaskId> {
    public string Title { get; private set; }
    public string Description { get; private set; }
    public TaskStatus Status { get; private set; }
    public UserId? AssigneeId { get; private set; }
    public ProjectId ProjectId { get; private set; }
    public DateTime CreatedAt { get; private set; }
    public DateTime UpdatedAt { get; private set; }
    
    private Task() { } // EF Core
    
    public static Task Create(TaskId id, string title, string description, ProjectId projectId, UserId creatorId) {
        var task = new Task {
            Id = id,
            Title = title,
            Description = description,
            ProjectId = projectId,
            Status = TaskStatus.Backlog,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        task.AddDomainEvent(new TaskCreatedEvent(task.Id, task.Title, task.ProjectId, creatorId));
        return task;
    }
    
    public void Assign(UserId userId) {
        if (Status == TaskStatus.Done || Status == TaskStatus.Archived)
            throw new InvalidOperationException("Cannot assign completed task");
        AssigneeId = userId;
        UpdatedAt = DateTime.UtcNow;
        AddDomainEvent(new TaskAssignedEvent(Id, userId));
    }
    
    public void StartWork() {
        if (Status != TaskStatus.Backlog) throw new InvalidOperationException("Task must be in Backlog");
        Status = TaskStatus.InProgress;
        UpdatedAt = DateTime.UtcNow;
        AddDomainEvent(new TaskStatusChangedEvent(Id, TaskStatus.Backlog, TaskStatus.InProgress));
    }
    
    public void Complete() {
        if (Status != TaskStatus.InReview) throw new InvalidOperationException("Task must be in review");
        Status = TaskStatus.Done;
        UpdatedAt = DateTime.UtcNow;
        AddDomainEvent(new TaskCompletedEvent(Id));
    }
}
```

### Domain Events
```csharp
public record TaskCreatedEvent(TaskId TaskId, string Title, ProjectId ProjectId, UserId CreatorId) : IDomainEvent;
public record TaskAssignedEvent(TaskId TaskId, UserId AssigneeId) : IDomainEvent;
public record TaskStatusChangedEvent(TaskId TaskId, TaskStatus OldStatus, TaskStatus NewStatus) : IDomainEvent;
public record TaskCompletedEvent(TaskId TaskId) : IDomainEvent;
```

## 2️⃣ Application Layer — CQRS с MediatR

### Commands
```csharp
public record CreateTaskCommand(string Title, string Description, Guid ProjectId) : IRequest<TaskId>;

public class CreateTaskHandler : IRequestHandler<CreateTaskCommand, TaskId> {
    private readonly ITaskRepository _repo;
    private readonly IUnitOfWork _uow;
    private readonly ICurrentUserService _currentUser;
    
    public CreateTaskHandler(ITaskRepository repo, IUnitOfWork uow, ICurrentUserService currentUser) {
        _repo = repo; _uow = uow; _currentUser = currentUser;
    }
    
    public async Task<TaskId> Handle(CreateTaskCommand cmd, CancellationToken ct) {
        var projectId = new ProjectId(cmd.ProjectId);
        var task = Task.Create(TaskId.New(), cmd.Title, cmd.Description, projectId, _currentUser.UserId!);
        await _repo.AddAsync(task, ct);
        await _uow.SaveChangesAsync(ct);
        return task.Id;
    }
}
```

### Queries
```csharp
public record GetTaskQuery(TaskId Id) : IRequest<TaskDto?>;

public class GetTaskHandler : IRequestHandler<GetTaskQuery, TaskDto?> {
    private readonly ITaskReadRepository _repo;
    private readonly IMapper _mapper;
    
    public GetTaskHandler(ITaskReadRepository repo, IMapper mapper) {
        _repo = repo; _mapper = mapper;
    }
    
    public async Task<TaskDto?> Handle(GetTaskQuery query, CancellationToken ct) {
        var task = await _repo.GetByIdAsync(query.Id, ct);
        return task == null ? null : _mapper.Map<TaskDto>(task);
    }
}
```

### Pipeline Behaviors
```csharp
// Validation
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

// Transaction
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
```

## 3️⃣ Infrastructure — EF Core, SignalR, JWT

### DbContext
```csharp
public class AppDbContext : DbContext {
    public DbSet<Task> Tasks => Set<Task>();
    public DbSet<User> Users => Set<User>();
    public DbSet<Project> Projects => Set<Project>();
    
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
    
    protected override void OnModelCreating(ModelBuilder model) {
        model.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
        
        // Outbox pattern для Domain Events
        model.Entity<OutboxMessage>(e => {
            e.HasKey(m => m.Id);
            e.Property(m => m.Type).HasMaxLength(200);
            e.Property(m => m.Content).HasColumnType("jsonb");
        });
    }
    
    public override async Task<int> SaveChangesAsync(CancellationToken ct = default) {
        // Dispatch Domain Events -> Outbox
        var entities = ChangeTracker.Entries<IAggregateRoot>()
            .Select(e => e.Entity)
            .Where(e => e.DomainEvents.Any())
            .ToList();
        
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

### SignalR Hub
```csharp
[Authorize]
public class TaskHub : Hub {
    public async Task JoinProject(string projectId) 
        => await Groups.AddToGroupAsync(Context.ConnectionId, $"project-{projectId}");
    
    public async Task LeaveProject(string projectId) 
        => await Groups.RemoveFromGroupAsync(Context.ConnectionId, $"project-{projectId}");
}

// Service для отправки уведомлений
public class SignalRNotificationService : INotificationService {
    private readonly IHubContext<TaskHub> _hub;
    
    public async Task NotifyTaskCreated(TaskDto task) 
        => await _hub.Clients.Group($"project-{task.ProjectId}").SendAsync("TaskCreated", task);
    
    public async Task NotifyTaskUpdated(TaskDto task) 
        => await _hub.Clients.Group($"project-{task.ProjectId}").SendAsync("TaskUpdated", task);
}
```

### JWT Authentication
```csharp
// Program.cs
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => {
        options.TokenValidationParameters = new TokenValidationParameters {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!))
        };
        options.Events = new JwtBearerEvents {
            OnMessageReceived = ctx => {
                var token = ctx.Request.Query["access_token"];
                if (!string.IsNullOrEmpty(token) && ctx.Request.Path.StartsWithSegments("/hubs"))
                    ctx.Token = token;
                return Task.CompletedTask;
            }
        };
    });

builder.Services.AddSignalR();
```

## 4️⃣ API Layer — Minimal API

```csharp
// Program.cs
var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();
app.UseRateLimiter();
app.MapHub<TaskHub>("/hubs/tasks");

var api = app.MapGroup("/api").RequireAuthorization();

api.MapGet("/tasks", async (ISender sender, Guid projectId) => 
    Results.Ok(await sender.Send(new GetTasksQuery(projectId))));

api.MapGet("/tasks/{id}", async (ISender sender, Guid id) => 
    await sender.Send(new GetTaskQuery(new TaskId(id))) is TaskDto dto ? Results.Ok(dto) : Results.NotFound());

api.MapPost("/tasks", async (ISender sender, CreateTaskCommand cmd) => 
    Results.Created($"/api/tasks/{await sender.Send(cmd)}", null));

api.MapPut("/tasks/{id}/assign", async (ISender sender, Guid id, AssignTaskCommand cmd) => {
    await sender.Send(cmd with { TaskId = new TaskId(id) });
    return Results.NoContent();
});

api.MapPost("/tasks/{id}/complete", async (ISender sender, Guid id) => {
    await sender.Send(new CompleteTaskCommand(new TaskId(id)));
    return Results.NoContent();
});

app.Run();
```

## 5️⃣ Blazor Client — Real-time UI

### SignalR Client Service
```csharp
public class TaskSignalRService {
    private HubConnection? _connection;
    private readonly ILogger<TaskSignalRService> _logger;
    
    public event Action<TaskDto>? OnTaskCreated;
    public event Action<TaskDto>? OnTaskUpdated;
    
    public async Task StartAsync(string token) {
        _connection = new HubConnectionBuilder()
            .WithUrl("https://api.taskmanager.com/hubs/tasks", options => {
                options.AccessTokenProvider = () => Task.FromResult(token)!;
            })
            .WithAutomaticReconnect()
            .Build();
        
        _connection.On<TaskDto>("TaskCreated", dto => OnTaskCreated?.Invoke(dto));
        _connection.On<TaskDto>("TaskUpdated", dto => OnTaskUpdated?.Invoke(dto));
        
        await _connection.StartAsync();
    }
    
    public async Task JoinProject(Guid projectId) 
        => await _connection?.InvokeAsync("JoinProject", projectId.ToString());
    
    public async Task StopAsync() => await _connection?.StopAsync();
}
```

### Blazor Component
```razor
@page "/projects/{ProjectId}/tasks"
@inject TaskSignalRService SignalR
@inject ITaskApiClient ApiClient
@implements IDisposable

<PageTitle>Tasks</PageTitle>

<h3>Tasks for Project @ProjectId</h3>

<TaskForm OnSubmit="CreateTask" />

<div class="task-list">
    @foreach (var task in Tasks) {
        <TaskCard Task="task" OnUpdate="UpdateTask" />
    }
</div>

@code {
    [Parameter] public Guid ProjectId { get; set; }
    private List<TaskDto> Tasks = new();
    
    protected override async Task OnInitializedAsync() {
        Tasks = await ApiClient.GetTasksAsync(ProjectId);
        SignalR.OnTaskCreated += HandleTaskCreated;
        SignalR.OnTaskUpdated += HandleTaskUpdated;
        await SignalR.JoinProject(ProjectId);
    }
    
    private void HandleTaskCreated(TaskDto task) {
        Tasks.Insert(0, task);
        StateHasChanged();
    }
    
    private void HandleTaskUpdated(TaskDto task) {
        var index = Tasks.FindIndex(t => t.Id == task.Id);
        if (index >= 0) { Tasks[index] = task; StateHasChanged(); }
    }
    
    public void Dispose() {
        SignalR.OnTaskCreated -= HandleTaskCreated;
        SignalR.OnTaskUpdated -= HandleTaskUpdated;
    }
}
```

## 6️⃣ Tests — Unit + Integration

### Unit Test (Handler)
```csharp
public class CreateTaskHandlerTests {
    private readonly Mock<ITaskRepository> _repoMock;
    private readonly Mock<IUnitOfWork> _uowMock;
    private readonly Mock<ICurrentUserService> _userMock;
    private readonly CreateTaskHandler _handler;
    
    public CreateTaskHandlerTests() {
        _repoMock = new Mock<ITaskRepository>();
        _uowMock = new Mock<IUnitOfWork>();
        _userMock = new Mock<ICurrentUserService>();
        _userMock.Setup(u => u.UserId).Returns(UserId.New());
        _handler = new CreateTaskHandler(_repoMock.Object, _uowMock.Object, _userMock.Object);
    }
    
    [Fact]
    public async Task Handle_ValidCommand_ReturnsTaskId() {
        var cmd = new CreateTaskCommand("Test Task", "Description", Guid.NewGuid());
        var result = await _handler.Handle(cmd, CancellationToken.None);
        
        result.Should().NotBeEmpty();
        _repoMock.Verify(r => r.AddAsync(It.IsAny<Task>(), It.IsAny<CancellationToken>()), Times.Once);
        _uowMock.Verify(u => u.SaveChangesAsync(It.IsAny<CancellationToken>()), Times.Once);
    }
}
```

### Integration Test (Testcontainers)
```csharp
public class TasksApiTests : IClassFixture<DatabaseFixture>, IAsyncLifetime {
    private readonly HttpClient _client;
    private readonly DatabaseFixture _fixture;
    
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
            Title = "Integration Test Task",
            Description = "Created via test",
            ProjectId = _fixture.TestProjectId
        });
        
        response.StatusCode.Should().Be(HttpStatusCode.Created);
    }
}
```

## 7️⃣ Docker & Kubernetes

### Dockerfile (Multi-stage, Distroless)
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

### Helm Chart (values.yaml)
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

## 8️⃣ CI/CD — GitHub Actions + ArgoCD

### GitHub Actions Workflow
```yaml
# .github/workflows/ci-cd.yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: taskmanager_test
        ports: [5432:5432]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
    - uses: actions/checkout@v4
    - name: Setup .NET
      uses: actions/setup-dotnet@v4
      with:
        dotnet-version: '8.0.x'
    - name: Restore
      run: dotnet restore
    - name: Build
      run: dotnet build --no-restore -c Release
    - name: Unit Tests
      run: dotnet test TaskManager.Tests.Unit --no-build -c Release --logger "trx"
    - name: Integration Tests
      run: dotnet test TaskManager.Tests.Integration --no-build -c Release --logger "trx"
    - name: Upload Coverage
      uses: codecov/codecov-action@v3

  docker:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
    - uses: actions/checkout@v4
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    - name: Login to GHCR
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    - name: Build and Push
      uses: docker/build-push-action@v5
      with:
        context: .
        file: src/TaskManager.Api/Dockerfile
        push: true
        tags: ghcr.io/${{ github.repository }}/api:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: docker
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - name: Update ArgoCD Application
      run: |
        kubectl set image deployment/taskmanager-api \
          taskmanager-api=ghcr.io/${{ github.repository }}/api:${{ github.sha }} \
          -n production
        kubectl rollout status deployment/taskmanager-api -n production --timeout=300s
```

### ArgoCD Application
```yaml
# argocd/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: taskmanager
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/taskmanager-config
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

## 📋 Чек-лист готовности

- [ ] Clean Architecture: 4 слоя, зависимости внутрь
- [ ] Domain: Aggregates, Value Objects, Domain Events, Repository interfaces
- [ ] Application: CQRS (Commands/Queries), MediatR, Pipeline Behaviors, FluentValidation
- [ ] Infrastructure: EF Core, Repositories, Outbox Pattern, SignalR, JWT, Background Jobs
- [ ] API: Minimal API, Auth, Rate Limiting, Health Checks, SignalR Hub
- [ ] Client: Blazor WASM, SignalR Client, State Management, Components
- [ ] Tests: Unit (xUnit, Moq, FluentAssertions), Integration (Testcontainers), E2E (Playwright)
- [ ] Docker: Multi-stage, Distroless, Non-root, Health Checks, .dockerignore
- [ ] K8s: Deployment, Service, Ingress, ConfigMap, Secret, HPA, PDB
- [ ] Helm: Chart с values, dependencies (PostgreSQL, Redis)
- [ ] CI/CD: GitHub Actions (test, build, push), ArgoCD (GitOps deploy)
- [ ] Observability: Serilog + Seq, OpenTelemetry Metrics/Traces, Prometheus/Grafana

## 🎉 Поздравляете!

Вы прошли полный курс C# от основ до продакшен-уровня. Этот проект объединяет:
- **Основы**: типы, коллекции, LINQ, async/await
- **ООП/Дизайн**: SOLID, Clean Architecture, DDD, CQRS
- **Продвинутые темы**: GC, SIMD, Source Generators, Pattern Matching
- **Инфраструктура**: Docker, K8s, Helm, Service Mesh, CI/CD
- **Надежность**: Testing, Observability, Security, Resilience

**Следующие шаги**: углубитесь в темы, которые интересны: gRPC, Event Sourcing, ML.NET, NativeAOT, WebAssembly, IoT.

## 🔗 Полезные ссылки для продолжения

- .NET Docs: https://learn.microsoft.com/dotnet/
- ASP.NET Core: https://learn.microsoft.com/aspnet/core/
- EF Core: https://learn.microsoft.com/ef/core/
- Blazor: https://learn.microsoft.com/aspnet/core/blazor/
- Kubernetes: https://kubernetes.io/docs/home/
- CNCF Landscape: https://landscape.cncf.io/
""",
    "practice_tasks": [
        "Создайте Clean Architecture решение с 4 проектами. Настройте зависимости.",
        "Реализуйте Domain слой: Task aggregate, Value Objects, Domain Events.",
        "Реализуйте Application слой: CQRS команды/запросы, MediatR handlers, FluentValidation.",
        "Настройте Infrastructure: EF Core DbContext, Outbox pattern, SignalR, JWT.",
        "Постройте Minimal API endpoints с авторизацией и SignalR Hub.",
        "Создайте Blazor WASM клиент с SignalR real-time обновлениями.",
        "Напишите Unit тесты для Handlers и Domain логики (xUnit, Moq, FluentAssertions).",
        "Напишите Integration тесты с Testcontainers (PostgreSQL) и WebApplicationFactory.",
        "Создайте Multi-stage Dockerfile с distroless базой, non-root пользователем, health check.",
        "Настройте Helm чарт с зависимостями PostgreSQL и Redis. Настройте values-prod.yaml.",
        "Настройте GitHub Actions pipeline: test → build → docker push → ArgoCD deploy.",
        "Настройте Observability: Serilog + Seq, OpenTelemetry Metrics/Traces → Prometheus/Grafana."
    ],
    "common_errors": [
        {"mistake": "Нарушение Dependency Rule (Domain ссылается на Infrastructure)", "correct": "Интерфейсы в Application, реализации в Infrastructure"},
        {"mistake": "Анемичная доменная модель (логика в Handlers)", "correct": "Переносите бизнес-логику в Aggregates/Entities"},
        {"mistake": "Отсутствие Outbox Pattern для Domain Events", "correct": "Сохраняйте события в Outbox таблицу в той же транзакции"},
        {"mistake": "JWT секрет в коде / appsettings.json", "correct": "User Secrets (dev), Key Vault / Env Vars (prod)"},
        {"mistake": "Отсутствие Rate Limiting и Health Checks", "correct": "Всегда добавляйте в API"},
        {"mistake": "Dockerfile: COPY . . перед restore", "correct": "COPY csproj → restore → COPY . → publish"},
        {"mistake": "Запуск контейнера от root", "correct": "USER 65532:65532 в distroless"},
        {"mistake": "K8s без resources.requests/limits и probes", "correct": "Обязательны для production"},
        {"mistake": "Secrets в Git / Helm values.yaml", "correct": "Sealed Secrets, External Secrets Operator, Vault"},
        {"mistake": "CI/CD без тестов", "correct": "Unit + Integration тесты обязательны в pipeline"}
    ],
    "resources": [
        "Clean Architecture: https://github.com/jasontaylordev/CleanArchitecture",
        "eShopOnWeb (Microsoft reference): https://github.com/dotnet-architecture/eShopOnWeb",
        "Blazor Docs: https://learn.microsoft.com/aspnet/core/blazor/",
        "Testcontainers: https://dotnet.testcontainers.org/",
        "ArgoCD: https://argo-cd.readthedocs.io/",
        "CNCF Landscape: https://landscape.cncf.io/"
    ],
    "key_takeaways": [
        "Clean Architecture — 4 слоя, зависимости только внутрь, интерфейсы в Application",
        "DDD — Aggregates, Value Objects, Domain Events, Repository pattern",
        "CQRS + MediatR — Commands/Queries, Pipeline Behaviors (Validation, Transaction, Logging)",
        "EF Core — Outbox Pattern для надежности Domain Events, миграции",
        "SignalR — real-time уведомления, Groups для проектов, JWT в query string для WebSockets",
        "Blazor WASM — SignalR клиент, автоматическое переподключение, state management",
        "Testing — Unit (Moq), Integration (Testcontainers), E2E (Playwright)",
        "Docker — Multi-stage, Distroless, Non-root, Health Checks, Layer Caching",
        "K8s/Helm — Deployment, Service, Ingress, HPA, PDB, ConfigMap/Secret, dependencies",
        "CI/CD — GitHub Actions (test, build, push), ArgoCD (GitOps), semver tags",
        "Observability — Serilog, OpenTelemetry, Prometheus/Grafana, Jaeger/Zipkin"
    ],
    "estimated_minutes": 120,
    "language_slug": "csharp",
    "lesson_order": 33,
    "name_en": "Lesson: Final Project — Full Stack App",
    "short_description_en": "Clean Architecture, ASP.NET Core API, Blazor, SignalR, Tests, Docker, K8s, CI/CD"
}

# ============================================================
# MAIN EXECUTION
# ============================================================

def convert_md_to_blocks(md: str):
    """Convert markdown to list of content blocks with code extraction."""
    return markdown_to_blocks(md)


def write_lesson(num, data):
    """Write lesson to JSON file with proper formatting."""
    path = f'fixtures/lessons/csharp/{num:02d}.json'
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    # Convert markdown content to blocks
    if 'content_md' in data:
        data['content_blocks'] = convert_md_to_blocks(data.pop('content_md'))
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Written lesson {num:02d}: {data["title"][:60]}...')


if __name__ == '__main__':
    print("Generating lessons 14-33...")
    for num in range(14, 34):
        if num in LESSONS:
            write_lesson(num, LESSONS[num])
        else:
            print(f"WARNING: Lesson {num} not defined!")
    print("All lessons generated!")