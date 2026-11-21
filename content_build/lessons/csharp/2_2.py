"""Урок 2 курса C#: проектирование ООП."""

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
    "topic_order": 2,
    "name": "2.2. Проектирование ООП",
    "slug": "csharp-2-2-проектирование-ооп",
    "short_description": (
        "Как проектировать иерархии типов: интерфейсы и абстрактные классы, полиморфизм "
        "и принцип подстановки Лисков, композиция вместо наследования, обобщения, паттерны и SOLID."
    ),
    "topic_name": "Проектирование ООП",
    "topic_description": (
        "Проектирование объектной модели в C#: выбор между интерфейсом и абстрактным классом, "
        "подтиповый полиморфизм и контракты, композиция и стратегии, обобщения с ограничениями, "
        "паттерны Factory, Builder и Decorator, практическое применение принципов SOLID."
    ),
    "learning_objectives": [
        "Осознанно выбирать между интерфейсом и абстрактным классом для новой иерархии",
        "Применять полиморфизм подтипов и проверять иерархии на соответствие принципу Лисков",
        "Использовать ковариантность и контрвариантность интерфейсов и делегатов",
        "Заменять глубокое наследование композицией и паттерном «Стратегия»",
        "Писать обобщённые типы с ограничениями и применять обобщённую математику",
        "Реализовывать паттерны Factory Method, Builder и Decorator и объяснять их область применения",
        "Находить нарушения принципов SOLID в существующем коде и исправлять их",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "csharp",
        "ооп",
        "интерфейсы",
        "полиморфизм",
        "solid",
        "паттерны",
    ],
    "starter_code": code(
        """
        // Контракт и две его реализации.
        interface IShape
        {
            string Name { get; }
            double Area();
        }

        sealed class Circle(double radius) : IShape
        {
            public string Name => "Круг";
            public double Area() => Math.PI * radius * radius;
        }

        sealed class Rectangle(double w, double h) : IShape
        {
            public string Name => "Прямоугольник";
            public double Area() => w * h;
        }

        IShape[] shapes = [new Circle(1), new Rectangle(3, 4)];

        foreach (IShape shape in shapes)
        {
            Console.WriteLine($"{shape.Name}: {shape.Area():F2}");
        }
        """
    ),
    "hints": [
        "Если тип должен выражать контракт для никак не связанных классов, выбирайте интерфейс. Абстрактный класс нужен тогда, когда нужна общая реализация и общее состояние.",
        "Подтип должен принимать хотя бы те же входные данные и возвращать не более слабые гарантии, чем базовый тип. Если производный класс требует больше условий, принцип подстановки нарушен.",
        "Для ковариантности параметр типа объявляется с out и используется только в возвращаемых значениях, для контрвариантности — с in и только в параметрах методов.",
        "Ограничение `where T : class` запрещает значимые типы и не позволяет вызвать `new T()` — добавьте `new()`, но помните, что порядок ограничений важен: `class, IEntity, new()`.",
    ],
    "content": [
        text(
            "Объектно-ориентированное программирование не сводится к ключевым словам class и new. "
            "Главная его ценность — в проектировании: в умении разложить задачу на типы, договориться "
            "о контрактах между ними и выстроить иерархию так, чтобы новые требования добавлялись без "
            "переписывания уже работающего кода. Именно эта часть работы отличает опытного разработчика "
            "от того, кто просто умеет объявлять поля и методы.\n\n"
            "Урок опирается на предыдущий материал о системе типов: значимые и ссылочные типы, "
            "наследование, переопределение виртуальных методов, модификаторы доступа. Здесь эти "
            "возможности рассматриваются как инструменты проектирования: что выбрать, когда есть два "
            "подходящих механизма, как проверить, что иерархия не сломается при расширении, и почему "
            "иногда прямолинейное наследование приносит больше вреда, чем пользы.\n\n"
            "Материал устроен от общего к частному. Сначала сравниваются интерфейсы и абстрактные "
            "классы, затем разбирается полиморфизм подтипов и принцип подстановки Лисков, потом "
            "композиция и паттерны, обобщения с ограничениями и, наконец, принципы SOLID."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "осознанно выбирать между интерфейсом и абстрактным классом для новой иерархии;",
            "применять полиморфизм подтипов и проверять иерархии на соответствие принципу Лисков;",
            "использовать ковариантность и контрвариантность интерфейсов и делегатов;",
            "заменять глубокое наследование композицией и паттерном «Стратегия»;",
            "писать обобщённые типы с ограничениями и применять обобщённую математику;",
            "реализовывать паттерны Factory Method, Builder и Decorator и объяснять их область применения;",
            "находить нарушения принципов SOLID в существующем коде и исправлять их.",
        ),
        heading("Интерфейсы и абстрактные классы"),
        text(
            "Интерфейс в C# — это контракт: набор сигнатур, которые обязан реализовать тип, "
            "объявивший этот интерфейс. По соглашению имена интерфейсов начинаются с заглавной буквы I. "
            "До C# 8 интерфейс не мог содержать реализаций, сегодня эта возможность появилась, но "
            "использовать её стоит осторожно: реализация в интерфейсе нужна прежде всего для "
            "версионирования уже опубликованных библиотек.\n\n"
            "Абстрактный класс — это обычный класс, у которого нельзя создать экземпляр. "
            "Он сочетает контракт и реализацию: часть методов объявляется с ключевым словом "
            "abstract и требует переопределения, часть объявляется как virtual и может быть "
            "переопределена по желанию, а остальные наследуются как есть. Абстрактный класс хранит "
            "состояние в полях и может иметь конструктор, который вызывают наследники через base.\n\n"
            "Ключевое ограничение C#: класс наследует только один базовый класс, но может реализовать "
            "сколько угодно интерфейсов. Поэтому интерфейс — основной инструмент для выражения "
            "независимых соглашений: тип может быть одновременно IComparable, IDisposable и "
            "IEnumerable без какого-либо родства в дереве классов."
        ),
        table(
            ["Сценарий", "Что выбрать", "Почему"],
            [
                ["Контракт для несвязанных типов", "Интерфейс", "Один класс имеет только один базовый класс, а интерфейсов может быть много"],
                ["Нужна общая реализация и состояние", "Абстрактный класс", "Интерфейс не хранит поля, общую логику пришлось бы дублировать"],
                ["Нужен шаблонный алгоритм с точками расширения", "Абстрактный класс", "Шаблонный метод опирается на защищённые виртуальные члены"],
                ["Расширение опубликованной библиотеки", "Интерфейс с реализацией по умолчанию", "Добавление метода не ломает существующие реализации"],
                ["Обобщённая математика", "Интерфейс со статическими абстрактными членами", "Операторы объявляются как static abstract (C# 11)"],
                ["Иерархия версий и семейств", "Иерархия абстрактного класса", "Поведение развивается вместе с данными"],
            ],
        ),
        example(
            "csharp",
            """
            public interface IDisposable
            {
                void Dispose();
            }

            public interface ILogger
            {
                void Log(string message);

                // Реализация по умолчанию (C# 8+)
                void LogInfo(string message) => Log($"[INFO] {message}");
                void LogError(string message) => Log($"[ERROR] {message}");
            }

            public abstract class Animal
            {
                public string Name { get; protected set; }

                public abstract void MakeSound();
                public virtual void Sleep() => Console.WriteLine($"{Name} sleeps");
                public void Eat() => Console.WriteLine($"{Name} eats");

                protected Animal(string name) => Name = name;
            }

            public sealed class Dog : Animal
            {
                public Dog(string name) : base(name) { }

                public override void MakeSound() => Console.WriteLine("Woof!");
                public override void Sleep() => Console.WriteLine($"{Name} спит во сне о косточках");
            }
            """,
        ),
        example(
            "csharp",
            """
            var dog = new Dog("Бим");
            dog.Eat();        // унаследован без изменений
            dog.MakeSound();  // переопределён
            dog.Sleep();      // переопределён иначе, чем в базовом классе
            Console.WriteLine(dog is Animal);  // собака остаётся животным
            """,
        ),
        text(
            "Вывод:\n"
            "Бим eats\n"
            "Woof!\n"
            "Бим спит во сне о косточках\n"
            "True"
        ),
        callout(
            "info",
            "Правило выбора",
            "Начинайте с интерфейса: контракт проще, не занимает слот единственного базового класса "
            "и слабее связывает реализации. Переходите к абстрактному классу, когда появляется общее "
            "состояние или общая реализация, которую не хочется копировать. Не создавайте "
            "«на всякий случай» интерфейс с одним методом и одной реализацией — это лишний уровень "
            "косвенности без пользы."
        ),
        text(
            "Метод Eat объявлен обычным: он не предполагает вариаций, поэтому случайно переопределить его нельзя. "
            "Sleep виртуальный: у собаки поведение отличается, но наследовать версию базового класса допустимо. "
            "MakeSound абстрактный: у каждого животного звук свой, и забыть его реализовать компилятор не позволит. "
            "Такое распределение модификаторов и есть проектирование контракта."
        ),
        heading("Полиморфизм и принцип подстановки Лисков"),
        text(
            "Полиморфизм — способность одного кода работать с разными типами через общий контракт. "
            "В C# есть три его разновидности. Ad-hoc полиморфизм — это перегрузка методов: один и тот же "
            "метод с разными наборами параметров. Параметрический полиморфизм — обобщения: код один, "
            "а тип подставляется при использовании. Полиморфизм подтипов — переопределение виртуальных "
            "методов, когда переменная базового типа ссылается на объект производного, и вызов "
            "выбирает реализацию по фактическому типу объекта.\n\n"
            "Именно третий вид чаще всего называют ООП-полиморфизмом. Его гарантию формулирует "
            "принцип подстановки Лисков (Liskov Substitution Principle, LSP): объект производного "
            "класса должен использоваться везде, где ожидается объект базового, без изменения "
            "корректности программы. На практике это означает, что подтип не может усиливать "
            "предусловия (требовать больше, чем база), не может ослаблять постусловия (обещать "
            "меньше, чем база) и не должен бросать новые исключения."
        ),
        example(
            "csharp",
            """
            // Нарушение LSP: квадрат не является полноценным прямоугольником
            public class Rectangle
            {
                public virtual int Width { get; set; }
                public virtual int Height { get; set; }
            }

            public class Square : Rectangle
            {
                public override int Width
                {
                    set => base.Width = base.Height = value;
                }
                public override int Height
                {
                    set => base.Width = base.Height = value;
                }
            }

            static void Resize(Rectangle r, int w, int h)
            {
                r.Width = w;
                r.Height = h;
                // Ожидание: площадь w * h
            }
            """,
        ),
        text(
            "Метод Resize написан корректно с точки зрения типов, но получает неверный результат, если "
            "в него передать квадрат: второе присваивание перезаписывает первую сторону. Программа "
            "не падает и не выдаёт исключение: она молча считает неправильно, и это худший вид "
            "нарушения. Исправление — отказаться от наследования в пользу общего интерфейса и "
            "неизменяемых значений."
        ),
        example(
            "csharp",
            """
            public interface IShape
            {
                int Area();
            }

            public readonly record struct RectangleShape(int Width, int Height) : IShape
            {
                public int Area() => Width * Height;
            }

            public readonly record struct SquareShape(int Size) : IShape
            {
                public int Area() => Size * Size;
            }

            IShape[] shapes = [new RectangleShape(3, 4), new SquareShape(3)];
            Console.WriteLine(string.Join(", ", shapes.Select(s => s.Area())));
            """,
        ),
        text(
            "Вывод:\n"
            "12, 9\n\n"
            "Оба типа независимы, но разделяют контракт IShape, и клиентский код работает с ними "
            "одинаково. Проверка на LSP звучит так: можно ли подставить подтип туда, где написан "
            "старый код, и останется ли он правильным? Если ответ «нет» или «только если клиент "
            "проверяет тип», наследование выбрано неверно."
        ),
        heading("Ковариантность и контрвариантность"),
        text(
            "Обобщённые интерфейсы и делегаты в C# могут разрешать подстановку родственных типов. "
            "Параметр типа, помеченный ключевым словом out, называется ковариантным: он может "
            "появляться только в возвращаемых значениях. Это отражает свойство «производный можно "
            "вернуть как базовый»: читатель IReadOnlyRepository<Dog> одновременно является читателем "
            "IReadOnlyRepository<Animal>, ведь всё, что он возвращает, есть животное.\n\n"
            "Параметр типа, помеченный ключевым словом in, называется контрвариантным: он может "
            "появляться только в параметрах методов. Записывающий репозиторий, принимающий любое "
            "животное, справится и с собакой, поэтому IWriteOnlyRepository<Animal> пригоден там, где "
            "ожидают IWriteOnlyRepository<Dog>. В стандартной библиотеке так устроены IEnumerable<out T>, "
            "IComparer<in T>, Func<in T, out TResult> и Action<in T>.\n\n"
            "Важно: значимый и ссылочный типы подставить друг вместо друга нельзя, даже при "
            "объявленной вариантности: IEnumerable<string> не приводится к IEnumerable<object>, "
            "потому что эти значения устроены в памяти по-разному."
        ),
        example(
            "csharp",
            """
            public class Animal { }
            public class Dog : Animal { }

            public interface IReadOnlyRepository<out T>
            {
                T GetById(int id);
                IEnumerable<T> GetAll();
            }

            public interface IWriteOnlyRepository<in T>
            {
                void Add(T entity);
                void Remove(T entity);
            }

            public sealed class DogRepository : IReadOnlyRepository<Dog>
            {
                public Dog GetById(int id) => new Dog();
                public IEnumerable<Dog> GetAll() => new[] { new Dog() };
            }

            public sealed class AnimalWriter : IWriteOnlyRepository<Animal>
            {
                private int _count;
                public void Add(Animal entity) => _count++;
                public void Remove(Animal entity) => _count--;
                public int Count => _count;
            }

            IReadOnlyRepository<Animal> animals = new DogRepository();  // Dog -> Animal
            IWriteOnlyRepository<Dog> dogWriter = new AnimalWriter();  // Animal -> Dog
            dogWriter.Add(new Dog());
            dogWriter.Add(new Dog());
            dogWriter.Remove(new Dog());
            Console.WriteLine($"Собак у писателя: {((AnimalWriter)dogWriter).Count}");
            Console.WriteLine($"Животных: {animals.GetAll().Count()}");
            """,
        ),
        text(
            "Вывод:\n"
            "Собак у писателя: 1\n"
            "Животных: 1"
        ),
        heading("Композиция вместо наследования"),
        text(
            "Наследование моделирует отношение «является»: собака — животное, круг — фигура. "
            "Когда моделируемое отношение на самом деле звучит как «умеет» или «состоит из», "
            "наследование превращается в ловушку. Классический пример — автомобиль, который умеет "
            "летать: если завести подкласс FlyingCar от Car, придётся добавлять метод, который "
            "бессмысленен для всех остальных машин, а через три уровня иерархия становится такой "
            "ветвистой, что любое изменение угрожает рабочим сценариям.\n\n"
            "Композиция означает, что объект содержит другие объекты и делегирует им работу. "
            "Способности описываются отдельными интерфейсами, а класс собирает нужный набор "
            "способностей в конструкторе. Такой код проще тестировать (компоненты подменяются "
            "заглушками), проще развивать (новая способность — новая реализация, а не правка "
            "иерархии) и проще переиспользовать (одна и та же реализация двигателя годится "
            "и для машины, и для катера)."
        ),
        example(
            "csharp",
            """
            public interface IEngine { void Start(); void Stop(); }
            public interface IFlyable { void Fly(); double Altitude { get; } }
            public interface ISwimmable { void Swim(); double Depth { get; } }

            public sealed class ElectricEngine : IEngine
            {
                public void Start() => Console.WriteLine("Двигатель запущен");
                public void Stop() => Console.WriteLine("Двигатель остановлен");
            }

            public sealed class Propeller : IFlyable
            {
                public double Altitude { get; private set; }
                public void Fly() { Altitude += 100; Console.WriteLine($"Высота: {Altitude} м"); }
            }

            public sealed class PropellerDrive : ISwimmable
            {
                public double Depth { get; private set; }
                public void Swim() { Depth += 5; Console.WriteLine($"Глубина: {Depth} м"); }
            }

            public sealed class Vehicle
            {
                public IEngine Engine { get; }
                public IFlyable? FlyBehavior { get; }
                public ISwimmable? SwimBehavior { get; }

                public Vehicle(IEngine engine, IFlyable? fly = null, ISwimmable? swim = null)
                {
                    Engine = engine;
                    FlyBehavior = fly;
                    SwimBehavior = swim;
                }

                public void Fly() => FlyBehavior?.Fly();
                public void Swim() => SwimBehavior?.Swim();
            }

            var flyingCar = new Vehicle(new ElectricEngine(), new Propeller());
            var boat = new Vehicle(new ElectricEngine(), swim: new PropellerDrive());

            flyingCar.Engine.Start();
            flyingCar.Fly();
            boat.Swim();
            boat.Fly();
            """,
        ),
        text(
            "Вывод:\n"
            "Двигатель запущен\n"
            "Высота: 100 м\n"
            "Глубина: 5 м\n\n"
            "Последний вызов Fly у катера ничего не выводит: способность отсутствует, и обращение "
            "к ней безопасно пропускается благодаря оператору ?. Ни одна иерархия не выросла, "
            "но поведение настраивается при создании объекта."
        ),
        heading("Паттерн «Стратегия»"),
        text(
            "Самый частый случай композиции на практике — паттерн «Стратегия» (Strategy). "
            "Изменяемый алгоритм описывается интерфейсом, реализации содержат конкретные варианты, "
            "а класс-контекст получает стратегию извне. Он не знает, как именно выполняется работа, "
            "и не меняется при добавлении нового варианта: в этом практическая ценность.\n\n"
            "Контекст получает зависимость через конструктор, а не создаёт её сам. В больших "
            "приложениях такую сборку выполняет контейнер зависимостей, но принцип тот же."
        ),
        example(
            "csharp",
            """
            public interface IPaymentStrategy
            {
                void Pay(decimal amount);
            }

            public sealed class CreditCardPayment : IPaymentStrategy
            {
                public void Pay(decimal amount) => Console.WriteLine($"Карта: списано {amount:C}");
            }

            public sealed class PayPalPayment : IPaymentStrategy
            {
                public void Pay(decimal amount) => Console.WriteLine($"PayPal: списано {amount:C}");
            }

            public sealed class OrderService
            {
                private readonly IPaymentStrategy _payment;

                public OrderService(IPaymentStrategy payment) => _payment = payment;

                public void Checkout(decimal amount) => _payment.Pay(amount);
            }

            new OrderService(new CreditCardPayment()).Checkout(1500m);
            new OrderService(new PayPalPayment()).Checkout(700m);
            """,
        ),
        text(
            "Вывод:\n"
            "Карта: списано 1500,00\n"
            "PayPal: списано 700,00\n\n"
            "Сумма печатается форматом C, поэтому разделитель дробной части зависит от региональных настроек. "
            "Чтобы добавить оплату криптовалютой, достаточно написать новый "
            "класс с IPaymentStrategy, а OrderService остаётся неизменным."
        ),
        heading("Обобщения и ограничения"),
        text(
            "Обобщения (generics) позволяют писать тип или метод один раз, а работать со многими "
            "типами данных без потери проверки типов и без упаковки значимых типов. "
            "В отличие от object, где приведение проверяется во время выполнения, параметр типа "
            "проверяется компилятором. Для значимых типов среда выполнения создаёт "
            "специализированный вариант кода, поэтому List<int> не упаковывает элементы.\n\n"
            "Список операций, доступных для параметра типа, определяется ограничениями. "
            "Без ограничений разрешены только операции, общие для всех типов: сравнение с null, "
            "присваивание, вызов методов object. Ограничение class требует ссылочного типа, struct — "
            "значимого, new() разрешает создание экземпляра без параметров, unmanaged разрешает "
            "небезопасные операции над блоками памяти, notnull исключает null и nullable-значения, "
            "а ссылка на класс или интерфейс открывает его члены."
        ),
        example(
            "csharp",
            """
            public interface IEntity
            {
                int Id { get; }
            }

            public sealed class GenericRepository<T> where T : class, IEntity, new()
            {
                private readonly Dictionary<int, T> _items = new();

                public T Create() => new T();

                public void Save(T entity) => _items[entity.Id] = entity;

                public T? GetById(int id) => _items.TryGetValue(id, out var found) ? found : null;
            }

            public static class Validation
            {
                public static T Max<T>(IEnumerable<T> values, IComparer<T> comparer) where T : struct
                {
                    using var e = values.GetEnumerator();
                    e.MoveNext();
                    T best = e.Current;
                    while (e.MoveNext())
                        if (comparer.Compare(e.Current, best) > 0) best = e.Current;
                    return best;
                }

                public static T Default<T>(T value) where T : struct => value;
            }
            """,
        ),
        text(
            "Ограничения записываются через where и комбинируются через запятую, причём порядок "
            "фиксирован: сначала primary-ограничение (class, struct, unmanaged, notnull или базовый тип), "
            "затем интерфейсы, затем new(). Нарушение порядка — ошибка компиляции, а не предупреждение. "
            "Две распространённые ловушки: ограничение new() несовместимо с abstract-типами, "
            "а для значимого типа оно излишне, потому что конструктор без параметров у него есть всегда."
        ),
        text(
            "В примере ниже используется пространство имён System.Numerics, поэтому добавьте "
            "в начало файла using System.Numerics;."
        ),
        example(
            "csharp",
            """
            public static class Stats
            {
                public static T Add<T>(T a, T b) where T : INumber<T> => a + b;

                public static (T Sum, T Min, T Max) Calculate<T>(IEnumerable<T> values)
                    where T : INumber<T>
                {
                    using var e = values.GetEnumerator();
                    e.MoveNext();
                    T sum = e.Current, min = e.Current, max = e.Current;
                    while (e.MoveNext())
                    {
                        T v = e.Current;
                        sum += v;
                        if (v < min) min = v;
                        if (v > max) max = v;
                    }
                    return (sum, min, max);
                }
            }

            Console.WriteLine(Stats.Add(2, 3));
            Console.WriteLine(Stats.Add(1.5m, 2.25m));

            var ints = Stats.Calculate(new[] { 4, 9, 1, 7 });
            var doubles = Stats.Calculate(new[] { 0.5, 2.75, 1.25 });
            Console.WriteLine($"int: sum={ints.Sum}, min={ints.Min}, max={ints.Max}");
            Console.WriteLine($"double: sum={doubles.Sum}, min={doubles.Min}, max={doubles.Max}");
            """,
        ),
        text(
            "Вывод:\n"
            "5\n"
            "3.75\n"
            "int: sum=21, min=1, max=9\n"
            "double: sum=4.5, min=0.5, max=2.75\n\n"
            "Интерфейс INumber<T> появился в .NET 7 и опирается на статические абстрактные члены: "
            "компилятор разрешает операторы +, - и < именно потому, что они объявлены в ограничении. "
            "Одна реализация работает с int, decimal, double и любым собственным числовым типом."
        ),
        heading("Паттерны проектирования"),
        text(
            "Паттерн — повторяемое решение типовой задачи проектирования с известным набором "
            "участников и связей. Это описание структуры, которую нужно адаптировать к своей задаче. "
            "Полезно знать наизусть не десятки паттернов, а три-четыре базовых: их хватает "
            "в большинстве повседневных ситуаций.\n\n"
            "Factory Method решает задачу создания объектов, когда конкретный тип зависит от "
            "условий или должен быть скрыт от клиента. Builder собирает сложный объект пошагово, "
            "когда конструктор с десятком параметров уже нечитаем. Decorator добавляет поведение, "
            "оборачивая объект в другой объект с тем же интерфейсом, не изменяя исходный класс."
        ),
        example(
            "csharp",
            """
            public abstract class Document
            {
                public abstract void Open();
                public abstract void Save();
            }

            public sealed class WordDocument : Document
            {
                public override void Open() => Console.WriteLine("Открыт DOCX");
                public override void Save() => Console.WriteLine("Сохранён DOCX");
            }

            public sealed class PdfDocument : Document
            {
                public override void Open() => Console.WriteLine("Открыт PDF");
                public override void Save() => Console.WriteLine("Сохранён PDF");
            }

            public abstract class DocumentCreator
            {
                public abstract Document CreateDocument();

                public void Process()
                {
                    var doc = CreateDocument();
                    doc.Open();
                    doc.Save();
                }
            }

            public sealed class WordCreator : DocumentCreator
            {
                public override Document CreateDocument() => new WordDocument();
            }

            public sealed class PdfCreator : DocumentCreator
            {
                public override Document CreateDocument() => new PdfDocument();
            }

            new WordCreator().Process();
            new PdfCreator().Process();
            """,
        ),
        text(
            "Вывод:\n"
            "Открыт DOCX\n"
            "Сохранён DOCX\n"
            "Открыт PDF\n"
            "Сохранён PDF\n\n"
            "Метод Process описан в базовом классе один раз и не знает о конкретных форматах. "
            "Новый формат добавляется наследником, а не ветвлением внутри Process."
        ),
        example(
            "csharp",
            """
            public sealed class HttpRequestBuilder
            {
                private string _baseUrl = "";
                private TimeSpan _timeout = TimeSpan.FromSeconds(30);
                private readonly Dictionary<string, string> _headers = new();

                public HttpRequestBuilder WithBaseUrl(string url) { _baseUrl = url; return this; }
                public HttpRequestBuilder WithTimeout(TimeSpan t) { _timeout = t; return this; }
                public HttpRequestBuilder AddHeader(string key, string value) { _headers[key] = value; return this; }

                public (string Url, TimeSpan Timeout, int Headers) Build()
                {
                    if (string.IsNullOrWhiteSpace(_baseUrl))
                        throw new InvalidOperationException("Адрес не задан");
                    return (_baseUrl, _timeout, _headers.Count);
                }
            }

            var built = new HttpRequestBuilder()
                .WithBaseUrl("https://api.example.com")
                .WithTimeout(TimeSpan.FromSeconds(10))
                .AddHeader("Accept", "application/json")
                .AddHeader("User-Agent", "Kernify")
                .Build();

            Console.WriteLine(built);
            """,
        ),
        text(
            "Вывод:\n"
            "(https://api.example.com, 00:00:10, 2)\n\n"
            "Каждый метод возвращает тот же экземпляр, поэтому вызовы выстраиваются в цепочку. "
            "Метод Build проверяет обязательные данные и только потом создаёт результат. "
            "Вместо реального HttpClient здесь возвращается кортеж, чтобы пример оставался компактным."
        ),
        example(
            "csharp",
            """
            public interface INotifier
            {
                void Send(string message);
            }

            public sealed class EmailNotifier : INotifier
            {
                public void Send(string message) => Console.WriteLine($"Email: {message}");
            }

            public sealed class SmsNotifierDecorator : INotifier
            {
                private readonly INotifier _inner;

                public SmsNotifierDecorator(INotifier inner) => _inner = inner;

                public void Send(string message)
                {
                    _inner.Send(message);
                    Console.WriteLine($"SMS: {message}");
                }
            }

            INotifier notifier = new SmsNotifierDecorator(new EmailNotifier());
            notifier.Send("Заказ готов");
            """,
        ),
        text(
            "Вывод:\n"
            "Email: Заказ готов\n"
            "SMS: Заказ готов\n\n"
            "Декоратор реализует тот же интерфейс, что и оборачиваемый объект, поэтому его можно "
            "передавать куда угодно, где ожидается INotifier. Декораторы складываются в цепочку. "
            "Так устроены потоки .NET, где GZipStream оборачивает FileStream."
        ),
        heading("Принципы SOLID на практике"),
        text(
            "Пять принципов SOLID описывают свойства хорошо спроектированной системы. "
            "Single Responsibility (единственная ответственность) означает, что у класса "
            "одна причина для изменения. Open/Closed (открытость и закрытость) требует, "
            "чтобы расширение шло добавлением кода, а не правкой существующего. "
            "Liskov Substitution разобран выше. Interface Segregation (разделение "
            "интерфейсов) советует мелкие контракты вместо одного с десятком методов. "
            "Dependency Inversion (инверсия зависимостей) требует, чтобы модули зависели "
            "от абстракций, а не от конкретных классов. Принципы — ориентиры, а не законы: "
            "полезнее задать вопрос, какая перемена в будущем сломает этот код."
        ),
        table(
            ["Принцип", "Суть", "Признак нарушения в C#"],
            [
                ["Единственная ответственность", "У класса одна причина для изменения", "UserService сам отправляет письма и пишет в лог"],
                ["Открытость и закрытость", "Расширение без правки существующего кода", "switch по типу оплаты внутри ProcessOrder"],
                ["Подстановка Лисков", "Подтип заменяет базовый без сюрпризов", "MethodNotSupportedException из наследника"],
                ["Разделение интерфейсов", "Мелкие специализированные контракты", "IUserRepository с 15 методами, из которых нужно 3"],
                ["Инверсия зависимостей", "Модули зависят от абстракций", "new SmtpClient() внутри бизнес-логики"],
            ],
        ),
        example(
            "csharp",
            """
            // Нарушение: класс отвечает за сохранение, уведомление и журналирование
            public sealed class OrderServiceBefore
            {
                public void Place(Order order, string customer)
                {
                    Console.WriteLine("Заказ сохранён в базу");
                    Console.WriteLine($"Письмо для {customer}");
                    Console.WriteLine("Запись в журнал");
                }
            }

            public sealed class Order { public decimal Total { get; init; } }

            // После: каждая ответственность вынесена в отдельный контракт
            public interface IOrderRepository { void Save(Order order); }
            public interface IEmailSender { void Send(string to, string text); }
            public interface ILogger { void Log(string message); }

            public sealed class OrderService
            {
                private readonly IOrderRepository _repository;
                private readonly IEmailSender _email;
                private readonly ILogger _logger;

                public OrderService(IOrderRepository repository, IEmailSender email, ILogger logger)
                {
                    _repository = repository;
                    _email = email;
                    _logger = logger;
                }

                public void Place(Order order, string customer)
                {
                    _repository.Save(order);
                    _email.Send(customer, $"Заказ на {order.Total:C} принят");
                    _logger.Log("Заказ оформлен");
                }
            }

            public sealed class ConsoleEmailSender : IEmailSender
            {
                public void Send(string to, string messageText) => Console.WriteLine($"Письмо для {to}");
            }

            public sealed class ConsoleLogger : ILogger
            {
                public void Log(string message) => Console.WriteLine($"Лог: {message}");
            }

            public sealed class MemoryOrderRepository : IOrderRepository
            {
                public void Save(Order order) => Console.WriteLine("Заказ сохранён");
            }

            var service = new OrderService(new MemoryOrderRepository(), new ConsoleEmailSender(), new ConsoleLogger());
            service.Place(new Order { Total = 1200m }, "anna@example.com");
            """,
        ),
        text(
            "Вывод:\n"
            "Заказ сохранён\n"
            "Письмо для anna@example.com\n"
            "Лог: Заказ оформлен\n\n"
            "В тестах достаточно подставить реализации-заглушки, а замена базы данных или "
            "почтового провайдера не затрагивает бизнес-логику. Формат денежной суммы зависит "
            "от региональных настроек, поэтому в вашем выводе запись о письме может отличаться."
        ),
        example(
            "csharp",
            """
            // Нарушение принципа разделения интерфейсов
            public interface IRepository
            {
                void Add(string item);
                void Update(string item);
                void Delete(string item);
                void Export();
                void Backup();
            }

            // Правильно: два независимых контракта
            public interface IReadable { IReadOnlyList<string> GetAll(); }
            public interface IWritable { void Add(string item); }

            public sealed class InMemoryStore : IReadable, IWritable
            {
                private readonly List<string> _items = new();
                public IReadOnlyList<string> GetAll() => _items;
                public void Add(string item) => _items.Add(item);
            }

            IReadable reader = new InMemoryStore();
            if (reader is IWritable writer)
            {
                writer.Add("первый");
                writer.Add("второй");
            }
            Console.WriteLine(string.Join(", ", reader.GetAll()));
            """,
        ),
        text(
            "Вывод:\n"
            "первый, второй"
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Глубокое наследование на четыре уровня", "Любая правка базового класса затрагивает всё дерево", "Композиция и интерфейсы способностей"],
                ["Абстрактный класс там, где достаточно интерфейса", "Занят единственный слот наследования", "Интерфейс для чистого контракта"],
                ["Квадрат наследует прямоугольник", "Изменение одной стороны меняет другую", "Два независимых типа с общим IShape"],
                ["Метод наследника бросает NotSupportedException", "Клиент не может работать через базовый тип", "Пересмотреть иерархию, выделить отдельный контракт"],
                ["Обобщение без ограничения и приведение внутри", "Приведение падает во время выполнения", "Ограничение where T : IInterface"],
                ["Ограничение new() для значимого типа", "Избыточное ограничение, мешает расширению", "Оставить struct без new()"],
                ["Класс сам создаёт зависимости через new", "Нельзя подменить реализацию в тестах", "Передать зависимость через конструктор"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполняйте задания в консольном проекте .NET 8 или новее: `dotnet new console -o oop-design`, "
            "`cd oop-design`, затем `dotnet run`. Собирайте после каждого изменения, "
            "чтобы компилятор сразу указывал на обобщения без нужных ограничений."
        ),
        numbered(
            "Исправьте нарушение LSP: перепишите иерархию Rectangle и Square из урока так, чтобы метод Resize перестал быть опасным.",
            "Обобщённый репозиторий: реализуйте IRepository<T> с отдельными контрактами для чтения (ковариантность через out) и записи (контрвариантность через in).",
            "Стратегии валидации: создайте интерфейс IValidator с методом Validate, реализации для проверки длины строки и диапазона числа, а также класс, применяющий список валидаторов.",
            "Кэширующий декоратор: оберните репозиторий пользователей декоратором, который возвращает сохранённый результат для повторного идентификатора и считает число попаданий в кэш.",
            "Аудит SOLID: возьмите любой свой класс длиннее пятидесяти строк, выпишите причины для изменения и разделите его минимум на два типа с контрактами.",
        ),
        text("Пример ожидаемого результата для четвёртого задания:"),
        example(
            "text",
            "Первый запрос пользователя 42\n"
            "Из базы: Id=42, Имя=Анна\n"
            "Второй запрос пользователя 42\n"
            "Из кэша: Id=42, Имя=Анна\n"
            "Попаданий в кэш: 1"
        ),
        callout(
            "success",
            "Подсказка к заданию 1",
            "Не сохраняйте наследование между прямоугольником и квадратом. Введите общий интерфейс IShape с методом Area, "
            "сделайте оба типа неизменяемыми (readonly record struct)."
        ),
        heading("Проверьте себя"),
        numbered(
            "В каких случаях стоит выбирать абстрактный класс, а не интерфейс?",
            "Чем опасен метод наследника, который бросает NotSupportedException?",
            "Почему параметр типа out разрешено использовать только в возвращаемых значениях?",
            "Как формулируется принцип подстановки Лисков и как проверить иерархию на его соблюдение?",
            "Зачем нужны ограничения обобщений и что произойдёт, если их не указать?",
            "В чём отличие паттерна «Стратегия» от декоратора, если оба построены на интерфейсе?",
        ),
        heading("Ответы", 3),
        numbered(
            "Когда нужны общая реализация, состояние в полях и конструктор для наследников.",
            "Нарушается подстановка: клиентский код, написанный для базового типа, падает на части наследников.",
            "Читатель может возвращать производный тип вместо базового без нарушения ожиданий вызывающего кода.",
            "Объект подтипа должен работать везде, где ожидается базовый, без новых условий и проверок конкретного типа.",
            "Ограничения открывают доступ к членам типа: конструктору, интерфейсу, структуре памяти. Без них доступны только члены object.",
            "Стратегия подменяет алгоритм внутри объекта, а декоратор оборачивает объект, добавляя поведение вокруг вызова.",
        ),
        heading("Итоги"),
        bullets(
            "Интерфейс выражает контракт для независимых типов, абстрактный класс добавляет общую реализацию и состояние.",
            "Полиморфизм подтипов выбирает реализацию по фактическому типу объекта; подтип не должен усиливать предусловия.",
            "out даёт ковариантность в возвращаемых значениях, in — контрвариантность в параметрах.",
            "Композиция описывает отношение «состоит из», наследование — «является».",
            "Ограничения обобщений (class, struct, new(), unmanaged, notnull, интерфейс) открывают доступ к нужным операциям.",
            "Factory Method, Builder и Decorator решают задачи создания, пошаговой сборки и добавления поведения.",
            "SOLID помогает делать код расширяемым, но при буквальном применении ведёт к избыточным абстракциям.",
        ),
        heading("Что дальше"),
        text(
            "Следующий урок посвящён делегатам и событиям: вы узнаете, как передавать поведение как "
            "значение, в чём разница между делегатом и событием, как работает вариантность делегатов "
            "и как строится модель уведомлений, на которой держатся события платформы .NET. "
            "Материал урока о проектировании пригодится напрямую: подписка на события — это тот же "
            "контракт с клиентским кодом, только операция передаётся не через интерфейс, а через "
            "типизированный указатель на метод."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Документация Microsoft Learn: интерфейсы в C# — learn.microsoft.com/dotnet/csharp/fundamentals/types/interfaces",
            "Документация Microsoft Learn: ключевое слово abstract — learn.microsoft.com/dotnet/csharp/language-reference/keywords/abstract",
            "Ограничения параметров типа — learn.microsoft.com/dotnet/csharp/language-reference/keywords/where-generic-type-constraint",
            "Обобщённая математика в .NET — learn.microsoft.com/dotnet/standard/generics/math",
            "Принципы SOLID в архитектуре приложений .NET — learn.microsoft.com/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures",
            "Каталог паттернов проектирования на C# — refactoring.guru/design-patterns/csharp",
        ),
    ],
}
