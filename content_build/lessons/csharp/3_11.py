"""Урок 3.11 курса C#: продвинутый проект."""

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
    "topic_order": 11,
    "name": "3.11. Продвинутый проект",
    "slug": "csharp-3-11-продвинутый-проект",
    "short_description": (
        "Сборка production-ready сервиса на C#: Clean Architecture, CQRS, доменные "
        "события, EF Core, Minimal API, архитектурные тесты, CI/CD, наблюдаемость "
        "и эксплуатационная документация."
    ),
    "topic_name": "Продвинутый проект",
    "topic_description": (
        "Итоговый проект курса: от структуры решения и богатой доменной модели до "
        "конвейера поставки, OpenTelemetry, runbook-ов и плана обслуживания. Урок "
        "показывает, как собрать изученные паттерны в один поддерживаемый сервис."
    ),
    "learning_objectives": [
        "Разложить решение на слои Domain, Application, Infrastructure и API с корректным направлением зависимостей",
        "Реализовать богатую доменную модель с инвариантами, фабричным методом и доменными событиями",
        "Разделить операции чтения и записи через CQRS и конвейер обработчиков с поведением валидации",
        "Настроить EF Core: конфигурации без data annotations, теневые поля и интерсептор аудита",
        "Собрать Minimal API с ProblemDetails, версионированием и централизованной обработкой ошибок",
        "Защитить архитектуру тестами и настроить CI-конвейер из сборки, тестов, сканирования и публикации",
        "Внедрить наблюдаемость: метрики, трассировку и проверки работоспособности",
        "Подготовить эксплуатацию: ADR, runbook, обновление зависимостей и профилирование",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "csharp",
        "архитектура",
        "cqrs",
        "ef-core",
        "ci-cd",
        "наблюдаемость",
        "production",
    ],
    "starter_code": code(
        r"""
        using System;
        using System.Collections.Generic;
        using System.Linq;

        var order = Order.Create(
            customerId: "c-17",
            items: new[]
            {
                new OrderItemData("sku-1", quantity: 2, unitPrice: 1500m),
                new OrderItemData("sku-2", quantity: 1, unitPrice: 990m),
            });

        order.Confirm();
        Console.WriteLine($"Заказ {order.Id}: статус {order.Status}, сумма {order.Total}");

        foreach (var domainEvent in order.DomainEvents)
            Console.WriteLine($"Событие: {domainEvent.GetType().Name}");

        public enum OrderStatus { Pending, Confirmed, Cancelled }

        public sealed record OrderItemData(string ProductId, int Quantity, decimal UnitPrice);

        public sealed record OrderItem(string ProductId, int Quantity, decimal UnitPrice)
        {
            public decimal LineTotal => Quantity * UnitPrice;
        }

        public sealed class Order
        {
            private readonly List<OrderItem> _items = new();
            private readonly List<object> _domainEvents = new();

            public Guid Id { get; private init; }
            public string CustomerId { get; private init; } = "";
            public OrderStatus Status { get; private set; }
            public decimal Total => _items.Sum(i => i.LineTotal);
            public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly();
            public IReadOnlyCollection<object> DomainEvents => _domainEvents.AsReadOnly();

            private Order() { }

            public static Order Create(string customerId, IEnumerable<OrderItemData> items)
            {
                var order = new Order { Id = Guid.NewGuid(), CustomerId = customerId };
                foreach (var item in items)
                    order.AddItem(item);

                if (!order._items.Any())
                    throw new DomainException("Заказ не может быть пустым");

                order._domainEvents.Add(new { OrderId = order.Id, Total = order.Total });
                return order;
            }

            public void AddItem(OrderItemData data)
            {
                if (Status != OrderStatus.Pending)
                    throw new DomainException("Состав заказа можно менять только до подтверждения");
                if (data.Quantity <= 0)
                    throw new DomainException("Количество должно быть положительным");
                if (data.UnitPrice <= 0)
                    throw new DomainException("Цена должна быть положительной");

                var index = _items.FindIndex(i => i.ProductId == data.ProductId);
                if (index >= 0)
                    _items[index] = _items[index] with { Quantity = _items[index].Quantity + data.Quantity };
                else
                    _items.Add(new OrderItem(data.ProductId, data.Quantity, data.UnitPrice));
            }

            public void Confirm()
            {
                if (Status != OrderStatus.Pending)
                    throw new DomainException($"Нельзя подтвердить заказ в статусе {Status}");
                Status = OrderStatus.Confirmed;
                _domainEvents.Add(new { OrderId = Id, ConfirmedAt = DateTimeOffset.UtcNow });
            }

            public void ClearDomainEvents() => _domainEvents.Clear();
        }

        public sealed class DomainException(string message) : Exception(message);
        """
    ),
    "hints": [
        "Направление зависимостей задаёт слои: Domain не ссылается ни на кого, Application — только на Domain, Infrastructure — на Application и Domain, API — на всё. Нарушение видно в .csproj.",
        "Богатая модель означает, что инварианты живут в сущности: фабричный метод и методы-команды бросают DomainException, сеттеры закрыты, коллекции отдаются только для чтения.",
        "Для EF Core используйте IEntityTypeConfiguration вместо атрибутов и PropertyAccessMode.Field: тогда материалы работают с полями, а не с навигационными свойствами.",
        "Архитектурные тесты дешевле ошибок на ревью: один тест на Layers и один на запрет reference на внешние сборки закрывают большую часть дрейфа архитектуры.",
    ],
    "content": [
        text(
            "Этот урок собирает пройденный материал в один артефакт — сервис, который"
            " можно отдать в эксплуатацию. Отдельные приёмы из предыдущих разделов"
            " работают и сами по себе, но в реальной системе они связаны: архитектура"
            " определяет слои, слои задают места для тестов, тесты защищают контракт"
            " API, а конвейер поставки и наблю дают уверенность, что изменения не"
            " ломают пользователей. Самой частой проблемой зрелого проекта становится"
            " не отсутствие функций, а стоимость изменений.\n\n"
            "Ниже разобран сквозной пример сервиса заказов: от структуры решения до"
            " runbook-а дежурного. Код собран из фрагментов рабочего проекта: он"
            " сокращён, но сохраняет типы, сигнатуры и порядок вызовов, которые важны"
            " для понимания. Там, где показан вывод, он соответствует"
            " последовательному запуску консольного примера.",
        ),
        heading("Чему вы научитесь"),
        bullets(
            "проектировать структуру решения, где зависимости направлены внутрь, к домену;",
            "переносить инварианты в сущности и агрегаты, а не в контроллеры и обработчики;",
            "разделять чтение и запись через команды, запросы и обработчики с конвейером поведения;",
            "настраивать EF Core конфигурациями и интерсепторами без атрибутов в домене;",
            "описывать API через Minimal API, ProblemDetails и стабильные коды ошибок;",
            "закреплять архитектурные правила тестами и проверками CI;",
            "встраивать метрики, трассировку и health checks как часть контракта сервиса;",
            "вести документацию и план обслуживания, а не оставлять их «на потом».",
        ),
        heading("Структура решения"),
        text(
            "Ссылочная архитектура — это не папки ради папок, а правило компиляции:"
            " проект Domain вообще не имеет ссылок на другие проекты, Application"
            " ссылается только на Domain, Infrastructure — на Application и Domain,"
            " а API — на все прикладные слои. Такое направление зависимостей делает"
            " домен переиспользуемым и тестируемым без базы данных и фреймворка.\n\n"
            "Отдельно выносят сборку с контрактами: события интеграции, DTO и"
            " интерфейсы, которыми пользуются другие сервисы. Она не содержит"
            " инфраструктуры и подключается к потребителям как обычный пакет. Сборка"
            " worker-а отделена от API, потому что у них разные профили нагрузки,"
            " развёртывание и масштабирование.\n\n"
            "Каталог tests повторяет слои: юнит-тесты домена не требуют окружения,"
            " интеграционные тесты поднимают реальную базу через контейнеры,"
            " архитектурные тесты проверяют ссылки между сборками, тесты"
            " производительности фиксируют базовые значения. В корне решения лежат"
            " файлы, влияющие на все проекты: Directory.Build.props с настройками"
            " компилятора и анализаторов, Directory.Packages.props с версиями"
            " пакетов, global.json с версией набора SDK.",
        ),
        example(
            "text",
            """
            Orders/
            ├── .github/workflows/ci.yml
            ├── docs/adr/001-clean-architecture.md
            ├── docs/runbooks/order-processing-failure.md
            ├── src/
            │   ├── Orders.Domain/
            │   ├── Orders.Application/
            │   ├── Orders.Infrastructure/
            │   ├── Orders.Api/
            │   ├── Orders.Worker/
            │   └── Orders.Contracts/
            ├── tests/
            │   ├── Orders.UnitTests/
            │   ├── Orders.IntegrationTests/
            │   └── Orders.ArchitectureTests/
            ├── Directory.Build.props
            ├── Directory.Packages.props
            ├── global.json
            └── Orders.sln
            """,
        ),
        callout(
            "info",
            "Проверка направления ссылок",
            "Откройте .csproj домена: там должен быть только TargetFramework и, при необходимости, анализатор. Любая PackageReference на EF Core или ASP.NET Core в Domain — сигнал, что слой начал подменять инфраструктуру.",
        ),
        heading("Богатая доменная модель"),
        text(
            "Домен отвечает за правила предметной области. Сущность заказа не позволяет"
            " добавить позицию с нулевым количеством, не разрешает менять состав после"
            " подтверждения и сама решает, какие события поднять. Все эти проверки"
            " находятся рядом с данными, поэтому их нельзя обойти, вызвав другой метод"
            " или обратившись напрямую к коллекции.\n\n"
            "Агрегат — кластер объектов, который изменяется как единое целое. В примере"
            " корнем агрегата является Order, а позиции доступны только через методы"
            " корня. Позиции отдаются как интерфейс только для чтения: вызывающий код"
            " получает возможность перечислить элементы, но не изменить список в обход"
            " инвариантов.\n\n"
            "Создание объекта идёт через фабричный метод: он гарантирует, что заказ"
            " рождается в согласованном состоянии и сразу порождает событие"
            " OrderCreated. Конструктор без параметров закрыт, но EF Core умеет"
            " обходиться и без него — это важно, когда свойства инициализируются"
            " только материалами.",
        ),
        example(
            "csharp",
            """
            public sealed class Order
            {
                private readonly List<OrderItem> _items = new();
                private readonly List<IDomainEvent> _events = new();

                public Guid Id { get; private set; }
                public CustomerId CustomerId { get; private set; }
                public OrderStatus Status { get; private set; }
                public decimal Total => _items.Sum(i => i.LineTotal);
                public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly();
                public IReadOnlyCollection<IDomainEvent> DomainEvents => _events.AsReadOnly();

                private Order() { }

                public static Order Create(CustomerId customerId, IEnumerable<OrderItemData> items)
                {
                    var order = new Order { Id = Guid.NewGuid(), CustomerId = customerId };
                    foreach (var item in items)
                        order.AddItem(item);

                    if (order._items.Count == 0)
                        throw new DomainException("В заказе должна быть хотя бы одна позиция");

                    order._events.Add(new OrderCreated(order.Id, order.CustomerId, order.Total));
                    return order;
                }

                public void Confirm()
                {
                    if (Status != OrderStatus.Pending)
                        throw new DomainException($"Нельзя подтвердить заказ в статусе {Status}");

                    Status = OrderStatus.Confirmed;
                    _events.Add(new OrderConfirmed(Id));
                }

                public void ClearDomainEvents() => _events.Clear();
            }
            """,
        ),
        text(
            "Проверим основные правила домена на консольном примере: создание заказа,"
            " суммирование позиций, подтверждение и попытку изменить подтверждённый"
            " заказ."
        ),
        example(
            "csharp",
            """
            var order = Order.Create(
                new CustomerId(Guid.NewGuid()),
                new[] { new OrderItemData("sku-1", 2, 1500m), new OrderItemData("sku-2", 1, 990m) });

            Console.WriteLine($"Создан заказ {order.Id}, статус {order.Status}, сумма {order.Total}");
            order.Confirm();
            Console.WriteLine($"После подтверждения: {order.Status}");

            try
            {
                order.AddItem(new OrderItemData("sku-3", 1, 100m));
            }
            catch (DomainException ex)
            {
                Console.WriteLine($"Отклонено: {ex.Message}");
            }
            """,
        ),
        text(
            "Вывод: \n"
            "Создан заказ 8f2c1a35-6d1e-4b52-9a37-1c0e7f43b11a, статус Pending, сумма 3990\n"
            "После подтверждения: Confirmed\n"
            "Отклонено: Состав заказа можно менять только до подтверждения"
        ),
        heading("Прикладной слой и CQRS"),
        text(
            "Прикладной слой описывает сценарии: создать заказ, получить список заказов,"
            " подтвердить заказ. Разделение на команды и запросы — CQRS — позволяет"
            " проектировать чтение и запись по отдельности: команда меняет состояние"
            " через агрегат, запрос возвращает плоский DTO и не тянет доменные связи.\n\n"
            "Команда — это запись, описывающая намерение, запрос — описание результата."
            " Обработчик получает зависимости через конструктор и реализует ровно один"
            " сценарий. Обработчики не знают про HTTP, базы данных и сериализацию:"
            " они работают с репозиториями и возвращают результат. Исключение с"
            " ошибками валидации перехватывает фильтр на границе API.\n\n"
            "Поперечные задачи — валидация, логирование, замер времени — выносятся в"
            " поведение конвейера. Конвейер оборачивает каждый обработчик, поэтому"
            " правило добавляется один раз и применяется ко всем командам. Валидация"
            " в поведении отделена от доменных инвариантов: валидатор проверяет форму"
            " запроса, домен проверяет бизнес-правила.",
        ),
        example(
            "csharp",
            """
            public sealed record CreateOrderCommand(
                Guid CustomerId,
                List<OrderItemDto> Items) : IRequest<Result<Guid>>;

            public sealed class CreateOrderHandler : IRequestHandler<CreateOrderCommand, Result<Guid>>
            {
                private readonly IOrderRepository _orders;
                private readonly IProductCatalog _catalog;
                private readonly IUnitOfWork _unitOfWork;
                private readonly IDomainEventDispatcher _dispatcher;

                public CreateOrderHandler(
                    IOrderRepository orders,
                    IProductCatalog catalog,
                    IUnitOfWork unitOfWork,
                    IDomainEventDispatcher dispatcher)
                {
                    _orders = orders;
                    _catalog = catalog;
                    _unitOfWork = unitOfWork;
                    _dispatcher = dispatcher;
                }

                public async Task<Result<Guid>> Handle(CreateOrderCommand request, CancellationToken ct)
                {
                    var order = Order.Create(
                        new CustomerId(request.CustomerId),
                        request.Items.Select(i => new OrderItemData(i.ProductId, i.Quantity, i.UnitPrice)));

                    var productIds = order.Items.Select(i => i.ProductId).ToArray();
                    if (!await _catalog.AllExistAsync(productIds, ct))
                        return Result.Failure<Guid>(Error.NotFound("Product.NotFound", "Позиции не найдены"));

                    await _orders.AddAsync(order, ct);
                    await _unitOfWork.SaveChangesAsync(ct);
                    await _dispatcher.DispatchAsync(order.DomainEvents, ct);
                    order.ClearDomainEvents();

                    return Result.Success(order.Id);
                }
            }
            """,
        ),
        text(
            "Порядок вызовов здесь принципиален. Сначала заказ добавляется в репозиторий,"
            " затем сохраняется транзакция, и только после успешной фиксации"
            " отправляются доменные события. Если отправить событие до SaveChanges,"
            " обработчик события может прочитать заказ, которого ещё нет в базе, а при"
            " отказе транзакции событие уже ушло внешним системам.\n\n"
            "Поведение валидации выполняет FluentValidation за пределы обработчика и"
            " прерывает конвейер при первой ошибке. Замер производительности пишет"
            " предупреждение, если команда выполняется дольше заданного порога. Оба"
            " поведения регистрируются один раз при старте и не засоряют логику"
            " сценария.",
        ),
        example(
            "csharp",
            """
            public sealed class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
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
                    if (!_validators.Any())
                        return await next();

                    var context = new ValidationContext<TRequest>(request);
                    var failures = new List<ValidationFailure>();

                    foreach (var validator in _validators)
                    {
                        var result = await validator.ValidateAsync(context, ct);
                        failures.AddRange(result.Errors);
                    }

                    if (failures.Count != 0)
                        throw new ValidationException(failures);

                    return await next();
                }
            }
            """,
        ),
        heading("Инфраструктура: EF Core и аудит"),
        text(
            "Материальные конфигурации держат домен свободным от атрибутов: класс"
            " IEntityTypeConfiguration описывает таблицу, ключ, конвертации типов и"
            " владение объектами-значениями. Адрес доставки — объект-значение, который"
            " хранится в тех же колонках заказа, а не в отдельной таблице. Статус"
            " хранится как строка: так база не зависит от порядка констант в enum и"
            " остаётся читаемой при ручном разборе.\n\n"
            "Свойство элементов доступно только через поле, потому что мутация"
            " коллекции должна идти через методы агрегата. Параметр PropertyAccessMode"
            " говорит EF Core использовать поле _items при загрузке и сохранении.\n\n"
            "Аудит — типичная поперечная задача инфраструктуры. Интерсептор"
            " SaveChanges проверяет отслеживаемые сущности, помеченные интерфейсом"
            " IAuditable, и проставляет время и пользователя. Это надёжнее, чем"
            " заполнять поля вручную в каждом обработчике: одна точка, один формат.",
        ),
        example(
            "csharp",
            """
            public sealed class OrderConfiguration : IEntityTypeConfiguration<Order>
            {
                public void Configure(EntityTypeBuilder<Order> builder)
                {
                    builder.ToTable("Orders");
                    builder.HasKey(o => o.Id);
                    builder.Property(o => o.Id).ValueGeneratedNever();
                    builder.Property(o => o.Status).HasConversion<string>().HasMaxLength(20);

                    builder.OwnsOne(o => o.ShippingAddress, address =>
                    {
                        address.Property(a => a.Street).HasMaxLength(200);
                        address.Property(a => a.City).HasMaxLength(100);
                        address.Property(a => a.Country).HasMaxLength(2);
                    });

                    builder.HasMany(o => o.Items)
                        .WithOne()
                        .HasForeignKey("OrderId")
                        .OnDelete(DeleteBehavior.Cascade);

                    builder.Navigation(o => o.Items).UsePropertyAccessMode(PropertyAccessMode.Field);
                }
            }
            """,
        ),
        example(
            "csharp",
            """
            public sealed class AuditingInterceptor(ICurrentUserService currentUser) : SaveChangesInterceptor
            {
                public override InterceptionResult<int> SavingChanges(
                    DbContextEventData eventData,
                    InterceptionResult<int> result)
                {
                    var context = eventData.Context;
                    if (context is null)
                        return base.SavingChanges(eventData, result);

                    var userId = currentUser.UserId ?? "system";
                    var now = DateTimeOffset.UtcNow;

                    foreach (var entry in context.ChangeTracker.Entries<IAuditable>())
                    {
                        if (entry.State == EntityState.Added)
                        {
                            entry.Entity.CreatedAt = now;
                            entry.Entity.CreatedBy = userId;
                        }
                        else if (entry.State == EntityState.Modified)
                        {
                            entry.Entity.UpdatedAt = now;
                            entry.Entity.UpdatedBy = userId;
                        }
                    }

                    return base.SavingChanges(eventData, result);
                }
            }
            """,
        ),
        heading("API как граница сервиса"),
        text(
            "API не содержит логики: он принимает запрос, передаёт его в приложение и"
            " переводит результат в HTTP. Группа маршрутов задаёт версию в пути"
            " /api/v1/orders, требования к авторизации и теги для документации. Каждый"
            " маршрут возвращает либо результат, либо ошибку в формате ProblemDetails.\n\n"
            "ProblemDetails — стандартный формат ошибок из RFC 9457: тип, заголовок,"
            " код состояния и расширения. Клиенты перестают зависеть от текста"
            " сообщения, если сервер отдаёт стабильный машиночитаемый код. Расширение"
            " ToProblemDetails сопоставляет доменные ошибки со статусами: Validation —"
            " 400, NotFound — 404, Conflict — 409, остальное — 500 без утечки"
            " внутренних деталей.\n\n"
            "Версия в маршруте позволяет выпускать обратно совместимые изменения без"
            " поломки клиентов. Композиционный корень Program.cs — единственное место,"
            " где известно, какие реализации скрыты за интерфейсами: база данных,"
            " почта, платёжный шлюз, диспетчер событий. Здесь же настраиваются"
            " политики устойчивости для внешних HTTP-вызовов.",
        ),
        example(
            "csharp",
            """
            public static class OrdersEndpoints
            {
                public static void MapOrdersEndpoints(this IEndpointRouteBuilder app)
                {
                    var group = app.MapGroup("/api/v1/orders")
                        .RequireAuthorization()
                        .WithTags("Orders");

                    group.MapPost("/", async (
                        CreateOrderCommand command,
                        IMediator mediator,
                        CancellationToken ct) =>
                    {
                        var result = await mediator.Send(command, ct);
                        return result.IsSuccess
                            ? Results.Created($"/api/v1/orders/{result.Value}", result.Value)
                            : result.ToProblemDetails();
                    })
                    .Produces<Guid>(StatusCodes.Status201Created)
                    .ProducesValidationProblem();

                    group.MapGet("/{id:guid}", async (Guid id, IMediator mediator, CancellationToken ct) =>
                    {
                        var result = await mediator.Send(new GetOrderQuery(id), ct);
                        return result.IsSuccess ? Results.Ok(result.Value) : result.ToProblemDetails();
                    })
                    .Produces<OrderDto>()
                    .ProducesProblem(StatusCodes.Status404NotFound);
                }
            }
            """,
        ),
        example(
            "csharp",
            """
            public static class ResultExtensions
            {
                public static IResult ToProblemDetails(this Result result)
                {
                    if (result.IsSuccess)
                        throw new InvalidOperationException("Успешный результат не превращается в ошибку");

                    return result.Error.Code switch
                    {
                        "Validation" => Results.ValidationProblem(result.Error.ToDictionary()),
                        "NotFound" => Results.Problem(
                            title: "Объект не найден",
                            detail: result.Error.Message,
                            statusCode: StatusCodes.Status404NotFound),
                        "Conflict" => Results.Problem(
                            title: "Конфликт состояния",
                            detail: result.Error.Message,
                            statusCode: StatusCodes.Status409Conflict),
                        _ => Results.Problem(
                            title: "Внутренняя ошибка",
                            statusCode: StatusCodes.Status500InternalServerError),
                    };
                }
            }
            """,
        ),
        heading("Тесты, которые защищают архитектуру"),
        text(
            "Юнит-тесты покрывают инварианты агрегата, интеграционные — сценарий с базой"
            " данных, контрактные — совместимость API или событий. Отдельно стоит"
            " архитектурный тест: он превращает договорённость о слоях в проверку,"
            " которая падает на этапе сборки.\n\n"
            "Инструмент NetArchTest читает метаданные сборок и позволяет описать"
            " правила декларативно: типы домена не зависят от прикладного и"
            " инфраструктурного слоёв, обработчики живут в пространстве имён"
            " приложения, сущности наследуют базовый агрегат. Тест выполняется за"
            " миллисекунды и работает в CI без окружения.\n\n"
            "Такие тесты ловят самый дорогой класс нарушений — постепенный дрейф"
            " архитектуры. Например, кто-то добавляет ссылку на пакет EF Core в домен,"
            " чтобы «быстро поправить маппинг». Сборка проходит, код работает, но"
            " домен теряет независимость. Архитектурный тест не даст этому уйти в"
            " основную ветку.",
        ),
        example(
            "csharp",
            """
            [Fact]
            public void Domain_ShouldNotDependOnOtherLayers()
            {
                var domain = Types.InAssembly(typeof(Order).Assembly);

                var result = domain
                    .ShouldNot()
                    .HaveDependencyOn("Orders.Application")
                    .AndShouldNot()
                    .HaveDependencyOn("Orders.Infrastructure")
                    .AndShouldNot()
                    .HaveDependencyOn("Microsoft.EntityFrameworkCore")
                    .GetResult();

                Assert.True(result.IsSuccessful, result.FailingTypeNames is null
                    ? string.Empty
                    : string.Join(", ", result.FailingTypeNames));
            }

            [Fact]
            public void AggregateRoots_ShouldHavePrivateConstructor()
            {
                var result = Types.InAssembly(typeof(Order).Assembly)
                    .That().Inherit(typeof(AggregateRoot<>))
                    .Should().HavePrivateConstructor()
                    .GetResult();

                Assert.True(result.IsSuccessful);
            }
            """,
        ),
        text(
            "Вывод при запуске набора архитектурных тестов: \n"
            "Проход сборки: 17 из 17 тестов успешно\n"
            "Нарушения слоёв: не найдено"
        ),
        heading("CI/CD и поставка"),
        text(
            "Конвейер непрерывной интеграции превращает локальные договорённости в"
            " обязательные проверки. Минимальный набор для сервиса на C#: восстановление"
            " пакетов с фиксированной версией SDK, сборка в конфигурации Release с"
            " включёнными анализаторами, юнит-тесты со сбором покрытия, интеграционные"
            " тесты, проверка уязвимых пакетов, сканирование файловой системы и образа,"
            " публикация артефакта и развёртывание по окружениям.\n\n"
            "Настройка TreatWarningsAsErrors меняет отношение к предупреждениям: они"
            " становятся ошибкой сборки, и код с потенциальными null-проблемами не"
            " доходит до основной ветки. Уровень анализа анализаторов Microsoft"
            " повышается постепенно, чтобы команда не утонула в старых нарушениях.\n\n"
            "Развёртывание разделено по веткам: develop ведёт в staging, main — в"
            " production с защищённым окружением и обязательным ревью. Миграции базы"
            " данных применяются отдельным шагом с возможностью отката, а образ"
            " собирается по фиксированной базе, а не по плавающему тегу latest.",
        ),
        example(
            "yaml",
            """
            name: ci

            on:
              push: { branches: [main, develop] }
              pull_request: { branches: [main] }

            jobs:
              build:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: actions/setup-dotnet@v4
                    with:
                      global-json-file: global.json
                  - run: dotnet restore
                  - run: dotnet build --no-restore -c Release
                  - run: dotnet test --no-build -c Release --collect:"XPlat Code Coverage"
                  - run: dotnet list package --vulnerable --include-transitive

              publish:
                needs: build
                if: github.ref == 'refs/heads/main'
                runs-on: ubuntu-latest
                environment: production
                steps:
                  - uses: actions/checkout@v4
                  - run: dotnet publish src/Orders.Api -c Release -o out
                  - run: echo "Публикация образа и деплой через helm"
            """,
        ),
        heading("Наблюдаемость"),
        text(
            "Наблюдаемость строится на трёх сигналах: журналах, метриках и трассах. В"
            " C# метрики удобно объявлять через Meter из System.Diagnostics.Metrics:"
            " счётчик считает созданные заказы, гистограмма фиксирует распределение"
            " суммы, счётчик вверх-вниз показывает число активных заказов. Имена метрик"
            " стабильны, потому что дашборды и алерты ссылаются на них напрямую.\n\n"
            "Трассировка связывает операции: источник ActivitySource создаёт активность"
            " Activity с именем шага и тегами. При экспорте в OTLP трасса объединяет"
            " HTTP-запрос, команду, запрос к базе и вызов платёжного шлюза, поэтому"
            " узкое место видно без чтения логов.\n\n"
            "Проверки работоспособности отвечают на два вопроса. Liveness проверяет,"
            " что процесс жив и не завис. Readiness — что сервис готов принимать"
            " трафик: база доступна, Redis отвечает. Если суммарная проверка включается"
            " в readiness, кратковременный сбой базы выведет узел из балансировщика —"
            " это лучше, чем отвечать ошибкой клиенту.",
        ),
        example(
            "csharp",
            """
            public static class OrdersInstrumentation
            {
                public static readonly Meter Meter = new("Orders.Application");

                public static readonly Counter<long> OrdersCreated =
                    Meter.CreateCounter<long>("orders.created", description: "Создано заказов");

                public static readonly Histogram<double> OrderValue =
                    Meter.CreateHistogram<double>("orders.value", unit: "RUB", description: "Сумма заказа");

                public static readonly Counter<long> OrdersFailed =
                    Meter.CreateCounter<long>("orders.failed", description: "Ошибки обработки");

                public static readonly ActivitySource Source = new("Orders.Application");
            }
            """,
        ),
        example(
            "csharp",
            """
            using var activity = OrdersInstrumentation.Source.StartActivity("CreateOrder");
            activity?.SetTag("customer.id", request.CustomerId.ToString());
            activity?.SetTag("orders.items.count", request.Items.Count);

            try
            {
                var orderId = await HandleCore(request, ct);

                OrdersInstrumentation.OrdersCreated.Add(1);
                OrdersInstrumentation.OrderValue.Record((double)order.Total);
                activity?.SetStatus(ActivityStatusCode.Ok);
                return Result.Success(orderId);
            }
            catch (Exception ex)
            {
                OrdersInstrumentation.OrdersFailed.Add(1);
                activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
                throw;
            }
            """,
        ),
        heading("Документация и эксплуатация"),
        text(
            "Документация — часть программного продукта, и её тоже ревьюят. Запись об"
            " архитектурном решении (ADR) фиксирует контекст, выбранный вариант и"
            " последствия. Через полгода вопрос «почему здесь MediatR, а не прямой"
            " вызов» получает ответ в репозитории, а не в переписке.\n\n"
            "Runbook — инструкция для дежурного: симптом, как диагностировать, что"
            " делать в каждом из типовых случаев и как предотвратить повторение."
            " Хороший runbook начинается с наблюдаемых признаков — роста метрики,"
            " алерта, застрявшего статуса — и не требует знания внутренностей сервиса.\n\n"
            "Обслуживание зависимости — регулярный процесс. Dependabot и обновление"
            " пакетов мелкими шагами снижают риск внезапного крупного обновления."
            " Профилирование в продакшене через dotnet-counters, dotnet-trace и"
            " dotnet-dump отвечает на вопросы о нагрузке, а план ёмкости фиксирует"
            " базовые значения CPU, памяти и соединений, чтобы отличать деградацию"
            " от нормального роста.",
        ),
        example(
            "markdown",
            """
            # ADR 001: Слоистая архитектура сервиса заказов

            **Статус**: принято

            ## Контекст
            Сервис заказов развивается быстрее, чем его инфраструктура. Нужна
            возможность менять базу данных и платёжный провайдер без правок правил
            расчёта заказа.

            ## Решение
            Домен, прикладной слой, инфраструктура и API разнесены по отдельным
            сборкам. Зависимости направлены к домену.

            ## Последствия
            Положительные: домен тестируется без базы; интеграции заменяемы.
            Отрицательные: больше проектов и конфигурации при старте.
            Смягчение: шаблон решения и архитектурные тесты в CI.
            """,
        ),
        example(
            "markdown",
            """
            # Runbook: заказы застряли в статусе Pending

            ## Признаки
            Метрика orders.failed растёт, очередь orders:pending не убывает.

            ## Диагностика
            1. dotnet-counters monitor -p <PID> --counters System.Runtime
            2. Проверить глубину очереди в Redis и блокировки в PostgreSQL.
            3. Найти в журналах повторяющиеся исключения платёжного шлюза.

            ## Действия
            - Сбой базы: перезапуск worker-ов после восстановления связи.
            - Недоступен шлюз: включить резервный режим, уведомить дежурного.
            - Дедлок: снять блокирующий запрос, проверить индексы.

            ## Профилактика
            Ключи идемпотентности, предохранитель на платёжный шлюз, распределённая
            блокировка обработки заказа.
            """,
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Логика в контроллере или endpoint-е", "Правила дублируются, домен пустой, тесты требуют HTTP", "Сценарий в обработчике, правила в агрегате, endpoint только переводит результат"],
                ["Ссылка на EF Core в Domain", "Домен зависит от ORM, тесты требуют базы", "Использовать IEntityTypeConfiguration в Infrastructure, архитектурный тест на запрет ссылки"],
                ["Публичные сеттеры у сущности", "Инварианты обходятся извне", "Приватные сеттеры, фабричный метод и методы-команды"],
                ["Доменные события до SaveChanges", "Внешние системы узнают о заказе, которого нет в базе", "Сохранить транзакцию, затем отправить события и очистить список"],
                ["Entity Framework на горячем чтении", "Лишний трекинг и материализация пишут избыточные запросы", "AsNoTracking и проекция в DTO для запросов"],
                ["Health check с проверкой базы в liveness", "Перезапуск pod при кратком сбое базы", "Базу проверять в readiness, liveness оставить лёгким"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняются в собственном репозитории: создайте решение из четырёх"
            " проектов и одного тестового, затем добавляйте функции по шагам. После"
            " каждого шага сборка должна проходить без предупреждений при"
            " TreatWarningsAsErrors."
        ),
        numbered(
            "Структура: создайте решение с проектами Domain, Application, Infrastructure, Api и ArchitectureTests, задайте ссылки строго внутрь и добавьте global.json с фиксированной версией SDK.",
            "Домен: реализуйте агрегат Order с фабричным методом, операциями AddItem, Confirm и Cancel, доменным исключением и списком событий только для чтения. Покройте инварианты юнит-тестами.",
            "Прикладной слой: добавьте команду CreateOrder и обработчик, возвращающий Result, и поведение валидации через FluentValidation для проверки количества и цены.",
            "Инфраструктура: настройте DbContext с конфигурацией заказа, владением адресом и интерсептором аудита, затем создайте миграцию и проверьте схему.",
            "API и CI: опишите Minimal API с версией /api/v1, ProblemDetails и проверками health, затем настройте GitHub Actions с тестами, сканированием уязвимых пакетов и публикацией артефакта.",
        ),
        text(
            "Ожидаемый результат после первого запуска интеграционного сценария: \n"
            "POST /api/v1/orders -> 201 Created\n"
            "GET  /api/v1/orders/{id} -> 200 OK, status Pending\n"
            "POST /api/v1/orders/{id}/confirm -> 200 OK, status Confirmed\n"
            "POST /api/v1/orders/{id}/confirm повторно -> 409 Conflict"
        ),
        callout(
            "success",
            "Порядок выполнения",
            "Не начинайте с инфраструктуры. Сначала доведите домен и обработчик с тестами в памяти, и только потом подключайте EF Core, HTTP и CI: так ошибки в правилах всплывут раньше, чем их закроют фреймворки.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему Domain не должен ссылаться на EF Core?",
            "В чём разница между валидацией в поведении и инвариантом в агрегате?",
            "Почему доменные события отправляются после SaveChanges, а не до него?",
            "Зачем в запросах чтения используют AsNoTracking и проекцию в DTO?",
            "Какой проверке работоспособности место в readiness, а какой — в liveness?",
        ),
        heading("Ответы", 3),
        numbered(
            "Ссылка на ORM тянет в домен механизмы хранения, ломает тестируемость без базы и нарушает независимость модели от инфраструктуры.",
            "Поведение проверяет форму входящего запроса и прерывает конвейер до вызова обработчика; инвариант защищает бизнес-правило при любом вызове доменного метода.",
            "Если событие отправлено раньше, внешние системы получают уведомление о заказе, который может не сохраниться из-за отката транзакции.",
            "Трекинг не нужен для чтения, он создаёт лишнюю работу ChangeTracker; проекция в DTO уменьшает объём данных и материализует только нужные поля.",
            "Готовность принимать трафик, включая доступность базы, — для readiness; простая проверка, что процесс жив, — для liveness.",
        ),
        heading("Итоги"),
        bullets(
            "Слои задаются ссылками проектов: Domain без зависимостей, Application на Domain, Infrastructure на оба, API на все.",
            "Инварианты живут в агрегате, создание идёт через фабричные методы, коллекции отдаются только для чтения.",
            "CQRS разделяет команды и запросы, поперечные задачи выносятся в поведения конвейера.",
            "EF Core настраивается конфигурациями и интерсепторами, домен не содержит ORM-атрибутов.",
            "API переводит результат в HTTP и ProblemDetails со стабильными кодами ошибок.",
            "Архитектурные тесты и CI-проверки делают правила обязательными, а не рекомендацией.",
            "Метрики, трассы и health checks являются частью контракта сервиса.",
            "ADR и runbook снижают стоимость эксплуатации и сохраняют решения команды.",
        ),
        heading("Что дальше"),
        text(
            "Курс завершён, но работа над проектом продолжается. Следующий разумный шаг —"
            " вынести один из сценариев в отдельный сервис и сравнить стоимость"
            " монолита и разделения на практике. Параллельно полезно взять реальный"
            " профиль нагрузки: соберите базовые бенчмарки, настройте алерты на"
            " регрессию и защититесь от изменений платёжного шлюза политиками"
            " устойчивости. Документируйте каждое значимое решение в ADR — тогда"
            " проект останется понятным не только вам."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "eShopOnContainers как большой пример приложения — github.com/dotnet-architecture/eShopOnContainers",
            "Руководство по микросервисам на .NET — learn.microsoft.com/dotnet/architecture/microservices",
            "Шаблон записей об архитектурных решениях — adr.github.io",
            "Документация OpenTelemetry для .NET — opentelemetry.io/docs/languages/net",
            "Каталог правил анализаторов .NET — learn.microsoft.com/dotnet/fundamentals/code-analysis/quality-rules",
        ),
    ],
}
