"""Урок 2.9 курса Python: работа с данными."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


LESSON = {
    "language": "python",
    "program_order": 2,
    "topic_order": 9,
    "name": "2.9. Работа с данными",
    "slug": "python-2-9-работа-с-данными",
    "short_description": (
        "Форматы данных (JSON, CSV, YAML, TOML), базы данных (SQLite, SQLAlchemy), "
        "сериализация и базовый анализ с pandas."
    ),
    "topic_name": "Работа с данными",
    "topic_description": (
        "Как читать, записывать, преобразовывать и анализировать данные в "
        "разных форматах: от простых файлов до реляционных баз и DataFrame."
    ),
    "learning_objectives": [
        "Читать и записывать JSON, CSV, YAML, TOML с стандартной библиотекой и сторонними пакетами",
        "Работать с SQLite через sqlite3 и ORM (SQLAlchemy)",
        "Понимать разницу между синхронными и асинхронными драйверами БД",
        "Сериализовать и десериализовать объекты: pickle, msgpack, orjson",
        "Выполнять базовый анализ данных с pandas DataFrame",
    ],
    "estimated_minutes": 45,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "python",
        "данные",
        "json",
        "csv",
        "sqlite",
        "sqlalchemy",
        "pandas",
        "сериализация",
    ],
    "starter_code": code(
        """
        import json
        import csv

        # JSON
        data = {"users": [{"name": "Анна", "age": 25}, {"name": "Борис", "age": 30}]}
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        print(json_str)

        # CSV
        with open("users.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age"])
            writer.writeheader()
            writer.writerows(data["users"])
        """
    ),
    "hints": [
        "ensure_ascii=False сохраняет кириллицу читаемой, а не в виде \\u0430\\u043d\\u043d\\u0430.",
        "newline='' в open() для CSV предотвращает лишние пустые строки на Windows.",
        "SQLAlchemy ORM позволяет работать с БД как с объектами, не пишя SQL вручную.",
        "pandas удобен для анализа, но для простых задач часто достаточно стандартной библиотеки.",
        "pickle небезопасен для непроверенных данных — используйте JSON или msgpack для обмена.",
    ],
    "content": [
        {
            "type": "text",
            "content": (
                "Программы редко работают в вакууме: они читают конфигурации, "
                "сохраняют результаты, обмениваются данными с другими сервисами. "
                "Умение работать с разными форматами данных — базовый навык "
                "любого разработчика. В этом уроке разберём основные форматы "
                "обмена (JSON, CSV, YAML, TOML), работу с реляционными базами "
                "данных через SQLite и SQLAlchemy, сериализацию объектов и "
                "базовый анализ данных с pandas."
            ),
        },
        {"type": "heading", "level": 2, "content": "Чему вы научитесь"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "читать и записывать JSON, CSV, YAML, TOML, понимать их особенности и ограничения;",
                "работать с SQLite напрямую через sqlite3 и через ORM (SQLAlchemy);",
                "понимать, когда нужен асинхронный драйвер БД (asyncpg, aiosqlite);",
                "сериализовать данные: pickle для Python, JSON/msgpack/orjson для обмена;",
                "загружать данные в pandas DataFrame, фильтровать, группировать и агрегировать.",
            ],
        },
        {"type": "heading", "level": 2, "content": "JSON — стандарт обмена данными"},
        {"type": "heading", "level": 3, "content": "Базовая работа с json"},
        {
            "type": "text",
            "content": (
                "JSON (JavaScript Object Notation) — самый распространённый формат "
                "обмена данными в вебе. В Python модуль json входит в стандартную "
                "библиотеку и не требует установки. Он умеет кодировать базовые "
                "типы: dict, list, str, int, float, bool, None."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import json

                data = {"name": "Анна", "age": 25, "skills": ["Python", "SQL"]}

                # В строку
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                print(json_str)

                # Из строки
                parsed = json.loads(json_str)
                print(parsed["name"])

                # В файл
                with open("data.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                # Из файла
                with open("data.json", encoding="utf-8") as f:
                    loaded = json.load(f)
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "{\n  \"name\": \"Анна\",\n  \"age\": 25,\n  \"skills\": [\n    \"Python\",\n    \"SQL\"\n  ]\n}\nАнна",
        },
        {
            "type": "text",
            "content": (
                "Параметр ensure_ascii=False критически важен для кириллицы: "
                "без него русские буквы превращаются в escape-последовательности "
                "вида \\u0410\\u043d\\u043d\\u0430. indent=2 делает вывод "
                "читаемым (pretty-print), но увеличивает размер файла. Для "
                "передачи по сети indent обычно опускают."
            ),
        },
        {"type": "heading", "level": 3, "content": "Кастомный JSONEncoder"},
        {
            "type": "text",
            "content": (
                "Стандартный json не умеет сериализовать datetime, dataclass, "
                "Decimal, set и пользовательские классы. Решение — свой класс "
                "от json.JSONEncoder с переопределением метода default()."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import json
                from datetime import datetime
                from dataclasses import dataclass, asdict

                @dataclass
                class User:
                    name: str
                    age: int

                class CustomEncoder(json.JSONEncoder):
                    def default(self, obj):
                        if isinstance(obj, datetime):
                            return obj.isoformat()
                        if hasattr(obj, "__dataclass_fields__"):
                            return asdict(obj)
                        return super().default(obj)

                data = {
                    "time": datetime(2026, 1, 15, 14, 30),
                    "user": User("Анна", 25)
                }
                print(json.dumps(data, cls=CustomEncoder, ensure_ascii=False))
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "{\"time\": \"2026-01-15T14:30:00\", \"user\": {\"name\": \"Анна\", \"age\": 25}}",
        },
        {"type": "heading", "level": 3, "content": "orjson — быстрый JSON на Rust"},
        {
            "type": "text",
            "content": (
                "Стандартный json написан на C, но orjson (написан на Rust) "
                "работает в 2–10 раз быстрее и возвращает bytes, а не str. "
                "Это де-факто стандарт для высоконагруженных сервисов."
            ),
        },
        {
            "type": "code",
            "language": "bash",
            "content": "pip install orjson"
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import orjson

                data = {"users": [{"id": i, "name": f"User{i}"} for i in range(1000)]}

                # Быстрее в 2-10 раз, возвращает bytes
                data_bytes = orjson.dumps(data)
                parsed = orjson.loads(data_bytes)

                # Опции форматирования
                pretty = orjson.dumps(
                    {"a": 1},
                    option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS
                )
                print(pretty)
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "{\n  \"a\": 1\n}",
        },
        {
            "type": "callout",
            "style": "info",
            "title": "Когда использовать orjson",
            "content": (
                "orjson быстрее, но требует установки и возвращает bytes. "
                "Используйте в высоконагруженных API, логировании, кэшировании. "
                "Для конфигов и простых скриптов стандартного json достаточно."
            ),
        },
        {"type": "heading", "level": 2, "content": "CSV — табличные данные"},
        {"type": "heading", "level": 3, "content": "Стандартная библиотека csv"},
        {
            "type": "text",
            "content": (
                "CSV (Comma-Separated Values) — простой формат табличных данных. "
                "Модуль csv из стандартной библиотеки справляется с чтением и "
                "записью, корректно обрабатывая кавычки, запятые внутри полей "
                "и переносы строк."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import csv

            # Запись через writer
            with open("users.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["name", "age", "city"])
                writer.writerow(["Анна", 25, "Москва"])
                writer.writerow(["Борис", 30, "СПб"])

            # DictWriter — удобнее для словарей
            with open("users.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["name", "age", "city"])
                writer.writeheader()
                writer.writerow({"name": "Анна", "age": 25, "city": "Москва"})

            # Чтение
            with open("users.csv", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    print(row)
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "{'name': 'Анна', 'age': '25', 'city': 'Москва'}\n{'name': 'Борис', 'age': '30', 'city': 'СПб'}",
        },
        {
            "type": "text",
            "content": (
                "Важный момент: newline='' при открытии файла на запись "
                "предотвращает преобразование \\n в \\r\\n на Windows, "
                "что создавало бы лишние пустые строки. При чтении DictReader "
                "автоматически использует первую строку как заголовки и "
                "возвращает словари. Все значения приходят строками — "
                "преобразование типов (int, float) на вашей совести."
            ),
        },
        {"type": "heading", "level": 3, "content": "pandas — мощный анализ CSV"},
        {
            "type": "text",
            "content": (
                "Для анализа больших таблиц стандартная библиотека неудобна. "
                "pandas — де-факто стандарт: DataFrame даёт SQL-подобные "
                "операции (фильтрация, группировка, join, pivot) и быстрый "
                "векторный расчёт."
            ),
        },
        {
            "type": "code",
            "language": "bash",
            "content": "pip install pandas"
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import pandas as pd

                # Чтение
                df = pd.read_csv("users.csv")
                print(df.head())
                print(df.dtypes)

                # Фильтрация
                adults = df[df["age"] >= 18]

                # Группировка
                by_city = df.groupby("city")["age"].mean()
                print(by_city)

                # Новые колонки
                df["age_next_year"] = df["age"] + 1
                """
            ),
        },
        {
            "type": "callout",
            "style": "info",
            "title": "Когда pandas, а когда csv",
            "content": (
                "csv модуль: простые задачи, стриминг больших файлов, "
                "минимальные зависимости. pandas: анализ, статистика, "
                "сложные трансформации, join таблиц. Для 100К+ строк "
                "pandas удобнее, для простого чтения — csv."
            ),
        },
        {"type": "heading", "level": 2, "content": "YAML и TOML — конфигурация"},
        {"type": "heading", "level": 3, "content": "YAML — читаемый формат"},
        {
            "type": "code",
            "language": "bash",
            "content": "pip install pyyaml"
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import yaml

                config = {
                    "database": {"host": "localhost", "port": 5432},
                    "features": ["auth", "cache", "logging"],
                    "debug": True
                }

                # Запись
                with open("config.yaml", "w") as f:
                    yaml.dump(config, f, allow_unicode=True, sort_keys=False)

                # Чтение
                with open("config.yaml") as f:
                    loaded = yaml.safe_load(f)
                print(loaded)
                """
            ),
        },
        {
            "type": "callout",
            "style": "warning",
            "title": "Безопасность yaml.load",
            "content": (
                "Всегда используйте yaml.safe_load(), а не yaml.load(). "
                "yaml.load() без Loader может выполнять произвольный Python-код "
                "через !!python/object теги — критическая уязвимость."
            ),
        },
        {"type": "heading", "level": 3, "content": "TOML — современный стандарт конфигов"},
        {
            "type": "text",
            "content": (
                "TOML (Tom's Obvious Minimal Language) — формат конфигурации, "
                "стандарт в Python-экосистеме (pyproject.toml). В Python 3.11+ "
                "модуль tomllib встроен для чтения, для записи нужен tomli-w."
            ),
        },
        {
            "type": "code",
            "language": "bash",
            "content": "pip install tomli-w  # для записи, чтение встроено в 3.11+"
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import tomllib
                import tomli_w

                config = {
                    "tool": {"pytest": {"ini_options": {"asyncio_mode": "auto"}}},
                    "project": {"name": "myapp", "version": "1.0.0"}
                }

                # Запись (tomli-w)
                with open("pyproject.toml", "wb") as f:
                    tomli_w.dump(config, f)

                # Чтение (tomllib в 3.11+, иначе tomllib через pip)
                with open("pyproject.toml", "rb") as f:
                    loaded = tomllib.load(f)
                print(loaded)
                """
            ),
        },
        {
            "type": "callout",
            "style": "info",
            "title": "YAML vs TOML",
            "content": (
                "YAML: гибкий, поддерживает комментарии, якоря, алиасы — "
                "хорош для сложных конфигов. TOML: строже, проще, стандарт "
                "в Python — лучше для pyproject.toml и простых настроек."
            ),
        },
        {"type": "heading", "level": 2, "content": "SQLite и SQLAlchemy"},
        {"type": "heading", "level": 3, "content": "Встроенный sqlite3"},
        {
            "type": "text",
            "content": (
                "SQLite — встроенная в Python база данных: файл на диске, "
                "нет отдельного сервера. Модуль sqlite3 входит в стандартную "
                "библиотеку. Подходит для локальных приложений, тестов, кэша."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import sqlite3

                with sqlite3.connect("app.db") as conn:
                    # Создание таблицы
                    conn.execute('''
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            age INTEGER,
                            email TEXT UNIQUE
                        )
                    ''')

                    # Вставка
                    conn.execute(
                        "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
                        ("Анна", 25, "anna@example.com")
                    )

                    # Выборка
                    cursor = conn.execute("SELECT * FROM users WHERE age > ?", (18,))
                    for row in cursor:
                        print(row)
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Плейсхолдеры ? (или :name) защищают от SQL-инъекций — никогда "
                "не форматируйте SQL строку вручную через f-строки. "
                "sqlite3 возвращает строки как tuple, можно использовать "
                "conn.row_factory = sqlite3.Row для доступа по имени колонки."
            ),
        },
        {"type": "heading", "level": 3, "content": "SQLAlchemy Core и ORM"},
        {
            "type": "text",
            "content": (
                "SQLAlchemy — мощный toolkit: Core даёт SQL-выражения на Python, "
                "ORM отображает таблицы в классы. Установка: pip install sqlalchemy."
            ),
        },
        {
            "type": "code",
            "language": "bash",
            "content": "pip install sqlalchemy"
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from sqlalchemy import create_engine, Column, Integer, String, select
                from sqlalchemy.orm import DeclarativeBase, Session

                class Base(DeclarativeBase):
                    pass

                class User(Base):
                    __tablename__ = "users"
                    id = Column(Integer, primary_key=True)
                    name = Column(String, nullable=False)
                    age = Column(Integer)
                    email = Column(String, unique=True)

                engine = create_engine("sqlite:///app.db", echo=True)
                Base.metadata.create_all(engine)

                # Запись через Session
                with Session(engine) as session:
                    user = User(name="Анна", age=25, email="anna@example.com")
                    session.add(user)
                    session.commit()

                    # Чтение
                    stmt = select(User).where(User.age >= 18)
                    for user in session.scalars(stmt):
                        print(user.name, user.age)
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "DeclarativeBase (SQLAlchemy 2.0+) заменяет старый declarative_base(). "
                "Session управляет транзакцией: commit() фиксирует, при исключении "
                "автоматически rollback(). scalars() возвращает скалярные "
                "результаты (объекты), не кортежи."
            ),
        },
        {"type": "heading", "level": 3, "content": "Асинхронная работа с БД"},
        {
            "type": "text",
            "content": (
                "В асинхронных приложениях (FastAPI, aiogram, aiohttp) "
                "синхронный sqlite3 или SQLAlchemy блокируют event loop. "
                "Нужны асинхронные драйверы: aiosqlite для SQLite, "
                "asyncpg для PostgreSQL, aiomysql для MySQL."
            ),
        },
        {
            "type": "code",
            "language": "bash",
            "content": "pip install aiosqlite sqlalchemy[asyncio]"
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
                from sqlalchemy.orm import DeclarativeBase, sessionmaker
                from sqlalchemy import Column, Integer, String, select

                class Base(DeclarativeBase):
                    pass

                class User(Base):
                    __tablename__ = "users"
                    id = Column(Integer, primary_key=True)
                    name = Column(String)
                    age = Column(Integer)

                async_engine = create_async_engine("sqlite+aiosqlite:///app.db", echo=True)
                async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

                async def main():
                    async with async_engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)

                    async with async_session() as session:
                        user = User(name="Анна", age=25)
                        session.add(user)
                        await session.commit()

                        result = await session.execute(select(User).where(User.age >= 18))
                        for user in result.scalars():
                            print(user.name)

                import asyncio
                asyncio.run(main())
                """
            ),
        },
        {
            "type": "callout",
            "style": "info",
            "title": "Async vs Sync SQLAlchemy",
            "content": (
                "API почти идентично: create_async_engine вместо create_engine, "
                "AsyncSession вместо Session, await перед commit/execute. "
                "В sync-версии Session — контекстный менеджер, в async — "
                "async_session() возвращает асинхронный контекстный менеджер."
            ),
        },
        {"type": "heading", "level": 2, "content": "Сериализация объектов"},
        {"type": "heading", "level": 3, "content": "pickle — нативная сериализация Python"},
        {
            "type": "text",
            "content": (
                "pickle сериализует почти любой Python-объект: классы, функции, "
                "замыкания, рекурсивные структуры. Формат бинарный, специфичен "
                "для Python, не подходит для обмена с другими языками."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import pickle

                data = {"users": [User("Анна", 25), User("Борис", 30)]}

                # Запись
                with open("data.pkl", "wb") as f:
                    pickle.dump(data, f)

                # Чтение
                with open("data.pkl", "rb") as f:
                    loaded = pickle.load(f)

                # protocol=5 (Python 3.8+) — быстрее и компактнее
                pickle.dump(data, open("data.pkl", "wb"), protocol=5)
                """
            ),
        },
        {
            "type": "callout",
            "style": "danger",
            "title": "pickle небезопасен",
            "content": (
                "pickle.load() может выполнять произвольный код при десериализации "
                "злонамеренных данных. Никогда не делайте pickle.load() с "
                "недоверенных источников (файлы из интернета, загрузки пользователей). "
                "Для обмена данными используйте JSON, msgpack или orjson."
            ),
        },
        {"type": "heading", "level": 3, "content": "msgpack — компактная бинарная сериализация"},
        {
            "type": "code",
            "language": "bash",
            "content": "pip install msgpack"
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import msgpack

                data = {"users": [{"id": i, "name": f"User{i}"} for i in range(1000)]}

                packed = msgpack.packb(data, use_bin_type=True)
                unpacked = msgpack.unpackb(packed, raw=False)

                print(f"JSON: {len(json.dumps(data))} байт")
                print(f"msgpack: {len(packed)} байт")
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "msgpack компактнее JSON (обычно в 2–3 раза), быстрее парсится "
                "и поддерживает бинарные данные. Формат кроссплатформенный, "
                "есть реализации на многих языках. Подходит для RPC, кэша, "
                "обмена между сервисами."
            ),
        },
        {"type": "heading", "level": 2, "content": "Базовый анализ данных с pandas"},
        {"type": "heading", "level": 3, "content": "DataFrame — основная структура"},
        {
            "type": "text",
            "content": (
                "DataFrame — двумерная таблица с индексами строк и колонок. "
                "Поддерживает векторные операции, отсутствующие значения (NaN), "
                "временные ряды и сложные трансформации."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import pandas as pd
                import numpy as np

                # Создание
                df = pd.DataFrame({
                    "name": ["Анна", "Борис", "Виктор"],
                    "age": [25, 30, 35],
                    "salary": [80000, 120000, 95000],
                    "dept": ["IT", "HR", "IT"]
                })

                # Базовые операции
                print(df.describe())          # статистика
                print(df[df["age"] > 28])     # фильтрация
                print(df.groupby("dept")["salary"].mean())  # группировка
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "Чтение из разных источников"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import pandas as pd

                # CSV
                df = pd.read_csv("data.csv", encoding="utf-8")

                # JSON
                df = pd.read_json("data.json", orient="records")

                # Excel
                df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

                # SQL
                import sqlite3
                conn = sqlite3.connect("app.db")
                df = pd.read_sql("SELECT * FROM users", conn)

                # Parquet (быстрый колоночный формат)
                df.to_parquet("data.parquet")
                df = pd.read_parquet("data.parquet")
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "Очистка и трансформация"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import pandas as pd
                import numpy as np

                df = pd.read_csv("dirty_data.csv")

                # Пропуски
                df = df.dropna(subset=["email"])      # удалить строки без email
                df["age"] = df["age"].fillna(df["age"].median())  # заполнить пропуски

                # Типы
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                df["salary"] = df["salary"].astype(float)

                # Строки
                df["email"] = df["email"].str.lower().str.strip()
                df["name"] = df["name"].str.title()

                # Новые колонки
                df["age_group"] = pd.cut(df["age"], bins=[0, 18, 35, 60, 100],
                                         labels=["child", "young", "adult", "senior"])
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "Слияние и агрегация"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import pandas as pd

                users = pd.DataFrame({"id": [1, 2], "name": ["Анна", "Борис"]})
                orders = pd.DataFrame({"user_id": [1, 1, 2], "amount": [100, 200, 50]})

                # JOIN
                merged = users.merge(orders, left_on="id", right_on="user_id", how="left")

                # Агрегация
                summary = merged.groupby("name")["amount"].agg(["sum", "mean", "count"])
                print(summary)
                """
            ),
        },

        {"type": "heading", "level": 2, "content": "Глубина погружения: архитектура хранения данных"},
        {"type": "text", "content": (
            "Выбор формата хранения и инструмента работы с данными определяет "
            "архитектуру всего приложения. Неправильный выбор на ранней стадии "
            "приводит к дорогостоящим миграциям позже. Рассмотрим ключевые "
            "критерии выбора."
        )},
        {"type": "heading", "level": 3, "content": "Критерии выбора формата"},
        {"type": "list", "ordered": False, "items": [
            "Структура данных: плоские таблицы -> CSV/Parquet/SQL, вложенные объекты -> JSON/YAML/TOML, графы -> специализированные БД.",
            "Объём данных: <100 МБ — любые форматы, 100 МБ - 10 ГБ -> Parquet/SQLite/ DuckDB, >10 ГБ -> распределённые системы (ClickHouse, Snowflake).",
            "Частота обновлений: редкие записи/частое чтение -> колоночные форматы (Parquet), частые записи/чтение -> строковые БД (SQLite/PostgreSQL).",
            "Требования к консистентности: ACID транзакции -> реляционные БД, eventual consistency достаточно -> NoSQL/файлы.",
            "Интероперабельность: JSON для веб-API, Parquet для аналитики, Protobuf/Avro для микросервисов."
        ]},
        {"type": "heading", "level": 3, "content": "Производительность сериализации"},
        {"type": "text", "content": (
            "Выбор сериализатора влияет на пропускную способность системы. "
            "Ориентировочные скорости для типичного объекта 1 КБ (операций в секунду):"
        )},
        {"type": "table", "headers": ["Формат", "Скорость (отн.)", "Размер (отн.)", "Безопасность"], "rows": [
            ["orjson", "100%", "100%", "Высокая"],
            ["msgpack", "80%", "40%", "Высокая"],
            ["JSON (stdlib)", "30%", "100%", "Высокая"],
            ["pickle (proto=5)", "20%", "80%", "Низкая (RCE)"],
            ["YAML", "5%", "120%", "Средняя (safe_load)"],
            ["TOML", "10%", "110%", "Высокая"]
        ]},
        {"type": "heading", "level": 3, "content": "Параллелизм и данные"},
        {"type": "text", "content": (
            "В асинхронных приложениях доступ к данным требует особого внимания. "
            "Основные паттерны:"
        )},
        {"type": "list", "ordered": False, "items": [
            "Connection pooling: переиспользование соединений к БД (asyncpg pool, aiosqlite не поддерживает пул нативно).",
            "Read replicas: разделение чтения и записи для масштабирования.",
            "Caching: Redis/memcached для горячих данных, TTL и инвалидация.",
            "Batch processing: накопление операций и пакетная запись (bulk insert) вместо поштучной.",
            "Idempotency: ключи идемпотентности для повторных запросов без побочных эффектов."
        ]},
        {"type": "heading", "level": 3, "content": "Миграции схемы"},
        {"type": "text", "content": (
            "Эволюция схемы данных неизбежна. Инструменты и практики:"
        )},
        {"type": "list", "ordered": False, "items": [
            "Alembic для SQLAlchemy: версионирование миграций, автогенерация, откат.",
            "Обратная совместимость: новые колонки — nullable или с default, старые не удалять сразу.",
            "Blue-green deployment: новая схема в параллельной БД, переключение трафика.",
            "Тестирование миграций: на копии продакшн-данных в staging."
        ]},
        {"type": "heading", "level": 3, "content": "Качество данных"},
        {"type": "text", "content": (
            "Данные в реальном мире грязные. Стратегии очистки:"
        )},
        {"type": "list", "ordered": False, "items": [
            "Валидация на входе: Pydantic модели, JSON Schema, Cerberus.",
            "Дедупликация: детерминированные ключи, fuzzy matching для нечётких дублей.",
            "Аномалии: статистические методы (IQR, z-score), isolation forest для выбросов.",
            "Логирование качества: метрики полноты, валидности, согласованности данных."
        ]},

        {"type": "heading", "level": 3, "content": "Профилирование производительности"},
        {"type": "text", "content": (
            "Прежде чем оптимизировать, нужно измерить. Инструменты профилирования:"
        )},
        {"type": "list", "ordered": False, "items": [
            "cProfile / snakeviz: CPU профилирование, поиск горячих функций.",
            "memory_profiler / objgraph: поиск утечек памяти.",
            "py-spy: sampling профайлер для продакшена, низкие накладные расходы.",
            "line_profiler: построчное профилирование медленных функций."
        ]},
        {"type": "heading", "level": 3, "content": "Тестирование слоя данных"},
        {"type": "text", "content": (
            "Тесты для слоя данных критически важны — ошибки здесь стоят дорого."
        )},
        {"type": "list", "ordered": False, "items": [
            "Unit-тесты: мокаем БД/файлы, тестируем логику преобразования.",
            "Интеграционные тесты: реальная БД (testcontainers), тестовые фикстуры.",
            "Property-based testing (hypothesis): генерация случайных валидных данных.",
            "Контракт-тесты: проверка схемы API/БД совпадает с ожиданиями."
        ]},
        {"type": "heading", "level": 2, "content": "Типичные ошибки"},
        {
            "type": "table",
            "headers": ["Ошибка", "Что происходит", "Как правильно"],
            "rows": [
                [
                    "json.load() вместо json.loads() для строки",
                    "TypeError: ожидается файловый объект.",
                    "json.loads() для строки, json.load() для файла.",
                ],
                [
                    "CSV без newline=''",
                    "На Windows лишние пустые строки между записями.",
                    "Всегда open(..., newline='').",
                ],
                [
                    "SQL-инъекция через f-строку",
                    "Полный контроль над БД атакующего.",
                    "Только плейсхолдеры ? или :name.",
                ],
                [
                    "pickle.load() с недоверенных данных",
                    "Выполнение произвольного кода (RCE).",
                    "Только JSON/msgpack/orjson для внешних данных.",
                ],
                [
                    "pandas: цепочечное присвоение df[df['a']>0]['b'] = 1",
                    "SettingWithCopyWarning, изменения теряются.",
                    "df.loc[df['a']>0, 'b'] = 1.",
                ],
                [
                    "yaml.load() без safe_load",
                    "RCE через !!python/object.",
                    "Всегда yaml.safe_load().",
                ],
            ],
        },
        {"type": "heading", "level": 2, "content": "Практика"},
        {
            "type": "text",
            "content": (
                "Выполните задания по порядку. Используйте временные файлы "
                "или папку tempfile для изоляции."
            ),
        },
        {
            "type": "list",
            "ordered": True,
            "items": [
                "Напишите скрипт, который читает users.csv, фильтрует пользователей старше 30 лет и сохраняет результат в filtered.json.",
                "Создайте SQLite БД с таблицей products (id, name, price, category). Напишите функцию добавления товара и выборки по категории через SQLAlchemy ORM.",
                "Напишите асинхронную функцию, которая читает большой CSV чанками (chunksize=1000) через pandas и считает сумму колонки amount.",
                "Сравните скорость сериализации словаря 10000 элементов: json, orjson, msgpack, pickle. Выведите время в миллисекундах.",
                "Прочитайте config.yaml с настройками БД, создайте SQLAlchemy engine и проверьте соединение SELECT 1.",
            ],
        },
        {
            "type": "callout",
            "style": "success",
            "title": "Подсказка к заданию 4",
            "content": (
                "Используйте time.perf_counter() для измерения. Запускайте "
                "каждый сериализатор несколько раз и берите медиану. "
                "pickle protocol=5 будет быстрее JSON, orjson — быстрее всего."
            ),
        },
        {"type": "heading", "level": 2, "content": "Проверьте себя"},
        {
            "type": "list",
            "ordered": True,
            "items": [
                "Чем json.dump отличается от json.dumps?",
                "Почему в CSV writer.writerow принимает список, а DictWriter — словарь?",
                "Чем SQLAlchemy ORM отличается от Core?",
                "Почему pickle опасен для десериализации чужого данных?",
                "В чём разница между df.loc и df.iloc в pandas?",
            ],
        },
        {"type": "heading", "level": 3, "content": "Ответы"},
        {
            "type": "list",
            "ordered": True,
            "items": [
                "dump пишет в файловый объект, dumps возвращает строку. load читает из файла, loads — из строки.",
                "writer работает с последовательностями (списками/кортежами), DictWriter — с отображениями (словарями), требуя fieldnames.",
                "Core — SQL-выражения на Python (ближе к SQL). ORM — отображение таблиц в классы, работа с объектами.",
                "pickle.load может выполнить произвольный код через __reduce__. Для обмена используйте JSON/msgpack.",
                "loc — по меткам (имени строки/колонки), iloc — по целочисленным позициям. loc включает конечные границы среза, iloc — нет.",
            ],
        },
        {"type": "heading", "level": 2, "content": "Итоги"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "JSON — универсальный формат обмена, ensure_ascii=False для кириллицы, orjson для скорости.",
                "CSV — просто таблицы, csv модуль для простых задач, pandas — для анализа.",
                "YAML/TOML — конфигурация, safe_load для YAML, tomllib (3.11+) для TOML.",
                "SQLite + sqlite3 для простых задач, SQLAlchemy ORM для сложных моделей.",
                "Асинхронные БД: aiosqlite, asyncpg, SQLAlchemy async.",
                "Сериализация: pickle только для доверенных данных, JSON/msgpack/orjson для обмена.",
                "pandas DataFrame — мощный инструмент анализв: чтение, фильтрация, группировка, join.",
            ],
        },
        {"type": "heading", "level": 2, "content": "Что дальше"},
        {
            "type": "text",
            "content": (
                "Работа с данными — основа бэкенда. Следующий урок про "
                "веб-разработку: FastAPI, маршрутизация, валидация через "
                "Pydantic, зависимость, тестирование. Асинхронная БД и "
                "сериализация напрямую пригодятся там."
            ),
        },
        {"type": "heading", "level": 2, "content": "Если хотите углубиться"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "SQLAlchemy 2.0 tutorial: docs.sqlalchemy.org/en/20/tutorial/",
                "pandas documentation: pandas.pydata.org/docs/",
                "orjson GitHub: github.com/ijl/orjson",
                "msgpack specification: github.com/msgpack/msgpack",
                "PEP 3118 — буферный протокол для сериализации.",
            ],
        },
    ],
}