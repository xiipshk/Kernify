with open('content_build/lessons/python/2_10.py') as f:
    s = f.read()

# 1. After FastAPI intro
old1 = """        {"type": "text", "content": (
                "FastAPI построен на Starlette (ASGI) и Pydantic. Ключевые особенности: "
                "автоматическая OpenAPI/Swagger документация, валидация входных и "
                "выходящих данных через типы Python, нативная поддержка async/await, "
                "Dependency Injection система. Установка минимальная: pip install fastapi uvicorn[standard]."
            )},
        {"type": "heading", "level": 3, "content": "Минимальное приложение"}"""
new1 = """        {"type": "text", "content": (
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
            )},
        {"type": "heading", "level": 3, "content": "Минимальное приложение"}"""
s = s.replace(old1, new1)

# 2. After minimal app
old2 = """        {"type": "text", "content": (
                "Декораторы @app.get, @app.post, @app.put, @app.delete, @app.patch "
                "связывают HTTP-методы с функциями. Параметры функции автоматически "
                "становятся параметрами запроса: путь (/hello/{name}) — path параметр, "
                "остальные — query параметры. Тип str в аннотации включает валидацию."
            )},
        {"type": "heading", "level": 3, "content": "Запуск и документация"}"""
new2 = """        {"type": "text", "content": (
                "Декораторы @app.get, @app.post, @app.put, @app.delete, @app.patch "
                "связывают HTTP-методы с функциями. Параметры функции автоматически "
                "становятся параметрами запроса: путь (/hello/{name}) — path параметр, "
                "остальные — query параметры. Тип str в аннотации включает валидацию.\n\n"
                "FastAPI использует аннотации типов Python для автоматической валидации "
                "и документации. Если клиент передаст user_id как строку, FastAPI "
                "автоматически вернёт 422 с понятным сообщением об ошибке. Это "
                "исключает целый класс багов, связанных с неверными типами данных."
            )},
        {"type": "heading", "level": 3, "content": "Запуск и документация"}"""
s = s.replace(old2, new2)

# 3. After Path params
old3 = """        {"type": "text", "content": (
                "Path(...) означает обязательный параметр. ge=1, le=1000 проверяют "
                "диапазон. description попадает в Swagger. При нарушении валидации "
                "FastAPI вернёт 422 Unprocessable Entity с деталями ошибки."
            )},
        {"type": "heading", "level": 3, "content": "Query параметры"}"""
new3 = """        {"type": "text", "content": (
                "Path(...) означает обязательный параметр. ge=1, le=1000 проверяют "
                "диапазон. description попадает в Swagger. При нарушении валидации "
                "FastAPI вернёт 422 Unprocessable Entity с деталями ошибки.\n\n"
                "Path параметры подходят для идентификаторов ресурсов: /users/123, "
                "/posts/456/comments/789. Они являются частью URL и обязательны. "
                "FastAPI автоматически конвертирует строку из URL в указанный тип "
                "(int, uuid.UUID, etc.) и проверяет ограничения до вызова функции."
            )},
        {"type": "heading", "level": 3, "content": "Query параметры"}"""
s = s.replace(old3, new3)

# 4. After Pydantic models
old4 = """        {"type": "text", "content": (
                "UserCreate — входная модель (без id, created_at). UserResponse "
                "расширяет её, добавляя id и created_at. response_model=UserResponse "
                "гарантирует, что клиент получит только эти поля с правильными типами. "
                "status_code=201 возвращает Created вместо 200 OK."
            )},
        {"type": "callout", "style": "info", "title": "model_dump() вместо dict()", "content": (
            "В Pydantic v2 user.model_dump() заменяет user.dict(). Поддерживает "
            "exclude, include, by_alias параметры для тонкого управления сериализацией."
        )},
        {"type": "heading", "level": 2, "content": "Dependency Injection"}"""
