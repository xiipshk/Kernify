"""Урок 3.10 курса Python: экосистема и инструменты."""

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
    "topic_order": 10,
    "name": "3.10. Экосистема и инструменты",
    "slug": "python-3-10-экосистема-и-инструменты",
    "short_description": (
        "Обзор экосистемы Python: веб-фреймворки (Django, Flask, FastAPI), "
        "CLI-инструменты, Data Science стек, базы данных (SQL/NoSQL), "
        "мониторинг, выбор инструментов для задач."
    ),
    "topic_name": "Экосистема и инструменты",
    "topic_description": (
        "Навигация по экосистеме Python: веб-фреймворки (Django, Flask, FastAPI), "
        "CLI-инструменты (click, typer, rich), Data Science стек (NumPy, pandas, polars, "
        "scikit-learn, PyTorch), базы данных (SQLAlchemy, Redis, MongoDB, DuckDB), "
        "мониторинг (OpenTelemetry, Prometheus), выбор инструментов под задачи."
    ),
    "learning_objectives": [
        "Ориентироваться в веб-фреймворках: Django, Flask, FastAPI, Starlette — когда что применять",
        "Создавать CLI-приложения: click, typer, rich, tqdm, watchdog, apscheduler",
        "Ориентироваться в Data Science стеке: NumPy, pandas, polars, scikit-learn, PyTorch, TensorFlow, JAX",
        "Работать с базами данных: SQLAlchemy 2.0 (sync/async), Alembic миграции, Redis, MongoDB, DuckDB, ClickHouse",
        "Выбирать правильный инструмент для задачи: чек-лист решений, матрица решений",
        "Настраивать наблюдаемость: OpenTelemetry (метрики, логи, трейсинг), Prometheus, Grafana, Jaeger, Sentry",
        "Избегать типичных ошибок при выборе инструментов",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "python",
        "экосистема",
        "веб-фреймворки",
        "django",
        "flask",
        "fastapi",
        "cli",
        "data science",
        "базы данных",
        "мониторинг",
    ],
    "starter_code": code(
        """
        # FastAPI — современный выбор для API
        from fastapi import FastAPI
        from pydantic import BaseModel

        app = FastAPI()

        class Item(BaseModel):
            name: str
            price: float

        @app.post("/items")
        async def create_item(item: Item):
            return {"id": 42, **item.model_dump()}
        """
    ),
    "hints": [
        "Django — для полноценных приложений с админкой, FastAPI — для высоконагруженных API, Flask — для простых сервисов.",
        "pandas для анализа, polars — для больших данных и скорости, DuckDB — для аналитики на месте.",
        "SQLAlchemy 2.0 поддерживает async нативно. Alembic для миграций.",
        "OpenTelemetry — стандарт observability. Инструментируйте один раз, отправляйте куда угодно.",
    ],
    "content": [
        text(
            "Python силен не языком, а экосистемой. На PyPI более 500 тысяч пакетов — "
            "для любой задачи есть библиотека. Но изобилие создаёт проблему выбора: "
            "Django или FastAPI? pandas или polars? SQLAlchemy или Tortoise? "
            "Prometheus или Datadog? В этом уроке разберём основные домены экосистемы, "
            "популярные инструменты, критерии выбора и типичные ошибки, чтобы вы могли "
            "быстро принимать обоснованные архитектурные решения.\n\n"
            "Экосистема Python уникальна: стандартная библиотека покрывает 80% повседневных задач "
            "(файлы, сеть, JSON, CSV, сжатие, криптография, асинхронность), а PyPI добавляет "
            "специализированные инструменты для любого домена. Главный навык — не знать все "
            "пакеты наизусть, а уметь быстро оценивать: качество поддержки, лицензия, "
            "активность разработки, совместимость с Python версией, производительность, "
            "размер сообщества. В этом уроке мы не просто перечислим инструменты, а дадим "
            "рамки для принятия решений."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "различать веб-фреймворки: Django (batteries-included), Flask (микро), FastAPI (async, OpenAPI), Starlette (низкий уровень);",
            "создавать CLI: click/typer (декларативные), rich (красивый вывод), tqdm (прогресс), apscheduler (расписание);",
            "ориентироваться в Data Science: NumPy/pandas (база), polars (скорость), scikit-learn (классика ML), PyTorch/TensorFlow/JAX (Deep Learning);",
            "работать с БД: SQLAlchemy 2.0 (sync/async + Alembic), Redis/Redis-py, MongoDB/motor, DuckDB/ClickHouse для аналитики;",
            "применять чек-лист выбора инструментов под тип проекта, нагрузку, команду, сроки;",
            "настраивать наблюдаемость: OpenTelemetry (tracing/metrics/logs), Prometheus/Grafana, Jaeger, Sentry;",
            "избегать типичных ошибок: Django для простого API, pandas для big data, сырые SQL, отсутствие connection pooling.",
        ),
        heading("Веб-разработка"),
        heading("Синхронные фреймворки", 3),
        table(
            ["Фреймворк", "Особенности", "Когда использовать"],
            [
                ["Django", "batteries-included: ORM, админка, auth, миграции, шаблоны, безопасность", "Полноценные приложения, CRM, CMS, e-commerce, быстрый старт, монолит"],
                ["Flask", "Микрофреймворк, расширяемость через extensions, простота, гибкость", "Малые/средние API, микросервисы, прототипы, когда нужен контроль"],
                ["FastAPI", "Async нативно, автодокументация OpenAPI/Swagger, Pydantic-валидация, высокая производительность", "Современные REST/gRPC API, высокая нагрузка, микросервисы, ML serving"],
                ["Starlette", "Низкоуровневый ASGI toolkit, основа FastAPI, минимализм", "Когда нужен полный контроль над ASGI приложением, кастомные middleware"],
            ],
        ),
        text(
            "Выбор фреймворка:\n"
            "- **Django** — если нужен монолит с админкой, auth, ORM, миграциями, шаблонами из коробки. Идеален для CRM, CMS, e-commerce, внутренние инструменты. Django 4.1+ поддерживает async views.\n"
            "- **Flask** — если нужен минимализм, гибкость, прототипирование. Расширяется через extensions (Flask-SQLAlchemy, Flask-Login, Flask-Migrate). Подходит для микросервисов.\n"
            "- **FastAPI** — современный стандарт для API. Async нативно, автогенерация OpenAPI/Swagger, валидация через Pydantic, dependency injection. На Uvicorn/Gunicorn даёт высокую производительность. Идеален для ML serving, высоконагруженные API, микросервисы.\n"
            "- **Starlette** — если нужен полный контроль над ASGI, кастомные routing/middleware, легковесность. Основа FastAPI."
        ),
        heading("Асинхронные (ASGI)", 3),
        example(
            "python",
            """
            # FastAPI пример
            from fastapi import FastAPI, Depends, HTTPException
            from pydantic import BaseModel
            from typing import Annotated

            app = FastAPI(title="My API")

            class Item(BaseModel):
                name: str
                price: float
                in_stock: bool = True

            @app.post("/items")
            async def create_item(item: Item):
                return {"id": 42, **item.model_dump()}

            # Запуск: uvicorn main:app --reload
            """,
        ),
        text(
            "ASGI (Asynchronous Server Gateway Interface) — стандарт для async Python веб. "
            "Uvicorn — быстрый ASGI сервер (на uvloop + httptools). "
            "Gunicorn + Uvicorn workers — production deployment pattern:\n"
            "`gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`.\n"
            "FastAPI автоматически генерирует OpenAPI схему: `/docs` (Swagger UI), `/redoc` (ReDoc). "
            "Dependency Injection через `Depends()` — мощный паттерн для БД сессий, авторизации, кэша.\n\n"
            "FastAPI advanced features:\n"
            "- BackgroundTasks — фоновые задачи после ответа клиенту (email, логи, вебхуки).\n"
            "- WebSocket поддержка: `@app.websocket('/ws')` + `await websocket.accept()`.\n"
            "- File upload: `File`, `UploadFile` с streaming, валидация размера/типа.\n"
            "- OAuth2 + JWT: `OAuth2PasswordBearer`, `Security`, scopes/permissions.\n"
            "- Testing: `TestClient` (sync) + `AsyncClient` (httpx) для async тестов.\n"
            "- Lifespan events: `@app.on_event('startup')` / `@app.on_event('shutdown')` для пулов БД, кэша.\n"
            "- Middleware: CORS, GZip, TrustedHost, Custom (request/response processing).\n"
            "- OpenAPI customization: `openapi_tags`, `openapi_url`, `docs_url`, custom `openapi()` method."
        ),
        heading("Деплой веб-приложений", 3),
        table(
            ["Инструмент", "Назначение"],
            [
                ["Gunicorn + Uvicorn workers", "Production ASGI сервер (multi-process)"],
                ["Nginx", "Reverse proxy, статика, SSL termination, rate limiting, gzip"],
                ["Docker", "Контейнеризация, воспроизводимые билды, multi-stage builds"],
                ["Kubernetes / ECS / Fly.io / Railway / Render", "Оркестрация, автоскейлинг, rolling updates"],
                ["Traefik / Caddy", "Автоматический HTTPS (Let's Encrypt), reverse proxy с авто-дисквери"],
            ],
        ),
        text(
            "Production чек-лист:\n"
            "- Nginx перед Gunicorn: SSL termination, статика, rate limiting, buffer overflow защита.\n"
            "- Gunicorn workers: `(2 * CPU) + 1` для sync, `CPU` для async (UvicornWorker).\n"
            "- Health checks: `/health` (liveness), `/ready` (readiness) для K8s.\n"
            "- Graceful shutdown: обрабатывать SIGTERM, завершать запросы, закрывать пулы БД.\n"
            "- Логи в stdout/stderr (JSON), собираются sidecar'ом (Promtail/Fluent Bit)."
        ),
        heading("Автоматизация и скриптинг"),
        heading("CLI-инструменты", 3),
        example(
            "python",
            """
            # click — декларативные CLI
            import click

            @click.group()
            def cli(): pass

            @cli.command()
            @click.argument("name")
            @click.option("--count", "-c", default=1)
            def greet(name, count):
                for _ in range(count):
                    click.echo(f"Hello, {name}!")

            if __name__ == "__main__":
                cli()
            """,
        ),
        table(
            ["Библиотека", "Назначение"],
            [
                ["click / typer", "Создание CLI (typer = click + type hints, FastAPI-стиль)"],
                ["rich", "Красивый вывод: таблицы, прогресс-бары, синтаксис, логи, трейсбэки"],
                ["tqdm", "Прогресс-бары для циклов (tqdm.auto для notebooks)"],
                ["watchdog", "Мониторинг файловой системы (события создания/изменения/удаления)"],
                ["schedule / apscheduler", "Планировщик задач (cron-like, interval, one-off)"],
                ["fabric / invoke", "Удалённое выполнение команд по SSH"],
                ["typer", "FastAPI-стиль CLI на базе click + type hints"],
            ],
        ),
        heading("Системная автоматизация", 3),
        example(
            "python",
            """
            # pathlib + subprocess — современная замена bash-скриптам
            from pathlib import Path
            import subprocess
            import shutil

            def backup_project(src: Path, dst: Path):
                dst.mkdir(parents=True, exist_ok=True)
                for file in src.rglob("*.py"):
                    rel = file.relative_to(src)
                    target = dst / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, target)
                result = subprocess.run(
                    ["tar", "-czf", "backup.tar.gz", "-C", str(dst), "."],
                    capture_output=True, text=True
                )
                result.check_returncode()
                print(f"Backup created: {result.stdout}")
            """,
        ),
        text(
            "`pathlib.Path` — объектно-ориентированные пути (вместо os.path). "
            "`subprocess.run()` с `capture_output=True, text=True` — безопасный запуск команд. "
            "`check_returncode()` выбрасывает исключение при ошибке. "
            "Для сложных задач: `invoke` / `fabric` (SSH), `ansible` (инфраструктура), `just` (command runner)."
        ),
        heading("Научные вычисления и Data Science"),
        heading("Стек Data Science", 3),
        table(
            ["Библиотека", "Назначение"],
            [
                ["NumPy", "N-мерные массивы, линейная алгебра, случайные числа, база для всего стека"],
                ["pandas", "DataFrame, манипуляции табличными данными, I/O (CSV, Parquet, Excel, SQL)"],
                ["polars", "Быстрый DataFrame (на Rust), ленивые вычисления, streaming, альтернатива pandas"],
                ["matplotlib / seaborn", "Базовое/статистическое визуализирование (публикационное качество)"],
                ["plotly / altair", "Интерактивные графики (zoom, hover, dashboards)"],
                ["scikit-learn", "Классическая ML: классификация, регрессия, кластеринг, preprocessing, CV"],
                ["scipy", "Научные алгоритмы: оптимизация, статистика, сигналы, спец. функции"],
                ["statsmodels", "Статистическое моделирование, эконометрика, тесты гипотез"],
                ["polars", "DataFrame на Rust, multi-threaded, lazy evaluation, out-of-core"],
                ["DuckDB", "Встраиваемая OLAP БД, SQL на Parquet/CSV, встраивается в Python"],
            ],
        ),
        text(
            "Когда что использовать:\n"
            "- **pandas** — стандарт для EDA, манипуляции, малые/средние данные (<10GB RAM).\n"
            "- **polars** — быстрее pandas (multi-threaded, Rust), lazy evaluation, streaming, out-of-core. Для больших данных, pipelines.\n"
            "- **DuckDB** — встраиваемая OLAP БД, SQL над Parquet/CSV/JSON, колончатый формат, векторное выполнение. Для аналитики без сервера.\n"
            "- **Dask / Ray** — распределённые вычисления, scaling pandas/sklearn на кластер.\n"
            "- **Ray** — unified compute: data, train, serve, tune. Для ML at scale."
        ),
        heading("Пример пайплайна", 3),
        example(
            "python",
            """
            import pandas as pd
            import numpy as np
            from sklearn.model_selection import train_test_split
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.metrics import classification_report

            df = pd.read_parquet("data.parquet")
            X = df.drop("target", axis=1)
            y = df["target"]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            model = RandomForestClassifier(n_estimators=200, n_jobs=-1)
            model.fit(X_train, y_train)

            print(classification_report(y_test, model.predict(X_test)))
            """,
        ),
        heading("Глубокое обучение", 3),
        table(
            ["Фреймворк", "Особенности"],
            [
                ["PyTorch", "Динамический граф, research-friendly, огромная экосистема (Lightning, HF Transformers, TIMM)"],
                ["TensorFlow / Keras", "Статический граф (TF2 eager), production-ready, TFX, TFLite, TF.js, широкая индустрия"],
                ["JAX", "Функциональный, автодифф, JIT компиляция (XLA), для research/HPC, Flax/Haiku для NN"],
            ],
        ),
        text(
            "Выбор DL фреймворка:\n"
            "- **PyTorch** — доминирует в research, динамический граф удобен для отладки, "
            "экосистема: Lightning (training loop), HuggingFace Transformers (NLP), TIMM (CV), "
            "torchcompile (PyTorch 2.0+ JIT).\n"
            "- **TensorFlow/Keras** — strong в production (TFX pipeline, TFLite mobile, TF.js web, TF Serving). "
            "Keras — высокоуровневый API. Статический граф сложнее для отладки.\n"
            "- **JAX** — функциональный подход, автодифф + JIT (XLA), single-source для CPU/GPU/TPU. "
            "Flax/Haiku для NN. Сложнее для новичков, мощнее для HPC.\n\n"
            "Для production serving: ONNX export → TensorRT / Triton Inference Server / BentoML."
        ),
        heading("Работа с базами данных"),
        heading("ORM", 3),
        table(
            ["ORM", "Синхронность", "Особенности"],
            [
                ["SQLAlchemy 2.0", "Sync + Async", "Mature, гибкий, Core + ORM, миграции (Alembic), типизация Mapped"],
                ["Tortoise ORM", "Async-only", "Django-like API, быстрый для async, Pydantic интеграция"],
                ["Prisma (Python client)", "Sync + Async", "Type-safe, генерация клиента из схемы Prisma"],
                ["Django ORM", "Sync (async в 4.1+)", "Встроен в Django, мощный QuerySet, миграции встроены"],
            ],
        ),
        example(
            "python",
            """
            # SQLAlchemy 2.0 async
            from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
            from sqlalchemy import String, select

            class Base(DeclarativeBase): pass

            class User(Base):
                __tablename__ = "users"
                id: Mapped[int] = mapped_column(primary_key=True)
                email: Mapped[str] = mapped_column(String(255), unique=True)

            engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

            async def get_user(email: str) -> User | None:
                async with AsyncSession(engine) as session:
                    return await session.scalar(select(User).where(User.email == email))
            """,
        ),
        text(
            "SQLAlchemy 2.0 — golden standard для Python БД:\n"
            "- `Mapped` + `mapped_column` — типизация полей, автогенерация `__init__`.\n"
            "- `AsyncSession` + `async with` — правильное управление транзакциями.\n"
            "- `select()` / `insert()` / `update()` / `delete()` — unified API.\n"
            "- Connection pooling: `pool_size=10, max_overflow=20, pool_pre_ping=True`.\n"
            "- `pool_pre_ping=True` — проверка соединения перед использованием (защита от stale connections)."
        ),
        heading("Миграции", 3),
        example(
            "bash",
            """
            # Alembic (для SQLAlchemy)
            pip install alembic
            alembic init migrations
            # редактируйте env.py (target_metadata = Base.metadata), затем:
            alembic revision --autogenerate -m "create users table"
            alembic upgrade head
            # откат: alembic downgrade -1
            """,
        ),
        text(
            "Alembic — стандарт миграций для SQLAlchemy:\n"
            "- `alembic revision --autogenerate` — автогенерация из изменений моделей.\n"
            "- Всегда проверяйте сгенерированный скрипт перед `upgrade`.\n"
            "- `alembic history` — история, `alembic current` — текущая ревизия.\n"
            "- Для production: `alembic upgrade head` в CI/CD перед деплоем приложения."
        ),
        heading("NoSQL / Специализированные БД", 3),
        table(
            ["База", "Клиент", "Кейс"],
            [
                ["Redis", "redis-py (async: redis.asyncio)", "Кэш, сессии, очереди (RQ, Celery), rate limit, pub/sub, sorted sets"],
                ["MongoDB", "motor (async), pymongo", "Документы, гибкая схема, агрегации, гео, TTL indexes"],
                ["Elasticsearch", "elasticsearch-py (async)", "Полнотекстовый поиск, логи, метрики, APM, security analytics"],
                ["ClickHouse", "clickhouse-connect (sync), clickhouse-driver", "OLAP, аналитика, wide tables, колоночное сжатие, materialized views"],
                ["DuckDB", "duckdb (встроенный)", "Встраиваемая аналитика, SQL на Parquet/CSV/JSON, out-of-core, векторное выполнение"],
                ["TimescaleDB", "psycopg2/asyncpg", "Time-series на PostgreSQL, hypertables, continuous aggregates"],
                ["Redis Stack / Redisearch", "redis-py", "Full-text search, vector similarity (RAG), JSON, probabilistic data structures"],
            ],
        ),
        text(
            "Redis — must-have для любого продакшена:\n"
            "- Кэш: `redis.setex(key, ttl, value)`, `redis.get(key)`.\n"
            "- Сессии: `session:{id}` с TTL, сериализация в JSON/msgpack.\n"
            "- Rate limiting: `INCR` + `EXPIRE` / sliding window (sorted sets).\n"
            "- Очереди: `LPUSH`/`BRPOP` (RQ, Celery broker).\n"
            "- Pub/Sub: real-time уведомления. Streams — persistent logs с consumer groups.\n\n"
            "DuckDB — game changer для аналитики: `duckdb.sql('SELECT * FROM read_parquet(\"s3://bucket/data/*.parquet\") WHERE year=2024')`. "
            "Нет сервера, встраивается в процесс, векторное выполнение, out-of-core."
        ),
        heading("Выбор инструментов: чек-лист решения"),
        heading("Для нового проекта — вопросы", 3),
        numbered(
            "Тип приложения: REST API / GraphQL / gRPC / CLI / Web UI / Data pipeline / ML model serving / Real-time (WebSocket)?",
            "Нагрузка: ожидаемые RPS, latency requirements (p50/p95/p99), необходима ли асинхронность?",
            "Команда: опыт с async/await, типизацией (mypy), конкретными фреймворками, DevOps?",
            "Сроки: нужен ли быстрый старт (Django, batteries-included) или гибкость/производительность (FastAPI)?",
            "Деплой: контейнеры (Docker/K8s), serverless (Lambda/Cloud Run), VM, managed services (RDS, ElastiCache)?",
            "Данные: реляционные (PostgreSQL) vs документы (MongoDB) vs аналитика (ClickHouse/DuckDB) vs time-series (TimescaleDB)?",
            "Наблюдаемость: нужен ли полный observability stack (OTel, Prometheus, Grafana, Jaeger, Loki, Sentry)?",
        ),
        heading("Декларативный выбор (пример)", 3),
        example(
            "python",
            """
            DECISION_MATRIX = {
                "fullstack_monolith": "Django + HTMX/Alpine.js + PostgreSQL",
                "rest_api_high_perf": "FastAPI + SQLAlchemy async + PostgreSQL + Redis",
                "microservice": "FastAPI / Starlette + Pydantic + SQLAlchemy async",
                "data_pipeline": "polars + DuckDB + Airflow/Prefect/Dagster",
                "ml_serving": "FastAPI + ONNX/TensorRT + Triton / BentoML / vLLM",
                "cli_tool": "typer + rich + click",
                "realtime_ws": "FastAPI WebSocket / socket.io (python-socketio) + Redis pub/sub",
                "graphql": "Strawberry (FastAPI integration) / Ariadne + DataLoaders",
                "event_driven": "FastAPI + Kafka (aiokafka) / RabbitMQ (aio-pika) + Outbox pattern",
                "etl": "polars + DuckDB + dbt / Airflow / Dagster",
            }
            """,
        ),
        text(
            "Используйте матрицу как отправную точку. Каждый проект уникален — адаптируйте под контекст. "
            "Избегайте over-engineering: начните проще (Django/FastAPI + PostgreSQL), "
            "сложность добавляйте по мере роста требований (кэш, очереди, микросервисы, отдельные БД)."
        ),
        heading("Мониторинг и observability", 3),
        table(
            ["Категория", "Инструменты"],
            [
                ["Метрики", "Prometheus client, OpenTelemetry metrics, Datadog, Grafana Cloud"],
                ["Логи", "structlog + Loki/ELK/Datadog, JSON formatter, correlation IDs"],
                ["Трейсинг", "OpenTelemetry + Jaeger/Zipkin/Tempo, baggage propagation"],
                ["Профилирование", "py-spy (sampling), scalene (CPU+GPU+mem), pyinstrument (call graph)"],
                ["Ошибки", "Sentry, Rollbar, Honeybadger, GlitchTip (self-hosted Sentry)"],
                ["Алерты", "Prometheus Alertmanager, Grafana Alerting, PagerDuty, Opsgenie, Opsgenie"],
            ],
        ),
        example(
            "python",
            """
            # OpenTelemetry минимальный сетап
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

            trace.set_tracer_provider(TracerProvider())
            tracer = trace.get_tracer(__name__)

            otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
            trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

            # Автоинструментация
            FastAPIInstrumentor.instrument_app(app)
            SQLAlchemyInstrumentor().instrument(engine=engine)

            # Ручные спаны
            with tracer.start_as_current_span("db_query") as span:
                span.set_attribute("db.statement", "SELECT * FROM users")
                result = await db.execute(...)
            """,
        ),
        text(
            "OpenTelemetry — стандарт observability:\n"
            "- **Traces** — распределённые трассировки (request flow через сервисы).\n"
            "- **Metrics** — счетчики, гистограммы, gauges (Prometheus format).\n"
            "- **Logs** — корреляция через trace_id/span_id.\n"
            "- **Baggage** — передача контекста между сервисами.\n\n"
            "Автоинструментация: `FastAPIInstrumentor`, `SQLAlchemyInstrumentor`, "
            "`HTTPXClientInstrumentor`, `RedisInstrumentor`, `Psycopg2Instrumentor`. "
            "Экспорт: OTLP (gRPC/HTTP) → Jaeger / Tempo / Zipkin / Datadog / Grafana Cloud. "
            "Baggage propagation: W3C TraceContext headers."
        ),
        heading("Типичные ошибки", 2),
        table(
            ["Ошибка", "Последствия", "Как правильно"],
            [
                ["Django для простого REST API", "Overhead, лишняя сложность, медленнее", "FastAPI / Flask для API"],
                ["pandas для стриминга/big data", "OOM, медленно, нет стриминга", "polars / DuckDB / Dask / Ray / streaming"],
                ["Сырые SQL строки в коде", "SQL Injection, сложно поддерживать", "SQLAlchemy ORM / Core + параметризованные запросы"],
                ["Отсутствие connection pooling", "Превышение лимитов БД, медленно", "`pool_size`, `max_overflow`, `pool_pre_ping=True`"],
                ["Синхронные вызовы в async коде", "Блокировка event loop, падение производительности", "`run_in_threadpool` / асинхронные драйверы (asyncpg, aioredis, motor)"],
                ["Непиннутые зависимости в проде", "Сломанные билды, supply chain attacks", "`pip-tools` / `uv lock` / lockfile в репо (`requirements.txt` закоммичен)"],
                ["pandas для OLAP аналитики", "Медленно, много памяти", "DuckDB / ClickHouse / Polars для аналитики"],
                ["Отсутствие health checks", "K8s не знает, жив ли под", "/health (liveness) + /ready (readiness)"],
            ],
        ),
        heading("Практика", 2),
        text(
            "Выполните задания по порядку. Используйте Docker для PostgreSQL/Redis при необходимости."
        ),
        numbered(
            "Веб: создайте FastAPI CRUD API с PostgreSQL (SQLAlchemy async + Alembic миграции). Эндпоинты: POST/GET/PUT/DELETE /items. Добавьте Pydantic модели запроса/ответа.",
            "CLI: напишите `typer` приложение для бэкапа папки с прогресс-баром (`rich.progress.Progress`), логированием через `rich.logging.RichHandler`.",
            "Данные: загрузите датасет (Kaggle/UCI — California Housing / Wine Quality / Titanic), сделайте EDA в pandas/polars, обучите baseline модель (sklearn), залогируйте в MLflow.",
            "БД: настройте Redis для кэширования (TTL 5 мин) + rate limiting (10 req/min на IP) в FastAPI через middleware. Проверьте: `curl` превышает лимит → 429.",
            "Наблюдаемость: добавьте OpenTelemetry трейсинг в существующий FastAPI проект, отправьте в Jaeger (all-in-one Docker). Проверьте: запрос → трейс в Jaeger с DB spans.",
        ),
        text("Пример ожидаемого результата для первого задания (структура):"),
        example(
            "text",
            "fastapi-crud/\n"
            "├── app/\n"
            "│   ├── main.py          # FastAPI app\n"
            "│   ├── models.py        # SQLAlchemy models\n"
            "│   ├── schemas.py       # Pydantic schemas\n"
            "│   ├── database.py      # engine, session\n"
            "│   └── crud.py          # DB operations\n"
            "├── migrations/          # Alembic\n"
            "├── tests/\n"
            "├── Dockerfile\n"
            "├── docker-compose.yml\n"
            "├── pyproject.toml\n"
            "└── README.md",
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "Typer: `@app.command()` для команд, `@click.option` для опций. Rich: `Progress()` контекстный менеджер, `track()` для итераторов. `RichHandler` для красивых логов с tracebacks. `typer.run(main)` в `__main__`.",
        ),
        heading("Проверьте себя", 2),
        numbered(
            "Когда выбирать Django, а когда FastAPI?",
            "В чём преимущество polars над pandas?",
            "Зачем нужен connection pooling в SQLAlchemy?",
            "Когда использовать DuckDB вместо PostgreSQL?",
            "Какие три столпа observability (Three Pillars)?",
            "Зачем нужен OpenTelemetry, если есть Prometheus?",
            "В чём разница между sync и async SQLAlchemy?",
        ),
        heading("Ответы", 2),
        numbered(
            "Django — для полноценных приложений с админкой, auth, ORM из коробки (CRM, CMS). FastAPI — для высоконагруженных REST/gRPC API, микросервисов, ML serving, где важны async и производительность.",
            "Polars: multi-threaded (Rust), lazy evaluation, streaming/out-of-core, быстрее в 2-10x на больших данных, строгая типизация схем. Pandas — удобнее для EDA, мелких данных, богатая экосистема.",
            "Connection pooling переиспользует соединения к БД, избегая накладных расходов на handshake. `pool_size` — постоянные соединения, `max_overflow` — доп. при пиках. `pool_pre_ping=True` проверяет живые соединения.",
            "DuckDB — встраиваемая OLAP БД, SQL над Parquet/CSV/JSON, колончатое хранение, векторное выполнение, out-of-core. Для аналитики, ETL, ad-hoc запросов без сервера. PostgreSQL — для OLTP, транзакции, конкурентность.",
            "Metrics (метрики), Logs (логи), Traces (трейсы). Metrics — агрегаты (RPS, latency p95). Logs — события с контекстом. Traces — request flow через сервисы с таймингами.",
            "Prometheus — метрики (pull model). OpenTelemetry — унифицированный сбор traces/metrics/logs, vendor-neutral, автоинструментация, экспорт куда угодно (Jaeger, Tempo, Datadog, Grafana). OTel собирает, Prometheus хранит/алертит.",
            "Sync: блокирующие вызовы, проще для простых скриптов. Async: неблокирующие, выше concurrency, нужно везде (драйверы, БД, HTTP клиенты). Asyncpg/asyncpg + SQLAlchemy async даёт 2-5x throughput на I/O bound нагрузках.",
        ),
        heading("Итоги", 2),
        bullets(
            "Веб: Django (монолит, админка), Flask (простые сервисы), FastAPI (современные API, async, OpenAPI), Starlette (ASGI toolkit). Деплой: Gunicorn+Uvicorn+Nginx, Docker, K8s.",
            "CLI: click/typer (декларативные), rich (красивый вывод, прогресс-бары), tqdm (progress bars), apscheduler (расписание), fabric/invoke (SSH). pathlib + subprocess вместо bash.",
            "Data Science: NumPy (база), pandas (EDA, манипуляции), polars (скорость, big data), scikit-learn (классика ML), PyTorch/TensorFlow/JAX (Deep Learning), DuckDB (OLAP встраиваемая).",
            "БД: SQLAlchemy 2.0 (sync/async, Mapped, Alembic), Redis (кэш/сессии/очереди/rate limit), MongoDB (motor), Elasticsearch (поиск), ClickHouse/DuckDB (OLAP), TimescaleDB (time-series).",
            "Выбор инструментов: чек-лист (тип приложения, нагрузка, команда, сроки, деплой, данные, observability). Матрица решений как отправная точка. Начинайте проще, добавляйте сложность по мере роста.",
            "Observability: Three Pillars (Metrics/Logs/Traces). OpenTelemetry — стандарт сбора (автоинструментация + ручные спаны). Экспорт OTLP → Jaeger/Tempo/Zipkin (traces), Prometheus (metrics), Loki (logs). Sentry для ошибок. Алерты → Alertmanager/PagerDuty.",
            "Ошибки: Django для API, pandas для big data, сырые SQL, нет pooling, sync в async, непиннутые депы, нет health checks. Исправления: FastAPI, polars/DuckDB, SQLAlchemy+params, pool_pre_ping, async драйверы, pip-tools/uv lock, /health+/ready.",
        ),
        heading("Что дальше", 2),
        text(
            "Экосистема Python огромна и постоянно развивается. В следующем (финальном) уроке курса "
            "соберём всё вместе: пройдём полный цикл создания профессионального проекта — "
            "от идеи через проектирование, разработку, тестирование, CI/CD, деплой до мониторинга "
            "и поддержки. Это будет капистанный проект, демонстрирующий все навыки трех уровней."
        ),
        heading("Если хотите углубиться", 2),
        bullets(
            "Awesome Python — github.com/vinta/awesome-python (курируемый список библиотек по категориям)",
            "Python Package Index Trends — pypistats.org/ (статистика загрузок, тренды)",
            "Django vs FastAPI vs Flask — testdriven.io/blog/fastapi-vs-flask-vs-django/",
            "SQLAlchemy 2.0 Tutorial — docs.sqlalchemy.org/en/20/tutorial/",
            "Polars User Guide — docs.pola.rs/",
            "OpenTelemetry Python — opentelemetry.io/docs/instrumentation/python/",
            "Awesome Observability — github.com/ziadoz/awesome-observability",
            "System Design Primer — github.com/donnemartin/system-design-primer",
        ),
    ],
}