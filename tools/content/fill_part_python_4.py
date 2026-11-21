# -*- coding: utf-8 -*-
"""Пустые code-блоки: Python, уроки 3.3–3.5."""

from fill_common import apply_fill

FILL = {
    'python/25.json': {
        3: r"""
# ❌ Спагетти-код: HTTP, бизнес-логика, SQL и почта в одном месте
@app.post("/orders")
def create_order(request):
    data = request.json
    if not data.get("items"):
        return {"error": "Нет товаров"}, 400
    total = sum(item["price"] * item["qty"] for item in data["items"])
    connection = sqlite3.connect("shop.db")
    connection.execute(
        "INSERT INTO orders (user_id, total) VALUES (?, ?)",
        (data["user_id"], total),
    )
    connection.commit()
    send_email(data["user_email"], "Заказ создан", f"Сумма: {total}")
    return {"total": total}, 201
""",
        10: r"""
from dataclasses import dataclass, field

@dataclass
class Order:
    id: str
    user_id: str
    items: list["OrderItem"] = field(default_factory=list)
    status: str = "new"

    @property
    def total(self) -> float:
        return sum(item.price * item.quantity for item in self.items)

    def add_item(self, item: "OrderItem") -> None:
        if self.status != "new":
            raise ValueError("Нельзя менять оплаченный заказ")
        self.items.append(item)

    def pay(self) -> None:
        if not self.items:
            raise ValueError("Пустой заказ нельзя оплатить")
        self.status = "paid"
""",
        12: r"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: float
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Сумма не может быть отрицательной")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Разные валюты")
        return Money(self.amount + other.amount, self.currency)

price = Money(100, "RUB")
""",
        14: r"""
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass(frozen=True)
class OrderPaid(DomainEvent):
    order_id: str = ""
    amount: float = 0.0

event = OrderPaid(order_id="42", amount=1500)
print(event)
""",
        16: r"""
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: str) -> "Order | None": ...

    @abstractmethod
    def save(self, order: "Order") -> None: ...

    @abstractmethod
    def next_id(self) -> str: ...
""",
        18: r"""
@dataclass
class CreateOrder:
    orders: OrderRepository
    events: EventPublisher

    def execute(self, user_id: str, items: list[dict]) -> str:
        order = Order(id=self.orders.next_id(), user_id=user_id)
        for item in items:
            order.add_item(OrderItem(**item))
        self.orders.save(order)
        self.events.publish(OrderCreated(order.id))
        return order.id
""",
        21: r"""
class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, order_id: str) -> Order | None:
        row = self.session.get(OrderModel, order_id)
        return self._to_domain(row) if row else None

    def save(self, order: Order) -> None:
        self.session.merge(self._to_model(order))
        self.session.commit()

    def next_id(self) -> str:
        return str(uuid.uuid4())
""",
        23: r"""
class InMemoryEventPublisher(EventPublisher):
    def __init__(self):
        self.published = []

    def publish(self, event) -> None:
        self.published.append(event)

class KafkaEventPublisher(EventPublisher):
    def __init__(self, producer):
        self.producer = producer

    def publish(self, event) -> None:
        self.producer.send("domain-events", value=asdict(event))
""",
        25: r"""
# Ручная сборка зависимостей (composition root)
def build_create_order(session: Session) -> CreateOrder:
    orders = SqlAlchemyOrderRepository(session)
    events = InMemoryEventPublisher()
    return CreateOrder(orders=orders, events=events)

with Session(engine) as session:
    use_case = build_create_order(session)
    order_id = use_case.execute(
        "user-1", [{"sku": "A", "price": 100, "quantity": 2}]
    )
""",
        28: r"""
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    session = providers.Singleton(create_session, config.database_url)
    orders = providers.Factory(SqlAlchemyOrderRepository, session=session)
    events = providers.Singleton(InMemoryEventPublisher)
    create_order = providers.Factory(
        CreateOrder, orders=orders, events=events
    )

container = Container()
use_case = container.create_order()
""",
        31: r"""
