"""Урок 3.8 курса Python: профессиональные инструменты."""

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
    "topic_order": 8,
    "name": "3.8. Профессиональные инструменты",
    "slug": "python-3-8-профессиональные-инструменты",
    "short_description": (
        "Современная упаковка (pyproject.toml), линтеры (ruff), форматтеры (black), "
        "статические анализаторы (mypy), pre-commit, CI/CD (GitHub Actions), "
        "полезные утилиты экосистемы."
    ),
    "topic_name": "Профессиональные инструменты",
    "topic_description": (
        "Как превратить код в профессиональный пакет: pyproject.toml (PEP 621), "
        "сборка и публикация на PyPI, линтинг (ruff), форматирование (black/ruff format), "
        "статическая типизация (mypy strict), pre-commit хуки, CI/CD в GitHub Actions, "
        "полезные утилиты (pip-tools, pip-audit, bandit, pytest-xdist, hypothesis)."
    ),
    "learning_objectives": [
        "Создавать pyproject.toml по PEP 621: метаданные, зависимости, optional-deps, entry points",
        "Собирать пакет (python -m build) и публиковать на PyPI через twine",
        "Настраивать ruff (линтинг + форматирование) и black",
        "Конфигурировать mypy в strict режиме, работать с stubs для сторонних библиотек",
        "Настраивать pre-commit хуки: ruff, mypy, базовые проверки",
        "Писать CI/CD пайплайн в GitHub Actions: matrix testing, lint, typecheck, test, build, publish",
        "Использовать полезные утилиты: pip-tools, pip-audit, bandit, pytest-xdist, hypothesis",
        "Следовать чек-листу готового проекта",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "python",
        "packaging",
        "pyproject.toml",
        "ruff",
        "black",
        "mypy",
        "pre-commit",
        "github actions",
        "ci/cd",
    ],
    "starter_code": code(
        """
        # pyproject.toml — современный стандарт упаковки (PEP 621)
        [build-system]
        requires = ["setuptools>=68", "wheel"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "my_package"
        version = "1.0.0"
        description = "Краткое описание"
        readme = "README.md"
        requires-python = ">=3.10"
        dependencies = ["requests>=2.31"]
        """
    ),
    "hints": [
        "Всегда используйте src/ layout — изолирует пакет от корня проекта.",
        "ruff заменяет flake8, isort, pyupgrade, black — быстрее и единый конфиг.",
        "mypy strict=true с первого дня ловит баги типов рано.",
        "pre-commit ловит проблемы до коммита, CI — страховка на сервере.",
    ],
    "content": [
        text(
            "Профессиональный Python-проект — это не только рабочий код. Это упаковка, "
            "линтинг, типизация, тесты, CI/CD, документация, безопасность зависимостей, "
            "версионирование, changelog, лицензии, код-ревью процесс. Многие разработчики "
            "пропускают эти шаги, и плата приходит позже: сломанные деплои, конфликты "
            "зависимостей, баги типов в продакшене, уязвимости в зависимостях, "
            "невоспроизводимые билды, потеря времени на рутину.\n\n"
            "Современный стандарт — pyproject.toml (PEP 621): один файл для метаданных, "
            "зависимостей, конфигурации инструментов. Ruff (на Rust) заменяет flake8, isort, "
            "pyupgrade, black — делает всё быстрее. Mypy в strict режиме ловит баги типов "
            "на этапе разработки. Pre-commit ловит проблемы до коммита. GitHub Actions "
            "автоматизирует проверку на каждом PR. В этом уроке соберём полный профессиональный стек.\n\n"
            "Правило: настройте инструменты СРАЗУ при создании проекта. Рефакторинг конфигов "
            "позже стоит в 10x дороже. Шаблон проекта (cookiecutter / copier) экономит часы."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "создавать pyproject.toml по PEP 621: метаданные, зависимости, optional-deps, entry points;",
            "собирать пакет (python -m build) и публиковать на PyPI через twine;",
            "настраивать ruff (линтинг + форматирование) и black;",
            "конфигурировать mypy в strict режиме, работать с stubs для сторонних библиотек;",
            "настраивать pre-commit хуки: ruff, mypy, базовые проверки;",
            "писать CI/CD пайплайн в GitHub Actions: matrix testing, lint, typecheck, test, build, publish;",
            "использовать полезные утилиты: pip-tools, pip-audit, bandit, pytest-xdist, hypothesis;",
            "следовать чек-листу готового профессионального проекта.",
        ),
        heading("Современная упаковка: pyproject.toml (PEP 621)"),
        text(
            "pyproject.toml — единый файл конфигурации проекта (PEP 621). "
            "Заменяет setup.py, setup.cfg, requirements.txt, .flake8, mypy.ini, pytest.ini. "
            "Все инструменты читают конфиг отсюда.\n\n"
            "PEP 621 стандартизировал метаданные проекта: name, version, description, readme, "
            "authors, license, requires-python, classifiers, dependencies, optional-dependencies, "
            "scripts (entry points), urls. Раньше каждый инструмент имел свой формат конфига, "
            "теперь единый источник правды. Build backends (setuptools, flit, poetry, hatch) "
            "читают `[build-system]` и строят пакет по PEP 517. PEP 621 — фундамент современной "
            "упаковки, поддерживаемый всеми современными бэкендами (setuptools, flit, poetry, hatch, pdm)."
        ),
        example(
            "toml",
            """
            # pyproject.toml — единый файл конфигурации проекта
            [build-system]
            requires = ["setuptools>=68", "wheel"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "my_package"
            version = "1.0.0"
            description = "Краткое описание"
            readme = "README.md"
            authors = [{name = "Имя", email = "you@example.com"}]
            license = {text = "MIT"}
            requires-python = ">=3.10"
            classifiers = [
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
            ]
            dependencies = [
                "requests>=2.31",
                "click>=8.1",
            ]

            [project.optional-dependencies]
            dev = [
                "pytest>=7.0",
                "pytest-cov>=4.0",
                "black>=23.0",
                "ruff>=0.1",
                "mypy>=1.0",
                "pre-commit>=3.0",
            ]
            docs = ["sphinx>=7.0", "furo>=2023"]

            [project.scripts]
            mycli = "my_package.cli:main"

            [tool.setuptools.packages.find]
            where = ["src"]
            include = ["my_package*"]

            [tool.black]
            line-length = 100
            target-version = ["py310"]

            [tool.ruff]
            line-length = 100
            target-version = "py310"
            select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM", "T20"]
            ignore = ["E501"]

            [tool.ruff.format]
            quote-style = "double"
            indent-style = "space"

            [tool.mypy]
            python_version = "3.10"
            warn_return_any = true
            warn_unused_configs = true
            disallow_untyped_defs = true
            strict = true

            [tool.pytest.ini_options]
            testpaths = ["tests"]
            addopts = "-v --cov=my_package --cov-report=term-missing"

            [tool.coverage.run]
            source = ["src/my_package"]
            """,
        ),
        text(
            "Ключевые секции:\n"
            "- `[build-system]` — как собирать (setuptools, wheel).\n"
            "- `[project]` — метаданные (PEP 621): name, version, description, readme, authors, license, "
            "requires-python, classifiers, dependencies, optional-dependencies, scripts.\n"
            "- `[project.optional-dependencies]` — extra groups: dev, docs, test, prod.\n"
            "- `[project.scripts]` — entry points (console_scripts, gui_scripts).\n"
            "- `[tool.setuptools.packages.find]` — где искать пакеты (src layout).\n"
            "- `[tool.*]` — конфиги инструментов: black, ruff, mypy, pytest, coverage."
        ),
        heading("src layout", 3),
        example(
            "text",
            """
            my_project/
            ├── pyproject.toml
            ├── README.md
            ├── LICENSE
            ├── src/
            │   └── my_package/
            │       ├── __init__.py
            │       ├── cli.py
            │       └── core.py
            ├── tests/
            │   ├── __init__.py
            │   ├── test_cli.py
            │   └── test_core.py
            └── .github/
                └── workflows/
                    └── ci.yml
            """,
        ),
        text(
            "src layout — лучшая практика:\n"
            "- Код пакета в `src/my_package/` — изолирован от корня проекта.\n"
            "- `pip install -e .` ставит пакет из src, тесты импортируют установленную версию.\n"
            "- Избегает `import my_package` из корня (где лежит pyproject.toml), что вызывает путаницу.\n"
            "- Tox, pytest, mypy, coverage — всё работает корректно с src layout.\n\n"
            "Почему не flat layout (код в корне): при `import my_package` Python находит пакет "
            "в текущей директории (корне проекта), а не установленный через pip. Тесты проходят, "
            "но установленный пакет может быть сломан (отсутствуют файлы, неверные импорты). "
            "src layout заставляет тесты использовать установленный пакет — тестируется то, что получит пользователь. "
            "Для namespace packages: `src/my_namespace/subpackage/` с `namespace_packages` в setuptools."
        ),
        heading("Сборка и публикация", 3),
        example(
            "bash",
            """
            # Установка инструментов
            pip install build twine

            # Сборка (создаёт dist/*.whl и dist/*.tar.gz)
            python -m build

            # Проверка артефактов
            twine check dist/*

            # Публикация на TestPyPI (для теста)
            twine upload --repository testpypi dist/*

            # Публикация на PyPI
            twine upload dist/*
            """,
        ),
        text(
            "`python -m build` (PEP 517) создаёт wheel (.whl) и sdist (.tar.gz) в `dist/`. "
            "`twine check` валидирует метаданные. TestPyPI — безопасное место для тестовой публикации. "
            "PyPI требует токен (Settings → API tokens). `twine upload` использует токен из `.pypirc` или env.\n\n"
            "Wheel — бинарный формат (установка быстрее, без компиляции). Sdist — исходный дистрибутив "
            "(для платформ без wheel, для аудита кода). Оба нужны. `build` изолирует сборку во временном "
            "окружении, не загрязняет текущий venv. Версионирование: SemVer в `[project] version` или "
            "динамически через `[tool.setuptools.dynamic]` (например, из git tag через setuptools-scm). "
            "Автоматизация: `cz` (commitizen) для конвенциональных коммитов и авто-бампа версии."
        ),
        heading("Установка в editable-режиме (для разработки)", 3),
        example(
            "bash",
            """
            pip install -e .           # базовая
            pip install -e ".[dev]"    # с dev-зависимостями
            pip install -e ".[dev,docs]" # несколько extra
            """,
        ),
        text(
            "`-e` (editable) создаёт .pth файл, указывающий на исходники. "
            "Изменения в коде сразу видны без переустановки. `[dev]` подтягивает optional-dependencies.\n\n"
            "Editable install modes:\n"
            "- `pip install -e .` — legacy (setuptools .egg-link).\n"
            "- `pip install -e . --config-settings editable_mode=compat` — совместимый режим.\n"
            "- `pip install -e . --config-settings editable_mode=strict` — строгий (PEP 660), создаёт .pth с абсолютными путями, лучше для современных инструментов.\n"
            "Для пакетов с C-расширениями editable режим может не работать — нужен полный rebuild. "
            "В poetry/pdm/hatch editable режим работает нативно через свои бэкенды."
        ),
        heading("Линтинг и форматирование"),
        heading("Ruff — быстрый линтер (на Rust)", 3),
        example(
            "bash",
            """
            pip install ruff

            # Проверка
            ruff check src/

            # Автоисправление
            ruff check --fix src/

            # Только форматирование (аналог black)
            ruff format src/
            """,
        ),
        text(
            "Ruff — на Rust, в 10-100x быстрее flake8+isort+black+pyupgrade. "
            "Заменяет: flake8 (lint), isort (imports), pyupgrade (syntax upgrades), black (format), "
            "pydocstyle, flake8-bugbear, flake8-comprehensions. Конфиг в pyproject.toml `[tool.ruff]`.\n\n"
            "Категории правил (select):\n"
            "- E/F — pyflakes (синтаксис, undefined names).\n"
            "- I — isort (порядок импортов).\n"
            "- N — pep8-naming (конвенции имен).\n"
            "- W — pycodestyle (whitespace, line length).\n"
            "- UP — pyupgrade (современный синтаксис: f-strings, union types).\n"
            "- B — flake8-bugbear (баги: unused loop vars, mutable defaults).\n"
            "- C4 — flake8-comprehensions (list/dict/set comprehensions).\n"
            "- SIM — flake8-simplify (упрощения: `any(...)` вместо `len([...]) > 0`).\n"
            "- T20 — flake8-print (print statements).\n"
            "ignore = [\"E501\"] — отключает line-too-long (ruff format сам форматирует).\n"
            "`ruff check --fix` автоисправляет большинство проблем (unsafe fixes не применяет)."
        ),
        heading("Black / ruff format", 3),
        example(
            "bash",
            """
            pip install black
            black src/ tests/
            # Или через ruff format (быстрее, тот же стиль)
            ruff format src/ tests/
            """,
        ),
        text(
            "Black — uncompromising formatter. Нет конфигурации (почти). "
            "Ruff format — быстрее, совместим со стилем Black. "
            "Настройка в `[tool.black]` или `[tool.ruff.format]`.\n\n"
            "Black принципы:\n"
            "- Однозначное форматирование — нет споров в code review.\n"
            "- Line length 88 (по умолчанию) или 100/120 (в pyproject.toml).\n"
            "- Двойные кавычки, trailing commas, правильные отступы.\n"
            "- Не форматирует: `# fmt: off` / `# fmt: on` блоки.\n"
            "- `--check` — только проверка (для CI), `--diff` — показывает изменения.\n"
            "Ruff format — drop-in replacement, в 10x быстрее, тот же стиль. "
            "Настройка в `[tool.ruff.format]`: `quote-style`, `indent-style`, `line-length`."
        ),
        heading("Статическая типизация: mypy", 3),
        example(
            "bash",
            """
            pip install mypy
            mypy src/
            """,
        ),
        text(
            "Mypy — статический анализатор типов. Находит баги до запуска: None вместо значения, "
            "несовпадение аргументов, отсутствующие атрибуты. Работает с type hints (PEP 484)."
        ),
        heading("Строгий режим (рекомендуется)", 3),
        example(
            "toml",
            """
            [tool.mypy]
            strict = true
            warn_return_any = true
            warn_unused_configs = true
            disallow_untyped_defs = true
            no_implicit_optional = true
            """,
        ),
        text(
            "`strict = true` включает набор проверок: `disallow_untyped_defs`, `disallow_incomplete_defs`, "
            "`check_untyped_defs`, `disallow_untyped_decorators`, `no_implicit_optional`, "
            "`warn_return_any`, `warn_unused_ignores`, `warn_redundant_casts`. "
            "Для новых проектов включайте сразу. Для легаси — по модулям через `[[tool.mypy.overrides]]`.\n\n"
            "Полезные overrides для легаси:\n"
            "```toml\n"
            "[[tool.mypy.overrides]]\n"
            "module = [\"legacy_module.*\"]\n"
            "disallow_untyped_defs = false\n"
            "```\n"
            "Инкрементальное внедрение: `mypy --install-types --non-interactive` устанавливает stubs автоматически. "
            "`mypy --html-report report/` — HTML отчёт. "
            "Daemon mode: `dmypy run -- src/` — быстрые повторные проверки (daemon кэширует AST). "
            "IDE интеграция: VS Code (Pylance), PyCharm — real-time подсветка ошибок типов."
        ),
        heading("Типы для сторонних библиотек", 3),
        example(
            "bash",
            """
            pip install types-requests types-PyYAML  # stubs для популярных пакетов
            # или
            pip install mypy-stubs  # общий набор
            """,
        ),
        text(
            "Сторонние библиотеки часто не имеют типов. `types-*` пакеты (от mypy) предоставляют stubs. "
            "`mypy-stubs` — агрегат популярных. Для своих библиотек: добавляйте `py.typed` маркер "
            "и поставляйте `.pyi` файлы или inline типы.\n\n"
            "Как найти/установить stubs:\n"
            "- `pip install types-requests types-pyyaml types-redis types-boto3` — по пакету на библиотеку.\n"
            "- `pip install types-<package>` — поиск на PyPI (многие популярные имеют types-*).\n"
            "- `stubgen` (входит в mypy) — автогенерация `.pyi` из исходников: `stubgen -o stubs/ mylib`.\n"
            "- Для своих пакетов: добавьте `py.typed` файл в пакет, поставляйте `.pyi` рядом с `.py` или inline типы.\n"
            "- `mypy --install-types --non-interactive` — автоустановка недостающих stubs при проверке.\n"
            "Если stubs нет: `# type: ignore` на импорт или создайте свой `.pyi` в `stubs/`. "
            "Не злоупотребляйте `# type: ignore` — лучше написать stub."
        ),
        heading("Pre-commit хуки", 3),
        example(
            "yaml",
            """
            # .pre-commit-config.yaml
            repos:
              - repo: https://github.com/astral-sh/ruff-pre-commit
                rev: v0.4.0
                hooks:
                  - id: ruff
                    args: [--fix]
                  - id: ruff-format

              - repo: https://github.com/pre-commit/mirrors-mypy
                rev: v1.8.0
                hooks:
                  - id: mypy
                    additional_dependencies: [types-requests]

              - repo: https://github.com/pre-commit/pre-commit-hooks
                rev: v4.5.0
                hooks:
                  - id: trailing-whitespace
                  - id: end-of-file-fixer
                  - id: check-yaml
                  - id: check-toml
                  - id: check-merge-conflict
            """,
        ),
        example(
            "bash",
            """
            # Установка и активация
            pip install pre-commit
            pre-commit install
            pre-commit run --all-files  # прогон вручную
            """,
        ),
        text(
            "Pre-commit запускает хуки перед каждым коммитом. `ruff --fix` автоисправляет, "
            "`ruff-format` форматирует. `mypy` проверяет типы. Базовые хуки: trailing-whitespace, "
            "end-of-file-fixer, check-yaml/toml, check-merge-conflict. `pre-commit run --all-files` "
            "прогоняет на всех файлах (полезно при первом внедрении).\n\n"
            "Продвинутое использование:\n"
            "- `stages: [commit, push]` — запуск разных хуков на разных стадиях (быстрые на commit, тяжёлые на push).\n"
            "- `exclude: '^migrations/'` — пропуск файлов (regex).\n"
            "- `verbose: true` — подробный вывод.\n"
            "- `fail_fast: true` — остановиться на первой ошибке.\n"
            "- CI тоже должен запускать: `pre-commit run --all-files` (страховка для PR от других).\n"
            "- Для monorepo: отдельные `.pre-commit-config.yaml` на пакет или общий в корне с `files` фильтрами.\n\n"
            "Популярные дополнительные хуки:\n"
            "- `check-ast` — валидность Python синтаксиса.\n"
            "- `check-docstring-first` — docstring сразу после def/class.\n"
            "- `debug-logic` — проверка `breakpoint()` / `print()` / `pdb`.\n"
            "- `requirements-txt-fixer` — сортировка requirements.txt.\n"
            "- `detect-secrets` — поиск секретов в коде."
        ),
        heading("CI/CD: GitHub Actions", 3),
        example(
            "yaml",
            """
            # .github/workflows/ci.yml
            name: CI

            on:
              push:
                branches: [main]
              pull_request:
                branches: [main]

            jobs:
              test:
                runs-on: ubuntu-latest
                strategy:
                  matrix:
                    python-version: ["3.10", "3.11", "3.12"]

                steps:
                  - uses: actions/checkout@v4

                  - name: Set up Python ${{ matrix.python-version }}
                    uses: actions/setup-python@v5
                    with:
                      python-version: ${{ matrix.python-version }}
                      cache: "pip"

                  - name: Install dependencies
                    run: |
                      python -m pip install --upgrade pip
                      pip install -e ".[dev]"

                  - name: Run Ruff
                    run: ruff check src/ tests/

                  - name: Run Ruff format
                    run: ruff format --check src/ tests/

                  - name: Run mypy
                    run: mypy src/

                  - name: Run tests with coverage
                    run: pytest --cov=my_package --cov-report=xml

                  - name: Upload coverage
                    uses: codecov/codecov-action@v3
                    with:
                      files: ./coverage.xml

              build:
                needs: test
                runs-on: ubuntu-latest
                if: github.event_name == 'push' && github.ref == 'refs/heads/main'
                steps:
                  - uses: actions/checkout@v4
                  - uses: actions/setup-python@v5
                    with:
                      python-version: "3.11"
                  - name: Build package
                    run: |
                      pip install build twine
                      python -m build
                  - name: Publish to PyPI
                    env:
                      TWINE_USERNAME: __token__
                      TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
                    run: twine upload dist/*
            """,
        ),
        text(
            "CI пайплайн:\n"
            "- `matrix` — тестирует на Python 3.10, 3.11, 3.12 параллельно.\n"
            "- `cache: pip` — кэширует pip пакеты между запусками.\n"
            "- `ruff check` + `ruff format --check` — линтинг и проверка формата.\n"
            "- `mypy src/` — статическая типизация.\n"
            "- `pytest --cov` — тесты с покрытием, загрузка в Codecov.\n"
            "- `build` job: только на push в main, после успешных тестов, публикует на PyPI.\n"
            "- Секреты: `PYPI_API_TOKEN` в Settings → Secrets.\n\n"
            "Best practices для CI:\n"
            "- `actions/checkout@v4` с `fetch-depth: 0` для истории (нужно для setuptools-scm).\n"
            "- `actions/setup-python@v5` с `cache: 'pip'` — кэш pip пакетов.\n"
            "- `pip install -e \".[dev]\"` — ставит пакет + dev зависимости одним командой.\n"
            "- `ruff format --check` — только проверка формата (не меняет файлы).\n"
            "- `mypy --install-types --non-interactive` — автоустановка stubs в CI.\n"
            "- `pytest -n auto --dist=loadscope` — параллельные тесты через xdist.\n"
            "- `codecov/codecov-action@v3` с `fail_ci_if_error: true` — фейлит CI при падении coverage.\n"
            "- `build` job с `needs: test` и `if: github.ref == 'refs/heads/main'` — деплой только из main.\n"
            "- Токены: `PYPI_API_TOKEN` (Settings → Secrets → Actions), не в коде.\n"
            "- Для release: теги `v*` триггерят отдельный workflow `release.yml` с changelog генерацией."
        ),
        heading("Полезные инструменты экосистемы", 3),
        table(
            ["Категория", "Инструмент", "Назначение"],
            [
                ["Зависимости", "`pip-tools`", "Компиляция requirements.txt из .in файлов"],
                ["", "`pip-audit`", "Проверка уязвимостей в зависимостях"],
                ["", "`deptry`", "Поиск неиспользуемых/отсутствующих зависимостей"],
                ["Документация", "`sphinx` + `furo`", "Генерация docs"],
                ["", "`mkdocs` + `mkdocstrings`", "Альтернатива, markdown-based"],
                ["Профилирование", "`py-spy`", "Сэмплинг профайлер (без изменений кода)"],
                ["", "`scalene`", "CPU/GPU/мемори профайлер"],
                ["Безопасность", "`bandit`", "Статический анализ безопасности"],
                ["", "`safety`", "Проверка известных CVE в зависимостях"],
                ["Прочее", "`pytest-xdist`", "Параллельный запуск тестов (`-n auto`)"],
                ["", "`hypothesis`", "Property-based testing"],
                ["", "`nox`", "Тестирование в нескольких окружениях"],
            ],
        ),
        text(
            "`pip-tools`: `pip-compile requirements.in` → `requirements.txt` (закреплённые версии). "
            "`pip-sync` — синхронизирует venv с requirements.txt. "
            "`pip-audit` сканирует установленные пакеты на CVE. "
            "`bandit` — статический анализ безопасности (hardcoded secrets, shell injection, etc). "
            "`pytest-xdist -n auto` — параллельные тесты на всех ядрах. "
            "`hypothesis` — генерирует тест-кейсы для property-based testing. "
            "`nox` — тестирует в изолированных venv для разных Python версий/зависимостей.\n\n"
            "Дополнительные инструменты:\n"
            "- `deptry` — находит неиспользуемые зависимости (в pyproject.toml но не в импортах) и отсутствующие (импортируются но нет в deps). `deptry .`.\n"
            "- `pyupgrade` — автоапгрейд синтаксиса на новый Python (f-strings, union types, walrus). Встроен в ruff (UP коды).\n"
            "- `autoflake` — удаляет неиспользуемые импорты и переменные. `autoflake --remove-all-unused-imports --recursive .`.\n"
            "- `isort` — сортировка импортов (встроен в ruff). Отдельно не нужен.\n"
            "- `pdoc` / `mkdocstrings` — автодокументация из docstrings. `pdoc -o docs/ src/`.\n"
            "- `commitizen` / `cz` — конвенциональные коммиты, авто-бамп версии, changelog генерация.\n"
            "- `semantic-release` — полностью автоматический релиз: анализ коммитов → бамп версии → changelog → publish.\n"
            "- `dependabot` / `renovate` — авто-PR для обновления зависимостей (настроен в GitHub).\n"
            "- `pre-commit-hooks` — базовые проверки (trailing-whitespace, end-of-file-fixer, check-yaml/toml, merge-conflict).\n"
            "- `detect-secrets` — сканирование кода на секреты (API keys, passwords). `detect-secrets scan > .secrets.baseline`."
        ),
        heading("Чек-лист готового проекта", 3),
        bullets(
            "`pyproject.toml` с метаданными, зависимостями, optional-deps",
            "`src/` layout (изоляция кода)",
            "`README.md` с badges (build, coverage, version, license)",
            "`LICENSE` (MIT/Apache-2.0/BSD)",
            "`.gitignore` (venv, __pycache__, .pytest_cache, dist, *.egg-info)",
            "`.pre-commit-config.yaml` + `pre-commit install`",
            "`ruff` + `black` (или `ruff format`) настроены",
            "`mypy` в strict режиме проходит",
            "`pytest` с coverage ≥ 80%",
            "GitHub Actions: lint → typecheck → test → build → publish",
            "`pip-audit` / `bandit` в CI",
            "Версионирование: SemVer, changelog (Keep a Changelog)",
        ),
        text(
            "Badges в README: `![build](...)`, `![coverage](...)`, `![version](...)`, `![license](...)`. "
            "`.gitignore`: `venv/`, `__pycache__/`, `.pytest_cache/`, `dist/`, `*.egg-info/`, `.mypy_cache/`, `.ruff_cache/`. "
            "SemVer: MAJOR.MINOR.PATCH (breaking.feature.fix). Changelog: `## [1.2.0] - 2024-01-15`."
        ),
        heading("Типичные ошибки", 2),
        table(
            ["Ошибка", "Последствия", "Как правильно"],
            [
                ["`setup.py` + `setup.cfg` вместо `pyproject.toml`", "Устаревший стандарт, не все инструменты поддерживают", "Только `pyproject.toml` (PEP 621)"],
                ["Код в корне проекта", "Путаница импортов, тесты ломаются", "Используйте `src/` layout"],
                ["Жёсткие версии в `dependencies`", "Конфликты зависимостей у пользователей", "Минимальные версии (`>=`), закрепляйте в `requirements.txt` через `pip-tools`"],
                ["`black` + `isort` + `flake8` отдельно", "Медленно, конфиги рассинхронизируются", "`ruff` делает всё это быстрее"],
                ["`mypy` без `strict`", "Пропускает баги типов", "Включайте `strict = true` с первого дня"],
                ["Нет pre-commit", "Плохой код попадает в репо", "pre-commit install + CI как страховка"],
                ["Тесты без coverage", "Слепые зоны", "pytest --cov, минимум 80%"],
                ["Публикация без TestPyPI", "Сломанный пакет на PyPI", "Сначала twine upload --repository testpypi"],
            ],
        ),
        heading("Практика", 2),
        text(
            "Выполните задания по порядку. Создайте новый репозиторий для практики."
        ),
        numbered(
            "Инициализируйте проект: `python -m venv venv`, создайте `pyproject.toml`, `src/mypkg/`, `tests/`.",
            "Настройте pre-commit: ruff, mypy, базовые хуки.",
            "Напишите CI: matrix testing 3.10-3.12, coverage upload.",
            "Опубликуйте на TestPyPI: `twine upload --repository testpypi dist/*`.",
            "Добавьте dependabot: `.github/dependabot.yml` для автообновлений.",
        ),
        text("Пример ожидаемого результата для первого задания (структура):"),
        example(
            "text",
            "my_project/\n"
            "├── pyproject.toml\n"
            "├── README.md\n"
            "├── LICENSE\n"
            "├── src/\n"
            "│   └── mypkg/\n"
            "│       ├── __init__.py\n"
            "│       └── core.py\n"
            "├── tests/\n"
            "│   ├── __init__.py\n"
            "│   └── test_core.py\n"
            "├── .pre-commit-config.yaml\n"
            "└── .github/workflows/ci.yml",
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "pre-commit: `pip install pre-commit && pre-commit install`. "
            "Ruff: `args: [--fix]` для автоисправления. MyPy: `additional_dependencies: [types-requests]` для stubs. "
            "Прогон вручную: `pre-commit run --all-files`.",
        ),
        heading("Проверьте себя", 2),
        numbered(
            "Зачем нужен `src/` layout?",
            "Какие секции обязательны в `pyproject.toml` по PEP 621?",
            "Чем `ruff` лучше набора `flake8 + isort + black + pyupgrade`?",
            "Что включает `mypy strict = true`?",
            "Зачем нужен `pre-commit`, если есть CI?",
            "Как опубликовать пакет на PyPI?",
            "Зачем нужен `pip-tools` и `requirements.in`?",
        ),
        heading("Ответы", 2),
        numbered(
            "`src/` изолирует пакет от корня, тесты импортируют установленную версию, избегает путаницы импортов.",
            "`[build-system]`, `[project]` (name, version, dependencies, optional-dependencies, scripts), "
            "`[tool.setuptools.packages.find]`. Опционально: `[project.optional-dependencies]`, `[project.urls]`.",
            "Ruff на Rust — в 10-100x быстрее, единый конфиг, заменяет 5+ инструментов, автофикс.",
            "strict включает: disallow_untyped_defs, disallow_incomplete_defs, check_untyped_defs, "
            "disallow_untyped_decorators, no_implicit_optional, warn_return_any, warn_unused_ignores, "
            "warn_redundant_casts.",
            "Pre-commit ловит проблемы мгновенно у разработчика (до пуша). CI — страховка на сервере для PR от других.",
            "`pip install build twine && python -m build && twine check dist/* && twine upload dist/*` "
            "(токен в .pypirc или env).",
            "`pip-tools`: `pip-compile requirements.in` → `requirements.txt` (закреплённые версии). "
            "`pip-sync` синхронизирует venv. Воспроизводимые билды.",
        ),
        heading("Итоги", 2),
        bullets(
            "pyproject.toml (PEP 621) — единый конфиг: метаданные, зависимости, optional-deps, entry points, tool configs.",
            "src layout — изоляция кода, корректные тесты, изоляция от корня проекта.",
            "Сборка: `python -m build` → wheel + sdist. Публикация: `twine upload` (TestPyPI → PyPI).",
            "Ruff — быстрый линтер/форматтер на Rust, заменяет flake8/isort/black/pyupgrade. Конфиг в pyproject.toml.",
            "Mypy strict — статическая типизация, ловит баги до запуска. Stubs для сторонних libs: `types-*`.",
            "Pre-commit — автопроверка перед коммитом (ruff, mypy, базовые хуки). CI — страховка на сервере.",
            "GitHub Actions CI: matrix testing, lint → typecheck → test → coverage → build → publish (на main).",
            "Полезные утилиты: pip-tools (compile/sync), pip-audit (CVE), bandit (security), pytest-xdist (parallel), hypothesis (property-based).",
            "Чек-лист: pyproject.toml, src/, README+badges, LICENSE, .gitignore, pre-commit, ruff/mypy, pytest+cov≥80%, CI, SemVer+changelog.",
        ),
        heading("Что дальше", 2),
        text(
            "Профессиональные инструменты — фундамент. В следующем уроке разберём безопасность и надёжность: "
            "продвинутая аутентификация (OAuth2, OIDC, JWT), управление секретами (Vault, AWS Secrets Manager), "
            "аудит безопасности (SAST/DAST), compliance (GDPR, PCI DSS), инцидент-менеджмент, "
            "chaos engineering, observability (metrics, logs, traces, SLO/SLI)."
        ),
        heading("Если хотите углубиться", 2),
        bullets(
            "Python Packaging User Guide — packaging.python.org/",
            "pyproject.toml spec (PEP 621) — packaging.python.org/en/latest/specifications/pyproject-toml/",
            "Ruff docs — docs.astral.sh/ruff/",
            "mypy docs — mypy.readthedocs.io/",
            "pre-commit.com — pre-commit.com/",
            "GitHub Actions for Python — docs.github.com/en/actions/use-cases-and-examples/building-and-testing-python",
            "pip-tools — github.com/jazzband/pip-tools",
            "Hypothesis — hypothesis.works/",
        ),
    ],
}