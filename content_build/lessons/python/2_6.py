"""Урок 2.6 курса Python: типизация и статический анализ."""

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
    "topic_order": 6,
    "name": "2.6. Типизация и статический анализ",
    "slug": "python-2-6-типизация-и-статический-анализ",
    "short_description": (
        "Аннотации типов, Generics, Union, Optional, Literal, TypedDict, "
        "Protocol и статический анализ через mypy."
    ),
    "topic_name": "Типизация и статический анализ",
    "topic_description": (
        "Как добавлять типы в Python-код, использовать дженерики, объединения "
        "и протоколы, и проверять корректность через mypy до запуска."
    ),
    "learning_objectives": [
        "Добавлять аннотации типов к переменным, функциям и методам",
        "Использовать Generics: list[int], dict[str, float], tuple[...]",
        "Применять Union, Optional, Literal для гибких типов",
        "Описывать структуру словарей через TypedDict",
        "Выражать структурную типизацию через Protocol",
        "Запускать mypy и читать его отчёты об ошибках",
    ],
    "estimated_minutes": 40,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "python",
        "типизация",
        "type hints",
        "mypy",
        "generics",
        "protocol",
    ],
    "starter_code": code(
        """
        def greet(name: str) -> str:
            return f"Привет, {name}!"

        print(greet("Анна"))
        """
    ),
    "hints": [
        "Аннотации не влияют на выполнение кода — это подсказки для инструментов и людей.",
        "Python 3.9+ позволяет писать list[int] вместо List[int] из typing.",
        "mypy проверяет типы статически, не запуская код.",
    ],
    "content": [
        text(
            "Python — динамически типизированный язык: типы проверяются во "
            "время выполнения. Это даёт гибкость, но ошибки вроде "
            "`\"строка\" + 5` или вызов несуществующего метода обнаруживаются "
            "только при запуске. **Аннотации типов** (type hints) позволяют "
            "описать ожидаемые типы в коде, а **статические анализаторы** вроде "
            "mypy проверяют их до запуска.\n\n"
            "В этом уроке разберём синтаксис аннотаций, дженерики для "
            "коллекций, объединения типов, литералы, типизированные словари, "
            "протоколы и как настроить mypy в проекте. Типизация не заменяет "
            "тесты, но находит целый класс ошибок до первого запуска."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "писать аннотации для переменных, аргументов функций и возвращаемых значений;",
            "использовать дженерики: list[int], dict[str, float], tuple[str, int];",
            "объединять типы через Union и оператор |, обозначать необязательные значения через Optional;",
            "задавать точные значения через Literal и структуру словарей через TypedDict;",
            "описывать интерфейсы через Protocol без наследования;",
            "запускать mypy, читать отчёты и настраивать строгость проверки.",
        ),
        heading("Базовые аннотации"),
        text(
            "Аннотация ставится после имени через двоеточие: `name: str = "
            "\"Анна\"`. Для функций: аргументы — `name: str`, возвращаемое "
            "значение — `-> str`. Аннотации не влияют на выполнение: Python "
            "их игнорирует, они нужны инструментам и читателям."
        ),
        example(
            "python",
            """
            age: int = 25
            name: str = "Анна"
            height: float = 1.75
            is_student: bool = True

            def greet(name: str) -> str:
                return f"Привет, {name}!"

            print(greet(name))
            """,
        ),
        example("text", "Привет, Анна!"),
        text(
            "Базовые типы: `int`, `float`, `str`, `bool`, `None`. `None` "
            "как тип пишется с заглавной буквы. Аннотации можно опускать там, "
            "где тип очевиден из значения, но для публичных функций лучше "
            "указывать явно."
        ),
        heading("Дженерики: коллекции с параметром типа"),
        text(
            "**Дженерики** (generics) — контейнеры, параметризованные типом "
            "элементов. В Python 3.9+ используются встроенные имена в нижнем "
            "регистре: `list[int]`, `dict[str, float]`, `set[str]`, "
            "`tuple[int, str]`. В старых версиях — `List[int]`, `Dict[str, "
            "float]` из модуля `typing`."
        ),
        example(
            "python",
            """
            numbers: list[int] = [1, 2, 3]
            user: dict[str, int] = {"age": 25, "score": 100}
            coords: tuple[float, float] = (55.75, 37.61)
            tags: set[str] = {"python", "typing"}

            print(numbers, user, coords, tags)
            """,
        ),
        example("text", "[1, 2, 3] {'age': 25, 'score': 100} (55.75, 37.61) {'python', 'typing'}"),
        text(
            "`tuple` с фиксированным числом элементов пишет типы каждого: "
            "`tuple[int, str, float]`. Для кортежа переменной длины с "
            "одинаковыми элементами: `tuple[int, ...]` (многоточие — часть "
            "синтаксиса)."
        ),
        example(
            "python",
            """
            fixed: tuple[int, str, float] = (1, "a", 1.0)
            variable: tuple[int, ...] = (1, 2, 3, 4)
            print(fixed, variable)
            """,
        ),
        example("text", "(1, 'a', 1.0) (1, 2, 3, 4)"),
        heading("Union, Optional, Literal"),
        text(
            "Часто значение может быть одного из нескольких типов. `Union[X, Y]` "
            "(или `X | Y` в Python 3.10+) означает «X или Y». `Optional[X]` — "
            "сокращение для `Union[X, None]`, то есть значение может отсутствовать."
        ),
        example(
            "python",
            """
            from typing import Union, Optional

            def process(value: Union[int, str]) -> str:
                return str(value)

            def find_user(id: int) -> Optional[str]:
                if id == 1:
                    return "Анна"
                return None

            print(process(42))
            print(process("текст"))
            print(find_user(1))
            print(find_user(2))
            """,
        ),
        example("text", "42\nтекст\nАнна\nNone"),
        text(
            "В Python 3.10+ можно писать `Union[int, str]` вместо `Union[int, str]` и "
            "`Optional[str]` вместо `Optional[str]`. Это короче и не требует "
            "импорта. `Literal` задаёт конкретные допустимые значения."
        ),
        example(
            "python",
            """
            from typing import Literal

            Mode = Literal["fast", "safe", "debug"]

            def run(mode: Mode) -> None:
                print(f"Режим: {mode}")

            run("fast")
            # run("unknown")  # mypy: Argument of type "unknown" is not assignable to "Mode"
            """,
        ),
        example("text", "Режим: fast"),
        heading("TypedDict — структура словаря"),
        text(
            "Обычный `dict[str, int]` говорит только о типах ключей и значений, "
            "но не о том, какие ключи обязательны. `TypedDict` описывает "
            "фиксированный набор ключей и их типы."
        ),
        example(
            "python",
            """
            from typing import TypedDict, Optional

            class User(TypedDict):
                name: str
                age: int
                email: Optional[str]

            def greet(user: User) -> str:
                return f"{user['name']}, {user['age']} лет"

            user: User = {"name": "Анна", "age": 25, "email": "anna@example.com"}
            print(greet(user))
            """,
        ),
        example("text", "Анна, 25 лет"),
        text(
            "Отсутствие обязательного ключа или лишний ключ будет ошибкой в "
            "mypy. `total=False` делает все ключи необязательными, `Required` "
            "и `NotRequired` (Python 3.11+) позволяют управлять по отдельности."
        ),
        heading("Protocol — структурная типизация"),
        text(
            "Обычная типизация номинальная: класс должен явно наследоваться от "
            "базового. **Protocol** (Python 3.8+) позволяет требовать наличие "
            "методов без наследования — «если у объекта есть эти методы, он "
            "подходит». Это **утиная типизация** на уровне типов."
        ),
        example(
            "python",
            """
            from typing import Protocol

            class Drawable(Protocol):
                def draw(self) -> None: ...


            class Circle:
                def draw(self) -> None:
                    print("Рисую круг")

            class Square:
                def draw(self) -> None:
                    print("Рисую квадрат")


            def render(shape: Drawable) -> None:
                shape.draw()


            render(Circle())
            render(Square())
            """,
        ),
        example("text", "Рисую круг\nРисую квадрат"),
        text(
            "`Circle` и `Square` не наследуются от `Drawable`, но имеют метод "
            "`draw`. mypy принимает их там, где нужен `Drawable`. Это позволяет "
            "писать гибкий код без наследования от базовых классов."
        ),
        heading("Callable — типизация функций"),
        text(
            "`Callable[[Arg1, Arg2], ReturnType]` описывает вызываемый объект "
            "с заданными типами аргументов и возвращаемого значения. Полезно "
            "для колбэков, декораторов и функций высшего порядка."
        ),
        example(
            "python",
            """
            from collections.abc import Callable

            def apply_twice(func: Callable[[int], int], x: int) -> int:
                return func(func(x))

            def add_one(x: int) -> int:
                return x + 1

            print(apply_twice(add_one, 5))
            """,
        ),
        example("text", "7"),
        heading("Статический анализ с mypy"),
        text(
            "**mypy** — статический анализатор типов для Python. Он читает "
            "исходный код, строит граф типов и сообщает о несоответствиях. "
            "Установка: `pip install mypy`. Запуск: `mypy файл.py` или "
            "`mypy папка/`."
        ),
        example(
            "bash",
            """
            pip install mypy
            mypy --strict main.py
            """,
        ),
        text(
            "Флаг `--strict` включает все проверки: необязательные аргументы, "
            "возвращаемые значения, неиспользуемые переменные и др. Без "
            "`--strict` mypy пропускает многие проверки."
        ),
        heading("Чтение отчёта mypy"),
        text(
            "Вывод mypy имеет формат: `файл:строка:колонка: код ошибки: сообщение`. "
            "Коды ошибок: `arg-type` — неверный тип аргумента, `return-value` — "
            "неверный тип возвращаемого значения, `attr-defined` — обращение к "
            "несуществующему атрибуту, `union-attr` — доступ к атрибуту, "
            "который есть не у всех типов в объединении."
        ),
        example(
            "text",
            """main.py:10: error: Argument 1 to "greet" has incompatible type "int"; expected "str"  [arg-type]
main.py:15: error: Function is missing a return statement  [return-value]
main.py:20: error: "User" has no attribute "phone"  [attr-defined]""",
        ),
        heading("Настройка mypy через pyproject.toml"),
        text(
            "Настройки проекта хранят в `pyproject.toml` секции `[tool.mypy]`. "
            "Это позволяет не передавать флаги каждый раз."
        ),
        example(
            "text",
            """[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true""",
        ),
        text(
            "`disallow_untyped_defs` требует аннотации у всех функций. "
            "`check_untyped_defs` проверяет и внутри неаннотированных функций. "
            "Начинать можно без `--strict`, постепенно включая проверки."
        ),
        heading("Игнорирование ошибок"),
        text(
            "Иногда mypy ошибается или код намеренно нарушает типы. "
            "Комментарий `# type: ignore` в конце строки подавляет ошибку на "
            "этой строке. `# type: ignore[code]` подавляет только конкретный "
            "код ошибки. Использовать экономно и с комментарием, почему."
        ),
        example(
            "python",
            """
            x: int = "строка"  # type: ignore[assignment]
            """,
        ),
        heading("TypeVar — параметризация функций"),
        text(
            "`TypeVar` позволяет писать обобщённые функции, где тип аргумента "
            "и возвращаемое значение связаны. Это основа дженерик-программирования."
        ),
        example(
            "python",
            """
            from typing import TypeVar

            T = TypeVar("T")

            def first(items: list[T]) -> T:
                return items[0]


            print(first([1, 2, 3]))
            print(first(["a", "b"]))
            """,
        ),
        example("text", "1\na"),
        text(
            "`T` — переменная типа. В первом вызове `T = int`, во втором `T = str`. "
            "mypy выведет типы автоматически. `TypeVar` можно ограничить: "
            "`TypeVar('T', int, str)` или сделать ковариантным/контравариантным."
        ),
        heading("Контравариантность и ковариантность"),
        text(
            "В дженериках важно, как подтипы соотносятся с параметром типа. "
            "`list` инвариантен: `list[int]` не подтип `list[object]`. "
            "`Callable` контравариантен по аргументам и ковариантен по возврату. "
            "Для неизменяемых контейнеров (`tuple`, `Sequence`) ковариантность "
            "разрешена."
        ),
        example(
            "python",
            """
            from typing import Sequence

            def process(seq: Sequence[int]) -> None:
                for x in seq:
                    print(x)

            # list[int] подходит, так как list — Sequence
            process([1, 2, 3])
            # tuple[int, ...] тоже подходит
            process((1, 2, 3))
            """,
        ),
        text(
            "`Sequence[int]` — ковариантный: `Sequence[int]` подтип "
            "`Sequence[object]`. Поэтому `list[int]` можно передать туда, где "
            "ожидается `Sequence[int]`. Для `list` это не работает, так как "
            "`list` изменяем."
        ),
        heading("Stub-файлы и py.typed"),
        text(
            "Для библиотек типы часто выносят в `.pyi` — стаб-файлы. Они "
            "содержат только сигнатуры без реализации. Папка с `py.typed` "
            "маркер-файлом сообщает mypy, что пакет поддерживает типизацию. "
            "Это позволяет пользователям библиотеки получать проверку типов "
            "без установки исходного кода."
        ),
        example(
            "text",
            """mypackage/
├── __init__.py
├── core.py
├── core.pyi
└── py.typed""",
        ),
        text(
            "В `core.pyi` только сигнатуры: `def func(x: int) -> str: ...`. "
            "При публикации в PyPI указывают `py.typed` в `package_data`."
        ),
        heading("Инкрементальное внедрение типизации"),
        text(
            "Внедрять типизацию в существующий проект лучше постепенно: "
            "сначала критичные модули, потом по одному. Используйте "
            "`# type: ignore` для временного игнорирования, но старайтесь "
            "убирать их. `mypy --install-types` может автоматически установить "
            "стабы для популярных библиотек."
        ),
        heading("Интеграция с IDE и редакторами"),
        text(
            "Современные редакторы (VS Code с Pylance, PyCharm, Neovim с pyright) "
            "используют аннотации типов для автодополнения, перехода к определению "
            "и подсветки ошибок в реальном времени. mypy запускается отдельно, "
            "но IDE часто интегрируют его вывод. Настройте `python.analysis.typeCheckingMode` "
            "в VS Code на `basic` или `strict` для проверки на лету."
        ),
        heading("Typing в стандартной библиотеке"),
        text(
            "Многие модули стандартной библиотеки имеют стаб-файлы. `collections.abc` "
            "содержит абстрактные базовые классы: `Sequence`, `Mapping`, `Set`, "
            "`Iterable`, `Iterator`, `Callable`, `Awaitable`. Используйте их "
            "в аннотациях вместо конкретных типов для большей гибкости."
        ),
        table(
            ["Абстракция", "Конкретные типы", "Когда использовать"],
            [
                ["Sequence", "list, tuple, range", "Только чтение, индексация"],
                ["MutableSequence", "list", "Чтение и запись"],
                ["Mapping", "dict", "Только чтение, ключи"],
                ["MutableMapping", "dict", "Чтение и запись"],
                ["Set", "set, frozenset", "Множество"],
                ["Iterable", "любой итерируемый", "Только for-цикл"],
            ],
        ),
        heading("Продвинутые Protocol"),
        text(
            "Protocol может описывать не только методы, но и атрибуты, свойства "
            "и даже `__init__`. `Protocol` с `__slots__` запрещает лишние "
            "атрибуты. `@runtime_checkable` позволяет проверять соответствие "
            "протоколу в runtime через `isinstance`."
        ),
        example(
            "python",
            """
            from typing import Protocol, runtime_checkable

            @runtime_checkable
            class Named(Protocol):
                name: str
                def greet(self) -> str: ...


            class Person:
                def __init__(self, name: str):
                    self.name = name
                def greet(self) -> str:
                    return f"Hi, {self.name}"


            p = Person("Анна")
            print(isinstance(p, Named))
            print(p.greet())
            """,
        ),
        example("text", "True\nHi, Anna"),
        text(
            "`@runtime_checkable` делает `isinstance(obj, Protocol)` рабочим. "
            "Без него `isinstance` всегда возвращает `False` для Protocol. "
            "Используйте осторожно: runtime-проверка медленнее статической."
        ),
        heading("Когда типизация избыточна"),
        text(
            "Не нужно аннотировать всё подряд. Локальные переменные с "
            "очевидным типом (`x = 5`), приватные хелперы в одном модуле и "
            "одноразовые скрипты могут не иметь аннотаций. Главное — публичный "
            "API: функции, классы и методы, которые вызывают другие. "
            "`mypy --strict` требует аннотаций везде, но в больших проектах "
            "часто используют более мягкую конфигурацию для старого кода."
        ),
        heading("Сравнение mypy, pyright и pyre"),
        text(
            "mypy — наиболее зрелый и популярный анализатор. pyright (Microsoft) "
            "быстрее, лучше работает с Language Server Protocol, используется в "
            "Pylance (VS Code). pyre (Meta) ориентирован на огромные кодовые базы "
            "и инкрементальную проверку. Для большинства проектов mypy или pyright "
            "подойдут. pyright часто быстрее на больших проектах."
        ),
        heading("Советы по производительности mypy"),
        text(
            "mypy может быть медленным на больших проектах. Ускорение: "
            "`--incremental` (кэш), `--num-workers=N` (параллельность), "
            "исключение папок через `exclude` в конфиге, "
            "`--no-site-packages` для изоляции. `dmypy` — daemon-режим, "
            "держит кэш в памяти между запусками."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                [
                    "Смешивание typing и встроенных generics",
                    "List[int] и list[int] — разные типы для mypy.",
                    "Выбрать один стиль: встроенные (3.9+) или typing.",
                ],
                [
                    "Mutable default в аннотации",
                    "`def f(items: list = [])` — та же ловушка.",
                    "Использовать `None` и создавать внутри.",
                ],
                [
                    "Игнорирование union-attr",
                    "Обращение к атрибуту только у одного типа в Union.",
                    "Сужение типа через `isinstance` или `if x is not None`.",
                ],
                [
                    "Несоответствие подписи в переопределении",
                    "Дочерний класс ужесточает или расширяет типы неверно.",
                    "Лисовское подстановка: аргументы — контравariant, возврат — ковариант.",
                ],
                [
                    "Отсутствие аннотаций в публичном API",
                    "mypy не проверяет внутреннюю логику.",
                    "Аннотировать все публичные функции и классы.",
                ],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. После каждого запустите mypy и "
            "исправьте ошибки."
        ),
        numbered(
            "Добавьте аннотации к функции `calculate(a: int, b: int) -> int`, возвращающей сумму. Создайте список `numbers: list[int]` и передайте его в функцию `sum_all(nums: list[int]) -> int`.",
            "Напишите функцию `find_item(items: list[str], target: str) -> Optional[str]`, возвращающую найденную строку или `None`.",
            "Опишите `TypedDict` для конфигурации: `host: str`, `port: int`, `debug: bool`. Напишите функцию, принимающую такой словарь.",
            "Определите `Protocol` с методом `save(self) -> None`. Создайте два класса, реализующих его, и функцию, принимающую `Protocol`.",
            "Создайте файл с намеренной ошибкой типов, запустите `mypy --strict` и исправьте её.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example("text", "Success: no issues found in 1 source file"),
        callout(
            "success",
            "Подсказка",
            "Для второго задания: `def find_item(items: list[str], target: str) -> Optional[str]: ...`. "
            "В Python <3.10 используйте `Optional[str]` из `typing`.",
        ),
        heading("Проверьте себя"),
        numbered(
            "В чём разница между `list[int]` и `List[int]`?",
            "Чем `Optional[str]` отличается от `Optional[str]`?",
            "Зачем нужен `Literal`, если есть `str`?",
            "В чём принципиальная разница между наследованием и Protocol?",
            "Что делает флаг `--strict` в mypy?",
        ),
        heading("Ответы", 3),
        numbered(
            "`list[int]` — встроенный generic (Python 3.9+), `List[int]` — из модуля `typing` (для старых версий). Для mypy это разные типы, не смешивайте.",
            "Ничем — это синонимы. `Optional[X]` — алиас для `Union[X, None]`. В Python 3.10+ предпочтительнее `X | None`.",
            "`Literal[\"a\", \"b\"]` ограничивает значения только указанными. `str` допускает любую строку. mypy проверит, что передаются только разрешённые варианты.",
            "Наследование требует явного `class Child(Parent)`. Protocol проверяет структуру: если у объекта есть нужные методы, он подходит, даже без наследования.",
            "Включает все проверки: необязательные аргументы, возвращаемые значения, `Any`, неиспользуемые импорты и др. Рекомендуется для новых проектов.",
        ),
        heading("Итоги"),
        bullets(
            "Аннотации типов: `x: int`, `def f(a: int) -> str:`. Не влияют на выполнение.",
            "Generics: `list[int]`, `dict[str, float]`, `tuple[int, str]`, `set[str]`.",
            "Union: `Union[int, str]` (или `Union[int, str]`), Optional: `Optional[str]` (или `Optional[str]`).",
            "Literal задаёт конкретные значения. TypedDict описывает структуру словаря.",
            "Protocol — структурная типизация: подходит любой объект с нужными методами.",
            "mypy проверяет типы статически. Запуск: `mypy --strict файл.py`. Настройки в `pyproject.toml`.",
        ),
        heading("Что дальше"),
        text(
            "Статический анализ находит ошибки до запуска. В следующем уроке "
            "разберём тестирование: как писать unit-тесты с pytest, измерять "
            "покрытие и использовать моки для изоляции зависимостей."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Документация mypy: `mypy.readthedocs.io` — полное руководство.",
            "PEP 484: `peps.python.org/pep-0484/` — спецификация type hints.",
            "PEP 544: `peps.python.org/pep-0544/` — Protocol.",
            "TypedDict: `docs.python.org/3/library/typing.html#typing.TypedDict`.",
        ),
    ],
}