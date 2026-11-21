"""Урок 6 курса csharp: async/await."""

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
    "program_order": 2,
    "topic_order": 6,
    "name": "2.6. Async/Await",
    "slug": "csharp-2-6-asyncawait",
    "short_description": (
        "Модель async/await в C#: Task как обещание результата, машина состояний "
        "компилятора, отмена через CancellationToken, обработка ошибок, "
        "параллельный запуск операций и типичные ловушки вроде .Result и async void."
    ),
    "topic_name": "Async/Await",
    "topic_description": (
        "Практическое руководство по асинхронному программированию в C#: чем Task отличается "
        "от Thread, как компилятор превращает async-метод в машину состояний, зачем нужен "
        "CancellationToken, как правильно ждать несколько операций и как не получить дедлок "
        "из-за .Result. Отдельно разобраны fire-and-forget, ConfigureAwait и асинхронные потоки."
    ),
    "learning_objectives": [
        "Отличать Task и Task<T> от потока и объяснять, почему await не блокирует поток",
        "Писать async-методы с правильным возвращаемым типом и понимать машину состояний компилятора",
        "Передавать CancellationToken и отменять длительные операции с таймаутом",
        "Обрабатывать исключения из асинхронных вызовов и понимать разницу await и .Wait()",
        "Запускать несколько операций одновременно через Task.WhenAll, WhenAny и SemaphoreSlim",
        "Избегать типичных ошибок: .Result, async void без обработки, лишний Task.Run для операций ввода-вывода",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "csharp",
        "async",
        "await",
        "task",
        "cancellation",
        "конкурентность",
    ],
    "starter_code": code(
        r"""
        using System;
        using System.Threading.Tasks;

        class Program
        {
            static async Task<int> AddSlowlyAsync(int a, int b)
            {
                await Task.Delay(500); // имитация операции ввода-вывода
                return a + b;
            }

            static async Task Main()
            {
                Console.WriteLine("Запрос отправлен");
                int sum = await AddSlowlyAsync(2, 3);
                Console.WriteLine($"Результат: {sum}");
            }
        }
        """
    ),
    "hints": [
        "Если метод содержит await, он почти всегда должен возвращать Task или Task<T>, а не void. Единственное исключение — обработчик события.",
        "Никогда не вызывайте .Result или .Wait() для асинхронных операций. Это блокирует поток и может привести к дедлоку. Используйте await.",
        "Task.Delay — это таймер, он не блокирует поток. Thread.Sleep блокирует. В асинхронном коде используйте Task.Delay.",
        "Для нескольких независимых операций запускайте задачи до ожидания: сначала массив задач, потом Task.WhenAll. Так они выполняются одновременно.",
    ],
    "content": [
        text(
            "Почти любая программа обменивается данными с внешним миром: читает файлы, "
            "обращается к базе данных, вызывает сервисы по сети. Такие операции занимают "
            "время не потому, что процессор занят вычислениями, а потому что программа ждёт "
            "ответа от диска или сети. Если ждать синхронно, поток простаивает и ничего не может "
            "делать, а в десктопном приложении на всё это время замирает интерфейс.\n\n"
            "Асинхронное программирование решает эту проблему: вместо блокировки поток «ставит "
            "операцию на паузу» и говорит планировщику, что его можно использовать для другой "
            "работы. Когда результат готов, выполнение метода продолжается с того же места. "
            "В C# этот подход выражен ключевыми словами `async` и `await`, а результатом "
            "асинхронной операции выступает тип `Task`.\n\n"
            "После урока вы будете писать асинхронные методы с правильной сигнатурой, "
            "отменять операции по запросу пользователя, корректно обрабатывать исключения "
            "и объединять несколько запросов в один пакет. Вы также научитесь узнавать "
            "код, который компилируется, но ведёт себя опасно."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "отличать `Task` и `Task<T>` от потока и объяснять, почему `await` не блокирует поток;",
            "писать `async`-методы с правильным возвращаемым типом и понимать, во что их превращает компилятор;",
            "передавать `CancellationToken` и отменять длительные операции, в том числе по таймауту;",
            "обрабатывать исключения из асинхронных вызовов и понимать разницу между `await` и `.Wait()`;",
            "запускать несколько операций одновременно через `Task.WhenAll`, `Task.WhenAny` и `SemaphoreSlim`;",
            "избегать типичных ошибок: `.Result`, `async void` без обработки, лишний `Task.Run` для ввода-вывода.",
        ),
        heading("Task и Thread: чем отличаются"),
        text(
            "Поток (`Thread`) — это единица планирования операционной системы. Он получает "
            "собственный стек (обычно 1 МБ зарезервированной памяти) и работает независимо. "
            "Потоки дороги: создание и переключение между ними стоит времени, а простаивающий "
            "поток всё равно занимает память.\n\n"
            "`Task` — это объект-обещание будущего результата. Пока операция не завершена, "
            "задача находится в состоянии ожидания; когда результат появился, задача переходит "
            "в состояние `RanToCompletion` и сообщает об этом всем, кто её ожидает. Задача может "
            "описывать работу в отдельном потоке, а может просто ждать ответа от устройства — "
            "в обоих случаях наружу это выглядит одинаково.\n\n"
            "Удобные фабрики задач: `Task.Run` запускает делегат в пуле потоков, "
            "`Task.Delay` возвращает задачу, которая завершится через заданный интервал "
            "и при этом не занимает поток, `Task.FromResult` создаёт уже готовую задачу "
            "с результатом, `Task.CompletedTask` — уже готовую задачу без результата."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Threading.Tasks;

            class Program
            {
                static async Task Main()
                {
                    Task<int> вычисление = Task.Run(() => 6 * 7);   // работа в пуле потоков
                    Task пауза = Task.Delay(200);                   // таймер, поток свободен

                    Task<int> заполненная = Task.FromResult(42);    // уже завершена
                    Task пустая = Task.CompletedTask;               // уже завершена, без результата

                    Console.WriteLine($"Статус до await: {вычисление.Status}");
                    int ответ = await вычисление;
                    await пауза;

                    Console.WriteLine($"Ответ: {ответ}");
                    Console.WriteLine($"Статус после await: {вычисление.Status}");
                    Console.WriteLine($"FromResult: {await заполненная}");
                    Console.WriteLine($"CompletedTask: {пустая.Status}");
                }
            }
            """,
        ),
        text(
            "Вывод: Статус до await: WaitingToRun\n"
            "Ответ: 42\n"
            "Статус после await: RanToCompletion\n"
            "FromResult: 42\n"
            "CompletedTask: RanToCompletion"
        ),
        callout(
            "info",
            "Thread.Sleep и Task.Delay не одно и то же",
            "`Thread.Sleep(1000)` блокирует текущий поток на секунду: он ничего не делает и "
            "не может обслуживать другие задачи. `Task.Delay(1000)` подписывается на таймер "
            "и возвращает управление сразу. В асинхронном коде практически всегда нужен "
            "второй вариант.",
        ),
        heading("Синтаксис async и await"),
        text(
            "Ключевое слово `async` в сигнатуре метода не делает его автоматически фоном: "
            "оно разрешает внутри использовать `await` и включает преобразование тела метода "
            "в машину состояний. `await` перед выражением, которое возвращает задачу, "
            "приостанавливает метод до готовности результата и одновременно отдаёт поток "
            "вызывающему коду.\n\n"
            "Правила именования и типов: асинхронные методы принято завершать суффиксом `Async`, "
            "а возвращаемое значение выбирается по таблице ниже. Исключения из правил редки "
            "и требуют осознанного решения."
        ),
        table(
            ["Возвращаемый тип", "Когда использовать", "Как получить результат"],
            [
                ["`void`", "Только обработчики событий", "Нет результата, нельзя ждать"],
                ["`Task`", "Асинхронная операция без результата", "`await` без присваивания"],
                ["`Task<T>`", "Асинхронная операция с результатом типа `T`", "`T x = await ...`"],
                ["`ValueTask` / `ValueTask<T>`", "Горячий путь, где часто результат уже готов", "Так же, но ждать только один раз"],
                ["`IAsyncEnumerable<T>`", "Асинхронный поток элементов", "`await foreach`"],
            ],
        ),
        example(
            "csharp",
            """
            using System;
            using System.Net.Http;
            using System.Threading.Tasks;

            class Program
            {
                static readonly HttpClient Client = new HttpClient();

                static async Task<string> DownloadAsync(string url)
                {
                    Console.WriteLine("Начали загрузку");
                    string content = await Client.GetStringAsync(url);  // пауза, поток свободен
                    Console.WriteLine("Загрузка завершена");
                    return content.Length.ToString();
                }

                static async Task Main()
                {
                    Task<string> задача = DownloadAsync("https://example.com");
                    Console.WriteLine("Основной метод продолжает работу");
                    string длина = await задача;
                    Console.WriteLine($"Длина содержимого: {длина}");
                }
            }
            """,
        ),
        text(
            "Вывод (порядок строк стабилен):\n"
            "Начали загрузку\n"
            "Основной метод продолжает работу\n"
            "Загрузка завершена\n"
            "Длина содержимого: 528\n\n"
            "Строка «Загрузка завершена» появляется только после ответа сервера, "
            "а «Основной метод продолжает работу» — сразу после вызова, потому что "
            "метод приостановился на `await` и вернул управление."
        ),
        heading("Машина состояний: что генерирует компилятор"),
        text(
            "`async`/`await` — синтаксический сахар. Компилятор превращает тело метода в класс "
            "с именем вроде `<DownloadAsync>d__2`, который реализует интерфейс "
            "`IAsyncStateMachine`. В этом классе хранятся локальные переменные, параметры "
            "и номер шага, на котором метод остановился.\n\n"
            "Каждый `await` становится точкой выхода: метод проверяет, завершена ли задача; "
            "если нет, регистрирует продолжение и возвращает `Task` вызывающему. Когда задача "
            "завершается, продолжение вызывается снова, номер шага извлекается из состояния, "
            "и выполнение переходит на нужный `switch`-case.\n\n"
            "Практическое следствие: первая часть `async`-метода выполняется синхронно в момент "
            "вызова, до первого `await`. Если ожидаемая задача уже завершена, машина "
            "состояний часто продолжает работу без приостановки."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Threading.Tasks;

            class Program
            {
                static async Task<string> StepAsync()
                {
                    Console.WriteLine("Шаг 1: до первого await");
                    await Task.Delay(100);
                    Console.WriteLine("Шаг 2: после await");
                    return "готово";
                }

                static async Task Main()
                {
                    Task<string> задача = StepAsync();
                    Console.WriteLine("Метод уже вернул Task, ожидание впереди");
                    Console.WriteLine(await задача);
                }
            }
            """,
        ),
        text(
            "Вывод: Шаг 1: до первого await\n"
            "Метод уже вернул Task, ожидание впереди\n"
            "Шаг 2: после await\n"
            "готово"
        ),
        callout(
            "warning",
            "Синхронная часть тоже выполняется",
            "До первого `await` код метода идёт синхронно в потоке вызывающего. Тяжёлые "
            "вычисления в начале `async`-метода заблокируют вызывающего, даже если дальше "
            "стоит `await`. Если нужна гарантированная фоновая работа, оберните такое "
            "вычисление в `Task.Run` и сразу вернитесь.",
        ),
        heading("Отмена: CancellationToken и CancellationTokenSource"),
        text(
            "Отмена в .NET кооперативная: токен не убивает операцию принудительно, "
            "а служит сигналом «результат больше не нужен». Операция сама решает, когда "
            "проверить флаг и остановиться. `CancellationTokenSource` создаёт токен и умеет "
            "его отменять; `CancellationToken` — это структура, которую передают внутрь. "
            "Пара связана односторонне: через токен нельзя отменить, только узнать об отмене.\n\n"
            "Стандартный приём внутри цикла — `token.ThrowIfCancellationRequested()`. "
            "Если отмена запрошена, метод бросает `OperationCanceledException`, и это "
            "правильное завершение, а не авария. Снаружи его ловят отдельно от прочих ошибок."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Threading;
            using System.Threading.Tasks;

            class Program
            {
                static async Task ProcessAsync(int steps, CancellationToken ct)
                {
                    for (int i = 1; i <= steps; i++)
                    {
                        ct.ThrowIfCancellationRequested();
                        await Task.Delay(100, ct);       // Delay тоже умеет отменяться
                        Console.WriteLine($"Элемент {i} обработан");
                    }
                }

                static async Task Main()
                {
                    using var cts = new CancellationTokenSource();
                    Task работа = ProcessAsync(10, cts.Token);

                    await Task.Delay(250);               // имитация работы пользователя
                    cts.Cancel();                        // запрос отмены

                    try
                    {
                        await работа;
                    }
                    catch (OperationCanceledException)
                    {
                        Console.WriteLine("Операция отменена");
                    }
                }
            }
            """,
        ),
        text(
            "Вывод (число обработанных элементов зависит от планировщика):\n"
            "Элемент 1 обработан\n"
            "Элемент 2 обработан\n"
            "Операция отменена"
        ),
        heading("Таймаут и связывание токенов", 3),
        text(
            "Таймаут — частный случай отмены: `new CancellationTokenSource(TimeSpan)` "
            "отменяет токен автоматически через заданное время, без отдельного потока.\n\n"
            "Когда у операции есть внешний токен (например, отменённый HTTP-запросом "
            "клиентом) и собственный таймаут, их объединяют через "
            "`CancellationTokenSource.CreateLinkedTokenSource`: результирующий токен "
            "сработает при отмене любого из исходных. Созданный источник нужно освобождать "
            "через `using`, иначе подписка на родительские токены останется в памяти."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Threading;
            using System.Threading.Tasks;

            class Program
            {
                static async Task WorkAsync(CancellationToken outer)
                {
                    using var timeout = new CancellationTokenSource(TimeSpan.FromMilliseconds(300));
                    using var linked = CancellationTokenSource.CreateLinkedTokenSource(outer, timeout.Token);

                    try
                    {
                        await Task.Delay(5000, linked.Token);
                        Console.WriteLine("Успели вовремя");
                    }
                    catch (OperationCanceledException) when (timeout.IsCancellationRequested)
                    {
                        Console.WriteLine("Сработал таймаут");
                    }
                    catch (OperationCanceledException)
                    {
                        Console.WriteLine("Отмена извне");
                    }
                }

                static async Task Main()
                {
                    await WorkAsync(CancellationToken.None);
                    Console.WriteLine($"Ожидали 5000 мс, фактически сработал таймаут 300 мс");
                }
            }
            """,
        ),
        text("Вывод: Сработал таймаут\nОжидали 5000 мс, фактически сработал таймаут 300 мс"),
        callout(
            "success",
            "Фильтр исключений различает причину отмены",
            "`when (timeout.IsCancellationRequested)` в `catch` позволяет отличить собственный "
            "таймаут от внешней отмены. Если свойство истинно — сработал таймер, иначе "
            "отменил вызывающий код. ",
        ),
        heading("Обработка ошибок"),
        text(
            "Асинхронные методы сообщают об ошибках так же, как синхронные: через исключения. "
            "`await` «разворачивает» задачу и пробрасывает сохранённое исключение в текущий "
            "метод, поэтому `try/catch` вокруг `await` работает привычным образом, "
            "а стек-трейс сохраняется.\n\n"
            "Ключевое отличие от `.Wait()` и `.Result`: эти методы бросают `AggregateException`, "
            "внутри которого лежит исходное исключение. `await` же возвращает первое исключение "
            "как есть. Поэтому в асинхронном коде `catch (Exception ex)` поймает ровно тот тип, "
            "который был брошен внутри задачи."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Threading.Tasks;

            class Program
            {
                static async Task<int> DivideAsync(int a, int b)
                {
                    await Task.Delay(50);
                    if (b == 0)
                        throw new DivideByZeroException($"Делитель равен нулю: {a}/{b}");
                    return a / b;
                }

                static async Task Main()
                {
                    try
                    {
                        int результат = await DivideAsync(10, 0);
                        Console.WriteLine(результат);
                    }
                    catch (DivideByZeroException ex)
                    {
                        Console.WriteLine($"Поймали через await: {ex.Message}");
                    }

                    Task<int> задача = DivideAsync(10, 0);
                    try
                    {
                        задача.Wait();
                    }
                    catch (AggregateException ex)
                    {
                        Console.WriteLine($"Через Wait: {ex.GetType().Name}");
                        Console.WriteLine($"Внутри: {ex.InnerException!.GetType().Name}");
                    }
                }
            }
            """,
        ),
        text(
            "Вывод: Поймали через await: Делитель равен нулю: 10/0\n"
            "Через Wait: AggregateException\n"
            "Внутри: DivideByZeroException"
        ),
        heading("Несколько операций сразу: WhenAll и WhenAny"),
        text(
            "Последовательное ожидание в цикле — частая причина медленной работы. Если "
            "сто запросов выполняются по одному и каждый занимает 100 мс, программа потратит "
            "секунды, хотя операции независимы. Решение: сначала запустить все задачи "
            "(вызов `async`-метода запускает его до первого `await`), затем дождаться их "
            "всех одновременно.\n\n"
            "`Task.WhenAll` возвращает задачу, которая завершится, когда завершатся все "
            "переданные. Если хотя бы одна упала с исключением, `await` бросит первое, "
            "но остальные ошибки доступны через свойство `Task.Exception`. "
            "`Task.WhenAny` возвращает задачу, которая завершится, как только завершится "
            "первая из переданных, — на нём строят таймауты и гонки."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Diagnostics;
            using System.Linq;
            using System.Threading.Tasks;

            class Program
            {
                static async Task<int> FetchAsync(int id)
                {
                    await Task.Delay(300);
                    return id * 10;
                }

                static async Task Main()
                {
                    var sw = Stopwatch.StartNew();

                    Task<int>[] задачи = Enumerable.Range(1, 5)
                        .Select(FetchAsync)
                        .ToArray();

                    int[] результаты = await Task.WhenAll(задачи);
                    Console.WriteLine($"Результаты: {string.Join(", ", результаты)}");
                    Console.WriteLine($"Прошло ~{sw.ElapsedMilliseconds / 100}00 мс");

                    Task<int> первая = await Task.WhenAny(задачи);
                    Console.WriteLine($"WhenAny вернул: {await первая}");
                }
            }
            """,
        ),
        text(
            "Вывод: Результаты: 10, 20, 30, 40, 50\n"
            "Прошло ~300 мс\n"
            "WhenAny вернул: 10\n\n"
            "Пять операций по 300 мс выполнились примерно за 300 мс, а не за 1500. "
            "`WhenAny` при одинаковой длительности вернёт ту, что завершилась первой."
        ),
        heading("Ограничение параллелизма: SemaphoreSlim"),
        text(
            "Запустить тысячу задач разом опасно: они захватят пул потоков и сокеты, "
            "а внешний сервис может ограничить частоту запросов. `SemaphoreSlim` — "
            "счётчик разрешений: перед работой задача занимает разрешение, после — "
            "возвращает его в блоке `finally`. Если разрешений нет, `WaitAsync` "
            "ждёт асинхронно, не занимая поток.\n\n"
            "Типичный шаблон — метод-обёртка, который принимает список элементов "
            "и функцию их обработки, а внутри пропускает через семафор не более N "
            "одновременных вызовов."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;
            using System.Linq;
            using System.Threading;
            using System.Threading.Tasks;

            class Program
            {
                static async Task<int> RunWithLimitAsync(
                    IReadOnlyList<int> items,
                    int maxDegree,
                    Func<int, Task<int>> work)
                {
                    using var gate = new SemaphoreSlim(maxDegree);

                    Task<int>[] tasks = items.Select(async item =>
                    {
                        await gate.WaitAsync();
                        try
                        {
                            return await work(item);
                        }
                        finally
                        {
                            gate.Release();
                        }
                    }).ToArray();

                    return (await Task.WhenAll(tasks)).Sum();
                }

                static async Task<int> Main()
                {
                    int[] data = Enumerable.Range(1, 6).ToArray();
                    Task<int> работа(int x) => Task.FromResult(x * x);
                    int сумма = await RunWithLimitAsync(data, 2, работа);
                    Console.WriteLine($"Сумма квадратов: {сумма}");
                    return 0;
                }
            }
            """,
        ),
        text("Вывод: Сумма квадратов: 91"),
        callout(
            "warning",
            "Release обязательно в finally",
            "Если между `WaitAsync` и `Release` случится исключение, разрешение "
            "не вернётся, и семафор со временем заблокирует все задачи навсегда. "
            "Всегда освобождайте разрешение в `finally`, даже если метод простой.",
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["`.Result` или `.Wait()` на задаче", "Поток блокируется, в контексте с синхронизацией — дедлок", "Использовать `await` и сделать метод `async`"],
                ["`async void` вне обработчика события", "Исключение не поймать, задачу нельзя дождаться", "Возвращать `Task` или `Task<T>`"],
                ["Fire-and-forget без `try/catch`", "Исключение теряется, сбой не виден в логах", "Обернуть тело в `try/catch` с логированием"],
                ["`Task.Run` вокруг сетевого вызова", "Лишний поток для операции, которая и так не блокирует", "`await` метода напрямую"],
                ["Забыли передать `CancellationToken`", "Операцию нельзя остановить, ресурсы тратятся зря", "Принимать токен и передавать его в каждый вызов"],
                ["Повторный `await` одного `ValueTask`", "Неопределённое поведение или ошибка", "Ждать `ValueTask` ровно один раз или вызвать `AsTask()`"],
            ],
        ),
        heading("Дедлоки и захват контекста", 3),
        text(
            "В старых приложениях WPF, WinForms и ASP.NET (.NET Framework) у потока есть "
            "`SynchronizationContext`, который отвечает за возврат продолжений в нужный поток: "
            "например, чтобы код после `await` мог обращаться к элементам интерфейса. Если "
            "вызывающий поток заблокирован на `.Result`, продолжение ждёт освобождения этого "
            "потока, а поток ждёт продолжения — наступает взаимная блокировка.\n\n"
            "`ConfigureAwait(false)` говорит, что возвращаться в исходный контекст не нужно. "
            "Это используют в библиотеках, чтобы продолжение могло выполниться в любом потоке "
            "пула. В UI-обработчиках этот вызов не нужен, а в ASP.NET Core собственного "
            "контекста синхронизации нет, поэтому там он на поведение не влияет."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Net.Http;
            using System.Threading.Tasks;

            class Downloader
            {
                private readonly HttpClient _client = new HttpClient();

                // Библиотечный код: не зависим от контекста вызывающего
                public async Task<string> GetTextAsync(string url)
                {
                    string json = await _client.GetStringAsync(url).ConfigureAwait(false);
                    return json.Trim();
                }

                // Показываем, что после .Result продолжение могло бы требовать UI-поток
                public string GetTextBad(string url)
                {
                    return GetTextAsync(url).Result;   // блокирует поток и рискует дедлоком
                }

                public async Task<string> GetTextGoodAsync(string url)
                {
                    return await GetTextAsync(url);   // ожидание без блокировки
                }
            }

            class Program
            {
                static async Task Main()
                {
                    var downloader = new Downloader();
                    Console.WriteLine("Метод .Result оставлен как пример антипаттерна, не вызываем его");
                    string текст = await downloader.GetTextGoodAsync("https://example.com");
                    Console.WriteLine($"Длина ответа: {текст.Length}");
                }
            }
            """,
        ),
        text("Вывод: Метод .Result оставлен как пример антипаттерна, не вызываем его\nДлина ответа: 528"),
        callout(
            "danger",
            "Дедлок диагностируется сложно",
            "Симптом: программа зависает и не реагирует, процессор почти не загружен. "
            "Ищите `.Result`, `.Wait()`, `GetAwaiter().GetResult()` в цепочке вызовов до "
            "`await`. Задача при этом уже выполнена, но продолжение ждёт поток, который "
            "никогда не освободится.",
        ),
        heading("Fire-and-forget: фоновые задачи"),
        text(
            "Иногда результат операции действительно не нужен: отправить телеметрию, "
            "прогреть кэш, записать журнал. Такой запуск («выстрелил и забыл» — "
            "fire-and-forget) допустим, но исключение из него не увидит никто, если "
            "не обработать его внутри.\n\n"
            "Правило: скрытая задача обязана сама обработать свои ошибки. Присваивание "
            "результата в `_` информирует компилятор, что задача намеренно не ожидается."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Threading.Tasks;

            class Program
            {
                static async Task WorkAsync(string name)
                {
                    await Task.Delay(100);
                    if (name == "сбой")
                        throw new InvalidOperationException("Фоновая операция упала");
                    Console.WriteLine($"Фоновая задача {name} завершена");
                }

                static void FireAndForget(string name)
                {
                    _ = Task.Run(async () =>
                    {
                        try
                        {
                            await WorkAsync(name);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"[лог] {name}: {ex.GetType().Name}: {ex.Message}");
                        }
                    });
                }

                static async Task Main()
                {
                    FireAndForget("отправка");
                    FireAndForget("сбой");
                    await Task.Delay(400);
                    Console.WriteLine("Главный метод завершён");
                }
            }
            """,
        ),
        text(
            "Вывод: Фоновая задача отправка завершена\n"
            "[лог] сбой: InvalidOperationException: Фоновая операция упала\n"
            "Главный метод завершён"
        ),
        heading("Асинхронные потоки и IAsyncDisposable", 3),
        text(
            "`IAsyncEnumerable<T>` — интерфейс асинхронной последовательности. Он решает "
            "проблему, когда элементы приходят по мере готовности: читать файл построчно, "
            "получать страницы из базы, слушать сообщения. Обработка идёт через "
            "`await foreach`, а параметр с атрибутом `[EnumeratorCancellation]` позволяет "
            "передавать токен напрямую в цикл: `await foreach (var x in Source(ct))`.\n\n"
            "Для ресурсов, у которых освобождение занимает время, есть `IAsyncDisposable` "
            "и `await using`. Классические примеры — сетевые соединения и клиенты БД."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;
            using System.Runtime.CompilerServices;
            using System.Threading;
            using System.Threading.Tasks;

            class Program
            {
                static async IAsyncEnumerable<int> CountdownAsync(
                    int from,
                    [EnumeratorCancellation] CancellationToken ct = default)
                {
                    for (int i = from; i > 0; i--)
                    {
                        ct.ThrowIfCancellationRequested();
                        await Task.Delay(50, ct);
                        yield return i;
                    }
                }

                static async Task Main()
                {
                    using var cts = new CancellationTokenSource(250);
                    try
                    {
                        await foreach (int число in CountdownAsync(10, cts.Token))
                        {
                            Console.WriteLine(число);
                        }
                    }
                    catch (OperationCanceledException)
                    {
                        Console.WriteLine("Поток остановлен по таймауту");
                    }
                }
            }
            """,
        ),
        text(
            "Вывод (может быть на один элемент больше или меньше из-за планировщика):\n"
            "10\n11\n...\n"
            "Поток остановлен по таймауту"
        ),
        heading("ValueTask: когда он уместен"),
        text(
            "Каждое создание `Task<T>` — это аллокация в куче. Если результат часто уже "
            "известен (данные в кэше, буфер полон), такую аллокацию можно избежать. "
            "`ValueTask<T>` — структура, которая либо содержит готовое значение, либо "
            "оборачивает `Task<T>`.\n\n"
            "Взамен появляются строгие ограничения: `ValueTask` нельзя ждать дважды, "
            "нельзя сохранять для последующего ожидания и нельзя ждать параллельно из "
            "нескольких потоков. По умолчанию для публичных `async`-методов выбирают "
            "`Task`; `ValueTask` оставляют для горячих путей после измерений."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;
            using System.Threading.Tasks;

            class Resolver
            {
                private readonly Dictionary<int, int> _cache = new() { [1] = 100 };
                private int _запросов;

                public ValueTask<int> GetAsync(int key)
                {
                    if (_cache.TryGetValue(key, out int готовое))
                        return new ValueTask<int>(готовое);          // без аллокации

                    return new ValueTask<int>(ComputeAsync(key));      // настоящий async
                }

                private async Task<int> ComputeAsync(int key)
                {
                    _запросов++;
                    await Task.Delay(50);
                    return key * 2;
                }

                public int Запросов => _запросов;
            }

            class Program
            {
                static async Task Main()
                {
                    var resolver = new Resolver();
                    Console.WriteLine($"Из кэша: {await resolver.GetAsync(1)}");
                    Console.WriteLine($"Вычислено: {await resolver.GetAsync(7)}");
                    Console.WriteLine($"Обращений к вычислению: {resolver.Запросов}");
                }
            }
            """,
        ),
        text("Вывод: Из кэша: 100\nВычислено: 14\nОбращений к вычислению: 1"),
        heading("Практика"),
        text(
            "Выполните задания в консольном проекте `dotnet new console`, "
            "запуская `dotnet run` после каждого изменения. Для заданий с сетью "
            "можно использовать `https://example.com` или собственную заглушку "
            "через `Task.Delay`."
        ),
        numbered(
            "Замер: напишите два метода, которые последовательно и параллельно вызывают `FetchAsync(id)` пять раз по 300 мс. Выведите время обоих вариантов и сравните.",
            "Отмена: реализуйте `ProcessAsync(int steps, CancellationToken ct)`, который обрабатывает шаги по 100 мс и останавливается по отмене, при этом снаружи ловится только `OperationCanceledException`.",
            "Таймаут: напишите обёртку `WithTimeoutAsync<T>(Func<CancellationToken, Task<T>> operation, TimeSpan timeout)`, которая отменяет операцию и бросает `TimeoutException`, если та не уложилась во время.",
            "Ограничение: обработайте список из 20 элементов с внешней функцией, занимающей 200 мс, пропуская не более 3 вызовов одновременно. Выведите общее время и сумму результатов.",
            "Fire-and-forget: сделайте безопасный запуск фоновой задачи, которая иногда бросает исключение. Убедитесь, что исключение попадает в `Console` с типом и сообщением, а основной метод не падает.",
        ),
        text(
            "Ожидаемый результат для второго задания при отмене через 250 мс:"
        ),
        example(
            "text",
            """
            Шаг 1 обработан
            Шаг 2 обработан
            Операция отменена
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 3",
            "Создайте `using var cts = new CancellationTokenSource(timeout)`, передайте токен "
            "в операцию и дождитесь её в `try/catch (OperationCanceledException when (cts.IsCancellationRequested))`. "
            "Там бросьте `TimeoutException` с исходным исключением внутри.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему `await Task.Delay(1000)` не блокирует поток, а `Thread.Sleep(1000)` блокирует?",
            "Что возвращает `async`-метод и почему нельзя делать его `async void` произвольно?",
            "Какая разница между перехватом исключения через `await` и через `.Wait()`?",
            "Зачем передавать `CancellationToken` в каждый асинхронный вызов внутри операции?",
            "Когда `Task.WhenAll` эффективнее последовательных `await`, а когда нет?",
        ),
        heading("Ответы", 3),
        numbered(
            "`Task.Delay` подписывается на таймер и сразу возвращает задачу, освобождая поток; `Thread.Sleep` останавливает поток ОС, и он не может выполнять другую работу.",
            "`Task` или `Task<T>`, чтобы вызывающий мог дождаться результата и исключения. `async void` не даёт задачу: исключения уходят в контекст синхронизации, и ожидать завершение нельзя.",
            "`await` пробрасывает исходное исключение напрямую; `.Wait()` и `.Result` бросают `AggregateException`, внутри которого лежит первое.",
            "Отмена кооперативная: токен нужно явно передать внутрь, иначе внутренняя операция про отмену не узнает и продолжит тратить ресурсы.",
            "`WhenAll` полезен для независимых операций ввода-вывода: они выполняются одновременно. Для последовательных по смыслу шагов или CPU-bound работы без реального ожидания выигрыша нет.",
        ),
        heading("Итоги"),
        bullets(
            "`Task` — обещание результата, а не поток: `await` приостанавливает метод и освобождает поток.",
            "`async` разрешает `await` и включает машину состояний; возвращаемый тип почти всегда `Task` или `Task<T>`.",
            "Код до первого `await` идёт синхронно в потоке вызывающего.",
            "Отмена кооперативная: `CancellationTokenSource` создаёт токен, операция проверяет его и бросает `OperationCanceledException`.",
            "Исключения в асинхронном коде ловятся `try/catch` вокруг `await`; `.Wait()` и `.Result` дают `AggregateException`.",
            "`Task.WhenAll` и `Task.WhenAny` позволяют запускать несколько операций сразу, `SemaphoreSlim` ограничивает их число.",
            "Скрытые задачи должны сами обрабатывать исключения.",
        ),
        heading("Что дальше"),
        text(
            "Следующий урок — «Внутреннее устройство .NET»: вы увидите, как Common Language "
            "Runtime загружает сборки, как работает сборка мусора, чем управляемая память "
            "отличается от неуправляемой и куда именно передаётся управление при `await`. "
            "Понимание среды выполнения помогает принимать решения о типах, производительности "
            "и границах между кодом приложения и системными вызовами."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Асинхронное программирование в C#: learn.microsoft.com/dotnet/csharp/asynchronous-programming",
            "Task-based Asynchronous Pattern (TAP): learn.microsoft.com/dotnet/standard/asynchronous-programming-patterns/task-based-asynchronous-pattern-tap",
            "CancellationToken: learn.microsoft.com/dotnet/api/system.threading.cancellationtoken",
            "Блог Стивена Клири о связанных с async темах: blog.stephencleary.com",
        ),
    ],
}
