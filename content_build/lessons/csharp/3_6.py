"""Урок 3.6 курса csharp: производительность."""

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
    "topic_order": 6,
    "name": "3.6. Производительность",
    "slug": "csharp-3-6-производительность",
    "short_description": (
        "Измерение вместо догадок: BenchmarkDotNet, профилирование, устройство JIT "
        "и Tiered Compilation, сокращение аллокаций, пулы, Span<T> и SIMD."
    ),
    "topic_name": "Производительность",
    "topic_description": (
        "Практическое руководство по оптимизации C#-кода: как ставить корректные "
        "замеры с BenchmarkDotNet, читать результаты профайлеров, понимать уровни "
        "компиляции JIT, публикацию ReadyToRun и Native AOT, а также сокращать "
        "давление на сборщик мусора через пулы, Span<T> и SIMD."
    ),
    "learning_objectives": [
        "Писать корректные замеры на BenchmarkDotNet с MemoryDiagnoser и Baseline",
        "Читать таблицу результатов: Mean, Error, StdDev, Gen0, Allocated",
        "Собирать трассы и метрики через dotnet-trace, dotnet-counters и dotnet-dump",
        "Объяснять уровни JIT: Tier 0, Tier 1, ReadyToRun, Native AOT",
        "Убирать лишние аллокации: StringBuilder, ArrayPool, stackalloc, структуры",
        "Ускорять числовые расчёты через Vector<T> и проверку IsSupported",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "csharp",
        "производительность",
        "benchmarkdotnet",
        "jit",
        "gc",
        "simd",
    ],
    "starter_code": code(
        r"""
        using System;
        using System.Collections.Generic;
        using System.Diagnostics;

        public static class Program
        {
            public static void Main()
            {
                var items = new List<int>();
                for (int i = 0; i < 20_000; i++)
                    items.Add(i);

                // Разогрев: JIT компилирует метод при первом вызове.
                ConcatStrings(items);
                JoinLoop(items);

                var sw = Stopwatch.StartNew();
                string slow = ConcatStrings(items);
                sw.Stop();
                Console.WriteLine($"Конкатенация: {sw.ElapsedMilliseconds} мс, длина {slow.Length}");

                sw.Restart();
                string fast = JoinLoop(items);
                sw.Stop();
                Console.WriteLine($"StringBuilder: {sw.ElapsedMilliseconds} мс, длина {fast.Length}");

                Console.WriteLine($"Результаты совпадают: {slow == fast}");
            }

            private static string ConcatStrings(List<int> items)
            {
                string result = "";
                foreach (int item in items)
                    result += item % 10;
                return result;
            }

            private static string JoinLoop(List<int> items)
            {
                var sb = new System.Text.StringBuilder(items.Count);
                foreach (int item in items)
                    sb.Append(item % 10);
                return sb.ToString();
            }
        }
        """
    ),
    "hints": [
        "Главный аргумент производительности — замер. Запускайте бенчмарки в конфигурации Release и только через BenchmarkDotNet.",
        "Оптимизируйте горячий путь, а не весь код: сначала профайлер показывает метод, который съедает время, и только потом вы его меняете.",
        "Большинство проблем с памятью в C# — это лишние аллокации в цикле: StringBuilder вместо конкатенации, ArrayPool вместо new byte[], Span<T> вместо копий.",
        "Для SIMD всегда проверяйте Vector.IsHardwareAccelerated или IsSupported и оставляйте скалярный запасной путь — иначе код не запустится на старых процессорах.",
    ],
    "content": [
        text(
            "Производительность в C# — это не набор трюков, а дисциплина измерений. "
            "Платформа выполняет код по-разному: JIT-компилятор превращает IL в машинный код "
            "при первом запуске метода, затем перекомпилирует его с оптимизациями, а сборщик "
            "мусора (GC) периодически останавливает потоки, чтобы очистить управляемую кучу. "
            "Поэтому любое «ускорение», не подтверждённое замером, — это догадка, которая "
            "часто делает код сложнее, но не быстрее.\n\n"
            "В этом уроке вы пройдёте весь путь: от постановки корректного бенчмарка до чтения "
            "профайлера, от понимания того, как JIT выбирает оптимизации, до конкретных приёмов — "
            "пулов массивов, `stackalloc`, `Span<T>` и векторных вычислений. Отдельно разберём "
            "публикацию приложения с ReadyToRun и Native AOT, где важно не только быстродействие, "
            "но и время холодного старта.\n\n"
            "Урок ориентирован на уровень продвинутых: примеры предполагают уверенное знание "
            "дженериков, структур и работы с памятью. Все примеры — рабочие фрагменты, которые "
            "можно запустить в консольном проекте .NET 8 и новее."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "писать корректные замеры на BenchmarkDotNet с `[MemoryDiagnoser]`, `[Params]` и `Baseline`;",
            "читать таблицу результатов и отличать значимую разницу от статистического шума;",
            "собирать трассы и живые метрики через `dotnet-trace`, `dotnet-counters` и `dotnet-dump`;",
            "объяснять, как работают Tier 0, Tier 1, ReadyToRun и Native AOT, и когда что выбирать;",
            "убирать лишние аллокации: `StringBuilder`, `ArrayPool<T>`, `stackalloc`, структуры вместо классов;",
            "ускорять числовые вычисления через `System.Numerics.Vector<T>` с безопасным запасным путём.",
        ),
        heading("Измерение важнее догадок"),
        text(
            "Прежде чем менять код, нужно понять, где он тратит время. Наивный подход — "
            "обернуть вызов в `Stopwatch` — годится только для грубой оценки: один прогон "
            "попадает под прогрев JIT, на время влияет фоновая нагрузка и работа GC, а разница "
            "в несколько процентов вообще находится внутри шума измерений.\n\n"
            "BenchmarkDotNet — библиотека для постановки замеров, которая делает всю рутину сама: "
            "запускает каждый метод в отдельном процессе, выполняет прогрев (warmup), "
            "делает несколько итераций, вычисляет среднее и доверительный интервал, "
            "считает аллокации и коллекции GC. Подключается она как обычный NuGet-пакет "
            "в отдельный консольный проект. Снизу — минимальный, но показательный набор."
        ),
        example(
            "csharp",
            r"""
            // Классы бенчмарков живут в отдельном консольном проекте,
            // а не в том же приложении, которое вы оптимизируете.
            using BenchmarkDotNet.Attributes;
            using BenchmarkDotNet.Running;

            BenchmarkRunner.Run<StringBenchmarks>();

            [MemoryDiagnoser]           // считать аллокации и коллекции GC
            [SimpleJob(BenchmarkDotNet.Jobs.RuntimeMoniker.Net80)]
            public class StringBenchmarks
            {
                private readonly string _longString = new('a', 10_000);

                [Benchmark(Baseline = true)]
                public int StringLength() => _longString.Length;

                [Benchmark]
                public int LinqCount() => System.Linq.Enumerable.Count(_longString);

                [Benchmark]
                public int SpanLength()
                {
                    ReadOnlySpan<char> span = _longString.AsSpan();
                    return span.Length;
                }
            }
            """,
        ),
        text(
            "Атрибут `[Benchmark]` помечает метод, который следует замерить. `Baseline = true` "
            "делает базовый метод точкой отсчёта: BenchmarkDotNet посчитает для остальных "
            "отношение (Ratio) относительно него. `[MemoryDiagnoser]` добавляет колонки "
            "`Gen0`, `Gen1`, `Gen2` и `Allocated`, без которых нельзя увидеть главную часть "
            "картины. `[Params]` подставляет в поля разные значения, чтобы увидеть, как "
            "поведение меняется с размером данных, а `[GlobalSetup]` создаёт тестовые данные "
            "один раз, вне замеряемой части."
        ),
        example(
            "csharp",
            r"""
            [MemoryDiagnoser]
            [SimpleJob(BenchmarkDotNet.Jobs.RuntimeMoniker.Net80)]
            public class CollectionBenchmarks
            {
                [Params(10, 100, 1_000, 10_000)]
                public int Size { get; set; }

                private List<int> _list = null!;
                private int[] _array = null!;

                [GlobalSetup]
                public void Setup()
                {
                    _array = Enumerable.Range(0, Size).ToArray();
                    _list = _array.ToList();
                }

                [Benchmark(Baseline = true)]
                public int ListForEach()
                {
                    int sum = 0;
                    foreach (int item in _list) sum += item;
                    return sum;
                }

                [Benchmark]
                public int ArrayFor()
                {
                    int sum = 0;
                    int[] array = _array;
                    for (int i = 0; i < array.Length; i++) sum += array[i];
                    return sum;
                }

                [Benchmark]
                public int SpanFor()
                {
                    int sum = 0;
                    ReadOnlySpan<int> span = _array;
                    for (int i = 0; i < span.Length; i++) sum += span[i];
                    return sum;
                }
            }
            """,
        ),
        heading("Как читать таблицу результатов", 3),
        text(
            "После запуска BenchmarkDotNet печатает таблицу. Она читается сверху вниз, "
            "но решение принимается по колонкам `Mean`, `Ratio` и `Allocated`. "
            "`Mean` — среднее время одной операции, `Error` и `StdDev` — разброс; "
            "если разница между двумя методами меньше этого разброса, считать её значимой нельзя. "
            "Ниже — типичный вывод на .NET 8 для приведённого набора."
        ),
        example(
            "text",
            r"""
            | Method      | Size  | Mean      | Error    | StdDev   | Gen0   | Allocated |
            |------------ |------ |----------:|---------:|---------:|-------:|----------:|
            | ListForEach | 1000  | 1.230 us  | 0.021 us | 0.019 us | 0.1234 |     256 B |
            | ArrayFor    | 1000  | 0.312 us  | 0.006 us | 0.005 us |      - |         - |
            | SpanFor     | 1000  | 1.940 us  | 0.030 us | 0.028 us |      - |         - |
            """,
        ),
        callout(
            "info",
            "Шум — тоже результат",
            "Если `StdDev` составляет четверть `Mean`, замер нестабилен: причиной могут быть "
            "фоновая нагрузка, ноутбук на батарее или параллельный запуск. "
            "Прогоняйте бенчмарки на разгруженной машине, в режиме Release и с отключённым "
            "энергосбережением, иначе вы будете оптимизировать шум.",
        ),
        text(
            "Строки `ArrayFor` и `ListForEach` показывают одинаковый результат по памяти, "
            "но разное время: перечислитель `List<T>` — структура и в куче не создаётся, "
            "однако `foreach` по списку делает дополнительную проверку версии и не даёт "
            "JIT так же уверенно убрать проверку границ, как в цикле по массиву. "
            "Индексный цикл по `Span<T>` в этом наборе оказался медленнее из-за чтения "
            "свойства `Length` и работы с интерфейсным значением — это повод не угадывать, "
            "а проверять каждую идею замером."
        ),
        heading("Профилирование: найти горячий путь"),
        text(
            "Бенчмарк отвечает на вопрос «что быстрее», а профайлер — «что тратит время в "
            "реальном приложении». Именно профиль показывает горячий путь (hot path) — цепочку "
            "методов, в которой сосредоточена основная нагрузка. Оптимизация кода вне горячего "
            "пути почти не даёт эффекта, даже если метод выглядит «неоптимально».\n\n"
            "Основные инструменты кроссплатформенны и работают как глобальные средства .NET: "
            "`dotnet-trace` снимает трассу выполнения, `dotnet-counters` показывает метрики "
            "в реальном времени, `dotnet-dump` снимает дамп памяти для анализа кучи. "
            "Все три устанавливаются командой `dotnet tool install -g` и не требуют пересборки "
            "приложения."
        ),
        example(
            "bash",
            r"""
            # Установка инструментов
            dotnet tool install -g dotnet-trace
            dotnet tool install -g dotnet-counters
            dotnet tool install -g dotnet-dump

            # Сбор трассы по идентификатору процесса
            dotnet trace collect --process-id 12345 \
                --providers Microsoft-DotNETCore-SampleProfiler

            # Или сразу с запуском приложения под трассой
            dotnet trace collect -- dotnet run -c Release --project MyApp.csproj

            # Конвертация в формат Speedscope для просмотра во фронтенде
            dotnet trace convert trace.nettrace --format speedscope

            # Живые метрики рантайма каждые 2 секунды
            dotnet counters monitor --process-id 12345 --counters System.Runtime
            """,
        ),
        text(
            "Трасса в формате `.nettrace` открывается в PerfView на Windows или конвертируется "
            "в Speedscope. Полезны три вида диаграмм: CPU Stacks — где поток проводит "
            "процессорное время (так находится горячий метод), GC Stats — сколько времени "
            "уходит на сборку мусора, Allocation Stacks — какие типы аллоцируются чаще всего. "
            "Если первым идёт `System.Byte[]`, вероятная причина — буферы, создаваемые в цикле. "
            "Дамп памяти (`dotnet-dump collect`, затем `dotnet-dump analyze`) полезен, когда "
            "приложение растёт в памяти или падает по нехватке ресурсов. Команды `dumpheap -stat` "
            "и `dumpheap -type ИмяТипа` показывают, сколько объектов каждого типа находится в куче "
            "и сколько они занимают. Это единственный надёжный способ понять, кто именно держит "
            "память, а не предполагать."
        ),
        callout(
            "warning",
            "Не оптимизируйте без профиля",
            "Интуиция о том, где медленно, обычно ошибочна: разработчики переоценивают "
            "стоимость мелких операций и недооценивают аллокации и синхронизацию. "
            "Сначала профиль, потом правки, затем повторный замер того же сценария.",
        ),
        heading("JIT, Tiered Compilation и ReadyToRun"),
        text(
            "C# компилируется в промежуточный язык IL, а не в машинный код. Компиляцию IL в "
            "машинные инструкции выполняет JIT (just-in-time) при первом вызове метода. "
            "С .NET Core 3.0 включена многоуровневая компиляция (Tiered Compilation): "
            "метод сначала компилируется быстро, без оптимизаций — это уровень Tier 0, "
            "чтобы приложение стартовало мгновенно. Рантайм собирает счётчики вызовов и циклов, "
            "и «горячий» метод перекомпилируется с полными оптимизациями — Tier 1.\n\n"
            "Из этого следует практический вывод: первый вызов метода медленнее последующих, "
            "и замер без прогрева искажает результат. Поэтому BenchmarkDotNet всегда делает "
            "warmup, а в собственных замерах через `Stopwatch` разогревочный прогон нужно "
            "делать вручную."
        ),
        example(
            "csharp",
            r"""
            using System;
            using System.Diagnostics;
            using System.Runtime.CompilerServices;

            public static class Program
            {
                public static void Main()
                {
                    const int n = 50_000_000;

                    // Прогрев: JIT компилирует метод, счётчики набирают статистику.
                    Sum(n / 10);

                    for (int round = 1; round <= 3; round++)
                    {
                        var sw = Stopwatch.StartNew();
                        long total = Sum(n);
                        sw.Stop();
                        Console.WriteLine($"Прогон {round}: {total}, {sw.ElapsedMilliseconds} мс");
                    }
                }

                private static long Sum(int n)
                {
                    long sum = 0;
                    for (int i = 0; i < n; i++)
                        sum += i;
                    return sum;
                }
            }
            """,
        ),
        text(
            "Приведённая программа выводит примерно такой результат: `Прогон 1: 1249999975000000, "
            "35 мс`, затем `Прогон 2: 1249999975000000, 8 мс` и `Прогон 3` с близким временем. "
            "Первый прогон заметно медленнее, потому что метод ещё не собран на уровне Tier 1; "
            "дальше время стабилизируется. Если запустить ту же программу в Debug, цифры будут "
            "в разы больше: в отладочной конфигурации JIT отключает основные оптимизации. "
            "Отсюда железное правило — замеры и публикация только в Release.\n\n"
            "Часто используемые подсказки компилятору задаются атрибутом `MethodImpl`. "
            "`AggressiveInlining` просит встроить небольшой метод в точку вызова, "
            "`NoInlining` запрещает встраивание, `AggressiveOptimization` сразу просит "
            "компилировать метод на уровне Tier 1, минуя профилирование, "
            "`NoOptimization` полностью отключает оптимизации."
        ),
        example(
            "csharp",
            r"""
            using System.Runtime.CompilerServices;

            public static class MathHelpers
            {
                // Малый метод с размером тела до порога инлайна — JIT встроит его сам,
                // атрибут лишь подтверждает намерение.
                [MethodImpl(MethodImplOptions.AggressiveInlining)]
                public static int Clamp(int value, int min, int max) =>
                    value < min ? min : (value > max ? max : value);

                // Нужен для честного замера отдельных шагов: без NoInlining
                // JIT может встроить метод и исказить профиль.
                [MethodImpl(MethodImplOptions.NoInlining)]
                public static long ComputeChecksum(ReadOnlySpan<byte> data)
                {
                    long hash = 0;
                    foreach (byte b in data)
                        hash = hash * 31 + b;
                    return hash;
                }

                // Заранее оптимизировать метод, который вызывается редко,
                // но критичен по задержке.
                [MethodImpl(MethodImplOptions.AggressiveOptimization)]
                public static double Normalize(double value, double min, double max) =>
                    max == min ? 0.0 : (value - min) / (max - min);
            }
            """,
        ),
        heading("ReadyToRun и Native AOT", 3),
        text(
            "JIT-компиляция тратит время и память на прогрев. Если холодный старт критичен — "
            "консольная утилита, серверное бессерверное приложение, мобильный сценарий — "
            "код можно скомпилировать заранее. ReadyToRun (R2R) публикует сборки с "
            "предкомпилированным машинным кодом для конкретной платформы: JIT всё равно "
            "остаётся доступным, но в большинстве случаев уже не нужен. "
            "Native AOT идёт дальше и создаёт полностью автономный исполняемый файл без "
            "рантайма JIT: он стартует за миллисекунды, занимает меньше памяти, "
            "но накладывает ограничения.\n\n"
            "Сравнение подходов приведено в таблице. Главный компромисс такой: AOT ускоряет "
            "старт и уменьшает потребление памяти, но лишает возможностей, требующих "
            "динамической генерации кода и разбора типов по имени."
        ),
        table(
            ["Подход", "Когда применяется", "Ограничения"],
            [
                ["JIT (.NET 8)", "Обычные приложения", "Прогрев и Tier 1 требуют времени"],
                ["ReadyToRun", "Сокращение холодного старта", "Больше размер сборки, код платформозависим"],
                ["Native AOT", "CLI-утилиты, контейнеры, минимальная память", "Нет `Reflection.Emit` и `dynamic`, ограничена рефлексия"],
                ["PGO (.NET 8)", "Максимальная скорость горячего кода", "Требует двухфазной сборки и нагрузки"],
            ],
        ),
        example(
            "csharp",
            r"""
            // Публикация ReadyToRun и Native AOT — это настройки csproj,
            // а не изменения в коде.

            // MyApp.csproj для ReadyToRun:
            // <PropertyGroup>
            //   <PublishReadyToRun>true</PublishReadyToRun>
            //   <PublishReadyToRunComposite>true</PublishReadyToRunComposite>
            // </PropertyGroup>

            // MyApp.csproj для Native AOT:
            // <PropertyGroup>
            //   <PublishAot>true</PublishAot>
            //   <StripSymbols>true</StripSymbols>
            //   <InvariantGlobalization>true</InvariantGlobalization>
            // </PropertyGroup>

            // Команды публикации:
            // dotnet publish -c Release -r win-x64 --self-contained   (ReadyToRun)
            // dotnet publish -c Release -r linux-x64                  (Native AOT)
            """,
        ),
        callout(
            "warning",
            "Native AOT и рефлексия",
            "`Reflection.Emit` и `dynamic` в AOT недоступны, `Assembly.LoadFrom` отсутствует, "
            "а рефлексия требует явных подсказок `[DynamicallyAccessedMembers]`; "
            "сериализация System.Text.Json без генератора исходного кода тоже не работает. Для JSON используйте source-generated контекст "
            "`JsonSerializerContext`, а для фабрик — зарегистрированные делегаты.",
        ),
        heading("Аллокации: главный источник проблем"),
        text(
            "Управляемая куча упрощает жизнь, но каждая аллокация стоит денег: память нужно "
            "выделить, а потом собрать. Молодое поколение (Gen 0) собирается часто и дёшево, "
            "но если объект пережил две сборки, он переезжает в Gen 1, а затем в Gen 2, "
            "коллекция которого полная и заметная по времени. Хуже того, большие объекты "
            "(от 85 000 байт) сразу попадают в Large Object Heap, которая не уплотняется и "
            "подвержена фрагментации.\n\n"
            "Главный приём простой: не создавайте мусор в горячем пути. Классический пример — "
            "конкатенация строк в цикле. Строки в C# неизменяемы, поэтому `result += item` "
            "на каждом шаге создаёт новую строку и копирует в неё содержимое старой. "
            "Сложность получается квадратичной, а объём мусора растёт пропорционально "
            "площади длины результата."
        ),
        example(
            "csharp",
            r"""
            using System;
            using System.Diagnostics;
            using System.Text;

            public static class Program
            {
                public static void Main()
                {
                    int before = GC.GetTotalAllocatedBytes(precise: true);

                    string slow = Concat(20_000);
                    int afterSlow = GC.GetTotalAllocatedBytes(precise: true);

                    string fast = Build(20_000);
                    int afterFast = GC.GetTotalAllocatedBytes(precise: true);

                    Console.WriteLine($"Конкатенация: {slow.Length} символов, " +
                        $"выделено {(afterSlow - before) / 1024 / 1024} МБ");
                    Console.WriteLine($"StringBuilder: {fast.Length} символов, " +
                        $"выделено {(afterFast - afterSlow) / 1024} КБ");
                }

                private static string Concat(int n)
                {
                    string result = "";
                    for (int i = 0; i < n; i++)
                        result += (char)('A' + i % 26);
                    return result;
                }

                private static string Build(int n)
                {
                    var sb = new StringBuilder(n);
                    for (int i = 0; i < n; i++)
                        sb.Append((char)('A' + i % 26));
                    return sb.ToString();
                }
            }
            """,
        ),
        text(
            "Вывод программы на .NET 8 выглядит примерно так: конкатенация выделяет сотни "
            "мегабайт и занимает заметное время, а `StringBuilder` — только заранее "
            "заданный буфер. Метод `GC.GetTotalAllocatedBytes(true)` — точный и удобный способ "
            "измерить объём аллокаций без внешних инструментов: разница значений до и после "
            "операции показывает, сколько байт выделено.\n\n"
            "В приложениях с интерфейсом этот набор встречается почти дословно: "
            "отчёт или журнал собирается в цикле через `+=`, а затем отправляется по сети. "
            "Для метода `Build` ёмкость буфера задаётся сразу, но альтернатива через "
            "`string.Join` тоже создаёт строку один раз и не требует ручного накопления."
        ),
        heading("Пулы, stackalloc и Span<T>", 3),
        text(
            "Когда без буфера не обойтись, память под него можно брать не у GC. "
            "`ArrayPool<T>.Shared` — общий пул массивов: `Rent` выдаёт буфер (возможно, "
            "больше запрошенного размера), `Return` возвращает его. Возвращать массив нужно "
            "в `finally`, иначе при исключении буфер утечёт, а содержимое перед возвратом "
            "лучше очистить, если в нём были конфиденциальные данные.\n\n"
            "`stackalloc` выделяет память в стеке потока, которая освобождается автоматически "
            "при выходе из метода: нет ни аллокации в куче, ни работы GC. Плата — ограниченный "
            "размер стека (обычно 1 МБ на поток), поэтому применять его стоит только для "
            "небольших буферов, порядка сотен байт. `Span<T>` в этом контексте — срез памяти "
            "без копирования: он может указывать и на массив, и на стек, и на неуправляемую "
            "память, при этом остаётся типобезопасным и проверяемым по границам."
        ),
        example(
            "csharp",
            r"""
            using System;
            using System.Buffers;
            using System.IO;

            public static class PooledProcessor
            {
                private const int SmallLimit = 512;

                // Малый буфер — на стеке, без участия GC.
                public static int CopySmall(ReadOnlySpan<byte> input, Span<byte> output)
                {
                    Span<byte> buffer = stackalloc byte[SmallLimit];
                    int count = Math.Min(input.Length, buffer.Length);
                    input.Slice(0, count).CopyTo(buffer);
                    buffer.Slice(0, count).CopyTo(output);
                    return count;
                }

                // Большой буфер — из общего пула с гарантированным возвратом.
                public static long Checksum(Stream input)
                {
                    long sum = 0;
                    byte[]? rented = ArrayPool<byte>.Shared.Rent(16 * 1024);
                    try
                    {
                        Span<byte> buffer = rented;
                        int read;
                        // Каждый вызов Read — системный вызов, поэтому читаем большими кусками.
                        while ((read = input.Read(buffer)) > 0)
                        {
                            foreach (byte b in buffer.Slice(0, read))
                                sum += b;
                        }
                    }
                    finally
                    {
                        // clearArray: false возвращает буфер быстрее, если данные не секретны.
                        ArrayPool<byte>.Shared.Return(rented, clearArray: false);
                    }

                    return sum;
                }
            }
            """,
        ),
        callout(
            "info",
            "Почему Span<T> безопаснее указателей",
            "`Span<T>` запрещает храниться в полях ссылочных типов, поэтому не может «пережить» "
            "стек, на который указывает. Проверка границ сохраняется, а JIT умеет её убирать "
            "в цикле вида `for (int i = 0; i < span.Length; i++)`, когда может доказать "
            "безопасность доступа. Такой проверки нет у обычного `byte[]` в циклах по "
            "переданному параметру.",
        ),
        text(
            "Ещё один источник скрытых аллокаций — упаковка (boxing). Она происходит, когда "
            "значимый тип передаётся туда, где ожидается `object` или интерфейс без ограничения "
            "на структуру. Каждый вызов `Tostring` структуры, добавление `int` в `ArrayList` "
            "или передача структуры в параметр типа `object` создаёт объект в куче.\n\n"
            "Лечение — дженерики с ограничением `where T : struct, IMyInterface`: вызов "
            "интерфейсного метода получает специализированный код без упаковки. "
            "Для коллекций ключей-значений используйте `Dictionary<TKey, TValue>` "
            "с конкретными типами, а не `Hashtable`."
        ),
        example(
            "csharp",
            r"""
            using System;

            public interface IProcessor
            {
                int Process(int value);
            }

            public struct Doubler : IProcessor
            {
                public int Process(int value) => value * 2;
            }

            public static class Boxings
            {
                // Плохо: p — интерфейсная переменная, структура упаковывается.
                public static int ThroughInterface(IProcessor p, int value) =>
                    p.Process(value);

                // Хорошо: специализация под конкретную структуру, без упаковки.
                public static int ThroughGeneric<T>(T p, int value)
                    where T : struct, IProcessor => p.Process(value);

                public static void Main()
                {
                    var doubler = new Doubler();
                    Console.WriteLine(ThroughInterface(doubler, 21)); // 42
                    Console.WriteLine(ThroughGeneric(doubler, 21));   // 42
                }
            }
            """,
        ),
        heading("SIMD: Vector<T> и интринсики"),
        text(
            "Процессоры умеют выполнять одну инструкцию над несколькими числами сразу — "
            "это SIMD (single instruction, multiple data). `System.Numerics.Vector<T>` даёт "
            "переносимый доступ к этому механизму: `Vector<float>.Count` показывает, сколько "
            "элементов помещается в вектор (4 для SSE, 8 для AVX2), а операторы применяются "
            "ко всем элементам параллельно.\n\n"
            "Код должен быть корректен и без аппаратного ускорения: `Vector.IsHardwareAccelerated` "
            "сообщает, включён ли SIMD, а остаток после основного цикла пишется отдельно, "
            "потому что длина массива редко кратна размеру вектора."
        ),
        example(
            "csharp",
            r"""
            using System;
            using System.Numerics;

            public static class SimdMath
            {
                public static void AddScalar(float[] a, float[] b, float[] result)
                {
                    for (int i = 0; i < a.Length; i++)
                        result[i] = a[i] + b[i];
                }

                public static void AddVector(float[] a, float[] b, float[] result)
                {
                    int i = 0;
                    int width = Vector<float>.Count;

                    for (; i <= a.Length - width; i += width)
                    {
                        var va = new Vector<float>(a, i);
                        var vb = new Vector<float>(b, i);
                        va += vb;
                        va.CopyTo(result, i);
                    }

                    for (; i < a.Length; i++)   // хвост
                        result[i] = a[i] + b[i];
                }

                public static float DotProduct(float[] a, float[] b)
                {
                    var sum = Vector<float>.Zero;
                    int i = 0;
                    int width = Vector<float>.Count;

                    for (; i <= a.Length - width; i += width)
                        sum += new Vector<float>(a, i) * new Vector<float>(b, i);

                    float total = Vector.Sum(sum);
                    for (; i < a.Length; i++)
                        total += a[i] * b[i];
                    return total;
                }
            }
            """,
        ),
        text(
            "Для максимального контроля над инструкциями есть интринсики: "
            "`System.Runtime.Intrinsics.X86.Avx2`, `Sse41`, `Fma` и `System.Runtime.Intrinsics.Arm.AdvSimd`. "
            "Они дают доступ к конкретным инструкциям, например к слитному умножению со "
            "сложением (FMA) `a * b + c`, которое выполняется одной инструкцией и точнее, "
            "чем раздельные умножение и сложение. Цена — привязка к архитектуре и необходимость "
            "писать запасной путь для каждого класса процессоров."
        ),
        example(
            "csharp",
            r"""
            using System;
            using System.Runtime.Intrinsics;
            using System.Runtime.Intrinsics.X86;

            public static class FmaMath
            {
                public static void MultiplyAdd(float[] a, float[] b, float[] c, float[] result)
                {
                    if (!Fma.IsSupported)
                    {
                        // Переносимый запасной вариант.
                        for (int i = 0; i < a.Length; i++)
                            result[i] = a[i] * b[i] + c[i];
                        return;
                    }

                    int i = 0;
                    for (; i <= a.Length - 8; i += 8)
                    {
                        var va = Avx.LoadVector256(a, i);
                        var vb = Avx.LoadVector256(b, i);
                        var vc = Avx.LoadVector256(c, i);
                        var vr = Fma.MultiplyAdd(va, vb, vc);
                        Avx.Store(result, i, vr);
                    }

                    for (; i < a.Length; i++)
                        result[i] = a[i] * b[i] + c[i];
                }
            }
            """,
        ),
        callout(
            "success",
            "Когда SIMD окупается",
            "Векторизация даёт выигрыш на плотных числовых циклах без ветвлений: обработка "
            "изображений, сигналов, матричная арифметика, подсчёт хешей. На коротких массивах "
            "или в коде с большим числом проверок накладные расходы перевешивают прибыль, "
            "поэтому решение принимается по бенчмарку, а не по теории.",
        ),
        heading("Рефакторинг по циклу"),
        text(
            "Работа над производительностью — итеративный процесс, а не разовая правка: "
            "измерить, найти узкое место, изменить, измерить снова. Ключевая деталь — сохранять "
            "один и тот же сценарий измерений: те же данные, тот же размер, та же машина, "
            "тот же режим Release. Иначе сравнение «до и после» теряет смысл.\n\n"
            "Полезно вести журнал оптимизаций: что изменили, почему и какой прирост получили. "
            "Это защищает от усложнения кода без выигрыша и помогает объяснить решения в ревью."
        ),
        numbered(
            "Сформулируйте цель в измеримых единицах: например, «снизить среднее время обработки запроса с 40 до 25 мс».",
            "Снимите профиль или бенчмарк на реалистичных данных и сохраните результаты.",
            "Выберите одно узкое место и внесите минимальное изменение, затрагивающее только его.",
            "Повторите замер на тех же данных и сравните с сохранённым результатом.",
            "Если прироста нет — откатите изменение: лишняя сложность без выигрыша вредна.",
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Замер в Debug", "JIT отключает оптимизации, цифры в разы больше", "Только `-c Release`"],
                ["Один прогон `Stopwatch`", "Результат искажён прогревом JIT и шумом", "Прогрев, серия прогонов или BenchmarkDotNet"],
                ["Нет `[MemoryDiagnoser]`", "Аллокации и GC остаются невидимыми", "Добавить атрибут и смотреть `Allocated`"],
                ["Бенчмарк без `[GlobalSetup]`", "Подготовка данных попадает в замер", "Готовить данные в `GlobalSetup`"],
                ["SIMD без проверки `IsSupported`", "Падение на процессоре без AVX2", "Проверка и скалярный запасной путь"],
                ["`stackalloc` на десятки килобайт", "Переполнение стека, падение процесса", "Буферы до ~1 КБ, иначе `ArrayPool<T>`"],
                ["Конкатенация строк в цикле", "Квадратичная сложность и мегабайты мусора", "`StringBuilder` с начальной ёмкостью"],
                ["Оптимизация без профиля", "Усложнение кода без реального выигрыша", "Сначала профиль, затем изменение"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняются в консольном проекте .NET 8 и новее, запуск через "
            "`dotnet run -c Release`. Бенчмарки выносятся в отдельный проект с пакетом "
            "`BenchmarkDotNet`."
        ),
        numbered(
            "Напишите бенчмарк, сравнивающий конкатенацию строк через `+=` и `StringBuilder` на 10, 1 000 и 10 000 элементах, с `[MemoryDiagnoser]` и базовой версией.",
            "Измерьте `GC.GetTotalAllocatedBytes(true)` вокруг трёх реализаций: `for` по массиву, `foreach` по `List<T>` и цикл по `ReadOnlySpan<T>`. Сравните вывод с таблицей BenchmarkDotNet.",
            "Замените `new byte[8192]` в цикле на `ArrayPool<byte>.Shared.Rent` с возвратом в `finally` и объясните, почему исчезли коллекции Gen 0.",
            "Реализуйте метод суммирования массива `float` в скалярной и векторной версиях через `Vector<float>`, проверьте совпадение результата и сравните время.",
            "Возьмите приложение, запустите `dotnet counters monitor` с `System.Runtime` и запишите значения `cpu-usage`, `gc-heap-size` и `threadpool-queue-length` под нагрузкой.",
        ),
        callout(
            "success",
            "Подсказка к заданию 3",
            "Массив из пула длиннее запрошенного размера, поэтому обрабатывайте только "
            "первые `n` байт через `buffer.AsSpan(0, n)` и возвращайте буфер ровно один раз.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему замер в конфигурации Debug даёт неверную картину производительности?",
            "Что такое Tier 0 и Tier 1 в многоуровневой компиляции?",
            "Зачем нужны колонки `Gen0` и `Allocated` в таблице BenchmarkDotNet?",
            "В каких случаях `stackalloc` не подходит, и что использовать вместо него?",
            "Что происходит при упаковке структуры и как её избежать в дженерик-методе?",
            "Почему перед использованием `Avx2` нужно проверять `IsSupported`?",
        ),
        heading("Ответы", 3),
        numbered(
            "В Debug JIT отключает основные оптимизации и добавляет отладочные проверки, поэтому время выполнения не отражает поведение опубликованного приложения.",
            "Tier 0 — быстрая компиляция без оптимизаций для моментального старта, Tier 1 — перекомпиляция горячего метода с полными оптимизациями после сбора профиля вызовов.",
            "`Gen0` показывает, сколько раз сработала сборка мусора нулевого поколения, а `Allocated` — сколько байт выделено на одну операцию; вместе они вскрывают скрытое давление на GC.",
            "`stackalloc` ограничен размером стека потока (обычно около 1 МБ), поэтому для больших или неизвестных заранее буферов используется `ArrayPool<T>.Shared`.",
            "Структура копируется в объект в куче при передаче в параметр типа `object` или интерфейс. Ограничение `where T : struct, IMyInterface` даёт специализацию без упаковки.",
            "На процессоре без AVX2 метод упадёт или поведёт себя непредсказуемо. Проверка `IsSupported` позволяет выбрать скалярный запасной путь.",
        ),
        heading("Итоги"),
        bullets(
            "Производительность начинается с замера: BenchmarkDotNet в Release с `[MemoryDiagnoser]` и прогревом.",
            "`Mean` показывает среднее, `StdDev` — шум; разница меньше шума не считается значимой.",
            "Профайлер (`dotnet-trace`, `dotnet-counters`, `dotnet-dump`) находит горячий путь и виновника аллокаций.",
            "Tiered Compilation компилирует метод быстро в Tier 0 и оптимизирует горячий код в Tier 1.",
            "ReadyToRun сокращает холодный старт, Native AOT убирает JIT, но ограничивает рефлексию и `dynamic`.",
            "Сокращайте аллокации: `StringBuilder` с ёмкостью, `ArrayPool<T>`, `stackalloc` до ~1 КБ, `Span<T>` вместо копий.",
            "Упаковку структур убирают дженерики с ограничением `where T : struct, IInterface`.",
            "`Vector<T>` и интринсики ускоряют плотные числовые циклы, но требуют проверки поддержки и запасного пути.",
        ),
        heading("Что дальше"),
        text(
            "Вы научились измерять, профилировать и оптимизировать код C# на уровне рантайма. "
            "Эти навыки применяются в любом следующем разделе программы: в архитектуре, "
            "асинхронности и работе с данными. Возьмите привычку: перед оптимизацией — "
            "бенчмарк, после правки — тот же бенчмарк."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "BenchmarkDotNet, официальное руководство — benchmarkdotnet.org/articles/guides/getting-started.html",
            "Microsoft Learn: производительность .NET — learn.microsoft.com/dotnet/core/performance/",
            "Microsoft Learn: Tiered Compilation — learn.microsoft.com/dotnet/core/run-time-config/compilation",
            "Microsoft Learn: Native AOT deployment — learn.microsoft.com/dotnet/core/deploying/native-aot",
            "Microsoft Learn: System.Numerics и Vector<T> — learn.microsoft.com/dotnet/api/system.numerics",
            "Sasha Goldshtein, «Pro .NET Performance»; Ben Watson, «Writing High-Performance .NET Code»",
        ),
    ],
}
