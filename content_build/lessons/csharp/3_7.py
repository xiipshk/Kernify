"""Урок 3.7 курса csharp: архитектура."""

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
    "topic_order": 7,
    "name": "3.7. Архитектура",
    "slug": "csharp-3-7-архитектура",
    "short_description": (
        "Времена жизни зависимостей и перехватчики DI, конвейер middleware в ASP.NET Core, "
        "Clean Architecture, CQRS с MediatR, Event Sourcing, проектирование API и модульный монолит."
    ),
    "topic_name": "Архитектура",
    "topic_description": (
        "Взгляд на архитектуру приложения на C# сверху вниз: как устроен контейнер внедрения "
        "зависимостей и его ловушки, как работает конвейер запросов ASP.NET Core, как разделять "
        "код на слои по Clean Architecture, применять CQRS, MediatR и Event Sourcing, "
        "проектировать HTTP API и собирать модульный монолит."
    ),
    "learning_objectives": [
        "Выбирать время жизни зависимости (Transient, Scoped, Singleton) и распознавать захваченные зависимости",
        "Применять продвинутые регистрации: фабрики, декораторы, Keyed Services и валидацию контейнера",
        "Писать собственный middleware и понимать порядок конвейера, включая терминальные обработчики",
        "Раскладывать код по слоям Clean Architecture с направлением зависимостей внутрь",
        "Реализовывать CQRS через MediatR с конвейерными поведениями для валидации и логирования",
        "Проектировать события домена, Event Store и проекции, а также версионировать API через Result-паттерн",
        "Собирать модульный монолит, в котором модули общаются контрактами, а не прямыми ссылками",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "csharp",
        "архитектура",
        "dependency-injection",
        "aspnet-core",
        "cqrs",
        "clean-architecture",
    ],
    "starter_code": code(
        r"""
        using System;
        using System.Collections.Generic;

        // Мини-контейнер, который показывает суть времён жизни.
        public enum Lifetime { Transient, Scoped, Singleton }

        public sealed class MiniContainer
        {
            private readonly Dictionary<Type, (Type Impl, Lifetime Life)> _registrations = new();
            private readonly Dictionary<Type, object> _singletons = new();

            public MiniContainer Add<TService, TImpl>(Lifetime life) where TImpl : TService
            {
                _registrations[typeof(TService)] = (typeof(TImpl), life);
                return this;
            }

            public TService Resolve<TService>(Scope scope)
            {
                var (impl, life) = _registrations[typeof(TService)];
                if (life == Lifetime.Singleton)
                {
                    if (!_singletons.TryGetValue(typeof(TService), out var existing))
                    {
                        existing = Activator.CreateInstance(impl)!;
                        _singletons[typeof(TService)] = existing;
                    }
                    return (TService)existing;
                }
                if (life == Lifetime.Scoped)
                {
                    if (!scope.Cache.TryGetValue(typeof(TService), out var scoped))
                    {
                        scoped = Activator.CreateInstance(impl)!;
                        scope.Cache[typeof(TService)] = scoped;
                    }
                    return (TService)scoped;
                }
                return (TService)Activator.CreateInstance(impl)!;
            }
        }

        public sealed class Scope
        {
            public Dictionary<Type, object> Cache { get; } = new();
        }

        public sealed class Clock { }
        public sealed class RequestContext { }

        public static class Program
        {
            public static void Main()
            {
                var container = new MiniContainer()
                    .Add<Clock, Clock>(Lifetime.Singleton)
                    .Add<RequestContext, RequestContext>(Lifetime.Scoped);

                var request1 = new Scope();
                var request2 = new Scope();

                bool sameSingleton =
                    ReferenceEquals(container.Resolve<Clock>(request1), container.Resolve<Clock>(request2));
                bool sameScope =
                    ReferenceEquals(container.Resolve<RequestContext>(request1), container.Resolve<RequestContext>(request1));
                bool differentScopes =
                    ReferenceEquals(container.Resolve<RequestContext>(request1), container.Resolve<RequestContext>(request2));

                Console.WriteLine($"Singleton внутри приложения: {sameSingleton}");
                Console.WriteLine($"Scoped внутри одного запроса: {sameScope}");
                Console.WriteLine($"Scoped между разными запросами: {differentScopes}");
            }
        }
        """
    ),
    "hints": [
        "Ошибка «Cannot consume scoped service from singleton» значит, что Singleton захватил Scoped-зависимость. Решение — IVariableScopeFactory или IServiceScopeFactory, а не смена времени жизни наугад.",
        "Порядок app.Use... в ASP.NET Core определяет порядок выполнения. Исключения, CORS и аутентификация должны стоять раньше маршрутизации и эндпоинтов, иначе они не увидят запрос.",
        "Если слой Domain ссылается на EF Core или ASP.NET Core, Clean Architecture нарушена: зависимости в таком проекте всегда направлены внутрь, а инфраструктура подключается через интерфейсы.",
        "CQRS оправдан там, где чтение и запись действительно расходятся по модели или нагрузке. Для CRUD-таблицы с полем «название» это лишняя сложность."
    ],
    "content": [
        text(
            "Архитектура в C# — это не про количество проектов в решении, а про управление зависимостями. "
            "ASP.NET Core построен вокруг контейнера внедрения зависимостей (Dependency Injection, DI): класс объявляет "
            "конструктором то, что ему нужно, а контейнер создаёт объекты. От времени жизни каждой зависимости "
            "и порядка обёрток над запросом зависит, будет ли приложение работать под нагрузкой.\n\n"
            "Выше контейнера лежит прикладная архитектура. Когда приложение вырастает из трёх файлов, бизнес-правила "
            "смешиваются с SQL, контроллер узнаёт о деталях хранения, а смена формата ответа ломает десятки тестов. "
            "Здесь помогают Clean Architecture, CQRS, Event Sourcing и модульный монолит — не как ритуал, "
            "а как способы очертить границы изменений.\n\n"
            "Урок рассчитан на продвинутый уровень: примеры предполагают знание ASP.NET Core, LINQ, записей "
            "и асинхронного кода и собираются в проекте .NET 8."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "выбирать время жизни зависимости осознанно и диагностировать захваченные зависимости (captive dependency);",
            "применять фабрики, декораторы, `Keyed Services` и валидацию контейнера при старте;",
            "писать собственный middleware с опциями, терминальными обработчиками и правильным порядком применения;",
            "раскладывать код по слоям Clean Architecture, в которых зависимости направлены внутрь;",
            "реализовывать CQRS через MediatR и выносить сквозную логику в конвейерные поведения;",
            "проектировать события домена, Event Store и проекции, а также версионировать API через Result-паттерн.",
        ),
        heading("Времена жизни зависимостей"),
        text(
            "Transient — новый экземпляр на каждый запрос к контейнеру: подходит для лёгких объектов без состояния. "
            "Scoped — один экземпляр на область видимости (scope); в ASP.NET Core scope создаётся на каждый HTTP-запрос, "
            "поэтому Scoped — место для `DbContext` и состояния запроса. Singleton — один экземпляр на всё приложение: "
            "кэши, клиенты, конфигурация.\n\n"
            "Главная ловушка — captive dependency: Singleton, который держит ссылку на Scoped-зависимость. "
            "Контейнер без валидации выдаст такой Singleton без ошибки, но Scoped-объект проживёт до конца процесса "
            "и станет общим. Правило простое: зависимость не может жить дольше того, кто её захватил."
        ),
        example(
            "csharp",
            r"""
            // Transient — новый экземпляр при каждом разрешении.
            builder.Services.AddTransient<IEmailSender, SmtpEmailSender>();

            // Scoped — один экземпляр на HTTP-запрос (scope).
            builder.Services.AddScoped<IOrderRepository, OrderRepository>();
            builder.Services.AddDbContext<AppDbContext>(o => o.UseSqlServer(connectionString));

            // Singleton — один экземпляр на всё приложение.
            builder.Services.AddSingleton<IClock, SystemClock>();

            // Проверка прямо при старте: ловит captive dependencies и незарегистрированные сервисы.
            builder.Host.UseDefaultServiceProvider(o =>
            {
                o.ValidateScopes = true;
                o.ValidateOnBuild = true;
            });
            """,
        ),
        text(
            "Флаг `ValidateScopes` заставляет контейнер бросать исключение, если Singleton разрешает Scoped-сервис "
            "из корневого провайдера, а `ValidateOnBuild` проверяет, что все конструкторные зависимости зарегистрированы. "
            "В режиме разработки эти флаги включены по умолчанию, но их стоит включать и в тестах окружения — ошибка "
            "конфигурации не должна всплывать на первом запросе пользователя.\n\n"
            "Ниже — мини-контейнер, который показывает разницу времён жизни: Singleton кэшируется в контейнере, "
            "Scoped — в объекте scope, Transient не кэшируется вовсе."
        ),
        example(
            "csharp",
            r"""
            using System;
            using System.Collections.Generic;

            public enum Lifetime { Transient, Scoped, Singleton }

            public sealed class Scope
            {
                public Dictionary<Type, object> Cache { get; } = new();
            }

            public sealed class Clock { }
            public sealed class RequestContext { }

            public sealed class MiniContainer
            {
                private readonly Dictionary<Type, (Type Impl, Lifetime Life)> _registrations = new();
                private readonly Dictionary<Type, object> _singletons = new();

                public MiniContainer Add<TService, TImpl>(Lifetime life) where TImpl : TService
                {
                    _registrations[typeof(TService)] = (typeof(TImpl), life);
                    return this;
                }

                public TService Resolve<TService>(Scope scope)
                {
                    var (impl, life) = _registrations[typeof(TService)];
                    if (life == Lifetime.Singleton)
                    {
                        if (!_singletons.TryGetValue(typeof(TService), out var existing))
                        {
                            existing = Activator.CreateInstance(impl)!;
                            _singletons[typeof(TService)] = existing;
                        }
                        return (TService)existing;
                    }
                    if (life == Lifetime.Scoped)
                    {
                        if (!scope.Cache.TryGetValue(typeof(TService), out var scoped))
                        {
                            scoped = Activator.CreateInstance(impl)!;
                            scope.Cache[typeof(TService)] = scoped;
                        }
                        return (TService)scoped;
                    }
                    return (TService)Activator.CreateInstance(impl)!;
                }
            }

            var container = new MiniContainer()
                .Add<Clock, Clock>(Lifetime.Singleton)
                .Add<RequestContext, RequestContext>(Lifetime.Scoped);

            var request1 = new Scope();
            var request2 = new Scope();

            Console.WriteLine(ReferenceEquals(
                container.Resolve<Clock>(request1),
                container.Resolve<Clock>(request2)));
            Console.WriteLine(ReferenceEquals(
                container.Resolve<RequestContext>(request1),
                container.Resolve<RequestContext>(request1)));
            Console.WriteLine(ReferenceEquals(
                container.Resolve<RequestContext>(request1),
                container.Resolve<RequestContext>(request2)));
            """,
        ),
        text(
            "Вывод показывает ровно то, чего мы ждём от каждого времени жизни."
        ),
        example("text", "True\nTrue\nFalse"),
        callout(
            "danger",
            "Captive dependency",
            "Singleton никогда не должен зависеть от Scoped или Transient сервиса, который хранит состояние запроса. "
            "Первый же запрос «приватизирует» этот объект для всего приложения. Если Singleton всё же нужен доступ к Scoped-сервису, "
            "внедряйте `IServiceScopeFactory` и создавайте scope явно на время работы."
        ),
        heading("Продвинутые регистрации и декораторы"),
        text(
            "Редко обходится парой строк `AddScoped`. Фабрика принимает `IServiceProvider` и сама решает, "
            "как построить объект, — удобно для параметров времени выполнения. `Lazy<T>` откладывает создание "
            "дорогого сервиса до первого обращения, но регистрировать его нужно как Singleton или Scoped, иначе "
            "кэширование теряется. Открытые генерики одной строкой закрывают реализацию для всех типов."
        ),
        example(
            "csharp",
            r"""
            // Фабрика: объект строится по данным времени выполнения.
            builder.Services.AddSingleton<IClock>(_ => new SystemClock(TimeProvider.System));

            // Отложенная инициализация тяжёлого сервиса.
            builder.Services.AddSingleton(sp =>
                new Lazy<IReportBuilder>(() => sp.GetRequiredService<ReportBuilder>()));

            // Открытый генерик: одна строка закрывает все типы.
            builder.Services.AddScoped(typeof(IRepository<>), typeof(EfRepository<>));

            // Условная регистрация по конфигурации.
            if (builder.Configuration.GetValue<bool>("UseRedis"))
                builder.Services.AddSingleton<ICache, RedisCache>();
            else
                builder.Services.AddSingleton<ICache, MemoryCache>();
            """,
        ),
        text(
            "Keyed Services (.NET 8) решают давнюю проблему: несколько реализаций одного интерфейса. Регистрации "
            "получают ключ, а выбор происходит при внедрении через атрибут `[FromKeyedServices]`.\n\n"
            "Декоратор реализует тот же интерфейс, принимает исходную реализацию и добавляет поведение до или после "
            "вызова. Логирование, кэширование и метрики навешиваются именно так, не трогая исходный класс. "
            "Пакет `Scrutor` добавляет метод `Decorate<TService, TDecorator>()`, которого нет в стандартном контейнере."
        ),
        example(
            "csharp",
            r"""
            // Много реализаций одного интерфейса — выбираем по ключу.
            builder.Services.AddKeyedSingleton<ICache, RedisCache>("redis");
            builder.Services.AddKeyedSingleton<ICache, MemoryCache>("memory");

            public sealed class PriceService([FromKeyedServices("redis")] ICache cache)
            {
                public decimal? Get(string sku) => cache.TryGet<decimal>(sku, out var value) ? value : null;
            }

            // Декораторы через Scrutor: порядок регистрации — снизу вверх по цепочке.
            builder.Services.AddScoped<IRepository, EfRepository>();
            builder.Services.Decorate<IRepository, CachingRepository>();
            builder.Services.Decorate<IRepository, LoggingRepository>();
            """,
        ),
        text(
            "Декораторы складываются в цепочку: внешний `LoggingRepository` получает `CachingRepository`, "
            "а тот — исходный `EfRepository`. Это аккуратнее, чем наследование, при котором каждый наследник "
            "повторяет всю цепочку поведения заново."
        ),
        heading("Конвейер middleware"),
        text(
            "Middleware — слой обработки HTTP-запроса. Он получает `RequestDelegate next` — ссылку на следующий "
            "обработчик — и может сделать что-то до вызова `next`, после него или вовсе не вызывать. Так образуется "
            "конвейер: запрос идёт вглубь, ответ возвращается наружу. Если middleware не вызывает `next`, "
            "запрос замыкается на нём — это терминальный middleware (health-check, ответ из кэша, редирект). "
            "Ответ тогда нужно завершить явно: статус-код, тип контента и тело.\n\n"
            "Ниже — middleware логирования с замером времени и журналом исключений."
        ),
        example(
            "csharp",
            r"""
            using System.Diagnostics;
            using Microsoft.AspNetCore.Http;

            public sealed class RequestLoggingMiddleware
            {
                private readonly RequestDelegate _next;
                private readonly ILogger<RequestLoggingMiddleware> _logger;

                public RequestLoggingMiddleware(RequestDelegate next, ILogger<RequestLoggingMiddleware> logger)
                {
                    _next = next;
                    _logger = logger;
                }

                public async Task InvokeAsync(HttpContext context)
                {
                    var sw = Stopwatch.StartNew();
                    var requestId = context.TraceIdentifier;

                    _logger.LogInformation("Request {RequestId} {Method} {Path} started",
                        requestId, context.Request.Method, context.Request.Path);

                    try
                    {
                        await _next(context);
                        _logger.LogInformation("Request {RequestId} completed in {Elapsed}ms with {Status}",
                            requestId, sw.ElapsedMilliseconds, context.Response.StatusCode);
                    }
                    catch (Exception ex)
                    {
                        _logger.LogError(ex, "Request {RequestId} failed after {Elapsed}ms",
                            requestId, sw.ElapsedMilliseconds);
                        throw;
                    }
                }
            }

            // Регистрация через метод расширения — так поступают все встроенные middleware.
            public static class MiddlewareExtensions
            {
                public static IApplicationBuilder UseRequestLogging(this IApplicationBuilder app)
                    => app.UseMiddleware<RequestLoggingMiddleware>();
            }
            """,
        ),
        text(
            "Метод `InvokeAsync` может принимать Scoped-сервисы дополнительными параметрами — контейнер разрешит "
            "их при каждом вызове. Внедрять Scoped-сервис в конструктор нельзя: middleware создаётся один раз "
            "как Singleton, и конструктор с Scoped-зависимостью — та самая captive dependency.\n\n"
            "Порядок ниже — правильная последовательность для типичного API."
        ),
        example(
            "csharp",
            r"""
            var app = builder.Build();

            app.UseExceptionHandler("/error");   // внешний слой: ловит всё, что ниже
            app.UseRequestLogging();             // замеряет полное время запроса
            app.UseHttpsRedirection();           // редирект до маршрутизации
            app.UseCors("Frontend");             // CORS для всех эндпоинтов
            app.UseAuthentication();             // сначала «кто вы»
            app.UseAuthorization();              // потом «что вам можно»
            app.UseMiddleware<RateLimitingMiddleware>();
            app.MapControllers();                // эндпоинты

            app.Run();
            """,
        ),
        callout(
            "warning",
            "Порядок решает всё",
            "`UseAuthentication` обязан идти раньше `UseAuthorization`, иначе политики не увидят пользователя. "
            "`UseCors` обязан идти раньше маршрутизации, иначе CORS-заголовки не попадут в ответ на preflight-запрос. "
            "Ошибка в порядке не ломает сборку — она ломает поведение в продакшене."
        ),
        heading("Мини-конвейер своими руками"),
        text(
            "Чтобы перестать воспринимать конвейер как магию, полезно один раз написать его упрощённую версию. "
            "`Use` добавляет функцию, которая принимает следующий обработчик и возвращает новый. Собирая список "
            "с конца, получаем цепочку замыканий."
        ),
        example(
            "csharp",
            r"""
            using System;
            using System.Collections.Generic;
            using System.Threading.Tasks;

            var pipeline = new Pipeline();
            pipeline.Use(async (ctx, next) =>
            {
                Console.WriteLine("auth: begin");
                await next(ctx);
                Console.WriteLine("auth: end");
            });
            pipeline.Use(async (ctx, next) =>
            {
                Console.WriteLine($"handler for {ctx}");
                await next(ctx);
            });

            await pipeline.InvokeAsync("/orders");

            public sealed class Pipeline
            {
                private readonly List<Func<string, Func<string, Task>, Task>> _steps = new();

                public void Use(Func<string, Func<string, Task>, Task> step) => _steps.Add(step);

                public Task InvokeAsync(string context)
                {
                    Func<string, Task> next = _ => Task.CompletedTask;
                    for (int i = _steps.Count - 1; i >= 0; i--)
                    {
                        var step = _steps[i];
                        var current = next;
                        next = ctx => step(ctx, current);
                    }
                    return next(context);
                }
            }
            """,
        ),
        example("text", "auth: begin\nhandler for /orders\nauth: end"),
        text(
            "Вывод показывает матрёшку: код до `await next` выполняется по порядку регистрации, код после — "
            "в обратном. Поэтому middleware логирования видит статус-код ответа: он читает его уже после того, "
            "как цепочка вернула управление."
        ),
        heading("Clean Architecture"),
        text(
            "Clean Architecture — это правило о направлении зависимостей, а не набор папок. Domain содержит "
            "сущности и бизнес-правила и не ссылается ни на что, кроме базовой библиотеки. Application описывает "
            "сценарии использования и зависит только от Domain. Infrastructure реализует порты — интерфейсы баз, "
            "очередей, платёжных шлюзов. WebApi знает о HTTP, но не о деталях хранения. Зависимости всегда "
            "направлены внутрь.\n\n"
            "Признак правильной архитектуры простой: если удалить проект базы данных, Domain и Application "
            "по-прежнему компилируются."
        ),
        example(
            "text",
            "src/\n"
            "├── Domain/              сущности, объекты-значения, события домена, интерфейсы репозиториев\n"
            "│   ├── Entities/\n"
            "│   ├── ValueObjects/\n"
            "│   └── Events/\n"
            "├── Application/         сценарии использования, команды и запросы\n"
            "│   ├── Commands/\n"
            "│   ├── Queries/\n"
            "│   ├── Handlers/\n"
            "│   └── Abstractions/\n"
            "├── Infrastructure/      реализации: EF Core, Dapper, почта, платёжный шлюз\n"
            "│   ├── Persistence/\n"
            "│   └── Services/\n"
            "└── WebApi/              контроллеры, middleware, фильтры",
        ),
        text(
            "Сущности Domain должны защищать инварианты — условия, которые всегда истинны для объекта. "
            "Классический пример — заказ, который нельзя изменить после отправки. Если проверка живёт в контроллере, "
            "её обойдёт вторая точка входа; если в сущности — обойти невозможно. Такой подход называют богатой "
            "доменной моделью в противоположность анемичной, где сущность — набор свойств, а логика размазана по сервисам."
        ),
        example(
            "csharp",
            r"""
            public enum OrderStatus { Draft, Submitted, Shipped }

            public sealed class Order
            {
                private readonly List<OrderItem> _items = new();

                public Guid Id { get; }
                public OrderStatus Status { get; private set; }
                public IReadOnlyList<OrderItem> Items => _items;

                private Order(Guid id) => Id = id;

                public static Order Create() => new(Guid.NewGuid());

                public void AddItem(string sku, int quantity)
                {
                    if (Status != OrderStatus.Draft)
                        throw new InvalidOperationException("Заказ уже отправлен — менять нельзя.");
                    if (quantity <= 0)
                        throw new ArgumentOutOfRangeException(nameof(quantity), "Количество должно быть > 0.");

                    _items.Add(new OrderItem(sku, quantity));
                }

                public void Submit()
                {
                    if (_items.Count == 0)
                        throw new InvalidOperationException("Пустой заказ отправить нельзя.");
                    Status = OrderStatus.Submitted;
                }
            }

            public sealed record OrderItem(string Sku, int Quantity);

            var order = Order.Create();
            order.AddItem("SKU-1", 2);
            order.Submit();
            try
            {
                order.AddItem("SKU-2", 1);
            }
            catch (InvalidOperationException ex)
            {
                Console.WriteLine(ex.Message);
            }
            Console.WriteLine($"Статус: {order.Status}, позиций: {order.Items.Count}");
            """,
        ),
        example("text", "Заказ уже отправлен — менять нельзя.\nСтатус: Submitted, позиций: 1"),
        text(
            "У этой сущности нет ни атрибутов EF Core, ни зависимостей на `DbContext`. Сохранит её реализация "
            "`IOrderRepository` из слоя Infrastructure. Приватный конструктор закрыт для всех, кроме фабрики `Create`, "
            "поэтому создать заказ в обход инвариантов нельзя. Если инфраструктура требует публичный конструктор, "
            "лучше настроить маппинг явно или читать такие агрегаты через `Dapper`."
        ),
        heading("CQRS и MediatR"),
        text(
            "Command Query Responsibility Segregation (CQRS) разделяет операции, которые меняют состояние, "
            "и операции, которые только читают. Команда — намерение что-то изменить, запрос — намерение получить данные. "
            "Польза в том, что чтение и запись оптимизируются независимо: запись идёт через сущности с инвариантами, "
            "а чтение — прямое проектирование в DTO.\n\n"
            "MediatR добавляет посредника: контроллер не знает обработчика, он отправляет команду в `IMediator`, "
            "а тот находит единственный `IRequestHandler<TRequest, TResponse>`."
        ),
        example(
            "csharp",
            r"""
            public sealed record CreateOrderCommand(Guid CustomerId, IReadOnlyList<OrderLine> Lines) : IRequest<Guid>;

            public sealed record OrderLine(string Sku, int Quantity);

            public sealed class CreateOrderHandler : IRequestHandler<CreateOrderCommand, Guid>
            {
                private readonly IOrderRepository _orders;
                private readonly IUnitOfWork _unitOfWork;

                public CreateOrderHandler(IOrderRepository orders, IUnitOfWork unitOfWork)
                {
                    _orders = orders;
                    _unitOfWork = unitOfWork;
                }

                public async Task<Guid> Handle(CreateOrderCommand request, CancellationToken ct)
                {
                    var order = Order.Create();
                    foreach (var line in request.Lines)
                        order.AddItem(line.Sku, line.Quantity);

                    await _orders.AddAsync(order, ct);
                    await _unitOfWork.SaveChangesAsync(ct);
                    return order.Id;
                }
            }

            // Регистрация всех обработчиков из сборки приложения.
            builder.Services.AddMediatR(cfg =>
                cfg.RegisterServicesFromAssembly(typeof(Program).Assembly));
            """,
        ),
        text(
            "Конвейерные поведения (pipeline behaviors) — главный козырь MediatR. Каждое поведение оборачивает "
            "вызов любого обработчика и получает ссылку на следующий шаг. Валидация, логирование, транзакции "
            "и метрики описываются один раз и применяются ко всем командам. Первым регистрируется самый внешний слой."
        ),
        example(
            "csharp",
            r"""
            public sealed class ValidationBehavior<TRequest, TResponse>
                : IPipelineBehavior<TRequest, TResponse>
                where TRequest : notnull
            {
                private readonly IEnumerable<IValidator<TRequest>> _validators;

                public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators)
                    => _validators = validators;

                public async Task<TResponse> Handle(
                    TRequest request,
                    RequestHandlerDelegate<TResponse> next,
                    CancellationToken ct)
                {
                    var context = new ValidationContext<TRequest>(request);
                    var failures = _validators
                        .Select(v => v.Validate(context))
                        .SelectMany(r => r.Errors)
                        .Where(f => f is not null)
                        .ToList();

                    if (failures.Count > 0)
                        throw new ValidationException(failures);

                    return await next(ct);
                }
            }

            // Логирование — внешний слой, валидация — внутренний.
            builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));
            builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));
            """,
        ),
        text(
            "Валидация в поведении проверяет структуру запроса — длину строки, диапазон чисел, обязательность полей. "
            "Бизнес-правила (запрет менять отправленный заказ) остаются в сущности. Правило, живущее только "
            "в валидаторе, обходят импортёры и фоновые задачи, которые валидаторы не вызывают."
        ),
        heading("Event Sourcing и проекции"),
        text(
            "В обычной системе в базе хранится текущее состояние, а история пишется отдельно. Event Sourcing "
            "переворачивает картину: единственный источник истины — последовательность событий. Заказ открыт, "
            "добавлена позиция, заказ отправлен — а текущее состояние получается проигрыванием событий по порядку.\n\n"
            "Агрегат не меняет поля напрямую: он порождает событие, а метод `When` применяет его. Это даёт аудит, "
            "состояние на любую дату и основу для синхронизации сервисов. Цена — проекции для быстрых чтений "
            "и проверка версии агрегата, чтобы параллельные записи не перезаписали друг друга."
        ),
        example(
            "csharp",
            r"""
            using System.Text.Json;

            public interface IDomainEvent { Guid AggregateId { get; } }

            public sealed record UserRegistered(Guid AggregateId, string Email) : IDomainEvent;
            public sealed record UserRenamed(Guid AggregateId, string Name) : IDomainEvent;

            public sealed class User
            {
                private readonly List<IDomainEvent> _changes = new();

                public Guid Id { get; private set; }
                public string Email { get; private set; } = "";
                public string Name { get; private set; } = "";
                public int Version { get; private set; }

                public IReadOnlyList<IDomainEvent> Changes => _changes;

                public static User Register(string email)
                {
                    var user = new User();
                    user.Raise(new UserRegistered(Guid.NewGuid(), email));
                    return user;
                }

                public void Rename(string name)
                {
                    if (Name == name) return;
                    Raise(new UserRenamed(Id, name));
                }

                public void Load(IEnumerable<IDomainEvent> history)
                {
                    foreach (var e in history)
                        Apply(e);
                }

                private void Raise(IDomainEvent e)
                {
                    Apply(e);
                    _changes.Add(e);
                }

                private void Apply(IDomainEvent e)
                {
                    switch (e)
                    {
                        case UserRegistered r: Id = r.AggregateId; Email = r.Email; break;
                        case UserRenamed r: Name = r.Name; break;
                    }
                    Version++;
                }
            }

            public sealed class EventStore
            {
                private readonly List<string> _log = new();

                public void Append(IEnumerable<IDomainEvent> events)
                {
                    foreach (var e in events)
                        _log.Add(JsonSerializer.Serialize(e));
                }

                public IReadOnlyList<string> All => _log;
            }

            var store = new EventStore();
            var user = User.Register("anna@example.com");
            user.Rename("Анна");
            store.Append(user.Changes);

            foreach (var json in store.All)
                Console.WriteLine(json);
            """,
        ),
        example(
            "text",
            '{"AggregateId":"d3b0d4a4-9c0d-4d1f-9e54-0f7d4e3a1b22","Email":"anna@example.com"}\n'
            '{"AggregateId":"d3b0d4a4-9c0d-4d1f-9e54-0f7d4e3a1b22","Name":"Анна"}',
        ),
        text(
            "Проекции читают поток событий и поддерживают денормализованную модель для запросов. Таблица "
            "`UsersView` обновляется подписчиком на события. Проекции можно сбросить и пересобрать из журнала — "
            "главный аргумент за Event Sourcing там, где аудит обязателен: финансы, бронирования, склад.\n\n"
            "Для CRUD-таблицы с тремя полями Event Sourcing добавит журнал и подписчиков без пользы. "
            "Частый способ провалиться — выбрать его для всей системы вместо одного критичного агрегата."
        ),
        callout(
            "info",
            "Согласованность",
            "Event Sourcing по умолчанию даёт согласованность в конечном счёте (eventual consistency): проекция обновится "
            "не сразу после записи события. Клиенту, который только что создал заказ, проекция чтения может ответить "
            "«нет данных» ещё несколько миллисекунд. Это проектируется явно: либо подтверждение до обновления проекции, "
            "либо чтение с ожиданием версии."
        ),
        heading("Проектирование API"),
        text(
            "REST остаётся самым распространённым стилем публичного API. Ресурсы — существительные во множественном "
            "числе, методы HTTP отражают смысл операции, коды статусов используются по назначению. При создании "
            "ресурса возвращайте 201 и заголовок `Location`. При ошибке — 4xx, а не 200 с текстом ошибки внутри.\n\n"
            "Версионирование обязательно: модель данных живёт дольше одного релиза. Версия в пути (`/api/v2/users`) "
            "проще для отладки, версия в заголовке (`X-Api-Version`) лучше соответствует REST, где адрес указывает "
            "на ресурс, а не на формат."
        ),
        table(
            ["Стиль", "Когда выбирать", "Ограничения"],
            [
                ["REST + JSON", "Публичный API, кэширование, браузерные клиенты", "Нет строгого контракта из коробки — нужен OpenAPI"],
                ["gRPC", "Сервис-сервис, низкая задержка, двунаправленные потоки", "Браузеры требуют прокси, бинарный формат сложнее отлаживать"],
                ["GraphQL", "Много клиентов с разными потребностями в данных", "Сложнее кэшировать, риск тяжёлых запросов"],
            ],
        ),
        text(
            "Ошибки — тоже часть контракта. Вместо исключений, которые превращаются в 500, используйте паттерн "
            "Result: обработчик возвращает значение или ошибку, а переход в HTTP-код происходит на границе приложения. "
            "Ожидаемые ошибки становятся видимыми в сигнатуре и тестируются без проверки статусов в бизнес-логике."
        ),
        example(
            "csharp",
            r"""
            public sealed record Error(string Code, string Message);

            public sealed record Result<T>(T? Value, Error? Error)
            {
                public bool IsSuccess => Error is null;
                public static Result<T> Success(T value) => new(value, null);
                public static Result<T> Failure(Error error) => new(default, error);
            }

            // Граница: всё, что знает про HTTP, живёт здесь.
            private ActionResult HandleError(Error error) => error.Code switch
            {
                "NotFound" => NotFound(error.Message),
                "Validation" => BadRequest(error.Message),
                "Conflict" => Conflict(error.Message),
                _ => StatusCode(500, error.Message),
            };

            [HttpGet("{id:guid}")]
            public async Task<ActionResult<UserDto>> Get(Guid id, CancellationToken ct)
            {
                var result = await _mediator.Send(new GetUserQuery(id), ct);
                return result.IsSuccess ? Ok(result.Value) : HandleError(result.Error!);
            }

            [HttpPost]
            public async Task<ActionResult<Guid>> Create(CreateUserCommand command, CancellationToken ct)
            {
                var id = await _mediator.Send(command, ct);
                return CreatedAtAction(nameof(Get), new { id }, id);
            }
            """,
        ),
        text(
            "REST и gRPC не обязаны конкурировать. Публичное API отдавайте по REST и документируйте через OpenAPI, "
            "а взаимодействие между сервисами ведите по gRPC, где важны строгий контракт `.proto` и скорость. "
            "Сгенерированный клиент не позволит отправить неверное поле — ошибка всплывает при компиляции."
        ),
        heading("Модульный монолит"),
        text(
            "Микросервисы решают проблемы масштаба, но приносят распределённые транзакции, сетевые отказы "
            "и инфраструктуру деплоя. Модульный монолит занимает промежуточное положение: один процесс и одна база, "
            "но явные границы модулей. Модуль Users не обращается к таблице модуля Orders напрямую — только через "
            "его контракт или событие.\n\n"
            "Границы внутри монолита легче перенести в отдельный сервис, когда появится причина. Но ничто не мешает "
            "импортировать чужой тип, поэтому границы поддерживаются тестами архитектуры и код-ревью."
        ),
        example(
            "csharp",
            r"""
            public interface IModule
            {
                void RegisterServices(IServiceCollection services, IConfiguration config);
                void MapEndpoints(IEndpointRouteBuilder endpoints);
            }

            public sealed class UsersModule : IModule
            {
                public void RegisterServices(IServiceCollection services, IConfiguration config)
                {
                    services.AddDbContext<UsersDbContext>(o =>
                        o.UseNpgsql(config.GetConnectionString("Users")));
                    services.AddScoped<IUserRepository, UserRepository>();
                    services.AddMediatR(cfg =>
                        cfg.RegisterServicesFromAssembly(typeof(UsersModule).Assembly));
                }

                public void MapEndpoints(IEndpointRouteBuilder endpoints)
                {
                    endpoints.MapGet("/api/users/{id:guid}", async (Guid id, ISender sender, CancellationToken ct) =>
                    {
                        var result = await sender.Send(new GetUserQuery(id), ct);
                        return result.IsSuccess ? Results.Ok(result.Value) : Results.NotFound(result.Error);
                    });
                }
            }

            var modules = new IModule[] { new UsersModule(), new OrdersModule() };

            foreach (var module in modules)
                module.RegisterServices(builder.Services, builder.Configuration);

            var app = builder.Build();

            foreach (var module in modules)
                module.MapEndpoints(app);
            """,
        ),
        text(
            "Между модулями общайтесь через событие интеграции (`UserRegistered` публикуется после коммита, "
            "модуль Orders на него подписывается) или через узкий интерфейс-контракт. Прямая ссылка "
            "на `OrderRepository` из модуля Users — та самая жёсткая связность, из-за которой монолит превращается "
            "в клубок.\n\n"
            "Тест архитектуры делает нарушения видимыми автоматически. NetArchTest описывает правила кодом: "
            "«Domain не зависит от EF Core», «модуль Users не ссылается на типы модуля Orders»."
        ),
        example(
            "csharp",
            r"""
            using NetArchTest.Rules;

            var domain = Types.InAssembly(typeof(Order).Assembly);
            var application = Types.InAssembly(typeof(CreateOrderHandler).Assembly);
            var infrastructure = Types.InAssembly(typeof(UserRepository).Assembly);

            var rules = new[]
            {
                domain.ShouldNot().HaveDependencyOnAny(
                    "Microsoft.EntityFrameworkCore", "Microsoft.AspNetCore"),
                domain.ShouldNot().HaveDependencyOn("Infrastructure"),
                application.ShouldNot().HaveDependencyOn("Infrastructure"),
                infrastructure.ShouldNot().HaveDependencyOn("WebApi"),
            };
            """,
        ),
        text(
            "Правила пишутся для каждого слоя и модуля и падают в CI при первом неправильном `using`. "
            "Меняется архитектура — сначала меняется правило, и только потом код."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Singleton зависит от Scoped", "Scoped-объект живёт весь процесс и делится между запросами", "`IServiceScopeFactory` или сменить время жизни"],
                ["Бизнес-логика в контроллере", "Правила дублируются, тесты требуют HTTP", "Логика в Application, контроллер только отображение"],
                ["Анемичная доменная модель", "Инварианты рассыпаны по сервисам и частично потеряны", "Инварианты в сущности, приватные конструкторы, фабрики"],
                ["CQRS и Event Sourcing везде", "Лишние классы, проекции и сложность без выгоды", "Эти подходы для сложных мест, CRUD — для простых"],
                ["`UseCors` после `MapControllers`", "Браузер получает ошибку CORS на preflight", "CORS до маршрутизации и эндпоинтов"],
                ["Модули ссылаются на чужие типы", "Любое изменение ломает соседние модули", "Контракты и события, тесты архитектуры"],
                ["Исключения вместо Result", "Ожидаемые ошибки превращаются в 500", "Result-паттерн и отображение в коды на границе"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняйте в одном решении на .NET 8 или новее. После каждого шага собирайте проект "
            "командой `dotnet build` и запускайте тесты `dotnet test`."
        ),
        numbered(
            "Диагностика DI: зарегистрируйте `DbContext` как Transient, а репозиторий как Singleton и запустите приложение с `ValidateScopes = true`. Добейтесь ошибки, затем исправьте регистрации.",
            "Декоратор: напишите `CachingUserRepository`, который реализует `IUserRepository`, оборачивает исходный репозиторий и кэширует результат `GetByIdAsync`. Подключите его через Scrutor.",
            "Middleware: реализуйте обработчик, который добавляет в каждый ответ заголовок `X-Correlation-Id` из 16-символьного Guid и возвращает 202 для запросов на `/health`.",
            "Clean Architecture: выделите в своём проекте слои Domain, Application и Infrastructure и добавьте тест архитектуры с NetArchTest, запрещающий Domain ссылаться на EF Core.",
            "CQRS: переведите один CRUD-сервис на команды и запросы через MediatR, добавьте `ValidationBehavior` с FluentValidation и убедитесь, что невалидный запрос возвращает 400.",
        ),
        text("Первый шаг третьего задания в виде кода:"),
        example(
            "csharp",
            r"""
            public sealed class CorrelationIdMiddleware(RequestDelegate next)
            {
                public async Task InvokeAsync(HttpContext context)
                {
                    var id = Guid.NewGuid().ToString("N")[..16];
                    context.Response.Headers["X-Correlation-Id"] = id;

                    if (context.Request.Path == "/health")
                    {
                        context.Response.StatusCode = 202;
                        await context.Response.WriteAsync("accepted");
                        return;
                    }

                    await next(context);
                }
            }
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 5",
            "Начните с одного обработчика и одного валидатора. Только когда сценарий заработает целиком, добавляйте `LoggingBehavior` — "
            "так проще понять, какой именно слой портит ответ."
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему Singleton не должен внедрять Scoped-сервис?",
            "В чём разница между middleware, который вызывает `next`, и терминальным middleware?",
            "Зачем в Clean Architecture зависимость направлена внутрь, к Domain?",
            "Какую задачу решают конвейерные поведения MediatR?",
            "Почему Event Sourcing требует отдельных проекций для чтения?",
            "Зачем публичный API нуждается в версионировании?",
        ),
        heading("Ответы", 3),
        numbered(
            "Singleton живёт весь процесс, поэтому Scoped-объект, попавший в него, становится общим для всех запросов и держит состояние одного запроса до конца работы приложения.",
            "Обычный middleware выполняет код до и после `next` и передаёт управление дальше. Терминальный обрабатывает запрос сам: формирует ответ и не вызывает `next`.",
            "Чтобы бизнес-правила не зависели от базы, HTTP и библиотек. Внутренний слой не знает, как он сохранён, а инфраструктура реализует его порты.",
            "Они оборачивают вызов любого обработчика и реализуют сквозную логику — валидацию, логирование, транзакции — один раз вместо копирования в каждом обработчике.",
            "Поток событий отвечает на вопрос «как» мы пришли к состоянию, а проекция отвечает на вопрос «что сейчас» быстро и в готовой форме для конкретного экрана или отчёта.",
            "Модель данных и её формат меняются со временем, а старые клиенты продолжают работать. Версия фиксирует контракт и позволяет менять поведение без поломки клиентов."
        ),
        heading("Итоги"),
        bullets(
            "Времена жизни: Transient на каждый запрос, Scoped на scope, Singleton на процесс; зависимость не должна жить дольше того, кто её захватил.",
            "Продвинутые регистрации: фабрики, `Lazy<T>`, `Keyed Services`, декораторы и валидация контейнера при старте.",
            "Middleware — матрёшка вокруг запроса; порядок `Use...` критичен, терминальный middleware не вызывает `next`.",
            "Clean Architecture — правило направления зависимостей: Domain не знает ничего снаружи, инфраструктура реализует порты.",
            "CQRS и MediatR разделяют чтение и запись; поведение навешивает сквозную логику на все обработчики сразу.",
            "Event Sourcing хранит события, а не состояние; проекции дают быстрые модели чтения, а архитектура — аудит и восстановление.",
            "API проектируется как контракт: корректные коды, версии, Result-паттерн и OpenAPI; модульный монолит держит границы внутри одного процесса.",
        ),
        heading("Что дальше"),
        text(
            "Вы прошли базовый курс по архитектуре на C#. Дальше два направления: вглубь — распределённые системы, "
            "брокеры сообщений, saga и идемпотентность; и вширь — измерение архитектуры: стоимость изменения, "
            "время сборки, наблюдаемость. Начните с практики: вынесите одно бизнес-правило в Domain-слой "
            "и добавьте тест архитектуры, запрещающий обратную зависимость."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Jason Taylor: Clean Architecture Solution Template — github.com/jasontaylordev/CleanArchitecture",
            "MediatR: документация и примеры конвейерных поведений — github.com/jbogard/MediatR",
            "Middleware в ASP.NET Core: документация Microsoft — learn.microsoft.com/aspnet/core/fundamentals/middleware",
            "Kamil Grzybek: Modular Monolith Architecture — github.com/kgrzybek/modular-monolith-with-ddd",
            "Greg Young и Martin Fowler: материалы по CQRS и Event Sourcing — martinfowler.com/bliki/CQRS.html",
            "Microsoft REST API Guidelines — github.com/microsoft/api-guidelines",
        ),
    ],
}
