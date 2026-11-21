"""Урок 3.10 курса C#: платформы и экосистема."""

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
    "topic_order": 10,
    "name": "3.10. Платформы и экосистема",
    "slug": "csharp-3-10-платформы-и-экосистема",
    "short_description": (
        "Жизненный цикл версий .NET, стратегии публикации от framework-dependent до "
        "Native AOT, многоэтапные контейнеры, кроссплатформенный код и управление "
        "зависимостями на уровне решения."
    ),
    "topic_name": "Платформы и экосистема",
    "topic_description": (
        "Как выбрать целевую платформу, упаковать приложение и доставить его в "
        "продакшен: релизный цикл LTS и STS, self-contained и AOT-публикация, "
        "контейнеры с минимальным образом, кроссплатформенные абстракции, "
        "Central Package Management и сканирование уязвимостей в CI."
    ),
    "learning_objectives": [
        "Различать LTS и STS релизы .NET, закреплять версию SDK через global.json",
        "Выбирать стратегию публикации: framework-dependent, self-contained, trimmed, ReadyToRun и Native AOT",
        "Собирать минимальный многоэтапный Docker-образ с non-root пользователем и distroless-базой",
        "Писать кроссплатформенный код через RuntimeInformation, OperatingSystem и корректную работу с путями",
        "Собирать multi-arch образы и учитывать особенности ARM64 и WebAssembly",
        "Организовать зависимости решения через Central Package Management и сканирование уязвимостей",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "csharp",
        "dotnet",
        "публикация",
        "docker",
        "кроссплатформенность",
        "зелёная сборка",
        "native-aot",
    ],
    "starter_code": code(
        r"""
        using System.Runtime.InteropServices;

        Console.WriteLine($"ОС: {RuntimeInformation.OSDescription}");
        Console.WriteLine($"Архитектура: {RuntimeInformation.ProcessArchitecture}");
        Console.WriteLine($"Framework: {RuntimeInformation.FrameworkDescription}");
        Console.WriteLine($"Платформа: {GetPlatformName()}");

        static string GetPlatformName() =>
            OperatingSystem.IsWindows() ? "Windows"
            : OperatingSystem.IsLinux() ? "Linux"
            : OperatingSystem.IsMacOS() ? "macOS"
            : "Неизвестная платформа";
        """
    ),
    "hints": [
        "Для контейнеров используйте self-contained или Native AOT публикацию: образ не должен зависеть от установленного на хосте рантайма.",
        "Рефлексия — главный враг trimming и AOT. Читайте предупреждения анализатора и помечайте члены атрибутом DynamicallyAccessedMembers.",
        "В CI задавайте TreatWarningsAsErrors и dotnet list package --vulnerable --include-transitive, иначе устаревшие транзитивные пакеты останутся незамеченными.",
        "global.json с rollForward pin'ит SDK команды: это избавляет от расхождений между локальной машиной и CI.",
    ],
    "content": [
        text(
            "Код на C# проходит путь от исходника до боевого сервера, и на каждом шаге"
            " принимаются решения о платформе: версию .NET, способ упаковки, целевое"
            " окружение и набор зависимостей. Ошибки здесь редко видны в юнит-тестах,"
            " но дорого стоят в продакшене: несовпавшие версии рантайма, образы на сотни"
            " мегабайт с уязвимостями, поломка после смены архитектуры процессора.\n\n"
            "Урок разбирает экосистему .NET с точки зрения инженера, отвечающего за"
            " доставку сервиса: релизный цикл, артефакт, контейнер, кроссплатформенный"
            " код, пакеты и проверки в CI. Примеры вывода приведены для Linux x64, если"
            " не сказано другое."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "различать LTS и STS релизы .NET и планировать обновления с учётом даты End of Life;",
            "закреплять версию SDK через global.json и объяснять параметры rollForward;",
            "выбирать стратегию публикации: framework-dependent, self-contained, trimmed, ReadyToRun и Native AOT;",
            "писать многоэтапный Dockerfile с кэшированием NuGet-пакетов, non-root пользователем и минимальным рантаймом;",
            "организовывать кроссплатформенный код через RuntimeInformation, OperatingSystem и обработку путей;",
            "собирать multi-arch образы для x64 и ARM64 и понимать ограничения WebAssembly;",
            "управлять зависимостями решения через Central Package Management, version locking и сканирование уязвимостей;",
            "выстраивать CI-конвейер, который проверяет сборку, тесты, безопасность образа и публикацию.",
        ),
        heading("Жизненный цикл версий .NET"),
        text(
            "Платформа .NET выпускается по предсказуемому графику: крупный релиз ежегодно"
            " и ежемесячные patch-обновления с исправлениями безопасности. Мажорные"
            " релизы делятся на два вида поддержки.\n\n"
            "**LTS (Long Term Support)** — релиз с длительной поддержкой, обычно три"
            " года: каждый чётный мажор (.NET 6, 8, 10). **STS (Standard Term Support)** —"
            " поддержка около 18 месяцев: нечётные мажоры (.NET 7, 9). После даты EOL"
            " (End of Life) обновления безопасности прекращаются: приложение не ломается"
            " сразу, но новые уязвимости в рантайме остаются незакрытыми.\n\n"
            "Для продакшена выбирайте LTS и планируйте обновление за полгода до EOL. STS"
            " оправдан, когда нужны новые возможности языка или JIT и команда готова"
            " мигрировать чаще; preview — только для экспериментов. **TargetFramework** в"
            " проекте (`net8.0`, `net9.0`, `net10.0`) определяет рантайм и набор"
            " доступных API."
        ),
        table(
            ["Тип релиза", "Пример", "Срок поддержки", "Когда выбирать"],
            [
                ["LTS", ".NET 8, .NET 10", "Около 3 лет", "Продакшен, долгие проекты, корпоративные системы"],
                ["STS", ".NET 7, .NET 9", "Около 18 месяцев", "Нужны свежие возможности, команда готова обновляться ежегодно"],
                ["Preview", ".NET 11 preview", "До финального релиза", "Оценка новых API, не для продакшена"],
            ],
        ),
        text(
            "Отдельно закрепите версию SDK. Компилятор и MSBuild поставляются вместе с"
            " SDK, и разные версии по-разному генерируют код, меняют предупреждения и"
            " разрешают зависимости. Если у разработчика SDK 8.0.402, а в CI — 9.0.100,"
            " сборки будут отличаться. Файл `global.json` в корне репозитория фиксирует"
            " версию для всей команды."
        ),
        example(
            "json",
            """
            {
              "sdk": {
                "version": "8.0.400",
                "rollForward": "latestFeature",
                "allowPrerelease": false
              }
            }
            """,
        ),
        text(
            "Параметр `rollForward` управляет поведением, когда точной версии нет на"
            " машине. Значение `latestPatch` разрешает только патч-обновления (8.0.400 →"
            " 8.0.407), `latestFeature` — обновления внутри минорной ветки (8.0.400 →"
            " 8.0.500), `latestMinor` и `latestMajor` разрешают переход на более новые"
            " минорные ветки и мажоры. Для CI разумный компромисс — `latestPatch`: он"
            " получает исправления безопасности, но не меняет поведение компилятора."
        ),
        callout(
            "info",
            "Где ещё живёт версия .NET",
            "TargetFramework задаёт целевую платформу проекта, global.json — версию SDK,"
            " а тег базового образа в Dockerfile определяет рантайм в контейнере. Все три"
            " места нужно обновлять согласованно, иначе локально приложение работает, а в"
            " контейнере падает на missing runtime.",
        ),
        heading("Стратегии публикации"),
        text(
            "`dotnet publish` собирает готовый к запуску артефакт: DLL, конфигурацию и"
            " при необходимости сам рантайм. Главное решение — будет ли на целевой"
            " машине установлен .NET.\n\n"
            "**Framework-dependent** (по умолчанию) занимает единицы мегабайт, но требует"
            " рантайма совместимой версии; подходит для сред, где .NET уже есть."
            " **Self-contained** кладёт в папку рантайм целиком, убирая внешнюю"
            " зависимость ценой десятков мегабайт.\n\n"
            "**Trimming** удаляет неиспользуемый код, **ReadyToRun (R2R)** заранее"
            " компилирует IL в машинный код и ускоряет старт, оставляя JIT для горячих"
            " путей, **Native AOT** компилирует приложение в нативный бинарник без JIT."
        ),
        example(
            "bash",
            """
            # Framework-dependent: маленький артефакт, нужен установленный рантайм
            dotnet publish src/WebApi -c Release -r linux-x64 --self-contained false
            # Артефакт: около 1-5 МБ

            # Self-contained: рантайм внутри, ничего устанавливать не нужно
            dotnet publish src/WebApi -c Release -r linux-x64 --self-contained true
            # Артефакт: около 60-100 МБ

            # Self-contained с trimming
            dotnet publish src/WebApi -c Release -r linux-x64 --self-contained true \\
              -p:PublishTrimmed=true -p:TrimMode=partial
            # Артефакт: около 20-40 МБ
            """,
        ),
        example(
            "xml",
            """
            <PropertyGroup>
              <PublishTrimmed>true</PublishTrimmed>
              <TrimMode>partial</TrimMode>
              <SuppressTrimAnalysisWarnings>false</SuppressTrimAnalysisWarnings>
            </PropertyGroup>

            <!-- Корневой узел для библиотек, работающих через рефлексию -->
            <ItemGroup>
              <TrimmerRootAssembly Include="MyLibrary" />
            </ItemGroup>
            """,
        ),
        text(
            "Trimming анализирует граф вызовов и удаляет код без статических ссылок. Если"
            " приложение обращается к типам по имени (`Activator.CreateInstance`,"
            " `Type.GetMethod`, сериализаторы на рефлексии), анализатор не видит связей и"
            " предупреждает. **TrimMode partial** сохраняет сборки, но удаляет"
            " неиспользуемые члены, **full** режет агрессивнее. `TrimmerRootAssembly`"
            " сообщает анализатору, что сборка используется целиком, — это инструмент для"
            " библиотек, которые не удаётся сделать trim-совместимыми.\n\n"
            "Native AOT идёт дальше: JIT и метаданные большей части типов исключаются."
            " Результат — нативный бинарник в 3-10 МБ с мгновенным стартом, что критично"
            " для serverless-функций, CLI и контейнеров с быстрым автоскейлингом. Цена —"
            " ограничения: нет динамической загрузки сборок, ограниченная рефлексия,"
            " обязательная source-generated сериализация JSON."
        ),
        example(
            "xml",
            """
            <PropertyGroup>
              <OutputType>Exe</OutputType>
              <TargetFramework>net8.0</TargetFramework>
              <PublishAot>true</PublishAot>
              <StripSymbols>true</StripSymbols>
              <InvariantGlobalization>true</InvariantGlobalization>
              <JsonSerializerIsReflectionEnabledByDefault>false</JsonSerializerIsReflectionEnabledByDefault>
            </PropertyGroup>
            """,
        ),
        example(
            "csharp",
            """
            using System.Text.Json;
            using System.Text.Json.Serialization;

            public sealed class OrderDto
            {
                public int Id { get; set; }
                public string Customer { get; set; } = "";
            }

            [JsonSerializable(typeof(OrderDto))]
            internal sealed partial class AppJsonContext : JsonSerializerContext
            {
            }

            public static class Program
            {
                public static void Main()
                {
                    var order = new OrderDto { Id = 7, Customer = "Анна" };
                    string json = JsonSerializer.Serialize(order, AppJsonContext.Default.OrderDto);
                    Console.WriteLine(json);

                    var parsed = JsonSerializer.Deserialize(json, AppJsonContext.Default.OrderDto);
                    Console.WriteLine(parsed is null ? "null" : parsed.Customer);
                }
            }
            """,
        ),
        text(
            "Вывод программы:\n\n```\n{\"Id\":7,\"Customer\":\"Анна\"}\nАнна\n```\n\n"
            "Контекст `JsonSerializerContext` генерирует код сериализации на этапе"
            " компиляции, поэтому AOT-приложению не нужна рефлексия по метаданным. Это же"
            " снимает предупреждения trimming: анализатор видит конкретные типы."
        ),
        table(
            ["Режим", "Размер", "Старт", "Ограничения"],
            [
                ["Framework-dependent", "1-5 МБ", "Средний, JIT на старте", "На хосте нужен совместимый рантайм"],
                ["Self-contained", "60-100 МБ", "Средний, JIT на старте", "Больший образ и больше обновлений безопасности"],
                ["Self-contained + trim", "20-40 МБ", "Средний", "Нужны trim-совместимые зависимости"],
                ["ReadyToRun", "+10-30 МБ к варианту", "Быстрый, код предкомпилирован", "Не помогает в AOT, размер растёт"],
                ["Native AOT", "3-10 МБ", "Мгновенный, без JIT", "Ограничены рефлексия, динамическая загрузка, часть библиотек"],
            ],
        ),
        callout(
            "success",
            "Выбор по сценарию",
            "CLI-утилита или лямбда: Native AOT. ASP.NET Core в контейнере: self-contained"
            " или AOT при совместимых зависимостях. Внутренний сервис на управляемом"
            " сервере: framework-dependent с обновляемым рантаймом платформы.",
        ),
        heading("Контейнеры: многоэтапная сборка"),
        text(
            "Докер-образ для .NET решает ту же задачу, что и публикация: доставить"
            " рантайм и приложение в изолированном окружении. Ключевой приём —"
            " **многоэтапная сборка**: SDK нужен только для компиляции, в финальный образ"
            " попадают лишь опубликованные файлы. Размер падает с гигабайтов до десятков"
            " мегабайт, а в рантайме нет компилятора и лишних утилит — меньше поверхность"
            " атаки.\n\n"
            "Второй приём — порядок слоёв: файлы проекта копируются и восстанавливаются"
            " раньше исходников, поэтому при изменении кода `dotnet restore` берётся из"
            " кэша. Третий — запуск от непривилегированного пользователя: скомпрометированный"
            " процесс не получит прав на запись в файловую систему."
        ),
        example(
            "dockerfile",
            """
            # ===== BUILD STAGE =====
            FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
            WORKDIR /src

            # Сначала только манифесты — слой restore кэшируется между сборками
            COPY Directory.Build.props Directory.Packages.props ./
            COPY src/WebApi/WebApi.csproj src/WebApi/
            RUN dotnet restore src/WebApi/WebApi.csproj

            # Затем исходники и публикация
            COPY . .
            RUN dotnet publish src/WebApi/WebApi.csproj -c Release -o /app/publish \\
                --self-contained true -r linux-musl-x64 \\
                /p:PublishTrimmed=true /p:TrimMode=partial

            # ===== RUNTIME STAGE =====
            FROM mcr.microsoft.com/dotnet/runtime-deps:8.0-alpine AS runtime
            WORKDIR /app

            RUN addgroup -g 1000 -S appgroup \\
             && adduser -u 1000 -S appuser -G appgroup
            USER appuser

            COPY --from=build --chown=appuser:appgroup /app/publish .

            EXPOSE 8080
            ENV ASPNETCORE_URLS=http://+:8080
            ENV DOTNET_GCServer=1

            HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
              CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

            ENTRYPOINT ["./WebApi"]
            """,
        ),
        text(
            "Обратите внимание на базовый образ финального этапа: `runtime-deps` содержит"
            " только системные библиотеки, необходимые self-contained приложению, без .NET"
            " — он уже лежит рядом. Для Native AOT используйте **distroless**: там нет"
            " оболочки и менеджера пакетов, поэтому эксплуатировать контейнер через `sh`"
            " нечем. Цена — сложнее отладка, нужны отдельные debug-образы."
        ),
        example(
            "dockerfile",
            """
            FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
            WORKDIR /src
            COPY . .
            RUN dotnet publish src/WebApi -c Release -r linux-musl-x64 -o /app \\
                --self-contained true /p:PublishAot=true

            # distroless: нет shell и package manager
            FROM gcr.io/distroless/static-debian12 AS runtime
            WORKDIR /app
            COPY --from=build /app .
            USER 65532:65532
            EXPOSE 8080
            ENTRYPOINT ["./WebApi"]
            """,
        ),
        text(
            "Для локальной разработки удобен Docker Compose: приложение собирается со"
            " стадии `build` с примонтированными исходниками, а база данных ждёт healthcheck."
        ),
        example(
            "yaml",
            """
            services:
              app:
                build:
                  context: .
                  target: build
                ports: ["8080:8080"]
                environment:
                  - ASPNETCORE_ENVIRONMENT=Development
                  - ConnectionStrings__Default=Host=db;Database=app;Username=app;Password=app
                depends_on:
                  db:
                    condition: service_healthy
                volumes:
                  - ./src:/src
                  - ~/.nuget/packages:/root/.nuget/packages

              db:
                image: postgres:16-alpine
                environment:
                  POSTGRES_DB: app
                  POSTGRES_USER: app
                  POSTGRES_PASSWORD: app
                healthcheck:
                  test: ["CMD-SHELL", "pg_isready -U app"]
                  interval: 5s
                  timeout: 5s
                  retries: 5
                volumes:
                  - pgdata:/var/lib/postgresql/data

            volumes:
              pgdata:
            """,
        ),
        example(
            "bash",
            """
            docker build -t myapp:1.0.0 .
            docker run --rm -p 8080:8080 myapp:1.0.0

            # Размер образа
            docker images myapp:1.0.0
            # myapp   1.0.0   a1b2c3d4e5f6   2 minutes ago   45.2MB

            trivy image myapp:1.0.0
            hadolint Dockerfile
            """,
        ),
        heading("Кроссплатформенный код"),
        text(
            "Начиная с .NET Core приложение обычно работает на Windows, Linux и macOS без"
            " пересборки, но код может зависеть от платформы: реестр, службы, сигналы,"
            " разделители путей, регистр букв в именах файлов. Определяйте платформу"
            " через `RuntimeInformation` и статические методы `OperatingSystem`: они"
            " компилируются в быстрые проверки без сравнения строк.\n\n"
            "Изолируйте платформенные ветки за интерфейсом, чтобы бизнес-логика не знала"
            " об ОС. Рантайм-проверки оставляйте для кода, работающего везде одним"
            " бинарником, условную компиляцию — для API, существующих только на одной"
            " платформе."
        ),
        example(
            "csharp",
            """
            using System.Runtime.InteropServices;

            static string DescribeEnvironment()
            {
                string os = OperatingSystem.IsWindows() ? "Windows"
                    : OperatingSystem.IsLinux() ? "Linux"
                    : OperatingSystem.IsMacOS() ? "macOS"
                    : "другая ОС";

                var arch = RuntimeInformation.ProcessArchitecture;
                bool is64 = Environment.Is64BitProcess;
                string version = Environment.Version.ToString();

                return $"{os}, {arch}, 64-bit: {is64}, .NET {version}";
            }

            Console.WriteLine(DescribeEnvironment());
            """,
        ),
        text(
            "Вывод на машине под управлением Linux ARM64 с .NET 8:\n\n```\nLinux, Arm64, 64-bit: True, .NET 8.0.8\n```\n\n"
            "В `ProcessArchitecture` возможны `X64`, `X86`, `Arm`, `Arm64`, `Wasm`,"
            " `S390x`, `LoongArch64` и `Armv6`. `OSArchitecture`, в отличие от неё,"
            " описывает ОС: значения расходятся при x64-приложении на ARM64."
        ),
        example(
            "csharp",
            """
            using System.Runtime.InteropServices;

            if (OperatingSystem.IsLinux())
            {
                Console.WriteLine("Linux: используем /proc для чтения данных о процессе");
                string[] lines = File.ReadAllLines("/proc/self/status");
                Console.WriteLine(lines.First(l => l.StartsWith("Threads:")));
            }
            else if (OperatingSystem.IsWindows())
            {
                string root = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
                Console.WriteLine($"Windows: общие данные в {root}");
            }
            else if (OperatingSystem.IsMacOS())
            {
                Console.WriteLine($"macOS: kernel {RuntimeInformation.OSDescription}");
            }
            else
            {
                Console.WriteLine("Платформа не поддержана, используем переносимый путь");
            }
            """,
        ),
        text(
            "Вывод на Linux:\n\n```\nLinux: используем /proc для чтения данных о процессе\nThreads:\t12\n```\n\n"
            "Помимо рантайм-проверок существует условная компиляция. Символы"
            " `NET8_0_OR_GREATER`, `NET9_0_OR_GREATER` и аналогичные позволяют развести"
            " код по версиям таргета в многоплатформенных библиотеках, которые"
            " собираются сразу под несколько TargetFramework."
        ),
        example(
            "csharp",
            """
            #if NET8_0_OR_GREATER
            // На .NET 8+ есть TimeProvider — кроссплатформенная абстракция времени
            TimeProvider timeProvider = TimeProvider.System;
            Console.WriteLine($"Сейчас: {timeProvider.GetUtcNow():O}");
            #else
            // Фолбэк для более старых таргетов
            Console.WriteLine($"Сейчас: {DateTime.UtcNow:O}");
            #endif
            """,
        ),
        text(
            "Вывод:\n\n```\nСейчас: 2026-03-14T09:21:45.1234567+00:00\n```\n\n"
            "Пути — вторая ловушка. Не склеивайте их через обратный слеш и не хардкодьте"
            " разделитель. `Path.Combine` учитывает настройки ОС, `Path.GetFullPath`"
            " нормализует путь, а `Environment.GetEnvironmentVariable` выносит данные за"
            " пределы приложения — обязательное требование для контейнеров."
        ),
        example(
            "csharp",
            """
            string dataDir = Environment.GetEnvironmentVariable("DATA_DIR")
                ?? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "appdata");

            string configPath = Path.Combine(dataDir, "config", "app.json");
            string absolute = Path.GetFullPath(configPath);

            Directory.CreateDirectory(Path.GetDirectoryName(absolute)!);

            Console.WriteLine($"Разделитель: '{Path.DirectorySeparatorChar}'");
            Console.WriteLine($"Порт: {absolute.Length}; файл: {Path.GetFileName(absolute)}");
            """,
        ),
        text(
            "Вывод на Linux:\n\n```\nРазделитель: '/'\nПорт: 24; файл: app.json\n```\n\n"
            "Ещё одна особенность контейнеров — культура. В минимальных образах часто нет"
            " ICU (International Components for Unicode), и приложение не может работать"
            " с locale. Два выхода: установить пакет `icu-libs` или включить"
            " `InvariantGlobalization`, который отключает зависимость от ICU и уменьшает"
            " размер, но оставляет только инвариантную культуру. В этом режиме парсинг и"
            " форматирование выполняйте явно через `CultureInfo.InvariantCulture`."
        ),
        example(
            "csharp",
            """
            using System.Globalization;

            // В режиме InvariantGlobalization культура только одна
            Console.WriteLine($"Культура: {CultureInfo.CurrentCulture.Name}");
            Console.WriteLine($"Invariant: {CultureInfo.CurrentCulture.Equals(CultureInfo.InvariantCulture)}");

            // Явный формат не зависит от культуры
            decimal amount = 1234.5m;
            Console.WriteLine(amount.ToString("0.00", CultureInfo.InvariantCulture));
            Console.WriteLine(DateTime.Parse("2026-01-15T10:30:00", CultureInfo.InvariantCulture,
                DateTimeStyles.RoundtripKind).ToString("yyyy-MM-dd"));
            """,
        ),
        text(
            "Вывод:\n\n```\nКультура: \nInvariant: True\n1234.50\n2026-01-15\n```\n\n"
            "Пустая строка в первой строке — это имя инвариантной культуры. Явное"
            " указание формата делает результат одинаковым на любом сервере и убирает"
            " самый частый источник расхождений между окружениями: локально дробная часть"
            " пишется через запятую, а в контейнере — через точку."
        ),
        callout(
            "warning",
            "Пути и регистр",
            "В Linux имена файлов регистрозависимы, а в Windows и macOS по умолчанию нет."
            " Код, который открывает «Images/logo.png», собранный на Windows, может упасть"
            " на Linux. Используйте единый регистр в путях и проверяйте в CI на Linux.",
        ),
        heading("ARM64 и multi-arch образы"),
        text(
            "Флот серверов всё чаще работает на ARM64: AWS Graviton, серверы на Ampere,"
            " Apple Silicon, одноплатные компьютеры и облачные функции. RID (Runtime"
            " Identifier) сообщает MSBuild целевую платформу, и результат перестаёт быть"
            " переносимым: нативный код AOT и R2R привязан к архитектуре.\n\n"
            "Современная практика — один образ для нескольких архитектур через `docker"
            " buildx` и переменную `TARGETARCH` в Dockerfile. Инструмент собирает вариант"
            " под каждую платформу и упаковывает их в **manifest list**, из которого"
            " Docker при скачивании выбирает нужный."
        ),
        example(
            "bash",
            """
            # Сборка под конкретные платформы
            dotnet publish src/Cli -c Release -r linux-arm64 --self-contained true
            dotnet publish src/Cli -c Release -r osx-arm64 --self-contained true
            dotnet publish src/Cli -c Release -r win-arm64 --self-contained true

            # Multi-arch образ: buildx собирает варианты и склеивает manifest list
            docker buildx create --use
            docker buildx build --platform linux/amd64,linux/arm64 \\
              -t registry.example.com/myapp:1.0.0 --push .
            """,
        ),
        example(
            "dockerfile",
            """
            # Сборка выполняется на архитектуре билд-хоста
            FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
            ARG TARGETARCH
            WORKDIR /src
            COPY . .
            RUN dotnet publish src/WebApi -c Release -r linux-${TARGETARCH} -o /app --self-contained true

            FROM mcr.microsoft.com/dotnet/runtime-deps:8.0-alpine
            WORKDIR /app
            COPY --from=build /app .
            USER 1000
            ENTRYPOINT ["./WebApi"]
            """,
        ),
        text(
            "Флаг `--platform=$BUILDPLATFORM` запускает этап сборки на архитектуре хоста,"
            " сокращая эмуляцию и ускоряя сборку. ARM64 стоит проверять отдельно из-за"
            " нативного кода: если зависимость не имеет ARM64-варианта, ошибка проявится"
            " не при сборке, а при первом вызове недостающего метода."
        ),
        heading("WebAssembly"),
        text(
            "WebAssembly (WASM) — целевая платформа .NET: приложение компилируется в"
            " байт-код, исполняемый в браузере, что позволяет писать клиент на C# без"
            " JavaScript — этот механизм лежит в основе Blazor WebAssembly.\n\n"
            "Песочница браузера ограничивает возможности: нет произвольного доступа к"
            " файловой системе, сокетам и потокам, SIMD ограничен. Вместо них —"
            " `HttpClient` и JS interop, вызовы JavaScript из C# и обратно. С .NET 8"
            " доступна AOT-компиляция WASM: быстрее выполнение ценой размера загрузки."
        ),
        example(
            "csharp",
            """
            using System.Runtime.InteropServices.JavaScript;
            using System.Runtime.InteropServices;

            if (RuntimeInformation.ProcessArchitecture == Architecture.Wasm)
            {
                Console.WriteLine("Запуск в браузере: доступен JS interop и LocalStorage");
            }

            public static partial class BrowserBridge
            {
                // Импорт функции из JavaScript, доступен и при интерпретации, и при AOT
                [JSImport("globalThis.console.log")]
                public static partial void Log(string message);
            }
            """,
        ),
        text(
            "Для вызова функции достаточно объявить partial-метод с атрибутом `JSImport`:"
            " генератор построит связующий код. Обратное направление задаёт `JSExport`."
            " Публикация WASM — `dotnet publish -c Release -r wasm`."
        ),
        heading("Управление зависимостями"),
        text(
            "Решение из десятка проектов быстро превращается в набор несогласованных"
            " версий: один проект ссылается на Serilog 3.1, другой — на 3.0, третий — на"
            " транзитивную 2.12. Central Package Management (CPM) переносит все версии в"
            " `Directory.Packages.props`, а в проектах остаются ссылки без версий."
        ),
        example(
            "xml",
            """
            <!-- Directory.Packages.props в корне решения -->
            <Project>
              <PropertyGroup>
                <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
                <CentralPackageTransitivePinningEnabled>true</CentralPackageTransitivePinningEnabled>
              </PropertyGroup>

              <ItemGroup>
                <PackageVersion Include="Serilog.AspNetCore" Version="8.0.3" />
                <PackageVersion Include="FluentValidation" Version="11.9.1" />
                <PackageVersion Include="MediatR" Version="12.4.1" />
                <PackageVersion Include="xunit" Version="2.9.2" />
                <PackageVersion Include="Testcontainers" Version="3.10.0" />
              </ItemGroup>
            </Project>
            """,
        ),
        example(
            "xml",
            """
            <!-- В проекте версия не указывается -->
            <Project Sdk="Microsoft.NET.Sdk">
              <ItemGroup>
                <PackageReference Include="Serilog.AspNetCore" />
                <PackageReference Include="FluentValidation" />
                <PackageReference Include="MediatR" />
              </ItemGroup>
            </Project>
            """,
        ),
        text(
            "Флаг `CentralPackageTransitivePinningEnabled` закрепляет и транзитивные"
            " версии: если два пакета требуют разные версии зависимости, вы явно выбираете"
            " ту, что увидит сборка. Это снижает эффект «алмазной» зависимости.\n\n"
            "Второй уровень контроля — воспроизводимость: `Deterministic` и"
            " `ContinuousIntegrationBuild` дают одинаковый результат при одинаковых"
            " исходниках, а `EmbedUntrackedSources` и `IncludeSymbols` позволяют"
            " сопоставить сборку с исходником при разборе инцидентов."
        ),
        example(
            "xml",
            """
            <PropertyGroup>
              <ContinuousIntegrationBuild>true</ContinuousIntegrationBuild>
              <Deterministic>true</Deterministic>
              <PublishRepositoryUrl>true</PublishRepositoryUrl>
              <EmbedUntrackedSources>true</EmbedUntrackedSources>
              <IncludeSymbols>true</IncludeSymbols>
              <SymbolPackageFormat>snupkg</SymbolPackageFormat>
            </PropertyGroup>
            """,
        ),
        example(
            "bash",
            """
            # Устаревшие и уязвимые пакеты, включая транзитивные зависимости
            dotnet list package --outdated
            dotnet list package --vulnerable --include-transitive

            # Сравнение с запрещёнными или устаревшими версиями в CI
            dotnet restore --no-cache
            """,
        ),
        text(
            "Вывод типичного отчёта об уязвимостях:\n\n```\n"
            "Project `src/WebApi` has the following vulnerable packages\n"
            "   [net8.0]:\n"
            "   Top-level Package      Requested   Resolved   Severity   Advisory URL\n"
            "   > Newtonsoft.Json      12.0.3      12.0.3     High       https://github.com/advisories/GHSA-5crp-9r3c-p9vr\n"
            "```\n\n"
            "Аудит NuGet включён по умолчанию в .NET 8+: уязвимости выше заданного порога"
            " дают предупреждения `NU1902`-`NU1904`, которые при `TreatWarningsAsErrors`"
            " ломают сборку."
        ),
        heading("CI-конвейер"),
        text(
            "Конвейер непрерывной интеграции выполняет проверки автоматически и одинаково"
            " для каждого изменения: восстановление по зафиксированным версиям, сборка с"
            " ошибками-предупреждениями, тесты, аудит пакетов, сборка образа и"
            " сканирование уязвимостей перед публикацией."        ),
        example(
            "yaml",
            """
            name: CI
            on: [push, pull_request]

            jobs:
              build:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4

                  - name: Setup .NET
                    uses: actions/setup-dotnet@v4
                    with:
                      global-json-file: global.json

                  - name: Restore
                    run: dotnet restore

                  - name: Build
                    run: dotnet build --no-restore -c Release -warnaserror

                  - name: Test
                    run: dotnet test --no-build -c Release --collect:"XPlat Code Coverage"

                  - name: Vulnerability audit
                    run: dotnet list package --vulnerable --include-transitive
            """,
        ),
        example(
            "yaml",
            """
            jobs:
              docker:
                needs: build
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - name: Build image
                    run: docker build -t myapp:${{ github.sha }} .
                  - name: Scan with Trivy
                    run: trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:${{ github.sha }}
                  - name: Push
                    if: github.event_name == 'push'
                    run: docker push myapp:${{ github.sha }}
                    env:
                      REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}
            """,
        ),
        text(
            "Обратите внимание на два тонких момента. `-warnaserror` превращает"
            " предупреждения анализаторов в ошибки, поэтому несовместимый с trimming код"
            " не попадёт в продакшен. Флаг `--exit-code 1` у Trivy делает шаг падающим при"
            " находке критичных уязвимостей. Сканирование образа после `docker build`"
            " находит и уязвимости системных пакетов базового образа, невидимые аудиту NuGet."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Нет global.json", "Разные SDK в команде и CI дают разное поведение сборки", "Зафиксировать SDK через global.json с rollForward"],
                ["Публикация в контейнер без self-contained", "Образ падает на missing framework, зависим от рантайма хоста", "self-contained или Native AOT в многоэтапной сборке"],
                ["Игнорирование предупреждений trimming", "Удалённый при рефлексии код приводит к runtime-ошибкам", "Исправить вхождения или пометить через DynamicallyAccessedMembers и TrimmerRootAssembly"],
                ["Хардкод путей с обратным слэшем", "Приложение не работает на Linux", "Path.Combine, Path.GetFullPath, переменные окружения"],
                ["Нет InvariantGlobalization в контейнере", "Приложение падает без ICU или тратит память на решения", "Включить InvariantGlobalization и указывать CultureInfo явно"],
                ["Образы не сканируются на уязвимости", "Критичные CVE уходят в продакшен незамеченными", "Trivy и аудит NuGet в CI с exit-code для HIGH"],
                ["Сборка от root в контейнере", "Компрометация процесса даёт полные права в контейнере", "Создать непривилегированного пользователя и указать USER"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполняйте задания в отдельном тестовом решении. Для сборки используйте"
            " `dotnet build -c Release` и `dotnet publish`, результат сравнивайте по"
            " размеру публикации и времени холодного старта."
        ),
        numbered(
            "Настройте `global.json` так, чтобы сборка требовала SDK минимальной версии 8.0.400 и принимала только patch-обновления. Проверьте поведение при подмене версии на отсутствующую.",
            "Опубликуйте консольное приложение в трёх режимах: framework-dependent, self-contained и Native AOT. Измерьте размер папки публикации и сравните время запуска.",
            "Переведите приложение на source-generated JSON с `AppJsonContext` и включите `PublishAot`. Устраните все ошибки, связанные с рефлексией.",
            "Соберите многоэтапный Dockerfile с non-root пользователем и healthcheck. Добейтесь размера образа менее 50 МБ и отсутствия HIGH/CRITICAL в Trivy.",
            "Настройте Central Package Management в решении из трёх проектов, добавьте закрепление транзитивных версий и шаг `dotnet list package --vulnerable` в CI.",
        ),
        text("Пример ожидаемого результата для второго задания:"),
        example(
            "text",
            """
            framework-dependent : 1.6 МБ   запуск ~0.42 с
            self-contained      : 72.4 МБ  запуск ~0.51 с
            Native AOT          : 6.1 МБ   запуск ~0.02 с
            """,
        ),
        callout(
            "info",
            "Подсказка к заданию 4",
            "Используйте рантайм-слой `runtime-deps` или distroless, а не полный SDK."
            " Не забывайте удалить из образа кэш NuGet и папку obj — они часто остаются"
            " при копировании всего каталога.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем LTS-версия .NET отличается от STS и как это влияет на планирование обновлений?",
            "В какой ситуации self-contained публикация лучше framework-dependent?",
            "Почему Native AOT требует source-generated JSON и какие ограничения накладывает?",
            "Зачем в Dockerfile сначала копируют csproj, а потом весь исходный код?",
            "Почему образ должен запускаться от непривилегированного пользователя?",
            "Что делает `CentralPackageTransitivePinningEnabled` и какую проблему решает?",
        ),
        heading("Ответы", 3),
        numbered(
            "LTS поддерживается около трёх лет и подходит для продакшена, STS — около 18 месяцев; обновление планируется до EOL.",
            "Когда на целевой машине нет нужного рантайма и установка .NET нежелательна: self-contained убирает внешнюю зависимость.",
            "AOT исключает метаданные для рефлексии. Source-generated контекст генерирует код сериализации заранее; нет динамической загрузки сборок.",
            "Чтобы слой `dotnet restore` кешировался и при изменении исходников не пересчитывался.",
            "Чтобы при компрометации сервиса процесс не мог изменять файлы образа и повышать права.",
            "Закрепляет версии транзитивных зависимостей в одном файле, убирая конфликты между пакетами.",
        ),
        heading("Итоги"),
        bullets(
            "LTS — около трёх лет поддержки, STS — около 18 месяцев; продакшену нужна LTS и план обновления до EOL.",
            "global.json фиксирует SDK, TargetFramework — целевую платформу, тег образа — рантайм: их обновляют согласованно.",
            "Framework-dependent экономит размер, self-contained убирает внешнюю зависимость, trimming и AOT сокращают вес и старт.",
            "Native AOT даёт мгновенный старт, но требует trim-совместимых зависимостей и source-generated JSON.",
            "Многоэтапная сборка отделяет SDK от рантайма, а порядок слоёв и non-root пользователь снижают вес и риски.",
            "RuntimeInformation, OperatingSystem и Path.Combine — основа кроссплатформенного кода; культура задаётся явно.",
            "Multi-arch образы собираются через buildx и TARGETARCH; WASM ограничен песочницей браузера.",
            "Central Package Management, детерминированная сборка и сканирование уязвимостей делают доставку воспроизводимой.",
        ),
        heading("Что дальше"),
        text(
            "Вы прошли путь от исходника до продакшена: версии, артефакт, контейнер,"
            " кроссплатформенность, зависимости и CI. Заключительный урок — продвинутый"
            " проект, где эти практики применяются вместе: несколько проектов, публикация"
            " в контейнер, тесты и автоматическая проверка на каждом изменении."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "График поддержки .NET — dotnet.microsoft.com/platform/support/policy/dotnet-core",
            "Публикация приложений .NET — learn.microsoft.com/dotnet/core/deploying/",
            "Native AOT — learn.microsoft.com/dotnet/core/deploying/native-aot",
            "Docker для .NET — learn.microsoft.com/dotnet/core/docker/",
            "Central Package Management — learn.microsoft.com/nuget/consume-packages/central-package-management",
            "Trivy — aquasecurity.github.io/trivy/",
        ),
    ],
}
