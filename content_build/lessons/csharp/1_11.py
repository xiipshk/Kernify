"""Урок 1.11 курса C#: первый проект."""

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
    "program_order": 1,
    "topic_order": 11,
    "name": "1.11. Первый проект",
    "slug": "csharp-1-11-первый-проект",
    "short_description": (
        "Собираем полноценное консольное приложение «Менеджер задач» на C#: "
        "классы, перечисления, коллекции, исключения, LINQ, сохранение в JSON и простые тесты."
    ),
    "topic_name": "Первый проект",
    "topic_description": (
        "Итоговый проект курса — консольный менеджер задач, в котором соединяются все изученные темы. "
        "Разбиваем приложение на модели, сервис, хранилище и интерфейс, сохраняем данные в JSON, "
        "фильтруем их через LINQ и проверяем поведение собственными тестами."
    ),
    "learning_objectives": [
        "Создавать консольный проект командой `dotnet new console` и понимать роль файла проекта",
        "Проектировать классы-модели со свойствами, конструктором с валидацией и вычисляемыми свойствами",
        "Использовать перечисления (enum) для приоритета и категории задачи",
        "Разделять приложение на модели, сервис, хранилище и интерфейс, чтобы логика не зависела от консоли",
        "Сохранять и загружать коллекцию объектов в JSON через `System.Text.Json`",
        "Фильтровать данные через LINQ и писать простые тесты без сторонних библиотек",
    ],
    "estimated_minutes": 30,
    "xp_reward": 10,
    "difficulty": "beginner",
    "tags": [
        "csharp",
        "проект",
        "консоль",
        "json",
        "linq",
        "тесты",
    ],
    "starter_code": code(
        """
        var item = new TaskItem("Изучить LINQ", Priority.High);

        Console.WriteLine(item);
        item.Complete();
        Console.WriteLine(item);

        public enum Priority { Low = 1, Medium = 2, High = 3, Critical = 4 }

        public class TaskItem
        {
            public string Title { get; set; }
            public Priority Priority { get; set; }
            public bool IsCompleted { get; private set; }

            public TaskItem(string title, Priority priority = Priority.Medium)
            {
                if (string.IsNullOrWhiteSpace(title))
                {
                    throw new ArgumentException("Название задачи не может быть пустым", nameof(title));
                }

                Title = title.Trim();
                Priority = priority;
            }

            public void Complete()
            {
                if (IsCompleted)
                {
                    throw new InvalidOperationException("Задача уже завершена");
                }

                IsCompleted = true;
            }

            public override string ToString() =>
                $"{(IsCompleted ? "[x]" : "[ ]")} {Priority}: {Title}";
        }
        """
    ),
    "hints": [
        "Начинайте с модели: сначала опишите, из чего состоит задача, и только потом пишите меню. "
        "Классы моделей не должны печатать в консоль.",
        "Логику храните в сервисе, а не в обработчиках меню. Тогда её можно проверить тестами без клавиатуры.",
        "Для JSON достаточно `JsonSerializer.Serialize` и `JsonSerializer.Deserialize` из `System.Text.Json` "
        "— отдельный пакет в .NET 8 не нужен.",
        "Один файл на класс не обязателен для учебного проекта, но папки `Models`, `Services` и `Tests` "
        "сразу наводят порядок.",
    ],
    "content": [
        text(
            "Предыдущие уроки дали отдельные инструменты: типы, циклы, методы, классы, коллекции, исключения, "
            "файлы и LINQ. Главный вопрос новичка — как из них собирается работающая программа. Ответ даёт "
            "итоговый проект: консольное приложение «Менеджер задач». Оно добавляет задачи, показывает список, "
            "отмечает выполнение, удаляет записи, ищет по тексту, выводит статистику и сохраняет данные в файл.\n\n"
            "Важнее самих функций — структура. Опытный программист отличается не объёмом знания синтаксиса, "
            "а тем, как раскладывает код по слоям, каждый из которых можно понять и проверить отдельно. "
            "Материал рассчитан на C# 12 и .NET 8: нужны установленный SDK и терминал."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "создавать консольный проект командой `dotnet new console` и запускать его через `dotnet run`;",
            "проектировать классы-модели со свойствами, конструктором с проверкой данных и вычисляемыми свойствами;",
            "описывать настройки задачи через перечисления `Priority` и `TaskCategory`;",
            "делить приложение на модели, сервис, хранилище и интерфейс, чтобы логика не зависела от консоли;",
            "сохранять и загружать коллекцию задач в JSON через `System.Text.Json`;",
            "фильтровать и сортировать задачи через LINQ (`Where`, `OrderByDescending`, `Any`, `Max`);",
            "сообщать об ошибках бизнес-логики собственным исключением `TaskNotFoundException`;",
            "писать простые тесты без сторонних фреймворков и запускать их перед работой приложения.",
        ),
        heading("Что мы строим и зачем"),
        text(
            "Главная идея проекта — **разделение ответственности** (separation of concerns). Каждый класс "
            "отвечает за одну вещь и не знает подробностей соседей. В учебных примерах всё часто пишут "
            "в одном `Main`: и чтение с клавиатуры, и вычисления, и запись файла. Пока строк десять, это "
            "работает; когда двести — любое изменение превращается в поиск по всему файлу.\n\n"
            "В проекте четыре слоя, и связь идёт в одну сторону: интерфейс вызывает сервис, сервис — "
            "хранилище, модели не вызывают никого."
        ),
        table(
            ["Слой", "Папка", "Ответственность", "О C# и консоли"],
            [
                ["Модели", "Models/", "Данные задачи и правила их корректности", "Ничего не знают"],
                ["Исключения", "Exceptions/", "Собственные типы ошибок", "Ничего не знают"],
                ["Сервис", "Services/TaskService.cs", "Бизнес-логика: добавление, фильтры, статистика", "Не знают о консоли"],
                ["Хранилище", "Services/FileStorage.cs", "Чтение и запись JSON", "Не знают о консоли"],
                ["Интерфейс", "Services/ConsoleUI.cs", "Меню, ввод, вывод", "Знают обо всех"],
                ["Тесты", "Tests/", "Проверка сервиса без ручного ввода", "Своя мини-библиотека"],
            ],
        ),
        text(
            "Устройство даёт три выгоды. Логику можно протестировать без клавиатуры: тест вызывает сервис "
            "напрямую. Интерфейс можно заменить, не переписывая правила работы с задачами. И ошибки "
            "локализуются: если JSON сохраняется неправильно, смотрим в `FileStorage`."
        ),
        heading("Создание проекта"),
        text(
            "Проект создаётся командой интерфейса командной строки `dotnet` из состава SDK. "
            "`dotnet new console` создаёт папку с двумя файлами: `TasksApp.csproj` и `Program.cs`.\n\n"
            "`.csproj` — **файл проекта**: XML-описание с версией платформы "
            "(`<TargetFramework>net8.0</TargetFramework>`) и зависимостями. Все файлы `.cs` в папке и "
            "подпапках компилируются автоматически. `Program.cs` — точка входа, где начинается выполнение."
        ),
        example(
            "bash",
            """
            dotnet new console -n TasksApp
            cd TasksApp
            dotnet run
            """,
        ),
        text(
            "Вывод:\n"
            "```\n"
            "The template \"Console App\" was created successfully.\n"
            "\n"
            "Hello, World!\n"
            "```\n\n"
            "`dotnet run` собирает проект и сразу запускает полученную программу.\n\n"
            "Дальше создайте папки `Models`, `Services`, `Exceptions` и `Tests`. Классы можно разложить "
            "по отдельным файлам или оставить в `Program.cs`: компилятору всё равно, но раздельные файлы "
            "облегчают навигацию. Пространства имён повторят имена папок: `TasksApp.Models`."
        ),
        heading("Перечисления: приоритет и категория"),
        text(
            "Настройки задачи нельзя хранить строками: строку `\"High\"` легко опечатать как `\"Hihg\"`, и "
            "компилятор этого не заметит. Для фиксированного набора вариантов в C# есть **перечисление** "
            "(enum) — тип с заранее известными именованными значениями.\n\n"
            "Числовые значения по умолчанию начинаются с нуля. Для приоритета их задают явно, начиная с "
            "единицы: тогда они совпадают с номером пункта в меню, а ноль не выберется случайно."
        ),
        example(
            "csharp",
            """
            namespace TasksApp.Models;

            public enum TaskCategory
            {
                Personal,
                Work,
                Study,
                Health,
                Other
            }

            public enum Priority
            {
                Low = 1,
                Medium = 2,
                High = 3,
                Critical = 4
            }
            """,
        ),
        text(
            "`namespace` объявляет **пространство имён** — логическую группу типов. Классы одного "
            "пространства видны друг другу, а из другого требуют `using TasksApp.Models;`.\n\n"
            "Перечисление печатается словом: `Priority.High` выведет `High`, а не `3`. Обратное "
            "преобразование делает приведение `(Priority)3`, а проверку диапазона — `Enum.IsDefined`."
        ),
        example(
            "csharp",
            """
            Console.WriteLine(Priority.High);
            Console.WriteLine((int)Priority.High);

            int choice = 3;
            if (Enum.IsDefined(typeof(Priority), choice))
            {
                Priority priority = (Priority)choice;
                Console.WriteLine($"Выбрано значение: {priority}");
            }
            else
            {
                Console.WriteLine($"Нет приоритета с номером {choice}");
            }
            """,
        ),
        text(
            "Вывод:\n"
            "```\n"
            "High\n"
            "3\n"
            "Выбрано значение: High\n"
            "```\n\n"
            "Поэтому `Enum.IsDefined` вызывают перед приведением ввода пользователя: без проверки число `7` "
            "тихо превратилось бы в `Priority` с непонятным содержимым."
        ),
        heading("Модель задачи"),
        text(
            "**Модель** — класс, который описывает данные. `TaskItem` хранит номер, название, описание, "
            "приоритет, категорию, дату создания и дату завершения. Для полей используется "
            "**автосвойство** — сокращённая форма свойства со скрытым полем.\n\n"
            "Модификатор доступа в автосвойстве решает, кто может менять значение: `{ get; set; }` — все, "
            "`{ get; init; }` — только при создании объекта, `{ get; private set; }` — только сам класс. "
            "Так закрывают `CompletedAt`: иначе легко получить задачу, где флаг `IsCompleted` не совпадает "
            "с датой."
        ),
        example(
            "csharp",
            """
            namespace TasksApp.Models;

            public class TaskItem
            {
                public int Id { get; init; }
                public string Title { get; set; } = string.Empty;
                public string Description { get; set; } = string.Empty;
                public bool IsCompleted { get; set; }
                public Priority Priority { get; set; }
                public TaskCategory Category { get; set; }
                public DateTime CreatedAt { get; init; }
                public DateTime? CompletedAt { get; private set; }
                public DateTime? DueDate { get; set; }
            }
            """,
        ),
        text(
            "Знак вопроса после типа (`DateTime?`) делает его **nullable-значением**: переменная хранит либо "
            "дату, либо `null`, то есть «не задано». Обычная `DateTime` пустой быть не может.\n\n"
            "Инициализатор `= string.Empty` защищает от `null`: в .NET 8 включена поддержка nullable-ссылок, "
            "и компилятор предупредит о возможном `null`. Само значение `null` в `Title` привело бы к "
            "исключению на первом же вызове вроде `ToUpper()`."
        ),
        heading("Конструктор с валидацией"),
        text(
            "Правило «название не может быть пустым» проверяется один раз и в одном месте — в конструкторе "
            "модели: объект либо создаётся корректным, либо не создаётся вовсе. Проверять его в каждом "
            "пункте меню опасно: какой-то пункт забудут.\n\n"
            "**Конструктор** вызывается при `new` и принимает начальные значения. Значения по умолчанию "
            "(`Priority priority = Priority.Medium`) позволяют вызвать `new TaskItem(\"Купить хлеб\")` без "
            "второй части. **Валидация** выполняется до присвоения полей: некорректный объект не должен "
            "появиться в памяти."
        ),
        example(
            "csharp",
            """
            using System.Text.Json.Serialization;

            namespace TasksApp.Models;

            public class TaskItem
            {
                public int Id { get; set; }
                public string Title { get; set; } = string.Empty;
                public string Description { get; set; } = string.Empty;
                public bool IsCompleted { get; private set; }
                public Priority Priority { get; set; }
                public TaskCategory Category { get; set; }
                public DateTime CreatedAt { get; init; } = DateTime.Now;
                [JsonIgnore]
                public DateTime? CompletedAt { get; private set; }
                public DateTime? DueDate { get; set; }

                public bool IsOverdue =>
                    !IsCompleted && DueDate.HasValue && DueDate.Value < DateTime.Now;

                public TaskItem() { }

                public TaskItem(string title, Priority priority = Priority.Medium,
                    TaskCategory category = TaskCategory.Other)
                {
                    if (string.IsNullOrWhiteSpace(title))
                    {
                        throw new ArgumentException("Название задачи не может быть пустым", nameof(title));
                    }

                    Title = title.Trim();
                    Priority = priority;
                    Category = category;
                    CreatedAt = DateTime.Now;
                }

                public void Complete()
                {
                    if (IsCompleted)
                    {
                        throw new InvalidOperationException("Задача уже завершена");
                    }

                    IsCompleted = true;
                    CompletedAt = DateTime.Now;
                }

                public void Reopen()
                {
                    if (!IsCompleted)
                    {
                        throw new InvalidOperationException("Задача уже активна");
                    }

                    IsCompleted = false;
                    CompletedAt = null;
                }

                public override string ToString()
                {
                    string status = IsCompleted ? "[x]" : "[ ]";
                    string due = DueDate.HasValue ? $" (до: {DueDate:dd.MM.yyyy})" : "";
                    string overdue = IsOverdue ? " [просрочено]" : "";
                    return $"{status} {Priority}: {Title}{due}{overdue}";
                }
            }
            """,
        ),
        text(
            "Два места выглядят неочевидно. Первое — формат `{DueDate:dd.MM.yyyy}`: двоеточие вводит "
            "**строку формата**, где `dd` — день, `MM` — месяц, `yyyy` — год. Для nullable-значения она "
            "работает без `DueDate.Value`.\n\n"
            "Второе — пустой конструктор `public TaskItem() { }`. Он нужен десериализатору JSON: объект "
            "создаётся без аргументов, затем свойства заполняются из документа. Без него загрузка упадёт."
        ),
        heading("Вычисляемое свойство и метод ToString"),
        text(
            "**Вычисляемое свойство** — свойство без хранимого значения: только `get` с выражением после "
            "`=>`. Оно не занимает память и пересчитывается при обращении. `IsOverdue` возвращает `true`, "
            "если задача не завершена, срок задан и уже прошёл.\n\n"
            "`ToString()` есть у любого объекта и неявно вызывается при выводе в консоль. "
            "Переопределение (`override`) задаёт единый формат печати задачи."
        ),
        example(
            "csharp",
            """
            var task = new TaskItem("Изучить LINQ", Priority.High, TaskCategory.Study)
            {
                DueDate = DateTime.Today.AddDays(-1)
            };

            Console.WriteLine(task);
            Console.WriteLine($"Просрочена: {task.IsOverdue}");

            task.Complete();
            Console.WriteLine(task);
            Console.WriteLine($"Просрочена: {task.IsOverdue}");

            try
            {
                task.Complete();
            }
            catch (InvalidOperationException ex)
            {
                Console.WriteLine($"Ошибка: {ex.Message}");
            }
            """,
        ),
        text(
            "Вывод:\n"
            "```\n"
            "[ ] High: Изучить LINQ (до: 14.11.2026) [просрочено]\n"
            "Просрочена: True\n"
            "[x] High: Изучить LINQ (до: 14.11.2026)\n"
            "Просрочена: False\n"
            "Ошибка: Задача уже завершена\n"
            "```\n\n"
            "После завершения пометка о просрочке исчезла: закрытая задача не бывает просроченной. Срок "
            "задан через `DateTime.Today.AddDays(-1)`, поэтому дата в выводе зависит от дня запуска. "
            "Повторный `Complete` выбрасывает `InvalidOperationException` — сигнал о нарушении порядка "
            "действий, а не об ошибке ввода."
        ),
        callout(
            "info",
            "Методы вместо открытых свойств",
            "Флаг `IsCompleted` лучше объявлять с `private set`, а состояние менять методами `Complete` и "
            "`Reopen`. Тогда время завершения и флаг всегда согласованы. В коде выше флаг `IsCompleted` "
            "пока открыт — это упрощение, которое стоит исправить на практике."
        ),
        heading("Собственное исключение"),
        text(
            "Когда запрашивают задачу с несуществующим номером, вызывающему коду полезно знать, какой "
            "именно номер не найден. Для этого объявляют свой класс исключения — наследник `Exception`.\n\n"
            "Конструктор производного класса вызывает конструктор базы через `: base(сообщение)`, и так "
            "заполняется `Message`. Свойство `TaskId` хранит номер, чтобы интерфейс показал его, не разбирая "
            "текст ошибки."
        ),
        example(
            "csharp",
            """
            namespace TasksApp.Exceptions;

            public class TaskNotFoundException : Exception
            {
                public int TaskId { get; }

                public TaskNotFoundException(int taskId)
                    : base($"Задача с ID {taskId} не найдена")
                {
                    TaskId = taskId;
                }
            }
            """,
        ),
        text(
            "`KeyNotFoundException` не подошёл бы: он говорит о словаре, а не о задаче. Тип исключения — "
            "часть контракта метода: `catch (TaskNotFoundException)` поймает только ошибку поиска задачи и "
            "не перехватит ошибку файла."
        ),
        heading("Хранилище: JSON-файл"),
        text(
            "**Сериализация** — превращение объекта в текст для хранения, **десериализация** — обратное "
            "преобразование. Формат JSON (JavaScript Object Notation) удобен для людей, а `System.Text.Json` "
            "входит в платформу. Коллекция задач превращается в JSON-массив.\n\n"
            "`JsonSerializerOptions` задаёт правила: `WriteIndented` добавляет отступы, "
            "`UnsafeRelaxedJsonEscaping` сохраняет кириллицу как есть, а не как `\\u0418\\u0437`. "
            "Для локального файла это безопасно."
        ),
        example(
            "csharp",
            """
            using System.Text.Json;
            using TasksApp.Models;

            namespace TasksApp.Services;

            public static class FileStorage
            {
                private static readonly JsonSerializerOptions Options = new()
                {
                    WriteIndented = true,
                    Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
                };

                public static void Save(string filePath, List<TaskItem> tasks)
                {
                    try
                    {
                        string json = JsonSerializer.Serialize(tasks, Options);
                        File.WriteAllText(filePath, json);
                    }
                    catch (UnauthorizedAccessException ex)
                    {
                        throw new IOException($"Нет прав на запись в файл: {filePath}", ex);
                    }
                    catch (Exception ex) when (ex is not IOException)
                    {
                        throw new IOException($"Ошибка сохранения: {ex.Message}", ex);
                    }
                }

                public static List<TaskItem> Load(string filePath)
                {
                    if (!File.Exists(filePath))
                    {
                        return new List<TaskItem>();
                    }

                    try
                    {
                        string json = File.ReadAllText(filePath);
                        return JsonSerializer.Deserialize<List<TaskItem>>(json, Options)
                               ?? new List<TaskItem>();
                    }
                    catch (JsonException ex)
                    {
                        throw new IOException($"Файл повреждён или неверный формат: {ex.Message}", ex);
                    }
                    catch (Exception ex) when (ex is not IOException)
                    {
                        throw new IOException($"Ошибка загрузки: {ex.Message}", ex);
                    }
                }
            }
            """,
        ),
        text(
            "`static class` не позволяет создать объект и годится для набора методов с параметрами: "
            "хранилищу не нужно состояние, путь передаётся в каждый вызов.\n\n"
            "Цепочка `catch` идёт от конкретного к общему. Фильтр `when (ex is not IOException)` не даёт "
            "обернуть исключение ввода-вывода повторно. Любая ошибка превращается в `IOException` с "
            "понятным текстом, а исходная причина остаётся в `InnerException`."
        ),
        example(
            "text",
            """
            [
              {
                "Id": 2,
                "Title": "Изучить LINQ",
                "Description": "Пройти урок 10",
                "IsCompleted": false,
                "Priority": 3,
                "Category": 2,
                "CreatedAt": "2026-11-14T09:15:42.1187231+03:00",
                "DueDate": "2026-12-15T00:00:00"
              }
            ]
            """,
        ),
        text(
            "Обратите внимание: перечисления попали в файл числами, а `DueDate` со значением `null` "
            "пропущен. Даты записаны в формате ISO 8601 и читаются любой системой, а `[JsonIgnore]` "
            "на `CompletedAt` не дал записать его с закрытым `set`."
        ),
        callout(
            "warning",
            "Не храните данные рядом с программой",
            "`dotnet run` запускает программу из папки проекта, и `tasks.json` ляжет туда. После сборки "
            "в `bin/Debug/net8.0` текущий каталог другой, и данные будто «теряются». Для настоящего "
            "приложения путь получают через "
            "`Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData)`."
        ),
        heading("Сервис: бизнес-логика"),
        text(
            "**Сервис** — класс с правилами предметной области. `TaskService` хранит задачи в `List<TaskItem>`, "
            "выдаёт им номера и вызывает хранилище после каждого изменения. «Сервис» здесь — роль в "
            "архитектуре, а не особенность языка: это обычный класс.\n\n"
            "Поле `_nextId` помнит следующий свободный номер, подчёркивание в начале имени обозначает "
            "приватное поле. `readonly` запрещает заменить список другим, но не мешает добавлять и "
            "удалять элементы."
        ),
        example(
            "csharp",
            """
            using TasksApp.Models;
            using TasksApp.Exceptions;

            namespace TasksApp.Services;

            public class TaskService
            {
                private readonly List<TaskItem> _tasks = new();
                private readonly string _dataFile;
                private int _nextId = 1;

                public TaskService(string dataFile = "tasks.json")
                {
                    _dataFile = dataFile;
                    LoadTasks();
                }

                public TaskItem CreateTask(string title, Priority priority = Priority.Medium,
                    TaskCategory category = TaskCategory.Other, DateTime? dueDate = null)
                {
                    var task = new TaskItem(title, priority, category)
                    {
                        Id = _nextId++,
                        DueDate = dueDate
                    };
                    _tasks.Add(task);
                    SaveTasks();
                    return task;
                }

                public TaskItem GetTask(int id)
                {
                    var task = _tasks.FirstOrDefault(t => t.Id == id);
                    if (task is null)
                    {
                        throw new TaskNotFoundException(id);
                    }
                    return task;
                }

                public void CompleteTask(int id)
                {
                    GetTask(id).Complete();
                    SaveTasks();
                }

                public void DeleteTask(int id)
                {
                    _tasks.Remove(GetTask(id));
                    SaveTasks();
                }

                public IEnumerable<TaskItem> GetTasks(bool? completed = null)
                {
                    var query = _tasks.AsEnumerable();
                    if (completed.HasValue)
                    {
                        query = query.Where(t => t.IsCompleted == completed.Value);
                    }
                    return query.OrderByDescending(t => t.Priority)
                                .ThenBy(t => t.DueDate ?? DateTime.MaxValue);
                }

                public IEnumerable<TaskItem> Search(string query)
                {
                    if (string.IsNullOrWhiteSpace(query))
                    {
                        return Enumerable.Empty<TaskItem>();
                    }

                    string lower = query.Trim().ToLower();
                    return _tasks.Where(t =>
                        t.Title.ToLower().Contains(lower) ||
                        t.Description.ToLower().Contains(lower));
                }

                public (int Total, int Completed, int Pending, int Overdue) GetStatistics()
                {
                    int total = _tasks.Count;
                    int completed = _tasks.Count(t => t.IsCompleted);
                    return (total, completed, total - completed, _tasks.Count(t => t.IsOverdue));
                }

                private void SaveTasks() => FileStorage.Save(_dataFile, _tasks);

                private void LoadTasks()
                {
                    _tasks.Clear();
                    _tasks.AddRange(FileStorage.Load(_dataFile));
                    _nextId = _tasks.Count > 0 ? _tasks.Max(t => t.Id) + 1 : 1;
                }
            }
            """,
        ),
        text(
            "Три решения заслуживают внимания. Первое: `_nextId = _tasks.Max(t => t.Id) + 1`. Если всегда "
            "начинать с единицы, после перезапуска новая задача получит занятый номер, и `GetTask` вернёт "
            "чужую запись.\n\n"
            "Второе: в `if (completed.HasValue)` проверяется наличие значения, а не его истинность, поэтому "
            "фильтр работает и при `false`. А `?? DateTime.MaxValue` в `ThenBy` отправляет задачи без срока "
            "в конец списка.\n\n"
            "Третье: `IEnumerable<TaskItem>` — **отложенный запрос**, он вычисляется при переборе. Если "
            "результатом нужно пользоваться дважды, сначала вызовите `.ToList()`."
        ),
        heading("LINQ в проекте"),
        text(
            "Бизнес-логика почти целиком построена на **LINQ** (Language Integrated Query) — встроенном "
            "языке запросов к коллекциям. Вместо ручного цикла пишется описание нужного результата, а "
            "перебор выполняет библиотека.\n\n"
            "Хватает пяти методов: `Where` — отбор, `OrderByDescending` и `ThenBy` — сортировка, `Count` — "
            "подсчёт, `Any` — проверка непустоты. Все они принимают **лямбда-выражение**: функцию без "
            "имени вида `t => t.IsCompleted`. Для отбора справа от `=>` должно быть значение `bool`."
        ),
        example(
            "csharp",
            """
            var tasks = new List<TaskItem>
            {
                new("Сдать отчёт", Priority.Critical, TaskCategory.Work),
                new("Купить молоко", Priority.Low, TaskCategory.Personal),
                new("Прочитать главу", Priority.High, TaskCategory.Study),
            };
            tasks[0].Complete();

            var active = tasks.Where(t => !t.IsCompleted)
                              .OrderByDescending(t => t.Priority)
                              .ToList();
            Console.WriteLine($"Активных задач: {active.Count}");
            foreach (var task in active)
            {
                Console.WriteLine(task);
            }

            var study = tasks.Count(t => t.Category == TaskCategory.Study);
            Console.WriteLine($"Учебных задач: {study}");
            Console.WriteLine($"Есть выполненные: {tasks.Any(t => t.IsCompleted)}");
            """,
        ),
        text(
            "Вывод:\n"
            "```\n"
            "Активных задач: 2\n"
            "[ ] High: Прочитать главу\n"
            "[ ] Low: Купить молоко\n"
            "Учебных задач: 1\n"
            "Есть выполненные: True\n"
            "```\n\n"
            "Запрос выдал задачи в порядке убывания приоритета, а завершённая «Сдать отчёт» не попала. "
            "Запись `new(...)` — целевое выражение `new`: тип известен по `List<TaskItem>`, поэтому его "
            "не повторяют (C# 9 и новее)."
        ),
        heading("Интерфейс: меню в консоли"),
        text(
            "Класс `ConsoleUI` отвечает только за диалог: подсказки, чтение строк, разбор команд и вывод. "
            "Обработка данных делегируется сервису, а зависимость `TaskService` передаётся через "
            "конструктор — это простейшая форма **внедрения зависимости** (dependency injection): "
            "в тестах вместо боевого файла подставляют временный путь.\n\n"
            "Сердце интерфейса — цикл с `switch`, который сравнивает строку команды с вариантами. "
            "`Trim()` убирает пробелы, `ToLower()` снимает зависимость от регистра, а `q` завершает "
            "цикл через `return`."
        ),
        example(
            "csharp",
            """
            using TasksApp.Models;
            using TasksApp.Exceptions;

            namespace TasksApp.Services;

            public class ConsoleUI
            {
                private readonly TaskService _service;

                public ConsoleUI(TaskService service) => _service = service;

                public void Run()
                {
                    Console.WriteLine("=== МЕНЕДЖЕР ЗАДАЧ ===");
                    Console.WriteLine("h - справка, a - добавить, l - список, c - завершить");
                    Console.WriteLine("d - удалить, s - статистика, f - поиск, q - выход");

                    while (true)
                    {
                        Console.Write("\\n> ");
                        string? input = Console.ReadLine()?.Trim().ToLower();

                        if (string.IsNullOrEmpty(input))
                        {
                            continue;
                        }

                        try
                        {
                            switch (input)
                            {
                                case "h": PrintHelp(); break;
                                case "a": AddTask(); break;
                                case "l": ListTasks(); break;
                                case "c": CompleteTask(); break;
                                case "d": DeleteTask(); break;
                                case "s": ShowStats(); break;
                                case "f": FindTasks(); break;
                                case "q": return;
                                default:
                                    Console.WriteLine("Неизвестная команда. Введите 'h' для справки.");
                                    break;
                            }
                        }
                        catch (TaskNotFoundException ex)
                        {
                            Console.WriteLine($"Ошибка: {ex.Message}");
                        }
                        catch (IOException ex)
                        {
                            Console.WriteLine($"Ошибка файла: {ex.Message}");
                        }
                    }
                }

                private void AddTask()
                {
                    Console.Write("Название: ");
                    string title = ReadRequiredString();

                    Console.Write("Приоритет (1-4) [2]: ");
                    Priority priority = ParsePriority(Console.ReadLine());

                    Console.Write("Дедлайн (dd.MM.yyyy) [нет]: ");
                    DateTime? dueDate = ParseDate(Console.ReadLine());

                    var task = _service.CreateTask(title, priority, dueDate: dueDate);
                    Console.WriteLine($"Задача создана: {task}");
                }

                private void ListTasks()
                {
                    var tasks = _service.GetTasks().ToList();
                    if (tasks.Count == 0)
                    {
                        Console.WriteLine("Задач нет");
                        return;
                    }

                    Console.WriteLine($"--- Задач: {tasks.Count} ---");
                    foreach (var task in tasks)
                    {
                        Console.WriteLine($"  {task.Id}. {task}");
                    }
                }

                private void CompleteTask()
                {
                    int id = ReadInt("ID задачи: ");
                    _service.CompleteTask(id);
                    Console.WriteLine("Задача завершена");
                }

                private void DeleteTask()
                {
                    int id = ReadInt("ID задачи: ");
                    _service.DeleteTask(id);
                    Console.WriteLine("Задача удалена");
                }

                private void ShowStats()
                {
                    var (total, completed, pending, overdue) = _service.GetStatistics();
                    Console.WriteLine($"Всего: {total}, выполнено: {completed}, "
                                      + $"в процессе: {pending}, просрочено: {overdue}");
                }

                private void FindTasks()
                {
                    Console.Write("Текст для поиска: ");
                    var found = _service.Search(Console.ReadLine() ?? "").ToList();
                    Console.WriteLine($"Найдено: {found.Count}");
                    foreach (var task in found)
                    {
                        Console.WriteLine($"  {task.Id}. {task}");
                    }
                }

                private void PrintHelp() => Console.WriteLine(
                    "a - добавить, l - список, c - завершить, d - удалить, s - статистика, f - поиск, q - выход");

                private string ReadRequiredString()
                {
                    while (true)
                    {
                        string? value = Console.ReadLine()?.Trim();
                        if (!string.IsNullOrEmpty(value))
                        {
                            return value;
                        }
                        Console.Write("Строка не может быть пустой. Повторите: ");
                    }
                }

                private int ReadInt(string prompt)
                {
                    while (true)
                    {
                        Console.Write(prompt);
                        if (int.TryParse(Console.ReadLine(), out int result))
                        {
                            return result;
                        }
                        Console.WriteLine("Введите целое число");
                    }
                }

                private Priority ParsePriority(string? input)
                {
                    if (int.TryParse(input, out int value)
                        && Enum.IsDefined(typeof(Priority), value))
                    {
                        return (Priority)value;
                    }
                    return Priority.Medium;
                }

                private static DateTime? ParseDate(string? input)
                {
                    if (DateTime.TryParseExact(input, "dd.MM.yyyy", null,
                            System.Globalization.DateTimeStyles.None, out var date))
                    {
                        return date;
                    }
                    return null;
                }
            }
            """,
        ),
        text(
            "Код длинный, но однообразный: обработчик спрашивает данные, вызывает один метод сервиса и "
            "печатает ответ. Вспомогательные методы защищают от неверного ввода: `ReadRequiredString` "
            "зацикливается до непустой строки, `ReadInt` применяет `int.TryParse`, `ParseDate` возвращает "
            "`null`, а `ParsePriority` подставляет `Medium`.\n\n"
            "`TryParseExact` с форматом `dd.MM.yyyy` строже `TryParse`: дата не зависит от региональных "
            "настроек. Метод `static` не использует поля класса."
        ),
        text(
            "Вывод при работе с программой (строки, набранные пользователем, показаны после `>`):\n"
            "```\n"
            "=== МЕНЕДЖЕР ЗАДАЧ ===\n"
            "\n"
            "> a\n"
            "Название: Изучить LINQ\n"
            "Приоритет (1-4) [2]: 3\n"
            "Дедлайн (dd.MM.yyyy) [нет]: 15.12.2026\n"
            "Задача создана: [ ] High: Изучить LINQ (до: 15.12.2026)\n"
            "\n"
            "> l\n"
            "--- Задач: 1 ---\n"
            "  1. [ ] High: Изучить LINQ (до: 15.12.2026)\n"
            "\n"
            "> c\n"
            "ID задачи: 1\n"
            "Задача завершена\n"
            "\n"
            "> c\n"
            "ID задачи: 1\n"
            "Ошибка: Задача уже завершена\n"
            "\n"
            "> s\n"
            "Всего: 1, выполнено: 1, в процессе: 0, просрочено: 0\n"
            "\n"
            "> q\n"
            "```\n\n"
            "Второй вызов `c` показывает, зачем нужен `try` вокруг `switch`: исключение из сервиса не "
            "обрушило программу, а стало строкой «Ошибка»."
        ),
        heading("Точка входа"),
        text(
            "Файл `Program.cs` в .NET 6 и новее использует **инструкции верхнего уровня** (top-level "
            "statements): метод `Main` писать не нужно, компилятор создаст его сам. Связывание занимает "
            "три строки: сервис с именем файла, интерфейс с сервисом, запуск цикла."
        ),
        example(
            "csharp",
            """
            using TasksApp.Services;

            var service = new TaskService("tasks.json");
            var ui = new ConsoleUI(service);
            ui.Run();
            """,
        ),
        text(
            "Запуск выполняется той же командой `dotnet run`. Файл появится после первой команды `a`: "
            "загрузка отсутствующего файла возвращает пустой список. Удалив `tasks.json`, вы начнёте "
            "с чистого листа."
        ),
        heading("Простые тесты без фреймворков"),
        text(
            "**Тест** — программа, которая проверяет поведение кода и сравнивает результат с ожидаемым. "
            "В реальных проектах берут xUnit или NUnit, но принцип проще понять на собственном мини-классе: "
            "тест вызывает сервис напрямую, без клавиатуры, и его можно запускать сколько угодно раз.\n\n"
            "Путь берётся из `Path.GetTempFileName()` — отдельный файл в системной папке, поэтому тест не "
            "испортит ваш `tasks.json`. Помощник `Assert` подсчитывает пройденные и упавшие проверки."
        ),
        example(
            "csharp",
            """
            using TasksApp.Models;
            using TasksApp.Services;
            using TasksApp.Exceptions;

            namespace TasksApp.Tests;

            public class TaskServiceTests
            {
                private int _passed;
                private int _failed;

                public void RunAll()
                {
                    string tempFile = Path.GetTempFileName();
                    var service = new TaskService(tempFile);

                    TestCreate(service);
                    TestNotFound(service);

                    File.Delete(tempFile);
                    Console.WriteLine($"Пройдено: {_passed}, упало: {_failed}");
                }

                private void Assert(bool condition, string name)
                {
                    if (condition)
                    {
                        _passed++;
                        Console.WriteLine($"[OK]   {name}");
                    }
                    else
                    {
                        _failed++;
                        Console.WriteLine($"[FAIL] {name}");
                    }
                }

                private void TestCreate(TaskService service)
                {
                    var task = service.CreateTask("Тестовая задача", Priority.High, TaskCategory.Work);

                    Assert(task.Id > 0, "CreateTask: номер присвоен");
                    Assert(task.Title == "Тестовая задача", "CreateTask: название сохранено");
                    Assert(task.Priority == Priority.High, "CreateTask: приоритет сохранён");
                    Assert(!task.IsCompleted, "CreateTask: задача активна по умолчанию");

                    try
                    {
                        service.CreateTask("   ");
                        Assert(false, "CreateTask: пустое название отклонено");
                    }
                    catch (ArgumentException)
                    {
                        Assert(true, "CreateTask: пустое название отклонено");
                    }
                }

                private void TestNotFound(TaskService service)
                {
                    try
                    {
                        service.GetTask(9999);
                        Assert(false, "GetTask: исключение для несуществующего ID");
                    }
                    catch (TaskNotFoundException ex)
                    {
                        Assert(ex.TaskId == 9999, "GetTask: исключение для несуществующего ID");
                    }
                }
            }
            """,
        ),
        text(
            "Вывод:\n"
            "```\n"
            "[OK]   CreateTask: номер присвоен\n"
            "[OK]   CreateTask: название сохранено\n"
            "[OK]   CreateTask: приоритет сохранён\n"
            "[OK]   CreateTask: задача активна по умолчанию\n"
            "[OK]   CreateTask: пустое название отклонено\n"
            "[OK]   GetTask: исключение для несуществующего ID\n"
            "Пройдено: 6, упало: 0\n"
            "```\n\n"
            "Обратите внимание на отрицательный сценарий: если `CreateTask(\"   \")` не выбросит "
            "`ArgumentException`, сработает `Assert(false)`, и проверка упадёт. Тестировать отказ так же "
            "важно, как успех."
        ),
        callout(
            "success",
            "Как запустить тесты",
            "Быстрая проверка: добавьте в конец `Program.cs` строку `new TasksApp.Tests.TaskServiceTests().RunAll();` "
            "перед `ui.Run()`. Постоянный вариант: отдельный проект "
            "`dotnet new console -n TasksApp.Tests` со ссылкой `<ProjectReference>` на основной, "
            "запуск через `dotnet run --project TasksApp.Tests`."
        ),
        heading("Что мы применили"),
        text(
            "Проект небольшой, но в нём есть почти всё из курса. Таблица связывает тему и место в коде."
        ),
        table(
            ["Тема", "Где использована", "Зачем"],
            [
                ["Классы и свойства", "`TaskItem`, `TaskService`", "Данные и логика сгруппированы"],
                ["Модификаторы доступа", "`private set`, `readonly`", "Доступ меняют только методы"],
                ["Конструкторы", "`TaskItem`, `TaskService`", "Объект создаётся корректным"],
                ["Перечисления", "`Priority`, `TaskCategory`", "Никаких строк-опечаток"],
                ["Коллекции", "`List<TaskItem>`", "Динамический набор задач"],
                ["Исключения", "`TaskNotFoundException`, `try`", "Ошибки обрабатываются осознанно"],
                ["Файлы и JSON", "`FileStorage`", "Данные переживают перезапуск"],
                ["LINQ", "`Where`, `OrderByDescending`, `Max`", "Фильтры и сортировка без циклов"],
                ["Кортежи", "`GetStatistics`", "Несколько чисел одним значением"],
            ],
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Вся логика в `Program.cs`", "Код нельзя протестировать, трудно найти нужное место", "Логика — в `TaskService`, ввод-вывод — в `ConsoleUI`"],
                ["`int.Parse` для ввода", "Опечатка даёт `FormatException` и падение", "`int.TryParse` с циклом ввода"],
                ["Строки вместо перечисления", "`\"Hihg\"` компилируется и ломает статистику", "Перечисление `Priority`"],
                ["`_nextId` = 1 после загрузки", "Номера повторяются, `GetTask` вернёт чужую задачу", "`_tasks.Max(t => t.Id) + 1`"],
                ["Коллекция без `ToList()`", "Отложенный запрос пересчитывается дважды", "Материализуйте результат один раз"],
                ["Нет конструктора без параметров", "Десериализация JSON не создаёт объекты", "Публичный `TaskItem()`"],
                ["`catch { }` с пустым телом", "Ошибка исчезает, файл портится молча", "Обработать, залогировать или `throw;`"],
                ["Печать меню внутри модели", "Модель не годится для тестов и другого интерфейса", "`ToString()` в модели, печать — в `ConsoleUI`"],
            ],
        ),
        heading("Практика"),
        text(
            "Не копируйте код урока целиком. Создайте проект сами командой `dotnet new console -n TasksApp` "
            "и набирайте классы по одному, запуская `dotnet run` после каждого шага."
        ),
        numbered(
            "Основа: создайте проект и класс `TaskItem` с конструктором и проверкой названия. Добавьте три задачи в `Main` и выведите их в консоль. Убедитесь, что пустое название выбрасывает `ArgumentException`.",
            "Перечисления: добавьте `TaskCategory` из пяти значений и выведите распределение задач по категориям через `Where` и `Count`.",
            "Сервис: перенесите создание задач в `TaskService` с `List<TaskItem>` и методом `CompleteTask`. Проверьте, что повторное завершение даёт `InvalidOperationException`.",
            "Сохранение: реализуйте `FileStorage` на `System.Text.Json`, сохраните три задачи, закройте программу, запустите снова и выведите загруженные задачи с теми же номерами.",
            "Тесты: напишите класс `TaskServiceTests` с методами `Assert`, `TestCreate`, `TestComplete` и `TestNotFound`, используя временный файл. Добейтесь вывода `Пройдено: 8, упало: 0`.",
        ),
        text("Пример ожидаемого результата для четвёртого задания:"),
        example(
            "text",
            """
            Сохранено задач: 3
            --- После перезапуска ---
            1. [ ] Medium: Купить молоко
            2. [ ] High: Сдать отчёт
            3. [x] Low: Позвонить в банк
            Следующий ID: 4
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 4",
            "Если после перезапуска список пуст, проверьте путь: `tasks.json` должен лежать рядом с "
            "файлом `.csproj`. Кириллица в файле, записанная как `\\u041a\\u0443...`, означает, что нужен "
            "`UnsafeRelaxedJsonEscaping` в `JsonSerializerOptions`."
        ),
        heading("Проверьте себя"),
        numbered(
            "Зачем делить приложение на модели, сервис, хранилище и интерфейс? Назовите хотя бы две выгоды.",
            "Почему приоритет задачи описан перечислением, а не строкой?",
            "Почему для `CompletedAt` используют `{ get; private set; }`, а не обычное `{ get; set; }`?",
            "Что произойдёт с номерами задач, если после загрузки файла снова начать `_nextId` с единицы?",
            "Зачем модели `TaskItem` нужен публичный конструктор без параметров?",
        ),
        heading("Ответы", 3),
        numbered(
            "Логику можно проверить тестами без клавиатуры, интерфейс можно заменить, не переписывая правила, "
            "и ошибки быстрее локализуются в нужном слое.",
            "Компилятор не допустит опечатку в списке вариантов, а значение нельзя записать произвольной строкой; "
            "соответственно, статистика и фильтры не ломаются из-за `\"Hihg\"`.",
            "Время завершения должно меняться только вместе с флагом `IsCompleted`, то есть внутри методов "
            "`Complete` и `Reopen`. Открытый `set` позволил бы выставить дату, не меняя состояние.",
            "Новая задача получила бы уже занятый номер, и `GetTask` возвращал бы чужую запись. "
            "Поэтому номер продолжают с `_tasks.Max(t => t.Id) + 1`.",
            "Десериализатор `System.Text.Json` создаёт объект до заполнения свойств и нуждается в конструкторе "
            "без обязательных аргументов. Без него загрузка файла завершится ошибкой.",
        ),
        heading("Итоги"),
        bullets(
            "`dotnet new console` создаёт проект, `dotnet run` собирает и запускает его; файлы `.cs` включаются автоматически.",
            "Модель описывает данные и проверяет их корректность в конструкторе, но ничего не знает о консоли.",
            "Перечисления `Priority` и `TaskCategory` исключают опечатки и дают осмысленный вывод.",
            "`{ get; private set; }` и `{ get; init; }` ограничивают запись там, где состояние должен менять только класс.",
            "Сервис хранит бизнес-логику, хранилище — файл, интерфейс — диалог с пользователем.",
            "`System.Text.Json` сохраняет коллекцию в читаемый JSON; constructor без параметров нужен для десериализации.",
            "LINQ (`Where`, `OrderByDescending`, `ThenBy`, `Count`, `Any`, `Max`) заменяет ручные циклы описанием запроса.",
            "Собственное исключение `TaskNotFoundException` хранит номер задачи, а `try` в цикле меню не даёт приложению упасть.",
            "Тесты без фреймворков проверяют и успешные сценарии, и отказы, запускаясь на временном файле.",
        ),
        heading("Что дальше"),
        text(
            "Первый проект собран, но это только начало. У приложения есть очевидные направления роста: "
            "редактирование задачи отдельной командой, подзадачи и теги, экспорт в CSV и Markdown, "
            "цветной вывод приоритетов через `Console.ForegroundColor`, настройки в `appsettings.json`. "
            "Каждое из них вы теперь способны реализовать самостоятельно, потому что архитектура уже "
            "задаёт место для изменений.\n\n"
            "Следующий раздел курса углубляет инструменты, которых в проекте не хватило: обобщения, "
            "интерфейсы и абстрактные классы, структуры и записи (`record`), более сложные возможности "
            "LINQ и асинхронные операции с файлами. Начните с интерфейсов: они позволят заменить "
            "`FileStorage` на хранилище в памяти или в базе данных, не меняя `TaskService`."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Документация Microsoft: «Create a .NET console application using Visual Studio Code» — learn.microsoft.com/dotnet/core/tutorials/with-visual-studio-code",
            "Документация Microsoft: «C# top-level statements» — learn.microsoft.com/dotnet/csharp/fundamentals/program-structure/top-level-statements",
            "Документация Microsoft: «Serialization and deserialization in System.Text.Json» — learn.microsoft.com/dotnet/standard/serialization/system-text-json/overview",
            "Документация Microsoft: «Language Integrated Query (LINQ)» — learn.microsoft.com/dotnet/csharp/linq",
            "Документация Microsoft: «Unit testing C# with xUnit» — learn.microsoft.com/dotnet/core/testing/unit-testing-with-dotnet-test",
        ),
    ],
}
