"""Урок 2.11 курса C#: проект — многослойное приложение."""

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
    "topic_order": 11,
    "name": "2.11. Проект: многослойное приложение",
    "slug": "csharp-2-11-проект-многослойное-приложение",
    "short_description": (
        "Собираем заказы в полноценный сервис: слои Domain, Application, Infrastructure "
        "и Api, результат-объекты вместо исключений, сквозные фильтры, тесты и проверка "
        "зависимостей между сборками."
    ),
    "topic_name": "Проект: многослойное приложение",
    "topic_description": (
        "Итоговый проект среднего уровня: разделение решения на слои по Clean Architecture, "
        "правила зависимостей между проектами, доменная модель с инвариантами, обработчики "
        "сценариев, доступ к данным через EF Core, Minimal API с middleware обработки ошибок "
        "и архитектурные тесты."
    ),
    "learning_objectives": [
        "Раскладывать решение на слои Domain, Application, Infrastructure и Api и объяснять роль каждого",
        "Соблюдать правило зависимостей: внутренние слои не знают о внешних",
        "Моделировать сущность с инвариантами и доменными исключениями в слое Domain",
        "Отделять сценарии (команды и запросы) от контроллеров через обработчики и DTO",
        "Подключать EF Core, репозитории и строку подключения в слое Infrastructure",
        "Собирать Minimal API с групповыми эндпоинтами и глобальной обработкой ошибок",
        "Писать модульные и архитектурные тесты, проверяющие границы между слоями",
        "Готовить приложение к запуску: конфигурация, логирование, health check, Docker",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "csharp",
        "clean architecture",
        "слои",
        "asp.net core",
        "ef core",
        "тесты",
    ],
    "starter_code": code(
        r"""
        using System;
        using System.Collections.Generic;

        namespace LayeredDemo;

        public enum OrderStatus { Pending, Confirmed, Cancelled }

        public sealed class Order
        {
            private readonly List<OrderLine> _lines = new();

            public Order(Guid id, string customer)
            {
                Id = id;
                Customer = customer;
                Status = OrderStatus.Pending;
            }

            public Guid Id { get; }
            public string Customer { get; }
            public OrderStatus Status { get; private set; }
            public IReadOnlyList<OrderLine> Lines => _lines.AsReadOnly();

            public decimal Total
            {
                get
                {
                    decimal sum = 0m;
                    foreach (var line in _lines)
                        sum += line.Price * line.Quantity;
                    return sum;
                }
            }

            public void AddLine(string sku, int quantity, decimal price)
            {
                if (Status != OrderStatus.Pending)
                    throw new InvalidOperationException("Заказ можно менять только в статусе Pending.");
                if (quantity <= 0)
                    throw new ArgumentOutOfRangeException(nameof(quantity));
                _lines.Add(new OrderLine(sku, quantity, price));
            }

            public void Confirm()
            {
                if (_lines.Count == 0)
                    throw new InvalidOperationException("Пустой заказ нельзя подтвердить.");
                Status = OrderStatus.Confirmed;
            }
        }

        public sealed record OrderLine(string Sku, int Quantity, decimal Price);

        public static class Program
        {
            public static void Main()
            {
                var order = new Order(Guid.Parse("c0a80101-0000-0000-0000-000000000001"), "Иван");
                order.AddLine("KEYBOARD-01", 2, 2500m);
                order.AddLine("MOUSE-07", 1, 1200m);
                Console.WriteLine($"Строк: {order.Lines.Count}, сумма: {order.Total}");
                order.Confirm();
                Console.WriteLine($"Статус: {order.Status}");
            }
        }
        """,
    ),
    "hints": [
        "Если слою Domain понадобилось пространство имён Microsoft.EntityFrameworkCore, значит правило зависимостей уже нарушено: перенесите код в Infrastructure.",
        "Интерфейс репозитория объявляется в Application, а реализация на EF Core живёт в Infrastructure. Регистрация в DI связывает одно с другим без ссылки внутренних слоёв на внешние.",
        "Обработчик сценария возвращает результат (успех или ошибка), а не бросает исключение для ожидаемых ситуаций: «не найдено» и «не пройдена валидация» — это нормальные ответы.",
        "Архитектурный тест на ссылки сборок дешевле любого code review: как только кто-то добавит using из внешнего слоя, сборка тестов упадёт.",
    ],
    "content": [
        text(
            "До этого момента код каждого урока жил в одном файле или в одной сборке. "
            "Так удобно учиться, но так не живут настоящие сервисы: хранилище меняется, "
            "HTTP-слой переписывают на новую версию библиотеки, а бизнес-правила должны "
            "оставаться нетронутыми. Если всё перемешано, любая правка в одном месте "
            "ломает другое, а проверить правило без запуска базы данных невозможно.\n\n"
            "Многослойное приложение решает эту проблему делением кода на части с чёткими "
            "обязанностями и направленными зависимостями. Внутренние слои описывают предметную "
            "область и сценарии, внешние — технологии: базу данных, HTTP, логирование. "
            "В итоге доменную логику можно тестировать без сервера, а замену базы данных "
            "свести к переписыванию одного слоя.\n\n"
            "Это итоговый проект уровня. Мы соберём сервис заказов из четырёх проектов "
            "по образцу Clean Architecture: Domain, Application, Infrastructure и Api, "
            "опираясь на классы, асинхронность, доступ к данным и тесты из уроков 2.2–2.10."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "раскладывать решение на слои Domain, Application, Infrastructure и Api и объяснять роль каждого;",
            "соблюдать правило зависимостей, при котором внутренние слои не знают о внешних;",
            "моделировать сущность с инвариантами и доменными исключениями в слое Domain;",
            "отделять сценарии (команды и запросы) от HTTP-слоя через обработчики и DTO;",
            "подключать EF Core, репозитории и строку подключения в слое Infrastructure;",
            "собирать Minimal API с групповыми эндпоинтами и глобальной обработкой ошибок;",
            "писать модульные и архитектурные тесты, которые проверяют границы между слоями;",
            "готовить приложение к запуску: конфигурацию, логирование, health check и Docker.",
        ),
        heading("Зачем делить решение на слои"),
        text(
            "Слой (layer) — это набор типов с общей обязанностью и одинаковыми правилами "
            "зависимостей. Слои не обязаны совпадать с физическими проектами `.csproj`, "
            "но на практике их выносят в отдельные сборки: тогда компилятор сам не даст "
            "внутреннему слою сослаться на внешний. Ссылка проекта в `.csproj` — жёсткая, "
            "проверяемая компилятором граница, а не соглашение в документации.\n\n"
            "Сравните два подхода на задаче «создать заказ». В «слоёном пироге» "
            "контроллер напрямую вызывает `DbContext` и содержит проверки товаров; "
            "в слоистой архитектуре он лишь превращает HTTP-запрос в команду. "
            "Первое быстрее на первых ста строках, второе окупается на первых "
            "ста изменениях требований."
        ),
        table(
            ["Симптом", "Что происходит в слоёном коде", "Что происходит в коде со слоями"],
            [
                ["Новое правило цены", "Правка в контроллере, в фоновой задаче и в отчёте", "Правка только в сущности Domain"],
                ["Переезд с PostgreSQL на другую СУБД", "Правки по всему решению", "Меняется только Infrastructure"],
                ["Тест правила без базы", "Нужен поднятый сервер и данные", "Обычный модульный тест класса"],
                ["Новый интерфейс (gRPC, CLI)", "Логика дублируется", "Добавляется новый внешний слой"],
            ],
        ),
        callout(
            "info",
            "Правило зависимостей",
            "Зависимости направлены внутрь: Api знает Application и Infrastructure, "
            "Application знает Domain, Infrastructure знает Domain и интерфейсы Application, "
            "Domain не знает никого. Если стрелка развернулась наружу, слой перестал быть "
            "переиспользуемым и тестируемым отдельно.",
        ),
        heading("Структура решения"),
        text(
            "Типичное решение для такого проекта содержит папки `src` и `tests`. "
            "Четыре проекта исходного кода называют по слоям, а тестовые проекты "
            "повторяют деление: модульные тесты проверяют Domain и Application, "
            "интеграционные — Api вместе с Infrastructure, архитектурные — правила ссылок.\n\n"
            "Файл решения `MyApp.sln` объединяет проекты, а `Directory.Build.props` задаёт "
            "общие настройки: целевую платформу, включение анализаторов и nullable-контекст. "
            "Так повторяющиеся параметры не копируются в каждый `.csproj` вручную."
        ),
        example(
            "text",
            """
            MyApp.sln
            |-- src/
            |   |-- MyApp.Domain/           сущности, объекты-значения, доменные исключения
            |   |   |-- Entities/
            |   |   |-- Exceptions/
            |   |   `-- MyApp.Domain.csproj
            |   |-- MyApp.Application/      сценарии: команды, запросы, интерфейсы, DTO
            |   |   |-- Orders/
            |   |   |-- Common/
            |   |   `-- MyApp.Application.csproj
            |   |-- MyApp.Infrastructure/   EF Core, репозитории, внешние сервисы
            |   |   |-- Persistence/
            |   |   `-- MyApp.Infrastructure.csproj
            |   `-- MyApp.Api/              HTTP, DI, middleware, конфигурация
            |       |-- Endpoints/
            |       |-- Middleware/
            |       `-- Program.cs
            `-- tests/
                |-- MyApp.UnitTests/
                |-- MyApp.IntegrationTests/
                `-- MyApp.ArchitectureTests/
            """,
        ),
        text(
            "Проекты создают командами `dotnet new`, а ссылки между ними добавляют "
            "через `dotnet add reference`. Порядок ссылок повторяет правило зависимостей: "
            "Domain без ссылок, Application на Domain, Infrastructure на Domain и Application, "
            "Api на Application и Infrastructure."
        ),
        example(
            "bash",
            """
            dotnet new sln -n MyApp
            dotnet new classlib -n MyApp.Domain         -o src/MyApp.Domain
            dotnet new classlib -n MyApp.Application    -o src/MyApp.Application
            dotnet new classlib -n MyApp.Infrastructure -o src/MyApp.Infrastructure
            dotnet new web      -n MyApp.Api            -o src/MyApp.Api

            dotnet sln add src/MyApp.Domain src/MyApp.Application src/MyApp.Infrastructure src/MyApp.Api
            dotnet add src/MyApp.Application reference src/MyApp.Domain
            dotnet add src/MyApp.Infrastructure reference src/MyApp.Domain
            dotnet add src/MyApp.Infrastructure reference src/MyApp.Application
            dotnet add src/MyApp.Api reference src/MyApp.Application
            dotnet add src/MyApp.Api reference src/MyApp.Infrastructure
            """,
        ),
        text(
            "После этих команд сборка с нарушением направления (`Domain` ссылается "
            "на `Infrastructure`) просто не соберётся — это и проверяет `dotnet build`."
        ),
        example(
            "text",
            """
            $ dotnet build MyApp.sln
            Определение проектов для восстановления выполнено
            Все проекты актуальны для восстановления.

            MyApp.Domain -> /src/MyApp.Domain/bin/Debug/net8.0/MyApp.Domain.dll
            MyApp.Application -> /src/MyApp.Application/bin/Debug/net8.0/MyApp.Application.dll
            MyApp.Infrastructure -> /src/MyApp.Infrastructure/bin/Debug/net8.0/MyApp.Infrastructure.dll
            MyApp.Api -> /src/MyApp.Api/bin/Debug/net8.0/MyApp.Api.dll

            Сборка успешно завершена.
                0 Предупреждений
                0 Ошибок
            """,
        ),
        heading("Слой Domain: сущности и инварианты"),
        text(
            "Domain — сердце приложения. Здесь живут сущности (entity — объект с "
            "идентичностью, который сохраняется между изменениями), объекты-значения "
            "(value object — неизменяемое значение без собственной личности) "
            "и доменные исключения. У слоя нет внешних зависимостей.\n\n"
            "Инвариант — правило, которое должно выполняться всегда. Для заказа это "
            "«нельзя подтвердить пустой заказ» и «нельзя менять подтверждённый заказ». "
            "Если проверки живут внутри сущности, любое место программы, работающее "
            "с заказом, получает одинаковые гарантии — и HTTP-обработчик, и фоновая задача, "
            "и тест."
        ),
        example(
            "csharp",
            """
            namespace MyApp.Domain.Orders;

            public enum OrderStatus { Pending, Confirmed, Cancelled }

            public sealed class Order
            {
                private readonly List<OrderLine> _lines = new();

                private Order() { } // нужен EF Core для материализации

                private Order(Guid id, string customer)
                {
                    Id = id;
                    Customer = customer;
                    Status = OrderStatus.Pending;
                }

                public Guid Id { get; private set; }
                public string Customer { get; private set; } = "";
                public OrderStatus Status { get; private set; }
                public IReadOnlyList<OrderLine> Lines => _lines.AsReadOnly();

                public decimal Total
                {
                    get
                    {
                        decimal sum = 0m;
                        foreach (var line in _lines)
                            sum += line.Price * line.Quantity;
                        return sum;
                    }
                }

                public static Order Create(string customer, IEnumerable<OrderLineData> lines)
                {
                    if (string.IsNullOrWhiteSpace(customer))
                        throw new DomainException("CUSTOMER_REQUIRED", "Клиент обязателен.");

                    var order = new Order(Guid.NewGuid(), customer.Trim());
                    foreach (var line in lines)
                        order.AddLine(line.Sku, line.Quantity, line.Price);
                    return order;
                }

                public void AddLine(string sku, int quantity, decimal price)
                {
                    if (Status != OrderStatus.Pending)
                        throw new DomainException("ORDER_LOCKED", "Менять можно только новый заказ.");
                    if (quantity <= 0)
                        throw new DomainException("QUANTITY_INVALID", "Количество должно быть положительным.");
                    if (price < 0m)
                        throw new DomainException("PRICE_INVALID", "Цена не может быть отрицательной.");
                    _lines.Add(new OrderLine(sku, quantity, price));
                }

                public void Confirm()
                {
                    if (Status != OrderStatus.Pending)
                        throw new DomainException("ORDER_LOCKED", "Заказ уже не в статусе Pending.");
                    if (_lines.Count == 0)
                        throw new DomainException("ORDER_EMPTY", "Пустой заказ нельзя подтвердить.");
                    Status = OrderStatus.Confirmed;
                }
            }

            public sealed record OrderLine(string Sku, int Quantity, decimal Price);
            public sealed record OrderLineData(string Sku, int Quantity, decimal Price);
            """,
        ),
        text(
            "Разберём ключевые решения. Конструктор без параметров объявлен приватным: "
            "создавать заказ можно только через статический `Create`, где работают проверки. "
            "Список строк закрыт от внешнего изменения — снаружи виден только `IReadOnlyList`. "
            "Свойства со `private set` меняются лишь внутри сущности, поэтому статус "
            "невозможно выставить в обход метода `Confirm`.\n\n"
            "Доменное исключение — наследник `Exception` с машинным кодом ошибки. "
            "Код нужен, чтобы внешний слой превратил исключение в HTTP-ответ, не разбирая "
            "текст сообщения."
        ),
        example(
            "csharp",
            """
            namespace MyApp.Domain.Exceptions;

            public abstract class DomainException : Exception
            {
                protected DomainException(string code, string message) : base(message)
                {
                    Code = code;
                }

                public string Code { get; }
            }

            public sealed class OrderEmptyException : DomainException
            {
                public OrderEmptyException()
                    : base("ORDER_EMPTY", "Пустой заказ нельзя подтвердить.") { }
            }
            """,
        ),
        callout(
            "warning",
            "Domain не знает про EF Core",
            "Атрибуты `[Key]`, `[Table]`, `[Column]` из пространства имён EF Core "
            "в сущностях Domain — самая частая утечка технологии во внутренний слой. "
            "Настраивайте отображение отдельно в Infrastructure через `IEntityTypeConfiguration<T>`, "
            "а сущность оставляйте чистой.",
        ),
        heading("Слой Application: сценарии"),
        text(
            "Application описывает, что умеет приложение: «создать заказ», «получить заказ». "
            "Здесь нет SQL и HTTP — только координация. Сценарии разделяют на команды "
            "(изменяют состояние) и запросы (только читают). Такое разделение известно "
            "как CQRS — Command Query Responsibility Segregation, разделение обязанностей "
            "команд и запросов. В минимальном варианте это просто разные классы, "
            "а не отдельные базы данных, как в больших системах.\n\n"
            "Обработчик (handler) — класс с одним методом `Handle`, который принимает "
            "команду и выполняет шаги сценария: загрузить данные, вызвать методы домена, "
            "сохранить изменения. Обработчику нужны репозитории, поэтому он зависит "
            "от интерфейсов, а не от конкретных классов EF Core."
        ),
        example(
            "csharp",
            """
            namespace MyApp.Application.Orders;

            // DTO — объект передачи данных, удобный для внешнего слоя.
            public sealed record CreateOrderRequest(string Customer, IReadOnlyList<OrderLineDto> Lines);
            public sealed record OrderLineDto(string Sku, int Quantity, decimal Price);
            public sealed record OrderDto(Guid Id, string Customer, string Status, decimal Total);

            public sealed class CreateOrderCommand
            {
                public CreateOrderCommand(CreateOrderRequest request) => Request = request;
                public CreateOrderRequest Request { get; }
            }

            public sealed class CreateOrderHandler
            {
                private readonly IOrderRepository _orders;
                private readonly IUnitOfWork _unitOfWork;

                public CreateOrderHandler(IOrderRepository orders, IUnitOfWork unitOfWork)
                {
                    _orders = orders;
                    _unitOfWork = unitOfWork;
                }

                public async Task<OrderDto> HandleAsync(CreateOrderCommand command, CancellationToken ct)
                {
                    var data = command.Request.Lines
                        .Select(l => new OrderLineData(l.Sku, l.Quantity, l.Price));

                    var order = Order.Create(command.Request.Customer, data);
                    order.Confirm();

                    await _orders.AddAsync(order, ct);
                    await _unitOfWork.SaveChangesAsync(ct);

                    return new OrderDto(order.Id, order.Customer, order.Status.ToString(), order.Total);
                }
            }
            """,
        ),
        text(
            "Интерфейсы, которые нужны сценарию, объявляются рядом с ним. "
            "`IOrderRepository` описывает хранение заказов, `IUnitOfWork` — фиксацию "
            "изменений целиком. Application не знает, что за ними стоит EF Core: "
            "в тестах подставляется заглушка, в production — настоящий контекст."
        ),
        example(
            "csharp",
            """
            namespace MyApp.Application.Abstractions;

            public interface IOrderRepository
            {
                Task AddAsync(Order order, CancellationToken ct);
                Task<Order?> GetAsync(Guid id, CancellationToken ct);
            }

            public interface IUnitOfWork
            {
                Task<int> SaveChangesAsync(CancellationToken ct);
            }
            """,
        ),
        callout(
            "info",
            "Зачем интерфейс в Application, а реализация в Infrastructure",
            "Направление зависимости задаёт тот, кому нужна услуга. Сценарию нужен "
            "репозиторий, поэтому интерфейс объявлен в Application. Реализация опирается "
            "на конкретную технологию и потому лежит в Infrastructure. Это и есть "
            "инверсия зависимостей: внешний слой подстраивается под внутренний, а не наоборот.",
        ),
        heading("Слой Infrastructure: база и технологии"),
        text(
            "Infrastructure — единственное место, где живут конкретные технологии: "
            "EF Core, HTTP-клиенты, кэш, файловое хранилище, отправка почты. "
            "Если завтра PostgreSQL заменят на другую СУБД, правки будут именно здесь.\n\n"
            "Контекст базы данных наследует `DbContext` и реализует `IUnitOfWork`. "
            "Отображение сущностей настраивают классами `IEntityTypeConfiguration<T>`, "
            "которые EF Core находит автоматически. Так сущность Domain остаётся "
            "без атрибутов хранилища."
        ),
        example(
            "csharp",
            """
            using Microsoft.EntityFrameworkCore;
            using MyApp.Application.Abstractions;
            using MyApp.Domain.Orders;

            namespace MyApp.Infrastructure.Persistence;

            public sealed class AppDbContext : DbContext, IUnitOfWork
            {
                public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

                public DbSet<Order> Orders => Set<Order>();

                protected override void OnModelCreating(ModelBuilder model)
                {
                    model.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
                }
            }

            public sealed class OrderConfiguration : IEntityTypeConfiguration<Order>
            {
                public void Configure(Microsoft.EntityFrameworkCore.Metadata.Builders.EntityTypeBuilder<Order> builder)
                {
                    builder.HasKey(o => o.Id);
                    builder.Property(o => o.Customer).HasMaxLength(200).IsRequired();
                    builder.Property(o => o.Status).HasConversion<string>().HasMaxLength(20);
                    builder.OwnsMany(o => o.Lines, lines =>
                    {
                        lines.WithOwner().HasForeignKey("OrderId");
                        lines.Property(l => l.Price).HasPrecision(18, 2);
                    });
                    builder.Navigation(o => o.Lines).UsePropertyAccessMode(
                        Microsoft.EntityFrameworkCore.PropertyAccessMode.Field);
                }
            }
            """,
        ),
        text(
            "Репозиторий — тонкая обёртка над `DbSet`: он переводит язык предметной "
            "области в вызовы EF Core и не содержит бизнес-правил. Правило «нельзя "
            "подтвердить пустой заказ» остаётся в сущности, здесь его быть не должно."
        ),
        example(
            "csharp",
            """
            using Microsoft.EntityFrameworkCore;
            using MyApp.Application.Abstractions;
            using MyApp.Domain.Orders;

            namespace MyApp.Infrastructure.Persistence.Repositories;

            public sealed class OrderRepository : IOrderRepository
            {
                private readonly AppDbContext _db;

                public OrderRepository(AppDbContext db) => _db = db;

                public async Task AddAsync(Order order, CancellationToken ct)
                    => await _db.Orders.AddAsync(order, ct);

                public async Task<Order?> GetAsync(Guid id, CancellationToken ct)
                    => await _db.Orders.FirstOrDefaultAsync(o => o.Id == id, ct);
            }
            """,
        ),
        heading("Регистрация зависимостей"),
        text(
            "Композиционный корень (composition root) — место, где собирается всё "
            "приложение: классы связываются с интерфейсами. В ASP.NET Core это `Program.cs`, "
            "так как единственное место, знающее обо всех слоях, — самый внешний. "
            "DI-контейнер — встроенный механизм, который по запросу выдаёт объект "
            "вместе со всеми его зависимостями.\n\n"
            "Каждый слой предоставляет свой метод расширения `IServiceCollection`: "
            "`AddApplication` регистрирует обработчики, `AddInfrastructure` — контекст "
            "и репозитории. `Program.cs` вызывает их по порядку и не перечисляет десятки "
            "типов вручную."
        ),
        example(
            "csharp",
            """
            using Microsoft.Extensions.DependencyInjection;
            using MyApp.Application.Abstractions;
            using MyApp.Application.Orders;

            namespace MyApp.Application;

            public static class DependencyInjection
            {
                public static IServiceCollection AddApplication(this IServiceCollection services)
                {
                    services.AddScoped<CreateOrderHandler>();
                    services.AddScoped<GetOrderHandler>();
                    return services;
                }
            }
            """,
        ),
        example(
            "csharp",
            """
            using Microsoft.EntityFrameworkCore;
            using Microsoft.Extensions.Configuration;
            using Microsoft.Extensions.DependencyInjection;
            using MyApp.Application.Abstractions;

            namespace MyApp.Infrastructure;

            public static class DependencyInjection
            {
                public static IServiceCollection AddInfrastructure(
                    this IServiceCollection services, IConfiguration config)
                {
                    var connection = config.GetConnectionString("Default")
                        ?? throw new InvalidOperationException("Не задана строка подключения Default.");

                    services.AddDbContext<AppDbContext>(options =>
                        options.UseNpgsql(connection));
                    services.AddScoped<IUnitOfWork>(sp => sp.GetRequiredService<AppDbContext>());
                    services.AddScoped<IOrderRepository, OrderRepository>();

                    return services;
                }
            }
            """,
        ),
        callout(
            "warning",
            "Время жизни служб",
            "`Scoped` создаёт один экземпляр на HTTP-запрос, `Transient` — на каждое "
            "разрешение, `Singleton` — один на приложение. Нельзя внедрять `Scoped` "
            "(`DbContext`) в `Singleton`: контейнер выбросит исключение "
            "`Cannot consume scoped service`, потому что контекст нельзя переиспользовать "
            "между параллельными запросами.",
        ),
        heading("Слой Api: HTTP и обработка ошибок"),
        text(
            "Api отвечает за протокол: маршруты, коды состояния, форматы JSON. "
            "Здесь нет бизнес-правил, только перевод между внешними сообщениями "
            "и командами Application. Minimal API подходит такому слою: эндпоинты "
            "объединяют в группы, а зависимости обработчика внедряются параметрами.\n\n"
            "Эндпоинты группируют по ресурсу через `MapGroup`. Группа задаёт общий "
            "префикс, тег и требования авторизации. Обработчик принимает команду "
            "и отправляет её в Application, а результат превращает в код состояния."
        ),
        example(
            "csharp",
            """
            using Microsoft.AspNetCore.Builder;
            using Microsoft.AspNetCore.Http;
            using Microsoft.AspNetCore.Routing;
            using MyApp.Application.Orders;

            namespace MyApp.Api.Endpoints;

            public static class OrdersEndpoints
            {
                public static void MapOrders(this IEndpointRouteBuilder app)
                {
                    var group = app.MapGroup("/api/orders").WithTags("Orders");

                    group.MapPost("/", async (
                        CreateOrderRequest request,
                        CreateOrderHandler handler,
                        CancellationToken ct) =>
                    {
                        var dto = await handler.HandleAsync(new CreateOrderCommand(request), ct);
                        return Results.Created($"/api/orders/{dto.Id}", dto);
                    });

                    group.MapGet("/{id:guid}", async (
                        Guid id,
                        GetOrderHandler handler,
                        CancellationToken ct) =>
                    {
                        var dto = await handler.HandleAsync(id, ct);
                        return dto is null ? Results.NotFound() : Results.Ok(dto);
                    });
                }
            }
            """,
        ),
        text(
            "Ожидаемые ошибки не должны превращаться в `500`. Middleware — компонент "
            "конвейера, через который проходит каждый запрос, — перехватывает исключения "
            "и сопоставляет их тип с кодом состояния. Доменное исключение становится "
            "`400` с кодом ошибки, отсутствие данных — `404`, всё неожиданное — `500` "
            "с записью в журнал без подробностей для клиента."
        ),
        example(
            "csharp",
            """
            using System.Net;
            using Microsoft.AspNetCore.Http;
            using Microsoft.Extensions.Logging;
            using MyApp.Domain.Exceptions;

            namespace MyApp.Api.Middleware;

            public sealed class ExceptionHandlingMiddleware
            {
                private readonly RequestDelegate _next;
                private readonly ILogger<ExceptionHandlingMiddleware> _log;

                public ExceptionHandlingMiddleware(
                    RequestDelegate next, ILogger<ExceptionHandlingMiddleware> log)
                {
                    _next = next;
                    _log = log;
                }

                public async Task InvokeAsync(HttpContext context)
                {
                    try
                    {
                        await _next(context);
                    }
                    catch (DomainException ex)
                    {
                        _log.LogWarning("Доменная ошибка {Code}: {Message}", ex.Code, ex.Message);
                        await WriteAsync(context, StatusCodes.Status400BadRequest,
                            new { code = ex.Code, message = ex.Message });
                    }
                    catch (Exception ex)
                    {
                        _log.LogError(ex, "Необработанная ошибка");
                        await WriteAsync(context, StatusCodes.Status500InternalServerError,
                            new { code = "INTERNAL", message = "Внутренняя ошибка сервера." });
                    }
                }

                private static Task WriteAsync(HttpContext context, int status, object body)
                {
                    context.Response.StatusCode = status;
                    return context.Response.WriteAsJsonAsync(body);
                }
            }
            """,
        ),
        text(
            "`Program.cs` собирает приложение: читает конфигурацию, регистрирует слои, "
            "настраивает конвейер. Порядок middleware важен: обработка исключений стоит "
            "первой, чтобы поймать ошибку из любого последующего компонента, "
            "а логирование запросов и проверка авторизации идут после неё.\n\n"
            "Конвейер (pipeline) — цепочка middleware, где каждый компонент вызывает "
            "следующий через `_next`. В ASP.NET Core встроенный `UseExceptionHandler` "
            "умеет то же самое, и в реальном проекте его используют чаще собственного "
            "класса; свой вариант полезен, когда нужен особый формат ошибки."
        ),
        example(
            "csharp",
            """
            using MyApp.Api.Endpoints;
            using MyApp.Api.Middleware;
            using MyApp.Application;
            using MyApp.Infrastructure;

            var builder = WebApplication.CreateBuilder(args);

            builder.Services.AddApplication();
            builder.Services.AddInfrastructure(builder.Configuration);

            var app = builder.Build();

            app.UseMiddleware<ExceptionHandlingMiddleware>();
            app.UseAuthentication();
            app.UseAuthorization();

            app.MapOrders();
            app.MapGet("/health", () => Results.Ok(new { status = "ok" }));

            app.Run();
            """,
        ),
        heading("Тесты на разных уровнях"),
        text(
            "Слоистая архитектура окупается в тестах. Правило домена проверяется "
            "модульным тестом без базы данных: создать заказ, попробовать подтвердить "
            "пустой — ожидать исключение с нужным кодом. Такой тест выполняется "
            "за миллисекунды и не требует сети.\n\n"
            "Сценарии проверяют тестом обработчика с поддельными репозиториями. "
            "Подделка (fake) — класс в памяти, реализующий интерфейс: он запоминает "
            "добавленные заказы и считает вызовы сохранения."
        ),
        example(
            "csharp",
            """
            using System.Collections.Generic;
            using MyApp.Application.Abstractions;
            using MyApp.Domain.Orders;

            public sealed class FakeOrderRepository : IOrderRepository
            {
                public List<Order> Saved { get; } = new();

                public Task AddAsync(Order order, CancellationToken ct)
                {
                    Saved.Add(order);
                    return Task.CompletedTask;
                }

                public Task<Order?> GetAsync(Guid id, CancellationToken ct)
                    => Task.FromResult(Saved.Find(o => o.Id == id));
            }

            public sealed class FakeUnitOfWork : IUnitOfWork
            {
                public int Saves { get; private set; }

                public Task<int> SaveChangesAsync(CancellationToken ct)
                {
                    Saves++;
                    return Task.FromResult(1);
                }
            }
            """,
        ),
        example(
            "csharp",
            """
            using System;
            using MyApp.Application.Abstractions;
            using MyApp.Application.Orders;
            using Xunit;

            public class CreateOrderHandlerTests
            {
                [Fact]
                public async Task Handle_SavesOrderAndConfirmsIt()
                {
                    var repository = new FakeOrderRepository();
                    var uow = new FakeUnitOfWork();
                    var handler = new CreateOrderHandler(repository, uow);
                    var request = new CreateOrderRequest("Иван", new[]
                    {
                        new OrderLineDto("KEYBOARD-01", 2, 2500m)
                    });

                    var dto = await handler.HandleAsync(
                        new CreateOrderCommand(request), CancellationToken.None);

                    Assert.Single(repository.Saved);
                    Assert.Equal(1, uow.Saves);
                    Assert.Equal(5000m, dto.Total);
                    Assert.Equal("Confirmed", dto.Status);
                }
            }
            """,
        ),
        text(
            "Вывод теста в стандартном режиме краток, при провале xUnit "
            "показывает ожидаемое и фактическое значения."
        ),
        example(
            "text",
            """
            $ dotnet test tests/MyApp.UnitTests
            Определение проектов для восстановления выполнено
            Сборка успешно завершена.
            Тест-проект tests/MyApp.UnitTests (net8.0) выполнил:
            Пройдено!  - Не пройдено: 0, пройдено: 1, пропущено: 0, всего: 1
            """,
        ),
        heading("Архитектурные тесты"),
        text(
            "Архитектурный тест проверяет не поведение, а структуру: кто на кого "
            "ссылается. Это дешёвая страховка от того, что через полгода кто-то "
            "добавит `using Microsoft.EntityFrameworkCore` в сущность и никто не заметит.\n\n"
            "Проще всего проверить ссылки на уровне сборок: получить список "
            "`Assembly.GetReferencedAssemblies()` у сборки Domain и убедиться, "
            "что среди зависимостей нет Application, Infrastructure и Api. "
            "Тест падает на этапе сборки CI, а не в production."
        ),
        example(
            "csharp",
            """
            using System.Linq;
            using Xunit;

            public class LayeringTests
            {
                private static string[] ReferencesOfDomain() =>
                    typeof(MyApp.Domain.Orders.Order).Assembly
                        .GetReferencedAssemblies()
                        .Select(a => a.Name ?? string.Empty)
                        .ToArray();

                [Fact]
                public void Domain_DoesNotReferenceOuterLayers()
                {
                    var references = ReferencesOfDomain();

                    Assert.DoesNotContain("MyApp.Application", references);
                    Assert.DoesNotContain("MyApp.Infrastructure", references);
                    Assert.DoesNotContain("MyApp.Api", references);
                    Assert.DoesNotContain("Microsoft.EntityFrameworkCore", references);
                }
            }
            """,
        ),
        text(
            "Вывод провалившегося архитектурного теста сразу указывает виновника: "
            "`Assert.DoesNotContain` печатает найденную сборку. Для больших решений "
            "используют библиотеку NetArchTest, которая позволяет формулировать "
            "правила вроде «все типы из пространства Domain не должны зависеть от Infrastructure»."
        ),
        example(
            "text",
            """
            $ dotnet test tests/MyApp.ArchitectureTests
            Провалено LayeringTests.Domain_DoesNotReferenceOuterLayers [12 ms]
              Сообщение об ошибке:
              Assert.DoesNotContain() Failure: Item found in collection
              Collection: ["System.Runtime", "Microsoft.EntityFrameworkCore", ...]
              Found:      "Microsoft.EntityFrameworkCore"

            Не пройдено!  - Не пройдено: 1, пройдено: 0, пропущено: 0, всего: 1
            """,
        ),
        callout(
            "success",
            "Правило без соглашений",
            "Архитектурный тест превращает схему на слайде в проверяемое условие. "
            "Компилятор контролирует проектные ссылки, архитектурный тест — "
            "зависимости внутри сборки, например на NuGet-пакеты вроде EF Core.",
        ),
        heading("Запуск и подготовка к деплою"),
        text(
            "Приложение должно запускаться одинаково на машине разработчика, "
            "в CI и в production. Строка подключения приходит из конфигурации: "
            "переменные среды перекрывают `appsettings.json`, а секреты в репозиторий "
            "не попадают. Адрес и порт задаёт переменная `ASPNETCORE_URLS`.\n\n"
            "Логирование — сквозная задача, как и обработка ошибок. Структурированные "
            "журналы пишут набор полей, поэтому по ним можно искать по коду заказа. "
            "Health check — эндпоинт, который оркестратор опрашивает, чтобы понять, "
            "жива ли служба."
        ),
        example(
            "bash",
            """
            export ASPNETCORE_ENVIRONMENT=Production
            export ConnectionStrings__Default="Host=localhost;Database=myapp;Username=postgres;Password=postgres"
            dotnet run --project src/MyApp.Api

            # Проверка работоспособности и создание заказа
            curl -s http://localhost:5000/health
            curl -s -X POST http://localhost:5000/api/orders \
              -H "Content-Type: application/json" \
              -d '{"customer":"Иван","lines":[{"sku":"KEYBOARD-01","quantity":2,"price":2500}]}'
            """,
        ),
        example(
            "text",
            """
            {"status":"ok"}
            {"id":"8c1d5f4e-0d33-4a1e-9f2b-7c0a1b2c3d4e","customer":"Иван","status":"Confirmed","total":5000}
            """,
        ),
        text(
            "Для контейнерного запуска хватает двух файлов: `Dockerfile` с двумя стадиями "
            "и `docker-compose.yml` с приложением и базой. Сборка идёт в образе SDK, "
            "а запуск — в облегчённом образе ASP.NET Core runtime. Так итоговый образ "
            "содержит только то, что нужно в production, а не весь инструментарий компиляции."
        ),
        example(
            "dockerfile",
            """
            FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
            WORKDIR /src
            COPY . .
            RUN dotnet publish src/MyApp.Api/MyApp.Api.csproj -c Release -o /app/publish

            FROM mcr.microsoft.com/dotnet/aspnet:8.0
            WORKDIR /app
            COPY --from=build /app/publish .
            EXPOSE 8080
            ENTRYPOINT ["dotnet", "MyApp.Api.dll"]
            """,
        ),
        table(
            ["Область", "Что проверить перед выкладкой"],
            [
                ["Безопасность", "HTTPS, авторизация, ограничение частоты запросов, секреты вне репозитория"],
                ["Надёжность", "Health check, таймауты, повторные попытки, корректная остановка"],
                ["Наблюдаемость", "Структурированные журналы, идентификатор корреляции, метрики задержек"],
                ["Данные", "Миграции применяются при развёртывании, есть план резервного копирования"],
                ["Тесты", "Модульные на правила, интеграционные на критические сценарии, архитектурные на границы"],
            ],
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["`Domain` ссылается на `Infrastructure`", "Слой теряет независимость, сборка циклична", "Интерфейсы репозиториев в Application, реализация в Infrastructure"],
                ["Атрибуты EF Core в сущности", "Технология проникает в домен", "Настройка через `IEntityTypeConfiguration<T>` в Infrastructure"],
                ["Бизнес-проверки в эндпоинте", "Правило дублируется в других вызывающих местах", "Проверки в сущности, эндпоинт только переводит формат"],
                ["`DbContext` внедрён в `Singleton`", "Исключение контейнера или гонки при параллельных запросах", "`Scoped` для контекста и репозиториев"],
                ["Исключение вместо ожидаемого результата", "«Не найдено» превращается в `500`", "Возвращать `null`/результат, исключения — для нарушений правил"],
                ["Публичная коллекция `List<OrderLine>`", "Строки можно изменить в обход инвариантов", "Только `IReadOnlyList` и методы добавления"],
                ["Интеграционные тесты на реальной базе разработчика", "Тесты зависят от локальных данных", "Testcontainers или база в памяти для изоляции"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняются на собственном решении. Проверяйте после каждого шага: "
            "`dotnet build MyApp.sln` и `dotnet test`."
        ),
        numbered(
            "Создайте решение из четырёх проектов `src` и добавьте ссылки строго по правилу зависимостей. Проверьте, что `dotnet build` проходит, а попытка добавить ссылку `Domain` на `Infrastructure` не компилируется.",
            "Реализуйте в Domain сущность `Order` с инвариантами из урока и доменным исключением с кодом. Напишите два модульных теста: подтверждение пустого заказа бросает `ORDER_EMPTY`, добавление строки в подтверждённый заказ бросает `ORDER_LOCKED`.",
            "Добавьте сценарий отмены заказа: команду `CancelOrderCommand`, метод `Cancel` в сущности (нельзя отменить подтверждённый заказ) и обработчик. Ошибку верните как доменное исключение.",
            "Подключите EF Core с конфигурацией `OrderConfiguration` и реализуйте `IOrderRepository`. Запустите миграцию и убедитесь, что таблица заказов содержит колонку статуса строкой.",
            "Добавьте middleware обработки ошибок и эндпоинт `POST /api/orders`. Проверьте через `curl`, что пустой заказ даёт `400` с кодом `ORDER_EMPTY`, а корректный — `201` с адресом ресурса.",
            "Напишите архитектурный тест на сборку Domain и убедитесь, что он падает, если временно добавить `Microsoft.EntityFrameworkCore` в проект Domain.",
        ),
        text("Ожидаемый результат для задания 2:"),
        example(
            "text",
            """
            $ dotnet test --filter FullyQualifiedName~OrderTests
            Пройдено!  - Не пройдено: 0, пройдено: 2, пропущено: 0, всего: 2
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 5",
            "При отправке пустого списка строк обработчик вызывает `Confirm`, получает "
            "`OrderEmptyException`, middleware превращает его в `400`. Не добавляйте "
            "проверку в эндпоинт — правило принадлежит сущности.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему интерфейс репозитория объявляют в Application, а реализацию — в Infrastructure?",
            "Что произойдёт, если сущность Domain пометить атрибутами EF Core?",
            "Зачем в сущности `Order` конструктор без параметров объявлен приватным?",
            "Какие ошибки считаются ожидаемыми и почему для них лучше не бросать исключение?",
            "Какую роль играет `Program.cs` и почему только он знает обо всех слоях?",
            "Какой срок жизни у `DbContext` и что будет при внедрении его в `Singleton`?",
        ),
        heading("Ответы", 3),
        numbered(
            "Направление зависимости задаёт потребитель услуги. Сценарий нуждается в хранении, поэтому объявляет интерфейс; конкретная реализация на EF Core — технология и потому живёт во внешнем слое. Так внутренний слой не зависит от базы.",
            "Технология хранилища проникнет в домен, и Domain станет невозможно использовать и тестировать без EF Core. Отображение настраивают через `IEntityTypeConfiguration<T>` в Infrastructure.",
            "Чтобы заказ нельзя было создать в обход проверок. Единственный путь — статический `Create`, который валидирует данные. Приватный конструктор нужен EF Core для материализации из базы.",
            "«Не найдено» и «не пройдена валидация» — нормальные исходы сценария. Исключения дороже по производительности, прерывают поток управления, а middleware превращает доменные ошибки в `400`, а не в `500`.",
            "Это композиционный корень: он регистрирует службы, настраивает конвейер middleware и маршруты. Каждый слой регистрируется своим методом, поэтому только `Program.cs` ссылается на все слои сразу.",
            "`Scoped`: один экземпляр на HTTP-запрос. При внедрении в `Singleton` контейнер выбросит исключение `Cannot consume scoped service`, так как контекст нельзя делить между параллельными запросами.",
        ),
        heading("Итоги"),
        bullets(
            "Четыре слоя: Domain (правила), Application (сценарии), Infrastructure (технологии), Api (протокол).",
            "Правило зависимостей направлено внутрь; границы проверяет компилятор через `ProjectReference`.",
            "Domain содержит сущности с инвариантами, объекты-значения и доменные исключения с кодом ошибки.",
            "Application объявляет интерфейсы репозиториев и реализует команды и запросы через обработчики.",
            "Infrastructure хранит EF Core, конфигурации отображения и реализацию репозиториев.",
            "Api переводит HTTP в команды, middleware превращает доменные ошибки в осмысленные коды состояния.",
            "Тесты идут уровнями: модульные для правил, обработчиков и архитектурный для границ между слоями.",
        ),
        heading("Что дальше"),
        text(
            "Вы собрали приложение, в котором слои не путаются, а правила живут в одном месте. "
            "Дальше стоит добавить аутентификацию, пагинацию, версионирование API, "
            "идемпотентность повторных запросов и фоновые задания. Каждый шаг расширяет "
            "готовые места — эндпоинты, обработчики и слой данных."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Шаблон Jason Taylor Clean Architecture — github.com/jasontaylordev/CleanArchitecture",
            "Documentation: ASP.NET Core — Minimal API и middleware, learn.microsoft.com/aspnet/core",
            "Документация EF Core: рекомендации по моделированию и настройке — learn.microsoft.com/ef/core",
            "NetArchTest — библиотека правил архитектуры: github.com/BenMorris/NetArchTest",
        ),
    ],
}
