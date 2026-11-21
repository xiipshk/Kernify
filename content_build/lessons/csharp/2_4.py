"""Урок 4 курса csharp: продвинутый LINQ."""

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
    "topic_order": 4,
    "name": "2.4. Продвинутый LINQ",
    "slug": "csharp-2-4-продвинутый-linq",
    "short_description": (
        "Два синтаксиса LINQ, отложенное выполнение, разница между IEnumerable и IQueryable, "
        "группировка, соединения, операции над множествами и агрегаты."
    ),
    "topic_name": "Продвинутый LINQ",
    "topic_description": (
        "Углублённый разбор LINQ: синтаксис запросов и цепочек методов, операторы let и into, "
        "deferred execution и streaming против buffering, отложенные последовательности в EF Core, "
        "GroupBy, Join, операции над множествами, Aggregate и практическая оптимизация запросов."
    ),
    "learning_objectives": [
        "Выбирать между query syntax и method syntax в зависимости от формы запроса",
        "Использовать операторы let и into для промежуточных вычислений и продолжения запроса",
        "Объяснять отложенное выполнение LINQ, различать streaming и buffering операторы",
        "Не допускать многократного перечисления и лишних обращений к дорогим операциям",
        "Различать IEnumerable и IQueryable и понимать, когда запрос уходит в SQL, а когда выполняется в памяти",
        "Строить группировки, соединения, операции над множествами и свёртку через GroupBy, Join, Union, Aggregate",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "csharp",
        "linq",
        "запросы",
        "отложенное-выполнение",
        "группировка",
        "производительность",
    ],
    "starter_code": code(
        """
        using System;
        using System.Linq;

        var employees = new[]
        {
            new { Name = "Анна", Department = "Разработка", Salary = 180_000 },
            new { Name = "Борис", Department = "Разработка", Salary = 150_000 },
            new { Name = "Вера", Department = "Аналитика", Salary = 160_000 },
            new { Name = "Глеб", Department = "Поддержка", Salary = 90_000 },
        };

        var report = employees
            .GroupBy(e => e.Department)
            .Select(g => new
            {
                Department = g.Key,
                Count = g.Count(),
                Average = g.Average(e => e.Salary)
            })
            .OrderByDescending(d => d.Average);

        foreach (var row in report)
            Console.WriteLine($"{row.Department}: {row.Count} чел., средняя {row.Average:F0}");
        """
    ),
    "hints": [
        "Операторы Where, Select, Take и Skip ленивы: они выполняются только при перечислении результата. Материализуйте результат через ToList или ToArray, если будете обращаться к нему несколько раз.",
        "Если запрос используется больше одного раза или лежит в поле класса, сохраните результат в List или массив: повторное перечисление заново выполняет весь конвейер.",
        "Для количества элементов используйте Any вместо Count() > 0: Any останавливается на первом найденном элементе, а Count проходит всю последовательность.",
        "Для IQueryable держите фильтрацию и проекцию на стороне базы: загружайте только нужные колонки через Select и только нужные строки через Where до вызова ToList.",
    ],
    "content": [
        text(
            "LINQ (Language Integrated Query) превращает работу с данными в конвейер из небольших "
            "операторов: отфильтровать, отсортировать, сгруппировать, свернуть в одно значение. "
            "Базовые Where, Select и OrderBy знакомы вам по уроку «Основы LINQ». Но именно за их "
            "пределами начинается настоящая работа: группировка, соединение нескольких источников, "
            "операции над множествами и управление моментом выполнения запроса.\n\n"
            "Продвинутый LINQ — это не столько набор методов, сколько понимание двух вещей. "
            "Первое: как устроен конвейер и когда именно он выполняется. Второе: где выполняется "
            "работа — в памяти процесса или на сервере базы данных. Большинство проблем с LINQ в "
            "рабочем коде сводятся к ошибке в одном из этих двух мест: повторный проход по ленивой "
            "последовательности или лишняя загрузка всей таблицы в память.\n\n"
            "В этом уроке вы увидите оба синтаксиса и их границы применимости, разберёте механизм "
            "отложенного выполнения на примерах с реальным выводом, научитесь строить сложные "
            "запросы через GroupBy, Join и Aggregate и избегать типичных ошибок производительности."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "выбирать между query syntax и method syntax в зависимости от формы запроса;",
            "использовать let и into для промежуточных вычислений и продолжения запроса;",
            "объяснять отложенное выполнение и различать streaming и buffering операторы;",
            "находить в коде многократное перечисление и устранять его материализацией;",
            "различать IEnumerable и IQueryable, понимать роль деревьев выражений;",
            "строить группировки по одному и составному ключу через GroupBy;",
            "соединять источники через Join, GroupJoin и Zip;",
            "применять Union, Intersect, Except и Aggregate вместо ручных циклов.",
        ),
        heading("Два синтаксиса и их границы"),
        text(
            "Любой запрос LINQ можно записать двумя способами. Method syntax — это цепочка методов "
            "расширения, где каждый шаг вызывает следующий: Where, Select, OrderBy. "
            "Query syntax — синтаксис понимания (comprehension syntax), который выглядит как SQL "
            "и начинается со слова from, а не select.\n\n"
            "Компилятор C# переводит query syntax в вызовы тех же методов расширения. Это значит, "
            "что оба варианта дают одинаковый результат и одинаковую производительность — выбирать "
            "нужно по читаемости, а не по скорости. Единственное исключение — методы, у которых нет "
            "синтаксического аналога: Skip, Take, Distinct, First, Sum и большинство агрегатов "
            "пишутся только как вызовы.\n\n"
            "Правило, которое хорошо работает на практике: query syntax удобен для join, group by, "
            "let и into, потому что там появляется вложенность и несколько диапазонов. Для коротких "
            "цепочек из двух-трёх операторов метод-синтаксис короче и читается слева направо."
        ),
        example(
            "csharp",
            """
            var numbers = new[] { 5, 2, 8, 1, 9, 3 };

            // Method syntax: цепочка методов
            var byMethod = numbers
                .Where(n => n > 3)
                .OrderBy(n => n)
                .Select(n => n * 2)
                .ToList();
            Console.WriteLine(string.Join(", ", byMethod));

            // Query syntax: компилятор превращает в те же вызовы
            var byQuery =
                from n in numbers
                where n > 3
                orderby n
                select n * 2;
            Console.WriteLine(string.Join(", ", byQuery));
            """,
        ),
        text("Вывод: 8, 10, 16, 18 (оба варианта дают одно и то же)"),
        table(
            ["Сценарий", "Рекомендуемый синтаксис", "Причина"],
            [
                ["Короткая цепочка Where / Select / OrderBy", "Method syntax", "Читается как поток данных"],
                ["Join двух и более источников", "Query syntax", "Видны все диапазоны и ключи"],
                ["Группировка с продолжением запроса", "Query syntax", "Опора group by и into"],
                ["Промежуточные значения через let", "Query syntax", "Нет аналога в методах"],
                ["Условные фильтры во время выполнения", "Method syntax", "Where добавляется по условию"],
                ["Skip, Take, Distinct, First, Sum", "Method syntax", "Нет синтаксической формы"],
            ],
        ),
        text(
            "Оператор let объявляет переменную внутри запроса и вычисляет её один раз для каждого "
            "элемента. Он удобен, когда значение используется и в фильтре, и в проекции: без let "
            "выражение пришлось бы повторить дважды. Оператор into заканчивает текущую часть запроса "
            "и открывает новую, переменная диапазона из которой продолжает жить под новым именем."
        ),
        example(
            "csharp",
            """
            var products = new[]
            {
                ("Ноутбук", 1200m, 3),
                ("Мышь", 25m, 40),
                ("Монитор", 350m, 7),
                ("Клавиатура", 80m, 15),
            };

            var expensive = from p in products
                            let total = p.Item2 * p.Item3
                            where total > 1000m
                            orderby total descending
                            select (p.Item1, total);

            foreach (var item in expensive)
                Console.WriteLine($"{item.Item1}: {item.total}");
            """,
        ),
        text("Вывод: Ноутбук: 3600; Монитор: 2450; Клавиатура: 1200"),
        example(
            "csharp",
            """
            var numbers = new[] { 1, 2, 3, 4, 5, 6, 7 };

            // into: продолжение после group by
            var grouped = from n in numbers
                          group n by n % 2 into g
                          where g.Count() > 2
                          select new { Key = g.Key, Count = g.Count(), Sum = g.Sum() };

            foreach (var g in grouped)
                Console.WriteLine($"Key={g.Key}, Count={g.Count}, Sum={g.Sum}");
            """,
        ),
        text("Вывод: Key=1, Count=4, Sum=16; Key=0, Count=3, Sum=12"),
        heading("Отложенное выполнение"),
        text(
            "Отложенное выполнение (deferred execution) — ключевая особенность LINQ. Запрос, "
            "построенный из Where, Select или OrderBy, ничего не вычисляет в момент своего создания. "
            "Он запоминает источник данных и набор операций, а работа начинается только при "
            "перечислении результата: в foreach, при вызове ToList, ToArray, Count, First, Sum или "
            "в методе, который принимает IEnumerable и обходит его.\n\n"
            "Из этого следуют два важных свойства. Первое: запрос всегда видит актуальное состояние "
            "источника. Если между созданием запроса и перечислением в список добавили элемент, "
            "он попадёт в результат. Второе: каждое перечисление — это новый полный проход по "
            "конвейеру. Никакого кэша между проходами нет.\n\n"
            "По характеру работы операторы делятся на два класса. Streaming-операторы отдают "
            "элементы по одному, как только они готовы, и не хранят всю последовательность. "
            "Buffering-операторы обязаны прочитать весь источник, прежде чем выдать первый элемент, "
            "потому что им нужен полный порядок: сортировка, группировка, Distinct."
        ),
        example(
            "csharp",
            """
            static int Double(int n)
            {
                Console.WriteLine($"  вычисление для {n}");
                return n * 2;
            }

            var numbers = new[] { 1, 2, 3 };
            var query = numbers.Where(n => n > 1).Select(Double);

            Console.WriteLine("до перечисления");
            foreach (var n in query)
                Console.WriteLine($"результат: {n}");
            Console.WriteLine("после перечисления");
            """,
        ),
        text(
            "Вывод: строка «до перечисления» появляется раньше строк «вычисление для 2» и "
            "«вычисление для 3». Значит вызовы начались не при создании запроса, а внутри foreach."
        ),
        table(
            ["Оператор", "Класс", "Что делает"],
            [
                ["Where, Select, Take, Skip", "Streaming", "Передаёт элементы по одному"],
                ["SelectMany, Concat, Zip", "Streaming", "Обходит источники последовательно"],
                ["OrderBy, ThenBy", "Buffering", "Собирает все элементы и сортирует"],
                ["GroupBy, ToLookup", "Buffering", "Строит группы из всего источника"],
                ["Distinct, Union, Except", "Buffering", "Ведёт множество уникальных значений"],
                ["Reverse", "Buffering", "Нужен полный список для обратного порядка"],
                ["ToList, ToArray, Count, Sum", "Материализация", "Немедленно запускает конвейер"],
            ],
        ),
        callout(
            "info",
            "Почему List не годится для бесконечных источников",
            "Streaming-операторы способны работать с бесконечной последовательностью в паре с Take. "
            "Buffering-операторы, такие как OrderBy или Reverse, на бесконечном источнике не "
            "завершатся никогда: им нужно прочитать всё."
        ),
        heading("Многократное перечисление"),
        text(
            "Самая частая ошибка с отложенным выполнением — перечисление одного и того же запроса "
            "несколько раз. Для массива из шести чисел это незаметно, но если в конвейере есть "
            "обращение к базе данных, разбор файла или сетевой вызов, каждый проход повторит эту "
            "работу. Хуже того, результаты двух проходов могут отличаться, если источник меняется.\n\n"
            "Исправление простое: если запрос используется больше одного раза, материализуйте его "
            "явно. ToList создаёт независимую копию, которая перечисляется за константное время и "
            "не повторяет вычисления. Отдельно помните, что Count() и First() сами по себе "
            "перечисляют последовательность, поэтому вызовы query.Count() и query.First() подряд — "
            "это два разных прохода."
        ),
        example(
            "csharp",
            """
            var numbers = new[] { 1, 2, 3, 4, 5 };
            int calls = 0;

            var query = numbers.Where(n => { calls++; return n > 1; });

            Console.WriteLine($"Count: {query.Count()}");
            Console.WriteLine($"First: {query.First()}");
            Console.WriteLine($"обращений к предикату: {calls}");

            var list = query.ToList();
            calls = 0;
            Console.WriteLine($"Count: {list.Count}");
            Console.WriteLine($"First: {list[0]}");
            Console.WriteLine($"обращений после материализации: {calls}");
            """,
        ),
        text(
            "Вывод: Count: 4, First: 2, обращений к предикату: 10, затем списковые операции "
            "не обращаются к предикату вовсе — 0."
        ),
        callout(
            "warning",
            "Запросы в полях классов",
            "Запрос, сохранённый в поле класса или возвращённый из свойства как IEnumerable, "
            "будет пересчитан при каждом обращении. Храните в поле материализованный результат, "
            "а ленивую форму возвращайте только из методов, которые вызывают один раз."
        ),
        heading("IEnumerable и IQueryable"),
        text(
            "До сих пор речь шла о LINQ to Objects — запросах над данными в памяти. Второй мир — "
            "LINQ to Entities: запросы к базе данных через EF Core. Разница задаётся типом "
            "интерфейса и природой лямбды.\n\n"
            "Методы над IEnumerable принимают делегат Func: скомпилированный код, который "
            "выполняется в памяти процесса. Методы над IQueryable принимают Expression, то есть "
            "Expression<Func<T, bool>> — дерево выражений, структуру, которую можно разобрать "
            "и перевести в SQL. Компилятор превращает лямбду в дерево, а не в готовый код, поэтому "
            "провайдер запросов видит форму выражения целиком.\n\n"
            "Отсюда главное следствие: IQueryable не выполняет Where сразу, а накапливает выражения "
            "и переводит их в SQL при материализации. OrderBy и Take уходят в SQL как ORDER BY и "
            "TOP, значит сервер сортирует и отдаёт только нужные строки. Если вызвать AsEnumerable "
            "или ToList раньше времени, всё, что стоит после, выполнится в памяти уже над "
            "загруженными данными."
        ),
        example(
            "csharp",
            """
            // IEnumerable: делегат, вычисления в памяти
            IEnumerable<int> source = new[] { 1, 2, 3 };
            Func<int, bool> predicate = n => n > 1;

            // IQueryable: дерево выражений, переводится провайдером
            IQueryable<int>? queryable = source.AsQueryable();
            Expression<Func<int, bool>> tree = n => n > 1;

            Console.WriteLine($"делегат: {predicate(3)}");
            Console.WriteLine($"дерево: {tree}");
            Console.WriteLine($"тип выражения: {tree.NodeType}");
            """,
        ),
        text(
            "Вывод: делегат: True; дерево: n => (n > 1); тип выражения: Lambda."
        ),
        example(
            "csharp",
            """
            // Правильно: Where в SQL, в память попадают только строки совпадений
            var adults = await db.Users
                .Where(u => u.Age > 18 && u.IsActive)
                .OrderBy(u => u.LastName)
                .Take(10)
                .ToListAsync();

            // Опасно: фильтр в памяти, из базы придут все строки
            var all = await db.Users.ToListAsync();
            var filtered = all.Where(u => u.Age > 18 && u.IsActive).ToList();
            """,
        ),
        callout(
            "warning",
            "Клиентское вычисление",
            "Если выражение нельзя перевести в SQL, например в нём вызван ваш собственный метод, "
            "EF Core выбросит исключение о невозможности перевода. Вычислите значение заранее в "
            "переменную, а внутри лямбды используйте только поддерживаемые провайдером операции."
        ),
        heading("Фильтрация, проекция и элементы"),
        text(
            "Операторы выборки элемента делятся на две группы по поведению при отсутствии значения. "
            "First, Last и Single выбрасывают исключение, если элемента нет; их варианты с суффиксом "
            "OrDefault возвращают значение по умолчанию. Для ссылочных типов это null, поэтому "
            "результат стоит проверять.\n\n"
            "Single проверяет, что совпадение ровно одно, и выбрасывает исключение, если их ноль "
            "или больше. Это полезная защита инварианта, но дорогая операция: Single в отличие от "
            "First не может остановиться на первом найденном. ElementAt работает по индексу, а "
            "ElementAtOrDefault безопасно возвращает default при выходе за границы.\n\n"
            "SelectMany разворачивает вложенные коллекции: вместо последовательности списков "
            "получается плоская последовательность их элементов. Это стандартный способ "
            "превратить один ко многим в плоскую выборку."
        ),
        example(
            "csharp",
            """
            string[] names = { "Анна", "Борис", "Вера" };

            Console.WriteLine(string.Join(", ", names.Select((n, i) => $"{i}: {n}")));
            Console.WriteLine($"первый с А: {names.First(n => n.StartsWith("А"))}");
            Console.WriteLine($"индекс 1: {names.ElementAt(1)}");
            Console.WriteLine($"индекс 10: {names.ElementAtOrDefault(10) ?? "нет"}");

            int[][] rows = { new[] { 1, 2 }, new[] { 3 }, new[] { 4, 5, 6 } };
            Console.WriteLine(string.Join(", ", rows.SelectMany(r => r)));
            """,
        ),
        text("Вывод: 0: Анна, 1: Борис, 2: Вера; первый с А: Анна; индекс 1: Борис; "
             "индекс 10: нет; 1, 2, 3, 4, 5, 6"),
        heading("Сортировка и группировка"),
        text(
            "OrderBy задаёт первичный ключ сортировки, ThenBy — вторичный. Ключевая тонкость: "
            "повторный вызов OrderBy сбрасывает предыдущую сортировку, поэтому для нескольких "
            "ключей нужен именно ThenBy. Методы OrderByDescending и ThenByDescending задают "
            "обратный порядок на своём уровне.\n\n"
            "GroupBy разбивает последовательность на группы по ключу и возвращает "
            "последовательность объектов IGrouping<TKey, TElement>. У каждой группы есть свойство "
            "Key и все методы IEnumerable, поэтому внутри можно вызвать Count, Sum, Average или "
            "взять максимум. Ключом служит любое значение, включая анонимный тип: так получается "
            "группировка по нескольким полям сразу.\n\n"
            "Важная деталь: GroupBy — buffering-оператор. Он обходит всю входную последовательность, "
            "прежде чем выдать первую группу. Если результат нужен несколько раз, используйте "
            "ToLookup — он строит структуру с быстрым доступом по ключу."
        ),
        example(
            "csharp",
            """
            var employees = new[]
            {
                new { Name = "Анна", Dept = "Dev", Role = "Dev", Salary = 180 },
                new { Name = "Борис", Dept = "Dev", Role = "QA", Salary = 120 },
                new { Name = "Вера", Dept = "Ops", Role = "Dev", Salary = 150 },
                new { Name = "Глеб", Dept = "Ops", Role = "QA", Salary = 100 },
            };

            // Сортировка по двум ключам
            var sorted = employees.OrderBy(e => e.Dept).ThenByDescending(e => e.Salary);
            foreach (var e in sorted)
                Console.WriteLine($"{e.Dept} {e.Name} {e.Salary}");

            // Группировка с агрегатами
            var stats = employees
                .GroupBy(e => e.Dept)
                .Select(g => new { Dept = g.Key, Count = g.Count(), Avg = g.Average(e => e.Salary) });
            foreach (var s in stats)
                Console.WriteLine($"{s.Dept}: {s.Count} чел., средняя {s.Avg:F0}");

            // Составной ключ
            foreach (var g in employees.GroupBy(e => new { e.Dept, e.Role }))
                Console.WriteLine($"{g.Key.Dept}/{g.Key.Role}: {g.Count()}");
            """,
        ),
        text(
            "Вывод: Dev Анна 180, Dev Борис 120, Ops Вера 150, Ops Глеб 100; затем Dev: 2 чел., "
            "средняя 150; Ops: 2 чел., средняя 125; затем Dev/Dev: 1, Dev/QA: 1, Ops/Dev: 1, "
            "Ops/QA: 1."
        ),
        example(
            "csharp",
            """
            var orders = new[]
            {
                new { Id = 1, Amount = 500m, Customer = "Анна" },
                new { Id = 2, Amount = 150m, Customer = "Борис" },
                new { Id = 3, Amount = 900m, Customer = "Анна" },
                new { Id = 4, Amount = 300m, Customer = "Вера" },
            };

            var top2 = orders
                .GroupBy(o => o.Customer)
                .SelectMany(g => g.OrderByDescending(o => o.Amount).Take(2))
                .Select(o => $"{o.Customer}: {o.Amount}");

            Console.WriteLine(string.Join("; ", top2));
            """,
        ),
        text("Вывод: Анна: 900; Анна: 500; Вера: 300; Борис: 150"),
        heading("Соединения: Join, GroupJoin и Zip"),
        text(
            "Join соединяет две последовательности по ключу и возвращает только пары, у которых "
            "ключи совпали, — это внутреннее соединение. В method syntax четыре аргумента: внутренний "
            "источник, селектор ключа внешнего элемента, селектор ключа внутреннего и функция, "
            "которая строит результат из пары.\n\n"
            "GroupJoin делает левое соединение: каждый элемент внешней последовательности "
            "сохраняется, а во второе поле попадает последовательность совпавших элементов. Если "
            "совпадений нет, эта последовательность пуста. Именно так в query syntax работает запрос "
            "с продолжением into.\n\n"
            "Zip объединяет две последовательности попарно по позиции и останавливается на более "
            "короткой. Его удобно использовать для сопоставления двух списков одинакового смысла: "
            "имён и значений, дат и показателей."
        ),
        example(
            "csharp",
            """
            var employees = new[]
            {
                new { Name = "Анна", DeptId = 1 },
                new { Name = "Борис", DeptId = 2 },
                new { Name = "Вера", DeptId = 9 },
            };

            var departments = new[]
            {
                new { Id = 1, Title = "Разработка" },
                new { Id = 2, Title = "Поддержка" },
            };

            // Inner join в query syntax
            var inner = from e in employees
                        join d in departments on e.DeptId equals d.Id
                        select $"{e.Name} → {d.Title}";
            Console.WriteLine(string.Join("; ", inner));

            // Левое соединение через join ... into
            var left = from d in departments
                       join e in employees on d.Id equals e.DeptId into staff
                       select $"{d.Title}: {staff.Count()}";
            Console.WriteLine(string.Join("; ", left));

            // Zip: попарно по позиции
            var a = new[] { 1, 2, 3, 4 };
            var b = new[] { 10, 20, 30 };
            Console.WriteLine(string.Join(", ", a.Zip(b, (x, y) => x + y)));
            """,
        ),
        text(
            "Вывод: Анна → Разработка; Борис → Поддержка; затем Разработка: 1; Поддержка: 1; "
            "затем 11, 22, 33. Вера не попала в inner join, потому что отдела с Id 9 нет."
        ),
        heading("Множества и агрегаты"),
        text(
            "Операции над множествами сравнивают элементы по значению и используют "
            "EqualityComparer по умолчанию, который у ссылочных типов опирается на Equals и "
            "GetHashCode. Если реализовать их неправильно, Union начнёт дублировать элементы. "
            "Разница между операциями в судьбе повторов и порядка: Concat сохраняет все элементы "
            "подряд, Union оставляет уникальные, Intersect берёт общие, Except — те, что есть в "
            "первом источнике и отсутствуют во втором. Для уникальности внутри одной "
            "последовательности служит Distinct, а для ключа другого типа — DistinctBy.\n\n"
            "Aggregate — свёртка произвольной формы: на вход начальное значение и функция, которая "
            "получает накопленное значение и очередной элемент. С его помощью выражаются произведения, "
            "склейка строк и построение сложных объектов за один проход. Для типовых случаев "
            "используйте готовые Sum, Min, Max, Count и Average: они короче и быстрее.\n\n"
            "Кванторы All, Any и Contains отвечают на вопрос о всей последовательности. Any без "
            "предиката проверяет, что последовательность не пуста, и останавливается на первом "
            "элементе — это предпочтительный способ проверки Count() > 0."
        ),
        example(
            "csharp",
            """
            var a = new[] { 1, 2, 3, 4 };
            var b = new[] { 3, 4, 5, 6 };

            Console.WriteLine($"Union: {string.Join(", ", a.Union(b))}");
            Console.WriteLine($"Intersect: {string.Join(", ", a.Intersect(b))}");
            Console.WriteLine($"Except: {string.Join(", ", a.Except(b))}");
            Console.WriteLine($"Concat: {string.Join(", ", a.Concat(b))}");
            Console.WriteLine($"Distinct: {string.Join(", ", new[] { 2, 1, 2, 3, 1 }.Distinct().Order())}");
            """,
        ),
        text(
            "Вывод: Union: 1, 2, 3, 4, 5, 6; Intersect: 3, 4; Except: 1, 2; "
            "Concat: 1, 2, 3, 4, 3, 4, 5, 6; Distinct: 1, 2, 3. Порядок Distinct не гарантирован "
            "стандартным контрактом, поэтому для стабильного вывода он дополнен Order()."
        ),
        example(
            "csharp",
            """
            var numbers = new[] { 1, 2, 3, 4 };

            Console.WriteLine($"Sum: {numbers.Sum()}");
            Console.WriteLine($"Product: {numbers.Aggregate(1, (acc, n) => acc * n)}");
            Console.WriteLine($"Все положительные: {numbers.All(n => n > 0)}");
            Console.WriteLine($"Есть больше 3: {numbers.Any(n => n > 3)}");
            Console.WriteLine($"Содержит 2: {numbers.Contains(2)}");

            var words = new[] { "LINQ", "удобен", "для", "запросов" };
            Console.WriteLine(words.Aggregate((left, right) => left + " " + right));
            """,
        ),
        text(
            "Вывод: Sum: 10; Product: 24; Все положительные: True; Есть больше 3: True; "
            "Содержит 2: True; LINQ удобен для запросов."
        ),
        heading("Генерация и дополнительные операторы"),
        text(
            "Enumerable.Range, Repeat и Empty создают последовательности без исходного источника. "
            "В паре с Take и Where они позволяют строить бесконечные ленивые последовательности: "
            "Range(0, int.MaxValue) сам по себе не занимает памяти, потому что элементы вычисляются "
            "по требованию.\n\n"
            "Современный .NET добавил операторы, которые раньше приходилось писать вручную: "
            "Chunk разбивает последовательность на партии заданного размера, DistinctBy, MaxBy и "
            "MinBy работают с ключом вместо элемента, TryGetNonEnumeratedCount позволяет узнать "
            "размер без перечисления, если источник его знает. Все они доступны начиная с "
            "платформы .NET 6."
        ),
        example(
            "csharp",
            """
            Console.WriteLine(string.Join(", ", Enumerable.Range(1, 5)));
            Console.WriteLine(string.Join(", ", Enumerable.Repeat("x", 3)));
            Console.WriteLine($"пустая: {Enumerable.Empty<int>().Count()}");

            var odds = Enumerable.Range(0, int.MaxValue).Where(n => n % 2 == 1).Take(4);
            Console.WriteLine(string.Join(", ", odds));

            var users = new[] { ("anna@mail.ru", 30), ("bob@mail.ru", 22), ("anna@mail.ru", 41) };
            Console.WriteLine(string.Join(", ", users.DistinctBy(u => u.Item1)));
            Console.WriteLine($"старший: {users.MaxBy(u => u.Item2)}");
            """,
        ),
        text(
            "Вывод: 1, 2, 3, 4, 5; x, x, x; пустая: 0; 1, 3, 5, 7; (anna@mail.ru, 30), "
            "(bob@mail.ru, 22); старший: (anna@mail.ru, 41)."
        ),
        example(
            "csharp",
            """
            var items = Enumerable.Range(1, 10);
            foreach (var chunk in items.Chunk(4))
                Console.WriteLine($"[{string.Join(", ", chunk)}]");
            """,
        ),
        text("Вывод: [1, 2, 3, 4]; [5, 6, 7, 8]; [9, 10]"),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["query.Count() > 0", "Полный проход по всей последовательности", "query.Any()"],
                ["Where(...).First() вместо First(predicate)", "Лишний шаг конвейера и лишняя обёртка", "First(predicate)"],
                ["Повторное перечисление в цикле", "Конвейер выполняется заново на каждой итерации", "Материализовать через ToList один раз"],
                ["OrderBy дважды для двух ключей", "Вторая сортировка отменяет первую", "OrderBy(...).ThenBy(...)"],
                ["ToList до Where на IQueryable", "Из базы загружаются все строки", "Where и Select до материализации"],
                ["Concat вместо Union", "В результате остаются повторы", "Union для уникальных значений"],
                ["GroupBy без ToLookup при нескольких обращениях", "Группы строятся заново каждый раз", "ToLookup для многократного доступа"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания рассчитаны на консольное приложение .NET 8. Создайте проект командой "
            "`dotnet new console -n LinqPractice` и запускайте через `dotnet run`."
        ),
        numbered(
            "Отложенное выполнение: напишите запрос Where над массивом, который увеличивает счётчик "
            "вызовов предиката, и покажите, что до перечисления счётчик равен нулю, а Count() и "
            "ToList() дают разные значения счётчика.",
            "Группировка: для списка сотрудников постройте отчёт по отделам с количеством, средней и "
            "максимальной зарплатой, отсортированный по средней зарплате по убыванию.",
            "Соединение: есть массивы сотрудников и отделов. Напишите inner join и левое соединение "
            "через join ... into и покажите сотрудников без отдела.",
            "Свёртка: через Aggregate постройте словарь частот слов входной строки за один проход, "
            "не используя GroupBy.",
            "Партии: реализуйте обработку большого диапазона через Chunk(100) и посчитайте сумму "
            "каждой партии.",
        ),
        text("Пример ожидаемого результата для второго задания:"),
        example(
            "text",
            """
            Dev: 2 чел., средняя 165, максимум 180
            Ops: 2 чел., средняя 125, максимум 150
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 4",
            "Начальным значением Aggregate возьмите пустой Dictionary<string, int>. В лямбде "
            "увеличивайте счётчик для очередного слова и возвращайте тот же словарь: "
            "acc.TryGetValue(word, out var n); acc[word] = n + 1; return acc;"
        ),
        heading("Проверьте себя"),
        numbered(
            "В чём разница между query syntax и method syntax на уровне компиляции?",
            "Что означает отложенное выполнение и когда LINQ-запрос начинает работать?",
            "Чем streaming-операторы отличаются от buffering-операторов и что произойдёт, если "
            "применить OrderBy к бесконечной последовательности?",
            "Почему query.Count() и query.First() подряд — это два разных прохода по данным?",
            "В чём ключевое различие между IEnumerable и IQueryable при работе с EF Core?",
        ),
        heading("Ответы", 3),
        numbered(
            "Разницы нет: query syntax компилятор переводит в те же методы расширения Where, Select "
            "и другие. Выбор диктуется читаемостью, а не производительностью.",
            "Запрос только запоминает источник и операции. Выполнение начинается при перечислении — "
            "в foreach или при вызове материализующего метода вроде ToList, Count, First.",
            "Streaming отдаёт элементы по одному, buffering сначала читает весь источник. OrderBy "
            "на бесконечной последовательности не завершится никогда, потому что сортировать можно "
            "только полный набор.",
            "Каждый материализующий вызов перечисляет источник заново, и между проходами нет кэша. "
            "Материализация через ToList делает последующие операции операциями над списком.",
            "IEnumerable принимает делегат и выполняет работу в памяти. IQueryable принимает "
            "дерево выражений, которое провайдер переводит в SQL и выполняет на сервере базы.",
        ),
        heading("Итоги"),
        bullets(
            "Query syntax и method syntax дают одинаковый код после компиляции; let и into доступны "
            "только в форме запроса.",
            "Отложенное выполнение: запрос работает при перечислении, а не в момент создания, и "
            "видит актуальное состояние источника.",
            "Streaming-операторы работают с элементами по одному, buffering-операторы требуют полного "
            "источника; материализация запускает конвейер немедленно.",
            "Многократное перечисление повторяет все вычисления; лечится однократным ToList или ToArray.",
            "IQueryable и деревья выражений позволяют выполнять фильтрацию, сортировку и проекцию "
            "на стороне базы данных.",
            "GroupBy строит группы с ключом и даёт доступ ко всем агрегатам; для повторного доступа "
            "используйте ToLookup.",
            "Join даёт внутреннее соединение, GroupJoin и join ... into — левое, Zip объединяет по позиции.",
            "Union, Intersect, Except и Distinct строятся на равенстве элементов; Aggregate выражает "
            "произвольную свёртку за один проход.",
        ),
        heading("Что дальше"),
        text(
            "В следующем уроке «Коллекции и алгоритмы» вы свяжете LINQ с устройством структур данных: "
            "узнаете, какую цену платит каждый оператор, как выбрать между List, HashSet и Dictionary "
            "и как ленивые последовательности на yield return соотносятся с запросами. Понимание "
            "сложности операций превратит LINQ из удобного инструмента в инструмент предсказуемый."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Microsoft Learn: Общие сведения о LINQ — learn.microsoft.com/dotnet/csharp/linq/",
            "Microsoft Learn: Enumerable и стандартные операторы запросов — "
            "learn.microsoft.com/dotnet/api/system.linq.enumerable",
            "Microsoft Learn: Деревья выражений — "
            "learn.microsoft.com/dotnet/csharp/expression-trees",
            "Microsoft Learn: IQueryable — learn.microsoft.com/dotnet/api/system.linq.iqueryable",
            "Книга Джона Скита «C# in Depth», глава о LINQ to Objects и отложенном выполнении",
            "Библиотека MoreLINQ с дополнительными операторами — github.com/morelinq/MoreLINQ",
        ),
    ],
}
