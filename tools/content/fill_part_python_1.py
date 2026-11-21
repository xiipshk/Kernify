# -*- coding: utf-8 -*-
"""Пустые code-блоки: Python, уроки 1.1–1.9."""

from fill_common import apply_fill

FILL = {
    'python/01.json': {
        38: r"""
print("Привет, мир!")
print("Меня зовут Python")
print(2 + 2)
print("Результат:", 2 + 2)
""",
        42: r"""
# Это комментарий — Python его игнорирует
print("Код выполняется")  # комментарий в конце строки

# Хороший комментарий объясняет «почему»:
price = 1000
tax = price * 0.2  # НДС 20%
""",
    },
    'python/03.json': {
        5: r"""
a, b = 10, 3
print(a + b)   # 13   — сложение
print(a - b)   # 7    — вычитание
print(a * b)   # 30   — умножение
print(a / b)   # 3.333... — истинное деление
print(a // b)  # 3    — целочисленное деление
print(a % b)   # 1    — остаток
print(a ** b)  # 1000 — возведение в степень
""",
        8: r"""
n = 17
print(n % 2 == 0)   # False — число нечётное
print(n // 5)       # 3 — сколько целых пятёрок помещается
print(n % 5)        # 2 — остаток

for number in range(1, 6):
    print(number, "чётное" if number % 2 == 0 else "нечётное")
""",
        20: r"""
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)   # True  — одинаковое содержимое
print(a is b)   # False — разные объекты

c = a
print(a is c)   # True  — одна и та же ссылка
""",
        24: r"""
age = 20
has_ticket = True

print(age >= 18 and has_ticket)   # True
print(age < 18 or has_ticket)     # True
print(not has_ticket)             # False
""",
        27: r"""
def check():
    print("check() вызвана")
    return True

print(False and check())   # check() не вызывается -> False
print(True or check())     # check() не вызывается -> True

# Практическая польза — защита от деления на ноль:
divisor = 0
result = divisor != 0 and 10 / divisor
print(result)              # False, ошибки нет
""",
        36: r"""
fruits = ["apple", "banana", "cherry"]
print("banana" in fruits)      # True
print("grape" not in fruits)   # True
print("app" in "apple")        # True — подстрока
print("name" in {"name": "Ann", "age": 20})  # True — ключ словаря
""",
        40: r"""
a, b = 5, 3          # 101 и 011 в двоичном виде
print(a & b)         # 1   — побитовое И
print(a | b)         # 7   — побитовое ИЛИ
print(a ^ b)         # 6   — исключающее ИЛИ
print(~a)            # -6  — побитовое НЕ
print(a << 1)        # 10  — сдвиг влево
print(a >> 1)        # 2   — сдвиг вправо
""",
        49: r"""
age = 20
status = "взрослый" if age >= 18 else "ребёнок"
print(status)   # взрослый

username = None
display_name = username if username else "Гость"
print(display_name)   # Гость
""",
    },
    'python/04.json': {
        25: r"""
values = [False, None, 0, 0.0, "", [], {}, set()]
for value in values:
    print(repr(value), "->", bool(value))

print(bool("0"))    # True — непустая строка
print(bool([0]))    # True — непустой список
print(bool(-1))     # True — ненулевое число
""",
        29: r"""
age = 18
message = "Доступ разрешён" if age >= 18 else "Доступ запрещён"
print(message)

# Эквивалент через if/else:
if age >= 18:
    message = "Доступ разрешён"
else:
    message = "Доступ запрещён"
""",
        36: r"""
age = 25
if 18 <= age < 65:
    print("Работоспособный возраст")
""",
        38: r"""
role = "admin"
is_active = True

if role == "admin" and is_active:
    print("Полный доступ")
elif role == "editor" or role == "author":
    print("Редактирование контента")
else:
    print("Только чтение")
""",
    },
    'python/05.json': {
        5: r"""
countdown = 5
while countdown > 0:
    print(countdown)
    countdown -= 1
print("Старт!")
""",
        13: r"""
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

for index, fruit in enumerate(fruits, start=1):
    print(index, fruit)

for char in "Python":
    print(char)
""",
        17: r"""
for number in range(1, 11):
    if number == 5:
        break          # прекратить цикл
    print(number)

for number in range(1, 6):
    if number % 2 == 0:
        continue       # пропустить чётные
    print(number)

# else выполняется, если не было break:
for number in range(3):
    print(number)
else:
    print("Цикл завершился без break")
""",
        21: r"""
for row in range(1, 4):
    for col in range(1, 4):
        print(f"{row * col:2}", end=" ")
    print()
""",
        25: r"""
numbers = [1, 2, 3, 4, 5, 6]

# ❌ Плохо: удаление во время перебора
# for n in numbers:
#     if n % 2 == 0:
#         numbers.remove(n)

# ✅ Хорошо: новый список
odd = [n for n in numbers if n % 2 != 0]
print(odd)          # [1, 3, 5]
print(numbers)      # [1, 2, 3, 4, 5, 6]
""",
    },
    'python/06.json': {
        16: r"""
a = [1, 2, 3]
b = a              # ссылка на тот же список
c = a.copy()       # поверхностная копия
d = a[:]           # тоже копия

b.append(4)
print(a)           # [1, 2, 3, 4]
print(c)           # [1, 2, 3]

import copy
nested = [[1, 2], [3, 4]]
deep = copy.deepcopy(nested)
""",
        18: r"""
point = (10, 20)
x, y = point          # распаковка
print(x, y)

single = (42,)        # кортеж из одного элемента — нужна запятая
print(type(single))   # <class 'tuple'>

# point[0] = 5        # TypeError: кортеж неизменяем
""",
        20: r"""
numbers = {1, 2, 2, 3, 3, 4}
print(numbers)              # {1, 2, 3, 4} — дубликаты удалены

numbers.add(5)
numbers.discard(1)
print(2 in numbers)         # True

a = {1, 2, 3}
b = {3, 4, 5}
print(a | b)                # объединение
print(a & b)                # пересечение
print(a - b)                # разность
""",
        28: r"""
user = {"name": "Ann", "age": 20}

# Безопасное удаление
age = user.pop("age", None)
print(age)            # 20
print(user)           # {'name': 'Ann'}

# Значение по умолчанию
print(user.get("email", "не указан"))

# Объединение словарей (Python 3.9+)
defaults = {"theme": "light", "lang": "ru"}
settings = defaults | {"theme": "dark"}
print(settings)
""",
        34: r"""
person = {"name": "Ann", "age": 20, "city": "Москва"}

for key in person:
    print(key, person[key])

for key, value in person.items():
    print(f"{key}: {value}")

for index, (key, value) in enumerate(person.items(), start=1):
    print(index, key, value)
""",
    },
    'python/08.json': {
        16: r"""
# ❌ Ловушка: список создаётся один раз
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item("a"))   # ['a']
print(add_item("b"))   # ['a', 'b'] — неожиданно!

# ✅ Правильно: None как значение по умолчанию
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
""",
        20: r"""
x = "глобальная"

def outer():
    x = "внешняя"

    def inner():
        x = "локальная"
        print(x)       # локальная

    inner()
    print(x)           # внешняя

outer()
print(x)               # глобальная
""",
        26: r"""
square = lambda x: x ** 2
print(square(5))       # 25

numbers = [3, 1, 4, 2]
numbers.sort(key=lambda n: -n)
print(numbers)         # [4, 3, 2, 1]

pairs = [(1, "b"), (2, "a")]
print(sorted(pairs, key=lambda p: p[1]))  # [(2, 'a'), (1, 'b')]
""",
    },
    'python/09.json': {
        4: r"""
# Открытие файла вручную — нужно не забыть закрыть
file = open("example.txt", "r", encoding="utf-8")
try:
    content = file.read()
    print(content)
finally:
    file.close()
""",
        6: r"""
with open("example.txt", "r", encoding="utf-8") as file:
    content = file.read()
    print(content)
# файл автоматически закрыт
""",
        12: r"""
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("Первая строка\n")
    file.write("Вторая строка\n")

with open("output.txt", "a", encoding="utf-8") as file:
    file.write("Добавлено в конец\n")

with open("output.txt", "r", encoding="utf-8") as file:
    print(file.read())
""",
        14: r"""
data = bytes([0x48, 0x65, 0x6C, 0x6C, 0x6F])  # "Hello"

with open("data.bin", "wb") as file:
    file.write(data)

with open("data.bin", "rb") as file:
    raw = file.read()
    print(raw)          # b'Hello'
    print(raw.decode("utf-8"))
""",
        23: r"""
try:
    number = int("не число")
    result = 10 / number
except ValueError as error:
    print("Некорректное число:", error)
except ZeroDivisionError as error:
    print("Деление на ноль:", error)
else:
    print("Результат:", result)
finally:
    print("Блок finally выполняется всегда")
""",
    },
}

if __name__ == '__main__':
    apply_fill(FILL)
