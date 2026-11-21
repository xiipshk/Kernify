# -*- coding: utf-8 -*-
"""Пустые code-блоки: Python, уроки 2.8–3.2."""

from fill_common import apply_fill

FILL = {
    'python/19.json': {
        23: r"""
import asyncio

semaphore = asyncio.Semaphore(3)

async def fetch(url):
    async with semaphore:
        print("Запрос:", url)
        await asyncio.sleep(1)
        return url

async def main():
    urls = [f"https://example.com/{i}" for i in range(10)]
    results = await asyncio.gather(*(fetch(url) for url in urls))
    print("Готово:", len(results))

asyncio.run(main())
""",
        55: r"""
import asyncio
import signal

async def worker(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print("Обработка:", item)

async def main():
    queue = asyncio.Queue()
    task = asyncio.create_task(worker(queue))

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, task.cancel)

    for i in range(5):
        await queue.put(i)
    await queue.put(None)
    await task

asyncio.run(main())
""",
        57: r"""
import asyncio

async def main():
    # ❌ Блокирующий вызов останавливает весь event loop
    # time.sleep(1)

    # ✅ Используйте асинхронные аналоги
    await asyncio.sleep(1)

    # ❌ Забыли await — корутина не выполнилась
    # fetch()

    # ✅
    # await fetch()

asyncio.run(main())
""",
    },
    'python/20.json': {
        38: r"""
# alembic/env.py (фрагмент)
from alembic import context
from sqlalchemy import engine_from_config, pool
from models import Base

target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
""",
    },
    'python/21.json': {
        6: r"""
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
""",
        33: r"""
# test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

def test_read_item():
    response = client.get("/items/42?q=test")
    assert response.json() == {"item_id": 42, "q": "test"}
""",
    },
    'python/22.json': {
        34: r"""
# После сборки C-расширение импортируется как обычный модуль
import fastmath

print(fastmath.fib(100_000))
print(fastmath.sum_squares(10_000_000))

# То же самое на чистом Python работает в десятки раз медленнее,
# потому что вычисления выполняются интерпретатором, а не машинным кодом.
""",
        39: r"""
# O(n²) — проверка дубликатов вложенными циклами
def has_duplicates_slow(items):
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False

# O(n) — через множество
def has_duplicates_fast(items):
    return len(items) != len(set(items))

numbers = list(range(10_000)) + [0]
print(has_duplicates_fast(numbers))
""",
        41: r"""
from collections import deque

# ❌ list.pop(0) — O(n), сдвигает все элементы
queue = [1, 2, 3]
queue.pop(0)

# ✅ deque.popleft() — O(1)
queue = deque([1, 2, 3])
queue.popleft()

# ❌ Проверка вхождения в список — O(n)
# ✅ Проверка в множестве — O(1)
allowed = {"admin", "editor", "viewer"}
print("admin" in allowed)
""",
        45: r"""
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(100))   # мгновенно благодаря кэшу
print(fib.cache_info())
""",
        47: r"""
numbers = list(range(1_000_000))

# ❌ Медленно: цикл на Python
total = 0
for n in numbers:
    total += n

# ✅ Быстро: встроенная функция на C
total = sum(numbers)

# ✅ Генераторное выражение тоже быстрее явного цикла
squares = sum(n * n for n in numbers)
""",
        49: r"""
import sys

class PointSlots:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointDict:
    def __init__(self, x, y):
        self.x = x
        self.y = y

print(sys.getsizeof(PointSlots(1, 2)))   # меньше
print(sys.getsizeof(PointDict(1, 2)))    # больше
""",
    },
    'python/23.json': {
        5: r"""
# Класс создаётся вызовом метакласса type
class User:
    pass

# Эквивалентно:
User = type("User", (), {})

print(type(User))      # <class 'type'>
print(User.__name__)   # User
""",
        20: r"""
class Positive:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError("Значение должно быть положительным")
        instance.__dict__[self.name] = value

class Product:
    price = Positive("price")

    def __init__(self, price):
        self.price = price

print(Product(100).price)
""",
    },
    'python/24.json': {
        11: r"""
# setup.py
from setuptools import setup, Extension

setup(
    name="fastmath",
    version="0.1.0",
    ext_modules=[
        Extension(
            "fastmath",
            sources=["fastmath.c"],
            extra_compile_args=["-O3"],
        )
    ],
)
""",
        18: r"""
# fib.pyx
def fib(int n):
    cdef int a = 0
    cdef int b = 1
    cdef int i
    for i in range(n):
        a, b = b, a + b
    return a
""",
        22: r"""
# sum_squares.pyx
def sum_squares(int n):
    cdef long long total = 0
    cdef int i
    for i in range(n):
        total += i * i
    return total
""",
        39: r"""
# API mode: C-код генерируется и компилируется вместе с расширением
# build_fastmath.py
from cffi import FFI

ffi = FFI()
ffi.cdef("long long sum_squares(int n);")
ffi.set_source(
    "fastmath",
    "long long sum_squares(int n) {"
    " long long total = 0;"
    " for (int i = 0; i < n; i++) total += (long long)i * i;"
    " return total; }",
)
ffi.compile(verbose=True)
""",
    },
    'python/29.json': {
        19: r"""
import pandas as pd

df = pd.DataFrame({
    "city": ["Москва", "Москва", "Казань", "Казань"],
    "sales": [100, 150, 200, 50],
    "orders": [2, 3, 4, 1],
})

by_city = df.groupby("city").agg(
    total_sales=("sales", "sum"),
    avg_sales=("sales", "mean"),
    orders=("orders", "sum"),
)
print(by_city)
""",
    },
}

if __name__ == '__main__':
    apply_fill(FILL)
