"""Урок 3.3 курса Python: архитектура приложений."""

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
    "program_order": 3,
    "topic_order": 3,
    "name": "3.3. Архитектура приложений",
    "slug": "python-3-3-архитектура-приложений",
    "short_description": (
        "Принципы чистой архитектуры, разделение на слои (domain, application, "
        "infrastructure), DDD паттерны, Dependency Injection и организация "
        "крупных проектов."
    ),
    "topic_name": "Архитектура приложений",
    "topic_description": (
        "Как строить поддерживаемые, тестируемые и масштабируемые Python-приложения: "
        "Clean Architecture, Domain-Driven Design, Use Cases, Repository pattern, "
        "Dependency Injection и правильная структура проекта."
    ),
    "learning_objectives": [
        "Понимать проблему связанного кода и принципы чистой архитектуры",
        "Разделять приложение на слои: domain, application, infrastructure",
        "Проектировать Domain: Entities, Value Objects, Aggregates, Domain Events",
        "Писать Use Cases (Application Services) с внедрением зависимостей",
        "Реализовывать Repository pattern и инфраструктурные адаптеры",
        "Настраивать Dependency Injection вручную и через контейнеры",
        "Организовывать структуру крупного проекта",
        "Тестировать слои изолированно",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "python",
        "архитектура",
        "clean architecture",
        "ddd",
        "dependency injection",
        "repository pattern",
        "domain driven design",
    ],
    "starter_code": code(
        """
        # Проблема: спагетти-код
        def process_order(order_data):
            conn = sqlite3.connect("db.sqlite")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO orders ...", order_data)
            total = sum(item.price * item.qty for item in order_data.items)
            smtp = smtplib.SMTP("smtp.gmail.com")
            smtp.sendmail(...)
        """
    ),
    "hints": [
        "Domain слой не должен иметь внешних зависимостей (нет SQLAlchemy, FastAPI, requests).",
        "Use Case оркестрирует: получает данные -> вызывает Domain -> сохраняет через Repository -> публикует Event.",
        "Repository Interface в domain, реализация в infrastructure.",
        "DI контейнер (dependency-injector) собирает граф зависимостей в composition root.",
    ],
    "content": [
        text(
            "К концу второго уровня вы умеете писать отдельные функции, классы и модули. "
            "Но реальные проекты растут: появляются сотни файлов, десятки таблиц БД, "
            "микросервисы, внешние API. Без архитектуры код превращается в спагетти: "
            "бизнес-логика перемешана с SQL-запросами, HTTP-вызовами и логированием. "
            "Изменить одно — ломается другое. Тестировать невозможно без поднятой БД "
            "и моков всего мира.\n\n"
            "Этот урок — о том, как структурировать крупные Python-приложения так, "
            "чтобы они оставались понятными, тестируемыми и расширяемыми годами. "
            "Разберём Clean Architecture, Domain-Driven Design, Use Cases, "
            "Repository pattern, Dependency Injection и правильную структуру проекта."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "понимать, почему спагетти-код не масштабируется и как его избежать;",
            "разделять приложение на четыре слоя: Entities, Use Cases, Interface Adapters, Frameworks;",
            "проектировать Domain Layer: Entities, Value Objects, Aggregates, Domain Events, Repository Interfaces;",
            "писать Application Layer: Use Cases (Services), DTO, Event Publisher;",
            "реализовывать Infrastructure Layer: SQLAlchemy репозитории, Redis/Kafka паблишеры, email-сендеры;",
            "настраивать Dependency Injection вручную и через python-dependency-injector;",
            "организовывать структуру проекта: src-layout, разделение на domain/application/infrastructure;",
            "тестировать Domain без моков, Application с моками репозиториев.",
        ),
        heading("Проблема: спагетти-код"),
        text(
            "Типичный «всё в одном файле» скрипт:"
        ),
        example(
            "python",
            """
            # ПЛОХО: всё в одном месте
            def process_order(order_data):
                # БД
                conn = sqlite3.connect("db.sqlite")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO orders ...", order_data)
                conn.commit()

                # Бизнес-логика
                total = sum(item.price * item.qty for item in order_data.items)
                if total > 1000:
                    total *= 0.9  # скидка

                # Email
                smtp = smtplib.SMTP("smtp.gmail.com")
                smtp.sendmail(...)

                # Логирование
                logging.info(f"Order processed: {total}")
            """,
        ),
        text(
            "Проблемы такого кода:\n"
            "1. **Нетестируемо** — нельзя проверить бизнес-логику без живой БД и SMTP.\n"
            "2. **Жёсткие зависимости** — смена БД (SQLite → PostgreSQL) ломает бизнес-логику.\n"
            "3. **Дублирование** — одна и та же логика расчёта итогов копируется в разные места.\n"
            "4. **Нечитаемость** — функция делает всё: и сохраняет, и считает, и шлёт почту.\n"
            "5. **Незаменимость** — нельзя подставить другой способ уведомлений (push, SMS) "
            "не переписывая функцию."
        ),
        heading("Чистая архитектура (Clean Architecture)"),
        text(
            "Роберт Мартин (Uncle Bob) предложил концентрические круги. "
            "**Правило зависимостей**: внутренние слои НЕ знают о внешних. "
            "Зависимости направлены ВНУТРЬ — к домену."
        ),
        example(
            "text",
            """
            ┌─────────────────────────────────────┐
            │         Entities (Domain)           │  ← Бизнес-правила, нет зависимостей
            ├─────────────────────────────────────┤
            │      Use Cases (Application)        │  ← Orchestration, зависит от Domain
            ├─────────────────────────────────────┤
            │   Interface Adapters (Controllers)  │  ← Преобразование данных (API, CLI)
            ├─────────────────────────────────────┤
            │     Frameworks (Infrastructure)     │  ← DB, Web, Email, UI
            └─────────────────────────────────────┘
            """,
        ),
        text(
            "Четыре слоя (от центра к периферии):\n"
            "1. **Entities (Domain)** — ядро бизнеса. Чистый Python, никаких импортов "
            "фреймворков. Содержит бизнес-правила, инварианты.\n"
            "2. **Use Cases (Application)** — сценарии использования. Оркестрирует: "
            "получает данные -> вызывает Domain -> сохраняет через Repository -> "
            "публикует Event. Зависит только от Domain.\n"
            "3. **Interface Adapters** — контроллеры, презентеры, DTO. Преобразуют "
            "внешние данные (HTTP, CLI) в команды Use Cases и обратно.\n"
            "4. **Frameworks (Infrastructure)** — БД (SQLAlchemy), веб (FastAPI), "
            "очереди (Redis/Kafka), email, кэш. Реализуют интерфейсы из Domain/Application."
        ),
        callout(
            "info",
            "Ключевое правило",
            "Импорты идут ТОЛЬКО внутрь: infrastructure → application → domain. "
            "Обратная зависимость (domain → infrastructure) — ошибка архитектуры. "
            "Используйте интерфейсы (ABC) в domain, чтобы инвертировать зависимость.",
        ),
        heading("Domain Layer — ядро бизнеса"),
        text(
            "Domain — самый стабильный слой. Он не меняется при смене БД, веб-фреймворка "
            "или протокола обмена сообщениями. Содержит только бизнес-логику."
        ),
        heading("Entities (Сущности)", 3),
        text(
            "Entity — объект с идентичностью, который живет во времени. "
            "Имеет ID, состояние и поведение, защищающее инварианты."
        ),
        example(
            "python",
            """
            # domain/order.py
            from dataclasses import dataclass, field
            from datetime import datetime
            from typing import List
            from uuid import UUID, uuid4

            @dataclass
            class OrderItem:
                product_id: UUID
                quantity: int
                price: float

            @dataclass
            class Order:
                id: UUID = field(default_factory=uuid4)
                customer_id: UUID = None
                items: List[OrderItem] = field(default_factory=list)
                status: str = "pending"
                created_at: datetime = field(default_factory=datetime.now)

                def add_item(self, product_id: UUID, quantity: int, price: float):
                    if quantity <= 0:
                        raise ValueError("Quantity must be positive")
                    self.items.append(OrderItem(product_id, quantity, price))

                def total(self) -> float:
                    return sum(item.price * item.quantity for item in self.items)

                def apply_discount(self, threshold: float, rate: float):
                    if self.total() > threshold:
                        for item in self.items:
                            item.price *= (1 - rate)
            """,
        ),
        text(
            "Важно: методы `add_item`, `apply_discount` инкапсулируют бизнес-правила. "
            "Никакого SQL, HTTP, логирования — только чистый Python и проверки инвариантов."
        ),
        heading("Value Objects (Объекты-значения)", 3),
        text(
            "Value Object — неизменяемый объект, определяемый своим значением, "
            "а не идентичностью. Два Money с одинаковой суммой и валютой — равны. "
            "Иммутабельные (`frozen=True`), сравниваются по значению."
        ),
        example(
            "python",
            """
            # domain/value_objects.py
            from dataclasses import dataclass

            @dataclass(frozen=True)
            class Money:
                amount: float
                currency: str = "USD"

                def __add__(self, other: "Money") -> "Money":
                    if self.currency != other.currency:
                        raise ValueError("Currency mismatch")
                    return Money(self.amount + other.amount, self.currency)

                def __mul__(self, factor: float) -> "Money":
                    return Money(self.amount * factor, self.currency)
            """,
        ),
        text(
            "`frozen=True` делает датакласс неизменяемым (генерирует `__setattr__` "
            "с ошибкой). Value Objects безопасны для передачи по ссылке — их нельзя "
            "случайно изменить."
        ),
        heading("Domain Events", 3),
        text(
            "Domain Event — факт, произошедший в домене, важный для других частей "
            "системы. Имя в прошедшем времени: `OrderCreated`, `PaymentReceived`. "
            "Содержит только данные, никакого поведения."
        ),
        example(
            "python",
            """
            # domain/events.py
            from dataclasses import dataclass
            from datetime import datetime
            from uuid import UUID

            @dataclass
            class OrderCreated:
                order_id: UUID
                customer_id: UUID
                total: float
                occurred_at: datetime = datetime.now()
            """,
        ),
        heading("Repository Interface (Абстракция персистентности)", 3),
        text(
            "Repository — интерфейс для доступа к агрегатам. Domain определяет "
            "Интерфейс (ABC), Infrastructure — реализацию. Это инверсия зависимости: "
            "Domain не знает о SQLAlchemy, но зависит от абстракции."
        ),
        example(
            "python",
            """
            # domain/repositories.py
            from abc import ABC, abstractmethod
            from typing import Optional
            from uuid import UUID

            class OrderRepository(ABC):
                @abstractmethod
                def save(self, order: Order) -> None: ...

                @abstractmethod
                def get(self, order_id: UUID) -> Optional[Order]: ...

                @abstractmethod
                def list_by_customer(self, customer_id: UUID) -> list[Order]: ...
            """,
        ),
        heading("Domain Exceptions", 3),
        example(
            "python",
            """
            # domain/exceptions.py
            class DomainError(Exception):
                pass

            class OrderNotFound(DomainError):
                def __init__(self, order_id: UUID):
                    self.order_id = order_id
                    super().__init__(f"Order {order_id} not found")

            class InsufficientStock(DomainError):
                pass
            """,
        ),
        heading("Application Layer — Use Cases"),
        text(
            "Use Case (Application Service) — сценарий использования. "
            "Получает Command/DTO, оркестрирует Domain, вызывает Repository и Event Publisher. "
            "Не содержит бизнес-логики (она в Domain), только координацию."
        ),
        example(
            "python",
            """
            # application/order_service.py
            from dataclasses import dataclass
            from uuid import UUID
            from domain.order import Order, OrderItem
            from domain.repositories import OrderRepository
            from domain.events import OrderCreated
            from application.events import EventPublisher

            @dataclass
            class CreateOrderCommand:
                customer_id: UUID
                items: list[dict]  # [{"product_id": "...", "qty": 1, "price": 10.0}]

            class OrderService:
                def __init__(
                    self,
                    repo: OrderRepository,
                    events: EventPublisher,
                ):
                    self.repo = repo
                    self.events = events

                def create_order(self, cmd: CreateOrderCommand) -> Order:
                    order = Order(customer_id=cmd.customer_id)
                    for item in cmd.items:
                        order.add_item(
                            UUID(item["product_id"]),
                            item["qty"],
                            item["price"]
                        )

                    self.repo.save(order)
                    self.events.publish(OrderCreated(
                        order_id=order.id,
                        customer_id=order.customer_id,
                        total=order.total()
                    ))
                    return order

                def get_order(self, order_id: UUID) -> Order:
                    order = self.repo.get(order_id)
                    if not order:
                        raise OrderNotFound(order_id)
                    return order
            """,
        ),
        text(
            "Use Case принимает интерфейсы (`OrderRepository`, `EventPublisher`) через "
            "конструктор — это **Constructor Injection**. Реализации подставляются "
            "в composition root (main.py или DI контейнер)."
        ),
        heading("Application Events (интерфейс)", 3),
        example(
            "python",
            """
            # application/events.py
            from abc import ABC, abstractmethod
            from domain.events import OrderCreated

            class EventPublisher(ABC):
                @abstractmethod
                def publish(self, event: OrderCreated) -> None: ...
            """,
        ),
        heading("Infrastructure Layer — реализации"),
        text(
            "Infrastructure реализует интерфейсы из Domain и Application. "
            "Здесь живут SQLAlchemy, Redis, Kafka, SMTP, FastAPI."
        ),
        heading("SQLAlchemy Repository", 3),
        example(
            "python",
            """
            # infrastructure/sqlalchemy_repo.py
            from sqlalchemy import select
            from sqlalchemy.orm import Session
            from domain.order import Order
            from domain.repositories import OrderRepository
            from infrastructure.models import OrderModel

            class SqlAlchemyOrderRepository(OrderRepository):
                def __init__(self, session: Session):
                    self.session = session

                def save(self, order: Order) -> None:
                    model = OrderModel.from_domain(order)
                    self.session.merge(model)
                    self.session.commit()

                def get(self, order_id: UUID) -> Optional[Order]:
                    model = self.session.get(OrderModel, order_id)
                    return model.to_domain() if model else None

                def list_by_customer(self, customer_id: UUID) -> list[Order]:
                    stmt = select(OrderModel).where(OrderModel.customer_id == customer_id)
                    return [m.to_domain() for m in self.session.scalars(stmt)]
            """,
        ),
        text(
            "Репозиторий работает с ORM моделями (`OrderModel`), а не доменными объектами. "
            "Методы `from_domain` / `to_domain` преобразуют туда-обратно. "
            "Domain никогда не импортирует SQLAlchemy."
        ),
        heading("Event Publisher (Redis)", 3),
        example(
            "python",
            """
            # infrastructure/event_publisher.py
            from application.events import EventPublisher
            from domain.events import OrderCreated
            import json
            import redis

            class RedisEventPublisher(EventPublisher):
                def __init__(self, client: redis.Redis):
                    self.client = client

                def publish(self, event: OrderCreated) -> None:
                    self.client.publish(
                        "order_events",
                        json.dumps({
                            "type": "OrderCreated",
                            "order_id": str(event.order_id),
                            "customer_id": str(event.customer_id),
                            "total": event.total,
                        })
                    )
            """,
        ),
        heading("Dependency Injection — связывание"),
        text(
            "DI — передача зависимостей через конструктор, а не создание их внутри. "
            "Composition Root — место, где собирается граф объектов (main.py, контейнер)."
        ),
        heading("Ручное DI (Composition Root)", 3),
        example(
            "python",
            """
            # main.py / composition_root.py
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            import redis
            from infrastructure.sqlalchemy_repo import SqlAlchemyOrderRepository
            from infrastructure.event_publisher import RedisEventPublisher
            from application.order_service import OrderService

            # Конфигурация
            engine = create_engine("postgresql://user:pass@localhost/db")
            SessionLocal = sessionmaker(bind=engine)
            redis_client = redis.Redis()

            # Фабрика сервисов
            def create_order_service() -> OrderService:
                session = SessionLocal()
                repo = SqlAlchemyOrderRepository(session)
                events = RedisEventPublisher(redis_client)
                return OrderService(repo, events)

            # В FastAPI — через Depends
            from fastapi import Depends, FastAPI

            app = FastAPI()

            def get_order_service():
                return create_order_service()

            @app.post("/orders")
            def create_order(cmd: CreateOrderCommand, service: OrderService = Depends(get_order_service)):
                return service.create_order(cmd)
            """,
        ),
        heading("DI контейнеры (python-dependency-injector)", 3),
        example(
            "bash",
            """
            pip install dependency-injector
            """,
        ),
        example(
            "python",
            """
            # containers.py
            from dependency_injector import containers, providers
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            import redis

            class Container(containers.DeclarativeContainer):
                config = providers.Configuration()

                engine = providers.Singleton(
                    create_engine,
                    config.db.url,
                )

                session_factory = providers.Factory(
                    sessionmaker,
                    bind=engine,
                )

                session = providers.Factory(session_factory)

                redis_client = providers.Singleton(
                    redis.Redis.from_url,
                    config.redis.url,
                )

                order_repo = providers.Factory(
                    SqlAlchemyOrderRepository,
                    session=session,
                )

                event_publisher = providers.Factory(
                    RedisEventPublisher,
                    client=redis_client,
                )

                order_service = providers.Factory(
                    OrderService,
                    repo=order_repo,
                    events=event_publisher,
                )

            # Использование
            container = Container()
            container.config.db.url.from_env("DATABASE_URL")
            container.config.redis.url.from_env("REDIS_URL")

            service = container.order_service()
            """,
        ),
        text(
            "`dependency-injector` управляет жизненным циклом: Singleton (один на приложение), "
            "Factory (новый каждый раз), ThreadLocal. Конфигурация загружается из env/yml. "
            "В FastAPI интегрируется через `Depends(container.order_service)`."
        ),
        heading("DDD паттерны"),
        heading("Aggregate Root", 3),
        text(
            "Aggregate — кластер связанных объектов, которые изменяются вместе. "
            "Aggregate Root — единственная точка входа для изменений внутри агрегата. "
            "Внешний мир держит ссылку только на Root."
        ),
        example(
            "python",
            """
            # domain/customer.py
            from dataclasses import dataclass, field
            from uuid import UUID, uuid4
            from typing import List

            @dataclass
            class Customer:
                id: UUID = field(default_factory=uuid4)
                name: str = ""
                email: str = ""
                _orders: List[UUID] = field(default_factory=list)  # только ID!

                def place_order(self, order_id: UUID):
                    if not self.is_active:
                        raise DomainError("Customer not active")
                    self._orders.append(order_id)

                @property
                def order_ids(self) -> List[UUID]:
                    return list(self._orders)
            """,
        ),
        text(
            "`_orders` хранит только ID заказов, не сами объекты Order. "
            "Это предотвращает навигацию по графу объектов и нарушение границ агрегата."
        ),
        heading("Domain Services (логика не в Entity)", 3),
        text(
            "Не вся логика помещается в Entity. Domain Service — stateless сервис "
            "для операций, затрагивающих несколько агрегатов или не принадлежащих "
            "ни одному конкретному."
        ),
        example(
            "python",
            """
            # domain/services/pricing.py
            from domain.order import Order
            from domain.customer import Customer

            class PricingService:
                def calculate_price(self, order: Order, customer: Customer) -> float:
                    base = order.total()
                    if customer.is_vip:
                        base *= 0.9
                    if order.total() > 1000:
                        base *= 0.95
                    return round(base, 2)
            """,
        ),
        heading("Specification Pattern", 3),
        text(
            "Specification инкапсулирует бизнес-правило фильтрации. "
            "Позволяет комбинировать условия (AND, OR, NOT) и переиспользовать их."
        ),
        example(
            "python",
            """
            # domain/specifications.py
            from abc import ABC, abstractmethod
            from domain.order import Order

            class OrderSpecification(ABC):
                @abstractmethod
                def is_satisfied_by(self, order: Order) -> bool: ...

            class HighValueOrderSpec(OrderSpecification):
                def __init__(self, threshold: float):
                    self.threshold = threshold

                def is_satisfied_by(self, order: Order) -> bool:
                    return order.total() > self.threshold

            # Использование
            spec = HighValueOrderSpec(1000)
            orders = [o for o in all_orders if spec.is_satisfied_by(o)]
            """,
        ),
        heading("Структура проекта"),
        text(
            "Рекомендуемая структура (src-layout):"
        ),
        example(
            "text",
            """
            my_project/
            ├── src/
            │   └── myapp/
            │       ├── domain/
            │       │   ├── __init__.py
            │       │   ├── order.py
            │       │   ├── customer.py
            │       │   ├── value_objects.py
            │       │   ├── events.py
            │       │   ├── repositories.py
            │       │   ├── specifications.py
            │       │   └── exceptions.py
            │       ├── application/
            │       │   ├── __init__.py
            │       │   ├── order_service.py
            │       │   ├── customer_service.py
            │       │   ├── events.py
            │       │   └── dto.py
            │       ├── infrastructure/
            │       │   ├── __init__.py
            │       │   ├── sqlalchemy_repo.py
            │       │   ├── event_publisher.py
            │       │   ├── email_sender.py
            │       │   └── models.py
            │       ├── presentation/
            │       │   ├── __init__.py
            │       │   ├── api/
            │       │   │   ├── routes.py
            │       │   │   └── schemas.py
            │       │   └── cli/
            │       └── config/
            │           └── settings.py
            ├── tests/
            │   ├── unit/
            │   │   ├── domain/
            │   │   └── application/
            │   └── integration/
            ├── pyproject.toml
            └── README.md
            """,
        ),
        text(
            "Правила:\n"
            "- `src/myapp` — пакет приложения (src-layout решает проблемы импортов).\n"
            "- `domain` — никаких внешних зависимостей.\n"
            "- `application` — зависит только от `domain`.\n"
            "- `infrastructure` — зависит от `domain` и `application` (интерфейсы).\n"
            "- `presentation` — API, CLI, зависит от `application`.\n"
            "- `config` — настройки (pydantic-settings).\n"
            "- `tests/unit` — быстрые тесты без БД/сети. `tests/integration` — с БД."
        ),
        heading("Тестирование архитектуры"),
        heading("Unit тесты Domain (без моков!)", 3),
        text(
            "Domain — чистый Python, тестируется напрямую. Никаких моков, БД, сети."
        ),
        example(
            "python",
            """
            def test_order_total():
                order = Order()
                order.add_item(UUID(...), 2, 10.0)
                order.add_item(UUID(...), 1, 25.0)
                assert order.total() == 45.0

            def test_order_discount():
                order = Order()
                order.add_item(UUID(...), 10, 200.0)  # 2000
                order.apply_discount(1000, 0.1)
                assert order.total() == 1800.0

            def test_money_add():
                assert Money(10, "USD") + Money(5, "USD") == Money(15, "USD")

            def test_money_currency_mismatch():
                with pytest.raises(ValueError):
                    Money(10, "USD") + Money(5, "EUR")
            """,
        ),
        heading("Application тесты (с моками репозиториев)", 3),
        example(
            "python",
            """
            from unittest.mock import Mock
            import pytest

            def test_create_order():
                mock_repo = Mock(spec=OrderRepository)
                mock_events = Mock(spec=EventPublisher)
                service = OrderService(mock_repo, mock_events)

                cmd = CreateOrderCommand(customer_id=UUID(...), items=[...])
                order = service.create_order(cmd)

                mock_repo.save.assert_called_once_with(order)
                mock_events.publish.assert_called_once()
                published_event = mock_events.publish.call_args[0][0]
                assert published_event.order_id == order.id
                assert published_event.total == order.total()
            """,
        ),
        text(
            "Use Case тестируется изолированно: мокаем Repository и EventPublisher. "
            "Проверяем, что правильные методы вызваны с правильными аргументами."
        ),
        heading("Integration тесты"),
        text(
            "Интеграционные тесты поднимают реальную БД (Testcontainers или отдельная "
            "тестовая БД), проверяют репозитории, миграции, API эндпоинты."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Последствия", "Как правильно"],
            [
                [
                    "Бизнес-логика в репозитории",
                    "Репозиторий становится непереиспользуемым, логика размазана",
                    "Репозиторий — только CRUD. Логика в Entity/Domain Service.",
                ],
                [
                    "Entity знает о БД (импортирует SQLAlchemy)",
                    "Невозможно тестировать Domain без БД, нарушается Clean Architecture",
                    "Entity — чистый Python. ORM модели в infrastructure/models.py.",
                ],
                [
                    "Use Case делает валидацию полей",
                    "Дублирование валидации, Use Case раздувается",
                    "Валидация в Entity / Value Object / Pydantic DTO (presentation).",
                ],
                [
                    "Циклические импорты между слоями",
                    "ImportError, запутанные зависимости",
                    "Зависимости только внутрь: domain ← application ← infrastructure.",
                ],
                [
                    "Анемичная модель (только данные, методов нет)",
                    "Бизнес-логика утекает в сервисы, дублируется",
                    "Богатая модель: поведение в Entity (add_item, apply_discount).",
                ],
                [
                    "Aggregate хранит ссылки на другие Aggregate",
                    "Нарушение границ, каскадные изменения, проблемы с транзакциями",
                    "Хранить только ID других агрегатов. Навигация через Repository.",
                ],
                [
                    "DI контейнер в Domain/Application",
                    "Domain зависит от фреймворка DI",
                    "Контейнер только в composition root (main.py, presentation).",
                ],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Для DI контейнера нужен `pip install dependency-injector`."
        ),
        numbered(
            "Refactor: возьмите монолитный скрипт (например, из примера в начале урока) "
            "и разделите на слои: domain/order.py, application/order_service.py, "
            "infrastructure/sqlalchemy_repo.py, main.py с ручным DI.",
            "DDD: смоделируйте домен «Интернет-магазин»: Customer (Aggregate Root), "
            "Order (Aggregate Root), Product (Entity), Cart (Value Object или Entity). "
            "Добавьте Domain Events: OrderCreated, OrderShipped, PaymentReceived.",
            "DI: внедрите dependency-injector в FastAPI проект. Добавьте второй "
            "EventPublisher (in-memory для тестов, Redis для продакшена) и переключайте "
            "через config.",
            "Events: реализуйте Event Sourcing для Order — храните не текущее состояние, "
            "а последовательность событий. Добавьте метод `reconstruct(events)`.",
            "Hexagonal: добавьте второй адаптер (CLI через click/typer) к одному Use Case "
            "OrderService. API и CLI должны использовать один и тот же сервис.",
        ),
        text("Пример ожидаемого результата для первого задания (структура):"),
        example(
            "text",
            """
            src/
              myapp/
                domain/
                  order.py
                  repositories.py
                application/
                  order_service.py
                infrastructure/
                  sqlalchemy_repo.py
                main.py
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 1",
            "Начните с domain: перенесите класс Order, OrderRepository (ABC), исключения. "
            "Потом application: OrderService с конструктором (repo, events). "
            "Потом infrastructure: SqlAlchemyOrderRepository, InMemoryEventPublisher. "
            "В main.py соберите всё: engine, session, repo, events, service.",
        ),
        heading("Проверьте себя"),
        numbered(
            "В каком направлении идут зависимости в Clean Architecture?",
            "Чем Entity отличается от Value Object?",
            "Зачем Repository Interface в Domain, если реализация в Infrastructure?",
            "Что делает Use Case (Application Service) и чего НЕ делает?",
            "Как Domain Event отличается от Event в Infrastructure (Kafka message)?",
            "Где находится Composition Root и зачем он нужен?",
        ),
        heading("Ответы", 3),
        numbered(
            "Внутренние слои не знают о внешних. Зависимости направлены внутрь: "
            "Infrastructure → Application → Domain.",
            "Entity имеет идентичность (ID) и изменяемое состояние. Value Object "
            "идентифицируется своим значением, неизменяем (frozen=True).",
            "Инверсия зависимости: Domain зависит от абстракции (ABC), "
            "Infrastructure реализует её. Domain не импортирует SQLAlchemy.",
            "Use Case оркестрирует: получает DTO -> создаёт/изменяет Entity -> "
            "вызывает Repository.save -> публикует Domain Event. "
            "НЕ содержит бизнес-логики (она в Entity), НЕ знает о БД/HTTP.",
            "Domain Event — факт в бизнесе (OrderCreated), часть Domain, "
            "независим от транспорта. Infrastructure Event — сообщение в Kafka/Redis, "
            "сериализованное представление для передачи.",
            "Composition Root — main.py или DI контейнер в presentation слое. "
            "Собирает граф зависимостей: создаёт БД сессию, репозитории, паблишеры, "
            "передаёт их в Use Cases. Domain/Application не знают о контейнере.",
        ),
        heading("Итоги"),
        bullets(
            "Спагетти-код: бизнес-логика смешана с БД, HTTP, email — нетестируемо, нерасширяемо.",
            "Clean Architecture: 4 слоя (Entities, Use Cases, Interface Adapters, Frameworks). "
            "Зависимости только внутрь.",
            "Domain Layer: Entities (ID, поведение, инварианты), Value Objects (immutable, равенство по значению), "
            "Aggregates (Root + границы), Domain Events (факты), Repository Interfaces (ABC).",
            "Application Layer: Use Cases (Services) — оркестрация, DTO/Commands, Event Publisher Interface.",
            "Infrastructure Layer: реализации репозиториев (SQLAlchemy), паблишеры (Redis/Kafka), "
            "email, кэш, ORM модели, адаптеры фреймворков.",
            "Dependency Injection: Constructor Injection в Use Cases. Composition Root собирает граф. "
            "DI контейнер (dependency-injector) для сложных проектов.",
            "DDD паттерны: Aggregate Root (единая точка входа), Domain Services (логика нескольких агрегатов), "
            "Specification (инкапсуляция правил фильтрации).",
            "Структура проекта: src-layout, domain/application/infrastructure/presentation/config разделены.",
            "Тестирование: Domain — unit тесты без моков. Application — моки репозиториев. "
            "Integration — реальная БД/API.",
        ),
        heading("Что дальше"),
        text(
            "Архитектура приложения задаёт скелет. В следующем уроке разберём безопасность: "
            "аутентификация/авторизация (JWT, OAuth2), защита от распространённых атак "
            "(SQLi, XSS, CSRF), управление секретами, аудит и compliance."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Clean Architecture — Robert Martin (Uncle Bob)",
            "Domain-Driven Design — Eric Evans (синяя книга)",
            "Architecture Patterns with Python — Harry Percival, Bob Gregory (бесплатно: cosmicpython.com)",
            "Dependency Injection in Python — python-dependency-injector.ets-labs.org/",
            "DDD в Python примеры — github.com/cosmicpython/code",
            "Testcontainers для интеграционных тестов — testcontainers-python.readthedocs.io/",
        ),
    ],
}