new4 = """        {"type": "text", "content": (
                "UserCreate — входная модель (без id, created_at). UserResponse "
                "расширяет её, добавляя id и created_at. response_model=UserResponse "
                "гарантирует, что клиент получит только эти поля с правильными типами. "
                "status_code=201 возвращает Created вместо 200 OK.\n\n"
                "Разделение на входную и выходную модели — лучшая практика. Входная "
                "модель не должна содержать поля, которые сервер генерирует сам (id, "
                "created_at, updated_at). Выходная модель может добавлять вычисляемые "
                "поля (full_name, is_active). response_model также служит документацией: "
                "Swagger покажет точную структуру ответа."
            )},
        {"type": "callout", "style": "info", "title": "model_dump() вместо dict()", "content": (
            "В Pydantic v2 user.model_dump() заменяет user.dict(). Поддерживает "
            "exclude, include, by_alias параметры для тонкого управления сериализацией."
        )},
        {"type": "heading", "level": 2, "content": "Dependency Injection"}"""
s = s.replace(old4, new4)

# 5. After Depends section
old5 = """        {"type": "text", "content": (
                "Класс-зависимость удобна для группировки связанных параметров. "
                "FastAPI автоматически создаёт экземпляр класса, передавая query "
                "параметры в __init__. Depends() без аргумента использует тип "
                "аннотации параметра."
            )},
        {"type": "heading", "level": 2, "content": "Аутентификация и авторизация"}"""
new5 = """        {"type": "text", "content": (
                "Класс-зависимость удобна для группировки связанных параметров. "
                "FastAPI автоматически создаёт экземпляр класса, передавая query "
                "параметры в __init__. Depends() без аргумента использует тип "
                "аннотации параметра.\n\n"
                "Depends поддерживает вложенность: зависимость может зависеть от другой "
                "зависимости. FastAPI строит граф зависимостей и вызывает их в правильном "
                "порядке. Это позволяет строить сложные системы авторизации: "
                "get_db -> get_current_user -> require_admin, где каждая зависимость "
                "делает свою часть работы."
            )},
        {"type": "heading", "level": 2, "content": "Аутентификация и авторизация"}"""
s = s.replace(old5, new5)

# 6. After JWT section
old6 = """        {"type": "text", "content": (
                "OAuth2PasswordRequestForm автоматически парсит form-data с полями "
                "username и password. OAuth2PasswordBearer извлекает Bearer-токен из "
                "Authorization заголовка. get_current_user — зависимость, которую "
                "можно использовать в любом защищённом эндпоинте через Depends."
            )},
        {"type": "callout", "style": "warning", "title": "Секреты в .env", "content": (
            "SECRET_KEY никогда не хардкодьте. Используйте python-dotenv: pip install python-dotenv, "
            "создайте .env с SECRET_KEY=..., загрузите через os.getenv(). В продакшене "
            "используйте секреты оркестратора (K8s secrets, Docker secrets, AWS Secrets Manager)."
        )},
        {"type": "heading", "level": 2, "content": "Обработка ошибок"}"""
new6 = """        {"type": "text", "content": (
                "OAuth2PasswordRequestForm автоматически парсит form-data с полями "
                "username и password. OAuth2PasswordBearer извлекает Bearer-токен из "
                "Authorization заголовка. get_current_user — зависимость, которую "
                "можно использовать в любом защищённом эндпоинте через Depends.\n\n"
                "access_token живёт 15-30 минут — это ограничивает ущерб при утечке. "
                "Для долгих сессий используют refresh tokens: долгоживущий токен "
                "(дни/недели), хранящийся в HttpOnly cookie или БД, который позволяет "
                "получить новый access_token без повторного логина. Refresh token "
                "хранят в HttpOnly cookie (защита от XSS) или в БД с возможностью отзыва."
            )},
        {"type": "callout", "style": "warning", "title": "Секреты в .env", "content": (
            "SECRET_KEY никогда не хардкодьте. Используйте python-dotenv: pip install python-dotenv, "
            "создайте .env с SECRET_KEY=..., загрузите через os.getenv(). В продакшене "
            "используйте секреты оркестратора (K8s secrets, Docker secrets, AWS Secrets Manager)."
        )},
        {"type": "heading", "level": 2, "content": "Обработка ошибок"}"""
