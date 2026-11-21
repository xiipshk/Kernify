"""Урок 3.9 курса Rust: экосистема Cargo."""

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
    "language": "rust",
    "program_order": 3,
    "topic_order": 9,
    "name": "3.9. Экосистема Cargo",
    "slug": "rust-3-9-экосистема-cargo",
    "short_description": (
        "Workspaces, features и optional dependencies, профили сборки, кросс-компиляция, "
        "публикация на crates.io, build.rs, приватные реестры и автоматизация через xtask."
    ),
    "topic_name": "Экосистема Cargo",
    "topic_description": (
        "Углублённое изучение Cargo как инструмента сборки и платформы распространения кода: "
        "устройство workspaces и наследование настроек, модель features и её аддитивность, "
        "профили сборки и тонкая настройка оптимизации, кросс-компиляция и .cargo/config.toml, "
        "публикация крейтов с SemVer, build-скрипты, патчи зависимостей, приватные реестры "
        "и автоматизация релизов через паттерн xtask."
    ),
    "learning_objectives": [
        "Проектировать cargo workspace с виртуальным манифестом, resolver = \"2\" и наследованием зависимостей",
        "Описывать аддитивные features, optional dependencies, синтаксис dep: и weak-зависимости",
        "Настраивать профили dev, release, test и собственные профили с LTO, strip и per-package overrides",
        "Готовить крейт к публикации: SemVer, cargo package, cargo publish, cargo yank, cargo owner",
        "Писать build.rs с rerun-if-changed, OUT_DIR и передачей флагов линкеру",
        "Автоматизировать релиз через xtask и подключать cargo-audit, cargo-deny, cargo-outdated",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "rust",
        "cargo",
        "workspaces",
        "features",
        "публикация",
        "кросс-компиляция",
    ],
    "starter_code": code(
        r"""
        // Cargo.toml требует своего формата, поэтому стартовый пример —
        // маленькая программа, проверяющая информацию о сборке,
        // которую Cargo передаёт в код через переменные окружения.

        fn main() {
            let pkg = env!("CARGO_PKG_NAME");
            let ver = env!("CARGO_PKG_VERSION");
            let profile = if cfg!(debug_assertions) { "dev" } else { "release" };
            println!("{pkg} {ver} (профиль {profile})");
        }
        """
    ),
    "hints": [
        "Если несколько крейтов требуют разные версии зависимости, сначала посмотрите `cargo tree -d` и только потом добавляйте `[patch]`. Патч маскирует настоящую проблему конфликта версий.",
        "Features аддитивны: включение любого набора features даёт объединение, а не выбор одного варианта. Для взаимоисключающих бэкендов заводите отдельные крейты.",
        "Опубликовать крейт с зависимостью через `path` нельзя. Cargo требует `version` для каждой публикуемой зависимости, а `path` применяется только при локальной сборке.",
        "`cargo yank` не удаляет версию из индекса, а запрещает её выбирать в новых разрешениях. Уже существующий Cargo.lock продолжит использовать отозванную версию.",
    ],
    "content": [
        text(
            "Cargo — не только утилита для `cargo new` и `cargo run`, а менеджер пакетов, "
            "система сборки и платформа конфигурации, через которую в Rust-проекте задаётся "
            "всё: состав зависимостей, параметры оптимизации и даже то, какой код попадёт "
            "в компиляцию. Пока в проекте один крейт, хватает дефолтов, но со вторым крейтом, "
            "второй платформой или публикацией устройство Cargo начинает влиять на архитектуру "
            "и скорость сборки.\n\n"
            "Разработчик уровня advanced обязан понимать, откуда берётся версия зависимости, "
            "почему feature, включённая одним крейтом, «протекает» в другой, почему релизная "
            "сборка идёт долго и какие файлы войдут в пакет на crates.io.\n\n"
            "Урок охватывает workspaces, features, профили, кросс-компиляцию, публикацию, "
            "build-скрипты, компоновку релиза и автоматизацию задач."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "проектировать workspace с виртуальным манифестом, общим Cargo.lock и наследованием зависимостей;",
            "описывать аддитивные features, optional dependencies, синтаксис `dep:` и weak-зависимости;",
            "настраивать профили dev, release, test и собственные профили с LTO, strip и per-package переопределениями;",
            "готовить крейт к публикации: SemVer, `cargo package`, `cargo publish`, `cargo yank`, `cargo owner`;",
            "писать build.rs с `rerun-if-changed`, `OUT_DIR` и передачей флагов линкеру;",
            "автоматизировать проверки и релиз через `xtask`, `cargo-audit`, `cargo-deny`, `cargo-outdated`.",
        ),
        heading("Workspaces: несколько крейтов в одном репозитории"),
        text(
            "Workspace — набор крейтов, которые собираются вместе, разделяют каталог "
            "`target/` и файл `Cargo.lock`. Такой монорепозиторий удобен, когда рядом живут "
            "библиотека ядра, командная утилита и общий крейт: они зависят друг от друга "
            "через `path` и всегда используют согласованные версии сторонних библиотек.\n\n"
            "Корневой манифест в простейшем случае содержит только `[workspace]` без "
            "`[package]` — это виртуальный манифест. Ключ `members` перечисляет участников, "
            "`exclude` исключает каталоги внутри дерева, а `resolver = \"2\"` выбирает "
            "второй алгоритм разрешения features: он учитывает их отдельно для обычных "
            "зависимостей, build-скриптов и dev-тестов."
        ),
        example(
            "toml",
            """
            # Cargo.toml в корне репозитория (виртуальный манифест)
            [workspace]
            resolver = "2"
            members = ["core", "cli", "web-api", "shared-utils"]
            exclude = ["old-crate"]

            [workspace.dependencies]
            serde = { version = "1.0", features = ["derive"] }
            tokio = { version = "1.0", features = ["full"] }
            anyhow = "1.0"
            thiserror = "1.0"
            tracing = "0.1"
            """,
        ),
        text(
            "Ключевая возможность — наследование. Секция `[workspace.dependencies]` "
            "централизованно задаёт версии и features, а участники ссылаются на них через "
            "`{ workspace = true }`. Обновление serde правится в одном месте, а не в каждом "
            "манифесте; `[workspace.package]` так же наследует версию, edition и лицензию. "
            "На уровне участника можно дополнять features, не повторяя версию."
        ),
        example(
            "toml",
            """
            # core/Cargo.toml — участник workspace
            [package]
            name = "myapp-core"
            version.workspace = true
            edition.workspace = true

            [dependencies]
            serde = { workspace = true }
            thiserror = { workspace = true }

            # Дополнительная фича поверх унаследованной версии
            tokio = { workspace = true, features = ["fs"] }
            """,
        ),
        text(
            "Если центральный крейт существует, корневой `Cargo.toml` совмещает "
            "`[package]` и `[workspace]`, а остальные крейты перечисляются в `members`. "
            "Главное следствие единого `Cargo.lock`: все участники используют одну версию "
            "внешней зависимости, если это допускают SemVer-требования. Для приложений "
            "`Cargo.lock` хранят в репозитории, чтобы сборки воспроизводились."
        ),
        callout(
            "info",
            "Единый target/ и инкрементальность",
            "Все участники workspace делят каталог target/, поэтому уже собранные "
            "зависимости переиспользуются. Это заметно ускоряет сборку, но означает, "
            "что `cargo clean` в корне очищает артефакты сразу всех крейтов.",
        ),
        heading("Features: условная компиляция и аддитивность"),
        text(
            "Feature — именованный флаг сборки из секции `[features]`. Включить её можно "
            "через `--features name`, через набор `default` или через зависимость, которая "
            "требует её от нашего крейта. Выключенная feature означает, что соответствующий "
            "код не компилируется вовсе: это экономит время сборки и размер бинарника.\n\n"
            "Главное правило — аддитивность: любой набор features даёт объединение эффектов, "
            "а не выбор одного варианта, и библиотека обязана работать при любом сочетании. "
            "Поэтому features не подходят для взаимоисключающих бэкендов вроде «PostgreSQL "
            "или MySQL»: приложение и тестовая зависимость включат разные, получится смесь."
        ),
        example(
            "toml",
            """
            [features]
            default = ["std"]
            std = []
            serde = ["dep:serde"]
            async = ["dep:tokio", "std"]
            full = ["std", "serde", "async"]

            [dependencies]
            serde = { version = "1.0", optional = true, features = ["derive"] }
            tokio = { version = "1.0", optional = true, features = ["full"] }
            """,
        ),
        text(
            "Синтаксис `dep:serde` (Rust 1.60) отделяет зависимость от одноимённой "
            "неявной feature: запись `serde = [\"dep:serde\", \"serde/derive\"]` включает "
            "сам крейт и его feature, не создавая цикл. Слабая зависимость "
            "(`weak = true`, Rust 1.73) позволяет «увидеть» feature, включённую кем-то "
            "другим, но не тянуть зависимость самому — так библиотека подключает "
            "дополнительные слои, только если приложение уже использует tracing."
        ),
        example(
            "toml",
            """
            [dependencies]
            tracing = { version = "0.1", optional = true, default-features = false }
            # weak: не включает tracing, но зато видит его в графе
            tracing-subscriber = { version = "0.3", optional = true, weak = true }

            [features]
            tracing-support = ["dep:tracing", "tracing-subscriber/std"]
            """,
        ),
        text(
            "В коде features проверяются атрибутом `#[cfg(feature = \"name\")]`, "
            "а комбинировать условия позволяют `all`, `any` и `not` вместе с проверками "
            "платформы. `cfg` работает на этапе разбора, поэтому выключенный модуль "
            "не требует даже своих зависимостей."
        ),
        example(
            "rust",
            """
            #[cfg(feature = "serde")]
            use serde::{Deserialize, Serialize};

            #[cfg(feature = "serde")]
            #[derive(Serialize, Deserialize)]
            pub struct Config {
                pub name: String,
                pub retries: u32,
            }

            #[cfg(all(feature = "async", target_os = "linux"))]
            pub async fn serve() {
                println!("server: асинхронная Linux-ветка");
            }

            #[cfg(not(feature = "async"))]
            pub fn serve_blocking() {
                println!("server: синхронная реализация");
            }

            pub fn describe_build() {
                #[cfg(feature = "serde")]
                println!("serde включена");
                #[cfg(not(feature = "serde"))]
                println!("serde выключена");
            }

            fn main() {
                describe_build();
            }
            """,
        ),
        text(
            "Вывод при `cargo run` без указания features:",
        ),
        text("Вывод: serde выключена"),
        heading("Профили сборки"),
        text(
            "Профиль — набор параметров компиляции. Встроенных профилей четыре: `dev` "
            "(по умолчанию), `test`, `bench` и `release`. `dev` оптимизирует скорость "
            "компиляции: `opt-level = 0`, проверки переполнения включены, отладка сохранена. "
            "`release` делает наоборот, из-за чего паника при переполнении `i32` превращается "
            "в тихое переполнение. С Rust 1.57 собственные профили объявляются через "
            "`inherits` — так получают, например, профиль CI с оптимизацией, но с отладкой "
            "и проверками переполнения."
        ),
        example(
            "toml",
            """
            [profile.dev]
            opt-level = 0
            debug = true
            overflow-checks = true

            [profile.release]
            opt-level = 3
            lto = "thin"
            codegen-units = 1
            panic = "abort"
            strip = true

            [profile.test]
            inherits = "dev"
            opt-level = 1

            [profile.ci]
            inherits = "release"
            debug = true
            overflow-checks = true

            [profile.release.package."*"]
            opt-level = 3

            [profile.release.package."serde"]
            opt-level = "s"
            """,
        ),
        text(
            "Параметр `lto` включает межмодульную оптимизацию: `thin` даёт почти всю выгоду "
            "от встраивания через границы крейтов при приемлемом времени сборки, `fat` "
            "собирается дольше. `codegen-units = 1` заставляет компилятор обрабатывать крейт "
            "одной единицей кодогенерации: больше контекста для оптимизатора, но медленнее. "
            "`panic = \"abort\"` убирает размотку стека и уменьшает бинарник, запрещая "
            "`catch_unwind`. Секция `[profile.release.package.\"*\"]` настраивает оптимизацию "
            "зависимостей отдельно. Профиль применяется флагом `--profile ci`."
        ),
        table(
            ["Параметр", "dev", "release", "Что даёт"],
            [
                ["`opt-level`", "0", "3", "Уровень оптимизации кода"],
                ["`debug`", "true", "false", "Отладочные символы для gdb/lldb"],
                ["`overflow-checks`", "true", "false", "Паника при переполнении целых"],
                ["`lto`", "false", "`\"thin\"`", "Оптимизация между крейтами"],
                ["`codegen-units`", "256", "16 (или 1)", "Параллелизм кодогенерации"],
                ["`panic`", "`\"unwind\"`", "`\"unwind\"`", "Размотка стека или abort"],
            ],
        ),
        heading("Кросс-компиляция"),
        text(
            "Кросс-компиляция — сборка бинарника под платформу, отличную от текущей. "
            "Цель задаётся тройкой вида `архитектура-производитель-система`, например "
            "`x86_64-unknown-linux-musl`. `rustup target add` скачивает стандартную "
            "библиотеку цели, после чего `cargo build --target ...` собирает код. "
            "Линкер ищется в системе, и именно его чаще всего не хватает: компилятор "
            "делает объектный файл, а слинковать его должен подходящий `ld`.\n\n"
            "Настройки хранятся в `.cargo/config.toml`: секция `[target.<triple>]` "
            "задаёт `linker` и `runner` (последний нужен, чтобы `cargo test` запускал "
            "тесты через QEMU), а `[build] target` делает цель значением по умолчанию."
        ),
        example(
            "bash",
            """
            # Статически слинкованный Linux-бинарник
            rustup target add x86_64-unknown-linux-musl
            rustup target add aarch64-unknown-linux-gnu

            cargo build --release --target x86_64-unknown-linux-musl
            """,
        ),
        example(
            "toml",
            """
            # .cargo/config.toml
            [build]
            target = "x86_64-unknown-linux-musl"

            [target.x86_64-unknown-linux-musl]
            linker = "x86_64-linux-musl-gcc"

            [target.aarch64-unknown-linux-gnu]
            linker = "aarch64-linux-gnu-gcc"
            runner = "qemu-aarch64"

            [target.wasm32-unknown-unknown]
            rustflags = ["-C", "link-arg=-s"]
            """,
        ),
        text(
            "Для сложных целей удобен `cross` — тот же `cargo`, но со сборкой "
            "в Docker-образе с готовым тулчейном; конфигурация берётся из обычного "
            "`.cargo/config.toml`. Альтернатива — `zig cc` в роли универсального "
            "кросс-линкера, который знает многие платформы сразу. В коде цель "
            "проверяется через `cfg(target_os = ...)`, в build.rs — через `TARGET`."
        ),
        example(
            "rust",
            """
            #[cfg(target_arch = "wasm32")]
            pub fn platform_name() -> &'static str {
                "WebAssembly"
            }

            #[cfg(all(target_os = "linux", target_arch = "x86_64"))]
            pub fn platform_name() -> &'static str {
                "Linux x86_64"
            }

            #[cfg(all(target_os = "windows", target_env = "gnu"))]
            pub fn platform_name() -> &'static str {
                "Windows (MinGW)"
            }

            #[cfg(not(any(
                target_arch = "wasm32",
                all(target_os = "linux", target_arch = "x86_64"),
                all(target_os = "windows", target_env = "gnu"),
            )))]
            pub fn platform_name() -> &'static str {
                "другая платформа"
            }

            fn main() {
                println!("сборка для: {}", platform_name());
            }
            """,
        ),
        text("Вывод на типичном Linux-хосте при обычной сборке:"),
        text("Вывод: сборка для: Linux x86_64"),
        heading("Публикация на crates.io"),
        text(
            "Публикация начинается с метаданных: crates.io требует `description`, "
            "`license` в формате SPDX (`MIT OR Apache-2.0`), `repository`, ограниченное "
            "число `keywords` и `categories`. Поле `exclude` перечисляет шаблоны, которые "
            "не попадут в архив. `cargo package --list` показывает состав пакета, "
            "а `cargo package` собирает `.crate` в `target/package/` и проверяет сборку "
            "из архива, выявляя забытые файлы.\n\n"
            "Версии подчиняются SemVer: до 1.0.0 минорное обновление может ломать "
            "совместимость, после — MAJOR ломает, MINOR добавляет функциональность, "
            "PATCH исправляет ошибки. Предрелизы вроде `1.0.0-rc.1` не выбираются "
            "автоматически без явного требования."
        ),
        example(
            "toml",
            """
            [package]
            name = "my-awesome-crate"
            version = "0.1.0"
            edition = "2021"
            license = "MIT OR Apache-2.0"
            description = "Безопасный разбор конфигурационных файлов"
            repository = "https://github.com/user/my-awesome-crate"
            documentation = "https://docs.rs/my-awesome-crate"
            keywords = ["config", "parser"]
            categories = ["parsing", "config"]
            exclude = ["**/tests/fixtures/**", ".github/**", "benches/**"]

            [dependencies]
            serde = { version = "1.0", features = ["derive"] }
            """,
        ),
        example(
            "bash",
            """
            cargo package --list          # что попадёт в архив
            cargo package                 # создать .crate в target/package/
            cargo publish --dry-run       # полная проверка без отправки
            cargo login                   # API-токен (хранится в ~/.cargo/credentials.toml)
            cargo publish                 # публикация

            cargo publish -p myapp-core   # конкретный крейт в workspace
            """,
        ),
        text(
            "После публикации версия незыблема: заменить код под тем же номером нельзя, "
            "так как Cargo.lock зафиксировал контрольную сумму. Ошибочную версию отзывают "
            "`cargo yank`, которая запрещает её выбирать в новых разрешениях, но не удаляет "
            "из индекса; отзыв снимается через `--undo`. Соавторами управляет `cargo owner`. "
            "В workspace публикация идёт в порядке зависимостей, поэтому сначала "
            "публикуются крейты без внутренних зависимостей."
        ),
        example(
            "bash",
            """
            cargo yank --vers 1.0.1
            cargo yank --vers 1.0.1 --undo

            cargo owner --list
            cargo owner --add github:my-org:maintainers
            cargo owner --remove github:old-user
            """,
        ),
        callout(
            "warning",
            "path-зависимость не публикуется",
            "Если в `[dependencies]` указано `foo = { path = \"../foo\" }` без `version`, "
            "`cargo publish` завершится ошибкой. Публикуемый крейт обязан указывать "
            "версию для каждой внешней зависимости; `path` применяется только при "
            "локальной сборке, а в опубликованном манифесте версия является "
            "основным источником.",
        ),
        heading("Патчи зависимостей и управление версиями"),
        text(
            "Когда баг найден в чужом крейте, секция `[patch.crates-io]` подменяет "
            "источник зависимости, не меняя код: локальный форк указывается через `path`, "
            "коммит — через `git` с `rev`. Cargo переразрешит граф, будто версия пришла "
            "из crates.io; тот же приём тестирует неопубликованную ветку. Патч должен "
            "указывать совместимую версию. Устаревшая `[replace]` делала похожее "
            "по идентификатору `имя:версия`. Для обновления достаточно `cargo update` "
            "с `-p` и `--precise`, а `cargo tree -d` показывает дубликаты версий."
        ),
        example(
            "toml",
            """
            [patch.crates-io]
            broken-crate = { path = "../fixed-broken-crate" }
            another-crate = { git = "https://github.com/user/repo", rev = "abc1234" }
            """,
        ),
        example(
            "bash",
            """
            cargo update                       # до последних совместимых версий
            cargo update -p serde              # только serde
            cargo update -p serde --precise 1.0.197
            cargo tree -d                      # дубликаты версий в графе
            cargo tree -i openssl-sys          # кто тянет крейт
            """,
        ),
        heading("build.rs: код, который выполняется при сборке"),
        text(
            "Build-скрипт — Rust-программа, которая выполняется до сборки крейта, "
            "а её вывод Cargo читает как инструкции. `cargo:rerun-if-changed=<путь>` "
            "перезапускает скрипт при изменении файла, `cargo:rustc-link-search` "
            "и `cargo:rustc-link-lib` передают линкеру пути и библиотеки, "
            "`cargo:rustc-cfg` объявляет собственный cfg-флаг, `cargo:rustc-env` "
            "задаёт переменную для `env!`. Каталог для сгенерированного кода приходит "
            "через `OUT_DIR` и подключается макросом `include!`. Если ни одной директивы "
            "`rerun-if-changed` не напечатано, скрипт перезапускается при любом изменении "
            "файлов пакета, замедляя инкрементальную сборку."
        ),
        example(
            "rust",
            """
            // build.rs — выполняется во время `cargo build`
            use std::path::PathBuf;

            fn main() {
                println!("cargo:rerun-if-changed=src/native/config.txt");

                // Читаем файл и превращаем его в cfg-флаг
                let target = std::env::var("TARGET").unwrap_or_default();
                if target.contains("musl") {
                    println!("cargo:rustc-cfg=musl_target");
                }

                // Сгенерированный файл в OUT_DIR
                let out_dir = PathBuf::from(std::env::var("OUT_DIR").unwrap());
                let generated = "pub const BUILD_TAG: &str = \\"generated-by-build\\";";
                std::fs::write(out_dir.join("build_info.rs"), generated).unwrap();

                println!("cargo:rustc-env=MYAPP_BUILD_TAG=generated-by-build");
            }
            """,
        ),
        example(
            "rust",
            """
            // src/main.rs — использует результаты build-скрипта
            include!(concat!(env!("OUT_DIR"), "/build_info.rs"));

            #[cfg(musl_target)]
            const LINKAGE: &str = "статическая (musl)";

            #[cfg(not(musl_target))]
            const LINKAGE: &str = "динамическая (gnu)";

            fn main() {
                println!("тег сборки: {BUILD_TAG}");
                println!("тег из окружения: {}", env!("MYAPP_BUILD_TAG"));
                println!("линковка: {LINKAGE}");
            }
            """,
        ),
        text("Вывод на Linux-хосте с glibc:"),
        text(
            "Вывод: тег сборки: generated-by-build\n"
            "тег из окружения: generated-by-build\n"
            "линковка: динамическая (gnu)"
        ),
        text(
            "Build-скрипт выполняется с правами пользователя и может делать что угодно, "
            "поэтому незнакомый крейт с `build.rs` требует доверия — это одна из причин, "
            "по которым проверяют источники зависимостей. Для компиляции нативного "
            "C-кода применяется крейт `cc` из `[build-dependencies]`: эти зависимости "
            "нужны только самому скрипту и не попадают в дерево крейта."
        ),
        example(
            "toml",
            """
            [build-dependencies]
            cc = "1.0"

            [dependencies]
            # Здесь крейт cc не нужен
            """,
        ),
        heading("Приватные реестры и vendoring"),
        text(
            "Для внутреннего кода используется приватный реестр: он объявляется "
            "в `.cargo/config.toml` в секции `[registries]` с URL SPARSE-индекса "
            "или git-репозитория, зависимость ссылается на него через `registry`, "
            "а `cargo login --registry=my-private` сохраняет токен в "
            "`~/.cargo/credentials.toml`.\n\n"
            "Заменить crates.io целиком позволяет `[source.crates-io] replace-with` "
            "— например, на зеркало или на каталог `vendor/`. Команда `cargo vendor` "
            "скачивает исходники всех зависимостей в репозиторий, после чего сборка "
            "не обращается к сети: это стандартный приём для изолированных сборок "
            "и аудита сторонних исходников."
        ),
        example(
            "toml",
            """
            # .cargo/config.toml
            [registries]
            my-private = { index = "sparse+https://crates.example.com/index/" }

            [source.crates-io]
            replace-with = "vendored-sources"

            [source.vendored-sources]
            directory = "vendor"
            """,
        ),
        text(
            "В манифесте такая зависимость выглядит как обычная, но с полем `registry`. "
            "`cargo vendor` печатает готовый фрагмент конфигурации, который вставляется "
            "в `.cargo/config.toml`."
        ),
        example(
            "toml",
            """
            [dependencies]
            internal-macros = { version = "0.3", registry = "my-private" }
            """,
        ),
        heading("Плагины Cargo и автоматизация"),
        text(
            "Подкоманды Cargo расширяются исполняемыми файлами вида `cargo-<name>` "
            "в `PATH`. Установленные глобально подкоманды могут обновиться и сломать "
            "воспроизводимость, поэтому для команды версии фиксируют в CI-образе "
            "или ставят с флагом `--locked`. `cargo-expand` раскрывает макросы до "
            "компиляции, `cargo-audit` сверяет `Cargo.lock` с базой уязвимостей RustSec, "
            "`cargo-deny` проверяет лицензии, бан-лист и дубликаты версий, "
            "`cargo-outdated` показывает устаревшие зависимости."
        ),
        example(
            "toml",
            """
            # deny.toml
            [advisories]
            yanked = "deny"
            unmaintained = "warn"

            [licenses]
            allow = ["MIT", "Apache-2.0", "BSD-3-Clause"]
            deny = ["GPL-3.0-only", "AGPL-3.0-only"]

            [bans]
            multiple-versions = "warn"
            wildcards = "deny"
            deny = [{ name = "openssl" }]
            """,
        ),
        example(
            "bash",
            """
            cargo install cargo-audit cargo-deny cargo-outdated cargo-expand --locked
            cargo audit
            cargo deny check
            cargo outdated
            cargo expand --lib myapp-core
            """,
        ),
        text(
            "Для задач сложнее одиночной команды применяют паттерн xtask: в workspace "
            "заводится крейт `xtask`, который пишет на Rust и выполняет генерацию кода, "
            "проверки и релиз. Запуск выглядит как `cargo xtask release --version 1.2.0`. "
            "Преимущества — типизированные аргументы и те же библиотеки Rust без внешнего "
            "инструмента. Чтобы команда работала, в `.cargo/config.toml` регистрируется "
            "алиас, раскрывающийся в `run -p xtask`."
        ),
        example(
            "toml",
            """
            # .cargo/config.toml — алиас для `cargo xtask`
            [alias]
            xtask = "run --package xtask --quiet --"
            """,
        ),
        example(
            "rust",
            """
            // xtask/src/main.rs
            use std::process::Command;

            fn main() -> Result<(), Box<dyn std::error::Error>> {
                let task = std::env::args().nth(1).unwrap_or_else(|| "help".into());
                match task.as_str() {
                    "check" => {
                        run(&["fmt", "--all", "--check"])?;
                        run(&["clippy", "--workspace", "--all-targets", "--", "-D", "warnings"])?;
                        run(&["test", "--workspace"])?;
                    }
                    "release" => {
                        let version = std::env::args().nth(2).unwrap_or_else(|| "0.1.0".into());
                        run(&["build", "--workspace", "--release"])?;
                        println!("релиз v{version} готов к упаковке");
                    }
                    _ => println!("доступные задачи: check, release"),
                }
                Ok(())
            }

            fn run(args: &[&str]) -> Result<(), Box<dyn std::error::Error>> {
                println!("cargo {}", args.join(" "));
                let status = Command::new("cargo").args(args).status()?;
                if !status.success() {
                    return Err(format!("команда завершилась со статусом {:?}", status.code()).into());
                }
                Ok(())
            }
            """,
        ),
        text(
            "Альтернативы xtask — `just` с коротким синтаксисом `justfile` и "
            "`cargo-make` с задачами в TOML. Если задача требует логики на Rust "
            "и доступа к метаданным workspace, выбирают xtask; если это просто "
            "набор команд — достаточно `just`."
        ),
        callout(
            "success",
            "Порядок внедрения в команду",
            "Начните с `cargo fmt --check` и `cargo clippy -D warnings`, "
            "добавьте `cargo deny check` в CI, затем заведите xtask для "
            "повторяющихся операций. Постепенно переносите шаги релиза "
            "из документации в код, чтобы процесс не зависел от памяти "
            "одного разработчика.",
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                [
                    "`resolver` не указан в workspace",
                    "Старый resolver объединяет features build-скриптов и основных зависимостей",
                    "`resolver = \"2\"` (или `\"3\"` для edition 2024) в корне",
                ],
                [
                    "Взаимоисключающие бэкенды через features",
                    "При объединении набора features компилируются оба бэкенда",
                    "Отдельные крейты или generic-параметры вместо features",
                ],
                [
                    "`path`-зависимость без `version`",
                    "`cargo publish` отклоняет манифест",
                    "Указывать `{ version = \"1.0\", path = \"../foo\" }`",
                ],
                [
                    "Ключ `[replace]` вместо `[patch]`",
                    "Устаревший синтаксис, конфликты с современным Cargo",
                    "`[patch.crates-io]` с `path` или `git`",
                ],
                [
                    "build.rs без `rerun-if-changed`",
                    "Инкрементальная сборка перезапускает скрипт на любое изменение",
                    "Объявлять конкретные входные файлы",
                ],
                [
                    "Публикация без `--dry-run`",
                    "Ошибки манифеста выясняются после отправки, версия уже занята",
                    "`cargo package --list` и `cargo publish --dry-run`",
                ],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняются в отдельном тестовом репозитории. "
            "Проверяйте результат командами `cargo build`, `cargo tree`, "
            "`cargo package --list` и `cargo metadata`.",
        ),
        numbered(
            "Создайте workspace с крейтами `core` и `cli`, вынесите версию и `serde` в `[workspace.dependencies]`, подключите их через `{ workspace = true }` и убедитесь, что `cargo build --workspace` собирает оба крейта.",
            "Добавьте в `core` features `default = [\"std\"]`, `std = []` и `json = [\"dep:serde_json\"]` с optional-зависимостью; соберите проект с `--no-default-features` и с `--features json` и сравните `cargo tree -e features`.",
            "Объявите профиль `ci` наследующий `release`, но с `debug = true` и `overflow-checks = true`; соберите `cargo build --profile ci` и проверьте, что паника при переполнении `i32` возникает.",
            "Напишите build.rs, который записывает в `OUT_DIR` файл с константой-датой, подключает его через `include!` и печатает значение в `main`; убедитесь, что повторная сборка без изменений не перезапускает скрипт.",
            "Подготовьте библиотечный крейт к публикации: заполните метаданные, добавьте `exclude`, выполните `cargo package --list` и `cargo publish --dry-run` и убедитесь, что в архив не попали тестовые данные.",
        ),
        text("Пример ожидаемого вывода для третьего задания:"),
        example(
            "text",
            """
            $ cargo build --profile ci
               Compiling demo v0.1.0 (/tmp/demo)
                Finished `ci` profile [optimized + debuginfo] target(s) in 0.42s
            $ ./target/ci/demo
            поток 'main' запаниковал: attempt to add with overflow
            """,
        ),
        callout(
            "info",
            "Подсказка к заданию 2",
            "Команда `cargo tree -e features` показывает, кто и какую feature "
            "включил. Если `serde_json` появляется в дереве без `--features json`, "
            "значит optional-зависимость включена где-то ещё по умолчанию.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Зачем в корне workspace указывают `resolver = \"2\"` и чем он отличается от прежнего поведения?",
            "Почему features нельзя использовать для взаимоисключающих бэкендов?",
            "Что произойдёт, если опубликовать крейт с зависимостью `{ path = \"../foo\" }` без версии?",
            "Почему `cargo yank` не удаляет версию, и как проект с уже зафиксированным Cargo.lock на неё отреагирует?",
            "Какой директиве build.rs нужно отдать путь к файлу, чтобы Cargo перезапускал скрипт только при его изменении, и где находится каталог для сгенерированного кода?",
        ),
        heading("Ответы", 3),
        numbered(
            "Второй resolver учитывает features отдельно для обычных зависимостей, build-скриптов и dev-зависимостей; первый объединял их, из-за чего feature, нужная только для тестов, включалась в итоговый бинарник.",
            "Features аддитивны: Cargo объединяет все запрошенные флаги, и библиотека не управляет этим набором. Для выбора одного из нескольких бэкендов нужны отдельные крейты или параметризация кодом.",
            "Публикация завершится ошибкой: в опубликованном манифесте не может быть `path`-зависимости без версии, поскольку чужой машины этого пути не существует.",
            "Yank лишь запрещает выбирать версию в новых разрешениях, но оставляет её в индексе для воспроизводимости. Cargo.lock продолжит использовать отозванную версию, пока её не обновят через `cargo update`.",
            "Директива `cargo:rerun-if-changed=<путь>` задаёт отслеживаемый файл, а путь к сгенерированному коду приходит в переменной окружения `OUT_DIR`; подключают его через `include!(concat!(env!(\"OUT_DIR\"), \"/file.rs\"))`.",
        ),
        heading("Итоги"),
        bullets(
            "Workspace объединяет крейты общим `target/`, `Cargo.lock` и секциями `[workspace.dependencies]` и `[workspace.package]`; корень может быть виртуальным манифестом.",
            "Features аддитивны и вычисляются при сборке: `dep:` отделяет зависимость от одноимённой feature, `weak` подключается к уже выбранной зависимости.",
            "Профили `dev`, `test`, `bench`, `release` и собственные через `inherits` управляют `opt-level`, `lto`, `codegen-units`, `panic` и `strip`.",
            "Кросс-компиляция строится на `rustup target add` и `.cargo/config.toml` с `linker` и `runner`; `cross` и `zig cc` упрощают окружение.",
            "Публикация требует метаданных, SemVer-дисциплины и проверки через `cargo package`; ошибочные версии отзывают через `cargo yank`, владельцев правят через `cargo owner`.",
            "`build.rs` печатает директивы `cargo:...`, пишет сгенерированный код в `OUT_DIR` и требует явных `rerun-if-changed` для быстрой инкрементальной сборки.",
            "`[patch.crates-io]`, приватные registry и `cargo vendor` управляют источниками зависимостей; `cargo-audit`, `cargo-deny` и `cargo-outdated` контролируют их состояние.",
            "Автоматизация задач выполняется через xtask, `just` или `cargo-make`, а подкоманды Cargo расширяются бинарниками `cargo-<name>`.",
        ),
        heading("Что дальше"),
        text(
            "Экосистема Cargo освоена: вы умеете организовать монорепозиторий, "
            "управлять features, публиковать крейты и автоматизировать релиз. "
            "Следующий урок посвящён производительности и надёжности: профилированию, "
            "работе с аллокатором и кэшем, уменьшению размера бинарника. Многие его "
            "приёмы опираются на профили сборки и флаги `rustflags` из этого урока."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "The Cargo Book: Workspaces — doc.rust-lang.org/cargo/reference/workspaces.html",
            "The Cargo Book: Features — doc.rust-lang.org/cargo/reference/features.html",
            "The Cargo Book: Profiles — doc.rust-lang.org/cargo/reference/profiles.html",
            "The Cargo Book: Build Scripts — doc.rust-lang.org/cargo/reference/build-scripts.html",
            "Semantic Versioning 2.0.0 — semver.org",
            "RustSec Advisory Database — rustsec.org",
            "cargo-deny — github.com/EmbarkStudios/cargo-deny",
            "cargo-xtask pattern — github.com/matklad/cargo-xtask",
        ),
    ],
}
