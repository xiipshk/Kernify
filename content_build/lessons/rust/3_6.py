"""Урок 3.6 курса Rust: продвинутая конкурентность."""

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
    "program_order": 3,
    "topic_order": 6,
    "name": "3.6. Продвинутая конкурентность",
    "slug": "rust-3-6-продвинутая-конкурентность",
    "short_description": (
        "Неблокирующие структуры данных, модель памяти и значения Ordering, "
        "быстрые примитивы вроде parking_lot, шардированные словари и проверка "
        "конкурентного кода через loom."
    ),
    "topic_name": "Продвинутая конкурентность",
    "topic_description": (
        "Разбор уровней прогресса в параллельных структурах данных, проблемы ABA, "
        "точных правил выбора Ordering, отложенного освобождения памяти через "
        "epoch-based reclamation, быстрых примитивов синхронизации и модели-чекера loom."
    ),
    "learning_objectives": [
        "Различать obstruction-free, lock-free и wait-free алгоритмы и их гарантии прогресса",
        "Выбирать значения Ordering (Relaxed, Acquire, Release, AcqRel, SeqCst) по модели памяти",
        "Разбирать проблему ABA и применять тегированные указатели или отложенное освобождение",
        "Освобождать память в неблокирующих структурах через crossbeam-epoch и Guard",
        "Заменять std-примитивы на parking_lot и распараллеливать словарь через DashMap",
        "Проверять конкурентный код перебором чередований с помощью loom",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "rust",
        "concurrency",
        "lock-free",
        "atomics",
        "memory-ordering",
        "crossbeam",
    ],
    "starter_code": code(
        r"""
        use std::sync::atomic::{AtomicUsize, Ordering};
        use std::thread;

        const THREADS: usize = 4;
        const ROUNDS: usize = 10_000;

        static COUNTER: AtomicUsize = AtomicUsize::new(0);

        fn main() {
            thread::scope(|s| {
                for _ in 0..THREADS {
                    s.spawn(|| {
                        for _ in 0..ROUNDS {
                            COUNTER.fetch_add(1, Ordering::Relaxed);
                        }
                    });
                }
            });

            println!(
                "ожидалось {} , получено {}",
                THREADS * ROUNDS,
                COUNTER.load(Ordering::Relaxed)
            );
        }
        """,
    ),
    "hints": [
        "Счётчик и флаг обычно достаточно делать на Ordering::Relaxed: важна только атомарность, порядок не нужен.",
        "Пара Release (запись) — Acquire (чтение) гарантирует, что данные, записанные до флага, видны после прочтения флага.",
        "Сравнение compare_exchange может давать ложный отказ, поэтому внешний цикл повтора обязателен.",
        "Если не уверены, что выбранный ordering корректен, начните с SeqCst, а потом ослабляйте под тестом loom.",
    ],
    "content": [
        text(
            "Конкурентность в Rust начинается с потоков и мьютексов, но на этом уровне "
            "остаются структуры данных, которые работают без блокировок совсем. Их "
            "называют неблокирующими: потоки не ждут, пока другой поток освободит "
            "замок, а согласовывают изменения через атомарные операции над общей "
            "ячейкой памяти. Такой подход убирает блокировку потока операционной "
            "системой, но требует точных рассуждений о порядке операций.\n\n"
            "В этом уроке разберём четыре взаимосвязанные темы. Первая — уровни "
            "прогресса: чем lock-free отличается от wait-free и почему это влияет на "
            "устойчивость под нагрузкой. Вторая — модель памяти Rust и значения "
            "`Ordering`: какой порядок достаточен и как ошибка в нём превращается в "
            "редкий баг, незаметный на тестах. Третья — освобождение памяти в структурах "
            "без замков: проблема ABA, hazard pointers и epoch-based reclamation из "
            "`crossbeam-epoch`. Четвёртая — практическая сторона: быстрые примитивы "
            "`parking_lot`, шардированный словарь `dashmap`, RCU-паттерн для редко "
            "обновляемых данных и модель-чекер `loom`."
        ),
        text(
            "Материал опирается на `unsafe` и атомики из std, поэтому подразумевается "
            "знакомство с разделом про небезопасный Rust и базовыми потоками. Если "
            "термины `Acquire`, `Release`, `CAS` звучат впервые, это нормально: каждый "
            "из них вводится в тексте с определением и примером. Код запускается "
            "сборкой edition 2021 на stable; внешние крейты подключаются через "
            "`cargo add`."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "различать obstruction-free, lock-free и wait-free алгоритмы и понимать, какую гарантию прогресса даёт каждый;",
            "выбирать минимально достаточное значение `Ordering` и объяснять, какие переупорядочивания оно запрещает;",
            "строить lock-free стек по алгоритму Трейбера и понимать, почему простой CAS над `AtomicPtr` требует осторожности;",
            "распознавать проблему ABA и устранять её тегированными указателями или отложенным освобождением;",
            "использовать `crossbeam_epoch` с `Guard` для безопасного удаления узлов в структуре без замков;",
            "применять `parking_lot`, `dashmap` и паттерн RCU в прикладном коде с интенсивным чтением.",
        ),
        heading("Уровни прогресса: lock-free, wait-free, obstruction-free"),
        text(
            "**Obstruction-free** — самый слабый уровень: поток завершает шаг, если "
            "выполняется в одиночестве. **Lock-free** — прогресс гарантирован системе: "
            "за конечное время хотя бы один поток завершает операцию, хотя отдельный "
            "поток может голодать. **Wait-free** — каждый поток завершает операцию за "
            "ограниченное число шагов независимо от остальных."
        ),
        table(
            ["Уровень", "Гарантия", "Кому гарантирован прогресс", "Типичная цена"],
            [
                ["Obstruction-free", "завершение без конкуренции", "одному потоку", "повторы под нагрузкой"],
                ["Lock-free", "хотя бы один поток завершает шаг", "системе целиком", "голодание отдельного потока"],
                ["Wait-free", "каждый поток завершает шаг", "каждому потоку", "больше памяти и операций"],
                ["Блокировка", "поток ждёт освобождения", "держателю замка", "пробуждение из ядра, дедлоки"],
            ],
        ),
        text(
            "Практический смысл в том, что lock-free структура не держит поток в "
            "очереди за замком: неудачный шаг повторяется на месте. Цена — трата "
            "процессора на повторы при высокой конкуренции, поэтому суммарная "
            "пропускная способность может оказаться ниже, чем у мьютекса."
        ),
        callout(
            "info",
            "Терминология",
            "Атомарная операция — операция, которая наблюдается другими потоками целиком "
            "или не наблюдается вообще. CAS (compare-and-swap, в Rust — "
            "`compare_exchange`) заменяет значение, только если текущее совпало с "
            "ожидаемым. RMW (read-modify-write) — любой вариант «прочитать и изменить»: "
            "`fetch_add`, `swap`, `compare_exchange`."
        ),
        heading("Атомики std: что даёт базовая гарантия"),
        text(
            "Атомарные типы `AtomicUsize`, `AtomicBool`, `AtomicPtr` и другие живут в "
            "static или в переменной и позволяют нескольким потокам читать и изменять "
            "одну ячейку без гонки данных. Атомарность — это уже немало: тип-система "
            "Rust запрещает обычный общий доступ, и атомики дают ровно ту "
            "конструкцию, где он безопасен.\n\n"
            "Для простого счётчика достаточно `Ordering::Relaxed`: значение не "
            "используется для синхронизации других данных, важна только их сумма в "
            "конце. `thread::scope` позволяет потокам заимствовать локальные "
            "переменные, поэтому `Arc` не нужен."
        ),
        example(
            "rust",
            """
            use std::sync::atomic::{AtomicUsize, Ordering};
            use std::thread;

            fn main() {
                let counter = AtomicUsize::new(0);

                thread::scope(|s| {
                    for _ in 0..4 {
                        s.spawn(|| {
                            for _ in 0..25_000 {
                                counter.fetch_add(1, Ordering::Relaxed);
                            }
                        });
                    }
                });

                println!("итог: {}", counter.load(Ordering::Relaxed));
                println!("изменено перестановками: {}", counter.swap(0, Ordering::SeqCst));
            }
            """,
        ),
        text(
            "Вывод: `итог: 100000`, затем `изменено перестановками: 100000`. "
            "`Relaxed` здесь корректен именно потому, что никакой другой объект не "
            "связан с этим счётчиком."
        ),
        heading("Модель памяти и пять значений Ordering"),
        text(
            "Современный процессор и компилятор переставляют независимые чтения и "
            "записи, чтобы использовать конвейер эффективнее. Модель памяти Rust "
            "формализует, какие перестановки разрешены и как потоки синхронизируются. "
            "Каждая атомарная операция принимает параметр `Ordering` с ограничениями "
            "на переупорядочивание."
        ),
        table(
            ["Ordering", "Для каких операций", "Что запрещает", "Когда применять"],
            [
                ["`Relaxed`", "любые", "ничего, гарантирует только атомарность", "счётчики, статистика, флаги без данных"],
                ["`Release`", "запись (`store`, успешный CAS)", "переносит предыдущие записи за барьер", "публикация данных для читателя"],
                ["`Acquire`", "чтение (`load`, успешный CAS)", "переносит последующие чтения и записи перед барьером", "получение опубликованных данных"],
                ["`AcqRel`", "RMW (`fetch_add`, `swap`)", "и Acquire, и Release одновременно", "обновление, которое и читает, и публикует"],
                ["`SeqCst`", "любые", "дополнительно единый глобальный порядок", "когда нужна согласованность нескольких атомиков"],
            ],
        ),
        text(
            "Работает это так: запись с `Release` — «отпускание», а чтение того же "
            "атомика с `Acquire`, увидевшее её, — «захват». Между ними возникает "
            "отношение happens-before: всё, что писатель записал до `Release`, видно "
            "читателю после `Acquire`. Если для флага готовности взять `Relaxed` с двух "
            "сторон, читатель вправе увидеть флаг раньше содержимого буфера."
        ),
        example(
            "rust",
            """
            use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
            use std::thread;
            use std::time::Duration;

            static DATA: AtomicU64 = AtomicU64::new(0);
            static READY: AtomicBool = AtomicBool::new(false);

            fn main() {
                let writer = thread::spawn(|| {
                    DATA.store(0xDEAD_BEEF, Ordering::Relaxed);   // данные
                    READY.store(true, Ordering::Release);         // публикация
                });

                let reader = thread::spawn(|| {
                    while !READY.load(Ordering::Acquire) {
                        std::hint::spin_loop();
                    }
                    let value = DATA.load(Ordering::Relaxed);     // Acquire после Release
                    println!("прочитано: 0x{:X}", value);
                });

                writer.join().unwrap();
                reader.join().unwrap();
                let _ = Duration::from_millis(1);
            }
            """,
        ),
        text(
            "Вывод: `прочитано: 0xDEADBEEF`. Пары `Release` — `Acquire` на `READY` "
            "достаточно, чтобы `DATA`, записанное обычным `Relaxed`, стало видимым. "
            "`SeqCst` здесь не нужен: он добавил бы глобальный порядок всем атомикам "
            "программы, а связать надо только два места."
        ),
        callout(
            "warning",
            "Типичная ошибка с Relaxed",
            "Флаг, который «разрешает» чтение других данных, обязан быть парой "
            "`Release`/`Acquire`. Если чтение данных тоже сделать `Relaxed`, "
            "race-free не гарантируется: получится гонка данных, а не просто "
            "неожиданное значение. Ослаблять порядок можно только после доказательства, "
            "что данные не переставляются."
        ),
        heading("Счётчик ссылок и почему inc_relaxed корректен"),
        text(
            "Устройство `Arc` — пример разных требований к каждому `Ordering`. Внутри "
            "структура с сильным и слабым счётчиками и значением. Увеличение сильного "
            "счётчика делается `Relaxed`: поток уже владеет ссылкой, объект жив, нужна "
            "лишь атомарная арифметика. Уменьшение — `Release`: последняя ссылка должна "
            "дождаться завершения всех записей в значение. Чтение до нуля — `Acquire`, "
            "чтобы видеть записи предыдущих владельцев."
        ),
        example(
            "rust",
            """
            use std::sync::atomic::{fence, AtomicUsize, Ordering};

            struct Handle {
                strong: AtomicUsize,
            }

            impl Handle {
                fn new() -> Self {
                    Handle { strong: AtomicUsize::new(1) }
                }

                /// Клонирование: нужна только атомарность.
                fn clone_handle(&self) {
                    self.strong.fetch_add(1, Ordering::Relaxed);
                }

                /// Возвращает true, если это была последняя ссылка.
                fn drop_handle(&self) -> bool {
                    if self.strong.fetch_sub(1, Ordering::Release) != 1 {
                        return false;
                    }
                    // Последний владелец: дожидаемся всех записей перед разрушением
                    fence(Ordering::Acquire);
                    true
                }
            }

            fn main() {
                let h = Handle::new();
                h.clone_handle();
                println!("после клона: {}", h.strong.load(Ordering::Relaxed));
                println!("удалить: {}", h.drop_handle());
                println!("удалить: {}", h.drop_handle());
                println!("счётчик: {}", h.strong.load(Ordering::Relaxed));
                h.strong.store(1, Ordering::Relaxed);
            }
            """,
        ),
        text(
            "Вывод: `после клона: 2`, `удалить: false`, `удалить: true`, `счётчик: 0`. "
            "Форма `fetch_sub(Release)` с последующим `fence(Acquire)` — это идиома "
            "«уменьшить и проверить», которую используют вместо `AcqRel` в горячем "
            "пути: `AcqRel` на каждом уменьшении был бы дороже. Сброс в конце "
            "проведён отдельно, чтобы объект оставался в состоянии, пригодном для "
            "дорогого освобождения (в примере объект хранится на стеке)."
        ),
        heading("Lock-free стек и проблема ABA"),
        text(
            "Классический пример неблокирующей структуры — стек Трейбера: указатель на "
            "голову хранится в `AtomicPtr`, добавление узла — цикл со считыванием "
            "головы и `compare_exchange`, снимающее значение — тоже. Если между "
            "чтением и заменой кто-то успел изменить голову, сравнение не пройдёт и "
            "поток повторит попытку. Проблема в том, что сравнение проверяет только "
            "адрес.\n\n"
            "Предположим, поток A читает «голова — адрес X, следующий — Y». Пока A "
            "готовится к замене, поток B снимает X, затем Y, затем добавляет новый узел, "
            "и менеджер памяти выдаёт этому узлу тот же адрес X. A успешно заменяет "
            "голову на Y, хотя Y уже освобождён, а стек изменился. Это и есть "
            "**проблема ABA**: значение совпало, но состояние другое."
        ),
        table(
            ["Подход", "Как решает", "Ограничения"],
            [
                ["Тегированный указатель", "пересчитывается в пару «адрес + версия» каждым изменением", "CAS остаётся атомарным только если пара помещается в машинное слово"],
                ["Hazard pointers", "поток публикует адрес, который читает, удаление ждёт их снятия", "своя инфраструктура и стоимость на каждой операции"],
                ["Epoch-based reclamation", "удаление отложено до выхода всех потоков из эпохи", "память освобождается с задержкой"],
            ],
        ),
        text(
            "Демонстрация самого цикла CAS без освобождения памяти: узлы выделены "
            "навсегда, поэтому проблема ABA здесь не проявляется — так упрощают "
            "учебный код, чтобы сосредоточиться на логике."
        ),
        example(
            "rust",
            """
            use std::ptr;
            use std::sync::atomic::{AtomicPtr, Ordering};

            struct Node {
                value: u32,
                next: *mut Node,
            }

            struct Stack {
                head: AtomicPtr<Node>,
            }

            impl Stack {
                fn new() -> Self {
                    Stack { head: AtomicPtr::new(ptr::null_mut()) }
                }

                fn push(&self, value: u32) {
                    let node = Box::into_raw(Box::new(Node { value, next: ptr::null_mut() }));
                    loop {
                        let head = self.head.load(Ordering::Acquire);
                        unsafe { (*node).next = head };
                        match self.head.compare_exchange_weak(
                            head, node, Ordering::Release, Ordering::Acquire,
                        ) {
                            Ok(_) => return,
                            Err(_) => continue,  // конкурент успел первым
                        }
                    }
                }

                fn pop(&self) -> Option<u32> {
                    loop {
                        let head = self.head.load(Ordering::Acquire);
                        if head.is_null() {
                            return None;
                        }
                        let next = unsafe { (*head).next };
                        match self.head.compare_exchange_weak(
                            head, next, Ordering::AcqRel, Ordering::Acquire,
                        ) {
                            Ok(_) => {
                                let node = unsafe { Box::from_raw(head) };
                                return Some(node.value);
                            }
                            Err(_) => continue,
                        }
                    }
                }
            }

            fn main() {
                let stack = Stack::new();
                stack.push(1);
                stack.push(2);
                stack.push(3);
                println!("{:?}", stack.pop());
                println!("{:?}", stack.pop());
                println!("{:?}", stack.pop());
                println!("{:?}", stack.pop());
            }
            """,
        ),
        text(
            "Вывод: `Some(3)`, `Some(2)`, `Some(1)`, `None`. "
            "`compare_exchange_weak` может отказать даже при совпавшем значении, поэтому "
            "внешний цикл обязателен. Узлы здесь не возвращаются в систему — осознанное "
            "упрощение; настоящий стек требует и `crossbeam-epoch`, и защиты от ABA."
        ),
        callout(
            "warning",
            "Не строю CAS над AtomicPtr без схемы освобождения",
            "CAS над указателем сравнивает адреса, а не содержимое. Если узел успел "
            "освободиться и адрес повторно выдан, CAS сочтёт состояние прежним. "
            "До сих пор безопасны только два случая: узлы не освобождаются никогда "
            "либо освобождение отложено через `defer_destroy` или hazard pointers."
        ),
        heading("Epoch-based reclamation через crossbeam"),
        text(
            "`crossbeam-epoch` решает проблему освобождения памяти без собственного "
            "аллокатора. У каждого потока есть счётчик эпох. Читатель входит в "
            "критическую секцию через `guard` и помечает текущую эпоху как активную. "
            "Удалённый узел попадает в очередь отложенного удаления и освобождается, "
            "только когда все потоки покинули эпоху, в которой он был доступен. "
            "Поэтому читатель не обращается к освобождённой памяти, а адрес не может "
            "быть выдан повторно.\n\n"
            "Тип `crossbeam_epoch::Atomic<T>` похож на указатель, но несёт теги эпох. "
            "`load(ordering, &guard)` возвращает `Shared`, живой, пока жив `guard`, а "
            "удаление делается через `guard.defer_destroy(shared)`."
        ),
        example(
            "toml",
            """
            [dependencies]
            crossbeam-epoch = "0.9"

            # cargo add crossbeam-epoch
            """,
        ),
        example(
            "rust",
            """
            use std::sync::atomic::Ordering;
            use crossbeam_epoch::{self as epoch, Atomic, Owned};

            struct Node {
                value: u32,
                next: Atomic<Node>,
            }

            struct TreiberStack {
                head: Atomic<Node>,
            }

            impl TreiberStack {
                fn new() -> Self {
                    TreiberStack { head: Atomic::null() }
                }

                fn push(&self, value: u32) {
                    let guard = &epoch::pin();
                    let node = Owned::new(Node { value, next: Atomic::null() });
                    let mut head = self.head.load(Ordering::Relaxed, guard);
                    loop {
                        node.next.store(head, Ordering::Relaxed);
                        match self.head.compare_exchange(
                            head, node, Ordering::Release, Ordering::Relaxed, guard,
                        ) {
                            Ok(_) => return,
                            Err(e) => head = e.current,
                        }
                    }
                }

                fn pop(&self) -> Option<u32> {
                    let guard = &epoch::pin();
                    let mut head = self.head.load(Ordering::Acquire, guard);
                    loop {
                        let node = unsafe { head.as_ref()? };
                        let next = node.next.load(Ordering::Acquire, guard);
                        match self.head.compare_exchange(
                            head, next, Ordering::AcqRel, Ordering::Acquire, guard,
                        ) {
                            Ok(_) => {
                                unsafe { guard.defer_destroy(head) };
                                let value = node.value;
                                return Some(value);
                            }
                            Err(e) => head = e.current,
                        }
                    }
                }
            }

            fn main() {
                let stack = TreiberStack::new();
                for v in 1..=4 {
                    stack.push(v);
                }
                let mut drained = Vec::new();
                while let Some(v) = stack.pop() {
                    drained.push(v);
                }
                println!("{:?}", drained);
                epoch::pin();
                println!("память освобождена после сбора");
            }
            """,
        ),
        text(
            "Вывод: `[4, 3, 2, 1]` и строка про освобождение памяти. После выхода всех "
            "`Guard` из области видимости узлы освобождаются. При неудаче "
            "`Owned` возвращается в ошибке `e.new`, поэтому повтор использует тот же "
            "узел. `defer_destroy` откладывает освобождение до выхода `guard` "
            "последнего читателя. `as_ref()` на `Atomic::null` даёт `None`, так что "
            "`?` корректно завершает `pop` на пустом стеке."
        ),
        callout(
            "info",
            "Цена epoch-based reclamation",
            "Память освобождается с задержкой: если читатель задержался в критической "
            "секции, освобождение откладывается, и потребление памяти растёт. Поэтому "
            "`Guard` держат коротко и не удерживают при блокирующих операциях."
        ),
        heading("parking_lot: быстрые примитивы на замену std"),
        text(
            "Во многих прикладных случаях lock-free избыточен: мьютекс, который почти "
            "никогда не удерживается, дешевле и понятнее. Крейт `parking_lot` заменяет "
            "`std::sync::Mutex` и `RwLock`, устраняя несколько недостатков стандартных "
            "типов. В неконкурентном режиме захват не обращается к ядру ОС. `lock()` "
            "не возвращает `Result`: ядовитости блокировки нет, тип остаётся валидным "
            "даже после паники в критической секции. `RwLock` поддерживает честный "
            "режим, где писатель не голодает из-за потока читателей."
        ),
        table(
            ["Возможность", "std", "parking_lot"],
            [
                ["ядовитость", "`lock()` возвращает `LockResult`", "`lock()` отдаёт `MutexGuard`"],
                ["системный вызов при отсутствии конкуренции", "зависит от платформы", "не выполняется"],
                ["честный `RwLock`", "не гарантируется", "`RwLock::new_fair`"],
                ["`Condvar`", "связан с `std::sync::Mutex`", "работает с замком `parking_lot`"],
                ["объём типа", "больше", "один байт на мьютекс"],
            ],
        ),
        example(
            "rust",
            """
            use parking_lot::{Condvar, Mutex};
            use std::collections::VecDeque;
            use std::thread;
            use std::time::Duration;

            fn main() {
                let queue = Mutex::new(VecDeque::new());
                let available = Condvar::new();

                thread::scope(|s| {
                    s.spawn(|| {
                        let mut q = queue.lock();
                        q.push_back("job-1");
                        drop(q);
                        available.notify_one();
                    });

                    s.spawn(|| {
                        let mut q = queue.lock();
                        while q.is_empty() {
                            available.wait_for(&mut q, Duration::from_millis(500));
                        }
                        println!("получено: {:?}", q.pop_front());
                    });
                });
            }
            """,
        ),
        text(
            "Вывод: `получено: Some(\"job-1\")`. `wait_for` освобождает мьютекс на время "
            "ожидания и обязательно возвращает его перед `wait_for`. Условие "
            "`while q.is_empty()` — обязательный цикл, а не `if`: между пробуждением и "
            "повторным захватом замка другой поток мог забрать элемент, и ложное "
            "пробуждение не исключено. `notify_one` вызывается после `drop(q)`, чтобы "
            "разбуженный поток мог сразу захватить замок без лишнего переключения."
        ),
        heading("DashMap: словарь, шардированный по замкам"),
        text(
            "`DashMap` — реализация `HashMap`, которая изнутри разбита на несколько "
            "независимых шардов, каждый со своим `RwLock`. Ключ определяет шард по "
            "хешу, поэтому две операции с разными шардами не мешают друг другу: "
            "читатели и писатели работают параллельно, пока их ключи попадают в "
            "разные шарды. Это не lock-free, это мелкозернистая блокировка, и на "
            "практике она обгоняет `Mutex<HashMap>` на многопоточном коде почти без "
            "изменений в логике. Число шардов по умолчанию — 32, его можно задать "
            "через `with_shard_amount`. Поскольку `DashMap` создаёт внутренние "
            "блокировки, для общего владения между потоками достаточно `&DashMap`, "
            "`Arc` не обязателен внутри `thread::scope`."
        ),
        example(
            "rust",
            """
            use dashmap::DashMap;
            use std::thread;

            fn main() {
                let words: DashMap<&str, usize> = DashMap::with_shard_amount(64);

                let text = "lock free stack lock free queue stack";

                thread::scope(|s| {
                    for chunk in text.split(' ') {
                        s.spawn(|| {
                            *words.entry(chunk).or_insert(0) += 1;
                        });
                    }
                });

                let mut counts: Vec<(&&str, usize)> =
                    words.iter().map(|e| (e.key(), *e.value())).collect();
                counts.sort();
                for (word, n) in counts {
                    println!("{}: {}", word, n);
                }
                println!("шардов: {}", words.shards().len());
            }
            """,
        ),
        text(
            "Вывод: `free: 1`, `lock: 2`, `queue: 1`, `stack: 2`, `шардов: 64`. Метод "
            "`entry` берёт замок на нужный шард и позволяет менять значение через "
            "`Entry` без лишнего поиска. `DashMap` держит замок на шард, пока жив "
            "результат `iter()` или `Entry`; обращение к тому же шарду внутри этой "
            "области даёт дедлок, поэтому итерацию копируют в вектор."
        ),
        callout(
            "info",
            "Когда DashMap не нужен",
            "Если записей мало и они обновляются редко, а чтений много, выгоднее "
            "`RwLock<HashMap>` или RCU-паттерн: `DashMap` тратит память на шарды, и на "
            "маленьких словарях расходы перевешивают выигрыш."
        ),
        heading("RCU: копируй, изменяй, подменяй указатель"),
        text(
            "Read-Copy-Update (RCU) — паттерн для данных, которые читаются часто, а "
            "обновляются редко: конфигурации, таблицы маршрутов, индексы кэша. Читатель "
            "не берёт замков: он атомарно загружает указатель на текущую версию. "
            "Писатель создаёт копию, изменяет её и подменяет указатель, поэтому запись "
            "длится ровно столько, сколько занимает подмена. Старая версия освобождается "
            "после периода «тишины», когда читателей из старой эпохи гарантированно нет; "
            "для этого `crossbeam-epoch` и создан."
        ),
        example(
            "rust",
            """
            use std::collections::HashMap;
            use std::sync::atomic::{AtomicUsize, Ordering};

            struct RcuMap {
                generation: AtomicUsize,
                current: std::sync::Mutex<HashMap<String, u32>>,
            }

            impl RcuMap {
                fn new() -> Self {
                    RcuMap {
                        generation: AtomicUsize::new(1),
                        current: std::sync::Mutex::new(HashMap::new()),
                    }
                }

                fn read(&self, key: &str) -> Option<u32> {
                    let generation = self.generation.load(Ordering::Acquire);
                    let map = self.current.lock().unwrap();
                    let value = map.get(key).copied();
                    debug_assert_eq!(generation, 1);
                    value
                }

                fn publish(&self, key: &str, value: u32) {
                    let mut map = self.current.lock().unwrap();
                    let mut copy = map.clone();          // копия, а не правка на месте
                    copy.insert(key.to_string(), value);
                    *map = copy;                         // подмена за O(1)
                    self.generation.fetch_add(1, Ordering::Release);
                }
            }

            fn main() {
                let map = RcuMap::new();
                map.publish("timeout", 30);
                println!("timeout = {:?}", map.read("timeout"));
                println!("поколение = {}", map.generation.load(Ordering::Relaxed));
            }
            """,
        ),
        text(
            "Вывод: `timeout = Some(30)`, `поколение = 2`. Читатель только читает и "
            "не мешает другим читателям. Обновление под замком создаёт копию и "
            "подменяет содержимое, поэтому вставка не влияет на идущие чтения. "
            "В высоконагруженной системе вместо клонирования берут иммутабельный снимок "
            "(`Arc<HashMap>`) и подменяют его атомарно, а освобождение старого снимка "
            "доверяют epoch-based reclamation."
        ),
        callout(
            "warning",
            "RCU не бесплатен",
            "Полная копия при каждой записи даёт O(n) на запись и память под старые "
            "версии. Если данные обновляются часто, RCU проигрывает мьютексу или "
            "`DashMap`: паттерн выбирают под профиль «редкая запись, много чтений»."
        ),
        heading("Каналы и очереди crossbeam"),
        text(
            "`crossbeam-channel` и `crossbeam-queue` дают обмен сообщениями без замков "
            "на горячем пути. `bounded(n)` — ограниченный канал с обратным давлением: "
            "отправитель засыпает на полном буфере. `unbounded()` не блокирует, но "
            "позволяет очереди расти без предела. Макрос `select!` ждёт несколько "
            "каналов сразу, включая режим `default` для неблокирующей проверки.\n\n"
            "`SegQueue` — неограниченная очередь для многих производителей и "
            "потребителей, `ArrayQueue` — ограниченная очередь, где `push` возвращает "
            "`Err(item)` при переполнении."
        ),
        example(
            "rust",
            """
            use crossbeam_channel::{bounded, select, Receiver};
            use crossbeam_queue::ArrayQueue;
            use std::sync::Arc;

            fn drain_first(rx_a: &Receiver<&str>, rx_b: &Receiver<&str>) {
                loop {
                    select! {
                        recv(rx_a) -> msg => match msg {
                            Ok(v) => println!("канал A: {}", v),
                            Err(_) => break,
                        },
                        recv(rx_b) -> msg => match msg {
                            Ok(v) => println!("канал B: {}", v),
                            Err(_) => break,
                        },
                        default => {
                            println!("оба канала пусты");
                            break;
                        }
                    }
                }
            }

            fn main() {
                let (tx_a, rx_a) = bounded(4);
                let (tx_b, rx_b) = bounded(4);
                tx_a.send("task-1").unwrap();
                tx_b.send("task-2").unwrap();
                drop(tx_a);
                drop(tx_b);
                drain_first(&rx_a, &rx_b);

                let queue = Arc::new(ArrayQueue::new(2));
                queue.push(10).unwrap();
                queue.push(20).unwrap();
                println!("push в полную очередь: {:?}", queue.push(30));
                println!("извлечено: {:?}", queue.pop());
            }
            """,
        ),
        text(
            "Вывод: `канал A: task-1`, `канал B: task-2`, `оба канала пусты`, "
            "`push в полную очередь: Err(30)`, `извлечено: Some(10)`. `select!` берёт "
            "первый готовый канал, а после закрытия отправителей `recv` вернёт `Err`. "
            "`ArrayQueue` при переполнении возвращает значение обратно — явный отказ "
            "вместо скрытого роста памяти."
        ),
        heading("loom: перебор возможных чередований"),
        text(
            "Ошибки с `Ordering` проявляются раз в миллион запусков и обычно на другой "
            "архитектуре. Модель-чекер `loom` перебирает допустимые варианты "
            "чередования атомарных операций по модели памяти Rust и падает с "
            "трассировкой сценария.\n\n"
            "Внутри используют замены примитивов `loom::sync::atomic::AtomicUsize`, "
            "`loom::sync::Mutex`, `loom::thread`, а тело сценария помещают в "
            "`loom::model(|| { ... })`. Вариантов экспоненциально много, поэтому "
            "сценарий должен быть маленьким."
        ),
        example(
            "toml",
            """
            [dev-dependencies]
            loom = "0.7"

            # cargo test --features loom, либо просто тест на loom
            """,
        ),
        example(
            "rust",
            """
            use loom::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
            use loom::sync::Arc;
            use loom::thread;

            #[test]
            fn publish_then_read() {
                loom::model(|| {
                    let data = Arc::new(AtomicUsize::new(0));
                    let ready = Arc::new(AtomicBool::new(false));

                    let writer = {
                        let data = data.clone();
                        let ready = ready.clone();
                        thread::spawn(move || {
                            data.store(7, Ordering::Relaxed);
                            ready.store(true, Ordering::Release);
                        })
                    };

                    let reader = {
                        let data = data.clone();
                        let ready = ready.clone();
                        thread::spawn(move || {
                            while !ready.load(Ordering::Acquire) {
                                thread::yield_now();
                            }
                            // Release/Acquire гарантирует, что data видна
                            assert_eq!(data.load(Ordering::Relaxed), 7);
                        })
                    };

                    writer.join().unwrap();
                    reader.join().unwrap();
                });
            }
            """,
        ),
        text(
            "Запуск: `cargo test`. Loom перебирает все допустимые чередования и "
            "проверяет утверждение в каждом. Замените `Release` на `Relaxed` — и тест "
            "начнёт падать на варианте, где читатель видит `ready == true` раньше "
            "записи данных. Обычный запуск такой баг почти наверняка пропустил бы."
        ),
        callout(
            "success",
            "Практика с loom",
            "Пишите под loom только критическую часть: цикл проверки флага, смену "
            "указателя, счётчик ссылок. Каждое дополнительное ветвление в тесте "
            "умножает число вариантов. Для очень больших графов используйте "
            "переменную окружения `LOOM_MAX_PREEMPTIONS`, чтобы ограничить глубину "
            "переключений."
        ),
        heading("Wait-free счётчики и локальные буферы"),
        text(
            "Wait-free гарантии иногда достигают не алгоритмом, а сменой архитектуры "
            "данных: вместо общей ячейки каждый поток владеет своей. Массив "
            "`AtomicUsize` по одному на поток даёт wait-free инкремент: `fetch_add` по "
            "собственному индексу ни с кем не конфликтует, а сумма считается "
            "агрегацией. Так устроены счётчики в планировщиках и сборщиках мусора.\n\n"
            "Цена — отклонение от точного значения в промежутке и требование знать "
            "число потоков заранее. Если потоков больше, чем ячеек, индекс берут по "
            "`id % counters.len()`, и wait-free свойство уже не гарантируется."
        ),
        example(
            "rust",
            """
            use std::sync::atomic::{AtomicUsize, Ordering};
            use std::thread;

            struct StripedCounter {
                counters: Vec<AtomicUsize>,
            }

            impl StripedCounter {
                fn new(shards: usize) -> Self {
                    StripedCounter {
                        counters: (0..shards).map(|_| AtomicUsize::new(0)).collect(),
                    }
                }

                fn increment(&self, id: usize) {
                    self.counters[id % self.counters.len()]
                        .fetch_add(1, Ordering::Relaxed);
                }

                fn total(&self) -> usize {
                    self.counters.iter().map(|c| c.load(Ordering::Relaxed)).sum()
                }
            }

            fn main() {
                let counter = StripedCounter::new(4);
                thread::scope(|s| {
                    for id in 0..4 {
                        s.spawn(|| {
                            for _ in 0..1000 {
                                counter.increment(id);
                            }
                        });
                    }
                });
                println!("сумма: {}", counter.total());
            }
            """,
        ),
        text(
            "Вывод: `сумма: 4000`. Каждый поток пишет только в свою ячейку, поэтому "
            "ложное разделение (false sharing) — единственный физический конкурент: "
            "если две ячейки попадают в одну кэш-линию, процессоры всё равно "
            "перебрасывают линию между ядрами. В высоконагруженных счётчиках ячейки "
            "выравнивают по 64 байтам (кэш-линия). `Ordering::Relaxed` здесь корректен: "
            "промежуточное значение не является инвариантом, важна лишь итоговая сумма."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["`Relaxed` на флаге готовности", "читатель видит флаг раньше данных, гонка данных", "пара `Release`/`Acquire` на флаге"],
                ["Ожидание `compare_exchange_weak` без цикла", "отказ трактуется как реальная неудача, изменение теряется", "оборачивать в `loop` и повторять при `Err`"],
                ["CAS над указателем без защиты от освобождения", "ABA: адрес повторно выдан, CAS проходит на чужой узел", "`defer_destroy`, hazard pointers или тег версии"],
                ["Долгое удержание `Guard`", "отложенное освобождение задерживается, память растёт", "входить в epoch на короткую операцию"],
                ["Дедлок при итерации `DashMap`", "внутри области `iter()` захватывается тот же шард", "копировать данные и отпускать область"],
                ["`if` вместо `while` у `Condvar::wait`", "ложное пробуждение без данных", "проверять условие в цикле"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняются в отдельном корневом крейте (`cargo init lesson`). "
            "Проверяйте каждое решение `cargo test` и, где указано, `cargo clippy -- "
            "-D warnings`. Для loom добавляйте `loom` в `dev-dependencies`."
        ),
        numbered(
            "Реализуйте `StripedCounter` на 8 ячеек и напишите тест, который после `thread::scope` проверяет точную сумму 80 000. Измените `Ordering` на `SeqCst` и объясните, почему результат не изменился.",
            "Соберите lock-free стек по алгоритму Трейбера на `AtomicPtr` без освобождения памяти. Добавьте `pop`, `push`, `len` через отдельный `AtomicUsize` и проверьте, что порядок при `drain` обратный порядку вставки.",
            "Перепишите тот же стек на `crossbeam-epoch` с `defer_destroy` и прогоните 4 потока по 1000 операций. Затем ускоряйте `pop`: возьмите `Acquire` на чтение головы и `AcqRel` на CAS и поясните, зачем порядки различаются.",
            "Возьмите пример с флагом `READY` и замените пару `Release`/`Acquire` на `Relaxed` с двух сторон. Напишите тест на loom, докажите, что утверждение может нарушиться, и верните корректные порядки.",
            "Соберите небольшой сервис конфигурации: `DashMap` хранит значение, раз в секунду поток-читатель запрашивает его, а поток-обновление вносит 100 изменений. Измерьте, сколько чтений успевает первый поток, и сравните с `RwLock<HashMap>`.",
        ),
        text(
            "Пример ожидаемого вывода для первого задания:",
        ),
        example(
            "text",
            """
            running 1 test
            test counter_stays_exact ... ok

            test result: ok. 1 passed; 0 failed
            сумма: 80000
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 3",
            "`pop` публикует новую голову (`AcqRel`) и одновременно читает её (`Acquire`), "
            "потому что дальнейшая работа идёт с новой головой. `push` только публикует "
            "узел (`Release`), а голова читается без последствий для `Relaxed`: "
            "узел ещё не доступен другим потокам."
        ),
        *check_yourself(
            (
                "Чем lock-free отличается от wait-free?",
                "Что гарантирует пара `Release`/`Acquire` и на каком объекте она строится?",
                "Почему простой CAS над `AtomicPtr` подвержен проблеме ABA?",
                "Как `crossbeam-epoch` защищает от использования освобождённой памяти?",
                "Почему в `Arc` клонирование счётчика делается `Relaxed`, а уменьшение — `Release`?",
                "Что проверяет `loom::model` и почему под него пишут маленькие сценарии?",
            ),
            (
                "Lock-free гарантирует прогресс системы: хотя бы один поток завершает шаг. Wait-free строже: каждый поток завершает шаг за ограниченное число операций, даже при конкуренции.",
                "Пара связывает запись и чтение одного атомика: данные, записанные до `Release`, становятся видимы после `Acquire`, который увидел то же значение.",
                "CAS сравнивает только адрес. Узел может освободиться, а новый узел получить тот же адрес — CAS пройдёт, хотя структура изменилась.",
                "Читатель входит в эпоху через `Guard`, удалённые узлы помещаются в очередь отложенного удаления и освобождаются только после выхода всех читателей из их эпох.",
                "Клонирование уже имеет живую ссылку, нужна только атомарность. Уменьшение должно опубликовать все предыдущие записи в данные, чтобы последний владелец увидел завершённое состояние.",
                "`loom::model` перебирает допустимые чередования атомарных операций и проверяет утверждение на каждом. Каждая дополнительная операция и поток экспоненциально умножают число вариантов, поэтому сценарий должен быть маленьким.",
            ),
        ),
        *outro(
            (
                "Уровни прогресса: obstruction-free слабее lock-free, lock-free слабее wait-free. Уровень выбирают по профилю нагрузки, а не по моде.",
                "`Ordering` подбирают по данным: `Relaxed` для статистики, `Release` для публикации, `Acquire` для получения, `AcqRel` для RMW, `SeqCst` для глобального порядка.",
                "CAS над указателем требует защиты от ABA: тег версии, hazard pointers или epoch-based reclamation.",
                "`crossbeam_epoch` с `Guard` и `defer_destroy` безопасно освобождает память в неблокирующих структурах с задержкой.",
                "`parking_lot` даёт быстрые примитивы без ядовитости, `DashMap` — шардированный словарь, RCU — паттерн «копируй, изменяй, подменяй».",
                "`loom` перебирает чередования и ловит ошибки в `Ordering`, которые почти невозможно поймать обычным запуском.",
            ),
            "Дальше логично перейти к макросам: декларативные `macro_rules!` и процедурные макросы "
            "нужны, чтобы избежать дублирования в структурах, подобных `select!` и `Arc`-обёрткам. "
            "Отдельно стоит закрепить профилирование: неблокирующие структуры не всегда быстрее, и "
            "решение принимают по замерам, а не по названию алгоритма.",
            (
                "Crossbeam: репозитории `crossbeam-rs/crossbeam`, документация `crossbeam-epoch` — docs.rs/crossbeam-epoch",
                "parking_lot: репозиторий `Amanieu/parking_lot` и документация docs.rs/parking_lot",
                "DashMap: репозиторий `xacrimon/dashmap` и документация docs.rs/dashmap",
                "Loom: репозиторий `tokio-rs/loom` и примеры модель-чекера",
                "Rust Atomics and Locks, Mara Bos: главы про атомики, порядки и модель памяти",
                "The Rustonomicon: раздел «Atomics» и документация `std::sync::atomic`",
            ),
        ),
    ],
}
