"""Урок 5 курса csharp: коллекции и алгоритмы."""

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
    "topic_order": 5,
    "name": "2.5. Коллекции и алгоритмы",
    "slug": "csharp-2-5-коллекции-и-алгоритмы",
    "short_description": (
        "Иерархия интерфейсов коллекций, устройство List, Dictionary и HashSet, сравнение "
        "и сортировка, ленивые итераторы на yield, выбор подходящей структуры данных."
    ),
    "topic_name": "Коллекции и алгоритмы",
    "topic_description": (
        "Практическое руководство по коллекциям .NET: как устроены List<T>, Dictionary<TKey, TValue> "
        "и HashSet<T>, чем отличаются списки, множества, очереди и словари, как работают сравнение, "
        "сортировка и бинарный поиск, и как писать собственные ленивые последовательности на yield return."
    ),
    "learning_objectives": [
        "Ориентироваться в иерархии интерфейсов коллекций и выбирать тип параметра и возвращаемого значения",
        "Понимать внутреннее устройство List<T>, Dictionary<TKey, TValue>, HashSet<T> и оценивать стоимость операций",
        "Применять Queue<T>, Stack<T>, LinkedList<T> и PriorityQueue<TElement, TPriority> по назначению",
        "Реализовывать IComparable<T>, IComparer<T>, IEquatable<T> и согласовывать Equals с GetHashCode",
        "Сортировать и искать данные: Sort, OrderBy, BinarySearch и операции над множествами",
        "Писать ленивые последовательности на yield return и yield break, не материализуя данные без нужды",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "csharp",
        "коллекции",
        "структуры данных",
        "сортировка",
        "сравнение",
        "итераторы",
    ],
    "starter_code": code(
        """
        using System;
        using System.Collections.Generic;

        var inventory = new Dictionary<string, int>
        {
            ["яблоко"] = 12,
            ["груша"] = 7,
            ["слива"] = 25
        };

        inventory["банан"] = 3;
        inventory["яблоко"] += 5;

        foreach (var (name, count) in inventory)
        {
            Console.WriteLine($"{name}: {count}");
        }

        Console.WriteLine($"Всего видов: {inventory.Count}");
        """
    ),
    "hints": [
        "Для входа метода принимайте `IEnumerable<T>`, для выхода возвращайте `IReadOnlyList<T>` или `IReadOnlyCollection<T>`, если вызывающему нужен `Count`.",
        "`List<T>.BinarySearch` и `List<T>.Sort` работают корректно только на отсортированном списке с тем же компаратором, по которому сортировали.",
        "Переопределяя `Equals`, всегда переопределяйте `GetHashCode` и используйте одинаковые поля — иначе `Dictionary` и `HashSet` перестанут находить элементы.",
        "Тело метода с `yield return` не выполняется при вызове: оно стартует при первом `MoveNext`, то есть в `foreach` или `ToList()`.",
    ],
    "content": [
        text(
            "Коллекции — типы, которые хранят несколько значений и выполняют операции над ними: "
            "добавление, удаление, поиск, перебор. В C# они построены вокруг общей иерархии интерфейсов, "
            "поэтому взаимозаменяемы на уровне сигнатур методов. Внутри же список, словарь и множество "
            "устроены по-разному, и правильный выбор структуры данных влияет на программу сильнее, "
            "чем любая оптимизация кода.\n\n"
            "Вторая часть урока посвящена алгоритмам поверх коллекций: сравнение, сортировка, "
            "поиск и ленивые последовательности. Поиск в `List<T>` за O(n) заменяется проверкой "
            "в `HashSet<T>` за O(1) сменой типа объявления. Примеры рассчитаны на .NET 6 и новее."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "ориентироваться в иерархии интерфейсов `IEnumerable<T>`, `ICollection<T>`, `IList<T>`, `ISet<T>`, `IDictionary<TKey, TValue>`;",
            "понимать внутреннее устройство `List<T>`, `Dictionary<TKey, TValue>`, `HashSet<T>` и оценивать сложность операций;",
            "применять `Queue<T>`, `Stack<T>`, `LinkedList<T>` и `PriorityQueue<TElement, TPriority>` по назначению;",
            "реализовывать `IComparable<T>`, `IComparer<T>`, `IEquatable<T>` и согласовывать `Equals` с `GetHashCode`;",
            "сортировать и искать данные: `Sort`, `OrderBy`, `BinarySearch` и операции над множествами;",
            "писать ленивые последовательности на `yield return` и `yield break` без лишней материализации.",
        ),
        heading("Иерархия интерфейсов коллекций"),
        text(
            "Интерфейс — это контракт: набор членов, которые тип обязуется реализовать. На вершине иерархии "
            "коллекций стоит `IEnumerable<T>` — «последовательность, которую можно перебрать». Он объявляет "
            "единственный метод `GetEnumerator()`, возвращающий `IEnumerator<T>` с методами `MoveNext()`, "
            "свойством `Current` и `Dispose()`. Оператор `foreach` компилируется именно в вызовы этих членов.\n\n"
            "Ниже идут более «богатые» контракты. `ICollection<T>` добавляет `Count`, `Add`, `Remove`, "
            "`Clear`, `Contains`. `IList<T>` — ещё и доступ по индексу, `Insert` и `RemoveAt`. "
            "`ISet<T>` описывает множество уникальных элементов, `IDictionary<TKey, TValue>` — "
            "хранилище «ключ-значение». Параллельно существует семейство только для чтения: "
            "`IReadOnlyCollection<T>`, `IReadOnlyList<T>`, `IReadOnlySet<T>`. Ветка `IReadOnly*` "
            "не содержит методов изменения, поэтому объект можно отдать наружу без риска: "
            "`List<T>` приводится к `IReadOnlyList<T>` без копирования."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;

            class UserRepository
            {
                private readonly List<string> _users = new() { "Анна", "Борис" };

                // Наружу отдаём только чтение: изменить список снаружи нельзя
                public IReadOnlyList<string> GetUsers() => _users;

                // На входе достаточно последовательности: подойдёт массив, List, результат LINQ
                public void AddRange(IEnumerable<string> names)
                {
                    foreach (var name in names)
                    {
                        _users.Add(name);
                    }
                }
            }

            var repo = new UserRepository();
            repo.AddRange(new[] { "Вера" });

            IReadOnlyList<string> users = repo.GetUsers();
            Console.WriteLine(users.Count);          // 3
            Console.WriteLine(users[users.Count - 1]); // Вера
            """,
        ),
        text("Вывод: 3\nВера"),
        text(
            "Правило простое: входной параметр — максимально общий интерфейс (`IEnumerable<T>` или "
            "`IReadOnlyCollection<T>`, если нужен `Count`), возвращаемое значение — наиболее "
            "ограничивающий контракт, закрывающий потребности вызывающего. Конкретный класс "
            "фигурирует только там, где коллекция создаётся."
        ),
        table(
            ["Интерфейс", "Что добавляет", "Когда использовать"],
            [
                ["`IEnumerable<T>`", "Только перебор через `foreach`", "Входные параметры методов"],
                ["`IReadOnlyCollection<T>`", "`Count` без изменения", "Возврат, когда нужен размер"],
                ["`IReadOnlyList<T>`", "Индексатор и `Count`", "Возврат списков только для чтения"],
                ["`ICollection<T>`", "`Add`, `Remove`, `Clear`, `Contains`", "Когда нужно менять содержимое"],
                ["`IList<T>`", "Индексатор, `Insert`, `RemoveAt`, `IndexOf`", "Позиционное изменение списка"],
                ["`ISet<T>`", "Уникальность и операции множеств", "Проверка вхождения, дедупликация"],
                ["`IDictionary<TKey, TValue>`", "Доступ по ключу", "Быстрый поиск по ключу"],
            ],
        ),
        heading("List<T>: динамический массив"),
        text(
            "`List<T>` — самый распространённый класс коллекций. Внутри он хранит массив `T[]`, "
            "счётчик занятых элементов и номер версии, растущий при каждом изменении. "
            "`Count` — число элементов, `Capacity` — длина массива.\n\n"
            "Когда при `Add` массив заполнен, создаётся новый примерно вдвое большего размера, "
            "и элементы копируются. Копирования происходят всё реже, поэтому добавление в конец "
            "в среднем обходится O(1) — амортизированная оценка. Если размер известен заранее, "
            "передайте его в конструктор: `new List<int>(10_000)`.\n\n"
            "Доступ по индексу — O(1), вставка и удаление в середине — O(n) из-за сдвига. "
            "`TrimExcess()` подрезает `Capacity` до `Count`. Если коллекция изменилась во время "
            "`foreach`, итератор выбросит `InvalidOperationException` из-за смены версии."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;

            var numbers = new List<int>(capacity: 4);
            Console.WriteLine($"Capacity={numbers.Capacity}, Count={numbers.Count}");

            numbers.AddRange(new[] { 3, 1, 4 });
            numbers.Insert(0, 10);        // O(n) — сдвиг всех элементов
            numbers.RemoveAt(0);          // O(n) — обратный сдвиг

            Console.WriteLine($"Count={numbers.Count}, первый={numbers[0]}");
            Console.WriteLine($"Содержит 4: {numbers.Contains(4)}");

            numbers.TrimExcess();
            Console.WriteLine($"Capacity после TrimExcess={numbers.Capacity}");
            """,
        ),
        text("Вывод: Capacity=4, Count=0\nCount=3, первый=3\nСодержит 4: True\nCapacity после TrimExcess=3"),
        callout(
            "info",
            "Амортизированная сложность",
            "Амортизированное O(1) означает, что суммарная стоимость n вызовов Add пропорциональна n, "
            "хотя отдельные вызовы занимают O(n) из-за копирования массива.",
        ),
        heading("Dictionary<TKey, TValue>: хеш-таблица"),
        text(
            "Словарь хранит пары «ключ-значение» и находит значение по ключу в среднем за O(1). "
            "Внутри он содержит массив корзин `buckets` и массив записей `entries`. Каждая запись хранит "
            "хеш ключа, индекс следующей записи в цепочке, сам ключ и значение. Корзина хранит номер "
            "первой записи с подходящим остатком от деления хеша на размер таблицы.\n\n"
            "Коллизии — разные ключи в одной корзине — разрешаются цепочками: записи связываются "
            "через поле «следующий индекс». При поиске .NET вычисляет хеш, находит корзину и "
            "перебирает цепочку, сравнивая ключи через `Equals`.\n\n"
            "Индексатор `dict[key]` при чтении отсутствующего ключа выбрасывает "
            "`KeyNotFoundException`. Метод `TryGetValue` возвращает `bool` и через `out`-параметр "
            "отдаёт значение — это предпочтительный вариант без исключений. Есть и "
            "`GetValueOrDefault`, и `TryAdd`, возвращающий `false`, если ключ уже есть."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;

            var visits = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            visits["Home"] = 120;
            visits["About"] += 0;      // для int отсутствующий ключ даёт 0

            visits["Home"] += 5;

            if (visits.TryGetValue("about", out int about))
            {
                Console.WriteLine($"About: {about}");
            }

            Console.WriteLine($"Home: {visits["home"]}");
            Console.WriteLine($"Missing: {visits.GetValueOrDefault("Blog", -1)}");
            Console.WriteLine($"TryAdd существующего: {visits.TryAdd("HOME", 0)}");
            Console.WriteLine($"Ключей: {visits.Count}");
            """,
        ),
        text("Вывод: About: 0\nHome: 125\nMissing: -1\nTryAdd существующего: False\nКлючей: 2"),
        text(
            "Ключи словаря должны быть неизменяемыми по полям, участвующим в хеше. Если после "
            "добавления изменить свойство ключа, хеш изменится, запись останется в старой корзине, "
            "и найти её не получится — элемент фактически потерян, хотя `Count` его учитывает. "
            "Поэтому ключами служат строки, числа, `Guid` и `record`. Конструктор принимает "
            "`IEqualityComparer<TKey>`: `StringComparer.OrdinalIgnoreCase` делает ключи "
            "регистронезависимыми, как в примере выше."
        ),
        heading("HashSet<T>: множество уникальных элементов"),
        text(
            "`HashSet<T>` устроен так же, как `Dictionary<TKey, TValue>` без значений: таблица хешей, "
            "цепочки коллизий и `Equals` для проверки. Добавление возвращает `bool`: `true`, если элемент "
            "действительно добавлен, и `false`, если такой уже был. Проверка `Contains` занимает O(1) "
            "в среднем — это главный сценарий использования множества.\n\n"
            "Методы `UnionWith`, `IntersectWith`, `ExceptWith` и `SymmetricExceptWith` изменяют "
            "текущее множество, а не создают новое; для неразрушающих операций есть LINQ-аналоги "
            "`Union`, `Intersect`, `Except`. `SortedSet<T>` построен на красно-чёрном дереве: "
            "операции за O(log n), элементы всегда отсортированы, а `GetViewBetween` даёт диапазон."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;
            using System.Linq;

            var a = new HashSet<int> { 1, 2, 3, 4 };
            var b = new HashSet<int> { 3, 4, 5 };

            Console.WriteLine($"Добавление 4: {a.Add(4)}");
            Console.WriteLine($"Contains 2: {a.Contains(2)}");

            var copy = new HashSet<int>(a);
            copy.IntersectWith(b);
            Console.WriteLine($"Пересечение: {string.Join(", ", copy)}");

            var diff = new HashSet<int>(a);
            diff.ExceptWith(b);
            Console.WriteLine($"Разность: {string.Join(", ", diff)}");

            Console.WriteLine($"Подмножество: {b.IsSubsetOf(a.Union(b))}");

            var sorted = new SortedSet<int> { 3, 1, 2 };
            Console.WriteLine($"SortedSet: {string.Join(", ", sorted)}");
            """,
        ),
        text(
            "Вывод: Добавление 4: False\nContains 2: True\nПересечение: 3, 4\n"
            "Разность: 1, 2\nПодмножество: True\nSortedSet: 1, 2, 3"
        ),
        callout(
            "warning",
            "Методы множества изменяют его",
            "`set.IntersectWith(other)` заменяет содержимое `set` пересечением. Код вроде "
            "`var c = set.IntersectWith(other)` не скомпилируется: метод возвращает `void`. "
            "Для «чистых» неразрушающих операций используйте LINQ: `set.Intersect(other)`.",
        ),
        heading("Очередь, стек, связный список и очередь с приоритетом"),
        text(
            "`Queue<T>` реализует дисциплину FIFO (first in, first out): внутри кольцевой буфер "
            "на массиве, поэтому `Enqueue` и `Dequeue` амортизированно O(1). Очереди применяют "
            "в обработке задач и обходе в ширину.\n\n"
            "`Stack<T>` реализует LIFO (last in, first out): последний добавленный извлекается первым. "
            "У обеих коллекций есть `Peek` без удаления и безопасные `TryDequeue`/`TryPop`. "
            "`LinkedList<T>` — двусвязный список из узлов: вставка и удаление по известному узлу "
            "занимают O(1), поиск — O(n). На практике `List<T>` почти всегда быстрее из-за "
            "последовательного расположения в памяти.\n\n"
            "`PriorityQueue<TElement, TPriority>` извлекает элемент с наименьшим приоритетом за O(log n) "
            "и построен на двоичной куче — стандартная структура для Дейкстры и A*."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;

            var queue = new Queue<string>();
            queue.Enqueue("первый");
            queue.Enqueue("второй");
            Console.WriteLine(queue.Dequeue());  // первый
            Console.WriteLine(queue.Peek());     // второй

            var stack = new Stack<int>();
            stack.Push(1);
            stack.Push(2);
            Console.WriteLine(stack.Pop());      // 2
            Console.WriteLine(stack.Peek());     // 1

            var linked = new LinkedList<int>();
            var node = linked.AddLast(1);
            linked.AddAfter(node, 2);
            linked.AddBefore(node, 0);
            linked.Remove(node);
            Console.WriteLine(string.Join(", ", linked));  // 0, 2

            var pq = new PriorityQueue<string, int>();
            pq.Enqueue("срочно", 1);
            pq.Enqueue("потом", 5);
            pq.Enqueue("средне", 3);
            Console.WriteLine(pq.Dequeue());     // срочно
            Console.WriteLine(pq.Count);         // 2
            """,
        ),
        text("Вывод: первый\nвторой\n2\n1\n0, 2\nсрочно\n2"),
        heading("Сравнение и сортировка"),
        text(
            "Сортировке нужно знать, как упорядочивать элементы, и в .NET есть два механизма сравнения. "
            "`IComparable<T>` задаёт естественный порядок типа: `CompareTo(other)` возвращает "
            "отрицательное число, ноль или положительное. `IComparer<T>` — внешняя стратегия "
            "с `Compare(x, y)` для альтернативных порядков. Если тип не реализует ни один интерфейс, "
            "а компаратор не передан, `Sort` выбросит `InvalidOperationException`.\n\n"
            "Вместо класса компаратора удобно передать лямбду: `List<T>.Sort` принимает делегат "
            "`Comparison<T>`, а `OrderBy` — селектор ключа. `OrderBy` возвращает ленивую "
            "последовательность и не меняет исходную коллекцию, `Sort` сортирует на месте."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;
            using System.Linq;

            public record Employee(string Name, int Salary);

            var employees = new List<Employee>
            {
                new("Анна", 120),
                new("Борис", 90),
                new("Вера", 120),
                new("Глеб", 75)
            };

            // OrderBy — ленивая сортировка, исходный список не меняется
            var bySalary = employees
                .OrderBy(e => e.Salary)
                .ThenBy(e => e.Name)
                .ToList();

            foreach (var e in bySalary)
                Console.WriteLine($"{e.Name}: {e.Salary}");

            // Sort на месте с делегатом Comparison<T>
            var copy = new List<Employee>(employees);
            copy.Sort((a, b) => string.Compare(a.Name, b.Name, StringComparison.Ordinal));
            Console.WriteLine($"Первый по алфавиту: {copy[0].Name}");
            """,
        ),
        text("Вывод: Глеб: 75\nБорис: 90\nАнна: 120\nВера: 120\nПервый по алфавиту: Анна"),
        text(
            "Если тип должен сортироваться сам по себе, реализуйте `IComparable<T>`. Метод "
            "принимает `T?`, и сравнение с `null` по соглашению считает существующий объект большим. "
            "Для альтернативных порядков создавайте `IComparer<T>` и передавайте его явно."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;

            public sealed class Version2 : IComparable<Version2>
            {
                public int Major { get; }
                public int Minor { get; }

                public Version2(int major, int minor)
                {
                    Major = major;
                    Minor = minor;
                }

                public int CompareTo(Version2? other)
                {
                    if (other is null) return 1;
                    int cmp = Major.CompareTo(other.Major);
                    return cmp != 0 ? cmp : Minor.CompareTo(other.Minor);
                }

                public override string ToString() => $"{Major}.{Minor}";
            }

            var versions = new List<Version2>
            {
                new(1, 10), new(1, 2), new(2, 0), new(1, 2)
            };
            versions.Sort();
            Console.WriteLine(string.Join(" ", versions));

            // Обратный порядок через готовый Comparer<T>.Create
            versions.Sort((a, b) => b.CompareTo(a));
            Console.WriteLine(string.Join(" ", versions));
            """,
        ),
        text("Вывод: 1.2 1.2 1.10 2.0\n2.0 1.10 1.2 1.2"),
        heading("Равенство и хеш-код"),
        text(
            "Для `Dictionary` и `HashSet` недостаточно порядка, нужны равенство и хеш. "
            "`Equals` отвечает на вопрос «совпадают ли элементы», а `GetHashCode` даёт число, "
            "по которому коллекция выбирает корзину. Между ними есть обязательное соглашение: "
            "если два объекта равны по `Equals`, их `GetHashCode` обязан совпадать. Обратное неверно: "
            "разные объекты могут иметь одинаковый хеш, и это нормально — коллекция разрешит коллизию "
            "через `Equals`.\n\n"
            "Если переопределить только `Equals`, равные элементы попадут в разные корзины, "
            "и `HashSet` перестанет их находить. `IEquatable<T>` задаёт типизированный `Equals` "
            "без упаковки значимых типов. Классы `record` генерируют согласованные `Equals` и "
            "`GetHashCode` автоматически, поэтому служат хорошими ключами словаря."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;

            public sealed class CustomerKey : IEquatable<CustomerKey>
            {
                public int Id { get; }
                public CustomerKey(int id) => Id = id;

                public bool Equals(CustomerKey? other) => other is not null && Id == other.Id;
                public override bool Equals(object? obj) => Equals(obj as CustomerKey);
                public override int GetHashCode() => Id.GetHashCode();
            }

            var seen = new HashSet<CustomerKey> { new(1), new(2), new(1) };
            Console.WriteLine($"Уникальных: {seen.Count}");        // 2
            Console.WriteLine($"Содержит id=2: {seen.Contains(new(2))}"); // True
            """,
        ),
        text("Вывод: Уникальных: 2\nСодержит id=2: True"),
        heading("Поиск, конвертация и операции над последовательностями"),
        text(
            "`List<T>.BinarySearch` возвращает индекс найденного элемента, а при отсутствии — "
            "побитовое дополнение позиции вставки. Условие `index < 0` означает «не найдено», "
            "`~index` даёт точку вставки. Список должен быть отсортирован тем же компаратором.\n\n"
            "Данные преобразуют методами `ToArray`, `ToList`, `ToHashSet`, `ToDictionary`, "
            "`ToLookup`. `ToDictionary` требует уникальных ключей, `ToLookup` хранит несколько "
            "значений на ключ, `Chunk` делит последовательность на группы."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;
            using System.Linq;

            var sorted = new List<int> { 1, 3, 5, 7, 9, 11 };

            int found = sorted.BinarySearch(7);
            int missing = sorted.BinarySearch(8);
            Console.WriteLine($"7 найден по индексу {found}");
            Console.WriteLine($"8 отсутствует, вставить в позицию {~missing}");

            var words = new[] { "apple", "banana", "avocado", "blueberry", "apricot" };

            ILookup<char, string> byLetter = words.ToLookup(w => w[0]);
            Console.WriteLine($"На 'a': {string.Join(", ", byLetter['a'])}");

            var set = words.ToHashSet();
            Console.WriteLine($"Уникальных слов: {set.Count}");

            var dict = sorted.ToDictionary(x => x, x => x * x);
            Console.WriteLine($"Квадрат 9: {dict[9]}");

            foreach (var chunk in Enumerable.Range(1, 7).Chunk(3))
                Console.WriteLine(string.Join(" ", chunk));
            """,
        ),
        text(
            "Вывод: 7 найден по индексу 3\n8 отсутствует, вставить в позицию 4\n"
            "На 'a': apple, avocado, apricot\nУникальных слов: 5\nКвадрат 9: 81\n1 2 3\n4 5 6\n7"
        ),
        heading("Итераторы и yield return"),
        text(
            "Итератор — метод, который возвращает `IEnumerable<T>` и содержит `yield return`. "
            "При каждом `yield return` он отдаёт очередное значение и запоминает состояние: "
            "локальные переменные, позицию выполнения и текущее значение. Следующий `MoveNext` "
            "продолжает работу с места после `yield`.\n\n"
            "Компилятор генерирует класс-конечный автомат, реализующий `IEnumerable<T>` и "
            "`IEnumerator<T>`. Поэтому вызов метода возвращает объект, но тело не выполняется "
            "ни на строчку: работа стартует при первом `MoveNext`, то есть в `foreach` или в "
            "терминальном методе LINQ вроде `ToList`. Это называется ленивыми вычислениями "
            "(deferred execution).\n\n"
            "`yield break` досрочно завершает последовательность, как `return`. Блок `finally` "
            "итератора выполняется при `Dispose` — при выходе из `foreach`. Внутри `catch` "
            "использовать `yield` нельзя."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;

            static IEnumerable<int> Fibonacci()
            {
                int a = 0, b = 1;
                while (true)
                {
                    yield return a;
                    (a, b) = (b, a + b);
                }
            }

            static IEnumerable<int> TakeBelow(IEnumerable<int> source, int limit)
            {
                foreach (var n in source)
                {
                    if (n >= limit) yield break;   // досрочно заканчиваем
                    yield return n;
                }
            }

            Console.WriteLine("До перебора: ничего не вычислено");

            foreach (var n in TakeBelow(Fibonacci(), 100))
            {
                Console.Write(n + " ");
            }

            Console.WriteLine();
            """,
        ),
        text("Вывод: До перебора: ничего не вычислено\n0 1 1 2 3 5 8 13 21 34 55 89"),
        callout(
            "info",
            "Бесконечные последовательности безопасны",
            "`Fibonacci()` возвращает бесконечную последовательность, но память не растёт: "
            "выполняется только генерация следующего элемента. Ограничивающие методы вроде `Take`, "
            "`TakeWhile` или собственный `yield break` делают перебор конечным.",
        ),
        text(
            "У ленивых последовательностей есть подвох: каждый перебор запускает вычисления заново, "
            "а отложенный запрос видит данные на момент перебора. Материализуйте результат через "
            "`ToList()`, если нужен многократный доступ. Метод с `yield` не проверяет аргументы "
            "до первого перебора — для немедленной проверки `null` используйте обёртку без `yield`."
        ),
        heading("Выбор коллекции"),
        text(
            "Ни одна коллекция не быстрее всех сразу: выбор — компромисс между скоростью поиска, "
            "вставки, порядком перебора и памятью. Звёздочка означает амортизированную оценку "
            "или оценку при наличии ссылки на узел."
        ),
        table(
            ["Операция", "List<T>", "Dictionary", "HashSet", "SortedSet", "LinkedList"],
            [
                ["Доступ по индексу", "O(1)", "—", "—", "—", "O(n)"],
                ["Поиск по значению", "O(n)", "O(1)", "O(1)", "O(log n)", "O(n)"],
                ["Вставка в конец", "O(1)*", "—", "O(1)*", "O(log n)", "O(1)"],
                ["Вставка в середину", "O(n)", "—", "—", "O(log n)", "O(1)*"],
                ["Удаление", "O(n)", "O(1)", "O(1)", "O(log n)", "O(1)*"],
                ["Порядок перебора", "по индексу", "не определён", "не определён", "отсортирован", "по ссылкам"],
                ["Память на элемент", "низкая", "высокая", "высокая", "высокая", "очень высокая"],
            ],
        ),
        text(
            "Практические ориентиры: поиск по ключу и подсчёт частот — `Dictionary<TKey, TValue>`; "
            "проверка вхождения и дедупликация — `HashSet<T>`; упорядоченный перебор со вставками — "
            "`SortedSet<T>`; обработка в порядке поступления или в обратном — `Queue<T>` и `Stack<T>`; "
            "извлечение минимума — `PriorityQueue<TElement, TPriority>`. Для многопоточности "
            "используйте `System.Collections.Concurrent`, для неизменяемых данных — "
            "`System.Collections.Immutable`."
        ),
        callout(
            "success",
            "Правило большого пальца",
            "Если в коде есть вложенный цикл с проверкой `list.Contains(x)`, замена `list` на "
            "`HashSet<T>` превращает алгоритм из O(n·m) в O(n + m). Это одна из самых частых "
            "и самых выгодных оптимизаций в прикладном коде.",
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Изменение коллекции внутри `foreach`", "`InvalidOperationException` из-за смены `_version`", "Перебирайте `list.ToList()` или используйте индексы `for`"],
                ["Переопределён `Equals` без `GetHashCode`", "`Dictionary` и `HashSet` не находят равные элементы", "Переопределяйте оба метода или используйте `record`"],
                ["Изменяемый ключ словаря", "После изменения хеш не совпадает, запись теряется", "Ключи — только неизменяемые типы"],
                ["`Contains` внутри цикла по списку", "Алгоритм O(n·m) заметно замедляется", "Замените `List<T>` на `HashSet<T>` или `Dictionary`"],
                ["`BinarySearch` по неотсортированному списку", "Неверный индекс без исключения", "Сортируйте `Sort` с тем же компаратором перед поиском"],
                ["`yield`-метод с проверкой аргументов", "Исключение возникает не при вызове, а при переборе", "Проверяйте аргументы в методе-обёртке без `yield`"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняйте в консольном проекте .NET 6 или новее: `dotnet new console` в папке "
            "решения и `dotnet run` для запуска. Каждый пример проверяйте выводом в консоль."
        ),
        numbered(
            "Подсчёт частот: прочитайте массив слов и постройте `Dictionary<string, int>`, где ключ — слово, значение — количество вхождений. Выведите слова, встречающиеся больше одного раза.",
            "Кольцевой буфер: реализуйте класс `CircularBuffer<T>` фиксированной ёмкости, который перезаписывает самый старый элемент и реализует `IEnumerable<T>` через `yield return`.",
            "Сортировка и поиск: создайте список из 50 случайных чисел, отсортируйте его через `Sort`, найдите три заданных значения через `BinarySearch` и выведите результат с корректной обработкой отсутствующих элементов.",
            "Дедупликация: получите из массива с повторами уникальные значения без LINQ — только через `HashSet<T>`, сохранив исходный порядок.",
            "Очередь с приоритетом: смоделируйте обработку заявок в поддержку: заявки с более высоким приоритетом обрабатываются раньше, при равенстве приоритета соблюдается порядок поступления.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            "код: 3\nтест: 2\nПривет: 2\nуникальных слов: 4",
        ),
        callout(
            "success",
            "Подсказка к заданию 4",
            "`HashSet<T>.Add` возвращает `true` только при первом добавлении. Если перебирать исходный массив "
            "и добавлять в множество и в результат лишь при `Add == true`, порядок первого появления сохранится.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему `List<T>.Add` называют операцией с амортизированной сложностью O(1)?",
            "Чем `TryGetValue` отличается от индексатора словаря и почему его предпочитают при чтении?",
            "Почему `Equals` и `GetHashCode` нужно переопределять вместе?",
            "Что делает `yield return` и когда начинает выполняться тело метода-итератора?",
            "Почему `BinarySearch` нельзя применять к неотсортированному списку?",
        ),
        heading("Ответы", 3),
        numbered(
            "Внутренний массив удваивается лишь при заполнении, а стоимость копирований распределяется между всеми добавлениями, поэтому в среднем одно добавление стоит O(1).",
            "Индексатор при отсутствии ключа выбрасывает `KeyNotFoundException`, а `TryGetValue` возвращает `false` без исключения; это дешевле и позволяет обойтись без обработки исключений.",
            "Коллекции на хеш-таблице сначала ищут элемент по хешу, а затем сравнивают через `Equals`. Несогласованные методы дают равным объектам разные хеши, и элемент невозможно найти.",
            "`yield return` отдаёт очередной элемент и сохраняет состояние итератора. Тело метода начинает выполняться только при первом `MoveNext`, то есть при переборе, а не при вызове метода.",
            "Бинарный поиск отбрасывает половину диапазона, полагаясь на порядок. Если список не отсортирован, отброшенная половина может содержать искомое значение, и результат будет неверным.",
        ),
        heading("Итоги"),
        bullets(
            "Интерфейсы: принимайте `IEnumerable<T>`, возвращайте `IReadOnlyList<T>` или `IReadOnlyCollection<T>`, если нужен `Count`.",
            "`List<T>` — массив с запасом: доступ по индексу O(1), `Add` амортизированно O(1), вставка в середину O(n).",
            "`Dictionary<TKey, TValue>` и `HashSet<T>` дают O(1) в среднем благодаря хешам и разрешению коллизий цепочками.",
            "`Queue<T>` — FIFO, `Stack<T>` — LIFO, `LinkedList<T>` — O(1) по узлу, `PriorityQueue<TElement, TPriority>` — O(log n) извлечение минимума.",
            "Сравнение строится на трёх исходах: `IComparable<T>` задаёт естественный порядок, `IComparer<T>` и `Comparison<T>` — альтернативные.",
            "`Equals` и `GetHashCode` переопределяются только согласованно; `record` делает это автоматически.",
            "`yield return` создаёт ленивую последовательность, чьё тело выполняется по одному элементу при переборе; `yield break` завершает её досрочно.",
            "Выбирайте коллекцию под доминирующую операцию: поиск — множество или словарь, перебор по порядку — `List<T>` или `SortedSet<T>`.",
        ),
        heading("Что дальше"),
        text(
            "В следующем уроке речь пойдёт об асинхронности: `async` и `await`, `Task`, "
            "синхронизация контекста. Понимание итераторов пригодится и там: `IAsyncEnumerable<T>` "
            "устроен по тем же принципам, что и синхронные ленивые последовательности."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Документация Microsoft Learn: «Collections overview» — learn.microsoft.com/dotnet/standard/collections/",
            "Документация Microsoft Learn: «Choosing a collection class» — learn.microsoft.com/dotnet/standard/collections/selecting-a-collection-class",
            "Документация Microsoft Learn: «Iterators» — learn.microsoft.com/dotnet/csharp/iterators",
            "Документация Microsoft Learn: «Span<T> and Memory<T>» — learn.microsoft.com/dotnet/standard/memory-and-spans/",
            "Исходный код List<T> и Dictionary<TKey, TValue> — github.com/dotnet/runtime/tree/main/src/libraries/System.Private.CoreLib/src/System/Collections/Generic",
        ),
    ],
}
