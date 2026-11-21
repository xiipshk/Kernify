"""Урок 8 курса Rust: файлы, сеть и сериализация."""

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
    "topic_order": 8,
    "name": "2.8. Файлы, сеть и сериализация",
    "slug": "rust-2-8-файлы-сеть-и-сериализация",
    "topic_name": "Файлы, сеть и сериализация",
    "short_description": (
        "Работа с файловой системой и путями, трейты `std::io`, буферизация, сериализация структур через `serde`, "
        "HTTP-запросы и аккуратная обработка сетевых ошибок."
    ),
    "topic_description": (
        "Как читать и записывать файлы, строить кроссплатформенные пути, использовать трейты `Read`, `Write`, "
        "`Seek` и `BufRead`; как описывать структуры для `serde` и обмениваться данными в JSON и TOML; "
        "как выполнять HTTP-запросы и объединять источник данных, разбор формата и доменную модель в одну надёжную функцию."
    ),
    "learning_objectives": [
        "Читать и записывать файлы функциями `std::fs` и через дескрипторы `File` с `OpenOptions`",
        "Строить кроссплатформенные пути с `Path` и `PathBuf`, разбирать имя, расширение и родительский каталог",
        "Использовать трейты `Read`, `Write`, `Seek` и `BufRead`, включая буферизацию и построчное чтение",
        "Описывать структуры для `serde` и управлять форматом полей атрибутами `rename`, `default` и `skip_serializing_if`",
        "Сериализовать данные в JSON и TOML, разбирать их обратно и выбирать формат хранения под задачу",
        "Выполнять HTTP-запросы в блокирующем и асинхронном стиле, отличать ошибку транспорта от HTTP-статуса",
        "Объединять источник данных, разбор и доменную модель в функцию с понятной иерархией ошибок",
        "Избегать типичных промахов: неявное усечение файла, забытый `flush`, потерянный хвост буфера и `unwrap` на сетевых вызовах",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "rust",
        "файлы",
        "io",
        "serde",
        "json",
        "http",
    ],
    "starter_code": code(
        r"""
        use std::fs;
        use std::io;
        use std::path::{Path, PathBuf};

        #[derive(Debug, Clone, Copy)]
        enum Level {
            Info,
            Warning,
            Error,
        }

        impl Level {
            fn label(self) -> &'static str {
                match self {
                    Level::Info => "INFO",
                    Level::Warning => "WARN",
                    Level::Error => "ERROR",
                }
            }
        }

        fn entry(level: Level, message: &str) -> String {
            format!("[{}] {}\n", level.label(), message)
        }

        fn write_log(path: &Path, lines: &[String]) -> io::Result<()> {
            let content: String = lines.concat();
            fs::write(path, content)
        }

        fn count_lines(path: &Path) -> io::Result<usize> {
            let content = fs::read_to_string(path)?;
            Ok(content.lines().count())
        }

        fn main() -> io::Result<()> {
            let base = PathBuf::from("logs");
            fs::create_dir_all(&base)?;
            let file = base.join("app.log");

            let lines = [
                entry(Level::Info, "старт"),
                entry(Level::Warning, "медленный запрос"),
                entry(Level::Error, "нет соединения"),
            ];
            write_log(&file, &lines)?;

            if let Some(name) = file.file_name().and_then(|n| n.to_str()) {
                println!("файл: {}", name);
            }
            println!("строк: {}", count_lines(&file)?);
            Ok(())
        }
        """
    ),
    "hints": [
        "Для чтения целиком используйте `fs::read_to_string` и `fs::read`, а `File::open` берите, когда нужен поток или позиционирование.",
        "`File::create` усекает существующий файл. Чтобы дописывать, открывайте через `OpenOptions::new().create(true).append(true)`.",
        "Перед проверкой размера файла после записи через `BufWriter` вызывайте `flush`, иначе часть данных ещё лежит в памяти.",
        "Сетевой вызов возвращает `Result`, а не ошибку HTTP: проверяйте `status().is_success()` или вызывайте `error_for_status`.",
    ],
    "content": [
        text(
            "До сих пор программы внутри урока работали только с данными в памяти. Реальные утилиты читают "
            "настройки из файлов, сохраняют состояние на диск и обмениваются данными с удалёнными сервисами по "
            "HTTP. Все три сценария опираются на одни и те же идеи: источник данных может дать сбой, формат "
            "данных нужно проверить, а ошибку нужно донести до вызывающего кода в понятном виде.\n\n"
            "В Rust работа с внешним миром не отделена от системы типов. Чтение файла возвращает `io::Result`, "
            "разбор JSON — `serde_json::Error`, HTTP-вызов — `reqwest::Error`. Оператор `?` распространяет эти "
            "ошибки вверх, а тип возвращаемого значения функции документирует, что именно может пойти не так. "
            "Такой стиль позволяет объединять несколько шагов в одну цепочку без потери информации о сбое.\n\n"
            "Урок построен вокруг сквозного примера: приложение хранит журнал событий в файле, а список задач "
            "получает по сети и разбирает из JSON. Сначала разберём файловую систему и пути, затем трейты "
            "потокового ввода-вывода, затем сериализацию и, наконец, сетевые вызовы."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "читать и записывать файлы функциями `fs::read_to_string`, `fs::read` и `fs::write`;",
            "открывать файлы через `File` и `OpenOptions`, выбирая режим создания, перезаписи и дописывания;",
            "строить кроссплатформенные пути с `Path` и `PathBuf` и разбирать их на компоненты;",
            "использовать трейты `Read`, `Write`, `Seek` и `BufRead`, включая буферизацию и построчное чтение;",
            "описывать структуры для `serde` и настраивать формат полей атрибутами;",
            "обмениваться данными в JSON и TOML и выбирать формат под задачу;",
            "выполнять HTTP-запросы и правильно различать транспортные сбои и неуспешные статусы;",
            "собирать оба источника данных в одну функцию с понятной иерархией ошибок.",
        ),
        heading("Файловая система: `std::fs`"),
        text(
            "Модуль `std::fs` содержит удобные функции, которые выполняют одну операцию целиком. "
            "`fs::read_to_string` читает файл как `String` и проверяет, что содержимое является корректным UTF-8. "
            "`fs::read` читает те же данные как `Vec<u8>` — это единственный вариант для двоичных файлов. "
            "`fs::write` создаёт файл или полностью его перезаписывает: старое содержимое не сохраняется, "
            "даже если новый текст короче.\n\n"
            "Все функции возвращают `io::Result`, то есть `Result` с ошибкой типа `std::io::Error`. Оператор `?` "
            "пробрасывает ошибку вызывающему коду, поэтому `main` удобно объявить возвращающей `io::Result<()>`. "
            "Такой `main` завершает программу с ненулевым кодом и печатает ошибку, если она дошла до самого верха.\n\n"
            "Эти функции подходят, когда файл целиком помещается в память и обрабатывается за один проход. Для "
            "больших файлов ниже понадобятся потоки и буферизация."
        ),
        example(
            "rust",
            r"""
            use std::fs;
            use std::io;

            fn main() -> io::Result<()> {
                fs::write("note.txt", "первая строка\nвторая строка\n")?;

                let content = fs::read_to_string("note.txt")?;
                println!("всего байт: {}", content.len());

                fs::write("data.bin", [1u8, 2, 3, 4])?;
                let bytes = fs::read("data.bin")?;
                println!("двоичный файл: {:?}", bytes);

                fs::write("note.txt", "короткий текст")?;
                println!("после перезаписи: {:?}", fs::read_to_string("note.txt")?);

                Ok(())
            }
            """,
        ),
        text(
            "Вывод:\nвсего байт: 27\nдвоичный файл: [1, 2, 3, 4]\nпосле перезаписи: \"короткий текст\"\n\n"
            "Длина первого текста — 27 байт: по 13 байт на две строки с кириллицей, которая в UTF-8 занимает "
            "два байта на символ, плюс два перевода строки и пробел. Второй файл заметно короче, в нём всего "
            "13 кириллических символов и один пробел. Остатков прежнего содержимого не сохранилось: именно "
            "усечение при перезаписи чаще всего застаёт новичков врасплох."
        ),
        heading("Режимы открытия и `OpenOptions`"),
        text(
            "Когда нужно не просто записать строку, а управлять файлом по шагам, его открывают явно. "
            "`File::open` открывает файл только для чтения и требует, чтобы файл уже существовал. "
            "`File::create` создаёт файл и усекает его, если он был. Для промежуточных режимов служит "
            "`OpenOptions`: коллекция флагов `read`, `write`, `append`, `create`, `create_new`, `truncate`.\n\n"
            "Флаг `append` перемещает курсор в конец файла перед каждой записью, поэтому журнальные записи "
            "добавляются, а не затирают друг друга. Флаг `create_new` падает с ошибкой `AlreadyExists`, если "
            "файл существует, — это способ атомарно занять имя файла. Комбинация `truncate(true)` вместе с "
            "`write(true)` повторяет поведение `File::create`.\n\n"
            "Дескриптор `File` занимает системный ресурс и реализует трейты `Read` и `Write`, поэтому с ним "
            "работают те же методы, что и с файлом, открытым упрощённой функцией."
        ),
        example(
            "rust",
            r"""
            use std::fs::OpenOptions;
            use std::io::{self, Write};

            fn main() -> io::Result<()> {
                let path = "journal.log";
                let mut file = OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(path)?;
                for n in 1..=3 {
                    writeln!(file, "шаг {}", n)?;
                }

                let mut fresh = OpenOptions::new()
                    .write(true)
                    .create_new(true)
                    .open("once.txt");
                match fresh {
                    Ok(_) => println!("файл занят атомарно"),
                    Err(e) if e.kind() == io::ErrorKind::AlreadyExists => {
                        println!("файл уже существует");
                    }
                    Err(e) => return Err(e),
                }

                Ok(())
            }
            """,
        ),
        text(
            "Вывод:\nфайл занят атомарно\n\n"
            "При повторном запуске второй блок напечатает «файл уже существует». Метод `kind` возвращает "
            "перечисление `ErrorKind`, по которому различают отсутствие файла, отказ в доступе и занятость "
            "имени. Сравнивать полный текст ошибки нельзя: он зависит от операционной системы и языка окружения."
        ),
        callout(
            "warning",
            "`File::create` стирает содержимое",
            "`File::create` и `fs::write` усекают существующий файл до нуля байт. Если нужен журнал, куда "
            "дописывают данные, открывайте файл через `OpenOptions` с флагом `append(true)`."
        ),
        heading("Пути: `Path` и `PathBuf`"),
        text(
            "Путь в Rust — это тип, а не строка. `Path` ведёт себя как срез `str`, а `PathBuf` — как `String`: "
            "первый заимствуется, второй владеет и может изменяться. Такое разделение позволяет функциям "
            "принимать `&Path` и не копировать данные. Преобразование выполняется через `Path::new`, "
            "`PathBuf::from` и метод `as_path`.\n\n"
            "Путь разбирается методами, которые не зависят от платформы. `file_name` возвращает последний "
            "компонент, `file_stem` — имя без расширения, `extension` — расширение, `parent` — каталог. Все они "
            "возвращают `Option`, потому что путь `\"..\"` не имеет имени файла, а путь с несколькими расширениями "
            "неоднозначен по смыслу. На macOS и Linux разделитель — прямой слэш, на Windows учитываются и "
            "обратные, поэтому конкатенация строк вручную почти всегда ошибочна.\n\n"
            "Сборка пути выполняется методом `push`, который добавляет компонент с учётом разделителя, и "
            "оператором `join`, который возвращает новый `PathBuf` и не изменяет исходный. Метод `set_extension` "
            "заменяет расширение, не трогая имя файла."
        ),
        example(
            "rust",
            r"""
            use std::path::{Path, PathBuf};

            fn main() {
                let path = Path::new("/tmp/project/main.rs");

                println!("имя: {:?}", path.file_name());
                println!("стем: {:?}", path.file_stem());
                println!("расширение: {:?}", path.extension());
                println!("каталог: {:?}", path.parent());

                let mut buf = PathBuf::from("/tmp/project");
                buf.push("data");
                buf.push("report.rs");
                buf.set_extension("json");
                println!("собранный путь: {}", buf.display());

                let short = Path::new("/tmp/project/data").join("report.json");
                println!("через join: {}", short.display());
                println!("исходный путь не изменился: {}", buf.display());
            }
            """,
        ),
        text(
            "Вывод:\nимя: Some(\"main.rs\")\nстем: Some(\"main\")\nрасширение: Some(\"rs\")\n"
            "каталог: Some(\"/tmp/project\")\nсобранный путь: /tmp/project/data/report.json\n"
            "через join: /tmp/project/data/report.json\n"
            "исходный путь не изменился: /tmp/project/data/report.json\n\n"
            "Метод `display` печатает путь для человека; он может заменить непредставимые символы, поэтому для "
            "точного вывода в отладке используют `{:?}`. `canonicalize` убирает элементы `..` и `.` и разрешает "
            "символические ссылки, но требует существования пути и выполняется с обращением к файловой системе."
        ),
        heading("Трейты `Read`, `Write`, `Seek` и `BufRead`"),
        text(
            "Упрощённые функции `std::fs` читают файл целиком. Для потоков используются трейты из `std::io`, и "
            "код, написанный против трейта, одинаково работает с файлом, сетевым сокетом и буфером в памяти. "
            "Трейт `Read` предоставляет метод `read` для частичного чтения, `read_to_end` для чтения до конца и "
            "`read_exact`, который заполняет буфер полностью или возвращает ошибку `UnexpectedEof`.\n\n"
            "Трейт `Write` предоставляет метод `write` для частичной записи, а также `write_all`, который "
            "повторяет попытки, пока не запишет весь срез. Метод `flush` сбрасывает буфер в нижележащий поток. "
            "Трейт `Seek` позволяет перемещать курсор: `SeekFrom::Start`, `SeekFrom::End` и "
            "`SeekFrom::Current`, а `stream_position` возвращает текущую позицию.\n\n"
            "Трейт `BufRead` добавляет построчные методы. Реализация для `BufReader`, `Stdin` и срезов даёт "
            "`lines`, который отдаёт итератор `String` без символа перевода строки, и `read_line`, который "
            "дописывает строку вместе с `\\n` в существующий буфер. Именно `read_line` в цикле позволяет "
            "переиспользовать выделенную память."
        ),
        example(
            "rust",
            r"""
            use std::fs::File;
            use std::io::{self, Read, Seek, SeekFrom, Write};

            fn header(path: &str) -> io::Result<String> {
                let mut file = File::open(path)?;
                let mut buf = [0u8; 4];
                file.read_exact(&mut buf)?;
                Ok(String::from_utf8_lossy(&buf).to_string())
            }

            fn main() -> io::Result<()> {
                let mut out = File::create("seek.txt")?;
                out.write_all(b"RUST-SEEK")?;
                out.flush()?;

                println!("первые четыре байта: {}", header("seek.txt")?);

                let mut file = File::open("seek.txt")?;
                let pos = file.seek(SeekFrom::Start(5))?;
                println!("позиция после seek: {}", pos);

                let mut tail = String::new();
                file.read_to_string(&mut tail)?;
                println!("хвост: {}", tail);

                file.seek(SeekFrom::End(-4))?;
                let mut last = String::new();
                file.read_to_string(&mut last)?;
                println!("последние четыре символа: {}", last);
                Ok(())
            }
            """,
        ),
        text(
            "Вывод:\nпервые четыре байта: RUST\nпозиция после seek: 5\nхвост: SEEK\n"
            "последние четыре символа: SEEK\n\n"
            "В этом примере все символы однобайтовые в UTF-8, поэтому позиция в байтах совпадает с позицией в "
            "символах. С кириллицей `SeekFrom::Start(5)` попадёт внутрь символа, и `read_to_string` вернёт ошибку "
            "`InvalidData`. Смещения в потоке всегда считаются в байтах."
        ),
        heading("Буферизация и построчное чтение"),
        text(
            "Каждый вызов `read` и `write` у файла — это системный вызов. Если писать журнал по строке, "
            "программа сделает тысячи переключений в ядро. `BufReader` и `BufWriter` накапливают данные в "
            "памяти и обращаются к файлу блоками по несколько килобайт. Разница заметна уже на тексте в "
            "несколько мегабайт, а на сетевых потоках буферизация обязательна.\n\n"
            "Работа с `BufWriter` требует дисциплины. Данные остаются в буфере, пока он не заполнится или пока "
            "не вызван `flush`. При выходе из области видимости `BufWriter` пытается сбросить буфер в `Drop`, но "
            "ошибку записи в этот момент вернуть некому, поэтому в короткоживущей программе последние строки "
            "могут потеряться молча.\n\n"
            "`BufReader` даёт метод `lines`, который возвращает итератор элементов `io::Result<String>`. Ошибка "
            "возникает не на итераторе, а на конкретном элементе, поэтому `collect::<io::Result<Vec<_>>>()` "
            "превращает последовательность результатов в результат со списком и останавливается на первой ошибке."
        ),
        example(
            "rust",
            r"""
            use std::fs::File;
            use std::io::{self, BufRead, BufReader, BufWriter, Write};

            fn main() -> io::Result<()> {
                {
                    let file = File::create("lines.txt")?;
                    let mut writer = BufWriter::new(file);
                    for n in 1..=4 {
                        writeln!(writer, "запись {}", n)?;
                    }
                    writer.flush()?;
                }

                let file = File::open("lines.txt")?;
                let reader = BufReader::new(file);
                let all: io::Result<Vec<String>> = reader.lines().collect();
                let all = all?;
                println!("прочитано строк: {}", all.len());
                for (i, line) in all.iter().enumerate() {
                    println!("{}: {}", i + 1, line);
                }
                Ok(())
            }
            """,
        ),
        text(
            "Вывод:\nпрочитано строк: 4\n1: запись 1\n2: запись 2\n3: запись 3\n4: запись 4\n\n"
            "Вложенный блок вокруг записи нужен не для логики, а чтобы `writer` вышел из области видимости "
            "до открытия файла на чтение. Если убрать `flush` и читать до закрытия писателя, часть строк "
            "останется в буфере, и чтение увидит только сброшенные данные."
        ),
        callout(
            "info",
            "Когда буфер не нужен",
            "Для файла в несколько сотен байт лишний слой замедляет код незаметно для человека, но усложняет "
            "чтение. Буферизацию включают, когда операций много или размер данных заранее неизвестен."
        ),
        heading("Каталоги, обход и метаданные"),
        text(
            "Каталоги создаются функциями `fs::create_dir` и `fs::create_dir_all`. Вторая создаёт всю цепочку "
            "родительских каталогов и не падает, если последний уже есть. `fs::metadata` возвращает структуру "
            "`Metadata` с размером `len`, признаками `is_file` и `is_dir`, правами доступа и временем изменения "
            "в виде `SystemTime`.\n\n"
            "Чтение каталога выполняется через итератор `fs::read_dir`. Каждый его элемент — `io::Result<DirEntry>`, "
            "потому что ошибка может возникнуть на любом шаге обхода, например при обрыве сетевого диска. У "
            "`DirEntry` есть методы `path`, `file_name` и `metadata`, причём `metadata` у записи каталога часто "
            "дешевле вызывать методом самой записи, а не по пути.\n\n"
            "Удаление различается по области действия: `remove_file` удаляет файл, `remove_dir` — только пустой "
            "каталог, `remove_dir_all` удаляет каталог с содержимым. Перемещение `fs::rename` в пределах одной "
            "файловой системы атомарно, что позволяет безопасно заменять файл конфигурации целиком."
        ),
        example(
            "rust",
            r"""
            use std::fs;
            use std::io;
            use std::path::Path;

            fn total_size(dir: &Path) -> io::Result<u64> {
                let mut sum = 0;
                for entry in fs::read_dir(dir)? {
                    let meta = entry?.metadata()?;
                    if meta.is_file() {
                        sum += meta.len();
                    }
                }
                Ok(sum)
            }

            fn main() -> io::Result<()> {
                fs::create_dir_all("store/data")?;
                fs::write("store/data/a.txt", "12345")?;
                fs::write("store/data/b.txt", "123")?;

                let meta = fs::metadata("store/data/a.txt")?;
                println!("файл: {}, размер: {}", meta.is_file(), meta.len());
                println!("суммарный размер: {}", total_size(Path::new("store/data"))?);

                fs::rename("store/data/b.txt", "store/data/c.txt")?;
                println!("после переименования: {}", total_size(Path::new("store/data"))?);

                fs::remove_dir_all("store")?;
                println!("каталог существует: {}", Path::new("store").exists());
                Ok(())
            }
            """,
        ),
        text(
            "Вывод:\nфайл: true, размер: 5\nсуммарный размер: 8\nпосле переименования: 8\n"
            "каталог существует: false\n\n"
            "Переименование не меняет размер, поэтому сумма остаётся прежней. Метод `exists` возвращает "
            "`false` и при отсутствии файла, и при ошибке прав доступа, поэтому в проверках, где важно "
            "различие, лучше вызывать `fs::metadata` и разбирать ошибку."
        ),
        heading("Сериализация с `serde`: структуры и атрибуты"),
        text(
            "Сериализация — это превращение значения в последовательность байт для хранения или передачи, "
            "десериализация — обратное действие. В Rust эти задачи решает крейт `serde`, а конкретный формат "
            "подключается отдельным крейтом: `serde_json` для JSON, `toml` для TOML, `serde_yaml` для YAML. "
            "Крейт `serde` описывает общий набор трейтов, поэтому одна структура работает со всеми форматами "
            "сразу.\n\n"
            "Подключать признаки руками не нужно: макрос `#[derive(Serialize, Deserialize)]` генерирует "
            "реализации на этапе компиляции. Трейт `Serialize` нужен для записи, `Deserialize` — для чтения; "
            "если данные только передаются на сервер, достаточно первого. Для отладки к структуре добавляют "
            "`Debug`, а для сравнения в тестах — `PartialEq`.\n\n"
            "Атрибуты `serde` управляют форматом отдельных полей. `rename` меняет имя в документе и полезен для "
            "совместимости с внешним API. `default` подставляет значение по умолчанию, если поля нет в входных "
            "данных. `skip_serializing_if` не пишет поле, когда оно пустое, а `skip` исключает поле в обе "
            "стороны. `flatten` встраивает вложенную структуру в текущий объект без дополнительного уровня."
        ),
        example(
            "rust",
            r"""
            use serde::{Deserialize, Serialize};

            #[derive(Debug, Serialize, Deserialize, PartialEq)]
            struct Task {
                id: u64,
                title: String,
                #[serde(rename = "isDone", default)]
                done: bool,
                #[serde(skip_serializing_if = "Option::is_none")]
                assignee: Option<String>,
                #[serde(default = "default_priority")]
                priority: u8,
            }

            fn default_priority() -> u8 {
                3
            }

            fn main() {
                let json = r#"{"id": 7, "title": "собрать отчёт"}"#;
                let task: Task = serde_json::from_str(json).expect("корректный JSON");
                println!("{:?}", task);
                println!("готово: {}, приоритет: {}", task.done, task.priority);

                let out = serde_json::to_string(&task).unwrap();
                println!("{}", out);
                println!("содержит assignee: {}", out.contains("assignee"));
            }
            """,
        ),
        text(
            "Вывод:\nTask { id: 7, title: \"собрать отчёт\", done: false, assignee: None, priority: 3 }\n"
            "готово: false, приоритет: 3\n"
            "{\"id\":7,\"title\":\"собрать отчёт\",\"done\":false,\"priority\":3}\n"
            "содержит assignee: false\n\n"
            "Во входном документе не было ни `isDone`, ни `priority`, и оба поля получили значения по умолчанию. "
            "Поле `assignee` отсутствует в выводе, потому что равно `None`. При обратном разборе атрибут "
            "`default` восстановит `assignee: None` без дополнительной настройки: у `Option` значение по "
            "умолчанию задано заранее."
        ),
        callout(
            "warning",
            "Пропущенное поле — ошибка",
            "Без `default` и без `Option` отсутствующее поле в JSON даёт ошибку `missing field`. Это защита от "
            "опечаток в имени поля, но при работе с чужим API добавляйте атрибут осознанно: строгость помогает "
            "найти расхождение в контракте."
        ),
        heading("Форматы: JSON и TOML"),
        text(
            "JSON принимает любое значение и хорошо подходит для обмена по сети: его понимает почти любой язык и "
            "любой HTTP-инструмент. Формат не поддерживает комментарии, не различает целые и дробные числа без "
            "контекста типа и не содержит дат как отдельного типа. Функции `serde_json::to_string`, "
            "`to_string_pretty`, `to_vec` и `from_str`, `from_slice` покрывают все основные случаи.\n\n"
            "TOML создан для конфигурации: в нём есть комментарии, таблицы и явные строки, а числа не теряют "
            "целочисленность. Крейт `toml` требует, чтобы корнем документа была таблица, поэтому "
            "сериализация строки или числа напрямую возвращает ошибку, а структура с полями работает. YAML "
            "занимает промежуточное место и удобен для сложных вложенных документов, но чувствителен к отступам "
            "и типам.\n\n"
            "Выбор формата определяется читателем. Файл настроек, который правит человек, лучше хранить в TOML. "
            "Данные, которые уходят в сервис или принимаются от него, почти всегда JSON. Компактные двоичные "
            "форматы вроде CBOR подключаются теми же derive-макросами, если размер и скорость важнее читаемости."
        ),
        example(
            "rust",
            r"""
            use serde::{Deserialize, Serialize};

            #[derive(Debug, Serialize, Deserialize)]
            struct Server {
                host: String,
                port: u16,
            }

            #[derive(Debug, Serialize, Deserialize)]
            struct Config {
                retries: u8,
                server: Server,
            }

            fn main() {
                let config = Config {
                    retries: 2,
                    server: Server { host: "127.0.0.1".into(), port: 8080 },
                };

                let toml_text = toml::to_string(&config).expect("таблица");
                println!("{}", toml_text.trim());
                println!("---");

                let json_text = serde_json::to_string(&config).unwrap();
                println!("{}", json_text);

                let back: Config = toml::from_str(&toml_text).expect("обратный разбор");
                println!("порт: {}, попыток: {}", back.server.port, back.retries);
            }
            """,
        ),
        text(
            "Вывод:\n[server]\nhost = \"127.0.0.1\"\nport = 8080\nretries = 2\n---\n"
            "{\"server\":{\"host\":\"127.0.0.1\",\"port\":8080},\"retries\":2}\nпорт: 8080, попыток: 2\n\n"
            "Поле `retries` оказалось внутри таблицы `[server]`: TOML требует, чтобы все простые значения шли "
            "до следующей таблицы. Если нужно вынести его на верхний уровень, объявите `retries` в структуре "
            "`Config` перед `server` или задайте атрибут `#[serde(rename = \"retries\")]` вместе с изменением "
            "порядка полей. При чтении порядок не важен, значение зависит только от места в тексте документа."
        ),
        heading("HTTP-запросы и разбор ответа"),
        text(
            "Для сетевых запросов в экосистеме принят крейт `reqwest`. Блокирующий клиент живёт в модуле "
            "`reqwest::blocking` и подходит для утилит командной строки, скриптов и тестов. Асинхронный клиент "
            "работает под управлением `tokio` и нужен в сервисах, которые обслуживают много соединений "
            "одновременно. Оба варианта собираются через `Client`, который переиспользует пул соединений, "
            "поэтому создавать его нужно один раз на программу, а не перед каждым запросом.\n\n"
            "Запрос строится цепочкой: метод, заголовки, тело, таймаут. Метод `send` возвращает `Result` и "
            "сообщает только о транспортных проблемах — обрыве соединения, ошибке DNS, истечении таймаута. "
            "Ответ сервера с кодом 404 или 500 приходит как успешный `Result`, и статус проверяется отдельно "
            "методами `status`, `is_success` или `error_for_status`. Метод `json::<T>()` разбирает тело по "
            "правилам `serde`, а `text()` возвращает строку.\n\n"
            "Для блокирующего клиента внутри потоковой функции используйте `Client`, созданный заранее, и "
            "задавайте таймаут явно. Без таймаута запрос может висеть бесконечно, и приложение не завершится, "
            "даже если пользователь уже закрыл окно."
        ),
        example(
            "rust",
            r"""
            use reqwest::blocking::Client;
            use serde::Deserialize;
            use std::time::Duration;

            #[derive(Debug, Deserialize)]
            struct Repo {
                name: String,
                stars: u64,
                #[serde(default)]
                description: Option<String>,
            }

            fn parse_repo(raw: &str) -> serde_json::Result<Repo> {
                serde_json::from_str(raw)
            }

            fn describe(repo: &Repo) -> String {
                let text = repo.description.as_deref().unwrap_or("без описания");
                format!("{} ({} звёзд): {}", repo.name, repo.stars, text)
            }

            fn main() -> Result<(), Box<dyn std::error::Error>> {
                let client = Client::builder()
                    .timeout(Duration::from_secs(10))
                    .user_agent("kernify-lesson/1.0")
                    .build()?;

                let response = client
                    .get("https://api.example.com/repos/serde")
                    .send()?;
                if !response.status().is_success() {
                    println!("сервер ответил: {}", response.status());
                    return Ok(());
                }
                let repo: Repo = response.json()?;
                println!("{}", describe(&repo));
                Ok(())
            }
            """,
        ),
        text(
            "Вывод для успешного ответа:\nserde (1234 звёзд): среда сериализации\n\n"
            "Программа собирается командой `cargo build`, для неё нужны зависимости `reqwest` с функциями "
            "`blocking` и `json`, `serde` с `derive` и `serde_json`. Блок с разбором `parse_repo` и функция "
            "`describe` тестируются без сети: достаточно передать строку JSON. Такое разделение сетевого "
            "вызова и разбора позволяет проверять основную логику в обычных тестах."
        ),
        heading("Асинхронный вариант и обработка ошибок"),
        text(
            "Асинхронный клиент отличается только точками `await` и запуском в рантайме `tokio`. Атрибут "
            "`#[tokio::main]` превращает асинхронную функцию `main` в синхронную, которая запускает рантайм. "
            "Для нескольких независимых запросов применяют `futures::future::join_all` или "
            "`tokio::join!`, чтобы запросы выполнялись одновременно, а не по очереди.\n\n"
            "Ошибки в `reqwest::Error` различаются методами `is_timeout`, `is_connect`, `is_status`, "
            "`is_body` и `is_decode`. Ошибка с `is_status` появляется только после `error_for_status`; без "
            "него неуспешный статус остаётся в ответе. Разделение помогает выбрать поведение: для таймаута "
            "разумна повторная попытка, для ошибки разбора — сообщение о несовместимом формате.\n\n"
            "Для агрегирования ошибок из разных слоёв удобен `Box<dyn std::error::Error>` в возвращаемом типе "
            "или перечисление с вариантами и реализацией `From`. Второй подход точнее: вызывающий код может "
            "сравнить варианты и решить, что делать, а не разбирать текст сообщения."
        ),
        example(
            "rust",
            r"""
            use reqwest::Client;
            use std::time::Duration;

            async fn fetch_all(urls: &[&str]) -> Vec<Result<String, String>> {
                let client = Client::builder()
                    .timeout(Duration::from_secs(5))
                    .build()
                    .expect("клиент создаётся");

                let requests = urls.iter().map(|url| async {
                    match client.get(*url).send().await {
                        Ok(resp) if resp.status().is_success() => {
                            resp.text().await.map_err(|e| e.to_string())
                        }
                        Ok(resp) => Err(format!("статус {}", resp.status())),
                        Err(e) if e.is_timeout() => Err("таймаут".to_string()),
                        Err(e) => Err(e.to_string()),
                    }
                });

                futures::future::join_all(requests).await
            }

            #[tokio::main]
            async fn main() {
                let urls = [
                    "https://api.example.com/health",
                    "https://api.example.com/version",
                ];
                for outcome in fetch_all(&urls).await {
                    match outcome {
                        Ok(body) => println!("ответ: {} байт", body.len()),
                        Err(reason) => println!("ошибка: {}", reason),
                    }
                }
            }
            """,
        ),
        text(
            "Вывод при доступных двух адресах:\nответ: 14 байт\nответ: 9 байт\n\n"
            "Если первый адрес не отвечает, вместо первой строки появится «ошибка: таймаут», а второй запрос "
            "всё равно выполнится, потому что `join_all` дожидается всех переданных фьючерсов. Фьючерсы "
            "запускаются на том же рантайме, поэтому блокирующий ввод-вывод в асинхронном коде нельзя "
            "исполнять напрямую."
        ),
        callout(
            "danger",
            "Блокирующий вызов в асинхронной функции",
            "`std::fs` и `reqwest::blocking` внутри `async fn` останавливают весь поток рантайма и мешают "
            "остальным задачам. Используйте `tokio::fs` или выносите работу в `tokio::task::spawn_blocking`."
        ),
        heading("Сквозной пример: данные из файла и из сети"),
        text(
            "В реальной программе источник данных и доменная модель редко совпадают один к одному. Внешний API "
            "присылает поля в camelCase, часть полей необязательна, а локальный кеш хранит те же данные в "
            "другом формате. Чтобы код оставался управляемым, слой разбора отделяют от слоя сети и от бизнес-логики.\n\n"
            "Ниже задача решается в три шага. Функция `read_cache` читает локальный JSON и превращает ошибку "
            "чтения файла в `None`, если файла нет. Функция `parse_tasks` разбирает строку и оставляет в "
            "списке только незавершённые задачи. Функция `report` объединяет оба источника и возвращает "
            "строку отчёта, не зная, откуда пришли данные.\n\n"
            "Такая структура делает каждый шаг проверяемым без сети и файловой системы: `parse_tasks` "
            "принимает `&str`, поэтому её легко покрыть тестами с подготовленными строками."
        ),
        example(
            "rust",
            r"""
            use serde::Deserialize;
            use std::fs;
            use std::path::Path;

            #[derive(Debug, Deserialize, PartialEq)]
            struct Task {
                id: u64,
                #[serde(rename = "isDone", default)]
                done: bool,
                #[serde(default)]
                tags: Vec<String>,
            }

            fn read_cache(path: &Path) -> Option<String> {
                match fs::read_to_string(path) {
                    Ok(text) => Some(text),
                    Err(e) => {
                        eprintln!("кеш недоступен: {}", e.kind());
                        None
                    }
                }
            }

            fn parse_tasks(raw: &str) -> serde_json::Result<Vec<Task>> {
                let tasks: Vec<Task> = serde_json::from_str(raw)?;
                Ok(tasks.into_iter().filter(|t| !t.done).collect())
            }

            fn report(raw: Option<&str>) -> String {
                match raw.and_then(|text| parse_tasks(text).ok()) {
                    Some(tasks) => {
                        let ids: Vec<String> = tasks.iter().map(|t| t.id.to_string()).collect();
                        format!("ожидают {} задач: {}", tasks.len(), ids.join(", "))
                    }
                    None => "данных нет".to_string(),
                }
            }

            fn main() -> std::io::Result<()> {
                let path = Path::new("tasks.json");
                fs::write(
                    path,
                    r#"[{"id": 1, "tags": ["api"]}, {"id": 2, "isDone": true}]"#,
                )?;

                let raw = read_cache(path);
                println!("{}", report(raw.as_deref()));
                println!("{}", report(Some("не json")));
                Ok(())
            }
            """,
        ),
        text(
            "Вывод:\nожидают 1 задач: 1\nданных нет\n\n"
            "Вторая задача отфильтрована из-за `isDone: true`, а строки «не json» не прошли разбор и дали "
            "`None`. Функция `read_cache` печатает причину недоступности кеша, но не прерывает программу: "
            "отсутствие кеша — ожидаемая ситуация, а не сбой. Такое правило стоит закреплять в сигнатуре типа, "
            "и `Option` подходит для него лучше, чем `Result` с искусственной ошибкой."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                [
                    "`fs::write` вместо `OpenOptions::append` для журнала",
                    "Прежние записи стираются при каждом запуске",
                    "Открывать через `OpenOptions::new().create(true).append(true)`",
                ],
                [
                    "Забыть `flush` у `BufWriter`",
                    "Последние строки остаются в буфере и теряются",
                    "Вызывать `writer.flush()?` перед проверкой файла или выходом из области видимости",
                ],
                [
                    "Склеивать путь через `format!(\"{}/{}\")`",
                    "На Windows получается неверный разделитель, двойные слэши ломают сравнение",
                    "Использовать `Path::new(base).join(name)`",
                ],
                [
                    "Сериализовать строку в TOML",
                    "Крейт `toml` требует на верхнем уровне таблицу и возвращает ошибку",
                    "Оборачивать значение в структуру с именованным полем",
                ],
                [
                    "`serde_json::from_str` на поле, которого может не быть",
                    "Ошибка `missing field`, программа падает на первом же ответе",
                    "Добавить `#[serde(default)]` или хранить поле как `Option<T>`",
                ],
                [
                    "`unwrap` на `response.json()`",
                    "Паника на любом изменении контракта API или при 500",
                    "Проверять `status().is_success()` и возвращать `Result` вызывающему коду",
                ],
                [
                    "`std::fs` внутри `async fn`",
                    "Блокируется поток рантайма, остальные задачи ждут",
                    "Брать `tokio::fs` или выносить работу в `spawn_blocking`",
                ],
                [
                    "Смещение `Seek` в байтах при работе с текстом",
                    "Позиция попадает внутрь символа UTF-8, чтение возвращает `InvalidData`",
                    "Читать по строкам через `BufRead` или считать смещения в байтах осознанно",
                ],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняются в новом проекте: `cargo new io_practice`, затем `cd io_practice`. Добавьте "
            "зависимости вручную в `Cargo.toml` (например, `cargo add serde --features derive`), "
            "собирайте и запускайте через `cargo run`, проверяйте логику через `cargo test`."
        ),
        numbered(
            "Файлы: напишите функцию `copy_with_numbering(src, dst)`, которая копирует текстовый файл построчно и добавляет в начало каждой строки её номер в формате `1: текст`.",
            "Пути: для заданного пути выведите имя файла, расширение и родительский каталог, а затем постройте путь к файлу с расширением `toml` рядом с исходным.",
            "IO: прочитайте двоичный файл длиной не меньше 16 байт, извлеките первые 4 байта и последние 4 байта через `File` и `Seek`, и выведите их в шестнадцатеричном виде.",
            "Serde: опишите структуру `Note` с полями `id`, `text`, `pinned` и сериализуйте список заметок в JSON и TOML, затем разберите оба результата и сравните списки.",
            "Сеть: напишите функцию `fetch_json(url)`, которая выполняет GET-запрос, проверяет статус, разбирает тело в свой тип и возвращает `Result` с собственным перечислением ошибок (таймаут, статус, разбор).",
        ),
        callout(
            "info",
            "Задание 3",
            "После `seek(SeekFrom::End(-4))` используйте `read_exact` с массивом `[0u8; 4]`. Метод `read_to_string` "
            "на двоичных данных вернёт ошибку `InvalidData`, поэтому работайте с байтами и форматируйте их через `{:02x}`.",
        ),
        heading("Проверьте себя"),
        text(
            "Отвечайте своими словами, затем сверьтесь с разделом ответов. Вопросы проверяют не названия "
            "функций, а понимание того, почему выбранная функция подходит для конкретной задачи."
        ),
        numbered(
            "Чем `fs::read_to_string` отличается от `fs::read` и когда каждый вариант обязателен?",
            "Почему `File::create` опасен для файла журнала и какой флаг `OpenOptions` решает проблему?",
            "Зачем нужен `BufWriter` и что произойдёт, если не вызвать `flush` перед проверкой файла?",
            "Чем `Path` отличается от `PathBuf` и почему путь не хранят просто в `String`?",
            "Что делает атрибут `#[serde(default)]` и как он связан с полем типа `Option<T>`?",
            "Почему ответ с кодом 404 не является ошибкой `reqwest::Error` и как это проверить в коде?",
            "Какую проблему создаёт вызов `std::fs` внутри асинхронной функции и как её избежать?",
        ),
        heading("Ответы", 3),
        numbered(
            "`read_to_string` возвращает `String` и проверяет UTF-8, поэтому подходит для текста. `read` возвращает `Vec<u8>` и обязателен для двоичных данных, где проверка UTF-8 дала бы ошибку `InvalidData`.",
            "`File::create` усекает файл до нуля байт и стирает журнал. Нужен `OpenOptions` с флагом `append(true)`, а если файл может отсутствовать — ещё и `create(true)`.",
            "`BufWriter` накапливает записи в памяти и сокращает число системных вызовов. Без `flush` данные остаются в буфере, и чтение файла с диска увидит пустой или неполный результат.",
            "`Path` — заимствованный срез пути, `PathBuf` — владеющий и изменяемый. Строка не учитывает правила платформы: разделители, корень диска и нормализацию, поэтому сборку путей выполняют методами типа.",
            "Атрибут подставляет `Default::default()` для отсутствующего поля. У `Option<T>` значение по умолчанию — `None`, поэтому для необязательного поля атрибут не нужен, хотя явно указать его не вредно.",
            "`send` возвращает ошибку только при транспортном сбое; статус HTTP — часть успешного ответа. Проверяют через `status().is_success()` или вызовом `error_for_status()`, который преобразует неуспешный статус в ошибку.",
            "Синхронный ввод-вывод блокирует поток рантайма и задерживает другие задачи. Решение — `tokio::fs` для файлов или `tokio::task::spawn_blocking` для произвольного блокирующего кода.",
        ),
        *outro(
            (
                "`std::fs` покрывает простые случаи: `read_to_string` для текста, `read` для байтов, `write` для полной перезаписи.",
                "`OpenOptions` задаёт режим открытия; для журнала нужны `create(true)` и `append(true)`, а `create_new` атомарно занимает имя.",
                "`Path` и `PathBuf` разбирают и собирают пути по правилам платформы; `join`, `push` и `set_extension` заменяют склейку строк.",
                "Трейты `Read`, `Write`, `Seek` и `BufRead` делают код независимым от источника данных; `BufReader` и `BufWriter` ускоряют обмен.",
                "`serde` с derive-макросами даёт сериализацию в JSON и TOML, а атрибуты `rename`, `default` и `skip_serializing_if` управляют форматом полей.",
                "HTTP-вызов возвращает `Result` только за транспорт, статус проверяют отдельно, а разбор тела делегируется `serde`.",
                "Сетевой слой, разбор формата и доменную логику разделяют по функциям, чтобы каждую часть можно было проверить в тестах.",
                "Ошибки представляют перечислением или `Box<dyn Error>`, а `unwrap` оставляют только там, где сбой невозможен по построению.",
            ),
            "Вы научились получать данные из файлов и по сети и превращать их в типы Rust через `serde`. "
            "Следующий урок посвящён планировщику задач и приёмам повышения производительности: профилированию, "
            "измерениям и работе с аллокациями, которые отделяют реальные узкие места от догадок.",
            (
                "The Rust Programming Language, глава 12 о вводе-выводе — doc.rust-lang.org/book/ch12-00-an-io-project.html",
                "Документация `std::fs` — doc.rust-lang.org/std/fs/",
                "Документация `std::io` и список трейтов — doc.rust-lang.org/std/io/",
                "Документация `std::path` — doc.rust-lang.org/std/path/",
                "Официальный сайт `serde` с руководством по атрибутам — serde.rs",
                "Документация крейта `reqwest` — docs.rs/reqwest",
                "Руководство `tokio` по асинхронному вводу-выводу — tokio.rs",
            ),
        ),
    ],
}
