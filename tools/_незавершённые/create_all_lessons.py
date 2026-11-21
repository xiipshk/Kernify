#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create all advanced C# lessons (13-33) with real educational content.
"""

import json

def write_lesson(lesson_num, data):
    path = f'fixtures/lessons/csharp/{lesson_num:02d}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Written lesson {lesson_num}')

# ==================== LESSON 13: ООП и дизайн ====================
lesson_13 = {
    "title": "Урок 13: ООП и дизайн — интерфейсы, абстрактные классы, полиморфизм, композиция, дженерики",
    "slug": "lesson-13",
    "short_description": "интерфейсы, абстрактные классы, полиморфизм, композиция, дженерики",
    "goals": [
        "Понимать разницу между абстрактным классом и интерфейсом",
        "Применять полиморфизм через virtual/override",
        "Использовать композицию вместо наследования",
        "Работать с дженериками в ООП дизайне"
    ],
    "content_blocks": [
        {"type": "heading", "level": 2, "content": "Что вы узнаете"},
        {"type": "list", "items": [
            "Разница между abstract class и interface",
            "Полиморфизм через virtual/override",
            "Композиция вместо наследования (Composition over Inheritance)",
            "Дженерики в ООП дизайне",
            "SOLID принципы на практике"
        ], "ordered": False},
        {"type": "heading", "level": 2, "content": "Абстрактный класс vs Интерфейс: что выбрать?"},
        {"type": "text", "content": "Абстрактный класс (abstract class) — это неполная реализация, которая может иметь состояние (поля), конструкторы и реализованные методы. Класс может наследовать только ОДИН абстрактный класс.\n\nИнтерфейс (interface) — это чистый контракт без реализации (до C# 8). Класс может реализовывать НЕСКОЛЬКО интерфейсов.\n\n```csharp\n// Абстрактный класс — общая логика + состояние\nabstract class Animal {\n    public string Name { get; set; }\n    public abstract void MakeSound();\n    public void Sleep() => Console.WriteLine(\"Zzz...\"); // Реализация по умолчанию\n}\n\n// Интерфейс — только контракт\ninterface IFlyable {\n    void Fly();\n    int MaxAltitude { get; }\n}\n\n// Класс может: наследовать 1 абстрактный класс + реализовывать МНОГО интерфейсов\nclass Bird : Animal, IFlyable { ... }\n```"},
            {"type": "heading", "level": 2, "content": "Полиморфизм через virtual/override"},
            {"type": "text", "content": "Полиморфизм позволяет обращаться к объектам разных типов через единый интерфейс:\n\n```csharp\nabstract class Shape {\n    public abstract double Area();\n}\n\nclass Circle : Shape {\n    public double Radius { get; set; }\n    public override double Area() => Math.PI * Radius * Radius;\n}\n\nclass Rectangle : Shape {\n    public double Width, Height;\n    public override double Area() => Width * Height;\n}\n\n// Полиморфизм: переменная базового типа, объекты разных наследников\nList<Shape> shapes = new() { new Circle { Radius = 5 }, new Rectangle { Width = 3, Height = 4 } };\nforeach (var s in shapes) Console.WriteLine(s.Area()); // Каждый свой Area()\n```\n\nКлючевые правила:\n- `virtual` в базовом классе — метод можно переопределить\n- `override` в наследнике — новая реализация\n- Без `virtual` — `new` скрывает метод (не полиморфизм!)"},
            {"type": "heading", "level": 2, "content": "Композиция вместо наследования (Composition over Inheritance)"},
            {"type": "text", "content": "Наследование создает сильную связанность (tight coupling). Композиция — включение объекта как поля:\n\n```csharp\n// Наследование (плохо для изменений)\nclass Car : Engine { }\n\n// Композиция (гибко)\nclass Car {\n    private readonly IEngine _engine;\n    public Car(IEngine engine) => _engine = engine;\n    public void Start() => _engine.Start();\n}\n\n// Преимущества композиции:\n// - Слабая связанность (loose coupling)\n// - Легко тестировать (моки)\n// - Легко менять поведение в runtime\n// - Можно комбинировать поведения" },
            {"type": "heading", "level": 2, "content": "Дженерики в ООП дизайне"},
            {"type": "text", "content": "Дженерики позволяют писать типобезопасный переиспользуемый код:\n\n```csharp\n// Generic Repository\ninterface IRepository<T> where T : class {\n    Task<T> GetByIdAsync(int id);\n    Task AddAsync(T entity);\n}\n\nclass EfRepository<T> : IRepository<T> where T : class {\n    private readonly DbContext _db;\n    public EfRepository(DbContext db) => _db = db;\n    // реализация через DbSet<T>\n}\n\n// Generic Factory\ninterface IFactory<T> where T : new() {\n    T Create();\n}\n\n// Generic Strategy\ninterface IValidator<T> {\n    ValidationResult Validate(T item);\n}\n```"},
            {"type": "heading", "level": 2, "content": "SOLID принципы на практике"},
            {"type": "list", "items": [
                "S (SRP) — класс имеет одну ответственность. Разделяйте: UserService, EmailService, UserRepository.",
                "O (OCP) — открыт для расширения, закрыт для изменения. Используйте интерфейсы и полиморфизм вместо if/else.",
                "L (LSP) — наследник должен заменять базовый класс без ломания логики. Не выбрасывайте исключения в override там, где базовый их не бросает.",
                "I (ISP) — лучше много мелких интерфейсов (IPrintable, IScannable), чем один большой IDevice.",
                "D (DIP) — зависьте от абстракций (IUserRepository), не от конкретных классов. DI контейнер резолвит реализацию."
            ], "ordered": False},
            {"type": "heading", "level": 2, "content": "Типичные ошибки"},
            {"type": "table", "headers": ["Ошибка", "Проблема", "Решение"], "rows": [
                ["Наследование вместо композиции", "Жесткая связанность, сложно тестировать", "Композиция + интерфейсы"],
                ["God Interface (10+ методов)", "Классы вынуждены реализовывать неиспользуемые методы", "Разбивайте на мелкие интерфейсы (ISP)"],
                ["Забыли virtual при переопределении", "Метод скрывается (new), полиморфизм не работает", "Добавьте virtual в базовом классе, override в наследнике"],
                ["Вызов виртуального метода в конструкторе", "Вызывается override версия, но поля наследника еще не инициализированы!", "Избегайте вызова virtual методов в конструкторах"],
                ["Пытаются создать экземпляр abstract класса", "Ошибка компиляции: Cannot create an instance of abstract class", "Создайте не-абстрактного наследника"],
                ["as с value type", "int x = obj as int; — ошибка компиляции", "as только для ссылочных типов. Для value type используйте is + приведение"],
                ["Забыли base.Method() в override", "Потеряна базовая логика (валидация, логирование)", "Вызовите base.Method() в начале или в конце override"]
            ]},
            {"type": "heading", "level": 2, "content": "Практика"},
            {"type": "list", "items": [
                "Создайте интерфейс IPaymentProcessor с методом Process(decimal amount). Реализации: CreditCardProcessor, PayPalProcessor, CryptoProcessor. Сервис оплаты принимает IPaymentProcessor через конструктор.",
                "Создайте абстрактный класс Employee с полями Name, Salary. Абстрактный метод CalculateBonus(). Наследники: Manager (бонус = 20% от зарплаты), Developer (бонус = 10% + 1000 за каждый год стажа). Массив сотрудников — посчитать общий бонус.",
                "Создайте класс Document с protected полем Content. Наследники: TextDocument (метод WordCount()), ImageDocument (свойство Resolution). Используйте is для проверки типа в массиве документов.",
                "Исправьте ошибки:\n```csharp\nclass Animal { public virtual void Sound() { } }\nclass Dog : Animal { public void Sound() { } }  // Ошибка: нет override\n\nclass Base { public Base(int x) { } }\nclass Derived : Base { }  // Ошибка\n\nAnimal a = new Dog();\nDog d = a as Dog;  // OK\nint x = a as int;  // Ошибка\n```"
            ], "ordered": True},
            {"type": "heading", "level": 2, "content": "Кратко о главном"},
            {"type": "list", "items": [
                "abstract class — общее состояние + логика, один родитель. interface — только контракт, много интерфейсов",
                "virtual/override — полиморфизм. Без virtual — new (скрытие), полиморфизм не работает",
                "Композиция > Наследование. Слабая связанность, тестируемость, гибкость",
                "Дженерики — переиспользование кода с типовой безопасностью",
                "SOLID — основа поддерживаемой архитектуры"
            ], "ordered": False},
            {"type": "heading", "level": 2, "content": "Полезные ссылки"},
            {"type": "list", "items": [
                "Microsoft Docs — Inheritance: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/inheritance",
                "Microsoft Docs — Polymorphism: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/polymorphism",
                "Microsoft Docs — Interfaces: https://learn.microsoft.com/dotnet/csharp/programming-guide/interfaces/",
                "Microsoft Docs — Generics: https://learn.microsoft.com/dotnet/csharp/programming-guide/generics/",
                "SOLID principles: https://learn.microsoft.com/dotnet/standard/design-guidelines/solid"
            ], "ordered": False},
            {"type": "heading", "level": 2, "content": "Ключевые выводы"},
            {"type": "list", "items": [
                "abstract class — общее состояние + логика, один родитель. interface — только контракт, много интерфейсов",
                "virtual/override — полиморфизм. Без virtual — new (скрытие), полиморфизм не работает",
                "Композиция > Наследование. Слабая связанность, тестируемость, гибкость",
                "Дженерики — переиспользование кода с типовой безопасностью",
                "SOLID — основа поддерживаемой архитектуры"
            ], "ordered": False},
            {"type": "heading", "level": 2, "content": "Полезные ссылки"},
            {"type": "list", "items": [
                "Microsoft Docs — Inheritance: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/inheritance",
                "Microsoft Docs — Polymorphism: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/polymorphism",
                "Microsoft Docs — Interfaces: https://learn.microsoft.com/dotnet/csharp/programming-guide/interfaces/",
                "Microsoft Docs — Generics: https://learn.microsoft.com/dotnet/csharp/programming-guide/generics/",
                "SOLID principles: https://learn.microsoft.com/dotnet/standard/design-guidelines/solid"
            ], "ordered": False}
        ],
        "practice_tasks": [
            "Создайте интерфейс IPaymentProcessor с методом Process(decimal amount). Реализации: CreditCardProcessor, PayPalProcessor, CryptoProcessor. Сервис оплаты принимает IPaymentProcessor через конструктор.",
            "Создайте абстрактный класс Employee с полями Name, Salary. Абстрактный метод CalculateBonus(). Наследники: Manager (бонус = 20% от зарплаты), Developer (бонус = 10% + 1000 за каждый год стажа). Массив сотрудников — посчитать общий бонус.",
            "Создайте класс Document с protected полем Content. Наследники: TextDocument (метод WordCount()), ImageDocument (свойство Resolution). Используйте is для проверки типа в массиве документов.",
            "Исправьте ошибки:\n```csharp\nclass Animal { public virtual void Sound() { } }\nclass Dog : Animal { public void Sound() { } }  // Ошибка: нет override\n\nclass Base { public Base(int x) { } }\nclass Derived : Base { }  // Ошибка\n\nAnimal a = new Dog();\nDog d = a as Dog;  // OK\nint x = a as int;  // Ошибка\n```"
        ],
        "common_errors": [
            {"mistake": "Наследование вместо композиции", "correct": "Композиция + интерфейсы для слабой связанности"},
            {"mistake": "God Interface (10+ методов)", "correct": "Разбивайте на мелкие интерфейсы по ISP"},
            {"mistake": "Забыли virtual при переопределении", "correct": "Добавьте virtual в базовом классе, override в наследнике"},
            {"mistake": "Вызов виртуального метода в конструкторе", "correct": "Избегайте вызова virtual методов в конструкторах"},
            {"mistake": "Пытаются создать экземпляр abstract класса", "correct": "Создайте не-абстрактного наследника"},
            {"mistake": "as с value type", "correct": "as только для ссылочных типов. Для value type используйте is + приведение"},
            {"mistake": "Забыли base.Method() в override", "correct": "Вызовите base.Method() в начале или в конце override"}
        ],
        "resources": [
            "Microsoft Docs — Inheritance: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/inheritance",
            "Microsoft Docs — Polymorphism: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/polymorphism",
            "Microsoft Docs — Interfaces: https://learn.microsoft.com/dotnet/csharp/programming-guide/interfaces/",
            "Microsoft Docs — Generics: https://learn.microsoft.com/dotnet/csharp/programming-guide/generics/",
            "SOLID principles: https://learn.microsoft.com/dotnet/standard/design-guidelines/solid"
        ],
        "key_takeaways": [
            "abstract class — общее состояние + логика, один родитель. interface — только контракт, много интерфейсов",
            "virtual/override — полиморфизм. Без virtual — new (скрытие), полиморфизм не работает",
            "Композиция > Наследование. Слабая связанность, тестируемость, гибкость",
            "Дженерики — переиспользование кода с типовой безопасностью",
            "SOLID — основа поддерживаемой архитектуры"
        ],
        "resources": [
            "Microsoft Docs — Inheritance: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/inheritance",
            "Microsoft Docs — Polymorphism: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/polymorphism",
            "Microsoft Docs — Interfaces: https://learn.microsoft.com/dotnet/csharp/programming-guide/interfaces/",
            "Microsoft Docs — Generics: https://learn.microsoft.com/dotnet/csharp/programming-guide/generics/",
            "SOLID principles: https://learn.microsoft.com/dotnet/standard/design-guidelines/solid"
        ],
        "key_takeaways": [
            "abstract class — общее состояние + логика, один родитель. interface — только контракт, много интерфейсов",
            "virtual/override — полиморфизм. Без virtual — new (скрытие), полиморфизм не работает",
            "Композиция > Наследование. Слабая связанность, тестируемость, гибкость",
            "Дженерики — переиспользование кода с типовой безопасностью",
            "SOLID — основа поддерживаемой архитектуры"
        ],
        "estimated_minutes": 35,
        "language_slug": "csharp",
        "lesson_order": 13,
        "name_en": "Lesson: OOP Design - Interfaces, Abstract Classes, Polymorphism, Generics",
        "short_description_en": "Learn interfaces, abstract classes, polymorphism, composition, generics in C#"
    },
}

# ... Add more lessons here

def write_lesson(lesson_num, data):
    path = f'fixtures/lessons/csharp/{lesson_num:02d}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Written lesson {lesson_num}')

if __name__ == '__main__':
    # Write lesson 12 first
    with open('fixtures/lessons/csharp/12.json', 'r', encoding='utf-8') as f:
        lesson_12 = json.load(f)
    
    # Write lesson 13
    write_lesson(13, lesson_13)
    print('Lesson 13 written!')