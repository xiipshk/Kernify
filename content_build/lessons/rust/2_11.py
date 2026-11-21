"""Урок 11 курса Rust: проект — параллельный веб-краулер."""

from content_build.lesson_kit import (
    bullets,
    callout,
    check_yourself,
    code,
    example,
    heading,
    numbered,
    outro,
    table,
    text,
)

LESSON = {
    "language": "rust",
    "program_order": 2,
    "topic_order": 11,
    "name": "2.11. Проект",
    "slug": "rust-2-11-проект",
    "short_description": (
        "Практический проект: собираем параллельный веб-краулер на async Rust "
        "с токио, reqwest, scraper, конфигурацией TOML, ретраями и тестами."
    ),
    "topic_name": "Проект",
    "topic_description": (
        "Полный цикл разработки приложения на Rust: разбиение кода на модули, "
        "асинхронные HTTP-запросы с ограничением параллелизма через Semaphore, "
        "парсинг HTML, хранение результатов в JSON, структурированное логирование "
        "и интеграционные тесты."
    ),
    "learning_objectives": [
        "Планировать структуру проекта на Rust: библиотека, бинарник, модули и тесты",
        "Описывать конфигурацию в TOML и десериализовать её через serde",
        "Организовать предметные ошибки через thiserror и общий тип Result",
        "Ограничивать параллелизм асинхронных задач семафором из токио",
        "Писать ретраи с экспоненциальной задержкой и различать временные ошибки",
        "Покрывать компоненты интеграционными тестами и запускать их через cargo test",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "rust",
        "проект",
        "tokio",
        "async",
        "reqwest",
        "краулер",
    ],
    "starter_code": code(
        r"""
        use std::sync::Arc;
        use std::time::Duration;

        #[derive(Debug, Clone)]
        pub struct Settings {
            pub max_concurrent: usize,
            pub delay: Duration,
            pub max_depth: usize,
        }

        impl Default for Settings {
            fn default() -> Self {
                Self {
                    max_concurrent: 4,
                    delay: Duration::from_millis(100),
                    max_depth: 2,
                }
            }
        }

        #[tokio::main]
        async fn main() {
            let settings = Arc::new(Settings::default());
            println!("Параллельных запросов: {}", settings.max_concurrent);
            println!("Максимальная глубина: {}", settings.max_depth);
        }
        """
    ),
    "hints": [
        "Семафор выдаёт разрешения через acquire(). Разрешение освобождается автоматически, когда переменная выходит из области видимости.",
        "Не держите разрешение семафора во время сопрограммной паузы дольше, чем нужно: если взять его перед sleep, все задачи будут ждать друг друга.",
        "Для таймаута одного запроса используйте tokio::time::timeout вместо ручного опроса.",
        "Тесты размещайте в каталоге tests и обращайтесь к модулям через имя крейта, а не через crate::.",
    ],
    "content": [
        text(
            "Этот урок собирает воедино весь уровень: владение и ссылки, трейты, "
            "умные указатели, обработку ошибок, файлы и сериализацию, асинхронность "
            "и конкурентность. Мы построим параллельный веб-краулер — программу, "
            "которая обходит сайты, скачивает страницы, извлекает ссылки и сохраняет "
            "результат на диск.\n\n"
            "Краулер — удобный учебный пример. У него есть конфигурация, сеть, "
            "ограничение нагрузки, повторные попытки при сбоях, хранение состояния, "
            "логирование и тесты. Каждый кусок по отдельности мы уже встречали, "
            "а здесь важно собрать их в цельный проект с понятными границами модулей.\n\n"
            "Мы пойдём от пустого каталога к запущенной программе: сначала структура "
            "и манифест, затем конфигурация и типы ошибок, потом загрузчик и парсер, "
            "хранилище и планировщик обхода, и наконец входная точка и тесты. "
            "Все примеры компилируются и запускаются, кроме тех, что обращаются "
            "к живому сайту."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "раскладывать приложение на модули так, что библиотека переиспользуется в тестах, а бинарник остаётся тонким;",
            "подключать асинхронные зависимости в Cargo.toml и включать только нужные возможности крейтов;",
            "читать конфигурацию из TOML в типизированную структуру через serde и проверять её инварианты;",
            "проектировать перечисление ошибок с thiserror и возвращать единый `Result` из всех слоёв;",
            "ограничивать число одновременных запросов семафором из `tokio::sync` и не блокировать рантайм;",
            "реализовывать ретраи с экспоненциальной задержкой и корректно завершать работу по сигналу.",
        ),
        heading("Замысел проекта"),
        text(
            "Краулер получает стартовые адреса, скачивает страницы, находит ссылки "
            "и идёт по ним вглубь до заданного предела. Путь до каждой страницы "
            "делает один шаг: загрузка, разбор, сохранение, постановка новых адресов в работу. "
            "Из этого получается конвейер, который удобно резать на модули.\n\n"
            "Ограничения, которые мы закладываем сразу, важнее самой логики обхода. "
            "Краулер по определению генерирует тысячи сетевых запросов, и без потолка "
            "параллелизма он завалит сервер и собственный сетевой стек. "
            "Нужен семафор, пауза между запросами и таймаут. Нужны ретраи, потому что "
            "сеть ошибается регулярно. И нужна возможность остановиться по Ctrl+C, "
            "поскольку обход длится минуты, а не секунды.\n\n"
            "Разделим обязанности так: `config` знает о файле настроек, `error` "
            "описывает все способы отказа, `fetcher` умеет скачивать, `parser` — "
            "извлекать ссылки, `storage` — накапливать результат, `crawler` — решать, "
            "что скачивать. Каждый модуль можно протестировать отдельно от остальных."
        ),
        heading("Структура проекта и манифест"),
        text(
            "Начнём с `cargo new crawler`. По умолчанию Cargo создаёт только бинарник. "
            "Мы добавим вторую точку входа — библиотеку `src/lib.rs`. "
            "Библиотека экспортирует модули наружу, бинарник `main.rs` их подключает, "
            "а интеграционные тесты в каталоге `tests` импортируют те же модули как внешний крейт.\n\n"
            "Дерево каталогов выглядит так:"
        ),
        example(
            "text",
            """
            crawler/
            ├── Cargo.toml
            ├── config.toml
            ├── src/
            │   ├── main.rs
            │   ├── lib.rs
            │   ├── config.rs
            │   ├── crawler.rs
            │   ├── error.rs
            │   ├── fetcher.rs
            │   ├── parser.rs
            │   └── storage.rs
            └── tests/
                └── integration.rs
            """,
        ),
        text(
            "Файл `lib.rs` состоит из объявлений модулей. Ключевое слово `pub` "
            "делает их видимыми для бинарника и для тестов:"
        ),
        example(
            "rust",
            """
            // src/lib.rs
            pub mod config;
            pub mod crawler;
            pub mod error;
            pub mod fetcher;
            pub mod parser;
            pub mod storage;
            """,
        ),
        text(
            "Манифест подключает зависимости. Для асинхронного HTTP нужен `tokio` "
            "с рантаймом и макросами, `reqwest` с поддержкой TLS через rustls, "
            "`scraper` для разбора HTML, `serde` и `toml` для конфигурации, "
            "`anyhow` для прикладного кода и `thiserror` для библиотечных ошибок.\n\n"
            "Возможности крейта (`features`) включаются избирательно: так сборка "
            "быстрее, а бинарник меньше. Например, `reqwest` по умолчанию тянет "
            "системный OpenSSL, а включение `rustls-tls` позволяет собирать "
            "проект без внешних C-библиотек."
        ),
        example(
            "toml",
            """
            # Cargo.toml
            [package]
            name = "crawler"
            version = "0.1.0"
            edition = "2021"

            [dependencies]
            tokio = { version = "1", features = ["macros", "rt-multi-thread", "signal", "time", "sync"] }
            reqwest = { version = "0.12", features = ["rustls-tls"] }
            scraper = "0.18"
            url = "2.5"
            serde = { version = "1", features = ["derive"] }
            serde_json = "1"
            toml = "0.8"
            tracing = "0.1"
            anyhow = "1"

            [dev-dependencies]
            tempfile = "3"
            """,
        ),
        callout(
            "info",
            "Зачем нужна библиотека",
            "Если весь код лежит в `main.rs`, интеграционные тесты не смогут к нему "
            "обратиться: бинарник — отдельный крейт без публичного интерфейса. "
            "Вынесите логику в `lib.rs`, оставьте в `main.rs` разбор аргументов "
            "и запуск — и тесты получат доступ к модулям.",
        ),
        heading("Конфигурация в TOML"),
        text(
            "Настройки выносим в файл, чтобы не пересобирать программу ради изменения "
            "лимитов. Формат TOML читается человеком и напрямую ложится на структуры Rust: "
            "секции становятся вложенными полями."
        ),
        example(
            "toml",
            """
            # config.toml
            [crawler]
            start_urls = ["https://example.com"]
            max_depth = 2
            max_concurrent = 8
            request_timeout_secs = 10
            delay_ms = 150
            user_agent = "RustCrawler/1.0"

            [storage]
            path = "crawl_results.json"

            [logging]
            level = "info"
            """,
        ),
        text(
            "Структура с атрибутом `Deserialize` позволяет прочитать весь файл одной "
            "функцией `toml::from_str`. Обратите внимание на поле `type`: это ключевое "
            "слово языка Rust, поэтому в идентификаторе используется сырой вид `r#type`. "
            "Имя поля в файле при этом остаётся `type`, так как сырой идентификатор "
            "в serde сравнивается без префикса.\n\n"
            "После чтения проверяем инварианты: количество одновременных запросов "
            "не может быть нулевым, иначе семафор сразу заблокируется навсегда. "
            "Такие проверки возвращают понятную ошибку конфигурации."
        ),
        example(
            "rust",
            """
            // src/config.rs
            use serde::Deserialize;

            #[derive(Debug, Deserialize, Clone)]
            pub struct CrawlerConfig {
                pub start_urls: Vec<String>,
                pub max_depth: usize,
                pub max_concurrent: usize,
                pub request_timeout_secs: u64,
                pub delay_ms: u64,
                pub user_agent: String,
            }

            #[derive(Debug, Deserialize, Clone)]
            pub struct StorageConfig {
                pub path: String,
            }

            #[derive(Debug, Deserialize, Clone)]
            pub struct Config {
                pub crawler: CrawlerConfig,
                pub storage: StorageConfig,
            }

            impl Config {
                pub fn from_str(content: &str) -> Result<Self, String> {
                    let config: Config =
                        toml::from_str(content).map_err(|e| e.to_string())?;
                    if config.crawler.max_concurrent == 0 {
                        return Err("max_concurrent должен быть больше нуля".into());
                    }
                    if config.crawler.start_urls.is_empty() {
                        return Err("нужен хотя бы один стартовый адрес".into());
                    }
                    Ok(config)
                }
            }
            """,
        ),
        text(
            "Проверим разбор на минимальном файле. Программа печатает значения, "
            "которые попали в структуру:"
        ),
        example(
            "rust",
            """
            fn main() {
                let raw = r#"
            [crawler]
            start_urls = ["https://example.com", "https://docs.rs"]
            max_depth = 2
            max_concurrent = 4
            request_timeout_secs = 10
            delay_ms = 100
            user_agent = "RustCrawler/1.0"

            [storage]
            path = "results.json"
            "#;

                match Config::from_str(raw) {
                    Ok(cfg) => {
                        println!("адресов: {}", cfg.crawler.start_urls.len());
                        println!("параллельно: {}", cfg.crawler.max_concurrent);
                        println!("таймаут: {} с", cfg.crawler.request_timeout_secs);
                        println!("файл: {}", cfg.storage.path);
                    }
                    Err(e) => println!("ошибка конфигурации: {e}"),
                }
            }
            """,
        ),
        text(
            "Вывод:\n\n"
            "```\n"
            "адресов: 2\n"
            "параллельно: 4\n"
            "таймаут: 10 с\n"
            "файл: results.json\n"
            "```\n\n"
            "Если в файле испортить имя поля или поставить `max_concurrent = 0`, "
            "программа напечатает ошибку вместо паники. Это важное свойство "
            "конфигурации: неправильный ввод пользователя — ожидаемая ситуация, "
            "а не авария."
        ),
        heading("Ошибки проекта"),
        text(
            "В библиотеке принято описывать ошибки перечислением и реализовывать "
            "для него `std::error::Error`. Крейт `thiserror` генерирует эту реализацию "
            "из атрибутов: `#[error(...)]` задаёт текст сообщения, а `#[from]` — "
            "автоматическое преобразование из чужой ошибки через оператор `?`.\n\n"
            "Такой подход даёт вызывающему коду возможность различать причины отказа. "
            "Например, ошибка разбора HTML — повод пропустить страницу, "
            "а ошибка сети — повод повторить попытку."
        ),
        example(
            "rust",
            """
            // src/error.rs
            use thiserror::Error;

            #[derive(Error, Debug)]
            pub enum CrawlerError {
                #[error("сетевая ошибка: {0}")]
                Http(#[from] reqwest::Error),

                #[error("некорректный адрес: {0}")]
                Url(#[from] url::ParseError),

                #[error("ошибка разбора HTML: {0}")]
                Parse(String),

                #[error("ошибка ввода-вывода: {0}")]
                Io(#[from] std::io::Error),

                #[error("ошибка сериализации: {0}")]
                Json(#[from] serde_json::Error),

                #[error("превышена допустимая глубина обхода")]
                DepthExceeded,
            }

            pub type Result<T> = std::result::Result<T, CrawlerError>;
            """,
        ),
        callout(
            "info",
            "Два крейта — две роли",
            "`thiserror` используют в библиотеках: он даёт типизированные ошибки, "
            "которые вызывающий код может разобрать по вариантам. `anyhow` используют "
            "в прикладном коде и примерах: он складывает любую ошибку в один тип "
            "с цепочкой контекста. В одном проекте нормально применять оба.",
        ),
        heading("Загрузчик и повторные попытки"),
        text(
            "HTTP-клиент создаётся один раз и переиспользуется: внутри него живёт "
            "пул соединений, и новый клиент на каждый запрос сводит выгоду от "
            "keep-alive к нулю. Структура `Fetcher` хранит клиент и сама себя "
            "оборачивает в `Arc`, чтобы делить между задачами.\n\n"
            "Отдельно реализуем ретраи. Простая логика: пробуем до `max_retries + 1` "
            "раз, между попытками ждём с удвоением задержки. Экспоненциальная пауза "
            "даёт сбоящему серверу время восстановиться и не превращает всплеск "
            "ошибок в шторм повторных запросов."
        ),
        example(
            "rust",
            """
            // src/fetcher.rs
            use crate::error::{CrawlerError, Result};
            use std::time::Duration;

            pub struct Fetcher {
                client: reqwest::Client,
            }

            impl Fetcher {
                pub fn new(timeout_secs: u64, user_agent: &str) -> Result<Self> {
                    let client = reqwest::Client::builder()
                        .timeout(Duration::from_secs(timeout_secs))
                        .user_agent(user_agent)
                        .build()?;
                    Ok(Self { client })
                }

                pub async fn fetch(&self, url: &str) -> Result<String> {
                    let resp = self.client.get(url).send().await?;
                    let resp = resp.error_for_status()?;
                    Ok(resp.text().await?)
                }
            }

            impl std::fmt::Debug for Fetcher {
                fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                    f.write_str("Fetcher")
                }
            }

            #[allow(dead_code)]
            fn _check_enum(_e: CrawlerError) {}
            """,
        ),
        text(
            "Метод `error_for_status` превращает ответ 4xx и 5xx в ошибку `reqwest`, "
            "поэтому проверять код вручную не нужно. Функция повторных попыток "
            "принимает замыкание, возвращающее будущее, — так её можно тестировать "
            "без сети."
        ),
        example(
            "rust",
            """
            use std::future::Future;
            use std::time::Duration;

            pub async fn with_retry<F, Fut, T, E>(
                max_retries: u32,
                mut attempt_fn: F,
            ) -> std::result::Result<T, E>
            where
                F: FnMut() -> Fut,
                Fut: Future<Output = std::result::Result<T, E>>,
            {
                let mut last_err = None;
                for attempt in 0..=max_retries {
                    match attempt_fn().await {
                        Ok(value) => return Ok(value),
                        Err(e) => {
                            last_err = Some(e);
                            if attempt < max_retries {
                                let backoff = 100 * 2u64.pow(attempt);
                                tokio::time::sleep(Duration::from_millis(backoff)).await;
                            }
                        }
                    }
                }
                Err(last_err.expect("цикл выполнялся хотя бы раз"))
            }

            #[tokio::main]
            async fn main() {
                let counter = std::sync::atomic::AtomicU32::new(0);
                let mut calls = 0;
                let result: Result<&str, &str> = with_retry(3, || {
                    let n = counter.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
                    let _ = n;
                    calls += 1;
                    async move {
                        if calls < 3 {
                            Err("сервер занят")
                        } else {
                            Ok("готово")
                        }
                    }
                })
                .await;
                println!("{:?}", result);
            }
            """,
        ),
        text(
            "Вывод:\n\n"
            "```\n"
            "Ok(\"готово\")\n"
            "```\n\n"
            "Обратите внимание на замыкание: счётчик попыток меняется до создания "
            "будущего, а само будущее захватывает скопированное значение `calls`. "
            "Так тип замыкания остаётся `FnMut`, а возвращаемое будущее — независимым "
            "от изменяемого захвата."
        ),
        heading("Парсер ссылок"),
        text(
            "Селектор в `scraper` компилируется один раз и хранится в структуре, "
            "поскольку разбор CSS-выражения — относительно дорогая операция. "
            "Скачанный HTML разбираем в документ, затем проходим по всем элементам "
            "`a[href]`.\n\n"
            "Относительные ссылки приводим к абсолютным через `Url::parse` и `join`. "
            "Это ключевая деталь: без неё обход будет пытаться загрузить `/about`, "
            "который не является адресом в сети. Ещё отбрасываем всё, что не "
            "начинается с `http://` или `https://`: почтовые ссылки и `javascript:` "
            "нам не нужны."
        ),
        example(
            "rust",
            """
            // src/parser.rs
            use crate::error::{CrawlerError, Result};
            use scraper::{Html, Selector};
            use url::Url;

            pub struct Parser {
                link_selector: Selector,
            }

            impl Parser {
                pub fn new() -> Result<Self> {
                    let link_selector = Selector::parse("a[href]")
                        .map_err(|e| CrawlerError::Parse(e.to_string()))?;
                    Ok(Self { link_selector })
                }

                pub fn extract_links(&self, base_url: &str, html: &str) -> Result<Vec<String>> {
                    let document = Html::parse_document(html);
                    let base = Url::parse(base_url)?;
                    let mut links = Vec::new();

                    for element in document.select(&self.link_selector) {
                        if let Some(href) = element.value().attr("href") {
                            let absolute = match base.join(href) {
                                Ok(url) => url,
                                Err(_) => continue,
                            };
                            let url = absolute.to_string();
                            if url.starts_with("http://") || url.starts_with("https://") {
                                links.push(url);
                            }
                        }
                    }
                    Ok(links)
                }
            }
            """,
        ),
        text(
            "Проверим парсер на коротком фрагменте. Программа печатает только "
            "допустимые абсолютные адреса:"
        ),
        example(
            "rust",
            """
            fn main() {
                let parser = Parser::new().unwrap();
                let html = r#"
                    <html><body>
                        <a href="/about">О проекте</a>
                        <a href="https://docs.rs/tokio">Документация</a>
                        <a href="mailto:info@example.com">Почта</a>
                        <a href="#top">Наверх</a>
                    </body></html>
                "#;
                for link in parser.extract_links("https://example.com/base/", html).unwrap() {
                    println!("{link}");
                }
            }
            """,
        ),
        text(
            "Вывод:\n\n"
            "```\n"
            "https://example.com/about\n"
            "https://example.com/base/#top\n"
            "https://docs.rs/tokio\n"
            "```\n\n"
            "Адрес `#top` тоже становится абсолютным и попадает в список: формально "
            "это тот же документ, и отсеять такие варианты можно на уровне "
            "дедупликации, отбрасывая повторно встреченные адреса."
        ),
        heading("Семафор и ограничение параллелизма"),
        text(
            "`tokio::spawn` принимает будущее и запускает его независимо. "
            "Если поставить в цикл тысячу задач, все они одновременно обратятся к сети. "
            "Ограничитель — семафор: счётчик `tokio::sync::Semaphore`, который "
            "выдаёт не больше `N` разрешений одновременно.\n\n"
            "Разрешение — это RAII-значение. Когда `acquire_owned()` вернул permit, "
            "счётчик уменьшился; когда permit уничтожается, счётчик возвращается. "
            "Забыть освободить невозможно — именно поэтому семафор надёжнее ручного счётчика.\n\n"
            "Разрешение лучше брать прямо перед сетевым запросом и отпускать сразу "
            "после него. Если взять permit до длинной паузы, он будет простаивать, "
            "и реальная параллельность окажется ниже заявленной."
        ),
        example(
            "rust",
            """
            use std::sync::Arc;
            use std::time::Instant;
            use tokio::sync::Semaphore;
            use tokio::time::{sleep, Duration};

            async fn load(url: &str) -> Result<String, String> {
                sleep(Duration::from_millis(100)).await;
                if url.contains("bad") {
                    Err(format!("{url}: сервер недоступен"))
                } else {
                    Ok(format!("{url}: 1024 байта"))
                }
            }

            #[tokio::main]
            async fn main() {
                let urls: Vec<String> = (1..=8)
                    .map(|i| {
                        if i % 4 == 0 {
                            format!("https://example.com/bad/{i}")
                        } else {
                            format!("https://example.com/page/{i}")
                        }
                    })
                    .collect();

                let semaphore = Arc::new(Semaphore::new(3));
                let started = Instant::now();
                let mut tasks = Vec::new();

                for url in urls {
                    let semaphore = Arc::clone(&semaphore);
                    tasks.push(tokio::spawn(async move {
                        let _permit = semaphore.acquire_owned().await.unwrap();
                        load(&url).await
                    }));
                }

                let mut ok = 0;
                let mut failed = 0;
                for task in tasks {
                    match task.await.unwrap() {
                        Ok(line) => {
                            ok += 1;
                            println!("{line}");
                        }
                        Err(reason) => {
                            failed += 1;
                            println!("сбой: {reason}");
                        }
                    }
                }
                println!("успешно: {ok}, с ошибками: {failed}");
                println!("прошло: ~{} мс", started.elapsed().as_millis());
            }
            """,
        ),
        text(
            "Восемь задач по 100 миллисекунд при трёх разрешениях дают три волны, "
            "то есть около 300 миллисекунд вместо 100. Порядок строк в выводе "
            "недетерминирован: задачи завершаются в том порядке, в каком их отпустил "
            "планировщик."
        ),
        example(
            "text",
            """
            Вывод (порядок строк может отличаться):
            https://example.com/page/1: 1024 байта
            https://example.com/page/2: 1024 байта
            https://example.com/page/3: 1024 байта
            сбой: https://example.com/bad/4: сервер недоступен
            https://example.com/page/5: 1024 байта
            https://example.com/page/6: 1024 байта
            https://example.com/page/7: 1024 байта
            сбой: https://example.com/bad/8: сервер недоступен
            успешно: 6, с ошибками: 2
            прошло: ~300 мс
            """,
        ),
        text(
            "Главное здесь — обработка ошибки на уровне задачи. Функция `load` возвращает "
            "`Result`, поэтому один сбойный адрес не роняет весь обход и не превращается "
            "в панику внутри `spawn`. Результат задачи читается через `join.await`, "
            "и паника внутри задачи всплывает как ошибка `JoinError`, а не как "
            "немедленное завершение процесса."
        ),
        heading("Планировщик обхода"),
        text(
            "Теперь нужен компонент, который превращает список адресов в работу: "
            "проверяет глубину, отсекает уже посещённые адреса, скачивает страницу, "
            "извлекает ссылки и складывает всё в хранилище.\n\n"
            "Проверку и вставку в множество посещённых делаем под одной блокировкой "
            "записи. Если сначала прочитать множество, а потом отдельно вставить, "
            "две задачи успеют увидеть адрес непосещённым и скачают его дважды — "
            "классическая гонка проверки и действия.\n\n"
            "Обход рекурсивный: каждая страница порождает вызовы для своих ссылок. "
            "Это удобно читать, но в асинхронном коде рекурсия по `async fn` "
            "требует боксирования. Для глубины два-три проще обойтись итеративным "
            "подходом с очередью."
        ),
        example(
            "rust",
            """
            // src/crawler.rs
            use std::collections::{HashSet, VecDeque};
            use std::sync::Arc;
            use tokio::sync::{Mutex, Semaphore};
            use tokio::time::{sleep, Duration};

            use crate::config::CrawlerConfig;
            use crate::error::Result;

            pub struct Stats {
                pub pages: usize,
                pub links: usize,
                pub errors: usize,
            }

            impl Stats {
                pub fn new() -> Self {
                    Self { pages: 0, links: 0, errors: 0 }
                }
            }

            pub trait PageSource: Send + Sync {
                fn fetch(&self, url: &str) -> std::pin::Pin<Box<dyn std::future::Future<Output = Result<String>> + Send + '_>>;
                fn extract_links(&self, base: &str, html: &str) -> Result<Vec<String>>;
            }

            pub async fn run<S: PageSource>(
                source: &Arc<S>,
                config: &CrawlerConfig,
                stats: &Mutex<Stats>,
            ) -> Result<()> {
                let semaphore = Arc::new(Semaphore::new(config.max_concurrent));
                let visited = Arc::new(Mutex::new(HashSet::new()));
                let mut queue: VecDeque<(String, usize)> = VecDeque::new();

                for url in &config.start_urls {
                    queue.push_back((url.clone(), 0));
                }

                while let Some((url, depth)) = queue.pop_front() {
                    {
                        let mut seen = visited.lock().await;
                        if !seen.insert(url.clone()) {
                            continue;
                        }
                    }

                    let permit = Arc::clone(&semaphore).acquire_owned().await.unwrap();
                    sleep(Duration::from_millis(config.delay_ms)).await;

                    match source.fetch(&url).await {
                        Ok(html) => {
                            let links = source.extract_links(&url, &html)?;
                            drop(permit);
                            let mut s = stats.lock().await;
                            s.pages += 1;
                            s.links += links.len();
                            drop(s);
                            if depth < config.max_depth {
                                for link in links {
                                    queue.push_back((link, depth + 1));
                                }
                            }
                        }
                        Err(_) => {
                            drop(permit);
                            stats.lock().await.errors += 1;
                        }
                    }
                }
                Ok(())
            }
            """,
        ),
        text(
            "Обратите внимание на трейт `PageSource`. Вместо жёсткой привязки "
            "к реальному загрузчику планировщик принимает любую реализацию. "
            "Это делает его тестируемым без сети: достаточно написать заглушку, "
            "которая возвращает заранее подготовленный HTML.\n\n"
            "Итеративный обход с очередью заодно решает проблему бесконечного "
            "цикла: множество посещённых адресов растёт, и повторно встреченный "
            "адрес просто пропускается. Глубина ограничивает длину пути от стартового "
            "адреса, а не общее число страниц."
        ),
        callout(
            "warning",
            "Не держите блокировку через await",
            "Если удерживать `MutexGuard` во время `fetch().await`, все остальные "
            "задачи встанут в очередь на блокировку, и параллелизм исчезнет. "
            "Берите блокировку в узком блоке, меняйте данные и сразу отпускайте. "
            "Для структур, читаемых чаще, чем изменяемых, используйте `RwLock`.",
        ),
        heading("Хранение результатов"),
        text(
            "Хранилище копит страницы в памяти и по команде сбрасывает их в JSON. "
            "Сериализация через serde практически бесплатна: достаточно "
            "производных `Serialize` и `Deserialize`.\n\n"
            "Для записи файла полезна функция `tokio::fs::write`: она не блокирует "
            "поток исполнителя. Для больших объёмов лучше писать в отдельном потоке "
            "через `spawn_blocking`, но для результата в несколько мегабайт "
            "асинхронной записи достаточно."
        ),
        example(
            "rust",
            """
            // src/storage.rs
            use serde::{Deserialize, Serialize};
            use std::collections::BTreeMap;

            use crate::error::Result;

            #[derive(Debug, Serialize, Deserialize, Clone)]
            pub struct Page {
                pub url: String,
                pub title: String,
                pub links: Vec<String>,
                pub depth: usize,
            }

            #[derive(Debug, Serialize, Deserialize, Default)]
            pub struct Report {
                pub pages: BTreeMap<String, Page>,
                pub errors: usize,
            }

            impl Report {
                pub fn add(&mut self, page: Page) {
                    self.pages.insert(page.url.clone(), page);
                }

                pub async fn save(&self, path: &str) -> Result<()> {
                    let json = serde_json::to_string_pretty(self)?;
                    tokio::fs::write(path, json).await?;
                    Ok(())
                }
            }
            """,
        ),
        text(
            "`BTreeMap` здесь предпочтительнее `HashMap`: ключи в JSON будут "
            "отсортированы, и одинаковый набор страниц даст одинаковый файл. "
            "Это упрощает сравнение результатов между запусками и проверку в тестах."
        ),
        example(
            "rust",
            """
            #[tokio::main]
            async fn main() -> Result<()> {
                let mut report = Report::default();
                report.add(Page {
                    url: "https://example.com".into(),
                    title: "Example Domain".into(),
                    links: vec![
                        "https://example.com/about".into(),
                        "https://docs.rs/tokio".into(),
                    ],
                    depth: 0,
                });
                report.errors = 1;
                report.save("results.json").await?;
                println!("страниц: {}", report.pages.len());
                Ok(())
            }
            """,
        ),
        text(
            "Вывод:\n\n"
            "```\n"
            "страниц: 1\n"
            "```\n\n"
            "В файле `results.json` окажется отформатированный документ "
            "с полями `pages` и `errors`. Обратите внимание на сигнатуру `main`: "
            "возвращая `Result`, программа печатает ошибку и завершается "
            "с ненулевым кодом без паники и без ручного `match`."
        ),
        heading("Точка входа и корректное завершение"),
        text(
            "В `main.rs` остаётся связать модули: прочитать конфигурацию, "
            "инициализировать логирование, собрать компоненты и запустить обход. "
            "Рантайм `tokio` включается макросом `#[tokio::main]` с многопоточным "
            "исполнителем.\n\n"
            "Завершение по Ctrl+C полезно даже в учебном проекте. "
            "`tokio::select!` ждёт первый из двух сигналов: завершения обхода "
            "или нажатия Ctrl+C. Как только пришёл сигнал, мы перестаём принимать "
            "новые страницы и сохраняем уже собранное."
        ),
        example(
            "rust",
            """
            // src/main.rs
            use std::sync::Arc;
            use tracing::info;

            #[tokio::main]
            async fn main() -> anyhow::Result<()> {
                let content = tokio::fs::read_to_string("config.toml").await?;
                let config = crawler::config::Config::from_str(&content)
                    .map_err(|e| anyhow::anyhow!("конфигурация: {e}"))?;

                let fetcher = Arc::new(crawler::fetcher::Fetcher::new(
                    config.crawler.request_timeout_secs,
                    &config.crawler.user_agent,
                )?);

                info!(urls = config.crawler.start_urls.len(), "старт обхода");

                tokio::select! {
                    result = run_crawl(fetcher, &config) => {
                        result?;
                        info!("обход завершён");
                    }
                    _ = tokio::signal::ctrl_c() => {
                        info!("получен сигнал остановки, сохраняем результат");
                    }
                }
                Ok(())
            }

            async fn run_crawl(
                _fetcher: Arc<crawler::fetcher::Fetcher>,
                _config: &crawler::config::Config,
            ) -> anyhow::Result<()> {
                Ok(())
            }
            """,
        ),
        callout(
            "success",
            "Разделяйте слои",
            "`main.rs` не должен знать, как устроен обход. Его дело — собрать "
            "компоненты из конфигурации и позаботиться о завершении. Любая логика, "
            "которую хочется протестировать, живёт в библиотеке.",
        ),
        heading("Тесты проекта"),
        text(
            "Интеграционные тесты лежат в каталоге `tests` и компилируются как "
            "отдельные крейты, которые подключают нашу библиотеку. Поэтому все "
            "проверяемые модули должны быть объявлены в `lib.rs` через `pub mod`.\n\n"
            "Тестируем три вещи отдельно от сети: разбор конфигурации, извлечение "
            "ссылок и сохранение отчёта. Каждый тест работает с собственным "
            "временным файлом из `tempfile`, чтобы запуски не мешали друг другу."
        ),
        example(
            "rust",
            """
            // tests/integration.rs
            use crawler::{config::Config, parser::Parser, storage::{Page, Report}};

            #[test]
            fn config_rejects_zero_concurrency() {
                let raw = r#"
            [crawler]
            start_urls = ["https://example.com"]
            max_depth = 1
            max_concurrent = 0
            request_timeout_secs = 5
            delay_ms = 10
            user_agent = "test"

            [storage]
            path = "out.json"
            "#;
                assert!(Config::from_str(raw).is_err());
            }

            #[test]
            fn parser_makes_links_absolute() {
                let parser = Parser::new().unwrap();
                let html = r#"<a href="/page1">1</a><a href="mailto:a@b.c">2</a>"#;
                let links = parser
                    .extract_links("https://example.com", html)
                    .unwrap();
                assert_eq!(links, vec!["https://example.com/page1".to_string()]);
            }

            #[tokio::test]
            async fn report_roundtrip() {
                let dir = tempfile::tempdir().unwrap();
                let path = dir.path().join("report.json");
                let mut report = Report::default();
                report.add(Page {
                    url: "https://example.com".into(),
                    title: "Example".into(),
                    links: vec![],
                    depth: 0,
                });
                report.save(path.to_str().unwrap()).await.unwrap();

                let raw = std::fs::read_to_string(&path).unwrap();
                let parsed: Report = serde_json::from_str(&raw).unwrap();
                assert_eq!(parsed.pages.len(), 1);
                assert!(parsed.pages.contains_key("https://example.com"));
            }
            """,
        ),
        text(
            "Запуск тестов и сборка релиза выполняются обычными командами Cargo. "
            "Вывод сокращён, но показывает итог:"
        ),
        example(
            "text",
            """
            $ cargo test
               Compiling crawler v0.1.0 (/home/user/crawler)
                Finished `test` profile [unoptimized + debuginfo] target(s)
                 Running unittests src/lib.rs (target/debug/deps/crawler-3f1a)
                 Running tests/integration.rs (target/debug/deps/integration-9c02)

            running 3 tests
            test config_rejects_zero_concurrency ... ok
            test parser_makes_links_absolute ... ok
            test report_roundtrip ... ok

            test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured

            $ cargo build --release
                Finished `release` profile [optimized] target(s)
            """,
        ),
        text(
            "Тест `parser_makes_links_absolute` заодно документирует поведение: "
            "почтовая ссылка отбрасывается, относительная превращается в абсолютную, "
            "порядок сохраняется. Такой тест защищает от случайной поломки при "
            "рефакторинге — например, если кто-то заменит `join` на простую "
            "конкатенацию строк."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                [
                    "`acquire` вместо `acquire_owned` при передаче семафора в `spawn`",
                    "Разрешение заимствует семафор, и будущее не становится `'static`",
                    "Оборачивайте семафор в `Arc` и вызывайте `acquire_owned`",
                ],
                [
                    "`MutexGuard` живёт во время `.await`",
                    "Все остальные задачи встают на блокировке, параллелизм пропадает",
                    "Сужайте блок с блокировкой и отпускайте guard до ожидания",
                ],
                [
                    "Проверка посещённых и вставка в разных блоках",
                    "Две задачи скачивают один адрес, гонка проверки и действия",
                    "Делайте `contains` и `insert` под одной блокировкой записи",
                ],
                [
                    "Замыкание в `with_retry` меняет захваченное значение",
                    "Тип не реализует `FnMut`, компилятор отвергает вызов",
                    "Копируйте нужное значение до создания будущего",
                ],
                [
                    "Относительные ссылки идут в очередь как есть",
                    "Запросы вида `/about` завершаются ошибкой разбора адреса",
                    "Приводите к абсолютным через `Url::join` до постановки в очередь",
                ],
                [
                    "Задержка `sleep` внутри удерживаемого разрешения перед загрузкой",
                    "Разрешение занято впустую, фактическая параллельность ниже лимита",
                    "Спите до взятия разрешения или после освобождения",
                ],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняются в проекте `crawler`. Собирайте и запускайте после "
            "каждого шага: `cargo build` и `cargo test`."
        ),
        numbered(
            "Создайте проект, разнесите код по модулям из структуры урока и добейтесь, чтобы `cargo test` находил и запускал три интеграционных теста.",
            "Добавьте в `config.toml` секцию `[logging]` с уровнем и путём к файлу, расширьте `Config` и покройте разбор тестом на отсутствующий ключ.",
            "Реализуйте трейт `PageSource` для заглушки, которая возвращает HTML из `HashMap<String, String>`, и прогоните `run` на трёх связанных страницах с `max_depth = 1`.",
            "Замерьте время обхода восьми страниц при `max_concurrent`, равном 1, 2 и 4, и объясните разницу через число волн.",
            "Добавьте сохранение отчёта по Ctrl+C: запустите обход на медленной заглушке, прервите его и убедитесь, что файл с частичным результатом записан.",
        ),
        heading("Проверьте себя"),
        *check_yourself(
            (
                "Зачем выносить логику в `lib.rs`, если есть `main.rs`?",
                "Почему в конфигурации появляется поле `r#type`?",
                "В чём разница между задачами `thiserror` и `anyhow` в одном проекте?",
                "Что произойдёт, если удерживать разрешение семафора во время `sleep` перед запросом?",
                "Зачем в планировщике обход реализован очередью, а не рекурсивным `async fn`?",
            ),
            (
                "Интеграционные тесты в каталоге `tests` видят только публичный интерфейс библиотеки; код в бинарнике им недоступен.",
                "`type` — ключевое слово Rust, поэтому идентификатор записывается в сыром виде, а имя поля в TOML остаётся `type`.",
                "`thiserror` даёт типизированные ошибки библиотеки с вариантами, `anyhow` — единый тип с контекстом для прикладного кода.",
                "Разрешение будет занято без пользы, фактическая параллельность окажется ниже лимита, а обход замедлится.",
                "Рекурсивный `async fn` требует боксирования и рискует переполнить стек на длинных цепочках; очередь проще и безопаснее.",
            ),
        ),
        *outro(
            (
                "Проект разбит на библиотеку и тонкий бинарник: модули доступны интеграционным тестам.",
                "Конфигурация читается из TOML через serde, инварианты проверяются до запуска.",
                "Ошибки библиотеки описаны перечислением с `thiserror`, ретраи используют экспоненциальную задержку.",
                "Семафор `tokio::sync::Semaphore` ограничивает параллелизм, разрешение освобождается автоматически.",
                "Проверка посещённых адресов и вставка выполняются под одной блокировкой, чтобы избежать гонки.",
                "Результат сохраняется в JSON в детерминированном порядке, завершение по Ctrl+C обрабатывается через `select!`.",
            ),
            "Уровень 2 завершён: вы собрали полноценное асинхронное приложение от "
            "манифеста до тестов. Дальше начинается уровень 3 — внутреннее устройство "
            "языка. Первый урок посвящён памяти и владению: вы разберёте, где живут "
            "данные, как работает стек и куча, что такое время жизни на уровне "
            "машинного кода и почему заимствования проверяются статически.",
            (
                "Документация tokio: модуль `tokio::sync` и `Semaphore` — docs.rs/tokio",
                "reqwest: руководство по клиенту и таймаутам — docs.rs/reqwest",
                "Книга «Asynchronous Programming in Rust» — rust-lang.github.io/async-book",
                "Cargo Book: организация пакетов, библиотеки и интеграционных тестов — doc.rust-lang.org/cargo",
            ),
        ),
    ],
}