class Order:  # Aggregate Root
    def __init__(self, id: str, user_id: str):
        self.id = id
        self.user_id = user_id
        self.items: list[OrderItem] = []
        self._events: list = []

    def add_item(self, sku: str, price: float, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        self.items.append(OrderItem(sku, price, quantity))

    @property
    def total(self) -> float:
        return sum(i.price * i.quantity for i in self.items)
""",
        33: r"""
class DiscountService:
    def calculate(self, order: Order, user: User) -> Money:
        discount = 0.0
        if user.is_vip:
            discount += 0.1
        if order.total > 10_000:
            discount += 0.05
        return Money(order.total * (1 - discount), "RUB")
""",
        35: r"""
class Specification:
    def is_satisfied_by(self, candidate) -> bool:
        raise NotImplementedError

class OverdueOrder(Specification):
    def __init__(self, now):
        self.now = now

    def is_satisfied_by(self, order) -> bool:
        return (
            order.status == "new"
            and order.created_at < self.now - timedelta(days=7)
        )

class AndSpecification(Specification):
    def __init__(self, *specs):
        self.specs = specs

    def is_satisfied_by(self, candidate) -> bool:
        return all(s.is_satisfied_by(candidate) for s in self.specs)
""",
    },
    'python/26.json': {
        6: r"""
# ❌ Уязвимо: конкатенация строк
username = request.args["username"]
query = f"SELECT * FROM users WHERE name = '{username}'"
cursor.execute(query)

# ✅ Параметризованный запрос
cursor.execute("SELECT * FROM users WHERE name = ?", (username,))

# ✅ SQLAlchemy
user = session.execute(
    select(User).where(User.name == username)
).scalar_one_or_none()
""",
        8: r"""
# ❌ Опасно: объект из запроса попадает в фильтр как есть
user = db.users.find_one({"name": request.json["name"]})

# ✅ Приводим тип и валидируем
name = str(request.json["name"])
if not name.isidentifier():
    raise ValueError("Некорректное имя")
user = db.users.find_one({"name": name})
""",
        10: r"""
import shlex
import subprocess

# ❌ shell=True + пользовательский ввод
user_file = request.args["file"]
subprocess.run(f"cat {user_file}", shell=True)

# ✅ Без shell, аргументы списком
subprocess.run(["cat", user_file], check=True)

# ✅ Если нужна строка — экранируем
subprocess.run(shlex.split(f"cat {shlex.quote(user_file)}"), check=True)
""",
        12: r"""
from ldap3.utils.conv import escape_filter_chars

# ❌ Уязвимо: подстановка в filter
search_filter = f"(uid={username})"

# ✅ Экранируем спецсимволы LDAP
search_filter = f"(uid={escape_filter_chars(username)})"
connection.search("dc=example,dc=com", search_filter)
""",
        44: r"""
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    groups:
      dev-dependencies:
        patterns: ["pytest*", "ruff*", "mypy*"]
""",
        52: r"""
import os

# ✅ Секреты берутся из окружения
DATABASE_URL = os.environ["DATABASE_URL"]
SECRET_KEY = os.environ["SECRET_KEY"]

# ❌ Так делать нельзя:
# SECRET_KEY = "super-secret-hardcoded-value"

# В продакшене — Secret Manager (AWS/GCP/Vault), а не .env
""",
        61: r"""
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.9
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml", "-r", "src"]

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks
""",
    },
    'python/27.json': {
        4: r"""
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
        6: r"""
FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels
COPY . .

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
""",
        13: r"""
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest -q
""",
        15: r"""
jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
""",
        18: r"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/example/api:1.0.0
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: api-secrets
""",
        20: r"""
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
""",
        22: r"""
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt
spec:
  ingressClassName: nginx
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 80
""",
        24: r"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
data:
  LOG_LEVEL: info
  FEATURE_FLAGS: "new_ui,beta_api"
---
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
type: Opaque
stringData:
  DATABASE_URL: postgresql://user:pass@db:5432/app
""",
        33: r"""
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
""",
        39: r"""
from prometheus_client import Counter, Histogram, start_http_server

REQUESTS = Counter(
    "http_requests_total", "Всего запросов", ["method", "path", "status"]
)
LATENCY = Histogram("http_request_seconds", "Время ответа", ["path"])

@LATENCY.labels("/orders").time()
def handle_orders():
    REQUESTS.labels("GET", "/orders", "200").inc()
    return {"orders": []}

if __name__ == "__main__":
    start_http_server(9090)   # метрики на /metrics
""",
        41: r"""
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "api"
    metrics_path: /metrics
    static_configs:
      - targets: ["api:9090"]
""",
        45: r"""
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: containers
    static_configs:
      - targets: [localhost]
        labels:
          job: api
          __path__: /var/log/containers/*.log
""",
        48: r"""
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: api
spec:
  replicas: 5
  strategy:
    canary:
      steps:
        - setWeight: 20
        - pause: { duration: 5m }
        - setWeight: 50
        - pause: { duration: 10m }
        - setWeight: 100
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/example/api:1.1.0
""",
    },
}

if __name__ == '__main__':
    apply_fill(FILL)
