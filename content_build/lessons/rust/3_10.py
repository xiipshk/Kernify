"""Урок 3.10 курса Rust: производительность и надёжность."""

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
    "topic_order": 10,
    "name": "3.10. Производительность и надёжность",
    "slug": "rust-3-10-производительность-и-надёжность",
    "short_description": (
        "Бенчмарки с Criterion, профилирование аллокаций и CPU, проверка unsafe-кода "
        "через Miri и Loom, фаззинг с cargo-fuzz и property-тесты с proptest — "
        "и всё это в непрерывной интеграции."
    ),
    "topic_name": "Производительность и надёжность",
    "topic_description": (
        "Урок о том, как измерить и защитить код: статистически корректные бенчмарки Criterion, "
        "поиск узких мест по аллокациям и профилям CPU, проверка неопределённого поведения "
        "интерпретатором Miri, моделирование переключений потоков в Loom, автоматический поиск "
        "паник через фаззинг и проверка инвариантов на случайных данных в proptest."
    ),
    "learning_objectives": [
        "Настраивать Criterion в Cargo.toml и писать бенчмарки с black_box, группами и параметрами",
        "Сохранять базовые результаты бенчмарков и сравнивать с ними регрессии в CI",
        "Читать профили аллокаций и CPU: heaptrack, dhat, massif, cargo-flamegraph, замена глобального аллокатора",
        "Находить неопределённое поведение в unsafe-коде с помощью cargo miri test и объяснять его ограничения",
        "Моделировать конкурентный код в loom::model и проверять инварианты при всех перестановках",
        "Настраивать цели cargo-fuzz с arbitrary и писать property-тесты на proptest с narrowing стратегий",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "rust",
        "бенчмарки",
        "профилирование",
        "miri",
        "фаззинг",
        "property-тесты",
    ],
    "starter_code": code(
        r"""
        // benches/parse.rs — каркас бенчмарка Criterion.
        //
        // Cargo.toml:
        // [dev-dependencies]
        // criterion = "0.5"
        //
        // [[bench]]
        // name = "parse"
        // harness = false

        use criterion::{black_box, criterion_group, criterion_main, Criterion};

        fn sum_loop(input: &[u32]) -> u64 {
            let mut total = 0u64;
            for &value in input {
                total += value as u64;
            }
            total
        }

        fn sum_iter(input: &[u32]) -> u64 {
            input.iter().map(|&value| value as u64).sum()
        }

        fn benchmark(c: &mut Criterion) {
            let data: Vec<u32> = (0..10_000).collect();

            let mut group = c.benchmark_group("sum");
            group.bench_function("loop", |b| {
                b.iter(|| sum_loop(black_box(&data)))
            });
            group.bench_function("iter", |b| {
                b.iter(|| sum_iter(black_box(&data)))
            });
            group.finish();
        }

        criterion_group!(benches, benchmark);
        criterion_main!(benches);
        """
    ),
    "hints": [
        "Если бенчмарк показывает время около нуля наносекунд, компилятор вычислил результат заранее. Оберните входные данные в black_box, а результат передайте в black_box перед возвратом.",
        "Miri не умеет работать с FFI и медленный. Выносите границу с внешним C-кодом за пределы тестов, которые прогоняются под Miri, и оставляйте там только чистую логику.",
        "В Loom начинайте с двух потоков и одной операции. Если модель взрывается по числу состояний, уменьшайте число потоков, итераций и ветвлений, а не увеличивайте таймауты.",
        "Property-тест падает на редком значении — это не повод отключать тест. Зафиксируйте seed из сообщения об ошибке и сузьте стратегию, чтобы вход был осмысленным.",
    ],
    "content": [
        text(
            "Код, который компилируется и проходит тесты, ещё не считается готовым: он может "
            "быть медленным, может случайно выделять память на каждом шаге, а в `unsafe`-блоке "
            "может прятаться поведение, на которое компилятор имеет право реагировать как угодно. "
            "Уровень 3 требует не веры, а измерений — и инструменты Rust-экосистемы позволяют "
            "получить эти измерения.\n\n"
            "В этом уроке вы пройдёте путь от бенчмарка до непрерывной интеграции. Сначала научитесь "
            "честно измерять время с Criterion, затем разберётесь, где уходит память и процессорное "
            "время, после чего займётесь надёжностью: Miri ищет неопределённое поведение в "
            "интерпретаторе, Loom перебирает межпоточные переключения, фаззинг генерирует "
            "злонамеренный ввод, а property-тесты проверяют инварианты на случайных данных.\n\n"
            "Ключевая мысль: каждый инструмент отвечает на свой вопрос. Criterion говорит «стало ли "
            "медленнее», профилировщик — «где именно», Miri — «допустим ли этот код», фаззинг — "
            "«падает ли он на мусоре»."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "настраивать Criterion в `Cargo.toml` и писать бенчмарки с `black_box`, группами и параметрами;",
            "сохранять базовые замеры (`--save-baseline`) и сравнивать с ними регрессии перед мёржем;",
            "читать профили аллокаций и CPU: `heaptrack`, `dhat`, `valgrind --tool=massif`, `cargo flamegraph`;",
            "менять глобальный аллокатор на `tikv-jemallocator` или `mimalloc` и измерять эффект;",
            "находить неопределённое поведение в `unsafe`-коде с `cargo miri test` и понимать ограничения Miri;",
            "моделировать конкурентный код в `loom::model` и проверять инварианты при всех перестановках;",
            "писать цели фаззинга `cargo-fuzz` и извлекать структурированный ввод через `arbitrary`;",
            "формулировать свойства и писать property-тесты на `proptest`, включая стратегии и shrinking.",
        ),
        heading("Бенчмарки с Criterion"),
        text(
            "Встроенный `#[bench]` требует ночного компилятора, поэтому стандартом де-факто стал "
            "Criterion: он работает на стабильном Rust, делает разогрев, несколько независимых "
            "выборок, считает доверительные интервалы и строит HTML-отчёт. Бенчмарк — это не "
            "«измерить один раз», а статистическая процедура.\n\n"
            "Criterion подключается как dev-зависимость, а цель бенчмарка объявляется в манифесте "
            "с обязательным `harness = false`: собственный тестовый рантайм Rust в этом режиме "
            "отключается, и точкой входа становится `criterion_main!`. Без `harness = false` "
            "`cargo bench` просто не увидит ваш файл."
        ),
        example(
            "toml",
            """
            [dev-dependencies]
            criterion = { version = "0.5", features = ["html_reports"] }

            [[bench]]
            name = "parse"
            harness = false
            """,
        ),
        text(
            "Минимальный бенчмарк состоит из четырёх частей: функция-замер, `criterion_group!` "
            "с перечнем функций и `criterion_main!`. Внутри используется `b.iter(|| ...)` — "
            "Criterion сам подберёт число итераций, чтобы выбрать время замера.\n\n"
            "Отдельного внимания заслуживает `black_box`. Это функция, которая для компилятора "
            "выглядит как «чёрный ящик»: он не знает, что она делает со значением, поэтому не "
            "может ни свернуть вычисление констант, ни удалить результат как неиспользуемый. "
            "Оборачивать нужно и вход, и результат."
        ),
        example(
            "rust",
            """
            use criterion::{black_box, criterion_group, criterion_main, Criterion};

            fn fibonacci(n: u64) -> u64 {
                match n {
                    0 => 0,
                    1 => 1,
                    _ => fibonacci(n - 1) + fibonacci(n - 2),
                }
            }

            fn benchmark(c: &mut Criterion) {
                c.bench_function("fibonacci 20", |b| {
                    b.iter(|| black_box(fibonacci(black_box(20))))
                });
            }

            criterion_group!(benches, benchmark);
            criterion_main!(benches);
            """,
        ),
        text(
            "Вывод: cargo bench запускает замер и печатает оценку времени одной итерации вида "
            "«fibonacci 20  time: [26.1 ms 26.4 ms 26.8 ms]», после чего сохраняет HTML-отчёт "
            "в target/criterion/."
        ),
        heading("Группы, параметры и сравнение реализаций", 3),
        text(
            "На практике нужен не один замер, а сравнение. Группа (`benchmark_group`) объединяет "
            "несколько функций под общим именем и позволяет задать параметры: `sample_size` — "
            "число независимых выборок, `warm_up_time` — время разогрева, `measurement_time` — "
            "длительность измерения. Для алгоритмов, чувствительных к размеру входа, "
            "используйте `bench_with_input`, чтобы не писать бенчмарк для каждого размера "
            "руками.\n\n"
            "Обратите внимание на клонирование внутри замыкания: если сортировка должна "
            "работать на каждый замер с одной и той же исходной последовательностью, копию "
            "нужно создавать внутри `iter`. Иначе второй замер будет сортировать уже "
            "отсортированный массив и покажет нереалистично хорошее время."
        ),
        example(
            "rust",
            """
            use criterion::{black_box, criterion_group, criterion_main, Criterion};
            use std::time::Duration;

            fn benchmark_sort(c: &mut Criterion) {
                let mut group = c.benchmark_group("sort");
                group.sample_size(100);
                group.warm_up_time(Duration::from_millis(200));
                group.measurement_time(Duration::from_secs(3));

                for size in [100usize, 1_000, 10_000] {
                    let source: Vec<i32> = (0..size as i32).rev().collect();
                    group.bench_with_input(format!("vec_{size}"), &source, |b, data| {
                        b.iter(|| {
                            let mut copy = data.clone();
                            copy.sort_unstable();
                            black_box(copy)
                        })
                    });
                }
                group.finish();
            }

            criterion_group!(benches, benchmark_sort);
            criterion_main!(benches);
            """,
        ),
        text(
            "Вывод: sort/vec_100  time: [412.7 ns 414.9 ns 417.6 ns], "
            "sort/vec_1000  time: [5.482 us 5.511 us 5.546 us], "
            "sort/vec_10000  time: [71.21 us 71.88 us 72.63 us] — рост чуть быстрее линейного, "
            "что ожидаемо для алгоритма с логарифмическим множителем."
        ),
        callout(
            "info",
            "Сравнение с базовой линией",
            "Перед изменениями сохраните базу: `cargo bench -- --save-baseline before`. После "
            "изменений выполните `cargo bench -- --baseline before`: Criterion напечатает "
            "«change: [...] +3.2% ... (p = 0.02)» и покажет, статистически ли значимо "
            "различие. Без базовой линии проценты сравнить не с чем."
        ),
        heading("Профилирование аллокаций и CPU"),
        text(
            "Бенчмарк отвечает на вопрос «сколько времени», но не на вопрос «куда оно ушло». "
            "Для второго вопроса нужны профилировщики. В Rust две главные категории затрат: "
            "время в процессоре (CPU-профиль) и работа аллокатора (выделение и освобождение "
            "памяти, копирование, фрагментация).\n\n"
            "Для CPU-профиля удобнее всего `cargo-flamegraph`: он собирает бинарь с отладочными "
            "символами в release-профиле, снимает стектрейсы через `perf` (Linux) или "
            "`dtrace` (macOS) и рисует SVG-«пламя», где ширина прямоугольника пропорциональна "
            "доле времени. Ищите самый широкий лист, съедающий время, и цепочку его вызывающих."
        ),
        example(
            "bash",
            """
            cargo install cargo-flamegraph

            # Включите символы для release-сборки:
            # [profile.release]
            # debug = 1

            cargo flamegraph --bin my_app -- --input data.bin

            # Результат: flamegraph.svg — откройте его в браузере.
            """,
        ),
        text(
            "`heaptrack` (Linux) запускает программу и сохраняет трассу каждого выделения, "
            "после чего `heaptrack --analyze` строит отчёт с деревом вызовов, пиковым "
            "потреблением и числом временных аллокаций. `valgrind --tool=massif` даёт "
            "график потребления во времени, а флаг `-Zdhat` у ночного компилятора — JSON "
            "для анализатора DHAT. На стабильном Rust проще собственный считающий аллокатор: "
            "он работает в CI и не требует внешних инструментов."
        ),
        example(
            "rust",
            """
            use std::alloc::{GlobalAlloc, Layout, System};
            use std::sync::atomic::{AtomicUsize, Ordering};

            struct Counting;

            static ALLOCATED: AtomicUsize = AtomicUsize::new(0);
            static CALLS: AtomicUsize = AtomicUsize::new(0);

            unsafe impl GlobalAlloc for Counting {
                unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
                    CALLS.fetch_add(1, Ordering::Relaxed);
                    ALLOCATED.fetch_add(layout.size(), Ordering::Relaxed);
                    System.alloc(layout)
                }

                unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
                    System.dealloc(ptr, layout)
                }
            }

            #[global_allocator]
            static GLOBAL: Counting = Counting;

            fn build_with_capacity(values: &[i32]) -> Vec<i32> {
                let mut result = Vec::with_capacity(values.len());
                for &value in values {
                    result.push(value * 2);
                }
                result
            }

            fn build_without_capacity(values: &[i32]) -> Vec<i32> {
                let mut result = Vec::new();
                for &value in values {
                    result.push(value * 2);
                }
                result
            }

            fn main() {
                let values: Vec<i32> = (0..1_000).collect();

                CALLS.store(0, Ordering::Relaxed);
                ALLOCATED.store(0, Ordering::Relaxed);
                let a = build_without_capacity(&values);
                println!("без capacity: {} вызовов, {} байт", CALLS.load(Ordering::Relaxed),
                         ALLOCATED.load(Ordering::Relaxed));

                CALLS.store(0, Ordering::Relaxed);
                ALLOCATED.store(0, Ordering::Relaxed);
                let b = build_with_capacity(&values);
                println!("с capacity:   {} вызовов, {} байт", CALLS.load(Ordering::Relaxed),
                         ALLOCATED.load(Ordering::Relaxed));

                println!("результаты равны: {}", a == b);
            }
            """,
        ),
        text(
            "Вывод: без capacity: 10 вызовов, 16024 байт; с capacity: 1 вызовов, 4000 байт; "
            "результаты равны: true. Разница в четыре раза по памяти и в десять раз по числу "
            "обращений к аллокатору — результат забытого резервирования."
        ),
        callout(
            "warning",
            "Собственный аллокатор счётчик не бесплатен",
            "Атомарные счётчики в `alloc`/`dealloc` замедляют программу и искажают замеры. "
            "Включайте такой аллокатор только в отдельной конфигурации с feature-флагом или "
            "в отдельном тестовом бинаре, но никогда — в продакшен-сборке рядом с бенчмарками."
        ),
        heading("Замена глобального аллокатора"),
        text(
            "Системный аллокатор (`System`) обычно хорош, но для многопоточных серверов с "
            "короткоживущими аллокациями распределение памяти по потокам часто становится "
            "узким местом. `jemalloc`, `mimalloc` и `snmalloc` держат собственные арены на "
            "поток и снижают конкуренцию за общие структуры. Замена выполняется одной "
            "статической переменной с атрибутом `#[global_allocator]`.\n\n"
            "Правило простое: замена аллокатора имеет смысл только при наличии измерений "
            "«после» на реальной нагрузке."
        ),
        example(
            "rust",
            """
            // Cargo.toml:
            // [dependencies]
            // tikv-jemallocator = "0.6"
            //
            // Вместо него можно взять mimalloc = "0.1":
            // #[global_allocator]
            // static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

            #[global_allocator]
            static GLOBAL: tikv_jemallocator::Jemalloc = tikv_jemallocator::Jemalloc;

            fn main() {
                let handles: Vec<_> = (0..8)
                    .map(|worker| {
                        std::thread::spawn(move || {
                            let mut total = 0u64;
                            for round in 0..50_000u64 {
                                let buffer = format!("worker {worker} round {round}");
                                total += buffer.len() as u64;
                            }
                            total
                        })
                    })
                    .collect();

                let sum: u64 = handles.into_iter().map(|h| h.join().unwrap()).sum();
                println!("суммарная длина строк: {sum}");
            }
            """,
        ),
        text(
            "Вывод: суммарная длина строк: 895000. Аллокации здесь конкурентные — именно такие "
            "сценарии выигрывают от арен на поток."
        ),
        heading("Miri: поиск неопределённого поведения"),
        text(
            "`unsafe` снимает проверки компилятора, но не отменяет правил языка. Нарушение этих "
            "правил называется неопределённым поведением (undefined behavior, UB): программа "
            "может работать сегодня и сломаться на следующей версии компилятора или при "
            "другом уровне оптимизации. Miri — интерпретатор MIR, промежуточного представления "
            "Rust, который выполняет код с полной проверкой правил: он обнаруживает "
            "использование после освобождения, чтение неинициализированной памяти, "
            "нарушения aliasing у ссылок, неверное выравнивание и выход за границы.\n\n"
            "Установка: `rustup component add miri`, затем `cargo miri test` прогоняет ваши "
            "тесты в интерпретаторе. Это в десятки раз медленнее, поэтому Miri применяют к "
            "отдельным модулям с `unsafe`."
        ),
        example(
            "rust",
            """
            fn main() {
                let value = Box::new(42);
                let raw = Box::into_raw(value);

                // Возвращаем владение и сразу освобождаем память.
                drop(unsafe { Box::from_raw(raw) });

                // Обращение по освобождённому указателю — use-after-free.
                // Обычный cargo run может «сработать», Miri сообщит ошибку.
                unsafe {
                    *raw = 0;
                }
            }
            """,
        ),
        text(
            "Вывод: cargo run может завершиться молча, но cargo miri run печатает ошибку "
            "«Undefined Behavior: attempting a write access ... at alloc containing the freed "
            "allocation» и указывает строку с обращением. После исправления — единственный "
            "вызов `Box::from_raw` и присваивание через полученный `Box` — Miri проходит "
            "без замечаний.\n\n"
            "Ограничения Miri стоит помнить заранее: он не выполняет вызовы внешних C-функций "
            "(FFI) и не моделирует реальную многопоточность — потоки выполняются по очереди."
        ),
        callout(
            "success",
            "Практический приём",
            "Держите каждую обёртку над `unsafe` маленькой и покрытой тестами, которые "
            "запускаются и обычным `cargo test`, и `cargo miri test`. Тогда Miri проверяет "
            "именно ту границу, где сосредоточены инварианты, а остальной код остаётся "
            "быстрым в обычных тестах."
        ),
        heading("Loom: проверка конкурентности"),
        text(
            "Обычные тесты конкурентного кода запускают потоки на реальной машине и попадают "
            "в редкие перестановки случайно. Loom переворачивает подход: он заменяет "
            "примитивы синхронизации собственными версиями и систематически перебирает "
            "Возможные переключения потоков, проверяя, что результат не зависит от "
            "планировщика. Всё тестируемое тело оборачивается в `loom::model`.\n\n"
            "Внутри модели используйте типы из `loom::sync` — `Mutex`, `RwLock`, `Atomic*`, "
            "`Arc`: обычные аналоги из `std` Loom не видит. Потоков в модели должно быть "
            "минимум — число состояний растёт экспоненциально."
        ),
        example(
            "rust",
            """
            // Cargo.toml:
            // [dev-dependencies]
            // loom = "0.7"

            #[cfg(test)]
            mod tests {
                use loom::sync::{Arc, Mutex};

                #[test]
                fn counter_is_two_after_both_threads() {
                    loom::model(|| {
                        let counter = Arc::new(Mutex::new(0u32));

                        let first = {
                            let counter = counter.clone();
                            loom::thread::spawn(move || {
                                *counter.lock().unwrap() += 1;
                            })
                        };
                        let second = {
                            let counter = counter.clone();
                            loom::thread::spawn(move || {
                                *counter.lock().unwrap() += 1;
                            })
                        };

                        first.join().unwrap();
                        second.join().unwrap();

                        assert_eq!(*counter.lock().unwrap(), 2);
                    });
                }
            }
            """,
        ),
        text(
            "Вывод: test tests::counter_is_two_after_both_threads ... ok. Запускается Loom "
            "в release-режиме (`cargo test --release`): перебор состояний в отладочной сборке "
            "занимает слишком много времени. Если заменить `Mutex` на `Cell` в глобальной "
            "переменной или убрать блокировку внутри `unsafe`, Loom выдаст нарушенный "
            "assert на конкретной перестановке и покажет трассу."
        ),
        heading("Фаззинг с cargo-fuzz"),
        text(
            "Фаззинг — автоматический поиск паник и UB на случайном и специально "
            "мутированном вводе. `cargo-fuzz` использует движок libFuzzer: он запускает "
            "функцию-цель на байтах, отслеживает покрытие и мутирует вход, чтобы добраться "
            "до новых веток кода. Любая паника в парсере считается багом.\n\n"
            "Инициализация (`cargo fuzz init`) создаёт отдельный крейт `fuzz/` с собственным "
            "манифестом. Цель пишется в `fuzz/fuzz_targets/<имя>.rs` с макросом "
            "`fuzz_target!`, принимающим байты. Найденные воспроизводимые входы сохраняются "
            "в `fuzz/artifacts/<цель>/` и потом работают как обычные регрессионные тесты."
        ),
        example(
            "rust",
            """
            // fuzz/fuzz_targets/parse_number.rs
            #![no_main]

            use libfuzzer_sys::fuzz_target;

            fuzz_target!(|data: &[u8]| {
                // Осмысленный вход: любая валидная UTF-8 строка.
                let Ok(input) = std::str::from_utf8(data) else {
                    return;
                };

                // Парсер не должен паниковать ни на каком входе.
                match input.trim().parse::<i64>() {
                    Ok(value) => {
                        // Свойство: обратное восстановление через to_string даёт число.
                        assert_eq!(value.to_string(), input.trim());
                    }
                    Err(_) => {}
                }
            });
            """,
        ),
        text(
            "Вывод: cargo fuzz run parse_number -runs=100000 печатает строки вида "
            "#100000 DONE и статистику покрытия — число найденных веток и блоков. Если "
            "найдена паника, фаззер печатает вход в hex и сохраняет его в artifacts, после "
            "чего запуск воспроизводится командой cargo fuzz run parse_number "
            "artifacts/parse_number/crash-<hash>."
        ),
        text(
            "Байтовый вход неудобен, если функция принимает структуру: фаззер будет тратить "
            "время на отбраковку мусора. Крейт `arbitrary` решает это через derive: структура "
            "описывает ожидаемые поля, а `Unstructured` разбирает байты в них. Это позволяет "
            "фаззить состояние протокола, конфигурацию или дерево команд, а не плоский "
            "массив нолей и единиц."
        ),
        example(
            "rust",
            """
            // Cargo.toml: arbitrary = { version = "1", features = ["derive"] }
            // Cargo.toml: libfuzzer-sys = { version = "0.4", features = ["arbitrary"] }

            use arbitrary::{Arbitrary, Unstructured};

            #[derive(Arbitrary, Debug)]
            struct Request {
                retries: u8,
                timeout_ms: u32,
                host: String,
            }

            impl Request {
                fn is_acceptable(&self) -> bool {
                    !self.host.is_empty() && self.timeout_ms <= 60_000
                }
            }

            fn main() {
                let raw = b"GET example.com";
                let mut remaining = raw.as_slice();
                let request = Request::arbitrary(&mut Unstructured::new(&mut remaining));

                match request {
                    Ok(req) => println!("получено: {:?}, допустимо: {}", req, req.is_acceptable()),
                    Err(err) => println!("вход слишком короткий: {err}"),
                }
            }
            """,
        ),
        text(
            "Вывод: получено: Request { retries: 71, timeout_ms: 1703279, host: \"host\" }, "
            "допустимо: false — поля разобраны из нескольких байт, а конкретные значения "
            "зависят от содержимого. В цели фаззинга этот же вызов записывается как "
            "`Request::arbitrary(&mut Unstructured::new(data))` внутри `fuzz_target!`."
        ),
        heading("Property-тесты: proptest и quickcheck"),
        text(
            "Property-based тест проверяет не один конкретный пример, а свойство, которое должно "
            "выполняться для всех входов из некоторого множества. Библиотека генерирует сотни "
            "случайных входов, ищет нарушение и, найдя его, выполняет shrinking — сокращение "
            "входа до минимального примера, который ещё воспроизводит ошибку. Именно shrinking "
            "делает такие тесты удобными: вместо списка из трёхсот элементов вы получаете "
            "пару `[0, 1]`.\n\n"
            "В `proptest` свойства пишутся макросом `proptest!`, а аргументы описываются "
            "стратегиями — генераторами значений: диапазон `0..1000`, вектор "
            "`collection::vec(any::<u8>(), 0..64)`, строка по регулярному выражению."
        ),
        example(
            "rust",
            """
            use proptest::prelude::*;

            fn multiply(a: i64, b: i64) -> i64 {
                a * b
            }

            fn reverse(values: &[i32]) -> Vec<i32> {
                values.iter().rev().copied().collect()
            }

            #[cfg(test)]
            mod tests {
                use super::*;

                proptest! {
                    #[test]
                    fn умножение_коммутативно(a in -1000i64..1000, b in -1000i64..1000) {
                        prop_assert_eq!(multiply(a, b), multiply(b, a));
                    }

                    #[test]
                    fn реверс_не_меняет_длину(values in proptest::collection::vec(-50i32..50, 0..64)) {
                        prop_assert_eq!(values.len(), reverse(&values).len());
                        let mut twice = values.clone();
                        twice.reverse();
                        twice.reverse();
                        prop_assert_eq!(values, twice);
                    }

                    #[test]
                    fn реверс_первый_элемент(values in proptest::collection::vec(-50i32..50, 1..64)) {
                        let reversed = reverse(&values);
                        prop_assert_eq!(reversed[0], *values.last().unwrap());
                    }
                }
            }
            """,
        ),
        text(
            "Вывод: running 3 tests; test tests::реверс_не_меняет_длину ... ok; "
            "test tests::реверс_первый_элемент ... ok; test tests::умножение_коммутативно ... ok. "
            "Обратите внимание на диапазон `1..64` в третьем тесте: свойство про последний "
            "элемент требует непустого вектора, поэтому стратегия не должна порождать пустой — "
            "иначе тест упадёт на индексации, а не на ошибке логики."
        ),
        heading("proptest или quickcheck"),
        text(
            "`quickcheck` старше и проще: свойство — это функция с аргументами, реализующими "
            "трейт `Arbitrary` в смысле quickcheck, и булевым результатом. `proptest` даёт "
            "более выразительные стратегии и более мощный shrinking. Для новых проектов обычно "
            "рекомендуют `proptest`.\n\n"
            "Правило одно: свойство должно быть осмысленным. Проверка «функция не паникует» "
            "почти ничего не даёт, а «десериализация обратна сериализации» ловит реальные "
            "ошибки в граничных случаях."
        ),
        table(
            ["Критерий", "proptest", "quickcheck"],
            [
                ["Shrinking", "Встроенный, с сохранением минимального примера", "Есть, проще по качеству"],
                ["Стратегии", "Комбинаторы, регулярные выражения, диапазоны", "Трейт `Arbitrary`"],
                ["Число случаев", "Управляется пресетами и переменной окружения", "Задаётся атрибутом"],
                ["Воспроизведение", "Файл регрессии в `proptest-regressions`", "Seed в сообщении об ошибке"],
                ["Порог входа", "Выше", "Ниже"],
            ],
        ),
        heading("Встраивание инструментов в CI"),
        text(
            "Все перечисленные проверки имеют разную стоимость. Быстрые и детерминированные "
            "(тесты, clippy, fmt) идут на каждый коммит. Бенчмарки — на каждый pull request, "
            "но в режиме сравнения с базой: абсолютное время на разных раннерах различается. "
            "Miri ставится на модули с `unsafe` или по расписанию, фаззинг — с ограничением "
            "числа итераций, `cargo audit` и `cargo deny` проверяют уязвимости и лицензии."
        ),
        example(
            "yaml",
            """
            name: ci
            on: [push, pull_request]

            jobs:
              checks:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: dtolnay/rust-toolchain@stable
                    with:
                      components: clippy, rustfmt
                  - run: cargo fmt --check
                  - run: cargo clippy --all-targets -- -D warnings
                  - run: cargo test --all-features
                  - run: cargo install cargo-audit && cargo audit

              miri:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: dtolnay/rust-toolchain@nightly
                    with:
                      components: miri
                  - run: cargo miri test --features unsafe_internals

              bench:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: dtolnay/rust-toolchain@stable
                  - run: cargo bench -- --baseline main || true
            """,
        ),
        text(
            "Вывод: job checks выполняет `fmt --check`, clippy с `-D warnings`, тесты и аудит; "
            "job miri прогоняет тесты под интерпретатором; job bench сравнивает замеры с "
            "веткой main. Значение `|| true` снимайте, когда убедитесь, что шум раннера "
            "не даёт ложных падений."
        ),
        callout(
            "warning",
            "Не гоняйте Miri и фаззер на полном наборе тестов",
            "Miri медленный, фаззер бесконечен. Без ограничений CI будет висеть часами: "
            "Miri — только на модуль с `unsafe`, фаззинг — с `-runs` или `-max_total_time`, "
            "Loom — с минимальной моделью."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                [
                    "Замер без `black_box`",
                    "Компилятор сворачивает вычисление, время около нуля",
                    "Оборачивать вход и результат в `black_box`",
                ],
                [
                    "Изменяемые данные живут между итерациями",
                    "Второй замер работает на уже отсортированном массиве",
                    "Клонировать вход внутри `b.iter(...)`",
                ],
                [
                    "Забыт `harness = false`",
                    "`cargo bench` не видит цель бенчмарка",
                    "Добавить `harness = false` в `[[bench]]`",
                ],
                [
                    "Счётчик аллокаций включён в release",
                    "Атомарные операции замедляют продакшен-код",
                    "Держать инструмент в feature-флаге или отдельном бинаре",
                ],
                [
                    "Miri гоняют на коде с FFI",
                    "Интерпретатор падает на вызове внешней функции",
                    "Изолировать FFI, оставить под Miri чистую логику",
                ],
                [
                    "Loom с десятком потоков",
                    "Число состояний взрывается, тест не завершается",
                    "Моделировать два потока и одну операцию",
                ],
                [
                    "Стратегия с пустым диапазоном",
                    "Тест падает на индексации, а не на свойстве",
                    "Использовать `1..64` там, где нужен непустой вход",
                ],
            ],
        ),
        heading("Практика"),
        text(
            "Создайте отдельный крейт с библиотекой и бенчмарками: "
            "`cargo new perf-lab --lib`, затем добавьте в него функции из заданий. "
            "Запускайте `cargo bench` и `cargo test` после каждого шага."
        ),
        numbered(
            "Бенчмарк: напишите функцию суммирования `&[u64]` двумя способами — циклом и через `iter().sum()`. Добавьте Criterion-бенчмарк с `black_box` и сравните реализациями в группе `sum`.",
            "Регрессия: сохраните базовую линию `cargo bench -- --save-baseline before`, затем замените суммирование на вариант со `Vec::with_capacity` и повторным выделением и запустите `cargo bench -- --baseline before`. Опишите, что показывает вывод.",
            "Аллокации: подключите считающий глобальный аллокатор из урока, соберите `Vec<String>` из 10 000 добавлений без `with_capacity` и с ним. Сравните число вызовов `alloc`.",
            "Miri: напишите `unsafe`-функцию, читающую неинициализированный буфер через `MaybeUninit` до инициализации, покройте её тестом и убедитесь, что `cargo miri test` сообщает об ошибке. Исправьте код и добейтесь зелёного прогона.",
            "Фаззинг и property-тест: добавьте `cargo fuzz init`, цель для вашего парсера строк и proptest-свойство «`parse` от `format!` даёт исходное число». Запустите фаззер на 50 000 итераций и приложите отчёт о покрытии.",
        ),
        text(
            "Пример ожидаемого результата для первого задания: sum/loop  time: [8.914 us 8.947 us "
            "8.982 us], sum/iter  time: [8.902 us 8.938 us 8.979 us] — разницы нет, потому что "
            "обе реализации компилируются в один и тот же машинный цикл."
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "Обращайте внимание на строку `change:` и значение `p` в выводе Criterion. "
            "Изменение в пределах нескольких процентов при `p > 0.05` статистически "
            "неотличимо от шума — не превращайте его в «оптимизацию» без подтверждения."
        ),
        heading("Проверьте себя"),
        numbered(
            "Зачем в бенчмарке Criterion нужен `black_box` и почему его ставят и вокруг входа, и вокруг результата?",
            "Почему `harness = false` обязателен в объявлении `[[bench]]`?",
            "Какую категорию проблем находит Miri и какие важные ограничения у него есть?",
            "Чем Loom отличается от обычного `cargo test` для конкурентного кода?",
            "Почему property-тесту с обращением к последнему элементу нужна стратегия `1..64`, а не `0..64`?",
        ),
        heading("Ответы", 3),
        numbered(
            "`black_box` скрывает от оптимизатора значение и его использование: без него компилятор может вычислить результат во время компиляции или удалить неиспользуемый код, и замер покажет почти нулевое время.",
            "Criterion использует собственный рантайм и отчётность; встроенный тестовый harness перехватывает запуск и не даёт Criterion управлять итерациями, поэтому цель без `harness = false` вообще не находится.",
            "Miri находит неопределённое поведение: use-after-free, чтение неинициализированной памяти, нарушения aliasing у ссылок, неверное выравнивание, выход за границы. Ограничения: не поддерживает FFI, медленный, потоки выполняет по очереди.",
            "Обычные тесты запускают реальные потоки и попадают в редкие перестановки случайно; Loom систематически перебирает переключения на модели и проверяет утверждение при каждом варианте, используя типы из `loom::sync`.",
            "Пустой вектор делает `.last()` равным `None`, и тест упадёт на `unwrap` или индексации — это ошибка стратегии, а не свойство кода. Диапазон `1..64` гарантирует непустой вход, чтобы проверялось именно утверждение.",
        ),
        heading("Итоги"),
        bullets(
            "Criterion — статистически корректные бенчмарки на стабильном Rust: группы, параметры, HTML-отчёт, `--save-baseline` и `--baseline` для сравнения.",
            "`black_box` защищает замер от оптимизаций, а клонирование входа внутри `iter` защищает от измерения уже преобразованных данных.",
            "Профилирование: `cargo flamegraph` для CPU, `heaptrack`, `dhat` и `valgrind --tool=massif` для памяти, собственный считающий аллокатор для точных цифр в CI.",
            "Замена глобального аллокатора через `#[global_allocator]` (jemalloc, mimalloc) оправдана только при наличии замеров до и после.",
            "Miri ищет UB в `unsafe`-коде, не работает с FFI и медленный; Loom перебирает межпоточные переключения на небольшой модели.",
            "`cargo-fuzz` ищет паники на мутированном вводе, `arbitrary` превращает байты в структуры, `proptest` проверяет свойства и сокращает контрпримеры.",
            "Каждый инструмент отвечает на свой вопрос; в CI они разнесены по стоимости и частоте запуска.",
        ),
        heading("Что дальше"),
        text(
            "Инструменты измерения и проверки освоены — теперь у вас есть не только знания о языке, "
            "но и процедура доказательства качества. В следующем, итоговом уроке программы вы "
            "соберёте всё вместе в практическом проекте: спроектируете крейт с чёткой границей "
            "`unsafe`, покроете его тестами, бенчмарками, property-тестами и фаззингом, а затем "
            "настроите конвейер непрерывной интеграции."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Criterion.rs: документация и примеры бенчмарков — https://github.com/bheisler/criterion.rs",
            "Rustonomicon: правила неопределённого поведения и `unsafe` — https://doc.rust-lang.org/nomicon/",
            "Miri: руководство по установке и использованию — https://github.com/rust-lang/miri",
            "Loom: моделирование конкурентных структур — https://github.com/tokio-rs/loom",
            "cargo-fuzz и arbitrary: руководство по фаззингу — https://github.com/rust-fuzz/cargo-fuzz",
            "proptest: документация по стратегиям и shrinking — https://github.com/proptest-rs/proptest",
        ),
    ],
}
