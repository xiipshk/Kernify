"""Урок 3.1 курса csharp: продвинутая система типов."""

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
    "topic_order": 1,
    "name": "3.1. Продвинутая система типов",
    "slug": "csharp-3-1-продвинутая-система-типов",
    "short_description": (
        "Ограничения обобщённых типов, вариантность интерфейсов и делегатов, "
        "ссылочные nullable-типы, развитой pattern matching и записи от позиционных "
        "до record struct со сравнением по значению."
    ),
    "topic_name": "Продвинутая система типов",
    "topic_description": (
        "Возможности C#, которые превращают типы из описания данных в инструмент "
        "проектирования: where-ограничения и generic math, ковариантность и "
        "контравариантность, аннотации NRT с атрибутами анализа потока, "
        "свойства-паттерны, кортежные, реляционные и списочные паттерны, "
        "а также записи со сравнением по значению и неразрушающим обновлением."
    ),
    "learning_objectives": [
        "Подбирать ограничения обобщённого метода от class, struct, new() и notnull до unmanaged, Enum, Delegate и default",
        "Объяснять вариантность через безопасности присваивания и писать собственные интерфейсы с out и in",
        "Включать nullable-контекст и пользоваться аннотациями ?, !, а также атрибутами NotNullWhen, MaybeNull и MemberNotNull",
        "Строить паттерны-свойства, кортежные, реляционные и списочные паттерны с логическими связками or, and, not",
        "Применять записи, record struct и with-выражения, понимать семантику сравнения по значению, Equals, GetHashCode и ToString",
        "Оценивать стоимость и подводные камни, включая захват изменяемых объектов стратегиями с and и копирование больших структур",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "csharp",
        "обобщения",
        "вариантность",
        "nullable",
        "паттерны",
        "записи",
    ],
    "starter_code": code(
        r"""
        using System;

        record Money(decimal Amount, string Currency)
        {
            public Money Plus(Money other) =>
                Currency == other.Currency
                    ? this with { Amount = Amount + other.Amount }
                    : throw new InvalidOperationException("Валюты не совпадают");
        }

        decimal Discount(decimal total) => total switch
        {
            < 1000m => 0m,
            >= 1000m and < 5000m => total * 0.05m,
            _ => total * 0.1m,
        };

        var price = new Money(4000m, "RUB");
        var total = price.Plus(new Money(2500m, "RUB"));

        Console.WriteLine(total);
        Console.WriteLine($"Скидка: {Discount(total.Amount)}");
        Console.WriteLine(total == new Money(6500m, "RUB"));
        """
    ),
    "hints": [
        "Порядок ограничений в where фиксирован: сначала class, struct или notnull, затем базовый класс, затем интерфейсы, и только в конце new(). Нарушение порядка даёт ошибку компиляции CS0401.",
        "Вариантность объявляйте только у интерфейсов и делегатов и только там, где каждый параметр типа однозначно входной (in) или выходной (out). Если тип появляется и в параметрах, и в возвращаемых значениях, он инвариантен.",
        "В стратегии switch с and порядок ветвей задаёт приоритет: более конкретное условие должно стоять раньше общего, иначе оно станет недостижимым.",
        "Записи-классы сравниваются по значению через сгенерированные Equals и GetHashCode, а массивы и коллекции внутри записи сравниваются по ссылке, поэтому две записи с одинаковыми элементами массивов окажутся разными.",
    ],
    "content": [
        text(
            "До сих пор типы отвечали на вопрос «какие данные здесь лежат». "
            "На продвинутом уровне язык задаёт дополнительные вопросы: какие операции допустимы "
            "для параметра типа, можно ли подставить один обобщённый тип вместо другого, может ли "
            "ссылка быть пустой, в какую форму нужно привести значение, чтобы выбрать ветвь, и как "
            "отличить два объекта с одинаковыми данными.\n\n"
            "Все рассматриваемые механизмы работают на этапе компиляции: ограничения обобщений "
            "позволяют компилятору находить операцию, вариантность разрешает безопасные присваивания, "
            "ссылочные nullable-типы превращают возможные исключения в предупреждения, "
            "паттерны заменяют цепочки проверок типов, а записи дают сравнение по значению.\n\n"
            "Урок рассчитан на разработчиков, которые свободно пишут обобщённые методы и знают "
            "лямбда-выражения. Основное внимание уделено правилам выбора и ограничениям механизмов."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "подбирать ограничения обобщённых типов от class и struct до unmanaged, Enum, Delegate и default, а также понимать, почему для generic math нужен интерфейс-себя-ограничение;",
            "объяснять вариантность через тест «безопасно ли это присваивание» и проектировать собственные интерфейсы с параметрами out и in;",
            "включать nullable-контекст проекта, различать состояния анализа потока и применять аннотации ?, ! вместе с атрибутами NotNullWhen, MaybeNull и MemberNotNull;",
            "описывать условия паттернами-свойствами, кортежными, реляционными и списочными паттернами, комбинируя их связками or, and, not;",
            "создавать записи, record struct и readonly record struct, применять with-выражения и объяснять, как работает сравнение по значению;",
            "распознавать ограничения механизмов: копирование больших структур, потери гарантий NRT после каста и наследование записей только от записей.",
        ),
        heading("Ограничения обобщений: отражение возможностей типа"),
        text(
            "Ограничение обобщения (constraint) — обещание, которое вы даёте компилятору о "
            "параметре типа. Взамен компилятор позволяет вызывать операции, гарантированные этим "
            "обещанием, и запрещает подставлять типы, обещание нарушающие. "
            "Без ограничений параметр типа равносилен `where T : object`, поэтому доступны только "
            "члены `object`: `ToString`, `Equals`, `GetHashCode` и `GetType`.\n\n"
            "Ограничения проверяются при закрытии типа конкретным аргументом, но не при объявлении "
            "открытого `Repository<T>`. Таблица ниже сопоставляет основные виды ограничений."
        ),
        example(
            "csharp",
            """
            static void Main()
            {
                Console.WriteLine(typeof(Repository<object>).Name);
                Console.WriteLine(typeof(Repository<object>).GetGenericArguments()[0].Name);

                // Ошибка компиляции CS0452: int не является ссылочным типом.
                // var bad = new Repository<int>();

                Console.WriteLine(Sum(new[] { 1, 2, 3, 4 }));
                Console.WriteLine(Sum(new[] { 0.5, 1.25, 2.0 }));
                Console.WriteLine(Max(new[] { "яблоко", "груша", "банан" }));
            }

            class Repository<T> where T : class { }

            static T Sum<T>(IEnumerable<T> values)
                where T : IAdditionOperators<T, T, T>, IAdditiveIdentity<T, T>
            {
                T total = T.AdditiveIdentity;
                foreach (T value in values)
                {
                    total += value;
                }
                return total;
            }

            static T Max<T>(IEnumerable<T> values) where T : IComparable<T>
            {
                T best = values.First();
                foreach (T value in values)
                {
                    if (value.CompareTo(best) > 0)
                    {
                        best = value;
                    }
                }
                return best;
            }
            """
        ),
        text(
            "Вывод: `Repository\\`1`, `Object`, затем `10`, `3,75` и `яблоко`. Первые две строки поясняют, "
            "что обобщённый тип закрывается аргументом `object` независимо от имени параметра, а "
            "вызов `Sum` работает и для целых, и для чисел с плавающей точкой благодаря generic math."
        ),
        heading("Виды ограничений и их сочетания", 3),
        text(
            "Порядок ограничений строгий: после двоеточия одно из слов "
            "`class`, `struct` или `notnull`, затем не более одного базового класса, затем любое "
            "число интерфейсов, и в самом конце — `new()`. Нарушение порядка даёт ошибку CS0401.\n\n"
            "`struct` запрещает `Nullable<T>`, `unmanaged` требует значимый тип без ссылок на "
            "любом уровне вложенности, `Enum` и `Delegate` не сочетаются с `class` и `struct`, "
            "а `default` имеет смысл только в переопределениях."
        ),
        table(
            ["Ограничение", "Разрешено", "Запрещено", "Типичное применение"],
            [
                ["`class`", "любой ссылочный тип", "`int`, `struct`", "хранение объектов в безразличных к типу контейнерах"],
                ["`struct`", "значимые типы без `Nullable<T>`", "`string`, `Nullable<int>`", "структуры без боксинга"],
                ["`new()`", "типы с открытым конструктором без параметров", "типы только с интерфейсным конструктором, абстрактные", "фабрики и репозитории"],
                ["`notnull`", "любой тип, кроме `Nullable<T>`", "`Nullable<int>`, `string?`", "ключи словарей"],
                ["`unmanaged`", "`int`, `DateTime`, `Guid`, указатели", "`string`, классов и структуры со ссылками", "межъязыковой обмен, буферы"],
                ["`Enum`", "перечисления", "классы, оболочки интерфейсов", "типобезопасные флаги"],
                ["`unmanaged`, `Delegate`", "делегаты и их потомки", "лямбды как аргумент типа", "регистрация обработчиков"],
            ],
        ),
        callout(
            "info",
            "Почему generic math требует «себя» в ограничении",
            "Для арифметики нужно, чтобы тип умел складываться сам с собой, но до появления generic math такой операции не существовало. "
            "Интерфейсы вроде `IAdditionOperators<TSelf, TOther, TResult>` решают проблему тем, что параметр ограничения ссылается на сам тип: "
            "`where T : INumber<T>`. Это называется ограничением-себя (self constraint) и допустимо только для интерфейсов.",
        ),
        heading("Вариантность: безопасное преобразование обобщённых типов"),
        text(
            "Вариантность (variance) отвечает на вопрос, можно ли присвоить `IEnumerable<Derived>` переменной типа "
            "`IEnumerable<Base>`. Тест — представить, какие операции станут доступны через "
            "новую переменную, и проверить, не нарушают ли они исходную логику.\n\n"
            "Ковариантность (`out`) означает, что тип используется только как результат: "
            "`IEnumerable<Dog>` безопасно стать `IEnumerable<Animal>`. Контравариантность (`in`) "
            "зеркальна: тип используется только как аргумент, поэтому `IComparer<Animal>` безопасно "
            "стать `IComparer<Dog>`. Инвариантность (`IList<T>`) запрещает преобразование, потому что "
            "параметр встречается и на входе, и на выходе.\n\n"
            "Вариантность объявляется только у интерфейсов и делегатов. Если параметр с `out` "
            "появится в списке параметров метода, вы получите ошибку CS1961."
        ),
        example(
            "csharp",
            """
            IEnumerable<Dog> dogs = new List<Dog> { new("Рекс", "Лабрадор") };
            IEnumerable<Animal> animals = dogs;                 // out T

            Action<Animal> inspect = a => Console.WriteLine($"Животное: {a.Name}");
            Action<Dog> inspectDog = inspect;                   // in T

            IComparer<Animal> byName = Comparer<Animal>.Create(
                (left, right) => string.Compare(left.Name, right.Name, StringComparison.Ordinal));
            IComparer<Dog> dogComparer = byName;                // in T

            foreach (Animal animal in animals)
            {
                Console.WriteLine(animal.Name);
            }

            inspectDog(dogs.First());
            Console.WriteLine(dogComparer.Compare(new Dog("Альфа", "Метис"), new Dog("Бета", "Метис")));

            // Ошибка компиляции CS0266: IList<T> инвариантен.
            // IList<Animal> list = new List<Dog>();

            abstract record Animal(string Name);
            record Dog(string Name, string Breed) : Animal(Name);
            """
        ),
        text(
            "Вывод: `Рекс`, затем `Животное: Рекс`, затем `-1`. Метод `Compare` возвращает отрицательное "
            "число, потому что имя `Альфа` стоит раньше `Бета`. Второе присваивание проходит, хотя "
            "параметр типа объявлен как `in`."
        ),
        heading("Собственные вариантности интерфейсов", 3),
        text(
            "Разделяйте чтение и запись по отдельным интерфейсам: читающий делают "
            "ковариантным, изменяющий — контравариантным, а затем объединяют их в инвариантном.\n\n"
            "Объявляйте вариантность только после проверки, что "
            "каждый параметр однозначно входной или выходной. Комбинация `in` и `out` на одном "
            "параметре невозможна."
        ),
        example(
            "csharp",
            """
            IReadOnlyStore<Dog> dogs = new Store<Dog>();
            IReadOnlyStore<Animal> animals = dogs;      // out T: читаем как животных
            Console.WriteLine(animals.GetAll().Count());

            IWriteStore<Animal> sink = new Sink<Animal>();
            IWriteStore<Dog> dogSink = sink;            // in T: пишем собак в приёмник животных
            dogSink.Add(new Dog("Рекс", "Метис"));
            Console.WriteLine(sink.Count);

            interface IReadOnlyStore<out T>
            {
                IEnumerable<T> GetAll();
                T Get(int index);
            }

            interface IWriteStore<in T>
            {
                void Add(T item);
            }

            interface IStore<T> : IReadOnlyStore<T>, IWriteStore<T> { }

            sealed class Store<T> : IStore<T> where T : class
            {
                private readonly List<T> _items = new();

                public IEnumerable<T> GetAll() => _items;

                public T Get(int index) => _items[index];

                public void Add(T item) => _items.Add(item);
            }

            sealed class Sink<T> : IWriteStore<T>
            {
                public int Count { get; private set; }

                public void Add(T item) => Count++;
            }
            """
        ),
        text(
            "Вывод: `0` и `1`. Оба интерфейса работают через ссылки на один и тот же объект: "
            "`IReadOnlyStore<Dog>` читается как `IReadOnlyStore<Animal>` и сообщает, что значений нет — "
            "содержимое пустого хранилища не изменилось. Запись через контравариантную ссылку "
            "`IWriteStore<Dog>` попадает в исходный приёмник `Sink<Animal>`, поэтому счётчик равен единице."
        ),
        heading("Ссылочные nullable-типы и анализ потока"),
        text(
            "Ссылочные nullable-типы (nullable reference types, NRT) — система статических "
            "предупреждений, а не изменение среды исполнения. При включённом контексте `string` "
            "означает «непустая ссылка», а `string?` — «может быть null». Включение выполняется "
            "в файле проекта (`<Nullable>enable</Nullable>`) или директивой `#nullable enable`.\n\n"
            "У выражения есть состояние анализа потока (flow state): `NotNull`, `MaybeNull` или `None`. "
            "После `if (value is not null)` переменная считается `NotNull` до конца ветви. "
            "Знак `!` сообщает «здесь null невозможен», но это обещание, а не проверка."
        ),
        example(
            "csharp",
            """
            #nullable enable

            static void Main()
            {
                string? nickname = ReadNickname();
                if (nickname is not null)
                {
                    Console.WriteLine($"Длина: {nickname.Length}");
                }
                else
                {
                    Console.WriteLine("Псевдоним не задан");
                }

                // CS8602: возможное разыменование null без проверки.
                // Console.WriteLine(nickname.Length);

                string greeting = "Здравствуйте";
                Console.WriteLine(greeting.ToUpperInvariant());
                Console.WriteLine(nickname ?? "гость");
            }

            static string? ReadNickname() => null;
            """
        ),
        text(
            "Вывод: `Псевдоним не задан` и `гость`. Строка `nickname.Length` вне проверки дала бы "
            "предупреждение CS8602, но не ошибку: NRT по умолчанию не останавливает сборку."
        ),
        heading("Атрибуты анализа и обобщения с notnull", 3),
        text(
            "Метод `TryGetValue` возвращает признак успеха и значение одновременно, поэтому "
            "аннотация `out string?` не описывает связь между ними. Атрибуты анализа потока из "
            "`System.Diagnostics.CodeAnalysis` выражают эту зависимость:\n\n"
            "- `[NotNullWhen(true)]` — параметр не null, если метод вернул `true`;\n"
            "- `[return: NotNull]` и `[return: MaybeNull]` — гарантии возвращаемого значения;\n"
            "- `[MemberNotNull(nameof(...))]` — метод заполнил перечисленные поля.\n\n"
            "Ограничение `notnull` запрещает в качестве аргумента `Nullable<T>` и nullable-ссылку."
        ),
        example(
            "csharp",
            """
            using System.Diagnostics.CodeAnalysis;

            sealed class Settings
            {
                private string _connection = null!;

                [MemberNotNull(nameof(_connection))]
                public void Use(string connection) => _connection = connection;

                public string Describe() => _connection;
            }

            static bool TryParsePositive(string? input, [NotNullWhen(true)] out int? value)
            {
                if (int.TryParse(input, out int parsed) && parsed > 0)
                {
                    value = parsed;
                    return true;
                }

                value = null;
                return false;
            }

            [return: NotNull]
            static string Label(string? value) => value ?? "по умолчанию";

            var settings = new Settings();
            settings.Use("Server=local");
            Console.WriteLine(settings.Describe());
            Console.WriteLine(Label(null));

            if (TryParsePositive("42", out int? number))
            {
                Console.WriteLine(number + 1);
            }

            if (TryParsePositive("-7", out int? rejected))
            {
                Console.WriteLine(rejected);
            }
            else
            {
                Console.WriteLine("Отрицательное значение отклонено");
            }
            """
        ),
        text(
            "Вывод: `Server=local`, `по умолчанию`, `43` и `Отрицательное значение отклонено`. Внутри "
            "ветви с `true` компилятор считает `number` не null благодаря `NotNullWhen`."
        ),
        callout(
            "warning",
            "NRT не защищает от null во время исполнения",
            "Аннотации и `!` не генерируют проверок. Данные из JSON, базы, рефлексии и legacy-библиотек "
            "могут содержать null при любой аннотации. Проверяйте аргументы публичных API "
            "через `ArgumentNullException.ThrowIfNull`.",
        ),
        heading("Развитой pattern matching: свойства, кортежи и реляционные паттерны"),
        text(
            "Паттерн (pattern) — правило проверки формы значения. В отличие от `if (obj is Type t)`, "
            "развитой pattern matching проверяет тип, значения свойств и структуру одновременно.\n\n"
            "Паттерн-свойство записывается в фигурных скобках: "
            "`{ Age: >= 18 }`, вложенные свойства — через точку: `{ Address.Country: \"Россия\" }`. "
            "Внутри проверок применяются реляционные паттерны `<`, `<=`, `>`, `>=` и связки "
            "`and`, `or`, `not`. Кортежный паттерн проверяет несколько значений, списочный (C# 11) — "
            "элементы коллекции и срез `..`.\n\n"
            "`switch`-выражение останавливается на первой подошедшей ветви, "
            "поэтому конкретные условия указывают раньше общих."
        ),
        example(
            "csharp",
            """
            record Address(string City, string Country);

            record Person(string Name, int Age, Address Address);

            var anna = new Person("Анна", 30, new Address("Москва", "Россия"));
            var oleg = new Person("Олег", 17, new Address("Казань", "Россия"));

            Console.WriteLine(Describe(anna));
            Console.WriteLine(Describe(oleg));

            string Quadrant((int x, int y) point) => point switch
            {
                (0, 0) => "Начало координат",
                (> 0, > 0) => "I четверть",
                (< 0, > 0) => "II четверть",
                (< 0, < 0) => "III четверть",
                (> 0, < 0) => "IV четверть",
                (0, _) => "Ось Y",
                _ => "Ось X",
            };

            Console.WriteLine(Quadrant((3, 4)));
            Console.WriteLine(Quadrant((-2, 5)));
            Console.WriteLine(Quadrant((0, 7)));
            Console.WriteLine(Quadrant((5, 0)));

            string Describe(Person person) => person switch
            {
                { Age: < 18 } => $"{person.Name}: несовершеннолетний",
                { Age: >= 18 and < 65, Address.Country: "Россия" } => $"{person.Name}: взрослый житель России",
                { Age: >= 65 } => $"{person.Name}: пенсионер",
                _ => $"{person.Name}: взрослый",
            };
            """
        ),
        text(
            "Вывод: `Анна: взрослый житель России`, `Олег: несовершеннолетний`, `I четверть`, "
            "`II четверть`, `Ось Y`, `Ось X`. Обратите внимание: кортеж `(0, 7)` не подошёл ни под "
            "квадранты, потому что оба компонента должны быть строго положительными."
        ),
        heading("Списочные и типовые паттерны с условием when", 3),
        text(
            "Списочный паттерн описывает длину и крайние элементы. `[]` "
            "означает пустую последовательность, `[1, 2, ..]` — начинается с единицы и двойки, "
            "`[.., 0]` — заканчивается нулём. Срез `..` работает для массива, `List<T>`, "
            "`Span<T>` и любого типа с `Length` или `Count` и индексатором.\n\n"
            "Условие `when` дополняет типовой паттерн произвольным логическим выражением, когда "
            "проверка не выражается паттернами, например для сравнения двух значений между собой."
        ),
        example(
            "csharp",
            """
            static string Describe(int[] numbers) => numbers switch
            {
                [] => "Пустой",
                [0] => "Только ноль",
                [1, 2, ..] => "Начинается с 1 и 2",
                [.., 0] => "Заканчивается нулём",
                [var first, .., var last] when first == last => "Палиндром по краям",
                _ => $"Произвольный набор из {numbers.Length} элементов",
            };

            Console.WriteLine(Describe(Array.Empty<int>()));
            Console.WriteLine(Describe(new[] { 0 }));
            Console.WriteLine(Describe(new[] { 1, 2, 3 }));
            Console.WriteLine(Describe(new[] { 4, 5, 0 }));
            Console.WriteLine(Describe(new[] { 7, 8, 7 }));

            static string Classify(object value) => value switch
            {
                string s when s.Length > 5 => $"Длинная строка: {s}",
                string s => $"Короткая строка: {s}",
                int i when i > 0 => $"Положительное число: {i}",
                int i => $"Число: {i}",
                null => "Null",
                _ => "Неизвестный тип",
            };

            Console.WriteLine(Classify("переменная"));
            Console.WriteLine(Classify(42));
            Console.WriteLine(Classify(-1));
            """
        ),
        text(
            "Вывод: `Пустой`, `Только ноль`, `Начинается с 1 и 2`, `Заканчивается нулём`, "
            "`Палиндром по краям`, `Длинная строка: переменная`, `Положительное число: 42`, "
            "`Число: -1`. Ветвь `[var first, .., var last]` сработала для `7, 8, 7`, потому что "
            "первый и последний элементы совпали."
        ),
        callout(
            "warning",
            "Связка and вычисляет свои части полностью",
            "Паттерн `or` возвращает управление сразу после первого совпадения, но вторая часть "
            "может оказаться вычисленной, если проверка выражена через составные условия. Не выполняйте записи "
            "в поля внутри `and` и не полагайтесь на то, что вторая часть не будет вычислена: "
            "такой код компилируется, но работает неочевидно.",
        ),
        heading("Записи: сравнение по значению и копирование с изменением"),
        text(
            "Запись (record) — тип, который компилятор дополняет конструктором, свойствами только "
            "для инициализации, оператором `==`, методами `Equals`, `GetHashCode` и `ToString`, "
            "а также поддержкой `with`-выражений и деконструкции. В отличие от классов, две записи "
            "с одинаковыми значениями равны.\n\n"
            "`with { Age = 26 }` создаёт поверхностную копию с изменёнными свойствами: ссылочные "
            "поля копируются как ссылки, поэтому вложенные объекты остаются общими. "
            "`ToString` у записи печатает имя и свойства в фигурных скобках."
        ),
        example(
            "csharp",
            """
            var first = new Person("Иван", "Иванов", 25);
            var older = first with { Age = 26 };
            var renamed = first with { FirstName = "Пётр" };

            Console.WriteLine(first);
            Console.WriteLine(older);
            Console.WriteLine(renamed);
            Console.WriteLine(first == older);
            Console.WriteLine(first == new Person("Иван", "Иванов", 25));
            Console.WriteLine(first.GetHashCode() == new Person("Иван", "Иванов", 25).GetHashCode());

            (string firstName, string lastName, int age) = first;
            Console.WriteLine($"{firstName} {lastName}: {age}");

            public record Person(string FirstName, string LastName, int Age)
            {
                public string FullName => $"{FirstName} {LastName}";

                public Person
                {
                    if (Age < 0)
                    {
                        throw new ArgumentOutOfRangeException(nameof(Age));
                    }
                }
            }
            """
        ),
        text(
            "Вывод: `Person { FirstName = Иван, LastName = Иванов, Age = 25 }`, "
            "`Person { FirstName = Иван, LastName = Иванов, Age = 26 }`, "
            "`Person { FirstName = Пётр, LastName = Иванов, Age = 25 }`, затем `False`, `True`, "
            "`True` и `Иван Иванов: 25`. Оператор `==` у записи сравнивает значения всех "
            "свойств, а `ToString` печатает их автоматически."
        ),
        heading("record struct, readonly и сравнение с классами", 3),
        text(
            "`record struct` объединяет преимущества значения и равенства по значению. "
            "`readonly record struct` рекомендуема для небольших координат, диапазонов и "
            "идентификаторов: она не выделяет объект в куче.\n\n"
            "У `record struct` без модификатора `readonly` компилятор не создаёт `==` сам, "
            "поэтому сравнение выполняют через `Equals` или требуют явного оператора. "
            "Копирование структуры при передаче копирует все поля, поэтому структура из десятков "
            "полей в цикле может оказаться медленнее класса."
        ),
        table(
            ["Тип", "Равенство по умолчанию", "Где живёт", "Изменяемость"],
            [
                ["`class`", "по ссылке", "управляемая куча", "свойства по желанию"],
                ["`record` (класс)", "по значению всех свойств", "управляемая куча", "обычно с `init`"],
                ["`struct`", "по значению, если его объявили", "стек или тело объекта", "по полям"],
                ["`record struct`", "по значению всех полей", "по месту объявления", "свойства доступны для записи"],
                ["`readonly record struct`", "по значению всех полей", "по месту объявления", "неизменяемый после создания"],
            ],
        ),
        example(
            "csharp",
            """
            var start = new Point(3, 4);
            var moved = start with { X = 5 };
            Console.WriteLine(start);
            Console.WriteLine(moved);
            Console.WriteLine(start.Equals(moved));
            Console.WriteLine(start.Equals(new Point(3, 4)));
            Console.WriteLine(new Point(3, 4).DistanceFromOrigin.ToString("F1"));

            var left = new PlainPerson("A");
            var right = new PlainPerson("A");
            Console.WriteLine(left == right);

            var firstRecord = new Tag("A");
            var secondRecord = new Tag("A");
            Console.WriteLine(firstRecord == secondRecord);

            public readonly record struct Point(int X, int Y)
            {
                public double DistanceFromOrigin => Math.Sqrt(X * X + Y * Y);
            }

            public class PlainPerson
            {
                public PlainPerson(string name) => Name = name;

                public string Name { get; }
            }

            public record Tag(string Value);
            """
        ),
        text(
            "Вывод: `Point { X = 3, Y = 4 }`, `Point { X = 5, Y = 4 }`, затем `False`, `True`, "
            "`5,0` и `False`, `True`. Класс `PlainPerson` не переопределяет `Equals`, поэтому "
            "два экземпляра с одинаковым именем не равны, а запись `Tag` сравнивается по значению."
        ),
        heading("Записи и наследование: закрытая иерархия моделей"),
        text(
            "Записи образуют собственные иерархии: запись может наследоваться только от записи. "
            "Абстрактная запись — удобный корень модели данных, а `switch` по конкретным записям "
            "даёт исчерпывающую обработку с явным случаем по умолчанию."
        ),
        example(
            "csharp",
            """
            abstract record Shape;
            record Circle(double Radius) : Shape;
            record Rectangle(double Width, double Height) : Shape;
            record Triangle(double Base, double Height) : Shape;

            static double Area(Shape shape) => shape switch
            {
                Circle c => Math.PI * c.Radius * c.Radius,
                Rectangle { Width: var w, Height: var h } => w * h,
                Triangle t => t.Base * t.Height / 2,
                _ => throw new ArgumentOutOfRangeException(nameof(shape)),
            };

            Shape[] shapes =
            {
                new Circle(2),
                new Rectangle(3, 4),
                new Triangle(6, 2),
            };

            foreach (Shape shape in shapes)
            {
                Console.WriteLine($"{shape.GetType().Name}: {Area(shape):F2}");
            }

            var plan = new Rectangle(3, 4) with { Width = 10 };
            Console.WriteLine(plan);
            Console.WriteLine(plan == new Rectangle(10, 4));
            Console.WriteLine(new Circle(1) == new Circle(1));
            Console.WriteLine(((Shape)new Circle(1)).Equals(new Circle(1)));
            """
        ),
        text(
            "Вывод в стиле ru-RU: `Circle: 12,57`, `Rectangle: 12,00`, `Triangle: 6,00`, затем "
            "`Rectangle { Width = 10, Height = 4 }`, `True`, `True`, `True`. Последняя строка "
            "сравнивает через `Equals` значение переменной типа `Shape` с кругом того же радиуса: "
            "генерируемый `Equals` проверяет точный тип во время исполнения."
        ),
        heading("Как выбирать инструмент"),
        text(
            "Механизмы урока отвечают на разные вопросы: обобщения и вариантность определяют, что "
            "можно сделать с контейнером, паттерны — как ветвить логику, записи — как описывать данные. "
            "Практические правила:\n\n"
            "- алгоритм для многих типов — минимальные ограничения вместо `object`;\n"
            "- API хранения — разделение читающего и изменяющего интерфейсов и вариантность "
            "при одностороннем использовании параметра;\n"
            "- возможное отсутствие значения — NRT и аннотации, `!` только при внешней гарантии;\n"
            "- ветвление по форме данных — `switch`-выражение с паттернами;\n"
            "- набор данных — запись или `readonly record struct` для частых мелких значений."
        ),
        table(
            ["Задача", "Инструмент", "Почему"],
            [
                ["один алгоритм для чисел", "`where T : INumber<T>`", "арифметика проверяется компилятором"],
                ["один алгоритм для ссылок", "`where T : class`", "исключает упаковку"],
                ["чтение коллекции как базового типа", "`IReadOnlyList<out T>`", "ковариантность безопасна для чтения"],
                ["сравнение объектов извне", "`IComparer<in T>`", "контравариантность безопасна для аргументов"],
                ["возможное отсутствие строки", "`string?` и проверка потока", "ошибка видна при сборке"],
                ["значение зависит от структуры", "`switch` с паттернами", "исчерпывающая проверка ветвей"],
                ["модель данных неизменяема", "`record` или `readonly record struct`", "равенство по значению и `with`"],
            ],
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["`where T : class?`", "Ограничение допускает nullable-ссылки, но не заменяет `class` без причины и провоцирует предупреждения CS8602 при разыменовании", "`where T : class` для непустых ссылок; `class?` только тогда, когда null допустим"],
                ["`new()` перед базовым классом", "Ошибка CS0401: нарушен порядок ограничений", "Сначала `class`/`struct`/`notnull`, затем базовый класс, затем интерфейсы, `new()` последним"],
                ["`in` или `out` у класса", "Ошибка CS1962: вариантность допустима только для интерфейсов и делегатов", "Вынесите контракт в интерфейс"],
                ["`out T` там, где `T` — параметр метода", "Ошибка CS1961: некорректное использование вариантного параметра", "Оставьте интерфейс инвариантным или разделите его"],
                ["`!` вместо проверки", "Компилятор молчит, исключение возникает в рантайме", "`if`/`is not null` или `ArgumentNullException.ThrowIfNull`"],
                ["Общая ветвь раньше конкретной", "Ошибка CS8510: недостижимый паттерн", "Сортируйте ветви от конкретных к общим"],
                ["Запись с массивом внутри", "Две записи с одинаковыми элементами не равны", "Сравнивайте элементы отдельно или используйте неизменяемую коллекцию"],
                ["`record struct` и ожидание `==`", "Сравнение через `==` недоступно без явного объявления", "`readonly record struct` и `Equals` или явный `operator ==`"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполняйте задания в проекте .NET 8 с параметром `<Nullable>enable</Nullable>` и "
            "языком C# 12. Для заданий, связанных со сборкой, запускайте `dotnet build` и "
            "следите за предупреждениями: их отсутствие — часть критерия."
        ),
        numbered(
            "Реализуйте класс `Repository<T>` с ограничениями `where T : class, IEntity, new()`, где `IEntity` объявляет `Id` и `CreatedAt`. Добавьте метод `Add`, который назначает `Id` через `Guid.NewGuid()`, если идентификатор пуст.",
            "Спроектируйте пару интерфейсов `IReadOnlyFeed<out T>` с методами `GetAll` и `Get` и `IWriter<in T>` с одним `Add`. Объедините их в инвариантный `IFeed<T>` и продемонстрируйте оба присваивания в отдельном методе, пометив места, где преобразование запрещено.",
            "Возьмите класс с двумя nullable-полями, включите NRT, исправьте все предупреждения: используйте `?` для параметров, `!` только с обоснованием в комментарии и атрибут `NotNullWhen` для метода, возвращающего признак успеха.",
            "Напишите разбор строки команды `add купить молоко 120` и `remove 7` через кортежные паттерны и паттерны-свойства. Неизвестная команда должна возвращать понятное описание, а не исключение.",
            "Опишите набор DTO для API: `abstract record Request`, `record CreateRequest(string Title, decimal Amount) : Request`, `record UpdateRequest(Guid Id, decimal Amount) : Request`. Реализуйте обработчик через `switch` без приведения типов и продемонстрируйте неразрушающее обновление через `with`.",
        ),
        example(
            "text",
            """
            dotnet build
            Ожидаемая часть вывода для задания 3 при корректном исправлении:
            Сборка успешно завершена.
                0 Предупреждений
                0 Ошибок
            """
        ),
        callout(
            "success",
            "Подсказка к заданию 4",
            "Сначала разделите строку на команду и аргументы, затем переключитесь по `parts` с "
            "кортежным паттерном: `[\"add\", var title, var amount] when decimal.TryParse(amount, out var sum)`. "
            "Условие `when` нужно, потому что `TryParse` — не паттерн.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему параметр типа с ограничением `struct` нельзя закрыть типом `Nullable<int>`?",
            "В каком направлении безопасна ковариантность и почему `IList<T>` не может быть ковариантным?",
            "Чем `string?` отличается от `string` при включённом nullable-контексте?",
            "Что не так с паттерном `{ Age: >= 18 } or { Age: < 18 }` в ветви `switch`-выражения?",
            "Почему две записи с одинаковыми элементами массива внутри не равны?",
        ),
        heading("Ответы", 3),
        numbered(
            "`struct` разрешает только значимые типы, значения которых не бывает null. `Nullable<int>` — структура, но она несёт особое значение null, поэтому компилятор её запрещает (CS0453).",
            "Ковариантность безопасна при чтении: коллекцию собак можно читать как коллекцию животных. `IList<T>` содержит и `T this[int]`, и `void Add(T)`, поэтому параметр встречается на входе и на выходе и интерфейс инвариантен.",
            "Ничем во время исполнения; отличается статический контракт: `string` обещает отсутствие null, `string?` разрешает null и вызывает предупреждения при нарушении.",
            "Такая ветвь покрывает все значения `Age`, поэтому последующие ветви недостижимы и компилятор выдаёт ошибку CS8510.",
            "Сгенерированные `Equals` и `GetHashCode` сравнивают члены через `EqualityComparer<T>.Default`, а для массива это сравнение по ссылке.",
        ),
        heading("Итоги"),
        bullets(
            "Ограничения обобщений: `class`, `struct`, `new()`, `notnull`, `unmanaged`, `Enum`, `Delegate`, `default`; порядок строгий, `new()` всегда последним.",
            "Generic math опирается на ограничение-себя: `where T : INumber<T>`, которое позволяет арифметику без рефлексии.",
            "Вариантность: `out` для выходных позиций, `in` для входных, только у интерфейсов и делегатов; классы и структуры инвариантны.",
            "NRT — статические предупреждения: `?` разрешает null, `!` подавляет предупреждение без проверки, состояния анализа потока сбрасываются после вызовов.",
            "Паттерны: свойства, кортежи, реляционные, списочные с `..`, логические `and`, `or`, `not` и условие `when`; порядок ветвей задаёт приоритет.",
            "Записи дают равенство по значению, `ToString`, деконструкцию и `with`; `record struct` — значимый вариант, `readonly record struct` — неизменяемый.",
            "Ограничения механизмов: поверхностное копирование `with`, сравнение массивов по ссылке, наследование только от записей и возможность null из внешних данных.",
        ),
        heading("Что дальше"),
        text(
            "Система типов описывает, как данные устроены и что с ними допустимо. Следующий урок "
            "спускается на уровень ниже: как компилятор Roslyn превращает объявления в "
            "промежуточный язык, как JIT исполняет его и какую роль играют метаданные и атрибуты, "
            "которые вы уже использовали для анализа потока."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Справочник по обобщённым типам C# — learn.microsoft.com/dotnet/csharp/fundamentals/types/generics",
            "Ковариантность и контравариантность — learn.microsoft.com/dotnet/csharp/programming-guide/concepts/covariance-contravariance",
            "Ссылочные nullable-типы — learn.microsoft.com/dotnet/csharp/nullable-references",
            "Паттерны в C# — learn.microsoft.com/dotnet/csharp/language-reference/operators/patterns",
            "Записи в C# — learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/record",
            "Обобщённая математика — learn.microsoft.com/dotnet/standard/generics/math",
        ),
    ],
}
