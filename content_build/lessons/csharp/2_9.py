"""Урок 2.9 курса csharp: доступ к данным."""

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
    "topic_order": 9,
    "name": "2.9. Доступ к данным",
    "slug": "csharp-2-9-доступ-к-данным",
    "short_description": (
        "Практический набор инструментов для работы с данными в .NET: сериализация JSON "
        "через System.Text.Json, файлы и потоки, параметризованный SQL, ADO.NET, "
        "Dapper и Entity Framework Core."
    ),
    "topic_name": "Доступ к данным",
    "topic_description": (
        "Как приложение получает, хранит и отдаёт данные: сериализация JSON и настройка "
        "JsonSerializerOptions, работа с файлами и потоками, основы SQL и транзакций, "
        "низкоуровневый ADO.NET, микро-ORM Dapper и полноценный ORM Entity Framework Core "
        "с отслеживанием изменений, миграциями и типичными проблемами производительности."
    ),
    "learning_objectives": [
        "Сериализовать и десериализовать объекты в JSON через System.Text.Json с настройками именования и перечислений",
        "Читать и записывать файлы через File API, FileStream, StreamReader и потоки с буфером",
        "Писать SQL-запросы с фильтрацией и группировкой и понимать роль индексов и транзакций",
        "Работать с ADO.NET напрямую: SqlConnection, SqlCommand, SqlDataReader и параметры вместо конкатенации строк",
        "Использовать Dapper для коротких запросов и Entity Framework Core с LINQ, Include и AsNoTracking",
        "Распознавать узкие места: N+1 запросы, SQL-инъекции и чтение больших файлов целиком",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "csharp",
        "json",
        "потоки",
        "sql",
        "ado.net",
        "entity framework",
    ],
    "starter_code": code(
        r"""
        using System.Text.Json;

        record Product(int Id, string Title, decimal Price);

        var products = new List<Product>
        {
            new(1, "Клавиатура", 4500m),
            new(2, "Мышь", 2100m),
            new(3, "Монитор", 27900m),
        };

        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = true,
        };

        string json = JsonSerializer.Serialize(products, options);
        Console.WriteLine(json);

        var restored = JsonSerializer.Deserialize<List<Product>>(json, options)!;
        Console.WriteLine($"Восстановлено записей: {restored.Count}");
        """
    ),
    "hints": [
        "Создавайте JsonSerializerOptions один раз и переиспользуйте: при каждом новом экземпляре кэш метаданных компилируется заново.",
        "Никогда не склеивайте SQL строками. Используйте параметры: WHERE Name = @Name, а значение передавайте отдельно.",
        "EF Core по умолчанию отслеживает изменения. Для чтения только на экран берите данные через AsNoTracking() — это дешевле по памяти.",
        "Проблема N+1: один запрос за списком и по запросу на каждую связанную сущность. Решается через Include, проекцию в DTO или AsSplitQuery.",
    ],
    "content": [
        text(
            "Любое реальное приложение рано или поздно упирается в данные: их нужно сохранить, "
            "передать по сети, прочитать из файла или достать из базы. В .NET для каждой из этих "
            "задач есть готовый инструмент, и на среднем уровне важно не просто вызвать нужный метод, "
            "а понимать, какую цену вы платите за удобство.\n\n"
            "Урок устроен как постепенное погружение: сначала сериализация JSON — самый частый способ "
            "передать объекты наружу, затем файлы и потоки, затем базы данных: минимальный SQL, "
            "ADO.NET, Dapper и Entity Framework Core.\n\n"
            "Примеры с JSON и потоками запускаются в обычном консольном проекте и выводят результат. "
            "Примеры с базами данных показывают реальные классы и вызовы, но требуют подключения к "
            "серверу. Главный акцент — на типичных ловушках, а не на синтаксисе."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "сериализовать и десериализовать объекты через `JsonSerializer` и `JsonSerializerOptions`;",
            "настраивать имена свойств, перечисления и пустые значения при записи JSON;",
            "читать и писать файлы через `File`, `FileStream`, `StreamReader` и буферы;",
            "писать базовый SQL: `SELECT`, `JOIN`, `GROUP BY`, индексы и транзакции;",
            "работать с ADO.NET и Dapper, передавая значения только через параметры;",
            "применять EF Core: `Include`, `AsNoTracking`, проекции и `AsSplitQuery`;",
            "распознавать N+1 запросы, SQL-инъекции и другие типичные ошибки.",
        ),
        heading("Сериализация JSON через System.Text.Json"),
        text(
            "JSON (JavaScript Object Notation) — текстовый формат обмена данными, где объект записывается "
            "как набор пар «ключ: значение», а массивы — квадратными скобками. В современном .NET "
            "встроенная библиотека `System.Text.Json` уже содержит всё нужное.\n\n"
            "Ключевые понятия — сериализация (объект в текст) и десериализация (текст в объект). "
            "По умолчанию имена свойств в JSON совпадают с именами членов типа, а вложенные объекты "
            "обходятся рекурсивно. Для записей (`record`) сериализатор использует их публичные свойства.\n\n"
            "Метод `Deserialize<T>` возвращает `T?` и может вернуть `null`, например если на вход "
            "пришла строка `null`. Поэтому после вызова ставят оператор `!` только когда в данных "
            "уверены, либо проверяют результат явно."
        ),
        example(
            "csharp",
            """
            using System.Text.Json;

            record User(int Id, string Name, string Email);

            var user = new User(1, "Alice", "alice@example.com");

            string json = JsonSerializer.Serialize(user);
            Console.WriteLine(json);

            var restored = JsonSerializer.Deserialize<User>(json)!;
            Console.WriteLine($"{restored.Id}: {restored.Name} <{restored.Email}>");
            """,
        ),
        text(
            "Вывод: `{\"Id\":1,\"Name\":\"Alice\",\"Email\":\"alice@example.com\"}` и затем "
            "`1: Alice <alice@example.com>`. Обратите внимание: пробелов в JSON нет, потому что "
            "по умолчанию `WriteIndented` выключен — это экономит байты при передаче по сети."
        ),
        heading("Настройка JsonSerializerOptions"),
        text(
            "Почти всегда настройки сериализации отличаются от значений по умолчанию. Самые нужные "
            "параметры — политика именования свойств, форматирование и поведение для `null`-значений.\n\n"
            "`PropertyNamingPolicy = JsonNamingPolicy.CamelCase` переводит `UserName` в `userName`, что "
            "принято в JavaScript-клиентах и большинстве API. `WriteIndented` включает читаемый вывод "
            "с отступами для логов и файлов конфигурации. `DefaultIgnoreCondition = WhenWritingNull` "
            "не пишет свойства с `null`, уменьшая размер документов.\n\n"
            "Перечисления по умолчанию пишутся числами; конвертер `JsonStringEnumConverter` сохранит "
            "их строками, что упрощает чтение данных и защищает от путаницы при изменении порядка "
            "значений в `enum`."
        ),
        example(
            "csharp",
            """
            using System.Text.Json;
            using System.Text.Json.Serialization;

            enum Status { New, Paid, Shipped }

            record Order(int Id, Status Status, string? Comment);

            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                WriteIndented = true,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
                Converters = { new JsonStringEnumConverter() },
            };

            var order = new Order(10, Status.Paid, null);
            Console.WriteLine(JsonSerializer.Serialize(order, options));
            """,
        ),
        text(
            "Вывод (с отступами):\n\n"
            "```\n"
            "{\n"
            "  \"id\": 10,\n"
            "  \"status\": \"Paid\"\n"
            "}\n"
            "```\n\n"
            "Свойство `comment` исчезло полностью, а `status` стало строкой. Обратная десериализация "
            "с теми же `options` восстановит запись без потерь."
        ),
        callout(
            "warning",
            "Не создавайте options на каждый вызов",
            "Новый `JsonSerializerOptions` на каждый вызов теряет кеш метаданных. Держите один статический экземпляр на приложение."
        ),
        text(
            "Сериализацию можно генерировать на этапе компиляции (source generation). "
            "Атрибут `JsonSerializable` в наследнике `JsonSerializerContext` заставляет компилятор "
            "сгенерировать код чтения и записи без рефлексии. Это важно для Native AOT и сервисов, "
            "где задержка сериализации критична:\n\n"
            "```csharp\n"
            "[JsonSerializable(typeof(User))]\n"
            "public partial class AppJsonContext : JsonSerializerContext { }\n\n"
            "string json = JsonSerializer.Serialize(user, AppJsonContext.Default.User);\n"
            "```\n\n"
            "Для полиморфных иерархий в .NET 7+ есть атрибуты `JsonPolymorphic` и `JsonDerivedType`: "
            "они добавляют в JSON служебное свойство `$type` для восстановления конкретного подкласса."
        ),
        heading("Файлы и потоки"),
        text(
            "Статические методы `File` короткие, но загружают "
            "содержимое целиком: `ReadAllText` возвращает строку, `ReadAllBytes` — массив байтов. Для "
            "небольших конфигураций и логов этого достаточно.\n\n"
            "Когда файл не помещается в память, работают с потоками (stream). Поток — абстракция над "
            "источником байтов: он не хранит данные, а читает их порциями. `FileStream` связан с файлом, "
            "`MemoryStream` хранит данные в памяти, а `StreamReader` и `StreamWriter` преобразуют байты "
            "в текст и обратно.\n\n"
            "Метод `ReadAsync` возвращает число реально прочитанных байтов и `0`, когда файл закончился; "
            "именно это условие завершает цикл. Поток может вернуть меньше байтов, чем размер буфера, — "
            "это не конец файла. Поэтому обрабатывается только срез `buffer.AsSpan(0, bytesRead)`."
        ),
        example(
            "csharp",
            """
            var path = Path.Combine(Path.GetTempPath(), "kernify-demo.txt");

            File.WriteAllText(path, "первая строка\\nвторая строка\\nтретья строка");

            foreach (var line in File.ReadLines(path))
            {
                Console.WriteLine($"[{line.Length}] {line}");
            }

            var info = new FileInfo(path);
            Console.WriteLine($"Размер файла: {info.Length} байт");
            Console.WriteLine($"Существует: {File.Exists(path)}");
            """,
        ),
        text(
            "Вывод:\n\n"
            "```\n"
            "[13] первая строка\n"
            "[13] вторая строка\n"
            "[14] третья строка\n"
            "Размер файла: 77 байт\n"
            "Существует: True\n"
            "```\n\n"
            "Обратите внимание, что `File.ReadLines` возвращает перечисление и читает файл построчно по "
            "мере обхода, в отличие от `File.ReadAllLines`, который сразу создаёт массив всех строк. "
            "Размер в байтах больше суммы символов, потому что кириллица в UTF-8 занимает по два байта."
        ),
        text(
            "Для больших файлов используется буфер фиксированного размера. Такой цикл расходует "
            "мегабайт памяти независимо от размера файла:"
        ),
        example(
            "csharp",
            """
            var path = Path.Combine(Path.GetTempPath(), "kernify-big.bin");
            File.WriteAllBytes(path, Enumerable.Range(0, 100_000).Select(i => (byte)i).ToArray());

            long total = 0;
            var buffer = new byte[8192];

            await using var fs = new FileStream(
                path, FileMode.Open, FileAccess.Read, FileShare.Read, bufferSize: 4096);

            int bytesRead;
            while ((bytesRead = await fs.ReadAsync(buffer)) > 0)
            {
                total += bytesRead;
            }

            Console.WriteLine($"Прочитано: {total} байт");
            """,
        ),
        text(
            "Вывод: `Прочитано: 100000 байт`. Модификатор `await using` гарантирует, что поток будет "
            "закрыт даже при исключении. `bufferSize` задаёт внутренний буфер потока, а переменная "
            "`buffer` — размер порции за одно чтение. Для копирования целых потоков есть `CopyToAsync`:\n\n"
            "```csharp\n"
            "await using var source = File.OpenRead(\"from.bin\");\n"
            "await using var destination = File.Create(\"to.bin\");\n"
            "await source.CopyToAsync(destination, bufferSize: 81920);\n"
            "```\n\n"
            "Для текста удобнее `StreamReader`, который сам заботится о кодировке и переводах строк. "
            "А `FileSystemWatcher` позволяет отслеживать изменения в каталоге и перезагружать "
            "конфигурацию без перезапуска приложения."
        ),
        heading("Основы SQL"),
        text(
            "Библиотеки отправляют на сервер SQL. "
            "SQL (Structured Query Language) — язык запросов к реляционной базе данных. Данные хранятся "
            "в таблицах: строки — записи, столбцы — поля. Связи выражаются через ключи: первичный ключ "
            "(primary key) идентифицирует запись, внешний ключ (foreign key) ссылается на другую таблицу.\n\n"
            "`SELECT` описывает, какие столбцы вернуть, `FROM` — из каких таблиц, `JOIN` — как их "
            "соединить, `WHERE` — какие строки отобрать, `GROUP BY` и `HAVING` — как сгруппировать, "
            "`ORDER BY` с `OFFSET ... FETCH NEXT` — как отсортировать и выдать постранично.\n\n"
            "`INSERT`, `UPDATE` и `DELETE` изменяют данные. Изменения нескольких таблиц группируются в "
            "транзакцию: она применяется целиком через `COMMIT` или отменяется через `ROLLBACK`. "
            "Пример — перевод между счетами: списание и зачисление неделимы."
        ),
        example(
            "sql",
            """
            SELECT u.Id, u.Name, COUNT(o.Id) AS OrderCount
            FROM Users u
            LEFT JOIN Orders o ON u.Id = o.UserId
            WHERE u.IsActive = 1
            GROUP BY u.Id, u.Name
            HAVING COUNT(o.Id) > 0
            ORDER BY u.Name
            OFFSET 0 ROWS FETCH NEXT 20 ROWS ONLY;

            INSERT INTO Users (Name, Email, CreatedAt)
            VALUES ('Bob', 'bob@test.com', GETUTCDATE());

            BEGIN TRANSACTION;
            UPDATE Accounts SET Balance = Balance - 100 WHERE Id = 1;
            UPDATE Accounts SET Balance = Balance + 100 WHERE Id = 2;
            COMMIT;
            """,
        ),
        text(
            "Запрос выше возвращает активных пользователей с числом заказов. `LEFT JOIN` сохраняет "
            "пользователей даже без заказов, а `HAVING` отсекает тех, у кого заказов ноль. В `GROUP BY` "
            "входят все столбцы, не входящие в агрегатную функцию.\n\n"
            "Индекс (index) — структура, ускоряющая поиск по столбцу, как алфавитный указатель в книге. "
            "Без индекса база просматривает всю таблицу. Но каждый индекс замедляет `INSERT` и `UPDATE`, "
            "поэтому его создают на столбцы фильтрации и соединения: внешние ключи, `WHERE`-условия, "
            "поля сортировки.\n\n"
            "```sql\n"
            "CREATE INDEX IX_Users_Email ON Users(Email);\n"
            "CREATE INDEX IX_Orders_UserId_CreatedAt ON Orders(UserId, CreatedAt DESC);\n"
            "```\n\n"
            "Составной индекс эффективен для запросов, которые фильтруют по `UserId` и сортируются по "
            "`CreatedAt` — типичный сценарий «последние заказы пользователя»."
        ),
        heading("ADO.NET: доступ к базе напрямую"),
        text(
            "ADO.NET — низкоуровневый слой доступа к данным в .NET. Провайдер базы "
            "(`Microsoft.Data.SqlClient` для SQL Server, `Microsoft.Data.Sqlite` для SQLite) "
            "предоставляет `DbConnection`, `DbCommand` и `DbDataReader`. На этом слое построены "
            "Dapper и EF Core. Работа строится вокруг строки подключения (connection string): "
            "подключение открывается, выполняется команда, результат читается построчно. "
            "Подключения — дорогой ресурс, поэтому работает пул соединений: `Dispose` возвращает "
            "подключение в пул, а не закрывает физическое.\n\n"
            "`SqlDataReader` — потоковый курсор, забирающий строки по одной без загрузки всего "
            "результата в память. Для записи используется `ExecuteNonQueryAsync` с числом затронутых "
            "строк, для одного значения — `ExecuteScalarAsync`."
        ),
        example(
            "csharp",
            """
            using Microsoft.Data.SqlClient;

            const string connStr = "Server=localhost;Database=Shop;Trusted_Connection=true;TrustServerCertificate=true;";

            await using var conn = new SqlConnection(connStr);
            await conn.OpenAsync();

            const string sql = "SELECT Id, Name, Email FROM Users WHERE IsActive = @Active";

            await using var cmd = new SqlCommand(sql, conn);
            cmd.Parameters.AddWithValue("@Active", true);

            await using var reader = await cmd.ExecuteReaderAsync();
            while (await reader.ReadAsync())
            {
                int id = reader.GetInt32(0);
                string name = reader.GetString(1);
                string email = reader.IsDBNull(2) ? "" : reader.GetString(2);
                Console.WriteLine($"{id}: {name} <{email}>");
            }
            """,
        ),
        text(
            "Параметр `@Active` передаётся отдельно от текста запроса — это защита от SQL-инъекции. "
            "Перед чтением пустого столбца проверяется `IsDBNull`, иначе `GetString` бросит исключение. "
            "Примерный вывод: `1: Alice <alice@example.com>` и `2: Bob <>`. Для вставки параметры лучше "
            "задавать с явным типом и длиной, чем через `AddWithValue`:"
        ),
        example(
            "csharp",
            """
            var insert = new SqlCommand(
                "INSERT INTO Users (Name, Email) VALUES (@Name, @Email)", conn);

            insert.Parameters.Add("@Name", SqlDbType.NVarChar, 100).Value = "Alice";
            insert.Parameters.Add("@Email", SqlDbType.NVarChar, 200).Value = "alice@test.com";

            int affected = await insert.ExecuteNonQueryAsync();
            Console.WriteLine($"Добавлено строк: {affected}");
            """,
        ),
        callout(
            "danger",
            "SQL-инъекция",
            "Склейка строк вида $\"SELECT * FROM Users WHERE Name = '{name}'\" позволяет злоумышленнику подставить собственный SQL и прочитать или удалить данные. Всегда используйте параметры: \"SELECT * FROM Users WHERE Name = @Name\" и отдельно передавайте значение через Parameters."
        ),
        text(
            "Параметризованный запрос: база получает текст с заполнителями и значения отдельно, поэтому "
            "данные не интерпретируются как команды. Это и защита, и оптимизация — одинаковый текст "
            "запроса использует один закешированный план. Транзакция оформляется через "
            "`BeginTransactionAsync`, и все команды получают её объект:"
        ),
        example(
            "csharp",
            """
            await using var tx = (SqlTransaction)await conn.BeginTransactionAsync();
            try
            {
                var debit = new SqlCommand(
                    "UPDATE Accounts SET Balance = Balance - @Sum WHERE Id = @Id", conn, tx);
                debit.Parameters.AddWithValue("@Sum", 100m);
                debit.Parameters.AddWithValue("@Id", 1);
                await debit.ExecuteNonQueryAsync();

                var credit = new SqlCommand(
                    "UPDATE Accounts SET Balance = Balance + @Sum WHERE Id = @Id", conn, tx);
                credit.Parameters.AddWithValue("@Sum", 100m);
                credit.Parameters.AddWithValue("@Id", 2);
                await credit.ExecuteNonQueryAsync();

                await tx.CommitAsync();
            }
            catch
            {
                await tx.RollbackAsync();
                throw;
            }
            """,
        ),
        text(
            "Блок `try`/`catch` гарантирует, что при любой ошибке второй команды изменения будут "
            "отменены: без транзакции деньги бы исчезли. Перебрасывание исключения через `throw` после "
            "`Rollback` сообщает об ошибке вызывающему коду."
        ),
        heading("Dapper: микро-ORM"),
        text(
            "ADO.NET даёт полный контроль, но требует много служебного кода. Dapper — небольшая "
            "библиотека, которая убирает этот слой, оставаясь поверх чистого SQL. Это микро-ORM: "
            "она сопоставляет столбцы результата со свойствами класса по имени.\n\n"
            "`QueryAsync<T>` возвращает последовательность объектов, `QueryFirstOrDefaultAsync<T>` — "
            "первый объект или `null`, `ExecuteAsync` выполняет команду изменения. Параметры "
            "передаются анонимным объектом, свойства которого соответствуют заполнителям `@Name`. "
            "Для соединений таблиц есть multi-mapping с функцией сборки, связывающей строки "
            "двух таблиц в один объект."
        ),
        example(
            "csharp",
            """
            using Dapper;

            await using var conn = new SqlConnection(connStr);

            var activeUsers = await conn.QueryAsync<User>(
                "SELECT Id, Name, Email FROM Users WHERE IsActive = @Active",
                new { Active = true });

            var user = await conn.QueryFirstOrDefaultAsync<User>(
                "SELECT Id, Name, Email FROM Users WHERE Id = @Id",
                new { Id = 1 });

            int updated = await conn.ExecuteAsync(
                "UPDATE Users SET Email = @Email WHERE Id = @Id",
                new { Email = "new@test.com", Id = 1 });

            Console.WriteLine($"Активных: {activeUsers.Count()}, обновлено: {updated}");
            """,
        ),
        text(
            "Примерный вывод: `Активных: 2, обновлено: 1`. `QueryAsync` сам открывает подключение, если "
            "оно не открыто явно. Выбор между Dapper и EF Core — вопрос задачи: Dapper подходит для "
            "сложных отчётов и оптимизированных запросов, EF Core удобнее для обычных CRUD с объектной "
            "моделью и связями. Обе библиотеки часто используются в одном проекте."
        ),
        heading("Entity Framework Core"),
        text(
            "Entity Framework Core (EF Core) — полноценный ORM (Object-Relational Mapper). Он "
            "превращает LINQ-запросы в SQL, отслеживает изменения сущностей и обновляет схему базы "
            "через миграции. Основной класс настройки — `DbContext`, представляющий сессию работы с базой.\n\n"
            "Каждая таблица описывается свойством типа `DbSet<T>`. Связи настраиваются атрибутами или "
            "Fluent API в `OnModelCreating`; Fluent API предпочтительнее, потому что оставляет модели "
            "чистыми.\n\n"
            "Миграции (migrations) — механизм изменения схемы базы под изменение классов: "
            "`dotnet ef migrations add InitialCreate` создаёт миграцию, `dotnet ef database update` "
            "применяет её. Для продакшена генерируют SQL-скрипт через `dotnet ef migrations script`."
        ),
        example(
            "csharp",
            """
            public class AppDbContext : DbContext
            {
                public DbSet<User> Users => Set<User>();
                public DbSet<Order> Orders => Set<Order>();

                protected override void OnConfiguring(DbContextOptionsBuilder options)
                    => options.UseSqlServer(connStr);

                protected override void OnModelCreating(ModelBuilder model)
                {
                    model.Entity<User>(e =>
                    {
                        e.HasKey(u => u.Id);
                        e.Property(u => u.Email).HasMaxLength(200).IsRequired();
                        e.HasIndex(u => u.Email).IsUnique();
                        e.HasMany(u => u.Orders)
                         .WithOne(o => o.User)
                         .HasForeignKey(o => o.UserId);
                    });
                }
            }
            """,
        ),
        text(
            "Класс `User` содержит навигационное свойство `Orders`, а `Order` — обратное. Это отношение "
            "«один ко многим». `HasForeignKey` указывает столбец связи, а `HasIndex(...).IsUnique()` "
            "создаёт уникальный индекс на электронную почту. Запросы выполняются на сервере только при "
            "материализации — через `ToListAsync`, `FirstAsync` или `SaveChangesAsync`."
        ),
        example(
            "csharp",
            """
            using var ctx = new AppDbContext();

            var user = new User { Name = "Alice", Email = "alice@test.com" };
            ctx.Users.Add(user);
            await ctx.SaveChangesAsync();
            Console.WriteLine($"Новый идентификатор: {user.Id}");

            var found = await ctx.Users.FirstOrDefaultAsync(u => u.Email == "alice@test.com");

            var withOrders = await ctx.Users
                .Include(u => u.Orders)
                .AsNoTracking()
                .FirstOrDefaultAsync(u => u.Id == user.Id);

            Console.WriteLine($"{found?.Name}: заказов {withOrders?.Orders.Count ?? 0}");

            found!.Name = "Alice Updated";
            await ctx.SaveChangesAsync();

            ctx.Users.Remove(found);
            await ctx.SaveChangesAsync();
            """,
        ),
        text(
            "Примерный вывод: `Новый идентификатор: 1` и `Alice: заказов 0`. После `SaveChangesAsync` "
            "заполняется ключ, сгенерированный базой. Изменение `Name` не требует `Update`: EF Core "
            "сам сгенерирует `UPDATE` только для изменённых столбцов."
        ),
        heading("Отслеживание изменений и производительность"),
        text(
            "По умолчанию EF Core отслеживает все загруженные сущности: хранит их в `ChangeTracker` и "
            "сравнивает значения свойств. Это удобно, но стоит памяти и времени, поэтому для чтения "
            "отслеживание отключают через `AsNoTracking()`.\n\n"
            "Связанные данные по умолчанию не загружаются, и ленивая загрузка через прокси чаще всего "
            "приводит к проблеме N+1: один запрос получает сотню пользователей, а затем выполняется "
            "отдельный запрос заказов для каждого — сто один запрос вместо одного. Исправляется явной "
            "загрузкой через `Include`, проекцией в DTO со всеми полями одним `SELECT` или "
            "`AsSplitQuery`, когда `Include` раздувает декартово произведение строк."
        ),
        table(
            ["Задача", "Что использовать", "Почему"],
            [
                ["Прочитать справочник для отображения", "`AsNoTracking()`", "Не нужен `ChangeTracker` и сравнение значений"],
                ["Нужен список с вложенными данными", "`Include` или проекция в DTO", "Проекция возвращает только нужные столбцы"],
                ["Несколько коллекций на одной сущности", "`AsSplitQuery()`", "Позволяет избежать декартова произведения"],
                ["Один элемент по первичному ключу", "`FindAsync`", "Сначала ищет в уже загруженных сущностях"],
                ["Массовое обновление", "`ExecuteUpdateAsync` или Dapper", "Не загружает сущности в память"],
                ["Сложный аналитический запрос", "Dapper или `FromSqlRaw` с параметрами", "Легче контролировать SQL и план"],
            ],
        ),
        example(
            "csharp",
            """
            using var ctx = new AppDbContext();

            // Плохо: один запрос за пользователями и по запросу на каждого
            var users = await ctx.Users.ToListAsync();
            foreach (var u in users)
            {
                Console.WriteLine($"{u.Name}: {u.Orders.Count}");
            }

            // Хорошо: одна проекция в DTO со всеми нужными полями
            var rows = await ctx.Users
                .AsNoTracking()
                .Select(u => new { u.Name, Orders = u.Orders.Count })
                .ToListAsync();

            foreach (var row in rows)
            {
                Console.WriteLine($"{row.Name}: {row.Orders}");
            }
            """,
        ),
        text(
            "Во втором варианте EF Core сгенерирует один `SELECT` с подзапросом или `GROUP BY` и вернёт "
            "только имя и число заказов, не заполняя `ChangeTracker`. Для отчётов это оптимальный вариант.\n\n"
            "Для временных сбоев сети провайдеры предоставляют `EnableRetryOnFailure`:\n\n"
            "```csharp\n"
            "options.UseSqlServer(connStr, sql => sql.EnableRetryOnFailure(\n"
            "    maxRetryCount: 3,\n"
            "    maxRetryDelay: TimeSpan.FromSeconds(5),\n"
            "    errorNumbersToAdd: null));\n"
            "```\n\n"
            "Повторять стоит только преходящие ошибки: таймауты и обрыв соединения."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Склейка SQL строкой", "SQL-инъекция, планы запросов не кешируются", "Параметры `@Name` и отдельная передача значения"],
                ["Новый `JsonSerializerOptions` на каждый вызов", "Теряется кеш метаданных, сериализация медленнее в разы", "Один статический экземпляр на приложение"],
                ["`File.ReadAllText` для большого файла", "Файл целиком загружается в память, риск падения по памяти", "`StreamReader` или буферное чтение `ReadAsync`"],
                ["N+1 запросы в EF Core", "Сотни мелких запросов вместо одного", "`Include`, проекция в DTO, `AsSplitQuery`"],
                ["Отслеживание для отчёта", "Лишняя память и время на сравнение изменений", "`AsNoTracking()`"],
                ["`SaveChanges` в цикле", "Полный проход отслеживания на каждую запись", "`AddRange`, пакетная вставка, `ExecuteUpdateAsync`"],
                ["Забыли `IsDBNull` при чтении", "Исключение на первом `NULL` в столбце", "Проверять `IsDBNull` или `GetFieldValue<T?>`"],
                ["Нет индекса на внешний ключ", "Медленные соединения и каскадные проверки", "Индекс на столбцы `WHERE`, `JOIN`, `ORDER BY`"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания в отдельном консольном проекте. Для заданий с базой данных используйте "
            "SQLite: она не требует сервера и подходит для эксперимента с ADO.NET и EF Core."
        ),
        numbered(
            "JSON: создайте запись `Book(int Id, string Title, decimal Price)` и список из трёх книг. Сериализуйте его с `CamelCase` и `WriteIndented = true`, затем десериализуйте обратно и проверьте совпадение значений.",
            "Файлы: запишите список адресов, по одному на строку, через `StreamWriter`. Прочитайте файл построчно и выведите только строки, содержащие символ `@`.",
            "Потоки: создайте файл на 100 МБ, записывая блоки по 8192 байта, и посчитайте его размер через `FileInfo.Length` и через чтение буфером `ReadAsync`.",
            "ADO.NET: через `Microsoft.Data.Sqlite` создайте таблицу `Notes(Id, Text, CreatedAt)`, добавьте три записи параметризованным `INSERT` и выведите их через `SqlDataReader`.",
            "EF Core: настройте `DbContext` для `Author` и `Book` со связью «один ко многим» и выведите авторов с числом книг через проекцию в анонимный тип без `Include`.",
        ),
        text(
            "Ожидаемый результат первого задания:\n\n"
            "```\n"
            "[\n"
            "  {\n"
            "    \"id\": 1,\n"
            "    \"title\": \"C# в действии\",\n"
            "    \"price\": 3200\n"
            "  }\n"
            "]\n"
            "Книг после десериализации: 3\n"
            "Совпадает: True\n"
            "```"
        ),
        callout(
            "success",
            "Подсказка к заданию 5",
            "Проекция вида `Select(a => new { a.Name, Books = a.Books.Count() })` выполняется одним SQL-запросом с `GROUP BY` или коррелированным подзапросом — `Include` для подсчёта не нужен."
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем сериализация отличается от десериализации и почему `Deserialize<T>` может вернуть `null`?",
            "Зачем держать один экземпляр `JsonSerializerOptions` вместо создания нового на каждый вызов?",
            "Почему для большого файла нельзя использовать `File.ReadAllText` и что делать вместо этого?",
            "Что такое транзакция и какой сценарий без неё приведёт к потере данных?",
            "Почему параметризованный запрос защищает от SQL-инъекции?",
            "Что такое проблема N+1 и какими способами её устранить?",
            "Когда `AsNoTracking()` уместен, а когда — нет?",
        ),
        heading("Ответы", 3),
        numbered(
            "Сериализация превращает объект в текст, десериализация — наоборот. `Deserialize<T>` возвращает `T?`, потому что корректный JSON может содержать `null`.",
            "`JsonSerializerOptions` кеширует метаданные типов, поэтому новый экземпляр на каждый вызов означает повторное построение кеша и замедление.",
            "`ReadAllText` загружает файл целиком в одну строку, что может не поместиться в память. Вместо этого читают потоком: `FileStream` с буфером, `StreamReader` или `File.ReadLines`.",
            "Транзакция объединяет операции в неделимое действие с `COMMIT` или `ROLLBACK`. Без неё перевод может списать сумму и не зачислить её при сбое.",
            "Текст запроса и значения передаются базе отдельно, поэтому значение не разбирается как SQL: изменить можно значение, но не структуру команды.",
            "N+1 — один запрос за списком и по запросу на каждый элемент. Устраняется через `Include`, проекцию в DTO со счётчиком или `AsSplitQuery`.",
            "`AsNoTracking()` уместен для чтения без изменений: отчёты, справочники, ответы API. Он не подходит, когда сущность будет сохраняться через `SaveChangesAsync`.",
        ),
        heading("Итоги"),
        bullets(
            "JSON: `System.Text.Json` покрывает большинство задач; `JsonSerializerOptions` создаётся один раз и настраивает `CamelCase` и перечисления.",
            "Файлы: `File` удобен для небольших данных, потоки — для больших; `ReadAsync` возвращает `0` в конце, `await using` освобождает ресурсы.",
            "SQL: `SELECT` с `JOIN`, `GROUP BY` и пагинацией, изменение данных через `INSERT`/`UPDATE`/`DELETE`, несколько операций — в транзакции.",
            "ADO.NET: подключение, команда, параметры и построчное чтение через `SqlDataReader`; значения передаются только через параметры.",
            "Dapper: микро-ORM поверх чистого SQL, сопоставляет столбцы со свойствами и лаконичен для отчётов.",
            "EF Core: LINQ и `ChangeTracker`, миграции для схемы, `Include` для связей, `AsNoTracking` для чтения.",
            "Производительность: избегайте N+1, делайте проекции в DTO, не сохраняйте в цикле и индексируйте столбцы фильтрации.",
        ),
        heading("Что дальше"),
        text(
            "Вы научились получать и сохранять данные всеми основными способами, которые есть в .NET, "
            "и понимать цену каждого слоя. Следующий урок — «Разработка приложений» — объединит эти "
            "инструменты в архитектуру: конфигурация, внедрение зависимостей, логирование и слои. "
            "Оттуда вы перейдёте к итоговому проекту, где доступ к данным станет одним из слоёв."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "System.Text.Json — learn.microsoft.com/dotnet/standard/serialization/system-text-json",
            "File and stream I/O — learn.microsoft.com/dotnet/standard/io",
            "Entity Framework Core — learn.microsoft.com/ef/core",
            "Dapper — github.com/DapperLib/Dapper",
            "Мониторинг производительности SQL Server — learn.microsoft.com/sql/relational-databases/performance/performance-monitoring-and-tuning",
            "Книга «Entity Framework Core in Action» (Jon P Smith) — подробное руководство по EF Core на практике",
        ),
    ],
}
