"""Урок 3.9 курса Python: безопасность и надёжность."""

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
    "topic_order": 9,
    "name": "3.9. Безопасность и надёжность",
    "slug": "python-3-9-безопасность-и-надёжность",
    "short_description": (
        "Валидация данных (Pydantic), управление секретами, безопасная десериализация, "
        "сканирование уязвимостей, структурированное логирование и аудит, OWASP Top 10 для Python."
    ),
    "topic_name": "Безопасность и надёжность",
    "topic_description": (
        "Комплексный подход к безопасности Python-приложений: валидация входящих данных через Pydantic, "
        "безопасное управление секретами (env, Secret Managers), защита от небезопасной десериализации "
        "(pickle, yaml, eval), сканирование зависимостей на уязвимости (pip-audit, safety, Dependabot), "
        "структурированное логирование (structlog), аудит безопасных событий, OWASP Top 10 для Python."
    ),
    "learning_objectives": [
        "Валидировать входящие данные через Pydantic v2: Field, field_validator, model_validator",
        "Интегрировать Pydantic с FastAPI для автоматической валидации запросов",
        "Правильно управлять секретами: pydantic-settings, .env, AWS Secrets Manager, HashiCorp Vault",
        "Генерировать криптографически стойкие секреты через secrets.token_*",
        "Избегать небезопасной десериализации: pickle, yaml.load, eval, exec — только JSON, msgpack, safe YAML",
        "Применять HMAC-подписи если pickle неизбежен для доверенных данных",
        "Сканировать зависимости на уязвимости: pip-audit, safety, GitHub Dependabot, deptry",
        "Настраивать структурированное JSON-логирование: structlog или стандартный logging + JSON formatter",
        "Внедрять аудит безопасных событий: login, password change, permission changes, admin actions",
        "Понимать OWASP Top 10 для Python и применять защиту от каждой уязвимости",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "python",
        "безопасность",
        "pydantic",
        "секреты",
        "десериализация",
        "pip-audit",
        "structlog",
        "аудит",
        "owasp",
    ],
    "starter_code": code(
        """
        # ПЛОХО: секреты в коде
        API_KEY = "sk-1234567890abcdef"
        DATABASE_URL = "postgres://user:pass@localhost/db"

        # ХОРОШО: переменные окружения
        import os
        API_KEY = os.getenv("API_KEY")
        DATABASE_URL = os.getenv("DATABASE_URL")
        """
    ),
    "hints": [
        "Никогда не коммитьте секреты в git. Используйте .env.example для документации.",
        "Pydantic v2: @field_validator для полей, @model_validator(mode='after') для кросс-валидации.",
        "yaml.safe_load() вместо yaml.load(). pickle — только для доверенных данных с HMAC.",
        "structlog + JSONRenderer для продакшн логов. JSONFormatter для стандартного logging.",
    ],
    "content": [
        text(
            "Безопасность — не чек-лист на финале разработки, а архитектурное решение, заложенное "
            "с первого дня. Один упущенный `pickle.loads()` от пользовательских данных — и атакующий "
            "выполняет произвольный код на сервере (RCE). Один закоммиченный `SECRET_KEY` — и вся "
            "инфраструктура скомпрометирована. Недостаточное логирование — и инцидент обнаруживают "
            "неделями позже, когда ущерб необратим.\n\n"
            "В этом уроке пройдём полный цикл: валидация входа (Pydantic), секреты (env, Vault), "
            "безопасная десериализация (нет pickle/yaml.load/eval), сканирование зависимостей "
            "(pip-audit, Dependabot), структурированные логи (structlog), аудит событий, "
            "OWASP Top 10 для Python. Каждый пункт — практический паттерн, который можно внедрить сегодня."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "валидировать входящие данные через Pydantic v2: Field констрейнты, field_validator, model_validator;",
            "интегрировать Pydantic с FastAPI для автоматической валидации запросов и документации OpenAPI;",
            "правильно управлять секретами: pydantic-settings + .env для разработки, Secret Managers (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault) для продакшена;",
            "генерировать криптографически стойкие секреты через secrets.token_urlsafe / token_hex / token_bytes;",
            "избегать небезопасной десериализации: pickle, yaml.load, eval, exec — использовать только JSON, msgpack, yaml.safe_load, tomllib;",
            "при необходимости pickle — подписывать HMAC и проверять подпись перед загрузкой;",
            "сканировать зависимости на уязвимости: pip-audit (официальный PyPA), safety, GitHub Dependabot, deptry;",
            "настраивать структурированное JSON-логирование: structlog (processors, contextvars) или стандартный logging + JSONFormatter;",
            "внедрять аудит безопасных событий: login success/failed, password change, permission changes, admin actions, data export;",
            "понимать OWASP Top 10 для Python и применять защиту от каждой уязвимости.",
        ),
        heading("Валидация входящих данных"),
        text(
            "Никогда не доверяйте входящим данным. Любой ввод — от HTTP запроса, сообщения в очереди, "
            "файла конфига, переменной окружения — должен быть валидирован перед использованием. "
            "Pydantic v2 — стандарт де-факто для валидации данных в Python: быстрый (Rust core), "
            "мощный (Field, validators, computed fields), интегрирован с FastAPI, OpenAPI, SQLAlchemy."
        ),
        heading("Pydantic v2 — стандарт де-факто", 3),
        example(
            "python",
            """
            from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator, model_validator
            from typing import Optional
            from datetime import datetime
            from enum import Enum

            class UserRole(str, Enum):
                ADMIN = "admin"
                USER = "user"
                GUEST = "guest"

            class UserCreate(BaseModel):
                email: EmailStr
                username: str = Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
                password: str = Field(min_length=12, max_length=128)
                full_name: Optional[str] = Field(default=None, max_length=100)
                role: UserRole = UserRole.USER
                birth_date: Optional[datetime] = None

                @field_validator("password")
                @classmethod
                def password_complexity(cls, v: str) -> str:
                    if not any(c.isupper() for c in v):
                        raise ValueError("Пароль должен содержать заглавную букву")
                    if not any(c.islower() for c in v):
                        raise ValueError("Пароль должен содержать строчную букву")
                    if not any(c.isdigit() for c in v):
                        raise ValueError("Пароль должен содержать цифру")
                    if not any(c in "!@#$%^&*" for c in v):
                        raise ValueError("Пароль должен содержать спецсимвол")
                    return v

                @model_validator(mode="after")
                def check_adult(self) -> "UserCreate":
                    if self.birth_date and self.role == UserRole.ADMIN:
                        age = (datetime.now() - self.birth_date).days // 365
                        if age < 18:
                            raise ValueError("Админ должен быть старше 18 лет")
                    return self

            # Использование
            data = {"email": "test@example.com", "username": "john_doe", "password": "SecureP@ss123"}
            user = UserCreate(**data)  # ValidationError при невалидных данных
            """,
        ),
        text(
            "Ключевые возможности Pydantic v2:\n"
            "- `Field(..., min_length=3, max_length=20, pattern=...)` — декларативные констрейнты.\n"
            "- `@field_validator` — валидация отдельного поля (classmethod, получает значение).\n"
            "- `@model_validator(mode='after')` — кросс-валидация всего объекта после валидации полей.\n"
            "- `mode='before'` — валидация до парсинга полей (сырые данные).\n"
            "- `EmailStr`, `HttpUrl`, `IPvAnyAddress`, `UUID`, `SecretStr` — встроенные типы.\n"
            "- `model_config = ConfigDict(strict=True, extra='forbid')` — строгий режим, запрет лишних полей.\n"
            "- `model_dump(mode='json')` — сериализация в JSON-совместимый dict.\n"
            "- `ValidationError` — детальные ошибки с loc, msg, type для каждого поля."
        ),
        heading("Валидация на уровне API (FastAPI)", 3),
        example(
            "python",
            """
            from fastapi import FastAPI, HTTPException, status
            from pydantic import ValidationError

            app = FastAPI()

            @app.post("/users", status_code=status.HTTP_201_CREATED)
            async def create_user(user_data: UserCreate):
                try:
                    user = UserCreate(**user_data.model_dump())
                except ValidationError as e:
                    raise HTTPException(status_code=422, detail=e.errors())
                return await user_service.create(user)
            """,
        ),
        text(
            "FastAPI автоматически валидирует входящий JSON по Pydantic модели параметра функции. "
            "При ошибке возвращает 422 с детальным JSON: `{'loc': ['body', 'password'], 'msg': '...', 'type': 'value_error'}`. "
            "OpenAPI схема генерируется автоматически — Swagger UI (/docs) показывает схемы запроса/ответа."
        ),
        heading("Управление секретами"),
        text(
            "Секреты — API ключи, пароли БД, JWT секреты, токены сторонних сервисов — "
            "никогда не должны попадать в код, git, Docker образы, логи, сообщения об ошибках. "
            "Принцип: код открыт, секреты — нет."
        ),
        heading("НИКОГДА не храните секреты в коде", 3),
        example(
            "python",
            """
            # ПЛОХО — коммитится в git!
            API_KEY = "sk-1234567890abcdef"
            DATABASE_URL = "postgres://user:pass@localhost/db"
            JWT_SECRET = "my-secret-key"
            """,
        ),
        heading("Переменные окружения + .env (только для разработки)", 3),
        example(
            "bash",
            """
            # .env (НЕ коммитить в git! В .gitignore!)
            DATABASE_URL=postgres://user:pass@localhost/db
            API_KEY=sk-1234567890abcdef
            SECRET_KEY=your-secret-key-here
            DEBUG=false
            LOG_LEVEL=INFO
            """,
        ),
        example(
            "python",
            """
            # config.py
            from pydantic_settings import BaseSettings, SettingsConfigDict
            from typing import Optional

            class Settings(BaseSettings):
                model_config = SettingsConfigDict(
                    env_file=".env",
                    env_file_encoding="utf-8",
                    case_sensitive=False,
                    extra="ignore"
                )

                database_url: str
                api_key: str
                secret_key: str
                debug: bool = False
                log_level: str = "INFO"

            settings = Settings()  # читает из env/.env
            """,
        ),
        text(
            "`pydantic-settings` (BaseSettings) — стандарт де-факто: читает из env vars, "
            "поддерживает `.env` файл (для dev), типизирует значения, валидирует. "
            "`extra='ignore'` — игнорирует лишние env vars. `.env` в `.gitignore` обязателен. "
            "Для документации используйте `.env.example` с пустыми/фейковыми значениями."
        ),
        heading("Продакшн: Secret Managers", 3),
        example(
            "python",
            """
            # AWS Secrets Manager
            import boto3
            import json

            def get_secret(secret_name: str) -> dict:
                client = boto3.client("secretsmanager")
                response = client.get_secret_value(SecretId=secret_name)
                return json.loads(response["SecretString"])

            # HashiCorp Vault
            import hvac
            client = hvac.Client(url="https://vault.example.com", token="...")
            secret = client.secrets.kv.v2.read_secret_version(path="myapp/config")

            # Azure Key Vault / GCP Secret Manager — аналогично
            """,
        ),
        text(
            "Secret Managers решают: шифрование в покое/в пути, ротацию секретов, аудит доступа, "
            "динамические секреты (временные БД креды), RBAC. Внедряйте на ранней стадии. "
            "Паттерн: приложение стартует → читает секреты из Manager → кэширует в памяти с TTL. "
            "Для Kubernetes: External Secrets Operator, Vault Agent Injector, Sealed Secrets."
        ),
        heading("Генерация секретов", 3),
        example(
            "python",
            """
            import secrets
            import string

            # Криптографически стойкие случайные строки
            api_key = secrets.token_urlsafe(32)  # 43 chars, URL-safe base64
            password = "".join(secrets.choice(string.ascii_letters + string.digits + "!@#$%") for _ in range(16))
            token = secrets.token_hex(32)  # 64 hex chars (256 bits)
            csrf_token = secrets.token_urlsafe(16)

            # Для JWT HS256 нужен 256-bit ключ
            jwt_secret = secrets.token_bytes(32)  # 32 bytes = 256 bits
            """,
        ),
        text(
            "Модуль `secrets` (Python 3.6+) — CSPRNG (cryptographically secure PRNG). "
            "`random` — НЕ для криптографии! `secrets.token_urlsafe(n)` — n байт энтропии, "
            "base64url encoded. Для JWT HS256 минимум 256 бит (32 байта). "
            "Пароли: минимум 12-16 символов, включать спецсимволы."
        ),
        heading("Безопасная десериализация"),
        text(
            "Десериализация непроверенных данных — одна из самых опасных уязвимостей (RCE). "
            "Pickle, YAML (unsafe_load), eval, exec — выполняют произвольный код при десериализации. "
            "Правило: **никогда не десериализуйте непроверенные данные через небезопасные форматы**."
        ),
        heading("ОПАСНЫЕ паттерны (RCE уязвимости)", 3),
        example(
            "python",
            """
            # НИКОГДА не делайте так с непроверенными данными!
            import pickle
            pickle.loads(untrusted_data)  # RCE!

            import yaml
            yaml.load(untrusted_data)  # RCE через !!python/object

            eval(untrusted_input)  # RCE
            exec(untrusted_input)  # RCE

            import subprocess
            subprocess.run(f"echo {user_input}", shell=True)  # Command Injection
            """,
        ),
        heading("Безопасные альтернативы", 3),
        example(
            "python",
            """
            # JSON — безопасен (нет исполнения кода)
            import json
            data = json.loads(trusted_json_string)

            # YAML — только SafeLoader
            import yaml
            data = yaml.safe_load(trusted_yaml_string)  # не unsafe_load!

            # TOML — безопасен (Python 3.11+ встроен)
            import tomllib
            data = tomllib.loads(trusted_toml_string)

            # MessagePack / CBOR — бинарные, безопасные, быстрые
            import msgpack
            data = msgpack.unpackb(trusted_bytes, raw=False)

            # Command — только список аргументов, без shell=True
            import subprocess
            subprocess.run(["ping", "-c", "3", host], capture_output=True)
            """,
        ),
        text(
            "Безопасные форматы: JSON, MessagePack, CBOR, TOML, Protobuf, Avro — "
            "нет исполнения кода, только данные. YAML: **только `yaml.safe_load()`** (SafeLoader). "
            "Команды: `subprocess.run([cmd, arg1, arg2], ...)` — список аргументов, `shell=False` по умолчанию. "
            "`shlex.quote()` если нужен shell (редко)."
        ),
        heading("Если НУЖНО pickle (только доверенные данные!)", 3),
        example(
            "python",
            """
            import pickle
            import hmac
            import hashlib

            SECRET_KEY = b"your-secret-key"  # из Secret Manager!

            def safe_dumps(obj: object) -> bytes:
                data = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
                signature = hmac.new(SECRET_KEY, data, hashlib.sha256).digest()
                return signature + data

            def safe_loads(signed_data: bytes) -> object:
                signature, data = signed_data[:32], signed_data[32:]
                expected = hmac.new(SECRET_KEY, data, hashlib.sha256).digest()
                if not hmac.compare_digest(signature, expected):
                    raise ValueError("Invalid signature")
                return pickle.loads(data)
            """,
        ),
        text(
            "Если pickle неизбежен (например, кэш ML моделей, внутренний IPC):\n"
            "1. Подписывайте HMAC-SHA256 с секретным ключом (из Secret Manager).\n"
            "2. Проверяйте подпись через `hmac.compare_digest` (защита от timing атак).\n"
            "3. Ключ хранится в Secret Manager, ротируется.\n"
            "4. Десериализация только после проверки подписи.\n"
            "Лучше: используйте `joblib` (safe dump/load для numpy) или `cloudpickle` с подписью."
        ),
        heading("Сканирование уязвимостей зависимостей"),
        text(
            "Зависимости — основной вектор атак supply chain. Регулярное сканирование обязательно: "
            "в CI, по расписанию, при каждом PR. Инструменты: pip-audit (официальный PyPA), "
            "safety (коммерческая БД), GitHub Dependabot (авто-PR), deptry (проблемы с deps)."
        ),
        heading("pip-audit (официальный PyPA)", 3),
        example(
            "bash",
            """
            pip install pip-audit
            pip-audit                    # проверка текущего окружения
            pip-audit -r requirements.txt  # проверка файла
            pip-audit --format=json      # для CI
            pip-audit --fix              # автофикс версий (осторожно!)
            """,
        ),
        heading("Safety (коммерческий, более полная БД)", 3),
        example(
            "bash",
            """
            pip install safety
            safety check                 # проверка окружения
            safety check -r requirements.txt
            safety check --json          # для CI
            """,
        ),
        heading("GitHub Dependabot (автоматически)", 3),
        example(
            "yaml",
            """
            # .github/dependabot.yml
            version: 2
            updates:
              - package-ecosystem: "pip"
                directory: "/"
                schedule:
                  interval: "weekly"
                  day: "monday"
                open-pull-requests-limit: 10
                labels: ["dependencies", "security"]
                allow:
                  - dependency-type: "direct"
                  - dependency-type: "indirect"
            """,
        ),
        text(
            "Dependabot автоматически создаёт PR с обновлениями. Настройте `auto-merge` для patch версий "
            "после прохождения тестов. `dependabot alerts` в Settings репозитория показывает CVE. "
            "Для приватных репозиториев: настройте доступ к приватным регистрам."
        ),
        heading("В CI (GitHub Actions)", 3),
        example(
            "yaml",
            """
            - name: Run pip-audit
              run: |
                pip install pip-audit
                pip-audit --format=json --output=audit.json || true

            - name: Upload audit results
              uses: actions/upload-artifact@v4
              with:
                name: dependency-audit
                path: audit.json
            """,
        ),
        heading("deptry — поиск проблем с зависимостями", 3),
        example(
            "bash",
            """
            pip install deptry
            deptry .  # находит: неиспользуемые, отсутствующие в pyproject.toml, неиспользуемые в коде
            """,
        ),
        text(
            "`deptry` находит: неиспользуемые зависимости (в pyproject.toml но не в импортах), "
            "отсутствующие зависимости (импортируются но нет в deps), несовпадения версий. "
            "Запускайте в CI: `deptry . --fail-on-error`."
        ),
        heading("Структурированное логирование и аудит"),
        text(
            "Логи — глаза в продакшене. Неструктурированные текстовые логи не парсятся, "
            "не фильтруются, не коррелируются. Структурированные JSON логи + request_id correlation "
            "позволяют: найти все логи запроса, построить дашборды, настроить алерты на аномалии, "
            "провести расследование инцидента за минуты, а не часы."
        ),
        heading("structlog — structured logging", 3),
        example(
            "python",
            """
            import structlog
            import logging
            import sys

            structlog.configure(
                processors=[
                    structlog.contextvars.merge_contextvars,
                    structlog.processors.add_log_level,
                    structlog.processors.StackInfoRenderer(),
                    structlog.dev.set_exc_info,
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.JSONRenderer()  # для продакшн
                    # structlog.dev.ConsoleRenderer()  # для разработки
                ],
                wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
                context_class=dict,
                logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
                cache_logger_on_first_use=True,
            )

            logger = structlog.get_logger()

            # Использование
            logger.info("user_login", user_id=123, ip="192.168.1.1", method="oauth")
            logger.error("payment_failed", order_id=456, error="insufficient_funds", amount=100.50)

            # Контекст (автоматически добавляется ко всем логам в рамках запроса)
            structlog.contextvars.bind_contextvars(request_id="req-abc-123", user_id=123)
            """,
        ),
        text(
            "`structlog` — мощная библиотека для структурированного логирования:\n"
            "- `contextvars.merge_contextvars` — авто-добавление request_id, user_id из contextvars.\n"
            "- `JSONRenderer` — JSON строки для продакшн (Loki, ELK, Datadog).\n"
            "- `ConsoleRenderer` — красивый цветной вывод для разработки.\n"
            "- `bind_contextvars` / `clear_contextvars` — управление контекстом запроса.\n"
            "- Middleware в FastAPI: биндит request_id, user_id при входе, очищает при выходе.\n"
            "- `logger.bind(service='payment')` — постоянные поля для компонента."
        ),
        heading("Стандартный logging + JSON formatter", 3),
        example(
            "python",
            """
            import logging
            import json
            from datetime import datetime

            class JSONFormatter(logging.Formatter):
                def format(self, record):
                    log_obj = {
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "level": record.levelname,
                        "logger": record.name,
                        "message": record.getMessage(),
                        "module": record.module,
                        "function": record.funcName,
                        "line": record.lineno,
                    }
                    if record.exc_info:
                        log_obj["exception"] = self.formatException(record.exc_info)
                    # Дополнительные поля из extra
                    for key, value in record.__dict__.items():
                        if key not in ["name", "msg", "args", "created", "filename", "funcName",
                                      "levelname", "levelno", "lineno", "module", "msecs",
                                      "message", "name", "pathname", "process", "processName",
                                      "relativeCreated", "thread", "threadName", "exc_info", "exc_text", "stack_info"]:
                            log_obj[key] = value
                    return json.dumps(log_obj, ensure_ascii=False)

            handler = logging.StreamHandler()
            handler.setFormatter(JSONFormatter())
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.INFO)
            """,
        ),
        text(
            "Стандартный `logging` + кастомный `JSONFormatter` — без внешних зависимостей. "
            "Поля `extra` в `logger.info('msg', extra={'user_id': 123})` попадают в JSON. "
            "Фильтр секретов (см. ниже) обязателен для продакшена."
        ),
        heading("Фильтрация секретов из логов", 3),
        example(
            "python",
            """
            import logging
            import re

            class SecretFilter(logging.Filter):
                PATTERNS = [
                    (re.compile(r'(password|secret|token|api_key|key|authorization)=["\']?([^"\'\s]+)'), r'\1=***'),
                    (re.compile(r'Bearer\s+([A-Za-z0-9\-\._~+/]+=*)'), 'Bearer ***'),
                    (re.compile(r'(eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)'), '***JWT***'),
                    (re.compile(r'\b\d{16}\b'), '****-****-****-****'),  # credit cards
                ]

                def filter(self, record):
                    msg = record.getMessage()
                    for pattern, repl in self.PATTERNS:
                        msg = pattern.sub(repl, msg)
                    record.msg = msg
                    return True

            logging.getLogger().addFilter(SecretFilter())
            """,
        ),
        text(
            "`SecretFilter` маскирует пароли, токены, JWT, API ключи, номера карт перед записью в лог. "
            "Добавляйте паттерны под ваши форматы секретов. Применяйте к root logger или конкретным handlers. "
            "Никогда не логируйте пароли, даже в debug режиме."
        ),
        heading("Аудит безопасных событий", 3),
        example(
            "python",
            """
            from dataclasses import dataclass, asdict
            from datetime import datetime
            from enum import Enum
            import structlog

            class AuditEventType(str, Enum):
                LOGIN_SUCCESS = "login_success"
                LOGIN_FAILED = "login_failed"
                PASSWORD_CHANGED = "password_changed"
                PERMISSION_GRANTED = "permission_granted"
                DATA_EXPORTED = "data_exported"
                ADMIN_ACTION = "admin_action"

            @dataclass
            class AuditEvent:
                event_type: AuditEventType
                user_id: int
                timestamp: str = None
                ip: str = None
                details: dict = None

                def __post_init__(self):
                    self.timestamp = self.timestamp or datetime.utcnow().isoformat() + "Z"

            audit_logger = structlog.get_logger("audit")

            def log_audit(event: AuditEvent):
                audit_logger.info("audit_event", **asdict(event))

            # Использование
            log_audit(AuditEvent(
                event_type=AuditEventType.LOGIN_FAILED,
                user_id=123,
                ip="192.168.1.1",
                details={"reason": "invalid_password", "attempts": 3}
            ))
            """,
        ),
        text(
            "Аудит-логи — отдельный поток (logger 'audit'), разные retention policies, "
            "stringent access control. События: login success/failed, password change, MFA enable/disable, "
            "permission granted/revoked, role change, data export, admin actions, sensitive data access. "
            "Поля: event_type, user_id, timestamp (ISO8601 UTC), ip, user_agent, request_id, details (JSON). "
            "Хранение: отдельный индекс в Loki/ELK, retention 1-7 лет по compliance."
        ),
        heading("OWASP Top 10 для Python — защита", 3),
        table(
            ["Уязвимость", "Защита в Python"],
            [
                ["Injection (SQL, Command)", "Параметризованные запросы (SQLAlchemy ORM, cursor.execute с params), shlex.quote()"],
                ["Broken Auth", "bcrypt/argon2 для паролей, JWT с коротким TTL (15 мин), refresh tokens, MFA"],
                ["Sensitive Data Exposure", "Шифрование в покое (AES-GCM/Fernet), TLS 1.3, секреты не в логах/коде"],
                ["XXE", "defusedxml вместо xml.etree, отключить внешние сущности: parse(xml, forbid_dtd=True)"],
                ["Broken Access Control", "RBAC/ABAC, проверка прав на каждом эндпоинте (policy-based), deny by default"],
                ["Security Misconfiguration", "debug=False в проде, security headers (CSP, HSTS, X-Frame-Options, nosniff)"],
                ["XSS", "Jinja2 autoescape (включен по умолчанию), CSP, sanitize HTML (bleach.clean)"],
                ["Insecure Deserialization", "Только JSON/msgpack/TOML, избегать pickle/yaml.load, eval, exec"],
                ["Vulnerable Components", "pip-audit в CI, Dependabot, регулярное pip install --upgrade, deptry"],
                ["Insufficient Logging", "Structured JSON logs, корреляция request_id, алерты на аномалии (failed login spike)"],
            ],
        ),
        text(
            "OWASP Top 10 — база. Для Python специфично:\n"
            "- SQL Injection: SQLAlchemy ORM / text() с bindparams безопасны. Raw SQL — только с параметрами.\n"
            "- Command Injection: subprocess.run([cmd, arg]) без shell=True. shlex.quote() если нужен shell.\n"
            "- XXE: `defusedxml.defuse_stdlib()` в startup, или `ET.XMLParser(resolve_entities=False)`.\n"
            "- Path Traversal: `os.path.normpath`, проверка что путь внутри allowed directory.\n"
            "- SSRF: валидация URL (allowlist схем/хостов), таймауты, блокировка приватных IP (10.x, 172.16.x, 192.168.x)."
        ),
        heading("Типичные ошибки", 2),
        table(
            ["Ошибка", "Последствия", "Как правильно"],
            [
                ["`SECRET_KEY` в репозитории", "Полная компрометация инфраструктуры", "Только в secret manager / env vars, .env в .gitignore"],
                ["`pickle.load()` из сети/файлов пользователей", "RCE (Remote Code Execution)", "JSON / msgpack / safe yaml (yaml.safe_load)"],
                ["`yaml.load()` без `Loader=yaml.SafeLoader`", "RCE через !!python/object", "Только `yaml.safe_load()`"],
                ["Логирование паролей/токенов", "Утечка секретов через логи", "Фильтруйте чувствительные поля в formatter (SecretFilter)"],
                ["Отсутствие rate limiting", "Брутфорс авторизации, перебор паролей", "`slowapi` / nginx rate limit на /auth, /login, /register"],
                ["`debug=True` в продакшене", "Стек-трейсы, конфиг, секреты в ошибках", "Всегда `False`, отдельные settings для prod"],
                ["`eval()` / `exec()` пользовательского ввода", "RCE", "Никогда. Парсите через ast.literal_eval или JSON."],
                ["Отсутствие CSP / security headers", "XSS, clickjacking, MIME sniffing", "Middleware: CSP, X-Frame-Options: DENY, nosniff, HSTS"],
                ["Хранение паролей в открытом виде", "Утечка = все аккаунты скомпрометированы", "Только argon2/bcrypt через passlib.CryptContext"],
                ["Использование `random` для криптографии", "Предсказуемые токены, слабые ключи", "Только `secrets` модуль (CSPRNG)"],
            ],
        ),
        heading("Практика", 2),
        text(
            "Выполните задания по порядку. Для некоторых нужен AWS/Vault доступ (можно пропустить, использовать mock)."
        ),
        numbered(
            "Валидация: создайте Pydantic-модели для регистрации пользователя с комплексной валидацией пароля (min 12 chars, upper, lower, digit, special), email, username уникальность.",
            "Секреты: настройте `pydantic-settings` + `.env.example` (без реальных значений). Добавьте генерацию JWT secret через `secrets.token_bytes(32)`.",
            "Десериализация: напишите функцию `safe_load_config(path)` — загружает JSON/YAML/TOML, валидирует через Pydantic модель конфига, отбрасывает неизвестные поля.",
            "Сканирование: добавьте `pip-audit` в CI, настройте Dependabot в `.github/dependabot.yml`. Запустите `deptry .` локально.",
            "Логирование: настройте structlog с JSON выводом, добавьте SecretFilter. Настройте audit-логи для: login, logout, password_change, admin_action. Проверьте: в логах нет паролей/токенов.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            "UserCreate(email='test@example.com', username='john_doe', password='SecureP@ss123')\n"
            "ValidationError: 1 validation error for UserCreate\n"
            "password\n  ValueError: Пароль должен содержать спецсимвол [type=value_error, input_value='SimplePass123', input_type=str]",
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "`.env.example` с пустыми значениями: `DATABASE_URL=`, `SECRET_KEY=`, `API_KEY=`. "
            "В CI: `pip-audit --format=json --output=audit.json || true` (не фейлит билд, но артефакт сохраняется). "
            "Dependabot: `schedule.interval: weekly`, `labels: [dependencies, security]`. "
            "SecretFilter: тестируйте на реальных логах с фейковыми секретами.",
        ),
        heading("Проверьте себя", 2),
        numbered(
            "Какие встроенные типы Pydantic есть для валидации email, URL, IP?",
            "В чём разница между @field_validator и @model_validator(mode='after')?",
            "Почему нельзя хранить секреты в коде, даже в приватном репозитории?",
            "Какие форматы десериализации безопасны, а какие — нет?",
            "Как защититься от XXE при парсинге XML в Python?",
            "Что делает `secrets.token_urlsafe(32)` и зачем это нужно для JWT?",
            "Какие события обязательно аудировать?",
            "Как маскировать секреты в логах без внешних библиотек?",
        ),
        heading("Ответы", 2),
        numbered(
            "`EmailStr`, `HttpUrl`, `IPvAnyAddress`, `IPv4Address`, `IPv6Address`, `UUID`, `SecretStr`, `PositiveInt`, `NonNegativeFloat` и др.",
            "`@field_validator` — валидация одного поля (получает значение поля). `@model_validator(mode='after')` — кросс-валидация всего объекта после валидации полей (доступ к self).",
            "Приватный репозиторий может стать публичным, утечь через форки, CI логи, компрометация аккаунта разработчика. Секреты в git — навсегда (history). Ротация сложная.",
            "Безопасные: JSON, MessagePack, CBOR, TOML (tomllib), Protobuf, Avro, yaml.safe_load(). Небезопасные: pickle, yaml.load (без SafeLoader), eval, exec, marshal, shelve.",
            "`defusedxml.defuse_stdlib()` при старте приложения. Или `ET.XMLParser(resolve_entities=False, forbid_dtd=True)`. Стандартный `xml.etree` уязвим по умолчанию.",
            "Генерирует 32 байта (256 бит) криптографически стойкой энтропии, base64url encoded (43 chars). Для JWT HS256 нужен 256-битный ключ. `secrets` — CSPRNG, `random` — нет.",
            "Login success/failed, password change, MFA enable/disable, permission granted/revoked, role change, data export, admin actions, sensitive data access, API key creation/revocation.",
            "logging.Filter с regex паттернами: password=*** , Bearer *** , ***JWT*** , **** карты. Добавить к root logger через addFilter(). Регулярно тестировать на реальных логах.",
        ),
        heading("Итоги", 2),
        bullets(
            "Валидация: Pydantic v2 — Field, field_validator, model_validator, интеграция с FastAPI. Никогда не доверяйте входу.",
            "Секреты: никогда в коде/гите. pydantic-settings + .env (dev), Secret Managers (Vault, AWS, Azure, GCP) — продакшн. Генерация через secrets.token_*.",
            "Десериализация: только JSON, msgpack, TOML, yaml.safe_load, tomllib. Никогда pickle, yaml.load, eval, exec на непроверенных данных. Pickle — только с HMAC подписью для доверенных данных.",
            "Зависимости: pip-audit (CI), Dependabot (авто-PR), safety, deptry. Регулярные апдейты, закрепление версий в requirements.txt через pip-tools.",
            "Логирование: structlog (JSONRenderer, contextvars) или logging + JSONFormatter. Обязателен SecretFilter. Request correlation через contextvars.",
            "Аудит: отдельный logger 'audit', события: login, password, permissions, admin, data export. Поля: type, user_id, timestamp, ip, details. Отдельный retention.",
            "OWASP Top 10 для Python: Injection (params), Auth (argon2/JWT), Sensitive Data (encryption), XXE (defusedxml), Access Control (RBAC), Misconfig (headers), XSS (autoescape), Deserialization (safe formats), Vulnerable Components (pip-audit), Logging (structured).",
            "Ошибки: секреты в коде, pickle/eval на входе, логирование секретов, нет rate limiting, debug=True в проде, нет CSP, случайные числа не для криптографии.",
        ),
        heading("Что дальше", 2),
        text(
            "Безопасность и надёжность — непрерывный процесс. В следующем уроке разберём экосистему "
            "и инструменты: пакетирование (pip, conda, poetry, pdm), мониторинг (Prometheus, Grafana, "
            "OpenTelemetry), профилирование (py-spy, scalene), тестирование (pytest, hypothesis, "
            "contract testing), документация (Sphinx, MkDocs), CI/CD для библиотек, версионирование "
            "и changelog, релиз-менеджмент."
        ),
        heading("Если хотите углубиться", 2),
        bullets(
            "OWASP Top 10 — owasp.org/www-project-top-ten/",
            "OWASP Python Security — owasp.org/www-project-python-security/",
            "Pydantic docs — docs.pydantic.dev/",
            "structlog docs — structlog.org/",
            "pip-audit — pypi.org/project/pip-audit/",
            "Bandit (static security analysis) — bandit.readthedocs.io/",
            "CWE/SANS Top 25 — cwe.mitre.org/top25/",
            "NIST Secure SDLC — csrc.nist.gov/projects/secure-software-development-framework",
            "Cryptography.io — cryptography.io/ (hazmat primitives для продвинутой криптографии)",
        ),
    ],
}