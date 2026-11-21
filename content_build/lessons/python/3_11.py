"""Урок 3.11 курса Python: изучение языка и итоговый проект."""

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
    "program_order": 3,
    "topic_order": 11,
    "name": "3.11. Изучение языка и итоговый проект",
    "slug": "python-3-11-изучение-языка-и-итоговый-проект",
    "short_description": (
        "PEP процесс, CPython исходный код, C API (Cython, pybind11), "
        "совместимость версий, создание профессионального проекта-шаблона."
    ),
    "topic_name": "Изучение языка и итоговый проект",
    "topic_description": (
        "Как углубленно изучать Python: чтение PEP, навигация в CPython исходном коде, "
        "написание C-расширений (C API, Cython, pybind11), обеспечение совместимости "
        "версий Python, создание профессионального проекта-шаблона по лучшим практикам."
    ),
    "learning_objectives": [
        "Понимать PEP процесс: Standards Track, Informational, Process; читать ключевые PEP",
        "Навигироваться в CPython исходном коде: структура репозитория, ключевые файлы (ceval.c, typeobject.c)",
        "Собирать debug-билд CPython, отлаживать в gdb с python-gdb.py",
        "Писать C-расширения: ручной C API, Cython (nogil, типизация), pybind11 (C++)",
        "Обеспечивать совместимость версий: sys.version_info, typing_extensions, __future__, CI matrix",
        "Создавать профессиональный проект-шаблон: pyproject.toml, src layout, tests, docs, CI/CD, pre-commit",
        "Публиковать на PyPI: build, twine, GitHub Actions release workflow, SemVer, changelog",
        "Избегать типичных ошибок при глубоком погружении в Python",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "python",
        "pep",
        "cpython",
        "c-api",
        "cython",
        "pybind11",
        "совместимость",
        "проект",
        "профессиональная разработка",
    ],
    "starter_code": code(
        """
        # PEP 563 — отложенная оценка аннотаций
        from __future__ import annotations

        # PEP 572 — walrus operator
        if (n := len(data)) > 100:
            print(f"Large dataset: {n} items")

        # PEP 604 — union types
        def process(data: str | bytes) -> str:
            return data.decode() if isinstance(data, bytes) else data
        """
    ),
    "hints": [
        "PEP читать по порядку: Abstract → Motivation → Specification → Rationale → Backwards Compatibility.",
        "CPython debug build: ./configure --with-pydebug && make -j$(nproc).",
        "Cython: nogil требует только C-типов, никаких Python объектов внутри.",
        "typing_extensions — backport новых typing фич на старые Python версии.",
    ],
    "content": [
        text(
            "Три уровня курса пройдены: от базового синтаксиса через продвинутые паттерны "
            "до архитектуры систем. Но Python — бесконечно глубок. Этот финальный урок — "
            "переход от «пользователя языка» к «понимающему язык изнутри». Мы разберём: "
            "как читать PEP (официальные предложения изменений), как ориентироваться в "
            "миллионе строк C кода CPython, как писать нативные расширения (C API, Cython, "
            "pybind11), как обеспечивать совместимость версий Python 3.10–3.13+, и как "
            "собрать всё в профессиональный проект-шаблон — капитанский проект всего курса."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "читать и понимать PEP: Standards Track, Informational, Process; ключевые PEP для разработчика;",
            "навигироваться в CPython исходном коде: структура репозитория, ключевые файлы (ceval.c, typeobject.c, listobject.c);",
            "собирать debug-билд CPython, отлаживать в gdb с python-gdb.py (py-bt, py-list);",
            "писать C-расширения: ручной C API (PyArg_ParseTuple, PyLong_FromLong), Cython (cdef, nogil, типизация), pybind11 (C++ bindings);",
            "обеспечивать совместимость версий Python: sys.version_info, typing_extensions, __future__.annotations, CI matrix 3.10–3.13;",
            "создавать профессиональный проект-шаблон: pyproject.toml (PEP 621), src layout, tests, docs, CI/CD, pre-commit;",
            "публиковать на PyPI: python -m build, twine, GitHub Actions release workflow, SemVer, Keep a Changelog;",
            "избегать типичных ошибок при глубоком погружении: DeprecationWarning, upper bounds, GIL, lockfile, документация.",
        ),
        heading("PEP — процесс развития Python"),
        heading("Категории PEP", 3),
        table(
            ["Тип", "Примеры", "Назначение"],
            [
                ["Standards Track", "PEP 8, 20, 257, 484, 572, 636", "Изменения языка/стандартной библиотеки, требуют реализации"],
                ["Informational", "PEP 20 (Zen), PEP 257 (docstrings)", "Рекомендации, гайдлайны, best practices, не требуют изменения кода"],
                ["Process", "PEP 1, 12", "Мета-процессы: как создавать/рассматривать PEP, governance"],
            ],
        ),
        text(
            "PEP (Python Enhancement Proposal) — единственный официальный процесс изменения Python. "
            "Каждый PEP проходит стадии: Draft → Accepted → Final (или Rejected/Withdrawn/Deferred). "
            "PEP 1 описывает сам процесс. Читать PEP нужно по порядку: Abstract → Motivation → "
            "Specification → Rationale → Backwards Compatibility → Security Implications → "
            "Reference Implementation. Не читать только Abstract — там 10% полезной информации."
        ),
        heading("Ключевые PEP для разработчика", 3),
        example(
            "python",
            """
            # PEP 8   — Style Guide (база)
            # PEP 20  — Zen of Python: import this
            # PEP 257 — Docstring Conventions
            # PEP 484 — Type Hints (основа typing)
            # PEP 563 — Postponed Evaluation (from __future__ import annotations)
            # PEP 572 — Assignment Expressions (walrus :=)
            # PEP 585 — Type Hinting Generics (list[int] вместо List[int])
            # PEP 586 — Literal Types
            # PEP 591 — Final qualifier
            # PEP 604 — Union Types (X | Y вместо Union[X, Y])
            # PEP 612 — Parameter Specification Variables (ParamSpec)
            # PEP 613 — TypeAlias
            # PEP 626 — Precise line numbers for tracing
            # PEP 634/635/636 — Structural Pattern Matching (match/case)
            # PEP 646 — Variadic Generics (TypeVarTuple)
            # PEP 654 — Exception Groups (except*)
            # PEP 673 — Type Parameter Syntax (type T)
            # PEP 695 — Type Parameter Syntax (class G[T], def f[T]())
            # PEP 701 — Formalization of f-strings
            # PEP 709 — Inlining comprehensions
            """,
        ),
        text(
            "Практическое чтение PEP:\n"
            "- Онлайн: https://peps.python.org/pep-XXXX/ (XXXX — номер с ведущими нулями).\n"
            "- Локально: `python -m pydoc pep XXXX` (если установлен CPython source).\n"
            "- GitHub: https://github.com/python/peps/tree/main/peps (история изменений).\n"
            "- Не читать линейно: ищите Motivation (зачем), Specification (как), "
            "Rationale (почему так), Backwards Compatibility (что сломается)."
        ),
        heading("CPython Source Code — устройство интерпретатора"),
        heading("Структура репозитория", 3),
        example(
            "text",
            """
            cpython/
            ├── Python/           # Основной интерпретатор (ceval.c, compile.c, pymain.c)
            ├── Objects/          # Встроенные типы (listobject.c, dictobject.c, unicodeobject.c, typeobject.c)
            ├── Modules/          # C-модули стандартной библиотеки (_json, _sqlite3, _ssl, _asyncio)
            ├── Parser/           # Парсер (PEG parser в 3.9+, pegen.c)
            ├── Include/          # Публичные C API заголовки (Python.h, object.h, pyerrors.h)
            ├── Internal/         # Внутренние заголовки (internal/pycore_*.h)
            ├── Programs/         # python.exe, pythonw.exe, entry points
            ├── Lib/              # Стандартная библиотека (на Python: os.py, json/__init__.py, etc.)
            ├── Tools/            # Инструменты (freeze, gdb, benchmark, unicode, freeze)
            └── Doc/              # Документация (RST, Sphinx)
            """,
        ),
        heading("Ключевые файлы для изучения", 3),
        table(
            ["Файл", "Что внутри"],
            [
                ["`Python/ceval.c`", "Главный цикл интерпретатора (eval loop), PyEval_EvalFrameDefault — сердце Python"],
                ["`Python/compile.c`", "Компилятор AST → bytecode, symtable, codegen"],
                ["`Objects/typeobject.c`", "Реализация классов, MRO, дескрипторов, __new__/__init__, метаклассов"],
                ["`Objects/listobject.c` / `dictobject.c`", "Реализация list/dict: resize, hash table, compact dict (PEP 393/412)"],
                ["`Objects/unicodeobject.c`", "Строки: compact representation (PEP 393), UTF-8/UTF-16/UTF-32, interning"],
                ["`Include/cpython/*.h`", "Публичный C API: Python.h, object.h, pyerrors.h, pymem.h, pystate.h"],
                ["`Python/pymain.c`", "Точка входа: инициализация, аргументы командной строки, сайт-модули"],
                ["`Parser/pegen.c`", "PEG парсер (Python 3.9+), генерация AST из грамматики"],
            ],
        ),
        text(
            "Как читать CPython код:\n"
            "1. Начинайте с `Python/ceval.c` — `PyEval_EvalFrameDefault` — главный цикл.\n"
            "2. Ищите `PyObject` — базовая структура любого объекта (refcount + type pointer).\n"
            "3. `PyTypeObject` в `typeobject.c` — как работают классы, MRO, дескрипторы.\n"
            "4. `Objects/listobject.c` — list resize strategy (over-allocation), `listappend`.\n"
            "4. `Objects/dictobject.c` — hash table, open addressing, compact dict (Python 3.7+).\n"
            "5. `Objects/unicodeobject.c` — compact strings (PEP 393), 1/2/4 байт на символ."
        ),
        heading("Сборка CPython для отладки", 3),
        example(
            "bash",
            """
            # Клонирование
            git clone https://github.com/python/cpython
            cd cpython

            # Конфигурация с debug-сборкой
            ./configure --with-pydebug --enable-optimizations
            make -j$(nproc)

            # Запуск
            ./python -c "import sys; print(sys.version)"
            # Python 3.13.0a0 (debug build)
            """,
        ),
        text(
            "`--with-pydebug` включает: assert'ы, refcount checking, debug hooks, "
            "`sys.gettotalrefcount()`, `sys.getobjects()`. `--enable-optimizations` — PGO (Profile Guided Optimization), "
            "сборка дольше (10-20 мин), но быстрее. Для разработки CPython используйте `./configure --with-pydebug` без оптимизаций — быстрее пересборка."
        ),
        heading("Отладка C кода в gdb", 3),
        example(
            "bash",
            """
            gdb --args ./python script.py
            (gdb) break PyEval_EvalFrameDefault
            (gdb) run
            (gdb) py-bt          # Python backtrace (нужен python-gdb.py из Tools/gdb/libpython.py)
            (gdb) py-list        # Исходник Python функции
            (gdb) py-print var   # Печать Python переменной
            (gdb) p ((PyObject*)0x...)->ob_refcnt  # Refcount C объекта
            """,
        ),
        text(
            "Python-gdb.py (в `Tools/gdb/libpython.py`) добавляет команды:\n"
            "- `py-bt` / `py-bt-full` — Python backtrace с локальными переменными.\n"
            "- `py-list` — показывает Python исходник текущего фрейма.\n"
            "- `py-print expr` — вычисляет Python выражение в контексте фрейма.\n"
            "- `py-up` / `py-down` — навигация по Python стеку.\n"
            "Копируйте `Tools/gdb/libpython.py` в `~/.gdbinit` или загружайте: `source /path/to/libpython.py`."
        ),
        heading("C API — написание расширений"),
        heading("Минимальное расширение (ручное)", 3),
        example(
            "c",
            """
            // mymodule.c
            #define PY_SSIZE_T_CLEAN
            #include <Python.h>

            static PyObject* my_add(PyObject* self, PyObject* args) {
                long a, b;
                if (!PyArg_ParseTuple(args, "ll", &a, &b)) {
                    return NULL;
                }
                return PyLong_FromLong(a + b);
            }

            static PyMethodDef MyMethods[] = {
                {"add", my_add, METH_VARARGS, "Add two integers."},
                {NULL, NULL, 0, NULL}
            };

            static struct PyModuleDef mymodule = {
                PyModuleDef_HEAD_INIT,
                "mymodule",
                "Example module",
                -1,
                MyMethods
            };

            PyMODINIT_FUNC PyInit_mymodule(void) {
                return PyModule_Create(&mymodule);
            }
            """,
        ),
        example(
            "python",
            """
            # setup.py
            from setuptools import Extension, setup

            module = Extension("mymodule", sources=["mymodule.c"])

            setup(name="mymodule", version="1.0", ext_modules=[module])
            """,
        ),
        example(
            "bash",
            """
            pip install -e .
            python -c "import mymodule; print(mymodule.add(2, 3))"  # 5
            """,
        ),
        text(
            "Ключевые моменты C API:\n"
            "- `PY_SSIZE_T_CLEAN` — обязательно перед `#include <Python.h>` для совместимости 64-бит.\n"
            "- `PyArg_ParseTuple(args, \"ll\", &a, &b)` — парсинг аргументов: `l`=long, `i`=int, `d`=double, `s`=string, `O`=object, `|`=optional.\n"
            "- `PyLong_FromLong` — создаёт Python int из C long. Всегда возвращает new reference.\n"
            "- `PyMethodDef`: имя, функция, флаги (METH_VARARGS, METH_KEYWARGS, METH_O, METH_NOARGS), docstring.\n"
            "- `PyModuleDef`: имя, docstring, size (-1 для global state), methods.\n"
            "- `PyMODINIT_FUNC PyInit_name` — точка входа, имя должно совпадать с модулем.\n"
            "- Refcount: new reference (создали) — владелец, должен `Py_DECREF`. Borrowed reference (получили) — не декрементить."
        ),
        heading("Cython — Python-подобный синтаксис для C-расширений", 3),
        example(
            "cython",
            """
            # fastmath.pyx
            cdef public int fib_cython(int n) nogil:
                cdef int a = 0, b = 1, i
                for i in range(n):
                    a, b = b, a + b
                return a

            def fib(n: int) -> int:
                return fib_cython(n)
            """,
        ),
        example(
            "python",
            """
            # setup.py для Cython
            from setuptools import Extension, setup
            from Cython.Build import cythonize

            ext = Extension("fastmath", sources=["fastmath.pyx"])
            setup(ext_modules=cythonize([ext], language_level=3))
            """,
        ),
        example(
            "bash",
            """
            pip install cython
            pip install -e .
            python -c "import fastmath; print(fastmath.fib(10))"  # 55
            """,
        ),
        text(
            "Cython — компилятор Python-подобного кода в C:\n"
            "- `cdef` — C переменные/функции (невидимы из Python).\n"
            "- `cpdef` — C функция + Python wrapper (видна из Python).\n"
            "- `nogil` — блок/функция без GIL (только C типы, никаких Python объектов).\n"
            "- `cimport` — импорт C-уровня из `.pxd` файлов (без Python накладных расходов).\n"
            "- `memoryview` / `type[:]` — быстрый доступ к буферам (NumPy, bytes).\n"
            "- `cythonize(language_level=3)` — генерация C кода для Python 3.\n"
            "- Аннотации: `cython -a file.pyx` → HTML с жёлтыми линиями (Python API calls)."
        ),
        heading("pybind11 — современный C++ биндинг", 3),
        example(
            "cpp",
            """
            // bind.cpp
            #include <pybind11/pybind11.h>

            int add(int a, int b) { return a + b; }

            namespace py = pybind11;

            PYBIND11_MODULE(mycpp, m) {
                m.def("add", &add, "Add two integers");
            }
            """,
        ),
        example(
            "python",
            """
            # pyproject.toml (с pybind11 + scikit-build-core)
            [build-system]
            requires = ["scikit-build-core", "pybind11"]
            build-backend = "scikit_build_core.build"

            [project]
            name = "mycpp"
            version = "1.0.0"

            [tool.scikit-build]
            cmake.minimum-version = "3.15"
            """,
        ),
        example(
            "cmake",
            """
            # CMakeLists.txt
            cmake_minimum_required(VERSION 3.15)
            project(mycpp LANGUAGES CXX)

            find_package(pybind11 CONFIG REQUIRED)
            pybind11_add_module(mycpp bind.cpp)
            """,
        ),
        text(
            "pybind11 — заголовки-only C++ библиотека для биндингов:\n"
            "- Header-only: `#include <pybind11/pybind11.h>`, никакой линковки.\n"
            "- Автоматические конвертеры: STL контейнеры ↔ Python list/dict, Eigen ↔ NumPy.\n"
            "- Поддерживает: функции, классы, наследование, виртуальные методы, перегрузки, enum, свойства.\n"
            "- Build: `scikit-build-core` + CMake (современный стандарт) или `pybind11[global]` + setuptools.\n"
            "- Преимущества над C API: типобезопасность C++, RAII, исключения ↔ Python exceptions, шаблоны."
        ),
        heading("Совместимость версий Python"),
        heading("Стратегии поддержки", 3),
        example(
            "python",
            """
            # 1. Версионные проверки (в runtime)
            import sys

            if sys.version_info >= (3, 10):
                from typing import TypeAlias
            else:
                from typing_extensions import TypeAlias

            if sys.version_info >= (3, 11):
                # Exception Groups, except*
                try:
                    ...
                except* ValueError as eg:
                    ...
            else:
                try:
                    ...
                except ValueError as e:
                    ...
            """,
        ),
        example(
            "python",
            """
            # 2. typing_extensions — backport новых typing фич
            # pip install typing_extensions
            from typing_extensions import (
                TypeAlias, ParamSpec, TypeVarTuple, Unpack,
                Self, Never, LiteralString, Final, override
            )
            """,
        ),
        example(
            "python",
            """
            # 3. __future__ imports (должны быть первой строкой!)
            from __future__ import annotations  # PEP 563 — отложенная оценка аннотаций
            """,
        ),
        text(
            "Стратегии совместимости:\n"
            "1. `sys.version_info` — runtime проверки для кода, который нельзя выразить через typing.\n"
            "2. `typing_extensions` — backport всех новых typing фич на старые Python (3.7+).\n"
            "3. `from __future__ import annotations` — PEP 563, аннотации хранятся как строки, отложенная оценка. Обязательно первой строкой модуля.\n"
            "4. `sys.version_info >= (3, 10)` — кортежное сравнение работает корректно."
        ),
        heading("Матрица поддержки (пример pyproject.toml)", 3),
        example(
            "toml",
            """
            [project]
            requires-python = ">=3.10"
            classifiers = [
                "Programming Language :: Python :: 3.10",
                "Programming Language :: Python :: 3.11",
                "Programming Language :: Python :: 3.12",
                "Programming Language :: Python :: 3.13",
            ]

            [tool.tox]
            env_list = ["py310", "py311", "py312", "py313"]

            [tool.nox]
            sessions = ["tests-3.10", "tests-3.11", "tests-3.12", "tests-3.13"]
            """,
        ),
        heading("Тестирование на матрице версий", 3),
        example(
            "yaml",
            """
            # .github/workflows/test.yml
            jobs:
              test:
                runs-on: ubuntu-latest
                strategy:
                  matrix:
                    python-version: ["3.10", "3.11", "3.12", "3.13"]
                steps:
                  - uses: actions/setup-python@v5
                    with:
                      python-version: ${{ matrix.python-version }}
                  - run: pip install -e ".[dev]"
                  - run: pytest
            """,
        ),
        text(
            "Matrix testing best practices:\n"
            "- `actions/setup-python@v5` с `cache: 'pip'` — кэш pip пакетов.\n"
            "- `pip install -e \".[dev]\"` — ставит пакет + dev зависимости.\n"
            "- `pytest -n auto --dist=loadscope` — параллельные тесты (xdist).\n"
            "- `codecov/codecov-action` — загрузка coverage.\n"
            "- Для минимальных версий зависимостей: `pip install -e \".[dev]\" --constraint constraints-min.txt`.\n"
            "- `uv` (Astral) — быстрый установщик/ресолвер: `uv pip install -e .`, `uv lock`, `uv run pytest`."
        ),
        heading("Устаревшие модули (stdlib removals)", 3),
        table(
            ["Модуль", "Удалён в", "Замена"],
            [
                ["`distutils`", "3.12", "`setuptools`, `packaging`"],
                ["`imp`", "3.12", "`importlib`"],
                ["`optparse`", "3.12", "`argparse`"],
                ["`cgi`", "3.13", "`urllib.parse`, `html`"],
                ["`cgitb`", "3.13", "`traceback`"],
                ["`msilib`", "3.13", "—"],
                ["`telnetlib`", "3.13", "—"],
                ["`nntplib`", "3.13", "—"],
                ["`ossaudiodev`", "3.13", "—"],
            ],
        ),
        text(
            "Отслеживайте `DeprecationWarning`: `python -W default` или `pytest -W error::DeprecationWarning`. "
            "`python -X dev` — development mode: включает все предупреждения, asyncio debug mode, "
            "encoding warnings, tracemalloc. В CI всегда запускайте с `-W error::DeprecationWarning`."
        ),
        heading("Продвинутый итоговый проект: Архитектура библиотеки"),
        heading("Требования к проекту", 3),
        example(
            "text",
            """
            my_library/
            ├── pyproject.toml          # полная конфигурация (PEP 621)
            ├── README.md               # badges, quickstart, links
            ├── LICENSE                 # MIT/Apache-2.0
            ├── src/
            │   └── my_library/
            │       ├── __init__.py     # публичный API, __version__
            │       ├── core.py         # основная логика
            │       ├── models.py       # Pydantic модели / dataclasses
            │       ├── exceptions.py   # иерархия исключений
            │       ├── utils.py        # хелперы
            │       └── _c_ext/         # опционально: Cython/pybind11 расширения
            ├── tests/
            │   ├── conftest.py         # pytest fixtures
            │   ├── test_core.py
            │   ├── test_models.py
            │   └── test_integration.py
            ├── docs/
            │   ├── conf.py             # Sphinx config
            │   └── *.rst / *.md
            ├── examples/
            │   └── basic_usage.py
            ├── .github/
            │   ├── workflows/
            │   │   ├── ci.yml          # lint, typecheck, test matrix
            │   │   └── release.yml     # build + publish to PyPI
            │   └── dependabot.yml
            ├── .pre-commit-config.yaml
            ├── .ruff.toml / pyproject.toml (tool.ruff)
            ├── .mypy.ini / pyproject.toml (tool.mypy)
            └── CHANGELOG.md            # Keep a Changelog format
            """,
        ),
        heading("Чек-лист качества (Definition of Done)", 3),
        bullets(
            "`ruff check .` — 0 ошибок",
            "`ruff format --check .` — проходит",
            "`mypy src/` — strict mode, 0 ошибок",
            "`pytest --cov=my_library --cov-fail-under=85` — проходит",
            "`pip-audit` — 0 уязвимостей",
            "`bandit -r src/` — 0 высоких рисков",
            "Сборка: `python -m build` → `twine check dist/*`",
            "Документация собирается: `sphinx-build -b html docs docs/_build`",
            "Примеры запускаются: `python examples/basic_usage.py`",
            "Тесты проходят на 3.10–3.13 (matrix CI)",
            "Версия соответствует SemVer, CHANGELOG обновлён (Keep a Changelog)",
        ),
        heading("Публикация и поддержка", 3),
        example(
            "bash",
            """
            # Релиз (через tag push → GitHub Actions release.yml)
            git tag v1.2.0
            git push origin v1.2.0

            # Или вручную
            python -m build
            twine upload dist/*

            # Поддержка: backport фиксов в ветки maint/3.10, maint/3.11
            """,
        ),
        text(
            "Release workflow (GitHub Actions):\n"
            "1. Push tag `v*` → triggers `release.yml`.\n"
            "2. `python -m build` → wheel + sdist.\n"
            "3. `twine check dist/*` → валидация.\n"
            "4. `twine upload dist/*` → PyPI (token из secrets).\n"
            "5. `gh release create` → авто-changelog из коммитов.\n\n"
            "Ветки поддержки: `maint/3.10`, `maint/3.11` для backport критических фиксов. "
            "EOL (End of Life) политику Python: 5 лет (3.10 — EOL 2026-10, 3.11 — 2027-10)."
        ),
        heading("Полезные навыки для глубокого погружения", 3),
        table(
            ["Навык", "Ресурсы"],
            [
                ["Чтение C кода CPython", "`Python/ceval.c`, `Objects/typeobject.c`, Real Python \"CPython Internals\""],
                ["Написание C-расширений", "CPython \"Extending and Embedding\", Cython docs, pybind11 docs"],
                ["Профилирование C уровня", "`perf`, `py-spy --native`, `gdb` + `python-gdb.py`"],
                ["Участие в разработке Python", "devguide.python.org, bpo / GitHub issues, core-mentorship"],
                ["PEP процесс", "peps.python.org, PEP 1 (process)"],
            ],
        ),
        heading("Практика", 2),
        text(
            "Выполните задания по порядку. Для CPython сборки нужен Linux/macOS или WSL2."
        ),
        numbered(
            "PEP: Прочитайте PEP 695 (Type Parameter Syntax) и PEP 701 (f-strings), напишите краткую выжимку: что изменилось, зачем, примеры использования.",
            "CPython: Соберите debug-билд CPython (`./configure --with-pydebug && make -j$(nproc)`), поставьте breakpoint в `PyEval_EvalFrameDefault`, пошагово пройдите выполнение `1 + 1` в gdb (`py-bt`, `py-list`).",
            "C-расширение: напишите Cython-модуль с функцией быстрого вычисления чисел Фибоначчи (`nogil`, `cdef int`), сравните скорость с чистой Python-версией через `timeit`.",
            "Compat: добавьте в проект `typing_extensions`, настройте CI matrix 3.10–3.13. Добавьте `from __future__ import annotations` во все модули.",
            "Проект: создайте шаблон библиотеки по чек-листу выше (можно использовать `cookiecutter` или `copier` с `cookiecutter-pypackage`). Настройте CI, pre-commit, docs, examples.",
        ),
        text("Пример ожидаемого результата для первого задания (PEP 695 summary):"),
        example(
            "text",
            "PEP 695 — Type Parameter Syntax (Python 3.12+)\n"
            "Что: новый синтаксис для Generics: `class G[T]`, `def f[T](x: T) -> T`, `type T = int | str`.\n"
            "Зачем: убрать `TypeVar(\"T\")` boilerplate, улучшить читаемость, IDE support.\n"
            "Пример: `def first[T](seq: Sequence[T]) -> T: return seq[0]` вместо `T = TypeVar('T'); def first(seq: Sequence[T]) -> T`.",
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "CPython debug build: `./configure --with-pydebug --without-pymalloc && make -j$(nproc)`. "
            "В gdb: `break PyEval_EvalFrameDefault`, `run`, `py-bt`, `py-list`, `next`/`step`. "
            "Смотрите `f->f_code->co_name` — имя функции, `f->f_lasti` — bytecode offset."
        ),
        heading("Проверьте себя", 2),
        numbered(
            "Какие три категории PEP и в чём их разница?",
            "Какие 3 ключевых файла CPython для понимания работы интерпретатора?",
            "В чём разница между C API, Cython и pybind11 для написания расширений?",
            "Как обеспечить совместимость кода с Python 3.10–3.13?",
            "Какие файлы обязательны в профессиональном проекте-шаблоне?",
            "Зачем нужен `typing_extensions` и `from __future__ import annotations`?",
            "Какие модули удалены из stdlib в Python 3.12/3.13?",
        ),
        heading("Ответы", 2),
        numbered(
            "Standards Track (изменения языка, требуют реализацию), Informational (рекомендации), Process (мета-процессы).",
            "`Python/ceval.c` (eval loop), `Objects/typeobject.c` (классы/MRO/дескрипторы), `Objects/listobject.c`/`dictobject.c` (встроенные типы).",
            "C API — ручное управление refcount, максимальный контроль, максимальная сложность. Cython — Python-синтаксис, компилируется в C, nogil, типизация. pybind11 — C++, header-only, RAII, авто-конвертеры STL↔Python.",
            "`sys.version_info` checks, `typing_extensions` для backport, `__future__.annotations`, CI matrix 3.10–3.13, `requires-python = \">=3.10\"`.",
            "`pyproject.toml` (PEP 621), `src/` layout, `tests/`, `docs/`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `CHANGELOG.md`, `LICENSE`, `README.md`, `examples/`.",
            "`typing_extensions` — backport новых typing фич (Self, Never, TypeAlias, ParamSpec) на старые Python. `__future__.annotations` (PEP 563) — отложенная оценка аннотаций, строковое хранение, позволяет forward references без строковых кавычек.",
            "3.12: `distutils`, `imp`, `optparse`. 3.13: `cgi`, `cgitb`, `msilib`, `telnetlib`, `nntplib`, `ossaudiodev`. Всегда проверяйте `DeprecationWarning`.",
        ),
        heading("Итоги курса", 2),
        bullets(
            "Python — мощный, читаемый, с огромной экосистемой. База: типы, поток управления, функции, классы.",
            "Продвинутый уровень: декораторы, генераторы, контекстные менеджеры, типизация, асинхронность, метаклассы, дескрипторы.",
            "Профессиональный уровень: архитектура (Clean Architecture, DDD), производительность (Cython, C API, Numba), безопасность (валидация, секреты, десериализация), наблюдаемость (OTel, Prometheus, Loki), CI/CD, пакетирование.",
            "Глубина: PEP процесс, CPython internals, C API / Cython / pybind11, совместимость версий.",
            "Профессионализм: чистый код, тесты (pytest, coverage ≥80%), типизация (mypy strict), линтинг (ruff), форматирование (ruff format), pre-commit, CI/CD matrix, observability, безопасность.",
            "Обучение не заканчивается: читайте PEP, вкладывайтесь в open source, следуйте за What's New in Python, экспериментируйте с новыми инструментами (uv, ruff, polars, typer, pydantic v2).",
        ),
        heading("Поздравляем!", 2),
        text(
            "Вы прошли все 33 урока трёх уровней курса Python. От первого `print(\"Hello\")` до "
            "написания C-расширений и проектирования микросервисной архитектуры. "
            "Теперь у вас есть полный набор навыков для профессиональной Python-разработки. "
            "Продолжайте учиться, экспериментировать и создавать крутые проекты. Удачи!"
        ),
        heading("Что дальше", 2),
        text(
            "Курс завершён: три уровня, 33 урока — от первого print до C-расширений и "
            "архитектуры систем. Дальше — практика на собственных проектах: "
            "возьмите задачу из своей работы, доведите её от прототипа до продакшена "
            "с тестами, типизацией, CI и мониторингом. Именно так навыки из уроков "
            "становятся профессиональным опытом."
        ),
        heading("Если хотите углубиться", 2),
        bullets(
            "CPython Developer's Guide — devguide.python.org/",
            "CPython Source Tour — github.com/python/cpython (README.rst)",
            "Extending Python with C — docs.python.org/3/extending/",
            "Cython Documentation — cython.readthedocs.io/",
            "pybind11 Documentation — pybind11.readthedocs.io/",
            "PEP Index — peps.python.org/",
            "What's New In Python 3.X — docs.python.org/3/whatsnew/",
            "Cookiecutter templates — github.com/cookiecutter/cookiecutter-pypackage",
            "Real Python: CPython Internals — realpython.com/cpython-source-code-guide/",
            "Python Insider Blog — pythoninsider.blogspot.com/ (официальные новости релиза)",
        ),
    ],
}