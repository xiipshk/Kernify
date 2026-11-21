"""Урок 2.8 курса Python: асинхронность."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


LESSON = {
    "language": "python",
    "program_order": 2,
    "topic_order": 8,
    "name": "2.8. Асинхронность",
    "slug": "python-2-8-асинхронность",
    "short_description": (
        "Event loop, async/await, задачи, синхронизация, таймауты, "
        "асинхронный HTTP через aiohttp и паттерны асинхронного программирования."
    ),
    "topic_name": "Асинхронность",
    "topic_description": (
        "Как писать неблокирующий код с async/await, управлять задачами, "
        "синхронизировать доступ к ресурсам, работать с таймаутами и "
        "делать асинхронные HTTP-запросы через aiohttp."
    ),
    "learning_objectives": [
        "Понимать, как работает event loop и чем корутины отличаются от обычных функций",
        "Писать async/await код и запускать его через asyncio.run",
        "Создавать задачи через create_task и запускать несколько корутин параллельно",
        "Использовать gather, wait и as_completed для сбора результатов",
        "Применять Lock, Semaphore, Event и Queue для синхронизации задач",
        "Ограничивать время выполнения через wait_for и asyncio.timeout",
        "Отменять задачи и корректно обрабатывать CancelledError",
        "Выполнять блокирующий код в потоках через to_thread и run_in_executor",
        "Делать асинхронные HTTP-запросы через aiohttp.ClientSession",
        "Писать асинхронные контекстные менеджеры и итераторы",
    ],
    "estimated_minutes": 45,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "python",
        "asyncio",
        "асинхронность",
        "async",
        "await",
        "aiohttp",
        "синхронизация",
    ],
    "starter_code": code(
        """
        import asyncio

        async def fetch_data(url):
            # Имитация сетевого запроса
            await asyncio.sleep(0.1)
            return f"Данные с {url}"

        async def main():
            urls = ["api.example.com/1", "api.example.com/2", "api.example.com/3"]
            tasks = [fetch_data(url) for url in urls]
            results = await asyncio.gather(*tasks)
            for result in results:
                print(result)

        asyncio.run(main())
        """
    ),
    "hints": [
        "await работает только внутри async def. Снаружи используйте asyncio.run().",
        "create_task планирует выполнение, но не ждёт его. Нужен await или gather.",
        "asyncio.sleep отдаёт управление event loop'у, time.sleep — блокирует поток.",
        "Всегда перехватывайте CancelledError и делайте raise, иначе задача не отменится.",
        "ClientSession создавайте один раз на всё приложение, а не на каждый запрос.",
    ],
    "content": [
        {
            "type": "text",
            "content": (
                "В синхронном коде каждая операция ввода-вывода — запрос к сети, "
                "чтение файла, запрос к базе — останавливает выполнение программы "
                "до завершения. Пока программа ждёт ответ от сервера, процессор "
                "простаивает. При десятках и сотнях запросов это превращается в "
                "серьёзное замедление.\n\n"
                "Асинхронное программирование решает эту проблему иначе. Когда "
                "операция ввода-вывода начинается, программа не ждёт её завершения, "
                "а переключается на другую задачу. Когда данные готовы, event loop "
                "возвращает управление коду, который ждал результат. Это позволяет "
                "одному потоку обрабатывать тысячи соединений одновременно."
            ),
        },
        {"type": "heading", "level": 2, "content": "Чему вы научитесь"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "понимать, как работает event loop и чем корутины отличаются от обычных функций;",
                "писать async/await код и запускать его через asyncio.run;",
                "создавать задачи через create_task и запускать несколько корутин параллельно;",
                "использовать gather, wait и as_completed для сбора результатов;",
                "применять Lock, Semaphore, Event и Queue для синхронизации задач;",
                "ограничивать время выполнения через wait_for и asyncio.timeout;",
                "отменять задачи и корректно обрабатывать CancelledError;",
                "выполнять блокирующий код в потоках через to_thread и run_in_executor;",
                "делать асинхронные HTTP-запросы через aiohttp.ClientSession;",
                "писать асинхронные контекстные менеджеры и итераторы;",
            ],
        },
        {"type": "heading", "level": 2, "content": "Зачем нужна асинхронность"},
        {
            "type": "text",
            "content": (
                "Традиционный синхронный код выполняется последовательно: строка за "
                "строкой. Когда встречается операция ввода-вывода — например, "
                "HTTP-запрос через requests.get — поток блокируется и ждёт ответа. "
                "В это время он не может делать ничего полезного.\n\n"
                "Асинхронный подход разделяет понятие «запуск операции» и «ожидание "
                "результата». Программа запускает операцию ввода-вывода и сразу "
                "переходит к следующему коду. Когда результат готов, event loop "
                "возвращает управление в точку ожидания (await). Это не "
                "многопоточность: всё выполняется в одном потоке, но задачи "
                "кооперативно уступают управление друг другу в точках await."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import time
                import requests

                # Синхронно: последовательно, ждёт каждый запрос
                def sync_fetch(urls):
                    results = []
                    for url in urls:
                        resp = requests.get(url)  # БЛОКИРУЕТ поток!
                        results.append(resp.text)
                    return results
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "В этом примере каждый requests.get блокирует поток до получения "
                "ответа. Если три URL отвечают по 0.5 секунды, общее время — 1.5 "
                "секунды. Процессор простаивает 99% времени."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import aiohttp
                import asyncio

                async def fetch_one(session, url):
                    async with session.get(url) as resp:
                        return await resp.text()

                async def async_fetch(urls):
                    async with aiohttp.ClientSession() as session:
                        tasks = [fetch_one(session, url) for url in urls]
                        return await asyncio.gather(*tasks)
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Здесь все три запроса запускаются почти одновременно. "
                "asyncio.gather ждёт завершения всех задач. Если каждый URL "
                "отвечает за 0.5 секунды, общее время — около 0.5 секунды, "
                "потому что ожидание происходит параллельно. Event loop в момент "
                "await переключается на другую задачу вместо простоя."
            ),
        },
        {"type": "callout", "style": "info", "title": "Кооперативная многозадачность", "content": (
            "Asyncio использует кооперативную многозадачность: задача "
            "самостоятельно уступает управление в точке await. Если задача "
            "не содержит await (например, длинный цикл без await), она "
            "захватывает event loop полностью и блокирует другие задачи. "
            "Это главное отличие от прерывистой многозадачности ОС."
        )},
        {"type": "heading", "level": 2, "content": "Корутины и async/await"},
        {"type": "heading", "level": 3, "content": "Что такое корутина"},
        {
            "type": "text",
            "content": (
                "**Корутина** — функция, объявленная через async def. При вызове "
                "она не выполняется сразу, а возвращает объект-корутину. "
                "Это объект, который знает, как выполнить код по частям, "
                "приостанавливаясь в точках await и возобновляясь позже."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                async def hello():
                    print("Привет")
                    await asyncio.sleep(1)  # отдаёт управление event loop
                    print("Мир")

                # hello() НЕ выполняется, возвращает корутину
                coro = hello()
                print(type(coro))  # <class 'coroutine'>

                # Запуск через event loop
                asyncio.run(hello())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "<class 'coroutine'>\nПривет\n(пауза 1 секунда)\nМир",
        },
        {
            "type": "text",
            "content": (
                "Обратите внимание: при вызове hello() код внутри не выполняется. "
                "Печать «Привет» произойдёт только внутри asyncio.run, когда "
                "event loop начнёт выполнять корутину. await asyncio.sleep(1) — "
                "точка приостановки: корутина отдаёт управление event loop'у на "
                "1 секунду, а loop в это время может выполнять другие задачи."
            ),
        },
        {"type": "heading", "level": 3, "content": "Правило await"},
        {
            "type": "text",
            "content": (
                "await можно использовать только внутри async def. Попытка "
                "написать await на уровне модуля или внутри обычной функции "
                "вызовет SyntaxError."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                async def main():
                    await asyncio.sleep(0.1)
                    print("Готово")

                # ОШИБКА: await снаружи async функции
                # await asyncio.sleep(0.1)  # SyntaxError
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "await принимает awaitable-объект: корутину, Task, Future или "
                "объект с методом __await__. Выражение await выражение приостанавливает "
                "текущую корутину до готовности результата, а затем возвращает это "
                "значение."
            ),
        },
        {"type": "heading", "level": 3, "content": "asyncio.run — точка входа"},
        {
            "type": "text",
            "content": (
                "asyncio.run(coro) — стандартный способ запустить корутину. Эта "
                "функция создаёт новый event loop, запускает переданную корутину, "
                "ждёт её завершения, закрывает loop и возвращает результат. В "
                "Python 3.12+ loop создаётся автоматически при необходимости."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                async def compute():
                    await asyncio.sleep(0.1)
                    return 42

                result = asyncio.run(compute())
                print(result)  # 42
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "42",
        },
        {
            "type": "callout",
            "style": "warning",
            "title": "Нельзя вкладывать asyncio.run",
            "content": (
                "Вызов asyncio.run внутри уже работающего event loop вызовет "
                "RuntimeError. Внутри работающего loop используйте "
                "asyncio.create_task() или await напрямую."
            ),
        },
        {"type": "heading", "level": 2, "content": "Event Loop — цикл событий"},
        {
            "type": "text",
            "content": (
                "**Event loop** (цикл событий) — центральный компонент asyncio. "
                "Он хранит очередь задач, следит за таймерами, опрашивает "
                "сокеты на готовность ввода-вывода и распределяет управление "
                "между задачами. В любой момент времени loop выполняет одну "
                "задачу до следующего await."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                # Python 3.7+ — простой способ
                asyncio.run(main())

                # Низкий уровень: ручное управление loop
                loop = asyncio.get_event_loop()
                loop.run_until_complete(main())
                loop.close()
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "В современном коде (Python 3.7+) почти всегда достаточно "
                "asyncio.run(). Прямая работа с loop нужна редко: интеграция "
                "с чужими loop, тестирование или нестандартные сценарии."
            ),
        },
        {"type": "heading", "level": 3, "content": "Задачи (Task) — планирование выполнения"},
        {
            "type": "text",
            "content": (
                "**Задача (Task)** — обёртка над корутиной, которая планирует "
                "её выполнение в event loop. В отличие от простой корутины, "
                "Task начинает выполняться сразу после создания (в следующем "
                "цикле loop) и позволяет управлять выполнением: ждать "
                "завершения, отменять, проверять статус."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                async def background_work():
                    for i in range(3):
                        print(f"Фон: {i}")
                        await asyncio.sleep(0.1)

                async def main():
                    task = asyncio.create_task(background_work())
                    # background_work запускается параллельно!
                    print("Главная задача продолжается")
                    await asyncio.sleep(0.15)
                    print("Ждём завершения фона")
                    await task  # ждём завершения

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "Главная задача продолжается\nФон: 0\nФон: 1\nЖдём завершения фона\nФон: 2",
        },
        {
            "type": "text",
            "content": (
                "create_task ставит корутину в очередь event loop и сразу "
                "возвращает Task. Код после create_task продолжает выполняться, "
                "не дожидаясь завершения задачи. await task приостанавливает "
                "текущую корутину до завершения задачи. Если задача уже "
                "завершилась к моменту await, ожидание происходит мгновенно."
            ),
        },
        {"type": "heading", "level": 2, "content": "Запуск нескольких корутин параллельно"},
        {"type": "heading", "level": 3, "content": "asyncio.gather — собрать результаты"},
        {
            "type": "text",
            "content": (
                "asyncio.gather(*coros) — основной способ запустить несколько "
                "корутин параллельно и собрать их результаты в список. Порядок "
                "результатов соответствует порядку переданных корутин, "
                "независимо от порядка завершения."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                async def fetch(url, delay):
                    await asyncio.sleep(delay)
                    return f"{url}: готово за {delay}с"

                async def main():
                    results = await asyncio.gather(
                        fetch("api/1", 0.3),
                        fetch("api/2", 0.1),
                        fetch("api/3", 0.2),
                    )
                    print(results)

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "['api/1: готово за 0.3с', 'api/2: готово за 0.1с', 'api/3: готово за 0.2с']",
        },
        {
            "type": "text",
            "content": (
                "Обратите внимание: api/2 завершился первым (0.1с), но в "
                "результате он второй, потому что gather сохраняет порядок "
                "аргументов. Общее время выполнения — около 0.3 секунды "
                "(максимальная задержка), а не 0.6 (сумма)."
            ),
        },
        {
            "type": "callout",
            "style": "info",
            "title": "return_exceptions=True",
            "content": (
                "По умолчанию gather при первой ошибке отменяет все остальные "
                "задачи и поднимает исключение. С return_exceptions=True "
                "исключения возвращаются в списке результатов на месте упавших "
                "корутин, а остальные продолжают выполняться."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                async def risky(n):
                    if n == 2:
                        raise ValueError("ошибка в задаче 2")
                    await asyncio.sleep(0.1)
                    return n * 10

                async def main():
                    results = await asyncio.gather(
                        risky(1),
                        risky(2),
                        risky(3),
                        return_exceptions=True,
                    )
                    print(results)

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "[10, ValueError('ошибка в задаче 2'), 30]",
        },
        {"type": "heading", "level": 3, "content": "asyncio.wait — больше контроля"},
        {
            "type": "text",
            "content": (
                "asyncio.wait(tasks) возвращает два множества: done (завершённые "
                "задачи) и pending (ещё работающие). Параметр return_when "
                "управляет моментом возврата: FIRST_COMPLETED — как только "
                "хотя бы одна задача завершилась, FIRST_EXCEPTION — при первой "
                "ошибке, ALL_COMPLETED — когда все завершились (по умолчанию)."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                async def worker(n, delay):
                    await asyncio.sleep(delay)
                    return n

                async def main():
                    tasks = [asyncio.create_task(worker(i, d)) for i, d in
                             [(1, 0.3), (2, 0.1), (3, 0.2)]]

                    done, pending = await asyncio.wait(
                        tasks, return_when=asyncio.FIRST_COMPLETED
                    )
                    print(f"Завершилось: {len(done)}, работает: {len(pending)}")

                    # Отменяем оставшиеся
                    for task in pending:
                        task.cancel()
                    await asyncio.gather(*pending, return_exceptions=True)

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "Завершилось: 1, работает: 2",
        },
        {
            "type": "text",
            "content": (
                "wait полезен, когда нужно реагировать на первую завершённую "
                "задачу или отменять остальные при ошибке. После wait "
                "необходимо явно обработать pending: отменить или дождаться."
            ),
        },
        {"type": "heading", "level": 3, "content": "asyncio.as_completed — по мере готовности"},
        {
            "type": "text",
            "content": (
                "asyncio.as_completed(tasks) возвращает итератор, который "
                "даёт задачи в порядке их завершения. Это удобно для "
                "потоковой обработки результатов: можно начать работать с "
                "первым готовым результатом, не дожидаясь остальных."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                async def fetch(n, delay):
                    await asyncio.sleep(delay)
                    return f"Результат {n}"

                async def main():
                    tasks = [fetch(i, d) for i, d in [(1, 0.3), (2, 0.1), (3, 0.2)]]

                    for coro in asyncio.as_completed(tasks):
                        result = await coro
                        print(f"Получено: {result}")

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "Получено: Результат 2\nПолучено: Результат 3\nПолучено: Результат 1",
        },
        {"type": "heading", "level": 2, "content": "Синхронизация задач"},
        {
            "type": "text",
            "content": (
                "В асинхронном коде несколько задач могут одновременно читать "
                "и писать общие данные. Без синхронизации это приводит к "
                "состояниям гонки (race conditions). Asyncio предоставляет "
                "примитивы синхронизации, аналогичные threading, но "
                "адаптированные для event loop: Lock, Semaphore, Event, Queue."
            ),
        },
        {"type": "heading", "level": 3, "content": "Lock — взаимное исключение"},
        {
            "type": "text",
            "content": (
                "asyncio.Lock гарантирует, что только одна задача может "
                "находиться внутри критической секции. Асинхронный контекстный "
                "менеджер async with lock автоматически захватывает блокировку "
                "при входе и освобождает при выходе, даже если внутри "
                "возникло исключение."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                lock = asyncio.Lock()
                counter = {"value": 0}

                async def safe_increment():
                    async with lock:
                        # Критическая секция
                        current = counter["value"]
                        await asyncio.sleep(0)  # имитация работы, yield
                        counter["value"] = current + 1

                async def main():
                    tasks = [safe_increment() for _ in range(100)]
                    await asyncio.gather(*tasks)
                    print(counter["value"])

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "100",
        },
        {
            "type": "text",
            "content": (
                "Без lock результат был бы непредсказуемым из-за состояния "
                "гонки: две задачи могли прочитать одно значение, увеличить и "
                "записать обратно, теряя одно инкрементирование. await "
                "asyncio.sleep(0) внутри секции специально даёт возможность "
                "другой задаче захватить lock, демонстрируя, что защита "
                "работает даже при yield."
            ),
        },
        {"type": "heading", "level": 3, "content": "Semaphore — ограничение параллелизма"},
        {
            "type": "text",
            "content": (
                "Semaphore позволяет ограничить количество задач, "
                "одновременно выполняющих определённый участок кода. "
                "Semaphore(n) создаёт счётчик с начальным значением n. "
                "async with sem уменьшает счётчик (ждёт, если он 0), а при "
                "выходе увеличивает."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                # Не более 3 одновременных соединений
                semaphore = asyncio.Semaphore(3)

                async def limited_fetch(url, sem):
                    async with sem:
                        print(f"Начало: {url}")
                        await asyncio.sleep(0.2)
                        print(f"Конец: {url}")

                async def main():
                    urls = [f"url_{i}" for i in range(6)]
                    tasks = [limited_fetch(url, semaphore) for url in urls]
                    await asyncio.gather(*tasks)

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "Начало: url_0\nНачало: url_1\nНачало: url_2\nКонец: url_0\nКонец: url_1\nНачало: url_3\nКонец: url_2\nНачало: url_4\nКонец: url_3\nНачало: url_5\nКонец: url_4\nКонец: url_5",
        },
        {
            "type": "text",
            "content": (
                "Вывод показывает, что одновременно выполняются не более трёх "
                "задач. Как только одна завершается (Конец), следующая из "
                "ожидающих начинается (Начало). Это ключевой паттерн для "
                "ограничения нагрузки на внешние API, базы данных или "
                "файловую систему."
            ),
        },
        {"type": "heading", "level": 3, "content": "Event — сигнал между задачами"},
        {
            "type": "text",
            "content": (
                "Event — простой способ уведомить задачи о наступлении события. "
                "event.wait() приостанавливает задачу до вызова event.set() "
                "в другой задаче. После set все ожидающие задачи разблокируются "
                "одновременно. Event можно сбросить через event.clear()."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                event = asyncio.Event()

                async def waiter(name):
                    print(f"{name}: жду...")
                    await event.wait()
                    print(f"{name}: событие произошло!")

                async def setter():
                    await asyncio.sleep(1)
                    print("Сеттер: устанавливаю событие")
                    event.set()

                async def main():
                    await asyncio.gather(waiter("А"), waiter("Б"), setter())

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "А: жду...\nБ: жду...\nСеттер: устанавливаю событие\nА: событие произошло!\nБ: событие произошло!",
        },
        {"type": "heading", "level": 3, "content": "Queue — безопасная передача данных"},
        {
            "type": "text",
            "content": (
                "asyncio.Queue — потокобезопасная очередь для передачи данных "
                "между producer и consumer задачами. put(item) кладёт элемент "
                "(ждёт, если очередь полная), get() забирает элемент (ждёт, "
                "если пустая). task_done() сообщает, что обработка завершена, "
                "join() ждёт обработки всех элементов."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                queue = asyncio.Queue(maxsize=2)

                async def producer():
                    for i in range(5):
                        await queue.put(i)
                        print(f"Produced: {i}")
                        await asyncio.sleep(0.1)
                    await queue.put(None)  # сигнал завершения

                async def consumer(name):
                    while True:
                        item = await queue.get()
                        if item is None:
                            await queue.put(None)  # пробрасываем сигнал дальше
                            break
                        print(f"{name} consumed: {item}")
                        await asyncio.sleep(0.15)
                        queue.task_done()

                async def main():
                    await asyncio.gather(producer(), consumer("C1"), consumer("C2"))

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "Produced: 0\nProduced: 1\nC1 consumed: 0\nProduced: 2\nC2 consumed: 1\nProduced: 3\nC1 consumed: 2\nProduced: 4\nC2 consumed: 3\nC1 consumed: 4\nProduced: None\nC2 consumed: None",
        },
        {
            "type": "text",
            "content": (
                "maxsize=2 ограничивает накопление необработанных элементов. "
                "Если producer быстрее consumer, put будет ждать свободного "
                "места. Это естественная обратная связь (backpressure), "
                "предотвращающая переполнение памяти."
            ),
        },
        {"type": "heading", "level": 2, "content": "Таймауты и отмена задач"},
        {"type": "heading", "level": 3, "content": "asyncio.wait_for — таймаут на одну корутину"},
        {
            "type": "text",
            "content": (
                "asyncio.wait_for(coro, timeout) оборачивает корутину и "
                "поднимает asyncio.TimeoutError, если она не завершилась за "
                "указанное время (в секундах). Сама корутина при этом "
                "отменяется через cancel()."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                async def slow_operation():
                    await asyncio.sleep(10)
                    return "готово"

                async def main():
                    try:
                        result = await asyncio.wait_for(slow_operation(), timeout=1.0)
                        print(result)
                    except asyncio.TimeoutError:
                        print("Слишком долго!")

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "Слишком долго!",
        },
        {"type": "heading", "level": 3, "content": "asyncio.timeout — контекстный менеджер (Python 3.11+)"},
        {
            "type": "text",
            "content": (
                "Начиная с Python 3.11 доступен более удобный синтаксис через "
                "контекстный менеджер asyncio.timeout(seconds). Он работает "
                "аналогично wait_for, но позволяет обернуть любой блок кода "
                "с несколькими await."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                async def slow_operation():
                    await asyncio.sleep(10)
                    return "готово"

                async def main():
                    try:
                        async with asyncio.timeout(1.0):
                            await slow_operation()
                    except asyncio.TimeoutError:
                        print("Таймаут!")

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "Таймаут!",
        },
        {"type": "heading", "level": 3, "content": "Отмена задачи и CancelledError"},
        {
            "type": "text",
            "content": (
                "task.cancel() запрашивает отмену задачи. Внутри задачи это "
                "выглядит как подъём исключения CancelledError в точке "
                "следующего await. Задача должна перехватить это исключение, "
                "выполнить очистку (finally) и **обязательно сделать raise**, "
                "чтобы подтвердить отмену. Если просто заглотить исключение, "
                "задача продолжит выполняться."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                async def long_running():
                    try:
                        while True:
                            print("Работаю...")
                            await asyncio.sleep(1)
                    except asyncio.CancelledError:
                        print("Отменено! Делаю cleanup...")
                        raise  # обязательно пробрасываем дальше!

                async def main():
                    task = asyncio.create_task(long_running())
                    await asyncio.sleep(2.5)
                    print("Отправляю cancel...")
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        print("Задача отменена")

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "Работаю...\nРаботаю...\nРаботаю...\nОтправляю cancel...\nОтменено! Делаю cleanup...\nЗадача отменена",
        },
        {
            "type": "callout",
            "style": "warning",
            "title": "Никогда не заглушайте CancelledError",
            "content": (
                "Если перехватить CancelledError и не сделать raise, задача "
                "не будет считаться отменённой. Это приводит к утечкам задач "
                "и зависаниям. Всегда делайте raise после cleanup в finally "
                "или в блоке except CancelledError."
            ),
        },
        {"type": "heading", "level": 2, "content": "Запуск блокирующего кода в потоках и процессах"},
        {"type": "heading", "level": 3, "content": "asyncio.to_thread — для I/O-bound операций (Python 3.9+)"},
        {
            "type": "text",
            "content": (
                "Не всякий код можно сделать асинхронным. Библиотеки вроде "
                "requests, старые драйверы БД или CPU-intensive функции "
                "блокируют event loop. asyncio.to_thread(func, *args) запускает "
                "функцию в отдельном потоке из пула и возвращает awaitable, "
                "который можно await'ить. Это не делает функцию асинхронной, "
                "но не блокирует event loop."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio
                import time

                def blocking_io():
                    time.sleep(2)  # блокирующий вызов
                    return "готово"

                async def main():
                    print("Старт")
                    result = await asyncio.to_thread(blocking_io)
                    print(result)
                    print("Финиш")

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "Старт\n(пауза 2 секунды)\nготово\nФиниш",
        },
        {
            "type": "text",
            "content": (
                "Пока blocking_io спит в отдельном потоке, event loop свободен "
                "и может выполнять другие задачи. to_thread подходит для "
                "I/O-bound операций: работа с файлами, синхронные HTTP-клиенты, "
                "устаревшие драйверы БД."
            ),
        },
        {"type": "heading", "level": 3, "content": "run_in_executor — для CPU-bound задач"},
        {
            "type": "text",
            "content": (
                "Для задач, нагружающих процессор (вычисления, обработка "
                "изображений, парсинг больших JSON), потоки не помогают из-за "
                "GIL. run_in_executor с ProcessPoolExecutor запускает функцию "
                "в отдельном процессе, обходя GIL."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio
                import concurrent.futures

                def cpu_heavy(n):
                    return sum(i*i for i in range(n))

                async def main():
                    loop = asyncio.get_running_loop()
                    with concurrent.futures.ProcessPoolExecutor() as pool:
                        result = await loop.run_in_executor(pool, cpu_heavy, 10_000_000)
                    print(f"Сумма квадратов: {result}")

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "Сумма квадратов: 333333283333335000000",
        },
        {
            "type": "text",
            "content": (
                "ProcessPoolExecutor создаёт пул процессов. Передача данных "
                "между процессами происходит через pickle, поэтому аргументы и "
                "возвращаемое значение должны быть сериализуемы. Для частых "
                "вызовов накладные расходы на IPC могут перевешивать выгоду."
            ),
        },
        {"type": "heading", "level": 2, "content": "aiohttp — асинхронный HTTP клиент"},
        {"type": "heading", "level": 3, "content": "Базовое использование"},
        {
            "type": "text",
            "content": (
                "aiohttp — стандарт де-факто для асинхронных HTTP-запросов в "
                "Python. Ключевой объект — ClientSession. Она управляет пулом "
                "соединений, куками, заголовками и таймаутами. Сессию следует "
                "создавать один раз и переиспользовать для всех запросов."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import aiohttp
                import asyncio

                async def fetch(session, url):
                    async with session.get(url) as response:
                        return await response.text()

                async def main():
                    async with aiohttp.ClientSession() as session:
                        html = await fetch(session, "https://example.com")
                        print(html[:100])

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "session.get возвращает ClientResponse. Асинхронный контекстный "
                "менеджер async with гарантирует закрытие соединения. "
                "response.text() асинхронно читает тело ответа."
            ),
        },
        {"type": "heading", "level": 3, "content": "POST с JSON"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import aiohttp
                import asyncio

                async def post_data(session, url, data):
                    async with session.post(url, json=data) as resp:
                        return await resp.json()

                async def main():
                    async with aiohttp.ClientSession() as session:
                        result = await post_data(
                            session,
                            "https://httpbin.org/post",
                            {"name": "Анна", "age": 25}
                        )
                        print(result["json"])

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Параметр json= автоматически устанавливает Content-Type: "
                "application/json и сериализует словарь. Для form-data "
                "используйте data= вместо json=."
            ),
        },
        {"type": "heading", "level": 3, "content": "Таймауты и лимиты соединений"},
        {
            "type": "text",
            "content": (
                "По умолчанию aiohttp не имеет таймаута — запрос может "
                "висеть вечно. Всегда настраивайте ClientTimeout и "
                "TCPConnector для продакшн-кода."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import aiohttp

                timeout = aiohttp.ClientTimeout(total=30, connect=10)
                connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)

                async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                    async with session.get("https://api.example.com") as resp:
                        ...
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "total — общий таймаут на запрос (включая редиректы), connect — "
                "на установку TCP-соединения. limit — максимальное число "
                "одновременных соединений в пуле, limit_per_host — на один "
                "хост. Эти лимиты защищают от истощения файловых дескрипторов "
                "и перегрузки целевого сервера."
            ),
        },
        {"type": "heading", "level": 2, "content": "Асинхронные контекстные менеджеры и итераторы"},
        {"type": "heading", "level": 3, "content": "Async Context Manager"},
        {
            "type": "text",
            "content": (
                "Класс с методами __aenter__ и __aexit__ можно использовать в "
                "async with. Это позволяет инкапсулировать асинхронную "
                "инициализацию и очистку ресурсов: соединения, транзакции, "
                "файлы."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                class AsyncResource:
                    async def __aenter__(self):
                        await self.connect()
                        return self

                    async def __aexit__(self, exc_type, exc_val, exc_tb):
                        await self.close()

                    async def connect(self):
                        print("Подключение...")
                        await asyncio.sleep(0.1)

                    async def close(self):
                        print("Закрытие...")
                        await asyncio.sleep(0.1)

                    async def do_something(self):
                        print("Работа с ресурсом")

                async def main():
                    async with AsyncResource() as res:
                        await res.do_something()

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "Подключение...\nРабота с ресурсом\nЗакрытие...",
        },
        {"type": "heading", "level": 3, "content": "Async Iterator"},
        {
            "type": "text",
            "content": (
                "Класс с __aiter__ и __anext__ можно перебирать в async for. "
                "__anext__ должен возвращать awaitable, который выдаёт "
                "следующий элемент или поднимает StopAsyncIteration."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                class AsyncCounter:
                    def __init__(self, limit):
                        self.limit = limit
                        self.current = 0

                    def __aiter__(self):
                        return self

                    async def __anext__(self):
                        if self.current >= self.limit:
                            raise StopAsyncIteration
                        val = self.current
                        self.current += 1
                        await asyncio.sleep(0.1)
                        return val

                async def main():
                    async for i in AsyncCounter(3):
                        print(i)

                asyncio.run(main())
                """
            ),
        },
        {
            "type": "code",
            "language": "text",
            "content": "0\n(пауза 0.1с)\n1\n(пауза 0.1с)\n2",
        },
        {"type": "heading", "level": 2, "content": "Паттерны и лучшие практики"},
        {"type": "heading", "level": 3, "content": "Структура асинхронного приложения"},
        {
            "type": "text",
            "content": (
                "Типичное asyncio-приложение: инициализация ресурсов, запуск "
                "фоновых задач, основной цикл (веб-сервер, бот), graceful "
                "shutdown при сигнале завершения."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio
                import signal

                async def periodic_cleanup(cache):
                    while True:
                        await asyncio.sleep(60)
                        cache.cleanup()

                async def main():
                    async with Database() as db, Cache() as cache:
                        background = asyncio.create_task(periodic_cleanup(cache))
                        try:
                            await run_server(db, cache)
                        finally:
                            background.cancel()
                            await background

                asyncio.run(main())
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "Graceful shutdown по сигналу"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio
                import signal

                shutdown_event = asyncio.Event()

                def signal_handler():
                    shutdown_event.set()

                async def main():
                    loop = asyncio.get_running_loop()
                    for sig in (signal.SIGTERM, signal.SIGINT):
                        loop.add_signal_handler(sig, signal_handler)

                    await shutdown_event.wait()
                    print("Завершение работы...")

                asyncio.run(main())
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "Отладка асинхронного кода"},
        {
            "type": "text",
            "content": (
                "asyncio имеет встроенный debug-режим. Он логирует медленные "
                "коллбеки (по умолчанию > 0.1с), незакрытые корутины, "
                "исключения в задачах. Включается через asyncio.run(..., "
                "debug=True) или loop.set_debug(True)."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio

                async def slow_callback():
                    await asyncio.sleep(0.2)  # > 0.1s — попадёт в лог

                async def main():
                    await slow_callback()

                # Включение debug режима
                asyncio.run(main(), debug=True)
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Также полезно установить loop.slow_callback_duration = 0.05 "
                "для более чувствительного порога. В продакшне debug-режим "
                "может замедлить работу, используйте его выборочно."
            ),
        },
        {"type": "heading", "level": 2, "content": "Типичные ошибки"},
        {
            "type": "table",
            "headers": ["Ошибка", "Что происходит", "Как правильно"],
            "rows": [
                [
                    "Вызов корутины без await",
                    "Корутина создается, но не выполняется. Программа молчит.",
                    "Всегда await'ьте или передавайте в gather/create_task.",
                ],
                [
                    "Блокирующие вызовы (time.sleep, requests) в async коде",
                    "Весь event loop блокируется, параллелизм теряется.",
                    "Используйте asyncio.sleep, aiohttp, to_thread.",
                ],
                [
                    "Создание задач без сохранения ссылок",
                    "Задача может быть удалена сборщиком мусора до выполнения.",
                    "task = create_task(...) и сохраняйте ссылку.",
                ],
                [
                    "Отмена задачи без обработки CancelledError",
                    "Задача не завершается, ресурсы не освобождаются.",
                    "try/except CancelledError, cleanup, raise дальше.",
                ],
                [
                    "asyncio.run() внутри работающего loop",
                    "RuntimeError: cannot run loop while another is running.",
                    "Используйте create_task или ensure_future.",
                ],
                [
                    "ClientSession на каждый запрос",
                    "Потеря пула соединений, лишние накладные расходы.",
                    "Один ClientSession на всё приложение.",
                ],
                [
                    "Нет таймаутов на внешние запросы",
                    "Запрос может висеть вечно, блокируя задачу.",
                    "Всегда ClientTimeout и asyncio.timeout/wait_for.",
                ],
            ],
        },
        {"type": "heading", "level": 2, "content": "Практика"},
        {
            "type": "text",
            "content": (
                "Выполните задания по порядку. Каждое закрепляет конкретный "
                "навык. Запускайте код и проверяйте поведение."
            ),
        },
        {
            "type": "list",
            "ordered": True,
            "items": [
                "Напишите асинхронную функцию fetch_all(urls), которая параллельно скачивает список URL через aiohttp и возвращает словарь {url: длина_ответа}. Ограничьте параллелизм Semaphore(5).",
                "Реализуйте класс RateLimiter, позволяющий не более N запросов в секунду (токен-бакет). Используйте asyncio.Queue для хранения токенов и фоновую задачу для их пополнения.",
                "Напишите функцию download_with_retry(url, max_attempts=3), которая повторяет запрос при ошибках сети с экспоненциальной задержкой (0.5с, 1с, 2с). Используйте asyncio.wait_for с таймаутом 10с на попытку.",
                "Создайте producer-consumer паттерн: одна задача кладёт URL в Queue, три worker-задачи забирают и скачивают. Используйте None как сигнал завершения. Выведите статистику: сколько скачано, сколько ошибок.",
                "Реализуйте graceful shutdown для программы из задания 4: по SIGINT корректно остановить producer, дождаться обработки очереди, закрыть aiohttp сессию.",
            ],
        },
        {
            "type": "callout",
            "style": "success",
            "title": "Подсказка к заданию 1",
            "content": (
                "Создайте sem = asyncio.Semaphore(5). Внутри функции для одного "
                "URL используйте async with sem: перед запросом. Это "
                "автоматически ограничит одновременные соединения."
            ),
        },
        {"type": "heading", "level": 2, "content": "Проверьте себя"},
        {
            "type": "list",
            "ordered": True,
            "items": [
                "Чем корутина отличается от обычной функции?",
                "Зачем нужен asyncio.run() и можно ли вызывать его несколько раз в программе?",
                "В чём разница между gather, wait и as_completed?",
                "Почему await time.sleep() блокирует event loop, а await asyncio.sleep() — нет?",
                "Как корректно обработать CancelledError при отмене задачи?",
            ],
        },
        {"type": "heading", "level": 3, "content": "Ответы"},
        {
            "type": "list",
            "ordered": True,
            "items": [
                "Корутина (async def) возвращает объект-корутину, которая выполняется только при await. Обычная функция выполняется сразу и синхронно.",
                "asyncio.run() создаёт новый event loop, запускает корутину и закрывает loop. Нельзя вложить один run в другой — используйте create_task для планирования внутри работающего loop.",
                "gather ждёт все и возвращает список результатов в порядке аргументов. wait возвращает множества done/pending и даёт контроль над моментом возврата. as_completed — итератор, дающий задачи по мере завершения.",
                "time.sleep() блокирует весь поток (и event loop). asyncio.sleep() отдаёт управление loop'у, позволяя другим задачам работать.",
                "Обязательно перехватывайте CancelledError, делайте cleanup в finally или except, и делайте raise, иначе задача не отменится.",
            ],
        },
        {"type": "heading", "level": 2, "content": "Итоги"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "async/await — синтаксис для неблокирующего кода, event loop управляет выполнением.",
                "Корутины запускаются через asyncio.run() или create_task().",
                "gather / wait / as_completed — инструменты параллелизма.",
                "Lock, Semaphore, Event, Queue — примитивы синхронизации для задач.",
                "wait_for / asyncio.timeout — защита от зависаний.",
                "to_thread / run_in_executor — мост к блокирующему и CPU-bound коду.",
                "aiohttp.ClientSession — переиспользуйте для всех запросов.",
                "async with / async for — асинхронные протоколы менеджеров и итераторов.",
            ],
        },
        {"type": "heading", "level": 2, "content": "Что дальше"},
        {
            "type": "text",
            "content": (
                "Асинхронность — основа современных высоконагруженных сервисов. "
                "Следующий урок про работу с данными: базы данных, ORM, "
                "миграции и кэширование. Там эти навыки пригодятся для "
                "асинхронных драйверов БД (asyncpg, asyncpg, motor) и "
                "асинхронного кэширования."
            ),
        },
        {"type": "heading", "level": 2, "content": "Если хотите углубиться"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "Официальная документация asyncio: docs.python.org/3/library/asyncio.html",
                "Real Python: Async IO in Python — подробный туториал.",
                "aiohttp документация: docs.aiohttp.org — клиент и сервер.",
                "PEP 492: корутины и async/await — историческое обоснование.",
                "AsyncIO Best Practices: github.com/timofurrer/awesome-asyncio",
            ],
        },
    ],
}