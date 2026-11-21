"""Урок 2.10 курса JavaScript: безопасность и производительность."""

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
    "program_order": 2,
    "topic_order": 10,
    "name": "2.10. Безопасность и производительность",
    "slug": "javascript-2-10-безопасность-и-производительность",
    "short_description": (
        "Распространённые веб-уязвимости и их защита в JavaScript, а также "
        "практическая оптимизация загрузки, кэширования и времени выполнения кода."
    ),
    "topic_name": "Безопасность и производительность",
    "topic_description": (
        "Обзор атак XSS, CSRF и кликджекинга, защитные заголовки CSP и безопасная работа "
        "с куками, а затем — измерение веб-производительности, критический путь рендеринга, "
        "разделение бандла, кэширование и профилирование кода."
    ),
    "learning_objectives": [
        "Распознавать три вида XSS и безопасно вставлять пользовательские данные в DOM",
        "Настраивать Content Security Policy с nonce и параллельно включать защитные HTTP-заголовки",
        "Защищать сессионные куки флагами HttpOnly, Secure и SameSite и понимать основы CSRF-защиты",
        "Объяснять метрики Core Web Vitals и измерять их из JavaScript через PerformanceObserver",
        "Правильно подключать скрипты с defer и async и не блокировать критический путь рендеринга",
        "Уменьшать объём JavaScript через code splitting и tree shaking и настраивать долгое кэширование",
        "Находить узкие места кода с помощью профилирования, кеширования и устранения лишней работы",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "javascript",
        "безопасность",
        "xss",
        "csp",
        "производительность",
        "web-vitals",
        "оптимизация",
    ],
    "starter_code": code(
        r"""
        // Безопасный вывод пользовательских данных на страницу.
        const input = document.querySelector('#comment');
        const list = document.querySelector('#comments');

        function renderComment(rawText) {
          const item = document.createElement('li');
          // textContent вставляет данные как текст, а не как разметку
          item.textContent = rawText.trim();
          return item;
        }

        document.querySelector('#send').addEventListener('click', () => {
          const value = input.value;
          if (!value.trim()) return;
          list.append(renderComment(value));
          input.value = '';
        });
        """
    ),
    "hints": [
        "Если нужно вставить HTML, сначала пропустите строку через DOMPurify.sanitize(), а не через innerHTML напрямую.",
        "Systemfonts: до загрузки веб-шрифта используйте font-display: swap с запасным системным стеком.",
        "При кешировании: файлы с хешем в имени можно кешировать на год с директивой immutable, а HTML — никогда.",
        "Кешируйте результат тяжёлых вычислений через Map или WeakMap, если одни и те же входные данные повторяются.",
    ],
    "content": [
        text(
            "Веб-приложение одновременно открыто тысячам людей, часть которых может быть "
            "злоумышленниками. JavaScript выполняется в браузере и имеет доступ к сессии "
            "пользователя, поэтому ошибка в одном обработчике способна превратить безобидную "
            "форму комментариев в точку входа для атаки.\n\n"
            "Вторая часть урока посвящена производительности: если страница долго показывает "
            "белый экран или интерфейс «дёргается» при загрузке, качество кода уже не имеет "
            "значения. Браузер сообщает точные метрики, а инструменты разработчика показывают, "
            "какой ресурс или фрагмент кода тормозит.\n\n"
            "Обе темы связаны: директивы вроде CSP влияют на то, какие скрипты загрузятся, "
            "а code splitting сокращает количество кода, которому вы доверяете."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "распознавать три вида XSS и безопасно вставлять пользовательские данные в DOM;",
            "настраивать Content Security Policy с nonce и подключать защитные HTTP-заголовки;",
            "защищать сессионные куки флагами HttpOnly, Secure и SameSite и понимать основы CSRF-защиты;",
            "объяснять метрики Core Web Vitals и измерять их из JavaScript через PerformanceObserver;",
            "правильно подключать скрипты с defer и async и не блокировать критический путь рендеринга;",
            "уменьшать объём JavaScript через code splitting и tree shaking и настраивать долгое кэширование;",
            "находить узкие места кода с помощью профилирования, кеширования и устранения лишней работы.",
        ),
        heading("XSS: главная угроза для динамических страниц"),
        text(
            "XSS (Cross-Site Scripting, межсайтовый скриптинг) — внедрение чужого кода в страницу, "
            "которую просматривает другой пользователь. Если приложение вставляет полученную строку "
            "в HTML без проверки, злоумышленник пришлёт тег со скриптом, и код выполнится с правами "
            "вашего сайта.\n\n"
            "Различают три вида. **Reflected** — код приходит в параметрах URL и сразу отражается в "
            "ответе, например в строке поиска. **Stored** — код сохраняется в базе в отзывах и "
            "выполняется у всех посетителей; этот вид опаснее всего. **DOM-based** — JavaScript читает "
            "данные из `location` и передаёт их в `innerHTML`, не обращаясь к серверу."
        ),
        example(
            "javascript",
            """
            // ОПАСНО: строка из внешнего источника превращается в разметку
            const userInput = '<img src=x onerror="alert(document.cookie)">';
            document.querySelector('#output').innerHTML = userInput;

            // БЕЗОПАСНО: textContent экранирует угловые скобки и кавычки
            document.querySelector('#output').textContent = userInput;

            // БЕЗОПАСНО: создаём элемент и заполняем только текст
            const paragraph = document.createElement('p');
            paragraph.textContent = userInput;
            document.querySelector('#output').append(paragraph);
            """,
        ),
        text(
            "Вывод: в первом варианте браузер разбирает строку как HTML и выполняет `onerror`. Второй "
            "и третий показывают её как есть: `textContent` — безопасный приём по умолчанию."
        ),
        heading("Безопасная работа с HTML"),
        text(
            "Иногда разметка нужна по требованию продукта: пользователь пишет пост с выделением, "
            "списками и ссылками. Тогда применяют санитизацию — удаление опасных конструкций. "
            "Библиотека DOMPurify разбирает строку в изолированном документе и оставляет только "
            "элементы и атрибуты из белого списка, удаляя теги `script`, обработчики `on*` и "
            "схемы `javascript:`."
        ),
        example(
            "javascript",
            """
            import DOMPurify from 'dompurify';

            // Разрешаем только базовое оформление
            const config = {
              ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'ul', 'li', 'a'],
              ALLOWED_ATTR: ['href', 'title'],
            };

            function renderRichText(rawHtml) {
              const clean = DOMPurify.sanitize(rawHtml, config);
              document.querySelector('#post-body').innerHTML = clean;
              // Ссылки ведут прочь только по явному нажатию
              document.querySelectorAll('#post-body a').forEach((link) => {
                link.setAttribute('rel', 'noopener noreferrer');
                link.setAttribute('target', '_blank');
              });
            }

            renderRichText('<p>Привет</p><img src=x onerror=alert(1)>');
            """,
        ),
        text(
            "Вывод: в контейнер попадёт только `<p>Привет</p>`. Тег `img` с `onerror` удаляется "
            "целиком, потому что не входит в белый список. Атрибут `rel=\"noopener noreferrer\"` "
            "не даёт открытой ссылке доступ к `window.opener`."
        ),
        text("Правила для пользовательского контента:"),
        bullets(
            "используйте `textContent` и `createElement` везде, где разметка не нужна;",
            "выводите HTML только после санитизации на проверенном белом списке;",
            "не создавайте обработчики событий через строку атрибута и не передавайте `onclick` из данных;",
            "валидируйте и нормализуйте URL: разрешайте схемы `http`, `https`, отбрасывайте `javascript:` и `data:`;",
            "при вставке во фрейм или сторонний виджет помните, что `innerHTML` в чужих окнах тоже опасен.",
        ),
        callout(
            "warning",
            "innerHTML никогда не безопасен с внешними данными",
            "Даже если данные «приходят с вашего сервера», их мог записать пользователь на предыдущем шаге. "
            "XSS через хранимую заметку попадёт ко всем, кто её открыл. Санитизация обязательна для любого HTML, "
            "прошедшего через пользователя."
        ),
        heading("Content Security Policy"),
        text(
            "Content Security Policy (CSP) — HTTP-заголовок, который сообщает браузеру, из каких "
            "источников можно загружать скрипты, стили, изображения и шрифты. Если в страницу попал "
            "чужой тег `script`, браузер откажется его исполнять. CSP — второй слой защиты: она не "
            "заменяет экранирование, но резко снижает последствия ошибки.\n\n"
            "Политика состоит из директив; `default-src` — запасное значение, `'self'` разрешает "
            "только ваш домен, а `script-src` ограничивает исполнение JavaScript."
        ),
        table(
            ["Директива", "Что ограничивает", "Типичное значение"],
            [
                ["`default-src`", "все типы ресурсов по умолчанию", "`'self'`"],
                ["`script-src`", "подключаемые и инлайн-скрипты", "`'self' 'nonce-abc123'`"],
                ["`style-src`", "таблицы стилей, инлайн-стили", "`'self' https://fonts.googleapis.com`"],
                ["`img-src`", "изображения", "`'self' data: https:`"],
                ["`connect-src`", "`fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`", "`'self' https://api.example.com`"],
                ["`frame-ancestors`", "кто может встроить страницу во фрейм", "`'none'`"],
                ["`form-action`", "куда могут отправляться формы", "`'self'`"],
            ],
        ),
        text(
            "Инлайн-скрипты без атрибута `src` при строгой политике запрещены: именно они чаще всего "
            "являются результатом XSS. Чтобы разрешить легитимный код, сервер генерирует для каждого "
            "ответа случайный nonce (одноразовое число) и добавляет его в заголовок и в атрибут тега. "
            "Внедряйте политику поэтапно: сначала в режиме `Report-Only`, затем в блокирующем."
        ),
        example(
            "javascript",
            """
            import crypto from 'node:crypto';

            // В реальном приложении nonce создаётся на каждый HTTP-запрос
            const nonce = crypto.randomBytes(16).toString('base64');

            const policy = [
              "default-src 'self'",
              `script-src 'self' 'nonce-${nonce}' https://cdn.example.com`,
              "style-src 'self' https://fonts.googleapis.com",
              "img-src 'self' data: https:",
              "connect-src 'self' https://api.example.com",
              "frame-ancestors 'none'",
              "base-uri 'self'",
              "form-action 'self'",
            ].join('; ');

            console.log(policy);
            console.log(`<script nonce="${nonce}" src="/app.js"></script>`);
            """,
        ),
        text(
            "Вывод: в консоль попадёт строка политики `default-src 'self'; ...` и тег script "
            "с nonce-значением из неё; это значение меняется на каждом запросе."
        ),
        heading("Смежные заголовки и защита зависимостей"),
        text(
            "Другие заголовки закрывают отдельные векторы. Clickjacking (кликджекинг) — наложение "
            "прозрачного фрейма поверх вашей кнопки: пользователь думает, что нажимает «Ок», а "
            "подтверждает перевод. Защита — `frame-ancestors 'none'` или `X-Frame-Options: DENY`. "
            "`nosniff` запрещает угадывать тип файла, `Referrer-Policy` ограничивает утечку адресов.\n\n"
            "Большая часть инцидентов происходит в устаревших зависимостях: `npm audit` проверяет пакеты "
            "по базе уязвимостей, Dependabot обновляет их автоматически. Для файлов с чужого CDN "
            "используйте SRI: атрибут `integrity` гарантирует совпадение файла с хэшем."
        ),
        example(
            "html",
            """
            <!-- Файл с внешнего CDN должен совпасть с хэшем, иначе браузер его не исполнит -->
            <script
              src="https://cdn.example.com/lib-2.4.0.min.js"
              integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
              crossorigin="anonymous"></script>
            """,
        ),
        text(
            "Вывод: если файл изменился и хэш не совпал, браузер не выполнит скрипт. Хэш обновляют "
            "вместе с версией."
        ),
        heading("Куки, сессии и CSRF"),
        text(
            "Куки — пары «имя = значение», которые браузер прикладывает к запросам. В них обычно "
            "хранится идентификатор сессии, то есть фактически пароль пользователя. `HttpOnly` делает "
            "куку невидимой для `document.cookie`, поэтому украденный при XSS скрипт не прочтёт её, "
            "а `Secure` запрещает передачу по HTTP.\n\n"
            "CSRF (Cross-Site Request Forgery) — атака, при которой чужой сайт заставляет браузер "
            "жертвы отправить запрос на ваш сервер, а браузер сам приложит куки. Защищает атрибут "
            "`SameSite`: `Strict` не отправляет куку с чужих сайтов, `Lax` — только при безопасной "
            "навигации методом `GET`, `None` разрешает всё и требует `Secure`."
        ),
        table(
            ["Флаг", "Смысл", "Рекомендация"],
            [
                ["`HttpOnly`", "скрипт не видит куку через `document.cookie`", "всегда для сессии"],
                ["`Secure`", "кука уходит только по HTTPS", "всегда"],
                ["`SameSite=Strict`", "кука не отправляется с чужих сайтов", "для чувствительных операций"],
                ["`SameSite=Lax`", "работает безопасная навигация по ссылке", "разумное значение по умолчанию"],
                ["`SameSite=None`", "кука уходит всегда", "только вместе с `Secure` и осознанно"],
                ["`Max-Age`", "срок жизни в секундах", "короткий для сессии"],
            ],
        ),
        example(
            "javascript",
            """
            // Серверная функция установки сессионной куки (фреймворк Express)
            function setSessionCookie(res, sessionId) {
              res.cookie('session', sessionId, {
                httpOnly: true,   // недоступна для JavaScript
                secure: true,     // только по HTTPS
                sameSite: 'lax',  // не отправляется в межсайтовом POST
                path: '/',
                maxAge: 60 * 60,  // час
              });
            }

            // Атрибуты, которые увидит браузер в заголовке ответа
            setSessionCookie({ cookie(name, value, options) {
              const flags = Object.entries(options)
                .map(([key, val]) => (val === true ? key : `${key}=${val}`))
                .join('; ');
              console.log(`Set-Cookie: ${name}=${value}; ${flags}`);
            } }, 'abc123');
            """,
        ),
        text(
            "Вывод: `Set-Cookie: session=abc123; httpOnly; secure; sameSite=lax; path=/; maxAge=3600`. "
            "Помимо `SameSite`, сервер проверяет CSRF-токен из заголовка; сторонний сайт его не "
            "прочитает, поэтому поддельный запрос получит код 403."
        ),
        callout(
            "danger",
            "Куки без флагов — уязвимость по умолчанию",
            "Сессионная кука с одним только `Max-Age` отправляется по HTTP и читается из JavaScript. "
            "XSS-скрипт украдёт её, а CSRF-атака пройдёт проверку, потому что браузер приложит её "
            "к межсайтовому POST. Всегда ставьте `HttpOnly`, `Secure` и `SameSite`."
        ),
        heading("Core Web Vitals: измеряем то, что чувствует пользователь"),
        text(
            "Core Web Vitals — метрики, отражающие ощущения пользователя. **LCP** (Largest Contentful "
            "Paint) показывает, когда появился самый крупный элемент первого экрана; хорошо — до "
            "2,5 секунды. **CLS** (Cumulative Layout Shift) измеряет визуальную стабильность, хорошо — "
            "до 0,1. **INP** (Interaction to Next Paint) оценивает задержку ответа на действие, цель — "
            "до 200 миллисекунд. Метрика FID заменена на INP. Вспомогательные **TTFB** и **FCP** "
            "объясняют причины. Значения берут из реальных сессий, а не из лаборатории."
        ),
        table(
            ["Метрика", "Хорошо", "Плохо", "Что измеряет"],
            [
                ["LCP", "до 2,5 с", "больше 4 с", "скорость загрузки главного контента"],
                ["INP", "до 200 мс", "больше 500 мс", "отзывчивость на взаимодействие"],
                ["CLS", "до 0,1", "больше 0,25", "визуальная стабильность"],
                ["FCP", "до 1,8 с", "больше 3 с", "первый отрисованный контент"],
                ["TTFB", "до 800 мс", "больше 1,8 с", "скорость ответа сервера"],
            ],
        ),
        text(
            "LCP и CLS измеряют через `PerformanceObserver` — встроенный API, который подписывается на "
            "события производительности, без сторонних библиотек."
        ),
        example(
            "javascript",
            """
            function observeVitals(emit) {
              const seen = {};

              new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                  seen.lcp = entry.startTime; // последний крупный элемент
                }
              }).observe({ type: 'largest-contentful-paint', buffered: true });

              new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                  if (entry.hadRecentInput) continue;
                  seen.cls = (seen.cls ?? 0) + entry.value;
                }
              }).observe({ type: 'layout-shift', buffered: true });

              addEventListener('visibilitychange', () => {
                if (document.visibilityState !== 'hidden') return;
                emit({
                  lcp: Math.round(seen.lcp ?? 0),
                  cls: Number((seen.cls ?? 0).toFixed(3)),
                });
              });
            }

            observeVitals((metrics) => console.log('vitals', metrics));
            """,
        ),
        text(
            "Вывод при уходе со страницы: `vitals { lcp: 1840, cls: 0.023 }`. LCP в хорошем диапазоне, "
            "CLS близок к нулю. Отправка при `visibilitychange` — последний надёжный момент, чтобы "
            "не потерять данные ещё открытой страницы."
        ),
        heading("Критический путь рендеринга"),
        text(
            "Прежде чем пользователь увидит страницу, браузер строит DOM из HTML, CSSOM из CSS, "
            "объединяет их в дерево рендеринга, вычисляет расположение (layout), рисует пиксели "
            "(paint) и собирает слои (composite). Внешние ресурсы могут остановить эту цепочку. "
            "Синхронный тег `script` блокирует парсинг: браузер обязан скачать и выполнить его сразу.\n\n"
            "Атрибуты подключения это меняют. `defer` скачивает скрипт параллельно и выполняет после "
            "разбора HTML в исходном порядке. `async` выполняет сразу после загрузки, порядок не "
            "гарантирован. Модули `type=\"module\"` ведут себя как `defer`. Для аналитики годится "
            "`async`, для кода приложения — `defer`. CSS тоже блокирует отрисовку, поэтому критический "
            "стиль первого экрана встраивают в HTML, а для шрифтов применяют `font-display: swap`."
        ),
        example(
            "html",
            """
            <head>
              <meta charset="utf-8">
              <title>Магазин</title>

              <!-- defer: скачивается параллельно, выполняется после разбора HTML -->
              <script defer src="/app.js"></script>

              <!-- async: не блокирует, порядок не гарантирован -->
              <script async src="https://analytics.example.com/t.js"></script>

              <!-- шрифт и главное изображение загружаются раньше -->
              <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
              <link rel="preconnect" href="https://api.example.com">
            </head>
            <body>
              <img src="/hero.webp" width="1200" height="600" alt="Витрина" fetchpriority="high">
              <img src="/photo-1.webp" width="400" height="300" alt="Товар" loading="lazy">
            </body>
            """,
        ),
        text(
            "Вывод: браузер сразу ставит `app.js` в очередь загрузки, продолжая строить DOM, а выполняет "
            "после закрывающего `body`. Аналитика грузится в фоне. У главного изображения заданы "
            "`width` и `height`, поэтому место резервируется заранее и CLS не растёт; картинки ниже "
            "первого экрана загружаются по требованию."
        ),
        table(
            ["Подключение", "Блокирует разбор", "Порядок", "Когда использовать"],
            [
                ["`<script src>`", "да", "по порядку", "редко, только для крошечного критичного кода"],
                ["`<script defer src>`", "нет", "по порядку", "основной скрипт приложения"],
                ["`<script async src>`", "нет", "не гарантирован", "независимая аналитика и реклама"],
                ["`type=\"module\"`", "нет", "по порядку", "современный код с `import`"],
            ],
        ),
        heading("Меньше JavaScript: code splitting и tree shaking"),
        text(
            "Чем больше JavaScript, тем дольше скачивание, разбор и исполнение, а на слабом устройстве "
            "именно разбор кода часто становится причиной медленного INP. Бандл — собранный из модулей "
            "файл, который отдаётся браузеру.\n\n"
            "**Tree shaking** удаляет код, который никто не импортировал. Он работает с ES-модулями "
            "`import`/`export`: сборщик статически видит, какие экспорты используются. Условие — модули "
            "без побочных эффектов, о чём сообщает флаг `sideEffects: false`. **Code splitting** "
            "разбивает бандл на части по требованию: `import()` возвращает промис с модулем и запускает "
            "отдельный запрос, поэтому код личного кабинета не попадает на главную."
        ),
        example(
            "javascript",
            """
            // Модуль отчётности загружается только когда пользователь открыл отчёты
            async function openReports() {
              const button = document.querySelector('#reports');
              button.disabled = true;

              try {
                const { renderReport } = await import('./reports.js');
                renderReport(document.querySelector('#panel'));
              } catch (error) {
                console.error('Не удалось загрузить модуль отчётов', error);
              } finally {
                button.disabled = false;
              }
            }

            document.querySelector('#reports').addEventListener('click', openReports);
            """,
        ),
        text(
            "Вывод: при первом открытии вкладки в сетевой панели появится запрос вида "
            "`reports-4f2c1a.js`. Начальный бандл его не содержит, поэтому главная загружается быстрее. "
            "При сбое сети `catch` сообщит об ошибке, а кнопка снова станет активной."
        ),
        callout(
            "info",
            "Tree shaking требует сборку в production",
            "В режиме разработки сборщик сохраняет читаемые имена и не удаляет неиспользуемый код. "
            "Проверяйте размер бандла только на production-сборке, где включена минификация и "
            "оптимизация модулей."
        ),
        heading("Кэширование и доставка ресурсов"),
        text(
            "Повторный визит не должен заново скачивать всю статику: этим управляет заголовок "
            "`Cache-Control`. Файлы с хэшем в имени (`app-4f2c1a.js`) при изменении получают новое имя, "
            "поэтому их кэшируют надолго: `max-age=31536000, immutable`. HTML с долгим кэшем станет "
            "ловушкой, поэтому страницы отдают с `no-cache` и проверяют по `ETag`. Директива "
            "`stale-while-revalidate` показывает сохранённую копию сразу, а обновление запрашивает в фоне.\n\n"
            "**Service Worker** — скрипт в фоне независимо от страницы; он перехватывает запросы и "
            "отдаёт их из кэша, что даёт работу без сети. Изображения дают больше всего байтов, поэтому "
            "для них используют `avif` и `webp`, `width` и `height` против сдвигов и `srcset` под размер экрана."
        ),
        example(
            "http",
            """
            # Файл с хэшем в имени: кэшируем на год
            Cache-Control: public, max-age=31536000, immutable

            # HTML: всегда проверяем актуальность
            Cache-Control: no-cache
            ETag: "8f2c1a"

            # API: отдаём мгновенно, обновляем в фоне
            Cache-Control: public, max-age=300, stale-while-revalidate=86400
            """,
        ),
        text(
            "Вывод: при повторном запросе к HTML браузер отправит `If-None-Match: \"8f2c1a\"` и, если "
            "файл не менялся, получит 304 Not Modified без тела. Запрос к API вернётся из кэша сразу "
            "и обновится в фоне."
        ),
        example(
            "html",
            """
            <picture>
              <source srcset="hero.avif" type="image/avif">
              <source srcset="hero.webp" type="image/webp">
              <img src="hero.jpg" width="1200" height="600" alt="Витрина"
                   fetchpriority="high" decoding="async">
            </picture>

            <img src="card.webp"
                 srcset="card-400.webp 400w, card-800.webp 800w"
                 sizes="(max-width: 600px) 100vw, 400px"
                 width="400" height="300" alt="Карточка товара" loading="lazy">
            """,
        ),
        text(
            "Вывод: браузер выберет первый поддерживаемый формат из `picture`, а во втором теге — "
            "версию 400 или 800 пикселей по ширине экрана. `width` и `height` предотвращают сдвиг."
        ),
        heading("Профилирование и оптимизация кода"),
        text(
            "Метрики показывают, что страница медленная, но не объясняют почему. Для этого служит панель "
            "Performance в DevTools: Record, взаимодействие со страницей, анализ. Ищите длинные задачи "
            "дольше 50 миллисекунд — они занимают главный поток и не дают реагировать на ввод. Типичные "
            "причины: принудительный пересчёт стилей (чтение `offsetHeight` сразу после записи в DOM), "
            "обработчик прокрутки без ограничения частоты и частая сборка мусора. Lighthouse запускает "
            "набор проверок и выдаёт отчёт; в CI его подключают, чтобы регрессия ломала сборку."
        ),
        example(
            "javascript",
            """
            // Плохо: обработчик выполняет тяжёлую работу на каждое движение
            window.addEventListener('resize', () => {
              document.querySelector('#w').textContent = layoutEverything();
            });

            // Хорошо: не чаще одного раза за кадр
            let pending = false;
            window.addEventListener('resize', () => {
              if (pending) return;
              pending = true;
              requestAnimationFrame(() => {
                document.querySelector('#w').textContent = layoutEverything();
                pending = false;
              });
            });

            function layoutEverything() {
              return `${window.innerWidth} x ${window.innerHeight}`;
            }
            """,
        ),
        text(
            "Вывод: строка `1600 x 900`. При быстром изменении размера функция запускается один "
            "раз за кадр. Это троттлинг (throttling) — ограничение частоты вызовов."
        ),
        text(
            "Ускорять имеет смысл только то, что действительно дорого. Кеширование результата функции "
            "для повторяющихся аргументов называется мемоизацией: результат складывают в `Map` или "
            "`WeakMap` и возвращают при повторном вызове."
        ),
        example(
            "javascript",
            """
            function memoize(fn) {
              const cache = new Map();
              let hits = 0;
              let misses = 0;

              const wrapped = (arg) => {
                if (cache.has(arg)) {
                  hits += 1;
                  return cache.get(arg);
                }
                misses += 1;
                const value = fn(arg);
                cache.set(arg, value);
                return value;
              };

              wrapped.stats = () => ({ hits, misses, size: cache.size });
              return wrapped;
            }

            const slowSquare = (n) => {
              let sum = 0;
              for (let i = 0; i < 1e6; i += 1) sum += n;
              return n * n;
            };

            const fastSquare = memoize(slowSquare);
            console.log(fastSquare(12));
            console.log(fastSquare(12));
            console.log(fastSquare.stats());
            """,
        ),
        text(
            "Вывод: `144`, снова `144`, затем `{ hits: 1, misses: 1, size: 1 }`. Цена мемоизации — "
            "память: для объектов выбирайте `WeakMap`."
        ),
        callout(
            "success",
            "Сначала измеряйте, потом оптимизируйте",
            "Оптимизация без профиля — угадывание. Запустите Performance или Lighthouse, найдите функцию, "
            "которая занимает больше всего времени, и только потом меняйте её. Повторное измерение покажет, "
            "помогло ли изменение."
        ),
        heading("Стратегия защиты и скорости в одном проекте"),
        text(
            "Слои защиты не мешают скорости, если выстроить их по порядку: экранирование данных, строгая "
            "CSP с nonce (заодно исключает тяжёлые сторонние скрипты), code splitting и кэширование, "
            "затем профилирование. Проверяйте защиту регулярно: `npm audit` в CI и аудит CSP при "
            "добавлении нового сервиса."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["`innerHTML` с пользовательскими данными", "XSS: выполняется чужой скрипт в вашем сайте", "`textContent` или `DOMPurify.sanitize`"],
                ["Нет заголовка CSP", "Одна инъекция сразу даёт выполнение кода", "Строгая политика с nonce и белым списком"],
                ["Куки без `HttpOnly` и `SameSite`", "XSS читает сессию, CSRF проходит проверку", "`HttpOnly; Secure; SameSite=Lax`"],
                ["Синхронные скрипты в `head`", "Парсинг HTML останавливается до загрузки кода", "`defer`, `async` или модули"],
                ["`loading=\"lazy\"` на изображении LCP", "Главное изображение загружается с задержкой", "Lazy только для элементов ниже первого экрана"],
                ["Один огромный бандл", "Медленный разбор даже неиспользуемых страниц", "Динамический `import()` и tree shaking"],
                ["Долгий кэш для HTML", "Пользователь не получает новые версии", "`no-cache` и `ETag` для HTML, `immutable` для хешированных файлов"],
                ["Обработчик прокрутки без троттлинга", "Длинные задачи, интерфейс тормозит", "`requestAnimationFrame` или ограничение частоты"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Проверяйте результат в консоли и панелях Network "
            "и Performance инструментов разработчика."
        ),
        numbered(
            "Безопасный вывод: создайте форму комментария и выведите его через `textContent`. Введите строку с тегом и убедитесь, что она отображается как текст, а не выполняется.",
            "Санитизация: подключите DOMPurify и разрешите только теги `b`, `i`, `em`, `p`, `a`. Проверьте строку с тегом `script` и обработчиком `onerror` — оба должны исчезнуть.",
            "CSP: напишите функцию, собирающую заголовок политики с nonce. Соберите политику дважды и убедитесь, что значение nonce меняется.",
            "Куки: реализуйте функцию установки сессионной куки и напечатайте итоговый заголовок `Set-Cookie` со всеми флагами.",
            "Производительность: замените обработчик `resize` на вариант с `requestAnimationFrame` и посчитайте в консоли, сколько раз он сработал при одном изменении размера.",
        ),
        example(
            "javascript",
            """
            // Ожидаемый результат для третьего задания
            function buildCsp(nonce) {
              return [
                "default-src 'self'",
                `script-src 'self' 'nonce-${nonce}'`,
                "frame-ancestors 'none'",
              ].join('; ');
            }

            console.log(buildCsp('abc123'));
            console.log(buildCsp('def456'));
            """,
        ),
        text(
            "Вывод: `default-src 'self'; script-src 'self' 'nonce-abc123'; frame-ancestors 'none'` и "
            "вторая строка с другим nonce. Так политику генерируют на каждый запрос."
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем отличаются reflected, stored и DOM-based XSS?",
            "Зачем в CSP используется nonce и почему он должен меняться на каждом запросе?",
            "Чем `SameSite=Strict` отличается от `SameSite=Lax`?",
            "Какие три метрики образуют Core Web Vitals и какие значения считаются хорошими?",
            "Чем `defer` отличается от `async` при подключении скрипта?",
            "Почему `tree shaking` не убирает часть кода и как на это влияет поле `sideEffects`?",
        ),
        heading("Ответы", 3),
        numbered(
            "Reflected XSS приходит из параметров запроса и сразу отражается в ответе; stored XSS сохраняется на сервере и срабатывает у всех посетителей; DOM-based XSS возникает на клиенте при передаче внешних данных в опасный API вроде `innerHTML`.",
            "Nonce разрешает выполнение конкретного инлайн-скрипта в пределах одного ответа. Динамическое значение нельзя угадать или переиспользовать, поэтому внедрённый тег без этого значения будет заблокирован.",
            "`Strict` не отправляет куку при переходах с чужих сайтов вообще, включая обычные ссылки. `Lax` отправляет её при безопасной навигации методом `GET`, поэтому сессия сохраняется при переходе по ссылке, но межсайтовый `POST` остаётся защищённым.",
            "LCP до 2,5 с, INP до 200 мс и CLS до 0,1. Эти метрики отражают скорость показа главного контента, отзывчивость интерфейса и визуальную стабильность.",
            "`defer` скачивает скрипт параллельно и выполняет после разбора HTML в исходном порядке. `async` выполняет скрипт сразу после загрузки, и порядок между несколькими скриптами не гарантирован.",
            "Tree shaking удаляет только неиспользуемые экспорты модулей без побочных эффектов. По умолчанию сборщик считает модуль «грязным»; `sideEffects: false` сообщает, что импорт ничего не меняет снаружи, а список исключений оставляет файлы с эффектами, например полифилы и CSS.",
        ),
        heading("Итоги"),
        bullets(
            "XSS — внедрение скрипта в вашу страницу; по умолчанию используйте `textContent` и `createElement`, а HTML вставляйте только после санитизации.",
            "CSP с nonce ограничивает источники скриптов и служит вторым слоем защиты; вместе с ней используйте `nosniff`, `frame-ancestors` и проверку зависимостей.",
            "Сессионная кука обязательно имеет флаги `HttpOnly`, `Secure` и `SameSite`; от CSRF дополнительно проверяют токен и `Origin`.",
            "Core Web Vitals — LCP до 2,5 с, INP до 200 мс, CLS до 0,1; измеряйте их через `PerformanceObserver` на реальных пользователях.",
            "Скрипты приложения подключайте с `defer` или как модули, критический CSS и главное изображение загружайте раньше, остальные изображения — с `loading=\"lazy\"`.",
            "Объём JavaScript сокращают tree shaking и динамический `import()`; статику с хэшем кэшируйте на год, HTML проверяйте по `ETag`.",
            "Оптимизацию начинайте с профиля: длинные задачи, принудительные пересчёты стилей и лишние аллокации — главные причины медленного интерфейса.",
        ),
        heading("Что дальше"),
        text(
            "В следующем уроке вы соберёте итоговый проект курса: приложение с безопасным выводом "
            "данных, асинхронной загрузкой и настройками производительности. Продумайте заранее, "
            "какие заголовки и метрики вы проверите."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "OWASP Top 10 — обзор основных категорий веб-уязвимостей: owasp.org/www-project-top-ten",
            "MDN: Content Security Policy — справочник по директивам: developer.mozilla.org/ru/docs/Web/HTTP/CSP",
            "web.dev: Performance — практические руководства по скорости: web.dev/performance",
            "web.dev: Web Vitals — метрики и способы измерения: web.dev/vitals",
            "MDN: HTTP-кэширование — директивы Cache-Control и валидаторы: developer.mozilla.org/ru/docs/Web/HTTP/Caching",
            "Chrome for Developers: Workbox — сервис-воркеры и офлайн-кэш: developer.chrome.com/docs/workbox",
        ),
    ],
}
