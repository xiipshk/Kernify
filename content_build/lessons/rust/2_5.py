"""Урок 5 курса Rust: архитектура приложения."""

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
    "topic_order": 5,
    "name": "2.5. Архитектура",
    "slug": "rust-2-5-архитектура",
    "topic_name": "Архитектура",
    "short_description": (
        "Слоистая архитектура приложения на Rust: домен, сервисы, инфраструктура и интерфейс, "
        "инверсия зависимостей через трейты, DTO, конфигурация, единая ошибка и тестируемость."
    ),
    "topic_description": (
        "Как устроить проект на Rust так, чтобы бизнес-логика не зависела от базы данных и веб-фреймворка: "
        "слои Domain, Application, Infrastructure и Presentation, паттерны Repository и Service, "
        "DTO для границ приложения, централизованная конфигурация, единый тип ошибки и внедрение зависимостей "
        "через трейты с подменой реализаций в тестах."
    ),
    "learning_objectives": [
        "Разделять проект на слои Domain, Application, Infrastructure и Presentation и объяснять направление зависимостей",
        "Описывать контракт хранения трейтом Repository и подменять реализацию: база данных, память, заглушка",
        "Переносить бизнес-логику из обработчиков в сервисный слой с явными командами и запросами",
        "Отделять доменную сущность от DTO запроса и ответа и не выпускать секреты наружу",
        "Собирать конфигурацию из файла и переменных окружения в одну типизированную структуру",
        "Проектировать единый тип ошибки с `thiserror` и преобразованием во внешний ответ",
        "Внедрять зависимости через трейты и параметры типа и подменять их в тестах без базы данных",
        "Распознавать архитектурные антипаттерны: God Object, Anemic Domain, Leaky Abstraction, Tight Coupling",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "rust",
        "архитектура",
        "трейты",
        "репозиторий",
        "внедрение-зависимостей",
        "тестирование",
    ],
    "starter_code": code(
        r"""
        // Минимальный скелет слоистого приложения на Rust.
        // Контракт домена: что нужно приложению от хранилища.
        pub trait UserRepository {
            fn find_by_id(&self, id: u64) -> Result<Option<User>, RepoError>;
            fn save(&self, user: &User) -> Result<(), RepoError>;
        }

        #[derive(Debug, Clone, PartialEq, Eq)]
        pub struct User {
            pub id: u64,
            pub email: String,
            pub name: String,
        }

        #[derive(Debug)]
        pub struct RepoError(pub String);

        // Сервис зависит от трейта, а не от конкретной базы.
        pub struct UserService<R: UserRepository> {
            repo: R,
        }

        impl<R: UserRepository> UserService<R> {
            pub fn new(repo: R) -> Self {
                Self { repo }
            }

            pub fn rename(&self, id: u64, name: &str) -> Result<User, ServiceError> {
                let mut user = self
                    .repo
                    .find_by_id(id)
                    .map_err(ServiceError::Storage)?
                    .ok_or(ServiceError::NotFound)?;
                user.name = name.to_string();
                self.repo.save(&user).map_err(ServiceError::Storage)?;
                Ok(user)
            }
        }

        #[derive(Debug)]
        pub enum ServiceError {
            NotFound,
            Storage(RepoError),
        }

        fn main() {
            // В тестах и в примере подставляется реализация в памяти,
            // в рабочей сборке — реализация поверх настоящей базы.
            let repo = InMemoryUserRepository::default();
            let service = UserService::new(repo);
            println!("{:?}", service.rename(1, "Анна"));
        }
        """
    ),
    "hints": [
        "Начинайте с домена: типы и трейты, которые описывают бизнес-правила. Если для компиляции домена нужен интернет-фреймворк, слой спроектирован неверно.",
        "Сервис принимает параметр типа `R: UserRepository` — так он работает с любой реализацией, а тест подставляет простую структуру в памяти.",
        "Если сервисы удобнее хранить в общем состоянии, используйте `Arc<dyn UserRepository>`: трейт-объект стирает конкретный тип, а `Arc` позволяет делить один экземпляр между обработчиками.",
        "Ошибки домена описывают бизнес-смысл (не найдено, конфликт, запрещено), а HTTP-коды, SQL-коды и тексты для пользователя живут в слое инфраструктуры.",
    ],
    "content": [
        text(
            "Rust не навязывает структуру проекта: обязательна только точка входа в `main.rs`, остальное — "
            "модули, слои и границы между ними — разработчик выбирает сам. Пока код помещается в один файл, "
            "это удобно. Когда в проекте база данных, HTTP-сервер, планировщик и несколько интеграций, "
            "отсутствие границ приводит к тому, что любое изменение требует правок во всех частях сразу.\n\n"
            "Архитектура приложения отвечает на один вопрос: какая часть кода что знает. Хорошо разделённый "
            "проект позволяет заменить драйвер базы, не трогая правила расчёта скидок, и проверить эти правила "
            "тестом без базы. Модули и видимость `pub` в Rust делают такое разделение механическим: "
            "зависимости объявлены в сигнатурах и не прячутся.\n\n"
            "Дальше — слои и направление зависимостей, паттерны Repository и Service, DTO на границах, "
            "конфигурация, единая ошибка, внедрение зависимостей, тестируемость и антипаттерны. Примеры "
            "самодостаточны: их можно собрать без базы данных и веб-фреймворка."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "делить код на слои `domain`, `application`, `infrastructure` и `presentation` и объяснять, куда направлены зависимости;",
            "описывать контракт хранения трейтом `Repository` и подменять реализацию без переписывания логики;",
            "переносить бизнес-логику из обработчиков в сервисный слой с явными командами и запросами;",
            "отделять доменную сущность от DTO запроса и ответа и не выпускать служебные поля наружу;",
            "собирать конфигурацию из файла и переменных окружения в одну типизированную структуру;",
            "описывать единый тип ошибки через `thiserror` и преобразовывать его во внешний ответ;",
            "внедрять зависимости через трейты и параметры типа и подменять их в тестах без внешней инфраструктуры;",
            "распознавать архитектурные антипаттерны: God Object, Anemic Domain, Leaky Abstraction, Tight Coupling.",
        ),
        heading("Слои и направление зависимостей"),
        text(
            "Четыре слоя покрывают почти любое приложение. **Domain** (домен) содержит сущности и правила "
            "предметной области — то, что останется верным при смене стека. **Application** (приложение) "
            "описывает сценарии использования: зарегистрировать пользователя, оформить заказ. "
            "**Infrastructure** (инфраструктура) содержит технические детали: SQL, HTTP-клиенты, файлы. "
            "**Presentation** (интерфейс) принимает запросы извне: HTTP-обработчики, подкоманды CLI, gRPC.\n\n"
            "Главное правило — **направление зависимостей**. Домен не зависит ни от чего, кроме стандартной "
            "библиотеки и узких крейтов вроде `serde`. Прикладной слой зависит только от домена. "
            "Инфраструктура зависит от домена и реализует его трейты. Интерфейсный слой зависит от "
            "прикладного. Нарушение видно сразу: попробуйте скомпилировать домен без инфраструктуры — если "
            "не собирается, домен знает лишнее.\n\n"
            "В терминах Cargo это значит отдельные крейты. Небольшие сервисы обходятся модулями одного "
            "крейта, крупные выносят `domain` в библиотечный крейт, чтобы зависимость от `postgres` была "
            "невозможна на уровне сборки. Начинайте с модулей: разносить по крейтам позже дешевле, чем "
            "разбирать циклы."
        ),
        example(
            "text",
            """
            src/
            ├── domain/               # Бизнес-логика, сущности, трейты
            │   ├── models.rs         # User, Order, OrderStatus
            │   ├── repositories.rs   # трейты UserRepository, OrderRepository
            │   └── errors.rs         # DomainError
            ├── application/          # Сценарии использования
            │   ├── commands.rs       # CreateUserCommand, PlaceOrderCommand
            │   ├── queries.rs        # GetUserQuery
            │   └── services.rs       # UserService, OrderService
            ├── infrastructure/       # Реализации (SQL, HTTP, файлы)
            │   ├── in_memory.rs      # InMemoryUserRepository
            │   └── postgres.rs       # PgUserRepository
            ├── presentation/         # Входные точки
            │   ├── http.rs           # обработчики
            │   └── cli.rs            # подкоманды
            ├── config.rs             # Конфигурация
            └── main.rs               # Сборка приложения, точка входа
            """
        ),
        callout(
            "info",
            "Проверка границ",
            "Если для компиляции модуля `domain` приходится подключать `postgres`, `axum` или `reqwest`, "
            "значит, граница проведена неверно. Удалите лишнюю зависимость из `Cargo.toml` и замените "
            "конкретный тип трейтом — компилятор сам покажет все места, которые нарушали слой.",
        ),
        heading("Инверсия зависимостей и трейты"),
        text(
            "**Инверсия зависимостей** делает правило направления зависимостей выполнимым. Вместо обращения "
            "к базе напрямую домен объявляет трейт с нужными операциями, а инфраструктура реализует его. "
            "Стрелка зависимости в коде указывает на домен, хотя во время выполнения управление идёт от "
            "домена к базе.\n\n"
            "Трейт — естественный носитель таких абстракций. Соглашение — требовать от трейта хранилища "
            "`Send + Sync`, если его будут использовать из нескольких потоков асинхронного сервера."
        ),
        example(
            "rust",
            r"""
            // domain/repositories.rs — контракт, объявленный доменом
            use crate::domain::models::{User, UserId};
            use crate::domain::errors::DomainError;

            pub trait UserRepository: Send + Sync {
                fn find_by_id(&self, id: UserId) -> Result<Option<User>, DomainError>;
                fn save(&self, user: &User) -> Result<(), DomainError>;
            }

            // application/services.rs — сервис зависит от абстракции
            pub struct UserService<R: UserRepository> {
                repo: R,
            }

            impl<R: UserRepository> UserService<R> {
                pub fn new(repo: R) -> Self {
                    Self { repo }
                }

                pub fn get_user(&self, id: UserId) -> Result<User, DomainError> {
                    self.repo.find_by_id(id)?.ok_or(DomainError::NotFound)
                }
            }
            """
        ),
        text(
            "Сервис универсален: `R` — любая реализация `UserRepository`. В рабочей сборке там "
            "`PostgresUserRepository`, в тесте — структура поверх `HashMap`. Конкретный тип подставляется при "
            "сборке, поэтому вызов `self.repo.find_by_id` остаётся статическим: ни таблиц виртуальных "
            "методов, ни накладных расходов, пока тип известен. Это и есть zero-cost abstractions."
        ),
        heading("Repository Pattern"),
        text(
            "**Repository** ведёт себя как коллекция сущностей и скрывает способ хранения. Сервису не важно, "
            "лежат пользователи в PostgreSQL, файле или памяти: он просит `find_by_id` и `save`. Репозиторий "
            "возвращает доменные объекты, а не строки таблицы, и не выпускает SQL наружу.\n\n"
            "Три реализации покрывают почти всё. **Настоящая** работает с базой. **В памяти** держит данные в "
            "`HashMap` и подходит для примеров, тестов и локальной разработки. **Заглушка** возвращает "
            "заданные значения и записывает вызовы, чтобы проверить, что сервис обратился к хранилищу ровно "
            "один раз с нужными аргументами. Начинайте с реализации в памяти: она требует десятка строк и "
            "сразу делает сервис проверяемым."
        ),
        example(
            "rust",
            r"""
            use std::collections::HashMap;
            use std::sync::RwLock;

            #[derive(Debug, Clone, PartialEq, Eq)]
            pub struct User {
                pub id: u64,
                pub email: String,
                pub name: String,
            }

            #[derive(Debug, Clone, Copy, PartialEq, Eq)]
            pub enum DomainError {
                NotFound,
                Storage,
            }

            pub trait UserRepository: Send + Sync {
                fn find_by_id(&self, id: u64) -> Result<Option<User>, DomainError>;
                fn find_by_email(&self, email: &str) -> Result<Option<User>, DomainError>;
                fn save(&self, user: &User) -> Result<(), DomainError>;
            }

            #[derive(Default)]
            pub struct InMemoryUserRepository {
                users: RwLock<HashMap<u64, User>>,
            }

            impl UserRepository for InMemoryUserRepository {
                fn find_by_id(&self, id: u64) -> Result<Option<User>, DomainError> {
                    let guard = self.users.read().map_err(|_| DomainError::Storage)?;
                    Ok(guard.get(&id).cloned())
                }

                fn find_by_email(&self, email: &str) -> Result<Option<User>, DomainError> {
                    let guard = self.users.read().map_err(|_| DomainError::Storage)?;
                    Ok(guard.values().find(|u| u.email == email).cloned())
                }

                fn save(&self, user: &User) -> Result<(), DomainError> {
                    let mut guard = self.users.write().map_err(|_| DomainError::Storage)?;
                    guard.insert(user.id, user.clone());
                    Ok(())
                }
            }
            """
        ),
        text(
            "Обратите внимание на обработку ошибки `RwLock::read` и `RwLock::write`: блокировка отравляется, "
            "когда другой поток запаниковал, удерживая её. Возврат `DomainError::Storage` вместо `unwrap` "
            "позволяет сервису обработать сбой так же, как сбой базы. В асинхронном коде репозиторий поверх базы "
            "подключают через таблицу `async_trait`: стабильный Rust пока не умеет объявлять в трейтах "
            "асинхронные методы, пригодные для трейт-объектов."
        ),
        heading("Service Layer: команды и запросы"),
        text(
            "Сервисный слой содержит сценарии использования — то, что можно попросить приложение сделать. "
            "Сценарии бывают двух видов. **Команда** (command) меняет состояние: создать пользователя, "
            "оплатить заказ. **Запрос** (query) только читает: показать карточку или список заказов. "
            "Разделение практично: запросы можно кэшировать и повторять, команды — нет.\n\n"
            "Сервис отвечает за порядок действий: проверить данные, проверить бизнес-правила, сохранить, "
            "отправить уведомление. Это единственное место, где порядок описан. Обработчик интерфейса "
            "остаётся тонким: разобрать ввод, вызвать сервис, преобразовать результат. Если в обработчике "
            "появилось условие про уникальность почты — правило живёт не в том слое."
        ),
        example(
            "rust",
            r"""
            pub struct CreateUserCommand {
                pub email: String,
                pub name: String,
            }

            pub struct UserService<R: UserRepository> {
                repo: R,
            }

            impl<R: UserRepository> UserService<R> {
                pub fn create_user(&self, cmd: CreateUserCommand) -> Result<User, CreateUserError> {
                    let email = cmd.email.trim().to_lowercase();
                    if !email.contains('@') {
                        return Err(CreateUserError::InvalidEmail);
                    }
                    if cmd.name.trim().len() < 2 {
                        return Err(CreateUserError::NameTooShort);
                    }
                    if self.repo.find_by_email(&email)?.is_some() {
                        return Err(CreateUserError::EmailTaken);
                    }
                    let user = User {
                        id: 0,
                        email,
                        name: cmd.name.trim().to_string(),
                    };
                    self.repo.save(&user)?;
                    Ok(user)
                }
            }

            #[derive(Debug, PartialEq, Eq)]
            pub enum CreateUserError {
                InvalidEmail,
                NameTooShort,
                EmailTaken,
                Storage,
            }

            impl From<DomainError> for CreateUserError {
                fn from(_: DomainError) -> Self {
                    CreateUserError::Storage
                }
            }
            """
        ),
        text(
            "Здесь видна характерная черта Rust-сервисов: ошибка сценария — собственное перечисление, где "
            "каждый вариант назван по бизнес-причине. Оператор `?` вместе с реализацией "
            "`From<DomainError>` превращает ошибку хранилища в `Storage` автоматически, и код читается как "
            "последовательность шагов, а не лестница из `match`."
        ),
        callout(
            "success",
            "Правило одного действия",
            "Если метод сервиса не укладывается в название `глагол + существительное` "
            "(`place_order`, `cancel_subscription`), вероятно, он делает два сценария сразу. Разделите его: "
            "два маленьких метода проще покрыть тестами и повторно использовать из разных интерфейсов.",
        ),
        heading("DTO на границах приложения"),
        text(
            "**DTO** (Data Transfer Object, объект передачи данных) — простая структура без поведения, "
            "описывающая данные на границе системы. У сущности и DTO разное назначение. Сущность хранит "
            "инварианты и методы: `change_email` проверяет формат и правила смены адреса. DTO содержит только "
            "поля, которые разрешено принимать или отдавать наружу.\n\n"
            "Разделение закрывает три проблемы. Безопасность: в сущности пользователя лежит хеш пароля, и "
            "прямая сериализация отправит секрет в ответ API. Устойчивость контракта: переименование поля в "
            "базе не обязано ломать клиентов. Контроль ввода: DTO запроса содержит только задаваемые поля, "
            "а идентификатор и дата создания присваиваются сервером.\n\n"
            "Преобразование делают через `From`. Такая реализация работает с `Into` автоматически, и в "
            "сервисе достаточно написать `user.into()`."
        ),
        example(
            "rust",
            r"""
            // Домен: инварианты и служебные поля внутри
            #[derive(Debug, Clone)]
            pub struct User {
                pub id: u64,
                pub email: String,
                pub name: String,
                pub password_hash: String,
                pub is_admin: bool,
            }

            // DTO ответа: только публичные поля
            #[derive(Debug, serde::Serialize)]
            pub struct UserDto {
                pub id: u64,
                pub email: String,
                pub name: String,
            }

            impl From<User> for UserDto {
                fn from(user: User) -> Self {
                    Self {
                        id: user.id,
                        email: user.email,
                        name: user.name,
                    }
                }
            }

            // DTO запроса: клиент не может подменить id или флаг администратора
            #[derive(Debug, serde::Deserialize)]
            pub struct CreateUserRequest {
                pub email: String,
                pub name: String,
                pub password: String,
            }

            impl From<CreateUserRequest> for CreateUserCommand {
                fn from(req: CreateUserRequest) -> Self {
                    Self {
                        email: req.email,
                        name: req.name,
                    }
                }
            }
            """
        ),
        text(
            "Обратите внимание: в DTO ответа нет `is_admin` и `password_hash`. Добавить их в `From` "
            "случайно не получится — компилятор потребует сначала расширить структуру, а это заметное "
            "изменение контракта. Это дешевле, чем искать утёкший хеш пароля в логах."
        ),
        heading("Конфигурация приложения"),
        text(
            "Конфигурация — параметры, различающиеся между окружениями: адрес прослушивания, строка "
            "подключения, размер пула, ключи внешних сервисов. Антипаттерн — чтение `std::env::var` в "
            "случайных местах: список обязательных переменных неизвестен, а тесты зависят от окружения.\n\n"
            "Правильный подход — один модуль, который собирает значения по приоритету: значения по умолчанию, "
            "файл конфигурации, файл окружения, переменные окружения. Результат превращается в структуру с "
            "`serde::Deserialize`, и остальной код работает с полями, а не со строками. Ошибка разбора "
            "видна при запуске, а не при первом запросе к базе. Чем ближе источник к среде запуска, тем он "
            "важнее: секреты передают переменной, а не кладут в образ."
        ),
        example(
            "rust",
            r"""
            use std::net::SocketAddr;

            #[derive(Debug, Clone, serde::Deserialize)]
            #[serde(default)]
            pub struct AppConfig {
                pub addr: SocketAddr,
                pub workers: usize,
                pub database_url: String,
                pub max_connections: u32,
            }

            impl Default for AppConfig {
                fn default() -> Self {
                    Self {
                        addr: "0.0.0.0:8080".parse().expect("корректный адрес по умолчанию"),
                        workers: 4,
                        database_url: String::from("postgres://localhost/app"),
                        max_connections: 10,
                    }
                }
            }

            impl AppConfig {
                // Простой разбор без внешнего крейта: значение строки вида KEY=VALUE.
                pub fn apply(&mut self, key: &str, value: &str) -> Result<(), String> {
                    match key {
                        "APP_ADDR" => self.addr = value.parse().map_err(|_| format!("плохой адрес: {value}"))?,
                        "APP_WORKERS" => self.workers = value.parse().map_err(|_| format!("плохое число: {value}"))?,
                        "APP_DATABASE_URL" => self.database_url = value.to_string(),
                        "APP_MAX_CONNECTIONS" => {
                            self.max_connections = value.parse().map_err(|_| format!("плохое число: {value}"))?
                        }
                        _ => return Err(format!("неизвестный ключ: {key}")),
                    }
                    Ok(())
                }
            }

            fn main() -> Result<(), String> {
                let mut app = AppConfig::default();
                for (key, value) in std::env::vars().filter(|(k, _)| k.starts_with("APP_")) {
                    app.apply(&key, &value)?;
                }
                println!("сервер: {}", app.addr);
                println!("воркеров: {}", app.workers);
                Ok(())
            }
            """
        ),
        text(
            "Вывод при запуске без переменных окружения: `сервер: 0.0.0.0:8080`, затем `воркеров: 4`. "
            "С `APP_WORKERS=8 ./app` вторая строка покажет `воркеров: 8`. В реальном проекте разбор "
            "разумно отдать крейту `config`, который накладывает TOML-файлы и разбирает вложенные ключи, но "
            "принцип тот же: одна структура на всё приложение, собранная до запуска основной логики."
        ),
        callout(
            "warning",
            "Конфигурация и секреты",
            "Не печатайте всю структуру конфигурации в лог: строка подключения к базе часто содержит пароль, "
            "а ключи внешних сервисов — токены. Реализуйте `Debug` вручную или выводите только отобранные "
            "поля вроде адреса и количества воркеров.",
        ),
        heading("Единая обработка ошибок"),
        text(
            "В приложении пересекаются ошибки разной природы: нарушено правило (`EmailTaken`), сущность не "
            "найдена (`NotFound`), база недоступна, внешний сервис ответил таймаутом. Хранить их строками "
            "удобно до первого инцидента: наверху непонятно, что показать пользователю, а что залогировать.\n\n"
            "Рабочая схема — три уровня. Домен объявляет узкую ошибку своего трейта. Прикладной слой "
            "объявляет `AppError` со всеми вариантами, которые умеет различать. Интерфейсный слой "
            "преобразует его во внешний формат: статус, код, текст. Крейт `thiserror` избавляет от ручной "
            "реализации `Display`, `Error` и `From`: `#[derive(Error, Debug)]` создаёт `std::error::Error`, "
            "`#[error(\"...\")]` задаёт текст через `Display` полей, а `#[from]` — реализацию `From`, "
            "благодаря которой работает `?`."
        ),
        example(
            "rust",
            r"""
            #[derive(Debug, thiserror::Error)]
            pub enum AppError {
                #[error("не найдено: {0}")]
                NotFound(String),

                #[error("конфликт: {0}")]
                Conflict(String),

                #[error("неверные данные: {0}")]
                Validation(String),

                #[error("нет доступа")]
                Forbidden,

                #[error("ошибка хранилища")]
                Storage(#[source] DomainError),

                #[error("внутренняя ошибка")]
                Internal(#[from] anyhow::Error),
            }

            pub fn status_code(err: &AppError) -> u16 {
                match err {
                    AppError::NotFound(_) => 404,
                    AppError::Conflict(_) => 409,
                    AppError::Validation(_) => 400,
                    AppError::Forbidden => 403,
                    AppError::Storage(_) | AppError::Internal(_) => 500,
                }
            }

            pub fn public_message(err: &AppError) -> String {
                match err {
                    AppError::NotFound(msg)
                    | AppError::Conflict(msg)
                    | AppError::Validation(msg) => msg.clone(),
                    AppError::Forbidden => String::from("доступ запрещён"),
                    AppError::Storage(_) | AppError::Internal(_) => String::from("внутренняя ошибка"),
                }
            }
            """
        ),
        text(
            "Функция `public_message` отвечает на второй вопрос — что можно показать клиенту. Тексты "
            "внутренних ошибок содержат имена таблиц и адреса, поэтому наружу они не уходят; подробности "
            "пишутся в лог с идентификатором запроса. В `axum` функцию `status_code` не пишут вручную: "
            "достаточно реализовать для `AppError` трейт `IntoResponse`.\n\n"
            "`anyhow` удобен на верхнем уровне и в тестах, где важен факт ошибки. `thiserror` — в слоях, "
            "где вызывающий должен различать варианты. Совместить их просто: в `AppError` остаётся вариант "
            "`Internal(anyhow::Error)` для всего, что не требует отдельной реакции."
        ),
        heading("Внедрение зависимостей"),
        text(
            "**Внедрение зависимостей** (Dependency Injection, DI) означает, что объект не создаёт "
            "зависимости сам, а получает их снаружи. В Rust есть два механизма.\n\n"
            "**Параметр типа** — `UserService<R: UserRepository>` — даёт статическую диспетчеризацию: "
            "компилятор знает точный тип, вызовы встраиваются, накладных расходов нет. Так пишут сервисы. "
            "**Трейт-объект** — `Arc<dyn UserRepository>` — стирает конкретный тип и позволяет хранить "
            "разные реализации в одном поле ценой косвенного вызова. Он нужен там, где тип выбирается во "
            "время выполнения: в общем состоянии сервера, в плагинах.\n\n"
            "Сборка происходит в одном месте — в `main` или функции построения состояния. Только этот код "
            "знает конкретные типы, поэтому замена базы данных затрагивает десяток строк."
        ),
        example(
            "rust",
            r"""
            use std::sync::Arc;

            pub struct AppState {
                pub user_repo: Arc<dyn UserRepository>,
                pub config: AppConfig,
            }

            impl AppState {
                // Сборка «боевой» конфигурации.
                pub fn production(config: AppConfig) -> Self {
                    let repo = PgUserRepository::connect(&config.database_url, config.max_connections);
                    Self {
                        user_repo: Arc::new(repo),
                        config,
                    }
                }

                // Сборка тестовой и локальной конфигурации: та же структура, другой репозиторий.
                pub fn for_tests(config: AppConfig) -> Self {
                    Self {
                        user_repo: Arc::new(InMemoryUserRepository::default()),
                        config,
                    }
                }
            }

            fn handle_rename(state: &AppState, id: u64, name: &str) -> Result<User, AppError> {
                let service = UserService::new(Arc::clone(&state.user_repo));
                service.rename(id, name)
            }
            """
        ),
        text(
            "Реализация трейта для хранения в `Arc<dyn ...>` должна удовлетворять `Send + Sync`, если "
            "состояние делится между потоками, — поэтому требование указано над объявлением трейта. "
            "`Arc::clone` дёшев: он лишь увеличивает счётчик ссылок. Внутри обработчика проще принять "
            "`&AppState`, а не владеть копией. Асинхронные сервисы с трейт-объектами требуют `async_trait` "
            "или `Pin<Box<dyn Future + Send>>`."
        ),
        table(
            ["Критерий", "Параметр типа `R: Repo`", "Трейт-объект `Arc<dyn Repo>`"],
            [
                ["Скорость вызова", "статическая диспетчеризация, встраивание", "косвенный вызов через таблицу"],
                ["Размер типа", "зависит от реализации, возможен мономорфизм", "фиксированный размер указателя"],
                ["Подмена во время выполнения", "невозможна без пересборки", "возможна через конфигурацию"],
                ["Где применяют", "сервисы, бизнес-логика, тесты", "состояние сервера, плагины, наборы стратегий"],
                ["Сложность кода", "ниже, ошибки видны на этапе компиляции", "ниже для вызывающего, но выше для автора"],
            ],
        ),
        heading("Тестируемость архитектуры"),
        text(
            "Выгода от слоёв видна в тестах. Если сервис принимает трейт, тест подставляет реализацию в "
            "памяти или ручной мок и проверяет только логику: правила валидации, порядок вызовов, обработку "
            "ошибок. База, сеть и время не участвуют, поэтому тест идёт миллисекунды.\n\n"
            "Ручной мок в Rust пишут на `RefCell` внутри структуры: счётчики меняются через `&self`, как "
            "требует трейт. Это дешевле и прозрачнее генерации библиотекой. Набор тестов трёхуровневый: "
            "модульные тесты домена, тесты сервисов с подделками, интеграционные тесты с настоящей базой в "
            "контейнере. Последние в разы дороже, поэтому их немного."
        ),
        example(
            "rust",
            r"""
            use std::cell::RefCell;

            #[derive(Default)]
            struct SpyUserRepository {
                stored: RefCell<Vec<User>>,
                calls: RefCell<Vec<String>>,
                email_taken: bool,
            }

            impl UserRepository for SpyUserRepository {
                fn find_by_id(&self, id: u64) -> Result<Option<User>, DomainError> {
                    self.calls.borrow_mut().push(format!("find_by_id({id})"));
                    Ok(self.stored.borrow().iter().find(|u| u.id == id).cloned())
                }

                fn find_by_email(&self, email: &str) -> Result<Option<User>, DomainError> {
                    self.calls.borrow_mut().push(format!("find_by_email({email})"));
                    if self.email_taken {
                        Ok(Some(User {
                            id: 7,
                            email: email.to_string(),
                            name: "Занято".into(),
                        }))
                    } else {
                        Ok(None)
                    }
                }

                fn save(&self, user: &User) -> Result<(), DomainError> {
                    self.calls.borrow_mut().push(String::from("save"));
                    self.stored.borrow_mut().push(user.clone());
                    Ok(())
                }
            }

            #[cfg(test)]
            mod tests {
                use super::*;

                #[test]
                fn create_user_stores_normalized_email() {
                    let repo = SpyUserRepository::default();
                    let service = UserService::new(&repo);

                    let user = service
                        .create_user(CreateUserCommand {
                            email: "  Anna@Example.COM ".into(),
                            name: "Анна".into(),
                        })
                        .expect("пользователь должен создаться");

                    assert_eq!(user.email, "anna@example.com");
                    assert_eq!(repo.calls.borrow().len(), 2);
                    assert_eq!(repo.stored.borrow().len(), 1);
                }

                #[test]
                fn taken_email_returns_conflict() {
                    let repo = SpyUserRepository {
                        email_taken: true,
                        ..Default::default()
                    };
                    let service = UserService::new(&repo);

                    let result = service.create_user(CreateUserCommand {
                        email: "anna@example.com".into(),
                        name: "Анна".into(),
                    });

                    assert_eq!(result, Err(CreateUserError::EmailTaken));
                    assert!(repo.stored.borrow().is_empty());
                }
            }
            """
        ),
        text(
            "Оба теста проходят без базы и без асинхронного рантайма. Первый проверяет не только результат, "
            "но и поведение: два обращения к хранилищу. Второй убеждается, что при конфликте запись не "
            "создаётся. Для этого и нужен счётчик вызовов: без него тест прошёл бы и при сохранении "
            "«на всякий случай» после ошибки."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["God Object: один `AppService` со всеми методами", "файл растёт, тесты идут минутами, правки конфликтуют", "разбить на сервисы по сценариям, по одному действию на метод"],
                ["Anemic Domain: сущность только из полей", "правила пересчитываются в каждом обработчике по-своему", "перенести правила в методы сущности: `change_email`, `cancel`"],
                ["SQL прямо в сервисе", "логика зависит от схемы таблицы, тест требует базу", "репозиторий с методами «по смыслу», а не «по запросу»"],
                ["В сигнатурах конкретные типы `PgPool`, `Reqwest`", "слой нельзя протестировать без сети", "зависимость через трейт или обёртку с узким набором методов"],
                ["`std::env::var` в разных модулях", "список обязательных переменных неизвестен, тесты зависят от окружения", "одна структура `AppConfig`, собранная в `main`"],
                ["Сущность сериализуется напрямую в ответ", "хеш пароля и служебные поля уходят клиенту", "отдельный DTO ответа и реализация `From`"],
                ["Циклическая зависимость модулей", "неудобный `use`, невозможность вынести крейт", "вынести общий контракт в домен, направить стрелки к нему"],
                ["`unwrap` в обработчике", "паника обрушивает соединение вместо кода 500", "возвращать `Result` и отдавать ошибку через `IntoResponse`"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняйте по порядку в одном проекте: `cargo new layered_app && cd layered_app`. "
            "Проверяйте сборку `cargo check` и тесты `cargo test`."
        ),
        numbered(
            "Разложите проект по модулям `domain`, `application`, `infrastructure`, `presentation` и перенесите в домен `User` с трейтом `UserRepository`.",
            "Реализуйте `InMemoryUserRepository` поверх `RwLock<HashMap<u64, User>>` и протестируйте сохранение и поиск по идентификатору и почте.",
            "Добавьте в сервис метод `rename(&self, id, name)` с ошибками `NotFound` и `Validation` для имени короче двух символов.",
            "Соберите `AppConfig` с адресом, размером пула и строкой подключения из переменных окружения и напишите тест на переопределение.",
            "Опишите `AppError` через `thiserror` с вариантами `NotFound`, `Conflict`, `Validation`, `Forbidden`, `Internal` и функцию перевода в код ответа.",
            "Напишите тест сервиса с мок-репозиторием на `RefCell`, который считает вызовы `save`, и проверьте отсутствие сохранения при конфликте.",
        ),
        text(
            "Ожидаемая структура после первого задания."
        ),
        example(
            "text",
            """
            src/
            ├── domain/
            │   ├── mod.rs
            │   ├── models.rs
            │   └── repositories.rs
            ├── application/
            │   └── services.rs
            ├── infrastructure/
            │   └── in_memory.rs
            ├── config.rs
            └── main.rs
            """
        ),
        callout(
            "success",
            "Подсказка к заданию 5",
            "Начните функцию перевода в код с `match err` по всем вариантам — компилятор не даст пропустить "
            "ни одного. Если код ответа нужен только HTTP-слою, оставьте его там: домен не должен знать "
            "про 404 и 409.",
        ),
        *check_yourself(
            (
                "В каком направлении должны быть направлены зависимости между слоями и почему?",
                "Зачем сервису параметр типа `R: UserRepository` вместо конкретной структуры репозитория?",
                "Почему нельзя сериализовать доменную сущность `User` напрямую в ответ API?",
                "Какой результат дают атрибуты `#[error(\"...\")]` и `#[from]` в `thiserror`?",
                "Когда стоит выбрать `Arc<dyn Trait>`, а когда — параметр типа?",
                "Почему тест сервиса с реализацией в памяти называют модульным, а не интеграционным?",
            ),
            (
                "Зависимости направлены к домену: домен не знает ни о чём, прикладной слой знает домен, "
                "инфраструктура реализует его трейты, интерфейс зависит от прикладного. Так правила можно "
                "менять и тестировать без базы и транспорта.",
                "Сервис не фиксируется на конкретной реализации: в рабочей сборке в него передаётся "
                "репозиторий поверх СУБД, в тесте — структура в памяти. Логика не дублируется, а вызовы "
                "остаются статическими.",
                "В сущности лежат хеш пароля, флаги ролей и счётчик версии. При сериализации они попадут в "
                "ответ и утекут клиенту. DTO ответа перечисляет только разрешённые поля.",
                "`#[error(\"...\")]` реализует `Display` с подстановкой полей, а `#[from]` генерирует "
                "`impl From<Источник>` для варианта. Второе позволяет использовать `?` без `map_err`.",
                "`Arc<dyn Trait>` нужен, когда реализация выбирается во время выполнения или хранится в общем "
                "состоянии. Параметр типа предпочтителен в сервисах: он быстрее и даёт ошибки при компиляции.",
                "Тест модульный, потому что проверяет один компонент с подставными зависимостями, не поднимая "
                "базу, сеть и файловую систему. Интеграционный тест проверяет несколько слоёв вместе.",
            ),
        ),
        *outro(
            (
                "Слои `domain`, `application`, `infrastructure`, `presentation` разделяют правила, сценарии, технические детали и транспорт; зависимости направлены к домену.",
                "Репозиторий — трейт в домене; реализации бывают настоящие, в памяти и моковые, и именно они делают сервис тестируемым.",
                "Сервисный слой содержит сценарии: команды меняют состояние, запросы только читают; обработчик остаётся тонким.",
                "DTO отделяют внешний контракт от доменной сущности, скрывают служебные поля и создаются реализацией `From`.",
                "Конфигурация собирается в одну типизированную структуру из файла и переменных окружения до запуска логики.",
                "Единый `AppError` с `thiserror` различает причины, а слой интерфейса решает, какой код и текст увидит клиент.",
                "Внедрение зависимостей делают параметром типа для скорости и `Arc<dyn Trait>` для выбора во время выполнения.",
                "Антипаттерны — God Object, Anemic Domain, Leaky Abstraction, Tight Coupling, размазанная конфигурация — проще заметить, когда слои разделены.",
            ),
            "Архитектура задаёт каркас для остального курса: асинхронная обработка запросов и база данных "
            "будут опираться на сервисы и репозитории из этого урока. Следующий урок посвящён умным "
            "указателям: `Box`, `Rc`, `Arc`, `RefCell` и внутренней изменяемости — именно они лежат в основе "
            "`Arc<dyn Trait>` из состояния приложения.",
            (
                "The Rust Programming Language, глава о модулях и видимости — doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html",
                "Rust API Guidelines: интерфейсы и параметры типа — rust-lang.github.io/api-guidelines",
                "Domain Modeling Made Functional, Scott Wlaschin — о типах как описании домена",
                "Architecture Patterns with Python, Percival и Gregory — переносимые идеи слоёв и репозиториев",
                "Крейт `thiserror`: документация — docs.rs/thiserror",
                "Крейт `config`: документация — docs.rs/config",
            ),
        ),
    ],
}
