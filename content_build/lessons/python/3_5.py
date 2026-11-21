"""Урок 3.5 курса Python: DevOps и CI/CD."""

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
    "topic_order": 5,
    "name": "3.5. DevOps и CI/CD",
    "slug": "python-3-5-devops-и-cicd",
    "short_description": (
        "Docker для Python (multi-stage), GitHub Actions CI/CD, Kubernetes манифесты "
        "(Deployment, Service, Ingress, HPA), Helm чарты, Prometheus/Grafana мониторинг, "
        "Blue-Green и Canary деплои."
    ),
    "topic_name": "DevOps и CI/CD",
    "topic_description": (
        "Полный цикл доставки Python-приложения: от Docker образа через CI пайплайн "
        "до продакшена в Kubernetes с мониторингом, логированием и стратегиями деплоя."
    ),
    "learning_objectives": [
        "Создавать оптимизированные Docker образы (multi-stage, non-root, .dockerignore)",
        "Настраивать CI/CD в GitHub Actions: тесты, линтеры, coverage, build/push образа",
        "Писать Kubernetes манифесты: Deployment, Service, Ingress, ConfigMap, Secret, HPA",
        "Упаковывать приложение в Helm чарт с values для разных окружений",
        "Интегрировать Prometheus метрики в FastAPI, настраивать Grafana дашборды",
        "Настраивать логирование через Loki/Promtail/Grafana",
        "Понимать стратегии деплоя: RollingUpdate, Blue-Green, Canary (Argo Rollouts)",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "python",
        "docker",
        "kubernetes",
        "helm",
        "github actions",
        "ci/cd",
        "prometheus",
        "grafana",
        "monitoring",
    ],
    "starter_code": code(
        """
        # Базовый Dockerfile для FastAPI
        FROM python:3.11-slim
        WORKDIR /app
        COPY pyproject.toml poetry.lock* ./
        RUN pip install poetry && poetry install --only=main
        COPY src/ ./src/
        CMD ["uvicorn", "myapp.main:app", "--host", "0.0.0.0", "--port", "8000"]
        """
    ),
    "hints": [
        "Используйте python:3.11-slim как базовый образ — меньше размер, меньше уязвимостей.",
        "Multi-stage build: builder ставит зависимости, runtime копирует только site-packages.",
        "Всегда создавайте non-root пользователя (USER appuser).",
        "Health checks в Kubernetes: livenessProbe (/health) и readinessProbe (/ready).",
    ],
    "content": [
        text(
            "Код написан, тесты проходят, безопасность проверена. Теперь нужно доставить "
            "приложение пользователям — быстро, надёжно и повторяемо. DevOps и CI/CD — это "
            "инженерия процесса доставки: от коммита разработчика до работающего продакшена "
            "с мониторингом, алертами и возможностью отката за минуты.\n\n"
            "В этом уроке пройдём полный путь: Docker (контейнеризация) → GitHub Actions "
            "(CI/CD) → Kubernetes (оркестрация) → Helm (управление релизами) → Prometheus/"
            "Grafana (мониторинг) → Loki (логи) → стратегии деплоя (Canary/Blue-Green)."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "писать production-ready Dockerfile: multi-stage, non-root, кэширование слоёв;",
            "настраивать .dockerignore и docker-compose для локальной разработки;",
            "создавать GitHub Actions workflows: CI (тесты, линтеры, coverage) и CD (build/push);",
            "писать Kubernetes манифесты: Deployment, Service, Ingress, ConfigMap, Secret, HPA;",
            "упаковывать манифесты в Helm чарт с values.yaml для dev/staging/prod;",
            "добавлять /metrics эндпоинт (prometheus-client), настраивать Prometheus scrape;",
            "создавать Grafana дашборды: RPS, latency p95/p99, error rate, ресурсы;",
            "настраивать централизованное логирование: Loki + Promtail + Grafana;",
            "понимать стратегии деплоя: RollingUpdate, Blue-Green, Canary (Argo Rollouts);",
        ),
        heading("Docker для Python"),
        heading("Базовый Dockerfile", 3),
        example(
            "dockerfile",
            """
            # Используем slim образ для меньшего размера
            FROM python:3.11-slim

            # Не запускать от root
            RUN useradd --create-home appuser
            WORKDIR /home/appuser

            # Копируем только файлы зависимостей для кэширования слоя
            COPY --chown=appuser:appuser pyproject.toml poetry.lock* ./

            # Устанавливаем poetry и зависимости
            RUN pip install --no-cache-dir poetry && \
                poetry config virtualenvs.create false && \
                poetry install --only=main --no-interaction --no-ansi

            # Копируем код приложения
            COPY --chown=appuser:appuser src/ ./src/

            USER appuser

            EXPOSE 8000

            CMD ["uvicorn", "myapp.main:app", "--host", "0.0.0.0", "--port", "8000"]
            """,
        ),
        text(
            "Ключевые практики:\n"
            "- `python:3.11-slim` — меньше размер, меньше уязвимостей, чем full образ.\n"
            "- `useradd` + `USER appuser` — контейнер не запускается от root (security best practice).\n"
            "- Копируем `pyproject.toml` и `poetry.lock` **отдельно** от кода — Docker кэширует слой "
            "зависимостей. Изменение кода не ломает кэш.\n"
            "- `poetry config virtualenvs.create false` — ставим пакеты в системный Python, "
            "а не в виртуальное окружение (в контейнере это нормально).\n"
            "- `--no-cache-dir` — не сохраняем pip кэш в образе.\n"
            "- `EXPOSE 8000` — документация, сам порт не открывает.\n"
            "- CMD в exec-форме (`[\"uvicorn\", ...]`) — правильная обработка сигналов (SIGTERM)."
        ),
        heading("Multi-stage build (меньший итоговый образ)", 3),
        example(
            "dockerfile",
            """
            # Stage 1: builder
            FROM python:3.11-slim AS builder
            WORKDIR /app
            COPY pyproject.toml poetry.lock* ./
            RUN pip install --no-cache-dir poetry && \
                poetry config virtualenvs.create false && \
                poetry install --only=main --no-interaction --no-ansi

            # Stage 2: runtime
            FROM python:3.11-slim
            RUN useradd --create-home appuser
            WORKDIR /home/appuser

            # Копируем установленные пакеты из builder
            COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
            COPY --from=builder /usr/local/bin /usr/local/bin

            COPY --chown=appuser:appuser src/ ./src/

            USER appuser
            EXPOSE 8000
            CMD ["uvicorn", "myapp.main:app", "--host", "0.0.0.0", "--port", "8000"]
            """,
        ),
        text(
            "Multi-stage разделяет сборку и рантайм:\n"
            "- **Builder** — содержит poetry, компиляторы, заголовки, кэш pip. Может быть крупным.\n"
            "- **Runtime** — только Python, установленные пакеты (`site-packages`, `bin`), код приложения. "
            "Нет poetry, нет компиляторов, нет кэша. Образ в 2-3 раза меньше.\n"
            "- `COPY --from=builder` копирует артефакты из предыдущего этапа."
        ),
        heading(".dockerignore", 3),
        example(
            "text",
            """
            __pycache__
            *.pyc
            .pytest_cache
            .coverage
            htmlcov
            .tox
            .venv
            venv
            .env
            .git
            .gitignore
            README.md
            tests/
            docs/
            *.log
            """,
        ),
        text(
            ".dockerignore критически важен: без него весь проект (включая .git, venv, __pycache__) "
            "попадает в build context, замедляя сборку и увеличивая образ. Всегда исключайте: "
            "виртуальные окружения, кэши, тесты, документацию, логи, .env файлы."
        ),
        heading("docker-compose.yml для разработки", 3),
        example(
            "yaml",
            """
            version: '3.8'

            services:
              app:
                build: .
                ports:
                  - "8000:8000"
                volumes:
                  - ./src:/home/appuser/src  # hot reload
                environment:
                  - DATABASE_URL=postgresql://user:pass@db:5432/app
                  - REDIS_URL=redis://redis:6379/0
                depends_on:
                  - db
                  - redis
                command: uvicorn myapp.main:app --reload --host 0.0.0.0

              db:
                image: postgres:15
                environment:
                  POSTGRES_USER: user
                  POSTGRES_PASSWORD: pass
                  POSTGRES_DB: app
                volumes:
                  - pgdata:/var/lib/postgresql/data
                ports:
                  - "5432:5432"

              redis:
                image: redis:7-alpine
                ports:
                  - "6379:6379"

            volumes:
              pgdata:
            """,
        ),
        text(
            "`docker compose up` поднимает приложение, БД и Redis одной командой. "
            "Volume `./src:/home/appuser/src` даёт hot reload (--reload в uvicorn). "
            "`depends_on` задаёт порядок запуска, но не ждёт готовности — используйте "
            "healthcheck или `wait-for-it.sh` для production-compose."
        ),
        heading("GitHub Actions CI/CD"),
        heading("Базовый CI workflow", 3),
        example(
            "yaml",
            """
            # .github/workflows/ci.yml
            name: CI

            on:
              push:
                branches: [main, develop]
              pull_request:
                branches: [main]

            jobs:
              test:
                runs-on: ubuntu-latest
                services:
                  postgres:
                    image: postgres:15
                    env:
                      POSTGRES_USER: test
                      POSTGRES_PASSWORD: test
                      POSTGRES_DB: test
                    ports: ["5432:5432"]
                    options: >-
                      --health-cmd="pg_isready"
                      --health-interval=10s
                      --health-timeout=5s
                      --health-retries=5

                steps:
                  - uses: actions/checkout@v4

                  - name: Set up Python
                    uses: actions/setup-python@v5
                    with:
                      python-version: "3.11"
                      cache: "pip"

                  - name: Install dependencies
                    run: |
                      pip install poetry
                      poetry config virtualenvs.create false
                      poetry install --with=dev --no-interaction

                  - name: Run linters
                    run: |
                      poetry run ruff check src/
                      poetry run black --check src/
                      poetry run mypy src/

                  - name: Run tests
                    run: |
                      poetry run pytest --cov=src --cov-report=xml --cov-fail-under=80
                    env:
                      DATABASE_URL: postgresql://test:test@localhost:5432/test

                  - name: Upload coverage
                    uses: codecov/codecov-action@v3
                    with:
                      files: ./coverage.xml
            """,
        ),
        text(
            "Структура workflow:\n"
            "- `on: push/pull_request` — триггеры. `services` поднимает PostgreSQL для тестов.\n"
            "- `actions/setup-python@v5` с `cache: pip` — кэширует pip пакеты между запусками.\n"
            "- Линтеры: `ruff` (быстрый линтер), `black --check` (форматирование), `mypy` (типы).\n"
            "- Тесты: `pytest --cov=src --cov-fail-under=80` — минимум 80% покрытия.\n"
            "- `codecov/codecov-action` — загрузка отчёта в Codecov для UI."
        ),
        heading("Build и Push Docker образа", 3),
        example(
            "yaml",
            """
            # .github/workflows/docker.yml
            name: Docker

            on:
              push:
                branches: [main]
                tags: ['v*']
              workflow_dispatch:

            jobs:
              build:
                runs-on: ubuntu-latest
                permissions:
                  contents: read
                  packages: write

                steps:
                  - uses: actions/checkout@v4

                  - name: Set up Docker Buildx
                    uses: docker/setup-buildx-action@v3

                  - name: Login to GHCR
                    uses: docker/login-action@v3
                    with:
                      registry: ghcr.io
                      username: ${{ github.actor }}
                      password: ${{ secrets.GITHUB_TOKEN }}

                  - name: Extract metadata
                    id: meta
                    uses: docker/metadata-action@v5
                    with:
                      images: ghcr.io/${{ github.repository }}
                      tags: |
                        type=ref,event=branch
                        type=semver,pattern={{version}}
                        type=semver,pattern={{major}}.{{minor}}
                        type=sha

                  - name: Build and push
                    uses: docker/build-push-action@v5
                    with:
                      context: .
                      push: true
                      tags: ${{ steps.meta.outputs.tags }}
                      labels: ${{ steps.meta.outputs.labels }}
                      cache-from: type=gha
                      cache-to: type=gha,mode=max
            """,
        ),
        text(
            "CD workflow:\n"
            "- `docker/setup-buildx-action` — включает BuildKit (кэш, multi-platform).\n"
            "- `docker/login-action` — логин в GHCR через `GITHUB_TOKEN` (не нужен PAT).\n"
            "- `docker/metadata-action` — авто-теги: `main` для ветки, `v1.2.3` для тегов, `sha-...` для коммитов.\n"
            "- `docker/build-push-action` — сборка с BuildKit кэшем (`cache-from/type=gha`). "
            "Кэш сохраняется в GitHub Actions cache — последующие сборки мгновенны."
        ),
        heading("Kubernetes — манифесты"),
        heading("Deployment", 3),
        example(
            "yaml",
            """
            # k8s/deployment.yaml
            apiVersion: apps/v1
            kind: Deployment
            metadata:
              name: myapp
              labels:
                app: myapp
            spec:
              replicas: 3
              selector:
                matchLabels:
                  app: myapp
              template:
                metadata:
                  labels:
                    app: myapp
                spec:
                  containers:
                    - name: myapp
                      image: ghcr.io/user/myapp:v1.2.3
                      ports:
                        - containerPort: 8000
                      envFrom:
                        - secretRef:
                            name: myapp-secrets
                        - configMapRef:
                            name: myapp-config
                      resources:
                        requests:
                          memory: "256Mi"
                          cpu: "250m"
                        limits:
                          memory: "512Mi"
                          cpu: "500m"
                      livenessProbe:
                        httpGet:
                          path: /health
                          port: 8000
                        initialDelaySeconds: 30
                        periodSeconds: 10
                      readinessProbe:
                        httpGet:
                          path: /ready
                          port: 8000
                        initialDelaySeconds: 5
                        periodSeconds: 5
            """,
        ),
        text(
            "Deployment управляет ReplicaSet'ами:\n"
            "- `replicas: 3` — желаемое количество подов.\n"
            "- `resources.requests/limits` — **обязательно** для QoS (Guaranteed/Burstable/BestEffort) и планирования.\n"
            "- `livenessProbe` — если падает, k8s перезапускает под. `/health` — быстрая проверка (DB не пингуем).\n"
            "- `readinessProbe` — если падает, под удаляется из Service endpoints. `/ready` — проверка готовности (DB, миграции).\n"
            "- `envFrom` — секреты и конфиг подключаются как переменные окружения."
        ),
        heading("Service", 3),
        example(
            "yaml",
            """
            # k8s/service.yaml
            apiVersion: v1
            kind: Service
            metadata:
              name: myapp
            spec:
              selector:
                app: myapp
              ports:
                - port: 80
                  targetPort: 8000
              type: ClusterIP
            """,
        ),
        text(
            "Service абстрагирует доступ к подам:\n"
            "- `selector: app: myapp` — находит поды с этим лейблом.\n"
            "- `port: 80` — порт сервиса внутри кластера. `targetPort: 8000` — порт контейнера.\n"
            "- `ClusterIP` — внутренний IP, доступен только внутри кластера. Для внешнего — Ingress."
        ),
        heading("Ingress", 3),
        example(
            "yaml",
            """
            # k8s/ingress.yaml
            apiVersion: networking.k8s.io/v1
            kind: Ingress
            metadata:
              name: myapp
              annotations:
                cert-manager.io/cluster-issuer: letsencrypt-prod
                nginx.ingress.kubernetes.io/rate-limit: "100"
            spec:
              tls:
                - hosts:
                    - api.example.com
                  secretName: myapp-tls
              rules:
                - host: api.example.com
                  http:
                    paths:
                      - path: /
                        pathType: Prefix
                        backend:
                          service:
                            name: myapp
                            port:
                              number: 80
            """,
        ),
        text(
            "Ingress — вход в кластер (L7 балансировщик):\n"
            "- `cert-manager.io/cluster-issuer` — авто-выпуск TLS сертификатов Let's Encrypt.\n"
            "- `nginx.ingress.kubernetes.io/rate-limit` — rate limiting на уровне Ingress.\n"
            "- `tls` — секрет с сертификатом (cert-manager создаёт автоматически).\n"
            "- `pathType: Prefix` — матчит все пути, начинающиеся с `/`."
        ),
        heading("ConfigMap и Secret", 3),
        example(
            "yaml",
            """
            # k8s/configmap.yaml
            apiVersion: v1
            kind: ConfigMap
            metadata:
              name: myapp-config
            data:
              LOG_LEVEL: "INFO"
              WORKERS: "4"
            ---
            # k8s/secret.yaml (значения в base64!)
            apiVersion: v1
            kind: Secret
            metadata:
              name: myapp-secrets
            type: Opaque
            stringData:
              DATABASE_URL: "postgresql://user:pass@postgres:5432/app"
              SECRET_KEY: "your-secret-key"
              REDIS_URL: "redis://redis:6379/0"
            """,
        ),
        text(
            "`ConfigMap` — несекретная конфигурация. `Secret` — секреты (в `stringData` пишем "
            "plain text, k8с кодирует в base64 сам). **Никогда не храните секреты в ConfigMap** "
            "и не коммитьте Secret манифесты в git — используйте External Secrets Operator, "
            "Sealed Secrets или Vault Agent Injector."
        ),
        heading("HPA (Horizontal Pod Autoscaler)", 3),
        example(
            "yaml",
            """
            # k8s/hpa.yaml
            apiVersion: autoscaling/v2
            kind: HorizontalPodAutoscaler
            metadata:
              name: myapp
            spec:
              scaleTargetRef:
                apiVersion: apps/v1
                kind: Deployment
                name: myapp
              minReplicas: 3
              maxReplicas: 10
              metrics:
                - type: Resource
                  resource:
                    name: cpu
                    target:
                      type: Utilization
                      averageUtilization: 80
            """,
        ),
        text(
            "HPA автоматически масштабирует реплики:\n"
            "- `minReplicas: 3`, `maxReplicas: 10` — границы.\n"
            "- Метрика CPU: когда среднее использование > 80%, добавляет поды.\n"
            "- Можно добавить custom metrics (RPS, latency, queue length) через Prometheus Adapter."
        ),
        heading("Helm — пакетный менеджер k8s"),
        heading("Структура чарта", 3),
        example(
            "text",
            """
            myapp/
            ├── Chart.yaml
            ├── values.yaml
            ├── templates/
            │   ├── deployment.yaml
            │   ├── service.yaml
            │   ├── ingress.yaml
            │   ├── configmap.yaml
            │   ├── secret.yaml
            │   └── hpa.yaml
            └── charts/
            """,
        ),
        heading("Chart.yaml", 3),
        example(
            "yaml",
            """
            apiVersion: v2
            name: myapp
            description: My Python Application
            version: 1.2.3
            appVersion: "1.2.3"
            keywords:
              - python
              - fastapi
            maintainers:
              - name: Dev Team
                email: dev@example.com
            """,
        ),
        heading("values.yaml", 3),
        example(
            "yaml",
            """
            replicaCount: 3

            image:
              repository: ghcr.io/user/myapp
              tag: "v1.2.3"
              pullPolicy: IfNotPresent

            service:
              type: ClusterIP
              port: 80

            ingress:
              enabled: true
              className: nginx
              hosts:
                - host: api.example.com
                  paths:
                    - path: /
                      pathType: Prefix
              tls:
                - secretName: myapp-tls
                  hosts:
                    - api.example.com

            resources:
              limits:
                cpu: 500m
                memory: 512Mi
              requests:
                cpu: 250m
                memory: 256Mi

            autoscaling:
              enabled: true
              minReplicas: 3
              maxReplicas: 10
              targetCPUUtilizationPercentage: 80

            env:
              - name: LOG_LEVEL
                value: "INFO"
              - name: WORKERS
                value: "4"

            envFromSecrets:
              - name: myapp-secrets
            """,
        ),
        text(
            "Helm чарт — это шаблоны (Go templates) + values. Один чарт, разные values для dev/staging/prod:\n"
            "- `helm install myapp ./myapp -n production --create-namespace`\n"
            "- `helm upgrade myapp ./myapp -n production`\n"
            "- `helm template myapp ./myapp -f values-prod.yaml` — рендерит манифесты без установки."
        ),
        heading("HPA в шаблоне", 3),
        example(
            "yaml",
            """
            # templates/hpa.yaml
            {{- if .Values.autoscaling.enabled }}
            apiVersion: autoscaling/v2
            kind: HorizontalPodAutoscaler
            metadata:
              name: {{ include "myapp.fullname" . }}
            spec:
              scaleTargetRef:
                apiVersion: apps/v1
                kind: Deployment
                name: {{ include "myapp.fullname" . }}
              minReplicas: {{ .Values.autoscaling.minReplicas }}
              maxReplicas: {{ .Values.autoscaling.maxReplicas }}
              metrics:
                - type: Resource
                  resource:
                    name: cpu
                    target:
                      type: Utilization
                      averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
            {{- end }}
            """,
        ),
        heading("Мониторинг и логирование"),
        heading("Prometheus метрики в Python", 3),
        example(
            "bash",
            """
            pip install prometheus-client
            """,
        ),
        example(
            "python",
            """
            # metrics.py
            from prometheus_client import Counter, Histogram, Gauge, generate_latest
            from fastapi import Response
            import time

            REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests',
                                    ['method', 'endpoint', 'status'])
            REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency',
                                        ['method', 'endpoint'])
            ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active connections')

            # Middleware
            @app.middleware("http")
            async def metrics_middleware(request, call_next):
                ACTIVE_CONNECTIONS.inc()
                start = time.perf_counter()
                try:
                    response = await call_next(request)
                    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
                    return response
                finally:
                    REQUEST_LATENCY.labels(request.method, request.url.path).observe(time.perf_counter() - start)
                    ACTIVE_CONNECTIONS.dec()

            @app.get("/metrics")
            def metrics():
                return Response(content=generate_latest(), media_type="text/plain")
            """,
        ),
        text(
            "Типы метрик:\n"
            "- `Counter` — только растёт (requests total, errors total).\n"
            "- `Histogram` — распределение значений (latency, response size). buckets для квантилей.\n"
            "- `Gauge` — текущее значение вверх/вниз (active connections, queue size).\n"
            "- Middleware инкрементирует счётчики и наблюдает за латенси."
        ),
        heading("Prometheus Config", 3),
        example(
            "yaml",
            """
            # prometheus.yml
            global:
              scrape_interval: 15s

            scrape_configs:
              - job_name: 'myapp'
                kubernetes_sd_configs:
                  - role: pod
                relabel_configs:
                  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
                    action: keep
                    regex: true
                  - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
                    action: replace
                    target_label: __metrics_path__
                    regex: (.+)
            """,
        ),
        text(
            "Prometheus использует Service Discovery в k8s:\n"
            "- `kubernetes_sd_configs: role: pod` — находит все поды.\n"
            "- `relabel_configs` — фильтрует поды с аннотацией `prometheus.io/scrape: true` "
            "и берёт путь из `prometheus.io/path`.\n"
            "- Добавьте аннотации в Deployment template:\n"
            "  `prometheus.io/scrape: \"true\"`\n"
            "  `prometheus.io/path: \"/metrics\"`\n"
            "  `prometheus.io/port: \"8000\"`"
        ),
        heading("Grafana Dashboard", 3),
        example(
            "json",
            """
            {
              "title": "MyApp Metrics",
              "panels": [
                {
                  "title": "Request Rate",
                  "type": "graph",
                  "targets": [{"expr": "rate(http_requests_total[5m])"}]
                },
                {
                  "title": "Latency (p95)",
                  "type": "graph",
                  "targets": [{"expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"}]
                },
                {
                  "title": "Error Rate",
                  "type": "graph",
                  "targets": [{"expr": "rate(http_requests_total{status=~\"5..\"}[5m])"}]
                }
              ]
            }
            """,
        ),
        text(
            "Ключевые дашборды (RED method):\n"
            "- **Rate** — `rate(http_requests_total[5m])` запросов в секунду.\n"
            "- **Errors** — `rate(http_requests_total{status=~\"5..\"}[5m])` 5xx ошибок в сек.\n"
            "- **Duration** — `histogram_quantile(0.95, ...)` p95 латенси.\n"
            "Добавьте: CPU/Memory usage, HPA replicas, DB connections, Redis memory."
        ),
        heading("Логирование — Loki + Promtail", 3),
        example(
            "yaml",
            """
            # docker-compose.logging.yml
            version: '3.8'
            services:
              loki:
                image: grafana/loki:2.9
                ports: ["3100:3100"]
                volumes:
                  - ./loki-config.yaml:/etc/loki/local-config.yaml

              promtail:
                image: grafana/promtail:2.9
                volumes:
                  - /var/log:/var/log
                  - ./promtail-config.yaml:/etc/promtail/config.yaml
                depends_on: [loki]

              grafana:
                image: grafana/grafana:10.0
                ports: ["3000:3000"]
                environment:
                  - GF_AUTH_ANONYMOUS_ENABLED=true
                volumes:
                  - ./grafana-dashboards:/etc/grafana/provisioning/dashboards
            """,
        ),
        text(
            "Loki — легковесная альтернатива ELK для логов:\n"
            "- Индексирует только labels (stream selectors), не полный текст — быстрее, дешевле.\n"
            "- Promtail собирает логи с нод/контейнеров, шлёт в Loki.\n"
            "- Grafana query: `{app=\"myapp\"} |= \"error\"` — фильтр по лейблам и тексте.\n"
            "В Python используйте `structlog` или `logging` с JSON formatter, вывод в stdout — "
            "Promtail подхватит из контейнера."
        ),
        heading("Стратегии деплоя"),
        heading("RollingUpdate (по умолчанию)", 3),
        example(
            "yaml",
            """
            # В Deployment spec
            strategy:
              type: RollingUpdate
              rollingUpdate:
                maxSurge: 1        # на 1 под больше
                maxUnavailable: 0  # недоступных 0 (нужно ресурсы для +1)
            """,
        ),
        text(
            "RollingUpdate — стандартная стратегия: создаёт новые поды, ждёт готовности, "
            "удаляет старые. `maxUnavailable: 0` гарантирует, что всегда работает полный комплект "
            "(требует запас ресурсов). `maxSurge: 25%` позволяет временно превысить реплики."
        ),
        heading("Blue-Green Deployment", 3),
        text(
            "Blue-Green: две идентичные среды (blue — текущая, green — новая). "
            "Деплой в green, тесты, переключение трафика (Service selector или Ingress) мгновенно. "
            "Откат — переключение назад за секунды. Требует 2x ресурсы во время деплоя."
        ),
        heading("Canary Deployment (Argo Rollouts)", 3),
        example(
            "yaml",
            """
            # rollout.yaml
            apiVersion: argoproj.io/v1alpha1
            kind: Rollout
            metadata:
              name: myapp
            spec:
              replicas: 10
              strategy:
                canary:
                  steps:
                    - setWeight: 10
                    - pause: {duration: 5m}
                    - setWeight: 30
                    - pause: {duration: 5m}
                    - setWeight: 50
                    - pause: {duration: 10m}
                    - setWeight: 100
                  canaryMetadata:
                    labels:
                      role: canary
                  stableMetadata:
                    labels:
                      role: stable
              selector:
                matchLabels:
                  app: myapp
              template:
                metadata:
                  labels:
                    app: myapp
                spec:
                  containers:
                    - name: myapp
                      image: ghcr.io/user/myapp:v1.2.3
            """,
        ),
        example(
            "bash",
            """
            kubectl argo rollouts set image myapp myapp=ghcr.io/user/myapp:v1.2.4
            kubectl argo rollouts promote myapp
            kubectl argo rollouts abort myapp
            """,
        ),
        text(
            "Canary — постепенное переключение трафика:\n"
            "- `setWeight: 10` — 10% трафика на новую версию, 90% на старую.\n"
            "- `pause: 5m` — время на метрики/алерты. Если ошибок нет — продолжаем.\n"
            "- `promote` — завершает-canary, делает новую версию stable.\n"
            "- `abort` — откат к stable.\n"
            "Argo Rollouts — CRD над Deployment, даёт тонкий контроль. Альтернатива: Flagger, Istio."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Последствия", "Как правильно"],
            [
                ["Запуск контейнера от root", "Повышение привилегий, escape to host", "`USER appuser` в Dockerfile, `runAsNonRoot: true` в Pod spec"],
                ["Нет health checks", "K8s не знает, жив ли под", "livenessProbe (/health) + readinessProbe (/ready)"],
                ["Хардкод секретов в манифестах", "Утечка при коммите, доступ всем", "Secret / External Secrets Operator / Vault Agent"],
                ["Нет resource limits", "OOM Kill, CPU throttling, noisy neighbor", "requests/limits на CPU и память"],
                ["Один реплика в продакшене", "SPOF, downtime при деплое/падении", "Минимум 3, HPA настроен"],
                ["Отсутствие роллбэка", "Плохой деплой = долгое восстановление", "Стратегия деплоя (RollingUpdate/Canary), helm rollback"],
                ["Нет кэша в CI", "Сборка 10-20 мин каждый раз", "docker/build-push-action с cache-from/to=gha"],
                ["Тесты без БД в CI", "Не ловят SQL ошибки", "services: postgres в GitHub Actions"],
                ["Отсутствие алертов", "Падение замечают пользователи", "Prometheus Alertmanager → PagerDuty/Slack/Telegram"],
                ["Логи только в контейнере", "Потеря при рестарте", "Loki/Promtail → Grafana, retention 30д"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Для Kubernetes нужен кластер (kind, minikube, k3d, или cloud)."
        ),
        numbered(
            "Dockerize: создайте multi-stage Dockerfile для FastAPI приложения из уроков 3.1-3.4. "
            "Проверьте: образ < 100MB, non-root пользователь, healthcheck эндпоинты `/health`, `/ready`.",
            "CI Pipeline: настройте GitHub Actions workflow с jobs: lint (ruff, black, mypy), "
            "test (pytest + postgres service + coverage 80%), build/push multi-arch (amd64/arm64) в GHCR.",
            "K8s Deploy: напишите манифесты Deployment, Service, Ingress, ConfigMap, Secret, HPA. "
            "Примените к кластеру (kind/minikube). Проверьте: `kubectl get pods`, `curl` через Ingress.",
            "Helm Chart: упакуйте манифесты в чарт `myapp`. Создайте `values-dev.yaml`, `values-prod.yaml`. "
            "`helm install` в dev namespace, `helm upgrade` с prod values.",
            "Monitoring: добавьте `/metrics` (prometheus-client) в FastAPI. Настройте Prometheus "
            "scrape через аннотации. Импортируйте Grafana дашборд (JSON). Настройте алерт: error rate > 1%.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            "$ docker build -t myapp .\n"
            "$ docker images myapp\n"
            "REPOSITORY   TAG       SIZE\n"
            "myapp        latest    85MB\n\n"
            "$ docker run --rm myapp whoami\n"
            "appuser\n\n"
            "$ curl localhost:8000/health\n"
            "{\"status\":\"ok\"}",
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "Используйте `docker/build-push-action@v5` с `platforms: linux/amd64,linux/arm64` "
            "для multi-arch. Кэш: `cache-from: type=gha`, `cache-to: type=gha,mode=max`. "
            "Для тестов в CI: `services.postgres` с `health-cmd=pg_isready`. "
            "`DATABASE_URL` передавайте через `env` в job.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Зачем нужен multi-stage Docker build?",
            "Какие два health check нужны в Kubernetes и чем отличаются?",
            "Что делает HPA и по какой метрике по умолчанию масштабирует?",
            "В чём разница между ConfigMap и Secret?",
            "Как Helm помогает управлять окружениями (dev/staging/prod)?",
            "Какие три ключевые метрики по методологии RED?",
            "В чём суть Canary deployment и чем отличается от Blue-Green?",
        ),
        heading("Ответы", 3),
        numbered(
            "Разделяет сборку (builder с компиляторами, poetry, кэшем) и рантайм (только Python + пакеты + код). Итоговый образ в 2-3 раза меньше, без инструментов сборки.",
            "livenessProbe — жив ли контейнер (перезапуск при падении). readinessProbe — готов ли принимать трафик (включение в Service endpoints). liveness падает — restart; readiness падает — уход из балансировщика.",
            "HorizontalPodAutoscaler автоматически меняет replicas Deployment. По умолчанию — CPU utilization (averageUtilization). Можно добавить custom metrics (RPS, latency).",
            "ConfigMap — несекретная конфигурация (plain text). Secret — секреты (base64, шифрование в etcd, RBAC). Secret монтируется как файлы или env vars.",
            "Один чарт (templates), разные values.yaml для каждого окружения. `helm install -f values-prod.yaml`. Переопределение: `helm upgrade --set image.tag=v1.2.4`.",
            "Rate (requests/sec), Errors (5xx rate), Duration (latency p95/p99). Rate — нагрузка, Errors — качество, Duration — UX.",
            "Canary: постепенное переключение трафика (10% → 30% → 50% → 100%) с паузами на метрики. Blue-Green: две полные среды, мгновенное переключение. Canary экономнее ресурсы, Blue-Green быстрее откат.",
        ),
        heading("Итоги"),
        bullets(
            "Docker: multi-stage build, non-root user, .dockerignore, кэширование слоёв зависимостей, healthcheck эндпоинты.",
            "GitHub Actions: CI (линтеры, типы, тесты с сервисами, coverage), CD (Buildx, multi-arch, GHCR, кэш).",
            "Kubernetes: Deployment (replicas, resources, probes, envFrom), Service (ClusterIP), Ingress (TLS, rate-limit), ConfigMap/Secret, HPA (CPU/custom metrics).",
            "Helm: чарт = templates + values. Один чарт, разные values для dev/staging/prod. `helm install/upgrade/template`.",
            "Prometheus: Counter/Histogram/Gauge, middleware для RED метрик, `/metrics` эндпоинт, Service Discovery в k8s.",
            "Grafana: дашборды Rate/Errors/Duration (p95), алерты через Alertmanager.",
            "Логи: Loki (labels-based) + Promtail (сбор) + Grafana (query). JSON логи в stdout.",
            "Деплой стратегии: RollingUpdate (по умолчанию), Blue-Green (2x среда, мгновенный switch), Canary (Argo Rollouts, поэтапный вес).",
            "Best practices: resource limits, multi-replica, secrets в Secret/External Secrets, алерты, роллбек за минуту.",
        ),
        heading("Что дальше"),
        text(
            "DevOps цикл закрыт: код → контейнер → CI → кластер → метрики → логи → алерты. "
            "В следующем уроке разберём микросервисы: распределённые системы, сервис-ту-сервис "
            "коммуникация (gRPC, REST, сообщения), Saga pattern, Circuit Breaker, "
            "Event-driven архитектура, API Gateway, Service Mesh (Istio/Linkerd)."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Docker Best Practices — docs.docker.com/develop/develop-images/dockerfile_best-practices/",
            "Kubernetes Docs — kubernetes.io/docs/home/",
            "Helm Docs — helm.sh/docs/",
            "GitHub Actions — docs.github.com/en/actions",
            "Prometheus Python Client — github.com/prometheus/client_python",
            "Argo Rollouts — argoproj.github.io/argo-rollouts/",
            "12 Factor App — 12factor.net/ (must read для cloud-native)",
            "Site Reliability Engineering — sre.google/workbook/table-of-contents/",
        ),
    ],
}