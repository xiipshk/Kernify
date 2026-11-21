"""Урок 8 курса csharp: тестирование и качество."""

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
    "topic_order": 8,
    "name": "2.8. Тестирование и качество",
    "slug": "csharp-2-8-тестирование-и-качество",
    "short_description": (
        "Как выстроить надёжную проверку кода на C#: модульные тесты с xUnit, шаблон "
        "Arrange-Act-Assert, подмена зависимостей, интеграционные тесты, покрытие, "
        "статический анализ и отладка."
    ),
    "topic_name": "Тестирование и качество",
    "topic_description": (
        "Практический разбор обеспечения качества в .NET: тестовые фреймворки xUnit, NUnit "
        "и MSTest, структура теста и его именование, библиотеки подмены Moq и NSubstitute, "
        "интеграционные тесты с Testcontainers и WebApplicationFactory, измерение покрытия, "
        "анализаторы Roslyn, отладка и измерение производительности."
    ),
    "learning_objectives": [
        "Писать модульные тесты на xUnit с атрибутами [Fact], [Theory] и [InlineData]",
        "Строить тесты по шаблону Arrange-Act-Assert и давать им читаемые имена",
        "Проверять исключения и собирать тестовые данные через паттерн Builder",
        "Подменять внешние зависимости через интерфейсы с помощью Moq и NSubstitute",
        "Различать модульные и интеграционные тесты и запускать реальную инфраструктуру в Docker",
        "Измерять покрытие тестами и подключать статические анализаторы и EditorConfig",
        "Отлаживать программы точками останова, условными остановами и дампами памяти",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "csharp",
        "тестирование",
        "xunit",
        "moq",
        "покрытие",
        "качество кода",
    ],
    "starter_code": code(
        r"""
        using Xunit;

        public class Calculator
        {
            public int Add(int a, int b) => a + b;
            public int Divide(int a, int b) => b == 0 ? throw new DivideByZeroException() : a / b;
        }

        public class CalculatorTests
        {
            [Fact]
            public void Add_TwoNumbers_ReturnsSum()
            {
                // Arrange
                var calc = new Calculator();

                // Act
                var result = calc.Add(2, 3);

                // Assert
                Assert.Equal(5, result);
            }
        }
        """
    ),
    "hints": [
        "Один тест проверяет одно поведение: если утверждений два и они про разные сценарии, лучше разделить на два теста.",
        "Подменяйте только внешние зависимости: HTTP, базу данных, файлы, время. Обычные классы и коллекции создавайте как есть.",
        "Имя теста строится по схеме Метод_Сценарий_ОжидаемыйРезультат, например Transfer_InsufficientFunds_ThrowsException.",
        "Для вариаций одного поведения используйте [Theory] с несколькими [InlineData], а не копию [Fact] на каждый случай.",
    ],
    "content": [
        text(
            "Код, который никто не проверяет, рано или поздно ломается. В C# культура проверки "
            "встроена в инструменты платформы .NET: генератор тестовых проектов, единый запуск через "
            "`dotnet test`, встроенные анализаторы Roslyn, отладчик и сборщик покрытия. Тестирование "
            "и качество — это не отдельный этап перед релизом, а постоянная часть разработки.\n\n"
            "Измерение качества начинается с нескольких понятий. **Модульный тест** (unit test) "
            "проверяет отдельную единицу кода — обычно один класс или метод — в изоляции от базы "
            "данных и сети. **Интеграционный тест** проверяет взаимодействие нескольких компонентов, "
            "например репозитория с настоящей базой данных. **Подмена** (mock) — объект, который "
            "имитирует зависимость и позволяет задать ожидаемый ответ. **Покрытие** (code coverage) — "
            "доля строк кода, которые выполнились во время прогона тестов.\n\n"
            "В этом уроке вы построите полный контур качества: от первого теста на xUnit до запуска "
            "реальной базы данных в Docker, от анализаторов, которые ловят ошибки без запуска "
            "программы, до отладки зависшего приложения по дампу памяти."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "писать модульные тесты на xUnit с атрибутами `[Fact]`, `[Theory]` и `[InlineData]`;",
            "строить тесты по шаблону Arrange-Act-Assert и давать им имена вида "
            "`Метод_Сценарий_ОжидаемыйРезультат`;",
            "проверять исключения и готовить тестовые данные через паттерны Builder и Object Mother;",
            "подменять внешние зависимости через интерфейсы с помощью Moq и NSubstitute;",
            "различать модульные и интеграционные тесты и запускать реальную инфраструктуру в Docker;",
            "измерять покрытие, подключать анализаторы Roslyn, EditorConfig и отлаживать программы "
            "точками останова и дампами.",
        ),
        heading("Зачем нужны тесты"),
        text(
            "Модульный тест — это небольшая программа, которая вызывает ваш код и сравнивает "
            "результат с ожидаемым. Ценность тестов не только в поиске ошибок. Тест фиксирует "
            "поведение: если через полгода кто-то изменит расчёт, тест сообщит об этом раньше "
            "пользователя. Тесты позволяют смело менять внутреннее устройство: пока публичное "
            "поведение сохраняется, выпускать правку можно уже через минуту после прогона.\n\n"
            "Кроме того, тесты выступают документацией. Имя `Transfer_InsufficientFunds_ThrowsException` "
            "сразу объясняет, что метод делает при нехватке средств, — точнее комментария, потому что "
            "расхождение с кодом ловится немедленно.\n\n"
            "Тесты разделяют на три уровня по форме пирамиды:\n\n"
            "- Основание — модульные тесты: их много, работают за миллисекунды и не требуют сети.\n"
            "- Середина — интеграционные: проверяют взаимодействие с базой, очередью, HTTP.\n"
            "- Вершина — сквозные (end-to-end), проходящие по всему сценарию. Их мало: они медленные и хрупкие."
        ),
        callout(
            "info",
            "Пирамида тестов",
            "Держите пропорцию примерно 70/20/10: много быстрых модульных тестов, часть интеграционных "
            "и совсем немного сквозных. Если в проекте всё покрыто сквозными тестами, прогон будет "
            "занимать часы, а падение теста не подскажет, какой компонент сломан."
        ),
        heading("Фреймворк xUnit: первый тест"),
        text(
            "xUnit — тестовый фреймворк, рекомендованный для современных приложений .NET. Он "
            "разворачивается как обычная библиотека через NuGet. Каждый тестовый класс — это "
            "публичный класс, каждый тест — публичный метод без параметров, помеченный атрибутом "
            "`[Fact]`. Атрибут — это метка для фреймворка, которая сообщает: этот метод нужно "
            "запустить и посчитать его успех.\n\n"
            "Проверки выполняются статическим классом `Assert`. Метод `Assert.Equal` сравнивает "
            "фактическое значение с ожидаемым и бросает исключение, если они различаются. Именно "
            "исключение срывает тест: никакого особого кода возврата не нужно. Если исключение не "
            "брошено, тест считается пройденным.\n\n"
            "Для запуска создайте отдельный проект `dotnet new xunit -n App.Tests`, добавьте ссылку "
            "на тестируемую библиотеку и выполните `dotnet test`."
        ),
        example(
            "csharp",
            r"""
            using Xunit;

            public class Calculator
            {
                public int Add(int a, int b) => a + b;
            }

            public class CalculatorTests
            {
                [Fact]
                public void Add_TwoNumbers_ReturnsSum()
                {
                    // Arrange: подготовка
                    var calc = new Calculator();

                    // Act: один вызов
                    var result = calc.Add(2, 3);

                    // Assert: проверка
                    Assert.Equal(5, result);
                }
                // Тест пройден: результат 5 совпал с ожидаемым
            }
            // Вывод:
            // Passed!  - Failed: 0, Passed: 1, Skipped: 0, Total: 1
            """,
        ),
        text(
            "Имя `CalculatorTests` соответствует имени класса, а `Add_TwoNumbers_ReturnsSum` "
            "читается как предложение. Конструктор тестового класса в xUnit исполняет роль setup: "
            "он вызывается перед каждым тестом, поэтому каждый тест получает свежие объекты."
        ),
        heading("Вариативные тесты: Theory и InlineData"),
        text(
            "Одно и то же поведение регулярно проверяют на нескольких наборах данных. Копировать "
            "тест под каждый набор — плохая идея: при изменении сигнатуры придётся править все "
            "копии. Вместо этого используется `[Theory]` — параметризованный тест. Наборы значений "
            "задаются атрибутами `[InlineData]`, и каждый набор фреймворк показывает в отчёте как "
            "отдельный случай.\n\n"
            "Метод с `[Theory]` принимает параметры, порядок которых совпадает с порядком аргументов "
            "в `[InlineData]`. Если один из наборов падает, вы видите, какой именно: xUnit выведет "
            "его в имени упавшего кейса. Для сложных данных можно указать источник через "
            "`[MemberData]` или `[ClassData]` вместо `[InlineData]`.\n\n"
            "Выбирайте значения осмысленно: положительные и отрицательные числа, ноль, "
            "граничные значения и входы, которые должны приводить к исключению."
        ),
        example(
            "csharp",
            r"""
            using System;
            using Xunit;

            public class Calculator
            {
                public int Add(int a, int b) => a + b;

                public int Divide(int a, int b) =>
                    b == 0 ? throw new DivideByZeroException() : a / b;
            }

            public class CalculatorTests
            {
                [Theory]
                [InlineData(1, 2, 3)]
                [InlineData(-1, 1, 0)]
                [InlineData(0, 0, 0)]
                [InlineData(int.MaxValue, 0, int.MaxValue)]
                public void Add_MultipleCases_ReturnsSum(int a, int b, int expected)
                {
                    Assert.Equal(expected, new Calculator().Add(a, b));
                }

                [Fact]
                public void Divide_ByZero_Throws()
                {
                    var calc = new Calculator();

                    Assert.Throws<DivideByZeroException>(() => calc.Divide(5, 0));
                }
            }
            // Вывод:
            // Passed!  - Failed: 0, Passed: 5, Skipped: 0, Total: 5
            // (4 случая Add_MultipleCases + 1 случай Divide_ByZero)
            """,
        ),
        callout(
            "warning",
            "Проверка исключений",
            "Не оборачивайте вызов в try/catch вручную со флагом «исключение было». Если тест "
            "забудет проверку, он пройдёт молча. Используйте Assert.Throws, который сам упадёт, "
            "когда исключение не брошено или брошено не того типа."
        ),
        heading("Сравнение фреймворков"),
        text(
            "В экосистеме .NET три основных фреймворка: xUnit, NUnit и MSTest. Все работают "
            "через `dotnet test` и поддерживают параметризованные тесты и фикстуры — общее "
            "окружение для нескольких тестов.\n\n"
            "xUnit запускает тестовые классы параллельно по умолчанию: тесты быстрее, но не "
            "должны делить изменяемое состояние. NUnit консервативнее и требует `[Parallelizable]`, "
            "зато даёт широкий набор утверждений через `Assert.That`. MSTest поставляется с Visual "
            "Studio и меньше всех расширяется. Менять фреймворк в проекте ради новизны не нужно — "
            "важнее один стиль во всём решении."
        ),
        table(
            ["Возможность", "xUnit", "NUnit", "MSTest"],
            [
                ["Параллельный запуск", "По умолчанию", "Через `[Parallelizable]`", "Через `[DoNotParallelize]` для отключения"],
                ["Параметризованные тесты", "`[Theory]` + `[InlineData]`", "`[TestCase(...)]`", "`[DataRow(...)]`"],
                ["Подготовка и очистка", "Конструктор и `IDisposable`", "`[SetUp]` / `[TearDown]`", "`[TestInitialize]` / `[TestCleanup]`"],
                ["Общее окружение", "`IClassFixture<T>`", "`[OneTimeSetUp]`", "`[ClassInitialize]`"],
                ["Проверки", "`Assert.Equal`, `Assert.Throws`", "`Assert.That(..., Is.EqualTo(...))`", "`Assert.AreEqual`"],
            ],
        ),
        example(
            "csharp",
            r"""
            // NUnit
            using NUnit.Framework;

            [TestFixture]
            public class CalculatorTests
            {
                [Test]
                public void Add_ReturnsSum() =>
                    Assert.That(new Calculator().Add(2, 3), Is.EqualTo(5));

                [TestCase(1, 2, 3)]
                [TestCase(-1, 1, 0)]
                public void Add_Cases(int a, int b, int expected) =>
                    Assert.That(new Calculator().Add(a, b), Is.EqualTo(expected));
            }

            // MSTest
            using Microsoft.VisualStudio.TestTools.UnitTesting;

            [TestClass]
            public class CalculatorTestsMstest
            {
                [TestMethod]
                public void Add_ReturnsSum() =>
                    Assert.AreEqual(5, new Calculator().Add(2, 3));
            }
            // Вывод:
            // Passed!  - Failed: 0, Passed: 3, Skipped: 0, Total: 3
            // (2 теста NUnit + 1 тест MSTest)
            """,
        ),
        heading("Arrange-Act-Assert: структура теста"),
        text(
            "Хороший тест читается сверху вниз за несколько секунд. Для этого его тело делят на три "
            "части по шаблону Arrange-Act-Assert. **Arrange** — подготовка: создание объектов, "
            "настройка подмен. **Act** — ровно одно действие, которое проверяется, обычно один "
            "вызов метода. **Assert** — проверка наблюдаемого результата.\n\n"
            "Разделение на три части даёт важный признак: если в блоке Act больше одной строки, "
            "вероятно, тест проверяет слишком много и его стоит разделить. Если в Arrange много "
            "повторяющегося кода, его выносят в фабричный метод или Builder.\n\n"
            "Имя теста в xUnit-C# принято строить по схеме `Метод_Сценарий_ОжидаемыйРезультат`. "
            "Подчёркивания вместо пробелов позволяют читать имя без документации. Часть «Сценарий» "
            "описывает входные условия, часть «ОжидаемыйРезультат» — что должно произойти."
        ),
        table(
            ["Пример имени", "Что проверяет"],
            [
                ["`Transfer_ValidAmount_UpdatesBalances`", "Успешный перевод уменьшает остаток отправителя и увеличивает остаток получателя"],
                ["`Transfer_InsufficientFunds_ThrowsException`", "Перевод при нехватке средств завершается исключением"],
                ["`Transfer_NegativeAmount_ThrowsArgumentException`", "Отрицательная сумма отвергается проверкой аргумента"],
            ],
        ),
        example(
            "csharp",
            r"""
            using System;
            using Xunit;

            public record Account(string Id, decimal Balance);

            public class TransferService
            {
                public void Transfer(Account from, Account to, decimal amount)
                {
                    if (amount <= 0)
                        throw new ArgumentOutOfRangeException(nameof(amount), "Сумма должна быть положительной");
                    if (from.Balance < amount)
                        throw new InvalidOperationException("Недостаточно средств");

                    from = from with { Balance = from.Balance - amount };
                    to = to with { Balance = to.Balance + amount };
                }
            }

            public class TransferTests
            {
                [Fact]
                public void Transfer_ValidAmount_UpdatesBalances()
                {
                    // Arrange
                    var from = new Account("A", 100);
                    var to = new Account("B", 50);
                    var service = new TransferService();

                    // Act
                    service.Transfer(from, to, 30);

                    // Assert
                    Assert.Equal(70, from.Balance);
                    Assert.Equal(80, to.Balance);
                }

                [Fact]
                public void Transfer_NegativeAmount_Throws()
                {
                    var from = new Account("A", 100);
                    var to = new Account("B", 50);

                    Assert.Throws<ArgumentOutOfRangeException>(
                        () => new TransferService().Transfer(from, to, -10));
                }
            }
            // Вывод:
            // Passed!  - Failed: 0, Passed: 2, Skipped: 0, Total: 2
            """,
        ),
        heading("Тестовые данные: Builder и Object Mother"),
        text(
            "Когда для теста нужно собрать объект с десятью свойствами, конструктор превращается "
            "в шум. Паттерн **Builder** прячет значения по умолчанию и позволяет указать только те "
            "поля, которые важны для конкретного теста. Каждый метод `With...` возвращает сам "
            "Builder, поэтому вызовы цепляются в цепочку, а `Build` создаёт итоговый объект.\n\n"
            "Паттерн **Object Mother** решает ту же проблему иначе: набор статических фабричных "
            "методов вида `AccountFactory.ClosedWithZeroBalance()`. Object Mother короче в вызове, "
            "но менее гибок, если понадобится нестандартная комбинация. Builder выигрывает, когда "
            "комбинаций много.\n\n"
            "Польза обоих паттернов не только в краткости. Значения по умолчанию делают тест "
            "устойчивым к новому свойству класса: правится один Builder, а не сотни тестов."
        ),
        example(
            "csharp",
            r"""
            using Xunit;

            public enum AccountStatus { Active, Closed }

            public sealed class Account
            {
                public string Id { get; init; } = "";
                public decimal Balance { get; init; }
                public AccountStatus Status { get; init; }
                public override string ToString() => $"{Id}: {Balance} ({Status})";
            }

            public class AccountBuilder
            {
                private string _id = "ACC-1";
                private decimal _balance = 100;
                private AccountStatus _status = AccountStatus.Active;

                public AccountBuilder WithId(string id) { _id = id; return this; }
                public AccountBuilder WithBalance(decimal b) { _balance = b; return this; }
                public AccountBuilder Closed() { _status = AccountStatus.Closed; return this; }

                public Account Build() => new() { Id = _id, Balance = _balance, Status = _status };
            }

            public class AccountBuilderTests
            {
                [Fact]
                public void Build_DefaultsActiveAccountWithHundred()
                {
                    var account = new AccountBuilder().Build();

                    Assert.Equal(100, account.Balance);
                    Assert.Equal(AccountStatus.Active, account.Status);
                }

                [Fact]
                public void Build_ClosedWithoutBalance()
                {
                    var account = new AccountBuilder().WithBalance(0).Closed().Build();

                    Assert.Equal("ACC-1: 0 (Closed)", account.ToString());
                }
            }
            // Вывод:
            // Passed!  - Failed: 0, Passed: 2, Skipped: 0, Total: 2
            """,
        ),
        heading("Подмена зависимостей: Moq и NSubstitute"),
        text(
            "Модульный тест должен быть быстрым и предсказуемым, поэтому реальные HTTP-сервисы и "
            "базы данных в нём заменяют подменой. Подмена возможна, потому что зависимость выражена "
            "интерфейсом: `IPaymentService`, `IInventoryService`. Библиотека создаёт класс, который "
            "реализует интерфейс и возвращает заранее заданные значения, а также запоминает все "
            "вызовы.\n\n"
            "В Moq подмена создаётся через `Mock<T>`, поведение задаётся методом `Setup`, а "
            "полученный объект-заглушка доступна через свойство `.Object`. Для асинхронных методов "
            "используется `ReturnsAsync`. Совпадение аргументов задаётся `It.IsAny<T>()` (любое "
            "значение) или `It.Is<T>(...)` (значение, удовлетворяющее условию). Проверка факта "
            "вызова выполняется через `Verify` с `Times.Once`.\n\n"
            "NSubstitute предлагает короткий синтаксис: объект создаётся через "
            "`Substitute.For<T>()`, ожидание настраивается вызовом метода с `.Returns(...)`, "
            "любой аргумент обозначается `Arg.Any<T>()`, проверка вызова — `Received(1)`."
        ),
        example(
            "csharp",
            r"""
            using System.Threading.Tasks;
            using Moq;
            using Xunit;

            public interface IPaymentService
            {
                Task<bool> ChargeAsync(decimal amount);
            }

            public interface IInventoryService
            {
                Task<bool> ReserveAsync(int productId, int quantity);
            }

            public class OrderService
            {
                private readonly IPaymentService _payment;
                private readonly IInventoryService _inventory;

                public OrderService(IPaymentService payment, IInventoryService inventory)
                    => (_payment, _inventory) = (payment, inventory);

                public async Task<bool> PlaceOrderAsync(int productId, int quantity, decimal price)
                {
                    if (!await _inventory.ReserveAsync(productId, quantity))
                        return false;
                    return await _payment.ChargeAsync(price * quantity);
                }
            }

            public class OrderServiceTests
            {
                [Fact]
                public async Task PlaceOrder_ValidOrder_ChargesFullPrice()
                {
                    // Arrange
                    var payment = new Mock<IPaymentService>();
                    var inventory = new Mock<IInventoryService>();

                    payment.Setup(p => p.ChargeAsync(It.IsAny<decimal>())).ReturnsAsync(true);
                    inventory.Setup(i => i.ReserveAsync(It.IsAny<int>(), It.IsAny<int>()))
                             .ReturnsAsync(true);

                    var service = new OrderService(payment.Object, inventory.Object);

                    // Act
                    var result = await service.PlaceOrderAsync(productId: 1, quantity: 2, price: 100);

                    // Assert
                    Assert.True(result);
                    payment.Verify(p => p.ChargeAsync(200m), Times.Once);
                    inventory.Verify(i => i.ReserveAsync(1, 2), Times.Once);
                }
            }
            // Вывод:
            // Passed!  - Failed: 0, Passed: 1, Skipped: 0, Total: 1
            """,
        ),
        example(
            "csharp",
            r"""
            using System.Threading.Tasks;
            using NSubstitute;
            using Xunit;

            public class OrderServiceNSubstituteTests
            {
                [Fact]
                public async Task PlaceOrder_InventoryRejects_DoesNotCharge()
                {
                    // Arrange
                    var payment = Substitute.For<IPaymentService>();
                    var inventory = Substitute.For<IInventoryService>();

                    payment.ChargeAsync(Arg.Any<decimal>()).Returns(true);
                    inventory.ReserveAsync(Arg.Any<int>(), Arg.Any<int>()).Returns(false);

                    var service = new OrderService(payment, inventory);

                    // Act
                    var result = await service.PlaceOrderAsync(productId: 7, quantity: 1, price: 50);

                    // Assert
                    Assert.False(result);
                    await payment.DidNotReceive().ChargeAsync(Arg.Any<decimal>());
                }
            }
            // Вывод:
            // Passed!  - Failed: 0, Passed: 1, Skipped: 0, Total: 1
            """,
        ),
        callout(
            "warning",
            "Когда подменять не нужно",
            "Подмена оправдана только для внешних зависимостей: сеть, база, файлы, текущее время, "
            "датчики. Простой класс, запись или `List<T>` создайте как есть: заглушка только запутает."
        ),
        heading("Интеграционные тесты"),
        text(
            "Модульные тесты с подменами не проверяют главного: правильно ли написан SQL, верно ли "
            "сопоставлена схема, работает ли сериализация. Эти риски закрывают интеграционные тесты, "
            "которые запускают настоящую инфраструктуру.\n\n"
            "Библиотека **Testcontainers** поднимает Docker-контейнер с базой данных на время "
            "теста и удаляет его после. Тестовый класс реализует `IAsyncLifetime` из xUnit: метод "
            "`InitializeAsync` запускает контейнер, `DisposeAsync` останавливает. Строка подключения "
            "берётся из живого контейнера через `GetConnectionString()`.\n\n"
            "Для ASP.NET Core есть второй инструмент — `WebApplicationFactory<Program>`. Она "
            "запускает приложение в памяти и выдаёт `HttpClient`, через который можно обращаться к "
            "настоящим контроллерам, не занимая порт. Комбинация обоих подходов даёт сквозной тест "
            "всего стека: реальная база и реальный HTTP-конвейер."
        ),
        example(
            "csharp",
            r"""
            using System.Threading.Tasks;
            using Microsoft.EntityFrameworkCore;
            using Testcontainers.PostgreSql;
            using Xunit;

            public class User { public int Id { get; set; } public string Email { get; set; } = ""; }

            public class AppDbContext : DbContext
            {
                public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
                public DbSet<User> Users => Set<User>();
            }

            public class DatabaseTests : IAsyncLifetime
            {
                private readonly PostgreSqlContainer _db = new PostgreSqlBuilder()
                    .WithImage("postgres:16")
                    .WithDatabase("testdb")
                    .WithUsername("test")
                    .WithPassword("test")
                    .Build();

                public Task InitializeAsync() => _db.StartAsync();
                public Task DisposeAsync() => _db.DisposeAsync().AsTask();

                [Fact]
                public async Task Users_SaveAndLoad_RoundTrips()
                {
                    var options = new DbContextOptionsBuilder<AppDbContext>()
                        .UseNpgsql(_db.GetConnectionString())
                        .Options;

                    await using var context = new AppDbContext(options);
                    await context.Database.EnsureCreatedAsync();

                    context.Users.Add(new User { Email = "test@example.com" });
                    await context.SaveChangesAsync();

                    var loaded = await context.Users.SingleAsync(u => u.Email == "test@example.com");
                    Assert.True(loaded.Id > 0);
                }
            }
            // Вывод:
            // Passed!  - Failed: 0, Passed: 1, Skipped: 0, Total: 1
            // (контейнер postgres:16 запущен и остановлен автоматически)
            """,
        ),
        example(
            "csharp",
            r"""
            using System.Net.Http;
            using System.Net.Http.Json;
            using System.Threading.Tasks;
            using Microsoft.AspNetCore.Mvc.Testing;
            using Xunit;

            public record UserDto(int Id, string Email);

            public class ApiTests : IClassFixture<WebApplicationFactory<Program>>
            {
                private readonly HttpClient _client;

                public ApiTests(WebApplicationFactory<Program> factory)
                    => _client = factory.CreateClient();

                [Fact]
                public async Task GetUsers_ReturnsOkWithBody()
                {
                    var response = await _client.GetAsync("/api/users");
                    response.EnsureSuccessStatusCode();

                    var users = await response.Content.ReadFromJsonAsync<UserDto[]>();
                    Assert.NotNull(users);
                }
            }
            // Вывод:
            // Passed!  - Failed: 0, Passed: 1, Skipped: 0, Total: 1
            """,
        ),
        heading("Покрытие тестами и статический анализ"),
        text(
            "**Покрытие** показывает, какие строки кода выполнились при прогоне тестов. В .NET "
            "покрытие собирает пакет `coverlet` — он запускается вместе с `dotnet test` флагом "
            "`--collect:\"XPlat Code Coverage\"`. Результат сохраняется в формате Cobertura, а "
            "`ReportGenerator` превращает его в удобный HTML-отчёт с подсветкой непокрытых строк.\n\n"
            "Важно понимать: высокое покрытие не означает хорошие тесты. Тест, который вызывает "
            "метод и ничего не проверяет, тоже даёт 100 процентов строк. Покрытие полезно как "
            "индикатор пробелов: непокрытые ветки обработки ошибок почти всегда означают, что "
            "сценарий никто не проверял. Ориентируйтесь на покрытие веток (branch coverage), а не "
            "только строк, и ставьте порог около 80 процентов для основной логики.\n\n"
            "**Статический анализ** — проверка кода без его запуска. В .NET анализаторы Roslyn "
            "встроены в компилятор и сообщают о потенциальных ошибках: неиспользуемых параметрах, "
            "некорректной работе с `async`, утечках `IDisposable`. Наборы правил поставляют пакеты "
            "`Microsoft.CodeAnalysis.NetAnalyzers`, `StyleCop.Analyzers`, `SonarAnalyzer.CSharp`, "
            "`Roslynator.Analyzers` и `Meziantou.Analyzer`."
        ),
        table(
            ["Инструмент", "Что проверяет"],
            [
                ["`coverlet`, `ReportGenerator`", "Покрытие строк и веток, отчёт в HTML"],
                ["`Microsoft.CodeAnalysis.NetAnalyzers`", "Базовые правила платформы .NET (CAxxxx): ресурсы, безопасность, производительность"],
                ["`StyleCop.Analyzers`", "Единый стиль кода (SAxxxx): порядок using, документация, именование"],
                ["`SonarAnalyzer.CSharp`", "Ошибки, уязвимости и сомнительные решения в коде"],
                ["`Roslynator.Analyzers`", "Сотни рефакторингов и подсказок по упрощению кода"],
            ],
        ),
        example(
            "xml",
            r"""
            <!-- App.csproj: включаем анализаторы и запрещаем игнорировать предупреждения -->
            <PropertyGroup>
              <TargetFramework>net8.0</TargetFramework>
              <Nullable>enable</Nullable>
              <EnableNETAnalyzers>true</EnableNETAnalyzers>
              <AnalysisLevel>latest</AnalysisLevel>
              <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
              <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
            </PropertyGroup>

            <ItemGroup>
              <PackageReference Include="StyleCop.Analyzers" Version="1.2.0-beta.556" PrivateAssets="all" />
              <PackageReference Include="Roslynator.Analyzers" Version="4.12.3" PrivateAssets="all" />
            </ItemGroup>

            <!-- App.Tests.csproj: собираем покрытие -->
            <PropertyGroup>
              <CollectCoverage>true</CollectCoverage>
              <CoverletOutputFormat>cobertura</CoverletOutputFormat>
              <Threshold>80</Threshold>
            </PropertyGroup>
            <!-- Вывод при dotnet test: "Line coverage: 87.4%" -->
            """,
        ),
        text(
            "Флаг `TreatWarningsAsErrors` превращает любое предупреждение анализатора в ошибку "
            "сборки. Это жёсткая, но полезная настройка для командной работы: предупреждения не "
            "накапливаются годами. Отдельные правила при необходимости ослабляют в `.editorconfig` "
            "строкой вида `dotnet_diagnostic.CA1822.severity = suggestion`, указывая уровень "
            "важности вместо полного отключения."
        ),
        example(
            "ini",
            r"""
            # .editorconfig — единый стиль для всей команды
            root = true

            [*.cs]
            indent_style = space
            indent_size = 4
            charset = utf-8
            insert_final_newline = true
            csharp_style_namespace_declarations = file_scoped:warning

            # Стиль документации
            dotnet_diagnostic.SA1200.severity = warning   # порядок using
            dotnet_diagnostic.SA1600.severity = suggestion

            # Производительность
            dotnet_diagnostic.CA1822.severity = suggestion

            # Надёжность: ConfigureAwait в библиотеках
            dotnet_diagnostic.CA2007.severity = warning
            """,
        ),
        heading("Отладка"),
        text(
            "Отладчик нужен, когда тесты упали, а причина непонятна. Базовый инструмент — "
            "**точка останова** (breakpoint): выполнение приостанавливается на строке, и видно "
            "значения переменных, стек вызовов и можно вычислять выражения.\n\n"
            "**Условный останов** останавливает программу только при выполнении условия, например "
            "`i == 42`, — это спасает в цикле на миллион итераций. **Точка журнала** (logpoint) "
            "печатает значение в окно вывода, не останавливая работу. **Окно немедленного "
            "выполнения** позволяет выполнить код во время остановки, а **окна наблюдения** "
            "(Watch) следят за выражениями.\n\n"
            "Если приложение упало на сервере, отладчик не поможет. Тогда снимают **дамп памяти** "
            "командой `dotnet-dump collect -p <pid>` и изучают его в режиме `dotnet-dump analyze`. "
            "Команда `dumpheap -stat` показывает, какие типы занимают память, `gcroot` подсказывает, "
            "кто удерживает объект, а `clrstack` выводит стек управляемых потоков."
        ),
        example(
            "bash",
            r"""
            # Прогон всех тестов с покрытием
            dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage

            # HTML-отчёт по покрытию
            dotnet tool install -g dotnet-reportgenerator-globaltool
            reportgenerator -reports:"./coverage/**/coverage.cobertura.xml" \
                            -targetdir:"./coverage/report" -reporttypes:Html

            # Снять дамп зависшего процесса
            dotnet-dump collect -p 4821

            # Изучить дамп
            dotnet-dump analyze core_20261119_101500
            # (вывод)
            # > dumpheap -stat
            #      MT    Count    TotalSize Class Name
            # 7f0a..     1842       29472 System.String
            # 7f1c..      320      256000 MyApp.Order
            # > gcroot 000001f2a3b4
            # Found 1 root: static field MyApp.Cache._orders
            """,
        ),
        example(
            "csharp",
            r"""
            using System;
            using BenchmarkDotNet.Attributes;
            using System.Text;

            [MemoryDiagnoser]
            public class StringConcatBenchmarks
            {
                [Benchmark(Baseline = true)]
                public string Concat() => "a" + "b" + "c";

                [Benchmark]
                public string StringBuilder()
                {
                    var sb = new StringBuilder();
                    sb.Append("a").Append("b").Append("c");
                    return sb.ToString();
                }
            }
            // Вывод (фрагмент):
            // | Method        | Mean      | Allocated |
            // |-------------- |---------- |---------- |
            // | Concat        |  9.10 ns  |      24 B |
            // | StringBuilder | 31.40 ns  |      72 B |
            """,
        ),
        text(
            "Когда программа работает, но медленно, интуиция часто обманывает. **BenchmarkDotNet** "
            "запускает метод много раз с прогревом, изолирует шум JIT и сборщика мусора и выдаёт "
            "достоверные числа: среднее время и выделенную память. Показанный результат показывает: "
            "`StringBuilder` полезен в цикле на тысячи итераций, но для трёх коротких строк "
            "конкатенация быстрее, потому что компилятор сворачивает её в один вызов `String.Concat`."
        ),
        heading("Тесты в конвейере"),
        text(
            "Тесты приносят пользу, когда запускаются автоматически при каждом изменении. Типичный "
            "конвейер выполняет три шага: восстановление пакетов, сборку в Release и прогон тестов "
            "с покрытием. Если хотя бы один тест упал, сборка помечается как неуспешная и правка не "
            "попадает в основную ветку.\n\n"
            "Прогон в CI защищает от двух проблем. Тест, который проходит только на машине "
            "автора из-за другой версии SDK, обнаруживается сразу; отчёт о покрытии делает "
            "снижение показателя заметным в каждом пулл-реквесте."
        ),
        example(
            "yaml",
            r"""
            # .github/workflows/test.yml
            name: Test
            on: [push, pull_request]

            jobs:
              test:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: actions/setup-dotnet@v4
                    with:
                      dotnet-version: '8.0.x'
                  - run: dotnet restore
                  - run: dotnet build --no-restore --configuration Release
                  - run: dotnet test --no-build --configuration Release --collect:"XPlat Code Coverage"
            # Вывод:
            # Passed!  - Failed: 0, Passed: 128, Skipped: 0, Total: 128
            """,
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Тесты делят общее изменяемое состояние", "Порядок запуска меняет результат, тесты падают случайно", "Каждый тест создаёт свои объекты; общее окружение — только через `IClassFixture`"],
                ["Подменяют всё подряд", "Тест проверяет настройку заглушек, а не код", "Подменяйте только сеть, БД, время"],
                ["Один тест проверяет много вещей", "При падении непонятно, что сломалось", "Один тест — одна проверяемая реакция на сценарий"],
                ["Проверяют только успешный сценарий", "Обработка ошибок остаётся непроверенной", "Добавляйте граничные значения и исключения"],
                ["Игнорируют предупреждения анализаторов", "Проблемы копятся и уже не замечаются", "Включите `TreatWarningsAsErrors` и исправляйте всё"],
                ["Гоняются за высоким процентом покрытия", "Пишутся тесты без утверждений ради цифры", "Покрытие — индикатор пробелов, а не цель"],
                ["В тесте `Thread.Sleep`", "Тесты медленные и нестабильные", "`Task.Delay` с токеном или абстракция времени"],
            ],
        ),
        heading("Практика"),
        text(
            "Создайте решение из двух проектов: `dotnet new classlib -n Shop` и "
            "`dotnet new xunit -n Shop.Tests`. Добавьте ссылку `dotnet add Shop.Tests reference Shop` "
            "и запускайте тесты командой `dotnet test`."
        ),
        numbered(
            "Напишите тест на `Calculator.Divide` для двух случаев: обычное деление и деление на ноль. Используйте `[Theory]` с `[InlineData]` и `Assert.Throws`.",
            "Реализуйте `DiscountService` с правилом: заказ дороже 1000 получает скидку 10 процентов. Напишите тесты для значений 999, 1000 и 2000 — проверьте граничные случаи.",
            "Введите интерфейс `IEmailSender` и подмените его через Moq. Проверьте, что при регистрации пользователя письмо отправлено ровно один раз.",
            "Добавьте `AccountBuilder` и напишите три теста, которые создают закрытый счёт, счёт с нулевым балансом и счёт с заданным идентификатором.",
            "Включите в `.csproj` флаги `TreatWarningsAsErrors` и `EnableNETAnalyzers`, затем соберите проект и исправьте все предупреждения.",
        ),
        text("Пример ожидаемого результата для второго задания:"),
        example(
            "text",
            r"""
            Вывод:
            dotnet test
            Passed!  - Failed: 0, Passed: 3, Skipped: 0, Total: 3
              DiscountTests.Apply_AmountBelowThreshold_ReturnsSameTotal
              DiscountTests.Apply_AmountAtThreshold_ReturnsDiscounted
              DiscountTests.Apply_AmountAboveThreshold_ReturnsDiscounted
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 3",
            "Настройте подмену так: `email.Setup(e => e.SendAsync(It.IsAny<string>())).Returns(Task.CompletedTask);` "
            "и проверьте `email.Verify(e => e.SendAsync(It.IsAny<string>()), Times.Once);`. Не забудьте, "
            "что метод интерфейса должен возвращать `Task`, иначе асинхронный тест не соберётся."
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем `[Theory]` отличается от `[Fact]` и зачем нужны атрибуты `[InlineData]`?",
            "Какие три блока содержит тест по шаблону Arrange-Act-Assert и что происходит, если в Act две строки?",
            "Что произойдёт с тестом, если внутри `Assert.Throws` не будет брошено исключение?",
            "Почему для подмены используется интерфейс, а не конкретный класс?",
            "Чем интеграционный тест отличается от модульного и что проверяет Testcontainers?",
            "Почему покрытие 100 процентов не означает, что тесты хорошие?",
        ),
        heading("Ответы", 3),
        numbered(
            "`[Fact]` запускает один тест без параметров, `[Theory]` — тест с параметрами, а каждый `[InlineData]` задаёт отдельный набор значений и запускается как отдельный случай.",
            "Arrange (подготовка), Act (действие) и Assert (проверка). Две строки в Act означают, что тест проверяет два действия, и его стоит разделить.",
            "Тест упадёт: `Assert.Throws` сам сообщает об ошибке, если ожидаемое исключение не было брошено или его тип не совпал.",
            "Можно подключить любую реализацию, включая сгенерированную библиотекой заглушку, не меняя тестируемый класс. Конкретный класс потребовал бы наследования и виртуальных методов.",
            "Модульный тест проверяет одну единицу в изоляции, интеграционный — взаимодействие нескольких компонентов. Testcontainers запускает реальную инфраструктуру, например PostgreSQL, в Docker на время теста.",
            "Покрытие считает выполненные строки, а не качество проверок. Тест, который вызывает метод и ничего не утверждает, тоже повышает покрытие.",
        ),
        heading("Итоги"),
        bullets(
            "Модульные тесты проверяют поведение в изоляции; пирамида тестов держит баланс между быстрыми и медленными проверками.",
            "xUnit использует `[Fact]` для одиночного теста и `[Theory]` с `[InlineData]` для параметризованного.",
            "Тест строится по шаблону Arrange-Act-Assert, имя — по схеме `Метод_Сценарий_ОжидаемыйРезультат`.",
            "Исключения проверяются через `Assert.Throws`; тестовые объекты собираются через Builder или Object Mother.",
            "Moq и NSubstitute подменяют внешние зависимости, выраженные интерфейсами; подменять всё подряд вредно.",
            "Интеграционные тесты поднимают реальную инфраструктуру: Testcontainers для баз данных, `WebApplicationFactory` для HTTP.",
            "Покрытие измеряют через coverlet и ReportGenerator, качество кода — анализаторы Roslyn и `TreatWarningsAsErrors`.",
            "Отладка включает условные остановы и точки журнала, а для упавших процессов — дампы `dotnet-dump` и BenchmarkDotNet.",
        ),
        heading("Что дальше"),
        text(
            "Теперь вы умеете проверять код и держать его качество под контролем: писать тесты на "
            "xUnit, изолировать зависимости, запускать интеграционные проверки и ловить ошибки "
            "анализаторами. Следующий урок — о доступе к данным: Entity Framework Core, миграции, "
            "запросы LINQ к базе и способы избежать лишних обращений к серверу."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "xUnit.net — документация и примеры: xunit.net",
            "NSubstitute — краткое введение: nsubstitute.github.io",
            "Moq — исходный код и вики: github.com/moq/moq4",
            "Testcontainers for .NET: dotnet.testcontainers.org",
            "BenchmarkDotNet: benchmarkdotnet.org",
            "StyleCop.Analyzers: github.com/DotNetAnalyzers/StyleCopAnalyzers",
            "Владимир Хориков, «Принципы модульного тестирования» (Unit Testing Principles, Practices, and Patterns)",
        ),
    ],
}
