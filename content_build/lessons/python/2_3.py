"""Урок 2.3 курса Python: декораторы и замыкания."""

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
    "topic_order": 3,
    "name": "2.3. Декораторы и замыкания",
    "slug": "python-2-3-декораторы-и-замыкания",
    "short_description": (
        "Замыкания, функции высшего порядка, синтаксис @декоратор, "
        "functools.wraps и практические паттерны: кэш, логирование, retry."
    ),
    "topic_name": "Декораторы и замыкания",
    "topic_description": (
        "Как функции могут создавать другие функции, запоминать внешние "
        "переменные и изменять поведение других функций без переписывания."
    ),
    "learning_objectives": [
        "Объяснять, что такое замыкание и как работает лексическая область видимости",
        "Писать декораторы без аргументов и с аргументами",
        "Использовать functools.wraps для сохранения имени и документации",
        "Применять lru_cache, singledispatch и cached_property",
        "Создавать декораторы для логирования, замера времени и повторных попыток",
    ],
    "estimated_minutes": 40,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "python",
        "декораторы",
        "замыкания",
        "functools",
        "lru_cache",
    ],
    "starter_code": code(
        """
        def timer(func):
            import time
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                print(f"{func.__name__}: {time.perf_counter() - start:.4f}s")
                return result
            return wrapper


        @timer
        def slow():
            import time
            time.sleep(0.1)


        slow()
        """
    ),
    "hints": [
        "Декоратор — функция, принимающая функцию и возвращающая функцию.",
        "Замыкание запоминает переменные из внешней области видимости.",
        "Всегда используйте @functools.wraps, иначе help() покажет wrapper.",
    ],
    "content": [
        text(
            "Функция в Python — полноценный объект: её можно присваивать "
            "переменной, передавать в другую функцию, возвращать из функции "
            "и класть в списки. Такое свойство называется **функциями "
            "первого класса**. Оно открывает мощные приёмы: функция может "
            "создавать другую функцию, запоминать значения между вызовами и "
            "менять поведение чужого кода, не трогая его исходник.\n\n"
            "В этом уроке разберём **замыкания** — функции, которые запоминают "
            "переменные из места своего создания, и **декораторы** — удобный "
            "синтаксис для оборачивания функций в дополнительную логику. Это "
            "база для метапрограммирования и многих паттернов в библиотеках."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "создавать замыкания и понимать, почему внутренняя функция видит внешние переменные;",
            "писать декораторы без аргументов и с аргументами через тройное вложение;",
            "сохранять метаданные оригинальной функции через functools.wraps;",
            "использовать lru_cache для мемоизации, singledispatch для перегрузки, cached_property для ленивых свойств;",
            "собирать практические декораторы: таймер, логгер, retry, валидатор аргументов.",
        ),
        heading("Функции — объекты первого класса"),
        text(
            "**Объект первого класса** — сущность, которой можно присваивать "
            "имя, передавать как аргумент, возвращать из функции и хранить в "
            "структуре данных. В Python функции подходят под это определение "
            "полностью."
        ),
        example(
            "python",
            """
            def greet(name):
                return f"Привет, {name}!"


            say_hello = greet
            print(say_hello("Анна"))

            def call_twice(func, arg):
                return func(arg) + " " + func(arg)

            print(call_twice(greet, "Борис"))
            """,
        ),
        example("text", "Привет, Анна!\nПривет, Борис! Привет, Борис!"),
        text(
            "Присваивание `say_hello = greet` не вызывает функцию, а делает "
            "второе имя для того же объекта. Передача в `call_twice` работает "
            "аналогично: `func` внутри — это та же функция `greet`."
        ),
        heading("Возврат функции из функции"),
        text(
            "Функция может создавать и возвращать другую функцию. Внутренняя "
            "функция получает доступ к переменным внешней — это и есть "
            "**замыкание**."
        ),
        example(
            "python",
            """
            def make_greeter(prefix):
                def greeter(name):
                    return f"{prefix}, {name}!"
                return greeter


            formal = make_greeter("Здравствуйте")
            casual = make_greeter("Привет")

            print(formal("Виктор"))
            print(casual("Виктор"))
            """,
        ),
        example("text", "Здравствуйте, Виктор!\nПривет, Виктор!"),
        text(
            "Каждый вызов `make_greeter` создаёт новую функцию `greeter`, "
            "которая запоминает свой `prefix`. Переменная `prefix` не "
            "является глобальной и не передаётся явно — она **захвачена** в "
            "замыкании. Атрибут `__closure__` показывает захваченные значения."
        ),
        example(
            "python",
            """
            def make_adder(x):
                def adder(y):
                    return x + y
                return adder


            add5 = make_adder(5)
            print(add5.__closure__[0].cell_contents)
            print(add5(3))
            """,
        ),
        example("text", "5\n8"),
        heading("Замыкания и лексическая область видимости"),
        text(
            "**Лексическая область видимости** означает, что переменные ищутся "
            "по структуре исходного кода: сначала в локальной области, потом "
            "в объемлющих функциях, потом в глобальной и встроенной. Замыкание "
            "фиксирует эту цепочку в момент создания."
        ),
        example(
            "python",
            """
            def make_multiplier(factor):
                def multiplier(n):
                    return n * factor
                return multiplier


            double = make_multiplier(2)
            triple = make_multiplier(3)

            print(double(5))
            print(triple(5))
            """,
        ),
        example("text", "10\n15"),
        callout(
            "warning",
            "Позднее связывание в циклах",
            "Лямбда в цикле захватывает переменную, а не её значение. Все "
            "функции увидят последнее значение. Решение: `lambda i=i: i` или "
            "`functools.partial`.",
        ),
        example(
            "python",
            """
            funcs = []
            for i in range(3):
                funcs.append(lambda i=i: i)

            print([f() for f in funcs])
            """,
        ),
        example("text", "[0, 1, 2]"),
        text(
            "Параметр `i=i` создаёт локальную копию значения на каждой "
            "итерации. Без неё все лямбды ссылаются на одну переменную `i`, "
            "которая к концу цикла равна `2`."
        ),
        heading("nonlocal — изменение захваченной переменной"),
        text(
            "По умолчанию замыкание может читать захваченные переменные, но "
            "не присваивать им новые значения — присваивание создало бы "
            "локальную переменную. Ключевое слово `nonlocal` разрешает "
            "менять переменную в объемлющей области."
        ),
        example(
            "python",
            """
            def counter():
                count = 0
                def inc():
                    nonlocal count
                    count += 1
                    return count
                return inc


            c = counter()
            print(c())
            print(c())
            print(c())
            """,
        ),
        example("text", "1\n2\n3"),
        text(
            "Без `nonlocal` строка `count += 1` вызвала бы `UnboundLocalError`, "
            "потому что Python бы решил, что `count` — локальная, но её нет. "
            "`nonlocal` говорит: «используй `count` из внешней функции»."
        ),
        heading("Декораторы"),
        text(
            "**Декоратор** — функция, принимающая другую функцию и возвращающая "
            "новую функцию, которая обычно вызывает оригинал и добавляет "
            "какую-то логику. Синтаксис `@decorator` над определением функции "
            "эквивалентен присваиванию: `func = decorator(func)`."
        ),
        example(
            "python",
            """
            def uppercase(func):
                def wrapper(*args, **kwargs):
                    result = func(*args, **kwargs)
                    return result.upper()
                return wrapper


            @uppercase
            def greet(name):
                return f"Привет, {name}"

            print(greet("Анна"))
            """,
        ),
        example("text", "ПРИВЕТ, АННА"),
        text(
            "Здесь `uppercase` — декоратор. Он получает `greet`, создаёт "
            "`wrapper`, который вызывает оригинал и преобразует результат. "
            "Имя `greet` теперь ссылается на `wrapper`, а оригинал доступен "
            "только внутри замыкания."
        ),
        heading("Декораторы с аргументами"),
        text(
            "Если декоратору нужны параметры, добавляют ещё один уровень "
            "вложенности: внешняя функция принимает аргументы декоратора и "
            "возвращает сам декоратор (функцию от функции)."
        ),
        example(
            "python",
            """
            def repeat(times):
                def decorator(func):
                    def wrapper(*args, **kwargs):
                        for _ in range(times):
                            result = func(*args, **kwargs)
                        return result
                    return wrapper
                return decorator


            @repeat(3)
            def say_hello():
                print("Привет")

            say_hello()
            """,
        ),
        example("text", "Привет\nПривет\nПривет"),
        text(
            "Вызов `@repeat(3)` выполняется сразу при определении функции и "
            "возвращает декоратор, который затем применяется к `say_hello`. "
            "Это три уровня: фабрика декораторов → декоратор → обёртка."
        ),
        heading("functools.wraps"),
        text(
            "Декоратор заменяет функцию на обёртку, поэтому `func.__name__`, "
            "`__doc__` и аннотации указывают на `wrapper`. `functools.wraps` "
            "копирует эти атрибуты из оригинала в обёртку."
        ),
        example(
            "python",
            """
            from functools import wraps

            def log_calls(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    print(f"Вызов {func.__name__}")
                    return func(*args, **kwargs)
                return wrapper


            @log_calls
            def add(a, b):
                \"\"\"Складывает два числа.\"\"\"
                return a + b


            print(add.__name__)
            print(add.__doc__)
            """,
        ),
        example("text", "add\nСкладывает два числа."),
        text(
            "Без `@wraps` имя было бы `wrapper`, а документация — `None`. "
            "Всегда используйте `wraps`: без неё отладка и `help()` становятся "
            "бесполезными."
        ),
        heading("Стандартные декораторы из functools"),
        text(
            "Модуль `functools` содержит готовые декораторы для частых задач."
        ),
        heading("lru_cache — мемоизация"),
        text(
            "`@lru_cache` запоминает результаты вызовов по аргументам. "
            "Повторный вызов с теми же аргументами возвращает сохранённый "
            "результат мгновенно. Идеально для чистых функций с тяжёлыми "
            "вычислениями или рекурсией."
        ),
        example(
            "python",
            """
            from functools import lru_cache

            @lru_cache(maxsize=None)
            def fib(n):
                if n < 2:
                    return n
                return fib(n - 1) + fib(n - 2)

            print(fib(30))
            print(fib.cache_info())
            """,
        ),
        example("text", "832040\nCacheInfo(hits=28, misses=31, maxsize=None, currsize=31)"),
        text(
            "Без кэша рекурсивное Фибоначчи работало бы экспоненциально "
            "долго. `maxsize=None` отключает ограничение размера. Метод "
            "`cache_info()` показывает статистику попаданий и промахов."
        ),
        heading("singledispatch — перегрузка по типу"),
        text(
            "`@singledispatch` позволяет регистрировать разные реализации "
            "одной функции для разных типов первого аргумента. Это "
            "перегрузка (overload) в стиле Python."
        ),
        example(
            "python",
            """
            from functools import singledispatch

            @singledispatch
            def process(value):
                print(f"Базовый: {value}")

            @process.register
            def _(value: int):
                print(f"Целое: {value * 2}")

            @process.register
            def _(value: str):
                print(f"Строка: {value.upper()}")

            process(5)
            process("hello")
            process([1, 2])
            """,
        ),
        example("text", "Целое: 10\nСтрока: HELLO\nБазовый: [1, 2]"),
        heading("cached_property — ленивое свойство"),
        text(
            "`@cached_property` (Python 3.8+) вычисляет значение один раз при "
            "первом обращении и сохраняет его как атрибут экземпляра. "
            "Повторные обращения возвращают сохранённое значение без "
            "пересчёта. Удобно для дорогих вычислений, которые не меняются."
        ),
        example(
            "python",
            """
            from functools import cached_property
            import time

            class DataProcessor:
                def __init__(self, data):
                    self.data = data

                @cached_property
                def sorted_data(self):
                    print("Сортировка...")
                    time.sleep(0.1)
                    return sorted(self.data)


            dp = DataProcessor([3, 1, 2])
            print(dp.sorted_data)
            print(dp.sorted_data)
            """,
        ),
        example("text", "Сортировка...\n[1, 2, 3]\n[1, 2, 3]"),
        heading("Практические паттерны декораторов"),
        heading("Таймер"),
        example(
            "python",
            """
            from functools import wraps
            import time

            def timer(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    start = time.perf_counter()
                    result = func(*args, **kwargs)
                    elapsed = time.perf_counter() - start
                    print(f"{func.__name__}: {elapsed:.4f}s")
                    return result
                return wrapper


            @timer
            def slow():
                time.sleep(0.05)


            slow()
            """,
        ),
        example("text", "slow: 0.0501s"),
        heading("Логирование вызовов"),
        example(
            "python",
            """
            from functools import wraps

            def log_calls(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    print(f"→ {func.__name__}({args}, {kwargs})")
                    result = func(*args, **kwargs)
                    print(f"← {func.__name__} = {result}")
                    return result
                return wrapper


            @log_calls
            def add(a, b):
                return a + b


            add(2, 3)
            """,
        ),
        example("text", "→ add((2, 3), {})\n← add = 5"),
        heading("Retry с задержкой"),
        example(
            "python",
            """
            from functools import wraps
            import time

            def retry(times=3, delay=0.1):
                def decorator(func):
                    @wraps(func)
                    def wrapper(*args, **kwargs):
                        for attempt in range(times):
                            try:
                                return func(*args, **kwargs)
                            except Exception:
                                if attempt == times - 1:
                                    raise
                                time.sleep(delay)
                    return wrapper
                return decorator


            @retry(times=3, delay=0.01)
            def flaky():
                import random
                if random.random() < 0.7:
                    raise ValueError("не повезло")
                return "успех"


            print(flaky())
            """,
        ),
        text("успех (или ValueError после 3 попыток)"),
        heading("Валидация аргументов"),
        example(
            "python",
            """
            from functools import wraps

            def validate_types(**expected):
                def decorator(func):
                    @wraps(func)
                    def wrapper(*args, **kwargs):
                        for name, typ in expected.items():
                            if name in kwargs and not isinstance(kwargs[name], typ):
                                raise TypeError(f"{name} must be {typ}")
                        return func(*args, **kwargs)
                    return wrapper
                return decorator


            @validate_types(age=int, name=str)
            def register(name, age):
                return f"{name}, {age}"


            print(register("Анна", age=25))
            try:
                register("Борис", age="много")
            except TypeError as e:
                print(e)
            """,
        ),
        example("text", "Анна, 25\nage must be <class 'int'>"),
        heading("Класс-декораторы"),
        text(
            "Декоратором может быть не только функция, но и класс, "
            "реализующий метод `__call__`. Экземпляр такого класса ведёт "
            "себя как функция и может хранить состояние в своих атрибутах. "
            "Это удобно, когда декоратору нужно накапливать данные между "
            "вызовами."
        ),
        example(
            "python",
            """
            class CallCounter:
                def __init__(self, func):
                    self.func = func
                    self.count = 0

                def __call__(self, *args, **kwargs):
                    self.count += 1
                    return self.func(*args, **kwargs)


            @CallCounter
            def add(a, b):
                return a + b


            add(1, 2)
            add(3, 4)
            print(add.count)
            """,
        ),
        example("text", "2"),
        text(
            "`__init__` получает декорируемую функцию и сохраняет её. "
            "`__call__` выполняется при каждом вызове и имеет доступ к "
            "`self.count`. Такой подход чище, чем атрибуты на функции-"
            "обёртке, и позволяет добавлять методы для управления состоянием."
        ),
        heading("Композиция декораторов"),
        text(
            "Несколько декораторов применяются снизу вверх: нижний выполняется "
            "первым, его результат передаётся выше. Порядок важен: "
            "`@timer @log_calls` засечёт время всего, включая логирование, а "
            "`@log_calls @timer` засечёт только выполнение функции."
        ),
        example(
            "python",
            """
            def log(func):
                def wrapper(*a, **kw):
                    print(f"log: {func.__name__}")
                    return func(*a, **kw)
                return wrapper

            def timeit(func):
                def wrapper(*a, **kw):
                    print(f"time: {func.__name__}")
                    return func(*a, **kw)
                return wrapper

            @log
            @timeit
            def foo():
                pass

            foo()
            """,
        ),
        example("text", "log: foo\ntime: foo"),
        text(
            "Правило: декоратор, написанный ближе к `def`, оборачивает "
            "функцию первым. Читать составной декоратор нужно снизу вверх."
        ),
        heading("Декораторы методов и self"),
        text(
            "Когда декоратор применяется к методу класса, первым аргументом "
            "в обёртку приходит `self`. Обёртка должна его принимать и "
            "передавать дальше. `*args, **kwargs` решает эту задачу "
            "автоматически."
        ),
        example(
            "python",
            """
            def log_calls(func):
                def wrapper(*args, **kwargs):
                    print(f"Вызов {func.__name__}")
                    return func(*args, **kwargs)
                return wrapper


            class Calculator:
                @log_calls
                def add(self, a, b):
                    return a + b


            calc = Calculator()
            calc.add(2, 3)
            """,
        ),
        example("text", "Вызов add\n5"),
        text(
            "Первый элемент `args` — это `self`. Обёртка не должна знать об "
            "этом, она просто передаёт всё дальше. Если декоратор должен "
            "работать и с функциями, и с методами, `*args, **kwargs` — "
            "единственный надёжный способ."
        ),
        heading("Декораторы для классов"),
        text(
            "Декоратор можно применять к классу: он получает класс и "
            "возвращает новый класс или модифицирует исходный. Это основа "
            "паттерна «декоратор класса» и используется в `dataclass`, "
            "`singleton` и библиотеках вроде `attrs`."
        ),
        example(
            "python",
            """
            def add_repr(cls):
                def __repr__(self):
                    attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
                    return f"{cls.__name__}({attrs})"
                cls.__repr__ = __repr__
                return cls


            @add_repr
            class Point:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y


            print(Point(1, 2))
            """,
        ),
        example("text", "Point(x=1, y=2)"),
        text(
            "Декоратор добавляет метод `__repr__` к классу. Такой приём "
            "использует `dataclasses.dataclass` для генерации `__init__`, "
            "`__repr__`, `__eq__` и других методов."
        ),
        heading("Context manager как декоратор"),
        text(
            "Контекстный менеджер (объект с `__enter__` и `__exit__`) можно "
            "использовать как декоратор через `contextlib.contextmanager`. "
            "Это позволяет оборачивать функцию в `with`-блок."
        ),
        example(
            "python",
            """
            from contextlib import contextmanager
            import time

            @contextmanager
            def timed():
                start = time.perf_counter()
                yield
                print(f"Время: {time.perf_counter() - start:.4f}s")


            @timed()
            def slow():
                time.sleep(0.05)


            slow()
            """,
        ),
        example("text", "Время: 0.0501s"),
        text(
            "Функция с `@contextmanager` должна содержать `yield`. Код до "
            "`yield` выполняется при входе в `with`, после — при выходе. Как "
            "декоратор она автоматически оборачивает вызов функции в этот "
            "контекст."
        ),
        heading("Профилирование декораторами"),
        text(
            "Декораторы удобны для измерения не только времени, но и памяти, "
            "вызовов функций и покрытия кода. Библиотека `cProfile` и модуль "
            "`tracemalloc` можно обернуть в декоратор для точечного "
            "профилирования отдельных функций без изменения их кода."
        ),
        example(
            "python",
            """
            import cProfile
            import pstats
            from functools import wraps

            def profile(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    profiler = cProfile.Profile()
                    profiler.enable()
                    result = func(*args, **kwargs)
                    profiler.disable()
                    stats = pstats.Stats(profiler).sort_stats("cumulative")
                    stats.print_stats(10)
                    return result
                return wrapper


            @profile
            def compute():
                return sum(i * i for i in range(10000))


            compute()
            """,
        ),
        text(
            "Декоратор включает профилировщик, выполняет функцию, выводит "
            "топ-10 функций по накопленному времени и возвращает результат. "
            "Это полезно для поиска узких мест в конкретной функции без "
            "запуска всего приложения под профилировщиком."
        ),
        heading("Когда не использовать декораторы"),
        text(
            "Декораторы добавляют слой косвенности. Если логика простая и "
            "вызывается в одном месте, явный вызов функции-обёртки читается "
            "лучше. Декоратор оправдан, когда одна и та же обёртка применяется "
            "ко многим функциям (логирование, кэш, валидация, тайминг) или "
            "когда нужно изменить поведение библиотечной функции без доступа "
            "к исходнику. Избыточные декораторы усложняют отладку: стек вызовов "
            "становится глубже, а точки останова в обёртке срабатывают "
            "неожиданно."
        ),
        heading("Продвинутые паттерны"),
        text(
            "Некоторые библиотеки используют декораторы для декларативного "
            "описания поведения. Фреймворки вроде FastAPI, Flask, Celery "
            "регистрируют маршруты, задачи и обработчики через декораторы. "
            "Понимание механики позволяет читать такой код и писать свои "
            "аналоги для внутренних инструментов."
        ),
        example(
            "python",
            """
            # Пример декларативного API
            routes = {}

            def route(path):
                def decorator(func):
                    routes[path] = func
                    return func
                return decorator


            @route("/")
            def index():
                return "Главная"

            @route("/about")
            def about():
                return "О нас"

            print(routes)
            """,
        ),
        example("text", "{'/': <function index at 0x...>, '/about': <function about at 0x...>}"),
        text(
            "Словарь `routes` заполняется в момент импорта модуля. Веб-сервер "
            "потом ищет обработчик по пути и вызывает соответствующую функцию. "
            "Такой паттерн — основа маршрутизации во многих фреймворках."
        ),
        heading("Отладка декораторов"),
        text(
            "Отладка декорированных функций сложнее: в стеке вызовов "
            "появляются лишние фреймы `wrapper`, а точки останова срабатывают "
            "дважды. Помогают: `@wraps` (сохраняет имя), печать `func.__name__` "
            "внутри обёртки, и запуск без декоратора через доступ к "
            "оригиналу: `decorated_func.__wrapped__` (добавляет `wraps`)."
        ),
        example(
            "python",
            """
            from functools import wraps

            def log(func):
                @wraps(func)
                def wrapper(*a, **kw):
                    print(f"before {func.__name__}")
                    return func(*a, **kw)
                return wrapper


            @log
            def add(a, b):
                return a + b


            print(add.__wrapped__(2, 3))
            """,
        ),
        example("text", "5"),
        text(
            "`__wrapped__` — атрибут, который добавляет `wraps` и указывает "
            "на оригинальную функцию. Это позволяет тестировать и отлаживать "
            "чистую логику без обёртки."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                [
                    "Забыть @wraps",
                    "`help()` и `__name__` показывают wrapper.",
                    "Всегда `@wraps(func)` над `wrapper`.",
                ],
                [
                    "Декоратор без аргументов вместо с аргументами",
                    "TypeError: декоратор вызван с аргументами.",
                    "Три уровня: фабрика → декоратор → обёртка.",
                ],
                [
                    "Захват переменной цикла в лямбде",
                    "Все функции видят последнее значение.",
                    "`lambda i=i: i` или `partial`.",
                ],
                [
                    "lru_cache на изменяемых аргументах",
                    "TypeError: unhashable type.",
                    "Только хешируемые аргументы (числа, строки, кортежи).",
                ],
                [
                    "nonlocal на глобальной переменной",
                    "SyntaxError.",
                    "`global` для глобальных, `nonlocal` для объемлющих.",
                ],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Каждое проверяет конкретный приём."
        ),
        numbered(
            "Напишите декоратор `@count_calls`, который считает, сколько раз была вызвана функция, и сохраняет счётчик в атрибуте `call_count`.",
            "Создайте замыкание `make_validator(min_len, max_len)`, возвращающее функцию, проверяющую длину строки.",
            "Используйте `@lru_cache` для оптимизации рекурсивной функции `factorial(n)`.",
            "Напишите декоратор `@require_role(role)`, который проверяет, что у переданного пользователя (объект с полем `role`) нужная роль, иначе поднимает `PermissionError`.",
            "Сделайте декоратор `@deprecated`, который печатает предупреждение при вызове функции, но выполняет её.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example("text", "call_count = 3"),
        callout(
            "success",
            "Подсказка",
            "Для `@count_calls`: обёртка увеличивает `wrapper.call_count += 1` "
            "и возвращает результат. Инициализируйте `wrapper.call_count = 0` "
            "при создании.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Что такое замыкание?",
            "В чём разница между `@decorator` и `@decorator(args)`?",
            "Зачем нужен `functools.wraps`?",
            "Почему `lru_cache` не работает с списками в аргументах?",
            "Что делает `nonlocal`?",
        ),
        heading("Ответы", 3),
        numbered(
            "Функция, которая запоминает переменные из объемлющей области видимости и может к ним обращаться после завершения внешней функции.",
            "`@decorator` — просто функция-декоратор. `@decorator(args)` — фабрика, которая принимает аргументы и возвращает декоратор.",
            "Копирует `__name__`, `__doc__`, `__annotations__` из оригинальной функции в обёртку, чтобы отладка и `help()` работали корректно.",
            "Ключи кэша должны быть хешируемыми. Списки изменяемы и нехешируемы. Используйте кортежи вместо списков.",
            "Разрешает присваивание переменной из объемлющей (не глобальной) области видимости внутри вложенной функции.",
        ),
        heading("Итоги"),
        bullets(
            "Функции — объекты первого класса: их можно передавать, возвращать и хранить.",
            "Замыкание захватывает переменные из внешней области видимости по ссылке.",
            "Декоратор — функция от функции, синтаксис `@` — сахар для присваивания.",
            "Декораторы с аргументами требуют трёх уровней вложенности.",
            "`functools.wraps` сохраняет метаданные оригинала.",
            "`lru_cache`, `singledispatch`, `cached_property` — готовые декораторы для кэша, перегрузки и ленивых свойств.",
        ),
        heading("Что дальше"),
        text(
            "Декораторы и замыкания — основа метапрограммирования. В "
            "следующем уроке разберём генераторы и итераторы: как создавать "
            "последовательности, которые вычисляются по требованию, и как "
            "работает протокол итерации в Python."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Официальный HOWTO: `docs.python.org/3/howto/functional.html` — функции высшего порядка и декораторы.",
            "Модуль `functools`: `docs.python.org/3/library/functools.html` — полный справочник.",
            "PEP 318: `peps.python.org/pep-0318/` — история и детали синтаксиса декораторов.",
        ),
    ],
}