# -*- coding: utf-8 -*-
"""Пустые code-блоки: Python, уроки 3.6–3.11."""

from fill_common import apply_fill

FILL = {
    'python/28.json': {
        9: r"""
# Сервис заказов вызывает сервис пользователей по HTTP
import httpx

async def get_user(user_id: str) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"http://users:8000/users/{user_id}")
        response.raise_for_status()
        return response.json()
""",
        12: r"""
# users.proto:
# service Users {
#   rpc GetUser(GetUserRequest) returns (User);
# }

import grpc
from users_pb2 import GetUserRequest
from users_pb2_grpc import UsersStub

async def get_user(user_id: str):
    async with grpc.aio.insecure_channel("users:50051") as channel:
        stub = UsersStub(channel)
        return await stub.GetUser(GetUserRequest(id=user_id))
""",
        15: r"""
import json
from aiokafka import AIOKafkaProducer

producer = AIOKafkaProducer(bootstrap_servers="kafka:9092")

async def publish_order_created(order_id: str):
    await producer.start()
    try:
        await producer.send_and_wait(
            "orders",
            json.dumps({"event": "order.created", "order_id": order_id}).encode(),
        )
    finally:
        await producer.stop()
""",
        17: r"""
# events/order_created.py
from datetime import datetime
from pydantic import BaseModel, Field

class OrderCreated(BaseModel):
    event_id: str
    order_id: str
    user_id: str
    total: float = Field(ge=0)
    occurred_at: datetime

# Схема — контракт между сервисами:
# изменения только обратносовместимые
""",
        20: r"""
# API Gateway на FastAPI: маршрутизация к внутренним сервисам
from fastapi import FastAPI, HTTPException, Request, Response
import httpx

app = FastAPI()
SERVICES = {
    "users": "http://users:8000",
    "orders": "http://orders:8000",
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(service: str, path: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(404, "Unknown service")
    url = f"{SERVICES[service]}/{path}"
    async with httpx.AsyncClient() as client:
        response = await client.request(
            request.method,
            url,
            content=await request.body(),
            headers=dict(request.headers),
        )
    return Response(response.content, response.status_code)
""",
        26: r"""
# Каждый сервис слушает события и публикует свои
async def handle_order_created(event):
    if not await inventory.reserve(event["order_id"]):
        await events.publish(
            "inventory.failed", {"order_id": event["order_id"]}
        )
        return
    await events.publish(
        "inventory.reserved", {"order_id": event["order_id"]}
    )

async def handle_payment_failed(event):
    # Компенсация: освобождаем резерв
    await inventory.release(event["order_id"])
""",
        30: r"""
# Command — изменяет состояние
@dataclass
class CreateOrderCommand:
    user_id: str
    items: list[dict]

class CreateOrderHandler:
    def __init__(self, orders, events):
        self.orders, self.events = orders, events

    def handle(self, command: CreateOrderCommand) -> str:
        order = Order.create(command.user_id, command.items)
        self.orders.save(order)
        self.events.publish(OrderCreated(order.id))
        return order.id

# Query — только чтение, из денормализованной проекции
class OrderQueryService:
    def get_order(self, order_id: str) -> dict:
        return self.read_db.orders.find_one({"_id": order_id})
""",
        35: r"""
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: orders
spec:
  hosts:
    - orders
  http:
    - route:
        - destination:
            host: orders
            subset: v1
          weight: 90
        - destination:
            host: orders
            subset: v2
          weight: 10
      retries:
        attempts: 3
        perTryTimeout: 2s
""",
        41: r"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("create_order"):
    order = use_case.execute("user-1", items)
""",
        48: r"""
def create_order(session: Session, user_id: str, items: list[dict]) -> str:
    order = Order.create(user_id, items)
    session.add(order)
    # Событие пишется в ту же транзакцию, что и заказ
    session.add(OutboxMessage(
        topic="orders",
        payload={"event": "order.created", "order_id": order.id},
    ))
    session.commit()
    return order.id

# Отдельный воркер читает outbox и публикует в Kafka
""",
        52: r"""
# test_contract.py
import pytest
from pact import Consumer, Provider

pact = Consumer("web").has_pact_with(Provider("users"))

@pytest.fixture
def users_pact():
    pact.start_service()
    yield pact
    pact.stop_service()

def test_get_user(users_pact):
    expected = {"id": "1", "name": "Ann"}
    (users_pact
        .given("user 1 exists")
        .upon_receiving("a request for user 1")
        .with_request("get", "/users/1")
        .will_respond_with(200, body=expected))

    with pact:
        result = get_user("1")
    assert result == expected
""",
    },
    'python/30.json': {
        3: r"""
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-library"
version = "0.1.0"
description = "Пример современного пакета"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.7",
]

[project.optional-dependencies]
dev = ["pytest>=8", "ruff>=0.5", "mypy>=1.10"]

[project.scripts]
myapp = "my_library.cli:main"
""",
        23: r"""
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.1
    hooks:
      - id: mypy
        additional_dependencies: [pydantic]
""",
        25: r"""
name: CI

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy src/
      - run: pytest --cov=my_library --cov-fail-under=85
""",
    },
    'python/31.json': {
        9: r"""
# ❌ Никогда так не делайте
DATABASE_URL = "postgresql://admin:P@ssw0rd@prod-db:5432/app"
API_KEY = "sk-live-51H8..."

# ❌ И не коммитьте .env в git:
# .gitignore
# .env
""",
        13: r"""
# AWS Secrets Manager
import boto3
import json

def get_secret(name: str) -> dict:
    client = boto3.client("secretsmanager", region_name="eu-central-1")
    response = client.get_secret_value(SecretId=name)
    return json.loads(response["SecretString"])

secrets = get_secret("prod/app")
DATABASE_URL = secrets["DATABASE_URL"]
""",
        18: r"""
# ❌ RCE: pickle/yaml.load на недоверенных данных
import pickle
import yaml

data = pickle.loads(request.data)   # может выполнить код
config = yaml.load(request.data)    # небезопасно

# ❌ eval/exec на пользовательском вводе
result = eval(request.args["expr"])
""",
        20: r"""
import json
import yaml
from pydantic import BaseModel

# ✅ JSON — только данные
data = json.loads(request.data)

# ✅ YAML — безопасный загрузчик
config = yaml.safe_load(request.data)

# ✅ Валидация схемой
class User(BaseModel):
    name: str
    age: int

user = User.model_validate_json(request.data)
""",
        29: r"""
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    security-updates-only: true
""",
    },
    'python/32.json': {
        6: r"""
# FastAPI — асинхронный ASGI-фреймворк
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.fetch_one(
        "SELECT * FROM users WHERE id = $1", user_id
    )
    return user
""",
        11: r"""
import typer

app = typer.Typer()

@app.command()
def greet(name: str, count: int = 1):
    for _ in range(count):
        typer.echo(f"Привет, {name}!")

if __name__ == "__main__":
    app()
""",
        13: r"""
from pathlib import Path
import shutil
import subprocess

# Обход файлов и переименование
for path in Path("downloads").rglob("*.jpeg"):
    path.rename(path.with_suffix(".jpg"))

# Копирование с сохранением структуры
shutil.copytree("src", "backup", dirs_exist_ok=True)

# Запуск системной команды без shell
subprocess.run(["git", "status", "--short"], check=True)
""",
        24: r"""
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

engine = create_engine("postgresql+psycopg://user:pass@localhost/app")

with Session(engine) as session:
    user = User(name="Ann", age=20)
    session.add(user)
    session.commit()

    adults = session.scalars(
        select(User).where(User.age >= 18)
    ).all()
""",
        36: r"""
# structlog + Prometheus — структурированные логи и метрики
import structlog
from prometheus_client import Counter

log = structlog.get_logger()
orders_created = Counter("orders_created_total", "Создано заказов")

def create_order(user_id: str):
    log.info("order.create.start", user_id=user_id)
    order = repo.create(user_id)
    orders_created.inc()
    log.info("order.create.done", order_id=order.id)
    return order
""",
    },
    'python/33.json': {
        6: r"""
# PEP 8   — стиль кода
# PEP 20  — Zen of Python
# PEP 484 — аннотации типов
# PEP 517/518 — сборка пакетов
# PEP 621 — метаданные проекта в pyproject.toml

import this   # PEP 20
""",
        21: r"""
#include <Python.h>

static PyObject* hello(PyObject* self, PyObject* args) {
    const char* name;
    if (!PyArg_ParseTuple(args, "s", &name)) {
        return NULL;
    }
    return PyUnicode_FromFormat("Hello, %s!", name);
}

static PyMethodDef methods[] = {
    {"hello", hello, METH_VARARGS, "Greet a user"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "example",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC PyInit_example(void) {
    return PyModule_Create(&module);
}
""",
        23: r"""
# primes.pyx
def primes(int limit):
    cdef list result = []
    cdef int n, d
    cdef bint is_prime
    for n in range(2, limit):
        is_prime = True
        for d in range(2, int(n ** 0.5) + 1):
            if n % d == 0:
                is_prime = False
                break
        if is_prime:
            result.append(n)
    return result
""",
        26: r"""
# pybind11 — C++ код, собираемый как Python-модуль:
# #include <pybind11/pybind11.h>
# int add(int a, int b) { return a + b; }
# PYBIND11_MODULE(example, m) {
#     m.def("add", &add, "Сложить два числа");
# }

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

setup(
    name="example",
    ext_modules=[Pybind11Extension("example", ["src/main.cpp"])],
    cmdclass={"build_ext": build_ext},
)
""",
        29: r"""
import sys

# Проверка версии во время выполнения
if sys.version_info < (3, 10):
    raise RuntimeError("Требуется Python 3.10+")

# Проверка возможностей вместо версии
try:
    from tomllib import loads          # Python 3.11+
except ImportError:
    import tomli as tomllib            # fallback для 3.10
""",
        33: r"""
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest -q
""",
    },
}

LANGUAGES = {
    ('python/33.json', 21): 'c',
}

if __name__ == '__main__':
    apply_fill(FILL, languages=LANGUAGES)
