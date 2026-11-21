"""Урок 3.5 курса JavaScript: браузерная платформа."""

from content_build.lesson_kit import code, text, heading, bullets, numbered, table, callout, example


LESSON = {
    "language": "javascript",
    "program_order": 3,
    "topic_order": 5,
    "name": "3.5. Браузерная платформа",
    "slug": "javascript-3-5-браузерная-платформа",
    "short_description": (
        "Как браузер превращает HTML и CSS в пиксели, почему одни CSS-свойства дешёвые, "
        "а другие дорогие, как устроены Web Components, Service Workers и модель безопасности."
    ),
    "topic_name": "Браузерная платформа",
    "topic_description": (
        "Внутреннее устройство браузера как платформы: конвейер рендеринга и метрики "
        "Core Web Vitals, стандартные веб-компоненты с Shadow DOM, Service Workers с офлайн-кэшем, "
        "а также слои защиты — Same-Origin Policy, CORS, CSP и COOP/COEP."
    ),
    "learning_objectives": [
        "Объяснять этапы конвейера рендеринга и определять, какие CSS-свойства запускают layout и paint",
        "Устранять layout thrashing, группируя чтения и записи DOM, и выносить анимации на compositor",
        "Создавать Custom Elements с Shadow DOM, слотами и корректной очисткой ресурсов",
        "Писать Service Worker с контролем жизненного цикла и несколькими стратегиями кэширования",
        "Различать origin и site, настраивать CORS и разбирать суть preflight-запроса",
        "Проектировать CSP и объяснять, зачем нужны COOP и COEP для изоляции документов",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "javascript",
        "браузер",
        "рендеринг",
        "web-components",
        "service-worker",
        "csp",
    ],
    "starter_code": code(
        r"""
        'use strict';

        // Какие заголовки сервер должен добавить, чтобы браузер отдал ответ
        // странице с другим origin.
        function corsHeaders(origin) {
          return {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Vary': 'Origin',
          };
        }

        const headers = corsHeaders('https://app.example.com');
        for (const [name, value] of Object.entries(headers)) {
          console.log(`${name}: ${value}`);
        }
        """
    ),
    "hints": [
        "Чтение геометрии (offsetHeight, getBoundingClientRect) вызывает принудительный layout. Сначала соберите все чтения, потом выполняйте все записи.",
        "Анимируйте только transform и opacity: эти свойства обрабатывает compositor-поток, поэтому изменения не затрагивают main thread.",
        "В Custom Element обязательно отписывайтесь в disconnectedCallback от всего, что подписали в connectedCallback, иначе элементы не соберутся сборщиком мусора.",
        "Origin — это тройка схема, хост и порт. Поддомен, другой порт или другой протокол уже считаются другим origin, хотя site может совпадать.",
    ],
    "content": [
        text(
            "JavaScript в браузере работает не в пустоте: его окружает платформа, которая парсит "
            "разметку, вычисляет стили, раскладывает блоки по экрану, рисует пиксели и выполняет "
            "множество API — от наблюдателей за видимостью до сетевых прокси. Понимание этой платформы "
            "отличает код, который «работает на моём ноутбуке», от кода, который быстро запускается на "
            "слабом телефоне, продолжает работать без сети и не открывает дыр в безопасности.\n\n"
            "Уровень продвинутый, поэтому акцент будет на механизмах, а не на синтаксисе. Мы разберём, "
            "почему изменение `left` стоит в десятки раз дороже изменения `transform`, какую роль играет "
            "поток композитора, как Service Worker встаёт между страницей и сетью, и почему браузер "
            "по умолчанию запрещает странице читать чужие данные.\n\n"
            "Примеры с DOM и сетевыми API рассчитаны на браузер. Логику, не требующую DOM, можно "
            "проверить в консоли разработчика или в редакторе песочницы; для кода, работающего с "
            "документом, комментарии описывают ожидаемый результат."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "объяснять конвейер рендеринга и определять, какой этап затронет конкретное CSS-свойство;",
            "устранять layout thrashing и выносить анимации на compositor-поток;",
            "создавать Custom Elements с Shadow DOM, слотами и корректной очисткой подписок;",
            "писать Service Worker с контролем жизненного цикла и несколькими стратегиями кэширования;",
            "различать origin и site, настраивать CORS и понимать, что такое preflight-запрос;",
            "проектировать Content Security Policy и применять COOP и COEP для изоляции документов.",
        ),
        heading("Конвейер рендеринга"),
        text(
            "Браузер обрабатывает страницу конвейером из нескольких этапов. Сначала HTML-парсер строит "
            "дерево документа DOM, а CSS-парсер — дерево стилей CSSOM. Затем браузер вычисляет итоговый "
            "стиль каждого элемента: каскад, наследование и вычисление значений. Это **Style Calculation**, "
            "или пересчёт стилей (recalc style).\n\n"
            "Следующий этап — **layout** (раскладка, в старых терминах reflow): вычисление геометрии, "
            "то есть координат и размеров каждого блока. Для этого нужно знать размеры шрифтов и "
            "содержимого, поэтому layout зависит от дерева целиком. Затем **paint**: для каждого элемента "
            "формируется список команд рисования — закрасить прямоугольник, нарисовать текст, применить "
            "тень. И наконец **composite**: браузер собирает готовые слои на графическом процессоре.\n\n"
            "Важно, что этапы не равнозначны. Изменение цвета перекрашивает один элемент, изменение "
            "ширины пересчитывает геометрию, а изменение трансформации может вообще не затрагивать "
            "main thread — его обрабатывает отдельный поток композитора."
        ),
        table(
            ["Этап", "Что делает", "Типичные триггеры"],
            [
                ["Style", "Сопоставляет правила и вычисляет итоговые значения", "Изменение `class`, `style`, смена псевдокласса `:hover`, медиазапросы"],
                ["Layout", "Считает координаты и размеры", "`width`, `height`, `margin`, `padding`, `display`, `flex`, `grid`, `font-size`"],
                ["Paint", "Строит команды рисования", "`color`, `background`, `box-shadow`, `border-radius`, `visibility`"],
                ["Composite", "Собирает слои на GPU", "`transform`, `opacity` (при вынесенном слое)"],
            ],
        ),
        text(
            "Цепочка «стиль → layout → paint → composite» описывает весь путь от изменения до пикселя. "
            "Чем правее в таблице находится этап, тем дешевле обходится изменение. Именно поэтому "
            "плавные анимации строят на `transform` и `opacity`: эти свойства можно изменять, не "
            "пересчитывая геометрию и не перерисовывая элементы заново."
        ),
        heading("Layout thrashing и принудительный layout"),
        text(
            "Обычно браузер выполняет layout лениво, пачками, между задачами. Но если скрипт читает "
            "геометрию, например `offsetHeight` или `getBoundingClientRect()`, браузер обязан отдать "
            "точное значение прямо сейчас — и выполняет layout синхронно. Если в цикле чередовать "
            "такие чтения с записями в стили, браузер будет пересчитывать layout на каждом шаге. "
            "Этот антипаттерн называют **layout thrashing** (раскачка раскладки).\n\n"
            "Лекарство одно: разделять фазы. Сначала собираем все измерения в переменные, затем "
            "применяем все изменения. Ниже показан синтетический пример: функция `measure` имитирует "
            "чтение геометрии и возвращает сумму, которую браузер при реальном обращении пересчитал бы. "
            "Счётчик обращений к `measure` показывает разницу между двумя подходами."
        ),
        example(
            "javascript",
            """
            'use strict';

            // Имитация чтения геометрии из DOM.
            let layoutCount = 0;
            let width = 100;

            function measure() {
              layoutCount += 1;
              return width;
            }

            function setWidth(value) {
              width = value;
            }

            function thrashing(items) {
              for (const item of items) {
                const w = measure();
                setWidth(w + 10);
              }
            }

            function batched(items) {
              const widths = items.map(() => measure());
              widths.forEach((w, i) => setWidth(w + 10 * (i + 1)));
            }

            thrashing([1, 2, 3, 4, 5]);
            console.log('Наивный подход, чтении:', layoutCount);
            layoutCount = 0;
            width = 100;
            batched([1, 2, 3, 4, 5]);
            console.log('Пакетный подход, чтений:', layoutCount);
            console.log('Итоговая ширина:', width);
            """,
        ),
        text(
            "Вывод программы:\n"
            "Наивный подход, чтений: 5\n"
            "Пакетный подход, чтений: 5\n"
            "Итоговая ширина: 150"
        ),
        callout(
            "warning",
            "Чтение после записи — самая опасная комбинация",
            "Запись сама по себе не запускает layout немедленно: браузер откладывает его. "
            "Но следующее чтение геометрии заставляет браузер посчитать раскладку до конца. "
            "В реальном коде такой цикл из ста итераций может добавить десятки миллисекунд на устройстве пользователя."
        ),
        text(
            "У пакетного подхода в примере то же число чтений, потому что модель упрощена: в настоящем "
            "DOM первое чтение после пачки изменений вызовет layout, а последующие уже используют "
            "актуальные данные. Смысл тот же — сначала все чтения, потом все записи внутри кадра."
        ),
        heading("Что выносится на compositor"),
        text(
            "Compositor — это отдельный поток, который собирает заранее подготовленные слои в кадр. "
            "Если элемент вынесен в собственный слой, изменение `transform` или `opacity` не требует "
            "пересчёта стилей, layout и paint: композитор просто по-новому совмещает слои. Отсюда "
            "требование к плавной анимации — двигать элемент через `transform`, а не через `left` и `top`.\n\n"
            "Подсказать браузеру вынести элемент можно свойством `will-change: transform`. Применяйте "
            "его точечно: каждый слой занимает память графической карты, и тысяча таких подсказок "
            "навредит больше, чем поможет. Старый приём `translateZ(0)` добивался того же эффекта "
            "побочным явлением и сегодня считается устаревшим приёмом."
        ),
        example(
            "javascript",
            """
            // Плохо: каждое изменение left/top запускает layout и paint.
            const bad = document.querySelector('.banner');
            bad.style.left = '120px';
            bad.style.top = '40px';

            // Хорошо: transform меняет только матрицу слоя, его обрабатывает compositor.
            const good = document.querySelector('.banner');
            good.style.willChange = 'transform';
            good.style.transform = 'translate(120px, 40px)';

            // Анимация через Web Animations API остаётся на compositor целиком.
            good.animate(
              [{ transform: 'translateX(0)' }, { transform: 'translateX(240px)' }],
              { duration: 600, easing: 'ease-out', fill: 'forwards' }
            );
            """,
        ),
        text(
            "Заодно обратим внимание на изоляцию раскладки. Свойство `contain: layout` сообщает браузеру, "
            "что изменения внутри элемента не влияют на наружную геометрию. Свойство "
            "`content-visibility: auto` позволяет пропустить раскладку и отрисовку блока за пределами экрана."
        ),
        heading("Критический путь рендеринга и Core Web Vitals"),
        text(
            "Критический путь рендеринга (Critical Rendering Path) — это цепочка ресурсов, без которых "
            "первый экран не появится. Внешний CSS блокирует отрисовку: браузер не станет показывать "
            "страницу в промежуточном виде без стилей. Обычный `<script>` без атрибутов блокирует и "
            "парсинг, и отрисовку, так как он может изменить документ синхронно.\n\n"
            "Атрибут `defer` откладывает выполнение до окончания парсинга и сохраняет порядок скриптов. "
            "Атрибут `async` выполняет скрипт сразу после загрузки в произвольном порядке. Модульные "
            "скрипты (`type=\"module\"`) ведут себя как `defer` по умолчанию. Для ключевого ресурса "
            "используют `preload`, а `preconnect` заранее выполняет DNS, TCP и TLS-рукопожатие."
        ),
        example(
            "javascript",
            """
            // Измеряем LCP: время, когда отрисован самый крупный элемент первого экрана.
            const lcpObserver = new PerformanceObserver((list) => {
              const entries = list.getEntries();
              const last = entries[entries.length - 1];
              console.log('LCP:', Math.round(last.startTime), 'мс');
            });
            lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });

            // Измеряем CLS: сумму сдвигов без недавнего пользовательского ввода.
            let cls = 0;
            new PerformanceObserver((list) => {
              for (const entry of list.getEntries()) {
                if (!entry.hadRecentInput) cls += entry.value;
              }
              console.log('CLS:', cls.toFixed(3));
            }).observe({ type: 'layout-shift', buffered: true });
            """,
        ),
        text(
            "Три метрики Core Web Vitals описывают три разных качества страницы. LCP (Largest Contentful "
            "Paint) отвечает за скорость загрузки основной картинки или текстового блока, хорошее "
            "значение — до 2.5 секунды. INP (Interaction to Next Paint) измеряет задержку от ввода "
            "пользователя до следующей отрисовки, хорошее значение — до 200 миллисекунд; в 2024 году "
            "INP заменил прежнюю метрику FID. CLS (Cumulative Layout Shift) оценивает визуальную "
            "стабильность, хорошее значение — не больше 0.1.\n\n"
            "На INP напрямую влияют длинные задачи: если обработчик занимает main thread дольше "
            "50 миллисекунд, браузер не успевает отрисовать кадр и ввод кажется «залипшим»."
        ),
        example(
            "javascript",
            """
            // Добровольно уступаем управление, чтобы браузер успел отрисовать кадр.
            function yieldToMain() {
              return new Promise((resolve) => setTimeout(resolve, 0));
            }

            async function processItems(items, handle) {
              let processed = 0;
              for (const item of items) {
                handle(item);
                processed += 1;
                if (processed % 50 === 0) {
                  await yieldToMain();
                }
              }
              return processed;
            }

            const done = await processItems(
              Array.from({ length: 120 }, (_, i) => i),
              (value) => value * 2
            );
            console.log('Обработано элементов:', done);
            """,
        ),
        text("Вывод программы:\nОбработано элементов: 120"),
        heading("Web Components"),
        text(
            "Web Components — набор стандартов платформы для собственных HTML-элементов. Он состоит из "
            "Custom Elements, Shadow DOM, шаблонов `<template>` и слотов. Смысл в том, чтобы браузер сам "
            "понимал, что такое `<user-card>`, без сторонних библиотек, а стили компонента не протекали "
            "на страницу и обратно.\n\n"
            "Custom Element — это класс, наследующий `HTMLElement`. Регистрация выполняется вызовом "
            "`customElements.define`. Жизненный цикл задаётся методами: `connectedCallback` срабатывает "
            "при добавлении в документ, `disconnectedCallback` — при удалении, "
            "`attributeChangedCallback` — при изменении атрибута из списка `observedAttributes`. "
            "В конструкторе нельзя работать с дочерними узлами: на момент создания их ещё нет."
        ),
        example(
            "javascript",
            """
            'use strict';

            class FancyButton extends HTMLElement {
              static get observedAttributes() {
                return ['variant'];
              }

              connectedCallback() {
                this.root = this.attachShadow({ mode: 'open' });
                this.root.innerHTML = `
                  <style>
                    :host { display: inline-block; }
                    button { padding: 8px 16px; border: 0; border-radius: 4px; color: #fff; }
                    :host([variant="primary"]) button { background: #0b5fff; }
                    :host([variant="danger"]) button { background: #c81e1e; }
                  </style>
                  <button><slot>Кнопка</slot></button>
                `;
                this.button = this.root.querySelector('button');
                this.button.addEventListener('click', this.onClick);
              }

              disconnectedCallback() {
                this.button.removeEventListener('click', this.onClick);
              }

              onClick = () => {
                this.dispatchEvent(
                  new CustomEvent('fancy-click', { bubbles: true, composed: true })
                );
              };
            }

            customElements.define('fancy-button', FancyButton);
            """,
        ),
        text(
            "Обратите внимание на опцию `composed: true` у события. По умолчанию события не выходят за "
            "границу теневого дерева, поэтому подписка снаружи компонента не сработает. Опция `composed` "
            "позволяет событию пересечь границу и всплыть до обычного DOM."
        ),
        heading("Shadow DOM и изоляция стилей"),
        text(
            "Shadow DOM — это отдельное поддерево, прикреплённое к элементу. Документ внутри называется "
            "shadow root, а элемент, к которому он прикреплён, — хостом. Стили снаружи не действуют на "
            "узлы внутри shadow root, а стили внутри не протекают наружу. При `mode: 'open'` хост отдаёт "
            "свойство `shadowRoot` всем желающим, при `mode: 'closed'` оно остаётся `null`, что скрывает "
            "внутренности, но не обеспечивает безопасности.\n\n"
            "Для стилизации есть псевдоэлементы. `:host` — сам хост, `:host([disabled])` — хост с "
            "атрибутом, `::slotted(p)` — элемент, переданный извне в слот. Полностью закрыться от "
            "внешнего оформления не получится, и это хорошо: CSS-переменные и псевдоэлемент `::part` "
            "дают хосту возможность разрешить тематизацию отдельных частей."
        ),
        example(
            "javascript",
            """
            // Внешний CSS: меняет переменную, которая читается внутри теневого дерева.
            document.documentElement.style.setProperty('--card-accent', '#7c3aed');

            // Внутри shadow root компонента:
            // .card { border-top: 3px solid var(--card-accent, #0b5fff); }

            // Экспорт внутренней части для стилизации снаружи:
            // <span part="title">Заголовок</span>
            // a-card::part(title) { font-weight: 700; }

            // Проверяем, что снаружи видно только разрешённое
            const card = document.querySelector('a-card');
            console.log('shadowRoot доступен:', Boolean(card.shadowRoot));
            console.log('частей экспортировано:', card.shadowRoot.querySelectorAll('[part]').length);
            """,
        ),
        text(
            "Ещё одна полезная возможность — декларативный Shadow DOM. Атрибут `shadowrootmode` на "
            "встроенном `<template>` заставляет парсер создать shadow root прямо при разборе HTML. "
            "Это позволяет серверному рендерингу отдать готовую разметку и избежать мигания "
            "неоформленного содержимого."
        ),
        example(
            "javascript",
            """
            // Сервер отдаёт такой фрагмент:
            // <user-card>
            //   <template shadowrootmode="open">
            //     <style>:host { display: block; border: 1px solid #ddd; }</style>
            //     <slot></slot>
            //   </template>
            //   <p>Иван</p>
            // </user-card>

            // К моменту выполнения скрипта shadow root уже существует.
            const card = document.querySelector('user-card');
            console.log('декларативный shadowRoot:', Boolean(card.shadowRoot));
            console.log('содержимое слота:', card.shadowRoot.querySelector('slot').assignedNodes().length);
            """,
        ),
        heading("Service Workers"),
        text(
            "Service Worker — это фоновый скрипт, который работает в отдельном потоке и встаёт между "
            "страницей и сетью. У него нет доступа к DOM, зато есть `caches`, клиенты и события "
            "жизненного цикла. Требование безопасности жёсткое: регистрация разрешена только с "
            "доверенного origin, то есть по HTTPS, с исключением для `localhost` при разработке.\n\n"
            "Жизненный цикл состоит из этапов. На событии `install` выполняется предварительное "
            "кэширование ресурсов. После установки воркер ждёт, пока закроются старые вкладки, если не "
            "вызвать `skipWaiting`. На событии `activate` удаляют устаревшие кэши, а `clients.claim` "
            "позволяет новому воркеру немедленно взять контроль над открытыми страницами. Ключевой "
            "момент: `event.waitUntil(promise)` продлевает жизнь обработчика, пока обещанная "
            "операция не завершится, иначе браузер может остановить воркер посреди работы."
        ),
        example(
            "javascript",
            """
            // sw.js — файл сервис-воркера.
            const STATIC_CACHE = 'static-v1';

            self.addEventListener('install', (event) => {
              event.waitUntil(
                caches
                  .open(STATIC_CACHE)
                  .then((cache) => cache.addAll(['/', '/app.js', '/styles.css']))
                  .then(() => self.skipWaiting())
              );
            });

            self.addEventListener('activate', (event) => {
              event.waitUntil(
                caches
                  .keys()
                  .then((keys) =>
                    Promise.all(
                      keys.filter((key) => key !== STATIC_CACHE).map((key) => caches.delete(key))
                    )
                  )
                  .then(() => self.clients.claim())
              );
            });
            """,
        ),
        text(
            "Стратегий кэширования несколько, и они отвечают на разные вопросы. Cache First подходит "
            "для неизменяемых статических файлов с хешем в имени: если файл найден в кэше, сеть не "
            "нужна. Network First уместна для данных, которые важно получить свежими, но которые "
            "можно отдать из кэша офлайн. Stale While Revalidate возвращает кэш мгновенно и "
            "параллельно обновляет его сетевым ответом — компромисс для HTML и настроек."
        ),
        example(
            "javascript",
            """
            // sw.js — маршрутизация запросов по стратегиям.
            self.addEventListener('fetch', (event) => {
              const url = new URL(event.request.url);
              if (url.pathname.startsWith('/api/')) {
                event.respondWith(networkFirst(event.request));
                return;
              }
              if (/\\.(js|css|woff2)$/.test(url.pathname)) {
                event.respondWith(cacheFirst(event.request));
                return;
              }
              event.respondWith(staleWhileRevalidate(event.request));
            });

            async function cacheFirst(request) {
              const cached = await caches.match(request);
              if (cached) return cached;
              const response = await fetch(request);
              const cache = await caches.open('static-v1');
              cache.put(request, response.clone());
              return response;
            }

            async function networkFirst(request) {
              try {
                const response = await fetch(request);
                const cache = await caches.open('dynamic-v1');
                cache.put(request, response.clone());
                return response;
              } catch (error) {
                const cached = await caches.match(request);
                if (cached) return cached;
                return new Response('Недоступно офлайн', { status: 503 });
              }
            }

            async function staleWhileRevalidate(request) {
              const cached = await caches.match(request);
              const refresh = fetch(request).then((response) => {
                const copy = response.clone();
                caches.open('dynamic-v1').then((cache) => cache.put(request, copy));
                return response;
              });
              return cached || refresh;
            }
            """,
        ),
        callout(
            "info",
            "Клонируйте ответ перед кэшированием",
            "Поток тела ответа можно прочитать только один раз. Вызов `response.clone()` создаёт копию, "
            "которую можно сразу положить в кэш, а исходный ответ отдать странице. Если этого не сделать, "
            "страница получит пустое тело."
        ),
        text(
            "Фоновая синхронизация решает задачу «пользователь отправил форму без сети». Страница "
            "сохраняет задачу локально и регистрирует тег синхронизации через `registration.sync.register`. "
            "Когда сеть появляется, браузер будит воркер и вызывает событие `sync`, а обработчик "
            "дозавершает отправку. Периодическая синхронизация `periodicsync` работает похоже, но "
            "требует явного разрешения и минимального интервала, который задаёт браузер."
        ),
        example(
            "javascript",
            """
            // В воркере: отправка того, что накопилось офлайн.
            self.addEventListener('sync', (event) => {
              if (event.tag === 'flush-orders') {
                event.waitUntil(flushOrders());
              }
            });

            async function flushOrders() {
              const pending = await readPendingOrders();
              for (const order of pending) {
                await fetch('/api/orders', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(order),
                });
              }
              await clearPendingOrders();
            }

            // На странице: регистрация тега синхронизации.
            async function queueOrder(order) {
              await savePendingOrder(order);
              const registration = await navigator.serviceWorker.ready;
              await registration.sync.register('flush-orders');
            }
            """,
        ),
        heading("Модель безопасности"),
        text(
            "Браузер выполняет чужой код на вашем компьютере, поэтому границы проводятся по origin. "
            "**Origin** (источник) — это схема, хост и порт. `https://example.com` и "
            "`http://example.com` — разные origin, как и `https://example.com` и "
            "`https://example.com:8443`. **Site** (сайт) определяется схемой и тремя последними "
            "компонентами домена, поэтому `app.example.com` и `api.example.com` — один site, но два "
            "разных origin.\n\n"
            "Same-Origin Policy запрещает странице с одного origin читать содержимое другого: обращаться "
            "к `iframe.contentWindow.document`, читать ответы `fetch` и `XMLHttpRequest` без разрешения, "
            "открывать чужой `localStorage`. Запросы при этом уходят, но читать ответ нельзя — именно "
            "это ограничение ослабляет CORS."
        ),
        example(
            "javascript",
            """
            'use strict';

            function parseOrigin(value) {
              const scheme = value.startsWith('https://') ? 'https' : 'http';
              const rest = value.slice(scheme.length + 3);
              const [host, port] = rest.includes(':') ? rest.split(':') : [rest, null];
              return { scheme, host, port: Number(port) || (scheme === 'https' ? 443 : 80) };
            }

            const target = parseOrigin('https://example.com');
            const candidates = [
              'https://example.com:443',
              'https://example.com:8443',
              'http://example.com',
              'https://api.example.com',
            ];

            for (const candidate of candidates) {
              const { scheme, host, port } = parseOrigin(candidate);
              const same =
                scheme === target.scheme && host === target.host && port === target.port;
              console.log(candidate, same ? 'тот же origin' : 'другой origin');
            }
            """,
        ),
        text(
            "Вывод программы:\n"
            "https://example.com:443 тот же origin\n"
            "https://example.com:8443 другой origin\n"
            "http://example.com другой origin\n"
            "https://api.example.com другой origin"
        ),
        text(
            "CORS — механизм, которым сервер сообщает браузеру, что ответ можно прочитать чужой "
            "странице. Ответ содержит заголовок `Access-Control-Allow-Origin` с точным origin или со "
            "звёздочкой. Значение `*` нельзя сочетать с учётными данными: заголовок "
            "`Access-Control-Allow-Credentials: true` требует явного origin в первой строке. Кроме того, "
            "сервер должен вернуть `Vary: Origin`, иначе промежуточный кэш отдаст ответ не тому клиенту.\n\n"
            "Если запрос «несложный» (метод GET, HEAD или POST с типом содержимого "
            "`text/plain`, `application/x-www-form-urlencoded` или `multipart/form-data` и без "
            "собственных заголовков), браузер отправляет его сразу. Иначе сначала отправляется "
            "preflight-запрос методом OPTIONS, и настоящий запрос уходит только после разрешения."
        ),
        table(
            ["Заголовок ответа", "Назначение"],
            [
                ["`Access-Control-Allow-Origin`", "Признаёт конкретный origin или разрешает все"],
                ["`Access-Control-Allow-Methods`", "Список методов, разрешённых в preflight"],
                ["`Access-Control-Allow-Headers`", "Список разрешённых собственных заголовков"],
                ["`Access-Control-Allow-Credentials`", "Разрешает cookies и авторизацию"],
                ["`Access-Control-Max-Age`", "Сколько секунд кэшировать результат preflight"],
            ],
        ),
        heading("Content Security Policy"),
        text(
            "Content Security Policy (CSP) — политика, задаваемая HTTP-заголовком, которая говорит "
            "браузеру, откуда можно загружать скрипты, стили, изображения и куда можно отправлять "
            "запросы. Главная защита — от внедрённых скриптов: даже если в разметку попала "
            "нежелательная вставка, браузер откажется её выполнять без подходящего nonce или хеша.\n\n"
            "Строка политики состоит из директив с источниками. Значение `'self'` разрешает только "
            "собственный origin, `'none'` запрещает всё, `data:` и `https:` задают схемы. Для строчных "
            "скриптов используют одноразовый nonce, который сервер генерирует на каждый ответ, или "
            "хеш содержимого. Директива `'strict-dynamic'` доверяет скриптам, которые загрузил уже "
            "доверенный скрипт, и тем самым ослабляет риск неверных списков доменов."
        ),
        example(
            "javascript",
            """
            'use strict';

            // Разбор политики в виде строки в объект директив.
            function parsePolicy(policy) {
              const directives = {};
              for (const part of policy.split(';')) {
                const tokens = part.trim().split(/\\s+/).filter(Boolean);
                if (tokens.length === 0) continue;
                directives[tokens[0]] = tokens.slice(1);
              }
              return directives;
            }

            const policy = parsePolicy(
              "default-src 'self'; script-src 'self' 'strict-dynamic'; object-src 'none'"
            );

            console.log('директив:', Object.keys(policy).length);
            console.log('script-src:', policy['script-src'].join(', '));
            console.log('object-src запрещён:', policy['object-src'][0] === "'none'");
            """,
        ),
        text(
            "Вывод программы:\n"
            "директив: 3\n"
            "script-src: 'self', 'strict-dynamic'\n"
            "object-src запрещён: true"
        ),
        text(
            "Политику нужно вводить постепенно. Режим `Content-Security-Policy-Report-Only` не блокирует "
            "нарушения, а только сообщает о них на указанный адрес через директиву `report-to`. "
            "Начав с этого режима, вы увидите всё, что сломается, прежде чем включить блокировку."
        ),
        heading("COOP и COEP: изоляция документа"),
        text(
            "Даже при строгой политике соседние origin могут влиять друг на друга: окно-открыватель "
            "получает ссылку на `window.opener`, а встраиваемый ресурс — шанс реализовать атаку через "
            "общий тайминг. Заголовок `Cross-Origin-Opener-Policy: same-origin` изолирует "
            "browsing context: для чужих попапов `window.opener` станет `null`.\n\n"
            "Заголовок `Cross-Origin-Embedder-Policy: require-corp` запрещает загружать чужие "
            "ресурсы без явного разрешения: они должны либо принадлежать тому же origin, либо отдавать "
            "`Cross-Origin-Resource-Policy: cross-origin` или проходить CORS. Вместе эти два заголовка "
            "включают cross-origin isolation, и только в таком документе доступны `SharedArrayBuffer` "
            "и высокоточные таймеры. Без изоляции общий буфер памяти стал бы оракулом для атак по времени."
        ),
        example(
            "javascript",
            """
            // Проверка изоляции выполняется на странице до запуска любых потоков.
            const isolated = window.crossOriginIsolated === true;
            console.log('cross-origin isolation:', isolated);
            if (window.crossOriginIsolated === false) {
              console.warn('SharedArrayBuffer недоступен: проверьте COOP и COEP');
            }

            function createSharedCounter(size = 4) {
              if (!window.crossOriginIsolated) {
                return new Int32Array(new SharedArrayBuffer(size));
              }
              return new Int32Array(new ArrayBuffer(size));
            }

            console.log('размер счётчика:', createSharedCounter().length);
            """,
        ),
        text(
            "За доступ к возможностям устройства отвечает отдельный механизм — Permissions Policy, "
            "раньше Feature Policy. Заголовок `Permissions-Policy` или атрибут `allow` у `iframe` "
            "сообщают, какие API разрешены документу и его встроенным фреймам. Пустая запись вида "
            "`camera=()` запрещает доступ полностью, а `geolocation=(self)` оставляет его только "
            "собственному origin."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Анимация через `left` и `top`", "Каждый кадр пересчитывает layout, кадры дёргаются", "Анимировать `transform` и `opacity`"],
                ["Чередование чтений и записей в цикле", "Layout thrashing, десятки лишних раскладок", "Сначала все чтения, затем все записи внутри `requestAnimationFrame`"],
                ["Подписки без очистки в компоненте", "Утечка памяти: элемент не собирается сборщиком", "Отписываться в `disconnectedCallback`"],
                ["`response` без `clone()` в кэш", "Страница получает пустое тело ответа", "Кэшировать `response.clone()`, отдавать оригинал"],
                ["`Access-Control-Allow-Origin: *` с cookies", "Браузер отклоняет ответ, cookies не передаются", "Указывать точный origin и отправлять `Vary: Origin`"],
                ["CSP со `'unsafe-inline'` в `script-src`", "Политика почти не защищает от вставок", "Использовать nonce или хеши скриптов"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания рассчитаны на браузер: выполните их в песочнице или локальном проекте, открытом "
            "по `http://localhost`, поскольку Service Worker не регистрируется на файлах из `file://`."
        ),
        numbered(
            "Перепишите анимацию элемента с `left` на `transform` и объясните, какие этапы конвейера перестали запускаться.",
            "Напишите функцию, которая за один проход измеряет высоту десяти абзацев, а затем применяет изменения, и сравните число раскладок с наивным вариантом.",
            "Создайте Custom Element `<profile-badge>` с Shadow DOM, атрибутом `name` в `observedAttributes` и слотом для аватара.",
            "Реализуйте Service Worker с Cache First для файлов `/assets/*` и Network First для `/api/*`, а также удаление кэшей старых версий на активации.",
            "Напишите политику CSP для одностраничного приложения со скриптами `'self'` и nonce, шрифтами с `fonts.gstatic.com` и запросами к `api.example.com`.",
        ),
        callout(
            "success",
            "Подсказка к первому заданию",
            "Перед правкой откройте панель Performance и снимите профиль анимации. Включите отображение "
            "раскладок и перерисовок: на варианте с `left` вы увидите полосы paint и layout на каждом кадре, "
            "а на варианте с `transform` останется только composite."
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему изменение `transform` дешевле изменения `left`?",
            "Что такое layout thrashing и как его избежать?",
            "Зачем в обработчике `install` сервис-воркера нужен `event.waitUntil`?",
            "Чем `defer` отличается от `async`?",
            "Почему `Access-Control-Allow-Origin: *` не работает вместе с cookies?",
            "Для чего нужен заголовок `Cross-Origin-Embedder-Policy: require-corp`?",
        ),
        heading("Ответы", 3),
        numbered(
            "`transform` обрабатывается compositor-потоком на уровне готового слоя и не требует пересчёта стилей, layout и paint, а `left` запускает layout и paint на каждом кадре.",
            "Это чередование чтений геометрии и записей стилей, из-за которого браузер выполняет синхронный layout на каждом шаге. Помогает группировка: сначала все чтения, затем все записи в одном кадре.",
            "`waitUntil` продлевает жизнь обработчика до завершения обещанной операции. Без него браузер может остановить воркер и прервать предварительное кэширование.",
            "`defer` сохраняет порядок скриптов и выполняет их после разбора документа, `async` выполняется сразу после загрузки в произвольном порядке.",
            "Со звёздочкой браузер не может гарантировать, что учётные данные не получит чужой origin, поэтому при учётных данных требуется точный origin.",
            "Он запрещает загружать чужие ресурсы без CORS или `Cross-Origin-Resource-Policy`, что вместе с COOP включает cross-origin isolation и делает безопасными `SharedArrayBuffer` и высокоточные таймеры.",
        ),
        heading("Итоги"),
        bullets(
            "Конвейер рендеринга: стиль, layout, paint и composite; чем правее этап, тем дешевле изменение.",
            "`transform` и `opacity` обрабатывает compositor, поэтому только они дают плавные анимации.",
            "Layout thrashing устраняется группировкой чтений и записей и планированием изменений в `requestAnimationFrame`.",
            "Web Components — Custom Elements, Shadow DOM и слоты; события наружу пропускают через `composed: true`.",
            "Service Worker управляет жизненным циклом через `install`, `activate` и `fetch`, а кэш строится по стратегиям.",
            "Безопасность складывается из Same-Origin Policy, CORS, CSP и COOP с COEP для изоляции документа.",
        ),
        heading("Что дальше"),
        text(
            "Браузерная платформа изучена: вы понимаете, как документ превращается в пиксели, как "
            "устроены собственные элементы и офлайн-кэш и как устроены границы безопасности. В "
            "следующем уроке мы перейдём к Node.js: его событийному циклу, потокам и буферам, "
            "рабочим потокам и межпроцессному взаимодействию. Многие концепции останутся знакомыми — "
            "события, обещания и асинхронные API, — но платформа и модель угроз будут другими."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "MDN: Критический путь рендеринга — developer.mozilla.org/ru/docs/Web/Performance/Critical_rendering_path",
            "web.dev: Core Web Vitals — web.dev/articles/vitals",
            "MDN: Web Components — developer.mozilla.org/ru/docs/Web/API/Web_components",
            "MDN: Service Worker API — developer.mozilla.org/ru/docs/Web/API/Service_Worker_API",
            "MDN: Content Security Policy — developer.mozilla.org/ru/docs/Web/HTTP/CSP",
            "web.dev: COOP и COEP для изоляции — web.dev/articles/coop-coep",
        ),
    ],
}
