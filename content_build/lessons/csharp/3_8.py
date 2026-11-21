"""Урок 3.8 курса csharp: продвинутый .NET."""

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
    "topic_order": 8,
    "name": "3.8. Продвинутый .NET",
    "slug": "csharp-3-8-продвинутый-net",
    "short_description": (
        "Прикладной .NET для продакшена: конвейер ASP.NET Core и Minimal APIs, "
        "производительность EF Core, gRPC и SignalR, фоновые службы с распределёнными "
        "блокировками, наблюдаемость через OpenTelemetry и проверки работоспособности."
    ),
    "topic_name": "Продвинутый .NET",
    "topic_description": (
        "Продвинутый разбор платформы .NET за пределами языка: как устроен конвейер "
        "обработки запросов ASP.NET Core и в каком порядке ставятся middleware, как "
        "ускорить EF Core и убрать проблемы N+1, чем отличаются gRPC и SignalR, как "
        "строить надёжные фоновые службы и какие инструменты дают наблюдаемость — "
        "логи, метрики и распределённые трассы."
    ),
    "learning_objectives": [
        "Объяснять порядок middleware в ASP.NET Core и собирать Minimal API с фильтрами и типизированными результатами",
        "Убирать проблемы производительности EF Core: N+1, декартово произведение, отсутствие NoTracking и пула контекстов",
        "Выбирать транспорт между HTTP/JSON, gRPC и SignalR под конкретную задачу и настраивать HttpClientFactory",
        "Писать периодические BackgroundService с корректным scope, обработкой ошибок и распределённой блокировкой",
        "Настраивать наблюдаемость: структурированные логи, собственные метрики, ActivitySource и экспорт в OTLP",
        "Разделять проверки liveness и readiness и защищать ими развёртывание",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "csharp",
        "aspnet-core",
        "ef-core",
        "background-services",
        "opentelemetry",
        "grpc",
    ],
    "starter_code": code(
        r"""
        using System;
        using System.Collections.Generic;

        // Мини-модель конвейера: middleware — это функция «запрос -> ответ»,
        // которая оборачивает следующий обработчик.
        public sealed record Request(string Path, Dictionary<string, string> Items);

        public static class Program
        {
            public static void Main()
            {
                var log = new List<string>();

                // Делегат, который обрабатывает запрос; null — значит, фильтр его не вызывает.
                Func<Request, string?> endpoint = req => $"200 OK {req.Path}";

                Func<Request, string?> tracing = req =>
                {
                    log.Add($"trace {req.Path}");
                    return endpoint(req);
                };

                Func<Request, string?> auth = req =>
                {
                    string? user = req.Items.GetValueOrDefault("user");
                    if (string.IsNullOrEmpty(user))
                    {
                        log.Add("auth rejected");
                        return "401 Unauthorized";
                    }
                    return tracing(req);
                };

                var pipeline = auth;

                foreach (var path in new[] { "/public", "/private" })
                {
                    var items = new Dictionary<string, string>();
                    if (path == "/private") items["user"] = "anna";
                    var req = new Request(path, items);

                    string status = pipeline(req) ?? "204 No Content";
                    Console.WriteLine($"{path} -> {status}");
                }

                Console.WriteLine(string.Join("; ", log));
            }
        }
        """
    ),
    "hints": [
        "Порядок middleware в ASP.NET Core определяет, что и в каком порядке выполнится: маршрутизация, затем аутентификация, затем авторизация. Перепутанный порядок даёт отказ, который трудно заметить в логах.",
        "Проблема N+1 в EF Core — это когда загрузка одной коллекции уходит в базу коллекцией запросов. Смотрите на лог SQL в консоли разработчика: количество запросов на один HTTP-вызов должно быть небольшим.",
        "BackgroundService живёт как singleton, поэтому scoped-сервисы получайте только через IServiceScopeFactory.CreateScope(), а не в конструкторе.",
        "Секундомер в консоли и необработанный exception в фоновом цикле ломают всю службу. Всегда ловите исключение внутри цикла, иначе BackgroundService молча завершится.",
    ],
    "content": [
        text(
            "Предыдущие уроки курса — это язык и рантайм. Этот урок — про платформу: про то, "
            "что стоит вокруг вашего кода в настоящем сервисе. ASP.NET Core принимает запросы, "
            "EF Core ходит в базу, HttpClient и gRPC разговаривают с другими сервисами, "
            "BackgroundService выполняет работу без пользователя, а OpenTelemetry объясняет "
            "постфактум, почему всё упало в три ночи.\n\n"
            "Уровень продвинутый означает, что базовые вещи — `AddControllers`, `DbContext`, "
            "`async/await` — уже известны. Здесь важны решения, которые почти не видны в коде, "
            "но определяют поведение системы: порядок middleware, стратегия загрузки связей, "
            "время жизни служб, точка выхода наружу. Ошибка в каждом из этих мест даёт не "
            "исключение в тесте, а проблему в продакшене через неделю.\n\n"
            "Все примеры рассчитаны на .NET 8 и старше: часть — фрагменты внутри сервиса, "
            "часть — самодостаточные программы с выводом."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "объяснять порядок middleware в конвейере ASP.NET Core и собирать Minimal API с фильтрами, группами и типизированными результатами;",
            "устранять типичные узкие места EF Core: проблему N+1, декартово произведение при `Include`, лишнее отслеживание изменений и создание контекста на каждый запрос;",
            "выбирать транспорт под задачу: HTTP с JSON, gRPC для межсервисных вызовов, SignalR для обновлений в реальном времени;",
            "правильно настраивать `HttpClient` через `IHttpClientFactory` и политики устойчивости;",
            "писать периодические фоновые службы с корректным `IServiceScopeFactory`, обработкой исключений и распределённой блокировкой;",
            "настраивать наблюдаемость: структурированные логи, собственные метрики через `IMeterFactory`, трассы через `ActivitySource` и проверки работоспособности liveness и readiness.",
        ),
        heading("Конвейер обработки запроса в ASP.NET Core"),
        text(
            "Каждый middleware получает "
            "запрос, может что-то сделать, вызвать следующий обработчик и повлиять на ответ. "
            "Последним в цепочке стоит обработчик конечной точки (endpoint), который выбирается "
            "маршрутизацией. Такая конструкция называется конвейером запросов (request pipeline), "
            "и порядок компонентов в нём не декоративен: он определяет поведение.\n\n"
            "Если аутентификация поставлена после авторизации, авторизация не увидит "
            "пользователя и отклонит запросы, которые должны были пройти. Если маршрутизация "
            "стоит после конечных точек, маршрут не будет найден. Ниже — типовой рабочий порядок."
        ),
        example(
            "csharp",
            r"""
            var builder = WebApplication.CreateBuilder(args);

            builder.Services.AddProblemDetails();
            builder.Services.AddAuthentication().AddJwtBearer();
            builder.Services.AddAuthorization();

            var app = builder.Build();

            app.UseExceptionHandler();      // 1. ловит исключения ниже по конвейеру
            app.UseHttpsRedirection();      // 2. переадресация на HTTPS
            app.UseStaticFiles();           // 3. статика, без обращения к базе
            app.UseRouting();               // 4. выбор конечной точки по маршруту
            app.UseAuthentication();        // 5. кто вы (заполняет User)
            app.UseAuthorization();         // 6. что вам можно (проверяет политики)

            app.MapGet("/orders/{id:int}", (int id) => Results.Ok(new { id }))
               .RequireAuthorization();

            app.Run();
            """,
        ),
        text(
            "Обратите внимание на зависимости между компонентами. `UseExceptionHandler` "
            "ставится первым, чтобы перехватывать исключения всех следующих компонентов. "
            "`UseStaticFiles` — до маршрутизации, чтобы запрос за картинкой не проходил через "
            "базу. `UseAuthentication` обязательно до `UseAuthorization`: авторизация проверяет "
            "принципала, которого создаёт аутентификация. Нарушение этого порядка — классическая "
            "причина ответов 401 там, где пользователь явно авторизован.\n\n"
            "Middleware — singleton по времени жизни, поэтому в него нельзя передавать "
            "`DbContext` или другой scoped-сервис: получится захваченная зависимость, живущая "
            "дольше, чем должна. Зависимость берут из `context.RequestServices` внутри вызова."
        ),
        callout(
            "warning",
            "Порядок middleware не переставляйте «на глаз»",
            "Порядок определяет не только логику, но и безопасность. Аутентификация до "
            "авторизации, исключения первыми, маршрутизация после статики. Если после правки "
            "ad-hoc начались 401 или 404 — проверьте порядок первым делом.",
        ),
        heading("Minimal APIs: группы, фильтры и типизированные результаты"),
        text(
            "Minimal APIs, появившиеся в .NET 6, — это способ описать HTTP-эндпоинт функцией "
            "вместо контроллера. Параметры функции связываются автоматически: значение из "
            "маршрута берётся по имени, из query-строки, из тела запроса или из контейнера "
            "зависимостей. Атрибут `[FromServices]` (или просто интерфейс в параметрах) "
            "позволяет получить зарегистрированный сервис, а `CancellationToken` приходит из "
            "`HttpContext.RequestAborted` и отменяется, если клиент отключился.\n\n"
            "Для крупных API удобны группы маршрутов: `MapGroup` задаёт общий префикс и общие "
            "политики вроде `RequireAuthorization()`. Фильтры эндпоинтов (endpoint filters) — "
            "это аналог action-фильтров: код, который выполняется до и после обработчика и "
            "может вернуть собственный ответ, не вызывая `next`."
        ),
        example(
            "csharp",
            r"""
            var api = app.MapGroup("/api/v1").RequireAuthorization();

            // Фильтр проверяет DTO и не пускает дальше при ошибке.
            var users = api.MapGroup("/users")
                           .AddEndpointFilter(async (ctx, next) =>
                           {
                               var dto = ctx.Arguments.OfType<CreateUserDto>().FirstOrDefault();
                               if (dto is not null && string.IsNullOrWhiteSpace(dto.Email))
                               {
                                   return Results.ValidationProblem(new Dictionary<string, string[]>
                                   {
                                       ["email"] = new[] { "Email обязателен" }
                                   });
                               }
                               return await next(ctx);
                           });

            users.MapGet("/{id:guid}", async (
                Guid id,
                IUserRepository repo,
                CancellationToken ct) =>
            {
                var user = await repo.FindAsync(id, ct);
                return user is null ? Results.NotFound() : Results.Ok(user);
            });

            users.MapPost("/", async (CreateUserDto dto, IUserRepository repo, CancellationToken ct) =>
            {
                var user = await repo.CreateAsync(dto, ct);
                return Results.Created($"/api/v1/users/{user.Id}", user);
            });

            public sealed record CreateUserDto(string Email, string Name);
            """,
        ),
        text(
            "`Results.Ok`, `Results.NotFound` и `Results.Created` возвращают `IResult` и удобны "
            "в условных выражениях. Если тип ответа должен быть известен компилятору (для "
            "OpenAPI и для тестов), используйте `TypedResults`: `TypedResults.Ok(user)` "
            "возвращает `Ok<User>`, и сигнатура метода точно сообщает возможные ответы.\n\n"
            "Для ошибок принят формат ProblemDetails (RFC 7807): объект с полями `title`, "
            "`status`, `detail` и `type`. ASP.NET Core генерирует его автоматически для "
            "неперехваченных исключений при `AddProblemDetails()`, а `Results.Problem(...)` и "
            "`Results.ValidationProblem(...)` создают такой ответ явно. Единый формат избавляет "
            "клиентов и дежурных от сверки по каждой ручке. В `.CustomizeProblemDetails` "
            "удобно добавлять идентификатор трассы."
        ),
        example(
            "csharp",
            r"""
            builder.Services.AddProblemDetails(options =>
            {
                options.CustomizeProblemDetails = ctx =>
                {
                    ctx.ProblemDetails.Instance = $"{ctx.HttpContext.Request.Method} {ctx.HttpContext.Request.Path}";
                    ctx.ProblemDetails.Extensions["traceId"] = ctx.HttpContext.TraceIdentifier;
                };
            });

            // Ответ на ошибочный запрос (сокращённо):
            // HTTP/1.1 404 Not Found
            // Content-Type: application/problem+json
            // { "type":"https://tools.ietf.org/html/rfc9110#section-15.5.5",
            //   "title":"Not Found", "status":404, "instance":"GET /api/v1/users/17",
            //   "traceId":"0HN7GQ2K3BC9P:00000002" }
            """,
        ),
        heading("EF Core: производительность прежде всего"),
        text(
            "EF Core удобен, но именно он чаще всего делает сервис медленным. Три причины "
            "покрывают большинство случаев. Первая — проблема N+1: код загружает список "
            "сущностей и для каждой обращается к навигационному свойству, а каждый доступ "
            "порождает отдельный SQL-запрос. Вторая — декартово произведение при "
            "жадной загрузке нескольких коллекций через `Include`. Третья — лишнее "
            "отслеживание изменений для данных, которые не меняются.\n\n"
            "Решение N+1 — загружать нужное заранее. Для связей многие-к-одному хорошо "
            "работает `Include`. Для больших коллекций жадная загрузка порождает широкий join "
            "с дублями — тогда лучше `AsSplitQuery()` либо проекция в набор идентификаторов."
        ),
        example(
            "csharp",
            r"""
            // Проблема N+1: 1 запрос за заказами + N запросов на клиентов.
            var orders = await db.Orders.ToListAsync(ct);
            foreach (var order in orders)
                Console.WriteLine(order.Customer.Name);   // каждый раз SELECT в базу

            // Вариант 1: проекция — один запрос, только нужные поля.
            var rows = await db.Orders
                .Select(o => new { o.Id, o.Total, Customer = o.Customer.Name })
                .ToListAsync(ct);

            // Вариант 2: отдельный запрос по собранным идентификаторам.
            var customerIds = await db.Orders.Select(o => o.CustomerId).Distinct().ToListAsync(ct);
            var names = await db.Customers
                .Where(c => customerIds.Contains(c.Id))
                .ToDictionaryAsync(c => c.Id, c => c.Name, ct);
            """,
        ),
        text(
            "Проекция через `Select` — самый эффективный приём: SQL выбирает только нужные "
            "колонки, а анонимный тип не является сущностью, поэтому не отслеживается. Вариант "
            "с двумя запросами оправдан, когда проекция слишком сложна. Оба варианта дают два "
            "обращения в базу вместо тысячи.\n\n"
            "Для чтения ради отображения добавляйте `AsNoTracking()`. Отслеживание делает "
            "снимок каждого объекта и сравнивает его при `SaveChanges` — для тысяч строк это "
            "ощутимая стоимость и память. Если одинаковые сущности достижимы разными путями, "
            "берите `AsNoTrackingWithIdentityResolution()`, чтобы EF Core не создал дубли."
        ),
        example(
            "csharp",
            r"""
            // Пул контекстов вместо создания нового на каждый запрос.
            builder.Services.AddDbContextPool<AppDbContext>(options =>
                options.UseNpgsql(connectionString)
                       .UseQuerySplittingBehavior(QuerySplittingBehavior.SplitQuery));

            // Чтение без отслеживания.
            var active = await db.Customers
                .AsNoTracking()
                .Where(c => c.IsActive)
                .OrderBy(c => c.Name)
                .Select(c => new { c.Id, c.Name })
                .ToListAsync(ct);

            // Две коллекции в одной жадной загрузке дают дубли строк;
            // AsSplitQuery выполняет несколько запросов вместо широкого join.
            var customers = await db.Customers
                .Include(c => c.Orders)
                .ThenInclude(o => o.Items)
                .AsSplitQuery()
                .ToListAsync(ct);

            // Скомпилированный запрос: разбор дерева выражений происходит один раз.
            private static readonly Func<AppDbContext, Guid, Task<Order?>> GetOrderById =
                EF.CompileAsyncQuery((AppDbContext ctx, Guid id) =>
                    ctx.Orders.AsNoTracking().FirstOrDefault(o => o.Id == id));

            var order = await GetOrderById(db, orderId);
            """,
        ),
        callout(
            "info",
            "Как увидеть SQL",
            "`options.LogTo(Console.WriteLine, LogLevel.Information)` в настройках контекста "
            "печатает реальные команды. Запустите проблемный сценарий в тесте или на "
            "разработке и посчитайте число строк `Executed DbCommand`: если на один "
            "HTTP-вызов их больше десяти — почти наверняка N+1.",
        ),
        text(
            "Перехватчики (interceptors) — механизм встраивания кода в моменты работы контекста: "
            "перед сохранением, при выполнении команды, при открытии соединения. Классический "
            "пример — аудит: `SaveChangesInterceptor` проходит по "
            "`ChangeTracker.Entries<IAuditable>()` и проставляет дату и автора. Код аудита "
            "живёт в одном месте, а регистрируется через `AddInterceptors` с зависимостями "
            "из контейнера."
        ),
        heading("HTTP-клиенты, gRPC и SignalR"),
        text(
            "Когда сервис вызывает другие сервисы, обычный выбор — `HttpClient`. Создавать его "
            "на каждый вызов нельзя: каждый экземпляр держит пул соединений, и новый означает "
            "новое TCP-соединение и TLS. Один статический экземпляр тоже плох: он не подхватит "
            "смену DNS, а его заголовки небезопасно менять из потоков. Правильный путь — "
            "`IHttpClientFactory`, который управляет пулами хендлеров."
        ),
        example(
            "csharp",
            r"""
            builder.Services.AddHttpClient<GitHubClient>(client =>
            {
                client.BaseAddress = new Uri("https://api.github.com/");
                client.DefaultRequestHeaders.UserAgent.ParseAdd("Shop/1.0");
            })
            .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
            {
                PooledConnectionLifetime = TimeSpan.FromMinutes(10),
                EnableMultipleHttp2Connections = true,
            })
            .AddStandardResilienceHandler();   // таймауты, ретраи, circuit breaker

            public sealed class GitHubClient(HttpClient http)
            {
                public async Task<string> GetRepoAsync(string owner, string name, CancellationToken ct)
                {
                    using var response = await http.GetAsync($"repos/{owner}/{name}", ct);
                    response.EnsureSuccessStatusCode();
                    return await response.Content.ReadAsStringAsync(ct);
                }
            }
            """,
        ),
        text(
            "`AddStandardResilienceHandler` из пакета `Microsoft.Extensions.Http.Resilience` "
            "добавляет таймаут на попытку, ограниченное число ретраев с экспоненциальной "
            "задержкой и защиту от перегрузки. Ретраи безопасны только для идемпотентных "
            "операций: повторять GET или PUT можно, а POST, который списал деньги, — только "
            "с ключом идемпотентности.\n\n"
            "gRPC — транспорт для другого случая. Контракт описывается в `.proto`, клиент и "
            "сервер генерируются автоматически, данные идут в бинарном Protobuf поверх HTTP/2: "
            "компактнее JSON, а строгая схема ловит несовместимость на сборке. gRPC подходит "
            "для внутренних вызовов и поддерживает серверный, клиентский и двунаправленный стрим."
        ),
        example(
            "csharp",
            r"""
            // Сервер: наследник сгенерированного базового класса.
            public sealed class CatalogService(ICatalogRepository repo)
                : Catalog.CatalogBase
            {
                public override async Task<ItemReply> GetItem(ItemRequest request, ServerCallContext context)
                {
                    var item = await repo.FindAsync(Guid.Parse(request.Id), context.CancellationToken);
                    if (item is null)
                        throw new RpcException(new Status(StatusCode.NotFound, "Товар не найден"));

                    return new ItemReply { Id = item.Id.ToString(), Title = item.Title, Price = (double)item.Price };
                }

                public override async Task ListItems(Empty request,
                    IServerStreamWriter<ItemReply> stream, ServerCallContext context)
                {
                    await foreach (var item in repo.StreamAllAsync(context.CancellationToken))
                        await stream.WriteAsync(new ItemReply { Id = item.Id.ToString(), Title = item.Title });
                }
            }

            app.MapGrpcService<CatalogService>();

            // Клиент: канал создаётся один раз и переиспользуется.
            using var channel = GrpcChannel.ForAddress("https://catalog:8081");
            var client = new Catalog.CatalogClient(channel);
            var item = await client.GetItemAsync(new ItemRequest { Id = id.ToString() });
            """,
        ),
        text(
            "SignalR решает задачу, о которой HTTP-запрос-ответ ничего не знает: сервер сам "
            "отправляет данные клиенту, когда они появились. Хаб — класс, методы которого "
            "вызываются с клиента, а `Clients` позволяет отправить сообщение одному соединению "
            "(`Caller`), группе (`Group`) или всем (`All`). Транспорт выбирается автоматически: "
            "WebSocket, затем Server-Sent Events или длинные опросы. При масштабировании нужен "
            "общий бэкплейн вроде Redis, иначе клиент на узле A не получит сообщение с узла B."
        ),
        example(
            "csharp",
            r"""
            public sealed class ChatHub : Hub
            {
                public Task JoinRoom(string room) => Groups.AddToGroupAsync(Context.ConnectionId, room);

                public Task Send(string room, string user, string message) =>
                    Clients.Group(room).SendAsync("ReceiveMessage", user, message);

                public override async Task OnConnectedAsync()
                {
                    await Clients.Caller.SendAsync("Connected", Context.ConnectionId);
                    await base.OnConnectedAsync();
                }
            }

            builder.Services.AddSignalR().AddStackExchangeRedis(redisConnection);
            app.MapHub<ChatHub>("/hub/chat");
            """,
        ),
        table(
            ["Транспорт", "Формат", "Когда подходит", "Ограничения"],
            [
                ["HTTP + JSON", "Текст JSON", "внешний API, интеграции с браузером", "больше накладных расходов, слабая схема"],
                ["gRPC", "Protobuf, HTTP/2", "межсервисные вызовы, потоковая передача, строгий контракт", "браузер требует gRPC-Web, нужен прокси"],
                ["SignalR", "по WebSocket и др.", "обновления в реальном времени, чаты, уведомления", "нужен бэкплейн при масштабировании"],
            ],
        ),
        heading("Фоновые службы и распределённые блокировки"),
        text(
            "Фоновая служба в .NET — класс, зарегистрированный через `AddHostedService`. "
            "`BackgroundService` даёт метод `ExecuteAsync(CancellationToken stoppingToken)`, "
            "вызываемый при старте, а токен отменяется при остановке. `IHostedService` нужен, "
            "когда требуется разное поведение в `StartAsync` и `StopAsync`.\n\n"
            "Время жизни службы — singleton, поэтому scoped-сервисы вроде `DbContext` берут "
            "через `IServiceScopeFactory`: на каждой итерации создаётся новый scope. Второе "
            "правило: исключение не должно выходить из `ExecuteAsync`, иначе фоновая задача "
            "остановится. Ошибку обрабатывают, логируют и продолжают цикл."
        ),
        example(
            "csharp",
            r"""
            public sealed class OrderProcessingService(
                IServiceScopeFactory factory,
                ILogger<OrderProcessingService> logger) : BackgroundService
            {
                private static readonly TimeSpan Interval = TimeSpan.FromSeconds(30);

                protected override async Task ExecuteAsync(CancellationToken stoppingToken)
                {
                    using var timer = new PeriodicTimer(Interval);
                    try
                    {
                        while (await timer.WaitForNextTickAsync(stoppingToken))
                        {
                            try
                            {
                                using var scope = factory.CreateScope();
                                var processor = scope.ServiceProvider.GetRequiredService<IOrderProcessor>();
                                int processed = await processor.ProcessPendingAsync(stoppingToken);
                                logger.LogInformation("Обработано заказов: {Count}", processed);
                            }
                            catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
                            {
                                break;
                            }
                            catch (Exception ex)
                            {
                                logger.LogError(ex, "Итерация обработки заказов завершилась ошибкой");
                            }
                        }
                    }
                    catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
                    {
                        // ожидаемая остановка хоста
                    }
                }
            }

            builder.Services.AddHostedService<OrderProcessingService>();
            """,
        ),
        text(
            "`PeriodicTimer` удобнее `Task.Delay` в цикле: он не накапливает сдвиг и "
            "завершается по токену. Обратите внимание на порядок обработчиков исключений: "
            "сначала ветка отмены, потом общий `catch` для ошибок итерации, иначе остановка "
            "хоста попадёт в лог как авария.\n\n"
            "В нескольких экземплярах каждая фоновая служба запускается на каждом из них, и "
            "ежедневный отчёт выполнится столько раз, сколько экземпляров. Решение — "
            "распределённая блокировка вне процесса. В Redis она строится на команде "
            "`SET key value NX PX ms`: ключ ставится только если его нет, с временем жизни. "
            "Снимать блокировку нужно атомарно и только своим токеном — через скрипт Lua."
        ),
        example(
            "csharp",
            r"""
            public sealed class DistributedLockService(IDatabase redis)
            {
                // Атомарно снимает блокировку, только если владелец совпадает.
                private const string ReleaseScript =
                    "if redis.call('get', KEYS[1]) == ARGV[1] then " +
                    "return redis.call('del', KEYS[1]) else return 0 end";

                public async Task<IDisposable?> TryAcquireAsync(string name, TimeSpan ttl)
                {
                    string key = $"lock:{name}";
                    string token = Guid.NewGuid().ToString("N");

                    bool acquired = await redis.StringSetAsync(key, token, ttl, When.NotExists);
                    return acquired ? new Handle(redis, key, token, ReleaseScript) : null;
                }

                private sealed class Handle(IDatabase redis, string key, string token, string script) : IDisposable
                {
                    public void Dispose() =>
                        redis.ScriptEvaluate(script, new RedisKey[] { key }, new RedisValue[] { token });
                }
            }
            """,
        ),
        callout(
            "danger",
            "Время жизни блокировки — тоже контракт",
            "Если задание выполняется дольше TTL блокировки, второй экземпляр получит её и "
            "работа пойдёт дважды. Задавайте TTL с запасом и продлевайте его, если операция "
            "может быть долгой. Снятие блокировки простым `DEL` без проверки токена "
            "освободит чужую блокировку.",
        ),
        heading("Наблюдаемость: логи, метрики и трассы"),
        text(
            "Наблюдаемость держится на трёх опорах. Логи отвечают, что произошло в этом "
            "конкретном случае. Метрики — сколько запросов, какова задержка, сколько ошибок "
            "в целом. Трассы (distributed tracing) — через какие сервисы прошёл один запрос "
            "и где он потратил время. Без всех трёх разбор инцидента превращается в догадки.\n\n"
            "Структурированные логи не собирайте строкой вручную. `ILogger` принимает шаблон "
            "с именованными дырами: `logger.LogInformation(\"Заказ {OrderId} создан\", id)` "
            "записывает поле `OrderId` отдельно от текста, и по нему можно фильтровать. "
            "`BeginScope` добавляет поля ко всем сообщениям внутри блока."
        ),
        example(
            "csharp",
            r"""
            public sealed class OrderService(ILogger<OrderService> logger, IOrderRepository repo)
            {
                public async Task<Order> CreateAsync(CreateOrderDto dto, CancellationToken ct)
                {
                    Guid orderId = Guid.NewGuid();
                    using var scope = logger.BeginScope(new Dictionary<string, object>
                    {
                        ["CustomerId"] = dto.CustomerId,
                        ["OrderId"] = orderId,
                    });

                    logger.LogInformation("Создание заказа на сумму {Amount}", dto.Amount);

                    try
                    {
                        var order = await repo.AddAsync(orderId, dto, ct);
                        logger.LogInformation("Заказ создан");
                        return order;
                    }
                    catch (Exception ex)
                    {
                        logger.LogError(ex, "Не удалось создать заказ");
                        throw;
                    }
                }
            }
            """,
        ),
        text(
            "Метрики в .NET пишутся через `System.Diagnostics.Metrics.Meter`. Экземпляр лучше "
            "получать из `IMeterFactory`: фабрика изолирует счётчики и правильно освобождает "
            "ресурсы. Три инструмента: `Counter<T>` для монотонно растущих значений "
            "(созданные заказы), `Histogram<T>` для распределений (сумма заказа), "
            "`UpDownCounter<T>` для величин, которые растут и падают (активные заказы). "
            "Не заменяйте счётчиком «текущее значение» — агрегация в бэкенде будет неверной."
        ),
        example(
            "csharp",
            r"""
            using System.Diagnostics.Metrics;

            public sealed class OrderMetrics
            {
                private readonly Counter<long> _created;
                private readonly Histogram<double> _value;
                private readonly UpDownCounter<long> _active;

                public OrderMetrics(IMeterFactory factory)
                {
                    var meter = factory.Create("Shop.Orders");
                    _created = meter.CreateCounter<long>("orders.created", unit: "{order}");
                    _value = meter.CreateHistogram<double>("orders.value", unit: "USD");
                    _active = meter.CreateUpDownCounter<long>("orders.active", unit: "{order}");
                }

                public void OnCreated(decimal value)
                {
                    _created.Add(1);
                    _value.Record((double)value);
                    _active.Add(1);
                }

                public void OnCompleted() => _active.Add(-1);
            }
            """,
        ),
        text(
            "Трассы строятся на `ActivitySource` из `System.Diagnostics`. Каждый "
            "`StartActivity` создаёт span: операцию с именем, длительностью и тегами. Если "
            "активность уже есть в контексте (например, со входящего запроса), новая становится "
            "её дочерней, и получается дерево. ASP.NET Core, HttpClient и EF Core создают "
            "активности сами; собственный источник нужен для бизнес-операций."
        ),
        example(
            "csharp",
            r"""
            using System.Diagnostics;

            public static class ShopDiagnostics
            {
                public const string SourceName = "Shop.Orders";
                public static readonly ActivitySource Source = new(SourceName);
            }

            public decimal PriceOrder(Order order)
            {
                using var activity = ShopDiagnostics.Source.StartActivity("PriceOrder");
                activity?.SetTag("order.id", order.Id);
                activity?.SetTag("order.items", order.Items.Count);

                try
                {
                    decimal total = order.Items.Sum(i => i.Price * i.Quantity);
                    activity?.SetTag("order.total", (double)total);
                    return total;
                }
                catch (Exception ex)
                {
                    activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
                    throw;
                }
            }

            builder.Services.AddOpenTelemetry()
                .ConfigureResource(r => r.AddService("shop-api"))
                .WithTracing(t => t
                    .AddSource(ShopDiagnostics.SourceName)
                    .AddAspNetCoreInstrumentation()
                    .AddHttpClientInstrumentation()
                    .AddEntityFrameworkCoreInstrumentation()
                    .AddOtlpExporter())
                .WithMetrics(m => m
                    .AddMeter("Shop.Orders")
                    .AddAspNetCoreInstrumentation()
                    .AddRuntimeInstrumentation()
                    .AddOtlpExporter());
            """,
        ),
        text(
            "OTLP — открытый протокол экспорта телеметрии. Приложение отправляет трассы, "
            "метрики и логи на коллектор (Jaeger, Tempo, Grafana Agent), а не в каждую систему "
            "хранения напрямую: коллектор разводит данные по бэкендам, и приложение знает один "
            "адрес.\n\n"
            "Логи тоже отправляйте по OTLP или в JSON: тогда строка лога связывается с трассой "
            "по `TraceId`, и из span можно открыть конкретные записи запроса."
        ),
        heading("Проверки работоспособности"),
        text(
            "Проверки работоспособности (health checks) — эндпоинты, по которым оркестратор "
            "понимает, живой ли экземпляр и готов ли он принимать трафик. Это две разные "
            "вещи, и путать их опасно.\n\n"
            "Liveness отвечает, нужно ли перезапустить процесс: проверяется только сам процесс. "
            "Readiness отвечает, можно ли отправлять трафик: сюда входят база, кэш, внешние "
            "API. Если readiness учитывает недоступную базу, экземпляр снимается с баланса, "
            "но не перезапускается — база починится сама, а перезапуск лишь добавит проблем."
        ),
        example(
            "csharp",
            r"""
            builder.Services.AddHealthChecks()
                .AddDbContextCheck<AppDbContext>("db", tags: new[] { "ready" })
                .AddNpgSql(connectionString, tags: new[] { "ready" })
                .AddRedis(redisConnection, tags: new[] { "ready" })
                .AddCheck<CustomHealthCheck>("custom", tags: new[] { "ready" });

            // Liveness: проверяем только процесс.
            app.MapHealthChecks("/health/live", new HealthCheckOptions
            {
                Predicate = _ => false,
            });

            // Readiness: проверяем зависимости.
            app.MapHealthChecks("/health/ready", new HealthCheckOptions
            {
                Predicate = check => check.Tags.Contains("ready"),
            });

            public sealed class CustomHealthCheck : IHealthCheck
            {
                public Task<HealthCheckResult> CheckHealthAsync(
                    HealthCheckContext context, CancellationToken ct = default)
                {
                    bool ok = File.Exists("/var/lib/shop/catalog.lock");
                    return Task.FromResult(ok
                        ? HealthCheckResult.Healthy("Каталог готов")
                        : HealthCheckResult.Degraded("Каталог ещё загружается"));
                }
            }
            """,
        ),
        text(
            "Предикат `_ => false` в liveness намеренный: если проверок нет, эндпоинт отвечает "
            "успехом, пока процесс способен обработать HTTP-запрос. `Degraded` — промежуточный "
            "результат: экземпляр работоспособен, но не оптимален. Порог задаётся в Kubernetes: "
            "`livenessProbe` идёт на `/health/live`, `readinessProbe` — на `/health/ready`."
        ),
        callout(
            "info",
            "Идентификатор корреляции",
            "Через все слои — HTTP, gRPC, фоновые задачи — прокиньте идентификатор запроса. "
            "ASP.NET Core уже создаёт `TraceIdentifier` и заголовок `traceparent` по "
            "стандарту W3C; добавьте его в логи и в ProblemDetails, и вы сможете связать "
            "жалобу пользователя с конкретной строкой лога.",
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["`UseAuthorization` до `UseAuthentication`", "Пользователь не определён, всё отвечает 401", "Сначала аутентификация, потом авторизация"],
                ["`DbContext` в конструкторе middleware или BackgroundService", "Captive dependency: один контекст на всё приложение", "Брать из `RequestServices` или через `IServiceScopeFactory`"],
                ["`Include` двух коллекций без `AsSplitQuery`", "Декартово произведение: десятки копий строк", "`AsSplitQuery()` или проекция через `Select`"],
                ["`AsNoTracking` не указан для чтения", "Лишняя память и время на ChangeTracker", "`AsNoTracking()` для отображаемых данных"],
                ["`new HttpClient()` на каждый вызов", "Утечка портов и сокетов", "`AddHttpClient` / `IHttpClientFactory`"],
                ["Исключение выходит из `ExecuteAsync`", "Фоновая служба молча завершается", "Ловить исключение внутри цикла и логировать"],
                ["Readiness проверяет базу на liveness", "Перезапуски при недоступной базе", "Отдельные эндпоинты `/health/live` и `/health/ready`"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания рассчитаны на консольный .NET-проект с локальной инфраструктурой в "
            "Docker (PostgreSQL и Redis). Запускайте `dotnet run` в конфигурации Development, "
            "чтобы видеть запросы EF Core.",
        ),
        numbered(
            "Конвейер: создайте Minimal API с `/health/live` и `/health/ready`, поставьте логирующий middleware, возвращающий заголовок `X-Trace-Id`, и убедитесь, что идентификатор виден в ответе и в логе.",
            "Minimal API: реализуйте группу `/api/v1/items` с фильтром проверки DTO, `TypedResults` и ProblemDetails для ошибок. Проверьте ответы на пустое имя и на несуществующий идентификатор.",
            "EF Core: воспроизведите проблему N+1 на заказах и клиентах, посчитайте число SQL-запросов в логе, затем перепишите код через проекцию и сравните число запросов.",
            "Фоновая служба: напишите `BackgroundService` с `PeriodicTimer`, пересоздающий scope на каждой итерации, и намеренно сломайте одну итерацию, чтобы убедиться, что цикл продолжается.",
            "Наблюдаемость: создайте `ActivitySource` для операции `PriceOrder`, добавьте счётчик созданных заказов и экспорт в консольный экспортёр OpenTelemetry; проверьте, что тег суммы попадает в трассу.",
        ),
        text("Ожидаемый формат вывода из первого задания:"),
        example(
            "text",
            r"""
            GET /health/ready -> 200 OK
            X-Trace-Id: 0HN7GQ2K3BC9P:00000007
            info: Shop.Pipeline[0]
                  GET /health/ready завершён за 3 мс, trace 0HN7GQ2K3BC9P:00000007
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 3",
            "Скомпилированная проекция через `Select` даёт один SELECT с join-подобной формой "
            "и не создаёт сущностей. Сравнивайте не только время, но и количество строк "
            "`Executed DbCommand` в логе — число запросов устойчивее к задержкам базы.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему `UseAuthentication` должен стоять до `UseAuthorization`?",
            "Что такое проблема N+1 и два способа её устранить?",
            "В каких случаях `AsSplitQuery` лучше одного запроса с `Include`?",
            "Почему в фоновой службе нельзя получать `DbContext` в конструкторе?",
            "Чем отличается проверка liveness от readiness и почему их нельзя перепутать?",
        ),
        heading("Ответы", 3),
        numbered(
            "Аутентификация заполняет `HttpContext.User`, а авторизация проверяет политики именно по этому принципалу. Если авторизация выполнится раньше, пользователь будет пустым, и валидные запросы получат 401.",
            "N+1 — это N дополнительных запросов, по одному на каждую сущность при обращении к навигационному свойству. Устраняется проекцией через `Select` или предварительной загрузкой нужных данных отдельным запросом по набору идентификаторов.",
            "Когда несколько коллекций загружаются одной жадной загрузкой: широкий join размножает строки и передаёт дубли. `AsSplitQuery` выполняет несколько запросов и собирает результат в памяти, сохраняя согласованность через единый снимок.",
            "Фоновая служба — singleton, а `DbContext` — scoped. Захват scoped-сервиса в singleton (captive dependency) означает, что один контекст используется всеми итерациями и потоками, его трекер растёт, а данные устаревают. Нужен `IServiceScopeFactory.CreateScope()` на каждой итерации.",
            "Liveness отвечает, нужно ли перезапустить процесс, и не должна зависеть от базы. Readiness отвечает, можно ли отправлять трафик, и включает проверки зависимостей. Readiness на liveness вызовет перезапуски при недоступной базе, что только ухудшит ситуацию.",
        ),
        heading("Итоги"),
        bullets(
            "Конвейер ASP.NET Core: исключения первыми, статика до маршрутизации, маршрутизация, затем аутентификация, затем авторизация. Порядок — часть поведения и безопасности.",
            "Minimal APIs опираются на связывание параметров, группы маршрутов, фильтры эндпоинтов и `TypedResults`; ошибки отдавайте в формате ProblemDetails.",
            "EF Core: `AsNoTracking` для чтения, проекции вместо `Include`, `AsSplitQuery` при нескольких коллекциях, `AddDbContextPool`, `EF.CompileAsyncQuery` для горячих запросов, перехватчики для аудита.",
            "`HttpClient` — только через `IHttpClientFactory` с политиками устойчивости; gRPC для межсервисных контрактов и потоков, SignalR для доставки обновлений клиентам.",
            "Фоновые службы: singleton, `IServiceScopeFactory`, `PeriodicTimer`, исключения ловятся внутри цикла, при масштабировании — распределённая блокировка с TTL и проверкой токена.",
            "Наблюдаемость: структурированные логи с полями, `Counter`/`Histogram`/`UpDownCounter` через `IMeterFactory`, `ActivitySource` для бизнес-операций и экспорт по OTLP.",
            "Health checks: liveness проверяет процесс, readiness — зависимости; `/health/live` и `/health/ready` — разные эндпоинты с разными предикатами.",
        ),
        heading("Что дальше"),
        text(
            "Следующий урок — «Тестирование и надёжность»: модульные и интеграционные тесты "
            "на `WebApplicationFactory`, тестовые контейнеры для базы, детерминированные "
            "тесты времени и сети. Метрики, трассы и health checks из этого урока станут "
            "там основой проверок и панелей мониторинга."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Документация ASP.NET Core — learn.microsoft.com/aspnet/core",
            "Minimal APIs: связывание параметров и фильтры — learn.microsoft.com/aspnet/core/fundamentals/minimal-apis",
            "Производительность EF Core — learn.microsoft.com/ef/core/performance",
            "OpenTelemetry .NET — opentelemetry.io/docs/languages/net",
            "gRPC в .NET — learn.microsoft.com/aspnet/core/grpc",
            "SignalR: масштабирование и бэкплейн — learn.microsoft.com/aspnet/core/signalr/scale",
            "Health checks в ASP.NET Core — learn.microsoft.com/aspnet/core/host-and-deploy/health-checks",
        ),
    ],
}
