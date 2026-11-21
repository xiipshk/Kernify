"""Урок 2.11 курса Python: производительность и профилирование."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


LESSON = {
    "language": "python",
    "program_order": 2,
    "topic_order": 11,
    "name": "2.11. Производительность и профилирование",
    "slug": "python-2-11-производительность-и-профилирование",
    "short_description": (
        "Измерение времени (timeit, perf_counter), CPU профилирование (cProfile, "
        "py-spy, snakeviz), память (memory_profiler, tracemalloc), GIL, "
        "оптимизации и продакшн-профилирование."
    ),
    "topic_name": "Производительность и профилирование",
    "topic_description": (
        "Как находить узкие места, измерять производительность, профилировать "
        "CPU и память, обходить GIL и оптимизировать код для продакшена."
    ),
    "learning_objectives": [
        "Измерять время выполнения через timeit и perf_counter",
        "Профилировать CPU: cProfile, snakeviz, py-spy, scalene",
        "Профилировать память: memory_profiler, tracemalloc, objgraph",
        "Понимать GIL и обходить его: multiprocessing, ProcessPoolExecutor, asyncio",
        "Применять оптимизации: алгоритмы, структуры данных, кэширование, генераторы",
        "Настраивать продакшн-профилирование: py-spy, scalene, continuous profiling",
    ],
    "estimated_minutes": 50,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "python",
        "производительность",
        "профилирование",
        "cProfile",
        "py-spy",
        "memory_profiler",
        "GIL",
        "оптимизация",
    ],
    "starter_code": code(
        """
        import timeit

        def sum_range(n):
            return sum(range(n))

        time = timeit.timeit(lambda: sum_range(1000), number=10000)
        print(f"Время: {time:.4f} сек")
        """
    ),
    "hints": [
        "Всегда профилируйте перед оптимизацией — без данных вы гадаете.",
        "cProfile показывает cumulative time — ищите функции с наибольшим cumulative time.",
        "py-spy работает без изменения кода и с минимальными накладными расходами.",
        "tracemalloc встроен в Python 3.4+ — не требует установки пакетов.",
        "lru_cache — простое и мощное кэширование для чистых функций.",
    ],
    "content": [
        {
            "type": "text",
            "content": (
                "Оптимизация без измерений — это гадание. Прежде чем переписывать код, "
                "нужно точно знать, где программа тратит время и память. Python даёт "
                "мощные инструменты: от встроенных timeit и cProfile до внешних "
                "py-spy, memory_profiler, scalene. В этом уроке разберём, как "
                "измерять, анализировать и устранять узкие места — от микробенчмарков "
                "до продакшн-профилирования.\n\n"
                "Главный принцип: сначала измерьте, потом оптимизируйте. Интуиция "
                "почти всегда обманывает — программист уверен, что узкое место в "
                "сложном алгоритме, а профилировщик показывает, что 80% времени "
                "уходит на сериализацию JSON или лишний запрос к базе. Правило "
                "Дональда Кнута остаётся верным: преждевременная оптимизация — "
                "корень всех зол. Но и откладывать измерения нельзя, когда "
                "пользователи уже жалуются на скорость.\n\n"
                "Профилирование отвечает на три вопроса: сколько времени занимает "
                "программа, в каких функциях это время уходит, и какие объекты "
                "съедают память. Ответив на них, вы получите список гипотез, "
                "которые можно проверить конкретными изменениями и снова замерить. "
                "Этот цикл — измерил, изменил, замерил — и есть инженерная "
                "оптимизация в отличие от угадывания."
            ),
        },
        {"type": "heading", "level": 2, "content": "Чему вы научитесь"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "измерять время выполнения через timeit, perf_counter и декораторы;",
                "профилировать CPU: cProfile, snakeviz, py-spy, scalene;",
                "профилировать память: memory_profiler, tracemalloc, objgraph;",
                "понимать GIL и обходить его: multiprocessing, ProcessPoolExecutor, asyncio;",
                "применять оптимизации: алгоритмы, структуры данных, кэширование, генераторы;",
                "настраивать продакшн-профилирование: py-spy, scalene, continuous profiling.",
            ],
        },
        {"type": "heading", "level": 2, "content": "Измерение времени выполнения"},
        {
            "type": "text",
            "content": (
                "Базовое измерение — timeit. Он запускает код много раз, отсекает "
                "накладные расходы и даёт статистически значимое время. Для разовых "
                "замеров удобен perf_counter — наносекундная точность, не зависит от "
                "системных часов."
            ),
        },
        {"type": "heading", "level": 3, "content": "timeit — точные замеры"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import timeit

                def sum_range(n):
                    return sum(range(n))

                # Замер
                time = timeit.timeit(lambda: sum_range(1000), number=10000)
                print(f"Время: {time:.4f} сек")

                # Из командной строки
                # python -m timeit -n 10000 "sum(range(1000))"
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "number — количество запусков. timeit автоматически подбирает "
                "количество итераций, если не указано. Lambda нужна, чтобы передать "
                "функцию с аргументами. Для сравнения вариантов кода запускайте "
                "timeit с одинаковым number."
            ),
        },
        {"type": "heading", "level": 3, "content": "perf_counter — высокоточный таймер"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import time

                start = time.perf_counter()
                result = heavy_computation()
                elapsed = time.perf_counter() - start
                print(f"Выполнено за {elapsed:.6f} сек")
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "perf_counter() — монотонные часы с наносекундной точностью, "
                "независимые от системных часов. time.time() может идти назад при "
                "синхронизации NTP, perf_counter — никогда. Для измерения интервалов "
                "всегда используйте perf_counter()."
            ),
        },
        {"type": "heading", "level": 3, "content": "Декоратор для тайминга"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import functools
                import time

                def timer(func):
                    @functools.wraps(func)
                    def wrapper(*args, **kwargs):
                        start = time.perf_counter()
                        result = func(*args, **kwargs)
                        elapsed = time.perf_counter() - start
                        print(f"{func.__name__}: {elapsed:.4f} сек")
                        return result
                    return wrapper

                @timer
                def slow_function():
                    time.sleep(1)
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "functools.wraps сохраняет __name__, __doc__, __annotations__ "
                "оригинальной функции. Декоратор удобен для быстрых замеров в "
                "разработке, но в продакшене лучше использовать specialised tools."
            ),
        },
        {"type": "heading", "level": 2, "content": "CPU профилирование — cProfile"},
        {"type": "heading", "level": 3, "content": "Базовое использование"},
        {
            "type": "text",
            "content": (
                "cProfile — встроенный детерминированный профайлер. Он считает "
                "вызовы, время в каждой функции (tottime — своё время, cumulative — "
                "с подвызовами). Встроен, не требует установки."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import cProfile
                import pstats

                profiler = cProfile.Profile()
                profiler.enable()

                # Код для профилирования
                result = compute_heavy()

                profiler.disable()

                # Статистика
                stats = pstats.Stats(profiler).sort_stats('cumulative')
                stats.print_stats(20)  # топ-20 функций
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "sort_stats: 'cumulative' — суммарное время с подвызовами (самое "
                "полезное), 'tottime' — только время в самой функции, 'calls' — "
                "количество вызовов. print_stats(20) показывает топ-20."
            ),
        },
        {"type": "heading", "level": 3, "content": "Сохранение и визуализация"},
        {
            "type": "code",
            "language": "bash",
            "content": code(
                """
                # Сохранить в файл
                python -m cProfile -o profile.stats script.py

                # Анализ в консоли
                python -m pstats profile.stats
                # В pstats: sort cumulative, stats 20

                # Визуализация (snakeviz)
                pip install snakeviz
                snakeviz profile.stats
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "snakeviz — интерактивный веб-интерфейс (icicle chart, call graph). "
                "Запускает локальный сервер, открывает в браузере. Полезно для "
                "понимания структуры вызовов."
            ),
        },
        {"type": "heading", "level": 3, "content": "py-spy — sampling профайлер (без изменения кода)"},
        {
            "type": "code",
            "language": "bash",
            "content": code(
                """
                pip install py-spy

                # Запуск на работающем процессе
                sudo py-spy top --pid 12345

                # Запись flamegraph
                py-spy record -o profile.svg -- python script.py

                # Flamegraph в браузере
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "py-spy — sampling профайлер на Rust. Работает без изменения кода, "
                "подключается к запущенному процессу (требует sudo/root). "
                "Flamegraph (SVG) показывает стек вызовов: ширина = время. "
                "Накладные расходы ~1-2%, можно использовать в продакшене."
            ),
        },
        {"type": "heading", "level": 2, "content": "Профилирование памяти"},
        {"type": "heading", "level": 3, "content": "memory_profiler — по строкам"},
        {
            "type": "code",
            "language": "bash",
            "content": "pip install memory_profiler"
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from memory_profiler import profile

                @profile
                def memory_heavy():
                    a = [1] * (10**6)
                    b = [2] * (2 * 10**7)
                    del b
                    return a

                # Запуск: python -m memory_profiler script.py
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Декоратор @profile показывает память (MiB) по строкам: Increment, "
                "Occurrences. Работает через sampling, накладные расходы заметны. "
                "Для точного анализа лучше tracemalloc."
            ),
        },
        {"type": "heading", "level": 3, "content": "tracemalloc — встроенный (Python 3.4+)"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import tracemalloc

                tracemalloc.start()

                # ... ваш код ...

                snapshot = tracemalloc.take_snapshot()
                top_stats = snapshot.statistics('lineno')

                for stat in top_stats[:10]:
                    print(stat)

                # Сравнение снапшотов
                snapshot1 = tracemalloc.take_snapshot()
                # ... код ...
                snapshot2 = tracemalloc.take_snapshot()

                top_stats = snapshot2.compare_to(snapshot1, 'lineno')
                for stat in top_stats[:10]:
                    print(stat)
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "tracemalloc — встроен, не требует установки. statistics('lineno') — "
                "по строкам, 'traceback' — по стеку вызовов. compare_to показывает "
                "разницу между снапшотами: где выделена/освобождена память. "
                "Требует tracemalloc.start() перед кодом."
            ),
        },
        {"type": "heading", "level": 3, "content": "objgraph — поиск утечек"},
        {
            "type": "code",
            "language": "bash",
            "content": "pip install objgraph"
        },
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import objgraph

                # Сколько объектов каждого типа
                objgraph.by_type('MyClass')

                # Кто ссылается на объект
                objgraph.find_backref_chain(obj, objgraph.is_proper_module)

                # Граф ссылок (нужен graphviz)
                objgraph.show_most_common_types(limit=20)
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "objgraph находит, кто держит ссылки на объекты (backref chains), "
                "показывает самые частые типы. Полезно для поиска утечек: "
                "objgraph.by_type() показывает рост количества объектов. "
                "Требует graphviz для визуализации графов."
            ),
        },
        {"type": "heading", "level": 2, "content": "GIL (Global Interpreter Lock)"},
        {"type": "heading", "level": 3, "content": "Что такое GIL"},
        {
            "type": "text",
            "content": (
                "GIL (Global Interpreter Lock) — мьютекс, позволяющий только одному "
                "потоку выполнять Python байт-код одновременно. CPU-bound задачи в "
                "потоках не ускоряются (даже замедляются из-за переключения контекста). "
                "I/O-bound задачи нормально работают — GIL отпускается при I/O "
                "(network, disk, sleep)."
            ),
        },
        {"type": "heading", "level": 3, "content": "Обход GIL"},
        {"type": "heading", "level": 3, "content": "multiprocessing — отдельные процессы"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from multiprocessing import Pool
                import time

                def cpu_heavy(n):
                    return sum(i*i for i in range(n))

                if __name__ == "__main__":
                    with Pool(4) as pool:
                        results = pool.map(cpu_heavy, [10**6] * 4)
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "concurrent.futures — высокоуровневый API"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

                def cpu_heavy(n):
                    return sum(i*i for i in range(n))

                # CPU-bound — процессы
                with ProcessPoolExecutor(max_workers=4) as executor:
                    futures = [executor.submit(cpu_heavy, 10**6) for _ in range(4)]
                    results = [f.result() for f in futures]

                # I/O-bound — потоки
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(fetch_url, url) for url in urls]
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "C-расширения (Cython, Rust/PyO3)"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                # cython_example.pyx
                def fib(int n):
                    cdef int a = 0, b = 1
                    for _ in range(n):
                        a, b = b, a + b
                    return a
                """
            ),
        },
        {
            "type": "code",
            "language": "bash",
            "content": code(
                """
                pip install cython
                # setup.py с Extension, затем pip install -e .
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Cython компилирует Python-подобный код в C. Типизация (cdef int) "
                "убирает проверки типов. Для числовых алгоритмов даёт 10-100x ускорение. "
                "Rust через PyO3/maturin — современная альтернатива с безопасностью памяти.\n\n"
                "Когда стоит выносить код в C-расширение: когда профилировщик показал, "
                "что время уходит на вычисления в чистом Python, и алгоритмические "
                "оптимизации уже исчерпаны. Перед этим проверьте три вещи. Первое — "
                "нельзя ли выразить вычисление через NumPy: векторизованные операции "
                "часто дают нужное ускорение без компиляции. Второе — не поможет ли "
                "кэширование: если функция вызывается с одними и теми же аргументами, "
                "lru_cache может дать больше, чем переписывание на C. Третье — не "
                "лучше ли распараллелить: если задача бьётся на независимые части, "
                "ProcessPoolExecutor даст ускорение без единой строки на C.\n\n"
                "Цена C-расширений высока: сборка под каждую платформу, отдельный "
                "цикл релизов, отладка сегфолтов, привязка к версии Python ABI. "
                "Поэтому правило простое: расширение нужно, только если другие "
                "способы измерены и не дали нужного результата, а выигрыш оправдывает "
                "рост сложности поддержки."
            ),
        },
        {"type": "heading", "level": 3, "content": "asyncio — для I/O без потоков"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                import asyncio
                import aiohttp

                async def fetch_all(urls):
                    async with aiohttp.ClientSession() as session:
                        tasks = [fetch(session, url) for url in urls]
                        return await asyncio.gather(*tasks)
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "asyncio не обходит GIL для CPU, но для I/O-bound задач (HTTP, DB, "
                "файлы) позволяет тысячи одновременных соединений в одном потоке. "
                "Event loop переключает задачи на await. Для CPU-bound внутри asyncio "
                "используйте run_in_executor с ProcessPoolExecutor."
            ),
        },
        {"type": "heading", "level": 2, "content": "Типичные оптимизации"},
        {"type": "heading", "level": 3, "content": "Алгоритмическая сложность"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                # ПЛОХО: O(n²)
                def has_duplicates_slow(lst):
                    for i, x in enumerate(lst):
                        for y in lst[i+1:]:
                            if x == y:
                                return True
                    return False

                # ХОРОШО: O(n)
                def has_duplicates_fast(lst):
                    seen = set()
                    for x in lst:
                        if x in seen:
                            return True
                        seen.add(x)
                    return False
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "Правильные структуры данных"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                # Поиск в списке — O(n)
                if item in my_list: ...

                # Поиск в множестве/словаре — O(1)
                if item in my_set: ...
                if key in my_dict: ...

                # collections.deque для очереди — O(1) с обеих сторон
                from collections import deque
                queue = deque()
                queue.append(item)
                queue.popleft()
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "Кэширование"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                from functools import lru_cache

                @lru_cache(maxsize=128)
                def expensive_computation(x):
                    # тяжёлые вычисления
                    return result

                # Ручной кэш
                cache = {}
                def cached_func(key):
                    if key not in cache:
                        cache[key] = compute(key)
                    return cache[key]
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "lru_cache мемоизирует результаты чистых функций. maxsize=None — "
                "неограниченный кэш. Для функций с аргументами используйте "
                "functools.cache (Python 3.9+, alias для lru_cache(maxsize=None)). "
                "Ручной кэш через dict нужен, когда ключи нехешируемы или нужна "
                "сложная логика инвалидации."
            ),
        },
        {"type": "heading", "level": 3, "content": "Генераторы вместо списков"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                # ПЛОХО: создаёт весь список в памяти
                def process_all(items):
                    return [expensive(x) for x in items]

                # ХОРОШО: ленивое вычисление
                def process_all(items):
                    return (expensive(x) for x in items)

                # Или yield
                def process_all(items):
                    for item in items:
                        yield expensive(item)
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Генераторные выражения и yield не создают список в памяти, "
                "вычисляют значения по требованию. Для больших данных экономия "
                "памяти колоссальна. sum(generator) работает, но list(generator) "
                "создаёт список — теряет смысл ленивости."
            ),
        },
        {"type": "heading", "level": 3, "content": "Встроенные функции быстрее циклов"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                # ПЛОХО
                result = []
                for x in items:
                    result.append(x * 2)

                # ХОРОШО
                result = [x * 2 for x in items]
                # Или map
                result = list(map(lambda x: x * 2, items))

                # sum, max, min, any, all — на C
                total = sum(items)
                maximum = max(items)
                """
            ),
        },
        {"type": "heading", "level": 3, "content": "Избегайте лишних атрибутов"},
        {
            "type": "code",
            "language": "python",
            "content": code(
                """
                # ПЛОХО: поиск атрибута в цикле
                for i in range(1000000):
                    obj.method()

                # ХОРОШО: кэшируйте ссылку
                method = obj.method
                for i in range(1000000):
                    method()
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Поиск атрибута (obj.method) — поиск в __dict__, дескрипторы, "
                "MRO. Кэширование ссылки (method = obj.method) делает поиск один раз. "
                "В горячих циклах даёт 10-20% ускорение."
            ),
        },
        {"type": "heading", "level": 2, "content": "Продакшн-профилирование"},
        {"type": "heading", "level": 3, "content": "py-spy на продакшене"},
        {
            "type": "code",
            "language": "bash",
            "content": code(
                """
                # Непрерывный профайлер
                py-spy record -o profile.svg --pid 12345 --duration 60

                # Top-функции в реальном времени
                py-spy top --pid 12345
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "py-spy работает без остановки процесса. --duration ограничивает "
                "время записи. flamegraph (SVG) открывается в браузере. Для "
                "постоянного мониторинга используйте continuous profiling."
            ),
        },
        {"type": "heading", "level": 3, "content": "Continuous profiling (Pyroscope, Datadog)"},
        {
            "type": "code",
            "language": "bash",
            "content": code(
                """
                # Pyroscope — open source
                docker run -d --name pyroscope \
                  -p 4040:4040 \
                  pyroscope/pyroscope
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Pyroscope — open source continuous profiling. Собирает профили "
                "непрерывно, показывает flamegraph по времени. Интегрируется с "
                "Grafana. Datadog, Elastic APM, New Relic — коммерческие аналоги "
                "с алертами и корреляцией логов/метрик/трейсов."
            ),
        },
        {"type": "heading", "level": 2, "content": "Инструменты для анализа производительности"},
        {
            "type": "table",
            "headers": ["Инструмент", "Назначение"],
            "rows": [
                ["timeit", "Микробенчмарки"],
                ["cProfile", "Детерминированное CPU профилирование"],
                ["py-spy", "Sampling профилирование (zero overhead)"],
                ["snakeviz", "Визуализация cProfile"],
                ["memory_profiler", "Построчное профилирование памяти"],
                ["tracemalloc", "Встроенное отслеживание аллокаций"],
                ["objgraph", "Анализ ссылок, поиск утечек"],
                ["scalene", "CPU + GPU + память вместе"],
                ["line_profiler", "Построчное CPU профилирование"],
            ],
        },
        {"type": "heading", "level": 3, "content": "Scalene — всё в одном"},
        {
            "type": "code",
            "language": "bash",
            "content": code(
                """
                pip install scalene
                python -m scalene script.py
                # Показывает CPU, GPU, память по строкам!
                """
            ),
        },
        {
            "type": "text",
            "content": (
                "Scalene — современный профайлер: CPU (sampling), GPU (CUDA), "
                "память (tracemalloc) одновременно. Показывает % времени/памяти "
                "по строкам, выделяет hotspots. Поддерживает HTML/JSON отчёты."
            ),
        },
        {"type": "heading", "level": 2, "content": "Типичные ошибки"},
        {
            "type": "table",
            "headers": ["Ошибка", "Правильно"],
            "rows": [
                ["Оптимизируют без профилирования", "Сначала cProfile / py-spy, потом оптимизируйте хотспоты"],
                ["Потоки для CPU-bound задач", "multiprocessing / ProcessPoolExecutor"],
                ["Преждевременная оптимизация", "\"Premature optimization is the root of all evil\" — Knuth"],
                ["Игнорируют аллокации памяти", "tracemalloc / memory_profiler для large data"],
                ["Тестируют на малых данных", "Бенчмарки на реалистичных объёмах"],
            ],
        },
        {"type": "heading", "level": 2, "content": "Практика"},
        {
            "type": "text",
            "content": (
                "Выполните задания по порядку. Используйте реалистичные объёмы данных.\n\n"
                "Как замерять честно: запускайте каждый замер несколько раз и берите "
                "медиану, а не единственное значение. Первый запуск почти всегда "
                "медленнее из-за загрузки модулей и холодного кэша процессора. "
                "Отключайте лишнее: закрывайте тяжёлые приложения, не запускайте "
                "бенчмарк под отладчиком. Для timeit используйте параметр number "
                "так, чтобы общее время замера было не меньше секунды — иначе "
                "погрешность таймера съест разницу.\n\n"
                "Сравнивая два варианта, меняйте только одну вещь за раз. Если "
                "переписали и алгоритм, и структуру данных, а результат улучшился, "
                "непонятно, что именно помогло — и следующий раз вы не сможете "
                "воспроизвести успех. Записывайте замеры до и после в таблицу: "
                "через полчаса память подведёт, а цифры останутся."
            ),
        },
        {
            "type": "list",
            "ordered": True,
            "items": [
                "Профилируйте: найдите узкое место в сортировке 1М чисел через cProfile и py-spy. Сравните результаты.",
                "Оптимизируйте: перепишите O(n²) алгоритм поиска дубликатов на O(n) через set. Замерьте скорость до/после через timeit.",
                "Memory leak: создайте утечку через циклические ссылки (a.b = b; b.a = a), найдите через objgraph.by_type() и tracemalloc.",
                "Multiprocessing: ускорьте CPU-bound задачу (факториал, рендеринг) через ProcessPoolExecutor. Замерьте speedup.",
                "Benchmark: сравните list vs deque vs array.array для очереди (append/pop/appendleft/popleft) на 100К операций.",
            ],
        },
        {
            "type": "callout",
            "style": "success",
            "title": "Подсказка к заданию 2",
            "content": (
                "Оригинал: двойной цикл for x in lst: for y in lst[i+1:]. "
                "Оптимизация: seen = set(); for x in lst: if x in seen: return True; seen.add(x). "
                "timeit покажет 100-1000x ускорение на 10К элементов."
            ),
        },
        {"type": "heading", "level": 2, "content": "Проверьте себя"},
        {
            "type": "list",
            "ordered": True,
            "items": [
                "В чём разница между tottime и cumulative time в cProfile?",
                "Почему py-spy не требует изменения кода и работает на продакшене?",
                "В чём разница между threading и multiprocessing для CPU-bound задач?",
                "Чем tracemalloc.compare_to помогает найти утечку памяти?",
                "Когда стоит использовать lru_cache, а когда ручной кэш через dict?",
            ],
        },
        {"type": "heading", "level": 3, "content": "Ответы"},
        {
            "type": "list",
            "ordered": True,
            "items": [
                "tottime — время только в самой функции (без подвызовов). cumulative — время в функции со всеми подвызовами. Для поиска хотспотов смотрите cumulative.",
                "py-spy читает память процесса через ptrace / process_vm_readv, не инжектирует код. Sampling (100Hz по умолчанию) — низкие накладные расходы, безопасен для продакшена.",
                "threading не помогает для CPU-bound из-за GIL — только один поток выполняет байт-код. multiprocessing создаёт отдельные процессы со своими GIL, даёт истинный параллелизм на многоядерных CPU.",
                "compare_to(snapshot1, 'lineno') показывает разницу аллокаций по строкам между двумя снапшотами. Положительные значения — рост памяти, отрицательные — освобождение. Позволяет локализовать утечку до строки кода.",
                "lru_cache для чистых функций с хешируемыми аргументами (авто-инвалидация по maxsize). Ручной dict для нехешируемых ключей, сложной инвалидации (TTL, events), общих кэшей между процессами.",
            ],
        },
        {"type": "heading", "level": 2, "content": "Итоги"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "timeit / perf_counter — микробенчмарки. cProfile / py-spy / scalene — CPU профилирование.",
                "memory_profiler / tracemalloc / objgraph — профилирование памяти и поиск утечек.",
                "GIL блокирует CPU-bound потоки. multiprocessing / ProcessPoolExecutor / asyncio — обход.",
                "Оптимизация: алгоритмы (O(n²)→O(n)), структуры (set/dict вместо list), кэш (lru_cache), генераторы, встроенные функции.",
                "Продакшн: py-spy (sampling), scalene (всё в одном), continuous profiling (Pyroscope).",
                "Всегда профилируйте перед оптимизацией. Оптимизируйте хотспоты, а не всё подряд.",
            ],
        },
        {"type": "heading", "level": 2, "content": "Что дальше"},
        {
            "type": "text",
            "content": (
                "Производительность — не разовая акция, а постоянный процесс. "
                "Следующий (последний урок второго уровня) — типизация и статический "
                "анализ: как mypy, pyright, pyright ловят баги до запуска, как "
                "описывать сложные типы через Generics, Protocol, TypedDict. "
                "Статический анализ дополняет профилирование: профилирование ловит "
                "проблемы производительности, статический анализ — логические ошибки."
            ),
        },
        {"type": "heading", "level": 2, "content": "Если хотите углубиться"},
        {
            "type": "list",
            "ordered": False,
            "items": [
                "Python Performance Tips: wiki.python.org/moin/PythonSpeed/PerformanceTips",
                "Real Python: Profiling — realpython.com/python-profiling/",
                "Scalene: github.com/plasma-umass/scalene — CPU+GPU+память.",
                "py-spy: github.com/benfred/py-spy — sampling профайлер для продакшена.",
                "High Performance Python: Micha Gorelick, Ian Ozsvald (O'Reilly).",
                "Effective Python: Item 66-68 — Brett Slatkin.",
            ],
        },
    ],
}