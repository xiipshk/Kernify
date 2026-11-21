"""Урок 3.2 курса csharp: внутреннее устройство языка и рантайма."""

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
    "topic_order": 2,
    "name": "3.2. Внутреннее устройство языка и рантайма",
    "slug": "csharp-3-2-внутреннее-устройство-языка-и-рантайма",
    "short_description": (
        "Путь от исходного кода C# до машинного: синтаксическое дерево Roslyn, IL, метаданные и JIT. "
        "Атрибуты, рефлексия, деревья выражений, Reflection.Emit и генераторы исходного кода "
        "как инструменты, которые открывают рантайм для управления им."
    ),
    "topic_name": "Внутреннее устройство языка и рантайма",
    "topic_description": (
        "Глубокий разбор того, как из текста программы появляется исполняемый код в .NET: "
        "устройство конвейера компилятора Roslyn, чтение промежуточного языка IL и метаданных, "
        "создание собственных атрибутов и их чтение через рефлексию, деревья выражений для "
        "динамических запросов и Reflection.Emit, а также инкрементальные генераторы исходного "
        "кода, переносящие работу с рефлексии на этап компиляции."
    ),
    "learning_objectives": [
        "Прослеживать путь исходного кода от синтаксического дерева Roslyn через IL и метаданные до машинного кода, который создаёт JIT",
        "Читать простой IL-код метода, понимать стек вычислений, инструкции загрузки аргументов, ветвления и вызова методов",
        "Создавать собственные атрибуты с AttributeUsage, позиционными и именованными параметрами и безопасно читать их через рефлексию",
        "Вызывать члены через рефлексию, работать с обобщёнными типами и отличать late binding от прямых вызовов по стоимости",
        "Строить деревья выражений вручную, трансформировать их через ExpressionVisitor и применять для динамических запросов",
        "Писать инкрементальный генератор исходного кода на IIncrementalGenerator и понимать, как он переносит проверки с исполнения на компиляцию",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "csharp",
        "il",
        "рефлексия",
        "атрибуты",
        "деревья-выражений",
        "генераторы-кода",
    ],
    "starter_code": code(
        r"""
        using System;
        using System.Linq;

        public static class Program
        {
            public static void Main()
            {
                // Атрибуты — это объекты, созданные из метаданных по запросу.
                var attrs = typeof(Program).GetCustomAttributes(typeof(ObsoleteAttribute), false);
                Console.WriteLine($"Атрибутов найдено: {attrs.Length}");

                // Рефлексия видит поверхности типов: методы, свойства, интерфейсы.
                var methods = typeof(string).GetMethods()
                    .Where(m => m.Name == "ToUpperInvariant")
                    .ToArray();
                Console.WriteLine($"Перегрузок ToUpperInvariant: {methods.Length}");

                // Прямой вызов компилятор связывает заранее, рефлексия — во время выполнения.
                Console.WriteLine("Привет".ToUpperInvariant());
            }
        }
        """
    ),
    "hints": [
        "Рефлексия дорого стоит при каждом вызове: получите MethodInfo или PropertyInfo один раз и сохраните в статическое поле. Компилированный делегат или Expression.Lambda(...).Compile() снижают накладные расходы лате-биндинга на порядки.",
        "GetMethods() без BindingFlags возвращает только публичные члены и может показать не то, что вы ожидали: явно перечисляйте BindingFlags.Public, NonPublic, Instance и Static.",
        "Reflection.Emit и деревья выражений строят код, который не проверяется компилятором: ошибка в типе параметра выяснится только при Compile() или CreateDelegate() с исключением InvalidProgramException.",
        "Генератор исходного кода падает молча, если исключение вылетает из Initialize или из transform: оборачивайте работу в try и сообщайте об ошибках через ReportDiagnostic, не бросая исключение наружу.",
    ],
    "content": [
        text(
            "Программа на C# проходит долгий путь, прежде чем начнёт исполняться. Компилятор Roslyn "
            "не превращает текст в машинные команды напрямую: он разбирает исходники в синтаксические "
            "деревья, проверяет семантику, опускает язык до промежуточного представления IL и кладёт "
            "его вместе с метаданными в сборку. Только при запуске «точно в срок» JIT-компилятор "
            "переводит IL в команды конкретного процессора. Каждый из этих слоёв оставляет швы — "
            "места, которыми язык открыт для программы.\n\n"
            "По этим швам и работают те механизмы, которые отличают опытного разработчика .NET от "
            "пользователя готового API. Атрибуты позволяют прикрепить к типу или методу данные, "
            "которые переживут компиляцию. Рефлексия даёт доступ к этим данным и к самой структуре "
            "типов во время выполнения. Деревья выражений превращают лямбды в инспектируемые "
            "структуры, из которых можно собрать другой код. Генераторы исходного кода выполняют "
            "похожую работу, только на этапе компиляции, когда рефлексия ещё недоступна.\n\n"
            "Урок построен как спуск по конвейеру: от текста к дереву, от дерева к IL, от IL к "
            "метаданным, а затем обратно — к генерации кода, сначала рефлективно во время "
            "выполнения, потом статически во время компиляции. После него вы сможете читать IL "
            "настолько, чтобы отличать упаковку значения от ссылочного вызова, писать атрибуты, "
            "которые не ломаются в наследовании, и поставлять генераторы, которые делают рефлексию "
            "в вашем коде ненужной."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "прослеживать путь от исходного кода к синтаксическому дереву, затем к IL, метаданным и машинному коду;",
            "читать простой IL-код метода: стек вычислений, загрузку аргументов, вызовы, упаковку и ветвления;",
            "создавать собственные атрибуты с AttributeUsage, позиционными и именованными параметрами;",
            "безопасно читать атрибуты через рефлексию и объяснять, почему объект атрибута создаётся по требованию;",
            "вызывать методы и свойства через рефлексию, строить обобщённые типы и кэшировать членов для повторного использования;",
            "строить деревья выражений вручную, трансформировать их через ExpressionVisitor и применять в динамических запросах;",
            "объяснять, почему деревья выражений обязательны для LINQ to SQL и EF Core, а делегаты для них недостаточны;",
            "писать инкрементальный генератор исходного кода и заменять им горячий путь рефлексии;",
            "взвешивать стоимость рефлексии, компилированных делегатов и сгенерированного кода в продакшене.",
        ),
        heading("Конвейер компиляции: от текста до сборки"),
        text(
            "Сборки .NET устроены по ECMA-335: это переносимый формат, который содержит IL, метаданные "
            "и таблицу ссылок. Файл .dll или .exe — не машинный код, а контейнер описания программы. "
            "Такой дизайн даёт независимость от процессора, возможность анализировать и "
            "трансформировать код после компиляции и общие метаданные для всех языков платформы.\n\n"
            "Компилятор C# (Roslyn, пакет Microsoft.CodeAnalysis) работает в несколько фаз:\n"
            "- лексер и парсер строят синтаксическое дерево (syntax tree) — иерархию узлов без смысла, "
            "только структуру;\n"
            "- объявление символов и привязка (binding) связывают имена с типами и членами, появляется "
            "семантическая модель (semantic model) — именно она знает, что `var` это `List<int>`, "
            "а не строка;\n"
            "- проверка корректности и анализ потоков данных отбрасывает программы с ошибками;\n"
            "- эмиссия порождает IL и метаданные, а также дополнительную таблицу последовательных "
            "точек (sequence points) для отладки.\n\n"
            "Синтаксическое дерево — неизменяемое (immutable) представление исходного текста. Узел "
            "выражения хранит свои дочерние узлы и позицию в файле. Отсюда берут данные analyser-ы и "
            "генераторы исходного кода: они получают дерево или его элементы и не могут изменить "
            "существующий код, только добавить новый."
        ),
        example(
            "csharp",
            """
            using Microsoft.CodeAnalysis.CSharp;
            using Microsoft.CodeAnalysis.CSharp.Syntax;

            var tree = CSharpSyntaxTree.ParseText("int x = a + b * 2;");

            // Синтаксическое дерево не знает типов: только форма.
            var addition = tree.GetRoot()
                .DescendantNodes()
                .OfType<BinaryExpressionSyntax>()
                .First(e => e.IsKind(SyntaxKind.AddExpression));

            Console.WriteLine(addition.Left);
            Console.WriteLine(addition.Right);
            """,
        ),
        text(
            "Вывод: `a` и `b * 2`. Обратите внимание: узлов с видом `AddExpression` в этом коде два — "
            "само сложение и внутренний `b * 2` имеет другой вид, поэтому фильтр по виду отбирает именно "
            "верхний узел. Чтобы узнать типы переменных, нужна семантическая модель, построенная на "
            "компиляции: `compilation.GetSemanticModel(tree).GetTypeInfo(node).Type` вернёт `int`. "
            "Разделение синтаксиса и семантики — фундаментальное свойство Roslyn: быстрый обход "
            "дерева ничего не вычисляет, а точная информация о типах стоит дороже."
        ),
        heading("IL: промежуточный язык и стек вычислений"),
        text(
            "IL — стековый язык: у него нет регистров и почти нет переменных выражения. Инструкции "
            "кладут значения на стек вычислений (evaluation stack) и снимают их оттуда. Аргументы "
            "метода адресуются по индексу: `ldarg.0` — это `this` в экземплярном методе, `ldarg.1` — "
            "первый явный аргумент. Локальные переменные объявляются в заголовке `locals`, "
            "ограничение глубины стека записано в `.maxstack`, а JIT использует его для проверки "
            "корректности.\n\n"
            "Почти вся «магия» C# — синтаксический сахар над IL. Автосвойства превращаются в поле и "
            "пару методов `get_X`/`set_X`; `foreach` — в вызов `GetEnumerator`, `MoveNext` и `Dispose`; "
            "лямбда — в метод с закрытым или открытым полем; `using` — в блок `try`/`finally` с "
            "вызовом `Dispose`. Читая IL, вы видите реальную стоимость кода.\n\n"
            "Стандартный цикл `for` по массиву с проверкой границ выглядит предсказуемо: загрузка "
            "индекса, сравнение с длиной, ветвление, загрузка элемента и сложение. Именно поэтому "
            "компилятор умеет отбрасывать проверку границ (bounds check elimination), а JIT — "
            "удалять лишние загрузки полей между вызовами."
        ),
        example(
            "csharp",
            """
            public static int Add(int a, int b) => a + b;

            // IL, который генерирует Roslyn:
            // .method public hidebysig static int32 Add(int32 a, int32 b) cil managed
            // {
            //     .maxstack 2
            //     ldarg.0        // положить аргумент a на стек
            //     ldarg.1        // положить аргумент b
            //     add            // снять два значения, положить сумму
            //     ret            // вернуть вершину стека
            // }
            """,
        ),
        example(
            "csharp",
            """
            public static int Sum(int[] values)
            {
                int total = 0;
                for (int i = 0; i < values.Length; i++)
                    total += values[i];
                return total;
            }

            // Сокращённый IL:
            // ldc.i4.0         total = 0
            // stloc.0
            // ldc.i4.0         i = 0
            // stloc.1
            // loop:
            // ldloc.1          i
            // ldarg.0          values
            // ldlen            длина массива
            // conv.i4
            // bge.s done       если i >= length — выйти
            // ldloc.0          total
            // ldarg.0
            // ldloc.1
            // ldelem.i4        values[i]
            // add
            // stloc.0
            // ldloc.1
            // ldc.i4.1
            // add
            // stloc.1
            // br.s loop
            // done:
            //	ldloc.0
            //	ret
            """,
        ),
        text(
            "Вывод в отладочной и релизной сборке отличается: без оптимизаций Roslyn оставляет "
            "локальные переменные в явном виде и запрещает перестановки, чтобы отладчик мог "
            "показывать промежуточные значения. В Release лишние `stloc`/`ldloc` исчезают, а "
            "недостижимый код удаляется. Если вы анализируете IL программы, собирайте её в "
            "конфигурации Release, иначе увидите отладочную форму и сделаете неверные выводы о "
            "производительности."
        ),
        heading("Чтение IL на практике"),
        text(
            "Для повседневной работы достаточно узнать десяток инструкций и привычек компилятора. "
            "Полезные группы:\n"
            "- загрузка: `ldarg.N` (аргумент), `ldloc.N` (локальная), `ldc.i4.N` (целая константа), "
            "`ldstr` (строковый литерал), `ldnull`;\n"
            "- сохранение: `starg.N`, `stloc.N`;\n"
            "- арифметика: `add`, `sub`, `mul`, `div`, `rem`; логика: `and`, `or`, `not`;\n"
            "- ветвления: `br` и `br.s` (безусловный), `brtrue`/`brfalse` (по истинности), "
            "`beq`/`bne.un`/`blt`/`bgt` (сравнения);\n"
            "- вызовы: `call` (статический или невиртуальный), `callvirt` (виртуальный, а также "
            "экземплярный через проверку на `null`), `newobj` (создание объекта), `calli` (вызов "
            "по указателю функции);\n"
            "- упаковка и приведение: `box`, `unbox.any`, `castclass`, `isinst`;\n"
            "- возврат — `ret`, исключение — `throw`.\n\n"
            "Отдельная особенность — `callvirt` для обычных экземплярных методов: он выбрасывает "
            "`NullReferenceException` при вызове на `null`, поэтому компилятор использует его даже "
            "для невиртуальных членов, когда нужна проверка."
        ),
        example(
            "csharp",
            """
            object boxed = 42;                  // box int32 -> object
            int unboxed = (int)boxed;           // unbox.any object -> int32

            string method = "ToUpperInvariant";
            // callvirt instance string [System.Runtime]System.String::ToUpperInvariant()
            string upper = method.ToUpperInvariant();

            // var d = new Dictionary<string, int>();
            // newobj instance void class Dictionary`2<string, int32>::.ctor()
            """,
        ),
        text(
            "Упаковка (`box`) — выделение объекта в управляемой куче и копирование в него значения. "
            "Обратное преобразование `unbox.any` копирует значение обратно и требует точного типа, "
            "иначе бросает `InvalidCastException`. Цикл, который кладёт `int` в `ArrayList` или "
            "`object`, занимается упаковкой на каждом шаге — именно этого избегают обобщённые "
            "коллекции, у которых элемент в IL представлен параметром типа без упаковки.\n\n"
            "Формат байткода IL — последовательность опкодов с операндами переменной длины. "
            "В метаданных методов лежит не только сам байткод, но и таблица исключительных "
            "областей: какие диапазоны инструкций защищены, где начинается обработчик и где — "
            "блок `finally`. Именно эта таблица, а не отдельные ловушки в байткоде, описывает "
            "структуру `try`/`catch`."
        ),
        callout(
            "info",
            "Где смотреть IL",
            "Пакет dotnet-ildasm из официального репозитория, утилита ilspycmd или отладчик ILSpy "
            "показывают полный IL, например: `dotnet tool install -g dotnet-ildasm`, "
            "`dotnet ildasm MyLibrary.dll -o MyLibrary.il`. Онлайн-площадка SharpLab.io показывает "
            "IL, дерево синтаксиса и результат декомпиляции одновременно, что удобно для обучения."
        ),
        heading("Атрибуты: данные, которые переживают компиляцию"),
        text(
            "Атрибут — это класс, унаследованный от `System.Attribute`, который компилятор записывает "
            "в метаданные связанного элемента. Объект атрибута существует не всегда: при загрузке "
            "сборки в памяти нет его экземпляров. Экземпляр создаётся, только когда вы запрашиваете "
            "его через рефлексию — конструктор выполняется в этот момент, а значения берутся из "
            "метаданных. Это важное следствие: конструктор атрибута должен быть быстрым и "
            "без побочных эффектов.\n\n"
            "Метаданные умеют хранить только ограниченный набор: примитивы, строки, `Type`, "
            "перечисления, массивы этих значений. Любые другие типы нельзя передать в атрибут, "
            "поэтому сложное состояние приходится передавать строками и разбирать в коде.\n\n"
            "`AttributeUsage` управляет тремя вещами: на какие цели можно применять атрибут "
            "(`AttributeTargets`), можно ли ставить несколько экземпляров на один элемент "
            "(`AllowMultiple`) и наследуется ли атрибут в производных типах и переопределённых "
            "методах (`Inherited`). Без этого атрибута действуют значения по умолчанию: "
            "`AttributeTargets.All`, `AllowMultiple = false`, `Inherited = true`."
        ),
        example(
            "csharp",
            """
            using System;

            [AttributeUsage(AttributeTargets.Class | AttributeTargets.Method,
                            AllowMultiple = true, Inherited = false)]
            public sealed class EndpointAttribute : Attribute
            {
                public string Path { get; }
                public string? Verb { get; set; }   // именованный аргумент
                public int Order { get; set; }

                public EndpointAttribute(string path) => Path = path;
            }

            [Endpoint("/users", Verb = "GET", Order = 2)]
            [Endpoint("/users", Verb = "POST")]
            public sealed class UsersController
            {
                [Endpoint("/users/{id}", Verb = "GET")]
                public void Get(int id) { }
            }

            public static class Program
            {
                public static void Main()
                {
                    foreach (var a in typeof(UsersController)
                                 .GetCustomAttributes<EndpointAttribute>(inherit: false))
                    {
                        Console.WriteLine($"{a.Verb,-5} {a.Path} (order {a.Order})");
                    }

                    var method = typeof(UsersController).GetMethod(nameof(UsersController.Get))!;
                    var single = method.GetCustomAttribute<EndpointAttribute>();
                    Console.WriteLine($"{single?.Verb} {single?.Path}");
                }
            }
            """,
        ),
        text(
            "Вывод: две строки `GET   /users (order 2)` и `POST  /users (order 0)`, затем "
            "`GET /users/{id}`. Позиционный аргумент `path` из конструктора и именованные "
            "`Verb`/`Order` из свойств — единственные способы передать данные в метаданные. "
            "Порядок перечисления атрибутов при `AllowMultiple = true` различается между "
            "компиляторами и даже версиями, поэтому на него нельзя опираться: если важна "
            "последовательность, выражайте её явным свойством вроде `Order`."
        ),
        heading("Встроенные атрибуты, которые меняют компиляцию"),
        text(
            "Часть атрибутов — не просто данные, а инструкции компилятору. `[Obsolete]` превращает "
            "использование в предупреждение или ошибку. `[Conditional(\"DEBUG\")]` удаляет вызовы "
            "метода целиком, если символ не определён, — это дешевле, чем проверка флага внутри "
            "метода, потому что исчезает даже вычисление аргументов. `[CallerMemberName]`, "
            "`[CallerFilePath]` и `[CallerLineNumber]` подставляют вызывающей стороны контекст, "
            "чём избавляют от ручного дублирования строк.\n\n"
            "Особый разряд — атрибуты, влияющие на инициализацию и поведение рантайма: "
            "`[Flags]` подсказывает `ToString` выводить комбинированные значения через запятую; "
            "`[MethodImpl(MethodImplOptions.AggressiveInlining)]` просит JIT встроить метод; "
            "`[StructLayout]` описывает точное размещение полей; `[MemberNotNull]` помогает "
            "статическому анализу потоков NULL. Все они записаны в метаданные и читаются либо "
            "компилятором C#, либо JIT, либо самим кодом."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Runtime.CompilerServices;

            public static class Trace
            {
                [Conditional("DEBUG")]
                public static void Log(string message,
                    [CallerMemberName] string caller = "",
                    [CallerLineNumber] int line = 0)
                {
                    Console.WriteLine($"{caller}:{line} {message}");
                }
            }

            public static class Program
            {
                public static void Main()
                {
                    Trace.Log("старт");          // в Release не компилируется вовсе
                    Run();
                }

                private static void Run() => Trace.Log("работает");
            }
            """,
        ),
        text(
            "Вывод в конфигурации Debug: `Main:19 старт` и `Run:22 работает`. В Release вывод "
            "отсутствует: вызовы `Trace.Log` удалены, включая вычисление аргументов. Обратите "
            "внимание, что имена членов и номера строк подставляются без единого строкового "
            "литерала в коде — их знает компилятор, а рантайм получает их уже готовыми."
        ),
        heading("Рефлексия: язык, который смотрит на себя"),
        text(
            "Рефлексия — это API, который превращает метаданные в объекты: `Type`, `MethodInfo`, "
            "`PropertyInfo`, `FieldInfo`, `ConstructorInfo`, `ParameterInfo`. `Type` даёт доступ к "
            "всему остальному и допускает два пути: статическую форму `typeof(T)` (компилятор "
            "создаёт ссылку на метаданные, объект возвращается из кеша рантайма) и `obj.GetType()` "
            "(поиск по таблице методов объекта). `Type.GetType(\"Namespace.Type, AssemblyName\")` "
            "третий путь — поиск по имени, самый медленный.\n\n"
            "Обобщённые типы в метаданных представлены открытыми определениями: `typeof(List<>)` "
            "описывает тип с параметром `T`, а `typeof(List<int>)` — замкнутую конструкцию. "
            "`MakeGenericType` строит замкнутый тип из определения, а `GetGenericArguments` "
            "возвращает аргументы. Рантайм кеширует замкнутые обобщения в отдельном кеше, "
            "поэтому повторные вызовы `MakeGenericType` с теми же типами дешевле первых."
        ),
        example(
            "csharp",
            """
            using System;

            var open = typeof(Dictionary<,>);
            var closed = open.MakeGenericType(typeof(string), typeof(int));

            Console.WriteLine(open.IsGenericTypeDefinition);   // True
            Console.WriteLine(closed.Name);                    // Dictionary`2
            Console.WriteLine(string.Join(",", closed.GetGenericArguments())); // System.String,System.Int32
            """,
        ),
        example(
            "csharp",
            """
            using System;
            using System.Collections.Generic;
            using System.Reflection;
            using System.Runtime.ExceptionServices;

            public sealed class Person
            {
                private readonly string _secret = "скрытое";
                public string Name { get; set; } = "Ада";
                public int Age { get; set; } = 36;
            }

            public static class Program
            {
                public static void Main()
                {
                    var type = typeof(Person);

                    foreach (var p in type.GetProperties(BindingFlags.Public | BindingFlags.Instance))
                        Console.WriteLine($"{p.PropertyType.Name} {p.Name}");

                    // Приватное поле читается через рефлексию — это инструмент диагностики, не дизайна.
                    var secret = type.GetField("_secret", BindingFlags.NonPublic | BindingFlags.Instance)!;
                    Console.WriteLine(secret.GetValue(new Person()));

                    // Ошибки внутри метода, вызванного через Invoke, приходят обёрнутыми.
                    var parse = typeof(int).GetMethod(nameof(int.Parse), new[] { typeof(string) })!;
                    try
                    {
                        parse.Invoke(null, new object[] { "сорок два" });
                    }
                    catch (TargetInvocationException ex)
                    {
                        Console.WriteLine($"Внутренняя причина: {ex.InnerException?.GetType().Name}");
                    }
                }
            }
            """,
        ),
        text(
            "Вывод: `String Name`, `Int32 Age`, затем `скрытое`, затем `Внутренняя причина: "
            "FormatException`. Рефлексивный вызов заворачивает исключение целевого метода в "
            "`TargetInvocationException`, и настоящая причина лежит в `InnerException`. Для "
            "повторной генерации исходного стекового следа существует "
            "`ExceptionDispatchInfo.Capture(ex.InnerException).Throw()`, которая сохраняет "
            "исходные строки стека."
        ),
        text(
            "Рефлексия решает задачи, недоступные статическому коду: сериализаторы, контейнеры "
            "зависимостей, ORM, плагины и инструменты тестирования находят типы и члены по имени. "
            "Но у неё три особенности. Вызовы не проверяются компилятором: опечатка в имени "
            "метода выявится только `NullReferenceException` или `AmbiguousMatchException`. "
            "Скорость: каждый вызов `Invoke` проводит проверку аргументов, упаковку и "
            "разрешение метода, эти издержки в десятки раз выше прямого вызова. И зависимость "
            "от JIT: рантайм не может встроить рефлексивный вызов и ничего не знает о типе "
            "объекта в точке вызова, поэтому вызов через `MethodInfo` часто лишает код "
            "встраивания."
        ),
        heading("Деревья выражений: лямбда как данные"),
        text(
            "Лямбда-выражение компилятор превращает в делегат, но если целевой тип — "
            "`Expression<Func<...>>`, он вместо этого строит дерево выражения: объектную модель, в "
            "которой каждый узел описывает операцию — сложение, доступ к свойству, вызов метода, "
            "константу, параметр. Дерево можно обойти, прочитать и превратить в SQL, в шаблон, в "
            "IL. Делегат этого не позволяет: внутри него только машинный код, недоступный "
            "для анализа.\n\n"
            "Именно поэтому LINQ to SQL и Entity Framework принимают "
            "`Expression<Func<T, bool>>`, а не `Func<T, bool>`: делегат был бы исполнен в памяти, "
            "а дерево переводится в запрос к базе. Метод, который принимает функцию для выполнения, "
            "берёт `Func`; метод, который переводит функцию в другой язык, берёт `Expression<Func>`.\n\n"
            "Деревья неизменяемы — как деревья синтаксиса. Каждый `Expression` — объект одного из "
            "десятков подтипов: `BinaryExpression`, `MemberExpression`, `MethodCallExpression`, "
            "`ConstantExpression`, `LambdaExpression`. Свойство `NodeType` даёт вид узла, "
            "`CanReduce` и `Reduce` позволяют раскрыть составные узлы."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Linq.Expressions;

            Expression<Func<int, int, int>> expr = (a, b) => a + b * 2;

            Console.WriteLine(expr.NodeType);          // Lambda
            Console.WriteLine(expr.Body.NodeType);     // Add
            Console.WriteLine(((BinaryExpression)expr.Body).Right.NodeType); // Multiply

            foreach (var p in expr.Parameters)
                Console.WriteLine($"{p.Name}:{p.Type.Name}");

            var compiled = expr.Compile();
            Console.WriteLine(compiled(3, 4));         // 11
            """,
        ),
        text(
            "Дерево, построенное компилятором, отражает приоритет операторов: тело лямбды — это "
            "сложение, правый операнд которого — умножение. Параметры — не значения, а "
            "идентификаторы (`ParameterExpression`), у каждого своя область видимости. Важно "
            "помнить: лямбда с блоком инструкций (несколько строк в фигурных скобках) в частях "
            "дерева невозможна — язык разрешает только выражения. Многооператорный код "
            "собирается вручную через `Expression.Block`.\n\n"
            "`Compile()` первый раз дороже, чем рефлексивный вызов: он порождает код через "
            "внутренний компилятор. Поэтому дерево компилируют один раз для часто повторяющегося "
            "вызова и повторно используют полученный делегат. С версии .NET выражение "
            "компилируется в `DynamicMethod` и попадает в кеш JIT, поэтому повторные вызовы "
            "практически совпадают с прямыми."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Linq.Expressions;

            public sealed class Person
            {
                public string Name { get; set; } = "";
                public int Age { get; set; }
            }

            public static class Program
            {
                public static void Main()
                {
                    var p = Expression.Parameter(typeof(Person), "p");
                    var name = Expression.Property(p, nameof(Person.Name));
                    var lambda = Expression.Lambda<Func<Person, string>>(name, p);
                    var getName = lambda.Compile();

                    Console.WriteLine(getName(new Person { Name = "Ада" }));

                    // Блок с локальной переменной: temp = 10; temp + 5
                    var temp = Expression.Variable(typeof(int), "temp");
                    var block = Expression.Block(
                        new() { temp },
                        Expression.Assign(temp, Expression.Constant(10)),
                        Expression.Add(temp, Expression.Constant(5)));

                    var getValue = Expression.Lambda<Func<int>>(block).Compile();
                    Console.WriteLine(getValue());
                }
            }
            """,
        ),
        text(
            "Вывод: `Ада` и `15`. Эти два примера показывают два способа работы: `Expression.Property` "
            "строит доступ к свойству из строки или `nameof`, а `Expression.Block` собирает "
            "последовательность инструкций с объявлением локальных переменных. При ручном построении "
            "дерева признак `MemberExpression` сохраняет имена — они нужны, когда дерево обходит "
            "поставщик запросов и ищет в нём столбцы таблицы.\n\n"
            "Главные практические сценарии: динамическая валидация и фильтрация (параметр "
            "сравнения пришёл строкой), построение запросов, где поле выбирается по имени, "
            "автоматическое создание выражений для проекций DTO (`Select`), повторное использование "
            "части выражения в составных запросах EF Core. В последнем случае просто вставить "
            "дерево внутрь другого нельзя — параметры не совпадают, и на помощь приходит визитор."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Linq.Expressions;

            public sealed class Person
            {
                public string Name { get; set; } = "";
                public int Age { get; set; }
            }

            public static class Program
            {
                private sealed class ParameterReplacer(ParameterExpression from, ParameterExpression to)
                    : ExpressionVisitor
                {
                    protected override Expression VisitParameter(ParameterExpression node) =>
                        node == from ? to : base.VisitParameter(node);
                }

                public static void Main()
                {
                    // Внешний фильтр: x => x.Age > 30
                    var x = Expression.Parameter(typeof(Person), "x");
                    var outer = Expression.Lambda<Func<Person, bool>>(
                        Expression.GreaterThan(
                            Expression.Property(x, nameof(Person.Age)),
                            Expression.Constant(30)),
                        x);

                    Console.WriteLine(outer);
                    Console.WriteLine(new ParameterReplacer(x, x).Visit(outer));
                }
            }
            """,
        ),
        text(
            "`ExpressionVisitor` — базовый посетитель дерева: он рекурсивно обходит все дочерние "
            "узлы, а каждый метод `VisitXxx` можно переопределить. Переопределив `VisitParameter`, "
            "можно подменить параметр одного выражения на параметр другого — стандартный приём в "
            "библиотеках, которые комбинируют условия и запросы. `ToString()` у `LambdaExpression` "
            "даёт текстовое представление дерева, это лучший способ отладки: если в дереве не хватает "
            "узла или порядок операций не тот, `ToString()` покажет расхождение.\n\n"
            "Ограничение подхода: посетитель возвращает новое дерево, исходное остаётся неизменным. "
            "Если внешнее дерево используется повторно в цикле, каждый раз строится новый объект — "
            "кешируйте результат, а не дерево."
        ),
        callout(
            "warning",
            "`Func` вместо `Expression<Func>`",
            "Если метод принимает `Func<T, bool>`, компилятор сложит лямбду в делегат, и EF Core "
            "выполнит фильтр в памяти после загрузки таблицы — иногда всей. Принимайте "
            "`Expression<Func<T, bool>>` в методы, которые переводят предикат в запрос, и "
            "`Func<T, bool>` — в методы, которые исполняют его в памяти."
        ),
        heading("Генерация кода во время выполнения: Reflection.Emit"),
        text(
            "Если дерево выражений — удобный конструктор кода, то `System.Reflection.Emit` — "
            "конструктор на уровне байткода. `DynamicMethod` создаёт метод, не входящий в "
            "сборку: он принадлежит рантайму и после `CreateDelegate` превращается в обычный "
            "делегат, который JIT компилирует и встраивает так же, как статический код.\n\n"
            "Писать IL вручную опасно: рантайм проверит стек и типы только при первой компиляции "
            "или исполнении, и ошибка проявится как `InvalidProgramException` без указания места. "
            "Именно поэтому в современном .NET руками IL порождают редко: express trees "
            "покрывают большинство задач с проверкой типов на этапе построения, а "
            "`System.Linq.Expressions` и генераторы исходного кода закрывают остальное."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Reflection.Emit;

            var method = new DynamicMethod("Add", typeof(int), new[] { typeof(int), typeof(int) });
            var il = method.GetILGenerator();
            il.Emit(OpCodes.Ldarg_0);
            il.Emit(OpCodes.Ldarg_1);
            il.Emit(OpCodes.Add);
            il.Emit(OpCodes.Ret);

            var add = (Func<int, int, int>)method.CreateDelegate(typeof(Func<int, int, int>));
            Console.WriteLine(add(3, 5));   // 8
            """,
        ),
        text(
            "Три строки IL — ровно то, что компилятор записал в метаданные для `Add` в первом "
            "примере. Теперь вы замкнули круг: код, который раньше читался в IL, собран вручную "
            "и исполнен JIT. `DynamicMethod` полезен в библиотеках сериализации и проксирования, "
            "где дерево выражений не выражает нужную операцию, например доступ к полю по "
            "адресу или структуре без обёртки. `DispatchProxy` даёт готовую замену ручному Emit "
            "для прокси: класс наследуется от `DispatchProxy`, а `Invoke` получает `MethodInfo` "
            "и аргументы и может логировать или подменять результат."
        ),
        heading("Генераторы исходного кода: та же работа, но заранее"),
        text(
            "Генератор исходного кода — это часть компилятора, написанная вами. Он подключается к "
            "проекту как анализатор Roslyn, получает доступ к компиляции и добавляет новые файлы "
            "C#, которые собираются вместе с остальным кодом. Главное следствие: сгенерированный "
            "код — полноценный статический код, проверенный компилятором и встраиваемый JIT.\n\n"
            "Исторически первая модель `ISourceGenerator` запускалась на каждую компиляцию целиком "
            "и генерировала всё заново. Инкрементальная модель `IIncrementalGenerator` (C# 9, "
            ".NET 5+) позволяет описать конвейер: из синтаксического провайдера берутся узлы, "
            "фильтруются и проецируются в простые неизменяемые модели, а результат кешируется по "
            "входу. При изменении одного файла пересчитывается только затронутая ветвь конвейера — "
            "это заметно ускоряет сборку в больших решениях.\n\n"
            "Генератор работает в изолированном процессе компилятора: у него нет доступа к файлам, "
            "к базе данных и к сети. Всё, что ему нужно, он выводит из синтаксического дерева и "
            "символов. Если генератор бросит исключение, сборка упадёт с трудно читаемой ошибкой, "
            "поэтому все исключения перехватываются и сообщаются через "
            "`SourceProductionContext.ReportDiagnostic`."
        ),
        example(
            "csharp",
            r"""
            using Microsoft.CodeAnalysis;
            using Microsoft.CodeAnalysis.CSharp.Syntax;
            using Microsoft.CodeAnalysis.Text;
            using System.Text;

            [Generator]
            public sealed class CountGenerator : IIncrementalGenerator
            {
                public void Initialize(IncrementalGeneratorInitializationContext context)
                {
                    // Классы, помеченные атрибутом [GenerateCount].
                    var classes = context.SyntaxProvider.ForAttributeWithMetadataName(
                            "GenerateCountAttribute",
                            predicate: static (node, _) => node is ClassDeclarationSyntax,
                            transform: static (ctx, _) => (ClassDeclarationSyntax)ctx.TargetNode)
                        .Select(static (node, _) => node.Identifier.Text);

                    context.RegisterSourceOutput(classes, static (ctx, name) =>
                    {
                        // Исходник собирается конкатенацией, чтобы не вкладывать кавычки в код.
                        string source =
                            "// <auto-generated />" + Environment.NewLine +
                            "partial class " + name + Environment.NewLine +
                            "{" + Environment.NewLine +
                            "    public static string Generated() => \"готово\";" + Environment.NewLine +
                            "}";
                        ctx.AddSource($"{name}.Generated.g.cs", SourceText.From(source, Encoding.UTF8));
                    });
                }
            }
            """,
        ),
        text(
            "Пользовательский код при этом выглядит без всякой рефлексии:\n"
            "- в основном проекте объявляется `partial class Users { }` с атрибутом "
            "`[GenerateCount]`;\n"
            "- генератор добавляет файл, в котором `partial class Users` получает метод "
            "`Generated()`;\n"
            "- вызов `Users.Generated()` связывается компилятором напрямую — никакого поиска в "
            "метаданных во время выполнения и никаких исключений за отсутствие атрибута.\n\n"
            "Практические применения обширны: источник System.Text.Json сам генерирует "
            "сериализаторы, `LoggerMessage` генерирует типизированные методы логирования без "
            "упаковки, библиотеки маппинга генерируют преобразования, а ASP.NET Core генерирует "
            "обработчики маршрутов и минимальных API. Общее правило: если работа выполнима на "
            "этапе компиляции, она выполняется там — это ускоряет старт, избавляет от рисков "
            "late binding и работает даже при обрезании сборки (trimming), которое удаляет "
            "неиспользуемые метаданные."
        ),
        callout(
            "success",
            "Правило выбора: сначала компилятор",
            "Порядок предпочтений при выборе механизма: статический код и генератор исходного "
            "кода, затем дерево выражений, затем рефлексия с кешированием, и в самом конце — "
            "ручной IL. Каждый шаг в этом списке добавляет гибкость и отнимает проверки "
            "компилятора и производительность."
        ),
        heading("Стоимость механизмов в цифрах"),
        text(
            "Производительность рефлексии зависит от точек измерения: первый вызов включает "
            "разрешение метода и проверки, последующие — кеш рантайма на уровне обработчиков "
            "вызовов. Компилированный из дерева делегат при повторных вызовах приближается к "
            "прямому вызову, но не всегда встраивается: делегат остаётся косвенным переходом. "
            "Сгенерированный код ничем не отличается от написанного руками и встраивается на "
            "общих основаниях.\n\n"
            "Порядки величин зависят от машины и версии .NET; цифры ниже показывают "
            "относительный масштаб, а не точные замеры. В реальном коде измеряйте "
            "`BenchmarkDotNet`, а не запоминайте числа."
        ),
        table(
            ["Механизм", "Проверка типов", "Относительная цена", "Когда выбирать"],
            [
                ["Прямой вызов", "Компилятор", "1", "Всегда, когда тип известен"],
                ["Сгенерированный код", "Компилятор", "1", "Известный набор типов и членов"],
                ["Дерево выражений, Compile", "Частично, при построении", "2–5 на повторном вызове", "Даже после первого Compile — кешировать делегат"],
                ["DynamicMethod", "Только при JIT", "1–2 после делегата", "Невыразимое деревом, низкоуровневые библиотеки"],
                ["MethodInfo.Invoke", "Только во время выполнения", "30–100", "Редкие вызовы, плагины, инструменты"],
                ["Получение Type и членов", "Только во время выполнения", "Относительно дорого", "Один раз, в статических кешах"],
            ],
        ),
        text(
            "Из таблицы следуют три практических правила. Кешируйте результаты поиска: "
            "`typeof(List<int>).GetMethod(...)` в цикле — типичная ошибка, а статическое поле "
            "`static readonly MethodInfo` решает её. Если член станет вызываться часто, "
            "компилируйте делегат один раз и храните его. Если типы известны на этапе "
            "компиляции, вынесите работу в генератор — тогда в горячем пути вообще не будет "
            "метаданных."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Рефлексия в горячем пути без кеширования", "Поиск `MethodInfo` и разбор аргументов на каждом вызове", "Кешировать `MethodInfo` и делегат в статическом поле"],
                ["`GetMethods()` без `BindingFlags`", "Возвращаются только публичные члены; неявные изменения при добавлении `NonPublic` ломают логику", "Явно перечислять `BindingFlags.Public | NonPublic | Instance | Static`"],
                ["`Invoke` с непроверенным результатом", "Ошибка метода маскируется `TargetInvocationException`, диагностика уходит в `InnerException`", "Разворачивать исключение или использовать `ExceptionDispatchInfo`"],
                ["Атрибут с побочными эффектами в конструкторе", "Конструктор выполняется при каждом чтении через рефлексию, а не один раз", "Делать конструктор быстрым, без ввода-вывода и исключений"],
                ["`Func` вместо `Expression<Func>` в запросном API", "Фильтр исполняется в памяти, EF Core тянет лишние данные", "Принимать `Expression<Func<T, bool>>` для перевода в запрос"],
                ["Дерево выражений с блоком в лямбде", "Компилятор не превращает блок в дерево, ошибка при компиляции", "Собирать блок через `Expression.Block` или использовать делегат"],
                ["Генератор бросает исключение", "Сборка падает без указания места, диагностика теряется", "Перехватывать и сообщать через `ReportDiagnostic`"],
                ["Генератор не перезапускается при изменении", "Некорректный предикат или изменяемое состояние в генераторе", "Использовать `IIncrementalGenerator` и неизменяемые модели"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполните в отдельном консольном проекте (`dotnet new console`). "
            "Для заданий с генератором создайте второй проект `<OutputItemType>Analyzer</OutputItemType>`, "
            "сославитесь на него из основного через `ProjectReference` только для `OutputItemType` и "
            "`ReferenceOutputAssembly=false`."
        ),
        numbered(
            "Инспектор IL: напишите программу, которая по `typeof(T)` перечисляет публичные методы типа, выводит имена, параметры и то, является ли метод виртуальным. Для двух методов подсмотрите IL через SharpLab и объясните разницу между вызовами `call` и `callvirt`.",
            "Валидация через атрибуты: определите атрибуты `[Required]`, `[StringLength(min, max)]` и `[Range(min, max)]`, примените их к классу `User` и реализуйте валидатор, читающий атрибуты свойств через рефлексию и возвращающий список ошибок.",
            "Дерево выражений: постройте вручную дерево для `x => x.Length >= minLength`, где `minLength` — внешняя переменная `int`. Скомпилируйте его и проверьте на строках разной длины. Затем объясните, каким узлом представлена захваченная переменная.",
            "Визитор: напишите посетитель, который заменяет в дереве `Expression.Constant(10)` на `Expression.Constant(100)`, и примените его к дереву `x => x + 10` для `x = 5`. Проверьте, что результат равен 105, а исходное дерево не изменилось.",
            "Сгенерированный код: определите атрибут `[GenerateOptions]`, константу строки с именем свойства и напишите инкрементальный генератор, создающий для помеченного `partial class` статическое свойство `Name => \"<ClassName>\"`. Убедитесь, что проект собирается и вызов компилируется без рефлексии.",
        ),
        text("Ожидаемый вывод для четвёртого задания:"),
        example(
            "text",
            "Исходное дерево: x => (x + 10)\n"
            "После визитора: x => (x + 100)\n"
            "Значение: 105",
        ),
        callout(
            "success",
            "Подсказка к заданию 3",
            "Захваченная лямбдой локальная переменная в документе выражения изображается узлом "
            "`MemberExpression` с `Expression` типа `ConstantExpression` — объекта-замыкания "
            "(closure), а `Member` — автогенераторное поле этого объекта. Работа с замыканием в "
            "деревьях — причина частых утечек в библиотеках, которые держат дерево дольше "
            "необходимого."
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем синтаксическое дерево Roslyn отличается от семантической модели и почему генераторы работают на первом, а анализаторы часто на обеих?",
            "Почему вызов обычного невиртуального метода в IL кодируется как `callvirt`, а не `call`?",
            "В какой момент создаётся объект атрибута и что это значит для его конструктора?",
            "Почему `Func<T, bool>` делает запрос EF Core неполноценным по сравнению с `Expression<Func<T, bool>>`?",
            "Зачем нужен `IIncrementalGenerator` вместо `ISourceGenerator` и в чём отличие его конвейера?",
        ),
        heading("Ответы", 3),
        numbered(
            "Синтаксическое дерево хранит структуру текста: узлы и их позиции, но не знает типов — `var` там просто ключевое слово. Семантическая модель связывает узлы с символами и типами, она требует построения компиляции и потому дороже. Генераторы добавляют код и часто работают только по форме и атрибутам, анализаторы же проверяют типы и поток данных, поэтому им нужен semantic model.",
            "`callvirt` перед вызовом проверяет, что ссылка на экземпляр не `null`, и бросает `NullReferenceException`, поэтому компилятор использует его и для невиртуальных экземплярных методов — это бесплатная проверка и защита от обращения к пустому экземпляру.",
            "Объект атрибута создаётся в момент чтения через рефлексию: конструктор не выполняется при загрузке сборки, а метаданные хранят лишь позиционные и именованные аргументы. Поэтому конструктор должен быть лёгким и без побочных эффектов, а выполнение может повториться при каждом запросе атрибута.",
            "`Func<T, bool>` компилятор превращает в делегат с исполняемым кодом: его нельзя перенести в SQL, поэтому провайдер загружает данные и фильтрует их в памяти. `Expression<Func<T, bool>>` — дерево, из которого провайдер строит SQL и передаёт фильтр в базу.",
            "`IIncrementalGenerator` строит конвейер из синтаксического провайдера и неизменяемых моделей, кеширует результат по входу и пересчитывает только затронутую ветвь. `ISourceGenerator` запускается на каждую компиляцию целиком и не кеширует промежуточные результаты, что замедляет сборку.",
        ),
        heading("Итоги"),
        bullets(
            "Путь кода: синтаксическое дерево Roslyn, семантика, IL и метаданные в сборке по ECMA-335, затем JIT при первом исполнении.",
            "IL — стековый язык без регистров: `ldarg`/`ldloc`/`ldc` кладут значения, `add` и вызовы снимают их, `.maxstack` ограничивает глубину, `callvirt` проверяет `null`.",
            "Атрибуты — классы от `System.Attribute`, записанные в метаданные; их экземпляры создаются только при чтении через рефлексию, а `AttributeUsage` управляет целями, кратностью и наследованием.",
            "`[Conditional]` и `[CallerXxx]` меняют компиляцию: первый удаляет вызовы целиком, остальные подставляют контекст вызова без литералов в коде.",
            "Рефлексия даёт `Type`, `MethodInfo` и `PropertyInfo`, открытые и замкнутые обобщения; она гибкая, но непроверяемая компилятором и дорогая — кешируйте и компилируйте делегаты.",
            "Деревья выражений превращают лямбду в данные, так что её можно перевести в SQL; `ExpressionVisitor` позволяет трансформировать дерево с подменой параметров.",
            "`Reflection.Emit` и `DynamicMethod` строят байткод вручную с минимальными проверками; его место — низкоуровневые библиотеки и прокси.",
            "Генераторы исходного кода переносят работу на этап компиляции: результат — обычный статический код без рефлексии в горячем пути и без риска отвалиться при trimming.",
        ),
        heading("Что дальше"),
        text(
            "Следующий урок закрывает тему продвинутого C#: паттерны сопоставления, записи, "
            "инициализаторы, `ref`-возвраты и особенности `async`-итераторов. Знание IL пригодится "
            "сразу: запись — это класс с генерируемыми членами, а сопоставление с образцом "
            "опускается в цепочки проверок типов, `isinst` и обращение к свойствам. Следующий урок "
            "после него — управление памятью, где понимание кучи и упаковки окончательно "
            "складывается в целостную картину."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "ECMA-335: Common Language Infrastructure — ecma-international.org/publications-and-standards/standards/ecma-335",
            "Документация .NET: System.Reflection.Emit — learn.microsoft.com/dotnet/api/system.reflection.emit",
            "Документация .NET: Expression Trees — learn.microsoft.com/dotnet/csharp/advanced-topics/expression-trees",
            "Примеры генераторов исходного кода от команды Roslyn — github.com/dotnet/roslyn-sdk/tree/main/samples/CSharp/SourceGenerators",
            "SharpLab.io — онлайн-просмотр IL, синтаксического дерева и декомпиляции — sharplab.io",
            "Сергей Тепляков, «Паттерны проектирования» — главы о прозрачных прокси и рефлексии на платформе .NET",
        ),
    ],
}
