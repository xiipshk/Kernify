"""Урок 3.3 курса csharp: продвинутый C#."""

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
    "topic_order": 3,
    "name": "3.3. Продвинутый C#",
    "slug": "csharp-3-3-продвинутый-c",
    "short_description": (
        "Расширения типов без изменения их кода, перегрузка операторов, индексаторы "
        "с поддержкой диапазонов, параметры ref/in/out, Span для работы без аллокаций "
        "и аккуратное использование unsafe-кода."
    ),
    "topic_name": "Продвинутый C#",
    "topic_description": (
        "Возможности языка, которые отделяют прикладной код от библиотечного: "
        "extension-члены, перегрузка операторов и преобразований, индексаторы и операторы ^ и .., "
        "семантика ref/in/out и ref struct, Span<T> и Memory<T> как безаллокационные представления памяти, "
        "а также указатели, stackalloc и fixed там, где без них не обойтись."
    ),
    "learning_objectives": [
        "Писать extension-методы и расширения на блоках extension, не меняя исходный тип",
        "Перегружать арифметические и сравнительные операторы, пары == и != и неявные и явные преобразования",
        "Строить индексаторы и типы с поддержкой Index и Range, включая многомерные",
        "Выбирать между ref, in и out и объяснять, как эти модификаторы влияют на копирование и ABI",
        "Применять Span<T>, ReadOnlySpan<char> и Memory<T> для разбора данных без выделения памяти",
        "Использовать unsafe, stackalloc и fixed осознанно, понимая риски и правила закрепления объектов",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "csharp",
        "extension methods",
        "операторы",
        "индексаторы",
        "spans",
        "unsafe",
    ],
    "starter_code": code(
        r"""
        using System;

        var point = new Point(3, 4);
        Point shifted = point + new Point(1, 2);

        Console.WriteLine(point);
        Console.WriteLine(shifted);
        Console.WriteLine($"Длина: {point.Length():F1}");
        Console.WriteLine($"x of shifted: {shifted["x"]}");
        """
    ),
    "hints": [
        "Перегрузка оператора == без Equals и GetHashCode даёт несогласованное поведение: словари и record найдут объект, а оператор сравнения сочтёт его другим.",
        "Span<T> — ref struct: его нельзя сохранить в поле класса, использовать в async-методе или итераторе. Для таких случаев берите Memory<T> и получайте Span в момент работы.",
        "out-параметр обязательно присваивается внутри метода до любого выхода, включая return в начале. Компилятор проверяет это на всех путях выполнения.",
        "stackalloc на стеке ограничен размером стека потока (обычно 1 МБ). Всё, что больше нескольких килобайт, выделяйте в куче или через ArrayPool.",
    ],
    "content": [
        text(
            "Продвинутый C# — это возможности, которые позволяют писать библиотечный код: расширять чужие типы, "
            "задавать для своих типов привычный синтаксис, работать с памятью без лишних копий и аллокаций. "
            "В повседневном приложении они встречаются реже, но именно на них построены LINQ, "
            "коллекции, сериализаторы и весь высокопроизводительный слой .NET.\n\n"
            "Многие из этих средств устроены так, что неверное использование компилируется без предупреждений, "
            "а ошибка проявляется в рантайме или в замерах производительности. "
            "Span в поле класса или указатель без fixed компилируются без ошибок там, где это возможно. "
            "Поэтому вместе с синтаксисом разберём правила, которые язык навязывает, и их причины."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "писать extension-методы и групповые расширения на блоках extension, не меняя исходный тип;",
            "перегружать арифметические и сравнительные операторы и согласовывать их с Equals, GetHashCode и IComparable;",
            "объявлять неявные и явные преобразования и выбирать между ними по риску потери данных;",
            "строить индексаторы, включая многомерные и совместимые с Index и Range;",
            "различать ref, in и out по смыслу, стоимости вызова и влиянию на бинарный интерфейс;",
            "использовать Span<T>, ReadOnlySpan<char> и Memory<T> для разбора и обработки данных без аллокаций;",
            "применять unsafe, stackalloc и fixed только там, где управляемого кода недостаточно;",
            "узнавать ошибки, которые компилятор в этих возможностях не ловит.",
        ),
        heading("Extension-члены"),
        text(
            "**Extension-метод** — статический метод в статическом классе, первый параметр которого помечен "
            "модификатором `this`. Компилятор позволяет вызывать его так, будто он объявлен в самом типе. "
            "Это не изменение типа и не наследование: метод просто транслируется в обычный статический вызов, "
            "а заодно попадает в автодополнение IDE.\n\n"
            "Дженерик-параметр расширения вводит новый тип, а не только расширяет существующий. "
            "Отдельная особенность: extension-метод можно вызвать и на null — вызов компилируется "
            "в статический метод с аргументом null."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Linq;

            public static class StringExtensions
            {
                public static bool IsNullOrEmpty(this string? value)
                    => string.IsNullOrEmpty(value);

                public static TResult? Pipe<T, TResult>(this T value, Func<T, TResult> func)
                    => value is null ? default : func(value);

                public static string Truncate(this string value, int maxLength)
                    => value.Length <= maxLength ? value : value[..maxLength] + "…";
            }

            Console.WriteLine("hello".IsNullOrEmpty());          // False
            Console.WriteLine(5.Pipe(x => x * 2).Pipe(x => x.ToString())); // 10
            Console.WriteLine("abcdefgh".Truncate(5));           // abcde…

            string? nothing = null;
            Console.WriteLine(nothing.IsNullOrEmpty());          // True
            """,
        ),
        text(
            "Вызов extension-метода на `null` допустим: он компилируется в статический вызов, и проверка на null "
            "внутри метода решает, что вернуть. Так `Pipe` не бросает `NullReferenceException`, а отдаёт значение по умолчанию."
        ),
        heading("Блоки extension"),
        text(
            "Начиная с C# 14 расширения объявляются блоком `extension(Type)` внутри статического класса. "
            "Внутри блока пишутся свойства, методы и даже статические члены; обращение к расширяемому значению "
            "идёт через ключевое слово `this`. Это позволяет добавить к типу **свойство**, чего обычные "
            "extension-методы сделать не могут.\n\n"
            "Блоки с одним и тем же типом можно объявлять несколько раз, и они группируются по назначению. "
            "Внутри одного блока у `this` один тип, поэтому параметры другого типа блок использовать не может: "
            "для этого пишут отдельный блок или обычный метод."
        ),
        example(
            "csharp",
            """
            public static class TextExtensions
            {
                extension(string text)
                {
                    public int WordCount
                        => text.Split(' ', StringSplitOptions.RemoveEmptyEntries).Length;

                    public bool IsPalindrome
                        => text.AsSpan().SequenceEqual(text.Reverse().ToArray());
                }
            }

            Console.WriteLine("check the words".WordCount);  // 3
            Console.WriteLine("а роза упала на лапу азора".WordCount); // 6
            """,
        ),
        callout(
            "info",
            "Расширения не ломают ABI",
            "Extension-члены — синтаксический сахар: в сборке остаётся обычный статический метод. "
            "Они не видны через рефлексию как члены типа, не участвуют в перегрузке виртуальных методов "
            "и проигрывают экземплярному методу с той же сигнатурой. Если метод появится в самом типе "
            "в более новой версии библиотеки, вызов начнёт уходить в него — это частая причина "
            "неожиданной смены поведения после обновления пакета."
        ),
        heading("Перегрузка операторов"),
        text(
            "**Перегрузка оператора** — объявление статического метода с именем `operator +`, `operator ==` и так далее. "
            "Хотя бы один операнд должен быть того типа, в котором объявлен оператор, поэтому переопределить "
            "сложение для `int` нельзя. Операторы обязаны быть `public` и `static`, а перегрузка присваиваний "
            "и `?:` невозможна — их компилятор строит из базовых операций.\n\n"
            "Правило простое: перегружайте операторы только там, где результат читается без объяснений. "
            "Сложение вектора с вектором ожидаемо, сложение двух заказов — нет."
        ),
        example(
            "csharp",
            """
            using System;

            public readonly struct Vector2
            {
                public double X { get; }
                public double Y { get; }

                public Vector2(double x, double y) => (X, Y) = (x, y);

                public static Vector2 operator +(Vector2 a, Vector2 b) => new(a.X + b.X, a.Y + b.Y);
                public static Vector2 operator -(Vector2 a, Vector2 b) => new(a.X - b.X, a.Y - b.Y);
                public static Vector2 operator *(Vector2 a, double k) => new(a.X * k, a.Y * k);
                public static Vector2 operator *(double k, Vector2 a) => a * k;
                public static Vector2 operator -(Vector2 a) => new(-a.X, -a.Y);

                public double Length() => Math.Sqrt(X * X + Y * Y);

                public override string ToString() => $"({X}, {Y})";
            }

            var a = new Vector2(1, 2);
            var b = new Vector2(3, 4);

            Console.WriteLine(a + b);        // (4, 6)
            Console.WriteLine(2.5 * a);      // (2.5, 5)
            Console.WriteLine(-a);           // (-1, -2)
            Console.WriteLine($"{(a + b).Length():F2}"); // 7.21
            """,
        ),
        text(
            "Нужны обе версии `operator *`: без второй формы выражение `2.5 * a` не скомпилируется, "
            "потому что `double` ничего не знает о `Vector2`. **Length** для вектора (4, 6) равна корню из 52, "
            "то есть 7.2111, и округляется до 7.21."
        ),
        heading("Операторы сравнения и Equals"),
        text(
            "Операторы `==` и `!=` объявляются только парой, а `<`, `>`, `<=`, `>=` — тоже парой с обеих сторон: "
            "компилятор требует противоположный оператор в том же типе. Для структур перегрузка `==` "
            "не переопределяет `Equals` автоматически, и без дополнительной работы появляется расхождение: "
            "`List.Contains` и словари пойдут через `Equals`, а написанный вручную код — через `==`.\n\n"
            "Правильный порядок такой: переопределить `Equals(T)`, реализовать `IEquatable<T>`, переопределить "
            "`Equals(object)`, `GetHashCode`, а операторы выразить через `Equals`. "
            "Для упорядочивания аналогично реализуют `IComparable<T>` и выражают через `CompareTo` операторы `<`, `>`."
        ),
        example(
            "csharp",
            """
            using System;

            public readonly struct Version : IComparable<Version>, IEquatable<Version>
            {
                public int Major { get; }
                public int Minor { get; }
                public int Patch { get; }

                public Version(int major, int minor, int patch) => (Major, Minor, Patch) = (major, minor, patch);

                public bool Equals(Version other)
                    => Major == other.Major && Minor == other.Minor && Patch == other.Patch;
                public override bool Equals(object? obj) => obj is Version v && Equals(v);
                public override int GetHashCode() => HashCode.Combine(Major, Minor, Patch);

                public int CompareTo(Version other)
                {
                    int c = Major.CompareTo(other.Major);
                    if (c != 0) return c;
                    c = Minor.CompareTo(other.Minor);
                    return c != 0 ? c : Patch.CompareTo(other.Patch);
                }

                public static bool operator ==(Version a, Version b) => a.Equals(b);
                public static bool operator !=(Version a, Version b) => !a.Equals(b);
                public static bool operator <(Version a, Version b) => a.CompareTo(b) < 0;
                public static bool operator >(Version a, Version b) => a.CompareTo(b) > 0;
                public static bool operator <=(Version a, Version b) => a.CompareTo(b) <= 0;
                public static bool operator >=(Version a, Version b) => a.CompareTo(b) >= 0;

                public override string ToString() => $"{Major}.{Minor}.{Patch}";
            }

            var v1 = new Version(1, 10, 0);
            var v2 = new Version(1, 9, 3);

            Console.WriteLine(v1 > v2);        // True
            Console.WriteLine(v1 == v2);       // False
            Console.WriteLine(1.10 < 1.9);     // False: сравнение как double
            """,
        ),
        callout(
            "warning",
            "Структура не должна быть mutable",
            "Перегрузка `++` для структуры требует изменяемого типа: оператор возвращает новое значение, "
            "а `x++` у структуры в поле только прочитает копию и запишет её обратно. "
            "Для неизменяемых структур `++` вводит в заблуждение и почти всегда уступает явному методу. "
            "В примере выше `1.10 < 1.9` ложно, потому что литералы сравниваются как дробные числа, "
            "а не как номера версий."
        ),
        heading("Неявные и явные преобразования"),
        text(
            "**Оператор преобразования** объявляется как `implicit operator` или `explicit operator` и превращает "
            "значение одного типа в другой. `implicit` разрешает делать это молча, `explicit` требует приведения в скобках. "
            "Правило выбора: неявное преобразование должно быть без потерь и без побочных эффектов.\n\n"
            "Преобразование с потерей данных или изменением смысла объявляют явным: слишком вольные неявные "
            "преобразования заставляют компилятор выбирать перегрузку метода неожиданно для читателя."
        ),
        example(
            "csharp",
            """
            using System;

            public readonly struct Celsius
            {
                public double Degrees { get; }
                public Celsius(double degrees) => Degrees = degrees;

                public static implicit operator Celsius(double degrees) => new(degrees);
                public static implicit operator double(Celsius c) => c.Degrees;

                public static explicit operator Fahrenheit(Celsius c)
                    => new(c.Degrees * 9 / 5 + 32);

                public override string ToString() => $"{Degrees} °C";
            }

            public readonly struct Fahrenheit
            {
                public double Degrees { get; }
                public Fahrenheit(double degrees) => Degrees = degrees;
                public override string ToString() => $"{Degrees} °F";
            }

            Celsius c = 25;              // implicit: double -> Celsius
            double d = c;                // implicit: Celsius -> double
            Fahrenheit f = (Fahrenheit)c; // explicit: нужен cast

            Console.WriteLine(c);        // 25 °C
            Console.WriteLine(d);        // 25
            Console.WriteLine(f);        // 77 °F
            """,
        ),
        text(
            "Из 25 градусов Цельсия получается ровно 77 по Фаренгейту. Чем больше объявленных преобразований, "
            "тем больше путей у компилятора при выводе типа выражения, поэтому набор стоит держать минимальным."
        ),
        heading("Индексаторы, Index и Range"),
        text(
            "**Индексатор** — член с именем `this`, который получает параметр в квадратных скобках. "
            "Он может иметь `get`, `set` или `init` и позволяет типу вести себя как коллекции. "
            "Индексатор с двумя параметрами даёт привычную запись `matrix[row, col]` вместо метода.\n\n"
            "Тип `Index` описывает позицию от начала или от конца (`^1` — последний элемент), "
            "тип `Range` — полуинтервал `..` с началом и концом. Компилятор транслирует `arr[^1]` в `arr[arr.Length - 1]` "
            "для массивов, а для своих типов нужно объявить индексатор с параметром `Index` или `Range` "
            "и воспользоваться методами `GetOffset` и `GetOffsetAndLength`."
        ),
        example(
            "csharp",
            """
            using System;

            int[] numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

            Console.WriteLine(numbers[^1]);      // 9
            Console.WriteLine(numbers[2..5].Length); // 3: элементы 2, 3, 4
            Console.WriteLine(numbers[..3].Length);  // 3
            Console.WriteLine(numbers[7..].Length);  // 3
            Console.WriteLine(numbers[^3..^1].Length); // 2

            Range middle = 4..7;
            Console.WriteLine(string.Join(",", numbers[middle])); // 4,5,6
            """,
        ),
        text(
            "Диапазон `2..5` включает индекс 2 и не включает 5, поэтому содержит три элемента. "
            "Срез `^3..^1` даёт значения 7 и 8. В отличие от Python, отрицательные индексы в C# "
            "не отсчитываются с конца: `numbers[-1]` выбросит исключение, для отсчёта с конца нужен `^`."
        ),
        example(
            "csharp",
            """
            using System;

            public sealed class Matrix
            {
                private readonly double[,] _cells;

                public Matrix(int rows, int cols) => _cells = new double[rows, cols];

                public int Rows => _cells.GetLength(0);
                public int Cols => _cells.GetLength(1);

                public double this[int row, int col]
                {
                    get => _cells[row, col];
                    set => _cells[row, col] = value;
                }

                public double this[Index row, Range cols]
                {
                    get
                    {
                        int r = row.GetOffset(Rows);
                        var (start, length) = cols.GetOffsetAndLength(Cols);
                        double sum = 0;
                        for (int c = start; c < start + length; c++) sum += _cells[r, c];
                        return sum;
                    }
                }
            }

            var m = new Matrix(3, 4);
            for (int r = 0; r < m.Rows; r++)
                for (int c = 0; c < m.Cols; c++)
                    m[r, c] = r * 10 + c;

            Console.WriteLine(m[1, 2]);        // 12
            Console.WriteLine(m[^1, 2..]);     // 22 + 23 = 45
            Console.WriteLine(m[1, ..3]);      // 10 + 11 + 12 = 33
            """,
        ),
        text(
            "В матрице последняя строка содержит 20, 21, 22, 23, поэтому `m[^1, 2..]` возвращает 45, "
            "а сумма первых трёх элементов строки 1 равна 33. `Range` и `Index` — обычные типы, "
            "их можно передавать параметрами, а `GetOffsetAndLength` проверяет границы "
            "и выбрасывает `ArgumentOutOfRangeException` при выходе за их пределы."
        ),
        heading("ref, in и out"),
        text(
            "Три модификатора параметров решают одну задачу — передать значение без копирования — "
            "и различаются по правам доступа внутри метода. `ref` даёт чтение и запись, значение должно быть "
            "инициализировано до вызова. `out` требует присвоить значение внутри метода и позволяет "
            "вызывать его с неинициализированной переменной. `in` даёт только чтение и был добавлен "
            "в C# 7.2 как безопасная замена `ref` для больших структур.\n\n"
            "Ключевая тонкость: `in` — это контракт для вызывающего кода, а не гарантия отсутствия копии. "
            "Компилятор может передать `in`-параметр по ссылке, но для маленьких структур может "
            "и скопировать значение, потому что это дешевле. А **ref readonly return** позволяет вернуть ссылку "
            "на уже существующее значение без копирования, обычно в поле структуры или в элемент массива."
        ),
        example(
            "csharp",
            """
            using System;

            public readonly struct BigRecord
            {
                public long A, B, C, D;          // 32 байта
                public long Sum => A + B + C + D;
            }

            public static class Operations
            {
                public static void Swap(ref int a, ref int b) => (a, b) = (b, a);

                public static bool TryHalf(int value, out int half)
                {
                    half = value / 2;
                    return value % 2 == 0;
                }

                public static long Total(in BigRecord r) => r.Sum;
            }

            int x = 1, y = 2;
            Operations.Swap(ref x, ref y);
            Console.WriteLine($"{x} {y}");                     // 2 1

            bool even = Operations.TryHalf(10, out int h1);
            bool odd = Operations.TryHalf(7, out int h2);
            Console.WriteLine($"{even} {h1} / {odd} {h2}");     // True 5 / False 3

            Console.WriteLine(Operations.Total(new BigRecord { A = 1, B = 2, C = 3, D = 4 })); // 10
            """,
        ),
        text(
            "`TryHalf(7)` возвращает `false`, но `out`-значение всё равно заполнено — 3. "
            "В этом смысл паттерна Try: итог передаётся через `bool`, а значение всегда доступно. "
            "`BigRecord` передаётся в `Total` по ссылке на чтение, поэтому 32 байта не копируются."
        ),
        heading("ref struct на стеке"),
        text(
            "**ref struct** — структура, экземпляр которой гарантированно живёт только на стеке. "
            "Такие типы нельзя упаковать, сохранить в поле класса или положить в массив: компилятор запрещает "
            "всё, что продлило бы жизнь значения за пределами кадра стека. `Span<T>` — самый известный ref struct, "
            "и его ограничения следуют именно из этого правила."
        ),
        example(
            "csharp",
            """
            using System;

            public ref struct Tokenizer
            {
                private ReadOnlySpan<char> _rest;

                public Tokenizer(ReadOnlySpan<char> input) => _rest = input;

                public bool MoveNext(out ReadOnlySpan<char> token)
                {
                    int comma = _rest.IndexOf(',');
                    if (comma < 0)
                    {
                        token = _rest;
                        _rest = default;
                        return token.Length > 0;
                    }

                    token = _rest[..comma];
                    _rest = _rest[(comma + 1)..];
                    return true;
                }
            }

            var t = new Tokenizer("a,b,cc,ddd");
            while (t.MoveNext(out var token))
                Console.WriteLine($"{token.Length} {token}");
            """,
        ),
        text(
            "Вывод: `1 a`, затем `1 b`, `2 cc`, `3 ddd`. Ни одна строка не создаётся: "
            "`Tokenizer` хранит остаток текста как `ReadOnlySpan<char>`, а каждый токен — срез той же памяти. "
            "Так работают `Utf8JsonReader` и разбор строк маршрутов в ASP.NET Core."
        ),
        heading("Span, Memory и отсутствие аллокаций"),
        text(
            "**Span<T>** — тип-значение из ссылки и длины, представляющий непрерывный участок памяти: "
            "массив, стек, строку или неуправляемую память. Срез `span[2..5]` не копирует данные, "
            "а создаёт новый Span над тем же участком. **Memory<T>** — то же представление, но не ref struct: "
            "его хранят в полях и передают в async-методы, получая Span через свойство `Span`.\n\n"
            "Правило выбора: синхронный код и горячий путь — Span; границы асинхронных методов и долгоживущие поля — Memory. "
            "Для текста используют `ReadOnlySpan<char>` из `AsSpan()`, а UTF-8-литералы C# 11 дают "
            "`ReadOnlySpan<byte>` прямо в коде без выделения строки."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Text;

            int[] data = [1, 2, 3, 4, 5, 6, 7, 8];
            Span<int> span = data;

            Span<int> middle = span[2..6];       // без копирования
            middle.Fill(0);

            Console.WriteLine(string.Join(",", data)); // 1,2,0,0,0,0,7,8

            Span<int> stack = stackalloc int[4];
            stack.Fill(42);
            Console.WriteLine(stack[0] + stack[3]);    // 84

            ReadOnlySpan<char> line = "key=value";
            int eq = line.IndexOf('=');
            Console.WriteLine($"[{line[..eq]}] [{line[(eq + 1)..]}]"); // [key] [value]
            """,
        ),
        text(
            "Заполнение среза нулями изменило исходный массив, потому что `middle` смотрит в ту же память. "
            "Span — представление, а не копия. `stackalloc int[4]` выделил буфер на стеке без обращения к куче, "
            "а разбор `key=value` по индексам не создал ни одной промежуточной строки."
        ),
        table(
            ["Тип", "Что представляет", "Хранение", "Типичное применение"],
            [
                ["`Span<T>`", "Изменяемый участок памяти", "Только стек, ref struct", "Синхронная обработка буферов и срезов"],
                ["`ReadOnlySpan<T>`", "Участок только для чтения", "Только стек, ref struct", "Разбор строк, поиск подстрок без аллокаций"],
                ["`Memory<T>`", "Изменяемый участок памяти", "Куча, обычная структура", "Поля классов, async-методы, пулы буферов"],
                ["`ReadOnlyMemory<T>`", "Участок только для чтения", "Куча, обычная структура", "Кэшированные блоки, контракты API"],
                ["`ArraySegment<T>`", "Диапазон массива", "Куча", "Старый код и API, которым нужна именно структура"],
            ],
        ),
        callout(
            "info",
            "Span не переживает await",
            "`await` может продолжить метод в другом потоке, а ссылка на стек предыдущего потока к тому моменту недействительна. "
            "Поэтому компилятор запрещает `await` в методе, где есть локальная переменная Span. "
            "Храните в поле `Memory<T>` и получайте Span после продолжения."
        ),
        heading("Разбор без аллокаций на практике"),
        text(
            "Главный выигрыш от Span — в коде, который разбирает текст: конфигурацию, CSV, заголовки HTTP. "
            "Наивная реализация через `Split` и `Substring` создаёт массив строк и отдельную строку на каждый фрагмент. "
            "Версия на `ReadOnlySpan<char>` не выделяет память вообще, а `TryParse` в типах .NET "
            "принимает срез и разбирает число прямо из исходной строки."
        ),
        example(
            "csharp",
            """
            using System;

            public static class QueryParser
            {
                public static int ParseValue(ReadOnlySpan<char> query, ReadOnlySpan<char> name)
                {
                    foreach (Range pair in query.Split('&'))
                    {
                        ReadOnlySpan<char> part = query[pair];
                        int eq = part.IndexOf('=');
                        if (eq < 0) continue;
                        if (part[..eq].SequenceEqual(name) && int.TryParse(part[(eq + 1)..], out int value))
                            return value;
                    }
                    return -1;
                }
            }

            ReadOnlySpan<char> query = "page=3&size=25&sort=name";
            Console.WriteLine(QueryParser.ParseValue(query, "size"));   // 25
            Console.WriteLine(QueryParser.ParseValue(query, "page"));   // 3
            Console.WriteLine(QueryParser.ParseValue(query, "offset")); // -1
            """,
        ),
        text(
            "Метод возвращает 25 для `size`, 3 для `page` и минус единицу для отсутствующего параметра. "
            "Все промежуточные значения — `ReadOnlySpan<char>` над исходной строкой, а такой разбор "
            "не выделяет память в куче."
        ),
        heading("unsafe, указатели и fixed"),
        text(
            "**Небезопасный код** (`unsafe`) снимает часть проверок: появляются настоящие указатели, "
            "арифметика над адресами и прямая запись в память. Чтобы использовать его, в файле проекта "
            "нужен параметр `<AllowUnsafeBlocks>true</AllowUnsafeBlocks>`. "
            "Нужен он при взаимодействии с неуправляемыми библиотеками и в очень горячем коде, где заметна "
            "даже проверка границ массива.\n\n"
            "Главная опасность — **перемещение объектов сборщиком мусора**: массив может сдвинуться при уплотнении "
            "кучи, и указатель без закрепления станет недействительным. Блок `fixed` закрепляет объект "
            "до своего завершения; после блока указатель использовать нельзя."
        ),
        example(
            "csharp",
            """
            using System;

            unsafe void SumWithPointers(int[] values)
            {
                int total = 0;

                fixed (int* p = values)
                {
                    for (int i = 0; i < values.Length; i++)
                        total += *(p + i);          // p[i] эквивалентно *(p + i)
                }

                Console.WriteLine(total);
            }

            SumWithPointers([1, 2, 3, 4, 5]);       // 15

            // stackalloc в unsafe-контексте: буфер живёт на стеке
            unsafe
            {
                int* buffer = stackalloc int[4];
                for (int i = 0; i < 4; i++)
                    buffer[i] = i * i;

                Console.WriteLine(buffer[0] + buffer[1] + buffer[2] + buffer[3]); // 0+1+4+9 = 14
            }
            """,
        ),
        text(
            "Указательная версия суммы получает 15, а буфер на стеке даёт 14. В современном .NET тот же результат "
            "обычно достигается без `unsafe` через `Span<int>`, поэтому указатели оставляют "
            "для interop-сценариев."
        ),
        heading("Когда unsafe оправдан"),
        table(
            ["Ситуация", "Подходить unsafe", "Обычно лучше"],
            [
                ["Чтение данных из native-библиотеки", "Да, через `fixed` и `Marshal`", "Использовать `Span<byte>` и `MemoryMarshal`"],
                ["Разбор большого текста в цикле", "Нет", "`ReadOnlySpan<char>` с `IndexOf` и `TryParse`"],
                ["Быстрая арифметика над массивами", "Почти никогда", "`Span<T>`, `Vector<T>` или SIMD-интринсики"],
                ["Структура с фиксированным размером для interop", "Да, `fixed`-буфер в `unsafe struct`", "`[InlineArray]` или `MarshalAs`"],
                ["Временный буфер до нескольких килобайт", "Не обязательно", "`stackalloc` с `Span<T>` без unsafe"],
            ],
        ),
        text(
            "Последняя строка таблицы важна: `stackalloc`, присвоенный `Span<T>`, не требует небезопасного "
            "контекста, но буфер всё равно лежит на стеке и освобождается автоматически. "
            "Мост к неуправляемому коду строят через `MemoryMarshal.GetReference`: он даёт ссылку "
            "на первый элемент, из которой получают Span нужной длины."
        ),
        example(
            "csharp",
            """
            using System;
            using System.Runtime.InteropServices;

            long ticks = DateTime.UtcNow.Ticks;

            Span<byte> bytes = stackalloc byte[8];
            MemoryMarshal.Write(bytes, in ticks);          // запись структуры в буфер

            long back = MemoryMarshal.Read<long>(bytes);   // чтение обратно
            Console.WriteLine(back == ticks);              // True

            Span<byte> flipped = bytes;
            flipped.Reverse();
            Console.WriteLine(MemoryMarshal.Read<long>(flipped) == ticks); // False: порядок байт обратный
            """,
        ),
        text(
            "Первый вывод — `True`: структура записана и прочитана в одном порядке байт. После разворота "
            "буфера получается `False`, потому что `long` собирается из переставленных байт. "
            "Для сетевых протоколов используют `BinaryPrimitives.ReadInt64BigEndian`, а не ручную сборку."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Перегружен `==`, но не `Equals`", "Словарь и `Contains` сравнивают по `Equals`, а оператор — иначе", "Реализовать `IEquatable<T>`, `Equals`, `GetHashCode` и выразить операторы через `Equals`"],
                ["Span сохранён в поле класса", "Ошибка компиляции: ref struct не может быть полем ссылочного типа", "Хранить `Memory<T>`, получать Span в методе через `.Span`"],
                ["`await` в методе с локальным Span", "Компилятор запрещает: ссылка на стек не переживает await", "Получать Span после await или передавать `Memory<T>`"],
                ["Указатель на массив без `fixed`", "Сборщик мусора перемещает объект, указатель становится недействительным", "Брать адрес только внутри блока `fixed`"],
                ["`stackalloc` на сотни килобайт", "Переполнение стека и аварийное завершение процесса", "Ограничить буфер несколькими килобайтами, для крупных — `ArrayPool`"],
                ["`in`-параметр изменён внутри метода", "Ошибка компиляции: параметр доступен только для чтения", "Использовать `ref`, если значение нужно менять"],
                ["Неявное преобразование с потерей точности", "Компилятор молча принимает опасный код в любом месте", "Объявить преобразование явным и требовать приведения"],
            ],
        ),
        heading("Практика"),
        text(
            "Работайте в консольном проекте .NET 9 или новее: `dotnet new console -n Advanced3`. "
            "Для заданий с указателями добавьте в файл проекта `<AllowUnsafeBlocks>true</AllowUnsafeBlocks>`, "
            "запуск — `dotnet run`."
        ),
        numbered(
            "Extension-методы: напишите расширения `ToSnakeCase` для строки и `Chunk` для целого числа, разбивающий коллекцию на куски указанного размера, не изменяя исходный тип.",
            "Операторы: реализуйте структуру `Money` с полем `decimal Amount` и строкой валюты. Перегрузите `+`, `-`, `==`, `!=`, реализуйте `IEquatable<Money>` и `GetHashCode`; при сложении валют разного вида бросайте исключение.",
            "Индексаторы: сделайте `RingBuffer<T>` с индексатором, поддерживающим `Index` и `Range`, и проверьте поведение с `buffer[^1]` и `buffer[0..3]`.",
            "Span: напишите разбор строки `a=1;b=22;c=333` на `ReadOnlySpan<char>`, возвращающий сумму значений. Убедитесь, что метод не вызывает `Split` и `Substring`.",
            "unsafe: реализуйте подсчёт байтов строки UTF-8 через `fixed` и `byte*` и сравните результат с `Encoding.UTF8.GetByteCount`.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            """
            HelloWorld -> hello_world
            Chunks of 7 into 2: [1, 2, 3, 4] [5, 6, 7]
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 4",
            "Сначала найдите позицию `;` через `IndexOf` в Span, затем внутри фрагмента — `=`, и передайте срез справа от `=` в `int.TryParse`. "
            "Такой цикл накапливает сумму без единой строковой аллокации."
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему extension-метод с тем же именем, что и экземплярный метод, не вызывается, если экземплярный метод существует?",
            "Что произойдёт, если перегрузить `==`, но не переопределить `Equals` в структуре?",
            "Почему `Span<T>` нельзя использовать в async-методе, а `Memory<T>` можно?",
            "Чем `in`-параметр отличается от `ref` и зачем он нужен для больших структур?",
            "Зачем нужен блок `fixed` и что произойдёт, если взять адрес массива без него?",
        ),
        heading("Ответы", 3),
        numbered(
            "Компилятор сначала ищет кандидатов среди экземплярных членов типа и находит подходящий метод; extension-методы рассматриваются только если собственных методов с такой сигнатурой нет.",
            "Поведение станет несогласованным: `Contains`, `List.IndexOf` и словари используют `Equals`, а написанный вручную код — перегруженный оператор. Кроме того, компилятор выдаст предупреждение CS0660 и CS0661 о согласованности.",
            "Span хранит ссылку на память и обязан жить в пределах кадра стека; после await продолжение может выполниться в другом потоке, и ссылка станет недействительной. Memory — обычная структура, её можно хранить в поле и передавать через await, а Span получать уже после продолжения.",
            "`in` даёт доступ только для чтения и позволяет не копировать большой аргумент; `ref` разрешает менять значение. Для маленьких структур компилятор всё равно может скопировать аргумент, поэтому `in` — это контракт API, а не гарантия отсутствия копии.",
            "`fixed` закрепляет управляемый объект, чтобы сборщик мусора не переместил его во время работы с указателем. Без закрепления объект может быть сдвинут при уплотнении кучи, и адрес станет недействительным — в лучшем случае испортятся данные, в худшем произойдёт нарушение доступа к памяти.",
        ),
        heading("Итоги"),
        bullets(
            "Extension-методы и блоки extension добавляют методы и свойства к типам без их изменения; экземплярный член всегда выигрывает у расширения.",
            "Операторы объявляются парой, а `==` обязан согласовываться с Equals и GetHashCode — иначе коллекции и оператор сравнивают по-разному.",
            "Неявные преобразования допускаются только без потерь; преобразование с риском потери данных объявляют явным.",
            "Индексаторы дают синтаксис квадратных скобок, включая многомерный; Index и Range добавляют срезы, а GetOffsetAndLength проверяет границы.",
            "ref передаёт и позволяет менять значение, out требует присваивания и удобен в паттерне Try, in даёт чтение без копирования больших структур.",
            "Span и ReadOnlySpan — ref struct для стека, Memory — структура для полей и async; срезы не копируют данные, а указывают на ту же память.",
            "stackalloc и Span позволяют обойтись без аллокаций в куче в пределах нескольких килобайт; для больших буферов берут ArrayPool.",
            "unsafe применяют для interop и сверхгорячего кода; адрес управляемого объекта берут только внутри fixed.",
        ),
        heading("Что дальше"),
        text(
            "Эти возможности напрямую нужны следующему уроку — управлению памятью. Span, ref struct "
            "и ref-возвраты — тот же инструмент, что позволяет избегать давления на сборщик мусора, "
            "а понимание fixed и неуправляемой памяти поможет разобраться с финализаторами, пулами буферов "
            "и работой с неуправляемыми ресурсами. Кроме того, вы увидите, как правило о жизни объектов в памяти "
            "объясняет часть ограничений, с которыми уже познакомились здесь."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Документация по операторам и перегрузке — learn.microsoft.com/dotnet/csharp/language-reference/operators",
            "Span<T> и Memory<T> — learn.microsoft.com/dotnet/standard/memory-and-spans",
            "ref struct и правила безопасной ссылочной семантики — learn.microsoft.com/dotnet/csharp/language-reference/builtin-types/ref-struct",
            "Небезопасный код, fixed и stackalloc — learn.microsoft.com/dotnet/csharp/language-reference/unsafe-code",
            "Index и Range — learn.microsoft.com/dotnet/csharp/language-reference/operators/index-range",
            "Книга Stephen Toub, «Span<T>: A New Value Type for Working with Arbitrary Memory» — разбор устройства Span из первых рук",
        ),
    ],
}
