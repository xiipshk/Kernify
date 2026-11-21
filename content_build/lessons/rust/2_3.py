"""Урок 3 курса rust: дженерики и трейты."""

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
    "topic_order": 3,
    "name": "2.3. Дженерики и трейты",
    "slug": "rust-2-3-дженерики-и-трейты",
    "short_description": (
        "Обобщённое программирование в Rust: параметры типов, ограничения трейтами, "
        "собственные и ассоциированные типы, динамическая диспетчеризация, coherence и sealed traits."
    ),
    "topic_name": "Дженерики и трейты",
    "topic_description": (
        "Подробный разбор дженериков и трейтов: синтаксис параметров типов, bounds, where-clauses, "
        "trait objects и dyn, associated types, реализация стандартных трейтов, правила сиротства, "
        "marker traits и закрытые иерархии трейтов."
    ),
    "learning_objectives": [
        "Объявлять дженерики: функции, структуры, перечисления, impl-блоки и методы",
        "Ограничивать параметры типов трейтами через `<T: Trait>` и `where`",
        "Определять собственные трейты с методами по умолчанию и реализовывать их",
        "Различать статическую и динамическую диспетчеризацию: `impl Trait` против `dyn Trait`",
        "Использовать ассоциированные типы и связанные константы в трейтах",
        "Понимать правила coherence и orphan rule, обходить их через newtype",
        "Применять бланкетные реализации и marker traits: `Send`, `Sync`, `Sized`, `Copy`",
        "Строить sealed traits для закрытия иерархии реализаций",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "rust",
        "дженерики",
        "трейты",
        "полиморфизм",
        "bounds",
        "dyn",
    ],
    "starter_code": code(
        r"""
        trait Shape {
            fn area(&self) -> f64;
            fn name(&self) -> String {
                String::from("фигура")
            }
        }

        struct Circle { radius: f64 }
        struct Rect { width: f64, height: f64 }

        impl Shape for Circle {
            fn area(&self) -> f64 {
                3.14159 * self.radius * self.radius
            }
            fn name(&self) -> String { String::from("круг") }
        }

        impl Shape for Rect {
            fn area(&self) -> f64 { self.width * self.height }
            fn name(&self) -> String { String::from("прямоугольник") }
        }

        fn describe<T: Shape>(item: &T) {
            println!("{}: площадь {:.2}", item.name(), item.area());
        }

        fn main() {
            describe(&Circle { radius: 2.0 });
            describe(&Rect { width: 3.0, height: 4.0 });
        }
        """
    ),
    "hints": [
        "Если функция принимает `T: Trait` по значению, она забирает владение. Для чтения берите `&T` или `&impl Trait`.",
        "`dyn Trait` требует размера, поэтому используйте ссылку `&dyn Trait` или указатель `Box<dyn Trait>`.",
        "Когда ограничений больше двух, переносите их в `where`-блок — так сигнатура читается легче.",
        "Orphan rule запрещает реализовывать чужой трейт для чужого типа. Оберните внешний тип в свою структуру (newtype).",
    ],
    "content": [
        text(
            "Дженерики и трейты — два механизма, на которых держится вся библиотечная часть Rust. "
            "Дженерики позволяют написать код один раз и использовать его для разных типов: "
            "`Vec<T>` из стандартной библиотеки хранит любой тип, не теряя при этом скорости. "
            "Трейты описывают поведение, которое тип обязан реализовать, — набор методов и связанных сущностей. "
            "Вместе они дают обобщённое программирование с проверкой на этапе компиляции.\n\n"
            "Главное отличие от динамических языков в том, что в Rust обобщение не означает потери "
            "производительности: компилятор создаёт специализированную версию функции для каждого "
            "конкретного типа вызывающего кода. При этом никакого общего «базового класса» не нужно. "
            "В этом уроке вы разберёте синтаксис дженериков, ограничения трейтами, собственные трейты, "
            "ассоциированные типы, динамическую диспетчеризацию, правила coherence и идиомы "
            "вроде бланкетных и закрытых трейтов.\n\n"
            "Материал рассчитан на уровень 2: предыдущие уроки про владение, заимствование и структуры "
            "уже знакомы. Примеры собраны так, чтобы их можно было запустить командой `cargo run` "
            "в пустом проекте: каждый пример — законченная программа с функцией `main`."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "объявлять дженерик-функции, структуры, перечисления и impl-блоки;",
            "ограничивать параметры типов трейтами через `<T: Trait>` и `where`-clauses;",
            "определять собственные трейты с методами по умолчанию и реализовывать их для своих типов;",
            "различать статическую и динамическую диспетчеризацию: `impl Trait` против `dyn Trait`;",
            "использовать ассоциированные типы и связанные константы для выражения связи типов;",
            "понимать правила coherence и orphan rule и обходить их через newtype-обёртку;",
            "применять бланкетные реализации и marker traits: `Send`, `Sync`, `Sized`, `Copy`;",
            "строить sealed traits, чтобы запретить внешние реализации.",
        ),
        heading("Обобщённые функции"),
        text(
            "Дженерик-функция принимает параметр типа, который записывается в угловых скобках после имени: "
            "`fn largest<T>(list: &[T]) -> &T`. Компилятор-моноформизатор (monomorphization) при сборке "
            "подставляет реальные типы в места вызова и генерирует отдельную машинную функцию для каждого набора "
            "параметров. Никаких проверок типов в рантайме, никакого боксинга — только статически известный код.\n\n"
            "Обратите внимание на ошибку, которую выдаст следующий пример без ограничения. "
            "Компилятор не знает, что значит «больше» для произвольного `T`, поэтому сравнение `>` требует, "
            "чтобы тип реализовывал трейт `PartialOrd`. Ошибка `binary operation cannot be applied to type T` "
            "возникает именно потому, что трейты в Rust явные: обобщённый код работает только с теми типами, "
            "для которых поведение гарантировано."
        ),
        example(
            "rust",
            """
            fn sum_pair<T: std::ops::Add<Output = T>>(a: T, b: T) -> T {
                a + b
            }

            fn largest<T: PartialOrd + Copy>(list: &[T]) -> T {
                let mut biggest = list[0];
                for &item in list.iter() {
                    if item > biggest {
                        biggest = item;
                    }
                }
                biggest
            }

            fn main() {
                println!("{}", sum_pair(2, 3));
                println!("{}", sum_pair(1.5, 2.25));
                println!("{}", largest(&[4, 9, 2, 7]));
                println!("{:?}", largest(&["kiwi", "apple", "pear"]));
            }
            """,
        ),
        text(
            "Вывод: 5, затем 3.75, затем 9 и \"pear\". Одна функция `largest` работает и для целых, "
            "и для строковых срезов, потому что `i32` и `&str` оба реализуют `PartialOrd` и `Copy` "
            "(`&str` — это ссылка на строковые данные, она копируется дёшево). Обратите внимание, "
            "что ограничение `Copy` нужно только потому, что мы копируем элемент из среза в переменную; "
            "с сигнатурой `-> &T` можно было бы обойтись только `PartialOrd`."
        ),
        heading("Дженерики в структурах и перечислениях"),
        text(
            "Параметр типа можно повесить на структуру и перечисление. Внутри impl-блока параметр указывается "
            "после `impl<T>`, чтобы компилятор понимал, к какому типу относятся методы. "
            "Если метод требует дополнительных возможностей от `T`, ограничение пишется прямо в `impl`.\n\n"
            "Часто удобно разделять блоки: общие методы доступны для любого `T`, а методы, которым нужно "
            "сравнение или вывод в консоль, — только для `T: PartialOrd` или `T: std::fmt::Debug`. "
            "Такое разделение даёт точные сообщения об ошибках: компилятор скажет, какое именно ограничение "
            "не выполнено."
        ),
        example(
            "rust",
            """
            struct Point<T> {
                x: T,
                y: T,
            }

            impl<T> Point<T> {
                fn new(x: T, y: T) -> Self {
                    Point { x, y }
                }

                fn swap(self) -> Point<T> {
                    Point { x: self.y, y: self.x }
                }
            }

            impl<T: std::fmt::Display> Point<T> {
                fn show(&self) {
                    println!("({}, {})", self.x, self.y);
                }
            }

            enum Either<L, R> {
                Left(L),
                Right(R),
            }

            impl<L: std::fmt::Debug, R: std::fmt::Debug> Either<L, R> {
                fn describe(&self) -> String {
                    match self {
                        Either::Left(value) => format!("левый {:?}", value),
                        Either::Right(value) => format!("правый {:?}", value),
                    }
                }
            }

            fn main() {
                let p = Point::new(1, 2);
                p.show();
                let q = Point::new(1.5, 2.5).swap();
                q.show();

                let values = vec![
                    Either::Left(10),
                    Either::Right("текст"),
                ];
                for value in &values {
                    println!("{}", value.describe());
                }
            }
            """,
        ),
        text(
            "Программа печатает `(1, 2)`, `(2.5, 1.5)`, затем `левый 10` и `правый \"текст\"`. "
            "Перечисление `Either<L, R>` — распространённый паттерн: он позволяет вернуть из функции "
            "одно из двух разных значений, не упаковывая их в `Box<dyn Any>`. "
            "Вектор `Vec<Either<i32, &str>>` при этом остаётся однородным, потому что варианты "
            "принадлежат одному типу."
        ),
        heading("Ограничения трейтами и where-клаузы"),
        text(
            "Ограничение трейтом (trait bound) говорит компилятору: параметр `T` может быть любым, "
            "но обязан реализовывать перечисленные трейты. Объявлять ограничения можно тремя способами: "
            "в inline-позиции `<T: Trait>`, через `where`-клаузу после сигнатуры или через `impl Trait` "
            "в позиции аргумента. Все три варианта эквивалентны по смыслу, различается только читаемость.\n\n"
            "Комбинировать ограничения можно оператором `+`: `T: Clone + Default`. "
            "Пустые ограничения через `?Sized` ослабляют неявное требование размера — об этом позже. "
            "Когда ограничений много, `where`-клауза почти всегда выигрывает у inline-формы: "
            "она позволяет разложить условия по строкам и не растягивает имя функции на пол-экрана."
        ),
        table(
            ["Форма", "Пример", "Когда выбирать"],
            [
                ["Inline bound", "`fn f<T: Clone>(x: T)`", "Одно-два ограничения на один параметр"],
                ["Where-клауза", "`fn f<T>(x: T) where T: Clone + Debug`", "Много ограничений или несколько параметров"],
                ["`impl Trait` в аргументе", "`fn f(x: impl Clone)`", "Функция не называет тип параметра в других позициях"],
                ["`impl Trait` в возврате", "`fn f() -> impl Iterator<Item = u8>`", "Скрыть конкретный тип результата"],
                ["`dyn Trait`", "`fn f(x: &dyn Clone)`", "Много разнотипных значений в одной коллекции"],
            ],
        ),
        example(
            "rust",
            """
            use std::fmt::Debug;

            #[derive(Debug)]
            struct Tag<'a> {
                name: &'a str,
            }

            fn render_inline<T: Debug + ToString>(value: &T) -> String {
                format!("inline: {}", value.to_string())
            }

            fn render_where<T>(value: &T) -> String
            where
                T: Debug + ToString,
            {
                format!("where: {:?}", value)
            }

            fn render_impl(value: &impl ToString) -> String {
                format!("impl: {}", value.to_string())
            }

            fn main() {
                let tag = Tag { name: "alpha" };
                println!("{}", render_inline(&tag));
                println!("{}", render_where(&tag));
                println!("{}", render_impl(&tag));
            }
            """,
        ),
        text(
            "Все три функции принимают ссылку на `Tag` и печатают строку. Вывод: "
            "`inline: Tag { name: \"alpha\" }`, `where: Tag { name: \"alpha\" }`, "
            "`impl: Tag { name: \"alpha\" }`. Разные префиксы нужны только для наглядности: "
            "с точки зрения компилятора это одинаковые обобщённые функции после подстановки типа."
        ),
        heading("Собственные трейты"),
        text(
            "Трейт — это контракт поведения. Он объявляет методы, которые тип обязуется предоставить, "
            "и может содержать реализации по умолчанию. Тип получает поведение через `impl Trait for Type`. "
            "Методы по умолчанию переопределяются при необходимости, а обязательные методы без тела "
            "должны быть реализованы, иначе компилятор сообщит `not all trait items implemented`.\n\n"
            "Внутри трейта методы видят `self` с любым режимом: `&self` для чтения, `&mut self` для изменения, "
            "`self` для потребления. Метод по умолчанию может вызывать обязательный метод, "
            "и тогда конкретная реализация может ограничиться минимумом кода. "
            "Статические методы без `self` (ассоциированные функции) тоже допустимы, например конструкторы."
        ),
        example(
            "rust",
            """
            trait Printable {
                fn summary(&self) -> String;

                fn print_card(&self) {
                    println!("[карточка] {}", self.summary());
                }
            }

            struct User {
                login: String,
                age: u8,
            }

            impl Printable for User {
                fn summary(&self) -> String {
                    format!("{} ({} лет)", self.login, self.age)
                }
            }

            struct Guest;

            impl Printable for Guest {
                fn summary(&self) -> String {
                    String::from("гость-аноним")
                }

                fn print_card(&self) {
                    println!("[карточка] анонимный доступ");
                }
            }

            fn main() {
                let user = User { login: String::from("ivan"), age: 30 };
                let guest = Guest;

                user.print_card();
                guest.print_card();
            }
            """,
        ),
        text(
            "Вывод: `[карточка] ivan (30 лет)` и `[карточка] анонимный доступ`. "
            "Метод `print_card` объявлен один раз и подходит всем реализациям, "
            "а `Guest` переопределил его, потому что для анонимного пользователя формат отличается. "
            "Это типичный приём: выносить общую логику в трейт, а специфику оставлять реализациям."
        ),
        heading("Ассоциированные типы и константы"),
        text(
            "Ассоциированный тип — это «слот» в трейте, который заполняет каждая реализация. "
            "Он выражает более тесную связь, чем параметр типа: у одной реализации `Iterator` "
            "есть ровно один `Item`, и он не может варьироваться между вызовами. "
            "Запись `Self::Item` в сигнатуре метода означает «тот тип, который выбрал конкретный тип».\n\n"
            "Сравните с дженериком `trait Into2<T>`: там `T` — свободный параметр, и один тип может "
            "реализовать трейт несколько раз для разных `T` (именно так устроен `From`). "
            "Ассоциированный тип, наоборот, всегда один, зато его не нужно указывать в каждом bound: "
            "пишут `I: Iterator<Item = u32>`, и компилятор знает, какие значения выдаёт итератор. "
            "Связанные константы работают так же — их значение фиксируется на этапе реализации."
        ),
        example(
            "rust",
            """
            trait Counter {
                const LIMIT: u32;
                type Output;

                fn label(&self) -> String;
                fn convert(&self, value: u32) -> Self::Output;
            }

            struct Small;
            struct Big;

            impl Counter for Small {
                const LIMIT: u32 = 10;
                type Output = u8;

                fn label(&self) -> String {
                    format!("малый счётчик, лимит {}", Self::LIMIT)
                }

                fn convert(&self, value: u32) -> Self::Output {
                    value as u8
                }
            }

            impl Counter for Big {
                const LIMIT: u32 = 1_000_000;
                type Output = u64;

                fn label(&self) -> String {
                    format!("большой счётчик, лимит {}", Self::LIMIT)
                }

                fn convert(&self, value: u32) -> Self::Output {
                    value as u64
                }
            }

            fn report<C>(counter: &C, values: &[u32])
            where
                C: Counter,
                C::Output: std::fmt::Debug,
            {
                println!("{}", counter.label());
                let converted: Vec<C::Output> =
                    values.iter().map(|&v| counter.convert(v)).collect();
                println!("{:?}", converted);
            }

            fn main() {
                report(&Small, &[1, 2, 3]);
                report(&Big, &[1, 2, 3]);
            }
            """,
        ),
        text(
            "Вывод: `малый счётчик, лимит 10`, `[1, 2, 3]`, затем `большой счётчик, лимит 1000000` "
            "и снова `[1, 2, 3]`. Сам массив значений одинаковый, но тип результата `convert` "
            "различается для каждой реализации: `u8` у `Small` и `u64` у `Big`. "
            "Обратите внимание на ограничение `C::Output: Debug` — у ассоциированного типа тоже могут быть bounds."
        ),
        callout(
            "info",
            "Когда выбирать ассоциированный тип, а когда параметр",
            "Ассоциированный тип подходит, если у реализации ровно одна версия характеристики: элемент итератора, тип ошибки, тип ключа. "
            "Параметр типа нужен, если одна реализация должна поддерживать несколько вариантов сразу: `From<i32>`, `From<u8>`, `From<&str>`.",
        ),
        heading("Статическая и динамическая диспетчеризация"),
        text(
            "Дженерики решают задачу обобщения статически: конкретный тип известен на этапе компиляции, "
            "моноформизация создаёт отдельный код, вызовы методов встраиваются (inline). Это максимально быстро, "
            "но увеличивает размер бинарника и требует однородности типов в коллекциях. "
            "Когда нужно хранить в одном `Vec` значения разных типов, используют трейт-объекты `dyn Trait`.\n\n"
            "`dyn Trait` — это тип-указатель с виртуальной таблицей (vtable). Вызов метода проходит "
            "через таблицу, поэтому стоит небольших накладных расходов, зато конкретный тип скрыт. "
            "Так как `dyn Trait` — тип динамического размера (DST), его нельзя использовать по значению: "
            "берите `&dyn Trait`, `Box<dyn Trait>`, `Rc<dyn Trait>` или `Arc<dyn Trait>`. "
            "Трейт должен быть object-safe: без обобщённых методов, без `Self` в возвращаемом типе, "
            "без методов, возвращающих `Self`."
        ),
        table(
            ["Подход", "Когда тип известен", "Стоимость вызова", "Где хранится"],
            [
                ["`fn f<T: Trait>(x: T)`", "При компиляции", "Нулевая, часто inline", "Стек, без указателя"],
                ["`fn f(x: impl Trait)`", "При компиляции", "Нулевая, часто inline", "Стек, без указателя"],
                ["`fn f(x: &dyn Trait)`", "В рантайме", "Косвенный вызов через vtable", "Ссылка на существующее значение"],
                ["`Box<dyn Trait>`", "В рантайме", "Косвенный вызов плюс аллокация", "Куча"],
            ],
        ),
        example(
            "rust",
            """
            trait Shape {
                fn area(&self) -> f64;
                fn name(&self) -> &'static str;
            }

            struct Circle { radius: f64 }
            struct Square { side: f64 }
            struct Triangle { base: f64, height: f64 }

            impl Shape for Circle {
                fn area(&self) -> f64 { std::f64::consts::PI * self.radius * self.radius }
                fn name(&self) -> &'static str { "круг" }
            }

            impl Shape for Square {
                fn area(&self) -> f64 { self.side * self.side }
                fn name(&self) -> &'static str { "квадрат" }
            }

            impl Shape for Triangle {
                fn area(&self) -> f64 { self.base * self.height / 2.0 }
                fn name(&self) -> &'static str { "треугольник" }
            }

            fn static_area(shape: &impl Shape) -> f64 {
                shape.area()
            }

            fn total_dynamic(shapes: &[Box<dyn Shape>]) -> f64 {
                shapes.iter().map(|s| s.area()).sum()
            }

            fn main() {
                let circle = Circle { radius: 1.0 };
                println!("{}: {:.2}", circle.name(), static_area(&circle));

                let shapes: Vec<Box<dyn Shape>> = vec![
                    Box::new(Circle { radius: 1.0 }),
                    Box::new(Square { side: 2.0 }),
                    Box::new(Triangle { base: 4.0, height: 3.0 }),
                ];

                for shape in &shapes {
                    println!("{}: {:.2}", shape.name(), shape.area());
                }
                println!("итого: {:.2}", total_dynamic(&shapes));
            }
            """,
        ),
        text(
            "Вывод: `круг: 3.14`, затем `круг: 3.14`, `квадрат: 4.00`, `треугольник: 6.00` "
            "и `итого: 13.14`. Функция `static_area` мономорфизируется под один тип, а `total_dynamic` "
            "работает с любым набором фигур благодаря трейт-объектам. "
            "Фигуры разных типов лежат в одном векторе, потому что `Box<dyn Shape>` стирает конкретный тип, "
            "сохраняя только путь к его виртуальной таблице."
        ),
        callout(
            "warning",
            "`dyn Trait` по значению не компилируется",
            "Запись `fn f(shape: dyn Shape)` вызовет ошибку `the size for values of type dyn Shape cannot be known at compilation time`. "
            "Всегда используйте указатель: `&dyn Shape`, `Box<dyn Shape>`. Дополнительно добавляйте `+ Send + Sync`, если значение может переехать в другой поток.",
        ),
        heading("Реализация стандартных трейтов"),
        text(
            "Стандартная библиотека определяет десятки трейтов, которые стоит реализовать для своих типов: "
            "`Display` и `Debug` для печати, `From` и `Into` для преобразований, `Iterator` для обхода, "
            "`Default` для значений по умолчанию, `PartialEq`, `PartialOrd`, `Hash` для сравнений и "
            "использования в коллекциях, `Drop` для освобождения ресурсов.\n\n"
            "Для многих из них есть вывод через атрибут `#[derive(...)]`: он генерирует реализацию по полям. "
            "`Display` не выводится автоматически, потому что формат зависит от смысла типа: "
            "как именно показывать сумму, дату или пользователя, решает автор. "
            "Если реализовать `Display`, то `ToString` и `to_string()` появляются у типа автоматически "
            "благодаря бланкетной реализации в стандартной библиотеке."
        ),
        example(
            "rust",
            """
            use std::fmt;

            #[derive(Debug, Clone, PartialEq, Default)]
            struct Money {
                cents: i64,
            }

            impl Money {
                fn new(cents: i64) -> Self {
                    Money { cents }
                }

                fn dollars(&self) -> f64 {
                    self.cents as f64 / 100.0
                }
            }

            impl fmt::Display for Money {
                fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                    write!(f, "{}.{:02} $", self.cents / 100, (self.cents % 100).abs())
                }
            }

            impl From<i64> for Money {
                fn from(cents: i64) -> Self {
                    Money::new(cents)
                }
            }

            fn main() {
                let price = Money::from(1999);
                let tax = Money::new(300);
                let empty = Money::default();

                println!("цена: {}", price);
                println!("с налогом: {}", Money::new(price.cents + tax.cents));
                println!("доллары: {:.2}", price.dollars());
                println!("пусто: {:?}", empty);
                println!("равны: {}", price == Money::from(1999));
                println!("строка: {}", price.to_string());
            }
            """,
        ),
        text(
            "Вывод: `цена: 19.99 $`, `с налогом: 22.99 $`, `доллары: 19.99`, "
            "`пусто: Money { cents: 0 }`, `равны: true`, `строка: 19.99 $`. "
            "Реализация `From<i64>` дала бесплатно метод `into()`, а реализация `Display` — метод `to_string()`. "
            "Атрибут `#[derive(Debug, Clone, PartialEq, Default)]` сгенерировал четыре реализации по полям."
        ),
        heading("Coherence, orphan rule и newtype"),
        text(
            "Правило сиротства (orphan rule) гарантирует, что реализации трейта не конфликтуют между крейтами: "
            "реализовать трейт можно, только если хотя бы одна из сторон — трейт или тип — объявлена в вашем крейте. "
            "Вместе с запретом перекрывающихся реализаций (coherence) это значит, что для пары «тип, трейт» "
            "реализация ровно одна и она известна компилятору глобально.\n\n"
            "Отсюда четыре комбинации: свой трейт для своего типа — можно; чужой трейт для своего типа — можно "
            "(`impl std::fmt::Display for Money`); свой трейт для чужого типа — можно, но только для локальных "
            "типов из вашего крейта — см. предостережение ниже; чужой трейт для чужого типа — нельзя. "
            "На практике хочется реализовать `Display` для `Vec<i32>` или `From<MyError>` для `String`, "
            "но оба варианта запрещены. Обходной путь — newtype: тонкая обёртка из одного поля."
        ),
        example(
            "rust",
            """
            use std::fmt;

            struct Meters(f64);
            struct Celsius(f64);

            impl fmt::Display for Meters {
                fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                    write!(f, "{} м", self.0)
                }
            }

            impl std::ops::Add for Meters {
                type Output = Meters;

                fn add(self, other: Meters) -> Meters {
                    Meters(self.0 + other.0)
                }
            }

            impl Celsius {
                fn to_fahrenheit(&self) -> f64 {
                    self.0 * 9.0 / 5.0 + 32.0
                }
            }

            impl fmt::Display for Celsius {
                fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                    write!(f, "{} °C, это {:.1} °F", self.0, self.to_fahrenheit())
                }
            }

            fn main() {
                let a = Meters(1.5);
                let b = Meters(2.25);
                println!("{}", a + b);

                let t = Celsius(21.0);
                println!("{}", t);

                let plain = 100.0_f64;
                println!("без обёртки: {}", plain);
            }
            """,
        ),
        text(
            "Вывод: `3.75 м` и `21 °C, это 69.8 °F`, затем `без обёртки: 100`. "
            "Обе обёртки — структуры с одним полем, поэтому занимают столько же памяти, что и внутреннее значение. "
            "Дополнительное преимущество newtype в том, что он защищает от смешения единиц: "
            "`Meters` и `f64` — разные типы, и сложить метры с секундами случайно не получится."
        ),
        callout(
            "danger",
            "Нельзя реализовать чужой трейт для чужого типа",
            "Код `impl fmt::Display for Vec<i32> { }` падает с ошибкой `E0117: only traits defined in the current crate can be implemented for types defined outside of the crate` (нарушение orphan rule). "
            "Используйте обёртку `struct MyVec(Vec<i32>)` и реализуйте `Display` для неё. "
            "Если `MyVec` реализует `Deref<Target = Vec<i32>>`, методы вектора останутся доступными.",
        ),
        heading("Бланкетные реализации и blanket impls"),
        text(
            "Бланкетная реализация — это `impl<T: Trait> Trait2 for T`, то есть реализация для всех типов, "
            "удовлетворяющих условию. Так устроены `ToString` (для любого `T: Display`) и `Into` "
            "(для любого `T`, у которого есть `From<T>`). Свои бланкетные реализации полезны, когда вы хотите "
            "бесплатно дать всем совместимым типам готовое поведение.\n\n"
            "Ограничение одно: такие реализации очень жадные. Если объявить `impl<T> MyMarker for T {}`, "
            "тот же трейт нельзя будет реализовать для конкретного типа отдельно — получится `conflicting implementations`. "
            "Кроме того, бланкетный impl на чужом трейте нарушает orphan rule. "
            "Поэтому на практике бланкетные реализации пишут в своих крейтах и с минимальным набором ограничений."
        ),
        example(
            "rust",
            """
            trait Description {
                fn describe(&self) -> String;
            }

            trait Tagged {
                fn tag(&self) -> &'static str;
            }

            impl<T: std::fmt::Display> Description for T {
                fn describe(&self) -> String {
                    format!("значение {}", self)
                }
            }

            impl<T: Tagged> Description for T {
                fn describe(&self) -> String {
                    format!("тег {}", self.tag())
                }
            }

            struct Device;
            """
        ),
        heading("Дженерики в методах и типах ошибок"),
        text(
            "Обобщённая функция может возвращать `Result<T, E>` и принимать преобразование ошибок. "
            "Так устроены библиотеки: `File::open` возвращает `Result<File, io::Error>`, "
            "а функция пользователя может объявить `E: From<io::Error>`, чтобы ошибка ввода-вывода "
            "автоматически конвертировалась в общий тип ошибки приложения.\n\n"
            "Благодаря бланкетной реализации `impl<T, U> Into<U> for T where U: From<T>` "
            "и методу `map_err` получается чистый код без ручных `match` на каждую ошибку. "
            "Ограничение `E: From<io::Error>` — это и есть обобщённая обработка: функция не привязана "
            "к конкретному типу ошибки, но компилятор проверяет, что преобразование существует."
        ),
        example(
            "rust",
            """
            use std::error::Error;
            use std::fmt;
            use std::num::ParseIntError;

            #[derive(Debug)]
            enum ConfigError {
                Missing,
                BadNumber(ParseIntError),
            }

            impl fmt::Display for ConfigError {
                fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                    match self {
                        ConfigError::Missing => write!(f, "нет значения"),
                        ConfigError::BadNumber(e) => write!(f, "не число: {}", e),
                    }
                }
            }

            impl Error for ConfigError {
                fn source(&self) -> Option<&(dyn Error + 'static)> {
                    match self {
                        ConfigError::BadNumber(e) => Some(e),
                        ConfigError::Missing => None,
                    }
                }
            }

            impl From<ParseIntError> for ConfigError {
                fn from(e: ParseIntError) -> Self {
                    ConfigError::BadNumber(e)
                }
            }

            fn read_limit<E: From<ParseIntError>>(value: Option<&str>) -> Result<u32, E> {
                let raw = value.ok_or_else(|| String::from("пусто"))?;
                let parsed: u32 = raw.parse()?;
                Ok(parsed)
            }

            fn run() -> Result<(), ConfigError> {
                let limit = read_limit(Some("128"))?;
                println!("лимит {}", limit);
                let bad = read_limit::<ConfigError>(Some("сто"))?;
                println!("{}", bad);
                Ok(())
            }

            fn main() {
                runner();
            }

            fn runner() {
                match run() {
                    Ok(()) => println!("готово"),
                    Err(e) => println!("ошибка: {}", e),
                }
            }
            """,
        ),
        text(
            "Программа печатает `лимит 128`, затем `ошибка: не число: invalid digit found in string` "
            "и не доходит до строки `готово`, потому что оператор `?` вернул ошибку из `run`. "
            "Функция `read_limit` обобщена по типу ошибки: она вернёт `Result<u32, E>` для любого `E`, "
            "в который умеет превращаться `ParseIntError`."
        ),
        heading("Marker traits и ограничения размера"),
        text(
            "Marker traits (трейты-маркеры) не содержат методов, их смысл — в самом факте реализации. "
            "Компилятор проверяет маркеры на этапе компиляции и переносит решение с рантайма на сборку. "
            "Самые важные из них: `Sized` (размер известен на этапе компиляции), `Send` (значение можно "
            "передать в другой поток), `Sync` (ссылку на значение можно передать в другой поток), "
            "`Copy` (побитовое копирование вместо перемещения), `Unpin` (значение можно безопасно двигать "
            "по памяти, что важно для `Pin`).\n\n"
            "`Sized` неявно подставляется во все параметры типов. Для работы с DST вроде `str`, `[T]`, "
            "`dyn Trait` используют ослабление `?Sized`. `Send` и `Sync` выводятся автоматически: "
            "структура из `Send`-полей сама становится `Send`. Если нужно запретить автоматический вывод, "
            "поле-маркер `PhantomData` с типом `Rc<()>` или `*const ()` лишает тип `Send` и `Sync`."
        ),
        table(
            ["Трейт", "Что означает", "Как ослабить"],
            [
                ["`Sized`", "Размер известен при компиляции", "`T: ?Sized` в bound"],
                ["`Send`", "Значение переносимо между потоками", "Поле `PhantomData<Rc<()>>`"],
                ["`Sync`", "Ссылки переносимы между потоками", "Поле `PhantomData<Cell<()>>`"],
                ["`Copy`", "Неявное побитовое копирование", "Не реализовывать, а только `Clone`"],
                ["`Unpin`", "Значение можно свободно перемещать в памяти", "Поле `PhantomPinned`"],
            ],
        ),
        example(
            "rust",
            """
            use std::marker::PhantomData;
            use std::rc::Rc;

            struct Shared {
                value: i32,
            }

            struct NotSync {
                value: i32,
                marker: PhantomData<std::cell::Cell<()>>,
            }

            fn requires_send<T: Send>(_: &T) -> &'static str {
                "тип Send"
            }

            fn requires_sized<T: Sized>(_: &T) -> &'static str {
                "тип Sized"
            }

            fn take_slice<T: ?Sized>(_: &T) -> &'static str {
                "размер не важен"
            }

            fn accepts_any<T: ?Sized + std::fmt::Debug>(value: &T) -> String {
                format!("{:?}", value)
            }

            fn main() {
                let shared = Shared { value: 7 };
                println!("{}", requires_send(&shared));
                println!("{}", requires_sized(&shared));
                println!("{}", take_slice(&shared));

                let text_ref: &str = "строка динамической длины";
                println!("{}", take_slice(text_ref));
                println!("{}", accepts_any(text_ref));
                println!("{}", accepts_any(&[1, 2, 3][..]));

                let count: usize = std::mem::size_of::<Shared>();
                println!("размер Shared: {} байт", count);
                let _suppress = Rc::new(NotSync { value: 1, marker: PhantomData });
            }
            """,
        ),
        text(
            "Вывод: `тип Send`, `тип Sized`, `размер не важен`, `размер не важен`, "
            "`\"строка динамической длины\"`, `[1, 2, 3]`, `размер Shared: 4 байт`. "
            "Функция `accepts_any` принимает и `&str`, и срез `[i32]`, потому что у параметра стоит `?Sized`. "
            "Структура `NotSync` содержит `PhantomData<Cell<()>>` и поэтому не является `Sync`, "
            "хотя и создаётся в этом примере без конфликтов."
        ),
        heading("Sealed traits"),
        text(
            "Иногда трейт нужен публично для чтения или вызовов, но реализовывать его должны только типы из вашего крейта. "
            "Причина — инварианты: если посторонний крейт реализует `Database`, ваш код может получить "
            "некорректную реализацию. Orphan rule такую ситуацию не запрещает: трейт ваш, значит реализовать его "
            "может кто угодно.\n\n"
            "Паттерн sealed trait решает задачу: публичный трейт объявляет ограничение на приватный трейт "
            "`Sealed`, который виден только внутри модуля. Внешний код не может назвать `Sealed`, "
            "а значит и реализовать публичный трейт не сможет. Компилятор при этом остаётся доволен: "
            "все реализации находятся в вашем крейте."
        ),
        example(
            "rust",
            """
            mod sealed {
                pub trait Sealed {}
                pub fn is_sealed() -> bool {
                    true
                }
            }

            pub trait Report: sealed::Sealed {
                fn line(&self) -> String;

                fn print(&self) {
                    println!("{}", self.line());
                }
            }

            pub struct JsonReport;
            pub struct CsvReport;

            impl sealed::Sealed for JsonReport {}
            impl Report for JsonReport {
                fn line(&self) -> String {
                    String::from("{\"status\":\"ok\"}")
                }
            }

            impl sealed::Sealed for CsvReport {}
            impl Report for CsvReport {
                fn line(&self) -> String {
                    String::from("status;ok")
                }
            }

            pub fn make(kind: &str) -> Box<dyn Report> {
                match kind {
                    "json" => Box::new(JsonReport),
                    _ => Box::new(CsvReport),
                }
            }

            fn main() {
                println!("sealed: {}", sealed::is_sealed());
                for kind in ["json", "csv"] {
                    make(kind).print();
                }
            }
            """,
        ),
        text(
            "Вывод: `sealed: true`, `{\"status\":\"ok\"}`, `status;ok`. "
            "Внешний крейт мог бы вызвать `Report::print`, но не смог бы написать `impl Report for MyType`, "
            "потому что `sealed::Sealed` скрыт за границей приватности модуля. "
            "Заодно функция `make` возвращает `Box<dyn Report>`, что демонстрирует сочетание закрытого трейта с трейт-объектом."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["`impl Display for Vec<i32>`", "E0117: нарушение orphan rule", "Обернуть в `struct MyVec(Vec<i32>)` и реализовать трейт для обёртки"],
                ["Сравнение `>` без `PartialOrd`", "Оператор не применим к типу `T`", "Добавить bound `T: PartialOrd`"],
                ["`Vec<dyn Shape>`", "DST нельзя хранить по значению", "`Vec<Box<dyn Shape>>` или дженерик-параметр"],
                ["Свой трейт с методом `fn make() -> Self` для `Box<dyn Trait>`", "Трейт не object-safe", "Убрать `Self` из возвращаемого типа или вернуть `Box<Self>` с `where Self: Sized`"],
                ["`impl<T> MyTrait for T {}` плюс `impl MyTrait for u8 {}`", "Конфликтующие реализации", "Сузить бланкетный impl ограничением или использовать отдельный трейт"],
                ["`T` в структуре, который не используется в полях", "E0392: параметр не используется", "Добавить `PhantomData<T>`"],
                ["Много ограничений в inline-форме", "Сигнатура нечитаема", "Вынести условия в `where`-клаузу"],
            ],
        ),
        heading("Практика"),
        text(
            "Создайте проект командой `cargo new generics_lab` и выполняйте задания по порядку. "
            "Сборка: `cargo run`. Отключать предупреждения не нужно — они подсказывают, где код можно улучшить."
        ),
        numbered(
            "Напишите дженерик-функцию `max_by<T, F>(items: &[T], key: F) -> Option<&T>`, где `F: Fn(&T) -> i32`. Функция возвращает элемент с наибольшим ключом. Проверьте её на строках (ключ — длина) и на структурах `Employee { name, salary }`.",
            "Определите трейт `Area` с методом `area(&self) -> f64` и методом по умолчанию `is_larger_than(&self, other: &impl Area) -> bool`. Реализуйте трейт для `Circle`, `Rect` и `Triangle`.",
            "Сделайте трейт `Stack` с ассоциированным типом `Item`, методами `push(&mut self, item: Self::Item)` и `pop(&mut self) -> Option<Self::Item>`, а также методом `len`. Реализуйте его для структуры `FixedStack<T, const N: usize>` на основе массива.",
            "Определите трейт `Validation` и реализуйте его для newtype-обёрток `Email(String)`, `Age(u8)` и `Username(String)`. Funktsiya `validate_all` должна принимать `&[Box<dyn Validation>]` и возвращать список ошибок.",
            "Сделайте sealed trait `PaymentMethod` с приватным трейтом `Sealed` и двумя публичными реализациями `Card` и `Cash`. Попробуйте во втором крейте реализовать `PaymentMethod` для своей структуры и объясните ошибку компилятора.",
        ),
        callout(
            "success",
            "Подсказка к заданию 3",
            "Константный параметр `const N: usize` позволяет хранить данные в `[Option<T>; N]`. Инициализируйте массив через `std::array::from_fn(|_| None)` и отслеживайте текущую длину в поле `len`.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем `fn f(x: impl Trait)` отличается от `fn f(x: &dyn Trait)` с точки зрения производительности и размера бинарника?",
            "Зачем нужен ассоциированный тип `Item` в трейте `Iterator`, если можно было сделать параметр `Iterator<T>`?",
            "Почему нельзя написать `impl std::fmt::Display for Vec<String>` в своём крейте и как это обойти?",
            "Что такое sealed trait и какую проблему он решает?",
            "Почему для `Vec<dyn Shape>` компилятор выдаёт ошибку размера?",
            "Что произойдёт, если объявить бланкетный `impl<T> MyTrait for T {}` и одновременно `impl MyTrait for u8 {}`?",
        ),
        heading("Ответы", 3),
        numbered(
            "`impl Trait` подставляет конкретный тип на этапе компиляции: вызов обычно встраивается, но для каждого типа генерируется своя копия кода. `&dyn Trait` работает через vtable в рантайме: одна копия кода, чуть большая стоимость вызова и меньше размер бинарника.",
            "Параметр `Iterator<T>` допускал бы несколько реализаций для одного типа и требовал бы указывать `T` в каждом ограничении. Ассоциированный тип фиксирует ровно один элемент на итератор и позволяет писать `I: Iterator<Item = u8>` без лишних переменных.",
            "Orphan rule разрешает реализацию, только если хотя бы трейт или тип объявлены в вашем крейте. `Display` и `Vec` чужие. Обход — newtype-обёртка `struct MyVec(Vec<String>)`, для которой реализуется `Display`.",
            "Sealed trait — публичный трейт с ограничением на приватный `Sealed`. Такой трейт можно вызывать, но нельзя реализовать вне крейта. Это защищает инварианты библиотеки от сторонних, потенциально некорректных реализаций.",
            "`dyn Shape` — тип динамического размера, его размер известен только через vtable. Вектор требует одинакового фиксированного размера элементов, поэтому используют `Box<dyn Shape>` или ссылки.",
            "Компилятор вернёт ошибку `conflicting implementations of trait MyTrait for type u8`: бланкетная реализация уже покрывает `u8`. Нужно сузить ограничение бланкетного impl или разделить поведение на два трейта.",
        ),
        heading("Итоги"),
        bullets(
            "Дженерики подставляются на этапе компиляции через моноформизацию: один источник кода, отдельная машинная версия для каждого типа.",
            "Ограничения трейтами пишутся inline (`<T: Trait>`), через `where`-клаузу или `impl Trait` в аргументе; все три формы эквивалентны.",
            "Трейт описывает контракт с обязательными методами и методами по умолчанию, а `impl Trait for Type` связывает тип с контрактом.",
            "Ассоциированные типы фиксируют ровно одну характеристику на реализацию, параметры типа допускают несколько реализаций.",
            "`impl Trait` даёт статическую диспетчеризацию без накладных расходов, `&dyn Trait` и `Box<dyn Trait>` — динамическую для разнородных коллекций.",
            "Orphan rule и coherence гарантируют единственность реализаций; обход — newtype-обёртки.",
            "Marker traits `Sized`, `Send`, `Sync`, `Copy`, `Unpin` проверяются компилятором и управляют безопасностью и переносимостью между потоками.",
            "Sealed trait ограничивает набор реализаций вашим крейтом, защищая инварианты публичного API.",
        ),
        heading("Что дальше"),
        text(
            "Дженерики и трейты теперь знакомы в базовом объёме. Следующий шаг — итераторы и функциональный стиль: "
            "вы увидите, что `Iterator`, `Map` и `Filter` устроены ровно на тех механизмах, которые разобраны здесь. "
            "Затем перейдёте к обработке ошибок через `Result` и собственные типы ошибок, "
            "где пригодятся `From`, `Error` и трейт-объекты."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "The Rust Programming Language, глава 10 «Generic Types, Traits, and Lifetimes» — doc.rust-lang.org/book/ch10-00-generics.html",
            "Rust by Example: Traits и Generics — doc.rust-lang.org/rust-by-example/trait.html",
            "Справочник языка: Implementations и orphan rules — doc.rust-lang.org/reference/items/implementations.html",
            "RFC 2451: re-rebalancing coherence — rust-lang.github.io/rfcs/2451-re-rebalancing-coherence.html",
            "Документация `std::marker`: Send, Sync, Sized, Unpin — doc.rust-lang.org/std/marker/",
        ),
    ],
}
