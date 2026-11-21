# -*- coding: utf-8 -*-
"""Пустые code-блоки: Python, уроки 1.11–2.7."""

from fill_common import apply_fill

FILL = {
    'python/11.json': {
        5: r"""
# helpers.py — обычный модуль
def greet(name):
    return f"Привет, {name}!"

PI = 3.14159
""",
        7: r"""
# main.py
import helpers
from helpers import greet
from helpers import greet as say_hello

print(helpers.PI)
print(greet("Анна"))
print(say_hello("Иван"))
""",
        16: r"""
# mypackage/__init__.py — публичный API пакета
from .core import process
from .utils import helper

__all__ = ["process", "helper"]
__version__ = "1.0.0"
""",
        18: r"""
from mypackage import process, helper
from mypackage.core import internal_function

process()
helper()
""",
        41: r"""
# mypackage/cli.py
import click

@click.command()
@click.option("--name", default="мир", help="Кого приветствовать")
@click.option("--count", default=1, help="Сколько раз")
def main(name, count):
    # Простое консольное приложение
    for _ in range(count):
        click.echo(f"Привет, {name}!")

if __name__ == "__main__":
    main()
""",
        43: r"""
# mypackage/cli.py
import argparse

def main():
    parser = argparse.ArgumentParser(description="Простое CLI")
    parser.add_argument("name", nargs="?", default="мир")
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()

    for _ in range(args.count):
        print(f"Привет, {args.name}!")

if __name__ == "__main__":
    main()
""",
        46: r"""
# mypackage/__main__.py
from .cli import main

if __name__ == "__main__":
    main()
""",
        56: r"""
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
""",
    },
    'python/12.json': {
        8: r"""
a = [1, 2, 3]
b = a              # b ссылается на тот же объект
b.append(4)
print(a)           # [1, 2, 3, 4]
print(a is b)      # True

b = [9, 9]         # теперь b — новый объект
print(a)           # [1, 2, 3, 4] — a не изменился
print(a is b)      # False
""",
        19: r"""
def add_task(task, tasks=[]):
    tasks.append(task)
    return tasks

print(add_task("код"))    # ['код']
print(add_task("тесты"))  # ['код', 'тесты'] — баг!

def add_task(task, tasks=None):
    tasks = [] if tasks is None else tasks
    tasks.append(task)
    return tasks
""",
        28: r"""
value = None
print(value is None)          # True — правильная проверка

print(1 is 1)                 # True (интернирование)
print([] is [])               # False — разные объекты

if value is not None:
    print("Значение задано")
""",
        30: r"""
a = 256
b = 256
print(a is b)     # True — малые числа кэшируются

c = 257
d = 257
print(c is d)     # может быть False (зависит от реализации)

x = "hello"
y = "hello"
print(x is y)     # True — строковые литералы интернируются
""",
        32: r"""
def is_empty(value):
    if not value:          # использует __bool__ / __len__
        return True
    return False

print(is_empty(""))        # True
print(is_empty([]))        # True
print(is_empty("0"))       # False
print(is_empty([0]))       # False
""",
    },
    'python/13.json': {
        3: r"""
users = [
    {"name": "Ann", "skills": ["python", "sql"]},
    {"name": "Bob", "skills": ["go", "docker"]},
]

for user in users:
    print(user["name"], "->", ", ".join(user["skills"]))

matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(matrix[1][2])                 # 6
print([row[0] for row in matrix])   # [1, 4, 7]
""",
        6: r"""
numbers = range(1, 11)

squares = [n ** 2 for n in numbers]
even = [n for n in numbers if n % 2 == 0]
labels = ["чёт" if n % 2 == 0 else "нечёт" for n in numbers]

print(squares)
print(even)
print(labels)
""",
        8: r"""
words = ["apple", "banana", "cherry"]

lengths = {word: len(word) for word in words}
print(lengths)

prices = {"apple": 50, "banana": 30, "cherry": 120}
cheap = {name: price for name, price in prices.items() if price < 100}
print(cheap)
""",
        12: r"""
numbers = range(1, 1_000_000)

squares = (n ** 2 for n in numbers)   # ленивый генератор
print(next(squares))                  # 1
print(next(squares))                  # 4

total = sum(n ** 2 for n in range(10))
print(total)                          # 285
""",
        21: r"""
from operator import itemgetter, attrgetter

rows = [("Ann", 25), ("Bob", 20), ("Cid", 30)]

print(sorted(rows, key=itemgetter(1)))       # по возрасту
print(sorted(rows, key=itemgetter(1, 0)))    # возраст, затем имя

class User:
    def __init__(self, name, age):
        self.name, self.age = name, age

users = [User("Ann", 25), User("Bob", 20)]
print([u.name for u in sorted(users, key=attrgetter("age"))])
""",
        37: r"""
stack = []

stack.append("a")
stack.append("b")
stack.append("c")

print(stack.pop())   # c — LIFO
print(stack.pop())   # b
print(stack)         # ['a']

def is_balanced(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for char in text:
        if char in "([{":
            stack.append(char)
        elif char in pairs:
            if not stack or stack.pop() != pairs[char]:
                return False
    return not stack

print(is_balanced("([{}])"))   # True
print(is_balanced("([)]"))     # False
""",
        44: r"""
print(hash("hello"))
print(hash(42))

# Ключи словаря должны быть хешируемыми (неизменяемыми):
data = {("x", 1): "точка", "name": "Ann"}

# data[[1, 2]] = "ошибка"   # TypeError: unhashable type: 'list'
""",
        46: r"""
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

points = {Point(1, 2), Point(1, 2), Point(3, 4)}
print(len(points))   # 2 — дубликат схлопнулся
""",
    },
    'python/14.json': {
        10: r"""
# ❌ Ловушка: все функции используют последнее значение i
functions = [lambda: i for i in range(3)]
print([f() for f in functions])   # [2, 2, 2]

# ✅ Исправление: значение фиксируется при создании функции
functions = [lambda i=i: i for i in range(3)]
print([f() for f in functions])   # [0, 1, 2]
""",
    },
    'python/15.json': {
        4: r"""
numbers = [1, 2, 3]        # итерируемый объект
iterator = iter(numbers)   # итератор

print(next(iterator))      # 1
print(next(iterator))      # 2
print(next(iterator))      # 3
# next(iterator)           # StopIteration

for value in numbers:      # for сам вызывает iter()
    print(value)
""",
        28: r"""
squares = (n ** 2 for n in range(5))
print(next(squares))     # 0
print(list(squares))     # [1, 4, 9, 16]

total = sum(n ** 2 for n in range(1, 101))
print(total)
""",
        55: r"""
import tracemalloc
from itertools import islice

def numbers():
    n = 0
    while True:
        yield n
        n += 1

tracemalloc.start()
first = list(islice(numbers(), 1_000_000))
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print("Элементов:", len(first))
print(f"Пик памяти: {peak / 1024 / 1024:.2f} МБ")
""",
    },
    'python/16.json': {
        4: r"""
# Проблема: если между open() и close() произойдёт ошибка,
# файл останется открытым.
file = open("data.txt", "r", encoding="utf-8")
data = file.read()
file.close()

# Решение — with:
with open("data.txt", "r", encoding="utf-8") as file:
    data = file.read()
""",
        49: r"""
from contextlib import ExitStack

with open("a.txt", "w") as first, open("b.txt", "w") as second:
    first.write("A")
    second.write("B")

# Динамический набор ресурсов:
files = ["a.txt", "b.txt", "c.txt"]
with ExitStack() as stack:
    opened = [stack.enter_context(open(name, "w")) for name in files]
    for index, handle in enumerate(opened, start=1):
        handle.write(f"file {index}\n")
""",
    },
    'python/17.json': {
        3: r"""
def greet(name: str, age: int) -> str:
    return f"{name}, {age} лет"

count: int = 10
price: float = 99.5
is_active: bool = True
names: list[str] = ["Ann", "Bob"]

print(greet("Ann", 20))
""",
        5: r"""
# Python 3.9+ — без импорта из typing
def first(items: list[int]) -> int | None:
    return items[0] if items else None

mapping: dict[str, list[int]] = {"ages": [20, 30]}
pair: tuple[str, int] = ("Ann", 20)
unique: set[str] = {"a", "b"}

print(first([10, 20]))
""",
        45: r"""
# mylib.pyi — описание типов для mylib.py
def process(data: bytes, *, strict: bool = ...) -> str: ...

class Client:
    def __init__(self, url: str) -> None: ...
    def get(self, path: str) -> bytes: ...
""",
    },
    'python/18.json': {
        6: r"""
# test_calculator.py
from calculator import add, divide

def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(10, 2) == 5
""",
        45: r"""
# 1. RED — пишем падающий тест
def test_add():
    assert add(2, 3) == 5

# 2. GREEN — минимальная реализация
def add(a, b):
    return a + b

# 3. REFACTOR — улучшаем код, тесты остаются зелёными
def add(*numbers):
    return sum(numbers)
""",
        49: r"""
# conftest.py
import pytest

@pytest.fixture
def user():
    return {"name": "Ann", "age": 20}

@pytest.fixture
def client():
    from app import create_app
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client
""",
    },
}

if __name__ == '__main__':
    apply_fill(FILL)
