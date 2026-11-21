"""Урок 2.7 курса JavaScript: Browser API."""

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
    "topic_order": 7,
    "name": "2.7. Browser API",
    "slug": "javascript-2-7-browser-api",
    "short_description": (
        "Работа с DOM и системой событий, HTTP-запросы через Fetch API, "
        "браузерные хранилища, URL и History API, а также обработка форм."
    ),
    "topic_name": "Browser API",
    "topic_description": (
        "Урок целиком посвящён API браузера: поиск и изменение элементов страницы, "
        "всплытие и перехват событий, сетевые запросы с отменой и таймаутами, "
        "localStorage и IndexedDB, управление адресной строкой в одностраничных "
        "приложениях и валидация форм средствами платформы."
    ),
    "learning_objectives": [
        "Находить и изменять элементы DOM, отличать NodeList от HTMLCollection и безопасно вставлять пользовательские данные",
        "Объяснять фазы события, применять делегирование и настраивать addEventListener через options",
        "Отправлять запросы через fetch, проверять response.ok, читать тело один раз и отменять запросы через AbortController",
        "Выбирать между localStorage, sessionStorage и IndexedDB и сериализовать объекты в JSON",
        "Разбирать URL через URL и URLSearchParams и строить навигацию в SPA через History API",
        "Читать формы через FormData, использовать встроенную валидацию и отправлять данные без перезагрузки страницы",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "javascript",
        "browser-api",
        "dom",
        "события",
        "fetch",
        "localstorage",
        "формы",
    ],
    "starter_code": code(
        r"""
        // Список задач: добавление элементов и делегирование событий.
        const form = document.querySelector('#new-task');
        const input = form.querySelector('input[name="title"]');
        const list = document.querySelector('#tasks');

        function addTask(title) {
          const item = document.createElement('li');
          item.dataset.title = title;
          item.textContent = title;
          list.append(item);
        }

        form.addEventListener('submit', (event) => {
          event.preventDefault();          // не перезагружать страницу
          const title = input.value.trim();
          if (!title) return;
          addTask(title);
          input.value = '';
        });

        // Один слушатель на весь список вместо слушателя на каждом пункте
        list.addEventListener('click', (event) => {
          const item = event.target.closest('li');
          if (!item) return;
          item.classList.toggle('done');
        });
        """
    ),
    "hints": [
        "Помните, что querySelectorAll возвращает статический NodeList, а getElementsByClassName — живой HTMLCollection: второй обновляется автоматически при изменении страницы.",
        "fetch не считает ответы 404 и 500 ошибкой. Всегда проверяйте response.ok перед чтением тела, иначе JSON.parse упадёт на HTML-странице ошибки.",
        "Тело ответа можно прочитать только один раз. Если нужны и текст, и JSON, вызовите response.clone() до первого чтения.",
        "localStorage хранит только строки. Для объектов используйте JSON.stringify при записи и JSON.parse при чтении, а пустое значение обрабатывайте через ?? или проверку на null.",
    ],
    "content": [
        text(
            "Среда выполнения JavaScript в браузере — это не только сам язык, но и набор "
            "встроенных интерфейсов, которые называют Browser APIs. Именно они превращают "
            "изолированный скрипт в полноценное приложение: позволяют читать и менять страницу, "
            "реагировать на действия пользователя, общаться с сервером, сохранять данные "
            "между визитами и управлять адресной строкой без перезагрузки.\n\n"
            "Все эти интерфейсы описаны в стандартах платформы (WHATWG и W3C) и предоставляются "
            "браузером, а не движком языка. Поэтому объекта document нет в Node.js, а setTimeout "
            "в браузере и в Node.js ведёт себя почти одинаково, но принадлежит разным реализациям. "
            "Понимание границы между языком и платформой помогает быстро находить, где именно искать "
            "документацию.\n\n"
            "Ниже разобраны шесть крупных групп API: DOM, события, Fetch, хранилища, URL и History, "
            "а также формы — с рабочими примерами и ожидаемым выводом."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "находить элементы через querySelector и querySelectorAll, понимать отличия NodeList от HTMLCollection;",
            "создавать, перемещать и удалять узлы без innerHTML, чтобы не открывать уязвимость XSS;",
            "объяснять фазы события и применять делегирование;",
            "отправлять запросы через fetch, проверять ответ и обрабатывать сетевые ошибки;",
            "отменять запросы и задавать таймауты через AbortController;",
            "выбирать между localStorage, sessionStorage и IndexedDB, хранить объекты в JSON;",
            "разбирать адреса через URL и URLSearchParams, строить навигацию SPA;",
            "читать и валидировать формы через FormData и Constraint Validation API.",
        ),
        text(
            "Общий принцип: почти все браузерные API асинхронны или событийны. Запрос к серверу "
            "и открытие базы данных не блокируют главный поток, а возвращают Promise или вызывают "
            "колбэк позже — поэтому в примерах много async/await."
        ),
        heading("DOM: поиск и навигация по элементам"),
        text(
            "DOM (Document Object Model) — объектная модель документа. Браузер разбирает HTML "
            "и строит дерево узлов, где каждый тег становится элементом, а текст внутри тега — "
            "текстовым узлом. Объект document — точка входа в это дерево, а объект Element "
            "представляет конкретный тег и даёт доступ к его родителям, детям, атрибутам и стилям.\n\n"
            "Для поиска элементов есть две группы методов. Универсальные querySelector и "
            "querySelectorAll принимают любой CSS-селектор и возвращают первый подходящий элемент "
            "либо всех подходящих соответственно. Специализированные getElementById, "
            "getElementsByClassName и getElementsByTagName работают чуть быстрее на больших "
            "документах, но поддерживают только простые критерии.\n\n"
            "Ключевое отличие — тип результата. querySelectorAll возвращает статический NodeList: "
            "снимок на момент вызова, где есть forEach, но нет map и filter. "
            "Методы getElementsBy* возвращают живой HTMLCollection без forEach."
        ),
        example(
            "javascript",
            r"""
            // HTML: <div id="app"><ul><li class="item" data-id="1">A</li></ul></div>
            const first = document.querySelector(".item");      // первый подходящий или null
            const items = document.querySelectorAll(".item");   // статический NodeList
            const live = document.getElementsByClassName("item"); // живая HTMLCollection

            console.log(first.textContent);        // A
            console.log(items.length);             // 1
            console.log(typeof items.forEach);     // function
            console.log(typeof items.map);         // undefined

            // Приведение к массиву, если нужны методы массива
            const asArray = Array.from(items);
            console.log(asArray.map((el) => el.dataset.id)); // [ '1' ]

            // Живая коллекция меняется сама
            document.querySelector("ul").append(document.createElement("li"));
            console.log(live.length);              // 2
            console.log(items.length);             // 1 — снимок не изменился

            // Навигация по дереву
            const ul = first.parentElement;         // родитель
            console.log(ul.children.length);        // 2
            console.log(ul.firstElementChild.textContent); // A
            console.log(first.nextElementSibling !== null); // true
            console.log(first.closest("#app") !== null);    // true
            """,
        ),
        text(
            "Вывод: textContent равен 'A', NodeList даёт forEach, но не map — Array.from открывает "
            "методы массива; живая коллекция после вставки второго пункта содержит 2 элемента, "
            "а статический снимок по-прежнему 1. Свойства parentElement, children, closest и "
            "nextElementSibling позволяют обойти дерево без повторного поиска.\n\n"
            "Различайте children и childNodes: первое содержит только элементы, второе — все узлы, "
            "включая текстовые и пробельные."
        ),
        heading("Изменение элементов и безопасная вставка"),
        text(
            "Узлы создаются через document.createElement и вставляются методами append, prepend, "
            "before, after или replaceWith; remove убирает узел из документа, сохраняя объект.\n\n"
            "Атрибуты задаются через setAttribute и читаются через getAttribute, привычные "
            "свойства вроде id и value дублируют их. Атрибуты data-* доступны через dataset, "
            "где дефисы превращаются в camelCase: data-user-name читается как dataset.userName. "
            "Классы меняйте через classList, а не переписывая className целиком.\n\n"
            "Когда элементов много, каждый append вызывает пересчёт макета. DocumentFragment — "
            "лёгкий контейнер вне документа: наполните его сотней узлов и вставьте один раз."
        ),
        example(
            "javascript",
            r"""
            const container = document.querySelector("#list");
            const fragment = document.createDocumentFragment();

            const titles = ["Первый", "Второй", "Третий"];
            titles.forEach((title, index) => {
              const li = document.createElement("li");
              li.className = "row";
              li.dataset.index = index;
              li.textContent = title;
              fragment.append(li);
            });
            container.append(fragment);   // одна вставка в документ

            const firstRow = container.querySelector("li");
            console.log(firstRow.textContent);        // Первый
            console.log(firstRow.dataset.index);      // 0
            console.log(container.children.length);   // 3

            firstRow.classList.add("active", "visible");
            console.log(firstRow.classList.contains("active")); // true
            firstRow.classList.toggle("visible");
            console.log(firstRow.className);          // row active

            firstRow.setAttribute("aria-current", "true");
            console.log(firstRow.getAttribute("aria-current")); // true
            firstRow.removeAttribute("aria-current");
            console.log(firstRow.hasAttribute("aria-current")); // false
            """,
        ),
        callout(
            "danger",
            "innerHTML и пользовательские данные",
            "Присваивание в innerHTML разбирает строку как HTML. Если в ней есть данные от пользователя, "
            "злоумышленник может внедрить тег script или обработчик onerror и выполнить произвольный код "
            "на странице. Используйте textContent для текста и createElement для разметки; "
            "innerHTML допустим только для доверенных строк-шаблонов."
        ),
        text(
            "Для повторяющейся разметки в HTML предусмотрен тег template. Его содержимое не "
            "отображается и не загружает ресурсы, пока его не вставят в документ. Шаблон лежит "
            "в свойстве content, откуда его клонируют методом cloneNode(true) — аргумент true "
            "означает глубокое клонирование вместе со всеми потомками. Такой подход сочетает "
            "удобство разметки и безопасность: данные подставляются не в HTML-строку, а в "
            "textContent конкретных узлов клона."
        ),
        example(
            "javascript",
            r"""
            // HTML:
            // <template id="card"><article class="card"><h2></h2><p></p></article></template>
            // <div id="cards"></div>
            const template = document.querySelector("#card-template");
            const target = document.querySelector("#cards");

            const data = { title: "Курс", description: "Browser API" };

            const clone = template.content.cloneNode(true);
            clone.querySelector("h2").textContent = data.title;   // текст, не разметка
            clone.querySelector("p").textContent = data.description;
            target.append(clone);

            console.log(target.querySelector(".card h2").textContent); // Курс
            console.log(target.querySelectorAll(".card").length);     // 1
            """,
        ),
        heading("События: фазы, слушатели и options"),
        text(
            "Событие проходит три фазы: перехват (capture) — движение от window вниз к цели, "
            "фаза цели (target), затем всплытие (bubbling) — движение обратно к window. "
            "Большинство событий всплывают, поэтому слушатель на родителе видит события детей.\n\n"
            "Слушатель добавляется через addEventListener с объектом options: capture включает "
            "вызов на фазе перехвата, once снимает слушатель после первого вызова, passive "
            "обещает, что preventDefault не будет вызван, а signal привязывает подписку к "
            "AbortSignal, и один abort() снимает все слушатели сразу.\n\n"
            "Различайте target — самый глубокий элемент, где возникло событие, и currentTarget — "
            "элемент, на котором работает слушатель. preventDefault отменяет действие браузера "
            "по умолчанию (переход, отправку формы, прокрутку), а stopPropagation останавливает "
            "всплытие, что может сломать ожидания других слушателей."
        ),
        example(
            "javascript",
            r"""
            const button = document.querySelector("#save");

            function onClick(event) {
              console.log(event.type);            // click
              console.log(event.currentTarget === button); // true
              console.log(event.bubbles);         // true
              console.log(event.isTrusted);       // true для реального клика
            }

            // Слушатель сработает один раз и снимется сам
            button.addEventListener("click", onClick, { once: true });

            // Отправка формы: отменяем перезагрузку страницы
            document.querySelector("form").addEventListener("submit", (event) => {
              event.preventDefault();
              console.log("Отправка перехвачена");
            });

            // Скролл не блокируется, потому что preventDefault не нужен
            window.addEventListener("scroll", () => {}, { passive: true });
            """,
        ),
        heading("Делегирование событий"),
        text(
            "Вешать слушатель на каждый из сотен пунктов дорого и неудобно при динамическом "
            "добавлении. Делегирование ставит один слушатель на общего предка и определяет "
            "пункт по event.target — приём основан на всплытии.\n\n"
            "Внутри обработчика используйте event.target.closest(selector), чтобы найти нужный "
            "элемент, даже если клик пришёлся на вложенную иконку. Проверка ul.contains(li) "
            "защищает от вложенных списков других контейнеров. Новые пункты работают автоматически."
        ),
        example(
            "javascript",
            r"""
            const list = document.querySelector("#tasks");

            list.addEventListener("click", (event) => {
              const item = event.target.closest("li");
              if (!item || !list.contains(item)) return;  // клик не по нашему пункту
              console.log("Клик по задаче:", item.dataset.id);
            });

            // Пункты, добавленные позже, тоже обрабатываются
            const item = document.createElement("li");
            item.dataset.id = "42";
            item.textContent = "Поздняя задача";
            list.append(item);

            // Программный клик для демонстрации (isTrusted будет false)
            item.click();   // Клик по задаче: 42
            """,
        ),
        text(
            "Полезно знать и жизненные события документа. DOMContentLoaded наступает, когда HTML "
            "разобран, но ресурсы могут ещё грузиться; load на window ждёт и их. visibilitychange "
            "вместе с document.hidden позволяет остановить анимацию в скрытой вкладке; online и "
            "offline сообщают о сети, а storage приходит в другие вкладки при изменении localStorage."
        ),
        heading("Fetch API: запросы к серверу"),
        text(
            "Fetch API — современная замена XMLHttpRequest. Функция fetch возвращает Promise "
            "объекта Response, а не готовых данных: тело читается отдельно методами json, text, "
            "blob, arrayBuffer или formData, каждый из которых тоже возвращает Promise.\n\n"
            "Главная ловушка: fetch отклоняет Promise только при сетевой ошибке — нет соединения, "
            "CORS, неизвестный домен. Ответы 404 и 500 считаются доставленными, поэтому их нужно "
            "проверять через response.ok (истинно для 200–299) или response.status. Иначе "
            "response.json() попытается разобрать HTML-страницу ошибки.\n\n"
            "Тело читается один раз; response.clone() даёт копию, если нужны два формата."
        ),
        example(
            "javascript",
            r"""
            async function loadUsers() {
              const response = await fetch("/api/users");

              if (!response.ok) {
                // 404 и 500 не бросают исключение автоматически
                throw new Error(`HTTP ${response.status} ${response.statusText}`);
              }

              console.log(response.headers.get("Content-Type")); // application/json
              return response.json();   // Promise с разобранными данными
            }

            // POST с JSON: сериализуем объект и явно указываем тип
            async function createUser(user) {
              const response = await fetch("/api/users", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(user),
              });
              if (!response.ok) throw new Error(`HTTP ${response.status}`);
              return response.json();
            }

            // Два чтения одного ответа через клон
            const response = await fetch("/api/report");
            const forCache = response.clone();
            const data = await response.json();
            const rawText = await forCache.text();
            console.log(typeof data, typeof rawText);  // object string
            """,
        ),
        callout(
            "warning",
            "fetch и HTTP-ошибки",
            "Ответ 404 или 500 не приводит к reject. Проверяйте response.ok до чтения тела, "
            "иначе ошибка проявится позже и в другом месте, например при разборе JSON."
        ),
        text(
            "fetch не принимает параметр timeout, но принимает AbortSignal в опции signal. "
            "Классический способ — AbortController: вызвать controller.abort() по таймеру. "
            "Более короткий — AbortSignal.timeout(миллисекунды). В обоих случаях Promise "
            "отклоняется с ошибкой, у которой name равен 'AbortError' или 'TimeoutError', "
            "и её важно отличать от сетевой.\n\n"
            "Один контроллер обслуживает несколько запросов: удобно отменять устаревшие "
            "ответы, когда пользователь быстро меняет фильтр."
        ),
        example(
            "javascript",
            r"""
            async function loadWithTimeout(url, ms) {
              try {
                const response = await fetch(url, { signal: AbortSignal.timeout(ms) });
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return await response.json();
              } catch (error) {
                if (error.name === "AbortError" || error.name === "TimeoutError") {
                  console.log("Запрос отменён или истёк таймаут");
                  return null;
                }
                throw error;   // сетевые ошибки пробрасываем дальше
              }
            }

            // Ручная отмена через контроллер
            const controller = new AbortController();
            const timer = setTimeout(() => controller.abort(), 5000);
            try {
              const response = await fetch("/api/slow", { signal: controller.signal });
              console.log(response.status);  // 200
            } finally {
              clearTimeout(timer);           // таймер больше не нужен
            }
            """,
        ),
        heading("Параллельные и последовательные запросы"),
        text(
            "Независимые запросы запускайте одновременно. Promise.all ждёт все промисы, но при "
            "первой ошибке отклоняется сам, не отменяя остальные; Promise.allSettled всегда "
            "завершается успешно и возвращает массив со статусом fulfilled или rejected.\n\n"
            "Последовательность нужна, когда адрес следующего запроса зависит от предыдущего. "
            "Три независимых запроса по 200 миллисекунд последовательно дадут 600, а параллельно — "
            "около 200, поэтому не заставляйте ответы ждать друг друга без причины."
        ),
        example(
            "javascript",
            r"""
            // Параллельно: общее время равно самому медленному запросу
            const [users, posts] = await Promise.all([
              fetch("/api/users").then((r) => r.json()),
              fetch("/api/posts").then((r) => r.json()),
            ]);
            console.log(users.length, posts.length);

            // Последовательно: второй запрос зависит от первого
            const user = await fetch("/api/users/1").then((r) => r.json());
            const userPosts = await fetch(`/api/users/${user.id}/posts`).then((r) => r.json());

            // allSettled не падает, если часть запросов упала
            const results = await Promise.allSettled([
              fetch("/api/a"),
              fetch("/api/b"),
            ]);
            for (const result of results) {
              console.log(result.status);   // fulfilled или rejected
            }
            """,
        ),
        heading("Хранилища браузера"),
        text(
            "Хранилище выбирают по объёму и назначению. localStorage держит пары ключ-значение "
            "бессрочно и доступен всем вкладкам домена; sessionStorage очищается при закрытии "
            "вкладки и подходит для черновиков. Оба синхронны, ограничены примерно 5 МБ и хранят "
            "только строки. IndexedDB — клиентская база данных с индексами, транзакциями и "
            "объёмом в десятки мегабайт.\n\n"
            "Куки автоматически уходят на сервер с каждым запросом, поэтому подходят для сессии, "
            "но не для объёмных данных. document.cookie возвращает одну строку, которую нужно "
            "разбирать вручную. Куки с флагом HttpOnly из JavaScript недоступны — это защита "
            "от кражи сессии через XSS."
        ),
        table(
            ["Хранилище", "Объём", "Время жизни", "Синхронность", "Тип данных"],
            [
                ["localStorage", "около 5 МБ", "до явного удаления", "синхронное", "строки"],
                ["sessionStorage", "около 5 МБ", "до закрытия вкладки", "синхронное", "строки"],
                ["IndexedDB", "десятки МБ и больше", "до явного удаления", "асинхронное", "структурированные объекты"],
                ["cookies", "около 4 КБ на куку", "по атрибуту max-age", "синхронное", "строки, уходят на сервер"],
            ],
        ),
        example(
            "javascript",
            r"""
            const storage = localStorage;   // или sessionStorage

            storage.setItem("theme", "dark");
            console.log(storage.getItem("theme"));    // dark
            console.log(storage.getItem("missing"));  // null
            console.log(storage.length);              // 1

            // Хранятся только строки: числа приводятся, объекты превращаются в [object Object]
            storage.setItem("count", 5);
            console.log(storage.getItem("count"));    // '5' — строка

            // Объекты сериализуем в JSON и разбираем обратно
            const settings = { theme: "dark", fontSize: 14 };
            storage.setItem("settings", JSON.stringify(settings));

            const raw = storage.getItem("settings");
            const parsed = raw ? JSON.parse(raw) : null;
            console.log(parsed.fontSize);             // 14

            storage.removeItem("count");
            console.log(storage.getItem("count"));    // null
            """,
        ),
        text(
            "Запись в хранилище может выбросить исключение: в приватном режиме она запрещена, "
            "а при переполнении квоты setItem бросает QuotaExceededError. Оборачивайте запись в "
            "try/catch. И помните, что JSON.parse(null) падает — проверяйте результат getItem "
            "на null перед разбором.\n\n"
            "IndexedDB многословна: open возвращает запрос, onupgradeneeded создаёт хранилища "
            "объектов и индексы, операции идут внутри транзакций, а tx.oncomplete подтверждает "
            "фиксацию. Обёртка idb превращает этот API в промисы."
        ),
        example(
            "javascript",
            r"""
            const request = indexedDB.open("AppDB", 1);

            request.onupgradeneeded = (event) => {
              const db = event.target.result;
              if (!db.objectStoreNames.contains("users")) {
                const store = db.createObjectStore("users", {
                  keyPath: "id",
                  autoIncrement: true,
                });
                store.createIndex("email", "email", { unique: true });
              }
            };

            request.onsuccess = (event) => {
              const db = event.target.result;

              // Запись: транзакция readwrite
              const write = db.transaction("users", "readwrite");
              write.objectStore("users").add({ name: "Анна", email: "anna@example.com" });
              write.oncomplete = () => console.log("Записано");   // Записано

              // Чтение по индексу
              const read = db.transaction("users", "readonly");
              const byEmail = read.objectStore("users").index("email");
              const get = byEmail.get("anna@example.com");
              get.onsuccess = () => console.log(get.result.name);  // Анна
            };

            request.onerror = (event) => {
              console.log("Ошибка открытия:", event.target.error.name);
            };
            """,
        ),
        heading("URL, URLSearchParams и History API"),
        text(
            "Объект URL разбирает адрес на части и собирает обратно, а на некорректной строке "
            "бросает TypeError, поэтому он удобен для проверки адресов из данных. Второй аргумент "
            "задаёт базу для относительных ссылок: new URL('/api/users', location.origin) даёт "
            "абсолютный адрес.\n\n"
            "Параметры запроса доступны через url.searchParams — объект URLSearchParams с методами "
            "get, getAll, has, set, append и delete. get возвращает первое значение, для "
            "повторяющихся параметров вида tag=js&tag=css нужен getAll. Изменения сразу отражаются "
            "в url.search, а кодирование символов браузер выполняет сам."
        ),
        example(
            "javascript",
            r"""
            const url = new URL("https://example.com/shop?tag=js&tag=css&page=2#top");

            console.log(url.origin);                 // https://example.com
            console.log(url.pathname);               // /shop
            console.log(url.hash);                   // #top
            console.log(url.searchParams.get("tag"));    // js
            console.log(url.searchParams.getAll("tag")); // [ 'js', 'css' ]
            console.log(url.searchParams.has("page"));   // true

            url.searchParams.set("page", "3");       // заменить
            url.searchParams.append("sort", "price"); // добавить
            url.searchParams.delete("tag");          // удалить все tag

            console.log(url.search);                 // ?page=3&sort=price
            console.log(url.toString());             // https://example.com/shop?page=3&sort=price#top

            // Относительный адрес от базы
            const api = new URL("/api/users", "https://example.com");
            console.log(api.href);                   // https://example.com/api/users

            // Некорректная строка — исключение TypeError
            try {
              new URL("не адрес");
            } catch (error) {
              console.log(error.name);               // TypeError
            }
            """,
        ),
        text(
            "History API меняет адресную строку и сохраняет состояние без перезагрузки страницы — "
            "на нём строятся маршрутизаторы SPA. pushState добавляет запись в историю, "
            "replaceState заменяет текущую; оба принимают состояние и новый адрес, а состояние "
            "доступно в history.state.\n\n"
            "Ключевой момент: pushState и replaceState не вызывают popstate. Событие приходит "
            "только на кнопки назад и вперёд, поэтому после своего pushState интерфейс нужно "
            "отрисовать вручную. pushState работает лишь в пределах текущего источника, "
            "иначе выбрасывается SecurityError."
        ),
        example(
            "javascript",
            r"""
            function render(path, state) {
              console.log("Страница:", path, "состояние:", state);
            }

            function navigate(path, state = {}) {
              history.pushState(state, "", path);
              render(path, state);      // рисуем сами: popstate не придёт
            }

            window.addEventListener("popstate", (event) => {
              render(location.pathname, event.state);  // кнопки назад и вперёд
            });

            navigate("/profile/42", { tab: "posts" });
            // Страница: /profile/42 состояние: { tab: 'posts' }

            history.replaceState({ tab: "about" }, "", "/profile/42");
            console.log(history.state);       // { tab: 'about' }
            console.log(history.length);      // число записей в истории
            """,
        ),
        heading("Формы: FormData и валидация"),
        text(
            "Конструктор FormData принимает элемент form и читает все успешные поля: у поля "
            "должен быть атрибут name, отключённые поля пропускаются, checkbox и radio попадают "
            "только отмеченными. Если передать объект в fetch как body, браузер сам выставит "
            "Content-Type multipart/form-data, а файлы отправятся бинарными частями. Для JSON "
            "используйте Object.fromEntries(formData).\n\n"
            "Проверять поля платформа умеет сама через Constraint Validation API: атрибуты "
            "required, type=email, min, max, minlength, maxlength и pattern задают ограничения. "
            "Свойство validity содержит флаги по видам нарушений, validationMessage — текст "
            "ошибки, checkValidity возвращает результат проверки, reportValidity ещё и показывает "
            "подсказку. Своё правило задаёт setCustomValidity: пустая строка снимает ошибку.\n\n"
            "Помните: form.submit() обходит событие submit и проверки, а form.requestSubmit() "
            "ведёт себя как нажатие кнопки и потому предпочтительнее."
        ),
        example(
            "javascript",
            r"""
            // HTML: <form id="login"><input name="email" type="email" required>
            //       <input name="password" type="password" required></form>
            const form = document.querySelector("#login");

            form.addEventListener("submit", (event) => {
              event.preventDefault();               // без перезагрузки страницы

              const data = new FormData(form);
              for (const [name, value] of data) {
                if (name === "password") continue;  // пароль не выводим
                console.log(name, "=", value);
              }

              // Преобразование в обычный объект для JSON-запроса
              const payload = Object.fromEntries(data);
              console.log(Object.keys(payload));    // [ 'email', 'password' ]
            });

            const email = form.elements.email;
            email.addEventListener("invalid", (event) => {
              event.preventDefault();               // отключить встроенную подсказку
            });

            // Своя проверка: setCustomValidity("") снимает ошибку
            if (!email.value.endsWith("@example.com")) {
              email.setCustomValidity("Нужен адрес в домене example.com");
            } else {
              email.setCustomValidity("");
            }
            console.log(email.checkValidity());     // false при чужом домене
            """,
        ),
        example(
            "javascript",
            r"""
            // Отправка формы целиком через fetch с блокировкой кнопки
            const form = document.querySelector("#signup");

            form.addEventListener("submit", async (event) => {
              event.preventDefault();
              const button = form.querySelector('button[type="submit"]');
              button.disabled = true;

              try {
                const response = await fetch(form.action, {
                  method: form.method || "POST",
                  body: new FormData(form),
                });
                if (response.status === 422) {
                  const errors = await response.json();
                  console.log("Ошибки полей:", errors.fields);  // { email: 'Занят' }
                  return;
                }
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                console.log("Зарегистрировано");
              } catch (error) {
                console.log("Сетевая ошибка:", error.message);
              } finally {
                button.disabled = false;      // кнопка снова активна
              }
            });
            """,
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["`el.innerHTML = userInput`", "Пользовательские данные исполняются как HTML и код (XSS)", "`el.textContent = userInput` или `createElement`"],
                ["ожидание, что `querySelectorAll` вернёт массив", "У NodeList нет `map` и `filter`, код падает", "`[...els]` или `Array.from(els)` перед вызовом методов массива"],
                ["не проверяется `response.ok`", "Ответ 404 или 500 разбирается как данные, ошибка всплывает позже", "Проверять `ok` до чтения тела и бросать свою ошибку"],
                ["повторное `await response.json()`", "Тело уже прочитано, второе чтение даёт ошибку", "Читать один раз или клонировать через `response.clone()`"],
                ["слушатели не снимаются", "Накапливаются подписки, растёт память и число вызовов", "`{ once: true }`, `removeEventListener` или `AbortSignal`"],
                ["`JSON.parse(localStorage.getItem(...))` без проверки", "`JSON.parse(null)` возвращает null не всегда ожидаемо и падает на мусоре", "`const raw = getItem(k); raw ? JSON.parse(raw) : fallback`"],
                ["расчёт на `popstate` после `pushState`", "Интерфейс не обновляется, так как события нет", "Вызывать отрисовку сразу после `pushState`"],
                ["`form.submit()` для программной отправки", "Событие `submit` и валидация не выполняются", "`form.requestSubmit()`"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняйте в браузере с открытым файлом HTML и подключённым скриптом. "
            "Открывайте консоль разработчика, чтобы проверять вывод и состояние DOM. "
            "Для заданий с сетью подойдёт локальный сервер или публичный открытый API."
        ),
        numbered(
            "Счётчик кликов: создайте кнопку через `createElement`, добавьте её в документ и повесьте слушатель, который увеличивает число в `textContent`. Убедитесь, что повторное нажатие перезаписывает текст, а не добавляет новый узел.",
            "Делегирование: соберите список из 5 пунктов через `DocumentFragment` и один слушатель на `ul`, который по клику переключает класс `done` у нужного `li` через `closest` и `classList.toggle`.",
            "Загрузка данных: напишите функцию `loadJson(url)`, которая проверяет `response.ok`, отменяет запрос через `AbortSignal.timeout(3000)` и возвращает `null` при таймауте. Выведите результат для существующего и для несуществующего адреса.",
            "Настройки в хранилище: реализуйте функции `saveSettings(obj)` и `loadSettings()`, которые пишут и читают объект из `localStorage` через `JSON.stringify` и `JSON.parse`, корректно обрабатывая отсутствующее значение.",
            "Черновик формы: перехватите `submit`, отмените перезагрузку, выведите все значения через `FormData` и сохраните черновик в `sessionStorage`, чтобы после перезагрузки страницы поля восстановились.",
        ),
        text(
            "Пример ожидаемого вывода для третьего задания "
            "(используется публичный сервис, который возвращает служебные данные):"
        ),
        example(
            "text",
            """
            Существующий адрес: { id: 'a1', title: 'Данные получены' }
            Несуществующий адрес: HTTP 404
            Медленный адрес: Запрос отменён или истёк таймаут
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 5",
            "Восстановление черновика делайте в обработчике DOMContentLoaded: к этому моменту "
            "поля формы уже существуют в дереве. Очищайте черновик после успешной отправки, "
            "иначе старые данные будут возвращаться при следующем визите."
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем NodeList, возвращённый querySelectorAll, отличается от HTMLCollection из getElementsByClassName?",
            "Почему слушатель на родителе видит клики по дочерним элементам и как это использовать?",
            "Почему fetch не выбрасывает исключение при ответе 404 и что нужно проверить?",
            "В каких случаях выбирают IndexedDB, а не localStorage?",
            "Почему после вызова history.pushState обработчик popstate не выполняется?",
        ),
        heading("Ответы", 3),
        numbered(
            "NodeList статичен: это снимок на момент вызова, в нём есть forEach, но нет map и filter. HTMLCollection живёт: отражает изменения документа, но не имеет forEach без приведения к массиву.",
            "Потому что событие всплывает от цели к родителям, что и есть фаза bubbling. Слушатель на контейнере получает события детей, определяет нужный элемент через event.target.closest и так обслуживает динамически добавленные узлы одним обработчиком.",
            "Потому что отклонение происходит только при сетевой ошибке; статусы 4xx и 5xx считаются доставленным ответом. Нужно проверить response.ok (или response.status) и самостоятельно бросить ошибку.",
            "Когда данных много, они структурные, а синхронная блокировка главного потока недопустима. IndexedDB асинхронна, хранит объекты и индексы и имеет квоту в десятки мегабайт против примерно 5 МБ у localStorage.",
            "Событие popstate браузер отправляет только при навигации пользователя — кнопками назад и вперёд. pushState лишь добавляет запись в историю, поэтому отрисовку по новому адресу нужно выполнить самостоятельно.",
        ),
        heading("Итоги"),
        bullets(
            "DOM: `querySelector` и `querySelectorAll` для поиска, `createElement` и `DocumentFragment` для массовой вставки, `classList` и `dataset` для состояния.",
            "Безопасность: `textContent` и `createElement` вместо `innerHTML` с пользовательскими данными.",
            "События: фазы перехвата, цели и всплытия, options `capture`, `once`, `passive`, `signal`, делегирование через `closest`.",
            "Fetch: проверка `response.ok`, чтение тела один раз или через `clone`, отмена через `AbortController` и `AbortSignal.timeout`.",
            "Хранилища: `localStorage` и `sessionStorage` только для строк и небольших объёмов, `IndexedDB` для структурных данных и транзакций.",
            "URL и History: `URLSearchParams` для параметров, `pushState` и `replaceState` без события `popstate`, которое приходит только от кнопок браузера.",
            "Формы: `FormData` читает поля по атрибуту `name`, встроенная валидация через `validity` и `setCustomValidity`, отправка через `requestSubmit`.",
        ),
        heading("Что дальше"),
        text(
            "Теперь вы умеете работать с платформой напрямую: страница, события, сеть, "
            "хранилища и формы. Следующий шаг — асинхронные шаблоны поверх этих API: "
            "очереди задач и микрозадач, кэширование ответов и повторные попытки при сбоях. "
            "Полезное упражнение перед следующей темой — переписать одно из заданий практики "
            "так, чтобы отмена запроса освобождала все слушатели через `AbortSignal`."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "MDN: Document Object Model — developer.mozilla.org/ru/docs/Web/API/Document_Object_Model",
            "MDN: Справочник по событиям — developer.mozilla.org/ru/docs/Web/Events",
            "MDN: Fetch API — developer.mozilla.org/ru/docs/Web/API/Fetch_API",
            "MDN: IndexedDB API — developer.mozilla.org/ru/docs/Web/API/IndexedDB_API",
            "MDN: History API — developer.mozilla.org/ru/docs/Web/API/History_API",
            "MDN: FormData и Constraint Validation — developer.mozilla.org/ru/docs/Web/API/FormData",
            "Jake Archibald: In The Loop про задачи и микрозадачи — jakearchibald.com/2015/tasks-microtasks-queues-and-schedules/",
            "web.dev: Storage for the web — web.dev/storage-for-the-web/",
        ),
    ],
}
