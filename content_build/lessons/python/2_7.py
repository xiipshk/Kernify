"""Урок 2.7 курса Python: тестирование."""

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
    "topic_order": 7,
    "name": "2.7. Тестирование",
    "slug": "python-2-7-тестирование",
    "short_description": (
        "Написание тестов с pytest, фикстуры, параметризация, mock-объекты, "
        "покрытие кода и основы TDD."
    ),
    "topic_name": "Тестирование",
    "topic_description": (
        "Как писать автоматические тесты, изолировать зависимости через моки, "
        "измерять покрытие и применять разработку через тестирование."
    ),
    "learning_objectives": [
        "Писать тесты с pytest: assert, фикстуры, параметризация",
        "Использовать unittest.mock для изоляции: patch, MagicMock",
        "Измерять покрытие кода через coverage.py",
        "Применять TDD: красный-зелёный-рефакторинг",
        "Организовывать тесты в структуре проекта",
    ],
    "estimated_minutes": 40,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "python",
        "тестирование",
        "pytest",
        "mock",
        "coverage",
        "tdd",
    ],
    "starter_code": code(
        """
        def add(a, b):
            return a + b

        def test_add():
            assert add(2, 3) == 5
            assert add(-1, 1) == 0
        """
    ),
    "hints": [
        "Имена тестовых функций начинаются с test_, файлы — с test_.",
        "Фикстуры с yield делают cleanup после теста автоматически.",
        "patch работает как контекстный менеджер или декоратор.",
    ],
    "content": [
        text(
            "Код без тестов — это код, в котором неизвестно, работает ли он. "
            "Ручное проверка не масштабируется: после каждого изменения нужно "
            "перепроверять всё вручную. Автоматические тесты запускаются за "
            "секунды и гарантируют, что старый функционал не сломался.\n\n"
            "В этом уроке разберём pytest — де-факто стандарт тестирования в "
            "Python. Научимся писать тесты, использовать фикстуры для "
            "подготовки данных, изолировать внешние зависимости через моки, "
            "измерять покрытие кода и познакомимся с TDD — разработкой через "
            "тестирование."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "писать тесты с pytest: простые assert, фикстуры, параметризацию;",
            "использовать unittest.mock: patch, MagicMock, side_effect;",
            "запускать тесты с фильтрами, маркерами и параллельно;",
            "измерять покрытие кода через coverage.py и читать отчёты;",
            "понимать цикл TDD: красный → зелёный → рефакторинг;",
            "организовывать тесты в структуре проекта.",
        ),
        heading("pytest — базовый запуск"),
        text(
            "Установка: `pip install pytest`. Тесты — функции с префиксом "
            "`test_` в файлах `test_*.py`. Запуск: `pytest` находит и "
            "выполняет все тесты рекурсивно."
        ),
        example(
            "python",
            """
            # test_calc.py
            def add(a, b):
                return a + b

            def test_add_positive():
                assert add(2, 3) == 5

            def test_add_negative():
                assert add(-1, 1) == 0
            """,
        ),
        example("text", "============================= test session starts =============================\ncollected 2 items\n\ntest_calc.py::test_add_positive PASSED\n============================== 2 passed in 0.01s =============================="),
        text(
            "pytest показывает понятный diff при неравенстве списков, словарей и "
            "строк. Флаги: `-v` (verbose), `-k \"pattern\"` (фильтр по имени), "
            "`--tb=short` (короткий трейсбек), `-x` (остановиться на первой ошибке)."
        ),
        heading("Фикстуры — подготовка и очистка"),
        text(
            "**Фикстура** — функция, помеченная `@pytest.fixture`, которая "
            "подготавливает данные для теста. Тест получает фикстуру как "
            "аргумент по имени. Фикстура с `yield` выполняет код после yield "
            "как cleanup после завершения теста."
        ),
        example(
            "python",
            """
            import pytest

            @pytest.fixture
            def sample_users():
                return ["Анна", "Борис", "Виктор"]

            def test_count(sample_users):
                assert len(sample_users) == 3
            """,
        ),
        example(
            "python",
            """
            import pytest
            from pathlib import Path

            @pytest.fixture
            def temp_file(tmp_path):
                f = tmp_path / "data.txt"
                f.write_text("hello")
                yield f
                if f.exists():
                    f.unlink()

            def test_read(temp_file):
                assert temp_file.read_text() == "hello"
            """,
        ),
        text(
            "Встроенная фикстура `tmp_path` создаёт временную директорию, "
            "которая удаляется после теста. `yield` разделяет setup (до) и "
            "teardown (после). Фикстуры могут зависеть от других фикстур."
        ),
        heading("Параметризация — много тестов из одного"),
        text(
            "`@pytest.mark.parametrize` запускает одну тестовую функцию с "
            "разными наборами аргументов. Это устраняет дублирование кода."
        ),
        example(
            "python",
            """
            import pytest

            @pytest.mark.parametrize("a,b,expected", [
                (2, 3, 5),
                (0, 0, 0),
                (-1, 1, 0),
                (10, 20, 30),
            ])
            def test_add(a, b, expected):
                assert a + b == expected
            """,
        ),
        example("text", "============================= test session starts =============================\ncollected 4 items\n\ntest_calc.py::test_add[2-3-5] PASSED\n... 4 passed"),
        text(
            "Каждый набор — отдельный тест в отчёте. Имена параметров в "
            "декораторе должны совпадать с аргументами функции. Можно "
            "параметризовать несколько декораторами для комбинаций."
        ),
        heading("Моки — изоляция зависимостей"),
        text(
            "**Мок** (mock) — подставной объект, который имитирует поведение "
            "реального объекта. `unittest.mock.patch` временно заменяет объект "
            "в указанном модуле на мок. Это позволяет тестировать код в "
            "изоляции от базы данных, сети, файловой системы."
        ),
        example(
            "python",
            """
            from unittest.mock import patch, MagicMock

            def fetch_user(api, user_id):
                return api.get(f"/users/{user_id}")

            @patch("test_module.api")
            def test_fetch_user(mock_api):
                mock_api.get.return_value = {"id": 1, "name": "Анна"}
                result = fetch_user(mock_api, 1)
                assert result["name"] == "Анна"
                mock_api.get.assert_called_once_with("/users/1")
            """,
        ),
        text(
            "`patch` работает как декоратор или контекстный менеджер. "
            "`mock_api.get.return_value` задаёт возвращаемое значение. "
            "`assert_called_once_with` проверяет, что метод вызван с правильными "
            "аргументами. `side_effect` позволяет задать исключение или "
            "последовательность значений."
        ),
        example(
            "python",
            """
            from unittest.mock import patch

            def risky_call(service):
                return service.call()

            @patch("test_module.Service")
            def test_error_handling(MockService):
                instance = MockService.return_value
                instance.call.side_effect = ConnectionError("нет связи")
                try:
                    risky_call(instance)
                except ConnectionError:
                    pass
                else:
                    assert False, "ожидалось исключение"
            """,
        ),
        heading("Покрытие кода — coverage"),
        text(
            "**Покрытие** (coverage) — процент строк кода, выполненных при "
            "запуске тестов. `coverage.py` измеряет покрытие и генерирует "
            "отчёты. 100% покрытие не гарантирует отсутствие багов, но низкое "
            "покрытие точно указывает на нетестированные участки."
        ),
        example(
            "bash",
            """
            pip install coverage
            coverage run -m pytest
            coverage report
            coverage html  # подробный отчёт в htmlcov/
            """,
        ),
        example(
            "text",
            """Name         Stmts   Miss  Cover
------------------------------------------
calc.py         10      0   100%
main.py         25      5    80%
------------------------------------------
TOTAL           35      5    85%""",
        ),
        text(
            "Цель — не 100% любой ценой, а покрытие критичных путей. "
            "Исключайте из отчёта тесты и миграции через "
            "`--omit=test_*,migrations/*`. В CI порог часто ставят на 80-90%."
        ),
        heading("TDD — разработка через тестирование"),
        text(
            "**TDD (Test-Driven Development)** — цикл: 1) напишите падающий "
            "тест (красный), 2) напишите минимальный код, чтобы он прошёл "
            "(зелёный), 3) рефакторинг без изменения поведения. Повторяйте "
            "для каждого требования."
        ),
        example(
            "python",
            """
            # 1. Красный: тест для несуществующей функции
            def test_factorial():
                assert factorial(5) == 120

            # 2. Зелёный: минимальная реализация
            def factorial(n):
                if n == 0:
                    return 1
                return n * factorial(n - 1)

            # 3. Рефакторинг: добавить проверки, документацию
            """,
        ),
        text(
            "TDD заставляет думать об интерфейсе до реализации, приводит к "
            "модульному коду и полному покрытию. Не догма: иногда проще "
            "написать код, потом тесты. Главное — тесты есть до релиза."
        ),
        heading("Организация тестов в проекте"),
        text(
            "Стандартная структура: `tests/` рядом с исходным кодом. "
            "Внутри — зеркальная структура пакетов. `conftest.py` — общие "
            "фикстуры и хуки для всей папки. `pytest.ini` или `pyproject.toml` "
            "— настройки pytest."
        ),
        example(
            "text",
            """project/
├── src/
│   └── mypkg/
│       ├── __init__.py
│       └── calc.py
├── tests/
│   ├── conftest.py
│   └── test_calc.py
├── pytest.ini
└── pyproject.toml""",
        ),
        heading("Маркеры и пропуск тестов"),
        text(
            "`@pytest.mark` позволяет помечать тесты и фильтровать их. "
            "Встроенные: `skip` (пропуск), `skipif` (условный пропуск), "
            "`xfail` (ожидаемое падение), `parametrize`. Пользовательские "
            "маркеры регистрируются в `pytest.ini`."
        ),
        example(
            "python",
            """
            import pytest

            @pytest.mark.skip(reason="не реализовано")
            def test_future():
                assert False

            @pytest.mark.skipif(False, reason="демо: пропуск")
            def test_new_feature():
                assert True

            @pytest.mark.xfail(reason="известный баг")
            def test_buggy():
                assert 1 == 2
            """,
        ),
        text(
            "Запуск с фильтром: `pytest -m 'not slow'` — пропустить тесты с "
            "маркером `slow`. `pytest --runxfail` запускает xfail-тесты и "
            "считает их провалом, если они неожиданно проходят."
        ),
        heading("unittest — встроенный фреймворк"),
        text(
            "`unittest` — стандартная библиотека в стиле xUnit. Классы-тесты "
            "наследуются от `TestCase`, методы — `test_*`. `setUp`/`tearDown` "
            "аналогичны фикстурам. pytest может запускать unittest-тесты, "
            "но наоборот — нет. Для новых проектов pytest предпочтительнее."
        ),
        example(
            "python",
            """
            import unittest

            class TestMath(unittest.TestCase):
                def setUp(self):
                    self.value = 10

                def test_add(self):
                    self.assertEqual(self.value + 5, 15)

                def tearDown(self):
                    self.value = 0


            if __name__ == "__main__":
                unittest.main()
            """,
        ),
        heading("Параллельный запуск"),
        text(
            "`pytest-xdist` позволяет запускать тесты параллельно на нескольких "
            "процессах: `pytest -n auto`. Ускоряет большой набор тестов, "
            "но требует изоляции: нет общего состояния, файлы через tmp_path, "
            "база данных — отдельная на процесс."
        ),
        example(
            "bash",
            """
            pip install pytest-xdist
            pytest -n 4
            """,
        ),
        heading("Тестирование асинхронного кода"),
        text(
            "`pytest-asyncio` позволяет тестировать `async def` функции. "
            "Декоратор `@pytest.mark.asyncio` делает тест асинхронным, "
            "внутри можно использовать `await`. Фикстуры тоже могут быть "
            "асинхронными с `@pytest.fixture` и `async def`."
        ),
        example(
            "python",
            """
            import pytest

            @pytest.mark.asyncio
            async def test_async():
                await asyncio.sleep(0.01)
                assert True


            @pytest.fixture
            async def async_resource():
                yield "resource"
            """,
        ),
        text(
            "`asyncio.run` не нужен — pytest-asyncio управляет event loop. "
            "Фикстуры с `async def` и `yield` работают как асинхронные "
            "контекстные менеджеры."
        ),
        heading("Property-based testing — Hypothesis"),
        text(
            "`Hypothesis` генерирует случайные входные данные для тестов и "
            "ищет контрпримеры. `@given` задаёт стратегию генерации данных. "
            "Находит граничные случаи, которые программист упускает."
        ),
        example(
            "python",
            """
            from hypothesis import given, strategies as st

            # skip: требует hypothesis
            @pytest.mark.skip(reason="требует hypothesis")
            @given(st.lists(st.integers()))
            def test_reverse_twice(lst):
                assert lst[::-1][::-1] == lst
            """,
        ),
        text(
            "Hypothesis сам найдёт пустой список, список с одним элементом, "
            "дубликаты, большие числа — всё, что может сломать логику. "
            "Минимизирует контрпример до минимального."
        ),
        heading("Сравнение pytest и unittest"),
        text(
            "pytest: проще синтаксис, мощные фикстуры, параметризация, плагины, "
            "лучшие сообщения об ошибках. unittest: встроен, классы, "
            "setUp/tearDown, assert-методы. pytest может запускать unittest, "
            "но не наоборот. Для новых проектов — pytest."
        ),
        table(
            ["Характеристика", "pytest", "unittest"],
            [
                ["Синтаксис", "функции", "классы"],
                ["Фикстуры", "декораторы, yield", "setUp/tearDown"],
                ["Параметризация", "@pytest.mark.parametrize", "subTest / библиотеки"],
                ["Моки", "unittest.mock + pytest", "unittest.mock"],
                ["Плагины", "много (xdist, asyncio, hypothesis)", "мало"],
            ],
        ),
        heading("CI/CD интеграция"),
        text(
            "В CI (GitHub Actions, GitLab CI, Jenkins) тесты запускают на каждом "
            "пуше. Типичный шаблон: `pytest --tb=short --junitxml=report.xml` "
            "для XML-отчёта, `coverage xml` для Cobertura-отчёта покрытия. "
            "Порог покрытия: `coverage fail --min=80`. Кэширование зависимостей "
            "ускоряет CI."
        ),
        example(
            "yaml",
            """
            # .github/workflows/test.yml
            jobs:
              test:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: actions/setup-python@v5
                    with: {python-version: '3.11'}
                  - run: pip install pytest coverage
                  - run: coverage run -m pytest
                  - run: coverage xml
                  - run: coverage fail --min=80
            """,
        ),
        heading("Отладка падающих тестов"),
        text(
            "`pytest --pdb` запускает отладчик при первой ошибке. "
            "`pytest -x --pdb` останавливается на первой ошибке и открывает pdb. "
            "`pytest --lf` запускает только упавшие тесты прошлого запуска. "
            "`pytest --ff` запускает упавшие тесты первыми. Это ускоряет цикл "
            "исправления."
        ),
        heading("Когда не писать тесты"),
        text(
            "Не тестируйте: стандартную библиотеку, фреймворки, генерируемый код, "
            "тривиальные геттеры/сеттеры, UI-детали (часто меняются). Тестируйте: "
            "бизнес-логику, граничные случаи, интеграции, регрессии. "
            "Правило: если код может сломаться и это будет больно — тестируйте."
        ),
        heading("Тестирование CLI и веб-приложений"),
        text(
            "`click.testing.CliRunner` для Click-приложений, `TestClient` "
            "FastAPI/Starlette, `Flask.test_client()` — позволяют вызывать "
            "приложение в памяти без сетевого слоя. Это быстрее и надёжнее "
            "реальных HTTP-запросов."
        ),
        example(
            "python",
            """
            # skip: требует fastapi и main
            @pytest.mark.skip(reason="требует fastapi и main")
            from fastapi.testclient import TestClient
            from main import app

            client = TestClient(app)

            def test_root():
                response = client.get("/")
                assert response.status_code == 200
                assert response.json() == {"msg": "Hello"}
            """,
        ),
        heading("Тестирование базы данных"),
        text(
            "Для тестов с БД используют: in-memory SQLite (быстро, но другой "
            "диалект), Testcontainers (реальные контейнеры Postgres/MySQL), "
            "фикстуры с транзакциями и откатом (rollback). `pytest-postgresql` "
            "`pytest-mock` упрощают настройку."
        ),
        heading("Метрики качества тестов"),
        text(
            "Mutation testing (`mutmut`, `cosmic-ray`) меняет код и проверяет, "
            "упадёт ли тест. Если тест не падает — он слабый. Cyclomatic "
            "complexity (`radon cc`) показывает сложность функций: выше 10 — "
            "нужен рефакторинг. Тесты должны быть быстрыми (<100 мс на unit-тест), "
            "изолированными и детерминированными."
        ),
        heading("Сравнение pytest и unittest"),
        text(
            "pytest: проще синтаксис, мощные фикстуры, параметризация, плагины, "
            "лучшие сообщения об ошибках. unittest: встроен, классы, "
            "setUp/tearDown, assert-методы. pytest может запускать unittest, "
            "но не наоборот. Для новых проектов — pytest."
        ),
        table(
            ["Характеристика", "pytest", "unittest"],
            [
                ["Синтаксис", "функции", "классы"],
                ["Фикстуры", "декораторы, yield", "setUp/tearDown"],
                ["Параметризация", "@pytest.mark.parametrize", "subTest / библиотеки"],
                ["Моки", "unittest.mock + pytest", "unittest.mock"],
                ["Плагины", "много (xdist, asyncio, hypothesis)", "мало"],
            ],
        ),
        heading("Тестирование производительности"),
        text(
            "`pytest-benchmark` измеряет время выполнения кода и сравнивает "
            "результаты между запусками. `@pytest.mark.benchmark` помечает "
            "тест как бенчмарк. Результаты сохраняются в JSON для отслеживания "
            "регрессий производительности в CI."
        ),
        example(
            "python",
            """
            import pytest

            def test_sort_benchmark(benchmark):
                data = list(range(1000))
                random.shuffle(data)
                result = benchmark(sorted, data)
                assert len(result) == 1000
            """,
        ),
        heading("Советы по поддержке тестов"),
        text(
            "Тесты — это тоже код, который нужно читать и рефакторить. "
            "Правила: тест проверяет одно дело, имя описывает ожидаемое "
            "поведение (`test_returns_none_when_not_found`), нет магических "
            "чисел (выносить в константы), фикстуры изолированы, нет "
            "зависимости от порядка. Удаляйте тесты, которые не падают годами — "
            "они не несут ценности."
        ),
        heading("Когда тесты становятся бременем"),
        text(
            "Если набор тестов запускается минуты — разработчики перестают "
            "запускать его локально. Разделяйте: быстрые unit-тесты (<100 мс) "
            "запускаются на каждом коммите, медленные интеграционные — в CI "
            "ночью. `pytest -m 'not slow'` для быстрой проверки. "
            "Удаляйте или рефакторьте тесты, которые постоянно флакают "
            "(падают случайно). Флаки убивают доверие к тестам."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                [
                    "Тест зависит от порядка выполнения",
                    "Падает при запуске отдельно.",
                    "Фикстуры с cleanup, никакого общего состояния.",
                ],
                [
                    "patch не работает",
                    "Мокается не тот объект или не в том модуле.",
                    "Patch там, ГДЕ объект ИСПОЛЬЗУЕТСЯ, а не где определен.",
                ],
                [
                    "Тест слишком большой",
                    "Проверяет много вещей сразу.",
                    "Один тест — одна проверка. Разбивать на мелкие.",
                ],
                [
                    "Мок возвращает другой мок",
                    "Сложно отлаживать.",
                    "Настраивать return_value/side_effect конкретных методов.",
                ],
                [
                    "Покрытие 100%, баги есть",
                    "Покрытие строк != покрытие веток и логики.",
                    "Смотреть branch coverage, писать тесты на граничные случаи.",
                ],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Запустите pytest после каждого."
        ),
        numbered(
            "Напишите функцию `is_palindrome(s: str) -> bool` и тесты для неё: пустая строка, одиночный символ, палиндром, не-палиндром, регистр.",
            "Создайте фикстуру `db_connection`, которая возвращает мок-объект с методами `connect()`, `query(sql)`, `close()`. Напишите тест, проверяющий, что `close()` вызывается после ошибки.",
            "Параметризуйте тест для функции `clamp(value, min_val, max_val)` с наборами: (5, 0, 10)=5, (15, 0, 10)=10, (-5, 0, 10)=0.",
            "Напишите тест с `patch` для функции, вызывающей `requests.get(url)`. Проверьте, что при исключении `Timeout` функция возвращает `None`.",
            "Запустите `coverage run -m pytest` и `coverage report`. Добавьте тест для не покрытой ветки.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example("text", "============================= test session starts =============================\ncollected 5 items\n\ntest_palindrome.py::test_empty PASSED\n... 5 passed"),
        callout(
            "success",
            "Подсказка",
            "Для третьего задания: `@pytest.mark.parametrize(\"value,min_val,max_val,expected\", [(5,0,10,5), (15,0,10,10), (-5,0,10,0)])`."
        ),
        heading("Проверьте себя"),
        numbered(
            "Какое имя должен иметь тестовый файл, чтобы pytest его нашёл?",
            "Чем `yield` в фикстуре отличается от `return`?",
            "Для чего нужен `side_effect` в моке?",
            "Что показывает `coverage report`, чего не показывает?",
            "В каком порядке шаги в TDD?",
        ),
        heading("Ответы", 3),
        numbered(
            "Файл `test_*.py` или `*_test.py`, функция `test_*`.",
            "`return` завершает фикстуру, `yield` — возвращает значение тесту, а код после yield выполняется как cleanup после теста.",
            "`side_effect` задаёт исключение, итератор значений или функцию, которая вызывается при каждом вызове мока.",
            "Показывает % выполненных строк. Не показывает: покрытие веток (if/else), качество тестов, логические ошибки.",
            "Красный (тест падает) → Зелёный (тест проходит) → Рефакторинг (улучшение кода без изменения тестов).",
        ),
        heading("Итоги"),
        bullets(
            "pytest — стандарт тестирования: простые assert, автообнаружение, фикстуры.",
            "Фикстуры с `yield` делают setup/teardown. Параметризация — `@pytest.mark.parametrize`.",
            "`unittest.mock.patch` заменяет зависимости на моки. `MagicMock` — гибкий мок.",
            "`coverage run -m pytest` + `coverage report` — измерение покрытия.",
            "TDD: красный → зелёный → рефакторинг. Тесты пишутся до кода.",
            "Структура: `tests/`, `conftest.py`, `pytest.ini`.",
        ),
        heading("Что дальше"),
        text(
            "Тесты позволяют уверенно менять код. Следующая тема — асинхронность: "
            "как писать неблокирующий код с `async/await`, работать с "
            "Event Loop и запускать задачи параллельно."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Официальная документация pytest: `docs.pytest.org` — полное руководство.",
            "unittest.mock: `docs.python.org/3/library/unittest.mock.html` — моки и patch.",
            "Coverage.py: `coverage.readthedocs.io` — измерение покрытия.",
            "TDD: `testdriven.io` — практические примеры разработки через тестирование.",
        ),
    ],
}