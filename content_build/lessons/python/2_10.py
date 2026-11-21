"""Урок 2.10 курса Python: веб-разработка."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


LESSON = {
    "language": "python",
    "program_order": 2,
    "topic_order": 10,
    "name": "2.10. Веб-разработка",
    "slug": "python-2-10-веб-разработка",
    "short_description": (
        "FastAPI, Pydantic, Dependency Injection, JWT-аутентификация, "
        "тестирование, деплой через Docker. Сравнение с Flask."
    ),
    "topic_name": "Веб-разработка",
    "topic_description": (
        "Как создавать REST API на Python: FastAPI, Pydantic валидация, "
        "Dependency Injection, JWT-аутентификация, тестирование и деплой."
    ),
    "learning_objectives": [
        "Создавать REST API с FastAPI: маршруты, параметры, тело запроса",
        "Использовать Pydantic для валидации запросов и ответов",
        "Применять Dependency Injection через Depends для БД, пагинации, авторизации",
        "Реализовывать JWT-аутентификацию с OAuth2 и bcrypt",
        "Обрабатывать ошибки через HTTPException и кастомные exception handlers",
        "Писать тесты с TestClient и httpx",
        "Деплоить через Docker, docker-compose, gunicorn + uvicorn workers",
    ],
    "estimated_minutes": 50,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "python",
        "fastapi",
        "веб",
        "api",
        "pydantic",
        "jwt",
        "docker",
        "sqlalchemy",
    ],
    "starter_code": code(
        """
        from fastapi import FastAPI
        from pydantic import BaseModel

        app = FastAPI()

        class Item(BaseModel):
            name: str
            price: float
            is_offer: bool = False

        @app.post("/items")
        def create_item(item: Item):
            return {"item_name": item.name, "price": item.price}
        """
    ),
    "hints": [
        "FastAPI автоматически генерирует Swagger UI на /docs и ReDoc на /redoc.",
        "response_model валидирует исходящие данные и скрывает лишние поля.",
        "Depends позволяет переиспользовать логику БД, авторизации, пагинации.",
        "Всегда используйте response_model для валидации и документации.",
        "Секреты (SECRET_KEY, DATABASE_URL) храните в .env, не в коде.",
    ],
    "content": [
        {
            "type": "text",
            "content": (
                "Веб-разработка на Python пережила эволюцию: от синхронных фреймворков "
                "вроде Flask и Django до современных асинхронных решений на базе ASGI. "
                "FastAPI стал де-факто стандартом для новых проектов: он сочетает "
                "скорость разработки (автодокументация, валидация), производительность "
                "(Starlette + Uvicorn) и современный Python (type hints, Pydantic).\n\n"
                "В этом уроке разберём полный цикл создания REST API: от маршрутов и "
                "валидации через Pydantic до Dependency Injection, JWT-аутентификации, "
                "тестирования и деплоя через Docker. В конце кратко сравним с Flask "
                "для понимания, когда какой инструмент уместен."
            ),
        },
        {"type": "heading", "level": 2, "content": "Чему вы научитесь"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "создавать REST API с FastAPI: маршруты, параметры, тело запроса;",
                "валидировать входные данные через Pydantic модели (BaseModel, Field, EmailStr);",
                "применять Dependency Injection через Depends для БД, пагинации, авторизации;",
                "реализовывать JWT-аутентификацию с OAuth2 и bcrypt;",
                "обрабатывать ошибки через HTTPException и кастомные exception handlers;",
                "писать тесты с TestClient и httpx;",
                "деплоить через Docker, docker-compose, gunicorn + uvicorn workers.",
            ],
        },
        {"type": "heading", "level": 2, "content": "FastAPI — современный фреймворк"},
        {
            "type": "text",
            "content": (
                "FastAPI построен на Starlette (ASGI) и Pydantic. Ключевые особенности: "
                "автоматическая OpenAPI/Swagger документация, валидация входных и "
                "выходящих данных через типы Python, нативная поддержка async/await, "
                "Dependency Injection система. Установка минимальная: pip install fastapi uvicorn[standard].\n\n"
                "Starlette — это легковесный ASGI-фреймворк, который предоставляет "
                "роутинг, middleware, WebSockets, статические файлы. FastAPI добавляет "
                "к нему Pydantic-валидацию, автоматическую генерацию OpenAPI схемы, "
                "Dependency Injection систему и удобные декораторы для маршрутов. "
                "Uvicorn — это ASGI-сервер, который запускает приложение и управляет "
                "event loop. Пакет uvicorn[standard] включает дополнительные зависимости "
                "для производительности (httptools, websockets)."
            ),
        },
        {"type": "heading", "level": 3, "content": "Минимальное приложение"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from fastapi import FastAPI

                app = FastAPI(title="My API", version="1.0.0")

                @app.get("/")
                def root():
                    return {"message": "Hello World"}

                @app.get("/hello/{name}")
                def hello(name: str):
                    return {"message": f"Привет, {name}!"}
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Декораторы @app.get, @app.post, @app.put, @app.delete, @app.patch "
                "связывают HTTP-методы с функциями. Параметры функции автоматически "
                "становятся параметрами запроса: путь (/hello/{name}) — path параметр, "
                "остальные — query параметры. Тип str в аннотации включает валидацию.\n\n"
                "FastAPI использует аннотации типов Python для автоматической валидации "
                "и документации. Если клиент передаст user_id как строку, FastAPI "
                "автоматически вернёт 422 с понятным сообщением об ошибке. Это "
                "исключает целый класс багов, связанных с неверными типами данных."
            ),
        },
        {"type": "heading", "level": 3, "content": "Запуск и документация"},
        {
            "type": "code",
            "language": "bash",
            "content": "uvicorn main:app --reload\n# Swagger UI: http://127.0.0.1:8000/docs\n# ReDoc: http://127.0.0.1:8000/redoc"
        },
        {
            "type": "text",
            "content": (
                "Флаг --reload перезагружает сервер при изменении кода (только для разработки). "
                "Swagger UI (/docs) и ReDoc (/redoc) генерируются автоматически из "
                "аннотаций типов и docstrings. Это главное отличие от Flask/Django — "
                "документация всегда актуальна."
            ),
        },
        {"type": "heading", "level": 2, "content": "Параметры запроса: Path, Query, Body"},
        {"type": "heading", "level": 3, "content": "Path параметры с валидацией"},
        {
            "type": "text",
            "content": (
                "Path-параметры извлекаются из URL. FastAPI позволяет добавить "
                "валидацию через Path(..., ge=1, le=1000) — больше/меньше, "
                "min_length/max_length для строк, regex для паттернов."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from fastapi import Path

                @app.get("/users/{user_id}")
                def get_user(
                    user_id: int = Path(..., ge=1, le=1000, description="ID пользователя")
                ):
                    return {"user_id": user_id}
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Path(...) означает обязательный параметр. ge=1, le=1000 проверяют "
                "диапазон. description попадает в Swagger. При нарушении валидации "
                "FastAPI вернёт 422 Unprocessable Entity с деталями ошибки.\n\n"
                "Path параметры подходят для идентификаторов ресурсов: /users/123, "
                "/posts/456/comments/789. Они являются частью URL и обязательны. "
                "FastAPI автоматически конвертирует строку из URL в указанный тип "
                "(int, uuid.UUID, etc.) и проверяет ограничения до вызова функции."
            ),
        },
        {"type": "heading", "level": 3, "content": "Query параметры"},
        {
            "type": "text",
            "content": (
                "Параметры функции, не входящие в path, становятся query-параметрами. "
                "Optional[int] = None делает параметр необязательным. Можно добавить "
                "валидацию через Query(ge=0, le=100)."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from typing import Optional
                from fastapi import Query

                @app.get("/items")
                def read_items(
                    skip: int = Query(0, ge=0),
                    limit: int = Query(10, le=100),
                    search: str | None = None
                ):
                    return {"skip": skip, "limit": limit, "search": search}
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "skip=0, limit=10 — значения по умолчанию для пагинации. "
                "ge=0, le=100 проверяют диапазон. search | None = None делает "
                "параметр необязательным (Python 3.10+ синтаксис union)."
            ),
        },
        {"type": "heading", "level": 3, "content": "Request Body — Pydantic модели"},
        {
            "type": "text",
            "content": (
                "Тело запроса валидируется через Pydantic модели. BaseModel — базовый "
                "класс, Field добавляет метаданные (валидация, описание, пример), "
                "EmailStr проверяет email. response_model валидирует и фильтрует ответ."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from pydantic import BaseModel, EmailStr, Field
                from typing import Optional
                from datetime import datetime

                class UserCreate(BaseModel):
                    name: str = Field(..., min_length=1, max_length=50)
                    email: EmailStr
                    age: Optional[int] = Field(None, ge=0, le=150)

                class UserResponse(UserCreate):
                    id: int
                    created_at: datetime

                    class Config:
                        from_attributes = True  # для SQLAlchemy моделей

                @app.post("/users", response_model=UserResponse, status_code=201)
                def create_user(user: UserCreate):
                    new_user = User(id=1, **user.model_dump(), created_at=datetime.now())
                    return new_user
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "UserCreate — входная модель (без id, created_at). UserResponse "
                "расширяет её, добавляя id и created_at. response_model=UserResponse "
                "гарантирует, что клиент получит только эти поля с правильными типами. "
                "status_code=201 возвращает Created вместо 200 OK.\n\n"
                "Разделение на входную и выходную модели — лучшая практика. Входная "
                "модель не должна содержать поля, которые сервер генерирует сам (id, "
                "created_at, updated_at). Выходная модель может добавлять вычисляемые "
                "поля (full_name, is_active). response_model также служит документацией: "
                "Swagger покажет точную структуру ответа."
            ),
        },
        {
            "type": "callout",
            "style": "info",
            "title": "model_dump() вместо dict()",
            "content": (
                "В Pydantic v2 user.model_dump() заменяет user.dict(). Поддерживает "
                "exclude, include, by_alias параметры для тонкого управления сериализацией."
            ),
        },
        {"type": "heading", "level": 2, "content": "Dependency Injection — Depends"},
        {"type": "heading", "level": 3, "content": "Простая зависимость (генератор с yield)"},
        {
            "type": "text",
            "content": (
                "Depends — сердце FastAPI. Позволяет выносить общую логику (БД, кэш, "
                "авторизация) в отдельные функции. Генератор с yield: код до yield "
                "выполняется перед вызовом эндпоинта, после — при очистке (finally)."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from fastapi import Depends
                from sqlalchemy.orm import Session

                def get_db():
                    db = SessionLocal()
                    try:
                        yield db
                    finally:
                        db.close()

                @app.get("/users")
                def list_users(db: Session = Depends(get_db)):
                    return db.query(User).all()
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "get_db — генератор. FastAPI вызывает его, получает db из yield, "
                "передаёт в эндпоинт. После завершения запроса выполняется finally "
                "(db.close()). Это гарантирует закрытие соединения даже при ошибке."
            ),
        },
        {"type": "heading", "level": 3, "content": "Зависимость с параметрами"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from fastapi import Query, Depends

                def pagination(skip: int = Query(0, ge=0), limit: int = Query(10, le=100)):
                    return {"skip": skip, "limit": limit}

                @app.get("/items")
                def read_items(paging: dict = Depends(pagination)):
                    return paging
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "Классы-зависимости"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                class CommonParams:
                    def __init__(self, skip: int = 0, limit: int = 10):
                        self.skip = skip
                        self.limit = limit

                @app.get("/items")
                def read_items(params: CommonParams = Depends()):
                    return {"skip": params.skip, "limit": params.limit}
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Класс-зависимость удобна для группировки связанных параметров. "
                "FastAPI автоматически создаёт экземпляр класса, передавая query "
                "параметры в __init__. Depends() без аргумента использует тип "
                "аннотации параметра.\n\n"
                "Depends поддерживает вложенность: зависимость может зависеть от другой "
                "зависимости. FastAPI строит граф зависимостей и вызывает их в правильном "
                "порядке. Это позволяет строить сложные системы авторизации: "
                "get_db -> get_current_user -> require_admin, где каждая зависимость "
                "делает свою часть работы."
            ),
        },
        {"type": "heading", "level": 2, "content": "Аутентификация и авторизация (JWT + OAuth2)"},
        {"type": "heading", "level": 3, "content": "Настройка JWT"},
        {
            "type": "code",
            "language": "bash",
            "content": "pip install python-jose[cryptography] passlib[bcrypt] python-multipart"
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
                from jose import jwt, JWTError
                from passlib.context import CryptContext
                from datetime import datetime, timedelta
                from fastapi import HTTPException, Depends, status

                SECRET_KEY = "your-secret-key-change-in-production"
                ALGORITHM = "HS256"
                ACCESS_TOKEN_EXPIRE_MINUTES = 30

                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

                def verify_password(plain, hashed):
                    return pwd_context.verify(plain, hashed)

                def get_password_hash(password):
                    return pwd_context.hash(password)

                def create_access_token(data: dict, expires_delta: timedelta | None = None):
                    to_encode = data.copy()
                    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
                    to_encode.update({"exp": expire})
                    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "Эндпоинты логина и защищённый маршрут"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                @app.post("/token")
                def login(form_data: OAuth2PasswordRequestForm = Depends()):
                    user = authenticate_user(form_data.username, form_data.password)
                    if not user:
                        raise HTTPException(status_code=401, detail="Неверные учётные данные")
                    token = create_access_token(data={"sub": user.email})
                    return {"access_token": token, "token_type": "bearer"}

                async def get_current_user(token: str = Depends(oauth2_scheme)):
                    credentials_exception = HTTPException(
                        status_code=401, detail="Не удалось проверить учётные данные"
                    )
                    try:
                        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                        email: str = payload.get("sub")
                        if email is None:
                            raise credentials_exception
                    except JWTError:
                        raise credentials_exception
                    user = get_user_by_email(email)
                    if user is None:
                        raise credentials_exception
                    return user

                @app.get("/users/me")
                def read_users_me(current_user: User = Depends(get_current_user)):
                    return current_user
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "OAuth2PasswordRequestForm автоматически парсит form-data с полями "
                "username и password. OAuth2PasswordBearer извлекает Bearer-токен из "
                "Authorization заголовка. get_current_user — зависимость, которую "
                "можно использовать в любом защищённом эндпоинте через Depends.\n\n"
                "access_token живёт 15-30 минут — это ограничивает ущерб при утечке. "
                "Для долгих сессий используют refresh tokens: долгоживущий токен "
                "(дни/недели), хранящийся в HttpOnly cookie или БД, который позволяет "
                "получить новый access_token без повторного логина. Refresh token "
                "хранят в HttpOnly cookie (защита от XSS) или в БД с возможностью отзыва."
            ),
        },
        {
            "type": "callout",
            "style": "warning",
            "title": "Секреты в .env",
            "content": (
                "SECRET_KEY никогда не хардкодьте. Используйте python-dotenv: pip install python-dotenv, "
                "создайте .env с SECRET_KEY=..., загрузите через os.getenv(). В продакшене "
                "используйте секреты оркестратора (K8s secrets, Docker secrets, AWS Secrets Manager)."
            ),
        },
        {"type": "heading", "level": 2, "content": "Обработка ошибок"},
        {"type": "heading", "level": 3, "content": "HTTPException и кастомные исключения"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from fastapi import HTTPException, Request
                from fastapi.responses import JSONResponse
                from fastapi.exceptions import RequestValidationError

                class UserNotFound(Exception):
                    def __init__(self, user_id: int):
                        self.user_id = user_id

                @app.exception_handler(UserNotFound)
                async def user_not_found_handler(request: Request, exc: UserNotFound):
                    return JSONResponse(
                        status_code=404,
                        content={"detail": f"User {exc.user_id} not found"},
                    )

                @app.get("/users/{user_id}")
                def get_user(user_id: int):
                    user = find_user(user_id)
                    if not user:
                        raise UserNotFound(user_id)
                    return user
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "Глобальный обработчик валидации"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                @app.exception_handler(RequestValidationError)
                async def validation_exception_handler(request, exc):
                    return JSONResponse(
                        status_code=422,
                        content={"detail": exc.errors()},
                    )
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "exception_handler перехватывает исключения глобально. "
                "RequestValidationError перехватывает ошибки Pydantic (422). "
                "Кастомные исключения позволяют возвращать единообразные ошибки "
                "с правильными HTTP-кодами.\n\n"
                "Правила хорошего API-ошибок: единый формат (detail, code, fields), "
                "правильные HTTP-коды (400/401/403/404/422/500), "
                "логирование ошибок сервера (500) с traceback для разработчиков, "
                "но без утечки деталей клиенту. FastAPI позволяет настроить всё это "
                "через exception_handler на уровне приложения или роутера."
            ),
        },
        {"type": "heading", "level": 2, "content": "Фоновые задачи"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from fastapi import BackgroundTasks

                def send_email(email: str, message: str):
                    # Реальная отправка через SMTP/aiohttp
                    print(f"Отправка email на {email}: {message}")

                @app.post("/send-notification")
                def send_notification(email: str, background_tasks: BackgroundTasks):
                    background_tasks.add_task(send_email, email, "Уведомление")
                    return {"message": "Уведомление будет отправлено"}
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "BackgroundTasks выполняет задачи после отправки ответа клиенту. "
                "Полезно для email, пуш-уведомлений, логирования, очистки кэша. "
                "Для тяжёлых задач лучше использовать Celery/RQ.\n\n"
                "BackgroundTasks выполняются в том же процессе после отправки ответа. "
                "Если задача падает — клиент не узнает. Для критических задач нужны "
                "очереди (Celery/RQ) с ретраями, мониторингом, приоритетами. "
                "BackgroundTasks подходит для fire-and-forget: логирование, метрики, "
                "очистка временных файлов."
            ),
        },
        {"type": "heading", "level": 2, "content": "Тестирование FastAPI"},
        {
            "type": "code",
            "language": "bash",
            "content": "pip install httpx pytest"
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from fastapi.testclient import TestClient
                from main import app

                client = TestClient(app)

                def test_root():
                    response = client.get("/")
                    assert response.status_code == 200
                    assert response.json() == {"message": "Hello World"}

                def test_create_user():
                    response = client.post("/users", json={
                        "name": "Анна",
                        "email": "anna@example.com",
                        "age": 25
                    })
                    assert response.status_code == 201
                    data = response.json()
                    assert data["name"] == "Анна"
                    assert "id" in data
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "TestClient оборачивает ASGI-приложение и позволяет тестировать без "
                "запуска сервера. Для асинхронных тестов используйте httpx.AsyncClient "
                "с base_url. pytest-asyncio для async-тестов.\n\n"
                "TestClient выполняет запросы в том же процессе, что ускоряет тесты. "
                "Для асинхронного кода внутри эндпоинтов TestClient корректно работает "
                "с event loop. httpx.AsyncClient позволяет тестировать асинхронные "
                "эндпоинты с await client.get(...). Всегда тестируйте и успешные, "
                "и ошибочные сценарии (400, 401, 404, 422)."
            ),
        },
        {"type": "heading", "level": 2, "content": "Flask — альтернатива для простых приложений"},
        {
            "type": "code",
            "language": "bash",
            "content": "pip install flask"
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from flask import Flask, jsonify, request

                app = Flask(__name__)

                @app.route("/")
                def hello():
                    return jsonify(message="Hello from Flask")

                @app.route("/users/<int:user_id>")
                def get_user(user_id):
                    return jsonify(id=user_id, name=f"User {user_id}")

                if __name__ == "__main__":
                    app.run(debug=True)
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Flask — WSGI, синхронный, простой, огромная экосистема расширений. "
                "Подходит для монолитных приложений, админок, прототипов. FastAPI "
                "лучше для асинхронных высоконагруженных API, WebSockets, "
                "микросервисов. Выбор зависит от команды и требований.\n\n"
                "Flask имеет огромную экосистему расширений (Flask-SQLAlchemy, "
                "Flask-Login, Flask-Admin, Flask-Migrate). FastAPI экосистема моложе, "
                "но растёт быстро. Миграция с Flask на FastAPI возможна поэтапно: "
                "Starlette совместим с WSGI через middleware."
            ),
        },
        {"type": "heading", "level": 2, "content": "Деплой: Docker, docker-compose, Gunicorn + Uvicorn"},
        {"type": "heading", "level": 3, "content": "Dockerfile"},
        {
            "type": "code",
            "language": "dockerfile",
            "content": code(
                """
                FROM python:3.11-slim

                WORKDIR /app

                COPY pyproject.toml poetry.lock* ./
                RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

                COPY . .

                EXPOSE 8000

                CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "docker-compose.yml"},
        {
            "type": "code",
            "language": "yaml",
            "content": code(
                """
                version: '3.8'
                services:
                  app:
                    build: .
                    ports:
                      - "8000:8000"
                    environment:
                      - DATABASE_URL=postgresql://user:pass@db:5432/app
                    depends_on:
                      - db
                  db:
                    image: postgres:15
                    environment:
                      POSTGRES_USER: user
                      POSTGRES_PASSWORD: pass
                      POSTGRES_DB: app
                    volumes:
                      - pgdata:/var/lib/postgresql/data
                volumes:
                  pgdata:
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "Gunicorn + Uvicorn workers (production)"},
        {
            "type": "code",
            "language": "bash",
            "content": "gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"
        },
        {
            "type": "text",
            "content": (
                "Gunicorn управляет воркерами (prefork), каждый воркер — Uvicorn "
                "(ASGI). -w 4 — 4 воркера (обычно = CPU cores). --bind 0.0.0.0:8000 "
                "слушает все интерфейсы. В Docker CMD лучше использовать gunicorn, "
                "а не uvicorn напрямую.\n\n"
                "prefork означает: мастер-процесс форкает N воркеров, каждый имеет свой "
                "event loop. Запросы распределяются ОС между воркерами. Это даёт "
                "истинный параллелизм на многоядерных системах. uvicorn.workers.UvicornWorker "
                "— это воркер-класс, который заставляет Gunicorn запускать Uvicorn "
                "в каждом воркере. Альтернатива: hypercorn (тоже ASGI, поддерживает HTTP/3)."
            ),
        },
        {"type": "heading", "level": 2, "content": "ASGI vs WSGI — выбор фреймворка"},
        {
            "type": "table",
            "headers": ["Характеристика", "WSGI (Flask, Django)", "ASGI (FastAPI, Starlette)"],
            "rows": [
                ["Протокол", "Синхронный", "Асинхронный"],
                ["WebSockets", "Нет/сложно", "Да, нативно"],
                ["Concurrency", "Threads/Processes", "async/await (event loop)"],
                ["Серверы", "gunicorn, uwsgi", "uvicorn, hypercorn, daphne"],
                ["Подходит для", "CRUD, админки, синхронные задачи", "API, WebSockets, streaming, микросервисы"],
            ],
        },
        {"type": "heading", "level": 2, "content": "Производительность и мониторинг"},
        {
            "type": "text",
            "content": (
                "Production API требует мониторинга: latency (p50, p95, p99), error rate, "
                "throughput, CPU/memory. Инструменты: Prometheus + Grafana, Datadog, "
                "New Relic. FastAPI интегрируется с prometheus-fastapi-instrumentator "
                "для автоматических метрик. Логирование в JSON (structlog) упрощает "
                "парсинг в ELK/Loki.\n\n"
                "Кэширование: Redis для частых запросов, HTTP кэш (ETag, Cache-Control) "
                "для статических ресурсов. CDN для статики. Database connection pooling "
                "(SQLAlchemy pool_size, max_overflow) критично для производительности."
            ),
        },
        {"type": "heading", "level": 2, "content": "Типичные ошибки"},
        {
            "type": "table",
            "headers": ["Ошибка", "Правильно"],
            "rows": [
                ["Блокирующие вызовы в async эндпоинтах", "Используйте to_thread или асинхронные драйверы"],
                ["Забыли response_model", "Всегда указывайте для валидации и документации"],
                ["Хранение секретов в коде", "Переменные окружения + .env (python-dotenv)"],
                ["N+1 запросы в ORM", "selectinload, joinedload"],
                ["Нет обработки ошибок БД", "try/except + rollback в зависимостях"],
            ],
        },
        {"type": "heading", "level": 2, "content": "Практика"},
        {
            "type": "text",
            "content": (
                "Выполните задания по порядку. Используйте временную БД (SQLite in-memory) "
                "для изоляции тестов."
            ),
        },
        {
            "type": "list",
            "ordered": True,
            "items": [
                "Создайте CRUD API для блога: посты (title, content, published), комментарии. FastAPI + SQLAlchemy + SQLite. CRUD эндпоинты с пагинацией.",
                "Добавьте JWT-аутентификацию: регистрация, /token, защищённые эндпоинты. Добавьте refresh token (хранить в HttpOnly cookie).",
                "Реализуйте загрузку аватаров: POST /upload-avatar с multipart/form-data. Валидация: только изображения, max 5MB. Сохранение на диск/в S3.",
                "Добавьте rate limiting middleware: максимум 100 запросов в минуту с одного IP. Используйте Redis или in-memory словарь с TTL.",
                "Настройте CI/CD: GitHub Actions — pytest → сборка Docker образа → пуш в registry. Добавьте линтинг (ruff) и типизацию (mypy).",
            ],
        },
        {
            "type": "callout",
            "style": "success",
            "title": "Подсказка к заданию 2",
            "content": (
                "Refresh token храните в БД с полем expires_at. При логине выдавайте "
                "access (15 мин) + refresh (7 дней). Эндпоинт /refresh принимает refresh "
                "токен, проверяет в БД, выдаёт новую пару. HttpOnly cookie для refresh "
                "защищает от XSS."
            ),
        },
        {"type": "heading", "level": 2, "content": "Проверьте себя"},
        {
            "type": "list",
            "ordered": True,
            "items": [
                "В чём разница между @app.get и @app.post? Когда что использовать?",
                "Зачем нужен response_model, если можно просто вернуть dict?",
                "Как Depends(get_db) гарантирует закрытие соединения при ошибке?",
                "Почему SECRET_KEY нельзя коммитить в git? Как правильно хранить?",
                "В чём разница между WSGI и ASGI? Когда выбирать FastAPI, а когда Flask?",
            ],
        },
        {"type": "heading", "level": 3, "content": "Ответы"},
        {
            "type": "list",
            "ordered": True,
            "items": [
                "@app.get — для безопасных идемпотентных операций (чтение). @app.post — для создания ресурсов, небезопасных операций. PUT — полное обновление, PATCH — частичное, DELETE — удаление.",
                "response_model валидирует исходящие данные, скрывает лишние поля (пароли, внутренние ID), генерирует корректную OpenAPI схему. Без него клиент может получить лишние данные.",
                "yield в генераторе разделяет setup (до yield) и teardown (после yield). FastAPI гарантирует выполнение finally даже при исключении в эндпоинте.",
                "SECRET_KEY в git — компрометация всех токенов. Храните в .env (gitignore) + python-dotenv. В продакшене — секреты оркестратора (K8s, Docker, AWS).",
                "WSGI — синхронный, один запрос = один тред/процесс. ASGI — асинхронный, event loop, тысячи соединений в одном процессе. FastAPI для API/WebSockets/нагрузка, Flask — для админок/простых сайтов/команда знает только Flask.",
            ],
        },
        {"type": "heading", "level": 2, "content": "Итоги"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "FastAPI — современный ASGI фреймворк с автодокументацией и валидацией через типы.",
                "Pydantic BaseModel + Field + response_model — валидация входа и выхода.",
                "Depends — мощная DI система для БД, авторизации, пагинации, кэша.",
                "JWT + OAuth2PasswordBearer — стандарт аутентификации для REST API.",
                "HTTPException + exception_handler — единообразная обработка ошибок.",
                "BackgroundTasks — простые фоновые задачи, Celery/RQ — для тяжёлых.",
                "TestClient + pytest — быстрые интеграционные тесты без запуска сервера.",
                "Docker + gunicorn + uvicorn workers — стандартный production деплой.",
                "ASGI (FastAPI) для API/WebSockets, WSGI (Flask) для админок/простых сайтов.",
            ],
        },
        {"type": "heading", "level": 2, "content": "Что дальше"},
        {
            "type": "text",
            "content": (
                "Веб-разработка — широкая тема. Следующий урок про производительность "
                "и профилирование: как находить узкие места, оптимизировать код, "
                "использовать кэширование, работать с памятью. Эти навыки критичны "
                "для продакшн API под нагрузкой."
            ),
        },
        {"type": "heading", "level": 2, "content": "Если хотите углубиться"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "FastAPI docs: fastapi.tiangolo.com — полное руководство.",
                "Pydantic v2 docs: docs.pydantic.dev — валидация, сериализация.",
                "SQLAlchemy 2.0 tutorial: docs.sqlalchemy.org/en/20/tutorial/.",
                "JWT best practices: rfc7519, auth0.com/blog/jwt-best-practices.",
                "Docker best practices: docs.docker.com/develop/develop-images/dockerfile_best-practices/.",
            ],
        },
    ],
}