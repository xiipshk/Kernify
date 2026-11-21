"""Урок 3.9 курса C#: тестирование и надёжность."""

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
    "topic_order": 9,
    "name": "3.9. Тестирование и надёжность",
    "slug": "csharp-3-9-тестирование-и-надёжность",
    "short_description": (
        "Пирамида тестов на практике: unit с Moq и FluentAssertions, интеграционные "
        "тесты с Testcontainers и WebApplicationFactory, контрактное и property-based "
        "тестирование, бенчмарки в CI и политики Polly для отказоустойчивого сервиса."
    ),
    "topic_name": "Тестирование и надёжность",
    "topic_description": (
        "Как строить набор тестов, который ловит ошибки на ранних этапах и не тормозит "
        "разработку: изолированные unit-тесты с тестовыми двойниками, интеграционные "
        "тесты с реальной инфраструктурой, consumer-driven контракты, генерация входных "
        "данных через FsCheck, мутационное тестирование и защита от сбоев сети через "
        "retry, circuit breaker, timeout и fallback."
    ),
    "learning_objectives": [
        "Строить пирамиду тестов и выбирать уровень проверки для каждого сценария",
        "Писать unit-тесты по шаблону Arrange-Act-Assert с Moq и FluentAssertions",
        "Поднимать интеграционные тесты с Testcontainers и WebApplicationFactory",
        "Заключать контракты между сервисами через consumer-driven testing",
        "Формулировать свойства функции и проверять их через property-based testing",
        "Встраивать бенчмарки и мутационное тестирование в конвейер CI",
        "Проектировать политики Polly: retry с backoff, circuit breaker, timeout, bulkhead и fallback",
        "Строить метрики надёжности и находить слабые места через chaos engineering",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "csharp",
        "тестирование",
        "xunit",
        "testcontainers",
        "fscheck",
        "polly",
        "надёжность",
    ],
    "starter_code": code(
        r"""
        public sealed class PriceCalculator
        {
            public decimal Apply(decimal price, int quantity, decimal discountPercent)
            {
                if (price < 0)
                    throw new ArgumentOutOfRangeException(nameof(price));
                if (quantity <= 0)
                    throw new ArgumentOutOfRangeException(nameof(quantity));
                if (discountPercent is < 0 or > 100)
                    throw new ArgumentOutOfRangeException(nameof(discountPercent));

                var subtotal = price * quantity;
                return Math.Round(subtotal * (1 - discountPercent / 100m), 2);
            }
        }
        """
    ),
    "hints": [
        "Unit-тест проверяет одно поведение и не обращается к сети, файлам или часам. Всё внешнее подменяется интерфейсом.",
        "Мокируйте только внешние зависимости. Если для теста простого класса понадобился мок — вероятно, класс нарушает единственную ответственность.",
        "Для политик Polly используйте виртуальное время (Microsoft.Extensions.TimeProvider.Testing), иначе тесты с задержками станут медленными и нестабильными.",
        "Property-based тест формулирует закон (например, «кодирование и декодирование возвращает исходное значение»), а FsCheck подбирает данные и сам ищет контрпример.",
    ],
    "content": [
        text(
            "Тесты позволяют менять код быстро и с уверенностью — это инструмент, "
            "а не формальность ради покрытия. Зрелый проект держит несколько уровней: "
            "unit-тесты на бизнес-правила, интеграционные на инфраструктуру, "
            "контрактные на стыки между сервисами, бенчмарки на горячие участки.\n\n"
            "Второй герой урока — надёжность. Сеть моргает, база отвечает с задержкой, "
            "поставщик неделю отдаёт 503; политики повторов, размыкания цепи и "
            "тайм-аутов превращают жёсткий отказ в управляемую деградацию, и их тоже "
            "нужно тестировать — иначе они срабатывают впервые в момент инцидента.\n\n"
            "Примеры рассчитаны на .NET 8 с xunit, Moq, FluentAssertions, "
            "Testcontainers, FsCheck и Polly."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "выбирать уровень теста под задачу и формулировать проверяемое утверждение;",
            "писать unit-тесты по шаблону Arrange-Act-Assert с Moq и FluentAssertions;",
            "поднимать интеграционные тесты с Testcontainers и WebApplicationFactory;",
            "заключать consumer-driven контракты через Pact и объяснять, что они ловят;",
            "формулировать свойства и проверять их на сгенерированных данных через FsCheck;",
            "встраивать BenchmarkDotNet и Stryker.NET в CI с проверкой регрессий;",
            "строить цепочки политик Polly: retry, circuit breaker, timeout и fallback;",
            "проектировать метрики надёжности и проверять защиту через chaos engineering.",
        ),
        heading("Пирамида тестов и что она защищает"),
        text(
            "Пирамида тестов — модель, где основание составляют быстрые изолированные "
            "проверки, а вершину — редкие и дорогие сквозные сценарии. Чем выше "
            "уровень, тем медленнее и нестабильнее тест; чем ниже — тем быстрее "
            "обратная связь и точнее локализация дефекта.\n\n"
            "Unit-тест проверяет один класс в памяти процесса, все внешние зависимости "
            "заменены двойниками. Интеграционный тест проверяет код вместе с настоящей "
            "инфраструктурой: базой, HTTP-сервером, брокером. Контрактный тест "
            "проверяет совместимость двух сервисов без их одновременного запуска. "
            "Сквозной проходит путь пользователя через всю систему, бенчмарк измеряет "
            "производительность, мутационный тест — качество самих тестов.\n\n"
            "Ориентир: десятки unit-тестов на один интеграционный и единицы сквозных "
            "на весь продукт; полный набор локально должен проходить за минуты."
        ),
        table(
            ["Уровень", "Что проверяет", "Скорость", "Типичные инструменты"],
            [
                ["Unit", "Правила и ветвления одного класса", "Миллисекунды", "xUnit, Moq, FluentAssertions"],
                ["Интеграционный", "Код вместе с БД и HTTP-сервером", "Секунды", "Testcontainers, WebApplicationFactory"],
                ["Контрактный", "Совместимость сторон API", "Секунды", "Pact"],
                ["Сквозной", "Сценарий пользователя целиком", "Минуты", "Playwright, HttpClient"],
                ["Performance", "Время и аллокации на операцию", "Минуты", "BenchmarkDotNet"],
                ["Mutation", "Способность тестов ловить дефекты", "Минуты", "Stryker.NET"],
            ],
        ),
        callout(
            "info",
            "Пирамида — не догма",
            "В сервисах с тонкой доменной логикой разумно сместить акцент на "
            "интеграционные тесты: они проверяют то, что реально ломается — "
            "маппинг, SQL-запросы, сериализацию. Форма набора должна следовать "
            "за рисками продукта, а не за учебной картинкой."
        ),
        heading("Unit-тесты: шаблон AAA и FluentAssertions"),
        text(
            "Шаблон Arrange-Act-Assert делит тест на три части: подготовка данных, "
            "действие, проверка результата. Тестовый двойник — объект, заменяющий "
            "настоящую зависимость: заглушка (stub) отдаёт заданный ответ, а мок "
            "(mock) дополнительно проверяет, что к нему обратились с ожидаемыми "
            "аргументами. Moq создаёт двойники по интерфейсу через `new Mock<T>()`, "
            "FluentAssertions даёт читаемые цепочки проверок, а имя теста строится "
            "по схеме «Метод_Сценарий_Ожидание».\n\n"
            "Код под тест: сервис создания заказа считает сумму и сохраняет заказ."
        ),
        example(
            "csharp",
            """
            public sealed record OrderItem(Guid ProductId, int Quantity, decimal Price);

            public sealed record CreateOrderCommand(Guid CustomerId, IReadOnlyList<OrderItem> Items);

            public interface IOrderRepository
            {
                Task<Guid> AddAsync(Order order, CancellationToken ct);
            }

            public interface IEmailService
            {
                Task SendConfirmationAsync(Guid orderId, CancellationToken ct);
            }

            public sealed class OrderService
            {
                private readonly IOrderRepository _repository;
                private readonly IEmailService _email;

                public OrderService(IOrderRepository repository, IEmailService email)
                {
                    _repository = repository;
                    _email = email;
                }

                public async Task<Guid> CreateAsync(CreateOrderCommand command, CancellationToken ct)
                {
                    if (command.Items.Count == 0)
                        throw new ArgumentException("Заказ не может быть пустым.", nameof(command));

                    var order = new Order
                    {
                        CustomerId = command.CustomerId,
                        Items = command.Items.ToList(),
                        Total = command.Items.Sum(i => i.Price * i.Quantity),
                    };

                    var id = await _repository.AddAsync(order, ct);
                    await _email.SendConfirmationAsync(id, ct);
                    return id;
                }
            }
            """,
        ),
        text(
            "Тест ниже подменяет репозиторий и почту и проверяет два факта: "
            "сервис вернул непустой идентификатор и передал в репозиторий заказ "
            "с вычисленной суммой."
        ),
        example(
            "csharp",
            """
            public class OrderServiceTests
            {
                private readonly Mock<IOrderRepository> _repository = new();
                private readonly Mock<IEmailService> _email = new();
                private readonly OrderService _service;

                public OrderServiceTests()
                {
                    _service = new OrderService(_repository.Object, _email.Object);
                }

                [Fact]
                public async Task CreateAsync_ValidCommand_SavesAndNotifies()
                {
                    // Arrange
                    var customerId = Guid.NewGuid();
                    var command = new CreateOrderCommand(customerId, new[]
                    {
                        new OrderItem(Guid.NewGuid(), Quantity: 2, Price: 10.5m),
                        new OrderItem(Guid.NewGuid(), Quantity: 1, Price: 4.0m),
                    });

                    _repository
                        .Setup(r => r.AddAsync(It.IsAny<Order>(), It.IsAny<CancellationToken>()))
                        .ReturnsAsync(Guid.Parse("6f9619ff-8b86-d011-b42d-00c04fc964ff"));

                    // Act
                    var id = await _service.CreateAsync(command, CancellationToken.None);

                    // Assert
                    id.Should().Be(Guid.Parse("6f9619ff-8b86-d011-b42d-00c04fc964ff"));

                    _repository.Verify(r => r.AddAsync(
                        It.Is<Order>(o => o.CustomerId == customerId && o.Total == 25.0m),
                        It.IsAny<CancellationToken>()),
                        Times.Once);

                    _email.Verify(e => e.SendConfirmationAsync(id, It.IsAny<CancellationToken>()),
                        Times.Once);
                }
            }
            """,
        ),
        text(
            "Вывод: тест проходит: 2 × 10.5 + 1 × 4.0 = 25.0, и именно это значение "
            "проверяет `It.Is<Order>`. Если формула изменится без правки теста, "
            "упадёт конкретная проверка суммы. Не вызывайте `Verify` с `It.IsAny` "
            "там, где аргумент важен."
        ),
        heading("Testcontainers: интеграция с реальной базой"),
        text(
            "Unit-тест не расскажет, что EF Core сгенерировал неверный SQL или "
            "колонка объявлена с неверной длиной. Testcontainers поднимает "
            "контейнер Docker прямо из кода теста и отдаёт строку подключения. "
            "Класс-основа реализует `IAsyncLifetime`: `InitializeAsync` создаёт "
            "окружение один раз на набор, `DisposeAsync` останавливает контейнер.\n\n"
            "Строку подключения нельзя проектировать вручную: порт выбирает "
            "Docker, и `GetConnectionString()` возвращает актуальное значение. "
        ),
        example(
            "csharp",
            """
            using Microsoft.AspNetCore.Mvc.Testing;
            using Microsoft.Extensions.DependencyInjection;
            using Testcontainers.PostgreSql;
            using Xunit;

            public class IntegrationTestBase : IAsyncLifetime
            {
                private readonly PostgreSqlContainer _db = new PostgreSqlBuilder()
                    .WithImage("postgres:16-alpine")
                    .WithDatabase("testdb")
                    .WithUsername("test")
                    .WithPassword("test")
                    .Build();

                protected WebApplicationFactory<Program> Factory { get; private set; } = null!;

                public async Task InitializeAsync()
                {
                    await _db.StartAsync();

                    Factory = new WebApplicationFactory<Program>()
                        .WithWebHostBuilder(builder =>
                        {
                            builder.ConfigureServices(services =>
                            {
                                // Убираем рабочую регистрацию контекста и ставим тестовую строку.
                                var descriptor = services.SingleOrDefault(
                                    d => d.ServiceType == typeof(DbContextOptions<AppDbContext>));
                                if (descriptor is not null)
                                    services.Remove(descriptor);

                                services.AddDbContext<AppDbContext>(options =>
                                    options.UseNpgsql(_db.GetConnectionString()));
                            });
                        });

                    using var scope = Factory.Services.CreateScope();
                    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
                    await db.Database.MigrateAsync();
                }

                public async Task DisposeAsync() => await _db.DisposeAsync();
            }

            public class UsersApiTests : IntegrationTestBase
            {
                [Fact]
                public async Task GetUsers_EmptyDatabase_ReturnsOkWithEmptyArray()
                {
                    var client = Factory.CreateClient();

                    var response = await client.GetAsync("/api/users");

                    response.StatusCode.Should().Be(HttpStatusCode.OK);
                    var body = await response.Content.ReadFromJsonAsync<UserDto[]>();
                    body.Should().NotBeNull().And.BeEmpty();
                }
            }
            """,
        ),
        text(
            "Вывод: `Passed! - Failed: 0, Passed: 1, Skipped: 0, Total: 1, "
            "Duration: 4 s` — почти всё время уходит на запуск контейнера. "
            "Окружение поднимается в `InitializeAsync` один раз на набор; для "
            "нескольких наборов используйте `ICollectionFixture`.\n\n"
            "Класс `Program` должен иметь модификатор `public partial`, иначе "
            "`WebApplicationFactory<Program>` не скомпилируется: добавьте в конец "
            "`Program.cs` строку `public partial class Program { }`."
        ),
        callout(
            "warning",
            "Testcontainers требует Docker",
            "Если на агенте CI нет Docker (например, в некоторых песочницах "
            "macOS-раннеров), интеграционные тесты нужно явно отсеивать через "
            "trait `Category=Integration` и запускать отдельной стадией. Иначе "
            "пайплайн будет красным по причинам, не связанным с кодом."
        ),
        heading("Подмена окружения через WebApplicationFactory"),
        text(
            "`WebApplicationFactory` решает обратную задачу: интеграционный тест "
            "API без Docker. Наследник фабрики переопределяет `ConfigureWebHost`: "
            "регистрирует Fake-реализации платежей и почты, переключает базу на "
            "in-memory и выставляет среду `Testing`.\n\n"
            "Fake — не мок: он ведёт себя как настоящий сервис, но записывает "
            "вызовы в список и всегда отвечает успехом. Такой объект проходит "
            "реальный HTTP-путь с маршрутизацией, валидацией и сериализацией, "
            "оставаясь быстрым и детерминированным."
        ),
        example(
            "csharp",
            """
            public sealed class FakePaymentGateway : IPaymentGateway
            {
                public List<(Guid OrderId, decimal Amount)> Charges { get; } = new();

                public Task<bool> ChargeAsync(Guid orderId, decimal amount, CancellationToken ct)
                {
                    Charges.Add((orderId, amount));
                    return Task.FromResult(true);
                }
            }

            public class OrdersApiFactory : WebApplicationFactory<Program>
            {
                public FakePaymentGateway Payments { get; } = new();

                protected override void ConfigureWebHost(IWebHostBuilder builder)
                {
                    builder.UseEnvironment("Testing");
                    builder.ConfigureServices(services =>
                    {
                        services.AddSingleton<IPaymentGateway>(Payments);
                        services.AddSingleton<IEmailService, FakeEmailService>();

                        services.RemoveAll<DbContextOptions<AppDbContext>>();
                        services.AddDbContext<AppDbContext>(o => o.UseInMemoryDatabase("TestDb"));
                    });
                }
            }

            public class OrdersApiTests : IClassFixture<OrdersApiFactory>
            {
                private readonly OrdersApiFactory _factory;
                private readonly HttpClient _client;

                public OrdersApiTests(OrdersApiFactory factory)
                {
                    _factory = factory;
                    _client = factory.CreateClient();
                }

                [Fact]
                public async Task PostOrder_ValidRequest_ReturnsCreatedAndChargesPayment()
                {
                    var request = new
                    {
                        Email = "test@test.com",
                        Items = new[] { new { ProductId = Guid.NewGuid(), Quantity = 2 } },
                    };

                    var response = await _client.PostAsJsonAsync("/api/orders", request);

                    response.StatusCode.Should().Be(HttpStatusCode.Created);
                    response.Headers.Location.Should().NotBeNull();
                    _factory.Payments.Charges.Should().ContainSingle();
                }
            }
            """,
        ),
        text(
            "Вывод: `Passed! - Failed: 0, Passed: 1` без Docker и сети. Ответ 201 "
            "и заголовок `Location` подтверждают корректную обработку команды. "
            "`services.RemoveAll<T>()` удаляет рабочую регистрацию контекста, "
            "чтобы не осталось боевой строки подключения."
        ),
        heading("Контрактное тестирование: Pact"),
        text(
            "Два сервиса могут пройти свои тесты и не договориться: потребитель "
            "ждёт поле `email`, а поставщик переименовал его в `emailAddress`. "
            "Consumer-driven contract testing переворачивает процесс: потребитель "
            "(consumer) описывает ожидания, из них генерируется pact-файл — "
            "JSON-описание запросов и ответов, — а поставщик (provider) проверяет "
            "свои ответы против него; Pact Broker распространяет файл.\n\n"
            "В тесте потребителя задаётся мок-сервер, воспроизводящий сценарий "
            "поставщика. Если клиент читает отсутствующее поле, тест падает "
            "сразу, а не в продакшене."
        ),
        example(
            "csharp",
            """
            public class UserApiConsumerTests
            {
                private readonly IPactBuilderV3 _pact;

                public UserApiConsumerTests()
                {
                    _pact = Pact.V3("UserConsumer", "UserProvider", new PactConfig
                    {
                        PactDir = Path.Combine("..", "..", "..", "..", "pacts"),
                        LogLevel = PactLogLevel.Information,
                    });
                }

                [Fact]
                public async Task GetUser_ExistingUser_ReturnsParsedUser()
                {
                    var expected = new UserDto(Guid.NewGuid(), "John", "john@example.com");

                    _pact.UponReceiving("Запрос существующего пользователя")
                        .Given("Пользователь с id существует", new { id = expected.Id })
                        .WithRequest(HttpMethod.Get, $"/api/users/{expected.Id}")
                        .WillRespond()
                        .WithStatus(HttpStatusCode.OK)
                        .WithJsonBody(expected);

                    await _pact.VerifyAsync(async ctx =>
                    {
                        using var client = new HttpClient { BaseAddress = ctx.MockServerUri };
                        var response = await client.GetAsync($"/api/users/{expected.Id}");

                        response.StatusCode.Should().Be(HttpStatusCode.OK);
                        var user = await response.Content.ReadFromJsonAsync<UserDto>();
                        user.Should().BeEquivalentTo(expected);
                    });
                }
            }
            """,
        ),
        text(
            "Вывод: `Passed!` и файл `userconsumer-userprovider.json`: путь, метод, "
            "статус, структура тела. Если поставщик изменит формат `UserDto`, "
            "проверка контракта покажет, какой потребитель сломается. Контракты "
            "проверяют форму, а не бизнес-правила."
        ),
        heading("Property-based testing: FsCheck"),
        text(
            "Обычный тест проверяет пример: `ApplyDiscount(100, 10) == 90`. "
            "Property-based testing проверяет закон, справедливый для всех входов: "
            "«скидка не делает сумму отрицательной» или «разбор сериализованного "
            "значения возвращает исходное». FsCheck генерирует сотни входов, ищет "
            "минимальный контрпример сужением (shrinking) и показывает его в отчёте.\n\n"
            "Хорошее свойство описывает инвариант — идемпотентность, сохранение "
            "длины, эквивалентность реализаций, — а не повторяет тело метода. "
            "`[Property]` заменяет `[Fact]` и по умолчанию делает сто прогонов."
        ),
        example(
            "csharp",
            """
            using FsCheck;
            using FsCheck.Xunit;

            public class PriceProperties
            {
                private readonly PriceCalculator _calc = new();

                [Property(MaxTest = 500)]
                public bool Discount_NeverExceedsSubtotal(int price, int quantity, int discount)
                {
                    // Ограничиваем вход разумными границами домена.
                    price = Math.Abs(price % 10_000);
                    quantity = Math.Abs(quantity % 100) + 1;
                    discount = Math.Abs(discount % 101);

                    var result = _calc.Apply(price, quantity, discount);
                    return result >= 0 && result <= (decimal)price * quantity;
                }

                [Property]
                public bool ZeroDiscount_ReturnsExactSubtotal(int price, int quantity)
                {
                    price = Math.Abs(price % 1_000) + 1;
                    quantity = Math.Abs(quantity % 50) + 1;

                    return _calc.Apply(price, quantity, 0) == (decimal)price * quantity;
                }
            }
            """,
        ),
        text(
            "Вывод: `Passed! - Failed: 0, Passed: 2`. Если бы в `Apply` появилось "
            "деление на `(100 - discount)` без проверки границы, FsCheck нашёл бы "
            "вход `discount = 100` и сообщил минимальный контрпример вида "
            "`Falsifiable, after 7 tests: Original: 12, 3, 100`.\n\n"
            "Границы домена отсекаются внутри свойства: FsCheck генерирует "
            "`int.MinValue`, где `Math.Abs` бросает `OverflowException`."
        ),
        callout(
            "success",
            "Где property-based тесты окупаются",
            "Алгоритмы сжатия и хеширования, парсеры, сериализация, "
            "денежные расчёты, машины состояний и любая бизнес-логика с "
            "инвариантами. На UI и тривиальных геттерах они почти не дают выгоды."
        ),
        heading("Мутационное тестирование: Stryker.NET"),
        text(
            "Сто процентов покрытия не означают, что тесты что-то проверяют. "
            "Мутационное тестирование отвечает на другой вопрос: упадёт ли тест, "
            "если намеренно испортить код. Stryker.NET по очереди меняет в IL "
            "`+` на `-`, инвертирует условия и удаляет вызовы, запуская набор.\n\n"
            "Результат — mutation score, доля убитых мутантов. Выживший мутант "
            "показывает место, где поведение не проверяется; порог для домена "
            "ставят в 80–90 процентов. Настройка `stryker-config.json` живёт в "
            "тестовом проекте, полный прогон запускают ночью в CI."
        ),
        example(
            "json",
            """
            {
              "stryker-config": {
                "project": "Shop.Domain.csproj",
                "test-projects": [ "Shop.Domain.Tests.csproj" ],
                "mutation-level": "Standard",
                "thresholds": { "high": 90, "low": 80, "break": 75 },
                "reporters": [ "progress", "html", "dashboard" ],
                "ignore-mutations": [ "string" ]
              }
            }
            """,
        ),
        text(
            "Вывод фрагмента консоли: `File: PriceCalculator.cs`, "
            "`Mutant: 12 of 48`, `Killed: 11`, `Survived: 1`, "
            "`Mutation score: 91.67% (green)`. Если доля упадёт ниже порога "
            "`break`, Stryker завершится с ненулевым кодом и сборка станет "
            "красной. Так требование «тесты проверяют поведение» становится "
            "исполняемым, а не декларацией в code review."
        ),
        heading("Бенчмарки и защита от регрессий"),
        text(
            "Обычные тесты отвечают «работает или нет», бенчмарки — «за сколько». "
            "BenchmarkDotNet запускает метод много раз, отбрасывает прогрев и "
            "печатает статистику; `[MemoryDiagnoser]` добавляет аллокации и "
            "коллекции Gen 0. Для обнаружения регрессий нужен baseline — "
            "результат заведомо хорошей сборки. Сравнение в CI учитывает шум: "
            "на общих раннерах разница в 10–15 процентов ничего не значит."
        ),
        example(
            "csharp",
            """
            using BenchmarkDotNet.Attributes;
            using BenchmarkDotNet.Running;

            public class PriceCalculatorBenchmarks
            {
                private readonly PriceCalculator _calc = new();

                [Params(1, 100, 10_000)]
                public int Quantity { get; set; }

                [Benchmark]
                public decimal Apply()
                    => _calc.Apply(199.99m, Quantity, 7.5m);

                [Benchmark(Baseline = true)]
                public decimal ManualTotal()
                    => Math.Round(199.99m * Quantity * 0.925m, 2);
            }

            public static class EntryPoint
            {
                public static void Main(string[] args)
                    => BenchmarkRunner.Run<PriceCalculatorBenchmarks>(args);
            }
            """,
        ),
        text(
            "Сокращённый вывод: `| Method      | Quantity | Mean     | Ratio | "
            "Allocated |`, `| Apply       | 1        | 4.812 ns | 1.002 | "
            "0 B       |`, `| ManualTotal | 1        | 4.801 ns | 1.000 | "
            "0 B       |`. `Ratio` — отношение к baseline: 1.002 означает разницу "
            "в пределах погрешности. Запускайте бенчмарки только в Release."
        ),
        example(
            "yaml",
            """
            name: nightly-benchmarks
            on:
              schedule: [ { cron: "0 3 * * *" } ]

            jobs:
              bench:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: actions/setup-dotnet@v4
                    with:
                      dotnet-version: "8.0.x"

                  - name: Запуск бенчмарков
                    run: dotnet run -c Release --project bench/Bench.csproj

                  - name: Сравнение с эталоном
                    run: >
                      dotnet run --project bench/Compare.csproj --
                      --baseline baseline.json
                      --current BenchmarkDotNet.Artifacts/results/*.json
                      --max-regression 15
            """,
        ),
        text(
            "Вывод шага сравнения: `GetUsersBatch/100: 62.4 ms -> 71.8 ms (+15.1%)`, "
            "`Regression threshold 15% exceeded — exit code 1`. Сборка падает "
            "только на значимой деградации; для критичных сценариев используйте "
            "агент с фиксированной частотой процессора."
        ),
        heading("Надёжность: политики Polly"),
        text(
            "Любой сетевой вызов — ставка на то, что сервис доступен и отвечает "
            "быстро. Политика надёжности (resilience policy) — обёртка вокруг "
            "вызова, задающая реакцию на сбой; Polly предоставляет готовые "
            "политики, которые композируются в цепочку.\n\n"
            "Retry повторяет операцию при временном сбое, экспоненциальный "
            "backoff с джиттером разносит повторы во времени. Circuit breaker "
            "считает сбои и после порога перестаёт вызывать сервис, давая ему "
            "передышку. Timeout ограничивает ожидание, bulkhead — параллелизм, "
            "чтобы один медленный поставщик не занял весь пул. Fallback отдаёт "
            "заранее подготовленный ответ: кэш или значение по умолчанию."
        ),
        example(
            "csharp",
            """
            using Polly;
            using Polly.CircuitBreaker;
            using Polly.Extensions.Http;

            public static class ResiliencePolicies
            {
                public static IAsyncPolicy<HttpResponseMessage> Retry() =>
                    HttpPolicyExtensions
                        .HandleTransientHttpError()
                        .OrResult(r => r.StatusCode == HttpStatusCode.TooManyRequests)
                        .WaitAndRetryAsync(
                            retryCount: 3,
                            sleepDurationProvider: attempt =>
                                TimeSpan.FromMilliseconds(200 * Math.Pow(2, attempt))
                                + TimeSpan.FromMilliseconds(Random.Shared.Next(0, 100)),
                            onRetry: (outcome, delay, attempt, _) =>
                                Console.WriteLine(
                                    $"Повтор {attempt} через {delay.TotalMilliseconds:F0} мс " +
                                    $"({outcome.Result?.StatusCode.ToString() ?? "исключение"})"));

                public static IAsyncPolicy<HttpResponseMessage> CircuitBreaker() =>
                    HttpPolicyExtensions
                        .HandleTransientHttpError()
                        .CircuitBreakerAsync(
                            handledEventsAllowedBeforeBreaking: 5,
                            durationOfBreak: TimeSpan.FromSeconds(30));
            }
            """,
        ),
        text(
            "Вывод при двух 503 подряд: `Повтор 1 через 400 мс (ServiceUnavailable)` "
            "и `Повтор 2 через 800 мс (ServiceUnavailable)`. "
            "`HandleTransientHttpError` ловит 5xx, 408 и сетевые исключения; "
            "4xx повторять бессмысленно, а `OrResult` добавляет 429.\n\n"
            "Порядок обёртывания задаёт семантику: снаружи тайм-аут на весь "
            "вызов, затем retry, внутри — размыкатель цепи, чтобы разомкнутая "
            "цепь останавливала повторы немедленно."
        ),
        example(
            "csharp",
            """
            var pipeline = Policy.WrapAsync(
                Policy.TimeoutAsync<HttpResponseMessage>(TimeSpan.FromSeconds(10)),
                ResiliencePolicies.Retry(),
                ResiliencePolicies.CircuitBreaker());

            builder.Services
                .AddHttpClient<CatalogClient>(c => c.BaseAddress = new Uri("https://catalog.internal"))
                .AddPolicyHandler(pipeline);

            // Регистрация политик как синглтонов, а не создания на каждый запрос:
            // размыкатель хранит состояние счётчиков только в одном экземпляре.
            builder.Services.AddSingleton(pipeline);
            """,
        ),
        text(
            "Вывод при разомкнутой цепи: `BrokenCircuitException: The circuit is "
            "now open and is not allowing calls.` Исключение возникает до сетевого "
            "вызова. Через 30 секунд цепь переходит в полуоткрытое состояние и "
            "пропускает один пробный вызов: успех закрывает её, неудача продлевает "
            "размыкание.\n\n"
            "Политика — состояние, а не чистая функция. Созданный внутри "
            "обработчика размыкатель получит собственный счётчик и никогда не "
            "разомкнётся; храните его синглтоном или в `PolicyRegistry`."
        ),
        callout(
            "danger",
            "Двойные повторы",
            "Retry на клиенте, прокси и сервисе складываются: три попытки "
            "на каждом из трёх уровней дают 27 запросов при одном сбое. "
            "Договоритесь, где живут повторы — обычно на клиенте, — и "
            "снабжайте запросы заголовком идемпотентности на запись."
        ),
        heading("Bulkhead, fallback и тестирование политик"),
        text(
            "Bulkhead ограничивает одновременные вызовы: например, 10 активных "
            "и 20 в очереди, остальные немедленно получают "
            "`BulkheadRejectedException`. Fallback возвращает кэш или пустой "
            "результат вместо исключения.\n\n"
            "Тестировать политики мешает время: реальные паузы делают набор "
            "медленным. Внедряйте `TimeProvider` и проверяйте число попыток и "
            "переходы состояний за миллисекунды."
        ),
        example(
            "csharp",
            """
            using Microsoft.Extensions.Time.Testing;
            using Polly;

            public class RetryPolicyTests
            {
                [Fact]
                public async Task Retry_TransientFailures_AttemptsExactlyFourTimes()
                {
                    var time = new FakeTimeProvider();
                    var calls = 0;

                    var policy = Policy
                        .Handle<HttpRequestException>()
                        .WaitAndRetryAsync(
                            retryCount: 3,
                            sleepDurationProvider: _ => TimeSpan.FromSeconds(1),
                            onRetry: (_, _, _, _) => time.Advance(TimeSpan.FromSeconds(1)));

                    await Assert.ThrowsAsync<HttpRequestException>(() =>
                        policy.ExecuteAsync(async () =>
                        {
                            calls++;
                            await Task.Yield();
                            throw new HttpRequestException("Сбой сети");
                        }));

                    calls.Should().Be(4); // первая попытка и три повтора
                    time.GetUtcNow().Should().BeAfter(DateTimeOffset.UnixEpoch);
                }
            }
            """,
        ),
        text(
            "Вывод: `Passed! - Failed: 0, Passed: 1`. Тест утверждает ровно "
            "четыре попытки и проброс наружу итогового исключения; с "
            "`retryCount = 5` он упадёт с `Expected calls to be 4, but found 6`. "
            "Тот же приём проверяет переход размыкателя из открытого состояния "
            "в полуоткрытое после `durationOfBreak`."
        ),
        heading("Chaos engineering и метрики надёжности"),
        text(
            "Chaos engineering — проверка системы под искусственно внесёнными "
            "неисправностями. Simmy (расширение Polly) внедряет задержки и "
            "исключения с заданной вероятностью: сначала убедитесь, что защита "
            "работает, потом доверьтесь ей в продакшене.\n\n"
            "Эксперимент ограничен явной долей затронутых запросов и конкретным "
            "утверждением; «все запросы успешны» при 30 процентах инъекций "
            "сделает тест плавающим.\n\n"
            "Второй столп — наблюдение: четыре золотых сигнала SRE (latency, "
            "traffic, errors, saturation). Без них деградацию не заметить, "
            "а эффект политики не доказать."
        ),
        example(
            "csharp",
            """
            using Polly.Contrib.Simmy;
            using Polly.Contrib.Simmy.Latency;

            public class ChaosTests : IClassFixture<OrdersApiFactory>
            {
                private readonly HttpClient _client;

                public ChaosTests(OrdersApiFactory factory) => _client = factory.CreateClient();

                [Fact]
                public async Task Api_SurvivesThirtyPercentLatencyInjection()
                {
                    var latency = MonkeyPolicy
                        .InjectLatencyAsync<HttpResponseMessage>(
                            TimeSpan.FromMilliseconds(300),
                            injectionRate: 0.3,
                            enabled: true);

                    var retry = ResiliencePolicies.Retry();

                    var results = await Task.WhenAll(Enumerable.Range(0, 20).Select(_ =>
                        latency.WrapAsync(retry).ExecuteAsync(
                            () => _client.GetAsync("/api/orders"))));

                    results.Count(r => r.IsSuccessStatusCode).Should().BeGreaterThanOrEqualTo(19);
                }
            }
            """,
        ),
        text(
            "Вывод: `Passed! - Failed: 0, Passed: 1`. Около шести из двадцати "
            "вызовов получают задержку, но retry поглощает эффект. Порог, а не "
            "равенство, — иначе тест с вероятностной инъекцией будет плавающим. "
            "В продакшене эксперимент запускают по расписанию с условием остановки."
        ),
        table(
            ["Сигнал", "Что измеряем", "Порог для сервиса заказов", "Что строим"],
            [
                ["Latency", "p50, p95, p99 времени ответа", "p99 < 300 мс", "гистограммы в OpenTelemetry"],
                ["Traffic", "запросы в секунду по эндпоинтам", "пик × 2 без насыщения", "счётчики по маршрутам"],
                ["Errors", "доля ответов 5xx и тайм-аутов", "< 0,1 % за 5 минут", "rate-метрики и алерты"],
                ["Saturation", "загрузка пула, очереди, соединений", "< 70 % лимита bulkhead", "метрики HttpClient и очередей"],
            ],
        ),
        heading("Тестирование и CI"),
        text(
            "Распределяйте уровни по стадиям по стоимости. На каждый коммит — "
            "unit-тесты и контрактные проверки потребителя: они укладываются в "
            "минуты. Интеграционные тесты с Testcontainers — на pull request, "
            "бенчмарки и мутационное тестирование — ночью на выделенном раннере.\n\n"
            "Каждый тест изолирован: порядок выполнения не влияет на результат. "
            "Зависимости вроде текущего времени передавайте через "
            "`TimeProvider` вместо `DateTime.UtcNow`."
        ),
        example(
            "csharp",
            """
            [Fact]
            public async Task GetUser_Retries_DoesNotDependOnRealClock()
            {
                var clock = new FakeTimeProvider(DateTimeOffset.Parse("2026-01-01T00:00:00Z"));
                var sut = new SubscriptionService(clock);

                var active = sut.IsActive(endsAt: DateTimeOffset.Parse("2026-03-01T00:00:00Z"));

                active.Should().BeTrue();

                clock.Advance(TimeSpan.FromDays(90));
                sut.IsActive(DateTimeOffset.Parse("2026-03-01T00:00:00Z")).Should().BeFalse();
            }
            """,
        ),
        text(
            "Вывод: `Passed! - Failed: 0, Passed: 1`. Оба утверждения проверяют "
            "границу подписки без реального ожидания: `SubscriptionService` "
            "принимает `TimeProvider` и зовёт `clock.GetUtcNow()`."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Тесты делят изменяемое состояние", "Результат зависит от порядка запуска, падения невоспроизводимы", "Каждый тест сам создаёт данные, инфраструктура — через fixture"],
                ["Мокают всё подряд", "Тест проверяет реализацию, а не поведение, и ломается при рефакторинге", "Мокают только внешние зависимости: БД, HTTP, время"],
                ["Интеграционные тесты без очистки", "Данные протекают между тестами, тесты влияют друг на друга", "Контейнер с пустой базой или откат транзакции"],
                ["Бенчмарки в Debug", "Замер в десятки раз неверен и ничего не значит", "Только Release без отладчика, на стабильном агенте"],
                ["Политики Polly создаются на каждый запрос", "Счётчики размыкателя обнуляются, цепь никогда не срабатывает", "Синглтон или PolicyRegistry на всё приложение"],
                ["Retry на несколько уровней одновременно", "Один сбой размножается в 27 запросов", "Проектируйте повторы в одном месте, пишите идемпотентные операции"],
                ["Нет свойства для алгоритма", "FsCheck не применяется к парсерам и сериализации, дефект ловится позже", "Опишите инварианты и генерируйте входные данные"],
            ],
        ),
        heading("Практика"),
        text(
            "Создайте тестовое решение: `dotnet new xunit -n Shop.Tests` рядом с "
            "проектом домена и запускайте `dotnet test` после каждого шага."
        ),
        numbered(
            "Напишите unit-тесты на `PriceCalculator.Apply`: корректный расчёт, отрицательная цена, скидка 120 процентов (через `Should().Throw<ArgumentOutOfRangeException>()`).",
            "Добавьте интеграционный тест с Testcontainers: `postgres:16-alpine`, миграции, `GET /api/orders` на пустой базе отдаёт 200 и пустой массив.",
            "Опишите через FsCheck свойство «скидка не больше подытога и не меньше нуля» на 500 прогонах, затем сломайте формулу и убедитесь, что тест упал.",
            "Соберите цепочку Polly из timeout на 5 секунд, retry на 2 попытки и размыкателя на 3 сбоя. Тестом с `FakeTimeProvider` докажите, что после третьего сбоя вызова сети нет.",
            "Настройте `stryker-config.json` для домена, добавьте тесты, убивающие выживших мутантов, и сравните mutation score до и после.",
        ),
        callout(
            "success",
            "Подсказка к заданию 4",
            "Внутренний `Polly`-счётчик размыкателя живёт в экземпляре политики. Сохраните цепочку в поле теста и вызывайте её, а не создавайте заново в каждом итерации — иначе состояние обнулится.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему интеграционный тест не заменяет unit-тест и наоборот?",
            "Чем тестовый двойник `stub` отличается от `mock` и в какой момент проверяется каждый?",
            "Что именно ловит consumer-driven контракт, чего не ловит интеграционный тест?",
            "Зачем в политике retry нужен jitter (случайный разброс), если экспоненциальная задержка уже есть?",
            "Почему размыкатель цепи не работает, если политику создают внутри обработчика HTTP-запроса?",
            "Что означает выживший мутант и почему он не всегда указывает на плохой тест?",
        ),
        heading("Ответы", 3),
        numbered(
            "Unit-тест точно локализует логическую ошибку, но не видит SQL и сериализацию; интеграционный проверяет реальный стык с инфраструктурой, но медленнее и хуже локализует — они закрывают разные риски.",
            "Stub отдаёт заданный ответ и не проверяет вызовы; mock проверяет факт и аргументы вызова через Verify, что обычно делают в конце теста.",
            "Контракт фиксирует форму взаимодействия и ломает сборку поставщика при переименовании поля. Интеграционный тест одного сервиса второй сервис не видит.",
            "Без джиттера все клиенты, упавшие одновременно, повторят вызов синхронно и создадут пиковую нагрузку на восстанавливающийся сервис. Случайный разброс разносит повторы во времени.",
            "Счётчики сбоев и состояние открытой цепи хранятся в экземпляре политики. Новый экземпляр начинается с нуля, поэтому порог сбоя не достигается и вызовы продолжаются.",
            "Выживший мутант показывает место, где изменение поведения осталось незамеченным. Он может быть эквивалентным — не влияющим на результат, — и тогда это особенность мутатора, а не дыра в тестах.",
        ),
        heading("Итоги"),
        bullets(
            "Пирамида тестов: много быстрых unit-тестов, меньше интеграционных, единицы сквозных; форма следует рискам продукта.",
            "Unit-тест строится по Arrange-Act-Assert, проверяет одно поведение и подменяет внешние зависимости двойниками.",
            "Testcontainers поднимает настоящую базу для интеграционных тестов, WebApplicationFactory — HTTP-стек приложения с Fake-сервисами.",
            "Consumer-driven контракты ловят несовместимость API между командами до того, как она станет инцидентом.",
            "Property-based тесты формулируют инварианты, а FsCheck ищет контрпримеры и уменьшает их до минимального вида.",
            "Мутационное тестирование измеряет качество тестов, а бенчмарки в CI — производительность; оба защищают от незаметного ухудшения.",
            "Политики повторов, размыкателя, тайм-аута, bulkhead и fallback превращают жёсткий отказ во внешний сбой в управляемую деградацию.",
            "Политики — состояние: держите их синглтонами, тестируйте с виртуальными часами, не допускайте двойных повторов.",
        ),
        heading("Что дальше"),
        text(
            "Вы умеете проверять код на каждом уровне и проектировать поведение "
            "сервиса под сбои. Следующий шаг — наблюдаемость и работа с "
            "инцидентами: надёжность без телеметрии остаётся набором догадок."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "xUnit, документация — xunit.net",
            "FluentAssertions — fluentassertions.com",
            "Testcontainers for .NET — dotnet.testcontainers.org",
            "Pact .NET — github.com/pact-foundation/pact-net",
            "FsCheck — fscheck.github.io/FsCheck",
            "Polly — github.com/App-vNext/Polly; Simmy — github.com/Polly-Contrib/Simmy",
            "Stryker.NET — stryker-mutator.io/docs/stryker-net",
            "Vladimir Khorikov, «Unit Testing Principles, Practices, and Patterns»",
        ),
    ],
}
