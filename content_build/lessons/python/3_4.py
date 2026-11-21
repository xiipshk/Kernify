"""Урок 3.4 курса Python: безопасность."""

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
    "topic_order": 4,
    "name": "3.4. Безопасность",
    "slug": "python-3-4-безопасность",
    "short_description": (
        "OWASP Top 10, защита от инъекций (SQL, NoSQL, команда, LDAP), "
        "криптография (hashing, encryption, JWT), аутентификация/авторизация, "
        "аудит зависимостей, управление секретами."
    ),
    "topic_name": "Безопасность",
    "topic_description": (
        "Комплексный подход к безопасности Python-приложений: от защиты от инъекций "
        "до правильной криптографии, безопасной аутентификации, управления секретами "
        "и автоматизированного аудита кода и зависимостей."
    ),
    "learning_objectives": [
        "Знать OWASP Top 10 и понимать, как каждая уязвимость проявляется в Python",
        "Писать безопасные запросы к БД: параметризованные SQL, защита от NoSQL injection",
        "Избегать command injection через subprocess без shell=True",
        "Правильно хэшировать пароли (argon2/bcrypt), шифровать данные (Fernet, RSA)",
        "Реализовывать JWT аутентификацию с access/refresh токенами и отзывом",
        "Настраивать безопасные cookies, CSRF защиту, Rate Limiting, CSP заголовки",
        "Автоматизировать аудит зависимостей (pip-audit, safety, dependabot)",
        "Управлять секретами через переменные окружения и Secret Manager (Vault, AWS)",
        "Настраивать статический анализ безопасности (bandit, semgrep) в pre-commit/CI",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "python",
        "безопасность",
        "owasp",
        "sql injection",
        "криптография",
        "jwt",
        "аутентификация",
        "секреты",
        "bandit",
    ],
    "starter_code": code(
        """
        # ПЛОХО: SQL Injection
        cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")

        # ХОРОШО: параметризованный запрос
        cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
        """
    ),
    "hints": [
        "Никогда не конкатенируйте пользовательский ввод в SQL — используйте параметры.",
        "Для паролей только argon2 или bcrypt — никаких MD5/SHA.",
        "JWT секрет должен быть 256+ бит, храниться в env, ротироваться.",
        "Всегда фильтруйте чувствительные данные из логов (пароли, токены, ключи).",
    ],
    "content": [
        text(
            "Безопасность — не фича, которую можно «добавить потом». Это архитектурное "
            "решение, заложенное с первого дня. Один упущенный SQL injection или "
            "утечка секрета в git может стоить компании репутации, штрафов по GDPR "
            "и денег пользователей. В этом уроке пройдём по полному чек-листу: "
            "OWASP Top 10, инъекции, криптография, аутентификация/авторизация, "
            "зависимости, секреты, аудит кода и логирование безопасности."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "понимать OWASP Top 10 2021 и находить соответствующие уязвимости в коде;",
            "защищаться от SQL, NoSQL, Command, LDAP инъекций правильными приёмами;",
            "хэшировать пароли через argon2/bcrypt (passlib), проверять их безопасно;",
            "шифровать данные: симметрично (Fernet/AES), асимметрично (RSA), подписывать (HMAC, Ed25519);",
            "создавать и проверять JWT токены (access/refresh), реализовывать отзыв через Redis;",
            "настраивать безопасные cookies (HttpOnly, Secure, SameSite), CSRF, Rate Limiting, CSP;",
            "сканировать зависимости на уязвимости: pip-audit, safety, GitHub Dependabot;",
            "хранить секреты правильно: env для dev, Vault/AWS Secrets Manager для продакшена;",
            "внедрять bandit и semgrep в pre-commit и CI для автоматического аудита.",
        ),
        heading("OWASP Top 10 (2021) — карта угроз"),
        text(
            "OWASP Top 10 — ежегодный рейтинг самых критических уязвимостей веб-приложений. "
            "Версия 2021:"
        ),
        table(
            ["#", "Уязвимость", "Суть", "Пример в Python"],
            [
                ["A01", "Broken Access Control", "Пользователь получает доступ не к своим данным", "GET /api/users/42 без проверки owner_id"],
                ["A02", "Cryptographic Failures", "Слабая/отсутствующая криптография", "MD5 для паролей, HTTP вместо HTTPS"],
                ["A03", "Injection", "Внедрение кода через ввод", "SQLi, NoSQLi, Command Injection"],
                ["A04", "Insecure Design", "Архитектурные недостатки", "Отсутствие rate limiting на логин"],
                ["A05", "Security Misconfiguration", "Небезопасные настройки", "DEBUG=True в продакшене, дефолтные пароли"],
                ["A06", "Vulnerable Components", "Уязвимые библиотеки", "requests<2.28.0 с CVE-2022-XXXX"],
                ["A07", "Authentication Failures", "Слабая аутентификация", "Нет MFA, простые пароли, нет блокировок"],
                ["A08", "Software Integrity Failures", "Непроверенные обновления", "pip install без проверки подписей"],
                ["A09", "Logging Failures", "Недостаточное логирование", "Нет логов неудачных логинов"],
                ["A10", "SSRF", "Server-Side Request Forgery", "fetch_url(user_input) без валидации"],
            ],
        ),
        callout(
            "info",
            "Приоритет",
            "A01, A02, A03 — самые частые и опасные. Начните аудит с них. "
            "A06 (зависимости) — самый простой для автоматизации.",
        ),
        heading("Защита от инъекций"),
        heading("SQL Injection — параметризованные запросы", 3),
        text(
            "SQL Injection — классика. Пользовательский ввод попадает в запрос как часть "
            "SQL-кода, а не как параметр. Решение: **всегда** используйте параметры."
        ),
        example(
            "python",
            """
            # ПЛОХО — конкатенация
            cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")

            # ХОРОШО — параметры (placeholder зависит от ДБ: ?, %s, :name)
            cursor.execute("SELECT * FROM users WHERE name = ?", (name,))

            # SQLAlchemy ORM — безопасно по умолчанию
            session.query(User).filter(User.name == name).first()

            # Raw SQL в SQLAlchemy — text() с bindparams
            from sqlalchemy import text
            session.execute(text("SELECT * FROM users WHERE name = :name"), {"name": name})
            """,
        ),
        text(
            "Правила:\n"
            "- Никогда не используйте f-строки, `%`, `.format()` для SQL.\n"
            "- Placeholders: `?` (sqlite3), `%s` (psycopg2, mysqlclient), `:name` (SQLAlchemy, Oracle).\n"
            "- ORM (SQLAlchemy, Django ORM, Tortoise) безопасен, если не используете `raw()` / `extra()` без параметров.\n"
            "- LIMIT/OFFSET тоже параметризуйте: `LIMIT ? OFFSET ?`."
        ),
        heading("NoSQL Injection (MongoDB)", 3),
        text(
            "В MongoDB запрос — это документ. Если пользователь передаёт `{'$ne': null}` "
            "вместо строки, условие меняет смысл."
        ),
        example(
            "python",
            """
            # ПЛОХО — пользователь может передать {"$ne": null}
            db.users.find({"username": username, "password": password})

            # ХОРОШО — явные операторы
            db.users.find({"username": {"$eq": username}, "password": {"$eq": password}})

            # Или ODM (Beanie, Motor, ODMantic) с Pydantic моделями
            class User(Document):
                username: str
                password_hash: str

            await User.find_one(User.username == username, User.password_hash == hash)
            """,
        ),
        text(
            "Всегда валидируйте тип ввода (строка, число) и используйте явные операторы `$eq`, "
            "`$gt` вместо доверия структуре документа. ODM (Beanie, ODMantic) решает это через типы."
        ),
        heading("Command Injection", 3),
        text(
            "`shell=True` в `subprocess.run` запускает команду через оболочку (sh/bash). "
            "Пользовательский ввод с `; rm -rf /` или `$(reboot)` выполнится."
        ),
        example(
            "python",
            """
            # ПЛОХО
            os.system(f"ping {host}")
            subprocess.run(f"ping {host}", shell=True)

            # ХОРОШО — без shell, список аргументов
            import subprocess
            subprocess.run(["ping", "-c", "3", host], capture_output=True)

            # shlex.quote если нужен shell (редко)
            import shlex
            cmd = f"ping {shlex.quote(host)}"
            subprocess.run(cmd, shell=True)  # только с quote!
            """,
        ),
        text(
            "Правила:\n"
            "- Всегда `shell=False` (по умолчанию) и список аргументов.\n"
            "- Валидируйте ввод: хост — только буквы/цифры/точки/дефисы.\n"
            "- Для сложных команд — `shlex.quote()` каждый аргумент.\n"
            "- Лучше используйте Python-библиотеки вместо вызова CLI (ping → `pythonping`)."
        ),
        heading("LDAP Injection", 3),
        example(
            "python",
            """
            # ПЛОХО
            filter = f"(cn={user_input})"

            # ХОРОШО — escape
            import ldap3
            from ldap3.utils.conv import escape_filter_chars
            filter = f"(cn={escape_filter_chars(user_input)})"
            """,
        ),
        heading("Криптография: правильные инструменты"),
        text(
            "Криптографию легко сломать, написав свою. Используйте проверенные библиотеки: "
            "`cryptography` (низкий уровень), `passlib` (пароли), `python-jose` (JWT)."
        ),
        heading("Хэширование паролей — argon2 / bcrypt", 3),
        example(
            "bash",
            """
            pip install passlib[bcrypt] argon2-cffi
            """,
        ),
        example(
            "python",
            """
            from passlib.context import CryptContext

            # argon2 — первый, bcrypt — фоллбек, deprecated="auto" обновляет старые хэши
            pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

            def hash_password(password: str) -> str:
                return pwd_context.hash(password)

            def verify_password(plain: str, hashed: str) -> bool:
                return pwd_context.verify(plain, hashed)

            # Использование
            hashed = hash_password("secret123")  # $argon2id$v=19$m=65536,t=3,p=4$...
            verify_password("secret123", hashed)  # True
            verify_password("wrong", hashed)      # False
            """,
        ),
        text(
            "**argon2id** — современный стандарт (победитель PHC 2015). Параметры по умолчанию "
            "в passlib безопасны. `deprecated='auto'` автоматически перехэширует старые bcrypt "
            "при следующем успешном логине. **Никогда не используйте MD5, SHA1, SHA256** для паролей — "
            "они слишком быстрые, GPU перебирает миллиарды в секунду."
        ),
        heading("Симметричное шифрование — Fernet (AES-128-GCM)", 3),
        example(
            "bash",
            """
            pip install cryptography
            """,
        ),
        example(
            "python",
            """
            from cryptography.fernet import Fernet

            key = Fernet.generate_key()  # 32 байта, base64 — сохранить в секрете!
            f = Fernet(key)

            token = f.encrypt(b"секретные данные")
            # token = b'gAAAAABl...' — содержит IV, ciphertext, HMAC, timestamp

            data = f.decrypt(token)  # b"секретные данные"
            # decrypt проверяет HMAC и timestamp (TTL можно задать: f.decrypt(token, ttl=3600))
            """,
        ),
        text(
            "Fernet = AES-128 в режиме CBC + HMAC-SHA256. Ключ 32 байта (base64). "
            "Токен содержит версию, timestamp, IV, ciphertext, HMAC. "
            "Подходит для шифрования cookies, сессий, небольших секретов. "
            "Для больших файлов — используйте `cryptography.hazmat.primitives.ciphers.aead.AESGCM` напрямую."
        ),
        heading("Асимметричное шифрование — RSA-OAEP", 3),
        example(
            "python",
            """
            from cryptography.hazmat.primitives.asymmetric import rsa, padding
            from cryptography.hazmat.primitives import hashes, serialization

            # Генерация ключей
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            public_key = private_key.public_key()

            # Сериализация для хранения
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase")
            )
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            # Шифрование (публичный ключ) — только для малых данных (< key_size/8)
            ciphertext = public_key.encrypt(
                b"secret",
                padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )

            # Расшифрование (приватный ключ)
            plaintext = private_key.decrypt(
                ciphertext,
                padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            """,
        ),
        text(
            "RSA-OAEP с SHA-256 — стандарт для асимметричного шифрования. "
            "RSA шифрует только данные меньше размера ключа (2048 бит = 256 байт). "
            "Для больших данных: гибридное шифрование — генерируйте случайный AES-ключ, "
            "шифруйте им данные (Fernet), AES-ключ шифруйте RSA."
        ),
        heading("Подпись и целостность — HMAC / Ed25519", 3),
        example(
            "python",
            """
            import hmac
            import hashlib

            # HMAC для проверки целостности (симметричный)
            secret = b"shared-secret"
            message = b"data"
            sig = hmac.new(secret, message, hashlib.sha256).hexdigest()

            # Проверка — compare_digest защищает от timing атак
            expected = hmac.new(secret, message, hashlib.sha256).hexdigest()
            hmac.compare_digest(sig, expected)  # True/False
            """,
        ),
        example(
            "python",
            """
            # Ed25519 (современное, быстрое, асимметричное)
            from cryptography.hazmat.primitives.asymmetric import ed25519

            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()

            sig = private_key.sign(b"message")
            public_key.verify(sig, b"message")  # исключение если неверно
            """,
        ),
        text(
            "HMAC — для проверки целостности сообщения между доверенными сторонами (API webhooks, JWT HS256). "
            "Ed25519 — для публичных подписей (проверка авторства, обновления ПО, blockchain). "
            "Всегда используйте `hmac.compare_digest` — защита от timing атак."
        ),
        heading("JWT (JSON Web Tokens)", 3),
        example(
            "bash",
            """
            pip install python-jose[cryptography]
            """,
        ),
        example(
            "python",
            """
            from jose import jwt, JWTError
            from datetime import datetime, timedelta

            SECRET = "your-256-bit-secret"  # из env, 32+ байт
            ALGORITHM = "HS256"

            def create_token(user_id: str, expires_minutes: int = 15) -> str:
                payload = {
                    "sub": user_id,
                    "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
                    "iat": datetime.utcnow(),
                    "type": "access"
                }
                return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

            def create_refresh_token(user_id: str, expires_days: int = 30) -> str:
                payload = {
                    "sub": user_id,
                    "exp": datetime.utcnow() + timedelta(days=expires_days),
                    "iat": datetime.utcnow(),
                    "type": "refresh"
                }
                return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

            def decode_token(token: str) -> dict:
                return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
            """,
        ),
        text(
            "Best practices:\n"
            "- Access token: 10-15 минут. Refresh token: 7-30 дней.\n"
            "- Храните refresh токены в БД (хешированные) или Redis с TTL для отзыва.\n"
            "- Алгоритм: HS256 (симметричный) или RS256/ES256 (асимметричный для микросервисов).\n"
            "- Всегда валидируйте `exp`, `iat`, `nbf`, `aud`, `iss` при декодировании.\n"
            "- **Никогда не кладите секреты в payload** — JWT можно декодировать без ключа (base64)."
        ),
        heading("Отзыв токенов (Redis blacklist)", 3),
        example(
            "python",
            """
            import redis
            from jose import jwt, JWTError

            redis_client = redis.Redis()
            BLACKLIST_TTL = 30 * 24 * 3600  # 30 дней

            def revoke_token(token: str):
                payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM], options={"verify_exp": False})
                jti = payload.get("jti")  # добавляйте jti при создании
                if jti:
                    redis_client.setex(f"revoked:{jti}", BLACKLIST_TTL, "1")

            def is_revoked(token: str) -> bool:
                try:
                    payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM], options={"verify_exp": False})
                    jti = payload.get("jti")
                    return bool(jti and redis_client.exists(f"revoked:{jti}"))
                except JWTError:
                    return True
            """,
        ),
        heading("Аутентификация и авторизация: веб-безопасность"),
        heading("Безопасные Cookies", 3),
        example(
            "python",
            """
            from fastapi import Response

            response.set_cookie(
                key="session",
                value=token,
                httponly=True,      # недоступен JavaScript (защита от XSS)
                secure=True,        # только HTTPS (в dev можно False)
                samesite="lax",     # CSRF защита: lax / strict / none
                max_age=3600,       # TTL в секундах
                path="/"
            )
            """,
        ),
        text(
            "`HttpOnly` — защита от кражи токена через XSS. `Secure` — только по HTTPS. "
            "`SameSite=Lax` —.cookie не отправляется при cross-site POST (CSRF защита), "
            "но отправляется при навигации по ссылке. `Strict` — строже, может ломать UX. "
            "`None` — требует `Secure`, для cross-site запросов (например, embed)."
        ),
        heading("CSRF защита", 3),
        example(
            "bash",
            """
            pip install fastapi-csrf-protect
            """,
        ),
        example(
            "python",
            """
            from fastapi_csrf_protect import CsrfProtect
            from pydantic import BaseModel

            class CsrfSettings(BaseModel):
                secret_key: str = "csrf-secret-key-from-env"

            @CsrfProtect.load_config
            def get_csrf_config():
                return CsrfSettings()

            @app.post("/form")
            def submit_form(csrf_protect: CsrfProtect = Depends()):
                csrf_protect.validate_csrf(request)
                # или в шаблоне: {{ csrf_token() }}
                ...
            """,
        ),
        text(
            "CSRF токен генерируется на сервере, кладётся в форму (hidden input) и/или "
            "в заголовок `X-CSRF-Token`. При отправке формы токен проверяется. "
            "Для SPA: токен в meta теге или куке, отправляется в заголовке каждого AJAX запроса."
        ),
        heading("Rate Limiting", 3),
        example(
            "bash",
            """
            pip install slowapi
            """,
        ),
        example(
            "python",
            """
            from slowapi import Limiter, _rate_limit_exceeded_handler
            from slowapi.util import get_remote_address
            from slowapi.errors import RateLimitExceeded
            from fastapi import Request

            limiter = Limiter(key_func=get_remote_address)
            app.state.limiter = limiter
            app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

            @app.post("/auth/login")
            @limiter.limit("5/minute")
            def login(request: Request, credentials: Credentials):
                ...

            @app.get("/api")
            @limiter.limit("100/minute")
            def api(request: Request):
                return {"ok": True}
            """,
        ),
        text(
            "Rate limiting по IP (`get_remote_address`) или по пользователю (кастомный key_func). "
            "Критично для: логин, регистрация, сброс пароля, API. Защищает от брутфорса и DDoS."
        ),
        heading("Security Headers (CSP, HSTS, X-Frame-Options)", 3),
        example(
            "python",
            """
            from fastapi import Response

            @app.middleware("http")
            async def add_security_headers(request, call_next):
                response = await call_next(request)
                response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
                response.headers["X-Frame-Options"] = "DENY"
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
                # HSTS — только если точно HTTPS везде
                # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
                return response
            """,
        ),
        text(
            "CSP — сложная, но мощная защита от XSS. Начинайте с `default-src 'self'; report-uri /csp-report`, "
            "анализируйте отчёты, постепенно ослабляйте. `X-Frame-Options: DENY` — запрет iframe. "
            "`nosniff` — запрет MIME-sniffing. HSTS — принудительный HTTPS (включайте осторожно)."
        ),
        heading("Безопасность зависимостей"),
        heading("pip-audit", 3),
        example(
            "bash",
            """
            pip install pip-audit
            pip-audit                    # сканирует установленные пакеты
            pip-audit -r requirements.txt --fix  # сканирует файл, предлагает фиксы
            pip-audit --format=json    # для CI
            """,
        ),
        heading("Safety", 3),
        example(
            "bash",
            """
            pip install safety
            safety check
            safety check -r requirements.txt --json
            """,
        ),
        heading("GitHub Dependabot", 3),
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
                  time: "09:00"
                open-pull-requests-limit: 10
                labels:
                  - "dependencies"
                  - "security"
                allow:
                  - dependency-type: "direct"
                  - dependency-type: "indirect"
            """,
        ),
        text(
            "Dependabot автоматически создаёт PR с обновлениями. Настройте `auto-merge` для patch-версий "
            "после прохождения тестов. Для security updates — `dependabot alerts` в Settings репозитория."
        ),
        heading("Sigstore / SLSA — подпись пакетов", 3),
        example(
            "bash",
            """
            pip install sigstore
            sigstore sign dist/*.tar.gz dist/*.whl
            sigstore verify dist/*.tar.gz --identity=your@email.com --github-workflow=release.yml
            """,
        ),
        text(
            "Sigstore (cosign) подписывает артефакты без управления ключами — использует OIDC (GitHub Actions, GitLab CI). "
            "SLSA (Supply Chain Levels for Software Artifacts) — фреймворк уровней защиты цепочки поставок."
        ),
        heading("Управление секретами"),
        heading("Разработка: python-dotenv", 3),
        example(
            "bash",
            """
            pip install python-dotenv
            """,
        ),
        example(
            "python",
            """
            from dotenv import load_dotenv
            import os

            load_dotenv()  # .env файл НЕ в git!
            SECRET_KEY = os.getenv("SECRET_KEY")
            DATABASE_URL = os.getenv("DATABASE_URL")
            """,
        ),
        example(
            "text",
            """
            # .env (в .gitignore!)
            SECRET_KEY=super-secret-key-256-bit
            DATABASE_URL=postgresql://user:pass@localhost/db
            REDIS_URL=redis://localhost:6379/0
            """,
        ),
        text(
            "Всегда добавьте `.env` в `.gitignore`. Используйте `.env.example` с пустыми значениями "
            "для документации требуемых переменных."
        ),
        heading("Продакшн: Secret Managers", 3),
        example(
            "python",
            """
            # AWS Secrets Manager
            import boto3
            import json

            client = boto3.client('secretsmanager', region_name='us-east-1')
            secret = client.get_secret_value(SecretId="prod/myapp/config")['SecretString']
            config = json.loads(secret)
            SECRET_KEY = config['SECRET_KEY']
            """,
        ),
        example(
            "python",
            """
            # HashiCorp Vault
            import hvac

            client = hvac.Client(url="https://vault.example.com", token=os.getenv("VAULT_TOKEN"))
            secret = client.secrets.kv.v2.read_secret_version(path="app/config")
            config = secret['data']['data']
            DATABASE_URL = config['DATABASE_URL']
            """,
        ),
        text(
            "Secret Manager решает: ротацию секретов, аудит доступа, шифрование в покое/в пути, "
            "динамические секреты (временные БД пользователи). Внедряйте на ранней стадии."
        ),
        heading("Аудит кода: статический анализ"),
        heading("Bandit", 3),
        example(
            "bash",
            """
            pip install bandit
            bandit -r src/
            bandit -r src/ -f json -o bandit-report.json
            bandit -r src/ --severity-level high --confidence-level high
            """,
        ),
        text(
            "Bandit проверяет: hardcoded secrets, shell injection, SQLi паттерны, "
            "небезопасные десериализации (pickle), использование MD5/SHA1, `shell=True` и др."
        ),
        heading("Semgrep", 3),
        example(
            "bash",
            """
            pip install semgrep
            semgrep --config=auto src/          # встроенные правила безопасности
            semgrep --config=p/security-audit src/  # OWASP правила
            semgrep --config=p/python src/      # Python-специфичные
            semgrep --config=auto src/ --json=semgrep-report.json
            """,
        ),
        text(
            "Semgrep — более гибкий, работает по паттернам (YAML правила). "
            "`p/security-audit` — коллекция правил для OWASP Top 10. "
            "Можно писать свои правила под проект."
        ),
        heading("Pre-commit hooks", 3),
        example(
            "yaml",
            """
            # .pre-commit-config.yaml
            repos:
              - repo: https://github.com/PyCQA/bandit
                rev: 1.7.5
                hooks:
                  - id: bandit
                    args: ["-r", "src/", "-ll"]  # только high severity
              - repo: https://github.com/returntocorp/semgrep
                rev: v1.0.0
                hooks:
                  - id: semgrep
                    args: ["--config=auto", "src/"]
              - repo: https://github.com/PyCQA/isort
                rev: 5.12.0
                hooks:
                  - id: isort
              - repo: https://github.com/psf/black
                rev: 23.7.0
                hooks:
                  - id: black
            """,
        ),
        example(
            "bash",
            """
            pip install pre-commit
            pre-commit install
            pre-commit run --all-files
            """,
        ),
        text(
            "Pre-commit запускает проверки перед каждым коммитом. CI должен тоже запускать их: "
            "`pre-commit run --all-files`. Это ловит проблемы до попадания в репозиторий."
        ),
        heading("Logging и Monitoring безопасности"),
        example(
            "python",
            """
            import logging
            import json
            from datetime import datetime

            class JSONFormatter(logging.Formatter):
                def format(self, record):
                    return json.dumps({
                        "timestamp": datetime.utcnow().isoformat(),
                        "level": record.levelname,
                        "logger": record.name,
                        "message": record.getMessage(),
                        "module": record.module,
                        "function": record.funcName,
                        "line": record.lineno,
                    })

            logging.basicConfig(level=logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(JSONFormatter())
            logging.getLogger().handlers = [handler]

            # Логирование событий безопасности
            security_logger = logging.getLogger("security")
            security_logger.warning("Failed login attempt", extra={"ip": "1.2.3.4", "user": "admin", "reason": "invalid_password"})
            security_logger.info("Password changed", extra={"user_id": "123", "ip": "1.2.3.4"})
            security_logger.error("SQL injection attempt blocked", extra={"query": "SELECT * FROM users WHERE name = 'admin'--" })
            """,
        ),
        text(
            "JSON логи удобны для SIEM (Elastic, Splunk, Datadog). "
            "Всегда логируйте: неудачные логины, смену паролей, повышение привилегий, "
            "доступ к админке, подозрительные запросы. "
            "**Никогда не логируйте пароли, токены, ключи** — используйте фильтры."
        ),
        heading("Фильтрация секретов из логов"),
        example(
            "python",
            """
            import logging
            import re

            class SecretFilter(logging.Filter):
                PATTERNS = [
                    (re.compile(r'(password|secret|token|api_key|key)=["\']?([^"\'\s]+)'), r'\1=***'),
                    (re.compile(r'Bearer\s+([A-Za-z0-9\-\._~+/]+=*)'), 'Bearer ***'),
                    (re.compile(r'(eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)'), '***JWT***'),
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
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Последствия", "Как правильно"],
            [
                ["MD5/SHA1/SHA256 для паролей", "Гигабайты хэшей в секунду на GPU", "Только argon2 / bcrypt / scrypt через passlib"],
                ["Секреты в коде / git / Dockerfile", "Утечка при коммите, CI логах", "Переменные окружения / Secret Manager"],
                ["`shell=True` в subprocess", "Command Injection (RCE)", "Список аргументов, без shell"],
                ["Отсутствие rate limiting на логин/API", "Брутфорс, DDoS, перебор паролей", "slowapi / nginx limit_req / Redis sliding window"],
                ["Логирование паролей/токенов/ключей", "Утечка секретов через логи", "Фильтры (SecretFilter), structured logging"],
                ["Старые зависимости с CVE", "Известные эксплойты", "pip-audit / safety в CI, Dependabot"],
                ["DEBUG=True в продакшене", "Стек-трейсы, конфиг в ошибках", "Отдельные settings для prod"],
                ["Отсутствие CSP / security headers", "XSS, clickjacking, MIME sniffing", "Middleware с CSP, X-Frame-Options, nosniff"],
                ["JWT без exp / без проверки подписи", "Вечный токен, подделка", "Всегда exp, iat, alg=HS256/RS256, verify=True"],
                ["Refresh токены без отзыва", "Утечка = полный доступ навсегда", "Redis blacklist / БД с TTL, ротация"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Для некоторых нужен запущенный Redis (`docker run -p 6379:6379 redis`)."
        ),
        numbered(
            "SQLi Demo: создайте FastAPI эндпоинт `/search?q=` с уязвимым raw SQL. "
            "Эксплуатируйте: `q=test' UNION SELECT username,password FROM users--`. "
            "Исправьте через параметризованный запрос.",
            "Password Hashing: реализуйте регистрацию и логин с argon2 через passlib. "
            "Добавьте проверку сложности пароля (min 12 chars, спецсимволы).",
            "JWT Auth: реализуйте access token (15 мин) + refresh token (30 дней) с отзывом через Redis. "
            "Эндпоинты: `/auth/login`, `/auth/refresh`, `/auth/logout`, `/me`.",
            "Dependency Scan: добавьте `pip-audit` и `safety` в GitHub Actions workflow. "
            "Настройте Dependabot с авто-мержем для patch версий.",
            "Secrets: создайте `.env.example`, настройте `.gitignore`. "
            "Добавьте pre-commit с bandit и semgrep. Протестируйте: закоммитьте фейковый секрет — pre-commit должен заблокировать.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            "# Уязвимый:\n"
            "GET /search?q=test' UNION SELECT username,password FROM users--\n"
            "# Результат: выдаёт таблицу users\n\n"
            "# Исправленный:\n"
            "GET /search?q=test' UNION SELECT username,password FROM users--\n"
            "# Результат: пусто или ошибка синтаксиса (параметр экранирован)",
        ),
        callout(
            "success",
            "Подсказка к заданию 3",
            "Access token создавайте с `exp=15 min`, `type=access`. Refresh — `exp=30 days`, `type=refresh`, сохраняйте `jti` в Redis с TTL. "
            "При logout добавляйте jti в blacklist. В `/auth/refresh` проверяйте blacklist и выдавайте новую пару токенов (rotation).",
        ),
        heading("Проверьте себя"),
        numbered(
            "Какие три топовые уязвимости OWASP 2021?",
            "Почему `cursor.execute(f\"SELECT * FROM t WHERE x={x}\")` опасно?",
            "Какое хэширование выбрать для паролей в 2024 и почему?",
            "В чём разница между access token и refresh token?",
            "Зачем нужны `HttpOnly`, `Secure`, `SameSite` у cookies?",
            "Как защититься от Command Injection в `subprocess`?",
            "Что делает `pip-audit` и где его запускать?",
            "Почему нельзя логировать JWT токены?",
        ),
        heading("Ответы", 3),
        numbered(
            "A01 Broken Access Control, A02 Cryptographic Failures, A03 Injection.",
            "Пользовательский ввод становится частью SQL-кода. `x=1; DROP TABLE users` выполнит DROP. Используйте параметры: `cursor.execute(\"SELECT * FROM t WHERE x=?\", (x,))`.",
            "argon2id (через passlib) — современный, memory-hard, устойчивый к GPU. bcrypt — проверенный фоллбек. Никаких MD5/SHA.",
            "Access token (10-15 мин) — для авторизации запросов. Refresh token (7-30 дней) — для получения новых access токенов без повторного логина. Refresh хранится в БД/Redis для отзыва.",
            "HttpOnly — нечитаем JS (защита от XSS кражи). Secure — только HTTPS. SameSite=Lax/Strict — защита от CSRF (не шлётся при cross-site POST).",
            "Никогда не используйте `shell=True`. Передавайте аргументы списком: `subprocess.run([\"cmd\", \"arg1\", user_input])`. Валидируйте ввод (regex).",
            "Сканирует установленные пакеты или requirements.txt на известные CVE. Запускать в CI (GitHub Actions, GitLab CI) на каждом PR и по расписанию.",
            "JWT — base64, его может декодировать любой. В логах токен = полный доступ к аккаунту. Используйте фильтры, маскируйте чувствительные поля.",
        ),
        heading("Итоги"),
        bullets(
            "OWASP Top 10 — ориентир: A01 Access Control, A02 Crypto, A03 Injection — самые критичные.",
            "SQL Injection: только параметризованные запросы. ORM (SQLAlchemy) безопасен по умолчанию.",
            "NoSQL Injection: явные операторы `$eq`, валидация типов, лучше ODM (Beanie).",
            "Command Injection: никогда `shell=True`, всегда список аргументов в `subprocess.run`.",
            "Пароли: только argon2id / bcrypt через `passlib.CryptContext`. Никаких MD5/SHA.",
            "Симметричное шифрование: Fernet (AES-128-GCM) из `cryptography`. Асимметричное: RSA-OAEP (малые данные) или гибридное.",
            "JWT: HS256/RS256, короткий access (15 мин) + долгий refresh (30 дней) с отзывом через Redis blacklist.",
            "Cookies: HttpOnly, Secure, SameSite=Lax. CSRF токены для форм. Rate limiting на чувствительные эндпоинты.",
            "Security Headers: CSP, X-Frame-Options, nosniff, Referrer-Policy. HSTS — осторожно.",
            "Зависимости: pip-audit + safety в CI, Dependabot для авто-PR, Sigstore для подписи релизов.",
            "Секреты: .env для dev (в .gitignore), Vault / AWS Secrets Manager для продакшена. Ротация, аудит.",
            "Статический анализ: bandit (Python-специфичный), semgrep (паттерны, OWASP). Pre-commit + CI.",
            "Логирование безопасности: JSON формат, отдельный logger `security`, фильтрация секретов из логов.",
        ),
        heading("Что дальше"),
        text(
            "Безопасность — процесс, а не чек-лист. В следующем уроке разберём DevOps и CI/CD: "
            "контейнеризация (Docker, multi-stage), Kubernetes основы, GitHub Actions / GitLab CI, "
            "blue-green деплой, наблюдаемость (metrics, logs, traces), disaster recovery."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "OWASP Top 10 — owasp.org/www-project-top-ten/",
            "OWASP Python Security — owasp.org/www-project-python-security/",
            "Cryptography.io — cryptography.io/ (hazmat primitives)",
            "passlib — passlib.readthedocs.io/",
            "Bandit — bandit.readthedocs.io/",
            "Semgrep Rules — semgrep.dev/explore",
            "Sigstore — sigstore.dev/",
            "SLSA — slsa.dev/",
            "NIST Secure SDLC — csrc.nist.gov/projects/secure-software-development-framework",
        ),
    ],
}