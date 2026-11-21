"""Урок 2.10 курса C#: разработка приложений."""

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
    "topic_order": 10,
    "name": "2.10. Разработка приложений",
    "slug": "csharp-2-10-разработка-приложений",
    "short_description": (
        "Как собрать веб-приложение на ASP.NET Core: конфигурация и секреты, паттерн Options, "
        "структурированное логирование, внедрение зависимостей, Minimal APIs, контроллеры, "
        "конвейер middleware и проверки работоспособности."
    ),
    "topic_name": "Разработка приложений",
    "topic_description": (
        "Практические основы построения приложения на ASP.NET Core: источники конфигурации и порядок "
        "их приоритета, строго типизированные настройки, логирование через ILogger и Serilog, "
        "времена жизни сервисов в контейнере зависимостей, Minimal APIs и контроллеры, порядок "
        "middleware в конвейере обработки запросов и проверки работоспособности."
    ),
    "learning_objectives": [
        "Настраивать конфигурацию приложения из файлов JSON, переменных окружения, секретов пользователя и аргументов командной строки, понимая приоритет источников",
        "Описывать строго типизированные настройки в паттерне Options с IOptions, IOptionsSnapshot и IOptionsMonitor и валидировать их при старте",
        "Писать структурированные записи журнала через ILogger с именованными параметрами, областями видимости и настройкой фильтров",
        "Регистрировать сервисы в контейнере зависимостей с подходящими временами жизни и создавать область вручную через IServiceScopeFactory",
        "Создавать конечные точки на Minimal APIs с привязкой параметров, кодами ответов и группировкой маршрутов",
        "Объяснять порядок middleware в конвейере запроса и писать собственное middleware с измерением времени обработки",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "csharp",
        "aspnet-core",
        "configuration",
        "dependency injection",
        "logging",
        "minimal api",
        "middleware",
    ],
    "starter_code": code(
        """
        // Настройки приложения в виде словаря — модель источника конфигурации.
        var defaultSettings = new Dictionary<string, string?>
        {
            ["Database:Host"] = "localhost",
            ["Database:Port"] = "5432",
            ["Logging:Level"] = "Information",
        };

        var environmentVariables = new Dictionary<string, string?>
        {
            ["Database:Port"] = "6543",
        };

        // Поздние источники переопределяют ранние.
        var configuration = new Dictionary<string, string?>(defaultSettings);
        foreach (var pair in environmentVariables)
        {
            configuration[pair.Key] = pair.Value;
        }

        Console.WriteLine($"Host: {configuration["Database:Host"]}");
        Console.WriteLine($"Port: {configuration["Database:Port"]}");
        Console.WriteLine($"Size: {configuration.Count}");
        """
    ),
    "hints": [
        "Двоеточие в ключе (Database:Host) соответствует вложенности в JSON: { \"Database\": { \"Host\": ... } }.",
        "Поздние источники конфигурации переопределяют ранние, поэтому аргументы командной строки имеют наибольший вес.",
        "Сервис с временем жизни Scoped нельзя внедрять в Singleton напрямую — используйте IServiceScopeFactory.",
        "Порядок регистрации middleware определяет порядок обработки: обработка исключений ставится первой, конечные точки — последними.",
    ],
    "content": [
        text(
            "До этого момента программы в курсе работали в памяти одного процесса: считали, записывали "
            "файлы и выводили результат в консоль. Настоящее приложение на C# живёт дольше и "
            "обслуживает нескольких пользователей одновременно, поэтому ему нужны внешние настройки, "
            "журнал событий, разделение ответственности между классами и способ принимать запросы по "
            "сети. Все эти задачи решает ASP.NET Core — веб-платформа на базе .NET.\n\n"
            "Приложение на ASP.NET Core строится вокруг небольшого набора механизмов: конфигурация "
            "хранит настройки, которые меняются между средами без пересборки; журналирование фиксирует "
            "ход работы; контейнер зависимостей связывает интерфейсы с реализациями; конвейер "
            "middleware обрабатывает каждый запрос по цепочке. Эти механизмы одинаковы и для "
            "веб-сервиса, и для фоновой службы.\n\n"
            "Урок опирается на пройденные темы: интерфейсы, асинхронные методы, тестируемость и "
            "доступ к данным. Мы соберём небольшой сервис для учёта заказов и разберём, почему "
            "настройки не хранят в коде, чем Transient отличается от Scoped и зачем нужен порядок "
            "middleware."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "настраивать конфигурацию из файлов JSON, переменных окружения, секретов пользователя и аргументов командной строки и объяснять приоритет источников;",
            "описывать настройки строго типизированным классом и подключать его через паттерн Options с валидацией при старте;",
            "писать структурированные записи журнала через ILogger, использовать области видимости и фильтры уровней;",
            "регистрировать сервисы с временами жизни Transient, Scoped и Singleton и создавать область вручную;",
            "создавать конечные точки Minimal APIs с привязкой параметров, кодами ответов и группировкой маршрутов;",
            "объяснять порядок middleware в конвейере и писать собственное middleware замера времени.",
        ),
        heading("Как устроено приложение ASP.NET Core"),
        text(
            "Любое приложение на ASP.NET Core начинается с двух объектов: построителя "
            "(WebApplicationBuilder) и приложения (WebApplication). Построитель собирает всё, что нужно "
            "до первого запроса: читает конфигурацию, настраивает журналы, регистрирует сервисы и "
            "параметры веб-сервера. Метод Build() превращает накопленные настройки в готовое "
            "приложение. После этого описывают конвейер обработки запросов и вызывают Run().\n\n"
            "Слово «сервис» здесь ключевое. Сервисом называется любой класс, который выполняет работу "
            "для приложения: отправляет почту, читает заказы из базы, форматирует ответы. Приложение не "
            "создаёт такие классы через new, а запрашивает их у контейнера зависимостей — хранилища "
            "фабрик объектов. Такой подход называется внедрением зависимостей (dependency injection, DI)."
        ),
        example(
            "csharp",
            """
            // Program.cs — минимальное приложение с одной конечной точкой
            var builder = WebApplication.CreateBuilder(args);

            builder.Services.AddSingleton<IClock, SystemClock>();

            var app = builder.Build();

            app.MapGet("/", (IClock clock) => $"Серверное время: {clock.Now:HH:mm:ss}");

            app.Run();
            """
        ),
        text(
            "Разберём строки. WebApplication.CreateBuilder(args) создаёт построитель с конфигурацией и "
            "журналированием по умолчанию. Свойство builder.Services — коллекция регистраций "
            "контейнера. Метод Build() применяет регистрации и собирает приложение. Метод MapGet "
            "связывает маршрут \"/\" с функцией-обработчиком, и параметр IClock автоматически получает "
            "экземпляр зарегистрированного сервиса. Метод Run() запускает веб-сервер и обрабатывает "
            "запросы до остановки процесса."
        ),
        example(
            "text",
            "Вывод: Серверное время: 14:07:52"
        ),
        table(
            ["Элемент", "Роль", "Когда настраивается"],
            [
                ["WebApplicationBuilder", "Сборка конфигурации, журналов и сервисов", "До вызова Build()"],
                ["builder.Services", "Правила создания сервисов и их время жизни", "До вызова Build()"],
                ["WebApplication", "Обработка запросов и жизненный цикл", "После вызова Build()"],
                ["Конвейер middleware", "Последовательная обработка каждого запроса", "После Build(), до Run()"],
                ["Конечная точка", "Функция или действие для конкретного маршрута", "После Build(), до Run()"],
            ],
        ),
        callout(
            "info",
            "Среда выполнения",
            "Среда (environment) — именованный набор условий запуска. По умолчанию это Development при "
            "запуске через dotnet run, но Production при публикации. Имя среды хранится в переменной "
            "окружения ASPNETCORE_ENVIRONMENT и влияет на то, какой файл настроек загружается и какие "
            "диагностические средства включены.",
        ),
        heading("Конфигурация и её источники"),
        text(
            "Конфигурация — это дерево пар «ключ — значение», где ключи записываются через двоеточие: "
            "Database:Host, Database:Port. Такая запись соответствует вложенности в JSON-файле. "
            "Значения остаются строками, а приведение к числу или логическому типу выполняет читатель.\n\n"
            "Главное правило: источники подключаются по порядку, и каждый следующий слой перекрывает "
            "предыдущий для совпавших ключей. Порядок по умолчанию: appsettings.json, затем "
            "appsettings.{Среда}.json, затем секреты пользователя в Development, затем переменные "
            "окружения и в конце аргументы командной строки. Поэтому одна и та же сборка работает с "
            "разными базами данных: на сервере переменная окружения подменит значение из файла."
        ),
        example(
            "json",
            """
            // appsettings.json — общие настройки для всех сред
            {
              "Database": {
                "Host": "localhost",
                "Port": 5432,
                "MaxRetryCount": 3
              },
              "Orders": {
                "PageSize": 20
              }
            }
            """
        ),
        text(
            "Файл appsettings.Development.json содержит только отличающиеся значения, например адрес "
            "локальной базы. Дублировать всю структуру не нужно: слои накладываются друг на друга. "
            "Отсутствующий во всех источниках ключ через индексатор даёт null, а метод расширения "
            "GetValue с параметром по умолчанию возвращает заданное значение."
        ),
        example(
            "csharp",
            """
            var builder = WebApplication.CreateBuilder(args);

            // Чтение отдельных значений: вложенные ключи записываются через двоеточие
            var host = builder.Configuration["Database:Host"] ?? "не задан";
            int port = builder.Configuration.GetValue<int>("Database:Port", 5432);
            int pageSize = builder.Configuration.GetValue("Orders:PageSize", 10);

            Console.WriteLine($"Хост: {host}");
            Console.WriteLine($"Порт: {port}");
            Console.WriteLine($"Размер страницы: {pageSize}");

            var app = builder.Build();
            app.Run();
            """
        ),
        example(
            "text",
            "Вывод: Хост: localhost\nВывод: Порт: 5432\nВывод: Размер страницы: 20"
        ),
        text(
            "Кастомный источник подключается методом расширения на builder.Configuration. Например, "
            "AddJsonFile добавляет ещё один JSON-файл, а AddInMemoryCollection — набор значений, "
            "удобный в тестах. Параметр reloadOnChange заставляет перечитывать файл при изменении, "
            "а optional разрешает его отсутствие. Все методы возвращают тот же объект, поэтому "
            "вызовы объединяются в цепочку."
        ),
        example(
            "csharp",
            """
            var builder = WebApplication.CreateBuilder(args);

            builder.Configuration
                .AddJsonFile("custom.json", optional: true, reloadOnChange: true)
                .AddInMemoryCollection(new Dictionary<string, string?>
                {
                    ["FeatureFlags:NewCheckout"] = "true",
                });

            bool newCheckout = builder.Configuration.GetValue<bool>("FeatureFlags:NewCheckout");
            Console.WriteLine($"Новая касса включена: {newCheckout}");

            var app = builder.Build();
            app.Run();
            """
        ),
        example(
            "text",
            "Вывод: Новая касса включена: True"
        ),
        callout(
            "warning",
            "Пароли не место в репозитории",
            "Пароли и ключи не записывают в appsettings.json: файл попадает в систему контроля версий "
            "и в историю изменений. В Development их хранят в секретах пользователя командой "
            "dotnet user-secrets, а в рабочей среде передают через переменные окружения или облачное "
            "хранилище секретов.",
        ),
        heading("Секреты пользователя и паттерн Options"),
        text(
            "Секреты пользователя (user secrets) — механизм для локальной разработки. Команда "
            "dotnet user-secrets init добавляет в файл проекта идентификатор, а команда "
            "dotnet user-secrets set записывает пару «ключ — значение» в файл профиля пользователя. "
            "Настройки загружаются только в Development, но с тем же синтаксисом ключей через двоеточие."
        ),
        example(
            "bash",
            """
            dotnet user-secrets init
            dotnet user-secrets set "Database:Password" "СекретнаяСтрока123"
            dotnet user-secrets list
            """
        ),
        text(
            "Читать конфигурацию через индексаторы по всему коду неудобно: имена ключей превращаются в "
            "строковые литералы, ошибки обнаруживаются при выполнении. Паттерн Options решает это через "
            "обычный класс настроек со свойствами и значениями по умолчанию.\n\n"
            "Класс регистрируется методом Configure с указанием раздела. Цепочка AddOptions с методами "
            "Bind, ValidateDataAnnotations и ValidateOnStart добавляет атрибуты проверки и проверку "
            "при запуске. Проверка при старте (fail fast) не даёт приложению запуститься с пустой "
            "строкой подключения — это лучше, чем падение на первом запросе."
        ),
        example(
            "csharp",
            """
            using System.ComponentModel.DataAnnotations;

            // Класс настроек: обычные свойства с атрибутами проверки
            public class DatabaseOptions
            {
                [Required]
                public string ConnectionString { get; set; } = "";

                [Range(0, 10)]
                public int MaxRetryCount { get; set; } = 3;

                [Range(1, 300)]
                public int CommandTimeout { get; set; } = 30;
            }
            """
        ),
        example(
            "csharp",
            """
            var builder = WebApplication.CreateBuilder(args);

            // Регистрация строго типизированных настроек с проверкой
            builder.Services.AddOptions<DatabaseOptions>()
                .Bind(builder.Configuration.GetSection("Database"))
                .ValidateDataAnnotations()
                .ValidateOnStart();

            var app = builder.Build();

            // Получение настроек из контейнера для проверки
            var options = app.Services.GetRequiredService<IOptions<DatabaseOptions>>();
            Console.WriteLine($"Повторов: {options.Value.MaxRetryCount}");
            Console.WriteLine($"Таймаут: {options.Value.CommandTimeout} с");

            app.Run();
            """
        ),
        example(
            "text",
            "Вывод: Повторов: 3\nВывод: Таймаут: 30 с"
        ),
        table(
            ["Интерфейс", "Время жизни", "Когда менять настройки"],
            [
                ["IOptions<T>", "Singleton", "Никогда: значение вычисляется один раз при первом обращении"],
                ["IOptionsSnapshot<T>", "Scoped", "На каждый запрос: перечитывает настройки из источников"],
                ["IOptionsMonitor<T>", "Singleton", "По подписке OnChange: для фоновых служб и кэшей"],
            ],
        ),
        callout(
            "info",
            "Какой интерфейс выбрать",
            "Для статических настроек, которые не меняются без перезапуска, достаточно IOptions<T>. "
            "Если настройки могут меняться на лету и важны в пределах запроса, берите "
            "IOptionsSnapshot<T>. Если нужна реакция на изменение в долгоживущем объекте, используйте "
            "IOptionsMonitor<T> и подписку на событие OnChange.",
        ),
        heading("Логирование и структурированные записи"),
        text(
            "Журнал событий (лог) отвечает на вопрос, что происходило в приложении. Писать в журнал "
            "следует через интерфейс ILogger<T>, а не через Console.WriteLine: тогда уровень записи, "
            "категория и место назначения задаются настройками, а не кодом. Параметр типа T задаёт "
            "категорию, обычно им становится сам класс.\n\n"
            "Уровни журналирования упорядочены по важности: Trace, Debug, Information, Warning, Error, "
            "Critical. Настройка MinimumLevel отбрасывает записи ниже порога. Фильтры по категориям "
            "позволяют скрыть шум сторонних библиотек: сообщения Microsoft на уровне Warning выводятся "
            "редко, а собственные сообщения на уровне Debug — во время отладки."
        ),
        example(
            "csharp",
            """
            public class OrderService
            {
                private readonly ILogger<OrderService> _logger;

                public OrderService(ILogger<OrderService> logger)
                {
                    _logger = logger;
                }

                public void Process(int orderId, string customer)
                {
                    _logger.LogInformation(
                        "Обработка заказа {OrderId} для {Customer}",
                        orderId, customer);

                    try
                    {
                        // Здесь была бы реальная работа с заказом
                        _logger.LogDebug("Заказ {OrderId} подтверждён", orderId);
                    }
                    catch (InvalidOperationException ex)
                    {
                        _logger.LogError(ex, "Не удалось обработать {OrderId}", orderId);
                        throw;
                    }
                }
            }
            """
        ),
        text(
            "Обратите внимание на фигурные скобки в шаблоне сообщения. Это не интерполяция строк, а "
            "именованные параметры: библиотека сохраняет имя и значение отдельно, поэтому запись в JSON "
            "выглядит как {\"OrderId\": 1042, \"Customer\": \"Анна\"} и по полю можно искать. При "
            "интерполяции со знаком доллара текст склеивается заранее, и поиск по полю становится "
            "невозможным."
        ),
        example(
            "csharp",
            """
            var builder = WebApplication.CreateBuilder(args);

            // Убираем поставщиков по умолчанию и настраиваем свои
            builder.Logging.ClearProviders();
            builder.Logging.AddConsole();
            builder.Logging.AddFilter("Microsoft", LogLevel.Warning);
            builder.Logging.AddFilter("System", LogLevel.Warning);
            builder.Logging.AddFilter("Orders", LogLevel.Debug);

            var app = builder.Build();

            var logger = app.Services.GetRequiredService<ILogger<Program>>();
            using (logger.BeginScope("RequestId={RequestId}", "req-7f3a"))
            {
                logger.LogInformation("Сервис заказов запущен");
            }

            app.Run();
            """
        ),
        example(
            "text",
            "Вывод: info: Program[0]\n"
            "Вывод:       Сервис заказов запущен\n"
            "Вывод:       => RequestId=req-7f3a"
        ),
        text(
            "Метод BeginScope создаёт область видимости: все записи внутри блока получают "
            "дополнительные свойства. Область открывают на время обработки запроса с идентификатором "
            "корреляции, и тогда по журналу можно собрать все события одного запроса. Встроенный "
            "поставщик выводит записи в консоль, а для рабочей среды подключают Serilog с записью в "
            "файл и отправкой в систему сбора журналов."
        ),
        example(
            "csharp",
            """
            // Фрагмент Program.cs с подключением Serilog
            using Serilog;

            Log.Logger = new LoggerConfiguration()
                .MinimumLevel.Debug()
                .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
                .Enrich.WithProperty("Application", "OrdersApi")
                .WriteTo.Console()
                .WriteTo.File("logs/app-.log", rollingInterval: RollingInterval.Day)
                .CreateLogger();

            try
            {
                var builder = WebApplication.CreateBuilder(args);
                builder.Host.UseSerilog();

                var app = builder.Build();
                app.Run();
            }
            finally
            {
                Log.CloseAndFlush();
            }
            """
        ),
        callout(
            "warning",
            "Блокирующие вызовы в асинхронных действиях",
            "В асинхронном обработчике не вызывайте .Result и .Wait(): они блокируют поток, снижают "
            "пропускную способность и могут привести к взаимной блокировке. Используйте await. "
            "Для отмены длительной операции передавайте CancellationToken из запроса.",
        ),
        heading("Контейнер зависимостей и времена жизни"),
        text(
            "Правило создания экземпляра включает время жизни — как долго живёт созданный объект. "
            "Времён жизни три, и выбор между ними определяет поведение и безопасность приложения.\n\n"
            "Транзиентный вариант (Transient) — новый экземпляр при каждом запросе сервиса; подходит "
            "для лёгких вычислительных объектов без состояния. Scoped — один экземпляр на область "
            "видимости, в веб-приложении одна область создаётся на HTTP-запрос. Singleton — один "
            "экземпляр на всё время работы приложения; он подходит для кэшей и настроек."
        ),
        example(
            "csharp",
            """
            var builder = WebApplication.CreateBuilder(args);

            // Новый экземпляр при каждом получении
            builder.Services.AddTransient<IEmailSender, EmailSender>();

            // Один экземпляр на HTTP-запрос
            builder.Services.AddScoped<IOrderRepository, OrderRepository>();

            // Один экземпляр на всё приложение
            builder.Services.AddSingleton<IClock, SystemClock>();

            var app = builder.Build();

            // Каждый вызов из корневой области видимости возвращает тот же Singleton
            var first = app.Services.GetRequiredService<IClock>();
            var second = app.Services.GetRequiredService<IClock>();
            Console.WriteLine($"Тот же Singleton: {ReferenceEquals(first, second)}");

            app.Run();
            """
        ),
        example(
            "text",
            "Вывод: Тот же Singleton: True"
        ),
        text(
            "Дисциплина времён жизни важна из-за захвата зависимости. Singleton живёт дольше области "
            "видимости, поэтому если он напрямую зависит от Scoped-сервиса, тот останется в памяти "
            "после завершения области и будет использоваться одновременно несколькими запросами. Это "
            "ошибка проектирования: состояние одного запроса протекает в другой. В Development "
            "контейнер выявляет её при первом обращении к сервису.\n\n"
            "Если Singleton всё же должен работать со Scoped-сервисом, он получает фабрику областей "
            "IServiceScopeFactory и сам создаёт область на единицу работы. Так поступают фоновые "
            "службы: у них нет HTTP-запроса, поэтому область открывают явно."
        ),
        example(
            "csharp",
            """
            public class PendingOrdersWorker : BackgroundService
            {
                private readonly IServiceScopeFactory _scopeFactory;

                public PendingOrdersWorker(IServiceScopeFactory scopeFactory)
                {
                    _scopeFactory = scopeFactory;
                }

                protected override async Task ExecuteAsync(CancellationToken stoppingToken)
                {
                    while (!stoppingToken.IsCancellationRequested)
                    {
                        // Своя область видимости на одну единицу работы
                        using var scope = _scopeFactory.CreateScope();
                        var repository = scope.ServiceProvider
                            .GetRequiredService<IOrderRepository>();
                        await repository.ArchiveOldOrdersAsync();

                        await Task.Delay(TimeSpan.FromMinutes(5), stoppingToken);
                    }
                }
            }
            """
        ),
        text(
            "Внедрение зависимостей выполняется прежде всего через конструктор: зависимости становятся "
            "полями только для чтения, и класс нельзя создать с неполным набором. Сервис можно также "
            "запросить в действии через атрибут FromServices, но для постоянных зависимостей "
            "конструктор предпочтительнее: они видны в объявлении класса."
        ),
        heading("Minimal APIs и контроллеры"),
        text(
            "Конечная точка (endpoint) — правило сопоставления URL с функцией, формирующей ответ. В "
            "Minimal APIs её параметры привязываются автоматически: значение простого типа берётся из "
            "маршрута или строки запроса, сложный тип — из тела запроса в JSON, сервис — из "
            "контейнера. Это называется привязкой модели (model binding)."
        ),
        example(
            "csharp",
            """
            var builder = WebApplication.CreateBuilder(args);
            var app = builder.Build();

            var orders = new List<OrderDto>();
            int nextId = 1;

            app.MapGet("/api/orders", () => orders);

            app.MapGet("/api/orders/{id:int}", (int id) =>
                orders.FirstOrDefault(o => o.Id == id) is OrderDto order
                    ? Results.Ok(order)
                    : Results.NotFound());

            app.MapPost("/api/orders", (OrderDto dto) =>
            {
                var order = dto with { Id = nextId++ };
                orders.Add(order);
                return Results.Created($"/api/orders/{order.Id}", order);
            });

            app.Run();

            public record OrderDto(int Id, string Customer, decimal Total);
            """
        ),
        text(
            "Результат действия описывается объектом Results. Метод Results.Ok возвращает код 200 с "
            "телом, Results.Created — 201 с адресом нового ресурса, Results.NotFound — 404, "
            "Results.ValidationProblem — 400 с описанием ошибок. Метод MapPost получает объект из "
            "тела запроса: ASP.NET Core разбирает JSON и сам создаёт экземпляр записи."
        ),
        example(
            "bash",
            """
            curl -i -X POST http://localhost:5000/api/orders \
              -H "Content-Type: application/json" \
              -d '{"id":0,"customer":"Анна","total":1500}'
            """
        ),
        example(
            "text",
            "HTTP/1.1 201 Created\n"
            "Location: /api/orders/1\n"
            "Content-Type: application/json\n\n"
            "{\"id\":1,\"customer\":\"Анна\",\"total\":1500}"
        ),
        text(
            "Крупные приложения удобнее организовать через группы маршрутов и контроллеры. "
            "MapGroup создаёт общий префикс и общие правила для набора конечных точек, а атрибут "
            "RequireAuthorization защищает всю группу. Контроллер — класс с атрибутами, где каждый "
            "метод соответствует действию; такой стиль ближе к классическому шаблону MVC и "
            "пригодится в больших командах."
        ),
        example(
            "csharp",
            """
            [ApiController]
            [Route("api/[controller]")]
            public class OrdersController : ControllerBase
            {
                private readonly IOrderService _orders;

                public OrdersController(IOrderService orders)
                {
                    _orders = orders;
                }

                [HttpGet]
                public async Task<ActionResult<IEnumerable<OrderDto>>> GetAll()
                    => Ok(await _orders.GetAllAsync());

                [HttpGet("{id:int}")]
                public async Task<ActionResult<OrderDto>> Get(int id)
                {
                    var order = await _orders.GetByIdAsync(id);
                    return order is null ? NotFound() : Ok(order);
                }
            }
            """
        ),
        text(
            "Атрибут ApiController включает автоматические ответы 400 при неверной модели. При "
            "проверке данных атрибуты Required, StringLength, Range и EmailAddress на свойствах "
            "модели дают подробные описания ошибок без ручного кода. Контроллер не создаёт "
            "IOrderService через new — сервис приходит в конструктор из контейнера, поэтому в тестах "
            "его легко подменить подделкой."
        ),
        heading("Конвейер middleware"),
        text(
            "Слово middleware означает промежуточный компонент. Каждый HTTP-запрос проходит через "
            "цепочку таких компонентов, и каждый может выполнить действие до следующего звена, "
            "передать управление дальше и обработать ответ на обратном пути. Порядок регистрации "
            "совпадает с порядком входа, а прохождение обратно идёт в обратном порядке — как в "
            "матрёшке.\n\n"
            "Порядок критичен: обработчик исключений ставится первым и ловит сбои всех следующих "
            "звеньев, HTTPS идёт до работы с содержимым, CORS — до аутентификации, а проверка прав — "
            "до конечных точек, которые подключаются последними."
        ),
        table(
            ["Порядок", "Компонент", "Назначение"],
            [
                ["1", "UseExceptionHandler", "Перехват необработанных исключений"],
                ["2", "UseHsts, UseHttpsRedirection", "Защита транспорта и переход на HTTPS"],
                ["3", "UseStaticFiles", "Отдача файлов из папки wwwroot"],
                ["4", "UseRouting", "Выбор конечной точки по маршруту"],
                ["5", "UseCors", "Правила доступа для браузерных клиентов"],
                ["6", "UseAuthentication, UseAuthorization", "Проверка подлинности и прав"],
                ["7", "Собственное middleware", "Замер времени, журнал, ограничение частоты"],
                ["8", "MapControllers / MapGet", "Вызов обработчика и формирование ответа"],
            ],
        ),
        text(
            "Написать собственное middleware можно классом с методом InvokeAsync. Класс получает "
            "делегат RequestDelegate, который передаёт запрос следующему звену, и через "
            "внедрение зависимостей — журнал. Вызов await _next(context) продолжает цепочку, а код "
            "после него выполняется уже при формировании ответа."
        ),
        example(
            "csharp",
            """
            public class RequestTimingMiddleware
            {
                private readonly RequestDelegate _next;
                private readonly ILogger<RequestTimingMiddleware> _logger;

                public RequestTimingMiddleware(
                    RequestDelegate next,
                    ILogger<RequestTimingMiddleware> logger)
                {
                    _next = next;
                    _logger = logger;
                }

                public async Task InvokeAsync(HttpContext context)
                {
                    var started = Stopwatch.GetTimestamp();
                    try
                    {
                        await _next(context);
                    }
                    finally
                    {
                        var elapsed = Stopwatch.GetElapsedTime(started);
                        _logger.LogInformation(
                            "HTTP {Method} {Path} -> {StatusCode} за {Elapsed} мс",
                            context.Request.Method,
                            context.Request.Path,
                            context.Response.StatusCode,
                            elapsed.TotalMilliseconds);
                    }
                }
            }
            """
        ),
        example(
            "text",
            "Вывод: HTTP GET /api/orders -> 200 за 4.73 мс\n"
            "Вывод: HTTP GET /api/orders/99 -> 404 за 1.15 мс"
        ),
        text(
            "Блок finally гарантирует запись даже при исключении: журнал фиксирует неудачные запросы "
            "наравне с успешными. Метод расширения скрывает обёртку UseMiddleware. Важно помнить о "
            "состоянии: middleware создаётся один раз и используется всеми запросами параллельно, "
            "поэтому данные запроса хранят в параметре HttpContext, а не в полях класса."
        ),
        example(
            "csharp",
            """
            public static class MiddlewareExtensions
            {
                public static IApplicationBuilder UseRequestTiming(
                    this IApplicationBuilder app)
                    => app.UseMiddleware<RequestTimingMiddleware>();
            }

            // Использование в Program.cs
            app.UseExceptionHandler("/error");
            app.UseHttpsRedirection();
            app.UseRequestTiming();
            app.MapGet("/health", () => Results.Ok(new { status = "ok" }));
            """
        ),
        heading("Проверки работоспособности"),
        text(
            "Проверка работоспособности (health check) — конечная точка, которая сообщает оркестратору "
            "или балансировщику, готов ли экземпляр принимать трафик. Проверка базы данных, внешнего "
            "API и свободного места позволяет убрать неисправный экземпляр из работы заранее."
        ),
        example(
            "csharp",
            """
            var builder = WebApplication.CreateBuilder(args);

            builder.Services.AddHealthChecks()
                .AddCheck("disk-space", () =>
                {
                    long free = new DriveInfo(Path.GetPathRoot(
                        AppContext.BaseDirectory)!).AvailableFreeSpace;
                    return free > 1_000_000_000
                        ? HealthCheckResult.Healthy()
                        : HealthCheckResult.Unhealthy("Мало места на диске");
                });

            var app = builder.Build();
            app.MapHealthChecks("/health");
            app.Run();
            """
        ),
        example(
            "text",
            "Вывод: {\"status\":\"Healthy\",\"totalDuration\":\"00:00:00.0123456\"}",
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Пароль базы данных в appsettings.json", "Секрет попадает в историю контроля версий", "`dotnet user-secrets` для разработки, переменные окружения или хранилище секретов для рабочей среды"],
                ["`IOptions<T>` для настроек, которые меняются на лету", "Изменённое значение не доходит до приложения", "`IOptionsSnapshot<T>` или `IOptionsMonitor<T>`"],
                ["Singleton зависит от Scoped-сервиса", "Захват зависимости: состояние одного запроса видно в другом", "Scoped внутрь Scoped либо `IServiceScopeFactory` и своя область"],
                ["`Console.WriteLine` вместо `ILogger`", "Нет уровней, категорий и поиска по полям", "`ILogger<T>` и именованные параметры в шаблоне сообщения"],
                ["Интерполяция `$\"...{id}\"` в журнале", "Данные не структурированы, поиск по полю невозможен", "`LogInformation(\"Обработка {OrderId}\", id)`"],
                ["Конечные точки подключены раньше проверки прав", "Маршрут доступен без авторизации", "`UseAuthentication` и `UseAuthorization` до `MapGet` и `MapControllers`"],
                ["Вызов `.Result` в асинхронном действии", "Блокировка потока и риск взаимной блокировки", "Только `await` с передачей `CancellationToken`"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняйте в отдельном проекте: создайте его командой "
            "dotnet new web -n OrdersApi и перейдите в папку. После каждого изменения запускайте "
            "dotnet run и проверяйте результат через браузер или curl. Настройки проверяйте с "
            "помощью dotnet user-secrets list."
        ),
        numbered(
            "Конфигурация: добавьте в appsettings.json раздел Orders с ключами PageSize и MaxPageSize, прочитайте оба значения через GetValue и выведите их в журнал при старте.",
            "Секреты: выполните dotnet user-secrets init и dotnet user-secrets set для ключа Database:Password, затем убедитесь командой dotnet user-secrets list, что значение не попало в файл проекта.",
            "Options: опишите класс OrdersOptions с атрибутами Range, подключите его через AddOptions с ValidateOnStart и проверьте, что неверное значение останавливает запуск с понятным сообщением.",
            "Minimal API: создайте полный набор операций над заказами — список, получение по идентификатору, создание и удаление, используя Results.Ok, Results.NotFound, Results.Created и Results.NoContent.",
            "Middleware: напишите собственное middleware, которое добавляет в ответ заголовок X-Request-Id со случайным идентификатором и выводит его в журнал вместе с методом и путём запроса.",
        ),
        callout(
            "success",
            "Подсказка к заданию 3",
            "Пустое значение по умолчанию не пройдёт проверку атрибутом Required, а ValidateOnStart "
            "выбросит OptionsValidationException при запуске. Прочитайте текст исключения: в нём "
            "перечислены все нарушенные ограничения одного раздела настроек.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Какой источник конфигурации имеет наибольший приоритет по умолчанию?",
            "Чем IOptionsSnapshot отличается от IOptionsMonitor?",
            "Почему Singleton не должен напрямую зависеть от Scoped-сервиса?",
            "Зачем в шаблоне сообщения журнала используют именованные параметры вместо интерполяции?",
            "Почему обработку исключений подключают первым компонентом конвейера?",
        ),
        heading("Ответы", 3),
        numbered(
            "Аргументы командной строки: они подключаются последними, а каждый следующий источник перекрывает предыдущие.",
            "IOptionsSnapshot создаёт снимок настроек на каждый запрос в пределах области видимости, а IOptionsMonitor — один Singleton с событием OnChange для реакции на изменения в любой момент.",
            "Singleton живёт дольше области видимости и удержит Scoped-экземпляр после её завершения, из-за чего состояние одного запроса станет видно другим. Используйте IServiceScopeFactory и создавайте область на единицу работы.",
            "Именованные параметры сохраняются как отдельные поля и пригодны для поиска и фильтрации в системе сбора журналов, а интерполяция склеивает строку до записи.",
            "Конвейер входит в компоненты по порядку регистрации, поэтому обработчик исключений, зарегистрированный первым, оказывается внешним и перехватывает сбои всех последующих звеньев.",
        ),
        heading("Итоги"),
        bullets(
            "Конфигурация — дерево пар «ключ — значение» через двоеточие; последний подключённый источник перекрывает предыдущие.",
            "Порядок источников по умолчанию: `appsettings.json`, файл среды, секреты пользователя, переменные окружения, аргументы командной строки.",
            "Паттерн Options превращает раздел конфигурации в строго типизированный класс с валидацией и проверкой при старте.",
            "Журналирование идёт через `ILogger<T>` с именованными параметрами и областями видимости; `IOptionsSnapshot` читает настройки заново на каждый запрос.",
            "Времена жизни: Transient — новый экземпляр, Scoped — на запрос, Singleton — на приложение; Singleton не держит Scoped-зависимостей.",
            "Minimal APIs описывают конечные точки функциями с автоматической привязкой параметров, контроллеры группируют действия атрибутами.",
            "Порядок middleware задаёт поведение: обработка исключений, HTTPS, статические файлы, маршрутизация, CORS, аутентификация, собственные компоненты, конечные точки.",
            "Проверки работоспособности дают оркестратору сигнал о готовности экземпляра принимать запросы.",
        ),
        heading("Что дальше"),
        text(
            "Механизмы, разобранные в уроке, — каркас любого приложения на ASP.NET Core. В следующем "
            "уроке вы объедините их в многослойный проект: выделите слои представления, бизнес-логики "
            "и доступа к данным, соберёте решение из нескольких проектов и свяжете их через внедрение "
            "зависимостей. Перед переходом выполните практику: полный набор операций над заказами "
            "станет основой следующего проекта."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Документация ASP.NET Core — learn.microsoft.com/aspnet/core",
            "Основы Minimal APIs — learn.microsoft.com/aspnet/core/fundamentals/minimal-apis",
            "Внедрение зависимостей в ASP.NET Core — learn.microsoft.com/aspnet/core/fundamentals/dependency-injection",
            "Конфигурация в ASP.NET Core — learn.microsoft.com/aspnet/core/fundamentals/configuration",
            "Serilog — serilog.net",
            "Проверки работоспособности — learn.microsoft.com/aspnet/core/host-and-deploy/health-checks",
        ),
    ],
}
