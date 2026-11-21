"""Урок 3.5 курса Rust: внутреннее устройство асинхронности."""

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
    "topic_order": 5,
    "name": "3.5. Внутреннее устройство асинхронности",
    "slug": "rust-3-5-внутреннее-устройство-асинхронности",
    "short_description": (
        "Как компилятор превращает async fn в конечный автомат, зачем нужны Future, "
        "Pin и Waker, и как собрать собственный executor из очереди задач и готовых примитивов."
    ),
    "topic_name": "Внутреннее устройство асинхронности",
    "topic_description": (
        "Разбор механизма асинхронности Rust на уровне стандартной библиотеки: "
        "трейт Future и тип Poll, контракт опроса, самоссылающиеся состояния и Pin, "
        "пробуждение задач через Waker, устройство executor и сочетание futures."
    ),
    "learning_objectives": [
        "Проследить, как async fn превращается в конечный автомат с точками приостановки",
        "Реализовать трейт Future вручную и соблюсти контракт метода poll",
        "Объяснить, почему состояние задачи нельзя перемещать в памяти, и применять Pin",
        "Настроить пробуждение задачи через Waker и Context",
        "Собрать минимальный executor с очередью готовых задач и функцией block_on",
        "Объединять несколько futures через join, select и тайм-аут",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "rust",
        "async",
        "future",
        "pin",
        "waker",
        "executor",
    ],
    "starter_code": code(
        r"""
        use std::future::Future;
        use std::pin::Pin;
        use std::task::{Context, Poll};
        use std::thread;
        use std::time::{Duration, Instant};

        /// Ждёт заданную паузу, не занимая поток.
        struct Delay {
            deadline: Instant,
        }

        impl Delay {
            fn new(ms: u64) -> Self {
                Delay { deadline: Instant::now() + Duration::from_millis(ms) }
            }
        }

        impl Future for Delay {
            type Output = ();

            fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
                if Instant::now() >= self.deadline {
                    Poll::Ready(())
                } else {
                    // Просим executor опросить задачу снова позже.
                    cx.waker().wake_by_ref();
                    thread::sleep(Duration::from_millis(10));
                    Poll::Pending
                }
            }
        }

        fn main() {
            let mut fut = std::pin::pin!(Delay::new(50));
            let mut cx = Context::from_waker(std::task::Waker::noop());
            let mut polls = 0;
            loop {
                polls += 1;
                if let Poll::Ready(()) = fut.as_mut().poll(&mut cx) {
                    break;
                }
            }
            println!("Готово за {} опросов", polls);
        }
        """
    ),
    "hints": [
        "Метод poll опрашивает задачу заново только после возврата Poll::Pending, "
        "а проснуться задача может через Waker из Context.",
        "После возврата Poll::Ready повторный вызов poll запрещён контрактом Future — "
        "типы вроде select должны это учитывать.",
        "Pin<Box<T>> — самый простой способ закрепить значение; для стека есть макрос "
        "std::pin::pin!.",
        "Waker::noop и Waker::noop_waker_ref доступны начиная с Rust 1.85, "
        "это удобный инструмент для тестов и собственного block_on.",
    ],
    "content": [
        text(
            "Асинхронный код в Rust выглядит как обычный последовательный: вы пишете "
            "`let data = download().await;` и будто бы ждёте результат. На деле в этот момент "
            "ни один поток не спит — функция лишь возвращает управление исполнителю, "
            "а состояние вычисления сохраняется в структуре, которую компилятор сгенерировал "
            "за вас. Понимание этой структуры превращает асинхронность из магии в набор "
            "коротких и ясных правил."
        ),
        text(
            "У Rust нет встроенного рантайма: стандартная библиотека описывает трейт `Future` "
            "и несколько вспомогательных типов, а очередь задач, таймеры и пробуждение "
            "предоставляет выбранный вами исполнитель (tokio, async-std, smol). Именно поэтому "
            "устройство асинхронности стоит знать хотя бы на уровне контрактов, которые "
            "исполнитель и ваши типы обязаны друг другу.\n\n"
            "В этом уроке вы соберёте рабочий миниатюрный executor на стандартной библиотеке, "
            "реализуете свой `Future`, разберётесь, откуда берётся требование `Pin`, "
            "и увидите, как устроены комбинаторы вроде `join` и `select`."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "прослеживать, как `async fn` компилируется в конечный автомат с перечислением состояний;",
            "реализовывать трейт `Future` вручную и соблюдать контракт метода `poll`;",
            "объяснять, почему состояние задачи нельзя переносить в памяти, и использовать `Pin`;",
            "настраивать пробуждение задачи через `Waker` и `Context`;",
            "собирать минимальный executor с очередью готовых задач и функцией `block_on`;",
            "объединять несколько futures через `join`, `select` и тайм-аут.",
        ),
        heading("Future — это конечный автомат, а не поток"),
        text(
            "Абстракция, на которой держится вся асинхронность Rust, — трейт **`Future`** "
            "(в переводе «будущее»): значение, которое в какой-то момент станет результатом. "
            "Ключевое отличие от промисов в других языках в том, что `Future` ничего не делает "
            "само по себе. Пока его не начнут периодически опрашивать, не произойдёт ни одного шага "
            "вычисления.\n\n"
            "**Опрос** (poll) — вызов метода `poll` у future. Это работа для текущего "
            "исполнителя: он решает, когда опросить задачу. Результат опроса — тип **`Poll<T>`** "
            "с двумя вариантами: `Poll::Ready(T)` означает «работа закончена, вот результат», "
            "а `Poll::Pending` — «пока рано, я засну и позову вас сам»."
        ),
        example(
            "rust",
            """
            use std::future::Future;
            use std::pin::Pin;
            use std::task::{Context, Poll};

            pub trait Future {
                type Output;
                fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
            }

            pub enum Poll<T> {
                Ready(T),
                Pending,
            }
            """,
        ),
        text(
            "`self: Pin<&mut Self>` — изменяемая, но не перемещаемая ссылка: зачем так, "
            "разберём в разделе о `Pin`. `cx` даёт доступ к **`Waker`** — ручке, через "
            "которую future сообщает исполнителю «опросите меня снова». Контракт:"
        ),
        numbered(
            "`Poll::Ready(value)` возвращается ровно один раз; после него повторный опрос — "
            "логическая ошибка, тип вроде `select` или `join` может паниковать.",
            "`Poll::Pending` можно возвращать сколько угодно раз, но перед возвратом нужно "
            "зарегистрировать waker из `cx`, иначе задача не проснётся.",
            "Если future вернул `Pending`, а затем `Ready`, состояние между опросами "
            "сохраняется в самом значении — вы пишете его в поля структуры.",
        ),
        text(
            "Отсюда начинается главное: `async fn` — это синтаксический сахар. Компилятор "
            "превращает тело функции в перечисление состояний, а каждое `.await` становится "
            "точкой приостановки (**yield point**). Локальные переменные, которые переживают "
            "`.await`, переезжают в поля этого перечисления."
        ),
        example(
            "rust",
            """
            // Исходный код
            async fn load_config() -> String {
                let raw = read_file().await;
                let parsed = parse(raw).await;
                format!("config: {parsed}")
            }

            // Примерно во что превращается компилятором
            // (read_file и parse возвращают свои future-типы)
            enum LoadConfigState {
                Start,
                WaitingRead(ReadFileFuture),
                WaitingParse(ParseFuture),
                Done(String),
            }

            struct LoadConfigFuture {
                state: LoadConfigState,
            }

            impl Future for LoadConfigFuture {
                type Output = String;

                fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<String> {
                    // self.state меняется между итерациями, поэтому &mut берём заново
                    loop {
                        match self.state {
                            LoadConfigState::Start => {
                                self.state = LoadConfigState::WaitingRead(read_file());
                                // На следующей итерации опрашиваем новую ветку
                            }
                            LoadConfigState::WaitingRead(ref mut fut) => {
                                match Pin::new(fut).poll(cx) {
                                    Poll::Ready(raw) => {
                                        self.state = LoadConfigState::WaitingParse(parse(raw));
                                    }
                                    Poll::Pending => return Poll::Pending,
                                }
                            }
                            LoadConfigState::WaitingParse(ref mut fut) => {
                                match Pin::new(fut).poll(cx) {
                                    Poll::Ready(parsed) => {
                                        self.state =
                                            LoadConfigState::Done(format!("config: {parsed}"));
                                    }
                                    Poll::Pending => return Poll::Pending,
                                }
                            }
                            LoadConfigState::Done(ref value) => {
                                return Poll::Ready(value.clone());
                            }
                        }
                    }
                }
            }
            """,
        ),
        text(
            "Цикл вокруг `match` нужен не для красоты: получив результат в ветке `WaitingRead`, "
            "автомат переходит к следующему состоянию и продвигается дальше за один опрос. "
            "Возврат происходит, когда очередной future не готов или цепочка завершена.\n\n"
            "Следствие для практики: размер `async fn` равен сумме размеров всех её состояний. "
            "Если вы держите в одной функции десяток крупных буферов, future может получиться "
            "на сотни килобайт. Иногда такие данные переносят в `Box`, чтобы уменьшить "
            "размер итогового значения."
        ),
        callout(
            "info",
            "Асинхронность без потоков",
            "Один поток может вести тысячи задач: пока первая ждёт сеть, исполняется вторая. "
            "Потоки нужны только для параллельного выполнения на нескольких ядрах — "
            "их запускает исполнитель вроде tokio."
        ),
        heading("Свой Future и контракт опроса"),
        text(
            "Реализовать `Future` вручную стоит хотя бы раз: так становится ясно, что предлагают "
            "библиотеки. Начнём с будущего, которое готово ровно после N опросов. Каждый опрос "
            "увеличивает счётчик, пока он не достигнет цели.\n\n"
            "Обратите внимание на тип `self`. Мы работаем с ним через `&mut *self` — это "
            "небезопасно только на вид: `Pin<&mut Self>.as_mut()` даёт проекцию на те же данные "
            "без перемещения, и поле `count` меняется на месте."
        ),
        example(
            "rust",
            """
            use std::future::Future;
            use std::pin::Pin;
            use std::task::{Context, Poll};

            struct Countdown {
                left: u32,
            }

            impl Future for Countdown {
                type Output = &'static str;

                fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
                    if self.left == 0 {
                        return Poll::Ready("поехали");
                    }
                    self.left -= 1;
                    // Просим исполнитель опросить задачу ещё раз
                    cx.waker().wake_by_ref();
                    Poll::Pending
                }
            }

            fn main() {
                let mut fut = std::pin::pin!(Countdown { left: 3 });
                let waker = std::task::Waker::noop();
                let mut cx = Context::from_waker(waker);
                let mut polls = 0;
                loop {
                    polls += 1;
                    if let Poll::Ready(value) = fut.as_mut().poll(&mut cx) {
                        println!("{value} после {polls} опросов");
                        break;
                    }
                }
            }
            """,
        ),
        text(
            "Вывод: `поехали после 4 опросов`",
        ),
        text(
            "`wake_by_ref` — важная деталь. Вызов сообщает исполнителю, что задачу нужно "
            "поставить в очередь немедленно; без него `block_on` уснул бы навсегда, "
            "ведь у future нет другого источника событий. Такой «самооптимистичный» future "
            "неэффективен на практике, но идеально показывает механику: `Pending` — это "
            "не ошибка, а договорённость о следующем вызове.\n\n"
            "Для ввода-вывода waker сохраняют в структуре и вызывают позже из другого потока "
            "или из обработчика событий операционной системы:"
        ),
        example(
            "rust",
            """
            use std::future::Future;
            use std::pin::Pin;
            use std::sync::{Arc, Mutex};
            use std::task::{Context, Poll, Waker};
            use std::thread;
            use std::time::{Duration, Instant};

            struct Shared {
                done: bool,
                waker: Option<Waker>,
            }

            struct Timer {
                deadline: Instant,
                shared: Arc<Mutex<Shared>>,
            }

            impl Timer {
                fn new(ms: u64) -> Timer {
                    let shared = Arc::new(Mutex::new(Shared { done: false, waker: None }));
                    let worker = Arc::clone(&shared);
                    thread::spawn(move || {
                        thread::sleep(Duration::from_millis(ms));
                        let waker = {
                            let mut guard = worker.lock().unwrap();
                            guard.done = true;
                            guard.waker.take()
                        };
                        // Сбрасываем блокировку до вызова waker: он может перепланировать
                        // задачу на том же потоке
                        if let Some(waker) = waker {
                            waker.wake();
                        }
                    });
                    Timer {
                        deadline: Instant::now() + Duration::from_millis(ms),
                        shared,
                    }
                }
            }

            impl Future for Timer {
                type Output = Instant;

                fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Instant> {
                    let ready = self.shared.lock().unwrap().done || Instant::now() >= self.deadline;
                    if ready {
                        Poll::Ready(Instant::now())
                    } else {
                        self.shared.lock().unwrap().waker = Some(cx.waker().clone());
                        Poll::Pending
                    }
                }
            }

            fn main() {
                let start = Instant::now();
                let mut fut = std::pin::pin!(Timer::new(30));
                let waker = std::task::Waker::noop();
                let mut cx = Context::from_waker(waker);
                loop {
                    if fut.as_mut().poll(&mut cx).is_ready() {
                        println!("таймер сработал: {:?}", start.elapsed().as_millis() >= 30);
                        break;
                    }
                    // Для простоты: спим коротко, waker здесь noop
                    thread::sleep(Duration::from_millis(5));
                }
            }
            """,
        ),
        text(
            "Возможный вывод: `таймер сработал: true`",
        ),
        text(
            "С `Waker::noop` будильник ничего не перепланирует, поэтому цикл дополнительно "
            "спит 5 мс; в настоящем исполнителе `wake` ставит задачу в очередь. Зато видна "
            "правильная последовательность: проверка готовности, затем клонирование waker, "
            "затем `Pending`. Обратный порядок дал бы гонку: событие могло произойти между "
            "проверкой и регистрацией, и задача уснула бы навсегда."
        ),
        callout(
            "warning",
            "Порядок действий в poll",
            "Сначала проверка готовности, затем сохранение waker, затем `Poll::Pending`. "
            "Если заблокировать мьютекс и вызвать `wake` из-под того же мьютекса, "
            "задача может сразу попытаться опроситься и попасть в дедлок."
        ),
        heading("Pin: почему состояние нельзя переносить"),
        text(
            "Конечный автомат из первого раздела на самом деле хранит указатели внутрь себя. "
            "Если внутри `async fn` создана переменная и на неё взята ссылка, а затем произошёл "
            "`.await`, то после сохранения состояния эта ссылка указывает на поле той же "
            "структуры. Такие типы называют **самоссылающимися** (self-referential): копия "
            "структуры в другом месте памяти оставит ссылки указывающими на старый адрес.\n\n"
            "Перемещение значения в Rust — обычное дело: возврат из функции, упаковка в `Box`, "
            "перестановка элементов `Vec`. Для самоссылающихся значений это означало бы "
            "висячие указатели. Поэтому у `poll` и стоит `Pin<&mut Self>`."
        ),
        example(
            "rust",
            """
            async fn sample() {
                let buffer = vec![1u8, 2, 3];
                let view: &[u8] = &buffer;  // ссылка внутрь buffer
                yield_once().await;          // точка приостановки
                // buffer остался на месте, а view продолжает на него указывать
                println!("{:?}", view);
            }
            """,
        ),
        table(
            ["Тип", "Что гарантирует", "Когда использовать"],
            [
                ["`Pin<&mut T>`", "Значение не будет перемещено, пока живёт эта ссылка", "Сигнатуры `poll`, передача future по ссылке"],
                ["`Pin<Box<T>>`", "Значение живёт в куче и адрес стабилен", "Хранение `dyn Future`, стирание типа"],
                ["`std::pin::pin!(x)`", "Закрепление переменной на стеке", "Локальные future для собственного `block_on`"],
                ["`T: Unpin`", "Перемещение безопасно, `Pin` не нужен", "Счётчики, готовые значения, простые типы"],
                ["`unsafe { Pin::new_unchecked(&mut t) }`", "Перемещение запрещено только обещанием автора кода", "Только в обёртках, где перемещения точно нет"],
            ],
        ),
        text(
            "`Pin` не делает тип неподвижным физически: это маркер в системе типов, который "
            "запрещает безопасно получить `&mut T` у типа без `Unpin`. Числа, `String`, `Vec` "
            "реализуют `Unpin` автоматически, а сгенерированные `async fn` future — нет. "
            "Поэтому `Box::pin` так част: он переносит значение в кучу один раз, и адрес "
            "дальше не меняется."
        ),
        example(
            "rust",
            """
            use std::future::Future;
            use std::pin::Pin;
            use std::task::{Context, Poll};

            /// Сумма двух futures, у которых одинаковый тип результата.
            struct Sum<A, B> {
                a: A,
                b: B,
            }

            fn sum<A, B>(a: A, b: B) -> Sum<A, B> {
                Sum { a, b }
            }

            impl<A, B> Future for Sum<A, B>
            where
                A: Future<Output = i32> + Unpin,
                B: Future<Output = i32> + Unpin,
            {
                type Output = i32;

                fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<i32> {
                    // Unpin позволяет безопасно получить &mut Self
                    let this = self.get_mut();
                    let a = match Pin::new(&mut this.a).poll(cx) {
                        Poll::Ready(v) => v,
                        Poll::Pending => return Poll::Pending,
                    };
                    let b = match Pin::new(&mut this.b).poll(cx) {
                        Poll::Ready(v) => v,
                        Poll::Pending => return Poll::Pending,
                    };
                    Poll::Ready(a + b)
                }
            }

            async fn value(n: i32) -> i32 {
                n
            }

            fn main() {
                let mut fut = Box::pin(sum(value(2), value(3)));
                let waker = std::task::Waker::noop();
                let mut cx = Context::from_waker(waker);
                match fut.as_mut().poll(&mut cx) {
                    Poll::Ready(total) => println!("сумма: {total}"),
                    Poll::Pending => println!("ещё не готово"),
                }
                // Синтаксис .await для атрибута суммы
                let total = futures_join_await();
                println!("через await: {total}");
            }

            fn futures_join_await() -> i32 {
                // В async-контексте то же самое пишется как (value(2).await + value(3).await)
                5
            }
            """,
        ),
        text(
            "Вывод: `сумма: 5` и `через await: 5`",
        ),
        heading("Waker и Context"),
        text(
            "`Context` — обёртка над `&Waker`; в коде его почти не используют напрямую, "
            "а берут `cx.waker()` и клонируют ручку или будят задачу сразу. Внутри `Waker` "
            "хранит таблицу функций (`RawWakerVTable`), поэтому умеет копироваться, "
            "пробуждать и освобождать данные реализации. Три метода `Waker`:"
        ),
        bullets(
            "`wake(self)` — пробуждает задачу, потребляя ручку. Выгоднее, если копия вам больше не нужна.",
            "`wake_by_ref(&self)` — пробуждает, оставляя ручку у себя. Нужно вызывать перед `Pending`, когда waker сохранён.",
            "`clone(&self)` — делает независимую копию. Требуется, когда waker уходит в другой поток или в структуру.",
        ),
        text(
            "Реализовать `Waker` можно и вручную, через `RawWaker`, но для прикладного кода "
            "это почти не нужно: исполнители предоставляют свои реализации, а для тестов есть "
            "`Waker::noop` и `Waker::noop_waker_ref`. Вручную `RawWaker` собирают только авторы "
            "executor'ов и примитивов синхронизации."
        ),
        example(
            "rust",
            """
            use std::task::{Context, Poll, Waker};

            fn inspect(cx: &mut Context<'_>) -> Poll<()> {
                let waker: &Waker = cx.waker();

                // Будим задачу, оставляя ручку себе
                waker.wake_by_ref();

                // Копия — например, чтобы передать её в фоновый поток
                let copy: Waker = waker.clone();

                // Копия равна оригиналу: оба указывают на один источник
                let same = waker == &copy;
                println!("copy равен оригиналу: {same}");

                // noop-waker: пробуждение ничего не делает
                let idle = Waker::noop();
                let mut idle_cx = Context::from_waker(idle);
                idle_cx.waker().wake_by_ref();

                Poll::Pending
            }
            """,
        ),
        text(
            "Вывод: `copy равен оригиналу: true`",
        ),
        text(
            "Требование `Send + Sync` объясняет, почему future без `Send` не запустить "
            "в многопоточном исполнителе: будильник срабатывает в чужом потоке, а состояние "
            "задачи с `Rc` или `RefCell` к такому доступу не готово. Отсюда и ошибка "
            "`future cannot be sent between threads`."
        ),
        heading("Минимальный executor"),
        text(
            "Исполнитель (**executor**) — цикл, который забирает готовые задачи из очереди, "
            "опрашивает их и возвращает в очередь те, что просили разбудить. Всё остальное — "
            "оптимизации. Минимальная версия состоит из типа задачи, очереди и `Waker`, "
            "который умеет эту задачу вернуть в очередь."
        ),
        example(
            "rust",
            """
            use std::collections::VecDeque;
            use std::future::Future;
            use std::pin::Pin;
            use std::sync::{Arc, Mutex};
            use std::task::{Context, Poll, Wake, Waker};

            struct Queue {
                ready: Mutex<VecDeque<usize>>,
            }

            /// Реализация будильника: при пробуждении id задачи попадает в очередь.
            struct TaskWake {
                id: usize,
                queue: Arc<Queue>,
            }

            impl Wake for TaskWake {
                fn wake(self: Arc<Self>) {
                    self.queue.ready.lock().unwrap().push_back(self.id);
                }
            }

            struct Task {
                future: Pin<Box<dyn Future<Output = ()>>>,
                waker: Waker,
            }

            struct Executor {
                queue: Arc<Queue>,
                tasks: Vec<Option<Task>>,
            }

            impl Executor {
                fn new() -> Executor {
                    Executor {
                        queue: Arc::new(Queue { ready: Mutex::new(VecDeque::new()) }),
                        tasks: Vec::new(),
                    }
                }

                fn spawn(&mut self, future: impl Future<Output = ()> + 'static) {
                    let id = self.tasks.len();
                    let waker = Waker::from(Arc::new(TaskWake {
                        id,
                        queue: Arc::clone(&self.queue),
                    }));
                    self.tasks.push(Some(Task { future: Box::pin(future), waker }));
                    self.queue.ready.lock().unwrap().push_back(id);
                }

                fn run(&mut self) {
                    loop {
                        let id = match self.queue.ready.lock().unwrap().pop_front() {
                            Some(id) => id,
                            None => break,
                        };
                        let Some(task) = self.tasks[id].as_mut() else {
                            continue;
                        };
                        let mut cx = Context::from_waker(&task.waker);
                        if let Poll::Ready(()) = task.future.as_mut().poll(&mut cx) {
                            self.tasks[id] = None;
                        }
                    }
                }
            }

            async fn step(n: u32) {
                println!("шаг {n}");
            }

            fn main() {
                let mut exec = Executor::new();
                exec.spawn(step(1));
                exec.spawn(async {
                    step(2).await;
                    step(3).await;
                });
                // Пока очередь не опустеет, вторая задача
                // не продвинется дальше первого шага
                exec.run();
                println!("очередь пуста, все задачи завершены");
            }
            """,
        ),
        text(
            "Вывод: `шаг 1`, `шаг 2`, `шаг 3`, `очередь пуста, все задачи завершены`",
        ),
        text(
            "Ключевые решения. Задача хранится как `Pin<Box<dyn Future<Output = ()>>>`: тип "
            "future неизвестен вызывающему коду, а `Pin` запрещает перемещение состояния. "
            "Идентификатор — индекс в векторе, поэтому `wake` делает только `push_back`. "
            "Завершённая задача заменяется на `None` и больше не опрашивается. Очередь на "
            "`Mutex` — упрощение; реальные исполнители используют неблокирующие структуры. "
            "`spawn` сразу ставит задачу в очередь, иначе первый опрос не произойдёт."
        ),
        heading("block_on: исполнитель для одного потока"),
        text(
            "`block_on(future)` — синхронная обёртка для тестов и утилит: опрос, проверка "
            "результата, ожидание до следующего пробуждения. Главная сложность в том, что "
            "waker должен вести к этому же циклу. Поэтому будильник паркует поток, а цикл "
            "проверяет флаг после каждого `poll`. Для учебного примера достаточно `Waker::noop` "
            "и короткого сна."
        ),
        example(
            "rust",
            """
            use std::future::Future;
            use std::pin::Pin;
            use std::task::{Context, Poll};

            fn block_on<F: Future>(future: F) -> F::Output {
                let mut future = std::pin::pin!(future);
                let waker = std::task::Waker::noop();
                let mut cx = Context::from_waker(waker);
                loop {
                    match future.as_mut().poll(&mut cx) {
                        Poll::Ready(value) => return value,
                        // Настоящая реализация здесь парковала бы поток
                        // до вызова waker, а не крутилась вхолостую
                        Poll::Pending => std::thread::yield_now(),
                    }
                }
            }

            async fn compute() -> u32 {
                let a = 20;
                let b = 22;
                a + b
            }

            fn main() {
                let answer = block_on(compute());
                println!("ответ: {answer}");
                let doubled = block_on(async { answer * 2 });
                println!("удвоенный: {doubled}");
            }
            """,
        ),
        text(
            "Вывод: `ответ: 42` и `удвоенный: 84`",
        ),
        text(
            "Макрос `std::pin::pin!` закрепляет future на стеке без аллокации и возвращает "
            "`Pin<&mut F>`; опрос идёт через `as_mut()`. Тот же приём нужен в тестах.\n\n"
            "Вложенный `block_on` внутри асинхронного контекста блокирует поток вместе с "
            "чужими задачами. В tokio для этого есть `spawn_blocking` и `yield_now`."
        ),
        callout(
            "danger",
            "Не блокируйте поток исполнителя",
            "`thread::sleep`, синхронные файловые и сетевые вызовы, тяжёлые вычисления "
            "внутри `async fn` останавливают весь поток вместе с остальными задачами. "
            "Выносите их в отдельный поток."
        ),
        heading("Комбинаторы: join, select и тайм-аут"),
        text(
            "Futures — обычные значения, поэтому их можно складывать в новые future. "
            "Три базовых комбинатора покрывают почти все задачи планирования:\n\n"
            "**join** ждёт все входы и отдаёт кортеж результатов; **select** ждёт первый "
            "завершившийся и возвращает его; **race** гоняет два будущих значения и "
            "отдаёт любое первое. Комбинаторы опрашивают входы в одном `poll`, пока не "
            "получат нужный ответ, поэтому не занимают поток и не требуют нескольких задач."
        ),
        example(
            "rust",
            """
            use std::future::Future;
            use std::pin::Pin;
            use std::task::{Context, Poll};

            enum Either<A, B> {
                Left(A),
                Right(B),
            }

            /// Примерная реализация join: ждёт оба входа.
            struct Join2<A: Future, B: Future> {
                a: Option<A>,
                b: Option<B>,
                result_a: Option<A::Output>,
                result_b: Option<B::Output>,
            }

            impl<A, B> Future for Join2<A, B>
            where
                A: Future + Unpin,
                B: Future + Unpin,
            {
                type Output = (A::Output, B::Output);

                fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
                    let this = self.get_mut();
                    if this.result_a.is_none() {
                        if let Some(a) = this.a.as_mut() {
                            match Pin::new(a).poll(cx) {
                                Poll::Ready(v) => this.result_a = Some(v),
                                Poll::Pending => {}
                            }
                        }
                    }
                    if this.result_b.is_none() {
                        if let Some(b) = this.b.as_mut() {
                            match Pin::new(b).poll(cx) {
                                Poll::Ready(v) => this.result_b = Some(v),
                                Poll::Pending => {}
                            }
                        }
                    }
                    match (this.result_a.take(), this.result_b.take()) {
                        (Some(a), Some(b)) => Poll::Ready((a, b)),
                        (a, b) => {
                            this.result_a = a;
                            this.result_b = b;
                            Poll::Pending
                        }
                    }
                }
            }

            /// Возвращает первое завершившееся значение, другое отбрасывает.
            struct FirstTwo<A: Future, B: Future> {
                a: A,
                b: B,
            }

            impl<A, B> Future for FirstTwo<A, B>
            where
                A: Future + Unpin,
                B: Future + Unpin,
                A::Output: Unpin,
                B::Output: Unpin,
            {
                type Output = Either<A::Output, B::Output>;

                fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
                    let this = self.get_mut();
                    if let Poll::Ready(v) = Pin::new(&mut this.a).poll(cx) {
                        return Poll::Ready(Either::Left(v));
                    }
                    if let Poll::Ready(v) = Pin::new(&mut this.b).poll(cx) {
                        return Poll::Ready(Either::Right(v));
                    }
                    Poll::Pending
                }
            }
            """,
        ),
        text(
            "`Join2` хранит результаты завершившихся входов и не опрашивает их повторно — "
            "этого требует контракт. `FirstTwo` отбрасывает проигравшего вместе с состоянием, "
            "поэтому `select` опасен для операций с побочными эффектами. Тайм-аут — та же "
            "гонка, только один из участников — таймер."
        ),
        example(
            "rust",
            """
            use std::future::Future;
            use std::pin::Pin;
            use std::task::{Context, Poll};

            enum TimeoutResult<T> {
                Completed(T),
                Elapsed,
            }

            struct WithTimeout<F, D> {
                work: F,
                timer: D,
            }

            impl<F, D> Future for WithTimeout<F, D>
            where
                F: Future + Unpin,
                D: Future<Output = ()> + Unpin,
            {
                type Output = TimeoutResult<F::Output>;

                fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
                    let this = self.get_mut();
                    if let Poll::Ready(value) = Pin::new(&mut this.work).poll(cx) {
                        return Poll::Ready(TimeoutResult::Completed(value));
                    }
                    if let Poll::Ready(()) = Pin::new(&mut this.timer).poll(cx) {
                        return Poll::Ready(TimeoutResult::Elapsed);
                    }
                    Poll::Pending
                }
            }

            fn main() {
                // Оба входа готовы сразу — результат определяется первым
                let mut quick = Box::pin(WithTimeout {
                    work: async { "данные" },
                    timer: async {},
                });
                let waker = std::task::Waker::noop();
                let mut cx = Context::from_waker(waker);
                match quick.as_mut().poll(&mut cx) {
                    Poll::Ready(TimeoutResult::Completed(v)) => println!("успех: {v}"),
                    Poll::Ready(TimeoutResult::Elapsed) => println!("тайм-аут"),
                    Poll::Pending => println!("ждём"),
                }
            }
            """,
        ),
        text(
            "Вывод: `успех: данные`",
        ),
        text(
            "Комбинаторы crate `futures` устроены так же, но отдельно различают состояния "
            "«ещё не начат» и «завершён». В своём комбинаторе эти состояния тоже нужно "
            "хранить раздельно."
        ),
        heading("Async fn в трейтах и dyn"),
        text(
            "С версии 1.75 трейты поддерживают асинхронные методы напрямую:"
        ),
        example(
            "rust",
            """
            // Нативный синтаксис: метод возвращает анонимный Future
            trait Store {
                fn find(&self, key: &str) -> impl Future<Output = Option<String>> + '_;

                async fn save(&self, key: &str, value: String) -> bool {
                    // Реализация по умолчанию тоже может быть async
                    let _ = (key, value);
                    true
                }
            }

            // Это сокращение для
            // fn save<'a>(&'a self, key: &'a str, value: String)
            //     -> impl Future<Output = bool> + 'a;
            """,
        ),
        text(
            "Нативный вариант не поддерживает `dyn`: у future нет известного размера, "
            "и трейт теряет объектную безопасность. Для `Box<dyn Store>` нужен `#[async_trait]`, "
            "раскрывающий методы в `Pin<Box<dyn Future + Send + 'a>>`, что стоит одной "
            "аллокации на вызов."
        ),
        heading("Диагностика и производительность"),
        text(
            "`future is not Send` — в состоянии остался не-`Send` тип (`Rc`, `RefCell`, "
            "сырой указатель). Часто достаточно сузить область видимости или заменить "
            "`Rc` на `Arc`. `poll called after Ready` — нарушение контракта в комбинаторе. "
            "`... which is not Unpin` — попытка взять `&mut` без `Unpin`; решение — "
            "`Box::pin`. Размер future проверяйте через `std::mem::size_of_val`."
        ),
        table(
            ["Симптом", "Причина", "Решение"],
            [
                ["`future cannot be sent between threads`", "В состоянии остался `Rc` или `RefCell`", "Замените на `Arc` и `Mutex` либо ограничьте область видимости"],
                ["`poll called after Ready`", "Комбинатор опрашивает завершённый вход", "Помечайте завершённые входы как `None`"],
                ["`has type ... which is not Unpin`", "Нужен `&mut` к potentially-pinned значению", "`Box::pin`, `pin!` или проекция с `unsafe`"],
                ["Задача зависает навсегда", "Waker не сохранён перед `Pending`", "Клонируйте `cx.waker()` до возврата `Pending`"],
                ["Большой `size_of_val(&future)`", "Крупные буферы живут через `.await`", "Переносите буферы в `Box` или в отдельную функцию"],
            ],
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Возврат `Pending` без сохранения waker", "Задача никогда не проснётся", "`let w = cx.waker().clone();` до `Pending`"],
                ["`wake()` вызовом из-под блокировки", "Возможен дедлок при немедленном опросе", "Сбрасывайте guard, затем будите"],
                ["`block_on` внутри `async fn`", "Блокируется поток исполнителя", "`spawn`, `join!` или `spawn_blocking`"],
                ["Перемещение `Pin<&mut T>` через `map_unchecked_mut` без гарантий", "Висячие указатели, UB", "Проецируйте только поля, которые не перемещаются"],
                ["Опрос завершённого future в собственном комбинаторе", "Паника или неопределённое поведение", "Храните флаг «готово» и не опрашивайте повтор"],
                ["`Rc` внутри `async`-функции для многопоточного рантайма", "Future не реализует `Send`", "Используйте `Arc` или локальный `single_thread` рантайм"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняются в одном файле `main.rs` проекта `cargo new async-lab`. "
            "Сборка — `cargo run`, проверка типов без запуска — `cargo check`. "
            "Для первых трёх заданий достаточно стандартной библиотеки."
        ),
        numbered(
            "Реализуйте `Future` с именем `Countdown { left: u32 }`, который возвращает "
            "`Ready(left * 10)` после исчерпания счётчика и печатает номер каждого опроса. "
            "Убедитесь, что с `left = 3` опросов ровно четыре.",
            "Соберите `OnceFuture<T>`, который отдаёт значение только при первом опросе, "
            "а при повторном после `Ready` возвращает `Ready` с тем же результатом, "
            "не паникуя. Объясните, почему это нарушает контракт и почему для демонстрации "
            "всё же полезно.",
            "Перепишите `Executor` из урока так, чтобы в очереди лежали "
            "`Arc<Task>` с `Pin<Box<dyn Future + Send>>`, и запустите три задачи "
            "в двух потоках. Проверьте, что порядок выполнения не важен для результата.",
            "Соберите `block_on`, который не крутится вхолостую: waker паркует поток, "
            "а цикл разблокируется по сигналу. Замерьте число опросов для future, "
            "который просыпается трижды из фонового потока.",
            "Напишите функцию `timeout(future, ms)`, возвращающую `Result<T, Timeout>`, "
            "на основе `WithTimeout`. Проверьте её на будущем, которое готово сразу, "
            "и на будущем, которое ждёт через `thread::sleep`.",
        ),
        text("Пример вывода для первого и третьего заданий:"),
        example(
            "text",
            """
            опрос 1
            опрос 2
            опрос 3
            опрос 4
            результат: 0
            задача 0 завершена
            задача 1 завершена
            задача 2 завершена
            все потоки завершены
            """,
        ),
        callout(
            "success",
            "Подсказка к четвёртому заданию",
            "Самый простой будильник без дополнительных crate: `std::sync::mpsc` "
            "и `thread::park`. В `wake` отправляйте сообщение в канал, а цикл "
            "`block_on` читает канал с тайм-аутом вместо `yield_now`. "
            "Проверьте, что `wake` вызывается ровно три раза.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Что означает возврат `Poll::Pending` и кто отвечает за следующий опрос?",
            "Почему сигнатура `poll` использует `Pin<&mut Self>`, а не `&mut Self`?",
            "Чем `wake` отличается от `wake_by_ref` и когда какой уместен?",
            "Зачем в `Executor` задача хранится как `Pin<Box<dyn Future<Output = ()>>>`?",
            "Почему `select` может быть опасен для операций с побочными эффектами?",
            "Какой тип в состоянии future ломает его `Send` и как это исправить?",
        ),
        heading("Ответы", 3),
        numbered(
            "`Pending` значит «пока результата нет». Исполнитель будет ждать, пока task "
            "не разбудит сохранённый waker, и только после этого опросит future снова.",
            "`async fn` хранит указатели на собственные поля между точками приостановки. "
            "`Pin` запрещает безопасно переместить значение и тем самым защищает такие ссылки.",
            "`wake` потребляет waker, `wake_by_ref` оставляет копию. `wake_by_ref` используется "
            "перед возвратом `Pending`, когда ручка сохранена в структуре.",
            "Тип будущего значения неизвестен вызывающему коду — стирается через `dyn`; "
            "`Box` даёт стабильный адрес, а `Pin` запрещает перемещение после первого опроса.",
            "Проигравший future отбрасывается вместе с состоянием, а побочный эффект "
            "может остаться. Сначала убедитесь, что операция идемпотентна или отменяема.",
            "`Rc`, `RefCell` и сырые указатели. Замените на `Arc`/`Mutex` или "
            "локализуйте данные в блоке, который не переживает `.await`.",
        ),
        *outro(
            summary=(
                "`async fn` компилируется в конечный автомат; каждое `.await` — точка приостановки.",
                "`Future::poll` возвращает `Poll::Ready` ровно один раз или `Poll::Pending` "
                "с зарегистрированным waker.",
                "`Pin` защищает самоссылающиеся состояния; `Box::pin` переносит future в кучу.",
                "`Waker` — ручка пробуждения задачи, `Context` — её тонкая обёртка.",
                "Executor — цикл очереди готовых задач; `block_on` — его однопоточный вариант.",
                "`join`, `select` и тайм-аут собираются из тех же `poll`-вызовов.",
            ),
            next_text=(
                "В следующем уроке углубимся в продвинутую конкурентность: каналы, "
                "примитивы синхронизации, атомарные операции и модели конкурентности. "
                "Знание `poll` и `Waker` пригодится: каналы для асинхронного кода устроены "
                "именно как источники событий, которые вызывают `wake`."
            ),
            resources=(
                "Async Book: https://rust-lang.github.io/async-book/",
                "Документация `Future`: https://doc.rust-lang.org/std/future/trait.Future.html",
                "Документация `Pin`: https://doc.rust-lang.org/std/pin/",
                "Модуль `task` и `Waker`: https://doc.rust-lang.org/std/task/",
                "Статья «Rust futures: an uneducated, short and hopefully not-so-fun tutorial»"
                " — https://rust-lang.github.io/async-book/02_execution/02_future.html",
            ),
        ),
    ],
}
