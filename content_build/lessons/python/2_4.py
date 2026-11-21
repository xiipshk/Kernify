"""Урок 2.4 курса Python: генераторы и итераторы."""

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
    "program_order": 2,
    "topic_order": 4,
    "name": "2.4. Генераторы и итераторы",
    "slug": "python-2-4-генераторы-и-итераторы",
    "short_description": (
        "Протокол итератора, yield, генераторы, yield from, send, throw, "
        "itertools и асинхронные генераторы."
    ),
    "topic_name": "Генераторы и итераторы",
    "topic_description": (
        "Как создавать ленивые последовательности, писать свои итераторы, "
        "использовать yield для отдачи значений по требованию и работать с "
        "itertools для составных итераторов."
    ),
    "learning_objectives": [
        "Объяснять разницу между итерируемым объектом и итератором",
        "Реализовывать __iter__ и __next__ для собственных классов",
        "Писать генераторы через yield и понимать их ленивое выполнение",
        "Использовать yield from для делегирования другому генератору",
        "Применять send, throw и close для управления генератором",
        "Собирать сложные итераторы через itertools",
    ],
    "estimated_minutes": 40,
    "xp_reward": 15,
    "difficulty": "intermediate",
    "tags": [
        "python",
        "генераторы",
        "итераторы",
        "yield",
        "itertools",
        "ленивые вычисления",
    ],
    "starter_code": code(
        """
        def countdown(n):
            while n > 0:
                yield n
                n -= 1

        for x in countdown(5):
            print(x)
        """
    ),
    "hints": [
        "Вызов генераторной функции не выполняет её код, а возвращает объект-генератор.",
        "yield приостанавливает функцию и отдаёт значение; следующий next() продолжает с того же места.",
        "itertools.chain, cycle, islice закрывают большинство задач по склеиванию и срезам итераторов.",
    ],
    "content": [
        text(
            "В первых уроках цикл `for` казался магией: он сам перебирал "
            "списки, строки и range. На самом деле `for` работает по "
            "**протоколу итератора**: он вызывает `iter(объект)`, получает "
            "**итератор** и затем повторно вызывает `next(итератор)`, пока "
            "тот не поднимет `StopIteration`.\n\n"
            "Генераторы — самый удобный способ создать итератор. Вместо "
            "класса с `__next__` пишут функцию с `yield`. Каждый `yield` "
            "отдаёт значение и приостанавливает функцию; следующий вызов "
            "продолжает с того же места. Это позволяет работать с "
            "бесконечными последовательностями, обрабатывать большие файлы "
            "по кускам и писать понятные конвейеры данных."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "различать итерируемый объект и итератор и объяснять, как работает for;",
            "реализовывать __iter__ и __next__ для своих классов-итераторов;",
            "писать генераторные функции с yield и понимать их состояние;",
            "использовать yield from для вложенных генераторов;",
            "управлять генератором через send, throw и close;",
            "собирать конвейеры из itertools: chain, cycle, islice, groupby.",
        ),
        heading("Итерируемый объект и итератор"),
        text(
            "**Итерируемый объект** (iterable) — объект, у которого есть "
            "метод `__iter__`, возвращающий **итератор**. Списки, строки, "
            "кортежи, множества, словари, range — все итерируемы.\n\n"
            "**Итератор** — объект, у которого есть метод `__next__`, "
            "возвращающий следующий элемент. Когда элементов больше нет, "
            "`__next__` поднимает `StopIteration`. Итератор также имеет "
            "`__iter__`, возвращающий сам себя, поэтому итератор тоже "
            "является итерируемым объектом."
        ),
        example(
            "python",
            """
            data = [1, 2, 3]

            iterator = iter(data)
            print(next(iterator))
            print(next(iterator))
            print(next(iterator))
            # next(iterator)  # StopIteration
            """,
        ),
        example("text", "1\n2\n3"),
        text(
            "Функция `iter(x)` вызывает `x.__iter__()`, а `next(it)` — "
            "`it.__next__()`. Цикл `for` делает то же самое неявно: получает "
            "итератор через `iter()`, затем в цикле вызывает `next()` и "
            "ловит `StopIteration` для выхода."
        ),
        heading("Свой итератор через класс"),
        text(
            "Чтобы сделать объект итератором, нужно определить `__iter__` "
            "(возвращает `self`) и `__next__` (возвращает следующий элемент "
            "или поднимает `StopIteration`)."
        ),
        example(
            "python",
            """
            class CountDown:
                def __init__(self, start):
                    self.current = start

                def __iter__(self):
                    return self

                def __next__(self):
                    if self.current <= 0:
                        raise StopIteration
                    val = self.current
                    self.current -= 1
                    return val


            for n in CountDown(3):
                print(n)
            """,
        ),
        example("text", "3\n2\n1"),
        text(
            "`__iter__` возвращает `self`, потому что объект сам является "
            "итератором. Если нужен новый итератор на каждом проходе, "
            "`__iter__` должен создавать и возвращать новый экземпляр "
            "внутреннего класса."
        ),
        heading("Генераторы — yield"),
        text(
            "**Генераторная функция** — функция, содержащая `yield`. Её "
            "вызов **не выполняет тело**, а возвращает **объект-генератор**. "
            "Генератор — это итератор, который выполняет функцию по кускам: "
            "до первого `yield`, затем до следующего и так далее."
        ),
        example(
            "python",
            """
            def countdown(start):
                print(f"Старт: {start}")
                while start > 0:
                    yield start
                    start -= 1
                print("Конец")


            gen = countdown(3)
            print("Создан генератор")
            print(next(gen))
            print(next(gen))
            print(next(gen))
            """,
        ),
        example("text", "Создан генератор\nСтарт: 3\n3\n2\n1\nКонец"),
        text(
            "Обратите внимание: при создании `gen = countdown(3)` ничего не "
            "печатается. Код начинает выполняться только при первом `next()`. "
            "После каждого `yield` функция «засыпает», сохраняя все локальные "
            "переменные и позицию инструкции. Следующий `next()` «будит» "
            "её и продолжает с того же места."
        ),
        heading("Генераторные выражения"),
        text(
            "Для простых случаев не нужна отдельная функция: **генераторное "
            "выражение** (generator expression) пишется как list comprehension, "
            "но в круглых скобках. Оно сразу возвращает генератор."
        ),
        example(
            "python",
            """
            squares = (x**2 for x in range(5))
            print(type(squares))
            print(next(squares))
            print(next(squares))
            print(list(squares))
            """,
        ),
        example("text", "<class 'generator'>\n0\n1\n[4, 9, 16]"),
        text(
            "Разница с list comprehension: квадратные скобки создают список "
            "сразу, круглые — генератор, который вычисляет элементы по "
            "требованию. Для однократного прохода генератор экономит память."
        ),
        heading("yield from — делегирование"),
        text(
            "`yield from` передаёт управление другому генератору или "
            "итерируемому объекту. Все значения отдаются напрямую, а "
            "возвращаемое значение подгенератора становится результатом "
            "`yield from`."
        ),
        example(
            "python",
            """
            def inner():
                yield 1
                yield 2
                return "готово"

            def outer():
                print("до")
                result = yield from inner()
                print(f"после: {result}")

            for x in outer():
                print(x)
            """,
        ),
        example("text", "до\n1\n2\nпосле: готово"),
        text(
            "`yield from` не только пробрасывает значения, но и пробрасывает "
            "`send`, `throw` и `close` в подгенератор. Это позволяет строить "
            "сложные конвейеры из простых генераторов."
        ),
        heading("send — передача значения внутрь"),
        text(
            "Метод `send(value)` возобновляет генератор и передаёт `value` "
            "как результат выражения `yield`. Первый вызов должен быть "
            "`next()` или `send(None)`, потому что генератор ещё не достиг "
            "первого `yield`."
        ),
        example(
            "python",
            """
            def accumulator():
                total = 0
                while True:
                    x = yield total
                    if x is not None:
                        total += x


            gen = accumulator()
            print(next(gen))
            print(gen.send(5))
            print(gen.send(10))
            print(gen.send(-3))
            """,
        ),
        example("text", "0\n5\n15\n12"),
        text(
            "Генератор накапливает сумму. `send(5)` передаёт `5` в `x`, "
            "генератор добавляет к `total` и отдаёт новое значение через "
            "следующий `yield`. Это основа для корутин и асинхронного кода."
        ),
        heading("throw и close — управление исключениями"),
        text(
            "`throw(exc)` поднимает исключение `exc` внутри генератора в "
            "точке `yield`. Генератор может его поймать и продолжить работу. "
            "`close()` поднимает `GeneratorExit` внутри генератора и "
            "завершает его."
        ),
        example(
            "python",
            """
            def resilient():
                try:
                    while True:
                        x = yield
                        print(f"Получено: {x}")
                except ValueError:
                    print("Пойман ValueError, продолжаем")
                    yield "восстановлено"


            gen = resilient()
            next(gen)
            gen.send(1)
            gen.throw(ValueError)
            gen.send(2)
            """,
        ),
        example("text", "Получено: 1\nПойман ValueError, продолжаем\nвосстановлено\nПолучено: 2"),
        text(
            "`close()` полезен для гарантированной очистки ресурсов: в блоке "
            "`finally` генератора можно закрыть файл или соединение."
        ),
        example(
            "python",
            """
            def reader():
                try:
                    while True:
                        yield "данные"
                finally:
                    print("Файл закрыт")


            gen = reader()
            next(gen)
            gen.close()
            """,
        ),
        example("text", "Файл закрыт"),
        heading("itertools — конвейеры итераторов"),
        text(
            "Модуль `itertools` предоставляет функции для создания, "
            "фильтрации и комбинирования итераторов. Они работают лениво и "
            "экономично: не создают промежуточных списков."
        ),
        heading("chain — склейка"),
        example(
            "python",
            """
            from itertools import chain

            for x in chain([1, 2], "ab", range(3)):
                print(x, end=" ")
            """,
        ),
        example("text", "1 2 a b 0 1 2 "),
        heading("cycle — бесконечное повторение"),
        example(
            "python",
            """
            from itertools import cycle, islice

            for x in islice(cycle("AB"), 6):
                print(x, end=" ")
            """,
        ),
        example("text", "A B A B A B "),
        heading("islice — срез итератора"),
        example(
            "python",
            """
            from itertools import islice, count

            print(list(islice(count(), 5, 15)))
            print(list(islice(count(), 5)))
            """,
        ),
        example("text", "[5, 6, 7, 8, 9, 10, 11, 12, 13, 14]\n[0, 1, 2, 3, 4]"),
        heading("groupby — группировка подряд идущих"),
        example(
            "python",
            """
            from itertools import groupby

            data = [("a", 1), ("a", 2), ("b", 3), ("b", 4), ("a", 5)]
            for key, group in groupby(data, key=lambda x: x[0]):
                print(key, list(group))
            """,
        ),
        example("text", "a [('a', 1), ('a', 2)]\nb [('b', 3), ('b', 4)]\na [('a', 5)]"),
        text(
            "`groupby` группирует только **подряд идущие** элементы с одинаковым "
            "ключом. Если данные не отсортированы по ключу, группы будут "
            "разбиты. Поэтому перед `groupby` обычно сортируют."
        ),
        heading("Бесконечные итераторы"),
        text(
            "`count(start, step)` — бесконечный счётчик, `repeat(value, n)` — "
            "повторяет значение `n` раз или бесконечно, `cycle(iterable)` — "
            "циклически повторяет последовательность. Их удобно комбинировать "
            "с `zip`, `map`, `islice`."
        ),
        example(
            "python",
            """
            from itertools import count, repeat, zip_longest

            names = ["Анна", "Борис"]
            for i, name in zip(count(1), names):
                print(i, name)

            for x in zip_longest([1, 2], ["a"], fillvalue=0):
                print(x)
            """,
        ),
        example("text", "1 Анна\n2 Борис\n(1, 'a')\n(2, 0)"),
        heading("Асинхронные генераторы"),
        text(
            "Python 3.6+ поддерживает **асинхронные генераторы**: функции с "
            "`async def` и `yield`. Они возвращают асинхронный генератор, "
            "который перебирается через `async for`. Значения производятся "
            "по требованию, и между `yield` можно выполнять асинхронные "
            "операции (`await`)."
        ),
        example(
            "python",
            """
            import asyncio

            async def ticker(interval, count):
                for i in range(count):
                    await asyncio.sleep(interval)
                    yield i


            async def main():
                async for x in ticker(0.01, 3):
                    print(x)


            asyncio.run(main())
            """,
        ),
        example("text", "0\n1\n2"),
        text(
            "`async for` автоматически вызывает `__anext__` асинхронного "
            "генератора и ждёт готовность каждого значения. Это удобно для "
            "стриминговых API, чтения больших файлов по кускам и работы с "
            "базами данных."
        ),
        heading("itertools.accumulate — накопленные результаты"),
        text(
            "`accumulate(iterable, func)` возвращает итератор накопленных "
            "результатов. По умолчанию `func` — сложение, но можно передать "
            "любую бинарную функцию. Полезно для префиксных сумм, "
            "накопленных максимумов и других скользящих вычислений."
        ),
        example(
            "python",
            """
            from itertools import accumulate
            import operator

            data = [1, 2, 3, 4, 5]
            print(list(accumulate(data)))
            print(list(accumulate(data, operator.mul)))
            print(list(accumulate(data, max)))
            """,
        ),
        example("text", "[1, 3, 6, 10, 15]\n[1, 2, 6, 24, 120]\n[1, 2, 3, 4, 5]"),
        text(
            "С `operator.mul` получаем факториалы, с `max` — префиксные "
            "максимумы. `accumulate` ленив: элементы вычисляются по "
            "требованию, а не сразу весь список."
        ),
        heading("itertools.compress — фильтрация по маске"),
        text(
            "`compress(data, selectors)` отдаёт элементы `data`, для которых "
            "соответствующий элемент `selectors` истинно. Это быстрая "
            "векторная фильтрация без явного цикла."
        ),
        example(
            "python",
            """
            from itertools import compress

            data = ["a", "b", "c", "d", "e"]
            mask = [True, False, True, False, True]
            print(list(compress(data, mask)))
            """,
        ),
        example("text", "['a', 'c', 'e']"),
        text(
            "Селекторы могут быть любым итератором булевых значений. "
            "Комбинация `compress` с `cycle` позволяет выбирать каждый "
            "N-й элемент: `compress(data, cycle([True] + [False]*(n-1)))`."
        ),
        heading("itertools.starmap — распаковка аргументов"),
        text(
            "`starmap(func, iterable)` вызывает `func(*item)` для каждого "
            "элемента итерируемого объекта, если элемент — итерируемый "
            "сам. Удобно, когда функция принимает несколько аргументов, а "
            "данные лежат в кортежах."
        ),
        example(
            "python",
            """
            from itertools import starmap

            points = [(1, 2), (3, 4), (5, 6)]
            distances = list(starmap(lambda x, y: (x**2 + y**2)**0.5, points))
            print(distances)
            """,
        ),
        example("text", "[2.23606797749979, 5.0, 7.810249675906654]"),
        heading("tee — разделение итератора"),
        text(
            "`tee(iterable, n)` возвращает `n` независимых итераторов над "
            "одними и теми же данными. Исходный итератор буферизируется, "
            "чтобы каждый клон мог читать со своей скорости. Полезно, когда "
            "нужно пройти по данным несколько раз, но исходный итератор "
            "одноразовый."
        ),
        example(
            "python",
            """
            from itertools import tee

            gen = (x**2 for x in range(5))
            a, b = tee(gen, 2)
            print(list(a))
            print(list(b))
            """,
        ),
        example("text", "[0, 1, 4, 9, 16]\n[0, 1, 4, 9, 16]"),
        text(
            "Внимание: `tee` накапливает буфер для отставших итераторов. Если "
            "один итератор далеко ушёл вперёд, память растёт. После использования "
            "клонов исходный итератор не должен использоваться."
        ),
        heading("itertools.product — декартово произведение"),
        text(
            "`product(*iterables, repeat)` выдаёт декартово произведение — "
            "все возможные комбинации по одному элементу из каждого "
            "итерируемого объекта. Параметр `repeat` повторяет один и тот же "
            "итерируемый объект несколько раз."
        ),
        example(
            "python",
            """
            from itertools import product

            print(list(product("AB", repeat=2)))
            print(list(product([1, 2], "xy")))
            """,
        ),
        example("text", "[('A', 'A'), ('A', 'B'), ('B', 'A'), ('B', 'B')]\n[(1, 'x'), (1, 'y'), (2, 'x'), (2, 'y')]"),
        heading("permutations и combinations"),
        text(
            "`permutations(iterable, r)` — упорядоченные выборки длины `r`, "
            "`combinations(iterable, r)` — неупорядоченные (без повторов), "
            "`combinations_with_replacement` — с повторами. Всё лениво."
        ),
        example(
            "python",
            """
            from itertools import permutations, combinations

            print(list(permutations("ABC", 2)))
            print(list(combinations("ABC", 2)))
            """,
        ),
        example("text", "[('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]\n[('A', 'B'), ('A', 'C'), ('B', 'C')]"),
        heading("Сопоставление с образцом в itertools"),
        text(
            "Функции `filterfalse`, `takewhile`, `dropwhile` дополняют "
            "встроенные `filter` и `map`. Они позволяют пропускать или "
            "брать элементы, пока выполняется условие, и инвертировать "
            "фильтр без лямбды с `not`."
        ),
        example(
            "python",
            """
            from itertools import filterfalse, takewhile, dropwhile

            data = [1, 2, 3, 4, 5, 6, 7, 8]

            print(list(filterfalse(lambda x: x % 2 == 0, data)))
            print(list(takewhile(lambda x: x < 5, data)))
            print(list(dropwhile(lambda x: x < 5, data)))
            """,
        ),
        example("text", "[1, 3, 5, 7]\n[1, 2, 3, 4]\n[5, 6, 7, 8]"),
        text(
            "`filterfalse` — отрицание `filter`, `takewhile` берёт пока "
            "истинно, `dropwhile` пропускает пока истинно, затем берёт всё. "
            "Для уже отсортированных данных `takewhile`/`dropwhile` работают "
            "быстрее полного фильтра."
        ),
        heading("Генераторы как корутины"),
        text(
            "Комбинация `yield`, `send`, `throw` и `close` делает генератор "
            "полноценной **корутиной** — функцией, которая может приостанавливать "
            "исполнение, принимать значения извне и возобновлять работу. Это "
            "база для `asyncio` и асинхронного программирования."
        ),
        example(
            "python",
            """
            def coroutine():
                print("Старт")
                x = yield "готов"
                print(f"Получено: {x}")
                y = yield "дальше"
                return x + y


            gen = coroutine()
            print(next(gen))
            print(gen.send(10))
            try:
                print(gen.send(20))
            except StopIteration as e:
                print(f"Возвращено: {e.value}")
            """,
        ),
        example("text", "Старт\nготов\nПолучено: 10\nдальше\nВозвращено: 30"),
        text(
            "Генератор начинает выполняться при `next()`, останавливается на "
            "первом `yield`, возвращает \"готов\". `send(10)` передаёт 10 как "
            "результат `yield`, генератор продолжает, печатает, останавливается "
            "на втором `yield`, возвращает \"дальше\". `send(20)` передаёт 20, "
            "генератор завершается с `return x + y`, поднимая `StopIteration` "
            "со значением 30. Внешний код ловит `StopIteration` и читает "
            "возвращённое значение через атрибут `.value`."
        ),
        heading("Производительность генераторов"),
        text(
            "Генераторы экономят память, но имеют накладные расходы: каждый "
            "`yield`/`next` — это вызов функции и сохранение кадра стека. Для "
            "простых операций над большими массивами NumPy или списковые "
            "включения могут быть быстрее. Профилируйте на реальных данных, "
            "прежде чем выбирать генератор."
        ),
        example(
            "python",
            """
            import timeit

            gen_sum = timeit.timeit("sum(x*x for x in range(10000))", number=100)
            list_sum = timeit.timeit("sum([x*x for x in range(10000)])", number=100)
            print(f"gen: {gen_sum:.3f}s, list: {list_sum:.3f}s")
            """,
        ),
        text(
            "Результат зависит от версии Python и задачи. Генераторное выражение "
            "избегает создания списка, но `sum` всё равно итерируется в Python. "
            "Для математических операций над массивами NumPy почти всегда "
            "победит."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                [
                    "Повторный проход по генератору",
                    "Генератор исчерпан, второй цикл пуст.",
                    "Создайте новый генератор или соберите в список.",
                ],
                [
                    "`yield from` без return",
                    "Результат подгенератора теряется.",
                    "Присваивайте: `result = yield from inner()`.",
                ],
                [
                    "send() до первого next()",
                    "TypeError: can't send non-None value to a just-started generator.",
                    "Сначала `next(gen)` или `send(None)`.",
                ],
                [
                    "groupby без сортировки",
                    "Группы разбиты на фрагменты.",
                    "Сортируйте по ключу перед groupby.",
                ],
                [
                    "Модификация списка во время итерации",
                    "RuntimeError или пропуск элементов.",
                    "Итерируйте копию или собирайте изменения отдельно.",
                ],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Каждое проверяет конкретный приём."
        ),
        numbered(
            "Напишите генератор `fibonacci()`, который бесконечно выдаёт числа Фибоначчи. Возьмите первые 15 через `islice`.",
            "Создайте класс-итератор `RangeStep(start, stop, step)`, который работает как `range`, но с произвольным шагом (включая отрицательный).",
            "Используйте `yield from` для генератора `flatten(nested)`, который расплющивает вложенные списки любого уровня.",
            "Напишите генератор `running_average()`, который принимает числа через `send` и отдаёт текущее среднее значение.",
            "Соберите конвейер из `itertools`: из `count(1)` берите только нечётные, умножайте на 2, ограничьте первыми 10 через `islice`.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example("text", "1 1 2 3 5 8 13 21 34 55 89 144 233 377 610"),
        callout(
            "success",
            "Подсказка",
            "Для `fibonacci`: `a, b = 0, 1; while True: yield a; a, b = b, a + b`. "
            "Для `flatten`: рекурсивный `yield from` при `isinstance(x, list)`.",
        ),
        heading("Проверьте себя"),
        numbered(
            "В чём разница между `iter(list)` и `list.__iter__()`?",
            "Почему генератор нельзя пройти дважды?",
            "Что делает `yield from` и чем отличается от `yield`?",
            "Когда нужен `send` вместо `next`?",
            "Почему `groupby` требует отсортированных данных?",
        ),
        heading("Ответы", 3),
        numbered(
            "`iter(list)` вызывает `list.__iter__()` и возвращает новый итератор. Прямой вызов делает то же, но `iter` — стандартный способ.",
            "Генератор сохраняет состояние и после исчерпания поднимает StopIteration. Новый проход требует нового генератора.",
            "`yield from` делегирует подгенератору: пробрасывает значения, send, throw и возвращает результат подгенератора. `yield` просто отдаёт одно значение.",
            "`send` передаёт значение внутрь генератора как результат yield. Нужен для корутин и двустороннего обмена.",
            "`groupby` группирует только подряд идущие элементы с одинаковым ключом. Без сортировки одинаковые ключи в разных местах дадут разные группы.",
        ),
        heading("Итоги"),
        bullets(
            "Итерируемый объект имеет `__iter__`, итератор — `__next__`. for работает через протокол итератора.",
            "Генераторная функция с `yield` создаёт итератор, выполняющийся по кускам.",
            "`yield from` делегирует подгенератору, `send` передаёт значение внутрь, `throw`/`close` управляют исключениями.",
            "`itertools` даёт ленивые комбинаторы: chain, cycle, islice, groupby, count.",
            "Асинхронные генераторы (`async def` + `yield`) перебираются через `async for`.",
        ),
        heading("Что дальше"),
        text(
            "Генераторы и итераторы — основа ленивых вычислений. В следующем "
            "уроке разберём контекстные менеджеры: как гарантировать "
            "очистку ресурсов через `with` и писать свои менеджеры контекста."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "PEP 255: `peps.python.org/pep-0255/` — простая генераторы.",
            "PEP 342: `peps.python.org/pep-0342/` — coroutines via enhanced generators (send/throw).",
            "Модуль `itertools`: `docs.python.org/3/library/itertools.html` — полный справочник.",
            "Асинхронные генераторы: `docs.python.org/3/reference/expressions.html#async-generators`.",
        ),
    ],
}