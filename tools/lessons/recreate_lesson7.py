#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

lesson = {
  "title": "Урок 7: Наследование — расширение классов",
  "slug": "nasledovanie-rasshirenie-klassov",
  "short_description": "Базовые и производные классы, base, virtual/override, sealed, protected, абстрактные классы, is/as, pattern matching в is",
  "goals": [
    "Понимать, как работает наследование: базовый и производный классы",
    "Умеь вызывать конструктор базового класса через base",
    "Переопределять методы через virtual/override",
    "Использовать protected для доступа в наследниках",
    "Создавать абстрактные классы и методы",
    "Использовать is/as для проверки типа и безопасного приведения",
    "Знать, когда использовать sealed"
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
        "Как работает наследование: базовый (base) и производный (derived) классы",
        "Как вызвать конструктор базового класса через base(...)",
        "Что такое virtual/override — полиморфизм на уровне методов",
        "Чем protected отличается от private и public",
        "Что такое абстрактные классы и абстрактные методы",
        "Как безопасно проверять тип и приводить: is, as, pattern matching",
        "Когда использовать sealed (запрет наследования/переопределения)"
      ],
      "ordered": False
    },
    {
      "type": "heading",
      "level": 2,
      "content": "💡 Зачем нужно наследование: не повторяйся (DRY) для поведения"
    },
    {
      "type": "text",
      "content": "Представьте: у вас есть класс `Animal` с полями `Name`, `Age` и методом `MakeSound()`. Теперь нужны `Dog`, `Cat`, `Bird`. Без наследования пришлось бы копировать поля `Name`, `Age` в каждый класс. С наследованием: `Dog : Animal` — и `Dog` автоматически получает `Name`, `Age` и может добавить своё уникальное поведение (например, `Breed` для собаки)."
    },
    {
      "type": "heading",
      "level": 3,
      "content": "🏗 Базовый и производный классы: синтаксис `class Derived : Base`"
    },
    {
      "type": "text",
      "content": "В C# наследование **одиночное** (один базовый класс), но можно реализовывать много интерфейсов. Производный класс получает **все члены** базового (кроме конструкторов и финализаторов), но видимость зависит от модификаторов доступа:\n- `public` — везде\n- `protected` — в базовом классе и в наследниках\n- `private` — только в базовом классе (наследники НЕ видят)\n- `internal` — в той же сборке"
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "// Базовый класс\npublic class Animal {\n    public string Name { get; set; }\n    public int Age { get; set; }\n\n    public Animal(string name, int age) {\n        Name = name;\n        Age = age;\n    }\n\n    public virtual void MakeSound() {\n        Console.WriteLine($\"{Name} издаёт звук\");\n    }\n}\n\n// Производный класс\npublic class Dog : Animal {\n    public string Breed { get; set; }\n\n    // Конструктор наследника ВЫЗЫВАЕТ базовый через base(...)\n    public Dog(string name, int age, string breed) : base(name, age) {\n        Breed = breed;\n    }\n\n    // Переопределение виртуального метода\n    public override void MakeSound() {\n        Console.WriteLine($\"{Name} лает: Гав-гав!\");\n    }\n\n    // Свой метод\n    public void Fetch() {\n        Console.WriteLine($\"{Name} приносит палку\");\n    }\n}\n\n// Использование\nvar dog = new Dog(\"Бобик\", 3, \"Овчарка\");\ndog.MakeSound();  // Бобик лает: Гав-гав!\ndog.Fetch();      // Бобик приносит палку\nConsole.WriteLine(dog.Name);  // Бобик (унаследовано от Animal)"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "🔑 base — вызов конструктора и членов базового класса"
    },
    {
      "type": "text",
      "content": "**base** в наследнике означает «обратись к базовому классу». Два основных использования:\n1. `base(...)` в конструкторе — **обязательно** вызывать, если у базового класса нет конструктора по умолчанию. Передаёт аргументы вверх.\n2. `base.Method()` — вызов версии метода базового класса (например, при расширении логики в `override`)."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "public class Animal {\n    public string Name { get; }\n    public Animal(string name) => Name = name;\n}\n\npublic class Dog : Animal {\n    public string Breed { get; }\n\n    // base(name) ВЫЗЫВАЕТ Animal(name) — обязательно, так как у Animal нет конструктора без параметров\n    public Dog(string name, string breed) : base(name) {\n        Breed = breed;\n    }\n\n    // base для вызова метода базового класса\n    public override void MakeSound() {\n        base.MakeSound();  // сначала базовая логика\n        Console.WriteLine(\"  ...и лает!\");  // потом своя\n    }\n}"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "🔐 protected — доступ для наследников, но не для всех"
    },
    {
      "type": "text",
      "content": "**protected** — член виден **в самом классе** и **во всех наследниках**, но **не снаружи**. Идеально для: полей, которые должны быть доступны наследникам для чтения/записи, но скрыты от внешнего кода. Также есть `protected internal` (наследник ИЛИ та же сборка) и `private protected` (наследник И та же сборка)."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "public class Animal {\n    // private — только Animal\n    private string _secret = \"secret\";\n\n    // protected — Animal И наследники (Dog, Cat)\n    protected string _name;\n    protected int _age;\n\n    // public — все\n    public string Name => _name;\n}\n\npublic class Dog : Animal {\n    public void SetName(string name) {\n        _name = name;  // OK: protected доступен в наследнике\n        // _secret = \"x\"; // ОШИБКА: private не виден\n    }\n}\n\nvar dog = new Dog();\n// dog._name = \"x\"; // ОШИБКА: protected не доступен снаружи"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "🔄 virtual / override — полиморфизм методов"
    },
    {
      "type": "text",
      "content": "**virtual** в базовом классе — «этот метод можно переопределить». **override** в наследнике — «я даю свою реализацию». При вызове через переменную базового типа выполняется версия **фактического объекта** (позднее связывание). Без `virtual` — `new` (скрытие), но это не полиморфизм."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "public class Animal {\n    public virtual void MakeSound() {\n        Console.WriteLine(\"Животное издаёт звук\");\n    }\n}\n\npublic class Dog : Animal {\n    public override void MakeSound() {\n        Console.WriteLine(\"Гав-гав!\");\n    }\n}\n\npublic class Cat : Animal {\n    public override void MakeSound() {\n        Console.WriteLine(\"Мяу!\");\n    }\n}\n\n// Полиморфизм: переменная типа Animal, но объект Dog/Cat\nAnimal[] animals = { new Dog(), new Cat(), new Animal() };\nforeach (var a in animals) {\n    a.MakeSound();  // Вызывается версия ФАКТИЧЕСКОГО объекта\n}\n// Вывод:\n// Гав-гав!\n// Мяу!\n// Животное издаёт звук"
    },
    {
      "type": "text",
      "content": "**Важные правила:**\n- `override` может быть только на `virtual`, `abstract` или `override` методе\n- Нельзя менять сигнатуру (параметры, возврат) при override\n- `override` методы по умолчанию `virtual` — их можно дальше переопределять\n- `sealed override` — запрещает дальнейшее переопределение"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "🚫 new vs override — скрытие vs переопределение"
    },
    {
      "type": "text",
      "content": "Если базовый метод **не virtual**, а наследник объявляет метод с тем же именем — это **скрытие (new)**, не полиморфизм. При вызове через базовый тип выполнится базовый метод. `new` можно не писать (компилятор предупредит), но лучше писать явно."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "public class Base {\n    public void Show() => Console.WriteLine(\"Base\");\n}\n\npublic class Derived : Base {\n    public new void Show() => Console.WriteLine(\"Derived\");\n}\n\nBase b = new Derived();\nb.Show();  // \"Base\" — полиморфизма НЕТ, так как не virtual\n\nDerived d = new Derived();\nd.Show();  // \"Derived\"\n\n// Base.Show() всё равно доступен через приведение:\n((Base)d).Show();  // \"Base\""
    },
    {
      "type": "heading",
      "level": 2,
      "content": "🎭 Абстрактные классы и методы — контракт для наследников"
    },
    {
      "type": "text",
      "content": "**abstract class** — класс, от которого **нельзя создать объект** (`new AbstractClass()` — ошибка). Служит только базой для наследников. Может содержать:\n- **abstract методы** — без реализации, **обязательны к переопределению** в наследниках (если наследник не abstract)\n- **виртуальные методы** — с реализацией, можно переопределить\n- **обычные методы/свойства** — общая логика\n\nАбстрактный класс не может быть `sealed` или `static`."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "public abstract class Shape {\n    public string Color { get; set; }\n\n    // Абстрактный метод — ОБЯЗАТЕЛЬНО переопределить в наследнике\n    public abstract double GetArea();\n    public abstract double GetPerimeter();\n\n    // Виртуальный — можно переопределить, а можно не\n    public virtual void PrintInfo() {\n        Console.WriteLine($\"Фигура цвета {Color}\");\n    }\n\n    // Обычный метод — общая логика\n    public void PrintColor() => Console.WriteLine($\"Цвет: {Color}\");\n}\n\npublic class Circle : Shape {\n    public double Radius { get; set; }\n\n    public Circle(double radius) => Radius = radius;\n\n    public override double GetArea() => Math.PI * Radius * Radius;\n    public override double GetPerimeter() => 2 * Math.PI * Radius;\n\n    public override void PrintInfo() {\n        base.PrintInfo();  // базовая логика\n        Console.WriteLine($\"Радиус: {Radius}\");\n    }\n}\n\npublic class Rectangle : Shape {\n    public double Width { get; set; }\n    public double Height { get; set; }\n\n    public override double GetArea() => Width * Height;\n    public override double GetPerimeter() => 2 * (Width + Height);\n}\n\n// var s = new Shape(); // ОШИБКА: нельзя создать экземпляр абстрактного класса\nvar shapes = new Shape[] { new Circle(5), new Rectangle { Width = 4, Height = 6 } };\nforeach (var s in shapes) {\n    Console.WriteLine($\"Площадь: {s.GetArea():F2}\");\n}"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "🔍 Проверка типа и приведение: is, as, pattern matching"
    },
    {
      "type": "text",
      "content": "При работе с наследованием часто нужно: «этот Animal — Dog?» или «приведи Animal к Dog безопасно».\n\n- **is** — проверка типа, возвращает `bool`. С C# 7 поддерживает **pattern matching**: `if (animal is Dog dog)` — проверяет И объявляет переменную.\n- **as** — безопасное приведение: возвращает `null`, если тип не совпадает (не бросает исключение). Работает только для ссылочных типов.\n- **is not** (C# 9+) — отрицание."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "Animal animal = new Dog();\n\n// 1. Классический is + приведение\nif (animal is Dog) {\n    Dog d = (Dog)animal;  // второе приведение — лишняя работа\n    d.Fetch();\n}\n\n// 2. Pattern matching (C# 7+) — проверка И объявление переменной\nif (animal is Dog dog) {\n    dog.Fetch();  // dog уже приведён к Dog\n}\n\n// 3. as — безопасное приведение (null если не тот тип)\nDog dog2 = animal as Dog;\nif (dog2 != null) {\n    dog2.Fetch();\n}\n\n// 4. switch с pattern matching (C# 7+)\npublic void Process(Animal a) {\n    switch (a) {\n        case Dog dog:\n            Console.WriteLine($\"Dog: {dog.Name}\");\n            break;\n        case Cat cat:\n            Console.WriteLine($\"Cat: {cat.Name}\");\n            break;\n        case null:\n            Console.WriteLine(\"Null\");\n            break;\n        default:\n            Console.WriteLine(\"Unknown animal\");\n            break;\n    }\n}\n\n// 5. is not (C# 9+)\nif (animal is not Dog) {\n    Console.WriteLine(\"Не собака\");\n}"
    },
    {
      "type": "heading",
      "level": 3,
      "content": "🔒 sealed — запрет наследования или переопределения"
    },
    {
      "type": "text",
      "content": "**sealed class** — класс нельзя наследовать. **sealed override** — метод нельзя дальше переопределять. Используйте, когда:\n- Класс не предназначен для наследования (утилиты, DTO, security-критичные классы)\n- Метод завершает иерархию поведения (например, финальная валидация)\n- Производительность: JIT может инлайнить sealed методы"
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "public sealed class FinalClass { }\n// public class Derived : FinalClass { } // ОШИБКА\n\npublic class Base {\n    public virtual void Method() { }\n}\n\npublic class Middle : Base {\n    public sealed override void Method() { }\n}\n\npublic class Leaf : Middle {\n    // public override void Method() { } // ОШИБКА: sealed\n}"
    },
    {
      "type": "heading",
      "level": 2,
      "content": "📋 Порядок вызова конструкторов и финализаторов"
    },
    {
      "type": "text",
      "content": "При создании объекта наследника конструкторы вызываются **снизу вверх**: сначала базовый, потом производный. При уничтожении (GC) — деструкторы (финализаторы) вызываются **сверху вниз**: сначала производный, потом базовый."
    },
    {
      "type": "code",
      "language": "csharp",
      "content": "public class Base {\n    public Base() => Console.WriteLine(\"Base ctor\");\n    ~Base() => Console.WriteLine(\"Base dtor\");\n}\n\npublic class Derived : Base {\n    public Derived() => Console.WriteLine(\"Derived ctor\");\n    ~Derived() => Console.WriteLine(\"Derived dtor\");\n}\n\n// Создание:\nvar d = new Derived();\n// Вывод:\n// Base ctor\n// Derived ctor\n\n// Удаление (GC):\n// Derived dtor\n// Base dtor"
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
          "Забыли вызвать base(...) в конструкторе",
          "Ошибка компиляции: \"base class does not contain a constructor that takes 0 arguments\"",
          "Всегда вызывайте `: base(args)` если у базового нет parameterless конструктора"
        ],
        [
          "Пытаются обратиться к private члену базового",
          "`_privateField` в наследнике — ошибка компиляции",
          "Используйте protected или публичные свойства/методы"
        ],
        [
          "Забыли virtual при переопределении",
          "Метод скрывается (new), полиморфизм не работает",
          "Добавьте virtual в базовом классе, override в наследнике"
        ],
        [
          "Вызов виртуального метода в конструкторе",
          "Вызывается override версия, но поля наследника ещё не инициализизированы!",
          "Избегайте вызова virtual методов в конструкторах"
        ],
        [
          "Пытаются создать экземпляр abstract класса",
          "Ошибка компиляции: \"Cannot create an instance of abstract class\"",
          "Создайте не-абстрактного наследника"
        ],
        [
          "as с value type",
          "`int x = obj as int;` — ошибка компиляции",
          "as только для ссылочных типов. Для value type используйте `is` + приведение"
        ],
        [
          "Забыли base.Method() в override",
          "Потеряна базовая логика (валидация, логирование)",
          "Вызовите `base.Method()` в начале или в конце override"
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
        "Создайте базовый класс `Vehicle` с полями `Brand`, `Year`, виртуальным методом `Drive()`. Наследники: `Car` (поле `Doors`), `Motorcycle` (поле `HasSidecar`). Переопределите `Drive()`. Создайте массив `Vehicle[]` и вызовите `Drive()` для каждого.",
        "Создайте абстрактный класс `Employee` с полями `Name`, `Salary`. Абстрактный метод `CalculateBonus()`. Наследники: `Manager` (бонус = 20% от зарплаты), `Developer` (бонус = 10% + 1000 за каждый год стажа). Массив сотрудников — посчитать общий бонус.",
        "Создайте класс `Document` с `protected` полем `Content`. Наследники: `TextDocument` (метод `WordCount()`), `ImageDocument` (свойство `Resolution`). Используйте `is` для проверки типа в массиве документов.",
        "Исправьте ошибки:\n```csharp\nclass Animal { public virtual void Sound() { } }\nclass Dog : Animal { public void Sound() { } }  // Ошибка\n\nclass Base { public Base(int x) { } }\nclass Derived : Base { }  // Ошибка\n\nAnimal a = new Dog();\nDog d = a as Dog;  // OK\nint x = a as int;  // Ошибка\n```"
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
        "Наследование: `class Derived : Base`. Производный получает все члены (кроме конструкторов). private — не видит, protected — видит наследники.",
        "`base(...)` в конструкторе наследника — обязательно, если у базового нет parameterless конструктора. `base.Method()` вызывает версию базового.",
        "`protected` — видно в классе и наследниках, не видно снаружи. `private` — только в классе. `public` — везде.",
        "`virtual` / `override` — полиморфизм. Без virtual — `new` (скрытие), полиморфизм не работает.",
        "Абстрактный класс (`abstract`) — нельзя создать экземпляр. Абстрактные методы — обязаны переопределять.",
        "`is` — проверка типа + pattern matching (`if (x is Type t)`). `as` — безопасное приведение (null если не тот тип).",
        "`sealed class` — нельзя наследовать. `sealed override` — нельзя дальше переопределять.",
        "Конструкторы: базовый → производный. Деструкторы: производный → базовый."
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
        "Microsoft Docs — Inheritance: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/inheritance",
        "Microsoft Docs — Polymorphism: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/polymorphism",
        "Microsoft Docs — Abstract: https://learn.microsoft.com/dotnet/csharp/language-reference/keywords/abstract",
        "Microsoft Docs — Pattern matching: https://learn.microsoft.com/dotnet/csharp/pattern-matching",
        "Microsoft Docs — Sealed: https://learn.microsoft.com/dotnet/csharp/language-reference/keywords/sealed"
      ],
      "ordered": False
    }
  ],
  "practice_tasks": [
    "Создайте базовый класс `Vehicle` с полями `Brand`, `Year`, виртуальным методом `Drive()`. Наследники: `Car` (поле `Doors`), `Motorcycle` (поле `HasSidecar`). Переопределите `Drive()`. Создайте массив `Vehicle[]` и вызовите `Drive()` для каждого.",
    "Создайте абстрактный класс `Employee` с полями `Name`, `Salary`. Абстрактный метод `CalculateBonus()`. Наследники: `Manager` (бонус = 20% от зарплаты), `Developer` (бонус = 10% + 1000 за каждый год стажа). Массив сотрудников — посчитать общий бонус.",
    "Создайте класс `Document` с `protected` полем `Content`. Наследники: `TextDocument` (метод `WordCount()`), `ImageDocument` (свойство `Resolution`). Используйте `is` для проверки типа в массиве документов.",
    "Исправьте ошибки:\n```csharp\nclass Animal { public virtual void Sound() { } }\nclass Dog : Animal { public void Sound() { } }  // Ошибка\n\nclass Base { public Base(int x) { } }\nclass Derived : Base { }  // Ошибка\n\nAnimal a = new Dog();\nDog d = a as Dog;  // OK\nint x = a as int;  // Ошибка\n```"
  ],
  "common_errors": [
    {
      "mistake": "Забыли вызвать base(...) в конструкторе",
      "correct": "Всегда вызывайте `: base(args)` если у базового нет parameterless конструктора"
    },
    {
      "mistake": "Пытаются обратиться к private члену базового",
      "correct": "Используйте protected или публичные свойства/методы"
    },
    {
      "mistake": "Забыли virtual при переопределении",
      "correct": "Добавьте virtual в базовом классе, override в наследнике"
    },
    {
      "mistake": "Вызов виртуального метода в конструкторе",
      "correct": "Избегайте вызова virtual методов в конструкторах"
    },
    {
      "mistake": "Пытаются создать экземпляр abstract класса",
      "correct": "Создайте не-абстрактного наследника"
    },
    {
      "mistake": "as с value type",
      "correct": "as только для ссылочных типов. Для value type используйте `is` + приведение"
    },
    {
      "mistake": "Забыли base.Method() в override",
      "correct": "Вызовите `base.Method()` в начале или в конце override"
    }
  ],
  "resources": [
    "Microsoft Docs — Inheritance: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/inheritance",
    "Microsoft Docs — Polymorphism: https://learn.microsoft.com/dotnet/csharp/programming-guide/classes-and-structs/polymorphism",
    "Microsoft Docs — Abstract: https://learn.microsoft.com/dotnet/csharp/language-reference/keywords/abstract",
    "Microsoft Docs — Pattern matching: https://learn.microsoft.com/dotnet/csharp/pattern-matching",
    "Microsoft Docs — Sealed: https://learn.microsoft.com/dotnet/csharp/language-reference/keywords/sealed"
  ],
  "key_takeaways": [
    "Наследование: `class Derived : Base`. Производный получает все члены (кроме конструкторов). private — не видит, protected — видит наследники.",
    "`base(...)` в конструкторе наследника — обязательно, если у базового нет parameterless конструктора. `base.Method()` вызывает версию базового.",
    "`protected` — видно в классе и наследниках, не видно снаружи. `private` — только в классе. `public` — везде.",
    "`virtual` / `override` — полиморфизм. Без virtual — `new` (скрытие), полиморфизм не работает.",
    "Абстрактный класс (`abstract`) — нельзя создать экземпляр. Абстрактные методы — обязаны переопределять.",
    "`is` — проверка типа + pattern matching (`if (x is Type t)`). `as` — безопасное приведение (null если не тот тип).",
    "`sealed class` — нельзя наследовать. `sealed override` — нельзя дальше переопределять.",
    "Конструкторы: базовый → производный. Деструкторы: производный → базовый."
  ],
  "estimated_minutes": 35,
  "language_slug": "csharp",
  "lesson_order": 7,
  "name_en": "Lesson: Inheritance",
  "short_description_en": "Learn inheritance, polymorphism, abstract classes in C#"
}

with open('fixtures/lessons/csharp/07.json', 'w', encoding='utf-8') as f:
    json.dump(lesson, f, ensure_ascii=False, indent=2)
    f.write('\n')

print("Lesson 7 rewritten successfully!")
PYEOF