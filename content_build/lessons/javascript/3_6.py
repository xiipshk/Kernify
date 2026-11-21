"""Урок 3.6 курса JavaScript: внутреннее устройство Node.js."""

from content_build.lesson_kit import code, text, heading, bullets, numbered, table, callout, example


LESSON = {
    "language": "javascript",
    "program_order": 3,
    "topic_order": 6,
    "name": "3.6. Внутреннее устройство Node.js",
    "slug": "javascript-3-6-внутреннее-устройство-nodejs",
    "topic_name": "Внутреннее устройство Node.js",
    "short_description": (
        "Как устроен Node.js изнутри: V8, libuv и фазы событийного цикла, очереди микрозадач, "
        "потоки и обратное давление, буферы, рабочие потоки и дочерние процессы."
    ),
    "topic_description": (
        "Механика платформы Node.js: архитектура из V8, libuv и привязок к операционной системе, "
        "порядок фаз событийного цикла, устройство потоков и обратного давления, управление "
        "двоичными данными через буферы, параллелизм рабочих потоков и межпроцессное взаимодействие."
    ),
    "learning_objectives": [
        "Объяснять архитектуру Node.js из V8, libuv и связующих привязок к операционной системе",
        "Предсказывать порядок выполнения кода по фазам событийного цикла и очередям микрозадач",
        "Различать setImmediate, setTimeout и process.nextTick и объяснять, почему nextTick опасен",
        "Строить конвейеры из потоков с корректным обратным давлением через pipeline",
        "Выбирать между Buffer.alloc и Buffer.allocUnsafe и объяснять, как копии и подпредставления разделяют память",
        "Выносить тяжёлые вычисления в рабочие потоки и организовывать обмен сообщениями и пересылку данных",
        "Выбирать между spawn, exec, execFile и fork и понимать, как работает межпроцессный канал",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "javascript",
        "nodejs",
        "event-loop",
        "streams",
        "buffers",
        "worker-threads",
    ],
    "starter_code": code(
        r"""
        'use strict';

        // Предскажите порядок строк до запуска: node app.js
        // После запуска сравните вывод со своими ожиданиями.

        console.log('1: синхронный код');

        setTimeout(() => console.log('5: setTimeout'), 0);
        setImmediate(() => console.log('4: setImmediate'));
        queueMicrotask(() => console.log('3: queueMicrotask'));
        Promise.resolve().then(() => console.log('3: promise'));
        process.nextTick(() => console.log('2: nextTick'));
        """
    ),
    "hints": [
        "process.nextTick и микрозадачи промисов выполняются после каждого колбэка, а не только после фазы. Очередь nextTick опустошается до конца, поэтому рекурсивный nextTick блокирует цикл.",
        "Обратное давление появляется тогда, когда запись в поток возвращает false. Не игнорируйте этот результат: дождитесь события drain или используйте pipeline, который делает всё сам.",
        "Память Buffer выделяется вне кучи V8, поэтому сборщик мусора её не учитывает. Утечка буфера не видна в heapUsed и проявляется только в поле rss.",
        "Рабочие потоки — не процессы: у каждого свой изолированный изолятор V8 и своя куча. Массивы копируются при пересылке, а SharedArrayBuffer разделяется по-настоящему, но требует атомарных операций.",
    ],
    "content": [
        text(
            "Node.js часто описывают как «JavaScript на сервере». Это верно, но ничего не объясняет.\n\n"
            "Акцент будет на механизмах.\n\n"
            "Все примеры рассчитаны на запуск через `node имя_файла.js` и ядро начиная с версии 16. "
            "Там, где вывод зависит от системы, это указано отдельно. Наблюдения за памятью зависят "
            "от платформы и версии движка, поэтому важны отношения между числами, а не конкретные "
            "байты."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "объяснять архитектуру Node.js и роль V8, libuv и связующих привязок;",
            "предсказывать порядок выполнения по фазам событийного цикла и очередям микрозадач;",
            "различать `setImmediate`, `setTimeout` и `process.nextTick` и распознавать голодание цикла;",
            "строить конвейеры потоков с корректным обратным давлением;",
            "осознанно работать с буферами: выделять, копировать и делить память;",
            "выносить тяжёлые вычисления в пул рабочих потоков и передавать данные без лишних копий;",
            "выбирать между `spawn`, `exec`, `execFile` и `fork` и проектировать межпроцессный обмен.",
        ),
        heading("Архитектура: V8, libuv и привязки"),
        text(
            "Среда выполнения склеена из слоёв. **V8** — движок JavaScript от проекта Chromium: он разбирает код, "
            "компилирует его и выполняет, управляет памятью и сборкой мусора. **libuv** — "
            "библиотека на C, которая предоставляет событийный цикл, неблокирующие операции "
            "ввода-вывода и общий пул системных потоков. Между ними лежат **привязки** (bindings) — "
            "код на C++, который превращает вызовы JavaScript в вызовы libuv и обратно.\n\n"
            "libuv умеет предоставлять один и тот же интерфейс на разных системах. На Linux он "
            "использует механизм `epoll`, на macOS — `kqueue`, на Windows — порты завершения "
            "ввода-вывода (IOCP). Программе на JavaScript всё равно, какая система под ней: "
            "различия скрыты внутри libuv.\n\n"
            "JavaScript выполняется в единственном основном потоке, а система сообщает о готовности сокета или файла. Поэтому синхронная тяжёлая работа блокирует всё сразу."
        ),
        table(
            ["Слой", "Ответственность", "На чём написан"],
            [
                ["V8", "Разбор, компиляция и выполнение JavaScript, куча, сборка мусора", "C++"],
                ["Привязки", "Мост между вызовами JavaScript и системными возможностями", "C++"],
                ["libuv", "Событийный цикл, неблокирующий ввод-вывод, пул потоков", "C"],
                ["Стандартная библиотека", "Модули `fs`, `net`, `http`, `stream`, `worker_threads`", "JavaScript и C++"],
                ["Операционная система", "Реальные сокеты, файлы, таймеры, потоки", "Ядро"],
            ],
        ),
        heading("Событийный цикл: фазы и порядок"),
        text(
            "Событийный цикл (event loop) — бесконечный цикл libuv, который последовательно проходит "
            "фазы. В каждой фазе выполняется своя очередь колбэков, после чего управление переходит "
            "к следующей. Фазы такие:\n\n"
            "- **Таймеры** — колбэки `setTimeout` и `setInterval`, у которых истёк срок;\n"
            "- **Отложенные колбэки** — результат операций ввода-вывода, ошибки которых были "
            "отложены на следующий проход;\n"
            "- **Ожидание и подготовка** — внутренние нужды libuv, прикладного кода почти не касаются;\n"
            "- **Опрос** — здесь цикл блокируется в ожидании событий ввода-вывода, пока не появится "
            "что-то готовое или не истечёт таймер ближайшего таймера;\n"
            "- **Проверка** — колбэки `setImmediate`, выполняются сразу после фазы опроса;\n"
            "- **Завершение** — обработчики `close`, например закрытия сокета или файлового дескриптора."
        ),
        example(
            "javascript",
            """
            'use strict';

            // Порядок строк предсказуем независимо от версии Node.js.
            console.log('1: синхронно');

            setTimeout(() => console.log('7: таймер следующей итерации'), 0);
            setImmediate(() => console.log('6: фаза проверки'));

            Promise.resolve()
              .then(() => console.log('4: микрозадача промиса'))
              .then(() => console.log('5: составная микрозадача'));

            process.nextTick(() => console.log('2: очередь nextTick'));
            queueMicrotask(() => console.log('3: микрозадача очереди'));

            console.log('1: синхронно, конец');
            """,
        ),
        text(
            "Вывод программы:\n"
            "1: синхронно\n"
            "1: синхронно, конец\n"
            "2: очередь nextTick\n"
            "3: микрозадача очереди\n"
            "4: микрозадача промиса\n"
            "5: составная микрозадача\n"
            "6: фаза проверки\n"
            "7: таймер следующей итерации"
        ),
        text(
            "`setImmediate` обгоняет `setTimeout` потому, что после синхронного кода цикл сразу доходит до фазы проверки, а таймер ещё не готов. На верхнем уровне модуля порядок этих двух функций зависит от точности таймера. Таймер с нулевой задержкой ждёт не меньше миллисекунды, а фаза проверки не ждёт ничего."
        ),
        heading("Микрозадачи и очереди nextTick"),
        text(
            "Поверх фаз работают две очереди микрозадач: **nextTick** для `process.nextTick` и очередь **промисов** для `then`, `queueMicrotask` и `finally`. Сначала уходит nextTick, затем промисы, и только потом продолжается фаза. Рекурсивный `process.nextTick` бесконечно откладывает ввод-вывод."
        ),
        example(
            "javascript",
            """
            'use strict';

            let ticks = 0;
            const started = Date.now();

            function schedule() {
              ticks += 1;
              if (ticks < 5) {
                process.nextTick(schedule);
                return;
              }
              console.log('дозаписано nextTick-колбэков:', ticks);
              console.log('промис выполнился после:', ticks);
            }

            Promise.resolve().then(() => {
              console.log('промис выполнился после nextTick-волны');
            });

            process.nextTick(schedule);
            """,
        ),
        text(
            "Вывод программы:\n"
            "дозаписано nextTick-колбэков: 5\n"
            "промис выполнился после nextTick-волны"
        ),
        callout(
            "warning",
            "Рекурсивный nextTick останавливает ввод-вывод",
            "Очередь nextTick опустошается полностью до перехода к промисам и до продолжения фаз. "
            "Код, который планирует новый `process.nextTick` из самого nextTick-колбэка, "
            "не даёт циклу перейти к сети, диску и таймерам. Флаг `--trace-warnings` и счётчик "
            "в примере помогают увидеть такое поведение: число волн растёт, а другие события стоят."
        ),
        heading("setImmediate, setTimeout и nextTick"),
        text(
            "Три похожих функции решают разные задачи."
        ),
        table(
            ["Функция", "Где выполняется", "Типичное применение"],
            [
                ["`process.nextTick`", "Очередь nextTick до промисов", "Сообщить об ошибке асинхронно, как требуют соглашения об API"],
                ["`queueMicrotask`", "Очередь микрозадач после nextTick", "Отложить работу без риска голодания цикла"],
                ["`setImmediate`", "Фаза проверки, после ввода-вывода", "Продолжить обработку после завершения ввода-вывода"],
                ["`setTimeout(fn, 0)`", "Фаза таймеров, не раньше миллисекунды", "Паузы, повторные попытки, обход ограничений рекурсии"],
            ],
        ),
        example(
            "javascript",
            """
            'use strict';

            const fs = require('fs');

            // Колбэк вызывается из фазы опроса, после получения данных файла.
            fs.readFile(__filename, () => {
              console.log('1: колбэк чтения файла');

              setTimeout(() => console.log('4: таймер следующей итерации'), 0);
              setImmediate(() => console.log('3: фаза проверки этой итерации'));
              process.nextTick(() => console.log('2: nextTick до конца колбэка'));
            });
            """,
        ),
        text(
            "Вывод программы:\n"
            "1: колбэк чтения файла\n"
            "2: nextTick до конца колбэка\n"
            "3: фаза проверки этой итерации\n"
            "4: таймер следующей итерации"
        ),
        text(
            "Метка `2` подтверждает главное правило: микрозадачи выполняются до завершения текущего колбэка, а не после фазы."
        ),
        heading("Потоки и обратное давление"),
        text(
            "**Поток** (stream) — последовательность данных, читаемая и записываемая по частям: `Readable`, `Writable`, `Duplex` и `Transform`.\n\n"
            "У потока есть буфер ограниченного размера — порог `highWaterMark`, 16 килобайт по умолчанию. Когда буфер полон, `write` возвращает `false`: это **обратное давление** (backpressure)."
        ),
        example(
            "javascript",
            """
            'use strict';

            const { Readable, Writable } = require('stream');

            // Источник выдаёт числа и учитывает, сколько ещё поместится.
            class Counter extends Readable {
              constructor(max) {
                super({ objectMode: true, highWaterMark: 2 });
                this.current = 1;
                this.max = max;
              }

              _read() {
                if (this.current > this.max) {
                  this.push(null);
                  return;
                }
                this.push(this.current++);
              }
            }

            // Приёмник медленно обрабатывает элементы.
            class SlowSink extends Writable {
              constructor() {
                super({ objectMode: true, highWaterMark: 2 });
                this.total = 0;
              }

              _write(chunk, encoding, callback) {
                this.total += chunk;
                setTimeout(callback, 1);
              }
            }

            const counter = new Counter(6);
            const sink = new SlowSink();

            counter.pipe(sink);

            sink.on('finish', () => {
              console.log('сумма:', sink.total);
            });
            """,
        ),
        text("Вывод программы:\nсумма: 21"),
        text(
            "При `false` `pipe` вызывает `pause`, а после события `drain` возобновляет чтение. Для конвейеров предпочтительнее `pipeline` из `stream/promises`."
        ),
        example(
            "javascript",
            """
            'use strict';

            const { Readable, Transform, Writable } = require('stream');
            const { pipeline } = require('stream/promises');

            const source = Readable.from(['строка один\\n', 'строка два\\n', 'строка три']);

            class Splitter extends Transform {
              constructor() {
                super({ readableObjectMode: true });
                this.pending = '';
              }

              _transform(chunk, encoding, callback) {
                this.pending += chunk.toString();
                const lines = this.pending.split('\\n');
                this.pending = lines.pop();
                for (const line of lines) {
                  if (line) this.push(line);
                }
                callback();
              }

              _flush(callback) {
                if (this.pending) this.push(this.pending);
                callback();
              }
            }

            const collected = [];
            const collector = new Writable({
              objectMode: true,
              write(line, encoding, callback) {
                collected.push(line.toUpperCase());
                callback();
              },
            });

            pipeline(source, new Splitter(), collector)
              .then(() => console.log(collected))
              .catch((error) => console.error('ошибка конвейера:', error.message));
            """,
        ),
        text("Вывод программы:\n[ 'СТРОКА ОДИН', 'СТРОКА ДВА', 'СТРОКА ТРИ' ]"),
        callout(
            "info",
            "Не собирайте файлы в строку",
            "Чтение целого файла через `readFile` и запись через `writeFile` удобны для небольших "
            "документов, но для больших они удваивают потребление памяти. Конвейер из "
            "`fs.createReadStream`, преобразований и `fs.createWriteStream` держит память на уровне "
            "размера буфера независимо от размера файла."
        ),
        heading("Буферы и двоичные данные"),
        text(
            "`Buffer` наследует `Uint8Array`, но память выделяется вне кучи V8. `alloc` обнуляет байты, `allocUnsafe` — нет. Для сборщика мусора буфер остаётся непрозрачным внешним ресурсом, и его объём не виден в `heapUsed`."
        ),
        example(
            "javascript",
            """
            'use strict';

            const zero = Buffer.alloc(4);
            console.log('занулено:', zero.every((byte) => byte === 0));

            const fromString = Buffer.from('Привет', 'utf8');
            console.log('байт в utf8:', fromString.length);
            console.log('побайтово:', [...fromString]);

            const hex = Buffer.from('48 65 6c 6c 6f'.replace(/ /g, ''), 'hex');
            console.log('из hex:', hex.toString('utf8'));

            const base64 = Buffer.from('Node.js', 'utf8').toString('base64');
            console.log('base64:', base64, 'обратно:', Buffer.from(base64, 'base64').toString('utf8'));
            """,
        ),
        text(
            "Вывод программы (второй байт счётчика заменён на многоточие для краткости):\n"
            "занулено: true\n"
            "байт в utf8: 12\n"
            "побайтово: [ 208, 159, 209, 128, 208, 184, 208, 178, 208, 181, 209, 130 ]\n"
            "из hex: Hello\n"
            "base64: Tm9kZS5qcw== обратно: Node.js"
        ),
        text(
            "Символ кириллицы занимает два байта, поэтому `'Привет'.length` равно шести, а буфер — двенадцати. `subarray` не копирует байты: запись через представление видна в оригинале."
        ),
        example(
            "javascript",
            """
            'use strict';

            const original = Buffer.from('привет мир', 'utf8');

            // Копия: изменение копии не трогает оригинал.
            const copy = Buffer.from(original);
            copy[0] = 0x50;
            console.log('оригинал после копии:', original.toString('utf8'));

            // Представление: те же байты, без копирования.
            const view = original.subarray(0, 12);
            view.fill(0x50, 0, 1);
            view.fill(0x72, 1, 2);
            console.log('оригинал после представления:', original.toString('utf8'));
            console.log('длина представления:', view.length, 'длина оригинала:', original.length);

            const bytes = new Uint8Array(original.buffer, original.byteOffset, original.byteLength);
            bytes[0] = 0x44;
            console.log('через Uint8Array:', original.toString('utf8'));
            """,
        ),
        text(
            "Вывод программы:\n"
            "оригинал после копии: привет мир\n"
            "оригинал после представления: Прривет мир\n"
            "длина представления: 12 длина оригинала: 20\n"
            "через Uint8Array: Дрривет мир"
        ),
        text(
            "Запись одного байта ломает многобайтовый символ. Если фрагмент данных из сокета хранится долго, его копируют, иначе исходная аллокация остаётся в памяти."
        ),
        heading("Пул рабочих потоков libuv"),
        text(
            "Файловые операции, криптография, `zlib` и преобразование DNS выполняются в пуле потоков libuv, по умолчанию из четырёх потоков (`UV_THREADPOOL_SIZE`). Пул обслуживает эти операции, а JavaScript-код всё равно исполняется в основном потоке."
        ),
        example(
            "javascript",
            """
            'use strict';

            const crypto = require('crypto');

            function hashMany(count) {
              const started = process.hrtime.bigint();
              for (let i = 0; i < count; i += 1) {
                crypto.pbkdf2Sync('пароль', `соль-${i}`, 100000, 32, 'sha256');
              }
              const micros = Number(process.hrtime.bigint() - started) / 1000;
              return micros.toFixed(0);
            }

            console.log('размер пула libuv:', process.env.UV_THREADPOOL_SIZE || 'по умолчанию');
            console.log('последовательно, мкс:', hashMany(2));
            console.log('версия openssl:', process.versions.openssl.split('.')[0]);
            """,
        ),
        text(
            "Пример вывода (числа зависят от машины):\n"
            "размер пула libuv: по умолчанию\n"
            "последовательно, мкс: 84000\n"
            "версия openssl: 3"
        ),
        callout(
            "warning",
            "Синхронный вызов блокирует цикл",
            "Функция с суффиксом `Sync` выполняется в основном потоке и останавливает событийный цикл "
            "на всё время работы. В сервере это означает, что никакие запросы не обслуживаются, "
            "таймеры не срабатывают, а клиенты видят рост задержек. Асинхронный вариант уходит "
            "в пул libuv и возвращает управление немедленно."
        ),
        heading("Рабочие потоки и параллелизм"),
        text(
            "Рабочие потоки (worker threads) дают параллелизм внутри процесса: у каждого свой изолятор V8, своя куча и свой цикл. Обмен идёт сообщениями через `postMessage`, буферы передаются пересылкой или через `SharedArrayBuffer` с `Atomics`."
        ),
        example(
            "javascript",
            """
            'use strict';

            // Запуск: node worker.js
            const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

            function sumSquares(limit) {
              let sum = 0;
              for (let i = 0; i < limit; i += 1) {
                sum += i * i;
              }
              return sum;
            }

            if (isMainThread) {
              const limit = 200000;
              const worker = new Worker(__filename, { workerData: { limit } });

              worker.on('message', (result) => {
                console.log('из потока:', result);
                console.log('в основном потоке:', sumSquares(limit));
              });
              worker.on('error', (error) => console.error('ошибка потока:', error.message));
              worker.on('exit', (code) => console.log('выход потока:', code));
            } else {
              parentPort.postMessage(sumSquares(workerData.limit));
            }
            """,
        ),
        text(
            "Вывод программы:\n"
            "из потока: 2666656666700000\n"
            "в основном потоке: 2666656666700000\n"
            "выход потока: 0"
        ),
        text(
            "Готовый пул строят на `Piscina` или вручную, по числу ядер из `os.availableParallelism()`."
        ),
        example(
            "javascript",
            """
            'use strict';

            const os = require('os');

            const cpuCount = typeof os.availableParallelism === 'function'
              ? os.availableParallelism()
              : os.cpus().length;

            // Пул: не больше потоков, чем физических ядер, иначе растёт борьба за процессор.
            const poolSize = Math.max(1, cpuCount - 1);

            const tasks = Array.from({ length: 6 }, (_, index) => ({ id: index, cpuCount }));
            const queue = [];
            let running = 0;

            function runNext() {
              while (running < poolSize && queue.length > 0) {
                const task = queue.shift();
                running += 1;
                // На месте рабочего потока здесь стоял бы worker.postMessage(task)
                Promise.resolve(task).then((result) => {
                  running -= 1;
                  console.log(`задача ${result.id} на ${result.cpuCount} ядрах`);
                  runNext();
                });
              }
            }

            queue.push(...tasks);
            runNext();
            """,
        ),
        text(
            "Пример вывода на восьмиядерной машине (порядок задач может отличаться):\n"
            "задача 0 на 8 ядрах\n"
            "задача 1 на 8 ядрах\n"
            "задача 2 на 8 ядрах\n"
            "задача 3 на 8 ядрах\n"
            "задача 4 на 8 ядрах\n"
            "задача 5 на 8 ядрах"
        ),
        heading("Процессы и межпроцессное взаимодействие"),
        text(
            "Дочерний процесс имеет собственную память и падает независимо от родителя.\n\n"
            "Варианты запуска:\n"
            "- `spawn` отдаёт вывод по мере поступления;\n"
            "- `exec` идёт через оболочку и буферизует вывод;\n"
            "- `execFile` запускает файл без оболочки;\n"
            "- `fork` запускает модуль Node.js и создаёт канал.\n"
        ),
        example(
            "javascript",
            """
            'use strict';

            const { execFile } = require('child_process');

            execFile(
              process.execPath,
              ['-e', 'console.log("версия: " + process.version + " pid: " + process.pid)'],
              { timeout: 5000 },
              (error, stdout, stderr) => {
                if (error) {
                  console.error('команда не выполнилась:', error.message);
                  return;
                }
                console.log('получено:', stdout.trim());
                console.log('ошибок в потоке stderr:', stderr.length);
              }
            );
            """,
        ),
        text(
            "Пример вывода (идентификатор процесса меняется при каждом запуске):\n"
            "получено: версия: v20.11.1 pid: 51284\n"
            "ошибок в потоке stderr: 0"
        ),
        text(
            "`fork` запускает тот же `process.execPath` и добавляет четвёртый дескриптор IPC."
        ),
        example(
            "javascript",
            """
            'use strict';

            // Запуск: node ipc.js
            const { fork } = require('child_process');

            const child = fork(__filename, [], { stdio: ['inherit', 'inherit', 'inherit', 'ipc'] });

            child.on('message', (message) => {
              if (message.type === 'result') {
                console.log('родитель получил:', message.payload);
                child.disconnect();
              }
            });

            child.on('disconnect', () => {
              console.log('канал закрыт');
            });

            if (process.send) {
              // Эта ветка выполняется в дочернем процессе.
              process.on('message', (message) => {
                if (message.type === 'compute') {
                  const { a, b } = message.payload;
                  process.send({ type: 'result', payload: a + b });
                }
              });
            } else {
              child.send({ type: 'compute', payload: { a: 10, b: 20 } });
            }
            """,
        ),
        text(
            "Вывод программы:\n"
            "родитель получил: 30\n"
            "канал закрыт"
        ),
        text(
            "Вызов `process.send` есть только в потомке. Для HTTP-сервера на всех ядрах берут модуль `cluster`."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Тяжёлая синхронная функция в обработчике запроса", "Блокируется основной поток, все запросы ждут", "Вынести расчёт в рабочий поток или пул libuv"],
                ["Рекурсивный `process.nextTick`", "Очередь не кончается, ввод-вывод и таймеры стоят", "Использовать `setImmediate` или `queueMicrotask`"],
                ["Игнорирование `write() === false`", "Буфер растёт, память кончается", "Ждать `drain` или использовать `pipeline`"],
                ["`Buffer.allocUnsafe` без полной перезаписи", "В буфер попадают остатки чужих данных", "Использовать `Buffer.alloc` либо сразу заполнять все байты"],
                ["Долгое хранение `subarray` маленького фрагмента", "В памяти остаётся вся исходная аллокация", "Копировать фрагмент через `Buffer.from(view)`"],
                ["`exec` с пользовательской строкой", "Внедрение команд через оболочку", "Использовать `execFile` или `spawn` с массивом аргументов"],
                ["Ожидание `SharedArrayBuffer` в браузере как в Node.js", "В браузере нужна изоляция COOP и COEP", "Проверять `crossOriginIsolated` до использования"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняются локально, файлы запускаются командой `node имя_файла.js`. "
            "Перед каждым запуском запишите ожидаемый вывод, а затем сравните его с фактическим: "
            "расхождение показывает, какой механизм вы поняли не до конца."
        ),
        numbered(
            "Напишите скрипт без единого сетевого вызова, который выводит строки в порядке: синхронный код, nextTick, микрозадача, setImmediate, таймер. Объясните, почему такой порядок гарантирован.",
            "Реализуйте `Transform`, который разбивает текстовый поток на строки и выдаёт объекты с номером строки и длиной, а затем соберите конвейер через `pipeline` с приёмником, который печатает только строки длиннее десяти символов.",
            "Сравните время десяти последовательных вызовов `crypto.pbkdf2` с обратным вызовом при `UV_THREADPOOL_SIZE=1` и при значении по умолчанию. Запускайте процесс дважды с разной переменной окружения.",
            "Создайте буфер на 1 мегабайт, получите из него `subarray` длиной 16 байт и вызовите `process.memoryUsage()` до и после обнуления ссылки на оригинал. Объясните значения `heapUsed` и `rss`.",
            "Постройте пул из рабочих потоков, который считает сумму квадратов для ста задач, и сравните общее время с последовательным выполнением. Число потоков возьмите из `os.availableParallelism()`.",
        ),
        callout(
            "success",
            "Подсказка к третьему заданию",
            "Пул libuv по умолчанию состоит из четырёх потоков. При десяти задачах в очереди "
            "четыре выполняются параллельно, остальные ждут. С `UV_THREADPOOL_SIZE=1` всё идёт "
            "строго последовательно, и общее время должно оказаться заметно больше, если хеширование "
            "действительно нагружает процессор."
        ),
        heading("Проверьте себя"),
        numbered(
            "Какие задачи отвечает V8, а какие libuv?",
            "Почему `process.nextTick` выполняется раньше микрозадач промисов?",
            "Что означает `false`, возвращённое методом `write`?",
            "Зачем нужен `Buffer.allocUnsafe`, если он может содержать чужие данные?",
            "Чем рабочий поток отличается от дочернего процесса?",
            "Почему `exec` считают небезопасным для пользовательских строк?",
        ),
        heading("Ответы", 3),
        numbered(
            "V8 разбирает и выполняет JavaScript, управляет кучей и сборкой мусора. libuv предоставляет событийный цикл, неблокирующий ввод-вывод и пул потоков для блокирующих системных операций.",
            "У Node.js есть отдельная очередь nextTick с более высоким приоритетом, чем очередь микрозадач промисов. Опустошение nextTick всегда предшествует обработке промисов после каждого колбэка.",
            "Внутренний буфер приёмника заполнен. Источнику следует приостановиться до события `drain`, иначе память будет расти.",
            "Инициализация миллиона байт нулями стоит времени. Для больших потоков данных, где буфер сразу заполняется целиком, обнуление избыточно, а память выделяется быстрее.",
            "Рабочий поток живёт внутри того же процесса, имеет свой изолятор V8 и обменивается сообщениями. Дочерний процесс — отдельная программа с собственной памятью, своим жизненным циклом и возможностью упасть независимо от родителя.",
            "`exec` передаёт команду системной оболочке, поэтому символы вроде `;`, `&&` и обратных кавычек выполнятся как команды. `execFile` и `spawn` с массивом аргументов не порождают оболочку.",
        ),
        heading("Итоги"),
        bullets(
            "Node.js складывается из V8, libuv и привязок: движок выполняет код, библиотека ведёт цикл и ввод-вывод, привязки соединяют их с системой.",
            "Событийный цикл проходит фазы таймеров, отложенных колбэков, ожидания, опроса, проверки и завершения.",
            "Очередь nextTick опустошается раньше очереди промисов и после каждого колбэка, поэтому рекурсивный nextTick блокирует цикл.",
            "Внутри колбэка ввода-вывода `setImmediate` срабатывает раньше `setTimeout(fn, 0)`; на верхнем уровне порядок зависит от точности таймера.",
            "Потоки опираются на порог `highWaterMark`: `write` возвращает `false`, источник ждёт `drain`, а `pipeline` управляет этим автоматически.",
            "`Buffer.alloc` обнуляет память, `allocUnsafe` быстрее, а `subarray` и конструкторы над `ArrayBuffer` разделяют байты без копирования.",
            "Рабочие потоки дают настоящий параллелизм через изолированные изоляторы V8 и обмен сообщениями; процессы изолируют память и отказоустойчивость.",
            "Пул libuv из четырёх потоков обслуживает файловые, криптографические и сжимающие операции; синхронные версии API блокируют основной поток.",
        ),
        heading("Что дальше"),
        text(
            "Дальше — производительность: профилирование, утечки памяти, бюджет кадра и JIT."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Node.js: руководство по событийному циклу, таймерам и nextTick — nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick",
            "Документация libuv: дизайн и фазы цикла — docs.libuv.org/en/v1.x/design.html",
            "Node.js: модуль stream с разделом о обратном давлении — nodejs.org/api/stream.html",
            "Node.js: worker_threads и обмен сообщениями — nodejs.org/api/worker_threads.html",
            "Node.js: child_process и IPC-канал — nodejs.org/api/child_process.html",
            "Node.js: работа с Buffer и внешней памятью — nodejs.org/api/buffer.html",
            "Документация V8: обзор движка и сборки мусора — v8.dev/blog",
        ),
    ],
}
