"""Урок 3.5 курса csharp: асинхронность и конкурентность."""

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
    "topic_order": 5,
    "name": "3.5. Асинхронность и конкурентность",
    "slug": "csharp-3-5-асинхронность-и-конкурентность",
    "short_description": (
        "Как async/await устроен под капотом, когда использовать ValueTask, "
        "Channel для конвейеров данных, Parallel и PLINQ для CPU-bound работы "
        "и какие примитивы синхронизации не блокируют поток."
    ),
    "topic_name": "Асинхронность и конкурентность",
    "topic_description": (
        "Углублённый разбор асинхронности в C#: машина состояний компилятора, "
        "ConfigureAwait, ValueTask и IValueTaskSource, System.Threading.Channels, "
        "Parallel/PLINQ, SemaphoreSlim, Lock, ReaderWriterLockSlim, Interlocked "
        "и выбор между асинхронной и конкурентной обработкой."
    ),
    "learning_objectives": [
        "Объяснять, как компилятор превращает async-метод в машину состояний, и оценивать её накладные расходы",
        "Корректно расставлять ConfigureAwait и избегать взаимных блокировок при смешивании sync и async кода",
        "Выбирать между Task и ValueTask и соблюдать правила одноразового ожидания ValueTask",
        "Строить конвейеры producer/consumer на System.Threading.Channels с backpressure",
        "Применять Parallel.For, Parallel.ForEach и PLINQ только к CPU-bound задачам с независимыми итерациями",
        "Ограничивать конкурентность через SemaphoreSlim, выбирать Lock, ReaderWriterLockSlim и Interlocked по сценарию",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "csharp",
        "async",
        "await",
        "конкурентность",
        "channels",
        "синхронизация",
    ],
    "starter_code": code(
        """
        using System;
        using System.Linq;
        using System.Threading.Tasks;

        public static class Program
        {
            public static async Task Main()
            {
                int[] inputs = Enumerable.Range(1, 5).ToArray();

                // Запускаем все операции одновременно, ждём все сразу.
                Task<int>[] pending = inputs.Select(SquareAsync).ToArray();
                int[] results = await Task.WhenAll(pending);

                Console.WriteLine(string.Join(", ", results));
            }

            private static async Task<int> SquareAsync(int value)
            {
                await Task.Delay(10); // имитация ввода-вывода
                return value * value;
            }
        }
        """
    ),
    "hints": [
        "Никогда не блокируйте асинхронный код через .Result или .Wait(): в контексте с SynchronizationContext это гарантированная взаимная блокировка. Поднимайте async вверх по стеку.",
        "ValueTask можно ожидать только один раз и нельзя использовать как поле или кэшировать, если это не единственный потребитель. Для публичного API предпочитайте Task.",
        "Parallel.ForEach не ждёт async-делегат: лямбда async void тут означает потерю результата и исключений. Для асинхронной работы берите Task.WhenAll или Channel.",
        "Не держите lock внутри async-метода вокруг await: Monitor привязан к потоку, а после await поток другой. Для асинхронной критической секции используйте SemaphoreSlim.WaitAsync.",
    ],
    "content": [
        text(
            "Асинхронность в C# существует не для того, чтобы «ускорить» код, а для того, "
            "чтобы поток не простаивал в ожидании. Пока сетевой запрос или чтение файла "
            "не завершились, поток возвращается в пул и обслуживает другие задачи. "
            "Поэтому асинхронный сервер обрабатывает тысячи соединений немногими потоками, "
            "а интерфейс не замирает на время запроса к базе данных.\n\n"
            "Конкурентность — соседнее, но другое понятие: несколько операций выполняются "
            "одновременно и разделяют общие данные. Здесь появляются свои задачи: "
            "как не потерять запись счётчика, как ограничить число одновременных обращений, "
            "как распределить вычисления по ядрам и как передать данные между этапами "
            "обработки без лишних блокировок.\n\n"
            "Урок разбирает обе стороны: устройство async/await на уровне компилятора и рантайма, "
            "инструменты для I/O-bound сценариев (ValueTask, Channel), инструменты для CPU-bound "
            "сценариев (Parallel, PLINQ) и примитивы синхронизации, которые не блокируют поток."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "Объяснять, как компилятор превращает async-метод в машину состояний, и оценивать её накладные расходы.",
            "Корректно расставлять ConfigureAwait и избегать взаимных блокировок при смешивании синхронного и асинхронного кода.",
            "Выбирать между Task и ValueTask и соблюдать правила одноразового ожидания ValueTask.",
            "Строить конвейеры producer/consumer на System.Threading.Channels с backpressure.",
            "Применять Parallel.For, Parallel.ForEach и PLINQ только к CPU-bound задачам с независимыми итерациями.",
            "Ограничивать конкурентность через SemaphoreSlim и выбирать между Lock, ReaderWriterLockSlim и Interlocked по сценарию.",
        ),
        heading("Что происходит при компиляции async-метода"),
        text(
            "**Машина состояний** — структура, которую компилятор создаёт для тела async-метода: "
            "она хранит номер текущего шага и все локальные переменные, которые должны пережить await. "
            "Ключевое слово await не запускает поток и не блокирует его: оно проверяет, завершилась ли "
            "ожидаемая операция, и если нет — регистрирует продолжение и передаёт управление вызывающему коду.\n\n"
            "Продолжение — это код, который выполнится после завершения операции. Оно запускается заново "
            "через метод MoveNext, но уже не с начала метода, а с номера состояния, соответствующего "
            "ожидаемому await. Локальные переменные восстанавливаются из полей этой структуры.\n\n"
            "Если awaited-задача уже завершена к моменту проверки, метод продолжает работать синхронно "
            "в текущем потоке. Это так называемый синхронный путь (fast path): аллокация Task "
            "и переключение потока в этом случае не нужны."
        ),
        example(
            "csharp",
            """
            // Исходный код
            public static async Task<int> GetLengthAsync(HttpClient client, string url)
            {
                string data = await client.GetStringAsync(url);
                return data.Length;
            }

            // Во что его примерно превращает компилятор
            [AsyncStateMachine(typeof(GetLengthAsyncStateMachine))]
            public static Task<int> GetLengthAsync(HttpClient client, string url)
            {
                var stateMachine = new GetLengthAsyncStateMachine
                {
                    Builder = AsyncTaskMethodBuilder<int>.Create(),
                    Client = client,
                    Url = url,
                    State = -1
                };

                stateMachine.Builder.Start(ref stateMachine);
                return stateMachine.Builder.Task;
            }

            private struct GetLengthAsyncStateMachine : IAsyncStateMachine
            {
                public int State;                 // -1 старт, 0 ожидание, -2 исключение
                public AsyncTaskMethodBuilder<int> Builder;
                public HttpClient Client;
                public string Url;
                public TaskAwaiter<string> Awaiter;
                public string Data;

                public void MoveNext()
                {
                    int result;
                    try
                    {
                        TaskAwaiter<string> awaiter;
                        if (State != 0)
                        {
                            awaiter = Client.GetStringAsync(Url).GetAwaiter();
                            if (!awaiter.IsCompleted)
                            {
                                State = 0;
                                Awaiter = awaiter;
                                Builder.AwaitUnsafeOnCompleted(ref awaiter, ref this);
                                return;
                            }
                        }
                        else
                        {
                            awaiter = Awaiter;
                        }

                        Data = awaiter.GetResult();
                        result = Data.Length;
                    }
                    catch (Exception ex)
                    {
                        State = -2;
                        Builder.SetException(ex);
                        return;
                    }

                    State = -2;
                    Builder.SetResult(result);
                }

                public void SetStateMachine(IAsyncStateMachine stateMachine) { }
            }
            """
        ),
        text(
            "В реальности компилятор генерирует более тонкий код, но схема верна. Обратите внимание на три момента. "
            "Во-первых, при первом вызове структура машины создаётся и передаётся в builder: "
            "пока выполнение синхронно, она живёт в стеке. Во-вторых, при первом же незавершённом await "
            "машина копируется в кучу, потому что продолжение будет вызвано позже и уже не в стеке этого метода. "
            "В-третьих, исключения не выбрасываются из MoveNext: они записываются в builder, "
            "и вызывающий видит обычный faulted Task."
        ),
        table(
            ["Ситуация", "Аллокации", "Переключение потока"],
            [
                ["Метод вернулся до первого await", "обычно ни одной (или одна кэшированная задача)", "нет"],
                ["await дождался уже завершённой задачи", "машина в куче, Task", "нет"],
                ["await дождался незавершённой задачи", "машина в куче, Task, продолжение", "да, через TaskScheduler"],
                ["async void", "машина в куче, исключения уходят в контекст", "да"],
            ],
        ),
        callout(
            "info",
            "await не создаёт поток",
            "await освобождает текущий поток, а не порождает новый. Если в приложении тысяча одновременных HTTP-запросов, "
            "это не тысяча потоков, а тысяча незавершённых задач и небольшое число потоков, обслуживающих сокеты."
        ),
        heading("ConfigureAwait и взаимные блокировки"),
        text(
            "После await продолжение по умолчанию возвращается в **SynchronizationContext** — "
            "объект, который описывает, куда нужно отправить продолжение. В Windows-приложениях "
            "это UI-поток; в классическом ASP.NET — контекст запроса. Если такой контекст есть, "
            "возврат в него стоит денег: продолжение ставится в очередь контекста и ждёт, "
            "пока он освободится.\n\n"
            "Вызов ConfigureAwait(false) означает: «продолжение может выполниться в любом потоке, "
            "возвращаться в исходный контекст не нужно». В библиотеках это правило по умолчанию, "
            "потому что библиотека не знает, в каком контексте её вызовут, и не должна зависеть "
            "от UI-потока. В ASP.NET Core собственного SynchronizationContext нет, "
            "поэтому там ConfigureAwait(false) на практике ничего не меняет, но в коде библиотек "
            "его всё равно оставляют.\n\n"
            "Главная причина ошибок — синхронное ожидание асинхронной операции. Вызов .Result или .Wait() "
            "занимает текущий поток, а продолжение хочет вернуться именно в этот поток. "
            "Он занят ожиданием, продолжение не может выполниться — метод ждёт вечно. "
            "Это **взаимная блокировка** (deadlock)."
        ),
        example(
            "csharp",
            """
            // Плохо: синхронный метод ждёт асинхронный результат
            public static string LoadBlocking(string url)
            {
                using var client = new HttpClient();
                // В контексте с SynchronizationContext это взаимная блокировка.
                return client.GetStringAsync(url).Result;
            }

            // Хорошо: асинхронность поднимается до самого верха
            public static async Task<string> LoadAsync(string url)
            {
                using var client = new HttpClient();
                return await client.GetStringAsync(url);
            }

            // Библиотечный метод не захватывает контекст вызывающего кода
            public static async Task<int> CountAsync(HttpClient client, string url)
            {
                string body = await client.GetStringAsync(url).ConfigureAwait(false);
                return body.Length;
            }

            // Если синхронный мост действительно неизбежен (консольное приложение,
            // обработчик события без async), используйте GetAwaiter().GetResult():
            // он не оборачивает исключение в AggregateException.
            public static int LoadFromConsole(string url)
                => LoadAsync(url).GetAwaiter().GetResult();
            """
        ),
        callout(
            "warning",
            ".Result и .Wait() в асинхронном коде",
            "Внутри обработчиков UI и классического ASP.NET синхронное ожидание асинхронной операции "
            "приводит к зависанию. Правильное решение — сделать метод цепочки async Task, "
            "а не добавлять ConfigureAwait в одном месте и надеяться, что проблема уйдёт."
        ),
        heading("ValueTask: когда аллокация мешает"),
        text(
            "**Task** — ссылочный тип, объект в куче. Каждый async-метод, возвращающий Task, "
            "в общем случае создаёт хотя бы один такой объект. Для большинства кода это неважно: "
            "доминирует время сетевого вызова или чтения диска. Но в горячем пути, который "
            "вызывается миллионы раз и чаще всего завершается синхронно (например, попадание в кэш), "
            "аллокации становятся заметными.\n\n"
            "**ValueTask** и **ValueTask<T>** — структуры, которые могут хранить либо готовый результат, "
            "либо обычный Task, либо ссылку на IValueTaskSource. При синхронном завершении "
            "объект в куче не создаётся вообще. Это делает ValueTask подходящим для методов, "
            "которые вызываются часто и часто отвечают без ожидания.\n\n"
            "Плата за это — строгие правила. ValueTask можно ожидать только один раз. "
            "Его нельзя сохранять в поле для последующего использования несколькими потребителями, "
            "нельзя вызывать AsTask дважды и полагаться на результат. "
            "**IValueTaskSource** — интерфейс для ручной реализации такой задачи; "
            "на нём построены, например, ожидания в System.IO.Pipelines. В обычном коде "
            "его почти не пишут, а используют готовый ManualResetValueTaskSourceCore."
        ),
        example(
            "csharp",
            """
            using System.Collections.Generic;
            using System.Threading.Tasks;

            public sealed class UserCache
            {
                private readonly Dictionary<int, string> _cache = new();

                // Горячий путь: если значение есть, аллокации нет.
                public ValueTask<string> GetNameAsync(int id)
                {
                    if (_cache.TryGetValue(id, out string? cached))
                    {
                        return new ValueTask<string>(cached);
                    }

                    return LoadFromDatabaseAsync(id);
                }

                private async ValueTask<string> LoadFromDatabaseAsync(int id)
                {
                    await Task.Delay(20); // имитация запроса к базе данных
                    string name = $"user-{id}";
                    _cache[id] = name;
                    return name;
                }
            }
            """
        ),
        example(
            "csharp",
            """
            var cache = new UserCache();

            // Первое обращение: значение отсутствует, работаем асинхронно.
            string first = await cache.GetNameAsync(7);
            // Второе обращение: попадание в кэш, ValueTask уже завершён.
            string second = await cache.GetNameAsync(7);

            Console.WriteLine(first);
            Console.WriteLine(second);

            // Ошибочное использование: ValueTask нельзя ожидать дважды
            // и нельзя сохранять для нескольких потребителей.
            // ValueTask<string> broken = cache.GetNameAsync(7);
            // await broken;
            // await broken; // не определено спецификацией

            // Если нужно несколько раз, один раз преобразуйте в Task:
            Task<string> single = cache.GetNameAsync(7).AsTask();
            await single;
            await single;
            """
        ),
        text("Вывод: "),
        example(
            "text",
            """
            user-7
            user-7
            """
        ),
        table(
            ["Критерий", "Task", "ValueTask"],
            [
                ["Тип", "ссылочный, объект в куче", "структура, часто без аллокации"],
                ["Сколько раз ожидать", "сколько угодно", "один раз"],
                ["Хранить в поле", "можно", "нельзя без осторожности"],
                ["Публичный API библиотеки", "предпочтительно", "только при доказанной выгоде"],
                ["Внутренний горячий путь", "работает, но аллоцирует", "уместен"],
            ],
        ),
        callout(
            "warning",
            "Правило одного ожидания",
            "Если значение ValueTask нужно повторно использовать, вызовите AsTask() один раз "
            "и работайте с Task. Двойное ожидание ValueTask приводит к неопределённому поведению: "
            "второй await может вернуть мусор или бросить исключение."
        ),
        heading("Channels: конвейеры без ручной синхронизации"),
        text(
            "**System.Threading.Channels** — асинхронная очередь с раздельными ролями писателя и читателя. "
            "Писатель (producer) кладёт элементы, читатель (consumer) их забирает. "
            "Очередь сама решает, кому и когда продолжить выполнение, — блокировки и мониторинг не нужны.\n\n"
            "Канал бывает **неограниченным** (CreateUnbounded) и **ограниченным** (CreateBounded). "
            "Ограниченный канал задаёт **backpressure** — обратное давление: когда буфер полон, "
            "WriteAsync не завершается, пока читатель не заберёт элемент. Это защищает память "
            "от переполнения, если производитель быстрее потребителя.\n\n"
            "У канала два конца: `channel.Writer` и `channel.Reader`. Метод `Complete()` сообщает, "
            "что новых элементов не будет. На стороне читателя `ReadAllAsync()` — асинхронный поток, "
            "в котором можно писать `await foreach`; он завершается после Complete, "
            "когда буфер опустеет."
        ),
        example(
            "csharp",
            """
            using System.Threading.Channels;

            var channel = Channel.CreateBounded<int>(new BoundedChannelOptions(4)
            {
                FullMode = BoundedChannelFullMode.Wait, // производитель ждёт, а не теряет данные
                SingleReader = true,
                SingleWriter = true,
                AllowSynchronousContinuations = false
            });

            // Производитель
            Task producer = Task.Run(async () =>
            {
                for (int i = 1; i <= 10; i++)
                {
                    await channel.Writer.WriteAsync(i);
                }
                channel.Writer.Complete();
            });

            // Потребитель
            Task consumer = Task.Run(async () =>
            {
                int sum = 0;
                await foreach (int item in channel.Reader.ReadAllAsync())
                {
                    sum += item;
                }
                Console.WriteLine($"Сумма: {sum}");
            });

            await Task.WhenAll(producer, consumer);
            """
        ),
        text(
            "Вывод: Сумма: 55. Буфер размером 4 заставляет производителя ждать, "
            "когда потребитель не успевает: программа не держит в памяти все десять чисел заранее "
            "и не теряет ни одного элемента."
        ),
        heading("Конвейер из нескольких потребителей", 3),
        text(
            "Несколько читателей ограниченного канала образуют естественный пул воркеров: "
            "элементы распределяются между ними без ручной блокировки. "
            "Именно так строят пакетную обработку, когда на один вход приходится много независимых задач.\n\n"
            "Опция SingleReader = true сообщает каналу, что читатель один; если читателей несколько, "
            "её нужно выключать, иначе порядок и безопасность не гарантированы. "
            "Передача CancellationToken в ReadAllAsync и WriteAsync позволяет "
            "корректно завершить конвейер по внешнему сигналу."
        ),
        example(
            "csharp",
            """
            using System.Linq;
            using System.Threading;
            using System.Threading.Channels;

            Channel<int> input = Channel.CreateUnbounded<int>();

            async Task<int> ProcessAsync(int value, CancellationToken ct)
            {
                await Task.Delay(5, ct);
                return value * value;
            }

            // Один производитель кладёт 20 чисел
            _ = Task.Run(async () =>
            {
                for (int i = 1; i <= 20; i++)
                {
                    input.Writer.TryWrite(i);
                }
                input.Writer.Complete();
            });

            // Четыре независимых воркера делят одну очередь
            var workers = Enumerable.Range(0, 4).Select(_ => Task.Run(async () =>
            {
                int local = 0;
                await foreach (int value in input.Reader.ReadAllAsync())
                {
                    local += await ProcessAsync(value, CancellationToken.None);
                }
                return local;
            })).ToArray();

            int[] partial = await Task.WhenAll(workers);
            Console.WriteLine($"Сумма квадратов: {partial.Sum()}");
            """
        ),
        text(
            "Вывод: Сумма квадратов: 2870. Это сумма 1² + 2² + … + 20². "
            "Каждый воркер накапливает свою часть, итог складывается один раз после ожидания всех задач — "
            "общий счётчик не нужен, а значит, не нужен и lock вокруг него."
        ),
        heading("Parallel и PLINQ для вычислений"),
        text(
            "Асинхронность полезна, когда работа ждёт. Если работа считает — распараллеливание по ядрам "
            "делают **Parallel** и **PLINQ**. Их задача — разбить диапазон или коллекцию на части "
            "и выполнить их на нескольких потоках пула.\n\n"
            "`Parallel.For` и `Parallel.ForEach` подходят, когда на каждую итерацию приходится тяжёлое вычисление, "
            "а итерации независимы. `ParallelOptions` задаёт MaxDegreeOfParallelism и CancellationToken. "
            "Объект `ParallelLoopState` позволяет досрочно завершить цикл: `Break()` останавливает "
            "итерации с большим индексом, `Stop()` — все немедленно.\n\n"
            "**PLINQ** — это LINQ, выполняемый параллельно: после `.AsParallel()` методы Where, Select и OrderBy "
            "разбиваются по потокам. Для коротких запросов накладные расходы на разбиение и слияние "
            "могут превысить выгоду; PLINQ выбирают, когда одна итерация заметно дороже накладных расходов."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Diagnostics;
            using System.Linq;
            using System.Threading;
            using System.Threading.Tasks;

            static long Burn(int n)
            {
                long acc = 0;
                for (int i = 0; i < 50_000; i++) acc += (long)i % (n + 1);
                return acc;
            }

            var data = Enumerable.Range(1, 64).ToArray();

            Stopwatch sw = Stopwatch.StartNew();
            long sequential = data.Select(Burn).Sum();
            sw.Stop();
            Console.WriteLine($"Последовательно: {sequential}, {sw.ElapsedMilliseconds} мс");

            sw.Restart();
            long parallel = data.AsParallel()
                .WithDegreeOfParallelism(Environment.ProcessorCount)
                .Select(Burn)
                .Sum();
            sw.Stop();
            Console.WriteLine($"PLINQ: {parallel}, {sw.ElapsedMilliseconds} мс");
            """
        ),
        text(
            "Вывод (время зависит от машины): оба варианта печатают одинаковую сумму, "
            "но PLINQ проходит этап Select на нескольких ядрах и на 4–8-ядерной машине тратит меньше времени. "
            "Функция Burn должна быть чистой: она не меняет общие данные, поэтому результат складывается безопасно."
        ),
        callout(
            "warning",
            "Parallel не ждёт async",
            "Parallel.ForEach принимает Action, а async-лямбда превращается в async void. "
            "Цикл завершится раньше, чем операции, а исключения потеряются. "
            "Для асинхронной работы используйте Task.WhenAll или Channel с воркерами."
        ),
        example(
            "csharp",
            """
            using System.Collections.Generic;
            using System.Linq;
            using System.Threading;
            using System.Threading.Tasks;

            // Если итераций много и они дешёвые, разбиение на части снижает накладные расходы.
            var totals = new long[8];

            Parallel.For(0, 8, i =>
            {
                long local = 0;
                for (int j = i * 100_000; j < (i + 1) * 100_000; j++)
                {
                    local += j % 7;
                }
                totals[i] = local; // каждая ячейка пишется одним потоком
            });

            Console.WriteLine(totals.Sum());

            // Ограничение конкурентности при внешних ограничениях памяти или CPU
            Parallel.ForEach(Enumerable.Range(1, 100), new ParallelOptions
            {
                MaxDegreeOfParallelism = 2
            }, i => Burn(i));
            """
        ),
        heading("Ограничение конкурентности"),
        text(
            "**SemaphoreSlim** — счётчик разрешений с асинхронным ожиданием. "
            "Конструктор `new SemaphoreSlim(initialCount, maxCount)` задаёт стартовое и максимальное число. "
            "`WaitAsync()` уменьшает счётчик, не занимая поток, `Release()` увеличивает его. "
            "Это стандартный способ сделать так, чтобы к внешнему ресурсу одновременно обращались "
            "не более N операций.\n\n"
            "Правило дисциплины то же, что для любого семафора: Release() вызывается в finally. "
            "Если исключение между WaitAsync и Release, разрешение никогда не вернётся, "
            "и через N сбоев все последующие вызовы зависнут."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Linq;
            using System.Threading;
            using System.Threading.Tasks;

            static async Task<string> FetchAsync(string url, SemaphoreSlim gate)
            {
                await gate.WaitAsync();
                try
                {
                    await Task.Delay(50); // имитация сетевого запроса
                    return url.ToUpperInvariant();
                }
                finally
                {
                    gate.Release();
                }
            }

            var gate = new SemaphoreSlim(3, 3); // не более 3 запросов одновременно
            string[] urls = Enumerable.Range(1, 10).Select(i => $"site/{i}").ToArray();
            string[] results = await Task.WhenAll(urls.Select(u => FetchAsync(u, gate)));

            Console.WriteLine(string.Join(", ", results));
            """
        ),
        text(
            "Вывод: SITE/1, SITE/2, … SITE/10. Все десять задач созданы сразу, "
            "но проходят через семафор по три, поэтому внешний ресурс не получит "
            "десять одновременных запросов."
        ),
        heading("Lock, ReaderWriterLockSlim и Interlocked"),
        text(
            "Когда общие данные изменяются из нескольких потоков, нужна взаимоисключающая секция. "
            "Классический `lock` компилируется в Monitor.Enter и Monitor.Exit и привязан к потоку: "
            "поток должен отпустить блокировку сам. Поэтому вокруг await внутри lock держать нельзя: "
            "после await продолжение может выполниться в другом потоке.\n\n"
            "**Lock** — тип из пространства имён System.Threading, появившийся в .NET 9 "
            "вместе с ключевым словом `lock` над экземпляром. Для занятых секций он дешевле объекта-заглушки, "
            "но правила те же. **ReaderWriterLockSlim** даёт несколько читателей одновременно "
            "и одного писателя; это выгодно в кэшах, где чтений во много раз больше записей. "
            "**Interlocked** выполняет простые операции над одним полем атомарно без блокировки: "
            "Increment, Add, Exchange, CompareExchange."
        ),
        example(
            "csharp",
            """
            using System.Collections.Generic;
            using System.Threading;
            using System.Threading.Tasks;

            public sealed class Stats
            {
                private readonly object _gate = new();
                private readonly Dictionary<string, int> _hits = new();
                private long _total;

                // Атомарный счётчик без блокировки
                public void Hit(string key)
                {
                    lock (_gate)
                    {
                        _hits.TryGetValue(key, out int current);
                        _hits[key] = current + 1;
                    }

                    Interlocked.Increment(ref _total);
                }

                public int Total => (int)Interlocked.Read(ref _total);

                public bool TryGet(string key, out int value)
                {
                    lock (_gate)
                    {
                        return _hits.TryGetValue(key, out value);
                    }
                }
            }
            """
        ),
        example(
            "csharp",
            """
            using System.Collections.Generic;
            using System.Threading;

            public sealed class ReadHeavyCache
            {
                private readonly ReaderWriterLockSlim _rw = new();
                private readonly Dictionary<string, string> _store = new();

                public string GetOrAdd(string key)
                {
                    _rw.EnterReadLock();
                    try
                    {
                        if (_store.TryGetValue(key, out string? value))
                        {
                            return value;
                        }
                    }
                    finally
                    {
                        _rw.ExitReadLock();
                    }

                    _rw.EnterWriteLock();
                    try
                    {
                        // Повторная проверка: между чтением и записью другой поток мог всё заполнить.
                        if (_store.TryGetValue(key, out string? value))
                        {
                            return value;
                        }

                        _store[key] = $"value-{key}";
                        return _store[key];
                    }
                    finally
                    {
                        _rw.ExitWriteLock();
                    }
                }
            }
            """
        ),
        text(
            "Обратите внимание на повторную проверку под блокировкой записи: между выходом из чтения "
            "и входом в запись другой поток мог добавить значение. Такая схема называется "
            "double-checked locking, и без второй проверки в кэш попали бы дубли.\n\n"
            "Для асинхронной критической секции, внутри которой есть await, ReaderWriterLockSlim и lock не годятся. "
            "Берите SemaphoreSlim с одним разрешением или готовый AsyncLock из библиотеки Nito.AsyncEx."
        ),
        heading("Асинхронная критическая секция", 3),
        example(
            "csharp",
            """
            using System;
            using System.Threading;
            using System.Threading.Tasks;

            public sealed class AsyncSerialQueue
            {
                private readonly SemaphoreSlim _mutex = new(1, 1);
                private int _processed;

                public async Task RunAsync(Func<Task> work)
                {
                    await _mutex.WaitAsync();
                    try
                    {
                        await work();
                        _processed++;
                    }
                    finally
                    {
                        _mutex.Release();
                    }
                }

                public int Processed => _processed;
            }

            var queue = new AsyncSerialQueue();
            Task[] jobs = new Task[3];
            for (int i = 0; i < jobs.Length; i++)
            {
                jobs[i] = queue.RunAsync(async () => await Task.Delay(10));
            }

            await Task.WhenAll(jobs);
            Console.WriteLine($"Обработано: {queue.Processed}");
            """
        ),
        text(
            "Вывод: Обработано: 3. Работы выполнены строго по одной, хотя все три задачи запущены одновременно. "
            "SemaphoreSlim(1, 1) ведёт себя как асинхронный мьютекс: ожидание не занимает поток."
        ),
        heading("Асинхронность или параллелизм: как выбрать"),
        text(
            "Ключевой вопрос не «что быстрее», а «чего ждёт операция». Если программа ждёт сеть, "
            "диск, таймер или очередь сообщений — это I/O-bound работа, и правильный выбор — async/await "
            "с Task.WhenAll и Channel. Потоков при этом нужно мало, задач может быть много.\n\n"
            "Если операция считает и не ждёт внешнего мира — это CPU-bound работа. "
            "Тут помогают Parallel и PLINQ, но только если итераций достаточно много и они независимы. "
            "Запускать вычисления через Task.Run в ASP.NET-запросе почти всегда ошибка: "
            "это отнимает потоки пула у других запросов без ускорения самого запроса."
        ),
        table(
            ["Характер работы", "Инструмент", "Признак правильного выбора"],
            [
                ["Ожидание сети или диска", "async/await, Task.WhenAll", "поток освобождается на время ожидания"],
                ["Много параллельных I/O", "Task.WhenAll + SemaphoreSlim", "число одновременных операций ограничено"],
                ["Поток данных между этапами", "Channel, await foreach", "backpressure и явная остановка через Complete"],
                ["Тяжёлые вычисления", "Parallel.For/ForEach, PLINQ", "итерации независимы, ядра загружены"],
                ["Асинхронная критическая секция", "SemaphoreSlim(1, 1)", "внутри секции есть await"],
                ["Счётчик или одно поле", "Interlocked", "операция сводится к одной атомарной инструкции"],
            ],
        ),
        callout(
            "info",
            "Task.Run — не универсальное решение",
            "Task.Run переносит работу в пул потоков. Для CPU-bound кода в приложении с UI это способ "
            "разгрузить интерфейс, а для I/O-bound кода он только добавляет переключение контекста. "
            "Оборачивать HttpClient.GetAsync в Task.Run не нужно."
        ),
        heading("Отмена и таймауты"),
        text(
            "Асинхронные API принимают **CancellationToken** — структуру, через которую можно попросить операцию "
            "завершиться досрочно. Отмена кооперативна: отменяемая операция сама проверяет токен и бросает "
            "OperationCanceledException. Токен передаётся в Task.Delay, ReadAllAsync, WaitAsync и в собственные "
            "методы. Таймаут проще всего выразить через CancellationTokenSource.CancelAfter.\n\n"
            "Отмена — это не ошибка, и её не нужно логировать как сбой. В то же время не отменённые "
            "задачи после завершения родительской операции — источник утечек и фоновых исключений, "
            "которые всплывают в неожиданных местах."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Threading;
            using System.Threading.Tasks;

            public static class Program
            {
                public static async Task Main()
                {
                    using var cts = new CancellationTokenSource(TimeSpan.FromMilliseconds(150));

                    try
                    {
                        await SlowOperationAsync(cts.Token);
                        Console.WriteLine("Успели");
                    }
                    catch (OperationCanceledException)
                    {
                        Console.WriteLine("Операция отменена по таймауту");
                    }
                }

                private static async Task SlowOperationAsync(CancellationToken ct)
                {
                    for (int step = 1; step <= 10; step++)
                    {
                        await Task.Delay(50, ct);
                        Console.WriteLine($"Шаг {step}");
                    }
                }
            }
            """
        ),
        text(
            "Вывод: строки «Шаг 1» и «Шаг 2», затем «Операция отменена по таймауту». "
            "Task.Delay(50, ct) проверяет токен и бросает исключение на третьем шаге, потому что прошло около 150 миллисекунд."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                [".Result или .Wait() в асинхронном коде", "в контексте с SynchronizationContext наступает взаимная блокировка", "поднимать async вверх по стеку, использовать await"],
                ["await в цикле по одному элементу", "операции выполняются последовательно, а не одновременно", "await Task.WhenAll(items.Select(ProcessAsync))"],
                ["Двойной await над ValueTask", "неопределённое поведение", "один await или один AsTask() и работа с Task"],
                ["lock вокруг await", "Monitor привязан к потоку, после await он другой", "SemaphoreSlim.WaitAsync или AsyncLock"],
                ["Parallel.ForEach с async-лямбдой", "цикл не ждёт операций, исключения теряются", "Task.WhenAll или Channel с воркерами"],
                ["ConfigureAwait(true) в библиотеке", "библиотека захватывает контекст вызывающего кода", "ConfigureAwait(false) в библиотеках"],
                ["Release() не в finally", "после нескольких исключений семафор исчерпан", "освобождение всегда в finally"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняйте в консольном проекте .NET 8 или новее: `dotnet new console -o async-lab`, "
            "затем `dotnet run --project async-lab`. Для проверки поведения с контекстом подойдёт "
            "WinForms или WPF, но большинство выводов проверяется и в консоли."
        ),
        numbered(
            "Сравните время двух вариантов загрузки: десять вызовов `FetchAsync` в цикле с await и те же десять через `Task.WhenAll`. Выведите оба времени и объясните разницу.",
            "Реализуйте `UserCache` с `GetNameAsync`, возвращающим `ValueTask<string>`: при попадании в кэш результат выдаётся синхронно, при промахе выполняется `Task.Delay` и запись в словарь. Замерьте `GC.GetAllocatedBytesForCurrentThread()` до и после 10 000 попаданий.",
            "Постройте конвейер на Channel: производитель генерирует 100 чисел, три воркера вычисляют квадраты, отдельный агрегатор суммирует результаты. Ограничьте буфер размером 10.",
            "Напишите `AsyncRateLimiter` на `SemaphoreSlim` с ограничением 5 одновременных операций и счётчиком текущих активных задач. Убедитесь, что максимум активных за всё время не превышает 5.",
            "Сравните `Parallel.For` и последовательный `for` на массиве из 1 000 000 элементов, где каждый элемент проходит тяжёлое вычисление. Запустите BenchmarkDotNet или Stopwatch с прогревом и сформулируйте, на каком размере массива параллелизм перестаёт окупаться.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            """
            Последовательно: 1004 мс
            Параллельно: 112 мс
            Ускорение: 8.9x
            """
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "`ValueTask<T>` в структуре без аллокации хорошо работает, пока попадание в кэш — типичный случай. "
            "Но не делайте такой кэш публичным API без необходимости: потребители легко нарушат правило "
            "одного ожидания. Внутренний горячий путь — идеальное место для ValueTask."
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему await не создаёт новый поток и что происходит с текущим потоком на время ожидания?",
            "Что означает ConfigureAwait(false) и почему в библиотеках его ставят по умолчанию?",
            "В каких случаях ValueTask выгоднее Task и почему его нельзя ожидать дважды?",
            "Зачем ограниченному Channel нужен режим FullMode.Wait?",
            "Почему Parallel.ForEach не подходит для асинхронных операций?",
            "Чем SemaphoreSlim отличается от lock при работе с async-методами?",
        ),
        heading("Ответы", 3),
        numbered(
            "await проверяет, завершена ли операция; если нет, регистрирует продолжение и возвращает управление вызывающему коду. Поток освобождается и выполняет другую работу, а новый поток не создаётся.",
            "ConfigureAwait(false) разрешает продолжить выполнение в любом потоке, не возвращаясь в исходный SynchronizationContext. Библиотека не знает контекста вызывающего кода и не должна от него зависеть.",
            "ValueTask выгоден в горячих путях с частым синхронным завершением: структура не требует объекта в куче. Ожидать его нужно один раз, потому что внутри может лежать пул IValueTaskSource, который переиспользуется после завершения.",
            "FullMode.Wait заставляет WriteAsync ждать, пока в буфере освободится место. Без этого ограниченный канал отбрасывал бы элементы (DropWrite) или перезаписывал старые (DropOldest), и данные терялись бы молча.",
            "Parallel.ForEach принимает Action, поэтому async-лямбда становится async void: цикл считает её завершённой при первом await, не ждёт результата и теряет исключения. Нужен Task.WhenAll или Channel.",
            "lock основан на Monitor и привязан к потоку, который его взял; после await поток другой, и отпустить блокировку корректно не получится. SemaphoreSlim.WaitAsync освобождает поток на время ожидания и не привязан к потоку.",
        ),
        heading("Итоги"),
        bullets(
            "async-метод компилируется в машину состояний: структура хранит состояние и локальные переменные, при незавершённом await копируется в кучу.",
            "await освобождает поток, а не создаёт новый; синхронный путь при уже завершённой задаче не требует переключения потока.",
            "Синхронное ожидание через .Result и .Wait() в контексте с SynchronizationContext приводит к взаимной блокировке; асинхронность поднимается вверх по стеку.",
            "ValueTask экономит аллокации на горячих путях с синхронным завершением, но допускает только одно ожидание; для публичного API чаще подходит Task.",
            "Channel строит конвейеры producer/consumer с backpressure; несколько воркеров делят один канал без ручных блокировок.",
            "Parallel и PLINQ нужны для CPU-bound работы с независимыми итерациями; async-лямбда внутри Parallel.ForEach не ожидается.",
            "SemaphoreSlim ограничивает конкурентность и подходит для асинхронных критических секций; Interlocked — для одиночных атомарных операций; ReaderWriterLockSlim — для кэшей с преобладанием чтения.",
            "CancellationToken делает отмену кооперативной и позволяет выражать таймауты через CancelAfter.",
        ),
        heading("Что дальше"),
        text(
            "Асинхронность и конкурентность определяют, как код ведёт себя во времени, а следующий урок "
            "посвящён производительности: измерению, профилированию, аллокациям и выбору структур данных. "
            "Многие приёмы из этого урока понадобятся там напрямую: ValueTask, Span-подобные буферы "
            "и отказ от лишних блокировок — те же инструменты, что снижают нагрузку на сборщик мусора "
            "и задержки под нагрузкой."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Microsoft Learn: асинхронное программирование с async и await — learn.microsoft.com/dotnet/csharp/asynchronous-programming",
            "Stephen Toub, «Async/Await FAQ» и статьи о ConfigureAwait — devblogs.microsoft.com/pfxteam",
            "Документация System.Threading.Channels — learn.microsoft.com/dotnet/core/extensions/channels",
            "Документация по синхронизации потоков в .NET — learn.microsoft.com/dotnet/standard/threading/overview-of-synchronization-primitives",
            "Книга Riccardo Terrell, «Concurrency in .NET» — паттерны параллельной и асинхронной обработки",
        ),
    ],
}
