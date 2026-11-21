#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

lesson = {
  "title": "Урок 9: Интерфейсы — контракты поведения",
  "slug": "interfeysy-kontrakty-povedeniya",
  "short_description": "Интерфейсы, явная/неявная реализация, default методы, множественная реализация, ISP, DI через интерфейсы",
  "goals": [
    "Понимать, что такое интерфейс и зачем он нужен",
    "Умеь объявлять и реализовывать интерфейсы (явно и неявно)",
    "Работать с default методами (C# 8+) и статическими членами",
    "Применять множественную реализацию интерфейсов",
    "Понимать Interface Segregation Principle (ISP)",
    "Использовать интерфейсы для Dependency Injection и тестирования"
  ],
  "content_blocks": [
    {
      "type": "heading",
      "level": 2,
      "content": "🎯 Что вы узнаете"
    },
    {
      "type": "list",
      "items": [
        "Что такое интерфейс и чем он отличается от абстрактного класса",
        "Как реализовать интерфейс неявно и явно",
        "Что такое default методы (C# 8+) и статические члены",
        "Как реализовывать несколько интерфейсов с конфликтующими методами",
        "Что такое Interface Segregation Principle (ISP) и как его применять",
        "Зачем нужны интерфейсы для Dependency Injection и тестирования"
      ],
      "ordered": False
    },
    {
      "type": "heading",
      "level": 2,
      "content": "💡 Зачем нужны интерфейсы: контракт без реализации"
    },
    {
      "type": "text",
      "content": "Представьте: вы пишете программу для управления уведомлениями. Можно отправлять email, SMS, push-уведомления, вебхуки. Без интерфейсов ваш код отправки жестко привязан к конкретным классам `EmailSender`, `SmsSender`. Добавление нового способа — правка во всех местах.\n\nС интерфейсом `INotificationSender` вы пишете код, который работает с абстракцией `Send(message)`. Конкретная реализация подключается извне. Хотите добавить Telegram? Пишете новый класс `TelegramSender : INotificationSender` — остальной код не меняется."
    },
    {
      "type": "heading",
      "level": 3,
      "content": "📋 Что такое интерфейс и синтаксис объявления"
    },
    {
      "type": "text",
      "content": "**Интерфейс** — это контракт, описывающий *что* объект умеет делать, но не *как* он это делает. Содержит только сигнатуры методов, свойств, событий, индексаторов. Не содержит состояния (полей), конструкторов, финализаторов.\n\nВсе члены интерфейса **неявно public** (модификаторы доступа не пишутся). Класс может реализовывать **несколько интерфейсов** (множественное наследование контрактов)."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "// Объявление интерфейса\npublic interface INotificationSender {\n    void Send(string recipient, string message);\n    bool CanSendTo(string recipient);\n    event EventHandler<NotificationSentEventArgs> NotificationSent;\n    string ProviderName { get; }\n}\n\n// Реализация\npublic class EmailSender : INotificationSender {\n    public string ProviderName => \"Email\";\n    public event EventHandler<NotificationSentEventArgs> NotificationSent;\n\n    public bool CanSendTo(string recipient) => recipient.Contains(\"@\");\n    public void Send(string recipient, string message) {\n        // логика отправки email\n        NotificationSent?.Invoke(this, new NotificationSentEventArgs(recipient));\n    }\n}"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "🔧 Неявная vs Явная реализация интерфейса"
    },
    {
      "type": "text",
      "content": "**Неявная (implicit)** — методы интерфейса становятся публичными методами класса. Вызываются через объект класса или через интерфейс.\n\n**Явная (explicit)** — методы доступны **только** при приведении к интерфейсу. Полезно когда:\n- Класс реализует несколько интерфейсов с одинаковыми сигнатурами методов\n- Метод не должен быть частью публичного API класса\n- Нужно скрыть детали реализации от потребителей класса"
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "public interface ILogger {\n    void Log(string message);\n}\n\npublic interface IAuditor {\n    void Log(string message);\n}\n\npublic class Service : ILogger, IAuditor {\n    // Неявная реализация — доступна как service.Log()\n    public void Log(string message) {\n        Console.WriteLine($\"[LOG] {message}\");\n    }\n\n    // Явная реализация — доступна ТОЛЬКО через интерфейс\n    void IAuditor.Log(string message) {\n        Console.WriteLine($\"[AUDIT] {message}\");\n        WriteToAuditLog(message);\n    }\n\n    private void WriteToAuditLog(string msg) { }\n}\n\nvar service = new Service();\nservice.Log(\"test\");           // вызывает неявный Log\n((IAuditor)service).Log(\"audit\"); // вызывает явный IAuditor.Log"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "🆕 Default методы и статические члены (C# 8+)"
    },
    {
      "type": "text",
      "content": "Раньше интерфейсы не могли иметь реализации. C# 8 добавил **default методы** (с реализацией по умолчанию) и **статические члены**. Это позволяет развивать интерфейсы без ломания существующих реализаций."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "public interface IRepository<T> {\n    T GetById(int id);\n    void Add(T entity);\n\n    // Default метод — реализация по умолчанию\n    public virtual void AddRange(IEnumerable<T> entities) {\n        foreach (var e in entities) Add(e);\n    }\n\n    // Статический метод — принадлежит интерфейсу, не реализации\n    public static IRepository<T> CreateEmpty() => new EmptyRepository<T>();\n\n    // Статическое поле\n    public static int DefaultPageSize = 20;\n}\n\n// Использование default метода\nvar repo = new SqlRepository<User>();\nrepo.AddRange(users);  // работает, даже если не переопределяли\n\n// Статический доступ\nvar emptyRepo = IRepository<User>.CreateEmpty();\nint size = IRepository<User>.DefaultPageSize;"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "⚔️ Конфликты при множественной реализации"
    },
    {
      "type": "text",
      "content": "Если класс реализует два интерфейса с одинаковыми сигнатурами методов, происходит конфликт. Решается **явной реализацией** для каждого интерфейса."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "public interface IPrinter {\n    void Print(string text);\n}\n\npublic interface IScanner {\n    void Scan(string text);  // другое имя — конфликта нет\n}\n\n// Конфликт: оба имеют void Print()\npublic interface IPrintable {\n    void Print();\n}\n\npublic interface IScannable {\n    void Print();  // то же имя!\n}\n\npublic class Device : IPrintable, IScannable {\n    // Явная реализация для разделения\n    void IPrintable.Print() => Console.WriteLine(\"Printing...\");\n    void IScannable.Print() => Console.WriteLine(\"Scanning...\");\n}\n\nvar device = new Device();\n((IPrintable)device).Print();  // Printing...\n((IScannable)device).Print();  // Scanning..."
    },
    {
      "type": "heading",
      "level": 3,
      "content": "📐 Interface Segregation Principle (ISP) — принцип разделения интерфейсов"
    },
    {
      "type": "text",
      "content": "**ISP**: клиенты не должны зависеть от методов, которые они не используют. Лучше несколько маленьких интерфейсов, чем один большой \"божественный\".\n\nПлохо: `IUserService` с методами `GetUser`, `SendEmail`, `GenerateReport`, `BackupDatabase`. Класс, которому нужно только `GetUser`, вынужден реализовывать всё.\n\nХорошо: `IUserRepository` (GetUser), `IEmailSender` (SendEmail), `IReportGenerator` (GenerateReport), `IBackupService` (BackupDatabase). Классы реализуют только то, что им нужно."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "// ПЛОХО: жирный интерфейс\npublic interface IUserService {\n    User GetUser(int id);\n    void SendEmail(string to, string subject, string body);\n    byte[] GenerateReport();\n    void BackupDatabase();\n}\n\n// ХОРОШО: разделенные интерфейсы\npublic interface IUserRepository { User GetUser(int id); }\npublic interface IEmailSender { void SendEmail(string to, string subject, string body); }\npublic interface IReportGenerator { byte[] GenerateReport(); }\npublic interface IBackupService { void BackupDatabase(); }\n\n// Класс реализует только нужное\npublic class UserController : IUserRepository, IEmailSender {\n    public User GetUser(int id) => ...\n    public void SendEmail(string to, string subject, string body) => ...\n}"
    },
    {
      "type": "heading",
      "level": 2,
      "content": "🔌 Интерфейсы и Dependency Injection (DI)"
    },
    {
      "type": "text",
      "content": "Интерфейсы — фундамент **Dependency Injection**. Высокоуровневые модули зависят от абстракций (интерфейсов), а не от конкретных реализаций. Контейнер DI (встроенный в ASP.NET Core, Autofac, и др.) подставляет реализацию в runtime.\n\nПлюсы:\n- **Тестируемость**: в тестах подставляете мок/фейк вместо реальной БД/API\n- **Заменяемость**: смена БД, почтового провайдера, кэша — только конфиг DI\n- **Слабая связанность**: модули не знают друг о друге, знают только интерфейсы"
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "// Интерфейс\npublic interface IUserRepository {\n    User GetById(int id);\n    void Save(User user);\n}\n\n// Реализация для БД\npublic class SqlUserRepository : IUserRepository {\n    private readonly DbContext _db;\n    public SqlUserRepository(DbContext db) => _db = db;\n    // реализация...\n}\n\n// Реализация для тестов (In-Memory)\npublic class FakeUserRepository : IUserRepository {\n    private readonly Dictionary<int, User> _users = new();\n    public User GetById(int id) => _users.GetValueOrDefault(id);\n    public void Save(User user) => _users[user.Id] = user;\n}\n\n// Регистрация в DI контейнере (ASP.NET Core)\n// builder.Services.AddScoped<IUserRepository, SqlUserRepository>();\n\n// В контроллере — зависимость от интерфейса\npublic class UserController {\n    private readonly IUserRepository _repo;\n    public UserController(IUserRepository repo) => _repo = repo;\n    \n    public User Get(int id) => _repo.GetById(id);\n}"
    },
    {
      "type": "heading",
      "level": 2,
      "content": "🧪 Интерфейсы и Unit-тестирование"
    },
    {
      "type": "text",
      "content": "Интерфейсы позволяют легко подменять реальные зависимости на **моки (mocks)** или **фейки (fakes)** в тестах. Вы тестируете логику в изоляции от БД, внешних API, файловой системы."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "// Используя Moq\nvar mockRepo = new Mock<IUserRepository>();\nmockRepo.Setup(r => r.GetById(1)).Returns(new User { Id = 1, Name = \"Alex\" });\n\nvar controller = new UserController(mockRepo.Object);\nvar user = controller.GetUser(1);\nAssert.Equal(\"Alex\", user.Name);\n\n// Без интерфейса пришлось бы мокать класс — сложнее, хрупче, требует virtual методов"
    },
    {
      "type": "heading",
      "level": 2,
      "content": "⚠️ Типичные ошибки новичков"
    },
    {
      "type": "table",
      "headers": [
        "Ошибка",
        "Как проявляется",
        "Как правильно"
      ],
      "rows": [
        [
          "Слишком большие интерфейсы (God Interface)",
          "Класс вынужден реализовывать 10 методов, используя только 1",
          "Разбивайте на мелкие интерфейсы по ответственности (ISP)"
        ],
        [
          "Интерфейс для каждого класса 1:1",
          "`IUserService` реализует только `UserService` — лишняя абстракция",
          "Интерфейс нужен, если есть несколько реализаций или нужна подмена в тестах"
        ],
        [
          "Поля в интерфейсе",
          "`interface IConfig { string ConnectionString; }` — ошибка компиляции",
          "Только свойства (`string ConnectionString { get; }`)"
        ],
        [
          "Модификаторы доступа в интерфейсе",
          "`public void Method()` или `private void Method()` — ошибка",
          "Не пишите модификаторы — всё неявно public"
        ],
        [
          "Конструктор в интерфейсе",
          "`interface IRepo { IRepo(); }` — ошибка",
          "Интерфейсы не имеют конструкторов. Используйте фабрики или DI"
        ],
        [
          "Наследование интерфейсов вместо композиции",
          "`interface IAdminUser : IUser, IAdmin { }` — зачем?",
          "Класс реализует оба: `class Admin : IUser, IAdmin`"
        ],
        [
          "Отсутствие интерфейса там, где нужен DI/тесты",
          "Класс напрямую использует `SqlConnection` — не тестируется",
          "Выносите абстракцию: `IDbConnection` / `IUserRepository`"
        ]
      ]
    },
    {
      "type": "heading",
      "level": 2,
      "content": "🛠 Практика: закрепите навык"
    },
    {
      "type": "list",
      "items": [
        "Создайте интерфейс `IPaymentProcessor` с методом `Process(decimal amount)`. Реализуйте `CreditCardProcessor`, `PayPalProcessor`, `CryptoProcessor`. Напишите сервис оплаты, принимающий `IPaymentProcessor` через конструктор.",
        "Создайте интерфейс `ILogger` с методом `Log(string level, string message)`. Реализуйте `ConsoleLogger`, `FileLogger`, `NullLogger` (ничего не делает). Используйте в классе через DI.",
        "Создайте два интерфейса `IReadable` (метод `Read()`) и `IWritable` (метод `Write(string)`). Класс `FileStorage` реализует оба. Класс `ReadOnlyCache` реализует только `IReadable`. Проверьте, что `ReadOnlyCache` не может писать.",
        "Исправьте ошибки:\n```csharp\ninterface IRepo {\n    string ConnectionString;  // Ошибка: поле\n    void Save();\n    public void Save();  // Ошибка: модификатор\n}\n\nclass Service {\n    private IRepo _repo;\n    public Service() { _repo = new SqlRepo(); }  // Ошибка: прямая зависимость\n}\n```"
      ],
      "ordered": True
    },
    {
      "type": "heading",
      "level": 2,
      "content": "📌 Кратко о главном"
    },
    {
      "type": "list",
      "items": [
        "Интерфейс — контракт (что умеет), не реализация (как делает). Только сигнатуры, все public.",
        "Класс может реализовывать множество интерфейсов. Множественное наследование только через интерфейсы.",
        "Явная реализация (`void IInterface.Method()`) — скрывает метод от API класса, доступен только через интерфейс.",
        "Default методы (C# 8+) — реализация по умолчанию в интерфейсе. Статические члены — у интерфейса.",
        "ISP: лучше много маленьких интерфейсов, чем один большой. Клиент не должен знать о методах, которые не использует.",
        "Интерфейсы — основа DI и тестируемости. Зависимости от абстракций, не от конкретных классов.",
        "Не делайте интерфейс под каждый класс 1:1. Интерфейс нужен, если есть выбор реализации или нужна подмена в тестах."
      ],
      "ordered": False
    },
    {
      "type": "heading",
      "level": 2,
      "content": "🔗 Полезные ссылки"
    },
    {
      "type": "list",
      "items": [
        "Microsoft Docs — Interfaces: https://learn.microsoft.com/dotnet/csharp/programming-guide/interfaces/",
        "Microsoft Docs — Explicit Interface Implementation: https://learn.microsoft.com/dotnet/csharp/programming-guide/interfaces/explicit-interface-implementation",
        "Microsoft Docs — Default Interface Methods: https://learn.microsoft.com/dotnet/csharp/whats-new/tutorials/default-interface-methods",
        "Microsoft Docs — Dependency Injection: https://learn.microsoft.com/dotnet/core/extensions/dependency-injection",
        "Martin Fowler — Interface Segregation Principle: https://martinfowler.com/articles/interfaceSegregationPrinciple.html"
      ],
      "ordered": False
    }
  ],
  "practice_tasks": [
    "Создайте интерфейс `IPaymentProcessor` с методом `Process(decimal amount)`. Реализуйте `CreditCardProcessor`, `PayPalProcessor`, `CryptoProcessor`. Напишите сервис оплаты, принимающий `IPaymentProcessor` через конструктор.",
    "Создайте интерфейс `ILogger` с методом `Log(string level, string message)`. Реализуйте `ConsoleLogger`, `FileLogger`, `NullLogger` (ничего не делает). Используйте в классе через DI.",
    "Создайте два интерфейса `IReadable` (метод `Read()`) и `IWritable` (метод `Write(string)`). Класс `FileStorage` реализует оба. Класс `ReadOnlyCache` реализует только `IReadable`. Проверьте, что `ReadOnlyCache` не может писать.",
    "Исправьте ошибки:\n```csharp\ninterface IRepo {\n    string ConnectionString;  // Ошибка: поле\n    void Save();\n    public void Save();  // Ошибка: модификатор\n}\n\nclass Service {\n    private IRepo _repo;\n    public Service() { _repo = new SqlRepo(); }  // Ошибка: прямая зависимость\n}\n```"
  ],
  "common_errors": [
    {
      "mistake": "Слишком большие интерфейсы (God Interface)",
      "correct": "Разбивайте на мелкие интерфейсы по ответственности (ISP)"
    },
    {
      "mistake": "Интерфейс для каждого класса 1:1",
      "correct": "Интерфейс нужен, если есть несколько реализаций или нужна подмена в тестах"
    },
    {
      "mistake": "Поля в интерфейсе",
      "correct": "Только свойства (`string ConnectionString { get; }`)"
    },
    {
      "mistake": "Модификаторы доступа в интерфейсе",
      "correct": "Не пишите модификаторы — всё неявно public"
    },
    {
      "mistake": "Конструктор в интерфейсе",
      "correct": "Интерфейсы не имеют конструкторов. Используйте фабрики или DI"
    },
    {
      "mistake": "Наследование интерфейсов вместо композиции",
      "correct": "Класс реализует оба: `class Admin : IUser, IAdmin`"
    },
    {
      "mistake": "Отсутствие интерфейса там, где нужен DI/тесты",
      "correct": "Выносите абстракцию: `IDbConnection` / `IUserRepository`"
    }
  ],
  "resources": [
    "Microsoft Docs — Interfaces: https://learn.microsoft.com/dotnet/csharp/programming-guide/interfaces/",
    "Microsoft Docs — Explicit Interface Implementation: https://learn.microsoft.com/dotnet/csharp/programming-guide/interfaces/explicit-interface-implementation",
    "Microsoft Docs — Default Interface Methods: https://learn.microsoft.com/dotnet/csharp/whats-new/tutorials/default-interface-methods",
    "Microsoft Docs — Dependency Injection: https://learn.microsoft.com/dotnet/core/extensions/dependency-injection",
    "Martin Fowler — Interface Segregation Principle: https://martinfowler.com/articles/interfaceSegregationPrinciple.html"
  ],
  "key_takeaways": [
    "Интерфейс — контракт (что умеет), не реализация (как делает). Только сигнатуры, все public.",
    "Класс может реализовывать множество интерфейсов. Множественное наследование только через интерфейсы.",
    "Явная реализация (`void IInterface.Method()`) — скрывает метод от API класса, доступен только через интерфейс.",
    "Default методы (C# 8+) — реализация по умолчанию в интерфейсе. Статические члены — у интерфейса.",
    "ISP: лучше много маленьких интерфейсов, чем один большой. Клиент не должен знать о методах, которые не использует.",
    "Интерфейсы — основа DI и тестируемости. Зависимости от абстракций, не от конкретных классов.",
    "Не делайте интерфейс под каждый класс 1:1. Интерфейс нужен, если есть выбор реализации или нужна подмена в тестах."
  ],
  "estimated_minutes": 30,
  "language_slug": "csharp",
  "lesson_order": 9,
  "name_en": "Lesson: Interfaces",
  "short_description_en": "Learn interfaces, explicit implementation, default methods, DI in C#"
}

with open('fixtures/lessons/csharp/09.json', 'w', encoding='utf-8') as f:
    json.dump(lesson, f, ensure_ascii=False, indent=2)
    f.write('\n')

print("Урок 9 успешно перезаписан!")
PYEOF