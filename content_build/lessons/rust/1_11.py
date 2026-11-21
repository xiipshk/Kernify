"""Урок 1.11 курса Rust: первый проект."""

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
    "program_order": 1,
    "topic_order": 11,
    "name": "1.11. Первый проект",
    "slug": "rust-1-11-первый-проект",
    "short_description": (
        "Собираем консольный менеджер задач: разбиваем код на модули, храним данные "
        "в JSON-файле, разбираем команды пользователя и обрабатываем ошибки."
    ),
    "topic_name": "Первый проект",
    "topic_description": (
        "Итоговый проект уровня «Начинающий»: консольное приложение для списка задач "
        "с командами add, list, done, remove, help и quit. Данные сохраняются в JSON-файл. "
        "Урок собирает вместе структуры, перечисления, коллекции, модули, трейты "
        "и обработку ошибок, а в конце показывает, как расширять проект и тестировать его."
    ),
    "learning_objectives": [
        "Создавать проект через `cargo new`, добавлять зависимости в `Cargo.toml` и запускать его командами `cargo run` и `cargo build --release`",
        "Раскладывать программу на модули: `models`, `storage` и `commands`, связывать их через `lib.rs` и `mod`",
        "Описывать задачу структурой с `#[derive]` и печатать её через реализацию трейта `Display`",
        "Хранить задачи в `HashMap` и сохранять их в JSON-файл, восстанавливая состояние при следующем запуске",
        "Разбирать строку ввода в перечисление команд и реагировать на неверный ввод без паники",
        "Обрабатывать ошибки файловых операций через `Result` и оператор `?`, а потерю данных — с запасным вариантом",
        "Писать модульные тесты для логики хранения и разбора команд",
        "Планировать расширение проекта: фильтры, приоритеты, поиск, экспорт.",
    ],
    "estimated_minutes": 30,
    "xp_reward": 10,
    "difficulty": "beginner",
    "tags": [
        "rust",
        "проект",
        "cli",
        "cargo",
        "модули",
        "json",
        "ошибки",
    ],
    "starter_code": code(
        r"""
        use std::collections::HashMap;

        #[derive(Debug, Clone, PartialEq)]
        struct Task {
            id: u64,
            text: String,
            completed: bool,
        }

        struct TaskStore {
            tasks: HashMap<u64, Task>,
            next_id: u64,
        }

        impl TaskStore {
            fn new() -> Self {
                TaskStore {
                    tasks: HashMap::new(),
                    next_id: 1,
                }
            }

            fn add(&mut self, text: &str) -> &Task {
                let id = self.next_id;
                self.next_id += 1;
                self.tasks.insert(
                    id,
                    Task {
                        id,
                        text: text.to_string(),
                        completed: false,
                    },
                );
                self.tasks.get(&id).unwrap()
            }

            fn complete(&mut self, id: u64) -> bool {
                match self.tasks.get_mut(&id) {
                    Some(task) => {
                        task.completed = true;
                        true
                    }
                    None => false,
                }
            }
        }

        fn main() {
            let mut store = TaskStore::new();
            store.add("Изучить Rust");
            store.add("Собрать первый проект");
            store.complete(1);

            let mut tasks: Vec<&Task> = store.tasks.values().collect();
            tasks.sort_by_key(|task| task.id);
            for task in tasks {
                let mark = if task.completed { "x" } else { " " };
                println!("[{}] {}: {}", mark, task.id, task.text);
            }
        }
        """
    ),
    "hints": [
        "Создать проект: `cargo new todo_cli`, затем `cd todo_cli`. Файл `src/main.rs` уже содержит заготовку `fn main`.",
        "Для JSON добавьте в `[dependencies]` в `Cargo.toml` две строки: `serde = { version = \"1.0\", features = [\"derive\"] }` и `serde_json = \"1.0\"`, затем запустите `cargo build`, чтобы пакеты скачались.",
        "Если файл `tasks.json` ещё не существует, это не ошибка: возвращайте пустое хранилище через `TaskStore::default()`.",
        "Разбор команды удобно делать через `input.split_whitespace().collect::<Vec<_>>()` и `match` по `parts.as_slice()`.",
        "Оператор `?` в `main` работает только при возвращаемом типе `Result`, например `fn main() -> Result<(), Box<dyn std::error::Error>>`.",
    ],
    "content": [
        text(
            "Одиннадцать уроков курса дали набор инструментов: переменные и типы, функции, владение и ссылки, "
            "коллекции, структуры и перечисления, обработку ошибок, модули с Cargo, трейты и дженерики. "
            "По отдельности каждый из них выглядит простым, но настоящая проверка понимания — собрать из них "
            "работающую программу. Этим мы и займёмся: напишем **консольный менеджер задач** со списком дел.\n\n"
            "Приложение принимает команды в цикле: `add` добавляет задачу, `list` показывает список, `done` отмечает "
            "задачу выполненной, `remove` удаляет её, `help` печатает справку, `quit` завершает работу. "
            "Между запусками данные не теряются: они лежат в текстовом файле `tasks.json` в формате JSON.\n\n"
            "Проект небольшой, около двухсот строк, но в нём есть всё необходимое: чтение ввода, разбор команды, "
            "изменение коллекции, запись в файл и аккуратная реакция на ошибки. Готовый код можно расширять — "
            "в конце урока даны упражнения."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "создавать проект через `cargo new`, добавлять зависимости в `Cargo.toml` и запускать его командами `cargo run` и `cargo build --release`;",
            "раскладывать программу на модули `models`, `storage` и `commands`, связывать их через `lib.rs` и объявления `mod`;",
            "описывать задачу структурой с `#[derive]` и печатать её через реализацию трейта `Display`;",
            "хранить задачи в `HashMap` и сохранять их в JSON-файл, восстанавливая состояние при следующем запуске;",
            "разбирать строку ввода в перечисление команд и реагировать на неверный ввод без паники;",
            "обрабатывать ошибки файловых операций через `Result` и оператор `?`, а потерю данных — с запасным вариантом;",
            "писать модульные тесты для логики хранения и разбора команд;",
            "планировать расширение проекта: фильтры, приоритеты, поиск, экспорт.",
        ),
        heading("Что делает приложение"),
        text(
            "Перед написанием кода стоит зафиксировать поведение: не «что удобно писать», а «что должна уметь "
            "программа». Команды приложения:\n"
            "- `add \"текст задачи\"` — создать задачу с новым номером;\n"
            "- `list` — вывести все задачи по порядку номеров с отметкой о выполнении;\n"
            "- `done <номер>` — отметить задачу выполненной;\n"
            "- `remove <номер>` — удалить задачу;\n"
            "- `help` — напомнить доступные команды;\n"
            "- `quit` — выйти из программы.\n\n"
            "Все изменения сохраняются в файл `tasks.json` рядом с исполняемым кодом. Если файла нет, приложение "
            "начинает с пустого списка; повреждённый файл не должен ронять программу."
        ),
        table(
            ["Команда", "Вход", "Действие", "Ответ программы"],
            [
                ["add", "`add \"Купить хлеб\"`", "Создать задачу с новым номером", "`Задача 3 добавлена`"],
                ["list", "`list`", "Показать задачи по порядку", "`[ ] 1: Купить хлеб`"],
                ["done", "`done 1`", "Отметить задачу выполненной", "`Задача 1 выполнена`"],
                ["remove", "`remove 2`", "Удалить задачу", "`Задача 2 удалена`"],
                ["help", "`help`", "Напечатать справку", "Список команд"],
                ["quit", "`quit`", "Завершить программу", "`До свидания`"],
            ],
        ),
        heading("Структура проекта и Cargo"),
        text(
            "Проект создаётся командой `cargo new todo_cli` — Cargo подготовит папку и два файла: манифест "
            "`Cargo.toml` и `src/main.rs`. Код разложим по модулям и добавим ещё `src/lib.rs`: логика живёт в "
            "библиотеке, а `main.rs` только читает ввод и вызывает функции.\n\n"
            "**Манифест** (manifest) — файл `Cargo.toml` с метаданными пакета и списком зависимостей. "
            "**Крейт** (crate) — единица компиляции; в нашем случае их два: библиотека `todo_cli` и бинарник. "
            "**Модуль** (module) — именованная группа функций и типов внутри крейта.\n\n"
            "Дерево файлов выглядит так:\n"
            "```\n"
            "todo_cli/\n"
            "├── Cargo.toml\n"
            "└── src/\n"
            "    ├── main.rs      — точка входа бинарника\n"
            "    ├── lib.rs       — корень библиотеки\n"
            "    ├── models.rs    — структура Task\n"
            "    ├── storage.rs   — чтение и запись tasks.json\n"
            "    └── commands.rs  — разбор и выполнение команд\n"
            "```\n"
            "Файл `models.rs` внутри `src` становится модулем `models`, если объявить `mod models;` в `lib.rs`. "
            "Папки с `mod.rs` нужны только для вложенных модулей, здесь достаточно плоской структуры."
        ),
        example(
            "toml",
            """
            [package]
            name = "todo_cli"
            version = "0.1.0"
            edition = "2021"

            [dependencies]
            serde = { version = "1.0", features = ["derive"] }
            serde_json = "1.0"
            """,
        ),
        text(
            "Крейт `serde` описывает, как превращать значения Rust в текст и обратно, а `serde_json` добавляет "
            "формат JSON. Флаг `features = [\"derive\"]` включает процедурный макрос `#[derive(Serialize, Deserialize)]`, "
            "который генерирует код преобразования. Встроенных средств для JSON в стандартной библиотеке нет.\n\n"
            "**JSON** (JavaScript Object Notation) — текстовый формат, где объекты записываются в фигурных скобках, "
            "а поля — парами «ключ: значение». **Зависимость** (dependency) — внешний крейт из реестра crates.io. "
            "После правки `Cargo.toml` запустите `cargo build`: Cargo скачает пакеты и запишет точные версии "
            "в `Cargo.lock`."
        ),
        callout(
            "info",
            "Как запустить проект",
            "`cargo run` собирает и сразу запускает программу. `cargo build` только собирает, `cargo build --release` "
            "собирает оптимизированную версию в `target/release/todo_cli`. `cargo test` запускает тесты. "
            "Для учебного проекта достаточно `cargo run`.",
        ),
        heading("Модель задачи"),
        text(
            "Модуль `models` описывает, что такое задача. Структура `Task` содержит номер `id`, текст `text`, "
            "признак выполнения `completed` и время создания `created_at`. Время фиксируется один раз при "
            "добавлении.\n\n"
            "Атрибут `#[derive(...)]` автоматически реализует стандартные трейты: `Debug` даёт форматирование через "
            "`{:?}` для отладки, `Clone` позволяет делать копию задачи, `Serialize` и `Deserialize` обучают `serde` "
            "преобразованию в JSON и обратно, `PartialEq` разрешает сравнение через `==` (оно пригодится в тестах).\n\n"
            "Чтобы печатать задачу красиво, реализуем трейт `Display` вручную. Метод `fmt` пишет результат в "
            "переданный `Formatter` через макрос `write!`. Так `println!(\"{}\", task)` печатает строку без "
            "отдельного метода."
        ),
        example(
            "rust",
            r"""
            use serde::{Deserialize, Serialize};
            use std::fmt;

            #[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
            pub struct Task {
                pub id: u64,
                pub text: String,
                pub completed: bool,
                pub created_at: String,
            }

            impl Task {
                pub fn new(id: u64, text: String, created_at: String) -> Self {
                    Task {
                        id,
                        text,
                        completed: false,
                        created_at,
                    }
                }
            }

            impl fmt::Display for Task {
                fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                    let mark = if self.completed { "[x]" } else { "[ ]" };
                    write!(f, "{} {}: {} ({})", mark, self.id, self.text, self.created_at)
                }
            }

            fn main() {
                let task = Task::new(1, String::from("Купить хлеб"), String::from("2024-01-15 10:30"));
                println!("{}", task);
                println!("{:?}", task);
            }
            """,
        ),
        text(
            "Вывод:\n"
            "```\n"
            "[ ] 1: Купить хлеб (2024-01-15 10:30)\n"
            "Task { id: 1, text: \"Купить хлеб\", completed: false, created_at: \"2024-01-15 10:30\" }\n"
            "```\n"
            "Первая строка получена через `Display`, вторая — через `Debug`. Как видите, время передаётся в "
            "конструктор готовой строкой: так проект остаётся без лишних зависимостей. Получить настоящее время "
            "из системы можно крейтом `chrono`, но для учебного проекта достаточно того, что формат времени "
            "не влияет на остальную логику."
        ),
        callout(
            "info",
            "Почему поле `created_at` — строка",
            "Хранение времени строкой упрощает сохранение: JSON-поле тоже будет строкой, и никаких правил "
            "преобразования не нужно. Если позже потребуется сортировать по дате, формат `ГГГГ-ММ-ДД ЧЧ:ММ` "
            "лексикографически совпадает с хронологическим порядком, и сортировка строками даст верный результат.",
        ),
        heading("Хранилище и JSON"),
        text(
            "Хранилище отвечает за данные и за их сохранение. В памяти задачи лежат в `HashMap<u64, Task>`: ключ — "
            "номер задачи, значение — сама задача. Отдельно хранится счётчик `next_id`, чтобы удалённые номера "
            "не использовались повторно.\n\n"
            "`HashMap` — хеш-таблица из стандартной библиотеки: поиск по ключу выполняется в среднем за постоянное "
            "время, но порядок перебора не определён, поэтому при выводе список придётся сортировать.\n\n"
            "Чтение и запись выполняются через `std::fs`: `fs::read_to_string` возвращает `Result<String, io::Error>`, "
            "`fs::write` — `Result<(), io::Error>`, а функции `serde_json` — результаты с ошибкой разбора. Все они "
            "соединяются оператором `?`: если операция вернула ошибку, функция немедленно вернёт её наверх.\n\n"
            "Функция `load` возвращает готовое хранилище в трёх случаях: файл отсутствует, файл пуст, либо JSON "
            "разобран успешно. Ошибкой становится только сбой чтения или синтаксиса."
        ),
        example(
            "rust",
            r"""
            use serde::{Deserialize, Serialize};
            use std::collections::HashMap;
            use std::fs;
            use std::path::Path;

            #[derive(Serialize, Deserialize, Default)]
            pub struct TaskStore {
                tasks: HashMap<u64, Task>,
                next_id: u64,
            }

            pub struct JsonStorage {
                path: String,
            }

            impl JsonStorage {
                pub fn new(path: impl Into<String>) -> Self {
                    JsonStorage { path: path.into() }
                }

                fn load(&self) -> Result<TaskStore, Box<dyn std::error::Error>> {
                    if !Path::new(&self.path).exists() {
                        return Ok(TaskStore { tasks: HashMap::new(), next_id: 1 });
                    }
                    let content = fs::read_to_string(&self.path)?;
                    if content.trim().is_empty() {
                        return Ok(TaskStore { tasks: HashMap::new(), next_id: 1 });
                    }
                    let store = serde_json::from_str(&content)?;
                    Ok(store)
                }

                fn save(&self, store: &TaskStore) -> Result<(), Box<dyn std::error::Error>> {
                    let content = serde_json::to_string_pretty(store)?;
                    fs::write(&self.path, content)?;
                    Ok(())
                }
            }
            """,
        ),
        text(
            "Тип `Box<dyn std::error::Error>` означает «любая ошибка, помещённая в кучу». Это удобный способ "
            "собрать в одной функции разные виды ошибок: у `fs` и у `serde_json` они разные, но обе реализуют "
            "трейт `Error`, поэтому подходят под такую общую обёртку. `Box` — умный указатель на данные в куче, "
            "а `dyn Error` — динамический тип, известный только в момент выполнения. Конструкция знакома по "
            "предыдущим урокам и избавляет от множества ручных `match`."
        ),
        example(
            "json",
            """
            {
              "tasks": {
                "1": {
                  "id": 1,
                  "text": "Купить хлеб",
                  "completed": false,
                  "created_at": "2024-01-15 10:30"
                },
                "2": {
                  "id": 2,
                  "text": "Собрать первый проект",
                  "completed": true,
                  "created_at": "2024-01-15 10:31"
                }
              },
              "next_id": 3
            }
            """,
        ),
        text(
            "Так выглядит `tasks.json` после двух добавлений и одной отметки о выполнении. Ключи объекта JSON — "
            "всегда строки, поэтому числовые ключи `HashMap<u64, ...>` при сохранении превращаются в `\"1\"` и "
            "`\"2\"`, а при чтении разбираются обратно автоматически благодаря `Deserialize`."
        ),
        callout(
            "warning",
            "Проверяйте файл, а не только код",
            "Частая ошибка — читать файл другим путём, чем записывать. Путь `tasks.json` относителен текущей "
            "папки: если запустить `cargo run` из другой директории, программа создаст новый файл там. "
            "Запускайте `cargo run` из корня проекта.",
        ),
        heading("Методы хранилища"),
        text(
            "Поверх `load` и `save` удобно построить четыре метода: `all`, `add`, `complete` и `remove`. "
            "Каждый читает файл, меняет нужное поле и записывает его обратно: состояние всегда на диске.\n\n"
            "Важная деталь — `get_mut`. Метод `HashMap::get_mut(&id)` возвращает `Option<&mut Task>`: изменяемую "
            "ссылку на задачу, если она есть. Через неё мы меняем поле `completed`, не извлекая задачу из таблицы. "
            "Аналогично `remove(&id)` возвращает `Option<Task>` — удалённую задачу или `None`.\n\n"
            "`sort_by_key(|task| task.id)` упорядочивает срез по номеру: замыкание получает ссылку на задачу "
            "и возвращает ключ сортировки."
        ),
        example(
            "rust",
            r"""
            impl JsonStorage {
                pub fn all(&self) -> Result<Vec<Task>, Box<dyn std::error::Error>> {
                    let store = self.load()?;
                    let mut tasks: Vec<Task> = store.tasks.into_values().collect();
                    tasks.sort_by_key(|task| task.id);
                    Ok(tasks)
                }

                pub fn add(&self, text: String) -> Result<Task, Box<dyn std::error::Error>> {
                    let mut store = self.load()?;
                    let id = store.next_id;
                    let task = Task::new(id, text, String::from("только что"));
                    store.next_id += 1;
                    store.tasks.insert(id, task.clone());
                    self.save(&store)?;
                    Ok(task)
                }

                pub fn complete(&self, id: u64) -> Result<(), Box<dyn std::error::Error>> {
                    let mut store = self.load()?;
                    match store.tasks.get_mut(&id) {
                        Some(task) => {
                            task.completed = true;
                            self.save(&store)?;
                            Ok(())
                        }
                        None => Err(format!("Задача {} не найдена", id).into()),
                    }
                }

                pub fn remove(&self, id: u64) -> Result<(), Box<dyn std::error::Error>> {
                    let mut store = self.load()?;
                    if store.tasks.remove(&id).is_some() {
                        self.save(&store)?;
                        Ok(())
                    } else {
                        Err(format!("Задача {} не найдена", id).into())
                    }
                }
            }
            """,
        ),
        text(
            "Выражение `format!(...).into()` превращает строку в `Box<dyn Error>`: для `String` есть реализация "
            "трейта `From`, поэтому `.into()` работает. Всё, что возвращает `Result<T, E>`, где `E` реализует "
            "`Error`, можно превратить в `Box<dyn Error>`.\n\n"
            "Обратите внимание на владение в `all`: `store.tasks.into_values()` забирает `HashMap` по значению, "
            "поэтому `store` объявлен без `mut`. Метод `.values()` потребовал бы клонировать каждую задачу."
        ),
        heading("Разбор команд"),
        text(
            "Ввод пользователя приходит строкой, и прежде всего её нужно превратить в понятную структуру. "
            "Лучше всего подходит перечисление: каждый вариант описан явно, а `match` заставит обработать все "
            "варианты.\n\n"
            "`split_whitespace()` разбивает строку по пробелам, пропуская лишние. Собрав срез `&[&str]`, "
            "мы сопоставляем его с шаблонами в `match`. Шаблон `[\"add\", rest @ ..]` связывает хвост срезов с `rest`, "
            "а условие `if !rest.is_empty()` отсекает команду без текста. Ветка `[\"done\", id]` разбирает номер через "
            "`id.parse()`: метод возвращает `Result<u64, _>`, а `.ok()` превращает его в `Option<u64>`.\n\n"
            "Функция `parse` возвращает `Option<Command>`: `Some`, если команда распознана, и `None`, если нет. "
            "Так неверный ввод не становится аварией программы."
        ),
        example(
            "rust",
            r"""
            #[derive(Debug, PartialEq)]
            pub enum Command {
                Add(String),
                List,
                Done(u64),
                Remove(u64),
                Help,
                Quit,
            }

            pub fn parse(input: &str) -> Option<Command> {
                let parts: Vec<&str> = input.split_whitespace().collect();
                match parts.as_slice() {
                    ["add", rest @ ..] if !rest.is_empty() => {
                        Some(Command::Add(rest.join(" ")))
                    }
                    ["list"] => Some(Command::List),
                    ["done", id] => id.parse().ok().map(Command::Done),
                    ["remove", id] | ["rm", id] => id.parse().ok().map(Command::Remove),
                    ["help"] => Some(Command::Help),
                    ["quit"] => Some(Command::Quit),
                    _ => None,
                }
            }

            fn main() {
                let samples = ["add Купить хлеб", "list", "done 2", "rm 3", "help", "quit", "add", "xyz 1"];
                for line in samples {
                    println!("{:>20?} -> {:?}", line, parse(line));
                }
            }
            """,
        ),
        text(
            "Вывод:\n"
            "```\n"
            "     \"add Купить хлеб\" -> Some(Add(\"Купить хлеб\"))\n"
            "                \"list\" -> Some(List)\n"
            "               \"done 2\" -> Some(Done(2))\n"
            "                 \"rm 3\" -> Some(Remove(3))\n"
            "                \"help\" -> Some(Help)\n"
            "                \"quit\" -> Some(Quit)\n"
            "                 \"add\" -> None\n"
            "               \"xyz 1\" -> None\n"
            "```\n"
            "Строка `add` без текста и неизвестная команда `xyz` дают `None`. Кавычки в команде можно не "
            "писать: `split_whitespace` склеит слова обратно через `join(\" \")`. Двойной шаблон "
            "`[\"remove\", id] | [\"rm\", id]` описывает псевдоним: обе записи дают один вариант перечисления."
        ),
        callout(
            "info",
            "Почему перечисление, а не набор `if`",
            "Распознавание в перечисление сразу на входе — признак аккуратной архитектуры. Дальше по программе "
            "уже не ходят «сырые» строки, поэтому невозможно забыть проверить регистр, лишние пробелы или "
            "неверный номер. Компилятор дополнительно проверяет, что при добавлении нового варианта `match` "
            "будет обновлён.",
        ),
        heading("Цикл ввода и точка входа"),
        text(
            "Осталось связать части в `main.rs`. Программа печатает приглашение `> `, читает строку со "
            "стандартного ввода, убирает перевод строки методом `trim`, разбирает команду и выполняет её. "
            "Цикл `loop` повторяется, пока команда `execute` не вернёт `false`.\n\n"
            "Тонкость: `print!` не выводит текст сразу, потому что буфер не сброшен, и приглашение не видно. "
            "Решение — `io::stdout().flush()?` после `print!`.\n\n"
            "Функция `execute` принимает команду по значению и хранилище по ссылке `&JsonStorage`: хранилище "
            "само управляет данными на диске. Возвращаемый `bool` отвечает, продолжать ли цикл: `false` "
            "приходит только от `Quit`."
        ),
        example(
            "rust",
            r"""
            pub fn execute(cmd: Command, storage: &JsonStorage) -> Result<bool, Box<dyn std::error::Error>> {
                match cmd {
                    Command::Add(text) => {
                        let task = storage.add(text)?;
                        println!("Задача добавлена: {}", task);
                    }
                    Command::List => {
                        let tasks = storage.all()?;
                        if tasks.is_empty() {
                            println!("Список задач пуст");
                        }
                        for task in tasks {
                            println!("{}", task);
                        }
                    }
                    Command::Done(id) => {
                        storage.complete(id)?;
                        println!("Задача {} выполнена", id);
                    }
                    Command::Remove(id) => {
                        storage.remove(id)?;
                        println!("Задача {} удалена", id);
                    }
                    Command::Help => print_help(),
                    Command::Quit => {
                        println!("До свидания");
                        return Ok(false);
                    }
                }
                Ok(true)
            }

            fn print_help() {
                println!("Команды:");
                println!("  add <текст>   — добавить задачу");
                println!("  list          — показать задачи");
                println!("  done <номер>  — отметить выполненной");
                println!("  remove <номер> — удалить задачу");
                println!("  help          — эта справка");
                println!("  quit          — выход");
            }
            """,
        ),
        example(
            "rust",
            r"""
            use std::io::{self, Write};
            use todo_cli::{commands::{execute, parse}, storage::JsonStorage};

            fn main() -> Result<(), Box<dyn std::error::Error>> {
                let storage = JsonStorage::new("tasks.json");
                println!("Менеджер задач. Введите help для справки.");

                loop {
                    print!("> ");
                    io::stdout().flush()?;

                    let mut input = String::new();
                    if io::stdin().read_line(&mut input)? == 0 {
                        break;
                    }
                    let input = input.trim();
                    if input.is_empty() {
                        continue;
                    }

                    match parse(input) {
                        Some(cmd) => {
                            if !execute(cmd, &storage)? {
                                break;
                            }
                        }
                        None => println!("Неизвестная команда. Введите help."),
                    }
                }
                Ok(())
            }
            """,
        ),
        text(
            "Строка `if io::stdin().read_line(&mut input)? == 0` обрабатывает конец файла: ноль байт означает, "
            "что ввод закончился (например, нажали Ctrl+D). Без этой проверки программа закрутилась бы в "
            "бесконечном цикле. Файл `lib.rs` объединяет модули и делает их видимыми:\n"
            "```\n"
            "pub mod commands;\n"
            "pub mod models;\n"
            "pub mod storage;\n"
            "```\n"
            "`main.rs` импортирует элементы по пути `todo_cli::storage::JsonStorage`."
        ),
        example(
            "text",
            """
            Менеджер задач. Введите help для справки.
            > add Купить хлеб
            Задача добавлена: [ ] 1: Купить хлеб (только что)
            > add Собрать первый проект
            Задача добавлена: [ ] 2: Собрать первый проект (только что)
            > list
            [ ] 1: Купить хлеб (только что)
            [ ] 2: Собрать первый проект (только что)
            > done 1
            Задача 1 выполнена
            > list
            [x] 1: Купить хлеб (только что)
            [ ] 2: Собрать первый проект (только что)
            > remove 2
            Задача 2 удалена
            > done 7
            Error: Задача 7 не найдена
            > quit
            До свидания
            """,
        ),
        text(
            "Сессия показывает, что происходит при команде с несуществующим номером: `execute` возвращает "
            "ошибку, `?` в `main` передаёт её наверх, и среда выполнения печатает `Error: Задача 7 не найдена`. "
            "Данные при этом уже сохранены.\n\n"
            "Такой вариант недружественен: лучше напечатать предупреждение и вернуться в цикл, перехватив "
            "ошибку одной команды через `match` без `?`."
        ),
        example(
            "rust",
            r"""
            Some(cmd) => {
                let should_continue = match execute(cmd, &storage) {
                    Ok(flag) => flag,
                    Err(error) => {
                        println!("Ошибка: {}", error);
                        true
                    }
                };
                if !should_continue {
                    break;
                }
            }
            """,
        ),
        heading("Тестирование логики"),
        text(
            "Одна из сильных сторон Rust — встроенный тестовый фреймворк. Тесты пишут в том же файле, "
            "что и код, внутри модуля с атрибутами `#[cfg(test)]` и `#[test]`. Атрибут `cfg(test)` означает, "
            "что модуль компилируется только при запуске `cargo test`.\n\n"
            "Для хранилища удобны тесты на чистой структуре `TaskStore`, без диска: такие проверки быстрые "
            "и не оставляют мусора. Макросы `assert_eq!` и `assert!` сравнивают значения и сообщают о "
            "расхождении.\n\n"
            "Отдельно тестируется разбор команд: он не имеет побочных эффектов. Ниже — тесты для `parse` "
            "и для изменений в хранилище."
        ),
        example(
            "rust",
            r"""
            #[cfg(test)]
            mod tests {
                use super::*;

                #[test]
                fn parses_add_with_text() {
                    assert_eq!(
                        parse("add Купить хлеб"),
                        Some(Command::Add(String::from("Купить хлеб")))
                    );
                }

                #[test]
                fn parses_alias_rm() {
                    assert_eq!(parse("rm 3"), Some(Command::Remove(3)));
                }

                #[test]
                fn rejects_unknown_input() {
                    assert_eq!(parse("xyz 1"), None);
                    assert_eq!(parse("done abc"), None);
                }

                #[test]
                fn completes_existing_task() {
                    let mut store = TaskStore::default();
                    let task = Task::new(7, String::from("Тест"), String::from("вручную"));
                    store.tasks.insert(7, task);
                    assert!(store.complete(7));
                    assert_eq!(store.tasks.get(&7).map(|t| t.completed), Some(true));
                }
            }
            """,
        ),
        text(
            "Вывод `cargo test`: четыре строки `test ... ok` и итоговая строка "
            "`test result: ok. 4 passed; 0 failed`. Если тест падает, Rust печатает ожидаемое и полученное "
            "значения."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Нет `features = [\"derive\"]` у `serde`", "Компилятор не находит макрос `Serialize`", "Указать флаг в `Cargo.toml` и пересобрать проект"],
                ["Чтение файла без проверки существования", "Ошибка `No such file or directory` при первом запуске", "Возвращать пустое хранилище, если `Path::new(&path).exists()` ложно"],
                ["`Task` без `Serialize` и `Deserialize`", "`serde_json` не может сохранить структуру", "Добавить оба трейта в `#[derive(...)]`"],
                ["Забытый `flush` после `print!`", "Приглашение `> ` не появляется", "Вызвать `io::stdout().flush()?` сразу после `print!`"],
                ["`next_id` не сохраняется", "Новая задача может получить уже занятый номер", "Хранить `next_id` в той же структуре и записывать вместе с задачами"],
                ["`parse` возвращает `Command` и паникует", "Неверный ввод падает с `panic!`", "Возвращать `Option<Command>` и обрабатывать `None`"],
                ["Бесконечный цикл на конце ввода", "Программа крутится после Ctrl+D", "Проверять, что `read_line` вернул больше нуля байт"],
            ],
        ),
        heading("Практика"),
        text(
            "Создайте проект командой `cargo new todo_cli`, добавьте зависимости и реализуйте модули по "
            "описанным шагам. После каждой задачи запускайте `cargo run`."
        ),
        numbered(
            "Создайте проект и пройдите первую сессию: `cargo new todo_cli`, заполните `Cargo.toml`, добавьте две задачи и выйдите. Убедитесь, что появился файл `tasks.json`, и откройте его в редакторе.",
            "Восстановление состояния: перезапустите программу и выполните `list`. Задачи должны остаться на месте. Затем удалите поля `completed` и `next_id` из файла вручную и проверьте, что программа сообщает об ошибке или начинает с чистого листа — в зависимости от выбранной стратегии.",
            "Фильтр по состоянию: добавьте команды `list pending` и `list done`. Подсказка: `Command::List` может иметь поле `Option<bool>` — `None` означает «все». Обновите `parse` и `execute`.",
            "Поиск: реализуйте команду `search <слово>`, выводящую задачи, текст которых содержит слово без учёта регистра. Подсказка: `task.text.to_lowercase().contains(&needle.to_lowercase())`.",
            "Тесты: напишите минимум три теста на `parse` и два на `TaskStore`. Запустите `cargo test` и добейтесь строки `test result: ok` без падений.",
        ),
        callout(
            "success",
            "Ориентир для первого задания",
            "После двух команд `add` содержимое `tasks.json` содержит объект `tasks` с ключами `\"1\"` и `\"2\"` "
            "и поле `next_id` равное 3. Если файл выглядит иначе, проверьте, что `JsonStorage::new` вызывается "
            "с путём `\"tasks.json\"` и что `save` вызывается после каждого изменения.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Зачем в проекте используется `HashMap<u64, Task>` с отдельным полем `next_id`, а не `Vec<Task>`?",
            "Что произойдёт, если файл `tasks.json` пуст, а функция `load` вызывается первый раз?",
            "Почему приглашение `> ` не появляется без `io::stdout().flush()?`",
            "Почему `parse` возвращает `Option<Command>`, а не сразу паникует на неверный ввод?",
            "Что делает оператор `?` в функции, возвращающей `Result<bool, Box<dyn std::error::Error>>`?",
            "Зачем тестовый модуль помечают атрибутом `#[cfg(test)]`?",
        ),
        heading("Ответы", 3),
        numbered(
            "Хеш-таблица даёт быстрый поиск и удаление по номеру, а `next_id` гарантирует, что удалённые номера не будут выданы повторно. В `Vec<Task>` пришлось бы каждый раз искать по индексу и отдельно считать свободный номер.",
            "Функция вернёт пустое хранилище: сначала сработает проверка существования пути, а для пустого содержимого — проверка `content.trim().is_empty()`. Ошибки не будет.",
            "Вывод стандартного потока буферизуется. Без сброса текст остаётся в буфере до следующего `println!`, а пользователь не видит, что программа ждёт ввода.",
            "Неверный ввод — обычная ситуация, а не авария. `Option<Command>` позволяет напечатать справку и продолжить цикл, не завершая программу и не теряя введённые ранее задачи.",
            "Если выражение вернуло `Err`, оператор `?` немедленно завершает функцию и возвращает ошибку наверх. Если `Ok`, функция получает внутреннее значение и продолжает работу.",
            "Атрибут `#[cfg(test)]` включает модуль только при компиляции для тестов. В итоговый бинарник тестовый код не попадает, поэтому он не увеличивает размер программы.",
        ),
        heading("Итоги"),
        bullets(
            "Проект начинается с `cargo new`, а зависимости описываются в `Cargo.toml`; `cargo run` собирает и запускает программу.",
            "Код разложен по модулям: `models` для структуры, `storage` для файла, `commands` для разбора и выполнения; `lib.rs` связывает их.",
            "`Task` выводит `Serialize` и `Deserialize` через `#[derive]`, а `Display` реализуется вручную для удобной печати.",
            "`HashMap` хранит задачи по номеру, `next_id` выдаёт новые номера, `Vec` и `sort_by_key` обеспечивают предсказуемый порядок вывода.",
            "`load` и `save` используют `fs` и `serde_json`, а оператор `?` передаёт ошибки наверх без ручных `match`.",
            "`Command` как перечисление и `match` по срезу делают разбор ввода явным и проверяемым компилятором.",
            "Цикл ввода требует `flush`, иначе приглашение не видно; конец ввода обрабатывается проверкой результата `read_line`.",
            "Логика покрывается тестами в модуле `#[cfg(test)]`, а ошибки выполнения не должны разрушать уже сохранённые данные.",
        ),
        heading("Что дальше"),
        text(
            "Уровень «Начинающий» завершён. Следующий уровень углубляется в устройство Rust: жизненные циклы, "
            "итераторы, умные указатели `Box`, `Rc` и `Arc`, многопоточность и асинхронное программирование. "
            "Инструменты из этого проекта пригодятся и там: большая программа всё равно состоит из модулей, "
            "структур и аккуратной обработки ошибок."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "The Rust Programming Language, глава 12 «An I/O Project: Building a Command Line Program» — официальный разбор CLI-проекта с тестами: https://doc.rust-lang.org/book/ch12-00-an-io-project.html",
            "The Rust Programming Language, глава 11 «Testing» — модульные и интеграционные тесты: https://doc.rust-lang.org/book/ch11-00-testing.html",
            "Документация `serde_json` — сериализация структур, работа с `Value` и ошибками разбора: https://docs.rs/serde_json/latest/serde_json/",
            "Документация `std::collections::HashMap` — все методы таблицы, включая `into_values`, `get_mut` и `entry`: https://doc.rust-lang.org/std/collections/struct.HashMap.html",
            "The Cargo Book — профили сборки, рабочие пространства и команды cargo: https://doc.rust-lang.org/cargo/",
            "Rust By Example, раздел «Error handling» — практические примеры `Result`, `Option` и собственных ошибок: https://doc.rust-lang.org/rust-by-example/error.html",
        ),
    ],
}
