"""Урок 3.8 курса JavaScript: безопасность."""

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
    "language": "javascript",
    "program_order": 3,
    "topic_order": 8,
    "name": "3.8. Безопасность",
    "slug": "javascript-3-8-безопасность",
    "short_description": (
        "Межсайтовый скриптинг и защита от него, подделка межсайтовых запросов, "
        "политика одного источника и CORS, Content Security Policy, Trusted Types и "
        "безопасность зависимостей."
    ),
    "topic_name": "Безопасность",
    "topic_description": (
        "Модель угроз браузерного и серверного JavaScript: три разновидности XSS и "
        "контекстное экранирование, CSRF и SameSite-cookie, политика одного источника "
        "и типичные ошибки CORS, Content Security Policy с nonce, Trusted Types, "
        "загрязнение прототипа, clickjacking и безопасность цепочки поставок."
    ),
    "learning_objectives": [
        "Различать отражённый, сохранённый и DOM-ориентированный XSS и находить опасные приёмники данных",
        "Экранировать данные под контекст HTML, атрибута, JavaScript, CSS и URL и очищать HTML через DOMPurify",
        "Объяснять механику CSRF и строить защиту на SameSite-cookie, синхронизирующем токене и проверке Origin",
        "Понимать политику одного источника, корректно настраивать CORS и распознавать опасные конфигурации",
        "Составлять Content Security Policy с nonce и strict-dynamic, внедрять Trusted Types и мониторинг нарушений",
        "Защищаться от загрязнения прототипа, clickjacking, открытых редиректов и атак через зависимости"
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "javascript",
        "безопасность",
        "xss",
        "csrf",
        "csp",
        "cors",
        "зависимости",
    ],
    "starter_code": code(
        """
        function escapeHtml(value) {
          return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#x27;");
        }

        function renderComment(comment) {
          return `<div class="comment">${escapeHtml(comment)}</div>`;
        }

        const dirty = '<img src=x onerror=alert(1)>';
        console.log(renderComment(dirty));
        """
    ),
    "hints": [
        "Опасен не сам текст, а место, куда он попадает: `innerHTML`, `eval`, `location.href` исполняют данные как разметку и код.",
        "Для обычного текста используйте `textContent`, а не `innerHTML`: это встроенная защита без ручного экранирования.",
        "Не отражайте заголовок `Origin` без проверки: разрешение любому источнику равносильно отказу от политики одного источника.",
        "Перед разворачиванием новой политики запустите её в режиме `Content-Security-Policy-Report-Only` и соберите отчёты о нарушениях.",
    ],
    "content": [
        text(
            "Безопасность приложения на JavaScript — свойство всей системы: разметка, клиентский "
            "код, серверные обработчики, заголовки ответа и список зависимостей образуют одну "
            "цепочку. Браузер даёт мощные механизмы — политику одного источника, ограничения на "
            "cookie, Content Security Policy, — но почти все они настроены на совместимость и "
            "включаются явно.\n\n"
            "Урок идёт от внедрения кода к защите инфраструктуры: XSS и экранирование, CSRF, "
            "политика одного источника и CORS, CSP, Trusted Types, загрязнение прототипа, "
            "clickjacking и безопасность зависимостей. Уровень advanced: нужны уверенная работа "
            "с DOM и `fetch` и знакомство с серверным кодом на Node.js."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "различать отражённый, сохранённый и DOM-ориентированный XSS и прослеживать путь данных до приёмника;",
            "находить опасные приёмники и заменять их безопасными альтернативами;",
            "экранировать данные под контекст HTML, атрибута, JavaScript и URL и очищать HTML через DOMPurify;",
            "строить защиту от CSRF на SameSite-cookie, синхронизирующем токене и проверке `Origin`;",
            "корректно настраивать CORS и распознавать опасные конфигурации;",
            "составлять Content Security Policy с nonce и `strict-dynamic` и собирать отчёты;",
            "защищаться от загрязнения прототипа, clickjacking и атак через зависимости;",
            "выбирать защитные заголовки и cookie-флаги для типового веб-приложения.",
        ),
        heading("Источники, приёмники и модель угроз"),
        text(
            "Уязвимость внедрения описывается парой «источник — приёмник». Источник (source) — "
            "недоверенные данные: параметры адресной строки, поля формы, заголовки, ответы сторонних "
            "API, содержимое базы, `postMessage`. Приёмник (sink) интерпретирует данные как код или "
            "разметку: `innerHTML`, `document.write`, `eval`, `setTimeout` со строкой, "
            "`location.href`, `script.src`. Уязвимость существует, когда данные проходят из "
            "источника в приёмник без проверки.\n\n"
            "Задача разработчика — разорвать путь или обезвредить данные: экранировать, "
            "отфильтровать по белому списку, проверить схему URL. Второе называют санитизацией "
            "(sanitization). Имя пользователя из базы — тоже недоверенные данные."
        ),
        example(
            "javascript",
            """
            // Опасные приёмники: каждый интерпретирует строку как разметку или код.
            const dangerousSinks = [
              "element.innerHTML = data",
              "element.outerHTML = data",
              "document.write(data)",
              "eval(data)",
              "setTimeout(data, 0)",
              "location.href = data",
              "script.src = data",
            ];

            for (const sink of dangerousSinks) {
              console.log(`Приёмник: ${sink}`);
            }

            // Безопасные приёмники для текста.
            console.log("Безопасно: textContent, setAttribute не для обработчиков");
            """,
        ),
        text(
            "Вывод: Приёмник: element.innerHTML = data\n"
            "Приёмник: element.outerHTML = data\n"
            "Приёмник: document.write(data)\n"
            "Приёмник: eval(data)\n"
            "Приёмник: setTimeout(data, 0)\n"
            "Приёмник: location.href = data\n"
            "Приёмник: script.src = data\n"
            "Безопасно: textContent, setAttribute не для обработчиков\n\n"
            "Такой список закрепляют правилом линтера: появление `innerHTML` требует обоснования "
            "на ревью."
        ),
        heading("Межсайтовый скриптинг: три разновидности"),
        text(
            "Межсайтовый скриптинг (Cross-Site Scripting, XSS) — внедрение чужого JavaScript в "
            "страницу жертвы. Код исполняется в контексте доверенного источника: читает cookie без "
            "флага `HttpOnly`, обращается к хранилищу, отправляет запросы от имени пользователя. "
            "Тип определяется путём данных: отражённый приходит ссылкой, сохранённый лежит в базе, "
            "DOM-ориентированный возникает в клиентском коде при чтении `location.hash` или "
            "`postMessage`.\n\n"
            "Классические векторы выглядят безобидно: `<img src=x onerror=alert(1)>`, "
            "`<svg onload=alert(1)>`. Тег `script`, добавленный через `innerHTML`, браузер по "
            "спецификации не исполняет, зато обработчики событий исполняются. Чёрные списки тегов "
            "и регулярные выражения ненадёжны: обход вроде `<ScRiPt>` всегда находится."
        ),
        table(
            ["Разновидность", "Где хранятся данные", "Типичный сценарий", "Главная мера защиты"],
            [
                ["Отражённый", "В ссылке, на сервере не остаются", "Страница поиска или ошибки", "Экранирование при рендеринге"],
                ["Сохранённый", "В базе данных", "Комментарии, профили, форумы", "Экранирование при каждом выводе"],
                ["DOM-ориентированный", "Только в браузере", "Роутер SPA, обработчик `postMessage`", "Безопасные приёмники, Trusted Types"],
            ],
        ),
        heading("Контекстное экранирование"),
        text(
            "Одно значение требует разных преобразований в зависимости от места вставки. В тексте "
            "HTML достаточно заменить `&`, `<` и `>`. В значении атрибута нужны ещё кавычки, иначе "
            "значение можно закрыть и добавить обработчик. Внутри `<script>` нужен "
            "JavaScript-экранирование: слэш, кавычки, переводы строк, а `<`, `>`, `&` заменяются на "
            "Unicode-последовательности. Для URL используют `encodeURIComponent`.\n\n"
            "React, Vue и Angular экранируют строки из шаблона автоматически. Опасность возникает "
            "там, где защиту обходят: `dangerouslySetInnerHTML` и аналогичные «сырые» вставки. "
            "Форматированный HTML очищают DOMPurify — библиотекой на разборе DOM, а не на "
            "регулярных выражениях."
        ),
        example(
            "javascript",
            """
            function escapeHtml(value) {
              return String(value)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#x27;");
            }

            function escapeJsString(value) {
              return String(value)
                .replace(/\\\\/g, "\\\\\\\\")
                .replace(/'/g, "\\\\'")
                .replace(/"/g, '\\\\"')
                .replace(/\\n/g, "\\\\n")
                .replace(/</g, "\\\\u003C")
                .replace(/>/g, "\\\\u003E")
                .replace(/&/g, "\\\\u0026");
            }

            console.log(escapeHtml('<img src=x onerror="steal()">'));
            console.log(escapeJsString("');steal();//"));
            console.log(encodeURIComponent("a b&c"));
            """,
        ),
        text(
            "Вывод: &lt;img src=x onerror=&quot;steal()&quot;&gt;\n"
            "\\');steal();//\n"
            "a%20b%26c\n\n"
            "Во второй строке видны обратные слэши перед кавычками: строка стала данными и не может "
            "закрыть литерал. Третий вызов показывает URL-кодирование: пробел стал `%20`, амперсанд "
            "— `%26`."
        ),
        callout(
            "warning",
            "Порядок замен в escapeHtml",
            "Начинайте с амперсанда. Если сначала заменить `<` на `&lt;`, а потом обработать `&`, "
            "получится `&amp;lt;`, и пользователь увидит текст `&lt;` вместо символа `<`. "
            "Правильный порядок: `&`, затем `<`, `>`, кавычки.",
        ),
        example(
            "javascript",
            """
            // Вставка обычного текста не требует ручного экранирования.
            const node = document.createElement("p");
            node.textContent = "<script>alert(1)</script>"; // останется текстом
            document.body.append(node);

            // Очистка форматированного HTML через DOMPurify.
            const dirty = '<p>Привет</p><img src=x onerror=alert(1)><a href="javascript:alert(1)">ссылка</a>';
            const clean = DOMPurify.sanitize(dirty, {
              ALLOWED_TAGS: ["b", "i", "em", "strong", "a", "p", "br"],
              ALLOWED_ATTR: ["href", "target", "rel"],
            });
            console.log(clean);
            """,
        ),
        text(
            "Вывод: <p>Привет</p><a>ссылка</a>\n\n"
            "DOMPurify разобрал строку как HTML, удалил тег `img` с обработчиком и снял у ссылки "
            "атрибут `href` с `javascript:`-схемой. Разбор настоящим парсером DOM отличает "
            "библиотеку от регулярных выражений: она видит ту же структуру, что и браузер. Три "
            "уровня защиты: `textContent`, DOMPurify для нужного HTML и CSP как последний рубеж."
        ),
        heading("Подделка межсайтовых запросов (CSRF)"),
        text(
            "Подделка межсайтовых запросов (Cross-Site Request Forgery, CSRF) использует "
            "автоматическую отправку cookie: браузер прикрепляет их к запросу на их домен "
            "независимо от страницы, которая его инициировала. Атакующий размещает форму с адресом "
            "действия на чужой домен и отправляет её скриптом, а сервер видит обычный запрос "
            "авторизованного пользователя.\n\n"
            "В отличие от XSS атакующий не читает ответы, а лишь заставляет браузер выполнить "
            "действие — перевод, смену почты, удаление записи. Возможность даёт политика одного "
            "источника: межсайтовые запросы, инициированные разметкой, разрешены."
        ),
        example(
            "http",
            """
            # Cookie сессии с рекомендованными флагами.
            Set-Cookie: session=abc123; Path=/; Secure; HttpOnly; SameSite=Lax; Max-Age=86400

            # Режимы SameSite:
            # Strict — cookie не отправляется ни при каких межсайтовых переходах
            # Lax    — отправляется при безопасной навигации, но не при POST
            # None   — отправляется везде, обязателен флаг Secure
            """,
        ),
        text(
            "Режимы `SameSite`: `Lax` не отправляет cookie при межсайтовом POST и в iframe, но "
            "отправляет при переходе по ссылке методом GET; `Strict` не отправляет ни при каких "
            "переходах, что ломает сценарий со ссылкой из письма; `None` разрешает отправку везде "
            "и требует `Secure`. `HttpOnly` закрывает cookie от JavaScript.\n\n"
            "Одного `SameSite` мало: старые браузеры его не поддерживают, а встраивание в iframe "
            "партнёра требует `SameSite=None`. Поэтому параллельно применяют синхронизирующий токен "
            "(synchronizer token): сервер выдаёт случайное значение, привязанное к сессии, клиент "
            "возвращает его в поле формы или заголовке, сервер сравнивает с сохранённым. Без "
            "серверных сессий используют двойную отправку (double submit cookie): токен кладут в "
            "доступную JavaScript cookie и дублируют в заголовке. Дополнительный слой — проверка "
            "`Origin` и нестандартный заголовок, который чужой сайт не отправит без CORS-разрешения."
        ),
        example(
            "javascript",
            """
            // Сервер на Node.js: синхронизирующий токен и проверка Origin.
            import crypto from "node:crypto";

            const sessions = new Map();

            function issueToken(sessionId) {
              const token = crypto.randomBytes(32).toString("base64url");
              sessions.set(sessionId, token);
              return token;
            }

            function checkCsrf(req) {
              const origin = req.headers.origin || req.headers.referer || "";
              if (origin && !origin.startsWith("https://app.example.com")) {
                return { ok: false, reason: "cross-origin" };
              }
              const sent = Buffer.from(req.headers["x-csrf-token"] || "");
              const expected = Buffer.from(sessions.get(req.cookies.session) || "");
              const ok = sent.length > 0
                && sent.length === expected.length
                && crypto.timingSafeEqual(sent, expected);
              return { ok, reason: ok ? "ok" : "invalid-token" };
            }

            const token = issueToken("sess-42");
            console.log(`Длина токена: ${token.length}`);
            const base = { origin: "https://app.example.com", "x-csrf-token": token };
            console.log(checkCsrf({ headers: base, cookies: { session: "sess-42" } }));
            console.log(checkCsrf({
              headers: { ...base, origin: "https://evil.example" },
              cookies: { session: "sess-42" },
            }));
            """,
        ),
        text(
            "Вывод: Длина токена: 43\n{ ok: true, reason: 'ok' }\n"
            "{ ok: false, reason: 'cross-origin' }\n\n"
            "Длина 43 объясняется кодировкой base64url без выравнивающих знаков: 32 байта дают 43 "
            "символа. `timingSafeEqual` сравнивает за постоянное время и не даёт восстановить токен "
            "по времени ответа, тогда как обычное сравнение строк завершается на первом несовпавшем "
            "байте. Токен должен быть криптографически случайным: `Math.random()` предсказуем. Для "
            "критических операций дополнительно запрашивают повторную аутентификацию."
        ),
        heading("Политика одного источника и CORS"),
        text(
            "Политика одного источника (Same-Origin Policy, SOP) изолирует данные по тройке «схема, "
            "хост, порт»: `https://example.com` и `http://example.com` различаются, как и вариант с "
            "портом `8443`. Скрипт не может прочитать чужой iframe, cookie, хранилище и тело ответа "
            "на `fetch`. Запрещено именно чтение: навигация, отправка формы и подключение скриптов, "
            "стилей и картинок работают межсайтово — отсюда и CSRF, и загрузка с CDN.\n\n"
            "Cross-Origin Resource Sharing (CORS) — механизм, которым сервер разрешает чтение своих "
            "ответов другим источникам через `Access-Control-Allow-Origin`. Для непростых запросов "
            "браузер сначала отправляет предварительный запрос (preflight) методом `OPTIONS`."
        ),
        table(
            ["Заголовок ответа", "Назначение", "Типичная ошибка"],
            [
                ["`Access-Control-Allow-Origin`", "Разрешённый источник", "Отражать любой `Origin` без проверки"],
                ["`Access-Control-Allow-Credentials`", "Передача cookie и `Authorization`", "Сочетать со звёздочкой, что запрещено"],
                ["`Access-Control-Allow-Headers`", "Разрешённые заголовки запроса", "Разрешать `*` с учётными данными"],
                ["`Access-Control-Max-Age`", "Кеш preflight в секундах", "Огромное значение при меняющейся политике"],
                ["`Vary: Origin`", "Зависимость ответа от источника для кешей", "Забывать при динамическом заголовке"],
            ],
        ),
        text(
            "Самая частая уязвимость CORS — отражение `Origin` без проверки: сервер копирует любой "
            "источник в разрешающий заголовок. Вместе с `Access-Control-Allow-Credentials: true` "
            "это позволяет любому сайту читать ответы от имени пользователя. Второй случай — "
            "источник `null`, который присылают песочницы iframe. Правильная схема — белый список "
            "конкретных источников и `Vary: Origin`."
        ),
        example(
            "javascript",
            """
            const allowedOrigins = new Set([
              "https://app.example.com",
              "https://admin.example.com",
            ]);

            function corsHeaders(origin) {
              const headers = { "Vary": "Origin" };
              if (origin && allowedOrigins.has(origin)) {
                headers["Access-Control-Allow-Origin"] = origin;
                headers["Access-Control-Allow-Credentials"] = "true";
                headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE";
                headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-CSRF-Token";
                headers["Access-Control-Max-Age"] = "600";
              }
              return headers;
            }

            console.log(corsHeaders("https://app.example.com")["Access-Control-Allow-Origin"]);
            console.log("Allow-Origin" in corsHeaders("https://evil.example"));
            console.log("Allow-Origin" in corsHeaders("null"));
            """,
        ),
        text(
            "Вывод: https://app.example.com\nfalse\nfalse\n\n"
            "`Vary: Origin` присутствует всегда: он сообщает кешам, что ответ зависит от источника. "
            "Звёздочка допустима только для простых запросов без учётных данных. Для изоляции "
            "применяют `Cross-Origin-Opener-Policy: same-origin`, обнуляющий `window.opener` для "
            "чужих попапов."
        ),
        heading("Content Security Policy"),
        text(
            "Content Security Policy (CSP) — заголовок ответа, перечисляющий, откуда странице "
            "разрешено исполнять код и загружать ресурсы. `script-src`, `style-src` и `connect-src` "
            "задают источники, `frame-ancestors` управляет встраиванием в iframe, `default-src` "
            "служит запасным вариантом.\n\n"
            "CSP — второй рубеж: при пропущенном экранировании политика не даст исполнить "
            "внедрённый скрипт, потому что встроенный код разрешён только с nonce или совпадающим "
            "хешем, а `'unsafe-inline'` обесценивает политику против XSS. Политика на nonce: сервер "
            "генерирует случайное значение для каждого ответа, подставляет его в атрибут `nonce` "
            "доверенных тегов `script` и перечисляет в заголовке. Внедрённый тег nonce не знает и "
            "блокируется, а `'strict-dynamic'` доверяет скриптам, загруженным доверенным кодом."
        ),
        example(
            "javascript",
            """
            // Сервер на Node.js: nonce на каждый запрос и строгая CSP.
            import crypto from "node:crypto";

            function cspMiddleware(req, res, next) {
              const nonce = crypto.randomBytes(16).toString("base64");
              res.locals.nonce = nonce;
              res.setHeader("Content-Security-Policy", [
                "default-src 'self'",
                `script-src 'nonce-${nonce}' 'strict-dynamic' https: 'unsafe-inline'`,
                "style-src 'self'",
                "img-src 'self' data:",
                "connect-src 'self' https://api.example.com",
                "object-src 'none'",
                "base-uri 'self'",
                "frame-ancestors 'none'",
                "form-action 'self'",
                "upgrade-insecure-requests",
              ].join("; "));
              next();
            }

            const nonce = crypto.randomBytes(16).toString("base64");
            console.log(`Длина nonce: ${nonce.length}`);
            console.log(`script-src 'nonce-${nonce.slice(0, 6)}...' 'strict-dynamic'`);
            """,
        ),
        text(
            "Вывод: Длина nonce: 24\nscript-src 'nonce-Ab12Cd...' 'strict-dynamic'\n\n"
            "Длина 24 соответствует 16 байтам в base64; значение случайно. Сочетание `https:` и "
            "`'unsafe-inline'` рядом с nonce и `strict-dynamic` — политика с обратной "
            "совместимостью: новые браузеры эти два источника игнорируют, старые используют как "
            "запасной вариант. `frame-ancestors 'none'` заменяет `X-Frame-Options`. Строгую "
            "политику сначала запускают в режиме `Content-Security-Policy-Report-Only`: браузер "
            "не блокирует, но отправляет отчёты о забытых встроенных скриптах."
        ),
        callout(
            "info",
            "CSP — это не только script-src",
            "Директивы `base-uri 'self'`, `object-src 'none'`, `form-action 'self'` и "
            "`frame-ancestors 'none'` почти не требуют усилий, но закрывают подмену базового "
            "адреса, исполнение через плагины, подделку формы и clickjacking. Начинайте с них.",
        ),
        heading("Trusted Types и загрязнение прототипа"),
        text(
            "Trusted Types превращают DOM-приёмники в контролируемые точки: с директивой "
            "`require-trusted-types-for 'script'` присваивание строки в `innerHTML` или `eval` "
            "вызывает ошибку типа, и браузер принимает только `TrustedHTML`, `TrustedScript` и "
            "`TrustedScriptURL` из политики. Обычно внутри политики стоит DOMPurify, и все пути "
            "вставки HTML проходят через одно проверенное место.\n\n"
            "Загрязнение прототипа (prototype pollution) — атака через небезопасное слияние данных: "
            "ключ `__proto__` в недоверенном JSON записывает свойство в `Object.prototype`, и оно "
            "появляется у всех объектов: код, читающий `user.isAdmin`, увидит унаследованное `true`. "
            "Защита: обновление библиотек, фильтрация ключей, `Map` и `Object.create(null)`."
        ),
        example(
            "javascript",
            """
            const UNSAFE_KEYS = new Set(["__proto__", "constructor", "prototype"]);

            function safeMerge(target, source) {
              for (const key of Object.keys(source)) {
                if (UNSAFE_KEYS.has(key)) continue;
                const value = source[key];
                const isPlain = value && typeof value === "object" && !Array.isArray(value);
                target[key] = isPlain
                  ? safeMerge(Object.create(null), { ...target[key], ...value })
                  : value;
              }
              return target;
            }

            const payload = JSON.parse('{"theme":"dark","__proto__":{"isAdmin":true}}');
            const config = safeMerge({}, payload);

            console.log(config.theme);
            console.log(config.isAdmin);
            console.log({}.isAdmin);
            """,
        ),
        text(
            "Вывод: dark\nundefined\nundefined\n\n"
            "`JSON.parse` создаёт обычный объект, но ключ `__proto__` из текста становится "
            "собственным свойством; прототип меняется при небезопасном слиянии, поэтому фильтр "
            "ключей останавливает атаку, а `theme` сохраняется. Похожая проблема — подмена "
            "глобальных переменных элементами с `id`: помогают `let` и `const` и обращение через "
            "`document.getElementById`."
        ),
        heading("Clickjacking, редиректы и цепочка поставок"),
        text(
            "Clickjacking — наложение интерфейса: чужая страница встраивает вашу в прозрачный iframe и "
            "подсовывает кнопки. Защита — `frame-ancestors 'none'` в CSP или `X-Frame-Options: DENY` "
            "для старых браузеров.\n\n"
            "Открытый редирект возникает, когда адрес из параметра используется для перехода без "
            "проверки: `https://app.example.com/redirect?url=https://evil.example` выглядит "
            "доверенной ссылкой, но уводит на фишинг. Разрешайте относительные пути или сверяйте "
            "хост с белым списком. Похожая ошибка — сборка ссылок из заголовка `Host`: адрес для "
            "сброса пароля берётся из конфигурации.\n\n"
            "Код чужого пакета исполняется с правами приложения, а тянуть его могут сотни "
            "транзитивных зависимостей; известны захват ua-parser-js в 2021 году и вредоносная "
            "зависимость в event-stream. Меры: lock-файл, аудит, `npm ci` в CI, подпись пакетов и "
            "`integrity` для ресурсов с CDN."
        ),
        example(
            "html",
            """
            <!-- Сторонний скрипт с проверкой целостности файла. -->
            <script
              src="https://cdn.example.com/lib@4.17.21/lib.min.js"
              integrity="sha384-Q3fDd0Z2a3k+sE0xT9z0dQ0hJ3aF8vK9r2mQx1T0y7Np6Lk5C4b3A2z1Y0X9W8V7"
              crossorigin="anonymous"></script>

            <!-- Защита от clickjacking задаётся заголовком ответа, а не разметкой. -->
            <!-- Content-Security-Policy: frame-ancestors 'none' -->
            <!-- X-Frame-Options: DENY -->
            """,
        ),
        text(
            "Значение `integrity` — пример base64-хеша SHA-384. Его вычисляют командой "
            "`openssl dgst -sha384 -binary lib.min.js | openssl base64 -A`: при изменении файла "
            "браузер его не исполнит. `npm audit` показывает уязвимости, `npm audit fix` обновляет "
            "в допустимых диапазонах, `npm ci` ставит ровно то, что записано в lock-файле."
        ),
        table(
            ["Механизм", "Какую угрозу закрывает", "Где настраивается"],
            [
                ["`HttpOnly`, `Secure`, `SameSite`", "Кража сессии через XSS и CSRF", "Заголовок `Set-Cookie`"],
                ["`Content-Security-Policy`", "Исполнение внедрённого кода", "Заголовок ответа сервера"],
                ["`frame-ancestors 'none'`", "Clickjacking", "CSP или `X-Frame-Options`"],
                ["`X-Content-Type-Options: nosniff`", "Исполнение файла под чужим типом", "Заголовок ответа"],
                ["`Strict-Transport-Security`", "Понижение до HTTP и перехват", "Заголовок ответа по HTTPS"],
                ["`Referrer-Policy`", "Утечка адресов во внешние ресурсы", "Заголовок ответа"],
                ["Белый список в CORS", "Чтение ответов чужим источником", "Заголовки ответа API"],
                ["`integrity` у `<script>`", "Подмена файла на CDN", "Разметка страницы"],
            ],
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["`innerHTML = userInput`", "Разметка и обработчики исполняются", "`textContent` или DOMPurify"],
                ["Регулярное выражение вместо парсера", "Фильтр обходит экзотическая разметка", "Очистка через DOMPurify"],
                ["Cookie без `HttpOnly` и `SameSite`", "Сессию крадёт XSS, действия подделывает CSRF", "`Secure; HttpOnly; SameSite=Lax`"],
                ["Токен CSRF через `Math.random()`", "Значения предсказуемы", "`crypto.randomBytes`"],
                ["Сравнение токенов через `!==`", "Токен подбирают по времени ответа", "`timingSafeEqual`"],
                ["Отражение `Origin` без проверки", "Любой сайт читает ответы с учётными данными", "Белый список и `Vary: Origin`"],
                ["`script-src 'unsafe-inline'`", "CSP не мешает внедрению скриптов", "nonce, хеш и `strict-dynamic`"],
                ["Слияние JSON без проверки ключей", "Загрязнение `Object.prototype`", "Фильтр ключей и `Object.create(null)`"],
                ["`res.redirect(req.query.url)`", "Фишинговые ссылки с вашим доменом", "Относительные пути или белый список"],
                ["Установка без lock-файла", "Незаметный переход на вредоносную версию", "`npm ci` и контроль версий"],
            ],
        ),
        heading("Практика"),
        text("Сначала воспроизведите уязвимость, затем исправьте и проверьте, что эксплуатация не проходит."),
        numbered(
            "Отражённый XSS: отрендерите комментарий через шаблонную строку и `innerHTML`, воспроизведите внедрение `<img src=x onerror=alert(1)>`, затем исправьте экранированием и покажите результат для трёх нагрузок.",
            "Очистка HTML: подключите DOMPurify, разрешите теги `b`, `i`, `em`, `strong`, `a`, `p`, `br` и атрибуты `href`, `rel`, `target`, проверьте ссылку с `javascript:`-схемой.",
            "CSRF: реализуйте синхронизирующий токен с проверкой `Origin` и сравнением через `timingSafeEqual`, затем проверьте запрос со стороннего источника.",
            "CSP: добавьте middleware с nonce и `strict-dynamic`, включите режим `Report-Only` с эндпоинтом отчётов и объясните, какие отчёты появятся при скрипте без nonce.",
            "Прототип: соберите `safeMerge` с белым списком ключей и покажите, что после строки `{\"__proto__\":{\"isAdmin\":true}}` свойство не появляется у пустого объекта.",
            "Зависимости: выполните `npm audit`, зафиксируйте число уязвимостей по серьёзности, обновите одну зависимость и сравните результат.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            "До исправления: внедрение исполнено (тег img с обработчиком)\n"
            "После исправления:\n"
            "&lt;img src=x onerror=alert(1)&gt;\n"
            "&lt;svg onload=alert(1)&gt;\n"
            "&lt;script&gt;alert(1)&lt;/script&gt;",
        ),
        callout(
            "success",
            "Подсказка к заданию 4",
            "В режиме `Report-Only` политика не блокирует скрипт без nonce, но браузер отправляет "
            "отчёт на эндпоинт. Убедитесь, что запрос отчёта виден во вкладке Network, и только "
            "потом переключайте политику в режим блокировки.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем отражённый XSS отличается от сохранённого и DOM-ориентированного?",
            "Почему `element.innerHTML = userInput` опасно, а `element.textContent = userInput` — нет?",
            "Как `SameSite=Lax` защищает от CSRF и какие сценарии он не покрывает?",
            "Что такое preflight-запрос и когда браузер его отправляет?",
            "Зачем нужен `strict-dynamic` в Content Security Policy?",
            "Что такое загрязнение прототипа и какие меры его предотвращают?",
        ),
        heading("Ответы", 3),
        numbered(
            "Отражённый XSS приходит ссылкой и исполняется у жертвы один раз; сохранённый лежит в базе и исполняется у всех посетителей; DOM-ориентированный возникает целиком в браузере, когда `location.hash` или `postMessage` попадают в приёмник.",
            "`innerHTML` разбирает строку как разметку и исполняет обработчики, а `textContent` создаёт текстовый узел, и теги остаются символами.",
            "`SameSite=Lax` не отправляет cookie при межсайтовом POST и в iframe, но отправляет при переходе по ссылке методом GET, поэтому не закрывает изменение состояния через GET и сценарии с `SameSite=None`.",
            "Запрос `OPTIONS` отправляется до основного, когда запрос непростой: нестандартный метод, заголовок `Authorization` или тип `application/json`.",
            "`strict-dynamic` доверяет скриптам, загруженным доверенным кодом с nonce: внедрённый тег блокируется, а перечисление доменов не нужно.",
            "Это запись свойств в `Object.prototype` через ключ `__proto__` при небезопасном слиянии; помогают фильтрация ключей, `Map` и `Object.create(null)`.",
        ),
        heading("Итоги"),
        bullets(
            "Уязвимость внедрения описывается парой «источник — приёмник»: `innerHTML`, `eval` и `location.href` исполняют данные, а `textContent` — нет.",
            "Все виды XSS лечатся контекстным экранированием и очисткой HTML через DOM-парсер вроде DOMPurify.",
            "CSRF опирается на автоподстановку cookie; защита — `SameSite`, синхронизирующий токен и проверка `Origin`.",
            "Политика одного источника запрещает чтение ответов чужого источника; CORS открывает чтение для белого списка и отдаёт `Vary: Origin`.",
            "CSP с nonce и `strict-dynamic` блокирует внедрённый код; внедряют её через `Report-Only`.",
            "Trusted Types переносят контроль вставки HTML на уровень платформы, а от загрязнения прототипа спасает фильтрация ключей.",
            "Цепочка поставок — часть модели угроз: lock-файлы, аудит, `npm ci` и `integrity`.",
        ),
        heading("Что дальше"),
        text(
            "Вы разобрали основные классы веб-уязвимостей и механизмы защиты. Следующий урок посвящён "
            "инженерии крупных приложений: TypeScript, отсечению неиспользуемого кода, интеграционным "
            "тестам, непрерывной поставке и мониторингу. Меры безопасности окупаются только внутри "
            "конвейера сборки, поэтому вопросы интеграции логично продолжить там."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "OWASP Top 10 — owasp.org/www-project-top-ten",
            "OWASP Cheat Sheet по предотвращению XSS — cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html",
            "OWASP Cheat Sheet по предотвращению CSRF — cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html",
            "MDN: Content Security Policy — developer.mozilla.org/ru/docs/Web/HTTP/CSP",
            "MDN: Trusted Types — developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API",
            "Лабораторные по веб-безопасности — portswigger.net/web-security",
            "npm: об аудите зависимостей — docs.npmjs.com/about-security-audits",
            "Проверка пакетов на вредоносное поведение — socket.dev",
        ),
    ],
}
