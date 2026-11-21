# -*- coding: utf-8 -*-
import json

lesson = {
  "title": "Урок 1.2: Переменные и типы данных — присваивание, числа, строки, булевы значения, преобразования, ввод",
  "slug": "peremennye-i-tipy-prisvaivanie-chisla-stroki-boolean-preobrazovaniya-input",
  "short_description": "Научимся создавать переменные, работать с основными типами данных (числа, строки, булевы значения), преобразовывать типы и получать данные от пользователя через input()",
  "goals": [
    "Понимать, что такое переменная и как работает присваивание в Python (ссылка на объект в памяти)",
    "Знать основные встроенные типы данных: int, float, complex, str, bool, None",
    "Уметь преобразовывать типы: int(), float(), str(), bool() — и понимать, когда это нужно",
    "Работать с вводом пользователя через input() и правильно обрабатывать возвращаемую строку",
    "Проверять типы через isinstance() и понимать разницу с type()",
    "Избегать типичных ошибок новичков: сравнение строки с числом, = вместо ==, конкатенация строки и числа"
  ],
  "content_blocks": [
    {"type": "heading", "level": 2, "content": "Цели урока"},
    {"type": "list", "items": [
      "Понимать, что такое переменная и как работает присваивание в Python",
      "Знать основные встроенные типы данных: целые, вещественные, комплексные числа, строки, булевы значения, None",
      "Уметь преобразовывать один тип в другой: int(), float(), str(), bool()",
      "Работать с вводом пользователя через input() и знать, что он всегда возвращает строку",
      "Проверять типы данных через isinstance() (правильный способ) вместо type() == ...",
      "Распознавать и избегать частых ошибок: = вместо ==, сложение строки с числом, input() без подсказки"
    ], "ordered": False},
    {"type": "heading", "level": 2, "content": "1. Переменные и присваивание — как это работает на самом деле"},
    {"type": "heading", "level": 3, "content": "Что такое переменная в Python"},
    {"type": "text", "content": "Представьте, что память компьютера — это огромный склад с ячейками. В каждой ячейке лежит какой-то объект: число, строка, список, функция — что угодно. Переменная — это <strong>ярлычок</strong>, который вы наклеиваете на одну из этих ячеек, чтобы потом быстро найти её.\n\nКогда вы пишете:\n\n```python\nx = 42\n```\n\nPython делает три вещи:\n1. Создаёт объект `42` (целое число) где-то в памяти\n2. Создаёт имя `x` в текущей области видимости\n3. <strong>Привязывает</strong> имя `x` к этому объекту\n\nС этого момента, где бы вы ни написали `x`, Python подставляет тот самый объект `42`. Это не «коробка со значением» (как в C/C++), а именно <strong>имя, ссылающееся на объект</strong>.\n\n> **Аналогия**: Представьте, что вы приклеили стикер с надписью \"мой_возраст\" на коробку, в которой лежит число 25. Переменная — это стикер, а не коробка. Вы можете переклеить стикер на другую коробку — и тогда переменная будет ссылаться на другое значение."},
    {"type": "code", "language": "python", "content": "# Переменная — это имя, ссылающееся на объект в памяти\nx = 42\nname = \"Анна\"\nprice = 199.99\nis_active = True\n\nprint(x)           # 42\nprint(name)        # Анна\nprint(type(x))     # <class 'int'> — проверяем тип объекта, на который ссылается x\n\n# Важно: одна и та же переменная может ссылаться на объекты разного типа\nx = 42          # x ссылается на int\nx = \"привет\"    # теперь x ссылается на str — это нормально в Python!"},
    {"type": "heading", "level": 3, "content": "Правила именования переменных (жёсткие — нарушение даст ошибку)"},
    {"type": "list", "items": [
      "Только буквы (латиница), цифры и подчёркивание `_` — `user_name`, `count2`, `_private`",
      "Не может начинаться с цифры — `1st_user` ❌, `user_1` ✅",
      "Регистр важен: `name` и `Name` — <strong>две разные</strong> переменные",
      "Нельзя использовать ключевые слова языка: `if`, `for`, `while`, `class`, `def`, `import`, `from`, `as`, `try`, `except`, `finally`, `with`, `lambda`, `return`, `yield`, `await`, `async`, `match`, `case` и др."
    ], "ordered": False},
    {"type": "heading", "level": 3, "content": "Стиль кода (PEP 8) — так пишут профессионально"},
    {"type": "list", "items": [
      "`snake_case` для переменных и функций: `user_name`, `total_price`, `is_active`, `max_connection_count`",
      "`UPPER_SNAKE_CASE` для констант (значения, которые не меняются): `MAX_SIZE`, `PI`, `TAX_RATE`, `DEFAULT_TIMEOUT`",
      "Имена должны быть <strong>описательными</strong>: `user_count` намного понятнее, чем `uc`, `cnt` или `x`",
      "Избегайте однобуквенных имён, кроме счётчиков в простых циклах (`for i in range(10):`)",
      "Имена булевых переменных лучше начинать с `is_`, `has_`, `can_`, `should_`: `is_valid`, `has_access`, `can_edit`"
    ], "ordered": False},
    {"type": "heading", "level": 3, "content": "Множественное присваивание — удобный синтаксис"},
    {"type": "text", "content": "Python позволяет присваивать значения нескольким переменным за раз. Это не только короче, но и читается легче:"},
    {"type": "code", "language": "python", "content": "# Обычный способ\nx = 10\ny = 20\nz = 30\n\n# В одну строку — tuple unpacking\nx, y, z = 10, 20, 30\n\n# Обмен значений без временной переменной — классика Python!\na = 5\nb = 10\na, b = b, a   # теперь a=10, b=5\n\n# Распаковка списка/кортежа\ncoordinates = (10, 20)\nx, y = coordinates  # x=10, y=20\n\n# * для сбора «остатка»\nfirst, *middle, last = [1, 2, 3, 4, 5]\n# first=1, middle=[2,3,4], last=5"},
    {"type": "heading", "level": 2, "content": "2. Числовые типы — int, float, complex"},
    {"type": "heading", "level": 3, "content": "int — целые числа (неограниченной точности!)"},
    {"type": "text", "content": "Тип `int` хранит целые числа: `42`, `-10`, `0`, `1_000_000`. Главная суперсила Python — <strong>целые числа неограниченной точности</strong>. В C/C++/Java `int` обычно 32 бита (максимум ~2 миллиарда), а в Python число может быть сколь угодно большим — ограничение только объёмом оперативной памяти.\n\n```python\nbig = 10 ** 1000  # гугол — 1 с 1000 нулями, работает!\nprint(len(str(big)))  # 1001 цифра\n```\n\nПодчёркивания внутри чисел (Python 3.6+) делают их читаемее — они игнорируются интерпретатором:"},
    {"type": "code", "language": "python", "content": "x = 42\ny = -10\nz = 1_000_000          # 1000000 — легче читать\nphone = 7_999_123_45_67 # как телефонный номер\nhex_num = 0xFF         # шестнадцатеричное (255)\nbin_num = 0b1010       # двоичное (10)\noct_num = 0o755        # восьмеричное (493)"},
    {"type": "heading", "level": 3, "content": "float — числа с плавающей точкой (IEEE 754)"},
    {"type": "text", "content": "Тип `float` хранит числа с дробной частью: `3.14`, `-0.5`, `2.0`. Python использует стандарт <strong>IEEE 754 (64 бита / double precision)</strong> — тот же, что и в большинстве современных языков. Это значит:\n\n- ~15-17 значащих десятичных цифр точности\n- Диапазон примерно от `1e-308` до `1e308`\n- Специальные значения: `inf` (бесконечность), `-inf`, `nan` (не число)\n\n<strong>Важно</strong>: Не используйте `float` для денежных расчётов! Из-за двоичного представления `0.1 + 0.2 = 0.30000000000000004`. Для финансов — только `decimal.Decimal` (об этом в следующих уроках)."},
    {"type": "code", "language": "python", "content": "pi = 3.14159\nscientific = 1.5e-4      # 0.00015 (научная нотация: 1.5 × 10⁻⁴)\nlarge = 2.5e10           # 25000000000.0\n\n# Специальные значения\ninf = float('inf')       # бесконечность\nneg_inf = float('-inf')  # минус бесконечность\nnan = float('nan')       # Not a Number\n\nprint(1.0 / 0.0)         # inf\nprint(0.0 / 0.0)         # nan\n\n# Проверки (встроенные функции math)\nimport math\nmath.isfinite(42)        # True\nmath.isfinite(inf)       # False\nmath.isnan(nan)          # True\nmath.isinf(inf)          # True"},
    {"type": "heading", "level": 3, "content": "complex — комплексные числа (для инженеров и физики)"},
    {"type": "text", "content": "Тип `complex` представляет числа вида `a + bj`, где `a` — вещественная часть, `b` — мнимая. В математике мнимая единица обозначается `i`, в Python — `j` (как в инженерии). Для повседневных задач они редко нужны, но полезны в DSP, квантовой механике, ЭМС."},
    {"type": "code", "language": "python", "content": "z = 3 + 4j\nprint(z.real)    # 3.0 — вещественная часть\nprint(z.imag)    # 4.0 — мнимая часть\nprint(abs(z))    # 5.0 — модуль (√(3²+4²))\nprint(z.conjugate()) # (3-4j) — комплексно-сопряжённое\n\n# Математика работает естественно\nz1 = 1 + 2j\nz2 = 2 + 3j\nprint(z1 + z2)   # (3+5j)\nprint(z1 * z2)   # (-4+7j)"},
    {"type": "heading", "level": 2, "content": "3. Строки (str) — текстовые данные"},
    {"type": "heading", "level": 3, "content": "Создание строк и неизменяемость"},
    {"type": "text", "content": "Строки в Python — это <strong>неизменяемые</strong> последовательности Unicode-символов. \"Неизменяемые\" значит: когда вы создали строку, <strong>ни один символ в ней изменить нельзя</strong>. Любая \"изменяющая\" операция (замена, удаление, приведение к верхнему регистру) создаёт <strong>новую</strong> строку, а исходная остаётся нетронутой.\n\nСтроки можно писать в одинарных, двойных или тройных кавычках. Тройные (`\"\"\"` или `'''`) позволяют писать многострочный текст без экранирования переводов строки:"},
    {"type": "code", "language": "python", "content": "single = 'одинарные кавычки'\ndouble = \"двойные кавычки\"\nmultiline = \"\"\"Первая строка\nВторая строка\nТретья строка\"\"\"\n\n# Внутри тройных кавычек можно использовать и ', и \" без экранирования\nquote = \"\"\"Он сказал: \"Привет!\" и ушёл.\"\"\"\n\n# Экранирование специальных символов\npath = 'C:\\\\Users\\\\Name'     # обратный слеш нужно удвоить\n# или raw-строка (r-prefix) — экранирование отключено\npath = r'C:\\\\Users\\\\Name'        # удобно для путей и regex"},
    {"type": "heading", "level": 3, "content": "f-строки (f-strings) — современный способ форматирования (Python 3.6+)"},
    {"type": "text", "content": "f-строки — это <strong>самый быстрый и удобный</strong> способ вставить значения в строку. Просто поставьте `f` перед кавычкой и используйте `{переменная}` или `{выражение}` внутри:"},
    {"type": "code", "language": "python", "content": "name = \"Алекс\"\nage = 25\n\n# Базовая интерполяция\ngreeting = f\"Привет, {name}! Тебе {age} лет.\"\nprint(greeting)  # Привет, Алекс! Тебе 25 лет.\n\n# Выражения внутри {}\nprint(f\"Через год тебе будет {age + 1}\")  # Через год тебе будет 26\nprint(f\"{name.upper()}!\")                 # АЛЕКС!\n\n# Форматирование чисел\nprice = 1999.99\nprint(f\"Цена: {price:.2f} руб.\")     # Цена: 1999.99 руб. (2 знака после точки)\nprint(f\"Цена: {price:,.2f} руб.\")    # Цена: 1,999.99 руб. (разделитель тысяч)\n\n# Выравнивание и заполнение\nprint(f\"{name:>10}\")   # '     Алекс' (справа, ширина 10)\nprint(f\"{name:<10}\")   # 'Алекс     ' (слева)\nprint(f\"{name:^10}\")   # '  Алекс   ' (по центру)\nprint(f\"{name:*^10}\")  # '**Алекс**' (заполнение звёздочками)"},
    {"type": "heading", "level": 3, "content": "Полезные методы строк (не меняют оригинал!)"},
    {"type": "code", "language": "python", "content": "text = \"  Python Программирование  \"\n\nprint(text.strip())       # 'Python Программирование' — убрали пробелы по краям\nprint(text.lower())       # '  python программирование  '\nprint(text.upper())       # '  PYTHON ПРОГРАММИРОВАНИЕ  '\nprint(text.title())       # '  Python Программирование  ' (каждое слово с большой)\nprint(text.replace('Python', 'Py'))  # '  Py Программирование  '\n\n# Поиск\n\"hello world\".find('world')    # 6 (индекс, -1 если не найдено)\n\"hello world\".index('world')   # 6 (ValueError если не найдено)\n'world' in \"hello world\"        # True (самый питоничный способ проверки)\n\n# Разделение и объединение\n'a,b,c'.split(',')          # ['a', 'b', 'c']\n'  a  b  c  '.split()       # ['a', 'b', 'c'] — по любому пробелу\n['a', 'b', 'c'].join('-')   # 'a-b-c'\n\n# Новые методы Python 3.9+\n'hello world'.removeprefix('hello ')  # 'world'\n'hello world'.removesuffix(' world')  # 'hello'"},
    {"type": "heading", "level": 2, "content": "4. Булевы значения (bool) — логика"},
    {"type": "heading", "level": 3, "content": "Истина и ложь"},
    {"type": "text", "content": "Тип `bool` имеет всего два значения: `True` (истина) и `False` (ложь). В Python они являются подклассом `int`: `True == 1`, `False == 0`. Булевы значения используются в условиях (`if`), циклах (`while`), и везде, где нужно решение да/нет.\n\nРезультаты сравнений (`5 > 3`, `x == y`, `\"a\" in \"abc\"`) — это тоже значения типа `bool`."},
    {"type": "code", "language": "python", "content": "is_ready = True\nis_finished = False\n\nprint(5 > 3)              # True\nprint(5 == 3)             # False\nprint(5 != 3)             # True\nprint(\"a\" in \"abc\")          # True\nprint(10 not in [1, 2, 3]) # True\n\n# Явное приведение к bool\nprint(bool(1), bool(0))       # True False\nprint(bool(\"\"), bool(\"text\")) # False True\nprint(bool([]), bool([1]))     # False True\nprint(bool(None))              # False\n\n# Логические операторы: and, or, not\nprint(True and False)   # False\nprint(True or False)    # True\nprint(not True)         # False\n\n# Важно: and/or возвращают ОДИН ИЗ ОПЕРАНДОВ, не обязательно bool!\nprint(0 or 5)           # 5 (первый truthy)\nprint(\"\" or \"default\")   # 'default'\nprint([] and 42)        # [] (первый falsy)"},
    {"type": "heading", "level": 3, "content": "Falsy и Truthy значения — что считается ложью"},
    {"type": "text", "content": "В Python есть понятие <strong>правдивости</strong> (truthiness). Любой объект можно использовать в `if` или `while`. Правило простое:\n\n<strong>Falsy (ложные) — только эти значения:</strong>\n- `False`\n- `None`\n- `0`, `0.0`, `0j`, `Decimal(0)`, `Fraction(0, 1)` — нули любых числовых типов\n- `''`, `\"\"`, `b''` — пустые строки и байты\n- `[]`, `{}`, `()`, `set()`, `range(0)` — пустые контейнеры\n\n<strong>Всё остальное — Truthy (истинно).</strong> Даже `\"0\"` (строка с нулём), `\"False\"` (строка), `[0]` (список с нулём) — всё `True`!"},
    {"type": "code", "language": "python", "content": "# Falsy значения\nfalsy = [False, None, 0, 0.0, '', [], {}, (), set(), range(0)]\nfor v in falsy:\n    print(f\"{repr(v):10} -> {bool(v)}\")\n\n# Truthy (может удивить новичков!)\ntruthy = ['0', 'False', ' ', [0], [False], {None: None}, object()]\nfor v in truthy:\n    print(f\"{repr(v):15} -> {bool(v)}\")"},
    {"type": "heading", "level": 2, "content": "5. Преобразование типов (casting) — переводчики между мирами"},
    {"type": "heading", "level": 3, "content": "Зачем это нужно?"},
    {"type": "text", "content": "Классическая ситуация: функция `input()` <strong>всегда</strong> возвращает строку, даже если пользователь ввёл число. Чтобы сложить, вычесть или сравнить как числа — нужно преобразовать. Python даёт встроенные функции-переводчики:\n\n- `int(x)` → целое число (обрезает дробную часть, <strong>не округляет!</strong>)\n- `float(x)` → вещественное число\n- `str(x)` → строковое представление\n- `bool(x)` → булево значение (по правилам truthiness)\n- `complex(x)` или `complex(real, imag)` → комплексное"},
    {"type": "code", "language": "python", "content": "# Строка -> число\nnumber = int(\"42\")\nprint(number + 8)           # 50 (теперь это математика, не конкатенация!)\n\nprice = float(\"19.99\")\nprint(price * 2)            # 39.98\n\n# Число -> строка\nage = 20\nprint(\"Возраст: \" + str(age))  # \"Возраст: 20\"\n# или лучше — f-строка:\nprint(f\"Возраст: {age}\")       # то же самое, но быстрее и чище\n\n# int() отбрасывает дробную часть (не округляет!)\nprint(int(3.9))       # 3\nprint(int(-3.9))      # -3 (в сторону нуля!)\n# Для округления — round()\nprint(round(3.9))     # 4\nprint(round(3.5))     # 4 (к чётному — banker's rounding)\nprint(round(2.5))     # 2\n\n# bool() — по правилам truthiness\nprint(bool(\"\"))       # False\nprint(bool(\"0\"))      # True! (непустая строка)\nprint(bool(0))         # False\nprint(bool([]))        # False\nprint(bool([0]))       # True! (непустой список)"},
    {"type": "heading", "level": 3, "content": "Безопасный парсинг: int.parse vs try/except"},
    {"type": "text", "content": "`int(\"привет\")` выбросит `ValueError`. В реальных программах ввод пользователя <strong>всегда</strong> нужно валидировать. Два подхода:"},
    {"type": "code", "language": "python", "content": "# Способ 1: try/except (EAFP — Easier to Ask Forgiveness than Permission)\nuser_input = \"42\"\ntry:\n    number = int(user_input)\n    print(f\"Число: {number}\")\nexcept ValueError:\n    print(\"Нужно ввести целое число!\")\n\n# Способ 2: проверка строки (LBYL — Look Before You Leap) — менее питоничный\nuser_input = \"42\"\nif user_input.lstrip('-').isdigit():  # lstrip('-') для отрицательных\n    number = int(user_input)\nelse:\n    print(\"Некорректный ввод\")\n\n# Способ 3: для float — сложнее, лучше try/except\ndef safe_float(s):\n    try:\n        return float(s)\n    except ValueError:\n        return None\n\nprint(safe_float(\"3.14\"))   # 3.14\nprint(safe_float(\"abc\"))     # None"},
    {"type": "heading", "level": 2, "content": "6. Ввод пользователя — input()"},
    {"type": "heading", "level": 3, "content": "Как получить данные от человека за экраном"},
    {"type": "text", "content": "Функция `input(подсказка)` выводит подсказку на экран, ждёт, пока пользователь наберёт текст и нажмёт Enter, и <strong>возвращает строку</strong>. Всегда строку! Даже если пользователь ввёл `42` — вернётся `\"42\"` (тип `str`).\n\n<strong>Золотое правило</strong>: если ждёте число — сразу оборачивайте в `int()` или `float()`."},
    {"type": "code", "language": "python", "content": "# Всегда давайте понятную подсказку!\nname = input(\"Как вас зовут? \")           # пробел в конце — для удобства\nprint(f\"Привет, {name}!\")\n\nage = int(input(\"Сколько вам лет? \"))     # сразу в int!\nprint(f\"Через год вам будет {age + 1}\")\n\nheight = float(input(\"Ваш рост в метрах: \"))\nprint(f\"Рост в сантиметрах: {height * 100:.0f}\")\n\n# Несколько значений в одной строке — split()\nprint(\"Введите два числа через пробел:\")\na, b = map(int, input().split())\nprint(f\"Сумма: {a + b}\")\n\n# Значение по умолчанию, если пользователь просто нажал Enter\ncity = input(\"Город [Москва]: \") or \"Москва\"\nprint(f\"Город: {city}\")"},
    {"type": "heading", "level": 3, "content": "Продвинутый ввод: валидация в цикле"},
    {"type": "text", "content": "Настоящие программы не падают на некорректном вводе — они просят повторить:"},
    {"type": "code", "language": "python", "content": "def get_age():\n    \"\"\"Запрашивает возраст до тех пор, пока не введут корректное число.\"\"\"\n    while True:\n        try:\n            age = int(input(\"Возраст: \"))\n            if age < 0:\n                print(\"Возраст не может быть отрицательным!\")\n                continue\n            if age > 150:\n                print(\"Сомнительно... Попробуйте ещё раз.\")\n                continue\n            return age\n        except ValueError:\n            print(\"Нужно ввести целое число!\")\n\nage = get_age()\nprint(f\"Ок, вам {age} лет.\")"},
    {"type": "heading", "level": 2, "content": "7. None — отсутствие значения"},
    {"type": "heading", "level": 3, "content": "Когда ничего — это тоже значение"},
    {"type": "text", "content": "`None` — это специальный синглтон (объект-одиночка), означающий \"значения нет\", \"пусто\", \"ещё не задано\". Это <strong>не</strong> `0`, не `\"\"`, не `[]` — это отдельный тип `NoneType`.\n\nЧастые сценарии:\n- Значение по умолчанию для аргумента функции (mutable default argument trap!)\n- Возвращаемое значение функции, которая ничего не возвращает явно\n- Placeholder: \"пока не знаю, что сюда положить\""},
    {"type": "code", "language": "python", "content": "result = None\nprint(result is None)    # True — проверка ТОЛЬКО через 'is'!\nprint(result == None)    # True, но 'is' правильнее (проверка идентичности)\n\n# None в функциях\ndef greet(name=None):\n    if name is None:\n        name = \"Гость\"\n    print(f\"Привет, {name}!\")\n\ngreet()           # Привет, Гость!\ngreet(\"Анна\")   # Привет, Анна!\n\n# Ловушка: НИКОГДА не делайте так!\n# def bad_func(items=[]):  # ОПАСНО — список создаётся ОДИН РАЗ при определении!\n# def good_func(items=None):\n#     if items is None:\n#         items = []  # Новый список при КАЖДОМ вызове"},
    {"type": "heading", "level": 2, "content": "8. Проверка типов — type() и isinstance()"},
    {"type": "heading", "level": 3, "content": "Как правильно узнать тип объекта"},
    {"type": "text", "content": "Функция `type(x)` возвращает класс объекта. Полезно в REPL для быстрой проверки, но <strong>в коде лучше использовать `isinstance()`</strong>:\n\n- `isinstance(obj, Class)` — проверяет, является ли объект экземпляром класса (или подкласса)\n- Учитывает наследование: `isinstance(True, int) == True` (потому что `bool` — подкласс `int`)\n- Может проверять несколько типов сразу: `isinstance(x, (int, float))`"},
    {"type": "code", "language": "python", "content": "x = 42\n\n# В REPL — ок\ntype(x)           # <class 'int'>\ntype(x) == int    # True, но хрупко (не сработает для подклассов)\n\n# В продакшн-коде — ТОЛЬКО isinstance()\nisinstance(x, int)            # True\nisinstance(True, int)         # True (bool подкласс int!)\nisinstance(x, (int, float))   # True — проверка на несколько типов\nisinstance(\"text\", (str, bytes)) # True\n\n# pattern matching (Python 3.10+) — современная альтернатива\nmatch x:\n    case int() | float() if x > 0:\n        print(\"Положительное число\")\n    case str():\n        print(\"Строка\")\n    case _:\n        print(\"Другое\")"},
    {"type": "heading", "level": 2, "content": "Практические задания для закрепления"},
    {"type": "list", "items": [
      "Создайте переменные всех базовых типов (`int`, `float`, `complex`, `str`, `bool`, `None`) и выведите их значения и типы через `type()`",
      "Напишите программу: запрашивает имя и возраст, выводит `Привет, {имя}! Через 10 лет вам будет {возраст+10}`",
      "Поэкспериментируйте с `int()`, `float()`, `str()`, `bool()` на разных значениях: `\"42\"`, `\"3.14\"`, `\"hello\"`, `\"\"`, `0`, `1`, `[]`, `[1]`, `None`",
      "Найдите 5 способов преобразовать строку в число (подсказка: `int()`, `float()`, `eval()`, `ast.literal_eval()`, `decimal.Decimal()`)",
      "Создайте калькулятор: просит два числа и операцию (+, -, *, /), выводит результат. Обработайте деление на ноль и некорректный ввод",
      "Напишите функцию `safe_int(s)`, которая возвращает `int(s)` или `None`, если преобразование невозможно (без исключений)",
      "Используя `isinstance()`, напишите функцию `describe(x)`, которая печатает тип и значение: `describe(42) -> \"int: 42\"`, `describe(\"hi\") -> \"str: hi\"`"
    ], "ordered": True},
    {"type": "heading", "level": 2, "content": "Типичные ошибки новичков — и как их избежать"},
    {"type": "table", "headers": ["Ошибка", "Почему это не работает", "Как правильно"], "rows": [
      ["`input(\"Возраст: \")` → сравнение с числом", "`input()` возвращает строку `\"25\"`, а `\"25\" > 18` — ошибка TypeError или ложное сравнение", "`age = int(input(\"Возраст: \"))` — сразу преобразуйте в число"],
      ["`if x = 5:` — одинарное равно", "Это <strong>присваивание</strong>, а не сравнение! `x` станет 5, условие всегда `True` (в Python 3.8+ — SyntaxError)", "`if x == 5:` — двойное равно для сравнения"],
      ["`\"5\" + 3` — сложение строки и числа", "Python не умеет неявно складывать `str` и `int` — TypeError", "`\"5\" + str(3)` → `\"53\"` (строка) ИЛИ `int(\"5\") + 3` → `8` (число)"],
      ["`name = input()` без подсказки", "Пользователь видит мигающий курсор и не понимает, что вводить", "`name = input(\"Имя: \")` — всегда давайте понятную подсказку"],
      ["`if x = True:` или `if x == True:`", "Избыточно и может сломаться для truthy значений (`1`, `[1]`, `\"text\"`)", "`if x:` или `if not x:` — питоничный способ проверить truthiness"],
      ["`type(x) == int` вместо `isinstance(x, int)`", "Не сработает для подклассов (`bool`, `numpy.int64`, кастомные классы)", "`isinstance(x, int)` — учитывает наследование, это правильно"],
      ["`float` для денег (`price = 19.99`)", "`0.1 + 0.2 = 0.30000000000000004` — ошибки округления бинарного float", "Используйте `from decimal import Decimal; price = Decimal('19.99')`"],
      ["`if x == True:` или `if x == False:`", "Избыточно и может сломаться для truthy значений (`1`, `[1]`, `\"text\"`)", "`if x:` или `if not x:` — питоничный способ, работает для всех truthy/falsy"]
    ]},
    {"type": "heading", "level": 2, "content": "Полезные ресурсы для глубокого изучения"},
    {"type": "list", "items": [
      "**Python.org Tutorial: Variables and Types** — https://docs.python.org/3/tutorial/introduction.html#numbers (официальное руководство)",
      "**Real Python: Python Variables** — https://realpython.com/python-variables/ (глубокое погружение с примерами)",
      "**Real Python: Python Data Types** — https://realpython.com/python-data-types/ (все типы данных подробно)",
      "**PEP 8 — Style Guide** — https://peps.python.org/pep-0008/ (как писать чистый, читаемый код)",
      "**Python Docs: Built-in Types** — https://docs.python.org/3/library/stdtypes.html (справочник по всем методам)",
      "**Effective Python: Item 1** — https://effectivepython.com/ (книга Бретта Слаткина)"
    ], "ordered": False},
    {"type": "heading", "level": 2, "content": "Ключевые выводы урока"},
    {"type": "list", "items": [
      "Переменная в Python — это <strong>имя (ярлык)</strong>, ссылающееся на объект в памяти, а не коробка со значением",
      "Присваивание `x = 42` создаёт объект `42` и привязывает имя `x` к нему. Того же имени можно привязать другой объект: `x = \"hello\"`",
      "`int` в Python — <strong>неограниченной точности</strong> (нет переполнения), `float` — IEEE 754 (15-17 цифр точности, не для денег!)",
      "Строки <strong>неизменяемы</strong> — любая \"изменяющая\" операция создаёт новую строку. Используйте f-строки для форматирования",
      "`input()` <strong>всегда</strong> возвращает строку. Ожидаете число? Оборачивайте: `int(input(...))` или `float(input(...))`",
      "`None` — это объект-синглтон типа `NoneType`, означающий \"нет значения\". Проверяйте только через `is None`",
      "Для проверки типов в коде <strong>всегда</strong> используйте `isinstance(x, Type)`, а не `type(x) == Type` — это учитывает наследование",
      "Falsy значения: `False`, `None`, `0`, `0.0`, `''`, `[]`, `{}`, `()`, `set()`. <strong>Всё остальное — Truthy</strong> (даже `\"0\"`, `\"False\"`, `[0]`)",
      "Для парсинга ввода пользователя используйте `try/except` (EAFP) — это питоничнее, чем предварительные проверки"
    ], "ordered": False}
  ],
  "practice_tasks": [
    "Создайте переменные всех базовых типов (`int`, `float`, `complex`, `str`, `bool`, `None`) и выведите их значения и типы через `type()`",
    "Напишите программу: запрашивает имя и возраст, выводит `Привет, {имя}! Через 10 лет вам будет {возраст+10}`",
    "Поэкспериментируйте с `int()`, `float()`, `str()`, `bool()` на разных значениях: `\"42\"`, `\"3.14\"`, `\"hello\"`, `\"\"`, `0`, `1`, `[]`, `[1]`, `None`",
    "Найдите 5 способов преобразовать строку в число (подсказка: `int()`, `float()`, `eval()`, `ast.literal_eval()`, `decimal.Decimal()`)",
    "Создайте калькулятор: просит два числа и операцию (+, -, *, /), выводит результат. Обработайте деление на ноль и некорректный ввод",
    "Напишите функцию `safe_int(s)`, которая возвращает `int(s)` или `None`, если преобразование невозможно (без исключений)",
    "Используя `isinstance()`, напишите функцию `describe(x)`, которая печатает тип и значение: `describe(42) -> \"int: 42\"`, `describe(\"hi\") -> \"str: hi\"`"
  ],
  "common_errors": [
    {"mistake": "`input(\"Возраст: \")` → сравнение с числом", "correct": "`age = int(input(\"Возраст: \"))` — сразу преобразуйте в число"},
    {"mistake": "`if x = 5:` (присваивание вместо сравнения)", "correct": "`if x == 5:` — двойное равно для сравнения"},
    {"mistake": "`\"5\" + 3` (сложение строки и числа)", "correct": "`\"5\" + str(3)` → строка `\"53\"` ИЛИ `int(\"5\") + 3` → число `8`"},
    {"mistake": "`name = input()` без подсказки", "correct": "`name = input(\"Имя: \")` — всегда давайте понятную подсказку"},
    {"mistake": "`type(x) == int` для проверки типа", "correct": "`isinstance(x, int)` — учитывает наследование (bool, numpy типы)"},
    {"mistake": "`float` для денежных расчётов", "correct": "`from decimal import Decimal; price = Decimal('19.99')` — точная арифметика"},
    {"mistake": "`if x == True:` или `if x == False:`", "correct": "`if x:` или `if not x:` — питоничный способ, работает для всех truthy/falsy"}
  ],
  "resources": [
    "**Python.org Tutorial: Variables and Types** — https://docs.python.org/3/tutorial/introduction.html#numbers",
    "**Real Python: Python Variables** — https://realpython.com/python-variables/",
    "**Real Python: Python Data Types** — https://realpython.com/python-data-types/",
    "**PEP 8 — Style Guide** — https://peps.python.org/pep-0008/",
    "**Python Docs: Built-in Types** — https://docs.python.org/3/library/stdtypes.html",
    "**Effective Python: Item 1** — https://effectivepython.com/"
  ],
  "key_takeaways": [
    "Переменная — это имя (ярлык), ссылающееся на объект в памяти, а не коробка со значением",
    "int — неограниченной точности, float — IEEE 754 (не для денег!), complex — для инженерии",
    "Строки неизменяемы, f-строки — лучший способ форматирования (Python 3.6+)",
    "input() всегда возвращает строку — сразу оборачивайте в int()/float()",
    "None — синглтон \"нет значения\", проверяйте через `is None`",
    "isinstance() — правильная проверка типов, учитывает наследование",
    "Falsy: False, None, 0, 0.0, '', [], {}, (). Всё остальное — Truthy",
    "Парсинг ввода: try/except (EAFP) — питоничный стандарт"
  ],
  "estimated_minutes": 25,
  "language_slug": "python",
  "lesson_order": 2
}

with open('fixtures/lessons/python/02.json', 'w', encoding='utf-8') as f:
    json.dump(lesson, f, ensure_ascii=False, indent=2)
    f.write('\n')

print("✅ Lesson 02.json successfully written with proper JSON encoding!")