s = s.replace(old6, new6)

# 6. After error handling
old7 = """        {"type": "text", "content": (
                "exception_handler перехватывает исключения глобально. "
                "RequestValidationError перехватывает ошибки Pydantic (422). "
                "Кастомные исключения позволяют возвращать единообразные ошибки "
                "с правильными HTTP-кодами."
            )},
        {"type": "heading", "level": 2, "content": "Фоновые задачи"}"""
new7 = """        {"type": "text", "content": (
                "exception_handler перехватывает исключения глобально. "
                "RequestValidationError перехватывает ошибки Pydantic (422). "
                "Кастомные исключения позволяют возвращать единообразные ошибки "
                "с правильными HTTP-кодами.\n\n"
                "Правила хорошего API-ошибок: единый формат (detail, code, fields), "
                "правильные HTTP-коды (400/401/403/404/422/500), "
                "логирование ошибок сервера (500) с traceback для разработчиков, "
                "но без утечки деталей клиенту. FastAPI позволяет настроить всё это "
                "через exception_handler на уровне приложения или роутера."
            )},
        {"type": "heading", "level": 2, "content": "Фоновые задачи"}"""
s = s.replace(old7, new7)

# 7. After background tasks
old8 = """        {"type": "text", "content": (
                "BackgroundTasks выполняет задачи после отправки ответа клиенту. "
                "Полезно для email, пуш-уведомлений, логирования, очистки кэша. "
                "Для тяжёлых задач лучше использовать Celery/RQ."
            )},
        {"type": "heading", "level": 2, "content": "Тестирование FastAPI"}"""
new8 = """        {"type": "text", "content": (
                "BackgroundTasks выполняет задачи после отправки ответа клиенту. "
                "Полезно для email, пуш-уведомлений, логирования, очистки кэша. "
                "Для тяжёлых задач лучше использовать Celery/RQ.\n\n"
                "BackgroundTasks выполняются в том же процессе после отправки ответа. "
                "Если задача падает — клиент не узнает. Для критических задач нужны "
                "очереди (Celery/RQ) с ретраями, мониторингом, приоритетами. "
                "BackgroundTasks подходит для fire-and-forget: логирование, метрики, "
                "очистка временных файлов."
            )},
        {"type": "heading", "level": 2, "content": "Тестирование FastAPI"}"""
s = s.replace(old8, new8)

# 7. After testing
old9 = """        {"type": "text", "content": (
                "TestClient оборачивает ASGI-приложение и позволяет тестировать без "
                "запуска сервера. Для асинхронных тестов используйте httpx.AsyncClient "
                "с base_url. pytest-asyncio для async-тестов."
            )},
        {"type": "heading", "level": 2, "content": "Flask — альтернатива для простых приложений"}"""
new9 = """        {"type": "text", "content": (
                "TestClient оборачивает ASGI-приложение и позволяет тестировать без "
                "запуска сервера. Для асинхронных тестов используйте httpx.AsyncClient "
                "с base_url. pytest-asyncio для async-тестов.\n\n"
                "TestClient выполняет запросы в том же процессе, что ускоряет тесты. "
                "Для асинхронного кода внутри эндпоинтов TestClient корректно работает "
                "с event loop. httpx.AsyncClient позволяет тестировать асинхронные "
                "эндпоинты с await client.get(...). Всегда тестируйте и успешные, "
                "и ошибочные сценарии (400, 401, 404, 422)."
            )},
        {"type": "heading", "level": 2, "content": "Flask — альтернатива для простых приложений"}"""
s = s.replace(old9, new9)

