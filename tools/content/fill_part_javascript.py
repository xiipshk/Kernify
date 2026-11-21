# -*- coding: utf-8 -*-
"""Пустые code-блоки: JavaScript."""

from fill_common import apply_fill

FILL = {
    'javascript/20.json': {
        47: r"""
# ✅ Статика с хэшем в имени — кэшируем навсегда
Cache-Control: public, max-age=31536000, immutable

# ✅ HTML — всегда ревалидируем
Cache-Control: no-cache

# ✅ API: свежесть 60 с, затем ревалидация в фоне
Cache-Control: public, max-age=60, stale-while-revalidate=600

# ✅ CDN-кэш + проверка по ETag
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"
""",
    },
    'javascript/28.json': {
        53: r"""
# HTTP/1.1 — каждый ресурс по отдельному TCP-соединению
GET /app.js HTTP/1.1
Host: example.com
Connection: keep-alive

# HTTP/2 — мультиплексирование в одном соединении
:method: GET
:scheme: https
:authority: example.com
:path: /app.js

# HTTP/3 работает поверх QUIC (UDP) — нет head-of-line blocking
# Проверка протокола в DevTools: Protocol = h2 или h3
""",
        57: r"""
# ✅ Сжатие текстовых ресурсов
Accept-Encoding: br, gzip
Content-Encoding: br
Vary: Accept-Encoding

# ✅ Долгий кэш для хэшированных файлов
Cache-Control: public, max-age=31536000, immutable

# ✅ Ревалидация без повторной загрузки тела
If-None-Match: "abc123"
HTTP/1.1 304 Not Modified
""",
    },
    'javascript/29.json': {
        21: r"""
# ✅ SameSite=Lax — cookie не отправляется с cross-site POST
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax; Path=/

# ✅ SameSite=Strict — cookie только для same-site переходов
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict; Path=/

# ⚠️ SameSite=None обязателен для cross-site (требует Secure)
Set-Cookie: tracking=xyz; Secure; SameSite=None; Path=/

# Проверка в браузере: DevTools → Application → Cookies → SameSite
""",
        30: r"""
# Preflight-запрос (для нестандартных методов/заголовков)
OPTIONS /api/data HTTP/1.1
Origin: https://app.example.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type, authorization

# Ответ сервера
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: content-type, authorization
Access-Control-Max-Age: 86400
Access-Control-Allow-Credentials: true
""",
        32: r"""
# ❌ Уязвимо: отражение любого Origin
Access-Control-Allow-Origin: https://evil.com
Access-Control-Allow-Credentials: true

# ❌ Уязвимо: wildcard вместе с credentials (браузер отклонит, но логика опасна)
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true

# ✅ Безопасно: белый список Origin
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
Vary: Origin
""",
        34: r"""
# ✅ Cross-Origin Isolation (нужно для SharedArrayBuffer, high-res timers)
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp

# ✅ Ресурсы, которые разрешено встраивать при COEP
Cross-Origin-Resource-Policy: cross-origin

# Проверка в консоли:
# crossOriginIsolated === true
""",
        55: r"""
# ✅ Запрет встраивания в iframe
X-Frame-Options: DENY
# или разрешить только свой домен
X-Frame-Options: SAMEORIGIN

# ✅ Современный эквивалент через CSP frame-ancestors
Content-Security-Policy: frame-ancestors 'self';

# ✅ Дополнительно: запрет MIME-sniffing
X-Content-Type-Options: nosniff
""",
        63: r"""
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), camera=(), microphone=()
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
Cache-Control: no-store
""",
    },
    'javascript/30.json': {
        35: r"""
name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test -- --coverage
      - run: npm run build
""",
        37: r"""
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/deploy
          aws-region: eu-central-1
      - run: aws s3 sync dist/ s3://my-app-bucket --delete
      - run: aws cloudfront create-invalidation --distribution-id ABCDEF --paths "/*"
""",
        39: r"""
- uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-

- uses: actions/cache@v4
  with:
    path: .turbo
    key: ${{ runner.os }}-turbo-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-turbo-

- name: Build with remote cache
  run: npx turbo run build --cache-dir=.turbo
""",
        48: r"""
# service-level-objectives.yaml
service: checkout-api
slis:
  - name: availability
    metric: sum(rate(http_requests_total{status!~"5.."}[5m]))
      / sum(rate(http_requests_total[5m]))
    objective: 99.9
  - name: latency_p95
    metric: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
    objective: 0.3
window: 30d
error_budget:
  total_minutes: 1296      # 30 дней * 24 ч * 60 мин * 0.1%
  burn_rate_alerts: [14.4, 6, 1]
""",
        50: r"""
groups:
  - name: slo-alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Более 5% запросов завершаются ошибкой"

      - alert: ErrorBudgetBurn
        expr: |
          slo:error_budget_burn_rate{service="checkout-api"} > 14.4
        for: 2m
        labels:
          severity: page
        annotations:
          summary: "Error budget сгорает слишком быстро"
""",
        68: r"""
name: CI with Testcontainers

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run test:integration
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test
""",
    },
    'javascript/31.json': {
        31: r"""
# codegen.yml
schema: ./schema.graphql
documents: ./src/**/*.graphql
generates:
  ./src/generated/graphql.ts:
    plugins:
      - typescript
      - typescript-operations
      - typescript-react-apollo
    config:
      withHooks: true
      avoidOptionals: true
      immutableTypes: true
""",
    },
    'javascript/32.json': {
        21: r"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
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
          image: ghcr.io/example/collab-api:1.0.0
          ports:
            - containerPort: 3000
          envFrom:
            - secretRef:
                name: collab-secrets
          readinessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 5
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 3000
""",
    },
}

if __name__ == '__main__':
    apply_fill(FILL)
