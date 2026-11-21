"""Урок 2.5 курса Python: контекстные менеджеры."""

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
    "language": "python",
    "program_order": 2,
    "topic_order": 5,
    "name": "2.5. Контекстные менеджеры",
    "slug": "python-2-5-контекстные-менеджеры",
    "short_description": (
        "Протокол with, __enter__/__exit__, contextlib.contextmanager, "
        "ExitStack и правильное управление ресурсами."
    ),
    "topic_name": "Контекстные менеджеры",
    "topic_description": (
        "Как гарантировать очистку ресурсов через with, писать свои "
        "контекстные менеджеры и использовать contextlib для сложных случаев."
    ),
    "learning_objectives": [
        "Объяснять, как работает протокол with и зачем он нужен",
        "Реализовывать __enter__ и __exit__ в своих классах",
        "Писать генераторные контекстные менеджеры через contextlib.contextmanager",
        "Использовать ExitStack для динамического количества ресурсов",
        "Понимать, как __exit__ обрабатывает исключения и может их подавлять",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "python",
        "контекстные менеджеры",
        "with",
        "contextlib",
        "ExitStack",
        "ресурсы",
    ],
    "starter_code": code(
        """
        from contextlib import contextmanager

        @contextmanager
        def timer():
            import time
            start = time.perf_counter()
            yield
            print(f"Затрачено: {time.perf_counter() - start:.4f}s")

        with timer():
            sum(range(1000000))
        """
    ),
    "hints": [
        "__enter__ возвращает значение для `as`, __exit__ получает информацию об исключении.",
        "contextlib.contextmanager превращает генератор с yield в контекстный менеджер.",
        "ExitStack нужен, когда число ресурсов заранее неизвестно.",
    ],
    "content": [
        text(
            "Открытие файла, подключение к базе данных, захват блокировки — всё "
            "это **ресурсы**, которые нужно освободить после использования. Если "
            "забыть вызвать `close()`, `release()` или `unlock()`, программа "
            "утечёт дескрипторы, соединения или память. В худшем случае это "
            "приведёт к ошибкам, которые воспроизвести сложно.\n\n"
            "Конструкция `with` решает эту проблему: она гарантирует вызов "
            "метода очистки даже если внутри блока произошло исключение. В этом "
            "уроке разберём, как работает протокол контекстного менеджера, как "
            "писать свои классы с `__enter__` и `__exit__`, как использовать "
            "`contextlib` для генераторных менеджеров и как управлять "
            "несколькими ресурсами через `ExitStack`."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "понимать, что делает with на каждом шаге: __enter__, блок, __exit__;",
            "писать классы-менеджеры контекста с правильной обработкой исключений;",
            "использовать @contextmanager для простых менеджеров на генераторах;",
            "объединять несколько ресурсов через ExitStack;",
            "подавлять исключения в __exit__ возвратом True;",
            "работать с асинхронными контекстными менеджерами (async with).",
        ),
        heading("Зачем нужен with"),
        text(
            "Без `with` очистка ресурса — ответственность программиста. При "
            "любой ошибке между открытием и закрытием ресурс остаётся открытым."
        ),
        example(
            "python",
            """
            # Рискованно: при ошибке файл не закроется
            f = open("data.txt", "w")
            f.write("важные данные")
            # Если здесь исключение — f.close() не выполнится
            f.close()

            # Надёжно: файл закроется всегда
            with open("data.txt", "w") as f:
                f.write("важные данные")
            # Здесь файл точно закрыт
            """,
        ),
        text(
            "`with` не просто сокращение: он создаёт **контекст**, в котором "
            "гарантированно выполняется код очистки. Это работает для файлов, "
            "сокетов, соединений с БД, блокировок (`threading.Lock`), "
            "транзакций и любых объектов, реализующих протокол."
        ),
        heading("Протокол контекстного менеджера"),
        text(
            "**Контекстный менеджер** — объект с методами `__enter__` и "
            "`__exit__`. Конструкция `with EXPR as VAR: BLOCK` выполняется так:"
        ),
        numbered(
            "Вычисляется `EXPR`, получается менеджер.",
            "Вызывается `mgr.__enter__()`, результат присваивается `VAR` (если есть `as`).",
            "Выполняется `BLOCK`.",
            "При нормальном завершении вызывается `mgr.__exit__(None, None, None)`.",
            "При исключении вызывается `mgr.__exit__(exc_type, exc_val, exc_tb)`.",
        ),
        text(
            "`__exit__` получает три аргумента: класс исключения, сам объект "
            "исключения и traceback. Если исключения не было — все три `None`. "
            "Возврат `True` из `__exit__` **подавляет** исключение, `False` или "
            "`None` — пробрасывает его дальше."
        ),
        heading("Классовый контекстный менеджер"),
        text(
            "Самый явный способ — класс с `__enter__` и `__exit__`. `__enter__` "
            "подготавливает ресурс и возвращает объект для `as`. `__exit__` "
            "освобождает ресурс и решает, подавлять ли исключение."
        ),
        example(
            "python",
            """
            class Timer:
                def __init__(self, name):
                    self.name = name
                    self.start = None

                def __enter__(self):
                    import time
                    self.start = time.perf_counter()
                    return self

                def __exit__(self, exc_type, exc_val, exc_tb):
                    import time
                    elapsed = time.perf_counter() - self.start
                    print(f"{self.name}: {elapsed:.4f}s")
                    return False  # не подавляем исключение


            with Timer("сумма"):
                total = sum(range(1_000_000))
                print(total)
            """,
        ),
        example("text", "499999500000\nсумма: 0.0123s"),
        text(
            "`__enter__` возвращает `self`, поэтому внутри блока доступен "
            "объект таймера. `__exit__` всегда вызывается, даже если внутри "
            "блока `raise`. Возврат `False` (или отсутствие `return`) "
            "означает: исключение не подавлять."
        ),
        heading("Подавление исключений"),
        text(
            "Если `__exit__` возвращает `True`, исключение считается "
            "обработанным и не распространяется дальше. Это мощный, но "
            "опасный инструмент: легко скрыть настоящую ошибку."
        ),
        example(
            "python",
            """
            class SuppressValueError:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_val, exc_tb):
                    if exc_type is ValueError:
                        print(f"Подавлено: {exc_val}")
                        return True
                    return False


            with SuppressValueError():
                raise ValueError("неправильное значение")

            print("После with — программа продолжается")
            """,
        ),
        example("text", "Подавлено: неправильное значение\nПосле with — программа продолжается"),
        callout(
            "warning",
            "Осторожно с подавлением",
            "Возврат `True` для всех исключений (`return True` без проверки) "
            "скрывает баги и делает отладку невыносимой. Подавляйте только "
            "конкретные ожидаемые ошибки.",
        ),
        heading("contextlib.contextmanager — генераторный стиль"),
        text(
            "Для простых менеджеров удобнее написать генератор с `yield` и "
            "обернуть его в `@contextmanager`. Код до `yield` — это "
            "`__enter__`, после — `__exit__`. Значение после `yield` — "
            "результат для `as`."
        ),
        example(
            "python",
            """
            from contextlib import contextmanager
            import time

            @contextmanager
            def timer(name):
                start = time.perf_counter()
                yield
                print(f"{name}: {time.perf_counter() - start:.4f}s")


            with timer("сумма"):
                total = sum(range(1_000_000))
                print(total)
            """,
        ),
        example("text", "499999500000\nсумма: 0.0123s"),
        text(
            "Генератор должен содержать ровно один `yield`. Код перед ним — "
            "подготовка, после — очистка. Если внутри блока произошло "
            "исключение, оно поднимается в точке `yield`; генератор может "
            "его поймать через `try/except` вокруг `yield`."
        ),
        example(
            "python",
            """
            from contextlib import contextmanager

            @contextmanager
            def suppress_value_error():
                try:
                    yield
                except ValueError as e:
                    print(f"Подавлено: {e}")


            with suppress_value_error():
                raise ValueError("ошибка валидации")

            print("Продолжаем")
            """,
        ),
        example("text", "Подавлено: ошибка валидации\nПродолжаем"),
        heading("contextlib — утилиты"),
        text(
            "Модуль `contextlib` содержит вспомогательные инструменты для "
            "работы с контекстными менеджерами."
        ),
        heading("closing — вызов close у объекта"),
        text(
            "`closing(obj)` создаёт менеджер, который вызывает `obj.close()` "
            "при выходе. Полезно для объектов, у которых есть `close`, но нет "
            "`__enter__`/`__exit__`."
        ),
        example(
            "python",
            """
            from contextlib import closing
            from urllib.request import urlopen

            with closing(urlopen("https://example.com")) as resp:
                print(resp.read(50))
            """,
        ),
        text("b'<!doctype html>\\n<html>\\n<head>\\n    <title>Example Domain</title>'"),
        heading("nullcontext — пустой менеджер"),
        text(
            "`nullcontext(value)` — менеджер, который ничего не делает, но "
            "возвращает `value` для `as`. Полезен, когда менеджер "
            "условно нужен: `with (lock if need_lock else nullcontext()):`."
        ),
        example(
            "python",
            """
            from contextlib import nullcontext

            need_lock = False
            lock = nullcontext()

            with lock:
                print("Работаем без блокировки")
            """,
        ),
        example("text", "Работаем без блокировки"),
        heading("ExitStack — динамическое управление ресурсами"),
        text(
            "`ExitStack` позволяет войти в несколько контекстных менеджеров "
            "программно, когда их число неизвестно заранее. Он вызывает "
            "`__enter__` для каждого и гарантирует `__exit__` в обратном "
            "порядке (LIFO), даже если одно из входа выбросило исключение."
        ),
        example(
            "python",
            """
            from contextlib import ExitStack

            files = ["a.txt", "b.txt", "c.txt"]

            with ExitStack() as stack:
                handles = [stack.enter_context(open(f, "w")) for f in files]
                for h in handles:
                    h.write("данные\n")
            # Все файлы закрыты автоматически
            """,
        ),
        text(
            "`enter_context(mgr)` входит в менеджер и регистрирует его "
            "выход. `callback(func, *args)` регистрирует функцию, которую "
            "нужно вызвать при выходе (аналог `finally`). `pop_all()` "
            "переносит зарегистрированные выходы в новый стек, не выполняя их."
        ),
        example(
            "python",
            """
            from contextlib import ExitStack

            def make_backup():
                print("Создаём бэкап")

            try:
                with ExitStack() as stack:
                    stack.callback(make_backup)
                    raise ValueError("ошибка")
            except ValueError:
                pass
            """,
        ),
        example("text", "Создаём бэкап"),
        heading("Асинхронные контекстные менеджеры"),
        text(
            "Python 3.10+ поддерживает `async with` для асинхронных "
            "менеджеров. У них методы `__aenter__` и `__aexit__` (корутины). "
            "Используются для асинхронных соединений с БД, HTTP-клиентов, "
            "асинхронных блокировок."
        ),
        example(
            "python",
            """
            import asyncio

            class AsyncLock:
                def __init__(self):
                    self._lock = asyncio.Lock()

                async def __aenter__(self):
                    await self._lock.acquire()
                    return self

                async def __aexit__(self, *args):
                    self._lock.release()
                    return False


            async def worker(name, lock):
                async with lock:
                    print(f"{name} работает")
                    await asyncio.sleep(0.01)

            async def main():
                lock = AsyncLock()
                await asyncio.gather(worker("A", lock), worker("B", lock))

            asyncio.run(main())
            """,
        ),
        example("text", "A работает\nB работает"),
        text(
            "`async with` вызывает `__aenter__` и `__aexit__` через `await`. "
            "Внутри блока можно использовать `await`. `asyncio.Lock` и "
            "`asyncio.Semaphore` уже являются асинхронными контекстными "
            "менеджерами."
        ),
        heading("Вложенные контекстные менеджеры"),
        text(
            "Несколько `with` могут вкладываться друг в друга. Они выполняются "
            "последовательно: входы — в порядке написания, выходы — в обратном. "
            "Python 3.10+ позволяет писать несколько менеджеров в одном `with` "
            "через запятую: `with open(a) as f1, open(b) as f2:`."
        ),
        example(
            "python",
            """
            with open("a.txt", "w") as f1, open("b.txt", "w") as f2:
                f1.write("a")
                f2.write("b")
            # Оба файла закрыты
            """,
        ),
        text(
            "При вложении руками порядок выхода обратный: внутренний `with` "
            "завершается раньше внешнего. Это важно, если внешний ресурс "
            "зависит от внутреннего (например, транзакция и курсор)."
        ),
        heading("Контекстные менеджеры в стандартной библиотеке"),
        text(
            "Многие объекты стандартной библиотеки уже являются контекстными "
            "менеджерами. Их можно использовать в `with` без обёрток."
        ),
        table(
            ["Объект", "Модуль", "Что делает при выходе"],
            [
                ["`open(file)`", "`builtins`", "Закрывает файл"],
                ["`sqlite3.connect()`", "`sqlite3`", "Коммитит или откатывает транзакцию"],
                ["`threading.Lock()`", "`threading`", "Освобождает блокировку"],
                ["`socket.socket()`", "`socket`", "Закрывает сокет"],
                ["`tempfile.TemporaryDirectory()`", "`tempfile`", "Удаляет временную папку"],
                ["`gzip.open()`", "`gzip`", "Закрывает сжатый файл"],
                ["`mmap.mmap()`", "`mmap`", "Закрывает отображение памяти"],
            ],
        ),
        text(
            "Если объект не в таблице, проверьте наличие методов "
            "`__enter__`/`__exit__` или используйте `contextlib.closing`."
        ),
        heading("Собственные исключения в __exit__"),
        text(
            "Если `__exit__` сам поднимает исключение, оно заменяет исходное "
            "(если оно было). Это поведение может быть неожиданным. Лучше "
            "избегать исключений в `__exit__`; если очистка может упасть, "
            "обрабатывайте ошибки внутри."
        ),
        example(
            "python",
            """
            class BadExit:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    raise RuntimeError("ошибка очистки")


            try:
                with BadExit():
                    raise ValueError("оригинал")
            except Exception as e:
                print(type(e).__name__, e)
            """,
        ),
        example("text", "RuntimeError ошибка очистки"),
        text(
            "Исключение `ValueError` потерялось, вместо него вышло "
            "`RuntimeError` из `__exit__`. В реальном коде это скрывает "
            "причину проблемы. Оборачивайте очистку в `try/except` и "
            "логируйте ошибки, не поднимая их."
        ),
        heading("Производительность и накладные расходы"),
        text(
            "Контекстный менеджер добавляет накладные расходы: вызов двух "
            "методов, создание объекта-менеджера, обработка исключений. Для "
            "горячих путей, где критична производительность, иногда "
            "оправдано ручное управление ресурсами с `try/finally`. В 99% "
            "случаев накладные расходы `with` незначительны и перевешивают "
            "безопасность."
        ),
        example(
            "python",
            """
            import timeit

            class Resource:
                def __enter__(self): return self
                def __exit__(self, *a): pass
                def work(self): pass

            with_time = timeit.timeit("with Resource() as r: r.work()", globals=globals(), number=100000)
            try_time = timeit.timeit("r=Resource(); r.work(); r.__exit__(None,None,None)", globals=globals(), number=100000)
            print(f"with: {with_time:.3f}s, try: {try_time:.3f}s")
            """,
        ),
        text(
            "Разница обычно в микросекундах на вызов. Для файлов, сети и БД "
            "накладные расходы невидимы на фоне ввода-вывода."
        ),
        heading("Сравнение с try/finally"),
        text(
            "`with` — синтаксический сахар над `try/finally`. Эквивалент: "
            "`mgr = EXPR; val = mgr.__enter__(); try: BLOCK finally: "
            "mgr.__exit__(*sys.exc_info())`. Разница в том, что `with` "
            "автоматически передаёт информацию об исключении в `__exit__` и "
            "позволяет подавить его возвратом `True`."
        ),
        table(
            ["Конструкция", "Особенности"],
            [
                ["`try/finally`", "Ручное управление, полный контроль, больше кода"],
                ["`with`", "Автоматические __enter__/__exit__, подавление исключений, читаемость"],
                ["`contextlib.ExitStack`", "Динамическое число ресурсов, callback, LIFO"],
            ],
        ),
        text(
            "Используйте `with` везде, где есть ресурс с понятным жизненным "
            "циклом. `try/finally` оставьте для случаев, когда нет "
            "подходящего менеджера или нужна нестандартная логика."
        ),
        heading("ContextDecorator — декоратор и менеджер сразу"),
        text(
            "`contextlib.ContextDecorator` — базовый класс, экземпляры которого "
            "работают и как контекстные менеджеры (`with`), и как декораторы "
            "функций (`@`). Удобно для таймеров, логгеров и профилировщиков."
        ),
        example(
            "python",
            """
            from contextlib import ContextDecorator
            import time

            class timer(ContextDecorator):
                def __init__(self, name):
                    self.name = name

                def __enter__(self):
                    self.start = time.perf_counter()
                    return self

                def __exit__(self, *exc):
                    elapsed = time.perf_counter() - self.start
                    print(f"{self.name}: {elapsed:.4f}s")
                    return False


            @timer("функция")
            def compute():
                return sum(range(1_000_000))

            with timer("блок"):
                sum(range(1_000_000))
            """,
        ),
        example("text", "функция: 0.0123s\nблок: 0.0123s"),
        text(
            "Класс наследуется от `ContextDecorator` и реализует "
            "`__enter__`/`__exit__`. Декоратор создаёт экземпляр и вызывает "
            "`__enter__` перед функцией, `__exit__` после. Внутри функции "
            "доступен `self` через замыкание, но обычно не нужен."
        ),
        heading("Когда не нужен контекстный менеджер"),
        text(
            "Если ресурс живут недолго и очистка тривиальна (например, "
            "временная переменная), `with` избыточен. Не оборачивайте всё в "
            "`with` ради `with`: читаемость важнее следования паттерну. "
            "Используйте контекстные менеджеры там, где есть внешний "
            "ресурс: файл, сокет, блокировка, транзакция, временная "
            "директория, изменение глобального состояния."
        ),
        heading("Отладка контекстных менеджеров"),
        text(
            "При ошибке в `__enter__` блок не выполняется, и `__exit__` не "
            "вызывается. Если `__enter__` вернул значение, но внутри блока "
            "произошло исключение, `__exit__` получает его через аргументы. "
            "Для отладки полезно печатать этапы: `print('enter')`, "
            "`print('exit', exc_type)`."
        ),
        example(
            "python",
            """
            class DebugCM:
                def __enter__(self):
                    print("__enter__")
                    return "value"

                def __exit__(self, exc_type, exc_val, exc_tb):
                    print(f"__exit__: {exc_type}")
                    return False


            try:
                with DebugCM() as v:
                    print(f"block: {v}")
                    raise ValueError("oops")
            except ValueError:
                pass
            """,
        ),
        example("text", "__enter__\nblock: value\n__exit__: <class 'ValueError'>"),
        text(
            "`__exit__` видит тип исключения. Если бы мы вернули `True`, "
            "программа продолжилась бы после `with`."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                [
                    "Забыть return в __enter__",
                    "`as` получает `None`.",
                    "Возвращать нужный объект из `__enter__`.",
                ],
                [
                    "__exit__ не принимает 3 аргумента",
                    "TypeError при исключении.",
                    "Сигнатура: `__exit__(self, exc_type, exc_val, exc_tb)`.",
                ],
                [
                    "yield не в try/except при @contextmanager",
                    "Исключение не ловится внутри генератора.",
                    "Оборачивать yield в try/except/finally.",
                ],
                [
                    "ExitStack без enter_context",
                    "Ресурс не зарегистрирован на выход.",
                    "Всегда `stack.enter_context(mgr)`.",
                ],
                [
                    "async with для синхронного менеджера",
                    "TypeError: __aenter__ not defined.",
                    "Использовать обычный with или асинхронный менеджер.",
                ],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Каждое проверяет конкретный приём."
        ),
        numbered(
            "Напишите класс `Transaction`, который в `__enter__` начинает транзакцию (печатает «BEGIN»), а в `__exit__` делает `COMMIT` при успехе или `ROLLBACK` при исключении.",
            "Создайте генераторный менеджер `@contextmanager` под названием `cd(new_dir)`, который меняет текущую директорию на `new_dir` внутри блока и восстанавливает старую при выходе (используйте `os.chdir` и `os.getcwd`).",
            "Используйте `ExitStack`, чтобы открыть список файлов `['1.txt', '2.txt', '3.txt']` на запись, записать в каждый свой номер и гарантированно закрыть все.",
            "Напишите асинхронный контекстный менеджер `async_timer`, который замеряет время выполнения асинхронного блока и печатает результат.",
            "Сделайте менеджер `@contextmanager` под названием `suppress(*exceptions)`, который подавляет перечисленные типы исключений.",
        ),
        text("Пример ожидаемого результата для второго задания:"),
        example("text", "/home/user\n/tmp\n/home/user"),
        callout(
            "success",
            "Подсказка",
            "Для `cd`: сохраните `old = os.getcwd()`, сделайте `os.chdir(new_dir)`, "
            "`yield`, затем в `finally` верните `os.chdir(old)`."
        ),
        heading("Проверьте себя"),
        numbered(
            "В какой момент вызывается __exit__: до или после выполнения блока?",
            "Что означает возврат True из __exit__?",
            "Чем @contextmanager отличается от класса с __enter__/__exit__?",
            "Зачем нужен ExitStack, если можно написать несколько with подряд?",
            "Какие методы должны быть у асинхронного контекстного менеджера?",
        ),
        heading("Ответы", 3),
        numbered(
            "После: при нормальном завершении и при исключении. При исключении аргументы exc_type, exc_val, exc_tb не None.",
            "True подавляет исключение (оно считается обработанным), False/None — пробрасывает дальше.",
            "`@contextmanager` — генератор с одним yield, короче для простых случаев. Класс даёт больше контроля и сохраняет состояние в self.",
            "ExitStack нужен, когда число ресурсов известно только во время выполнения (список файлов). Несколько with подряд требуют известного заранее количества.",
            "`__aenter__` и `__aexit__` — обе корутины (async def). Используются с `async with`.",
        ),
        heading("Итоги"),
        bullets(
            "`with` гарантирует очистку: вызывает `__enter__` при входе, `__exit__` при выходе.",
            "`__exit__(exc_type, exc_val, exc_tb)` получает информацию об исключении; возврат `True` подавляет его.",
            "`@contextmanager` превращает генератор с `yield` в менеджер: до yield — `__enter__`, после — `__exit__`.",
            "`ExitStack` управляет динамическим набором ресурсов: `enter_context`, `callback`, `pop_all`.",
            "`async with` работает с `__aenter__`/`__aexit__` для асинхронных ресурсов.",
        ),
        heading("Что дальше"),
        text(
            "Контекстные менеджеры — стандартный способ работы с ресурсами. В "
            "следующем уроке разберём типизацию: как статические проверки "
            "помогают находить ошибки до запуска и как описывать сложные типы "
            "данных."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "PEP 343: `peps.python.org/pep-0343/` — контекстные менеджеры и with.",
            "Модуль `contextlib`: `docs.python.org/3/library/contextlib.html` — полный справочник.",
            "Асинхронные менеджеры: `docs.python.org/3/reference/datamodel.html#async-context-managers`.",
        ),
    ],
}