# 8. After Flask
old10 = """        {"type": "text", "content": (
                "Flask — WSGI, синхронный, простой, огромная экосистема расширений. "
                "Подходит для монолитных приложений, админок, прототипов. FastAPI "
                "лучше для асинхронных высоконагруженных API, WebSockets, "
                "микросервисов. Выбор зависит от команды и требований."
            )},
        {"type": "heading", "level": 2, "content": "Деплой: Docker, docker-compose, Gunicorn + Uvicorn"}"""
new10 = """        {"type": "text", "content": (
                "Flask — WSGI, синхронный, простой, огромная экосистема расширений. "
                "Подходит для монолитных приложений, админок, прототипов. FastAPI "
                "лучше для асинхронных высоконагруженных API, WebSockets, "
                "микросервисов. Выбор зависит от команды и требований.\n\n"
                "Flask имеет огромную экосистему расширений (Flask-SQLAlchemy, "
                "Flask-Login, Flask-Admin, Flask-Migrate). FastAPI экосистема моложе, "
                "но растёт быстро. Миграция с Flask на FastAPI возможна поэтапно: "
                "Starlette совместим с WSGI через middleware."
            )},
        {"type": "heading", "level": 2, "content": "Деплой: Docker, docker-compose, Gunicorn + Uvicorn"}"""
s = s.replace(old10, new10)

# 8. After Docker
old11 = """        {"type": "text", "content": (
                "Gunicorn управляет воркерами (prefork), каждый воркер — Uvicorn "
                "(ASGI). -w 4 — 4 воркера (обычно = CPU cores). --bind 0.0.0.0:8000 "
                "слушает все интерфейсы. В Docker CMD лучше использовать gunicorn, "
                "а не uvicorn напрямую."
            )},
        {"type": "heading", "level": 2, "content": "ASGI vs WSGI"}"""
new11 = """        {"type": "text", "content": (
                "Gunicorn управляет воркерами (prefork), каждый воркер — Uvicorn "
                "(ASGI). -w 4 — 4 воркера (обычно = CPU cores). --bind 0.0.0.0:8000 "
                "слушает все интерфейсы. В Docker CMD лучше использовать gunicorn, "
                "а не uvicorn напрямую.\n\n"
                "prefork означает: мастер-процесс форкает N воркеров, каждый имеет свой "
                "event loop. Запросы распределяются ОС между воркерами. Это даёт "
                "истинный параллелизм на многоядерных системах. uvicorn.workers.UvicornWorker "
                "— это воркер-класс, который заставляет Gunicorn запускать Uvicorn "
                "в каждом воркере. Альтернатива: hypercorn (тоже ASGI, поддерживает HTTP/3)."
            )},
        {"type": "heading", "level": 2, "content": "ASGI vs WSGI"}"""
s = s.replace(old11, new11)

# 8. Add performance section before common errors
old12 = """        {"type": "heading", "level": 2, "content": "Типичные ошибки"}"""
new12 = """        {"type": "heading", "level": 3, "content": "Производительность и мониторинг"},
        {"type": "text", "content": (
                "Production API требует мониторинга: latency (p50, p95, p99), error rate, "
                "throughput, CPU/memory. Инструменты: Prometheus + Grafana, Datadog, "
                "New Relic. FastAPI интегрируется с prometheus-fastapi-instrumentator "
                "для автоматических метрик. Логирование в JSON (structlog) упрощает "
                "парсинг в ELK/Loki.\n\n"
                "Кэширование: Redis для частых запросов, HTTP кэш (ETag, Cache-Control) "
                "для статических ресурсов. CDN для статики. Database connection pooling "
                "(SQLAlchemy pool_size, max_overflow) критично для производительности."
            )},
        {"type": "heading", "level": 2, "content": "Типичные ошибки"}"""
s = s.replace('        {"type": "heading", "level": 2, "content": "Типичные ошибки"}', new12)

with open('content_build/lessons/python/2_10.py', 'w') as f:
    f.write(s)

print("Added more content")