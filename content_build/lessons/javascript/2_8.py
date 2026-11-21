"""Урок 8 курса JavaScript: Node.js."""

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
    "topic_order": 8,
    "name": "2.8. Node.js",
    "slug": "javascript-2-8-nodejs",
    "short_description": (
        "Среда выполнения Node.js: модули ESM и CommonJS, объект process, работа с "
        "файловой системой, потоки, HTTP-сервер на встроенных средствах и переменные окружения."
    ),
    "topic_name": "Node.js",
    "topic_description": (
        "Практическое введение в серверный JavaScript: как устроена среда выполнения, "
        "как организуются модули, как читать файлы и создавать HTTP-сервер, "
        "как настраивать приложение через переменные окружения и обрабатывать завершение процесса."
    ),
    "learning_objectives": [
        "Понимать, из каких частей состоит среда выполнения Node.js: движок V8, libuv, очередь событий",
        "Создавать модули в формате ESM и CommonJS, подключать встроенные модули Node.js",
        "Использовать объект process: аргументы командной строки, переменные окружения, код завершения",
        "Работать с файловой системой через промисный API модуля node:fs/promises",
        "Читать и записывать большие файлы через потоки и функцию pipeline",
        "Создавать HTTP-сервер на встроенном модуле node:http и отвечать JSON-данными",
        "Выносить настройки в переменные окружения и корректно завершать процесс по сигналу",
    ],
    "estimated_minutes": 35,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": ["javascript", "node.js", "модули", "filesystem", "http", "process"],
    "starter_code": code(
        """
        import { createServer } from "node:http";

        const PORT = Number(process.env.PORT) || 3000;

        const server = createServer((req, res) => {
          if (req.url === "/health") {
            res.writeHead(200, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ status: "ok" }));
            return;
          }
          res.writeHead(404);
          res.end("Not Found");
        });

        server.listen(PORT, () => {
          console.log(`Сервер запущен: http://localhost:${PORT}`);
        });
        """
    ),
    "hints": [
        "Встроенные модули подключайте с префиксом node:, например import path from \"node:path\". Так видно, что модуль встроенный, а не из node_modules.",
        "В ESM-файлах нет переменных __dirname и __filename. Их получают через new URL(\".\", import.meta.url) или fileURLToPath(import.meta.url).",
        "Если файл большой, не читайте его целиком через readFile: используйте createReadStream и pipeline из node:stream/promises.",
        "Переменные окружения всегда строки. Числовые значения приводите явно через Number() и проверяйте результат на NaN.",
    ],
    "content": [
        text(
            "До этого момента весь ваш код выполнялся в браузере: у него был доступ к документу, "
            "местному хранилищу и сетевым запросам из страницы. Node.js — это среда выполнения, "
            "которая позволяет запускать JavaScript вне браузера: на сервере, в командной строке "
            "или на вашем ноутбуке. Вместо объектной модели документа она даёт доступ к файловой "
            "системе, сетевому вводу-выводу, процессам и переменным окружения.\n\n"
            "Среда выполнения (runtime) — это программа, которая читает исходный код, "
            "преобразует его во внутреннее представление и исполняет, попутно предоставляя "
            "готовые API, такие как `require` или `process`. Node.js состоит из движка V8 "
            "(того же, что в браузере Chrome, он исполняет JavaScript) и библиотеки libuv, "
            "которая берёт на себя операции ввода-вывода и таймеры.\n\n"
            "В этом уроке вы познакомитесь с ключевыми частями Node.js на практике: системой "
            "модулей, объектом `process`, работой с файлами и потоками, HTTP-сервером на "
            "встроенном модуле и настройкой через переменные окружения. Все примеры "
            "запускаются командой `node файл.mjs` без установки сторонних пакетов."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "понимать, из каких частей состоит среда выполнения Node.js и как она отличается от браузера;",
            "создавать модули в формате ESM и CommonJS и подключать встроенные модули с префиксом `node:`;",
            "использовать объект `process`: аргументы, переменные окружения, код завершения и сигналы;",
            "читать, записывать и перечислять файлы через `node:fs/promises` без блокировки процесса;",
            "обрабатывать большие файлы через потоки и функцию `pipeline`, чтобы не загружать всё в память;",
            "поднимать HTTP-сервер на `node:http`, различать маршруты и методы, отдавать JSON;",
            "выносить конфигурацию в переменные окружения, валидировать её и корректно завершать процесс.",
        ),
        heading("Как устроена среда выполнения"),
        text(
            "Node.js — это не язык и не фреймворк, а программа, встроенная в которую V8 исполняет "
            "JavaScript. Всё, что вы знаете о языке — переменные, функции, промисы, классы — "
            "работает одинаково. Отличается окружение: те глобальные объекты, которые "
            "предоставляет среда.\n\n"
            "В браузере доступны `window`, `document`, `localStorage`, `fetch`. В Node.js их нет, "
            "зато есть `process`, `Buffer`, `require` (в CommonJS), а также модули для работы "
            "с файлами и сетью. Глобальный объект здесь называется `globalThis`, и он же доступен "
            "через классический алиас `global`.\n\n"
            "Вся операция ввода-вывода — чтение файла, сетевой запрос, таймер — не выполняется "
            "в основном потоке JavaScript. libuv передаёт работу операционной системе или "
            "своему пулу потоков, а когда результат готов, колбэк ставится в очередь. "
            "Цикл событий (event loop) забирает задачи из очереди и вызывает их одну за другой. "
            "Поэтому однопоточный JavaScript успевает обслуживать тысячи одновременных соединений: "
            "поток занят только вычислениями и не простаивает в ожидании диска или сети."
        ),
        example(
            "javascript",
            """
            // global.mjs — что именно даёт Node.js поверх стандартного языка
            console.log("Версия Node.js:", process.version);
            console.log("Платформа:", process.platform);
            console.log("Архитектура:", process.arch);

            // Встроенные глобальные объекты
            console.log(typeof globalThis);   // object
            console.log(typeof process);      // object
            console.log(typeof Buffer);       // function
            console.log(typeof window);       // undefined — это не браузер
            console.log(typeof document);     // undefined
            """,
        ),
        text("Вывод: Версия Node.js: v22.11.0"),
        callout(
            "info",
            "Один поток, но не одно соединение",
            "Node.js исполняет JavaScript в одном потоке, поэтому долгие синхронные вычисления "
            "блокируют весь сервер. Тяжёлые задачи выносят в `worker_threads` или в отдельные "
            "процессы. Асинхронные операции ввода-вывода при этом идут параллельно на уровне "
            "операционной системы и не блокируют поток.",
        ),
        heading("Модули: ESM и CommonJS"),
        text(
            "Модуль — это отдельный файл со своим набором переменных, который явно определяет, "
            "что из него можно использовать снаружи. В Node.js исторически существуют две системы "
            "модулей. CommonJS появилась первой: в ней экспорт задаётся через `module.exports`, "
            "а импорт — через `require`. Спецификация ESM (`import` / `export`) является "
            "стандартной для JavaScript и сегодня считается рекомендуемым вариантов для нового кода.\n\n"
            "Тип модуля определяется расширением файла и полем `type` в ближайшем `package.json`. "
            "Файлы `.mjs` всегда ESM, файлы `.cjs` всегда CommonJS. Файлы `.js` работают как ESM, "
            "если в `package.json` указано `\"type\": \"module\"`, иначе — как CommonJS.\n\n"
            "Встроенные модули Node.js подключаются по имени, и с версии 16 к ним можно добавлять "
            "префикс `node:`. Это не формальность: префикс недвусмысленно говорит читателю, "
            "что модуль встроенный, а не установлен из `node_modules`."
        ),
        table(
            ["Система", "Экспорт", "Импорт", "Особенности"],
            [
                ["ESM", "`export` / `export default`", "`import ... from ...`", "Статический анализ, `import.meta`, top-level await"],
                ["CommonJS", "`module.exports` / `exports.x`", "`require(...)`", "`__dirname`, `__filename`, синхронная загрузка"],
            ],
        ),
        example(
            "javascript",
            """
            // math.mjs — модуль с именованным и по умолчанию экспортом
            export const PI = 3.14159;

            export function circleArea(radius) {
              return PI * radius ** 2;
            }

            export default function format(value, digits = 2) {
              return value.toFixed(digits);
            }
            """,
        ),
        example(
            "javascript",
            """
            // app.mjs — импорт частей модуля
            import format, { circleArea, PI } from "./math.mjs";

            console.log(PI);                      // 3.14159
            console.log(format(circleArea(2)));   // 12.57
            """,
        ),
        heading("Встроенные модули и import.meta", 3),
        text(
            "В ESM нет переменных `__dirname` и `__filename`, потому что они были специфичны "
            "для CommonJS. Поскольку ESM работает с URL, а не с абсолютными путями, текущий "
            "файл описывается свойством `import.meta.url` в формате `file:///...`. Чтобы получить "
            "обычный путь, используют `fileURLToPath` из модуля `node:url`; в Node.js 20.11+ "
            "для каталога доступно и готовое свойство `import.meta.dirname`.\n\n"
            "Чтобы указать путь относительно файла, а не текущего каталога запуска, "
            "используют `new URL(\"./data.json\", import.meta.url)` — конструктор `URL` "
            "корректно склеивает относительный путь с базовым адресом."
        ),
        example(
            "javascript",
            """
            // paths.mjs
            import { fileURLToPath } from "node:url";
            import { dirname, join } from "node:path";

            const __filename = fileURLToPath(import.meta.url);
            const __dirname = dirname(__filename);

            console.log("Файл:", __filename);

            const dataPath = join(__dirname, "data.json");
            const dataUrl = new URL("./data.json", import.meta.url);
            console.log("Через path:", dataPath);
            console.log("Через URL:", fileURLToPath(dataUrl));
            """,
        ),
        text("Вывод: Через path: /home/user/project/data.json"),
        callout(
            "warning",
            "Не берите пути от текущего каталога",
            "Относительные пути вроде `\"data.json\"` в `fs.readFile` отсчитываются от каталога, "
            "из которого запущен процесс, а не от расположения файла с кодом. Если запустить "
            "скрипт из другой папки, он не найдёт файл. Собирайте пути от `import.meta.url`.",
        ),
        heading("Объект process"),
        text(
            "`process` — это глобальный объект, описывающий текущий процесс Node.js. "
            "Через него приложение узнаёт, с какими аргументами его запустили, какие переменные "
            "окружения ему передали, сколько памяти оно занимает, и как завершиться с нужным "
            "кодом.\n\n"
            "Код завершения (exit code) — это число, которое процесс возвращает операционной "
            "системе. `0` означает успех, любое другое значение — ошибку. На этом построены "
            "сборочные скрипты и CI: команда `node script.mjs` после завершения отдаёт код, "
            "и следующий шаг выполняется только при нуле."
        ),
        table(
            ["Свойство или метод", "Что содержит"],
            [
                ["`process.argv`", "Массив аргументов: путь к node, путь к скрипту и далее всё, что передано"],
                ["`process.env`", "Объект переменных окружения, все значения в виде строк"],
                ["`process.cwd()`", "Текущий рабочий каталог"],
                ["`process.exitCode`", "Код, с которым процесс завершится после опустошения очереди"],
                ["`process.exit(code)`", "Немедленное завершение; опасен тем, что обрывает очередь"],
                ["`process.on(\"exit\", fn)`", "Обработчик последнего шага перед завершением, только синхронный код"],
            ],
        ),
        example(
            "javascript",
            """
            // sum.mjs — разбор аргументов командной строки
            const numbers = process.argv.slice(2).map(Number);

            if (numbers.some(Number.isNaN)) {
              console.error("Все аргументы должны быть числами");
              process.exit(1);
            }

            const total = numbers.reduce((acc, n) => acc + n, 0);
            console.log(`Сумма: ${total}`);
            """,
        ),
        text("Вывод для `node sum.mjs 3 4 5`: Сумма: 12"),
        text(
            "Аргументы после имени скрипта — первые два элемента `process.argv` занимают путь "
            "к исполняемому файлу Node.js и путь к самому скрипту. Поэтому разбор начинается "
            "с `slice(2)`. Если пользователь передал нечисловой аргумент, программа печатает "
            "сообщение в поток ошибок и завершается с кодом 1 — это корректный способ "
            "сигнализировать об ошибке внешним инструментам."
        ),
        heading("Файловая система: fs/promises"),
        text(
            "Модуль `node:fs` умеет всё, что нужно для работы с диском: читать и писать файлы, "
            "создавать каталоги, переименовывать, удалять. У него есть три варианта API: "
            "синхронный (например, `readFileSync`), с колбэками и промисный. В современном "
            "коде почти всегда используют промисный вариант из `node:fs/promises`: он "
            "сочетается с `async` / `await` и не блокирует поток на время дисковых операций.\n\n"
            "Все операции возвращают промис, поэтому ошибки перехватываются обычным `try` / "
            "`catch` вокруг `await`. Частая ошибка новичков — забыть `await` и получить "
            "не сам результат, а промис, который в `console.log` превращается в `Promise { <pending> }`."
        ),
        example(
            "javascript",
            """
            // files.mjs — чтение, запись и проверка существования файла
            import { readFile, writeFile, stat } from "node:fs/promises";
            import assert from "node:assert/strict";

            async function exists(path) {
              try {
                await stat(path);
                return true;
              } catch (error) {
                if (error.code === "ENOENT") return false;
                throw error;
              }
            }

            await writeFile("notes.txt", "Первая строка\\n", "utf-8");
            const content = await readFile("notes.txt", "utf-8");

            assert.equal(content, "Первая строка\\n");
            console.log("Содержимое:", content.trim());
            console.log("Файл существует:", await exists("notes.txt"));
            """,
        ),
        text("Вывод: Содержимое: Первая строка"),
        text(
            "Обратите внимание: проверка существования сделана через `stat`, а не через "
            "проверку «есть ли ошибка». Ловить все ошибки одинаково нельзя: `ENOENT` означает, "
            "что файла нет, а `EACCES` — что нет прав на чтение. Если проглотить вторую ошибку, "
            "приложение молча решит, что файла нет, и создаст его заново поверх нужного."
        ),
        heading("Каталоги и обход дерева файлов", 3),
        text(
            "Для перечисления содержимого каталога используют `readdir` с опцией "
            "`withFileTypes: true`. Тогда каждый элемент — объект `Dirent` с методами "
            "`isFile()` и `isDirectory()`, и для определения типа не нужен отдельный `stat` "
            "на каждый файл. Это заметно быстрее на крупных каталогах.\n\n"
            "`mkdir` с флагом `recursive: true` создаёт всю цепочку каталогов и не падает, "
            "если она уже существует. Это безопасный способ подготовить рабочую директорию."
        ),
        example(
            "javascript",
            """
            // walk.mjs — собрать имена всех файлов в дереве каталогов
            import { readdir, mkdir, writeFile } from "node:fs/promises";
            import { join } from "node:path";

            async function listFiles(dir, prefix = "") {
              const entries = await readdir(dir, { withFileTypes: true });
              const result = [];

              for (const entry of entries) {
                const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
                if (entry.isDirectory()) {
                  result.push(...(await listFiles(join(dir, entry.name), relative)));
                } else {
                  result.push(relative);
                }
              }
              return result;
            }

            await mkdir("demo/sub", { recursive: true });
            await writeFile("demo/a.txt", "a");
            await writeFile("demo/sub/b.txt", "b");

            console.log(await listFiles("demo"));
            """,
        ),
        text("Вывод: [ 'a.txt', 'sub/b.txt' ]"),
        heading("Потоки для больших файлов"),
        text(
            "Чтение файла целиком через `readFile` удобно, пока файл маленький. Файл в 2 ГБ "
            "не поместится в память процесса, и сервер упадёт. Для таких случаев существуют "
            "потоки (streams): данные обрабатываются кусками по несколько десятков килобайт "
            "по мере поступления, а память занята только текущим куском.\n\n"
            "`createReadStream` отдаёт данные частями, `createWriteStream` принимает. Функция "
            "`pipeline` из `node:stream/promises` соединяет поток чтения, промежуточные "
            "преобразования и поток записи, следит за обратным давлением (backpressure — когда "
            "запись не успевает за чтением, чтение приостанавливается) и кое-что важное: "
            "корректно закрывает все потоки и отклоняет свой промис при первой ошибке.\n\n"
            "Ещё один способ обработки — цикл `for await` по потоку чтения: он позволяет "
            "обработать каждый кусок вручную, например подсчитать строки."
        ),
        example(
            "javascript",
            """
            // copy.mjs — копирование файла через pipeline
            import { createReadStream, createWriteStream } from "node:fs";
            import { pipeline } from "node:stream/promises";
            import { stat } from "node:fs/promises";

            await pipeline(
              createReadStream("big.log"),
              createWriteStream("big.copy.log"),
            );

            const { size } = await stat("big.copy.log");
            console.log(`Скопировано байт: ${size}`);
            """,
        ),
        example(
            "javascript",
            """
            // lines.mjs — подсчёт строк в файле без загрузки в память
            import { createReadStream } from "node:fs";

            let lines = 0;
            for await (const chunk of createReadStream("big.log", { encoding: "utf-8" })) {
              for (const ch of chunk) {
                if (ch === "\\n") lines += 1;
              }
            }
            console.log(`Строк: ${lines}`);
            """,
        ),
        callout(
            "warning",
            "Не смешивайте потоки и readFile",
            "Если задача — скопировать, сжать или зашифровать файл, используйте `pipeline`. "
            "Комбинация `await readFile(...)` и `writeFile(...)` для больших файлов "
            "занимает память пропорционально размеру файла. `pipeline` также решает "
            "задачу освобождения дескрипторов при ошибке, которую легко забыть вручную.",
        ),
        heading("HTTP-сервер на node:http"),
        text(
            "Модуль `node:http` даёт минимальный сервер без каких-либо зависимостей. "
            "`createServer` принимает функцию-обработчик, которая получает два объекта: "
            "`req` (входящий запрос) и `res` (ответ). Объект `req` является потоком чтения "
            "тела запроса, а `res` — потоком записи ответа.\n\n"
            "Ответ всегда состоит из двух шагов: сначала заголовки (`writeHead`) и затем "
            "тело (`end`). Если вызвать `end` с текстом, Node.js отправит его и закроет ответ. "
            "Заголовок `Content-Type` сообщает клиенту, как интерпретировать тело; "
            "для JSON это `application/json; charset=utf-8`."
        ),
        table(
            ["Метод", "Назначение", "Тело запроса"],
            [
                ["GET", "Получить ресурс", "Обычно отсутствует"],
                ["POST", "Создать ресурс", "Обычно JSON"],
                ["PUT / PATCH", "Заменить или обновить ресурс", "JSON"],
                ["DELETE", "Удалить ресурс", "Обычно отсутствует"],
            ],
        ),
        example(
            "javascript",
            """
            // server.mjs — сервер с маршрутами и чтением тела запроса
            import { createServer } from "node:http";

            const tasks = [{ id: 1, title: "Изучить Node.js", done: false }];

            async function readBody(req) {
              let raw = "";
              for await (const chunk of req) raw += chunk;
              return raw ? JSON.parse(raw) : {};
            }

            const server = createServer(async (req, res) => {
              const url = new URL(req.url, `http://${req.headers.host}`);
              res.setHeader("Content-Type", "application/json; charset=utf-8");

              if (url.pathname === "/tasks" && req.method === "GET") {
                res.writeHead(200);
                res.end(JSON.stringify(tasks));
                return;
              }

              if (url.pathname === "/tasks" && req.method === "POST") {
                const body = await readBody(req);
                const task = { id: tasks.length + 1, title: body.title, done: false };
                tasks.push(task);
                res.writeHead(201);
                res.end(JSON.stringify(task));
                return;
              }

              res.writeHead(404);
              res.end(JSON.stringify({ error: "Not Found" }));
            });

            server.listen(3000, () => console.log("Сервер: http://localhost:3000"));
            """,
        ),
        text(
            "Проверить сервер можно командой `curl -X POST -H \"Content-Type: application/json\" "
            "-d '{\"title\": \"Новая задача\"}' http://localhost:3000/tasks`. В ответ придёт "
            "созданный объект с кодом 201. Разбор запроса выполнен через встроенный класс "
            "`URL`: он разбирает и путь, и строку запроса, и не требует модуля `node:url` "
            "в устаревшем виде."
        ),
        heading("Переменные окружения и конфигурация"),
        text(
            "Переменные окружения — способ передать приложению настройки, не меняя код. "
            "В контейнерах, системах оркестрации и на хостингах это основной механизм "
            "конфигурации: один и тот же образ запускается в разных средах с разными "
            "значениями. Все переменные доступны через `process.env`, и все они строки.\n\n"
            "Файл `.env` — договорённость, а не часть Node.js: это текстовый файл со строками "
            "вида `KEY=value`. Node.js 20.6+ умеет читать его флагом `node --env-file=.env "
            "script.mjs`, а в более старых версиях для этого используют пакет `dotenv`. "
            "Файл `.env` с секретами в репозиторий не добавляют: в него кладут "
            "`.env.example` с перечнем имён переменных без значений."
        ),
        example(
            "javascript",
            """
            // config.mjs — чтение и валидация настроек
            const DEFAULT_PORT = 3000;

            function readPort(raw) {
              if (!raw) return DEFAULT_PORT;
              const port = Number(raw);
              if (!Number.isInteger(port) || port <= 0 || port > 65535) {
                throw new Error(`Некорректный PORT: ${raw}`);
              }
              return port;
            }

            export const config = {
              port: readPort(process.env.PORT),
              nodeEnv: process.env.NODE_ENV ?? "development",
              dbUrl: process.env.DATABASE_URL ?? "sqlite:./dev.db",
            };

            console.log(config);
            """,
        ),
        text("Вывод при запуске `PORT=8080 node config.mjs`:"),
        example(
            "json",
            """
            { "port": 8080, "nodeEnv": "development", "dbUrl": "sqlite:./dev.db" }
            """,
        ),
        callout(
            "info",
            "Проверяйте конфигурацию при старте",
            "Ошибка в конфигурации должна обнаруживаться сразу при запуске, а не в момент, "
            "когда клиент впервые обратился к базе. Функция `readPort` делает именно это: "
            "падает с понятным сообщением, если значение некорректно. В крупных проектах "
            "для этого используют схемы валидации, например библиотеку zod.",
        ),
        heading("Корректное завершение процесса"),
        text(
            "Когда контейнер останавливают или вы нажимаете Ctrl+C, процессу приходит "
            "сигнал: `SIGINT` при нажатии Ctrl+C, `SIGTERM` при штатной остановке. По умолчанию "
            "процесс завершается немедленно, обрывая текущие запросы. Правильнее перехватить "
            "сигнал, перестать принимать новые соединения, дождаться завершения текущих "
            "запросов и закрыть ресурсы.\n\n"
            "Вызов `server.close()` прекращает слушать порт и вызывает колбэк, когда "
            "все активные соединения закрыты. Отдельный таймер страхует от случая, когда "
            "одно соединение зависло и не даёт серверу закрыться. Такое постепенное "
            "завершение называют graceful shutdown — плавным завершением."
        ),
        example(
            "javascript",
            """
            // shutdown.mjs — плавное завершение HTTP-сервера
            import { createServer } from "node:http";

            const server = createServer((req, res) => {
              // Имитация долгой обработки
              setTimeout(() => res.end("Готово"), 2000);
            });

            server.listen(3000);

            function shutdown(signal) {
              console.log(`Получен ${signal}, завершаемся`);
              server.close(() => {
                console.log("Сервер закрыт");
                process.exit(0);
              });
              setTimeout(() => process.exit(1), 10_000).unref();
            }

            process.on("SIGINT", () => shutdown("SIGINT"));
            process.on("SIGTERM", () => shutdown("SIGTERM"));
            """,
        ),
        text(
            "Метод `unref()` у таймера говорит: не удерживай процесс живым ради меня. "
            "Без него приложение ждало бы десять секунд даже после успешного закрытия сервера. "
            "Это типичная деталь, из-за которой контейнеры медленно останавливаются: "
            "оставшиеся таймеры и незакрытые соединения держат цикл событий."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["`readFile` без `await`", "Получаете промис, а не данные", "`const data = await readFile(path, \"utf-8\")`"],
                ["`__dirname` в ESM", "`ReferenceError: __dirname is not defined`", "`dirname(fileURLToPath(import.meta.url))`"],
                ["Проверка файла через `try { readFile }` с любым `catch`", "Ошибка прав `EACCES` маскируется под отсутствие файла", "Сравнивайте `error.code === \"ENOENT\"`"],
                ["`readFile` для файла в несколько гигабайт", "Переполнение памяти, падение процесса", "`createReadStream` и `pipeline`"],
                ["Относительный путь от текущего каталога", "Приложение не находит файл при запуске из другой папки", "Собирайте путь от `import.meta.url`"],
                ["`process.exit()` до закрытия ответов", "Клиенты получают оборванные соединения", "`server.close()` и только затем `exit`"],
                ["Числовое сравнение `process.env.PORT`", "Строка сравнивается как число, получаются неверные результаты", "Приводите явно: `Number(process.env.PORT)`"],
                ["`.env` в репозитории", "Секреты попадают в историю git", "Добавьте `.env` в `.gitignore`, храните `.env.example`"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку, запуская каждый файл командой `node имя-файла.mjs`. "
            "Для проверки результата сверяйтесь с ожидаемым выводом и, если нужно, "
            "используйте `curl` для HTTP-запросов."
        ),
        numbered(
            "Разберите `process.argv`: напишите скрипт, который выводит, сколько аргументов ему передали и сколько из них являются числами; при отсутствии чисел печатает сообщение в `console.error` и завершается с кодом 1.",
            "Создайте модуль `stats.mjs` с экспортом функций `mean` и `median`, а в отдельном файле подключите его и выведите среднее и медиану массива `[4, 8, 15, 16, 23, 42]`.",
            "Напишите скрипт, который принимает путь к каталогу и выводит все имена файлов в нём через `readdir` с `withFileTypes`, отсортированные по убыванию размера.",
            "С помощью `createReadStream` посчитайте количество строк в файле, сгенерированном заранее скриптом на десять тысяч строк, и выведите только число.",
            "Дополните HTTP-сервер маршрутом `DELETE /tasks/:id`: он находит задачу по идентификатору, удаляет её и отвечает кодом 204, а если задачи нет — кодом 404 с JSON `{ \"error\": \"Not Found\" }`.",
        ),
        text("Пример ожидаемого результата для второго задания:"),
        example(
            "text",
            """
            Среднее: 18
            Медиана: 15.5
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 4",
            "Счётчик строк увеличивайте, перебирая символы каждого куска: `for (const ch of chunk)`. "
            "Не используйте `chunk.split(\"\\n\")`, потому что строка может разрезаться на границе двух кусков.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем среда выполнения Node.js отличается от браузерного окружения?",
            "Как определяется, обрабатывается ли файл `.js` как ESM или как CommonJS?",
            "Зачем нужен префикс `node:` при подключении встроенных модулей?",
            "Почему при чтении большого файла предпочитают `pipeline`, а не `readFile`?",
            "Что произойдёт, если вызвать `process.exit(0)` в момент, когда клиент ещё получает ответ?",
            "Почему нельзя выполнять сравнение `process.env.PORT > 1024` без приведения типа?",
        ),
        heading("Ответы", 3),
        numbered(
            "В браузере доступны `window`, `document` и DOM, а в Node.js — `process`, `Buffer` и модули для файловой системы и сети. Язык и движок V8 те же.",
            "По расширению (`.mjs` — ESM, `.cjs` — CommonJS) и по полю `\"type\"` в ближайшем `package.json`; без него `.js` считается CommonJS.",
            "Префикс отделяет встроенные модули от пакетов в `node_modules` и делает происхождение импорта очевидным при чтении кода.",
            "`readFile` загружает файл целиком в память, а `pipeline` обрабатывает его порциями, управляет обратным давлением и корректно освобождает потоки при ошибке.",
            "Процесс завершится немедленно, соединение оборвётся, и клиент получит неполный ответ или ошибку. Нужно сначала закрыть сервер через `server.close()`.",
            "Значения в `process.env` всегда строки, поэтому `\"80\" > 1024` сравнивает строку с числом через приведение и даёт неверный результат. Нужен явный `Number()`.",
        ),
        heading("Итоги"),
        bullets(
            "Node.js — среда выполнения JavaScript на движке V8 с библиотекой ввода-вывода libuv; однопоточная, но неблокирующая за счёт цикла событий.",
            "Модули бывают двух видов: ESM (`import` / `export`) и CommonJS (`require` / `module.exports`); тип определяется расширением и полем `type`.",
            "Встроенные модули подключают с префиксом `node:`; для путей в ESM используют `import.meta.url` и `fileURLToPath`.",
            "`process` даёт аргументы, переменные окружения, рабочий каталог и управление завершением через коды выхода и сигналы.",
            "`node:fs/promises` — основной API для файлов; ошибки различают по полю `error.code`, а не по факту исключения.",
            "Потоки и `pipeline` обрабатывают большие данные порциями, не занимая память целиком; `for await` позволяет разбирать куски вручную.",
            "`node:http` позволяет поднять сервер без зависимостей: маршрутизация, чтение тела запроса, заголовки и коды ответов делаются вручную.",
            "Конфигурацию держат в переменных окружения, валидируют при старте, а процесс завершают плавно: сначала `server.close()`, затем `exit`.",
        ),
        heading("Что дальше"),
        text(
            "Вы познакомились со встроенными возможностями Node.js. На этом фундаменте "
            "строятся все серверные проекты на JavaScript. В следующем уроке вы перейдёте "
            "к Express — минимальному фреймворку, который избавляет от ручной маршрутизации "
            "и работы с заголовками, а затем к работе с базами данных и тестированию. "
            "Пока полезно закрепить навык: напишите небольшой CLI-скрипт, который читает "
            "каталог, считает размер файлов по расширениям и выводит таблицу в терминал, "
            "собирая пути через `import.meta.url` и обрабатывая ошибки через `error.code`."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "документация Node.js: nodejs.org/docs/latest/api/ — API модулей и стабильность функций;",
            "модульная система: nodejs.org/api/esm.html — ESM, разрешение спецификаторов, `import.meta`;",
            "файловая система: nodejs.org/api/fs.html — промисный API и опции операций;",
            "потоки: nodejs.org/api/stream.html — типы потоков, обратное давление, `pipeline`;",
            "модуль http: nodejs.org/api/http.html — серверные и клиентские сценарии;",
            "гид по переменным окружения: nodejs.org/en/learn/command-line/how-to-read-environment-variables-from-nodejs.",
        ),
    ],
}
