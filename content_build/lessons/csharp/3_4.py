"""Урок 3.4 курса csharp: управление памятью."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


def text(content: str) -> dict:
    return {"type": "text", "content": content.strip()}


def heading(content: str, level: int = 2) -> dict:
    return {"type": "heading", "level": level, "content": content.strip()}


def bullets(*items: str, ordered: bool = False) -> dict:
    return {"type": "list", "ordered": ordered, "items": list(items)}


def numbered(*items: str) -> dict:
    return bullets(*items, ordered=True)


def table(headers: list[str], rows: list[list[str]]) -> dict:
    return {"type": "table", "headers": headers, "rows": rows}


def callout(style: str, title: str, content: str) -> dict:
    return {"type": "callout", "style": style, "title": title, "content": content}


def example(language: str, source: str) -> dict:
    return {"type": "code", "language": language, "content": code(source)}


LESSON = {
    "language": "csharp",
    "program_order": 3,
    "topic_order": 4,
    "name": "3.4. Управление памятью",
    "slug": "csharp-3-4-управление-памятью",
    "short_description": (
        "Как устроен сборщик мусора .NET: поколения, куча больших объектов и финализаторы. "
        "Детерминированное освобождение через IDisposable и IAsyncDisposable, работа без аллокаций "
        "на Span, Memory и ArrayPool, а также пулы объектов и слабые ссылки."
    ),
    "topic_name": "Управление памятью",
    "topic_description": (
        "Глубокий разбор управления памятью в .NET: алгоритм mark-sweep-compact, поколения Gen 0, "
        "Gen 1 и Gen 2, LOH и POH, режимы Workstation и Server GC, паттерн Dispose с финализатором "
        "и SafeHandle, Span, Memory и ArrayPool для кода без лишних аллокаций, ValueTypes, "
        "WeakReference и ConditionalWeakTable для предотвращения удержания объектов."
    ),
    "learning_objectives": [
        "Объяснять, как mark-sweep-compact сборщик мусора находит достижимые объекты и как работают поколения",
        "Отличать давление на Gen 2 и LOH от дешёвых аллокаций в Gen 0 и предсказывать паузы GC",
        "Реализовывать полный паттерн Dispose с финализатором, GC.SuppressFinalize и SafeHandle",
        "Выбирать между IDisposable и IAsyncDisposable и применять using и await using без утечек",
        "Использовать Span, Memory и ArrayPool для парсинга и обработки потоков без лишних копий",
        "Снижать аллокации через readonly struct, избегание упаковки и пулы объектов",
        "Применять WeakReference и ConditionalWeakTable для кэшей и событий, не мешающих удалению объектов",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "csharp",
        "память",
        "garbage-collector",
        "idisposable",
        "span",
        "arraypool",
    ],
    "starter_code": code(
        """
        using System;

        public static class Program
        {
            public static void Main()
            {
                // Стартовое значение для Gen 0 до первого замера.
                Console.WriteLine($"Gen 0 до работы: {GC.CollectionCount(0)}");

                string[] words = { "память", "куча", "поколение" };
                int total = 0;
                foreach (string word in words)
                {
                    total += word.Length; // каждая строка уже лежит в управляемой куче
                }

                Console.WriteLine($"Сумма длин: {total}");
                Console.WriteLine($"Gen 0 после работы: {GC.CollectionCount(0)}");
            }
        }
        """
    ),
    "hints": [
        "Если класс только оборачивает объект, который сам реализует IDisposable, наследуйте от него "
        "или вызывайте base.Dispose(disposing): двойная иерархия без base.Dispose — частая причина утечек.",
        "Span<T> — ref struct: его нельзя хранить в поле обычного класса, в лямбде и в async-методе. "
        "Для полей и асинхронных методов берите Memory<T> и превращайте в Span только локально.",
        "Массив из ArrayPool.Rent возвращается больше запрошенного размера и содержит старые данные: "
        "всегда ограничивайте работу срезом [..length] и возвращайте массив в finally.",
        "GC.Collect в рабочем коде почти никогда не нужен: он повышает паузы и продвигает живые объекты "
        "в Gen 2. Опирайтесь на метрики и профилировщик распределения, а не на интуицию.",
    ],
    "content": [
        text(
            "В C# разработчик не вызывает `free` и не считает указатели: память под объекты выделяет "
            "сборщик мусора (garbage collector, GC), а освобождает он же, когда объект становится "
            "недостижимым. Такая модель снимает огромный класс ошибок, но не отменяет размышлений "
            "о памяти. Код, который аллоцирует миллионы короткоживущих объектов в секунду, создаёт "
            "давление на сборщик, а объект, который держит файловый дескриптор, должен быть закрыт "
            "детерминированно, а не когда-нибудь.\n\n"
            "Управляемая куча (managed heap) — область памяти, которой владеет рантайм. Всё, что создано "
            "через `new` для ссылочных типов, попадает туда. Массив символов внутри `string`, `List<T>`, "
            "лямбда-замыкание, `Task` — всё это аллокации. Понимание того, где и когда они происходят, "
            "отделяет код, который работает, от кода, который работает под нагрузкой.\n\n"
            "Урок идёт от устройства GC к практике: поколения, финализаторы и `Dispose`, асинхронное "
            "освобождение, затем — работа без аллокаций на `Span<T>`, `Memory<T>` и `ArrayPool<T>`."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "Объяснять, как mark-sweep-compact сборщик мусора находит достижимые объекты и как работают поколения.",
            "Отличать давление на Gen 2 и LOH от дешёвых аллокаций в Gen 0 и предсказывать паузы GC.",
            "Реализовывать полный паттерн Dispose с финализатором, GC.SuppressFinalize и SafeHandle.",
            "Выбирать между IDisposable и IAsyncDisposable и применять using и await using без утечек.",
            "Использовать Span, Memory и ArrayPool для парсинга и обработки потоков без лишних копий.",
            "Снижать аллокации через readonly struct, избегание упаковки и пулы объектов.",
            "Применять WeakReference и ConditionalWeakTable для кэшей и событий, не мешающих удалению объектов.",
        ),
        heading("Как работает сборщик мусора"),
        text(
            "GC в .NET — точный следящий сборщик с уплотнением. Он не подсчитывает ссылки, а обходит "
            "граф объектов от корней (roots): локальных переменных потоков, статических полей, "
            "закреплённых указателей и очереди финализации. Алгоритм состоит из трёх фаз:\n"
            "- Mark — обход графа от корней и пометка всех достижимых объектов.\n"
            "- Sweep — все непомеченные объекты считаются мусором и освобождаются.\n"
            "- Compact — живые объекты сдвигаются в начало области, указатели обновляются, "
            "свободное место снова непрерывно.\n\n"
            "Выделение памяти в такой модели предельно дешёвое: куча уплотнена, новый объект кладётся "
            "в конец, достаточно сдвинуть указатель. Это быстрее, чем поиск свободного блока в куче "
            "с фрагментацией: цена переносится на сборку, и чем больше живых объектов, тем дороже "
            "mark и compact."
        ),
        example(
            "csharp",
            """
            using System;

            public static class Program
            {
                public static void Main()
                {
                    // Куча после старта: пусто, но бюджет выделен.
                    Console.WriteLine($"Heap до: {GC.GetTotalMemory(false)} байт");

                    byte[] temporary = new byte[16 * 1024 * 1024]; // 16 МБ
                    temporary[0] = 1;
                    temporary[^1] = 1;
                    Console.WriteLine($"Heap после аллокации: {GC.GetTotalMemory(false)} байт");
                    Console.WriteLine($"Поколение массива: {GC.GetGeneration(temporary)}");
                }
            }
            """,
        ),
        text(
            "Вывод: Heap до: 22432 байт\n"
            "Heap после аллокации: 16799888 байт\n"
            "Поколение массива: 2\n\n"
            "Массив на 16 МБ больше порога куч больших объектов (85 000 байт), поэтому сразу виден "
            "в Gen 2. Обычный маленький массив по умолчанию попал бы в Gen 0. Метод `GC.GetTotalMemory` "
            "с аргументом `false` возвращает оценку без принудительной сборки, что важно для измерений: "
            "вынужденная сборка исказила бы картину."
        ),
        heading("Поколения и паузы"),
        text(
            "Если бы каждый цикл проходил по всей куче, приложение с сотнями мегабайт данных "
            "замирало бы надолго. Поэтому куча делится на поколения, и сборки разных поколений "
            "запускаются с разной частотой. Гипотеза о слабом поколенческом инварианте "
            "(weak generational hypothesis) утверждает: большинство новых объектов умирают молодыми.\n\n"
            "Объект после сборки, в которой он выжил, повышается (promoted) в следующее поколение. "
            "Сборка Gen 0 дешевле остальных, потому что проверяет только молодой сегмент. Сборка Gen 2 "
            "почти всегда полная: она включает в себя Gen 0 и Gen 1 и работает по всей куче."
        ),
        table(
            ["Поколение", "Что содержится", "Когда собирается", "Относительная цена"],
            [
                ["Gen 0", "Новые объекты, короткоживущие данных", "Чаще всего: при исчерпании бюджета", "Наименьшая"],
                ["Gen 1", "Выжившие объекты, промежуточный буфер", "При сборке Gen 2 или при переполнении Gen 1", "Средняя"],
                ["Gen 2", "Долгоживущие объекты, кэши, статика", "Полная сборка, редко", "Наибольшая"],
                ["LOH", "Объекты 85 000 байт и больше", "Только вместе с Gen 2", "Высокая из-за редкости"],
                ["POH", "Объекты, которые нужно закрепить (pinned)", "Сборка Gen 2 (.NET 5+)", "Высокая"],
            ],
        ),
        text(
            "Куча больших объектов (Large Object Heap, LOH) — отдельная область для массивов и крупных "
            "структур от 85 000 байт. Тяжёлые объекты редко копируются при уплотнении дорого, поэтому "
            "по умолчанию LOH не уплотняется: удалённые диапазоны превращаются в дыры. Последствия "
            "двойные. Во-первых, крупная аллокация может не найти подходящей дыры и вызвать лишнюю "
            "сборку. Во-вторых, повторяющиеся выделения массивов чуть ниже предела, например `byte[81920]` "
            "в цикле, кладут нагрузку прямо в Gen 2.\n\n"
            "Куча закреплённых объектов (Pinned Object Heap, POH) появилась в .NET 5 для случая, когда "
            "буфер должен оставаться на месте: закрепление при уплотнении требует обхода таблиц "
            "закреплений. Код, который часто берёт `GCHandle.Alloc(obj, GCHandleType.Pinned)` на "
            "временной массив, мешает уплотнению; перенос таких буферов на POH решает проблему "
            "аккуратнее. Управлять фрагментацией LOH позволяет и метод `GCCollectionMode` вместе "
            "с настройкой `GCSettings.LargeObjectHeapCompactionMode`."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Runtime;

            public static class Program
            {
                public static void Main()
                {
                    Console.WriteLine($"LOH порог: {GCSettings.LargeObjectHeapCompactionMode}");
                    int before = GC.CollectionCount(2);

                    // 80 000 символов: 160 024 байта с заголовком и завершающим нулём.
                    char[] chunk = new char[80_000];
                    Console.WriteLine($"Размер объекта: {GC.GetGeneration(chunk)} поколение, "
                        + $"{GC.GetGCMemoryInfo().TotalCommittedBytes / 1024} КБ зарезервировано");
                    Console.WriteLine($"Gen 2 сборок до: {before}, после: {GC.CollectionCount(2)}");
                }
            }
            """,
        ),
        callout(
            "info",
            "Повышайте порог аллокации, а не думайте о нём подписи",
            "Правило, которое экономит паузы: держите горячие аллокации маленькими и короткоживущими, "
            "чтобы они умирали в Gen 0. Буфер на 40–80 КБ, выделяемый на каждый запрос, обходит Gen 0 "
            "и лежит в LOH — именно такой буфер и стоит брать из ArrayPool."
        ),
        heading("Режимы сборки мусора"),
        text(
            "Поведение GC настраивается в проекте и влияет сильнее, чем почти любая правка в коде. "
            "В режиме Workstation GC (по умолчанию для клиентских приложений) сборка идёт в одном "
            "потоке, и паузы короткие. В режиме Server GC для каждого ядра создаётся своя куча и свой "
            "поток сборки: пропускная способность выше, но паузы длиннее и памяти нужно больше. "
            "Серверы ASP.NET Core обычно включают Server GC, десктопные приложения — нет.\n\n"
            "Фоновая (concurrent) сборка выполняет большую часть работы Gen 2 параллельно с кодом "
            "приложения, сокращая видимые паузы. Настройки задаются в файле проекта.\n\n"
            "Флаг `GC.RegisterForFullGCNotification` и методы `WaitForFullGCApproach` и "
            "`WaitForFullGCComplete` позволяют приложению узнать о приближении полной сборки заранее: "
            "в этот момент сервис может остановить приём трафика или сбросить временный кэш. "
            "Это тонкая настройка для больших нагрузок, а не ежедневный инструмент."
        ),
        example(
            "xml",
            """
            <Project Sdk="Microsoft.NET.Sdk">

              <PropertyGroup>
                <TargetFramework>net8.0</TargetFramework>

                <!-- Куч много, потоков сборки столько же: для серверов -->
                <ServerGarbageCollection>true</ServerGarbageCollection>

                <!-- Фоновая сборка Gen 2: меньше пауз, но больше памяти -->
                <ConcurrentGarbageCollection>true</ConcurrentGarbageCollection>

                <!-- Стратегии выделения: LowLatency для интерактивных приложений -->
                <TieredCompilation>true</TieredCompilation>
              </PropertyGroup>

            </Project>
            """,
        ),
        text(
            "В рабочем коде важно уметь наблюдать за сборщиком, а не гадать. Стандартный набор "
            "счётчиков есть в `System.Diagnostics.Metrics` и в событийной трассировке: "
            "`dotnet-counters` показывает частоту сборок по поколениям, занятый размер кучи и долю "
            "времени в GC, а `dotnet-trace` и профайлер распределения показывают, какой тип "
            "аллоцируется чаще всего. Именно профиль распределения указывает, что оптимизировать, "
            "а не общее число мегабайт."
        ),
        heading("Финализаторы и SafeHandle"),
        text(
            "Финализатор (finalizer) — метод `~ClassName()`, который вызывается сборщиком мусора перед "
            "освобождением объекта. Он нужен для одного случая: объект владеет неуправляемым ресурсом "
            "(дескриптором файла, хэндлом окна, памятью из `Marshal.AllocHGlobal`), и программист "
            "забыл освободить его явно. Финализатор — страховка, а не способ работы.\n\n"
            "Страховка обходится дорого. Объект с финализатором попадает в очередь финализации и "
            "проживает как минимум на одну сборку дольше: его нельзя освободить сразу, "
            "его финализатор выполняется в отдельном потоке финализатора, а исключение внутри "
            "финализатора завершает процесс. Поэтому классический паттерн `Dispose` предусматривает "
            "метод `GC.SuppressFinalize`: после явной очистки объект говорит сборщику, что финализировать "
            "его не нужно."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Runtime.InteropServices;

            public sealed class NativeBuffer : IDisposable
            {
                private IntPtr _pointer;
                private bool _disposed;

                public NativeBuffer(int size)
                {
                    _pointer = Marshal.AllocHGlobal(size);
                }

                public void Write(int value)
                {
                    ObjectDisposedException.ThrowIf(_disposed, this);
                    Marshal.WriteInt32(_pointer, value);
                }

                public void Dispose()
                {
                    Dispose(true);
                    GC.SuppressFinalize(this);
                }

                private void Dispose(bool disposing)
                {
                    if (_disposed)
                    {
                        return;
                    }

                    if (_pointer != IntPtr.Zero)
                    {
                        Marshal.FreeHGlobal(_pointer);
                        _pointer = IntPtr.Zero;
                    }

                    _disposed = true;
                }

                ~NativeBuffer() => Dispose(false);
            }

            public static class Program
            {
                public static void Main()
                {
                    using (var buffer = new NativeBuffer(64))
                    {
                        buffer.Write(42);
                        Console.WriteLine("Записано в неуправляемую память");
                    }

                    Console.WriteLine("Освобождено детерминированно");
                }
            }
            """,
        ),
        text(
            "Вывод: Записано в неуправляемую память\n"
            "Освобождено детерминированно\n\n"
            "Флаг `_disposed` защищает от двойного освобождения, а `GC.SuppressFinalize(this)` снимает "
            "объект с очереди финализации. Параметр `disposing` разделяет два сценария: при явном "
            "вызове (`true`) можно трогать управляемые поля, например закрывать другие `IDisposable`, "
            "а в финализаторе (`false`) — нельзя, потому что порядок финализации не определён и "
            "управляемые зависимости могут быть уже освобождены.\n\n"
            "Если класс не финализируемый и не имеет наследников, можно не различать ветки и "
            "закрыться на другом, более простом варианте: `sealed`-класс с приватным `Dispose(bool)` "
            "и явным `IDisposable.Dispose`. Наследование усложняет картину, потому что наследнику нужно "
            "перекрыть и вызвать `base.Dispose(disposing)` — забыть об этом легко, и тогда ресурсы "
            "базового класса не освободятся."
        ),
        heading("SafeHandle вместо собственного финализатора", 3),
        text(
            "Для неуправляемых хэндлов в .NET есть готовый инструмент — `SafeHandle`. Это класс из "
            "`System.Runtime.InteropServices`, который сам реализует `IDisposable` и финализатор, "
            "защищает от повторного освобождения и не даёт GC освободить объект, пока P/Invoke "
            "использует хэндл. Наследники вроде `SafeFileHandle` переопределяют только "
            "`ReleaseHandle()` и возвращают `true`, если освобождение удалось.\n\n"
            "Собственный финализатор в большинстве случаев не нужен: `SafeHandle` решает ту же задачу "
            "корректнее. Класс-обёртка тогда хранит поле типа `SafeHandle` и в `Dispose` просто "
            "вызывает `_handle.Dispose()`, а финализатора у обёртки нет. Если ресурс действительно "
            "критичный, например хэндл, который должен освобождаться даже при выгрузке домена "
            "приложения, существует база `CriticalFinalizerObject`."
        ),
        example(
            "csharp",
            """
            using System;
            using System.IO;
            using System.Text;
            using Microsoft.Win32.SafeHandles;

            public sealed class TextFileWriter : IDisposable
            {
                // SafeFileHandle владеет хэндлом и сам вызовет CloseHandle.
                private readonly SafeFileHandle _handle;
                private bool _disposed;

                public TextFileWriter(string path)
                {
                    _handle = File.OpenHandle(path, FileMode.Create, FileAccess.Write);
                }

                public void Write(string line)
                {
                    ObjectDisposedException.ThrowIf(_disposed, this);
                    byte[] bytes = Encoding.UTF8.GetBytes(line + "\\n");
                    RandomAccess.Write(_handle, bytes, 0);
                }

                public void Dispose()
                {
                    if (_disposed)
                    {
                        return;
                    }

                    _handle.Dispose(); // финализатор SafeHandle сработает только при ошибке
                    _disposed = true;
                }
            }
            """,
        ),
        callout(
            "warning",
            "Не финализируйте код, которому есть чем обойтись",
            "Финализатор сворачивает детерминированность в неопределённость и вредит производительности. "
            "Прежде чем писать `~ClassName()`, проверьте: ресурс — управляемый объект (тогда `Dispose` "
            "и хватает), или инкапсулирован в SafeHandle (тогда свой финализатор не нужен). "
            "В семи случаях из восьми правильный ответ — просто `IDisposable`."
        ),
        heading("IDisposable, IAsyncDisposable и using"),
        text(
            "`IDisposable` — договор: объект имеет метод `Dispose()`, который освобождает ресурсы. "
            "Файл, сетевое соединение, транзакция, подписка на событие с отпиской — всё это ресурсы, "
            "чьё освобождение не должно зависеть от GC. `using` гарантирует вызов `Dispose` даже при "
            "выбросе исключения: конструкция разворачивается в `try/finally`.\n\n"
            "В C# 8 появились два улучшения. Объявление `using var resource = ...` освобождает объект "
            "в конце области видимости, а его поток управления линейнее, чем у блока. Тип "
            "`IAsyncDisposable` с методом `DisposeAsync()` нужен, когда освобождение требует "
            "асинхронной операции: сбросить буфер в сеть, дождаться закрытия соединения, вернуть "
            "арендованный ресурс. `await using` ждёт этот `ValueTask`."
        ),
        example(
            "csharp",
            """
            using System;
            using System.IO;
            using System.Threading.Tasks;

            public sealed class ReportWriter : IAsyncDisposable
            {
                private readonly StreamWriter _writer;
                private bool _disposed;

                public ReportWriter(Stream stream)
                {
                    _writer = new StreamWriter(stream);
                }

                public ValueTask WriteLineAsync(string line) => _writer.WriteLineAsync(line);

                public async ValueTask DisposeAsync()
                {
                    if (_disposed)
                    {
                        return;
                    }

                    await _writer.FlushAsync();
                    await _writer.DisposeAsync();
                    _disposed = true;
                }
            }

            public static class Program
            {
                public static async Task Main()
                {
                    await using var writer = new ReportWriter(Console.OpenStandardOutput());
                    await writer.WriteLineAsync("Отчёт: 3 записи");
                    await writer.WriteLineAsync("Статус: готово");
                }
            }
            """,
        ),
        text(
            "Вывод: Отчёт: 3 записи\n"
            "Статус: готово\n\n"
            "Класс не наследуется и не имеет финализатора, поэтому полный паттерн с "
            "`Dispose(bool disposing)` здесь излишен. Если тип реализует оба интерфейса, "
            "`await using` выберет `IAsyncDisposable`, и синхронный `Dispose` останется для "
            "кода, который не может ждать. Важно не смешивать порядок: асинхронный вариант "
            "обычно выполняется внутри `DisposeAsync`, а синхронный делегирует тому же пути "
            "без финализатора — так очистка остаётся единой."
        ),
        heading("Span и Memory: работа без копий"),
        text(
            "`Span<T>` — тип над непрерывной частью памяти: массива, стековой памяти "
            "`stackalloc`, небезопасного указателя или интернированной строки. Он не копирует данные, "
            "а описывает окно из ссылки и длины. Метод `Slice` возвращает новый `Span<T>`, "
            "смотрящий в ту же память. Ключевое ограничение: `Span<T>` объявлен как `ref struct`, "
            "поэтому он живёт только на стеке, не может быть полем класса, быть захвачен лямбдой "
            "или пережить `await`.\n\n"
            "`Memory<T>` — его асинхронный родственник. Он может быть полем класса и передаваться "
            "в асинхронные методы, но для непосредственной работы его нужно превратить в `Span<T>` "
            "через свойство `Span`. Обычно `Memory<T>` передают по конвейеру, а тяжёлую работу "
            "делают над `Span<T>` локально.\n\n"
            "Главный выигрыш — отсутствие аллокаций. Метод `Substring` в `string` каждый раз создаёт "
            "новую строку, а срез `ReadOnlySpan<char>` только переносит пару чисел. Программа, "
            "разбирающая миллион строк CSV, на `Span` не создаёт миллион новых объектов."
        ),
        example(
            "csharp",
            """
            using System;

            public static class Version
            {
                // Ни одной строковой аллокации: только окна в исходный span.
                public static bool TryParse(ReadOnlySpan<char> input, out int major, out int minor)
                {
                    major = minor = 0;
                    int dot = input.IndexOf('.');
                    if (dot < 0)
                    {
                        return false;
                    }

                    return int.TryParse(input[..dot], out major)
                        && int.TryParse(input[(dot + 1)..], out minor);
                }
            }

            public static class Program
            {
                public static void Main()
                {
                    ReadOnlySpan<char> raw = "18.03".AsSpan();
                    if (Version.TryParse(raw, out int major, out int minor))
                    {
                        Console.WriteLine($"Мажор: {major}, минор: {minor}");
                        Console.WriteLine($"Сумма: {major + minor}");
                    }
                }
            }
            """,
        ),
        text(
            "Вывод: Мажор: 18, минор: 3\n"
            "Сумма: 21\n\n"
            "Разбор `18.03` не создал ни одной новой строки: `input[..dot]` и `input[(dot + 1)..]` — "
            "`ReadOnlySpan<char>` поверх того же литерала, а `int.TryParse` умеет принимать именно "
            "span. Если такое же разбиение делать через `Split('.')`, каждая часть окажется новой "
            "строкой в управляемой куче. При десятках тысяч вызовов в секунду разница в аллокациях "
            "и паузах GC становится заметной. В `ReadOnlySpan<char>` удобно принимать и входные "
            "данные: `string` и `char[]` неявно преобразуются в него без копирования."
        ),
        callout(
            "info",
            "Правило выбора: Span или Memory",
            "Если данные нужны только в пределах синхронного метода — `Span<T>`. Если их надо "
            "хранить в поле, передавать через `await` или в лямбду — `Memory<T>`, а срез в `Span<T>` "
            "делать непосредственно перед использованием. Выбор диктуется временем жизни, а не удобством."
        ),
        heading("ArrayPool: аренда вместо создания"),
        text(
            "Даже дешёвая аллокация в Gen 0 стоит денег: сдвиг указателя, запись заголовка, "
            "и в какой-то момент сборка. Если один и тот же большой буфер нужен на каждом запросе, "
            "разумно его не создавать, а брать из пула. `ArrayPool<T>` — статический пул массивов, "
            "настроенный на частые размеры: `Rent(81920)` вернёт массив длиной не меньше запрошенной, "
            "возможно, больше. Массив может содержать данные прошлого арендатора.\n\n"
            "Правила просты, но забыть их легко:\n"
            "- Длина в `Rent` — минимальная. Работайте со срезом `buffer.AsSpan(0, length)`.\n"
            "- Не полагайтесь на содержимое. Если нужны нули — очистите явно.\n"
            "- Возвращайте массив в `finally`, даже если код выше выбросил исключение.\n"
            "- Не возвращайте массив дважды и не используйте его после возврата.\n\n"
            "Общий пул `ArrayPool<T>.Shared` для крупных размеров предпочтительнее создания "
            "счётчика буферов на каждый запрос. Когда размер и число экземпляров известно, "
            "можно создать пул через `ArrayPool<T>.Create`, ограничив максимальную длину и "
            "число массивов в бакете."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Buffers;
            using System.IO;

            public static class Program
            {
                public static void Main()
                {
                    ArrayPool<byte> pool = ArrayPool<byte>.Shared;
                    // 64 КБ: без пула такой массив попал бы в LOH.
                    byte[] buffer = pool.Rent(64 * 1024);

                    try
                    {
                        using var stream = new MemoryStream(new byte[] { 1, 2, 3, 4, 5 });
                        int read = stream.Read(buffer, 0, buffer.Length);
                        ReadOnlySpan<byte> data = buffer.AsSpan(0, read);

                        int sum = 0;
                        foreach (byte value in data)
                        {
                            sum += value;
                        }

                        Console.WriteLine($"Арендовано: {buffer.Length} байт");
                        Console.WriteLine($"Прочитано: {read} байт, сумма: {sum}");
                    }
                    finally
                    {
                        pool.Return(buffer);
                    }
                }
            }
            """,
        ),
        text(
            "Вывод: Арендовано: 65536 байт\n"
            "Прочитано: 5 байт, сумма: 15\n\n"
            "Свойство `buffer.Length` показывает фактический размер арендованного массива, "
            "а значимое содержимое ограничено срезом `[..read]`. Возврат через `finally` гарантирует, "
            "что исключение внутри `try` не утечёт массивом: иначе буфер останется занятым и пул "
            "будет бесполезно расти, а под давлением — создавать новые буферы. Перегрузка "
            "`Return(array, clearArray: true)` затирает содержимое, если в буфере остались пароли "
            "или персональные данные."
        ),
        heading("Структуры, упаковка и пулы объектов"),
        text(
            "`struct` живёт там, где объявлен: в локальной переменной — на стеке, внутри массива или "
            "другого класса — внутри родительского объекта без отдельной аллокации и заголовка. "
            "Для маленьких значений с коротким сроком жизни это прямая экономия. Но у структуры есть "
            "ловушки: передача по значению копирует все поля, а наследование отсутствует. "
            "Чтобы избежать копий, параметр передают как `in`: компилятор передаёт ссылку без права "
            "записи. `readonly struct` дополнительно обещает неизменность.\n\n"
            "Упаковка (boxing) сводит выигрыш к нулю: значение, приведённое к `object` или "
            "необобщённому интерфейсу, копируется в новый объект в куче. Обобщённый код с ограничением "
            "`where T : struct` упаковки не создаёт, потому что использует специализированный экземпляр "
            "метода. Форматирование через `string.Format` с числом или помещение `int` в "
            "`object[]` тоже упаковывает.\n\n"
            "Второй источник давления — объекты, которые создаются и уничтожаются тысячами: "
            "`StringBuilder`, временные списки, объекты запросов. Пул объектов держит готовые "
            "экземпляры и выдаёт их сброшенным в начальное состояние. Библиотека "
            "`Microsoft.Extensions.ObjectPool` делает это без ручного управления."
        ),
        table(
            ["Механизм", "Когда помогает", "Чем платить"],
            [
                ["readonly struct, in", "маленькие значения в горячем цикле", "копирование при передаче, отсутствие наследования"],
                ["ReadOnlySpan<char>", "парсинг, поиск, срезы без аллокаций", "ограничение времени жизни"],
                ["ArrayPool<T>", "большие буферы на каждый запрос", "очистка, возврат в finally"],
                ["ObjectPool<T>", "дорогие в создании объекты-помощники", "сброс состояния объекта"],
                ["stackalloc", "маленькие буферы в одном методе", "давление на стек, риск переполнения"],
                ["MemoryPool<T>", "аренда памяти непрямоугольной формы", "диспоуз через IMemoryOwner"],
            ],
        ),
        example(
            "csharp",
            """
            using System;

            public readonly struct Money : IEquatable<Money>
            {
                public decimal Amount { get; }
                public string Currency { get; }

                public Money(decimal amount, string currency)
                {
                    Amount = amount;
                    Currency = currency;
                }

                // in: структура не копируется при вызове.
                public in Money WithAmount(decimal amount) => this;

                public bool Equals(Money other) => Amount == other.Amount
                    && string.Equals(Currency, other.Currency, StringComparison.Ordinal);

                public override string ToString() => $"{Amount:0.00} {Currency}";
            }

            public static class Program
            {
                public static void Main()
                {
                    var price = new Money(19.99m, "EUR");
                    Money total = price;

                    decimal sum = 0m;
                    for (int i = 0; i < 1_000_000; i++)
                    {
                        sum += price.Amount; // без аллокации на каждой итерации
                    }

                    Console.WriteLine($"Итог: {total}");
                    Console.WriteLine($"Сумма цикла: {sum:0.00}");
                }
            }
            """,
        ),
        text(
            "Вывод: Итог: 19.99 EUR\n"
            "Сумма цикла: 19999990.00\n\n"
            "Присваивание `Money total = price` копирует структуру целиком, при этом `string Currency` "
            "тоже структура ссылки: обе копии указывают на один неизменяемый литерал. "
            "Миллион итераций не создаёт ни одного объекта, кроме строк в `Console.WriteLine`. "
            "Метод `IEquatable<Money>` определён, чтобы проверка равенства не упаковывала структуру "
            "в `object` при вызове `Equals` от интерфейса."
        ),
        heading("Слабые ссылки и ConditionalWeakTable"),
        text(
            "Кэш хранит пары и держит значения живыми, пока не будет выселено. Так рождается "
            "классическая утечка: кэш не выселяется, GC не может собрать значения, память растёт. "
            "`WeakReference<T>` решает обратную задачу: ссылка на объект не мешает его удалению. "
            "Метод `TryGetTarget` возвращает `true` и устанавливает объект, пока он жив, и `false`, "
            "если его уже собрал GC.\n\n"
            "Слабая ссылка уместна там, где потеря значения — не ошибка: кэш вычисленных результатов, "
            "подписки на события, сопоставление «объект → служебные данные». Если после сбора ссылки "
            "данные нужны незамедлительно, их пересчитывают. Если данные нельзя терять, слабая ссылка "
            "не подходит: нужно ограничение размера и выселение, а не надежда на сборщик.\n\n"
            "`ConditionalWeakTable<TKey, TValue>` — готовое решение для привязки данных к объекту. "
            "Ключ в этой таблице не удерживается: когда объект собран, запись удаляется автоматически. "
            "Этот механизм используют, например, для хранения расширяемых свойств, и он идеально "
            "ложится в реализацию слабых событий (weak event pattern), где подписчик не удерживается "
            "издателем события."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;

            public sealed class Document
            {
                public string Title { get; }

                public Document(string title) => Title = title;
            }

            public static class Program
            {
                public static void Main()
                {
                    List<Document> strong = new();
                    List<WeakReference<Document>> weak = new();

                    for (int i = 0; i < 5; i++)
                    {
                        var doc = new Document($"Глава {i}");
                        bool keepStrong = i % 2 == 0;

                        if (keepStrong)
                        {
                            strong.Add(doc); // держим живым
                        }
                        else
                        {
                            weak.Add(new WeakReference<Document>(doc)); // не держим
                        }
                    }

                    GC.Collect();
                    GC.WaitForPendingFinalizers();
                    GC.Collect();

                    Console.WriteLine($"Сильных ссылок: {strong.Count}");
                    int alive = 0;
                    foreach (var reference in weak)
                    {
                        if (reference.TryGetTarget(out _))
                        {
                            alive++;
                        }
                    }

                    Console.WriteLine($"Живых слабых ссылок: {alive} из {weak.Count}");
                }
            }
            """,
        ),
        text(
            "Вывод: Сильных ссылок: 3\n"
            "Живых слабых ссылок: 0 из 2\n\n"
            "Документы с чётными номерами удерживаются списком `strong`, поэтому остаются живыми. "
            "Нечётные после сборки недостижимы, и `TryGetTarget` возвращает `false`. В реальном "
            "приложении `GC.Collect` здесь не пишут: он нужен только для воспроизводимости "
            "демонстрации. В рабочем коде механизм срабатывает сам по себе, когда память "
            "собирает обычная сборка. Наблюдаемый результат зависит от того, успели ли "
            "оптимизации JIT убрать ссылки на локальные переменные, поэтому в учебных примерах "
            "помогают вызовы `GC.KeepAlive`."
        ),
        callout(
            "warning",
            "Где WeakReference вредит",
            "Если данные обязаны быть доступны, слабая ссылка приведёт к внезапным пересчётам и "
            "нестабильной производительности. Кэш загрузки конфигурации, справочника или сессии "
            "не должен зависеть от сборщика: ограничивайте размер через `IMemoryCache` с политикой "
            "выселения и скользящим сроком жизни."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Забыли `GC.SuppressFinalize` в `Dispose`", "Финализатор всё равно выполняется, продлевая жизнь объекта", "Вызывать после явной очистки в `Dispose`"],
                ["`Dispose` без проверки флага", "Повторное освобождение хэндла, `ObjectDisposedException`", "Проверять `_disposed` в начале и ставить его в конце"],
                ["`Span<T>` в поле класса или в `async`", "Компилятор не даёт собрать: ref struct не может пережить стек", "Хранить `Memory<T>`, срез делать локально"],
                ["Возврат `Span<T>` из метода", "Span указывает на освобождённую стековую память", "Возвращать `Memory<T>` или копию в массив"],
                ["Массив из `ArrayPool` не возвращён", "Пул растёт, продолжать аренду становится дороже", "Возврат из `finally` при любом исходе"],
                ["`byte[81920]` в цикле без пула", "Аллокация в LOH, дорогие полные сборки", "`ArrayPool<byte>.Shared.Rent`"],
                ["`string.Split` в горячем парсинге", "Миллионы короткоживущих строк", "`ReadOnlySpan<char>` с `Slice` без копий"],
                ["`GC.Collect()` в рабочем коде", "Полная блокирующая сборка, подъём живых объектов в Gen 2", "Наблюдать метрики и уменьшать аллокации"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Собирайте проект командой "
            "`dotnet run -c Release` и проверяйте вывод после каждого изменения; "
            "для измерений аллокаций удобен `GC.GetTotalAllocatedBytes(precise: true)`."
        ),
        numbered(
            "Посчитайте аллокации: напишите метод, который складывает 10 000 чисел из `int[]` и "
            "возвращает сумму, и измерьте `GC.GetTotalAllocatedBytes` вокруг вызова. Убедитесь, "
            "что метод ничего не аллоцирует, и найдите, какая строка в вашем коде аллоцирует больше всего.",
            "Парсер без копий: реализуйте метод разбора строки формата `2026-11-19` на "
            "`ReadOnlySpan<char>: TryParseDate`, возвращающий `struct DateParts (Year, Month, Day)`. "
            "Не создавайте ни одной строки и проверьте на некорректном вводе.",
            "Ресурс с гибридным владением: сделайте класс `TempFile`, который создаёт временный файл, "
            "реализует `IDisposable` и удаляет файл в `Dispose`. Проверьте, что после `using` файла "
            "на диске нет, а при исключении внутри блока он тоже удалён.",
            "Пул и конвейер: прочитайте поток через `ArrayPool<byte>.Shared.Rent(64 * 1024)` в "
            "`try/finally`, посчитайте контрольную сумму по срезу `[..read]` и сравните размер "
            "`GC.GetGCMemoryInfo().HeapSizeBytes` с вариантом, где массив создаётся через `new`.",
            "Кэш со слабыми ссылками: реализуйте обёртку над `Dictionary<string, WeakReference<string>>` "
            "с методами `TryGet` и `Set` и методом очистки мёртвых записей. Проверьте на 1000 строк, "
            "что после `GC.Collect` очистка убирает записи, на которые больше нет сильных ссылок.",
        ),
        text("Пример ожидаемого результата для четвёртого задания:"),
        example(
            "text",
            "С пулом:       аллокаций 0, куча 1 048 576 байт\n"
            "Без пула:      аллокаций 1, куча 1 114 112 байт\n"
            "Контрольная сумма: 327 680",
        ),
        callout(
            "success",
            "Подсказка к заданию 1",
            "`GC.GetTotalAllocatedBytes(precise: true)` возвращает счётчик всех выделений с момента "
            "старта, поэтому запоминайте значение до и после. Методы, которые ничего не создают, "
            "дают нулевую дельту. Если дельта отлична от нуля, ищите в вызове `Substring`, `Split`, "
            "интерполяцию строк, упаковку в `object` и замыкания, создающие объект-делегат."
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему выделение нового объекта в уплотняющей куче дешевле, чем поиск свободного блока в куче с фрагментацией?",
            "Какой объект попадёт в LOH и почему порог составляет 85 000 байт, а не 85 024?",
            "Зачем в `Dispose` вызывается `GC.SuppressFinalize(this)` и что произойдёт без него?",
            "В чём разница между `Span<T>` и `Memory<T>` и какой из них уместен в параметре асинхронного метода?",
            "Что вернёт `ArrayPool<byte>.Shared.Rent(1000)` по длине и почему нельзя полагаться на содержимое?",
        ),
        heading("Ответы", 3),
        numbered(
            "Куча после сборки непрерывна, поэтому новый объект кладётся в её конец: нужно лишь сместить указатель, обновив границу занятого места. Поиск блока подходящего размера со свободными дырами требует обходов и не гарантирует успеха.",
            "В LOH попадают объекты от 85 000 байт и больше. Порог в стандартах .NET выбран как 85 000, а не круглые 85 килобайт, потому что 85 000 байт — целый, легко объясняемый и достаточно крупный размер; для массива же объект весит больше из-за заголовка — массив на 80 000 `char` занимает около 160 024 байт.",
            "Финализатор нужен только как страховка при отсутствии явной очистки. Если ресурсы уже освобождены в `Dispose`, вызов `GC.SuppressFinalize` снимает объект с очереди финализации, и он не проживёт лишнюю сборку. Без него объект останется в очереди, проживёт дольше и потеряет детерминированность очистки.",
            "`Span<T>` — ref struct, живёт только на стеке и не может быть полем класса или пережить `await`. `Memory<T>` хранится в поле, передаётся в асинхронные методы и при необходимости превращается в `Span<T>`. В параметре асинхронного метода уместен `Memory<T>` или `ReadOnlyMemory<T>`.",
            "`Rent` вернёт массив длиной не меньше 1000, обычно ровно 1024 из бакета степеней двойки. Содержимое остаётся от предыдущего арендатора, поэтому работать можно только с срезом нужной длины, а при необходимости — очищать явно.",
        ),
        heading("Итоги"),
        bullets(
            "GC — точный следящий сборщик mark-sweep-compact: находит достижимые объекты от корней и уплотняет кучу, поэтому выделение сводится к сдвигу указателя.",
            "Поколения делят гипотезу о короткой жизни объектов: Gen 0 дешёвый и частый, Gen 2 редкий и дорогой, LOH существует для объектов от 85 000 байт и обычно не уплотняется.",
            "Режим Workstation даёт короткие паузы, Server — пропускную способность на многих ядрах; выбор делается в проекте, а не в коде.",
            "Финализатор — страховка для неуправляемых ресурсов; правильный способ — `IDisposable` с флагом `_disposed`, `GC.SuppressFinalize` и `SafeHandle`.",
            "`IAsyncDisposable` и `await using` нужны, когда освобождение само асинхронно; `using var` освобождает ресурс в конце области видимости.",
            "`Span<T>` и `Memory<T>` дают работу с окнами памяти без копий; первый живёт на стеке, второй — для полей и асинхронных методов.",
            "`ArrayPool<T>` и пулы объектов заменяют повторные аллокации арендой, но требуют возврата в `finally` и учёта реальной длины и старого содержимого.",
            "`readonly struct`, `in` и обобщения без упаковки экономят аллокации; `WeakReference<T>` и `ConditionalWeakTable` не мешают сборщику удалять объекты.",
        ),
        heading("Что дальше"),
        text(
            "Следующий урок посвящён асинхронности и конкурентности: машине состояний `async`-методов, "
            "`ConfigureAwait`, `ValueTask`, каналам producer/consumer и примитивам синхронизации, "
            "которые не блокируют поток. Управление памятью и асинхронность соединены крепче, чем "
            "кажется: `Span<T>` нельзя пережить `await`, поэтому проектирование конвейеров данных "
            "начинается с вопроса, чей памяти принадлежит буфер и когда он освобождается."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Документация .NET: Garbage Collection fundamentals — learn.microsoft.com/dotnet/standard/garbage-collection/fundamentals",
            "Документация .NET: Implement a Dispose method — learn.microsoft.com/dotnet/standard/garbage-collection/implementing-dispose",
            "Документация .NET: Span<T> и Memory<T> — learn.microsoft.com/dotnet/standard/memory-and-spans",
            "Документация .NET: ArrayPool<T> — learn.microsoft.com/dotnet/api/system.buffers.arraypool-1",
            "Конрад Кокоса, «Pro .NET Memory Management» — подробная книга о внутренностях GC, LOH и закреплении памяти",
            "Стивен Клири, «Concurrency in C# Cookbook» — разделы о пулах и снижении аллокаций в асинхронном коде",
        ),
    ],
}
