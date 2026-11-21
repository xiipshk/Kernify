"""Урок 3.8 курса Rust: системное программирование."""

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
    "topic_order": 8,
    "name": "3.8. Системное программирование",
    "slug": "rust-3-8-системное-программирование",
    "short_description": (
        "Раскладка структур в памяти через repr-атрибуты, FFI с C и C++, системные вызовы, "
        "no_std и embedded, SIMD-интринсики, сырые указатели, mmap и безопасные обёртки над unsafe."
    ),
    "topic_name": "Системное программирование",
    "topic_description": (
        "Системное программирование на Rust: двоичная раскладка данных и атрибуты repr, "
        "границы FFI и их ловушки, системные вызовы в libc и nix, драйверы в no_std, "
        "SIMD и сырые указатели, отображение файлов в память и безопасные обёртки над unsafe."
    ),
    "learning_objectives": [
        "Описывать раскладку структур атрибутами repr(C), repr(transparent), repr(packed) и repr(align)",
        "Строить границы FFI через extern \"C\", cbindgen и cxx, передавать строки и владение без утечек",
        "Вызывать системные вызовы через libc и nix и понимать цену сгенерированных обёрток",
        "Писать код для no_std с обработчиком паники и доступом к регистрам через read_volatile",
        "Использовать SIMD-интринсики с проверкой is_x86_feature_detected и скалярным резервом",
        "Работать с сырыми указателями: NonNull, addr_of!, радикс-ARITHMETIC и корректные границы",
        "Отображать файлы в память через mmap и memmap2, освобождая ресурсы в Drop",
        "Проектировать безопасные обёртки над unsafe-кодом с проверенными инвариантами и Pin",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "rust",
        "ffi",
        "unsafe",
        "no_std",
        "simd",
        "mmap",
    ],
    "starter_code": code(
        r"""
        use std::os::raw::c_int;

        /// Считаем сумму байтов среза без выхода за его границы.
        fn checked_read(bytes: &[u8], index: usize) -> Option<u8> {
            bytes.get(index).copied()
        }

        /// Разбор целого числа из C-буфера фиксированного размера.
        fn parse_c_int(buf: &[u8; 4]) -> c_int {
            c_int::from_le_bytes(*buf)
        }

        fn main() {
            let data = [10u8, 20, 30];
            println!("data[1] = {:?}", checked_read(&data, 1));
            println!("data[5] = {:?}", checked_read(&data, 5));
            println!("value   = {}", parse_c_int(&[42, 0, 0, 0]));
        }
        """
    ),
    "hints": [
        "Атрибут repr влияет только на раскладку и ABI: он не делает доступ к полям безопасным. Для packed-структур берите адрес через addr_of! и читайте через read_unaligned.",
        "Внешняя функция, которая может упасть, должна быть объявлена как extern \"C-unwind\", иначе паника, дошедшая до границы, обрывает процесс.",
        "В no_std нельзя обращаться к периферии как к обычной памяти: компилятор вправе убрать «лишние» чтения и записи. Используйте read_volatile и write_volatile.",
        "Любая безопасная обёртка над unsafe должна проверять предусловия обычными средствами языка до входа в unsafe-блок, а не полагаться на вызывающего.",
    ],
    "content": [
        text(
            "Системное программирование — это работа ближе к операционной системе и железу: "
            "взаимодействие с библиотеками на C, прямые системные вызовы, драйверы без "
            "операционной системы, векторные инструкции процессора, управление виртуальной памятью. "
            "Rust создавался с расчётом на эту нишу, поэтому в языке есть и возможность писать "
            "низкоуровневый код, и механизмы, позволяющие держать такой код в узком проверяемом месте."
        ),
        text(
            "Ключевая идея — «unsafe как маленький остров внутри безопасной программы». "
            "Компилятор не проверит ABI, выравнивание или инварианты драйвера, "
            "но проверит, что остальной код пользуется абстракциями, которые эти инварианты соблюдают."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "описывать раскладку структур атрибутами repr(C), repr(transparent), repr(packed), repr(align);",
            "строить границы FFI через extern \"C\", экспортировать функции через #[no_mangle], генерировать привязки через bindgen и cbindgen, подключать C++ через cxx;",
            "вызывать системные вызовы напрямую через libc и nix;",
            "писать код для no_std и встраиваемых платформ с обработчиком паники, аллокатором и доступом к регистрам периферии;",
            "использовать SIMD-интринсики из core::arch с проверкой поддержки процессором и скалярным резервом;",
            "работать с сырыми указателями: NonNull, addr_of!, add, offset_from, wrapping_add;",
            "отображать файлы в память через mmap и memmap2, освобождать ресурсы в Drop;",
            "проектировать безопасные обёртки над unsafe-кодом и применять Pin для самореференциальных структур.",
        ),
        heading("Раскладка данных в памяти"),
        text(
            "По умолчанию Rust не даёт гарантий о порядке полей: компилятор вправе переставлять "
            "их для упаковки. Для обычного кода это преимущество, но на границе с C и при чтении "
            "бинарного формата нужна предсказуемая раскладка, и её задают атрибуты repr.\n\n"
            "«Выравнивание» — требование к адресу: объект u32 должен начинаться по адресу, кратному "
            "четырём. Чтобы его выполнить, между полями вставляются байты-заполнители, поэтому "
            "структура ниже занимает 12 байт при сумме полей 7."
        ),
        example(
            "rust",
            r"""
            use std::mem::{align_of, offset_of, size_of};

            #[repr(C)]
            struct CCompatible {
                a: u8,
                b: u32,
                c: u16,
            }

            fn main() {
                println!("size   = {}", size_of::<CCompatible>());
                println!("align  = {}", align_of::<CCompatible>());
                println!("b      = {}", offset_of!(CCompatible, b));
                println!("c      = {}", offset_of!(CCompatible, c));
            }
            """,
        ),
        text(
            "Вывод: size = 12, align = 4, поле b по смещению 4, поле c по смещению 8. "
            "Три байта заполнителя после a и два байта в конце добавлены, чтобы массив таких "
            "структур оставался выровненным."
        ),
        table(
            ["Атрибут", "Что гарантирует", "Типичное применение"],
            [
                ["repr(C)", "порядок полей как в объявлении, C-правила заполнения", "структуры для FFI, заголовки файлов"],
                ["repr(transparent)", "раскладка совпадает с единственным непустым полем", "обёртки-новотипы для ABI"],
                ["repr(packed)", "нет заполнителей, align = 1", "сетевые и аппаратные форматы"],
                ["repr(align(N))", "выравнивание не меньше N байт", "борьба с ложным разделением кэш-линий"],
                ["repr(u8)", "enum занимает ровно байт с заданными значениями", "коды ошибок и статусы для C"],
                ["repr(usize)", "дискриминант размером с указатель", "компактные перечисления с нишей"],
            ],
        ),
        text(
            "Отдельного внимания заслуживает repr(transparent). Новотип struct Metres(f64) с этим "
            "атрибутом имеет ту же раскладку и ABI, что и f64, поэтому его можно передавать "
            "в C вместо голого числа, не теряя типобезопасности. Условие: ровно одно поле имеет "
            "ненулевой размер, остальные обязаны быть пустыми типами с выравниванием 1."
        ),
        example(
            "rust",
            r"""
            #[repr(transparent)]
            struct Metres(f64);

            #[repr(C)]
            struct Frame {
                width: Metres,
                height: Metres,
            }

            extern "C" {
                fn c_draw_area(w: f64, h: f64) -> f64;
            }

            fn draw(frame: &Frame) {
                let area = unsafe { c_draw_area(frame.width.0, frame.height.0) };
                println!("area = {:.2}", area);
            }

            fn main() {
                let frame = Frame { width: Metres(1.5), height: Metres(2.0) };
                draw(&frame);
            }
            """,
        ),
        text(
            "Вывод: area = 3.00 (если библиотека c_draw_area слинкована). В функцию передаются "
            "именно f64: накладных расходов у обёрток нет, на границе они превращаются в примитивы."
        ),
        heading("Упакованные структуры и невыровненный доступ", 3),
        text(
            "repr(packed) убирает заполнители, но ссылка на поле такой структуры может оказаться "
            "невыровненной, а создание невыровненной ссылки в Rust — неопределённое поведение. "
            "Поэтому брать &packed.b нельзя ни в безопасном, ни в unsafe-коде.\n\n"
            "Правильный путь — получить сырой указатель макросом addr_of! (он не создаёт "
            "промежуточной ссылки) и прочитать значение через std::ptr::read_unaligned. "
            "Для записи есть write_unaligned."
        ),
        example(
            "rust",
            r"""
            use std::mem::size_of;
            use std::ptr::{addr_of, read_unaligned};

            #[repr(packed)]
            struct Packed {
                a: u8,
                b: u32,
                c: u16,
            }

            fn main() {
                let p = Packed { a: 1, b: 0xDEAD_BEEF, c: 7 };

                // let bad = &p.b;                 // ошибка компиляции: невыровненная ссылка
                let value = unsafe { read_unaligned(addr_of!(p.b)) };
                let flag = unsafe { read_unaligned(addr_of!(p.a)) };

                println!("size  = {}", size_of::<Packed>());
                println!("b     = {:#X}", value);
                println!("a     = {}", flag);
            }
            """,
        ),
        text(
            "Вывод: size = 7, b = 0xDEADBEEF, a = 1. Атрибут repr(align(64)) задаёт минимальное "
            "выравнивание. Его применяют, чтобы счётчики, которые меняются разными потоками, "
            "не попадали в одну кэш-линию: иначе производительность падает из-за ложного "
            "разделения (false sharing)."
        ),
        callout(
            "warning",
            "packed не превращает доступ в безопасный",
            "Атрибут меняет только раскладку. Любое обращение к полю идёт через addr_of! плюс "
            "read_unaligned или write_unaligned. Ссылка на невыровненное поле — неопределённое поведение, "
            "даже если программа «иногда работает»."
        ),
        heading("Граница с C: extern \"C\" и владение"),
        text(
            "FFI (Foreign Function Interface) связывает Rust с библиотеками на других языках. Блок "
            "extern \"C\" объявляет внешние функции, а #[no_mangle] с pub extern \"C\" экспортирует "
            "Rust-функцию в C. Главное правило: ABI должен совпадать с обеих сторон. String, Vec и "
            "trait-объекты C-представления не имеют, поэтому вместо строки передаётся пара "
            "«указатель и длина» либо C-строка с нулевым завершителем, а владение фиксируется "
            "письменно: кто выделил память, тот её и освобождает."
        ),
        example(
            "rust",
            r"""
            use std::ffi::{c_char, CStr, CString};

            extern "C" {
                fn strlen(s: *const c_char) -> usize;
                fn getenv(name: *const c_char) -> *const c_char;
            }

            /// Безопасная обёртка: проверяет наличие нулевого байта внутри строки.
            fn c_strlen(s: &str) -> Result<usize, std::ffi::NulError> {
                let owned = CString::new(s)?;
                Ok(unsafe { strlen(owned.as_ptr()) })
            }

            /// Возвращает Option: null-указатель превращается в None до разыменования.
            fn env(name: &str) -> Option<String> {
                let key = CString::new(name).ok()?;
                let raw = unsafe { getenv(key.as_ptr()) };
                if raw.is_null() {
                    return None;
                }
                Some(unsafe { CStr::from_ptr(raw) }.to_string_lossy().into_owned())
            }

            fn main() {
                println!("len = {:?}", c_strlen("systems"));
                println!("len = {:?}", c_strlen("nu\0l"));
                println!("PATH = {:?}", env("PATH").map(|v| !v.is_empty()));
            }
            """,
        ),
        text(
            "Вывод: len = Ok(7), len = Err(NulError ...), PATH = Some(true). CString проверяет вход "
            "до вызова, null-указатель превращается в None, а CStr::from_ptr живёт столько, сколько "
            "нужно для копирования. Утечек нет: getenv возвращает не нашу память."
        ),
        text(
            "Обратное направление требует осторожности: паника, пересекающая границу C, приводит к "
            "неопределённому поведению, а начиная с Rust 1.71 — к аварийному завершению процесса. "
            "Корректнее объявить функцию как extern \"C-unwind\", если вызывающий умеет обрабатывать "
            "развёртывание стека, либо обернуть тело в catch_unwind и вернуть код ошибки. Для "
            "экспорта в C в 2024 году предпочтителен #[unsafe(no_mangle)]: он делает явным, "
            "что за имя в бинарнике отвечает автор."
        ),
        heading("Инструменты: bindgen, cbindgen, cxx"),
        text(
            "Ручные объявления быстро расходятся с заголовками, поэтому привязки генерируют: "
            "bindgen читает C-заголовки и создаёт Rust-объявления, cbindgen делает обратное. "
            "Оба подключаются как build-dependencies, вызываются из build.rs и пишут результат "
            "в OUT_DIR.\n\n"
            "Для C++ используется крейт cxx: мост описывается в декларативном макросе, генератор "
            "создаёт обе стороны, и несовпадение типов видно на этапе компиляции. Это надёжнее "
            "bindgen для C++, где наследование, шаблоны и перегрузки требуют ручной работы."
        ),
        example(
            "rust",
            r"""
            // build.rs
            fn main() {
                println!("cargo:rerun-if-changed=wrapper.h");

                let bindings = bindgen::Builder::default()
                    .header("wrapper.h")
                    .allowlist_function("calc_.*")
                    .parse_callbacks(Box::new(bindgen::CargoCallbacks::new()))
                    .generate()
                    .expect("не удалось сгенерировать привязки");

                let out = std::path::PathBuf::from(std::env::var("OUT_DIR").unwrap());
                bindings.write_to_file(out.join("bindings.rs")).unwrap();
            }

            // src/lib.rs
            mod ffi {
                include!(concat!(env!("OUT_DIR"), "/bindings.rs"));
            }

            pub fn calc_total(values: &[i32]) -> i32 {
                let raw = values.as_ptr();
                unsafe { ffi::calc_sum(raw, values.len()) }
            }
            """,
        ),
        text(
            "Обратите внимание на allowlist: без него bindgen притянет из системных заголовков "
            "тысячи сущностей. И на сигнатуру: срез гарантирует, что указатель валиден и длина "
            "совпадает с реальным размером буфера."
        ),
        example(
            "rust",
            r"""
            #[cxx::bridge]
            mod ffi {
                unsafe extern "C++" {
                    include!("demo/geometry.h");

                    type Point;
                    fn new_point(x: f64, y: f64) -> UniquePtr<Point>;
                    fn norm(self: &Point) -> f64;
                }

                extern "Rust" {
                    fn scale(factor: f64) -> f64;
                }
            }

            fn scale(factor: f64) -> f64 {
                factor * 2.0
            }
            """,
        ),
        heading("Системные вызовы и их обёртки"),
        text(
            "Системный вызов — переход в ядро: открыть файл, прочитать байты, отобразить память. "
            "В Linux и macOS они доступны через C API, поэтому вызываются через libc, который "
            "повторяет платформенные объявления. Крейт nix предлагает идиоматичный слой: новотипы "
            "для дескрипторов, проверка ошибок и Result вместо errno. Функции libc возвращают -1 "
            "при ошибке и требуют ручной проверки errno, nix делает это за вас, но добавляет "
            "обёртки. Для узкой операции разумно взять libc, для большой подсистемы — nix."
        ),
        example(
            "rust",
            r"""
            use std::io;
            use std::os::fd::{FromRawFd, OwnedFd};

            fn open_readonly(path: &str) -> io::Result<OwnedFd> {
                let c_path = std::ffi::CString::new(path).map_err(|_| {
                    io::Error::new(io::ErrorKind::InvalidInput, "нулевой байт в пути")
                })?;

                let fd = unsafe { libc::open(c_path.as_ptr(), libc::O_RDONLY) };
                if fd < 0 {
                    return Err(io::Error::last_os_error());
                }

                // OwnedFd закрывает дескриптор в Drop, утечки при раннем выходе нет.
                Ok(unsafe { OwnedFd::from_raw_fd(fd) })
            }

            fn read_prefix(fd: &OwnedFd, len: usize) -> io::Result<Vec<u8>> {
                use std::os::fd::AsRawFd;

                let mut buf = vec![0u8; len];
                let read = unsafe { libc::read(fd.as_raw_fd(), buf.as_mut_ptr().cast(), buf.len()) };
                if read < 0 {
                    return Err(io::Error::last_os_error());
                }
                let read = read as usize;
                buf.truncate(read);
                Ok(buf)
            }

            fn main() -> io::Result<()> {
                let fd = open_readonly("/etc/hostname")?;
                let bytes = read_prefix(&fd, 64)?;
                println!("прочитано байт: {}", bytes.len());
                Ok(())
            }
            """,
        ),
        text(
            "Вывод зависит от системы, например: прочитано байт: 13. Главный элемент — "
            "OwnedFd: он превращает сырой дескриптор во владеющий тип, который закрывается в Drop. "
            "Без него пришлось бы вызывать close на каждом пути выхода, и ошибка давала бы утечку."
        ),
        text(
            "Для короткой нативной операции можно не подключать тяжёлые зависимости и описать "
            "объявление самостоятельно — так поступают, когда нужной функции нет в обёртках или "
            "важен минимальный образ. Для проектов на нескольких платформах лучше платформенные "
            "крейты: они уже учитывают различия раскладки и соглашений о вызовах."
        ),
        example(
            "rust",
            r"""
            #[cfg(unix)]
            fn process_id() -> i32 {
                extern "C" {
                    fn getpid() -> i32;
                }
                // Безопасно: getpid не имеет предусловий и не может завершиться ошибкой.
                unsafe { getpid() }
            }

            #[cfg(windows)]
            fn process_id() -> i32 {
                unsafe { windows_sys::Win32::System::Threading::GetCurrentProcessId() as i32 }
            }

            fn main() {
                println!("pid = {}", process_id());
            }
            """,
        ),
        heading("no_std и встраиваемые платформы"),
        text(
            "Атрибут #![no_std] отключает стандартную библиотеку: код собирается только с ядром "
            "core. Это нужно для микроконтроллеров, загрузчиков и ядер, где нет кучи и операционной "
            "системы. #![no_main] убирает стандартную точку входа: стартовая функция зависит от "
            "платформы.\n\n"
            "В no_std обработчик паники нужно написать самому, без #[panic_handler] программа не "
            "соберётся. Разумный обработчик не восстанавливается, а сохраняет состояние и "
            "перезагружает контроллер. Если используется куча, нужен глобальный аллокатор и "
            "стратегия реакции на исчерпание памяти."
        ),
        example(
            "rust",
            r"""
            #![no_std]
            #![no_main]

            use core::panic::PanicInfo;

            #[panic_handler]
            fn on_panic(info: &PanicInfo) -> ! {
                // В реальном проекте здесь запись в UART или semihosting.
                if let Some(location) = info.location() {
                    let _ = (location.file(), location.line());
                }
                loop {
                    core::hint::spin_loop();
                }
            }

            #[no_mangle]
            pub extern "C" fn main() -> ! {
                let state: u32 = 0x1234;
                loop {
                    let _volatile = core::hint::black_box(state);
                    core::hint::spin_loop();
                }
            }
            """,
        ),
        text(
            "Функция core::hint::black_box не даёт компилятору убрать вычисление, которое снаружи "
            "выглядит неиспользуемым, а spin_loop подсказывает, что процессор в холостой петле, "
            "и снижает энергопотребление на таких архитектурах, как ARM."
        ),
        table(
            ["Возможность", "std", "no_std плюс core", "Что делать вместо"],
            [
                ["String и Vec", "есть", "нужен alloc и аллокатор", "статические буферы фиксированного размера"],
                ["println!", "есть", "нет", "драйвер UART или отладочный вывод через semihosting"],
                ["panic и развёртывание стека", "есть", "abort", "panic = \"abort\" в профиле"],
                ["потоки и мьютексы", "есть", "нет", "критические секции и атомики"],
                ["время и файлы", "есть", "нет", "таймеры и регистры периферии"],
            ],
        ),
        text(
            "Доступ к периферии — это запись в память по фиксированному адресу, но компилятор вправе "
            "объединять, удалять и переставлять обращения к обычным переменным. Для регистров это "
            "недопустимо: чтение имеет побочный эффект, оно снимает флаг прерывания. Поэтому "
            "применяются read_volatile и write_volatile: они запрещают оптимизацию и гарантируют "
            "ровно одно обращение к памяти на операцию."
        ),
        example(
            "rust",
            r"""
            use core::ptr::{addr_of, addr_of_mut};

            #[repr(C)]
            struct UartRegisters {
                status: u32,
                data: u32,
                baud: u32,
                control: u32,
            }

            struct Uart {
                regs: *mut UartRegisters,
            }

            impl Uart {
                /// # Safety
                /// base обязан указывать на отображённый регион UART с такой раскладкой.
                unsafe fn new(base: *mut UartRegisters) -> Self {
                    Self { regs: base }
                }

                fn write_byte(&self, byte: u8) {
                    let status = unsafe { addr_of!((*self.regs).status).read_volatile() };
                    while status & (1 << 7) == 0 {
                        core::hint::spin_loop();
                    }
                    unsafe { addr_of_mut!((*self.regs).data).write_volatile(byte as u32) };
                }
            }
            """,
        ),
        callout(
            "info",
            "Почему не &mut UartRegisters",
            "Ссылка на регистры создаёт предположение об эксклюзивном доступе и допустимом "
            "выравнивании, которого у модели памяти для регистров нет. Сырой указатель плюс "
            "addr_of! и volatile-доступ выражают намерение точнее."
        ),
        heading("SIMD и интринсики"),
        text(
            "SIMD (Single Instruction, Multiple Data) — способность процессора одной инструкцией "
            "обработать несколько значений: восемь f32 за такт в AVX, четыре — в SSE. Интринсики "
            "core::arch вида _mm256_add_ps компилируются в конкретные машинные инструкции и "
            "требуют unsafe: без проверки поддержки процессором программа получит недопустимую "
            "инструкцию.\n\n"
            "Шаблон состоит из трёх частей: макрос is_x86_feature_detected! проверяет наличие "
            "расширения, функции помечаются #[target_feature(enable = \"avx\")], а хвост массива "
            "обрабатывается скалярно. Без третьего шага последние элементы останутся "
            "необработанными."
        ),
        example(
            "rust",
            r"""
            #[cfg(target_arch = "x86_64")]
            mod fast {
                use core::arch::x86_64::*;

                #[target_feature(enable = "avx")]
                unsafe fn add_avx(a: &[f32], b: &[f32], dst: &mut [f32]) {
                    let mut i = 0;
                    while i + 8 <= a.len() {
                        let va = _mm256_loadu_ps(a.as_ptr().add(i));
                        let vb = _mm256_loadu_ps(b.as_ptr().add(i));
                        _mm256_storeu_ps(dst.as_mut_ptr().add(i), _mm256_add_ps(va, vb));
                        i += 8;
                    }
                    for k in i..a.len() {
                        dst[k] = a[k] + b[k];
                    }
                }

                pub fn add(a: &[f32], b: &[f32], dst: &mut [f32]) {
                    assert_eq!(a.len(), b.len());
                    assert_eq!(a.len(), dst.len());
                    if is_x86_feature_detected!("avx") {
                        unsafe { add_avx(a, b, dst) };
                    } else {
                        for k in 0..a.len() {
                            dst[k] = a[k] + b[k];
                        }
                    }
                }
            }

            #[cfg(not(target_arch = "x86_64"))]
            fn scalar_add(a: &[f32], b: &[f32], dst: &mut [f32]) {
                for k in 0..a.len() {
                    dst[k] = a[k] + b[k];
                }
            }
            """,
        ),
        text(
            "Заметьте инкапсуляцию: безопасная функция add проверяет длины, выбирает путь и только "
            "затем вызывает unsafe-функцию, недоступную за пределы модуля. Вызвать инструкцию AVX "
            "на процессоре без AVX снаружи невозможно. Переносимая альтернатива core::simd из "
            "ночного компилятора использует тип f32x8 и выбирает инструкции сама."
        ),
        heading("Сырые указатели и адресная арифметика"),
        text(
            "Сырой указатель *const T или *mut T не отслеживается заимствованием: компилятор не "
            "проверяет ни срок жизни, ни выравнивание, ни наличие памяти по адресу. Различие со "
            "ссылкой принципиально: ссылка обязана быть валидной и выровненной всё время жизни, "
            "а сырой указатель может быть нулевым или невыровненным, пока по нему не разыменовывают.\n\n"
            "NonNull<T> — ненулевой указатель, который позволяет применять оптимизацию ниши: "
            "Option<NonNull<T>> занимает столько же, сколько один указатель. Именно NonNull лежит "
            "в основе Box, Vec и Rc."
        ),
        example(
            "rust",
            r"""
            use core::ptr::NonNull;

            struct MyBox<T> {
                ptr: NonNull<T>,
            }

            impl<T> MyBox<T> {
                fn new(value: T) -> Self {
                    let raw = Box::into_raw(Box::new(value));
                    Self { ptr: NonNull::new(raw).expect("Box не бывает нулевым") }
                }

                fn get(&self) -> &T {
                    // Безопасно: ptr создан из Box и жив до Drop.
                    unsafe { self.ptr.as_ref() }
                }

                fn set(&mut self, value: T) {
                    unsafe { *self.ptr.as_mut() = value };
                }
            }

            impl<T> Drop for MyBox<T> {
                fn drop(&mut self) {
                    unsafe { drop(Box::from_raw(self.ptr.as_ptr())) };
                }
            }

            fn main() {
                let mut b = MyBox::new(10);
                b.set(20);
                println!("value = {}", b.get());
                println!("option = {}", std::mem::size_of::<Option<NonNull<u8>>>());
            }
            """,
        ),
        text(
            "Вывод: value = 20, option = 8 на 64-битной платформе. Структура типична для безопасного "
            "типа поверх unsafe: конструктор получает владение, Drop возвращает его, а методы "
            "доступа опираются на инвариант «указатель всегда валиден»."
        ),
        text(
            "Макросы addr_of! и addr_of_mut! создают сырой указатель на поле, не создавая ссылки на "
            "него. Это критично для packed-структур и для ещё не инициализированной памяти. "
            "Приём &structure.field as *const _ создаёт промежуточную ссылку, и такой код "
            "следует заменять."
        ),
        example(
            "rust",
            r"""
            use std::alloc::{alloc, dealloc, Layout};
            use std::ptr;

            fn main() {
                let layout = Layout::array::<u32>(4).expect("корректная раскладка");

                unsafe {
                    let raw = alloc(layout) as *mut u32;
                    if raw.is_null() {
                        return;
                    }

                    for i in 0..4 {
                        raw.add(i).write(i as u32 * 10);
                    }

                    let total: u32 = (0..4).map(|i| raw.add(i).read()).sum();
                    let distance = raw.add(3).offset_from(raw);

                    println!("total    = {}", total);
                    println!("distance = {}", distance);
                    println!("is null  = {}", (raw as *const u8).is_null());

                    for i in 0..4 {
                        ptr::drop_in_place(raw.add(i));
                    }
                    dealloc(raw as *mut u8, layout);
                }
            }
            """,
        ),
        text(
            "Вывод: total = 60, distance = 3, is null = false. Метод add смещает указатель на "
            "элементы с учётом размера типа, offset_from возвращает разницу в элементах. В отличие "
            "от сложения с числом, они не разрешают выйти за пределы объекта; для внешних адресов "
            "применяется wrapping_add, который не вызывает неопределённого поведения."
        ),
        heading("Отображение файлов в память"),
        text(
            "mmap отображает файл или анонимный регион прямо в адресное пространство процесса: "
            "чтение байтов превращается в доступ к памяти, а изменения становятся видимы файлу. "
            "Это выигрышно для больших файлов, которые не помещаются в память целиком, и для "
            "разделяемой памяти между процессами.\n\n"
            "Регион создаётся через libc::mmap и уничтожается через munmap, ошибкой считается "
            "значение MAP_FAILED, а не null. Владение регионом удобно выразить типом с "
            "реализацией Drop: тогда освобождение произойдёт при любом выходе из области видимости."
        ),
        example(
            "rust",
            r"""
            use std::fs::File;
            use std::io;
            use std::os::fd::AsRawFd;

            struct MmapRegion {
                ptr: *mut u8,
                len: usize,
            }

            impl MmapRegion {
                fn new(file: &File, len: usize) -> io::Result<Self> {
                    let ptr = unsafe {
                        libc::mmap(
                            std::ptr::null_mut(),
                            len,
                            libc::PROT_READ | libc::PROT_WRITE,
                            libc::MAP_SHARED,
                            file.as_raw_fd(),
                            0,
                        )
                    };
                    if ptr == libc::MAP_FAILED {
                        return Err(io::Error::last_os_error());
                    }
                    Ok(Self { ptr: ptr.cast(), len })
                }

                fn as_slice(&self) -> &[u8] {
                    // Безопасно: регион жив, len совпадает с длиной отображения.
                    unsafe { std::slice::from_raw_parts(self.ptr, self.len) }
                }
            }

            impl Drop for MmapRegion {
                fn drop(&mut self) {
                    unsafe { libc::munmap(self.ptr.cast(), self.len) };
                }
            }
            """,
        ),
        text(
            "У метода as_slice есть скрытое условие: файл не должен усечь другой процесс, иначе "
            "часть страниц станет недоступной и обращение завершит программу сигналом. Поэтому "
            "рекомендуется крейт memmap2: он инкапсулирует платформенные различия, предоставляет "
            "безопасный Mmap и требует явно помечать небезопасные операции."
        ),
        example(
            "rust",
            r"""
            use memmap2::{Mmap, MmapOptions};
            use std::fs::File;
            use std::io;

            fn map_readonly(path: &str) -> io::Result<Mmap> {
                let file = File::open(path)?;
                // Безопасно при условии, что файл не изменяется извне во время работы.
                unsafe { MmapOptions::new().map(&file) }
            }

            fn main() -> io::Result<()> {
                let map = map_readonly("data.bin")?;
                let digits = map.iter().take(1024).filter(|b| b.is_ascii_digit()).count();
                println!("размер = {} байт", map.len());
                println!("цифр в начале = {}", digits);
                Ok(())
            }
            """,
        ),
        heading("Безопасные абстракции и Pin"),
        text(
            "Ценность unsafe держится на дисциплине: каждое небезопасное действие сопровождается "
            "описанием «Safety: какие условия обязан обеспечить вызывающий». Безопасная обёртка "
            "проверяет их сама и выставляет наружу только методы, которые нельзя вызвать "
            "неправильно. Такие описания оформляются разделом # Safety в документации, а линтер "
            "clippy::undocumented_unsafe_blocks требует комментарий к каждому unsafe-блоку."
        ),
        example(
            "rust",
            r"""
            use std::io;

            mod raw {
                /// # Safety
                /// ptr обязан указывать на читаемый регион длиной не меньше len байт.
                pub unsafe fn checksum(ptr: *const u8, len: usize) -> u32 {
                    let mut acc = 0u32;
                    for i in 0..len {
                        acc = acc.wrapping_add((*ptr.add(i)) as u32);
                    }
                    acc
                }
            }

            pub struct SafeBuffer {
                data: Vec<u8>,
            }

            impl SafeBuffer {
                pub fn new(size: usize) -> Self {
                    Self { data: vec![0u8; size] }
                }

                pub fn perform(&self) -> io::Result<u32> {
                    if self.data.is_empty() {
                        return Err(io::Error::new(io::ErrorKind::InvalidInput, "пустой буфер"));
                    }
                    // Инвариант выполнен: указатель и длина берутся из одного и того же Vec.
                    Ok(unsafe { raw::checksum(self.data.as_ptr(), self.data.len()) })
                }
            }

            fn main() {
                let buffer = SafeBuffer::new(4);
                println!("checksum = {:?}", buffer.perform());
                println!("empty    = {:?}", SafeBuffer::new(0).perform().is_err());
            }
            """,
        ),
        text(
            "Вывод: checksum = Ok(0), empty = true. Указатель и длина получены из одного вектора, "
            "поэтому несоответствие между ними невозможно — это инвариант обёртки. Проверка на "
            "пустоту выполняется до unsafe-блока."
        ),
        text(
            "Отдельный случай — самореференциальные структуры, где поле указывает на другое поле. "
            "При перемещении указатель станет висячим, поэтому применяется Pin<P>: он гарантирует, "
            "что значение не сдвинется с места, пока не будет вызван Drop. На этом основаны "
            "будущие объекты async."
        ),
        example(
            "rust",
            r"""
            use std::marker::PhantomPinned;
            use std::pin::Pin;

            struct SelfRef {
                data: String,
                ptr: *const String,
                _pin: PhantomPinned,
            }

            impl SelfRef {
                fn new(data: String) -> Pin<Box<Self>> {
                    let mut boxed = Box::pin(SelfRef {
                        data,
                        ptr: std::ptr::null(),
                        _pin: PhantomPinned,
                    });

                    let anchor: *const String = &boxed.data;
                    // Безопасно: значение закреплено, адрес поля больше не изменится.
                    unsafe { boxed.as_mut().get_unchecked_mut().ptr = anchor };
                    boxed
                }

                fn show(&self) {
                    let pointed = unsafe { &*self.ptr };
                    println!("data = {}, через указатель = {}", self.data, pointed);
                }
            }

            fn main() {
                let value = SelfRef::new(String::from("systems"));
                value.show();
            }
            """,
        ),
        text(
            "Вывод: data = systems, через указатель = systems. PhantomPinned делает структуру "
            "неперемещаемой, и компилятор не даст взять &mut SelfRef. get_unchecked_mut допустим "
            "внутри конструктора: значение уже в куче и закреплено."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["ссылка на поле packed-структуры", "невыровненная ссылка, неопределённое поведение", "addr_of! вместе с read_unaligned и write_unaligned"],
                ["передача String или Vec в C", "ABI не совпадает, другая сторона видит мусор", "передавать указатель и длину либо CString и CStr"],
                ["паника на границе extern \"C\"", "процесс аварийно завершается", "catch_unwind и код ошибки либо extern \"C-unwind\""],
                ["забытая проверка -1 у вызова libc", "читается errno вместо ошибки или мусор", "OwnedFd, io::Error::last_os_error, крейт nix"],
                ["read_volatile пропущен для регистров", "компилятор удалил или слил обращения", "read_volatile и write_volatile для всех регистров"],
                ["SIMD без is_x86_feature_detected!", "недопустимая инструкция на старом процессоре", "проверка расширения и скалярный резерв"],
                ["add за пределы объекта", "неопределённое поведение даже без разыменования", "wrapping_add для внешних адресов, with_addr внутри"],
                ["mmap без Drop", "утечка отображений и файловых дескрипторов", "тип с реализацией Drop или memmap2"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняются в отдельном проекте: cargo new sys-lab, затем cargo run. "
            "Для заданий с libc добавьте в Cargo.toml строку libc = \"0.2\" в раздел [dependencies]. "
            "Сборку держите с предупреждениями: RUSTFLAGS=\"-D warnings\" cargo build."
        ),
        numbered(
            "Раскладка: объявите repr(C)-структуру из полей u8, u64 и u16 и выведите size_of и offset_of для каждого поля. Объясните, откуда взялись байты заполнителя, и сравните с repr(packed).",
            "FFI: напишите функцию на C int mul_add(int a, int b, int c) в отдельном файле, соберите её через cc в build.rs и вызовите из Rust, не используя unsafe в вызывающем коде.",
            "Системный вызов: реализуйте функцию count_bytes(path: &str) через libc::open, libc::read и OwnedFd. Убедитесь, что при несуществующем пути возвращается io::Error, а не паника.",
            "Сырые указатели: реализуйте собственную обёртку UniqueBox<T> поверх NonNull<T> с методами new, get, set и Drop. Проверьте, что size_of::<Option<UniqueBox<u8>>>() не превышает размера указателя.",
            "Безопасная обёртка: напишите модуль, который экспортирует функцию extern \"C\" fn process(buf: *const u8, len: usize) -> i32, и убедитесь, что при нулевом указателе или нулевой длине она возвращает код ошибки, а не разыменовывает память.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            """
            repr(C):     size = 24, u8 = 0, u64 = 8, u16 = 16
            repr(packed): size = 11, u8 = 0, u64 = 1, u16 = 9
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 3",
            "Сохраните дескриптор в OwnedFd сразу после успешного open. Тогда ранний выход по "
            "ошибке чтения всё равно закроет дескриптор, а код останется линейным и без ручных "
            "вызовов close."
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему repr(C)-структура занимает больше места, чем сумма размеров её полей?",
            "Зачем нужен repr(transparent) и чем он отличается от обычного новотипа?",
            "Почему ссылку на поле packed-структуры нельзя брать напрямую?",
            "Что произойдёт, если паника возникнет внутри функции extern \"C\"?",
            "Почему для доступа к регистрам периферии недостаточно обычного чтения через ссылку?",
            "Когда следует применять wrapping_add, а не add?",
        ),
        heading("Ответы", 3),
        numbered(
            "Компилятор вставляет байты заполнителя, чтобы каждое поле начиналось по адресу, кратному его выравниванию, и чтобы выровнялся массив таких структур.",
            "Он гарантирует, что обёртка имеет ту же раскладку и ABI, что и единственное непустое поле, поэтому её можно передавать в C. Обычный новотип без атрибута никаких гарантий совместимости не даёт.",
            "Поле может оказаться по адресу, не кратному выравниванию типа, а ссылка в Rust обязана быть выровненной; нарушение этого условия — неопределённое поведение. Используются addr_of! и read_unaligned.",
            "Начиная с Rust 1.71 паника на границе extern \"C\" не разворачивает стек, а прерывает процесс. Для контролируемого поведения применяются catch_unwind и код ошибки либо extern \"C-unwind\".",
            "Обычное чтение компилятор вправе удалить, объединить или переставить, а чтение регистра часто имеет побочный эффект — снимает флаг прерывания. Поэтому нужны read_volatile и write_volatile.",
            "Для адресов, полученных извне: add требует оставаться в пределах одного объекта, иначе поведение неопределено, а wrapping_add допустим для любого адреса и корректно вычисляет результат при переполнении.",
        ),
        heading("Итоги"),
        bullets(
            "Раскладка: repr(C) для FFI, repr(transparent) для обёрток без накладных расходов, "
            "repr(packed) для плотных форматов, repr(align(N)) для выравнивания; поля packed "
            "читаются через addr_of! и read_unaligned.",
            "FFI: extern \"C\", экспорт через pub extern \"C\" и #[unsafe(no_mangle)], строки через "
            "CString и CStr, владение по принципу «кто выделил, тот освобождает».",
            "Инструменты: bindgen для C, cbindgen для экспорта в C, cxx для C++ с проверкой "
            "несоответствий на этапе компиляции.",
            "Системные вызовы: libc для низкого уровня, nix для идиоматичного слоя, OwnedFd для "
            "автоматического закрытия дескрипторов.",
            "no_std: #[panic_handler] и собственная точка входа, core вместо std, volatile-доступ "
            "к регистрам периферии.",
            "SIMD: core::arch с проверкой is_x86_feature_detected!, #[target_feature] и скалярный "
            "хвост; core::simd остаётся ночным.",
            "Указатели: NonNull, addr_of!, add и offset_from внутри объекта, wrapping_add для "
            "внешних адресов.",
            "Память: mmap с проверкой MAP_FAILED, регион в типе с Drop или memmap2, Pin и "
            "PhantomPinned для самореференциальных структур.",
            "Дисциплина: каждый unsafe-блок имеет документированный раздел Safety, а предусловия проверяются безопасным кодом до его входа.",
        ),
        heading("Что дальше"),
        text(
            "Следующий урок посвящён экосистеме Cargo: как из отдельных крейтов собирается "
            "workspace, как устроены features и профили сборки, как добавить build-скрипты с "
            "нативными библиотеками — всё это напрямую понадобится, когда системный код нужно будет "
            "распространять как зависимость."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Rust FFI Omnibus — рабочие примеры FFI: github.com/rust-embedded/rust-ffi-omnibus",
            "The Embedded Rust Book — учебник по no_std: docs.rust-embedded.org/book",
            "The Rustonomicon — небезопасный Rust и правила валидности: doc.rust-lang.org/nomicon",
            "Документация bindgen: rust-lang.github.io/rust-bindgen",
            "Документация cxx для C++-мостов: cxx.rs",
            "Крейт nix — идиоматичные системные вызовы: docs.rs/nix",
            "memmap2 — отображение файлов в память: docs.rs/memmap2",
            "core::arch — интринсики и SIMD: doc.rust-lang.org/core/arch",
        ),
    ],
}
