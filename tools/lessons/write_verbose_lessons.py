#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавляет подробные объяснения терминов ко всем 11 урокам C#
для полного понимания новичками.
"""

import json
from pathlib import Path

# Словарь терминов с подробными объяснениями для новичка
TERM_EXPLANATIONS = {
    # Базовые концепции
    "делегат": "**Делегат** — это тип, который хранит ссылку на метод. Представьте, что это «указатель на функцию», но типизированный и безопасный. Вы можете передать метод как аргумент в другой метод, сохранить в переменную, вызвать позже. В C# есть готовые: `Action` (метод без возврата), `Func<T>` (метод с возвратом), `Predicate<T>` (проверка условия).",
    "multicast": "**Мультикаст (multicast)** — способность делегата хранить список методов и вызывать их все по очереди при вызове. Используется `+=` для добавления, `-=` для удаления. Все методы выполняются по порядку, возвращаемое значение — только от последнего.",
    "событие (event)": "**Событие (event)** — обертка над делегатом, которая позволяет только подписываться (`+=`) и отписываться (`-=`), но не вызывать напрямую и не перезаписывать (`=`). Это защита: только владелец события решает, когда его поднять. Паттерн: `event EventHandler<T> Name; protected virtual void OnName() => Name?.Invoke(this, args);`.",
    "EventHandler": "**EventHandler<TEventArgs>** — стандартный делегат для событий в .NET. Сигнатура: `void Handler(object sender, TEventArgs e)`. `sender` — кто поднял событие, `e` — данные события. Всегда наследуйте аргументы от `EventArgs`.",
    "EventArgs": "**EventArgs** — базовый класс для данных события. Создавайте свои: `class MyEventArgs : EventArgs { public int Value { get; } }`. Для отмены используйте `CancelEventArgs` (свойство `Cancel`).",
    "лямбда": "**Лямбда-выражение** — краткий способ написать анонимный метод. Синтаксис: `параметры => тело`. Примеры: `x => x * 2`, `(a, b) => a + b`, `() => DoSomething()`. Используются для делегатов, LINQ, коллбэков.",
    "многопоточность": "**Многопоточность** — выполнение нескольких потоков кода одновременно. В C# используется `Thread`, `Task`, `async/await`. Главные проблемы: race condition (состояние гонки), deadlock (взаимная блокировка), синхронизация доступа к данным (`lock`, `Monitor`, `Interlocked`, `SemaphoreSlim`).",
    "async/await": "**async/await** — синтаксический сахар для асинхронного программирования. `async` помечает метод как асинхронный (возвращает `Task`/`Task<T>`). `await` приостанавливает выполнение до завершения задачи, не блокируя поток. Позволяет писать асинхронный код как синхронный.",
    "Task": "**Task / Task<T>** — представляет асинхронную операцию. `Task` — операция без результата, `Task<T>` — с результатом типа T. Методы: `Start()`, `Wait()`, `Result`, `ContinueWith()`, `WhenAll()`, `WhenAny()`. Не блокирует поток при `await`.",
    "поток (Thread)": "**Поток (Thread)** — легковесный процесс выполнения кода. У каждого приложения есть главный поток (UI поток). `Thread` — низкоуровневое управление, `Task` — высокоуровневое (ThreadPool). `Thread.Sleep()` блокирует поток, `Task.Delay()` — асинхронная пауза.",
    "lock": "**lock** — оператор синхронизации, гарантирующий, что только один поток выполняет блок кода. `lock (obj) { ... }` — эквивалент `Monitor.Enter/Exit` с `try/finally`. Аргумент должен быть ссылочным типом (обычно `private readonly object _lock = new();`).",
    "async void": "**async void** — асинхронный метод без возврата значения. ОПАСЕН: исключения теряются, нельзя `await`ить, порядок выполнения не гарантирован. Используйте ТОЛЬКО для обработчиков событий. Во всех остальных случаях — `async Task`.",
    "Task.Run": "**Task.Run** — запускает работу в пуле потоков (ThreadPool). Используйте для CPU-bound операций, чтобы не блокировать UI поток. Не используйте для I/O-bound (там `await` сам управляет).",
    "ThreadPool": "**ThreadPool** — пул рабочих потоков, управляемый CLR. `Task.Run`, `Task.Factory.StartNew`, асинхронные методы — все используют ThreadPool. Не создавайте `new Thread()` вручную без нужды.",
    "deadlock": "**Deadlock (взаимная блокировка)** — ситуация, когда два потока ждут друг друга (каждый держит лок, который нужен другому). Избегайте: не вызывайте `.Result`/`.Wait()` на асинхронных задачах, не поднимайте события под локом, используйте `async/await` везде.",
    "race condition": "**Race condition (состояние гонки)** — ошибка, когда результат зависит от порядка выполнения потоков. Пример: `x++` в двух потоках может дать неверный результат. Решение: `lock`, `Interlocked.Increment`, `Immutable` коллекции.",
    "boxing": "**Boxing (упаковка)** — преобразование value type (int, struct) в object/reference type. Создает объект в куче, копирует значение. Расходует память и время. `int x = 5; object o = x;` — boxing. Дженерики (`List<int>`) убирают boxing.",
    "unboxing": "**Unboxing (распаковка)** — обратная операция: извлечение value type из object. `object o = 5; int x = (int)o;` — unboxing. Требует проверки типа, может бросить `InvalidCastException`.",
    "value type": "**Value type (значимый тип)** — `struct`, `enum`, примитивы (`int`, `bool`, `double`). Хранится в стеке (обычно), копируется при присваивании, не может быть null (кроме `Nullable<T>`). Примеры: `int`, `DateTime`, `Guid`, `Point`.",
    "reference type": "**Reference type (ссылочный тип)** — `class`, `interface`, `delegate`, `array`, `string`. Хранится в куче, переменная хранит ссылку. Присваивание копирует ссылку, не объект. Может быть `null`. Примеры: `string`, `List<T>`, `class MyClass`.",
    "null": "**null** — отсутствие значения. Для reference types — отсутствие ссылки. Для value types — только через `Nullable<T>` (`int?`). Операторы: `??` (null-coalescing), `?.` (null-conditional), `!` (null-forgiving). `null` — источник `NullReferenceException`.",
    "nullable": "**Nullable<T> (T?)** — обертка над value type, позволяющая хранить `null`. `int? x = null;` — это `Nullable<int>`. Свойства: `HasValue`, `Value`. Операторы: `??`, `?.`, `?[]`. Не работает для reference types (они уже nullable).",
    "struct": "**struct** — значимый тип, определяемый пользователем. Нет наследования (кроме интерфейсов), нет деструктора, нельзя `null` (кроме `Nullable<T>`). Используйте для маленьких неизменяемых данных (Point, DateTime, Money). Копируется при присваивании.",
    "class": "**class** — ссылочный тип, поддерживает наследование, полиморфизм, интерфейсы. Хранится в куче, передается по ссылке. Может быть `abstract`, `sealed`, `static`, `partial`. Конструкторы, деструкторы, свойства, методы, события.",
    "record": "**record** (C# 9+) — ссылочный тип с value-based equality, неизменяемостью (init-only свойства), `with`-выражениями для копии с изменениями. Идеален для DTO, данных. `record Person(string Name, int Age);` — автоматически: конструктор, свойства, `Equals`, `GetHashCode`, `ToString`, `with`.",
    "interface": "**interface** — контракт, описывающий ЧТО делает тип, но не КАК. Только сигнатуры (методы, свойства, события, индексаторы). Все члены неявно `public`. Класс может реализовывать много интерфейсов. C# 8+: default реализации, статические члены.",
    "abstract": "**abstract** — модификатор для класса/метода/свойства. Абстрактный класс — нельзя создать экземпляр, только наследовать. Абстрактный член — без реализации, обязан переопределить в наследнике. Абстрактный класс может иметь реализацию.",
    "virtual/override": "**virtual** — метод можно переопределить в наследнике. **override** — переопределение виртуального/абстрактного метода. Полиморфизм: при вызове через базовый тип выполняется версия наследника. `sealed override` — запрет дальнейшего переопределения.",
    "sealed": "**sealed** — для класса: нельзя наследовать. Для метода: нельзя переопределять дальше. Используйте для безопасности, производительности (JIT может инлайнить), неизменяемости.",
    "static": "**static** — член принадлежит ТИПУ, а не экземпляру. Вызов: `TypeName.Member`. Статический конструктор (`.cctor`) вызывается один раз перед первым доступом. Статические поля — общие для всех экземпляров. Нельзя `override`, `virtual`, `override`.",
    "readonly": "**readonly** — поле можно назначить только в конструкторе или при объявлении. Для reference types — ссылка неизменна, но объект внутри можно менять. Для immutable типов — гарантия неизменности.",
    "const": "**const** — константа времени компиляции. Значение задается в коде, не меняется. Неявно `static`. Только примитивы, string, enum, null. Используйте для математических констант, версий, настроек, известных на этапе компиляции.",
    "property": "**property (свойство)** — метод доступа к данным, выглядит как поле. `get` — чтение, `set` — запись. Автосвойство: `public int Age { get; set; }`. С логикой: `private int _age; public int Age { get => _age; set => _age = value > 0 ? value : 0; }`. `init` (C# 9+) — только в конструкторе/инициализаторе.",
    "indexer": "**indexer** — позволяет обращаться к экземпляру как к массиву: `obj[i]`. Синтаксис: `public T this[int index] { get => ...; set => ...; }`. Используется в коллекциях, матрицах, обертках.",
    "operator overloading": "**operator overloading** — перегрузка операторов для своих типов. `public static Complex operator +(Complex a, Complex b)`. Доступны: `+ - * / % & | ^ << >> == != < > <= >= true false + - ! ~ ++ --`. Нельзя: `= . ?: ?? -> new is as is`.",
    "extension method": "**extension method** — метод расширения для существующего типа. `public static TResult Extend(this TSource source, ...)`. Вызов: `source.Extend()`. Должен быть в `static` классе. LINQ — это extension methods для `IEnumerable<T>`.",
    "LINQ": "**LINQ (Language Integrated Query)** — интегрированный язык запросов. Синтаксис: `from x in source where x > 5 select x` или методы: `source.Where(x => x > 5)`. Отложенное выполнение (`IEnumerable`): запрос выполняется при переборе (`foreach`, `ToList()`). `IQueryable` — для БД (переводится в SQL).",
    "IEnumerable": "**IEnumerable<T>** — интерфейс для перебора последовательности. Один метод: `GetEnumerator()`. База для LINQ, `foreach`, `yield return`. Отложенное выполнение: запрос не выполняется до перебора.",
    "yield return": "**yield return** — возвращает элемент последовательности и приостанавливает выполнение. Используется в `IEnumerable<T>` методах для ленивого создания последовательности. Сохраняет состояние метода между вызовами.",
    "IQueryable": "**IQueryable<T>** — интерфейс для запросов, которые можно транслировать (например, в SQL). Наследует `IEnumerable<T>`. Используется в Entity Framework: запрос строится в памяти, выполняется в БД при переборе (`ToList()`, `First()`).",
    "Entity Framework": "**Entity Framework (EF Core)** — ORM для .NET. Маппит классы на таблицы БД. `DbContext` — контекст, `DbSet<T>` — таблица. LINQ запросы переводятся в SQL. Миграции для схемы. Tracking изменений, Unit of Work.",
    "DI": "**Dependency Injection (DI)** — паттерн: зависимости получаются извне (через конструктор), а не создаются внутри. Контейнер (ASP.NET Core built-in, Autofac) управляет жизненным циклом: `Transient` (новый каждый раз), `Scoped` (один на запрос), `Singleton` (один на приложение).",
    "SOLID": "**SOLID** — 5 принципов ООП:\n1. **S**RP — класс имеет одну ответственность.\n2. **O**CP — открыт для расширения, закрыт для изменения.\n3. **L**SP — наследник может заменить базовый без ломания логики.\n4. **I**SP — лучше много мелких интерфейсов, чем один большой.\n5. **D**IP — завись от абстракций, не от конкретных классов.",
    "DRY": "**DRY (Don't Repeat Yourself)** — не дублируйте код. Выносите общую логику в методы/классы. Но не фанатично — иногда дублирование лучше, чем преждевременная абстракция.",
    "KISS": "**KISS (Keep It Simple, Stupid)** — пишите простой код. Не усложняйте без нужды. Простой код проще читать, тестировать, поддерживать.",
    "YAGNI": "**YAGNI (You Aren't Gonna Need It)** — не добавляйте функциональность \"на будущее\". Реализуйте только то, что нужно сейчас. Преждевременная оптимизация/абстракция — зло.",
    "ref/out/in": "**ref/out/in** — модификаторы параметров:\n- `ref` — передача по ссылке (чтение/запись). Переменная должна быть инициализирована ДО вызова.\n- `out` — передача по ссылке (только запись). Переменная инициализируется ВНУТРИ метода (обязательно до выхода).\n- `in` — передача по ссылке ТОЛЬКО для чтения (readonly). Защита от случайного изменения. Для больших struct — избегает копирования.",
    "params": "**params** — параметр-массив, позволяет передавать переменное число аргументов. `void Print(params string[] names)`. Вызов: `Print(\"a\", \"b\")` или `Print(new[] {\"a\", \"b\"})`. Только последний параметр, только один `params`.",
    "optional parameters": "**Optional parameters** — параметры со значениями по умолчанию. `void Greet(string name, string greeting = \"Hello\")`. Вызов: `Greet(\"Alex\")` или `Greet(\"Alex\", \"Hi\")`. Должны быть в конце списка параметров.",
    "named arguments": "**Named arguments** — передача аргументов по имени: `Greet(name: \"Alex\", greeting: \"Hi\")`. Позволяет пропускать параметры с дефолтом, менять порядок. Полезно при многих параметрах с дефолтами.",
    "null-coalescing (??)": "**?? (null-coalescing)** — если слева не null, возвращает левое, иначе правое. `x ?? defaultValue`. Цепочка: `a ?? b ?? c ?? default`. `??=` — присваивание, если null: `x ??= GetDefault();`.",
    "null-conditional (?.)": "**?. (null-conditional)** — если слева не null, обращается к члену, иначе возвращает null. `obj?.Method()` — вызовет только если `obj != null`. Цепочка: `obj?.Prop?.Method()`. Возвращает `null` (или `Nullable<T>` для value types).",
    "null-forgiving (!)": "**! (null-forgiving)** — говорит компилятору: \"я знаю, что это не null\". `string s = obj!.Name;`. Используйте осторожно — отключает защиту от null. Нужен при работе с legacy кодом или когда вы уверены на 100%.",
    "pattern matching": "**Pattern matching** — проверка типа/структуры и извлечение значений. `is Type var` — проверка + объявление переменной. `switch` expressions (C# 8+): `obj switch { Type t => ..., _ => default }`. Property patterns: `obj is { Prop: > 0 }`. Tuple patterns: `(x, y) switch { (0,0) => ... }`.",
    "switch expression": "**switch expression** (C# 8+) — выражение, возвращающее значение. `var result = x switch { 1 => \"one\", 2 => \"two\", _ => \"other\" };`. Поддерживает patterns: type, property, tuple, relational (`> 0`), var, discard (`_`).",
    "tuple": "**tuple (ValueTuple)** — легковесная структура для группы значений. `(int x, string name) = (1, \"Alex\")`. Доступ: `t.Item1`, `t.Name` (named). Распаковка: `var (x, name) = tuple;`. Возврат нескольких значений: `return (sum, count);`.",
    "deconstruction": "**deconstruction** — распаковка кортежа/объекта в переменные. `var (x, y) = tuple;`. Для классов: `public void Deconstruct(out int x, out int y)`. Позволяет: `var (x, y) = point;`.",
    "pattern matching switch": "**switch expression** с patterns:\n- Type: `obj is int i`\n- Property: `obj is { Age: > 18 }`\n- Tuple: `(x, y) switch { (0,0) => ... }`\n- Relational: `x switch { > 0 => \"+\", < 0 => \"-\", _ => \"0\" }`\n- Var: `obj is var v` (всегда true)\n- Discard: `_ => default`",
}

# Загружаем уроки и добавляем глоссарий
lessons_dir = Path('fixtures/lessons/csharp')

def process_lesson(lesson_path: Path):
    with open(lesson_path, 'r', encoding='utf-8') as f:
        lesson = json.load(f)

    # Добавим глоссарий в конец урока если его нет
    if 'glossary' not in lesson:
        lesson['glossary'] = {k: v for k, v in sorted(TERM_EXPLANATIONS.items())}

    with open(lesson_path, 'w', encoding='utf-8') as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Обработан: {lesson_path.name}')

if __name__ == '__main__':
    lessons_dir = Path('fixtures/lessons/csharp')
    for lesson_file in sorted(lessons_dir.glob('*.json')):
        process_lesson(lesson_file)
    print('Все 11 уроков обновлены с глоссарием!')