"""Урок 3.6 курса Python: микросервисы."""

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
    "topic_order": 6,
    "name": "3.6. Микросервисы",
    "slug": "python-3-6-микросервисы",
    "short_description": (
        "Архитектура микросервисов: коммуникация (REST, gRPC, async), паттерны "
        "(API Gateway, Circuit Breaker, Saga, CQRS), Service Mesh (Istio), "
        "наблюдаемость (OpenTelemetry, трассировка), тестирование."
    ),
    "topic_name": "Микросервисы",
    "topic_description": (
        "Как проектировать и эксплуатировать микросервисную архитектуру: "
        "выбор способа коммуникации, паттерны распределённых систем, "
        "Service Mesh, распределённая трассировка и тестирование контрактов."
    ),
    "learning_objectives": [
        "Понимать плюсы и минусы микросервисов vs монолит, когда их применять",
        "Выбирать способ коммуникации: синхронный (REST, gRPC) или асинхронный (RabbitMQ, Kafka)",
        "Реализовывать паттерны: API Gateway, Circuit Breaker, Saga (хореография/оркестрация), CQRS",
        "Настраивать Service Mesh (Istio): mTLS, traffic management, circuit breaker",
        "Внедрять OpenTelemetry для распределённой трассировки, коррелировать логи с trace_id",
        "Применять Transactional Outbox для надёжной публикации событий",
        "Писать Contract Tests (Pact) и использовать Testcontainers для интеграционных тестов",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "python",
        "микросервисы",
        "grpc",
        "kafka",
        "rabbitmq",
        "circuit breaker",
        "saga",
        "cqrs",
        "istio",
        "opentelemetry",
    ],
    "starter_code": code(
        """
        # Простой API Gateway на FastAPI
        from fastapi import FastAPI, Request, HTTPException
        import httpx

        app = FastAPI()
        SERVICES = {
            "users": "http://user-service:8000",
            "orders": "http://order-service:8000",
        }

        @app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def gateway(service: str, path: str, request: Request):
            if service not in SERVICES:
                raise HTTPException(404, "Service not found")
            # ... проксирование запроса
        """
    ),
    "hints": [
        "Микросервисы добавляют операционную сложность. Начинайте с модульного монолита.",
        "Для синхронных вызовов всегда ставьте timeout и retry. Используйте Circuit Breaker.",
        "Saga — для длинных распределённых транзакций. Хореография проще, оркестрация — понятнее.",
        "OpenTelemetry: автоинструментация (FastAPI, httpx) + ручные спаны для бизнес-логики.",
    ],
    "content": [
        text(
            "К концу урока 3.5 вы умеете деплоить одно приложение в Kubernetes с CI/CD, "
            "мониторингом и логами. Но реальные системы растут: появляются разные команды, "
            "разные домены, разные нагрузки. Монолит становится тормозом: малейшее изменение "
            "требует полного редеплоя, база данных разрастается, команды мешают друг другу. "
            "Микросервисы — архитектурный ответ на эту сложность. Но они приносят свою: "
            "сетевые сбои, eventual consistency, распределённая отладка. В этом уроке разберём, "
            "как строить микросервисы правильно: коммуникация, паттерны, Service Mesh, "
            "наблюдаемость и тестирование."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "понимать, когда микросервисы оправданы, а когда лучше модульный монолит;",
            "выбирать между синхронной (REST, gRPC) и асинхронной (RabbitMQ, Kafka) коммуникацией;",
            "реализовывать API Gateway: роутинг, аутентификация, rate limiting, трансформация;",
            "применять Circuit Breaker (pybreaker) для защиты от каскадных сбоев;",
            "проектировать распределённые транзакции через Saga (хореография и оркестрация);",
            "понимать CQRS: разделение Write/Read моделей, Event-driven проекции;",
            "настраивать Service Mesh (Istio): mTLS, VirtualService, DestinationRule, circuit breaker;",
            "внедрять OpenTelemetry: автоинструментация + ручные спаны, экспорт в Jaeger/Tempo;",
            "коррелировать логи с trace_id, использовать Transactional Outbox для событий;",
            "писать Contract Tests (Pact) и интеграционные тесты с Testcontainers.",
        ),
        heading("Монолит vs Микросервисы"),
        table(
            ["Аспект", "Монолит", "Микросервисы"],
            [
                ["Деплой", "Один артефакт", "Независимые деплои"],
                ["Масштабирование", "Всё сразу", "Выборочно по сервисам"],
                ["Технологический стек", "Один", "Полиглот (Python, Go, Rust...)"],
                ["Команда", "Одна большая", "Независимые небольшие команды"],
                ["Сложность", "Низкая (в начале)", "Высокая (операционная)"],
                ["Отладка", "Простая (локально)", "Распределённая трассировка"],
                ["Данные", "Одна БД, ACID", "Database per Service, eventual consistency"],
            ],
        ),
        text(
            "Микросервисы **не нужны**, если:\n"
            "- Команда меньше 5 человек\n"
            "- Домен простой (CRUD, без сложных бизнес-процессов)\n"
            "- Нет потребности в независимом масштабировании частей системы\n"
            "- В организации низкая DevOps зрелость (нет CI/CD, k8s, мониторинга)\n\n"
            "Начинайте с **модульного монолита** (clean architecture внутри одного деплоя). "
            "Выделяйте сервисы по границам доменов (bounded contexts) по мере роста."
        ),
        heading("Коммуникация между сервисами"),
        heading("Синхронная: REST / HTTP", 3),
        example(
            "python",
            """
            # Клиент (httpx — современный async HTTP клиент)
            import httpx

            async def get_user(user_id: str) -> dict:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(f"http://user-service/users/{user_id}")
                    resp.raise_for_status()
                    return resp.json()
            """,
        ),
        text(
            "REST/HTTP — просто, везде поддерживается, читается в логах. Правила:\n"
            "- Всегда ставьте `timeout` (connect + read).\n"
            "- Используйте `raise_for_status()` или проверяйте статус коды.\n"
            "- Для внутренней коммуникации добавляйте заголовки: `X-Request-ID`, `X-Trace-ID`.\n"
            "- Версионируйте API в пути (`/api/v1/users`) или заголовках."
        ),
        heading("Синхронная: gRPC (высокая производительность, контракты)", 3),
        example(
            "protobuf",
            """
            // user.proto
            syntax = "proto3";
            package user;

            service UserService {
              rpc GetUser(GetUserRequest) returns (User);
              rpc ListUsers(ListUsersRequest) returns (stream User);
            }

            message GetUserRequest { string id = 1; }
            message User { string id = 1; string name = 2; string email = 3; }
            """,
        ),
        example(
            "python",
            """
            # server
            import grpc
            from user_pb2 import User
            from user_pb2_grpc import UserServiceServicer

            class UserServicer(UserServiceServicer):
                async def GetUser(self, request, context):
                    return User(id=request.id, name="Анна", email="anna@example.com")

            # client
            channel = grpc.aio.insecure_channel("user-service:50051")
            stub = UserServiceStub(channel)
            user = await stub.GetUser(GetUserRequest(id="123"))
            """,
        ),
        text(
            "gRPC — бинарный протокол на HTTP/2, кодогенерация из `.proto`:\n"
            "- Контракт (`proto` файл) — единственный источник истины для клиента и сервера.\n"
            "- Поддерживает streaming (server-side, client-side, bidirectional).\n"
            "- gRPC-gateway позволяет экспортировать REST поверх gRPC.\n"
            "- Для Python: `pip install grpcio grpcio-tools`, генерация: `python -m grpc_tools.protoc`."
        ),
        heading("Асинхронная: Message-Driven (RabbitMQ / Kafka)", 3),
        example(
            "python",
            """
            # Producer (FastAPI + aio-pika для RabbitMQ)
            import aio_pika
            import json

            async def publish_order_created(order: dict):
                connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
                async with connection:
                    channel = await connection.channel()
                    exchange = await channel.declare_exchange("orders", aio_pika.ExchangeType.TOPIC)
                    await exchange.publish(
                        aio_pika.Message(body=json.dumps(order).encode()),
                        routing_key="order.created"
                    )

            # Consumer
            async def consume_orders():
                connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
                async with connection:
                    channel = await connection.channel()
                    queue = await channel.declare_queue("order_service_orders", durable=True)
                    await queue.bind(exchange, "order.*")
                    async with queue.iterator() as queue_iter:
                        async for message in queue_iter:
                            async with message.process():
                                order = json.loads(message.body)
                                await process_order(order)
            """,
        ),
        text(
            "RabbitMQ — умный брокер (exchange, queue, binding), гарантирует доставку, "
            "подходит для задач и событий. Kafka — лог событий, высокая пропускная способность, "
            "репликация, replay. Выбор:\n"
            "- RabbitMQ: команды, задачи, обычные события, сложная маршрутизация.\n"
            "- Kafka: event sourcing, audit log, высокая нагрузка, replay, stream processing.\n\n"
            "Для Kafka используйте Schema Registry (Avro/Protobuf) — контакты не ломаются."
        ),
        heading("Event Schema (Avro/Protobuf для Kafka)", 3),
        example(
            "python",
            """
            # Schema Registry пример (Avro)
            from confluent_kafka.schema_registry import SchemaRegistryClient
            from confluent_kafka.schema_registry.avro import AvroSerializer

            schema_str = '''
            {
              "type": "record",
              "name": "OrderCreated",
              "fields": [
                {"name": "order_id", "type": "string"},
                {"name": "customer_id", "type": "string"},
                {"name": "total", "type": "double"}
              ]
            }
            '''
            """,
        ),
        heading("Паттерны микросервисов"),
        heading("API Gateway", 3),
        example(
            "python",
            """
            # Kong / Traefik / NGINX / AWS API Gateway — production
            # Пример на FastAPI как простой gateway
            from fastapi import FastAPI, Request, HTTPException
            import httpx

            app = FastAPI()
            SERVICES = {
                "users": "http://user-service:8000",
                "orders": "http://order-service:8000",
                "products": "http://product-service:8000",
            }

            @app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
            async def gateway(service: str, path: str, request: Request):
                if service not in SERVICES:
                    raise HTTPException(404, "Service not found")

                async with httpx.AsyncClient() as client:
                    url = f"{SERVICES[service]}/{path}"
                    resp = await client.request(
                        request.method, url,
                        headers=dict(request.headers),
                        content=await request.body(),
                        params=request.query_params
                    )
                return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)
            """,
        ),
        text(
            "API Gateway — единая точка входа:\n"
            "- Роутинг к сервисам\n"
            "- Аутентификация/авторизация (JWT валидация, передача user_id в заголовки)\n"
            "- Rate limiting, DDoS защита\n"
            "- Трансформация запросов/ответов, агрегация\n"
            "- SSL termination\n\n"
            "Production: Kong, Traefik, NGINX Plus, AWS API Gateway, Envoy. "
            "FastAPI gateway подходит для прототипов и малых систем."
        ),
        heading("Circuit Breaker", 3),
        example(
            "bash",
            """
            pip install pybreaker
            """,
        ),
        example(
            "python",
            """
            import pybreaker
            import httpx

            breaker = pybreaker.CircuitBreaker(
                fail_max=5,
                reset_timeout=30,
                exclude=[httpx.HTTPStatusError]
            )

            @breaker
            async def call_user_service(user_id: str):
                async with httpx.AsyncClient() as client:
                    return await client.get(f"http://user-service/users/{user_id}")

            # Использование с fallback
            async def get_user_with_fallback(user_id: str):
                try:
                    return await call_user_service(user_id)
                except pybreaker.CircuitBreakerError:
                    return {"id": user_id, "name": "Unknown", "cached": True}
            """,
        ),
        text(
            "Circuit Breaker предотвращает каскадные сбои:\n"
            "- `fail_max=5` — после 5 ошибок переходит в OPEN.\n"
            "- `reset_timeout=30` — через 30 сек переходит в HALF-OPEN (пробный запрос).\n"
            "- `exclude` — не считать ошибки 4xx как сбои (это клиентские ошибки).\n"
            "- Fallback возвращает кэшированные/дефолтные данные вместо ошибки."
        ),
        heading("Saga Pattern (распределённые транзакции)", 3),
        heading("Хореография (события)", 3),
        example(
            "python",
            """
            # Order Service
            async def create_order(order_data):
                order = Order(**order_data)
                order.status = "pending"
                await order.save()

                # Публикуем событие
                await publish_event("order.created", {"order_id": order.id, "items": order.items})

                # Ждём подтверждений через callback/event
                return order

            # Payment Service — слушает order.created
            async def handle_order_created(event):
                try:
                    payment = await charge_customer(event["customer_id"], event["total"])
                    await publish_event("payment.completed", {"order_id": event["order_id"]})
                except PaymentFailed:
                    await publish_event("payment.failed", {"order_id": event["order_id"]})

            # Order Service — слушает payment.completed/failed
            async def handle_payment_result(event):
                order = await Order.get(event["order_id"])
                if event["type"] == "payment.completed":
                    order.status = "paid"
                else:
                    order.status = "cancelled"
                    await compensate_inventory(event["order_id"])
                await order.save()
            """,
        ),
        heading("Оркестрация (централизованный координатор)", 3),
        example(
            "python",
            """
            class OrderSaga:
                def __init__(self):
                    self.steps = [
                        (self.reserve_inventory, self.release_inventory),
                        (self.charge_payment, self.refund_payment),
                        (self.create_shipment, self.cancel_shipment),
                    ]

                async def execute(self, order_data):
                    completed = []
                    try:
                        for forward, _ in self.steps:
                            await forward(order_data)
                            completed.append(forward)
                    except Exception:
                        # Компенсация в обратном порядке
                        for _, backward in reversed(completed):
                            await backward(order_data)
                        raise
            """,
        ),
        text(
            "Выбор:\n"
            "- **Хореография** — сервисы общаются событиями, нет центрального координатора. "
            "Проще начать, но сложнее отлаживать (где застрял процесс?).\n"
            "- **Оркестрация** — централизованный Saga Orchestrator управляет шагами. "
            "Понятнее flow, легче мониторить, но создаёт связность с оркестратором.\n\n"
            "Для критических бизнес-процессов (заказ → оплата → инвентарь → доставка) "
            "оркестрация часто лучше."
        ),
        heading("CQRS (Command Query Responsibility Segregation)", 3),
        example(
            "python",
            """
            # Write Model (Commands)
            class OrderCommandHandler:
                async def handle_create_order(self, cmd: CreateOrderCommand):
                    order = Order.create(cmd.customer_id, cmd.items)
                    await order_repo.save(order)
                    await event_bus.publish(OrderCreated(order.id, ...))

            # Read Model (Queries) — отдельная БД/проекция
            class OrderQueryHandler:
                async def handle_get_order_summary(self, query: GetOrderSummary):
                    # Денормализованное представление из Elasticsearch/Redis
                    return await read_model.get_order_summary(query.order_id)

            # Event Handler обновляет Read Model
            async def on_order_created(event: OrderCreated):
                summary = OrderSummary(
                    order_id=event.order_id,
                    customer_name=event.customer_name,
                    total=event.total,
                    status="pending"
                )
                await read_model.save(summary)
            """,
        ),
        text(
            "CQRS разделяет запись и чтение:\n"
            "- **Write Model** — команды, валидация, бизнес-логика, события. Оптимизирован под консистентность.\n"
            "- **Read Model** — денормализованные проекции (Elasticsearch, Redis, материализованные вьюхи). "
            "Оптимизирован под запросы.\n"
            "- Event Handlers обновляют Read Model асинхронно (Eventual Consistency).\n"
            "Полезно, когда чтения >> записей, или сложные отчёты/поиск."
        ),
        heading("Service Mesh (Istio / Linkerd)"),
        heading("Зачем Service Mesh", 3),
        bullets(
            "mTLS между сервисами (автоматически, без изменений кода)",
            "Traffic management: canary, retry, timeout, fault injection",
            "Наблюдаемость: метрики, трейсы, логи — автоматически",
            "Политики авторизации: RBAC, JWT validation на уровне mesh",
        ),
        heading("Istio пример", 3),
        example(
            "yaml",
            """
            # VirtualService для canary
            apiVersion: networking.istio.io/v1beta1
            kind: VirtualService
            metadata:
              name: user-service
            spec:
              hosts: ["user-service"]
              http:
                - route:
                    - destination:
                        host: user-service
                        subset: v1
                      weight: 90
                    - destination:
                        host: user-service
                        subset: v2
                      weight: 10

            ---
            # DestinationRule с mTLS и circuit breaker
            apiVersion: networking.istio.io/v1beta1
            kind: DestinationRule
            metadata:
              name: user-service
            spec:
              host: user-service
              trafficPolicy:
                tls:
                  mode: ISTIO_MUTUAL
                connectionPool:
                  tcp:
                    maxConnections: 100
                  http:
                    h2UpgradePolicy: UPGRADE
                    http1MaxPendingRequests: 100
                    http2MaxRequests: 1000
                outlierDetection:
                  consecutive5xxErrors: 5
                  interval: 30s
                  baseEjectionTime: 30s
            """,
        ),
        text(
            "Service Mesh выносит cross-cutting concerns из кода:\n"
            "- `VirtualService` — маршрутизация трафика (canary 90/10, retry, timeout).\n"
            "- `DestinationRule` — mTLS (`ISTIO_MUTUAL`), connection pool, circuit breaker (outlierDetection).\n"
            "- Sidecar proxy (Envoy) внедряется в каждый под автоматически.\n"
            "Istio — наиболее полный, Linkerd — легче и проще. Для старта — Linkerd."
        ),
        heading("Наблюдаемость (Observability)"),
        heading("Three Pillars", 3),
        bullets(
            "**Metrics** — Prometheus (RED: Rate, Errors, Duration)",
            "**Logs** — Loki / ELK (структурированные JSON)",
            "**Traces** — OpenTelemetry → Jaeger / Tempo",
        ),
        heading("OpenTelemetry в Python", 3),
        example(
            "bash",
            """
            pip install opentelemetry-api opentelemetry-sdk \
                opentelemetry-instrumentation-fastapi \
                opentelemetry-instrumentation-httpx \
                opentelemetry-exporter-otlp
            """,
        ),
        example(
            "python",
            """
            # tracing.py
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

            trace.set_tracer_provider(TracerProvider())
            tracer = trace.get_tracer(__name__)

            otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
            trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

            # Автоинструментация
            FastAPIInstrumentor.instrument_app(app)
            HTTPXClientInstrumentor().instrument()

            # Ручные спаны для бизнес-логики
            async def get_user(user_id: str):
                with tracer.start_as_current_span("get_user") as span:
                    span.set_attribute("user.id", user_id)
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(f"http://user-service/users/{user_id}")
                    return resp.json()
            """,
        ),
        text(
            "OpenTelemetry — стандарт инструментации:\n"
            "- `FastAPIInstrumentor` — авто-спаны для HTTP запросов (входящие).\n"
            "- `HTTPXClientInstrumentor` — авто-спаны для исходящих HTTP/gRPC вызовов.\n"
            "- `OTLPSpanExporter` — экспорт в Jaeger (gRPC 4317), Tempo, Tempo, DataDog.\n"
            "- Ручные спаны (`tracer.start_as_current_span`) для бизнес-операций.\n"
            "- Атрибуты (`span.set_attribute`) для фильтрации в Jaeger UI."
        ),
        heading("Корреляция логов (trace_id)", 3),
        example(
            "python",
            """
            import logging
            from opentelemetry.trace import get_current_span

            class TraceIDFilter(logging.Filter):
                def filter(self, record):
                    span = get_current_span()
                    record.trace_id = f"{span.get_span_context().trace_id:032x}" if span.get_span_context().trace_id else "none"
                    return True

            logging.basicConfig(
                format='{"time": "%(asctime)s", "level": "%(levelname)s", "trace_id": "%(trace_id)s", "msg": "%(message)s"}'
            )
            logger = logging.getLogger()
            logger.addFilter(TraceIDFilter())
            """,
        ),
        text(
            "Trace ID в логах позволяет перейти от метрики/алерта к полному трейсу в Jaeger:\n"
            "- `TraceIDFilter` достаёт trace_id из текущего спана.\n"
            "- JSON логи с `trace_id` поле.\n"
            "- В Loki/Grafana: `{app=\"myapp\"} | trace_id=\"abc123\"` → связанные логи.\n"
            "- В Jaeger: поиск по trace_id → полный flamegraph запроса."
        ),
        heading("Данные в микросервисах"),
        heading("Database per Service", 3),
        bullets(
            "У каждого сервиса своя БД (схема или инстанс)",
            "Никаких прямых JOIN между сервисами",
            "Данные дублируются (Eventual Consistency)",
            "Синхронизация через события (Event-Driven)",
        ),
        heading("Transactional Outbox", 3),
        example(
            "python",
            """
            # Вместо прямой публикации события — пишем в outbox таблицу ТОЙ ЖЕ транзакцией
            async def create_order(order_data):
                async with session.begin():
                    order = Order(...)
                    session.add(order)

                    # Outbox запись в той же транзакции
                    outbox = OutboxEvent(
                        event_type="OrderCreated",
                        payload=json.dumps({"order_id": order.id, ...})
                    )
                    session.add(outbox)

            # Отдельный процесс (relay) читает outbox и публикует в брокер
            async def outbox_relay():
                while True:
                    events = await session.execute(
                        select(OutboxEvent).where(OutboxEvent.published == False).limit(100)
                    )
                    for event in events:
                        await publish_to_broker(event)
                        event.published = True
                    await session.commit()
                    await asyncio.sleep(1)
            """,
        ),
        text(
            "Transactional Outbox решает проблему «или сохраняем в БД, или публикуем событие»:\n"
            "- Событие пишется в таблицу `outbox` **в той же транзакции**, что и бизнес-данные.\n"
            "- Отдельный процесс (relay) читает outbox и публикует в брокер (Kafka/RabbitMQ).\n"
            "- Гарантирует **at-least-once** доставку (relay может упасть после публикации, перед commit).\n"
            "- Потребители должны быть идемпотентны (обрабатывать дубликаты)."
        ),
        heading("Тестирование микросервисов"),
        heading("Contract Testing (Pact)", 3),
        example(
            "bash",
            """
            pip install pact-python
            """,
        ),
        example(
            "python",
            """
            # Consumer test
            from pact import Consumer, Provider

            pact = Consumer("order-service").has_pact_with(Provider("user-service"))

            def test_get_user():
                expected = {"id": "123", "name": "Анна"}
                (pact
                 .given("user 123 exists")
                 .upon_receiving("a request for user 123")
                 .with_request("GET", "/users/123")
                 .will_respond_with(200, body=expected))

                with pact:
                    resp = httpx.get(f"{pact.uri}/users/123")
                    assert resp.json() == expected
            """,
        ),
        text(
            "Contract Testing проверяет совместимость consumer/provider без поднятия провайдера:\n"
            "- Consumer пишет ожидания (given/upon_receiving/will_respond_with).\n"
            "- Pact запускает mock server, проверяет запросы.\n"
            "- Pact файл публикуется в Pact Broker. Provider верифицирует его в своём CI.\n"
            "- Ловит breaking changes до деплоя."
        ),
        heading("Testcontainers для интеграционных тестов", 3),
        example(
            "bash",
            """
            pip install testcontainers
            """,
        ),
        example(
            "python",
            """
            from testcontainers.postgres import PostgresContainer
            from testcontainers.kafka import KafkaContainer

            def test_with_real_postgres():
                with PostgresContainer("postgres:15") as pg:
                    db_url = pg.get_connection_url()
                    # запускаем тесты с реальной БД

            def test_with_real_kafka():
                with KafkaContainer() as kafka:
                    bootstrap = kafka.get_bootstrap_server()
                    # тесты с реальным Kafka
            """,
        ),
        text(
            "Testcontainers поднимает реальные контейнеры (Postgres, Kafka, Redis, Mongo) в тестах:\n"
            "- Никаких моков — настоящие БД/брокеры.\n"
            "- Изолированно: каждый тест/класс — свой контейнер.\n"
            "- Интеграция с pytest: фикстуры `postgres_container`, `kafka_container`."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Последствия", "Как правильно"],
            [
                ["Распределённый монолит (сильные связи)", "Изменение одного ломает другие, каскадные сбои", "Слабая связанность, async коммуникация, четкие границы доменов"],
                ["Синхронные цепочки вызовов (A→B→C)", "Латенция суммируется, один сбой падает все", "Event-driven, Saga для длинных процессов, Circuit Breaker"],
                ["Общая БД между сервисами", "Связность по схеме, невозможно независимо мигрировать", "Database per Service, синхронизация через события"],
                ["Нет contract testing", "Breaking changes в проде", "Pact / схемы в Schema Registry, CI верификация"],
                ["Игнорируют eventual consistency", "Гонки данных, неконсистентное UI", "Проектируют под eventual consistency, компенсации"],
                ["Нет распределённой трассировки", "Отладка часами, черный ящик", "OpenTelemetry везде, trace_id в логах"],
                ["Синхронные HTTP вызовы без timeout", "Зависание всего цепочки", "Всегда timeout, retry, Circuit Breaker"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Для некоторых нужен запущенный кластер (kind/minikube) и брокеры."
        ),
        numbered(
            "Service Template: создайте шаблон микросервиса (FastAPI + Docker + k8s манифесты + CI workflow). "
            "Включите: health/ready эндпоинты, prometheus метрики, OpenTelemetry, структурированные логи.",
            "gRPC: реализуйте UserService с protobuf (GetUser, ListUsers streaming). "
            "Клиент с retry/timeout через grpc.aio. Добавьте Circuit Breaker.",
            "Event-Driven: Order Service публикует `OrderCreated` в Kafka. "
            "Payment/Inventory/Notification сервисы потребляют и реагируют. "
            "Реализуйте Transactional Outbox в Order Service.",
            "Circuit Breaker: добавьте pybreaker к HTTP/gRPC клиентам. Настройте fallback (кэш/дефолт). "
            "Проверьте: убиваете downstream — upstream не падает, возвращает fallback.",
            "Tracing: внедрите OpenTelemetry (авто + ручные спаны). Настройте экспорт в Jaeger (all-in-one). "
            "Добавьте TraceIDFilter в логи. Проверьте: запрос → трейс в Jaeger → логи в Loki по trace_id.",
        ),
        text("Пример ожидаемого результата для первого задания (структура):"),
        example(
            "text",
            """
            microservice-template/
              ├── src/
              │   └── myservice/
              │       ├── main.py          # FastAPI app
              │       ├── tracing.py       # OpenTelemetry setup
              │       ├── metrics.py       # Prometheus metrics
              │       ├── logging.py       # JSON logging + TraceIDFilter
              │       ├── health.py        # /health, /ready
              │       └── config.py        # Pydantic Settings
              ├── Dockerfile
              ├── docker-compose.yml
              ├── k8s/
              │   ├── deployment.yaml
              │   ├── service.yaml
              │   └── hpa.yaml
              ├── .github/workflows/ci.yml
              └── pyproject.toml
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 3",
            "Transactional Outbox: таблица `outbox_event` (id, event_type, payload, created_at, published_at). "
            "В той же транзакции, что создаёт Order, пишем в outbox. "
            "Relay: `asyncio.create_task(outbox_relay())` в lifespan FastAPI. "
            "Идемпотентность: consumer проверяет `event_id` в обработанных (Redis SETNX).",
        ),
        heading("Проверьте себя"),
        numbered(
            "Когда микросервисы оправданы, а когда лучше модульный монолит?",
            "В чём разница между хореографией и оркестрацией в Saga?",
            "Зачем нужен API Gateway и какие функции он выполняет?",
            "Как Circuit Breaker защищает от каскадных сбоев?",
            "Что такое CQRS и какую проблему решает?",
            "Какие три столпа наблюдаемости и инструменты для каждого?",
            "Зачем нужен Transactional Outbox и как он работает?",
        ),
        heading("Ответы", 3),
        numbered(
            "Микросервисы: команда >5, сложный домен, нужны независимые деплои/масштабирование, есть DevOps зрелость. "
            "Модульный монолит: маленькая команда, простой домен, быстрые итерации, нет k8s.",
            "Хореография — сервисы общаются событиями, нет координатора (проще, но сложнее отладка). "
            "Оркестрация — централизованный координатор управляет шагами (понятнее flow, легче мониторинг).",
            "Единая точка входа: роутинг, аутентификация (JWT валидация), rate limiting, "
            "SSL termination, трансформация, агрегация. Снимает cross-cutting concerns с сервисов.",
            "Считает ошибки. После `fail_max` — OPEN (блокирует вызовы, быстрый фейл). "
            "Через `reset_timeout` — HALF-OPEN (пробный запрос). Успех → CLOSED. "
            "Fallback возвращает кэш/дефолт вместо ошибки.",
            "Разделение Write (Commands) и Read (Queries) моделей. Write — консистентность, события. "
            "Read — денормализованные проекции (Elasticsearch/Redis) для быстрых запросов. "
            "Eventual consistency через Event Handlers.",
            "Metrics (Prometheus), Logs (Loki/ELK), Traces (OpenTelemetry → Jaeger/Tempo). "
            "Корреляция через trace_id во всех трёх.",
            "Проблема: транзакция БД + публикация события — две разные системы. Outbox: событие пишется "
            "в таблицу outbox в ТОЙ ЖЕ транзакции. Relay читает outbox и публикует в брокер. "
            "Гарантирует at-least-once. Consumer должен быть идемпотентен.",
        ),
        heading("Итоги"),
        bullets(
            "Микросервисы оправданы при: большой команде, сложном домене, потребности в независимых деплоях. Иначе — модульный монолит.",
            "Коммуникация: синхронная (REST/gRPC) для query/коротких команд, асинхронная (Kafka/RabbitMQ) для событий и длинных процессов.",
            "Паттерны: API Gateway (единая точка входа), Circuit Breaker (pybreaker, защита от каскадов), Saga (хореография/оркестрация для распределённых транзакций), CQRS (разделение read/write).",
            "Service Mesh (Istio/Linkerd): mTLS, traffic management (canary, retry), observability, auth policies — без изменений кода.",
            "Наблюдаемость: Metrics (Prometheus RED), Logs (Loki JSON + trace_id), Traces (OpenTelemetry → Jaeger). Корреляция через trace_id.",
            "Database per Service: изоляция данных, синхронизация через события. Transactional Outbox для надёжной публикации событий.",
            "Тестирование: Contract Testing (Pact) для consumer/provider совместимости, Testcontainers для реальных БД/брокеров в интеграционных тестах.",
            "Типичные ошибки: распределённый монолит, синхронные цепочки, общая БД, нет contract testing, игнорирование eventual consistency, нет трассировки.",
        ),
        heading("Что дальше"),
        text(
            "Микросервисы — архитектурный стиль, требующий зрелости. В следующем уроке разберём "
            "Data Science и ML в Python: pandas, numpy, scikit-learn, обучение моделей, "
            "feature engineering, MLflow для экспериментов, деплой моделей как микросервисов, "
            "мониторинг data drift."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Microservices Patterns — Chris Richardson (microservices.io/patterns)",
            "Building Microservices — Sam Newman",
            "gRPC Python — grpc.io/docs/languages/python/",
            "OpenTelemetry Python — opentelemetry.io/docs/instrumentation/python/",
            "Istio Docs — istio.io/latest/docs/",
            "Pact — docs.pact.io/",
            "Transactional Outbox — microservices.io/patterns/data/transactional-outbox.html",
            "Designing Data-Intensive Applications — Martin Kleppmann (библия распределённых систем)",
        ),
    ],
}