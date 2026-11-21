"""Урок 2 курса rust: продвинутые типы."""

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
    "program_order": 2,
    "topic_order": 2,
    "name": "2.2. Продвинутые типы",
    "slug": "rust-2-2-продвинутые-типы",
    "short_description": (
        "Паттерн newtype, псевдонимы типов, never-тип, типы динамического размера, трайт-объекты "
        "в разных умных указателях, вариантность и PhantomData для маркерных типов."
    ),
    "topic_name": "Продвинутые типы",
    "topic_description": (
        "Разбор инструментов системы типов Rust, которые нужны для построения безопасных API: "
        "newtype-обёртки, алиасы, diverging-функции и never-тип, DST и `?Sized`, "
        "трейт-объекты под `Box`, `Rc` и `Arc`, вариантность и маркер `PhantomData`."
    ),
    "learning_objectives": [
        "Строить newtype-обёртки для типобезопасности и реализовывать для них `Deref` и арифметику",
        "Применять алиасы типов через `type` и отличать их от полноценных новых типов",
        "Объявлять diverging-функции с never-типом `!` и использовать его в `match` и `Result`",
        "Понимать типы динамического размера: `str`, `[T]`, `dyn Trait`, и работать с ними через указатели",
        "Применять ограничение `?Sized` в дженериках и возвращать трейт-объекты из функций",
        "Различать `Box<dyn Trait>`, `Rc<dyn Trait>` и `Arc<dyn Trait>` по владению и потокам",
        "Объяснять ковариантность, контрвариантность и инвариантность ключевых типов",
        "Использовать `PhantomData` для маркерных типов, типобезопасных состояний и управления трейтами",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "rust",
        "newtype",
        "dst",
        "trait objects",
        "variance",
        "phantomdata",
    ],
    "starter_code": code(
        r"""
        use std::ops::Add;

        #[derive(Debug, Clone, Copy, PartialEq)]
        struct Meters(f64);

        impl Add for Meters {
            type Output = Meters;
            fn add(self, other: Meters) -> Meters {
                Meters(self.0 + other.0)
            }
        }

        fn main() {
            let a = Meters(10.0);
            let b = Meters(2.5);
            let c = a + b;
            println!("{:?}", c);
        }
        """
    ),
    "hints": [
        "Алиас через `type` не создаёт новый тип: `Meters` и `f64` для компилятора одно и то же. Для проверки типов нужна структура-обёртка.",
        "`dyn Trait` и `str` имеют неизвестный размер, поэтому живут только за указателем: `&dyn Trait`, `Box<dyn Trait>`, `Arc<dyn Trait>`.",
        "Чтобы дженерик принимал неразмерные типы, ослабьте ограничение: `fn show<T: ?Sized + Display>(value: &T)`.",
        "`PhantomData<T>` сообщает, что структура владеет `T`, хотя поля с этим типом нет. Без него будет ошибка E0392.",
    ],
    "content": [
        text(
            "Система типов Rust открыта для расширения: язык позволяет строить новые типы поверх "
            "существующих, скрывать конкретный тип за трейтом, описывать функции, которые никогда "
            "не возвращают управление, и управлять тем, как параметры типов подставляются друг вместо друга. "
            "В первой программе эти инструменты не нужны, но без них не обходится ни одна библиотека.\n\n"
            "Здесь вы разберёте newtype-паттерн, псевдонимы типов, never-тип, типы динамического размера "
            "и трейт-объекты, вариантность и маркер `PhantomData`. Тема связана с предыдущим уроком "
            "об ownership: именно владение определяет, какой умный указатель подойдёт для типа, "
            "размер которого неизвестен на этапе компиляции.\n\n"
            "Каждый пример — законченная программа с функцией `main`: её можно вставить "
            "в проект `cargo new types_lab` и запустить через `cargo run`."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "строить newtype-обёртки и реализовывать для них `Deref`, арифметику и валидацию;",
            "применять `type` для сокращения длинных сигнатур и понимать, что алиас не создаёт новый тип;",
            "объявлять функции с never-типом `!` и использовать `Result<T, Infallible>`;",
            "объяснять, почему `str`, `[T]` и `dyn Trait` нельзя хранить по значению;",
            "применять `?Sized`, `Box<str>`, `Box<[T]>` и возвращать `Box<dyn Trait>`;",
            "выбирать между `Box<dyn Trait>`, `Rc<dyn Trait>` и `Arc<dyn Trait>`;",
            "объяснять вариантность и правильно подбирать маркер `PhantomData` для структуры;",
            "строить типобезопасный построитель через маркерные типы состояний.",
        ),
        heading("Newtype: обёртка для типобезопасности"),
        text(
            "Newtype — это структура с единственным полем, которая создаёт новый тип поверх существующего: "
            "`struct UserId(u64)`. На уровне машинного кода такая обёртка бесплатна, "
            "но для компилятора `UserId` и `u64` — разные типы, и перепутать их уже нельзя.\n\n"
            "Функции `set_age(age: u32)` и `set_id(id: u32)` принимают один тип, поэтому вызов "
            "`set_age(user_id)` скомпилируется, хотя это ошибка смысла. С newtype-обёртками "
            "компилятор сообщит `expected Age, found UserId`.\n\n"
            "Пустые структуры вроде `struct Yes;` тоже полезны: они бесплатны и служат "
            "маркерами состояний, о которых речь пойдёт ниже."
        ),
        example(
            "rust",
            """
            struct UserId(u64);
            struct Age(u8);

            fn set_id(id: UserId) {
                println!("идентификатор {}", id.0);
            }

            fn set_age(age: Age) {
                println!("возраст {}", age.0);
            }

            fn main() {
                let id = UserId(42);
                let age = Age(30);
                set_id(id);
                set_age(age);
                // set_id(age); // ошибка: expected UserId, found Age
            }
            """,
        ),
        text(
            "Вывод: `идентификатор 42` и `возраст 30`. Строка `set_id(age)` не собирается: "
            "компилятор сообщает `mismatched types`. К полю обращаются через `.0` — "
            "это единственный синтаксис доступа к полю tuple-структуры."
        ),
        heading("Реализация трейтов для newtype", 3),
        text(
            "Newtype не наследует поведение внутреннего типа: только вы решаете, какие трейты "
            "реализовать, поэтому бессмысленные операции вроде сложения идентификаторов не появятся.\n\n"
            "Для обёртки-числа часто реализуют `Deref`, чтобы обращаться к значению без `.0`, "
            "и трейт арифметики. `Deref` с целевым типом `f64` разрешает писать `*distance` "
            "и вызывает методы внутреннего типа. `Add` возвращает такой же newtype, поэтому "
            "сумма двух `Meters` остаётся `Meters`."
        ),
        example(
            "rust",
            """
            use std::ops::{Add, Deref};

            #[derive(Debug, Clone, Copy, PartialEq)]
            struct Meters(f64);

            impl Deref for Meters {
                type Target = f64;
                fn deref(&self) -> &f64 {
                    &self.0
                }
            }

            impl Add for Meters {
                type Output = Meters;
                fn add(self, other: Meters) -> Meters {
                    Meters(self.0 + other.0)
                }
            }

            fn main() {
                let a = Meters(10.0);
                let b = Meters(5.5);
                let total = a + b;
                println!("{}", *total);
                println!("{:?}", total.sqrt());
            }
            """,
        ),
        text(
            "Вывод: `15.5`, затем `3.9370039370059056`. Метод `sqrt` из `f64` доступен прямо "
            "на `Meters`: компилятор автоматически разыменовывает значение. Это же свойство "
            "позволяет неявно передать `&Meters` туда, где ждут `&f64`, — для строгих API "
            "иногда лучше обойтись без `Deref`."
        ),
        callout(
            "info",
            "Когда newtype особенно полезен",
            "Обёртки окупаются там, где значения одного типа имеют разный смысл: идентификаторы, "
            "деньги, координаты, единицы измерения, токены. Приватное поле и конструктор `new`, "
            "возвращающий `Result`, гарантируют, что объекта с некорректным содержимым не существует.",
        ),
        heading("Псевдонимы типов"),
        text(
            "Оператор `type` вводит второе имя для существующего типа. Это синтаксическое удобство: "
            "алиас не создаёт новый тип, не даёт проверки типов и не влияет на размер. "
            "`type Kilometers = i64` означает, что оба имени взаимозаменяемы полностью.\n\n"
            "Практическая польза — сокращение длинных сигнатур. Тип "
            "`Box<dyn FnOnce() + Send + 'static>` повторяется в десятках мест, "
            "а алиас `type Task = ...` делает код читаемым. Так же объявляют "
            "`type Result<T> = std::result::Result<T, MyError>` и пишут в модуле просто `Result<T>`."
        ),
        example(
            "rust",
            """
            type Meters = u32;
            type Task = Box<dyn FnOnce() + Send + 'static>;
            type Events = Vec<(u64, String)>;

            fn takes_meters(m: Meters) {
                println!("{} м", m);
            }

            fn run(task: Task) {
                task();
            }

            fn make_task() -> Task {
                Box::new(|| println!("задача выполнена"))
            }

            fn main() {
                takes_meters(5);
                run(make_task());
                let log: Events = vec![(1, String::from("старт"))];
                println!("{:?}", log);
            }
            """,
        ),
        text(
            "Вывод: `5 м`, `задача выполнена`, `[(1, \"старт\")]`. Вызов `takes_meters(5_u32)` "
            "тоже скомпилировался бы: алиас не защищает от перепутывания. Алиасы бывают "
            "обобщёнными (`type Pair<T> = (T, T)`), но `impl` для алиаса запрещён."
        ),
        table(
            ["Свойство", "`struct Meters(f64)`", "`type Meters = f64`"],
            [
                ["Новый тип для компилятора", "Да", "Нет"],
                ["Собственные `impl` и трейты", "Да", "Нет (только у исходного типа)"],
                ["Размер в памяти", "Тот же", "Тот же"],
                ["Защита от перепутывания", "Да", "Нет"],
                ["Удобство в длинных сигнатурах", "Среднее", "Высокое"],
            ],
        ),
        heading("Never-тип и diverging-функции"),
        text(
            "Never-тип записывается как `!` и означает «значение, которого не существует»: "
            "функция с таким возвращаемым типом никогда не возвращает управление — "
            "она паникует, завершает процесс или крутится в бесконечном цикле. "
            "Такие функции называют diverging.\n\n"
            "`!` совместим с любым типом. Если одна ветка `match` возвращает `i32`, "
            "а другая вызывает паникующую функцию, компилятор не жалуется: ветка без "
            "возврата формально подходит под ожидаемый тип. Так же работают `loop {}` "
            "без `break`, `process::exit` и `unreachable!`.\n\n"
            "Второе применение — ошибки, которых не бывает: `Result<T, Infallible>` описывает "
            "операцию, гарантированно успешную, но участвующую в интерфейсе с `Result`."
        ),
        example(
            "rust",
            """
            use std::convert::Infallible;

            fn fail(message: &str) -> ! {
                panic!("сбой: {}", message);
            }

            fn pick(index: Option<i32>) -> i32 {
                match index {
                    Some(value) => value,
                    None => fail("значение отсутствует"),
                }
            }

            fn always_ok() -> Result<i32, Infallible> {
                Ok(42)
            }

            fn main() {
                println!("{}", pick(Some(7)));
                let value: i32 = always_ok().unwrap();
                println!("{}", value);
                // pick(None);
            }
            """,
        ),
        text(
            "Вывод: `7`, затем `42`. Вызов `pick(None)` паникует с сообщением `сбой: значение отсутствует`. "
            "Метод `unwrap` для `Result<i32, Infallible>` безопасен: в ветке `Err` нет ни одного значения."
        ),
        callout(
            "warning",
            "Never-тип стабилизирован не полностью",
            "Использовать `!` в позиции возвращаемого типа функции, в `match`, `if` и `loop` можно. "
            "А вот присваивать `!` явным типам вроде `let x: ! = ...` пока нельзя: это разрешение "
            "ещё не стабилизировано. Не путайте его с `Infallible` — это отдельное пустое перечисление, "
            "которое стабильно и удобно для `Result`.",
        ),
        heading("Типы динамического размера"),
        text(
            "Большинство типов Rust имеют известный на этапе компиляции размер. "
            "Но три типа так устроить нельзя: `str` (строка произвольной длины), "
            "`[T]` (срез любого количества элементов) и `dyn Trait` (трейт-объект, конкретный тип "
            "которого известен только в рантайме). Это типы динамического размера, DST.\n\n"
            "Записать `let s: str = ...` нельзя: размер типа не известен на этапе компиляции. "
            "DST живут только за указателем. Такой указатель называют толстым: кроме адреса "
            "данных он несёт длину для `str` и `[T]` или указатель на vtable для `dyn Trait`."
        ),
        example(
            "rust",
            """
            use std::fmt::Debug;
            use std::rc::Rc;

            fn main() {
                let s: &str = "привет";
                let boxed: Box<str> = Box::from("привет");
                let shared: Rc<str> = Rc::from("привет");

                let slice: &[i32] = &[1, 2, 3];
                let boxed_slice: Box<[i32]> = Box::new([1, 2, 3]);

                let object: &dyn Debug = &42;
                let boxed_object: Box<dyn Debug> = Box::new(42);

                println!("{} {}", s, boxed);
                println!("{} {}", shared, slice.len());
                println!("{:?} {:?} {:?}", boxed_slice, object, boxed_object);
            }
            """,
        ),
        text(
            "Вывод: `привет привет`, затем `привет 3`, затем `[1, 2, 3] 42 42`. "
            "За `Box` и `Rc` живёт именно `str`. `Box<str>` не хранит лишнюю ёмкость "
            "и потому компактнее `String`."
        ),
        heading("Ограничение `?Sized` и признак `Sized`", 3),
        text(
            "У каждого параметра типа по умолчанию подразумевается ограничение `T: Sized`, "
            "поэтому дженерик не примет `str` или `dyn Trait`. Ограничение `?Sized` снимает "
            "требование и разрешает неразмерные типы по ссылке или через указатель.\n\n"
            "Такая функция принимает и `&String`, и `&str`, и `&dyn Display`. "
            "Стандартная библиотека объявляет `Display::to_string` именно с `Self: ?Sized`."
        ),
        example(
            "rust",
            """
            use std::fmt::Display;

            fn show<T: Display + ?Sized>(label: &str, value: &T) {
                println!("{}: {}", label, value);
            }

            fn main() {
                let owned = String::from("владеемая строка");
                let slice: &str = "срез";
                show("string", &owned);
                show("str", slice);
                show("число", &42);
                show("тайп", &std::any::type_name::<str>());
            }
            """,
        ),
        text(
            "Вывод: четыре строки вида `string: владеемая строка`, `str: срез`, `число: 42`, "
            "`тайп: str`. Без `?Sized` четвёртый вызов не скомпилируется: `str` неразмерный. "
            "Одна функция обслуживает и владеемые строки, и срезы, и числа."
        ),
        heading("Трейт-объекты под разными указателями"),
        text(
            "`dyn Trait` описывает значение с поведением трейта без известного типа. "
            "Коллекция разнородных фигур хранится как `Vec<Box<dyn Shape>>`: элементы имеют "
            "одинаковый размер, а вызов `shape.area()` идёт через таблицу методов — "
            "это динамическая диспетчеризация, плата за гибкость по сравнению с дженериками.\n\n"
            "Выбор указателя определяется владением. `Box<dyn Trait>` — единственный владелец, "
            "его берут для коллекций и полей структур. `Rc<dyn Trait>` допускает несколько владельцев "
            "в пределах потока, `Arc<dyn Trait>` — между потоками, но требует атомарных счётчиков "
            "и потому дороже. Ссылка `&dyn Trait` ничего не владеет."
        ),
        example(
            "rust",
            """
            use std::sync::Arc;

            trait Shape {
                fn area(&self) -> f64;
                fn name(&self) -> &'static str;
            }

            struct Circle {
                radius: f64,
            }

            struct Square {
                side: f64,
            }

            impl Shape for Circle {
                fn area(&self) -> f64 {
                    3.14159 * self.radius * self.radius
                }
                fn name(&self) -> &'static str {
                    "круг"
                }
            }

            impl Shape for Square {
                fn area(&self) -> f64 {
                    self.side * self.side
                }
                fn name(&self) -> &'static str {
                    "квадрат"
                }
            }

            fn main() {
                let shapes: Vec<Box<dyn Shape>> = vec![
                    Box::new(Circle { radius: 2.0 }),
                    Box::new(Square { side: 3.0 }),
                ];
                let shared: Arc<dyn Shape + Send + Sync> =
                    Arc::new(Circle { radius: 1.0 });
                for shape in &shapes {
                    println!("{}: {:.2}", shape.name(), shape.area());
                }
                println!("второй владелец: {}", shared.name());
            }
            """,
        ),
        text(
            "Вывод: `круг: 12.57`, `квадрат: 9.00`, `второй владелец: круг`. "
            "Фигуры в векторе разного конкретного типа, и компилятор узнаёт его только по vtable. "
            "`Arc` дополнительно требует `Send + Sync`: без них объект нельзя передать в другой поток."
        ),
        text(
            "С трейт-объектами связано важное ограничение: трейт должен быть object-safe. "
            "Методы с `Self` в возвращаемом типе, с обобщёнными параметрами или принимающие `self` по значению, "
            "в vtable не помещаются. Обойти это можно пометкой `where Self: Sized`: "
            "метод остаётся доступен для конкретных типов, но исчезает из трейт-объекта."
        ),
        example(
            "rust",
            """
            trait Factory {
                fn create(&self, width: f64, height: f64) -> Box<dyn Shape>;
                fn clone_box(&self) -> Box<dyn Factory>
                where
                    Self: Sized;
            }

            trait Shape {
                fn area(&self) -> f64;
            }

            struct Rectangle {
                width: f64,
                height: f64,
            }

            impl Shape for Rectangle {
                fn area(&self) -> f64 {
                    self.width * self.height
                }
            }

            struct RectangleFactory;

            impl Factory for RectangleFactory {
                fn create(&self, width: f64, height: f64) -> Box<dyn Shape> {
                    Box::new(Rectangle { width, height })
                }
                fn clone_box(&self) -> Box<dyn Factory>
                where
                    Self: Sized,
                {
                    Box::new(RectangleFactory)
                }
            }

            fn main() {
                let factory: Box<dyn Factory> = Box::new(RectangleFactory);
                let shape: Box<dyn Shape> = factory.create(4.0, 2.5);
                println!("площадь {:.2}", shape.area());
            }
            """,
        ),
        text(
            "Вывод: `площадь 10.00`. `clone_box` с ограничением `Self: Sized` не входит в vtable "
            "и не мешает использовать `Box<dyn Factory>`; без ограничения компилятор сообщит, "
            "что трейт не является object-safe."
        ),
        table(
            ["Указатель", "Владение", "Потоки", "Вес", "Типичный случай"],
            [
                ["`&dyn Trait`", "Нет", "Зависит от типа", "2 слова, заём", "Параметр функции"],
                ["`Box<dyn Trait>`", "Один владелец", "Зависит от типа", "2 слова, куча", "Поле структуры, коллекция"],
                ["`Rc<dyn Trait>`", "Общий, не атомарный", "Только один поток", "2 слова + счётчик", "Граф внутри потока"],
                ["`Arc<dyn Trait>`", "Общий, атомарный", "Любые потоки с `Send + Sync`", "Дороже `Rc`", "Шаринг между потоками"],
            ],
        ),
        heading("Вариантность"),
        text(
            "Вариантность описывает, можно ли подставить один параметризованный тип вместо другого, "
            "если его аргумент — подтип. Подтипизация в Rust работает через времена жизни: "
            "`&'static str` является подтипом `&'a str`.\n\n"
            "Ковариантность: если `'static` подтип `'a`, то `&'static str` подтип `&'a str`. "
            "Так же ведут себя `Box<T>`, `Vec<T>`, `Rc<T>`, `Arc<T>` и `*const T`: через них "
            "нельзя записать новое значение, поэтому время жизни безопасно сократить. "
            "Контрвариантность встречается у параметров функций: `fn(&'a str)` подтип `fn(&'static str)`, "
            "потому что функция, принимающая короткоживущую ссылку, справится и с долгоживущей.\n\n"
            "Инвариантность: `&mut T`, `Cell<T>`, `RefCell<T>`, `UnsafeCell<T>` и `*mut T`. "
            "Через изменяемую ссылку можно записать значение, и ковариантность позволила бы "
            "положить короткоживущие данные в структуру с длинным временем жизни."
        ),
        example(
            "rust",
            """
            use std::cell::Cell;


            fn take_ref(s: &str) {
                println!("ссылка: {}", s);
            }

            fn take_mut(s: &mut String) {
                s.push_str(" и изменено");
            }

            fn call_with_static(f: fn(&'static str)) {
                f("статическая строка");
            }

            fn takes_any(s: &str) {
                println!("принято: {}", s);
            }

            fn main() {
                let text: &'static str = "долгоживущая";
                take_ref(text);

                let mut owned = String::from("значение");
                take_mut(&mut owned);
                println!("{}", owned);

                call_with_static(takes_any);

                let cell = Cell::new(0);
                cell.set(7);
                println!("{}", cell.get());
            }
            """,
        ),
        text(
            "Вывод: `ссылка: долгоживущая`, `значение и изменено`, "
            "`принято: статическая строка`, `7`. `&'static str` приводится к `&str` (ковариантность), "
            "а функция `takes_any` с типом `fn(&str)` приводится к `fn(&'static str)` (контрвариантность). "
            "Для чисел вариантность не проявляется, но для структур с временем жизни она решающая."
        ),
        table(
            ["Тип", "Вариантность по параметру", "Причина"],
            [
                ["`&'a T`", "Ковариантен", "Только чтение"],
                ["`&'a mut T`", "Инвариантен", "Можно записать любое значение"],
                ["`Box<T>`, `Vec<T>`, `Rc<T>`, `Arc<T>`", "Ковариантны", "Владение без скрытых записей"],
                ["`Cell<T>`, `RefCell<T>`, `UnsafeCell<T>`", "Инвариантны", "Внутренняя изменяемость"],
                ["`*const T`", "Ковариантен", "Требует `unsafe` для записи"],
                ["`*mut T`", "Инвариантен", "Позволяет запись"],
                ["`fn(T) -> U`", "Контрвариантен по `T`, ковариантен по `U`", "Параметр в контрапозиции"],
            ],
        ),
        heading("`PhantomData` и маркерные типы"),
        text(
            "Иногда структуре нужен параметр типа, который не хранится в полях: например, итератор "
            "держит сырой указатель и лишь выглядит владеющим. Запись "
            "`struct MyIter<T> { ptr: *const T }` даёт ошибку `parameter T is never used`. "
            "Решение — поле `PhantomData<T>`: оно не занимает места и сообщает компилятору, "
            "как относиться к `T`.\n\n"
            "Маркер определяет вариантность, проверку при удалении и трейты `Send` и `Sync`. "
            "`PhantomData<T>` ведёт себя как владение `T`, `PhantomData<&'a T>` — как заимствование, "
            "`PhantomData<*const T>` — как указатель, не связанный с потоками."
        ),
        example(
            "rust",
            """
            use std::marker::PhantomData;

            struct Handle<T> {
                raw: usize,
                _marker: PhantomData<T>,
            }

            impl<T> Handle<T> {
                fn new(raw: usize) -> Self {
                    Handle {
                        raw,
                        _marker: PhantomData,
                    }
                }
            }

            struct Borrowed<'a, T> {
                value: &'a T,
            }

            fn main() {
                let handle: Handle<String> = Handle::new(7);
                println!("{}", handle.raw);
                println!("размер Handle<String>: {}", std::mem::size_of::<Handle<String>>());
                println!("размер Borrowed: {}", std::mem::size_of::<Borrowed<i32>>());

                let number = 5;
                let borrowed = Borrowed { value: &number };
                println!("{}", borrowed.value);
            }
            """,
        ),
        text(
            "Вывод: `7`, `размер Handle<String>: 8`, `размер Borrowed: 8`, `5`. "
            "Маркер не занимает ни байта: структура из одного `usize` занимает восемь байт, "
            "а `Handle<String>` при этом считается владеющим `String`."
        ),
        heading("Типобезопасный построитель на маркерах", 3),
        text(
            "PhantomData позволяет кодировать состояние в самом типе. Построитель объявляет два "
            "маркерных параметра `HasName` и `HasAge` со значениями `No` или `Yes`. "
            "Метод `name` доступен только для `Builder<No, A>` и возвращает `Builder<Yes, A>`, "
            "метод `build` — только для `Builder<Yes, Yes>`, поэтому собрать объект без обязательных "
            "полей нельзя. Приём называют typed builder или type-state pattern; его минус — "
            "громоздкие сигнатуры, поэтому применяют его только там, где порядок шагов критичен."
        ),
        example(
            "rust",
            """
            use std::marker::PhantomData;

            struct Yes;
            struct No;

            struct Builder<HasName, HasAge> {
                name: Option<String>,
                age: Option<u32>,
                _state: PhantomData<(HasName, HasAge)>,
            }

            struct User {
                name: String,
                age: u32,
            }

            impl Builder<No, No> {
                fn new() -> Self {
                    Builder {
                        name: None,
                        age: None,
                        _state: PhantomData,
                    }
                }
            }

            impl<HasAge> Builder<No, HasAge> {
                fn name(self, name: &str) -> Builder<Yes, HasAge> {
                    Builder {
                        name: Some(String::from(name)),
                        age: self.age,
                        _state: PhantomData,
                    }
                }
            }

            impl<HasName> Builder<HasName, No> {
                fn age(self, age: u32) -> Builder<HasName, Yes> {
                    Builder {
                        name: self.name,
                        age: Some(age),
                        _state: PhantomData,
                    }
                }
            }

            impl Builder<Yes, Yes> {
                fn build(self) -> User {
                    User {
                        name: self.name.unwrap_or_default(),
                        age: self.age.unwrap_or_default(),
                    }
                }
            }

            fn main() {
                let user = Builder::new().age(30).name("Анна").build();
                println!("{} {}", user.name, user.age);
            }
            """,
        ),
        text(
            "Вывод: `Анна 30`. Порядок вызовов `age` и `name` не важен. "
            "А `Builder::new().build()` не скомпилируется: у `Builder<No, No>` нет метода `build`."
        ),
        callout(
            "warning",
            "Маркер влияет на удаление",
            "Если структура должна очищать ресурс, адресованный `T`, ей нужен `PhantomData<T>`, "
            "а не `PhantomData<&T>`: только владеющий маркер заставляет компилятор проверить, "
            "что `T` жив к моменту удаления. Неверный маркер приводит к ошибке времени жизни "
            "уже в коде пользователя, а не у вас.",
        ),
        heading("Автоматические трейты и их подавление"),
        text(
            "Трейты `Send`, `Sync`, `Unpin` компилятор выводит автоматически по составу полей. "
            "Сырые указатели `*const T` и `*mut T` не бывают `Send` и `Sync`: компилятор не знает, "
            "безопасно ли их разыменовывать в другом потоке. `PhantomData<*const T>` передаёт "
            "это свойство обёртке.\n\n"
            "Снять автоматический вывод помогает пустой тип `struct NoSend(PhantomData<*const u8>);`: "
            "он не станет `Send`, и компилятор не пустит его в поток. Обратное — объявить обёртку "
            "над указателем `Send` — делают только вручную через `unsafe impl Send`."
        ),
        example(
            "rust",
            """
            use std::marker::PhantomData;
            use std::thread;

            fn is_send<T: Send>() -> bool {
                true
            }

            struct Sendable(PhantomData<u8>);
            struct NotSendable(PhantomData<*const u8>);

            fn main() {
                println!("Sendable: {}", is_send::<Sendable>());
                let value = Sendable(PhantomData);
                thread::spawn(move || {
                    let _keep = value;
                })
                .join()
                .unwrap();
                println!("поток завершён");

                let guard = NotSendable(PhantomData);
                println!("{}", std::mem::size_of_val(&guard));
                // println!("{}", is_send::<NotSendable>()); // ошибка: не Send
            }
            """,
        ),
        text(
            "Вывод: `Sendable: true`, `поток завершён`, `0`. Маркерная структура не занимает памяти. "
            "Функция `is_send` проверяет ограничение на этапе компиляции: без комментария "
            "в последней строке сборка упадёт с ошибкой, что `NotSendable` нельзя передавать между потоками."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["`let s: str = ...` или `let v: [i32] = ...`", "E0277: размер не известен на этапе компиляции", "Хранить за указателем: `&str`, `Box<str>`, `Box<[i32]>`"],
                ["`Vec<dyn Shape>`", "Трейт-объект неразмерный", "`Vec<Box<dyn Shape>>` или дженерик-параметр"],
                ["`struct Handle<T> { raw: usize }`", "E0392: параметр `T` нигде не используется", "Добавить поле `_marker: PhantomData<T>`"],
                ["`type UserId = u64`", "Обёртка не защищает: `set_age(user_id)` компилируется", "Объявить `struct UserId(u64)`"],
                ["Трейт с `fn clone_all(&self) -> Self`", "Трейт не object-safe, `Box<dyn Trait>` не собирается", "Пометить `where Self: Sized` или вернуть `Box<dyn Trait>`"],
                ["`Arc<dyn Fn()>` для потока", "Ошибка `Send` или `Sync`", "`Arc<dyn Fn() + Send + Sync>`"],
                ["Короткоживущая ссылка в `struct Cache<T> { item: Option<T> }` через `&mut`", "Ошибка вариантости: требуется большее время жизни", "Хранить `T` целиком или использовать `PhantomData<&'a T>` в отдельной структуре"],
            ],
        ),
        heading("Практика"),
        text(
            "Создайте проект `cargo new types_lab` и выполняйте задания по порядку, запуская `cargo run`. "
            "Для первых трёх заданий достаточно одного `main`, остальные лучше разнести по модулям."
        ),
        numbered(
            "Реализуйте newtype `Email(String)` с приватным полем и конструктором `new(&str) -> Result<Email, String>`, который требует символ `@` и хотя бы один символ до него. Реализуйте `Display` и проверьте, что `Email::new(\"test@mail.ru\")` успешно, а `Email::new(\"mail.ru\")` возвращает ошибку.",
            "Объявите алиас `type Inventory = HashMap<String, u32>` и напишите функции `add_item`, `take_item` и `report`, принимающие `&mut Inventory`. Затем замените алиас на структуру `struct Inventory(HashMap<String, u32>)` и сравните объём изменений.",
            "Напишите функцию `describe<T: Display + ?Sized>(value: &T) -> String`, которая работает для `str`, `String`, `i32` и для `dyn Display`. Объясните, почему без `?Sized` часть вызовов не компилируется.",
            "Создайте трейт `Plugin` с методами `name(&self) -> &str` и `run(&self) -> String`, реализуйте его для двух структур и соберите из них `Vec<Box<dyn Plugin>>`. Добавьте вариант с `Arc<dyn Plugin + Send + Sync>` и запустите `run` в двух потоках.",
            "Постройте типобезопасный построитель `OrderBuilder` с маркерами `No` и `Yes` для обязательных полей `customer` и `items`. Метод `submit` должен быть доступен только для `OrderBuilder<Yes, Yes>`.",
        ),
        callout(
            "success",
            "Подсказка к заданию 1",
            "Проверяйте адрес символа через `find('@')` и сравнивайте с `Some(0)` и `None`, "
            "чтобы отсеять почту начинающуюся с символа или вообще без него. "
            "Поле сделайте приватным, иначе любой код сможет создать `Email` в обход проверки.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему `type UserId = u64` не защищает от перепутывания идентификатора и возраста, а `struct UserId(u64)` защищает?",
            "Почему функция с типом возврата `!` может стоять в ветке `match`, где ожидается `i32`?",
            "Сколько памяти занимает `&dyn Debug` на 64-битной платформе и из чего складывается этот размер?",
            "Что делает ограничение `?Sized` и почему его достаточно указывать только рядом со ссылкой или указателем?",
            "Почему `&mut T` инвариантен, а `&T` ковариантен?",
            "Зачем нужен `PhantomData`, если `T` всё равно не хранится в полях?",
        ),
        heading("Ответы", 3),
        numbered(
            "Алиас — второе имя того же типа, поэтому компилятор считает `UserId` и `u64` одним типом. Структура создаёт новый тип, и любая функция, ожидающая именно `UserId`, не примет `u64` или `Age`.",
            "Never-тип `!` обозначает отсутствие значения и совместим с любым типом: ветка, которая не возвращает управление, формально подходит под ожидаемый результат, и компилятор не требует завершения блока.",
            "Два слова, шестнадцать байт: адрес данных и указатель на vtable. Для `&str` и `&[T]` второе слово содержит длину, а не указатель на таблицу методов.",
            "`?Sized` снимает подразумеваемое ограничение `Sized` и разрешает передать неразмерный тип вроде `str` или `dyn Display`. Значение размера всё равно должно быть известно, поэтому оно живёт за указателем, и функция принимает ссылку.",
            "Через `&mut T` можно записать новое значение с другим временем жизни: если бы такая ссылка была ковариантной, короткоживущее значение попало бы в структуру с длинным временем жизни. Читающая `&T` не позволяет замены значения, поэтому сокращение времени жизни безопасно.",
            "Маркер сообщает компилятору, как структура относится к `T`: владеет, заимствует или не связан. От этого зависят вариантность, проверка удаления и автоматические `Send` и `Sync`. Без маркера компилятор выдаёт ошибку E0392.",
        ),
        heading("Итоги"),
        bullets(
            "Newtype-структура создаёт новый тип бесплатно по памяти и защищает от перепутывания значений; трейты `Deref` и `Add` возвращают удобство.",
            "`type` — только второе имя существующего типа, без проверки типов и без возможности писать `impl`.",
            "Never-тип `!` обозначает diverging-функции и совместим с любым типом; `Infallible` служит стабильной заменой в `Result`.",
            "`str`, `[T]` и `dyn Trait` — типы динамического размера; их хранят за ссылкой или умным указателем, который добавляет длину или vtable.",
            "`?Sized` снимает ограничение размера в дженериках, `Box<str>` и `Box<[T]>` хранят DST без лишней ёмкости.",
            "`Box<dyn Trait>` — единственный владелец, `Rc` делит чтение внутри потока, `Arc` — между потоками при `Send + Sync`.",
            "Вариантность: `&T`, `Box<T>`, `Rc<T>`, `Arc<T>` ковариантны, `&mut T`, `Cell<T>` и `*mut T` инвариантны, параметры `fn(T)` контрвариантны.",
            "`PhantomData<T>` задаёт отношение к параметру, а маркерные типы состояний позволяют ловить ошибки порядка вызовов на этапе компиляции.",
        ),
        heading("Что дальше"),
        text(
            "В следующем уроке вы перейдёте к дженерикам и трейтам в полном объёме: ограничения, "
            "ассоциированные типы, бланкетные реализации и правила coherence. "
            "`?Sized` понадобится в дженерик-функциях, трейт-объекты — при обсуждении динамической "
            "диспетчеризации, а newtype-обёртки — для обхода orphan rule."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "The Rust Programming Language, глава 19.4 «Advanced Types» — doc.rust-lang.org/book/ch19-04-advanced-types.html",
            "Rustonomicon: Subtyping and Variance — doc.rust-lang.org/nomicon/subtyping.html",
            "Справочник: Dynamically Sized Types — doc.rust-lang.org/reference/dynamically-sized-types.html",
            "Документация `std::marker::PhantomData` — doc.rust-lang.org/std/marker/struct.PhantomData.html",
            "Rust API Guidelines: Type Safety и newtype — rust-lang.github.io/api-guidelines/type-safety.html",
        ),
    ],
}
