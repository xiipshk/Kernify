#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

lesson = {
  "title": "Урок 11: Делегаты и события — инверсия управления",
  "slug": "delegaty-i-sobytiya-inversiya-upravleniya",
  "short_description": "Делегаты, multicast, события, event pattern, EventHandler, слабые события, async события, pattern matching с делегатами",
  "goals": [
    "Понимать, что такое делегат и как он отличается от интерфейса",
    "Работать с multicast делегатами и цепочками вызовов",
    "Правильно объявлять и поднимать события (event pattern)",
    "Работать с EventHandler<TEventArgs> и кастомными EventArgs",
    "Понимать проблему утечек памяти и слабые события",
    "Работать с async событиями и pattern matching для делегатов"
  ],
  "content_blocks": [
    {
      "type": "heading",
      "level": 2,
      "content": "🎯 Что вы узнаете"
    },
    {
      "type": "list",
      "items": [
        "Что такое делегат: типобезопасный указатель на метод",
        "Multicast делегаты: комбинирование нескольких методов",
        "События (event): инкапсуляция делегатов, паттерн publisher/subscriber",
        "EventHandler<TEventArgs>: стандартный паттерн событий",
        "Слабые события (WeakEventManager): предотвращение утечек памяти",
        "Async события: асинхронные обработчики, Task-based подход"
      ],
      "ordered": False
    },
    {
      "type": "heading",
      "level": 2,
      "content": "💡 Зачем нужны делегаты: инверсия управления"
    },
    {
      "type": "text",
      "content": "Представьте: вы пишете сортировку. Алгоритм один, но критерий сравнения разный — по возрастанию, убыванию, по длине строки, по дате. Без делегатов пришлось бы писать отдельный метод для каждого случая или использовать if/else.\n\nС делегатом:\n\n```csharp\n// Делегат — тип, описывающий сигнатуру метода\npublic delegate int Comparison<T>(T x, T y);\n\n// Сортировка принимает делегат как параметр\npublic static void Sort<T>(T[] array, Comparison<T> comparison) { }\n\n// Использование: передаем ЛЮБОЙ подходящий метод\nSort(numbers, (a, b) => a - b);           // по возрастанию\nSort(numbers, (a, b) => b - a);           // по убыванию\nSort(words, (a, b) => a.Length - b.Length); // по длине\n```\n\n**Делегат** — это тип, который представляет ссылку на метод с определенной сигнатурой. Это **инверсия управления**: алгоритм не знает, *как* сравнивать, он *делегирует* это решение вызывающему коду."
    },
    {
      "type": "heading",
      "level": 3,
      "content": "🎯 Делегаты vs Интерфейсы: когда что использовать"
    },
    {
      "type": "text",
      "content": "| Аспект | Делегат | Интерфейс |\n|---|---|---|\n| Назначение | Один метод (действие) | Контракт (несколько методов/свойств) |\n| Состояние | Нет (stateless) | Может иметь состояние |\n| Множественность | Multicast (список методов) | Одна реализация на класс |\n| Использование | Callback, стратегия одного действия | Контракт поведения, DI |\n| Анонимность | Лямбды, анонимные методы | Требует класса |\n\n**Правило**: если нужно **один метод** как параметр/возврат — **делегат**. Если **контракт с состоянием/несколькими методами** — **интерфейс**."
    },
    {
      "type": "heading",
      "level": 3,
      "content": "🔗 Multicast делегаты: цепочка вызовов"
    },
    {
      "type": "text",
      "content": "Делегаты в C# **мультикаст** — могут хранить список методов. При вызове выполняются **все** по порядку добавления.\n\n```csharp\npublic delegate void Notification(string message);\n\nNotification notify = null;\nnotify += EmailNotify;    // добавили\nnotify += SmsNotify;      // добавили\nnotify += PushNotify;     // добавили\n\nnotify(\"Hello!\");  // Вызовет ВСЕ три метода по порядку\n\nnotify -= SmsNotify;  // убрали SMS\n```\n\n**Важно**: возвращаемое значение — только от **последнего** метода в цепочке. Если методы возвращают значения — используйте `GetInvocationList()` и вызывайте вручную."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "public delegate int Operation(int a, int b);\n\nOperation ops = null;\nops += (a, b) => a + b;\nops += (a, b) => a - b;\nops += (a, b) => a * b;\n\nint result = ops(10, 5);  // result = 50 (только последнее: 10 * 5)\n\n// Чтобы получить все результаты:\nvar results = ops.GetInvocationList()\n    .Cast<Operation>()\n    .Select(d => d(10, 5))\n    .ToList();  // [15, 5, 50]"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "📢 События (event): инкапсуляция multicast делегата"
    },
    {
      "type": "text",
      "content": "**Событие** — это обертка над делегатом, которая:\n- Позволяет **только добавлять/удалять** обработчики (`+=`, `-=`)\n- **Запрещает** прямой вызов и присваивание (`=`)\n- Обеспечивает **инкапсуляцию**: класс сам решает, когда поднимать событие\n\n**Паттерн события (Event Pattern)**:\n1. Делегат-тип для обработчика (обычно `EventHandler<TEventArgs>`)\n2. Событие с ключевым словом `event`\n3. Защищенный виртуальный метод `OnEventName` для подъема\n4. Проверка на `null` перед вызовом (или `?.Invoke`)"
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "// Стандартный паттерн события\npublic class Timer {\n    // 1. Делегат (обычно EventHandler<T>)\n    public event EventHandler<TickEventArgs> Tick;\n\n    // 2. Метод подъема (protected virtual для наследования)\n    protected virtual void OnTick(TickEventArgs e) {\n        // Thread-safe вызов: копируем делегат, проверяем на null\n        Tick?.Invoke(this, e);\n    }\n\n    public void Start() {\n        while (true) {\n            Thread.Sleep(1000);\n            OnTick(new TickEventArgs(DateTime.Now));\n        }\n    }\n}\n\npublic class TickEventArgs : EventArgs {\n    public DateTime Time { get; }\n    public TickEventArgs(DateTime time) => Time = time;\n}\n\n// Использование\ntimer.Tick += (sender, e) => Console.WriteLine($\"Tick at {e.Time}\");\ntimer.Tick += LogToFile;  // второй обработчик"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "📦 EventHandler<TEventArgs> — стандартный паттерн"
    },
    {
      "type": "text",
      "content": "В BCL есть готовый делегат: `EventHandler<TEventArgs>` где `TEventArgs : EventArgs`.\n\nСигнатура: `void Handler(object sender, TEventArgs e)`\n- `sender` — объект, поднявший событие\n- `e` — данные события (наследник `EventArgs`)\n\n**Правила хорошего тона**:\n- Наследуйте аргументы от `EventArgs`\n- Имя класса аргументов: `<EventName>EventArgs`\n- Свойства только для чтения (`get;`) — данные события не меняются\n- Для отменяемых событий используйте `CancelEventArgs`"
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "// Стандартные EventArgs\npublic class UserRegisteredEventArgs : EventArgs {\n    public User User { get; }\n    public DateTime RegisteredAt { get; }\n    public UserRegisteredEventArgs(User user) {\n        User = user;\n        RegisteredAt = DateTime.UtcNow;\n    }\n}\n\n// Отменяемое событие\npublic class UserRegisteringEventArgs : CancelEventArgs {\n    public User User { get; }\n    public UserRegisteringEventArgs(User user) => User = user;\n}\n\n// Использование\npublic class UserService {\n    public event EventHandler<UserRegisteringEventArgs> UserRegistering;\n    public event EventHandler<UserRegisteredEventArgs> UserRegistered;\n\n    public void Register(User user) {\n        var args = new UserRegisteringEventArgs(user);\n        OnUserRegistering(args);\n        \n        if (!args.Cancel) {\n            // регистрация...\n            OnUserRegistered(new UserRegisteredEventArgs(user));\n        }\n    }\n\n    protected virtual void OnUserRegistering(UserRegisteringEventArgs e) =>\n        UserRegistering?.Invoke(this, e);\n    protected virtual void OnUserRegistered(UserRegisteredEventArgs e) =>\n        UserRegistered?.Invoke(this, e);\n}"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "🔌 Слабые события (Weak Events): решение утечек памяти"
    },
    {
      "type": "text",
      "content": "**Проблема**: подписчик на событие создает сильную ссылку от издателя к подписчику. Если подписчик не отписался (`-=`), GC не может его собрать — **утечка памяти**.\n\n**Решения**:\n1. **Всегда отписывайтесь** в `Dispose` / деструкторе / `Unloaded`\n2. **WeakEventManager** (WPF) — слабая ссылка на обработчик\n3. **Слабые делегаты** вручную через `WeakReference`\n4. **События как интерфейсы** — `IObservable<T>` / `IObserver<T>` (Rx.NET)"
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "// Ручная реализация слабого события через WeakReference\npublic class WeakEvent<TEventArgs> where TEventArgs : EventArgs {\n    private readonly List<WeakReference<EventHandler<TEventArgs>>> _handlers = new();\n\n    public void Add(EventHandler<TEventArgs> handler) {\n        _handlers.Add(new WeakReference<EventHandler<TEventArgs>>(handler));\n    }\n\n    public void Remove(EventHandler<TEventArgs> handler) {\n        _handlers.RemoveAll(wr => !wr.TryGetTarget(out var h) || h == handler);\n    }\n\n    public void Invoke(object sender, TEventArgs e) {\n        var dead = new List<WeakReference<EventHandler<TEventArgs>>>();\n        foreach (var wr in _handlers) {\n            if (wr.TryGetTarget(out var handler)) {\n                handler(sender, e);\n            } else {\n                dead.Add(wr);\n            }\n        }\n        foreach (var d in dead) _handlers.Remove(d);\n    }\n}"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "⚡ Async события: асинхронные обработчики"
    },
    {
      "type": "text",
      "content": "Стандартный `EventHandler` синхронен. Для async обработчиков нужен другой подход:\n\n```csharp\npublic delegate Task AsyncEventHandler<TEventArgs>(object sender, TEventArgs e);\n\npublic event AsyncEventHandler<UserRegisteredEventArgs> UserRegisteredAsync;\n\nprotected virtual async Task OnUserRegisteredAsync(UserRegisteredEventArgs e) {\n    var handlers = UserRegisteredAsync?.GetInvocationList();\n    if (handlers != null) {\n        var tasks = handlers.Cast<AsyncEventHandler<UserRegisteredEventArgs>>()\n            .Select(h => h(this, e));\n        await Task.WhenAll(tasks);  // параллельное выполнение\n    }\n}\n```\n\n**Важно**: исключения в одном обработчике не должны ломать остальные — используйте `Task.WhenAll` с try/catch внутри."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "public class AsyncEvent<TEventArgs> where TEventArgs : EventArgs {\n    private readonly List<Func<object, TEventArgs, Task>> _handlers = new();\n\n    public void Add(Func<object, TEventArgs, Task> handler) => _handlers.Add(handler);\n    public void Remove(Func<object, TEventArgs, Task> handler) => _handlers.Remove(handler);\n\n    public async Task InvokeAsync(object sender, TEventArgs e) {\n        var tasks = _handlers.Select(h => SafeInvoke(h, sender, e)).ToList();\n        await Task.WhenAll(tasks);\n    }\n\n    private async Task SafeInvoke(Func<object, TEventArgs, Task> handler, object sender, TEventArgs e) {\n        try { await handler(sender, e); }\n        catch (Exception ex) { /* log, не прерываем остальные */ }\n    }\n}"
    },
    {
      "type": "heading",
      "level": 2,
      "content": "🔍 Pattern Matching с делегатами"
    },
    {
      "type": "text",
      "content": "C# 7+ позволяет использовать pattern matching для работы с делегатами:"
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "Delegate d = SomeMethod;\n\n// Type pattern\nif (d is Action<int> a) { a(42); }\nelse if (d is Func<int, int> f) { var r = f(5); }\n\n// Switch expression (C# 8+)\nstring description = d switch {\n    Action => \"Action (void)\",\n    Func<int, int> => \"Func<int, int>\",\n    Action<int, string> => \"Action<int, string>\",\n    null => \"Null delegate\",\n    _ => \"Other delegate\"\n};\n\n// Property pattern (C# 8+)\nif (d is { Method: { Name: \"Callback\" } }) { }\n\n// Null-coalescing для делегата\nvar handler = onClick ??= () => Console.WriteLine(\"Default\");"
    },
    {
      "type": "heading",
      "level": 2,
      "content": "⚠️ Типичные ошибки новичков"
    },
    {
      "type": "table",
      "headers": [
        "Ошибка",
        "Как проявляется",
        "Как правильно"
      ],
      "rows": [
        [
          "Вызов события без проверки на null",
          "`Tick(this, e);` — NullReferenceException если нет подписчиков",
          "Используйте `Tick?.Invoke(this, e);` или `EventHandler` с `?.Invoke`"
        ],
        [
          "Прямое присваивание события",
          "`Click = Handler;` — ошибка компиляции (event не позволяет =)",
          "Только `+=` и `-=` для событий"
        ],
        [
          "Забыли отписаться от события",
          "Утечка памяти: подписчик живёт вечно",
          "Реализуйте `IDisposable` и делайте `-=` в `Dispose()`"
        ],
        [
          "Возврат значения в multicast делегате",
          "Возвращается только результат последнего метода",
          "Используйте `GetInvocationList()` для сбора всех результатов"
        ],
        [
          "Блокировка в обработчике события",
          "Deadlock: событие поднимается под локом, обработчик ждет тот же лок",
          "Не поднимайте события под локом. Используйте `Task.Run` или асинхронные события"
        ],
        [
          "Использование event для публичного API вместо делегата",
          "Нужно передать callback в метод — событие не подходит",
          "Для callback используйте `Func/Action/Delegate`, не `event`"
        ],
        [
          "Асинхронный void в обработчике",
          "`async void Handler()` — исключения теряются, порядок не гарантирован",
          "Используйте `async Task` и асинхронные события (`Task`-based)"
        ]
      ]
    },
    {
      "type": "heading",
      "level": 2,
      "content": "🛠 Практика: закрепите навык"
    },
    {
      "type": "list",
      "items": [
        "Создайте класс `EventBus` с методами `Subscribe<T>(Action<T>)`, `Publish<T>(T event)`. Реализуйте как синхронную, так и асинхронную версию.",
        "Создайте класс `Observable<T>` с событием `ValueChanged` (oldValue, newValue). Реализуйте привязку: `binding.Bind(textBox, \"Text\", viewModel, \"Name\")`.",
        "Реализуйте слабое событие `WeakEvent<T>` с `WeakReference`. Проверьте: подписчик собирается GC после потери сильных ссылок.",
        "Исправьте ошибки:\n```csharp\nclass Button {\n    public event Action Click;  // Ошибка: нет EventArgs\n    public void OnClick() => Click();  // Ошибка: нет ?.Invoke\n}\n\nclass Form {\n    public event EventHandler<EventArgs> Load;\n    protected void OnLoad() { Load(this, EventArgs.Empty); }  // Ошибка: нет ?.Invoke\n}\n```"
      ],
      "ordered": True
    },
    {
      "type": "heading",
      "level": 2,
      "content": "📌 Кратко о главном"
    },
    {
      "type": "list",
      "items": [
        "Делегат — типобезопасный указатель на метод. `Func<T, TResult>`, `Action<T>`, `Predicate<T>` — готовые делегаты.",
        "Multicast: `+=` добавляет, `-=` удаляет. Вызов — все методы по порядку. Возврат — только последний.",
        "Событие (`event`) — инкапсуляция делегата. Только `+=`/`-=`, вызов через `?.Invoke`.",
        "Паттерн события: `EventHandler<TEventArgs>`, `EventArgs`, `OnEventName`, `?.Invoke`.",
        "Async события: `Task`-based делегаты, `Task.WhenAll`, обработка ошибок в каждом обработчике.",
        "Утечки памяти: всегда отписывайтесь (`-=`), используйте `WeakEventManager` или `WeakReference`.",
        "Pattern matching: `is Action<int>`, `switch` на делегатах, property patterns."
      ],
      "ordered": False
    },
    {
      "type": "heading",
      "level": 2,
      "content": "🔗 Полезные ссылки"
    },
    {
      "type": "list",
      "items": [
        "Microsoft Docs — Delegates: https://learn.microsoft.com/dotnet/csharp/programming-guide/delegates/",
        "Microsoft Docs — Events: https://learn.microsoft.com/dotnet/csharp/programming-guide/events/",
        "Microsoft Docs — Weak Events: https://learn.microsoft.com/dotnet/desktop/wpf/advanced/weak-event-patterns",
        "Microsoft Docs — Async Events: https://learn.microsoft.com/dotnet/standard/events/",
        "Stephen Cleary — Async Events: https://blog.stephencleary.com/2013/02/async-events.html"
      ],
      "ordered": False
    }
  ],
  "practice_tasks": [
    "Создайте класс `EventBus` с методами `Subscribe<T>(Action<T>)`, `Publish<T>(T event)`. Реализуйте как синхронную, так и асинхронную версию.",
    "Создайте класс `Observable<T>` с событием `ValueChanged` (oldValue, newValue). Реализуйте привязку: `binding.Bind(textBox, \"Text\", viewModel, \"Name\")`.",
    "Реализуйте слабое событие `WeakEvent<T>` с `WeakReference`. Проверьте: подписчик собирается GC после потери сильных ссылок.",
    "Исправьте ошибки:\n```csharp\nclass Button {\n    public event Action Click;  // Ошибка: нет EventArgs\n    public void OnClick() => Click();  // Ошибка: нет ?.Invoke\n}\n\nclass Form {\n    public event EventHandler<EventArgs> Load;\n    protected void OnLoad() { Load(this, EventArgs.Empty); }  // Ошибка: нет ?.Invoke\n}\n```"
  ],
  "common_errors": [
    {
      "mistake": "Вызов события без проверки на null",
      "correct": "Используйте `Tick?.Invoke(this, e);` или `EventHandler` с `?.Invoke`"
    },
    {
      "mistake": "Прямое присваивание события",
      "correct": "Только `+=` и `-=` для событий"
    },
    {
      "mistake": "Забыли отписаться от события",
      "correct": "Реализуйте `IDisposable` и делайте `-=` в `Dispose()`"
    },
    {
      "mistake": "Возврат значения в multicast делегате",
      "correct": "Используйте `GetInvocationList()` для сбора всех результатов"
    },
    {
      "mistake": "Блокировка в обработчике события",
      "correct": "Не поднимайте события под локом. Используйте `Task.Run` или асинхронные события"
    },
    {
      "mistake": "Использование event для публичного API вместо делегата",
      "correct": "Для callback используйте `Func/Action/Delegate`, не `event`"
    },
    {
      "mistake": "Асинхронный void в обработчике",
      "correct": "Используйте `async Task` и асинхронные события (`Task`-based)"
    }
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
  "lesson_order": 11,
  "name_en": "Lesson: Delegates and Events",
  "short_description_en": "Learn delegates, multicast, events, async events in C#"
}

with open('fixtures/lessons/csharp/11.json', 'w', encoding='utf-8') as f:
    json.dump(lesson, f, ensure_ascii=False, indent=2)
    f.write('\n')

print("Урок 11 успешно перезаписан!")
PYEOF