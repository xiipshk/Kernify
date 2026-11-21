"""Урок 2.11 курса JavaScript: проект — менеджер задач."""

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
    "topic_order": 11,
    "name": "2.11. Проект",
    "slug": "javascript-2-11-проект",
    "short_description": (
        "Сборка учебного проекта «менеджер задач»: структура папок, клиент API, "
        "хранилище состояния, роутер с защитой маршрутов, перетаскивание карточек, "
        "офлайн-очередь изменений и проверка качества в CI."
    ),
    "topic_name": "Проект",
    "topic_description": (
        "Итоговый проект среднего уровня, который соединяет модули, классы, "
        "асинхронность и браузерные возможности в одно приложение. Разбираются "
        "архитектура по слоям, клиент HTTP API с обновлением токена, собственное "
        "хранилище состояния, роутер на History API, перетаскивание задач между "
        "колонками, офлайн-режим, тесты и непрерывная интеграция."
    ),
    "learning_objectives": [
        "Раскладывать проект по слоям app, pages, widgets, features, entities и shared и объяснять роль каждого слоя",
        "Писать клиент API на fetch с общим заголовком авторизации, повтором запроса и понятной ошибкой ApiError",
        "Делать хранилище состояния с подпиской и неизменяемым обновлением, а также подключать его к странице",
        "Строить роутер на History API с параметрами пути и охранниками защищённых маршрутов",
        "Реализовывать перетаскивание карточек между колонками Kanban и вычислять новую позицию задачи",
        "Добавлять офлайн-очередь изменений, тесты хранилища через поддельный сервер и проверки в непрерывной интеграции",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "javascript",
        "проект",
        "архитектура",
        "fetch",
        "роутинг",
        "офлайн",
    ],
    "starter_code": code(
        r"""
        // Фрагмент для онлайн-редактора: сборка связки store + задач.
        // В полном проекте этот код лежит в shared/store/store.js
        // и features/tasks/task-service.js.

        function createStore(initialState) {
          let state = initialState;
          const listeners = new Set();

          return {
            getState: () => state,
            setState(partial) {
              const next = typeof partial === "function" ? partial(state) : partial;
              state = { ...state, ...next };
              for (const listener of listeners) listener(state);
            },
            subscribe(listener) {
              listeners.add(listener);
              return () => listeners.delete(listener);
            },
          };
        }

        const store = createStore({ tasks: [] });

        store.subscribe((state) => {
          console.log("Задач:", state.tasks.length);
        });

        function addTask(title) {
          store.setState((state) => ({
            tasks: [
              ...state.tasks,
              { id: crypto.randomUUID().slice(0, 8), title, status: "backlog" },
            ],
          }));
        }

        addTask("Сверстать форму входа");
        addTask("Описать схему задач");
        console.table(store.getState().tasks);
        """
    ),
    "hints": [
        "Начинайте с данных и функций, а не с вёрстки: сначала опишите, что хранится в состоянии, затем сделайте генератор разметки, потом подключайте события.",
        "Все изменения состояния делайте через setState с новыми объектами и массивами через spread-оператор, иначе подписчики не увидят изменений.",
        "Защищённый маршрут без авторизации должен перенаправлять на страницу входа, а не просто показывать пустой экран.",
        "Для офлайн-очереди сохраняйте не результат, а само намерение (создать, обновить, удалить) и применяйте его к серверу в исходном порядке.",
    ],
    "content": [
        text(
            "Предыдущие уроки среднего уровня разобрали инструменты по отдельности: систему типов, "
            "замыкания, массивы и коллекции, прототипы и классы, модули, асинхронность, браузерные "
            "интерфейсы, Node.js, качество кода, безопасность и производительность. Отдельные "
            "инструменты не собираются в приложение сами, поэтому итоговый урок этого уровня "
            "посвящён проекту. Вы построите менеджер задач: приложение, где пользователь заводит "
            "проекты, раскладывает задачи по колонкам и перетаскивает их между статусами.\n\n"
            "Главная сложность реального приложения не в синтаксисе, а в организации: где хранить "
            "данные, кто отвечает за их загрузку, как не сломать всё при добавлении новой функции. "
            "Ниже показан рабочий каркас на чистом JavaScript без фреймворка, чтобы каждый элемент "
            "архитектуры был виден и оставался под вашим контролем. После урока вы сможете "
            "собрать похожее приложение от пустой папки до проверки в непрерывной интеграции, "
            "а также объяснять на собеседовании, почему слои разделены именно так.\n\n"
            "Весь код рассчитан на современные браузеры и Node.js 20. Части, которые касаются "
            "только страницы, помечены отдельно; код хранилища и клиента API можно запускать "
            "и в Node.js, и в браузере."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "раскладывать проект по слоям и объяснять, какая папка за что отвечает;",
            "писать клиент API на fetch с авторизацией, повтором запроса и ошибкой ApiError;",
            "создавать хранилище состояния с подпиской и неизменяемым обновлением;",
            "строить роутер на History API с параметрами пути и охранниками маршрутов;",
            "реализовывать перетаскивание карточек между колонками и вычислять новую позицию;",
            "добавлять офлайн-очередь изменений, тесты и проверки в непрерывной интеграции.",
        ),
        heading("Что именно строим"),
        text(
            "Учебный проект называется **Task Manager**: доска задач в стиле Kanban. "
            "**Kanban** — способ организации работы, при котором задачи лежат в колонках "
            "по статусам, например «Очередь», «В работе» и «Готово», а исполнитель переносит "
            "карточку из колонки в колонку по мере продвижения.\n\n"
            "Функциональные требования к проекту удобно держать списком: по ним же позже "
            "пишется практика и оценивается готовность. Полный набор выглядит так:\n\n"
            "- регистрация и вход, сервер выдаёт токен доступа, защищённые маршруты недоступны без входа;\n"
            "- несколько проектов, переключение между ними;\n"
            "- задачи со статусом, приоритетом, сроком и тегами;\n"
            "- перетаскивание задач между колонками;\n"
            "- фильтры и поиск по тексту, статусу и приоритету;\n"
            "- работа при потере сети с синхронизацией при возврате в онлайн.\n\n"
            "**Токен доступа** — короткая строка, которую сервер выдаёт после входа и по которой "
            "узнаёт пользователя в следующих запросах. Хранить его в `localStorage` небезопасно: "
            "любой внедрённый скрипт сможет его прочитать. Поэтому в проекте токен кладётся "
            "в cookie с флагом `HttpOnly` — такую cookie браузер отправляет автоматически, "
            "но JavaScript прочитать её не может."
        ),
        table(
            ["Требование", "Слой проекта", "Что используется"],
            [
                ["Вход и защита маршрутов", "features/auth, shared/router", "fetch, History API, охранники"],
                ["Проекты и задачи", "entities, features/tasks", "классы, модули, хранилище"],
                ["Доска со статусами", "widgets/KanbanBoard", "DOM, drag and drop"],
                ["Фильтры и поиск", "features/tasks", "Array.prototype.filter, debounce"],
                ["Офлайн-режим", "shared/offline", "IndexedDB, Service Worker, события online"],
                ["Проверки качества", "корень проекта", "Vitest, ESLint, GitHub Actions"],
            ],
        ),
        heading("Архитектура по слоям"),
        text(
            "В основе проекта лежит упрощённый **Feature-Sliced Design** — подход к организации "
            "кода, где файлы делятся по уровням ответственности, а не по типам вроде «все "
            "компоненты в одной папке». Название можно не запоминать дословно, важен принцип: "
            "у каждого слоя своя зона ответственности, и зависимости идут только в одну сторону — "
            "сверху вниз.\n\n"
            "Чем выше слой, тем конкретнее он знает про продукт. Нижние слои про продукт не знают "
            "и потому переиспользуются во всех функциях."
        ),
        table(
            ["Слой", "Ответственность", "Примеры"],
            [
                ["app", "Запуск приложения, провайдеры, конфигурация маршрутов", "app/main.js, app/routes.js"],
                ["pages", "Страницы, которые собирают виджеты и фичи", "pages/ProjectPage"],
                ["widgets", "Крупные самостоятельные блоки интерфейса", "widgets/KanbanBoard"],
                ["features", "Действия пользователя: вход, создание задачи, фильтры", "features/tasks"],
                ["entities", "Бизнес-сущности и их правила: задача, проект, пользователь", "entities/Task"],
                ["shared", "Переиспользуемое ядро без знания о продукте", "shared/api, shared/store"],
            ],
        ),
        example(
            "text",
            """
            src/
              app/
                main.js
                routes.js
              pages/
                LoginPage.js
                ProjectPage.js
              widgets/
                KanbanBoard.js
                Sidebar.js
              features/
                auth/login.js
                tasks/task-service.js
                tasks/dnd.js
              entities/
                Task.js
                Project.js
              shared/
                api/client.js
                router/router.js
                store/store.js
                offline/offline.js
                ui/button.js
            """,
        ),
        text(
            "Правило зависимостей звучит так: слой может импортировать только слои ниже себя. "
            "`pages` может брать код из `widgets`, `features`, `entities` и `shared`. Слой `shared` "
            "не может импортировать ничего из `features` или `pages` — иначе получается цикл, "
            "и файлы начинают зависеть друг от друга кольцом.\n\n"
            "Проверить справедливость правила просто: если файл из `shared` знает про задачи "
            "или про конкретный экран, он лежит не на своём месте. Переиспользуемый код не должен "
            "знать, кто его вызывает. Эта граница экономит время при росте проекта: новую функцию "
            "обычно добавляют в `features`, не трогая остальное."
        ),
        callout(
            "info",
            "Признак правильного слоя",
            "Задайте файлу вопрос «что он делает, если убрать продукт?». Кнопка, клиент HTTP и хранилище "
            "останутся полезными в любом приложении — это `shared`. Функция «перенести задачу в другую "
            "колонку» без продукта теряет смысл — это `features` или `entities`.",
        ),
        heading("Клиент API"),
        text(
            "Каждый запрос к серверу в проекте проходит через один класс `ApiClient`. "
            "**Клиент API** — слой в коде, который отвечает за все сетевые обращения: добавляет "
            "заголовки, разбирает ответ и превращает ошибки сервера в понятные исключения. "
            "Без такого слоя `fetch` вызывается десятки раз в разных файлах, а обработка ошибок "
            "в каждом месте выглядит по-своему.\n\n"
            "Ключевая часть клиента — обработка ответа 401. **HTTP-статус 401** означает, что "
            "сервер не признал пользователя: истёк срок жизни токена. Вместо того чтобы показывать "
            "ошибку, клиент один раз запрашивает новый токен и повторяет исходный запрос. "
            "Если ответы 401 приходят одновременно в нескольких местах, повторный запрос токена "
            "должен идти один, поэтому обещание обновления сохраняется в поле `refreshPromise`."
        ),
        example(
            "javascript",
            """
            export class ApiError extends Error {
              constructor(status, message, data) {
                super(message);
                this.name = "ApiError";
                this.status = status;
                this.data = data;
              }
            }

            export class ApiClient {
              constructor(baseUrl = "/api", fetchImpl = globalThis.fetch) {
                this.baseUrl = baseUrl;
                this.fetchImpl = fetchImpl;
                this.refreshPromise = null;
              }

              refresh() {
                if (!this.refreshPromise) {
                  this.refreshPromise = this.fetchImpl(`${this.baseUrl}/auth/refresh`, {
                    method: "POST",
                    credentials: "include",
                  }).then((response) => {
                    if (!response.ok) throw new ApiError(response.status, "Сессия истекла");
                    return true;
                  }).finally(() => {
                    this.refreshPromise = null;
                  });
                }
                return this.refreshPromise;
              }

              async request(path, { method = "GET", body, retry = true } = {}) {
                const options = {
                  method,
                  credentials: "include",
                  headers: { "Content-Type": "application/json" },
                };
                if (body !== undefined) options.body = JSON.stringify(body);

                let response = await this.fetchImpl(this.baseUrl + path, options);

                if (response.status === 401 && retry) {
                  await this.refresh();
                  return this.request(path, { method, body, retry: false });
                }

                if (!response.ok) {
                  const data = await response.json().catch(() => ({}));
                  throw new ApiError(response.status, data.message || "Ошибка запроса", data);
                }

                if (response.status === 204) return null;
                return response.json();
              }

              get(path) { return this.request(path); }
              post(path, body) { return this.request(path, { method: "POST", body }); }
              patch(path, body) { return this.request(path, { method: "PATCH", body }); }
              delete(path) { return this.request(path, { method: "DELETE" }); }
            }
            """,
        ),
        text(
            "Несколько деталей в этом классе важны больше остальных. Флаг `credentials: \"include\"` "
            "разрешает браузеру отправить cookie с токеном на другой источник; без него сервер "
            "не узнает пользователя. Параметр `retry = false` при повторе защищает от бесконечной "
            "серии обновлений, если сервер всё равно отвечает 401. Третье: метод `request` пытается "
            "разобрать тело ошибки в JSON, но если сервер вернул HTML или пустую страницу, "
            "выражение `catch(() => ({}))` подставляет пустой объект, и сообщение остаётся понятным.\n\n"
            "Проверить клиент можно без настоящего сервера: подставьте в конструктор вместо "
            "`fetch` свою функцию. Такой подход называется **внедрением зависимости** — "
            "объект, от которого зависит класс, передаётся снаружи, а не создаётся внутри. "
            "Именно поэтому `fetchImpl` стоит вторым аргументом конструктора."
        ),
        example(
            "javascript",
            """
            import { ApiClient, ApiError } from "./client.js";

            // Поддельный fetch, который сначала отвечает 401, затем отдаёт данные.
            let calls = 0;
            const fakeFetch = async (url, options) => {
              calls += 1;
              if (calls === 1) return { ok: false, status: 401 };
              if (url.endsWith("/auth/refresh")) return { ok: true, status: 200 };
              return {
                ok: true,
                status: 200,
                json: async () => [{ id: "t1", title: "Написать отчёт", status: "active" }],
              };
            };

            const api = new ApiClient("/api", fakeFetch);

            api.get("/tasks")
              .then((tasks) => console.log("Получили задач:", tasks.length))
              .catch((error) => {
                if (error instanceof ApiError) console.error("Статус", error.status);
              });
            """,
        ),
        example(
            "text",
            """
            Вывод:
            Получили задач: 1
            """,
        ),
        heading("Хранилище состояния"),
        text(
            "Всё изменяемое состояние приложения хранится в одном месте — **хранилище** "
            "(store). Страницы и виджеты не держат собственные копии задач: они читают данные "
            "из хранилища и подписываются на изменения. Когда задача добавляется или меняет "
            "статус, хранилище рассылает новое состояние всем подписчикам, и интерфейс "
            "перерисовывается сам.\n\n"
            "Подписка устроена через `Set`, коллекцию уникальных значений. Если один и тот же "
            "слушатель подписан дважды, он выполнится один раз — дубли не накапливаются. "
            "Метод `subscribe` возвращает функцию отписки, которую вызывают при удалении виджета, "
            "иначе слушатели остаются в памяти и продолжают работать со старым интерфейсом."
        ),
        example(
            "javascript",
            """
            export function createStore(initialState) {
              let state = { ...initialState };
              const listeners = new Set();

              function getState() {
                return state;
              }

              function setState(partial) {
                const patch = typeof partial === "function" ? partial(state) : partial;
                state = { ...state, ...patch };
                for (const listener of [...listeners]) listener(state);
              }

              function subscribe(listener) {
                listeners.add(listener);
                listener(state);
                return () => listeners.delete(listener);
              }

              return { getState, setState, subscribe };
            }
            """,
        ),
        text(
            "Обновление состояния обязано быть неизменяемым: `setState` не меняет текущий "
            "объект, а создаёт новый через spread-оператор. **Неизменяемое обновление** означает, "
            "что старый объект остаётся нетронутым, а новый содержит все прежние поля и изменённые "
            "значения. Из-за этого любое сравнение ссылок на два состояния или на два массива "
            "честно показывает, изменилось ли что-то.\n\n"
            "Массивы внутри состояния, например `tasks`, обновляются так же: `[...state.tasks, task]` "
            "создаёт новый массив, а `.push` меняет существующий. Если подписчик хранит предыдущее "
            "состояние и сравнивает массивы по ссылке, `push` оставит сравнение ложным, и экран "
            "не обновится."
        ),
        example(
            "javascript",
            """
            import { createStore } from "./store.js";

            const store = createStore({ tasks: [], filter: "all" });

            const unsubscribe = store.subscribe((state) => {
              console.log("Архив:", state.tasks.filter((t) => t.status === "готова").length);
            });

            store.setState((state) => ({
              tasks: [...state.tasks, { id: "t1", title: "Собрать доску", status: "готова" }],
            }));

            store.setState({ filter: "active" });
            unsubscribe();
            """,
        ),
        example(
            "text",
            """
            Вывод:
            Архив: 0
            Архив: 1
            """,
        ),
        text(
            "Обратите внимание: при записи `filter` подписчик срабатывает снова, хотя архив "
            "не изменился. Для небольшого приложения перерисовка всего экрана на любое изменение "
            "приемлема. Когда списки станут крупными, добавляют выборку части состояния (селектор) "
            "и перерисовывают только те части интерфейса, чьи данные действительно поменялись — "
            "об этом подробнее в уроках повышенного уровня."
        ),
        heading("Сервис задач: сущность и действия"),
        text(
            "Слой `entities` описывает, как выглядит задача и какие правила с ней связаны, "
            "слой `features` — какие действия пользователь может выполнить. Задача как объект "
            "имеет идентификатор, заголовок, статус и приоритет. **Статус** — положение задачи "
            "на доске, **приоритет** — порядок, в котором её стоит брать в работу."
        ),
        table(
            ["Поле", "Тип", "Допустимые значения"],
            [
                ["id", "string", "уникальный идентификатор, например из crypto.randomUUID"],
                ["title", "string", "непустая строка до 200 знаков"],
                ["status", "string", "backlog, active, review, done; в примерах ниже архив — статус готова"],
                ["priority", "string", "low, normal, high"],
                ["due", "string или null", "дата в формате ISO, например 2026-12-01"],
            ],
        ),
        example(
            "javascript",
            """
            export const STATUSES = ["backlog", "active", "review", "done"];

            export function createTask({ title, status = "backlog", priority = "normal" }) {
              const clean = String(title).trim();
              if (!clean) throw new Error("Заголовок задачи не может быть пустым");
              return {
                id: crypto.randomUUID(),
                title: clean.slice(0, 200),
                status: STATUSES.includes(status) ? status : "backlog",
                priority,
                due: null,
                createdAt: Date.now(),
              };
            }

            export function moveTask(tasks, taskId, toStatus, index) {
              const task = tasks.find((t) => t.id === taskId);
              if (!task || !STATUSES.includes(toStatus)) return tasks;

              const withoutTask = tasks.filter((t) => t.id !== taskId);
              const updated = { ...task, status: toStatus };
              return [
                ...withoutTask.slice(0, index),
                updated,
                ...withoutTask.slice(index),
              ];
            }
            """,
        ),
        text(
            "Функция `moveTask` не меняет исходный массив и не переставляет задачу вслепую: "
            "она сначала убирает карточку из списка, затем вставляет её в нужное место с новым "
            "статусом. Параметр `index` — позиция среди оставшихся задач, то есть та же цифра, "
            "которую браузер показывает при перетаскивании. Возврат исходного массива при "
            "неопознанном идентификаторе защищает от пустого сдвига и лишней перерисовки."
        ),
        heading("Роутер на History API"),
        text(
            "В одностраничных приложениях нет настоящего перехода между документами: все адреса "
            "ведёт один файл. Переходы имитирует **History API** — набор методов браузера, "
            "позволяющий менять адрес в строке без перезагрузки. Метод `history.pushState` "
            "добавляет адрес в историю, `replaceState` заменяет текущий, а событие `popstate` "
            "сообщает о нажатии кнопок «назад» и «вперёд».\n\n"
            "Собственный **роутер** — небольшая надстройка над этими методами. Он хранит список "
            "маршрутов, сравнивает текущий путь с шаблоном, извлекает параметры и вызывает "
            "обработчик. Шаблон `/projects/:id` превращается в регулярное выражение, где "
            "`:id` становится именованной группой, а `match.groups` даёт значение."
        ),
        example(
            "javascript",
            """
            export class Router {
              #routes = [];
              #base = "/";

              constructor(baseUrl = "/") {
                this.#base = baseUrl;
              }

              add(path, handler, guards = []) {
                const pattern = path.replace(/:([a-z]+)/g, "(?<$1>[^/]+)");
                this.#routes.push({ regex: new RegExp(`^${pattern}$`), handler, guards });
                return this;
              }

              async resolve(pathname) {
                for (const route of this.#routes) {
                  const match = pathname.match(route.regex);
                  if (!match) continue;

                  for (const guard of route.guards) {
                    if (!(await guard())) {
                      this.navigate("/login", { replace: true });
                      return null;
                    }
                  }

                  await route.handler(match.groups ?? {});
                  return route;
                }
                return null;
              }

              navigate(path, { replace = false } = {}) {
                const url = this.#base + path;
                history[replace ? "replaceState" : "pushState"](null, "", url);
                return this.resolve(path);
              }

              start() {
                window.addEventListener("popstate", () => this.resolve(location.pathname));
                return this.resolve(location.pathname);
              }
            }
            """,
        ),
        text(
            "Поля с решёткой `#routes` — приватные поля класса: они доступны только внутри класса, "
            "и снаружи их невозможно случайно перезаписать. Список **охранников** (guards) — "
            "массив асинхронных функций, каждая проверяет условие доступа. Обычная проверка — "
            "есть ли пользователь в хранилище. Если хотя бы одна вернула ложь, роутер отправляет "
            "на страницу входа и не вызывает обработчик защищённого маршрута."
        ),
        example(
            "javascript",
            """
            import { Router } from "./router.js";

            const router = new Router("/app");
            const isAuthenticated = () => Boolean(userStore.getState().user);

            router
              .add("/login", renderLogin)
              .add("/projects/:id", renderProject, [isAuthenticated])
              .add("/settings", renderSettings, [isAuthenticated]);

            function renderProject({ id }) {
              document.title = `Проект ${id}`;
            }

            function renderLogin() {
              document.title = "Вход";
            }

            function renderSettings() {
              document.title = "Настройки";
            }

            router.start();
            """,
        ),
        callout(
            "warning",
            "Сервер должен отдавать index.html",
            "Если обновить страницу по адресу `/projects/42`, браузер попросит этот путь у сервера. "
            "Настройте сервер и хостинг так, чтобы неизвестные пути отдавали `index.html`, иначе "
            "пользователь увидит страницу 404 вместо приложения.",
        ),
        heading("Доска Kanban и перетаскивание"),
        text(
            "Колонки доски собираются из `STATUSES`, а карточки рисуются из массива задач "
            "хранилища. Порядок кода в модуле виджета простой: сначала функции разметки, затем "
            "обработчики, затем подписка на хранилище. Благодаря подписке любое изменение "
            "задач автоматически приводит доску в актуальное состояние.\n\n"
            "Перетаскивание использует встроенный в браузер механизм **HTML5 Drag and Drop** — "
            "набор событий `dragstart`, `dragover`, `drop` и `dragend`. Элемент с атрибутом "
            "`draggable=\"true\"` становится перетаскиваемым, но по умолчанию браузер запрещает "
            "бросать в произвольные места: обработчик `dragover` обязан вызвать "
            "`event.preventDefault()`, иначе событие `drop` не случится."
        ),
        example(
            "javascript",
            """
            export function getDropIndex(column, clientY) {
              // Возвращает позицию, перед которой нужно вставить карточку.
              const cards = [...column.querySelectorAll("[data-task-id]")];
              const index = cards.findIndex((card) => {
                const box = card.getBoundingClientRect();
                return clientY < box.top + box.height / 2;
              });
              return index === -1 ? cards.length : index;
            }

            export function setupDnd(board, onMove) {
              let draggedId = null;

              board.addEventListener("dragstart", (event) => {
                const card = event.target.closest("[data-task-id]");
                if (!card) return;
                draggedId = card.dataset.taskId;
                event.dataTransfer.effectAllowed = "move";
              });

              board.addEventListener("dragover", (event) => {
                if (!draggedId) return;
                event.preventDefault();
                event.dataTransfer.dropEffect = "move";
              });

              board.addEventListener("drop", (event) => {
                const column = event.target.closest("[data-column-id]");
                if (!column || !draggedId) return;
                event.preventDefault();

                const status = column.dataset.columnId;
                const index = getDropIndex(column, event.clientY);
                onMove(draggedId, status, index);
              });

              board.addEventListener("dragend", () => {
                draggedId = null;
              });
            }
            """,
        ),
        text(
            "Модуль не трогает данные сам, а вызывает переданную функцию `onMove`. Такой приём "
            "называется **обратным вызовом** (callback): перетаскивание остаётся частью интерфейса "
            "и не знает, откуда берутся задачи. Подключение к хранилищу выглядит так:"
        ),
        example(
            "javascript",
            """
            import { store } from "../shared/store/app-store.js";
            import { moveTask } from "../entities/Task.js";
            import { api } from "../shared/api/app-api.js";
            import { setupDnd } from "./dnd.js";

            const board = document.querySelector("#board");

            setupDnd(board, async (taskId, status, index) => {
              const before = store.getState().tasks;
              store.setState({ tasks: moveTask(before, taskId, status, index) });

              try {
                await api.patch(`/tasks/${taskId}`, { status });
              } catch (error) {
                // Откат оптимистичного обновления: возвращаем прежний порядок.
                store.setState({ tasks: before });
                console.error("Не удалось сохранить перенос", error.message);
              }
            });
            """,
        ),
        callout(
            "info",
            "Оптимистичное обновление",
            "Порядок действий выше называют оптимистичным обновлением: интерфейс меняется сразу, "
            "не дожидаясь ответа сервера, а при ошибке изменения откатываются к сохранённой копии. "
            "Пользователь видит мгновенную реакцию, но каждое действие обязано иметь путь отката.",
        ),
        heading("Офлайн-режим и синхронизация"),
        text(
            "Если сеть пропала, приложение не должно терять введённые данные. Для этого нужен "
            "**Service Worker** — фоновый скрипт, который браузер запускает отдельно от страницы "
            "и который умеет перехватывать сетевые запросы и отдавать закэшированные файлы. "
            "Он позволяет открыть приложение без сети, а также получать события push.\n\n"
            "Изменения, сделанные офлайн, складываются в **очередь изменений** в **IndexedDB** — "
            "встроенной в браузер базе данных, которая, в отличие от `localStorage`, не ограничена "
            "несколькими мегабайтами и умеет хранить объекты без ручной сериализации. "
            "Каждая запись очереди описывает намерение: тип действия и данные задачи. Когда "
            "появляется сеть, очередь проигрывается по порядку и очищается по мере успеха.\n\n"
            "Порядок строго важен: если удаление уйдёт на сервер раньше создания, сервер ответит "
            "ошибкой. Поэтому при первой неудаче очередь остаётся как есть и повторяется позже."
        ),
        example(
            "javascript",
            """
            const DB_NAME = "task-manager";
            const QUEUE = "mutations";

            function openDb() {
              return new Promise((resolve, reject) => {
                const request = indexedDB.open(DB_NAME, 1);
                request.onupgradeneeded = () => {
                  request.result.createObjectStore(QUEUE, { keyPath: "id", autoIncrement: true });
                };
                request.onsuccess = () => resolve(request.result);
                request.onerror = () => reject(request.error);
              });
            }

            export async function enqueue(mutation) {
              const db = await openDb();
              const tx = db.transaction(QUEUE, "readwrite");
              tx.objectStore(QUEUE).add({ ...mutation, createdAt: Date.now() });
              await new Promise((resolve) => { tx.oncomplete = resolve; });
            }

            export async function syncAll(api) {
              const db = await openDb();
              const all = await new Promise((resolve) => {
                const request = db.transaction(QUEUE).objectStore(QUEUE).getAll();
                request.onsuccess = () => resolve(request.result);
              });

              for (const mutation of all.sort((a, b) => a.id - b.id)) {
                try {
                  if (mutation.type === "create") await api.post("/tasks", mutation.payload);
                  if (mutation.type === "update") await api.patch(`/tasks/${mutation.payload.id}`, mutation.payload);
                  if (mutation.type === "delete") await api.delete(`/tasks/${mutation.payload.id}`);
                } catch (error) {
                  console.warn("Синхронизация остановлена", error.message);
                  return;
                }

                await new Promise((resolve) => {
                  const tx = db.transaction(QUEUE, "readwrite");
                  tx.objectStore(QUEUE).delete(mutation.id);
                  tx.oncomplete = resolve;
                });
              }
            }

            window.addEventListener("online", () => syncAll(api));
            """,
        ),
        heading("Тесты и непрерывная интеграция"),
        text(
            "Тест хранилища проверяет поведение, а не внутреннюю реализацию: подписка срабатывает "
            "при обновлении, отписка прекращает вызовы, функция-обновление получает текущее "
            "состояние. **Vitest** — инструмент для запуска тестов в проектах на JavaScript; "
            "его функцию `vi.fn()` используют для создания подставного слушателя, который "
            "запоминает вызовы."
        ),
        example(
            "javascript",
            """
            import { describe, it, expect, vi } from "vitest";
            import { createStore } from "../store.js";

            describe("createStore", () => {
              it("вызывает подписчика сразу и на каждое изменение", () => {
                const store = createStore({ count: 0 });
                const listener = vi.fn();
                const unsubscribe = store.subscribe(listener);

                store.setState({ count: 1 });
                expect(listener).toHaveBeenCalledTimes(2);

                unsubscribe();
                store.setState({ count: 2 });
                expect(listener).toHaveBeenCalledTimes(2);
              });

              it("передаёт в обновление текущее состояние", () => {
                const store = createStore({ count: 2 });
                store.setState((state) => ({ count: state.count * 3 }));
                expect(store.getState().count).toBe(6);
              });
            });
            """,
        ),
        example(
            "text",
            """
            Вывод:
            Test Files  1 passed (1)
                 Tests  2 passed (2)
              createStore > вызывает подписчика сразу и на каждое изменение PASSED
              createStore > передаёт в обновление текущее состояние PASSED
            """,
        ),
        text(
            "Запросы к серверу в тестах подменяют **MSW** (Mock Service Worker) — библиотекой, "
            "которая перехватывает сетевые вызовы и отвечает так, как описано в тесте. "
            "В отличие от замены `fetch` вручную, MSW работает на уровне сети и одинаково "
            "применим в юнит-тестах, в браузере и в end-to-end проверках. Тест ниже проверяет, "
            "что клиент API разбирает ответ и что список задач непустой."
        ),
        example(
            "javascript",
            """
            import { http, HttpResponse } from "msw";
            import { setupServer } from "msw/node";
            import { beforeAll, afterEach, afterAll, it, expect } from "vitest";
            import { api } from "../shared/api/client.js";

            const server = setupServer(
              http.get("/api/tasks", () =>
                HttpResponse.json([{ id: "t1", title: "Написать тесты", status: "active" }]),
              ),
            );

            beforeAll(() => server.listen());
            afterEach(() => server.resetHandlers());
            afterAll(() => server.close());

            it("загружает список задач", async () => {
              const tasks = await api.get("/tasks");
              expect(tasks).toHaveLength(1);
              expect(tasks[0].status).toBe("active");
            });
            """,
        ),
        text(
            "**Непрерывная интеграция** (CI, Continuous Integration) — автоматический запуск "
            "проверок при каждом пуше или pull request. В проекте на GitHub это файл "
            "`.github/workflows/ci.yml`, где перечислены шаги: линтер, тесты и сборка. "
            "Если хотя бы один шаг падает, merge блокируется, и в основную ветку не попадает "
            "код, который не проходит проверки."
        ),
        example(
            "yaml",
            """
            name: CI
            on:
              push:
                branches: [main]
              pull_request:

            jobs:
              check:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: actions/setup-node@v4
                    with:
                      node-version: "20"
                      cache: npm
                  - run: npm ci
                  - run: npm run lint
                  - run: npm test -- --run
                  - run: npm run build
            """,
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Менять состояние через `state.tasks.push(...)`", "Подписчики не видят изменения или видят их случайно", "Создавать новый массив: `[...state.tasks, task]`"],
                ["Хранить токен в `localStorage`", "Токен доступен любому внедрённому скрипту", "Cookie с флагом `HttpOnly` и `credentials: \"include\"`"],
                ["Повторять запрос счёт 401 без ограничения", "Бесконечная серия обновления токена", "Повторять один раз с флагом `retry: false`"],
                ["Не вызывать `preventDefault` в `dragover`", "Событие `drop` не наступает, карточка не переносится", "Отменить действие браузера по умолчанию в `dragover`"],
                ["Сервер отвечает 404 на `/projects/42`", "Обновление страницы ломает приложение", "Отдавать `index.html` на все пути роутера"],
                ["Забыть отписку от хранилища", "Старые обработчики остаются в памяти и работают", "Вызывать функцию, возвращённую `subscribe`"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания идут от простого к сложному и складываются в один проект. "
            "Каждое можно проверить в браузере на локальном сервере или в Node.js. "
            "Для запуска используйте `npx vite` в папке проекта и открывайте адрес из вывода."
        ),
        numbered(
            "Разложите пустой проект по слоям из таблицы архитектуры и создайте файл-заглушку в каждом слое. Проверьте, что файлы импортируются без циклов.",
            "Добавьте в `ApiClient` параметр `retry` и продемонстрируйте на поддельном `fetch`, что при первом ответе 401 запрос повторяется ровно один раз.",
            "Реализуйте `addFilter(store)` для задач: функции по статусу, по тексту и по приоритету, объединённые в одну. Проверьте на массиве из пяти задач.",
            "Добавьте в роутер обработку неизвестного пути: если ни один маршрут не совпал, показывать страницу 404 и менять заголовок вкладки.",
            "Соберите доску с четырьмя колонками, нарисуйте разметку из хранилища и подключите перетаскивание. Проверьте, что после переноса задача существует в единственном экземпляре.",
            "Добавьте проверку `npm run lint` и `npm test` в workflow GitHub Actions и убедитесь, что падение теста блокирует merge.",
        ),
        text("Ожидаемый результат четвёртого задания для адреса `/projects/42/archive`:"),
        example(
            "text",
            """
            Вывод:
            Заголовок вкладки: Страница не найдена
            Адрес в строке: /app/404
            """,
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему клиент API обновляет токен только один раз для каждого запроса?",
            "Чем обновление состояния через `setState` отличается от прямого изменения объекта?",
            "Что произойдёт, если в обработчике `dragover` не вызвать `preventDefault`?",
            "Почему сервер должен отдавать `index.html` для адресов роутера?",
            "Почему офлайн-очередь изменений не удаляет запись при неудачной отправке?",
        ),
        heading("Ответы", 3),
        numbered(
            "Иначе истёкшая сессия приводит к бесконечным повторам: каждый новый ответ 401 снова запускает обновление. Одного повтора достаточно, чтобы пережить устаревший токен, а при провале ошибка возвращается вызывающему коду.",
            "`setState` создаёт новый объект состояния и уведомляет всех подписчиков. Прямое изменение меняет текущий объект, и сравнение по ссылке не покажет изменений, поэтому подписчики могут не сработать.",
            "Браузер считает область недоступной для сброса и не создаст событие `drop`, поэтому перенос не завершится. Отмена действия по умолчанию переводит элемент в допустимую цель.",
            "Переходы внутри приложения не перезагружают страницу, но обновление вкладки или прямая ссылка заставляют сервер искать файл с таким путём. Отдавая `index.html`, сервер передаёт маршрут роутеру.",
            "Удаление потеряет действие, если сеть снова пропадёт. Запись остаётся, пока сервер не подтвердит успех, и отправляется в исходном порядке при следующей попытке.",
        ),
        heading("Итоги"),
        bullets(
            "Слои app, pages, widgets, features, entities и shared держат ответственность по уровням, импорты идут только вниз.",
            "Клиент API берёт на себя заголовки, токен, повтор после 401 и превращает ошибки сервера в `ApiError`.",
            "Хранилище с подпиской и неизменяемым обновлением связывает данные и интерфейс без ручных перерисовок.",
            "Роутер на History API сопоставляет шаблоны путей, извлекает параметры и проверяет доступ через охранников.",
            "Перетаскивание карточек вызывает обратный вызов, а данные меняет сервис, сохраняя путь отката при ошибке сервера.",
            "Офлайн-очередь в IndexedDB проигрывается по порядку и очищается только после подтверждения сервером.",
            "Проверки в CI не дают попасть в основную ветку коду, который не проходит линтер, тесты или сборку.",
        ),
        heading("Что дальше"),
        text(
            "Уровень среднего JavaScript завершён. Следующий шаг — повышенный уровень: типизированный "
            "JavaScript и TypeScript, продвинутые шаблоны компонентов, серверный Node.js для того же "
            "проекта и внутреннее устройство модулей. Готовьтесь поддерживать проект в рабочем "
            "состоянии: чем осознаннее границы слоёв, тем проще будет подключать новые инструменты "
            "и технологии без переписывания готового кода."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "MDN: Drag and Drop API — developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API",
            "MDN: History API — developer.mozilla.org/en-US/docs/Web/API/History_API",
            "MDN: IndexedDB API — developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API",
            "Документация Feature-Sliced Design — feature-sliced.design/docs",
        ),
    ],
}
