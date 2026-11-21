#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate advanced lessons (29-33) with proper content extraction."""

import json
import re
from pathlib import Path

# Reuse the markdown processing functions
def extract_code_blocks(text):
    code_blocks = []
    placeholders = {}
    
    def protect_code(match):
        idx = len(code_blocks)
        lang = match.group(1) or 'csharp'
        code = match.group(2).rstrip()
        code_blocks.append({'type': 'code', 'language': lang, 'content': code})
        placeholder = f"{{{{CODE_BLOCK_{idx}}}}}"
        placeholders[placeholder] = idx
        return placeholder
    
    text = re.sub(r'```(\w*)\n(.*?)\n```', protect_code, text, flags=re.DOTALL)
    return text, code_blocks, placeholders


def markdown_to_html(text):
    if not text:
        return ""
    
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    text = re.sub(r'^\- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\n\1</ul>', text)
    text = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n)+', r'<ol>\n\1</ol>', text)
    
    def table_repl(match):
        lines = match.group(0).strip().split('\n')
        if len(lines) < 2:
            return match.group(0)
        headers = [h.strip() for h in lines[0].split('|') if h.strip()]
        rows = []
        for line in lines[2:]:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells:
                rows.append(cells)
        html = '<table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead><tbody>'
        for row in rows:
            html += '<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>'
        html += '</tbody></table>'
        return html
    text = re.sub(r'\|.*\|(\n\|[-:]+\|)+\n(\|.*\|\n?)+', table_repl, text)
    
    text = re.sub(r'\n\n+', '</p>\n<p>', text)
    text = '<p>' + text + '</p>'
    text = re.sub(r'<p>\s*</p>', '', text)
    text = re.sub(r'<p>(<h[1-6]>)', r'\1', text)
    text = re.sub(r'</h([1-6])></p>', r'</h\1>', text)
    text = re.sub(r'<p>(<ul>)', r'\1', text)
    text = re.sub(r'</ul></p>', r'</ul>', text)
    text = re.sub(r'<p>(<ol>)', r'\1', text)
    text = re.sub(r'</ol></p>', r'</ol>', text)
    text = re.sub(r'<p>(<table>)', r'\1', text)
    text = re.sub(r'</table></p>', r'</table>', text)
    
    return text


def process_markdown(md):
    text, code_blocks, placeholders = extract_code_blocks(md)
    html = markdown_to_html(text)
    
    for ph, idx in placeholders.items():
        html = html.replace(ph, f"[[CODE_BLOCK_{idx}]]")
    
    blocks = []
    parts = re.split(r'(<h[1-6]>.*?</h[1-6]>|<ul>.*?</ul>|<ol>.*?</ol>|<table>.*?</table>|<p>.*?</p>)', html, flags=re.DOTALL)
    
    def extract_code_markers(part):
        extracted = []
        remaining = part
        while True:
            m = re.search(r'\[\[CODE_BLOCK_(\d+)\]\]', remaining)
            if not m:
                break
            idx = int(m.group(1))
            extracted.append(code_blocks[idx])
            remaining = remaining[:m.start()] + remaining[m.end():]
        return extracted, remaining.strip()
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        code_markers, remaining = extract_code_markers(part)
        for cb in code_markers:
            blocks.append(cb)
        
        if not remaining:
            continue
        
        if remaining.startswith('<h'):
            level = int(remaining[2])
            content = re.sub(r'<h\d>(.*?)</h\d>', r'\1', remaining, flags=re.DOTALL)
            blocks.append({'type': 'heading', 'level': level, 'content': content.strip()})
        elif remaining.startswith('<ul>') or remaining.startswith('<ol>'):
            items = re.findall(r'<li>(.*?)</li>', remaining, flags=re.DOTALL)
            blocks.append({'type': 'list', 'items': [re.sub(r'<[^>]+>', '', i).strip() for i in items], 'ordered': remaining.startswith('<ol>')})
        elif remaining.startswith('<table>'):
            headers = re.findall(r'<th>(.*?)</th>', remaining)
            rows = []
            for tr in re.findall(r'<tr>(.*?)</tr>', remaining, flags=re.DOTALL):
                cells = re.findall(r'<td>(.*?)</td>', tr)
                if cells:
                    rows.append(cells)
            if headers:
                blocks.append({'type': 'table', 'headers': headers, 'rows': rows})
        elif remaining.startswith('<p>'):
            content = re.sub(r'<p>(.*?)</p>', r'\1', remaining, flags=re.DOTALL)
            content = re.sub(r'<[^>]+>', '', content).strip()
            if content:
                blocks.append({'type': 'text', 'content': content})
        elif remaining:
            content = re.sub(r'<[^>]+>', '', remaining).strip()
            if content:
                blocks.append({'type': 'text', 'content': content})
    
    return blocks


def write_lesson(num, data):
    path = f'fixtures/lessons/csharp/{num:02d}.json'
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Written lesson {num:02d}: {data["title"][:60]}...')


# ============================================================
# LESSON 29: Observability (already defined in previous script)
# ============================================================
# We'll reuse the content from the previous script
lesson_29_md = """## 🎯 Что вы узнаете
- Serilog: structured logging, sinks, enrichment, levels
- OpenTelemetry: metrics, traces, logs — единый стандарт
- Prometheus + Grafana: метрики, дашборды, алерты
- Distributed Tracing: Activity, ActivitySource, W3C TraceContext, Jaeger, Zipkin
- Профилирование: dotnet-trace, PerfView, BenchmarkDotNet, dotnet-counters

## 📝 Структурированное логирование — Serilog

### Базовая настройка

```csharp
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
    .MinimumLevel.Override("System", LogEventLevel.Warning)
    .Enrich.FromLogContext()           // свойства из LogContext.PushProperty
    .Enrich.WithProperty("App", "MyApp")
    .Enrich.WithThreadId()
    .Enrich.WithMachineName()
    .Enrich.WithProcessId()
    .Enrich.WithEnvironmentName()
    .WriteTo.Console(
        outputTemplate: "[{Timestamp:HH:mm:ss.fff} {Level:u3}] {Message:lj} {Properties:j}{NewLine}{Exception}")
    .WriteTo.Seq("http://seq:5341")    // UI для поиска/анализа логов
    .WriteTo.File("logs/app-.txt", 
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 30,
        outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{Level:u3}] {Message:lj} {Properties:j}{NewLine}{Exception}")
    .CreateLogger();

builder.Host.UseSerilog();
```

### Структурированные сообщения (ключ к поиску!)

```csharp
// ПЛОХО — строка, нельзя фильтровать
_logger.LogInformation("User 123 placed order 456 for $99.99");

// ХОРОШО — свойства для запросов в Seq/ELK
_logger.LogInformation("User {UserId} placed order {OrderId} for {Amount:C}", 123, 456, 99.99m);

// В Seq можно: UserId == 123 AND Amount > 50
```

### Enrichment — контекст

```csharp
// Добавить свойства к ВСЕМ логам в scope
using (LogContext.PushProperty("CorrelationId", correlationId))
using (LogContext.PushProperty("UserId", userId)) {
    _logger.LogInformation("Processing order"); // автоматически имеет CorrelationId, UserId
}

// Кастомный enricher
public class UserEnricher : ILogEventEnricher {
    private readonly IHttpContextAccessor _httpContext;
    public void Enrich(LogEvent logEvent, ILogEventPropertyFactory factory) {
        if (_httpContext.HttpContext?.User?.Identity?.IsAuthenticated == true) {
            var userId = _httpContext.HttpContext.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (userId != null) logEvent.AddPropertyIfAbsent(factory.CreateProperty("UserId", userId));
        }
    }
}

// Регистрация
.Enrich.With<UserEnricher>()
```

### Destructuring — сериализация объектов

```csharp
// По умолчанию ToString() — неинформативно
_logger.LogInformation("User: {@User}", user); // @ — сериализовать как JSON

// Настройка
.Destructure.ByTransforming<User>(u => new { u.Id, u.Name, u.Email }) // скрыть PasswordHash
.Destructure.AsScalar<CreditCardNumber>() // не разбирать, как есть
```

## 📊 Метрики — OpenTelemetry + Prometheus

### Настройка OpenTelemetry Metrics

```bash
dotnet add package OpenTelemetry.Exporter.Prometheus
dotnet add package OpenTelemetry.Extensions.Hosting
```

```csharp
builder.Services.AddOpenTelemetry()
    .WithMetrics(builder => builder
        .AddRuntimeInstrumentation()           // GC, ThreadPool, JIT метрики
        .AddAspNetCoreInstrumentation()        // HTTP запросы: duration, status codes
        .AddHttpClientInstrumentation()        // исходящие HTTP
        .AddEntityFrameworkCoreInstrumentation() // EF Core queries
        .AddMeter("MyApp.Metrics")             // кастомные метрики
        .AddPrometheusExporter());             // /metrics endpoint
```

### Кастомные метрики

```csharp
public class OrderMetrics {
    private readonly Counter<long> _ordersCreated;
    private readonly Histogram<double> _orderValue;
    private readonly UpDownCounter<long> _activeOrders;
    
    public OrderMetrics(IMeterFactory meterFactory) {
        var meter = meterFactory.Create("MyApp.Metrics");
        _ordersCreated = meter.CreateCounter<long>("orders.created.total", "orders", "Total orders created");
        _orderValue = meter.CreateHistogram<double>("order.value", "USD", "Order value distribution");
        _activeOrders = meter.CreateUpDownCounter<long>("orders.active", "orders", "Currently active orders");
    }
    
    public void OrderCreated(decimal value) {
        _ordersCreated.Add(1);
        _orderValue.Record((double)value);
        _activeOrders.Add(1);
    }
    
    public void OrderCompleted() => _activeOrders.Add(-1);
}
```

### Prometheus + Grafana

```yaml
# docker-compose.yml
prometheus:
  image: prom/prometheus
  volumes: ["./prometheus.yml:/etc/prometheus/prometheus.yml"]
  ports: ["9090:9090"]

grafana:
  image: grafana/grafana
  ports: ["3000:3000"]
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes: ["./grafana/dashboards:/etc/grafana/provisioning/dashboards"]
```

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'myapp'
    static_configs:
      - targets: ['host.docker.internal:5000'] # или k8s service discovery
```

## 🔍 Распределенное трассирование — OpenTelemetry Traces

### Настройка

```bash
dotnet add package OpenTelemetry.Exporter.Jaeger
dotnet add package OpenTelemetry.Exporter.Zipkin
dotnet add package OpenTelemetry.Instrumentation.AspNetCore
dotnet add package OpenTelemetry.Instrumentation.Http
dotnet add package OpenTelemetry.Instrumentation.EntityFrameworkCore
```

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(builder => builder
        .AddAspNetCoreInstrumentation(options => {
            options.Filter = ctx => !ctx.Request.Path.StartsWithSegments("/health");
            options.EnrichWithHttpRequest = (activity, request) => {
                activity.SetTag("http.request.body", GetRequestBody(request));
            };
        })
        .AddHttpClientInstrumentation(options => {
            options.EnrichWithHttpRequestMessage = (activity, request) => {
                activity.SetTag("http.client", request.RequestUri?.Host);
            };
        })
        .AddEntityFrameworkCoreInstrumentation(options => {
            options.SetDbStatementForText = true; // SQL в spans
        })
        .AddSource("MyApp.Activities")           // кастомные ActivitySource
        .AddJaegerExporter(options => {
            options.AgentHost = "jaeger";
            options.AgentPort = 6831;
        })
        .AddZipkinExporter(options => {
            options.Endpoint = new Uri("http://zipkin:9411/api/v2/spans");
        })
        .SetResourceBuilder(ResourceBuilder.CreateDefault()
            .AddService("MyApp")));
```

### ActivitySource — кастомные spans

```csharp
public static class AppActivitySource {
    public static readonly ActivitySource Source = new("MyApp.Activities");
}

public class OrderService {
    public async Task<Order> CreateOrderAsync(CreateOrderDto dto) {
        using var activity = AppActivitySource.Source.StartActivity("CreateOrder", ActivityKind.Internal);
        activity?.SetTag("customer.id", dto.CustomerId);
        activity?.SetTag("items.count", dto.Items.Count);
        
        // baggage — передается через контекст (W3C TraceContext)
        Baggage.Current.SetBaggage("user.id", dto.CustomerId.ToString());
        
        var order = await _repo.CreateAsync(dto);
        
        activity?.SetTag("order.id", order.Id);
        activity?.SetStatus(ActivityStatusCode.Ok);
        return order;
    }
}
```

### Context Propagation — W3C TraceContext

```http
# Заголовки автоматически добавляются/читаются
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
tracestate: vendor=value
baggage: user.id=123,correlation.id=abc
```

### Correlation в логах

```csharp
// Serilog + OpenTelemetry = TraceId/SpanId в логах
.Enrich.WithProperty("TraceId", () => Activity.Current?.TraceId.ToString() ?? "none")
.Enrich.WithProperty("SpanId", () => Activity.Current?.SpanId.ToString() ?? "none")
```

## ⚡ Профилирование и бенчмарки

### dotnet-trace — ETW трассировка

```bash
# Сборка с символами
dotnet publish -c Release -p:DebugType=portable -p:DebugSymbols=true

# Сбор трассировки
dotnet-trace collect --process-id <PID> \
  --providers Microsoft-Windows-DotNETRuntime:4:5 \
  --providers Microsoft-DotNETCore-SampleProfiler:4:5 \
  -o trace.nettrace

# Конвертация для Speedscope (веб-визуализатор)
dotnet-trace convert trace.nettrace --format speedscope
# Открыть в https://speedscope.app
```

### dotnet-counters — real-time метрики

```bash
dotnet-counters monitor --process-id <PID> \
  --counters System.Runtime.GC \
  --counters System.Runtime.Threading \
  --counters Microsoft.AspNetCore.Hosting
```

### BenchmarkDotNet — микробенчмарки

```bash
dotnet add package BenchmarkDotNet
```

```csharp
[MemoryDiagnoser]
[SimpleJob(RuntimeMoniker.Net80)]
public class StringConcatBenchmarks {
    private const int N = 1000;
    
    [Benchmark(Baseline = true)]
    public string StringBuilder() {
        var sb = new StringBuilder();
        for (int i = 0; i < N; i++) sb.Append(i);
        return sb.ToString();
    }
    
    [Benchmark]
    public string StringConcat() {
        string s = "";
        for (int i = 0; i < N; i++) s += i;
        return s;
    }
    
    [Benchmark]
    public string StringInterpolation() {
        string s = "";
        for (int i = 0; i < N; i++) s = $"{s}{i}";
        return s;
    }
}

// Запуск
BenchmarkRunner.Run<StringConcatBenchmarks>();
```

### PerfView — глубокий анализ

- Открытие `.nettrace` / `.etl`
- GC Stats: паузы, поколения, причины
- CPU Stacks: где тратится время (JIT, GC, ваш код)
- Memory: кто аллоцирует, GC Roots
- File I/O, Network, Lock Contention

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Логи не структурированы | Нельзя запрашивать/фильтровать в Seq | Используйте `{Property}` синтаксис, `@` для объектов |
| Отсутствие CorrelationId | Невозможно проследить запрос через сервисы | Добавляйте `TraceId`/`CorrelationId` в LogContext |
| Метрики без лейблов (high cardinality) | Prometheus OOM | Не добавляйте unbounded лейблы (userId, requestId) |
| Трассировка не включена для всех вызовов | Разрывы в trace | Включите instrumentation для HttpClient, EF Core, gRPC |
| Benchmark без `[MemoryDiagnoser]` | Не видно аллокации | Всегда добавляйте MemoryDiagnoser |
| `dotnet-trace` без символов | Нечитаемые стеки | Собирайте с `dotnet publish -c Release -p:DebugType=portable` |

## 🛠 Практика

1. Настройте Serilog: Console + Seq + File (rolling). Добавьте enrichment: ThreadId, MachineName, CorrelationId из Activity.
2. Добавьте OpenTelemetry Metrics: Runtime, AspNetCore, HttpClient, EF Core. Экспорт в Prometheus. Создайте Grafana дашборд.
3. Включите Distributed Tracing: Jaeger/Zipkin экспортер. Добавьте кастомный `ActivitySource` для бизнес-операций.
4. Напишите BenchmarkDotNet тест: сравните `StringBuilder` vs `string.Concat` vs `List<string>.Join`.
5. Профилируйте приложение под нагрузкой: `dotnet-trace collect`, анализ в PerfView / Speedscope.

## 📌 Кратко

- **Serilog** — structured logging, sinks, enrichment, `@` для объектов, LogContext для correlation
- **OpenTelemetry Metrics** — Runtime, AspNetCore, HttpClient, EF Core, custom meters → Prometheus/Grafana
- **Distributed Tracing** — ActivitySource, W3C TraceContext, Jaeger/Zipkin, baggage для propagation
- **Profiling** — dotnet-trace (ETW), dotnet-counters (real-time), BenchmarkDotNet (micro), PerfView (deep)

## 🔗 Ссылки

- Serilog: https://serilog.net/
- OpenTelemetry .NET: https://github.com/open-telemetry/opentelemetry-dotnet
- Prometheus: https://prometheus.io/
- Grafana: https://grafana.com/
- Jaeger: https://www.jaegertracing.io/
- BenchmarkDotNet: https://benchmarkdotnet.org/
- PerfView: https://github.com/microsoft/perfview
"""

# ============================================================
# LESSON 30: Cloud Native
# ============================================================
lesson_30_md = """## 🎯 Что вы узнаете
- Dockerfile оптимизация, multi-stage builds, distroless, non-root, health checks
- Kubernetes манифесты: Deployments, Services, Ingress, ConfigMaps, Secrets, HPA, PDB
- Helm: charts, values, dependencies, релизы
- Kustomize: base/overlays, patches, generators
- Service Mesh: Istio, Linkerd — mTLS, traffic splitting, observability
- CI/CD: GitHub Actions, GitLab CI, ArgoCD, Flux

## 🐳 Docker — оптимальные образы

### Multi-stage Build

```dockerfile
# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Кэшируем restore — копируем сначала csproj
COPY *.sln .
COPY src/*/*.csproj ./src/
RUN dotnet restore

# Копируем остальное и билдим
COPY . .
RUN dotnet publish src/MyApp.Api/MyApp.Api.csproj -c Release -o /app/publish --no-restore

# Stage 2: Runtime (distroless — минимальный, без shell, package manager)
FROM mcr.microsoft.com/dotnet/aspnet:8.0-distroless AS runtime
WORKDIR /app

# Non-root user (UID 65532 в distroless)
USER 65532:65532

COPY --from=build --chown=65532:65532 /app/publish .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["dotnet", "MyApp.Api.dll"]
```

### .dockerignore — критично для скорости

```dockerignore
# Исключаем из контекста сборки
**/bin
**/obj
**/.git
**/.vs
**/.idea
**/*.md
**/Dockerfile*
**/docker-compose*
**/tests
**/TestResults
```

### Layer Caching — порядок важен

```dockerfile
# ПЛОХО — копируем всё, потом restore (инвалидирует кэш при любом изменении кода)
COPY . .
RUN dotnet restore

# ХОРОШО — сначала csproj, restore, потом код
COPY *.sln .
COPY src/*/*.csproj ./src/
RUN dotnet restore
COPY . .
RUN dotnet publish ...
```

### Distroless vs Alpine vs Debian

| Base Image | Размер | Безопасность | Shell | Package Manager |
|---|---|---|---|---|
| `mcr.microsoft.com/dotnet/aspnet:8.0` (Debian) | ~100 MB | Стандарт | bash | apt |
| `mcr.microsoft.com/dotnet/aspnet:8.0-alpine` | ~30 MB | Меньше атакующих поверхностей | sh | apk |
| `mcr.microsoft.com/dotnet/aspnet:8.0-distroless` | ~25 MB | Минимальная (нет shell, нет пакетов) | **нет** | **нет** |

**Рекомендация**: distroless для продакшена (безопасность), alpine если нужен shell для отладки.

## ☸️ Kubernetes — манифесты

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels: { app: myapp }
spec:
  replicas: 3
  selector:
    matchLabels: { app: myapp }
  template:
    metadata:
      labels: { app: myapp }
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 65532
        fsGroup: 65532
      containers:
      - name: myapp
        image: myregistry/myapp:v1.2.3
        ports:
        - containerPort: 8080
          name: http
        envFrom:
        - configMapRef: { name: myapp-config }
        - secretRef: { name: myapp-secrets }
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet: { path: /health/live, port: 8080 }
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet: { path: /health/ready, port: 8080 }
          initialDelaySeconds: 5
          periodSeconds: 5
        startupProbe:
          httpGet: { path: /health/startup, port: 8080 }
          failureThreshold: 30
          periodSeconds: 10
```

### Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  labels: { app: myapp }
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
    name: http
  selector:
    app: myapp
```

### Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts: [myapp.example.com]
    secretName: myapp-tls
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp
            port: { number: 80 }
```

### ConfigMap и Secret

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  ASPNETCORE_ENVIRONMENT: "Production"
  Logging__LogLevel__Default: "Information"
  FeatureFlags__NewUi: "true"

---
# secret.yaml (значения в base64!)
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
type: Opaque
data:
  ConnectionStrings__Default: cG9zdGdyZXNxbDovLz... # base64
  Jwt__Key: c3VwZXItc2VjcmV0LWtleS1taW4tMjU2LWJpdHMh
```

### HPA (Horizontal Pod Autoscaler)

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

### PodDisruptionBudget — доступность при обновлениях

```yaml
# pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 2 # или maxUnavailable: 1
  selector:
    matchLabels:
      app: myapp
```

## ⛵ Helm — пакетный менеджер K8s

### Структура чарта

```
myapp/
├── Chart.yaml          # метаданные
├── values.yaml         # дефолтные значения
├── values-prod.yaml    # прод значения
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── hpa.yaml
    ├── configmap.yaml
    ├── secret.yaml
    └── _helpers.tpl    # хелперы
```

### Chart.yaml

```yaml
apiVersion: v2
name: myapp
description: My Application Helm Chart
type: application
version: 1.2.3
appVersion: "1.2.3"
dependencies:
- name: postgresql
  version: "12.x.x"
  repository: "https://charts.bitnami.com/bitnami"
  condition: postgresql.enabled
```

### Values.yaml

```yaml
replicaCount: 3
image:
  repository: myregistry/myapp
  tag: "1.2.3"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  hosts:
  - host: myapp.example.com
    paths: ["/"]
  tls:
  - secretName: myapp-tls
    hosts: [myapp.example.com]

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
  maxReplicas: 50
  targetCPUUtilizationPercentage: 70

postgresql:
  enabled: true
  auth:
    database: myapp
```

### Команды

```bash
# Установка
helm install myapp ./myapp -n production --create-namespace -f values-prod.yaml

# Обновление
helm upgrade myapp ./myapp -n production -f values-prod.yaml

# Откат
helm rollback myapp 1 -n production

# Шаблонизация (для проверки)
helm template myapp ./myapp -f values-prod.yaml
```

## 🎨 Kustomize — нативный K8s способ

### Структура

```
base/
├── deployment.yaml
├── service.yaml
├── kustomization.yaml
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   └── replica-patch.yaml
    ├── staging/
    │   ├── kustomization.yaml
    │   └── replica-patch.yaml
    └── prod/
        ├── kustomization.yaml
        ├── replica-patch.yaml
        └── resources-patch.yaml
```

### base/kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
commonLabels:
  app: myapp
  managed-by: kustomize
```

### overlays/prod/kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
- ../../base
patches:
- path: replica-patch.yaml
- path: resources-patch.yaml
images:
- name: myregistry/myapp
  newTag: v1.2.3
configMapGenerator:
- name: myapp-config
  behavior: merge
  literals:
  - ASPNETCORE_ENVIRONMENT=Production
  - FeatureFlags__NewUi=true
secretGenerator:
- name: myapp-secrets
  literals:
  - ConnectionStrings__Default=postgresql://...
```

### Применение

```bash
kubectl apply -k overlays/prod
```

## 🕸 Service Mesh — Istio / Linkerd

### Зачем Service Mesh

- **mTLS** — автоматическое шифрование между сервисами
- **Traffic Management** — canary, blue-green, mirroring, retries, timeouts
- **Observability** — автоматические метрики, трассировка, access logs
- **Security** — авторизация, JWT валидация, rate limiting

### Istio — пример

```yaml
# DestinationRule — настройки трафика
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
    loadBalancer:
      simple: LEAST_REQUEST
    tls:
      mode: ISTIO_MUTUAL # mTLS

---
# VirtualService — маршрутизация
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts: [myapp]
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: myapp
        subset: v2
      weight: 100
  - route:
    - destination:
        host: myapp
        subset: v1
      weight: 100

---
# AuthorizationPolicy — RBAC
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: myapp-authz
spec:
  selector:
    matchLabels:
      app: myapp
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

### Linkerd — легкий альтернативный

```bash
# Установка
linkerd install | kubectl apply -f -

# Автоматическое mTLS — просто добавьте аннотацию
kubectl annotate deploy myapp linkerd.io/inject=enabled
```

## 🔄 CI/CD — GitHub Actions, ArgoCD, Flux

### GitHub Actions — Build & Deploy

```yaml
# .github/workflows/ci-cd.yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

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
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=sha,prefix=
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/myapp myapp=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        kubectl rollout status deployment/myapp --timeout=300s
```

### ArgoCD — GitOps Continuous Delivery

```yaml
# Application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myapp-config
    targetRevision: HEAD
    path: overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
    - CreateNamespace=true
    - PrunePropagationPolicy=foreground
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### Flux — альтернативный GitOps

```bash
# Установка
flux bootstrap github \
  --owner=myorg \
  --repository=myapp-config \
  --branch=main \
  --path=clusters/prod \
  --personal
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| `latest` тег в проде | Непредсказуемые деплои, кэш | Всегда конкретные теги: semver, git sha |
| Отсутствие `resources.requests/limits` | OOM Kill, нестабильность, неэффективность | Всегда ставьте requests и limits |
| Отсутствие `liveness/readiness` probes | Kubernetes не знает, жив ли под | Добавляйте health endpoints |
| Запуск от root в контейнере | Безопасность | `USER 65532:65532` в Dockerfile |
| Secrets в Git / Helm values.yaml | Утечка | Sealed Secrets, External Secrets Operator, Vault |
| Отсутствие PDB | Downtime при node drain/update | Добавьте PodDisruptionBudget |
| Неправильный порядок слоев в Dockerfile | Медленные сборки | COPY csproj → restore → COPY . → publish |

## 🛠 Практика

1. Напишите оптимальный multi-stage Dockerfile для ASP.NET Core приложения с distroless базой, non-root пользователем, health check.
2. Создайте K8s манифесты: Deployment, Service, Ingress, ConfigMap, Secret, HPA, PDB.
3. Создайте Helm чарт с зависимостью от PostgreSQL (Bitnami). Настройте values-prod.yaml.
4. Настройте Kustomize: base + overlays для dev/staging/prod с разными replicaCount и ресурсами.
5. Настройте GitHub Actions pipeline: build multi-arch image, push to GHCR, deploy через kubectl/ArgoCD.

## 📌 Кратко

- **Docker**: multi-stage, layer caching (csproj first), distroless, non-root, .dockerignore, health checks
- **K8s**: Deployment, Service, Ingress, ConfigMap/Secret, HPA, VPA, PDB, probes, resources
- **Helm**: charts, values, dependencies, template functions, release management
- **Kustomize**: base/overlays, patches, generators, нативный K8s
- **Service Mesh**: Istio/Linkerd — mTLS, traffic splitting, observability, security policies
- **CI/CD**: GitHub Actions (build/push), ArgoCD/Flux (GitOps), semver tags, security scanning

## 🔗 Ссылки

- Docker Best Practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Kubernetes: https://kubernetes.io/docs/home/
- Helm: https://helm.sh/docs/
- Kustomize: https://kustomize.io/
- Istio: https://istio.io/latest/docs/
- Linkerd: https://linkerd.io/
- ArgoCD: https://argo-cd.readthedocs.io/
- Flux: https://fluxcd.io/
"""

# ============================================================
# LESSON 31: Performance
# ============================================================
lesson_31_md = """## 🎯 Что вы узнаете
- BenchmarkDotNet, профилирование (dotnet-trace, PerfView), Span/Memory, ArrayPool, SIMD, Vector<T>, PGO, NativeAOT
- Писать правильные бенчмарки с BenchmarkDotNet: MemoryDiagnoser, DisassemblyDiagnoser
- Профилировать CPU и память: dotnet-trace, PerfView, dotnet-counters, EventPipe
- Использовать Span/Memory, ArrayPool, Stackalloc для снижения аллокаций
- Применять SIMD: Vector<T>, HardwareIntrinsics (AVX2, SSE), System.Numerics
- Понимать PGO (Profile-Guided Optimization), NativeAOT, Tiered Compilation, ReadyToRun

## 📊 BenchmarkDotNet — наука о измерении

### Базовый бенчмарк

```bash
dotnet add package BenchmarkDotNet
```

```csharp
[MemoryDiagnoser]           // аллокации, GC
[DisassemblyDiagnoser]      // asm код (требует `dotnet build -c Release`)
[SimpleJob(RuntimeMoniker.Net80)]
[SimpleJob(RuntimeMoniker.Net90)] // сравнение версий
public class StringBenchmarks {
    private const int N = 1000;
    
    [Benchmark(Baseline = true)]
    public string StringBuilder() {
        var sb = new StringBuilder();
        for (int i = 0; i < N; i++) sb.Append(i);
        return sb.ToString();
    }
    
    [Benchmark]
    public string StringConcat() {
        string s = "";
        for (int i = 0; i < N; i++) s += i;
        return s;
    }
    
    [Benchmark]
    public string ListJoin() {
        var list = new List<string>(N);
        for (int i = 0; i < N; i++) list.Add(i.ToString());
        return string.Join("", list);
    }
    
    [GlobalSetup]
    public void Setup() { /* инициализация данных */ }
    
    [GlobalCleanup]
    public void Cleanup() { /* очистка */ }
}

// Запуск
BenchmarkRunner.Run<StringBenchmarks>();
```

### Параметризованные бенчмарки

```csharp
[Params(100, 1000, 10000)]
public int N { get; set; }

[Benchmark]
public void Test() { /* использует N */ }
```

### Диагностика

```csharp
[MemoryDiagnoser]           // Gen 0/1/2, Allocated Bytes
[DisassemblyDiagnoser(exportHtml: true, exportDiff: true)] // asm + diff
[ThreadingDiagnoser]        // lock contention
[EventPipeProfiler]         // EventPipe events
[NativeMemoryProfiler]      // нативная память (Windows)
```

### Анализ результатов

```
| Method         | N    | Mean      | Error    | StdDev   | Gen0   | Allocated |
|---------------|------|-----------|----------|----------|--------|-----------|
| StringBuilder | 1000 | 45.2 us   | 0.9 us   | 0.8 us   | 3.5 KB | 14 KB     |
| StringConcat  | 1000 | 1,250 us  | 25 us    | 22 us    | 150 KB | 600 KB    |
| ListJoin      | 1000 | 62.1 us   | 1.2 us   | 1.1 us   | 5.2 KB | 20 KB     |
```

## 🔍 Профилирование — инструменты

### dotnet-trace (ETW)

```bash
# Сборка с символами
dotnet publish -c Release -p:DebugType=portable -p:DebugSymbols=true

# Сбор трассировки
dotnet-trace collect --process-id <PID> \
  --providers Microsoft-Windows-DotNETRuntime:4:5 \
  --providers Microsoft-DotNETCore-SampleProfiler:4:5 \
  -o trace.nettrace

# Конвертация для Speedscope (веб-визуализатор)
dotnet-trace convert trace.nettrace --format speedscope
# Открыть в https://speedscope.app
```

### dotnet-counters (real-time)

```bash
dotnet-counters monitor --process-id <PID> \
  --counters System.Runtime.GC \
  --counters System.Runtime.Threading \
  --counters System.Runtime.Jit \
  --counters Microsoft.AspNetCore.Hosting
```

### PerfView — глубокий анализ

- Открытие `.nettrace` / `.etl`
- **GC Stats**: паузы, поколения, причины GC (Allocation, OutOfMemory, Induced)
- **CPU Stacks**: где тратится время (JIT, GC, ваш код, .NET libs)
- **Memory**: аллокации по типам/стекам, GC Roots
- **File I/O / Network / Lock Contention**

### Sampling vs Instrumentation

| Режим | Накладные расходы | Детализация |
|---|---|---|
| **Sampling** (default) | Низкие (~1-5%) | Статистическая, не видит быстрые методы |
| **Instrumentation** | Высокие | Точное время каждого вызова, счетчики |

```bash
# Instrumentation
dotnet-trace collect -p <PID> --providers Microsoft-DotNETCore-SampleProfiler:4:5:EventStack
```

## 🚀 Span, Memory, ArrayPool — снижение аллокаций

### Span<T> / Memory<T>

```csharp
// Парсинг без аллокаций подстрок
public static bool TryParseInt(ReadOnlySpan<char> span, out int value) {
    value = 0;
    bool negative = false;
    int start = 0;
    
    if (span[0] == '-') { negative = true; start = 1; }
    else if (span[0] == '+') { start = 1; }
    
    for (int i = start; i < span.Length; i++) {
        char c = span[i];
        if (c < '0' || c > '9') return false;
        value = value * 10 + (c - '0');
    }
    
    if (negative) value = -value;
    return true;
}

// Использование
ReadOnlySpan<char> input = "12345".AsSpan();
TryParseInt(input, out int val); // никаких аллокаций!

// Slice без копирования
var slice = input.Slice(1, 3); // "234"
```

### ArrayPool<T> — пулинг массивов

```csharp
// Вместо new byte[100000] в цикле
public async Task ProcessStreamAsync(Stream stream) {
    byte[] buffer = ArrayPool<byte>.Shared.Rent(65536);
    try {
        while (true) {
            int read = await stream.ReadAsync(buffer);
            if (read == 0) break;
            Process(buffer.AsSpan(0, read));
        }
    } finally {
        ArrayPool<byte>.Shared.Return(buffer, clearArray: true);
    }
}

// Для строк — StringBuilder не нужен, используйте ArrayPool<char>
var chars = ArrayPool<char>.Shared.Rent(1024);
// ... заполнение ...
var result = new string(chars, 0, length);
ArrayPool<char>.Shared.Return(chars);
```

### stackalloc — стек для малых буферов

```csharp
// Только для малых размеров (< ~1KB), иначе StackOverflow
public unsafe void ProcessSmall(int count) {
    if (count <= 256) {
        byte* buffer = stackalloc byte[count];
        // заполнение...
        NativeProcess(buffer, count);
    } else {
        byte[] buffer = ArrayPool<byte>.Shared.Rent(count);
        try { fixed (byte* ptr = buffer) NativeProcess(ptr, count); }
        finally { ArrayPool<byte>.Shared.Return(buffer); }
    }
}
```

### Object Pooling — для сложных объектов

```csharp
// Microsoft.Extensions.ObjectPool
public class StringBuilderPool : IPooledObjectPolicy<StringBuilder> {
    public StringBuilder Create() => new StringBuilder(256);
    public bool Return(StringBuilder obj) { obj.Clear(); return true; }
}

// Регистрация
services.AddSingleton<ObjectPool<StringBuilder>>(sp => 
    new DefaultObjectPool<StringBuilder>(new StringBuilderPool(), maximumRetained: 100));

// Использование
public class MyService {
    private readonly ObjectPool<StringBuilder> _pool;
    public MyService(ObjectPool<StringBuilder> pool) => _pool = pool;
    
    public string BuildString() {
        var sb = _pool.Get();
        try {
            sb.Append("data");
            return sb.ToString();
        } finally {
            _pool.Return(sb);
        }
    }
}
```

## ⚡ SIMD — Single Instruction Multiple Data

### Vector<T> — абстракция над SIMD

```csharp
using System.Numerics;

// Сумма массива
public static float SumVector(float[] data) {
    Vector<float> sum = Vector<float>.Zero;
    int i = 0;
    
    // Vector<float>.Count = 8 (AVX2) или 4 (SSE)
    for (; i <= data.Length - Vector<float>.Count; i += Vector<float>.Count) {
        var v = new Vector<float>(data, i);
        sum += v;
    }
    
    // Хвост
    float scalarSum = 0;
    for (; i < data.Length; i++) scalarSum += data[i];
    
    return Vector.Sum(sum) + scalarSum;
}

// Умножение матриц (упрощенно)
public static void Multiply(Vector<float> a, Vector<float> b, Vector<float> result) {
    result = a * b; // поэлементное умножение
}
```

### HardwareIntrinsics — прямой доступ к инструкциям

```csharp
using System.Runtime.Intrinsics;
using System.Runtime.Intrinsics.X86;

// AVX2 — 256-bit регистры (8 x float, 4 x double)
public static float SumAvx2(float[] data) {
    if (!Avx2.IsSupported) return SumVector(data); // fallback
    
    Vector256<float> sum = Vector256<float>.Zero;
    int i = 0;
    for (; i <= data.Length - 8; i += 8) {
        sum = Avx2.Add(sum, Avx2.LoadVector256(data.AsSpan(i)));
    }
    
    // Horizontal add
    var sum128 = Avx.Add(sum.GetLower(), sum.GetUpper());
    sum128 = Avx.Add(sum128, Avx2.Permute(sum128, 0b11101110)); // shuffle
    sum128 = Avx.Add(sum128, Avx.Permute(sum128, 0b01010101));
    return sum128.GetElement(0);
}

// SSE — 128-bit (4 x float)
public static float SumSse(float[] data) {
    if (!Sse.IsSupported) return SumScalar(data);
    // аналогично...
}
```

### Arm64 AdvSimd (NEON)

```csharp
using System.Runtime.Intrinsics.Arm;

public static float SumNeon(float[] data) {
    if (!AdvSimd.IsSupported) return SumScalar(data);
    // Vector128<float> = 4 float
    Vector128<float> sum = Vector128<float>.Zero;
    for (int i = 0; i <= data.Length - 4; i += 4) {
        sum = AdvSimd.Add(sum, AdvSimd.LoadVector128(data.AsSpan(i)));
    }
    // horizontal add...
}
```

### System.Numerics — математика для SIMD

```csharp
using System.Numerics;

Vector3 a = new(1, 2, 3);
Vector3 b = new(4, 5, 6);
Vector3 c = a + b;           // (5, 7, 9)
Vector3 d = a * b;           // (4, 10, 18)
float dot = Vector3.Dot(a, b); // 32
Vector3 cross = Vector3.Cross(a, b);
float len = a.Length();
```

## 🎯 Продвинутые оптимизации

### PGO — Profile-Guided Optimization (.NET 8+)

```xml
<!-- Dynamic PGO (рекомендуется) -->
<PropertyGroup>
  <TieredCompilation>true</TieredCompilation>
  <TieredPGO>true</TieredPGO>
</PropertyGroup>

<!-- Static PGO — требует профилирования -->
<!-- 1. dotnet build -c Release /p:OptimizePGOInstrument=true -->
<!-- 2. Запуск приложения под нагрузкой -->
<!-- 3. dotnet build -c Release /p:OptimizePGOTrain=true -->
```

### NativeAOT — нативный бинарь

```xml
<PropertyGroup>
  <PublishAot>true</PublishAot>
  <StripSymbols>true</StripSymbols>
  <IlcGenerateStackTraceData>false</IlcGenerateStackTraceData>
  <IlcOptimizationPreference>Speed</IlcOptimizationPreference>
</PropertyGroup>

# Публикация
dotnet publish -c Release -r linux-x64 --self-contained true
```
**Ограничения**: нет рефлексии, нет динамической загрузки сборок, нет JIT, больше бинарь.

### ReadyToRun (Crossgen2)

```xml
<PropertyGroup>
  <PublishReadyToRun>true</PublishReadyToRun>
  <PublishReadyToRunComposite>true</PublishReadyToRunComposite> # composite images
</PropertyGroup>
```
**Плюсы**: быстрее старт, меньше JIT. **Минусы**: больше размер, не все сборки совместимы.

### Tiered Compilation

```xml
<PropertyGroup>
  <TieredCompilation>true</TieredCompilation>
  <TieredPGO>true</TieredPGO> <!-- Dynamic PGO -->
</PropertyGroup>
```
- Tier 0: быстрая компиляция без оптимизаций
- Tier 1: оптимизированная для горячих методов
- OSR: замена метода на лету

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Бенчмарк без `[MemoryDiagnoser]` | Не видно аллокации/GC | Всегда добавляйте |
| `DateTime.Now` в бенчмарке | Низкое разрешение, системные вызовы | Используйте `Stopwatch` |
| JIT не прогрет | Первые итерации медленные | `[GlobalSetup]` с прогревом, `IterationSetup` |
| Dead code elimination | JIT выкидывает неиспользуемый код | `return` результат, `GC.KeepAlive` |
| SIMD без fallback | Падение на старых CPU | Проверяйте `Avx2.IsSupported`, `Sse.IsSupported` |
| `stackalloc` большого буфера | StackOverflow | Только < 1KB, иначе `ArrayPool` |
| PGO без нагрузочного теста | Профиль нерепрезентативен | Запускайте реальные сценарии |

## 🛠 Практика

1. Напишите BenchmarkDotNet тест: сравните `List<T>.Add` vs `ArrayPool` + `List<T>` с заранее выделенным массивом.
2. Профилируйте приложение под нагрузкой: `dotnet-trace collect`, найдите топ-5 горячих методов в PerfView/Speedscope.
3. Оптимизируйте парсинг CSV: замените `string.Split` на `Span<char>` парсинг без аллокаций.
4. Реализуйте сумму массива через `Vector<T>` и `Avx2` с fallback на скалярный код.
5. Настройте Dynamic PGO: `<TieredPGO>true</TieredPGO>`. Сравните производительность до/после.

## 📌 Кратко

- **BenchmarkDotNet**: MemoryDiagnoser, DisassemblyDiagnoser, Params, Baseline, правильный анализ результатов
- **Профилирование**: dotnet-trace (ETW), PerfView (deep), dotnet-counters (real-time), Speedscope (визуализация)
- **Низкие аллокации**: Span/Memory, ArrayPool, stackalloc (<1KB), ObjectPool
- **SIMD**: Vector<T> (переносимо), HardwareIntrinsics (AVX2/SSE/NEON), System.Numerics
- **Продвинутые**: Dynamic PGO, NativeAOT, ReadyToRun, Tiered Compilation

## 🔗 Ссылки

- BenchmarkDotNet: https://benchmarkdotnet.org/
- Span/Memory: https://learn.microsoft.com/dotnet/standard/memory-and-spans/
- SIMD: https://learn.microsoft.com/dotnet/api/system.runtime.intrinsics
- PGO: https://learn.microsoft.com/dotnet/core/deploying/profile-guided-optimization
- NativeAOT: https://learn.microsoft.com/dotnet/core/deploying/native-aot/
- PerfView: https://github.com/microsoft/perfview
"""

# ============================================================
# LESSON 32: Advanced Patterns
# ============================================================
lesson_32_md = """## 🎯 Что вы узнаете
- Functional C#: Result, Option, Railway-oriented, Rx.NET: IObservable, operators, schedulers, Akka.NET/Orleans actors
- Functional C#: `Result<T>`, `Option<T>`, `Either<L,R>`, Railway-oriented programming
- Rx.NET (Reactive Extensions): `IObservable<T>`, операторы, schedulers, backpressure
- Actor Model: Akka.NET и Orleans — actors, persistence, clustering
- Продвинутые паттерны: Circuit Breaker, Retry, Bulkhead, Saga, Event Sourcing

## 🧮 Функциональный C# — Result, Option, Railway

### Option<T> — отсутствие значения вместо null

```csharp
// Реализация (или используйте LanguageExt, OneOf, Functional.Maybe)
public readonly struct Option<T> {
    private readonly T _value;
    private readonly bool _hasValue;
    
    private Option(T value) { _value = value; _hasValue = true; }
    public static Option<T> Some(T value) => new(value);
    public static Option<T> None => default;
    
    public bool IsSome => _hasValue;
    public bool IsNone => !_hasValue;
    
    public T Value => _hasValue ? _value : throw new InvalidOperationException("Option is None");
    public T ValueOrDefault() => _hasValue ? _value : default!;
    public T ValueOr(T defaultValue) => _hasValue ? _value : defaultValue;
    
    // Map — трансформация если есть значение
    public Option<TResult> Map<TResult>(Func<T, TResult> mapper) 
        => _hasValue ? Option<TResult>.Some(mapper(_value)) : Option<TResult>.None;
    
    // Bind / FlatMap — цепочка Option
    public Option<TResult> Bind<TResult>(Func<T, Option<TResult>> binder)
        => _hasValue ? binder(_value) : Option<TResult>.None;
    
    // Match — pattern matching
    public TResult Match<TResult>(Func<T, TResult> some, Func<TResult> none)
        => _hasValue ? some(_value) : none();
}

// Использование
Option<User> FindUser(int id) => id > 0 ? Option<User>.Some(new User(id)) : Option<User>.None;

var name = FindUser(1)
    .Map(u => u.Name)
    .Bind(n => n.Length > 3 ? Option<string>.Some(n.ToUpper()) : Option<string>.None)
    .ValueOrDefault("UNKNOWN");
```

### Result<T> — успех или ошибка

```csharp
public readonly struct Result<T> {
    private readonly T _value;
    private readonly Error _error;
    private readonly bool _isSuccess;
    
    private Result(T value) { _value = value; _isSuccess = true; }
    private Result(Error error) { _error = error; _isSuccess = false; }
    
    public static Result<T> Success(T value) => new(value);
    public static Result<T> Failure(Error error) => new(error);
    
    public bool IsSuccess => _isSuccess;
    public bool IsFailure => !_isSuccess;
    public T Value => _isSuccess ? _value : throw new InvalidOperationException();
    public Error Error => !_isSuccess ? _error : throw new InvalidOperationException();
    
    public Result<TResult> Map<TResult>(Func<T, TResult> mapper)
        => _isSuccess ? Result<TResult>.Success(mapper(_value)) : Result<TResult>.Failure(_error);
    
    public Result<TResult> Bind<TResult>(Func<T, Result<TResult>> binder)
        => _isSuccess ? binder(_value) : Result<TResult>.Failure(_error);
    
    public TResult Match<TResult>(Func<T, TResult> success, Func<Error, TResult> failure)
        => _isSuccess ? success(_value) : failure(_error);
}

public readonly record struct Error(string Code, string Message);
```

### Railway-oriented programming — цепочка без исключений

```csharp
// Вместо try/catch — цепочка Result
public Result<Order> PlaceOrder(PlaceOrderCommand cmd) =>
    ValidateCommand(cmd)
    .Bind(CheckInventory)
    .Bind(ReserveItems)
    .Bind(CalculateTotal)
    .Bind(ProcessPayment)
    .Bind(CreateOrder)
    .Bind(SendConfirmation);

// Каждый шаг: Result<T> -> Result<U>
private Result<ValidatedCommand> ValidateCommand(PlaceOrderCommand cmd) {
    if (cmd.Items.Count == 0) return Result<ValidatedCommand>.Failure(new Error("EMPTY_ORDER", "Order must have items"));
    if (cmd.CustomerId <= 0) return Result<ValidatedCommand>.Failure(new Error("INVALID_CUSTOMER", "Invalid customer"));
    return Result<ValidatedCommand>.Success(new ValidatedCommand(cmd));
}

private Result<InventoryCheck> CheckInventory(ValidatedCommand cmd) {
    // ...
}
```

### LanguageExt — библиотека для функционального C#

```bash
dotnet add package LanguageExt.Core
```

```csharp
using LanguageExt;
using static LanguageExt.Prelude;

// Option
Option<int> some = Some(42);
Option<int> none = None;
var result = some.Map(x => x * 2).Bind(x => x > 50 ? Some(x) : None);

// Either<L, R> — Left (error) / Right (success)
Either<Error, User> GetUser(int id) => id > 0 
    ? Right(new User(id)) 
    : Left(Error.New("NOT_FOUND", "User not found"));

// Try — безопасное выполнение
Try<Option<User>> tryGet = () => _repo.GetByIdAsync(id);
var user = await tryGet.Match(
    Succ: u => u,
    Fail: ex => None
);
```

## 🔄 Rx.NET — Reactive Extensions

### IObservable<T> — push-базированные последовательности

```bash
dotnet add package System.Reactive
dotnet add package System.Reactive.Linq
```

```csharp
// Создание Observable
var observable = Observable.Create<int>(observer => {
    for (int i = 0; i < 10; i++) {
        observer.OnNext(i);
        Thread.Sleep(100);
    }
    observer.OnCompleted();
    return Disposable.Empty;
});

// Подписка
var subscription = observable.Subscribe(
    onNext: x => Console.WriteLine($"Received: {x}"),
    onError: ex => Console.Error.WriteLine($"Error: {ex}"),
    onCompleted: () => Console.WriteLine("Done")
);

// Отмена подписки
subscription.Dispose();
```

### Основные операторы

```csharp
// Трансформация
source.Select(x => x * 2)
source.SelectMany(x => Observable.Range(0, x)) // flatten

// Фильтрация
source.Where(x => x % 2 == 0)
source.OfType<string>()
source.Distinct()
source.DistinctUntilChanged()

// Комбинирование
Observable.Merge(source1, source2)           // объединение
Observable.Concat(source1, source2)          // последовательно
Observable.Zip(source1, source2, (a, b) => a + b) // попарно
Observable.CombineLatest(source1, source2, (a, b) => a + b) // последние значения
Observable.Amb(source1, source2)             // первый emit

// Временные
source.Throttle(TimeSpan.FromMilliseconds(300))  // debounce
source.Sample(TimeSpan.FromSeconds(1))           // последнее за период
source.Buffer(TimeSpan.FromSeconds(5))           // батчинг
source.Window(TimeSpan.FromSeconds(10))          // окна

// Обработка ошибок
source.Catch(Observable.Return(defaultValue))    // fallback
source.Retry(3)                                  // повторить 3 раза
source.RetryWhen(errors => errors.DelaySubscription(TimeSpan.FromSeconds(1)))
source.OnErrorResumeNext(fallbackObservable)     // продолжить с другого
```

### Schedulers — управление потоками

```csharp
// ThreadPool (default для подписок)
Observable.Start(() => HeavyCompute(), Scheduler.Default)

// UI Thread (WPF/WinForms/MAUI)
Observable.Start(() => HeavyCompute())
    .ObserveOnDispatcher() // или ObserveOn(SynchronizationContextScheduler.Current)

// Новый поток
Observable.Start(() => HeavyCompute(), Scheduler.NewThread)

// TaskPoolScheduler — для async
Observable.FromAsync(async () => await FetchAsync())
    .SubscribeOn(TaskPoolScheduler.Default);
```

### Backpressure — контроль скорости

```csharp
// Producer быстрее Consumer — буферизация/отбрасывание
var fastProducer = Observable.Interval(TimeSpan.FromMilliseconds(10));
var slowConsumer = fastProducer
    .Buffer(TimeSpan.FromSeconds(1)) // батчинг
    .Select(batch => batch.Average())
    .ObserveOn(TaskPoolScheduler.Default) // обработка в пуле
    .Subscribe(avg => Process(avg));

// Или Reactive Streams (IAsyncEnumerable) для нативного backpressure
```

## 🎭 Actor Model — Akka.NET и Orleans

### Akka.NET — классическая модель акторов

```bash
dotnet add package Akka
dotnet add package Akka.Hosting
dotnet add package Akka.Persistence.SqlServer
```

```csharp
// Actor
public class OrderActor : ReceiveActor {
    private OrderState _state = new();
    
    public OrderActor() {
        Command<PlaceOrder>(cmd => Handle(cmd));
        Command<GetOrder>(cmd => Sender.Tell(_state));
        
        // Persistence
        Recover<OrderPlaced>(e => _state = _state.Apply(e));
    }
    
    private void Handle(PlaceOrder cmd) {
        if (_state.Status != OrderStatus.Draft) {
            Sender.Tell(new OrderRejected("Invalid state"));
            return;
        }
        
        var evt = new OrderPlaced(cmd.OrderId, cmd.Items, DateTime.UtcNow);
        Persist(evt, e => {
            _state = _state.Apply(e);
            Sender.Tell(new OrderConfirmed(cmd.OrderId));
        });
    }
}

// Actor System
var system = ActorSystem.Create("OrderSystem");
var orderActor = system.ActorOf(Props.Create(() => new OrderActor()), "order-1");

// Использование
orderActor.Tell(new PlaceOrder(orderId, items));
var response = await orderActor.Ask<OrderConfirmed>(TimeSpan.FromSeconds(5));
```

### Supervision — отказоустойчивость

```csharp
protected override SupervisorStrategy SupervisorStrategy()
    => new OneForOneStrategy(
        maxNrOfRetries: 3,
        withinTimeRange: TimeSpan.FromMinutes(1),
        localOnlyDecider: ex => ex switch {
            SqlException => Directive.Restart,
            ArgumentException => Directive.Stop,
            _ => Directive.Escalate
        });
```

### Orleans — Virtual Actors (Grains)

```bash
dotnet add package Microsoft.Orleans.Core
dotnet add package Microsoft.Orleans.Persistence.AdoNet
dotnet add package Microsoft.Orleans.Clustering.AdoNet
```

```csharp
// Grain Interface
public interface IOrderGrain : IGrainWithIntegerKey {
    Task<OrderResult> PlaceOrder(PlaceOrderCommand cmd);
    Task<OrderState> GetOrder();
}

// Grain Implementation
public class OrderGrain : Grain, IOrderGrain {
    private readonly IPersistentState<OrderState> _state;
    
    public OrderGrain([PersistentState("order", "storage")] IPersistentState<OrderState> state) {
        _state = state;
    }
    
    public async Task<OrderResult> PlaceOrder(PlaceOrderCommand cmd) {
        if (_state.State.Status != OrderStatus.Draft)
            return OrderResult.Failed("Invalid state");
        
        _state.State = _state.State.Apply(new OrderPlaced(cmd.OrderId, cmd.Items));
        await _state.WriteStateAsync();
        return OrderResult.Success(cmd.OrderId);
    }
    
    public Task<OrderState> GetOrder() => Task.FromResult(_state.State);
}

// Client
var client = new ClientBuilder()
    .UseLocalhostClustering()
    .AddAdoNetGrainStorage("storage", opts => opts.ConnectionString = connStr)
    .Build();
await client.Connect();

var grain = client.GetGrain<IOrderGrain>(orderId);
var result = await grain.PlaceOrder(cmd);
```

### Orleans — Clustering, Streams, Reminders

```csharp
// Stream — для event-driven
public interface IOrderEvents : IGrainWithIntegerKey {
    Task Subscribe(IAsyncObserver<OrderEvent> observer);
}

// Reminder — надежные таймеры (выживают перезапускам)
public class OrderGrain : Grain, IOrderGrain {
    public async Task SetReminder(string name, TimeSpan dueTime) {
        await RegisterOrUpdateReminder(name, dueTime, TimeSpan.Zero);
    }
    
    public Task ReceiveReminder(string name, TickStatus status) {
        // обработка
        return Task.CompletedTask;
    }
}
```

## 🔄 Продвинутые паттерны

### Circuit Breaker

```csharp
public class CircuitBreaker {
    private int _failures;
    private DateTime _lastFailure;
    private CircuitState _state = CircuitState.Closed;
    private readonly int _threshold;
    private readonly TimeSpan _timeout;
    
    public async Task<T> ExecuteAsync<T>(Func<Task<T>> action) {
        if (_state == CircuitState.Open) {
            if (DateTime.UtcNow - _lastFailure > _timeout) _state = CircuitState.HalfOpen;
            else throw new CircuitBreakerOpenException();
        }
        
        try {
            var result = await action();
            OnSuccess();
            return result;
        } catch {
            OnFailure();
            throw;
        }
    }
    
    private void OnSuccess() {
        _failures = 0;
        _state = CircuitState.Closed;
    }
    
    private void OnFailure() {
        _failures++;
        _lastFailure = DateTime.UtcNow;
        if (_failures >= _threshold) _state = CircuitState.Open;
    }
}
```

### Saga — распределенная транзакция

```csharp
public class OrderSaga {
    private readonly IServiceProvider _services;
    
    public async Task ExecuteAsync(CreateOrderSagaData data) {
        var steps = new List<Func<Task>>();
        var compensations = new Stack<Func<Task>>();
        
        try {
            // Step 1: Reserve Inventory
            await _inventory.ReserveAsync(data.Items);
            compensations.Push(() => _inventory.ReleaseAsync(data.Items));
            
            // Step 2: Charge Payment
            await _payment.ChargeAsync(data.PaymentInfo);
            compensations.Push(() => _payment.RefundAsync(data.PaymentInfo));
            
            // Step 3: Create Order
            var order = await _order.CreateAsync(data);
            compensations.Push(() => _order.CancelAsync(order.Id));
            
            // Step 4: Send Notification
            await _notification.SendAsync(data.CustomerId, "Order created");
        } catch {
            // Compensate in reverse order
            while (compensations.Count > 0) {
                try { await compensations.Pop()(); } catch { /* log */ }
            }
            throw;
        }
    }
}
```

### Event Sourcing — события как источник истины

```csharp
// Aggregate
public class Account : EventSourcedAggregate {
    public decimal Balance { get; private set; }
    public bool IsClosed { get; private set; }
    
    public void Deposit(decimal amount) {
        if (IsClosed) throw new InvalidOperationException("Closed");
        Apply(new MoneyDeposited(Id, amount));
    }
    
    public void Withdraw(decimal amount) {
        if (Balance < amount) throw new InvalidOperationException("Insufficient funds");
        Apply(new MoneyWithdrawn(Id, amount));
    }
    
    protected override void When(object @event) {
        switch (@event) {
            case MoneyDeposited e: Balance += e.Amount; break;
            case MoneyWithdrawn e: Balance -= e.Amount; break;
            case AccountClosed e: IsClosed = true; break;
        }
    }
}

// Event Store
public interface IEventStore {
    Task AppendAsync(AggregateId id, IEnumerable<IDomainEvent> events, int expectedVersion);
    Task<IReadOnlyList<IDomainEvent>> GetEventsAsync(AggregateId id);
}

// Projection (Read Model)
public class AccountBalanceProjection : 
    IEventHandler<MoneyDeposited>, 
    IEventHandler<MoneyWithdrawn> {
    
    private readonly IReadModelRepository<AccountBalanceView> _repo;
    
    public async Task Handle(MoneyDeposited @event, CancellationToken ct) {
        var view = await _repo.GetAsync(@event.AccountId) ?? new AccountBalanceView(@event.AccountId);
        view.Balance += @event.Amount;
        await _repo.SaveAsync(view, ct);
    }
}
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Исключения для управления потоком | Медленно, трудно отлаживать | `Result<T>`, `Option<T>`, Railway-oriented |
| `Subscribe` без `Dispose` | Утечки памяти, лишние подписки | Всегда `using subscription = obs.Subscribe(...)` |
| Blocking в Rx (`Wait`, `FirstAsync().Wait()`) | Deadlock, потеря reactivity | Используйте `await observable.FirstAsync()` |
| Акторы с блокирующим кодом | Забивают dispatcher | `PipeTo`, `Ask`, асинхронные методы в акторах |
| Orleans Grain делает много работы | Один grain = single-threaded | Декомпозиция на гранулярные grains |
| Saga без идемпотентности | Повторные ретраи = дубликаты | Все шаги идемпотентны (проверка по correlationId) |

## 🛠 Практика

1. Реализуйте `Result<T>` и `Option<T>` с `Map`, `Bind`, `Match`. Напишите валидацию заказа в railway-стиле.
2. Создайте Rx.NET pipeline: генерация чисел → фильтрация чётных → батчинг по 5 → вывод среднего каждую секунду.
3. Напишите Akka.NET актор для управления состоянием заказа с Persistence (Event Sourcing).
4. Создайте Orleans Grain для корзины покупок с персистентным состоянием и reminders для abandoned cart.
5. Реализуйте Circuit Breaker и Saga для распределенного заказа (Inventory → Payment → Notification).

## 📌 Кратко

- **Functional C#**: `Result<T>`, `Option<T>`, `Either<L,R>`, Railway-oriented — нет исключений, композиция
- **Rx.NET**: `IObservable<T>`, операторы (Select, Where, Merge, CombineLatest, Throttle), Schedulers, Backpressure
- **Akka.NET**: Actors, Supervision, Persistence, Clustering — классическая модель акторов
- **Orleans**: Virtual Actors (Grains), Persistence, Streams, Reminders, Clustering — проще, масштабируемее
- **Patterns**: Circuit Breaker, Retry, Bulkhead, Saga, Event Sourcing — надежность в распределенных системах

## 🔗 Ссылки

- LanguageExt: https://github.com/louthy/language-ext
- Rx.NET: https://github.com/dotnet/reactive
- Akka.NET: https://getakka.net/
- Orleans: https://dotnet.github.io/orleans/
- Enterprise Integration Patterns: https://www.enterpriseintegrationpatterns.com/
"""

# ============================================================
# LESSON 33: Final Project
# ============================================================
lesson_33_md = """## 🎯 Финальный проект: Task Manager Full Stack

Мы соберем всё изученное в одно приложение: **Task Manager** — управление задачами с real-time обновлениями.

### Архитектура решения

```
src/
├── TaskManager.Domain/          # Domain Layer
│   ├── Entities/                # Task, User, Project (Aggregate Roots)
│   ├── ValueObjects/            # TaskId, UserId, Email, TaskStatus
│   ├── Events/                  # Domain Events: TaskCreated, TaskAssigned, TaskCompleted
│   ├── Repositories/            # Interfaces: ITaskRepository, IUserRepository
│   └── Exceptions/              # Domain Exceptions
│
├── TaskManager.Application/     # Application Layer
│   ├── Commands/                # CreateTask, AssignTask, CompleteTask, CreateProject
│   ├── Queries/                 # GetTask, GetTasks, GetProject, GetUserTasks
│   ├── Handlers/                # Command/Query Handlers
│   ├── Validators/              # FluentValidation validators
│   ├── DTOs/                    # TaskDto, ProjectDto, UserDto
│   ├── Mappers/                 # Mapster/MapsterMapper profiles
│   ├── Behaviors/               # MediatR Pipeline: Validation, Logging, Transaction
│   └── Interfaces/              # IEmailService, INotificationService
│
├── TaskManager.Infrastructure/  # Infrastructure Layer
│   ├── Persistence/             # EF Core DbContext, Migrations, Repositories
│   ├── Services/                # EmailService, SignalRNotificationService
│   ├── Identity/                # JWT TokenService, RefreshTokenService
│   ├── BackgroundJobs/          # Hangfire/Quartz: Reminders, Cleanup
│   └── Configuration/           # Options classes, DI registration
│
├── TaskManager.Api/             # Presentation Layer (ASP.NET Core)
│   ├── Endpoints/               # Minimal API endpoints (MapGroup)
│   ├── Hubs/                    # TaskHub (SignalR)
│   ├── Middleware/              # ExceptionHandling, RequestLogging, RateLimiting
│   ├── Filters/                 # ValidationFilter, AuthorizationFilter
│   ├── Program.cs               # Composition Root
│   └── appsettings.json
│
├── TaskManager.Client/          # Blazor WebAssembly
│   ├── Pages/                   # Tasks.razor, Projects.razor, Login.razor
│   ├── Components/              # TaskCard, TaskForm, ProjectSelector
│   ├── Services/                # ApiClient, SignalRClient, AuthStateProvider
│   ├── State/                   # Flux/Redux-like state management
│   └── wwwroot/
│
├── TaskManager.Tests.Unit/      # Unit Tests
│   ├── Domain/                  # Entity, ValueObject, DomainEvent tests
│   ├── Application/             # Handler, Validator tests (Moq)
│   └── Infrastructure/          # Repository, Service tests
│
├── TaskManager.Tests.Integration/ # Integration Tests
│   ├── Api/                     # Endpoint tests (WebApplicationFactory)
│   ├── Persistence/             # Repository tests (Testcontainers PostgreSQL)
│   └── SignalR/                 # Hub tests
│
└── TaskManager.Tests.E2E/       # E2E Tests (Playwright)
    └── specs/
```

## 1️⃣ Domain Layer — ЧЯС (Clean Architecture)

### Value Objects

```csharp
// TaskId — strongly typed ID
public readonly record struct TaskId(Guid Value) {
    public static TaskId New() => new(Guid.NewGuid());
    public static implicit operator Guid(TaskId id) => id.Value;
    public static implicit operator TaskId(Guid guid) => new(guid);
    public override string ToString() => Value.ToString();
}

// Email — валидация в конструкторе
public readonly record struct Email(string Value) {
    public Email {
        if (string.IsNullOrWhiteSpace(Value) || !Value.Contains("@"))
            throw new ArgumentException("Invalid email format", nameof(Value));
    }
    public static implicit operator string(Email e) => e.Value;
    public static implicit operator Email(string s) => new(s);
}

// TaskStatus — enum-like с поведением
public enum TaskStatus {
    Backlog = 1,
    InProgress = 2,
    InReview = 3,
    Done = 4,
    Archived = 5
}
```

### Aggregate Root — Task

```csharp
public class Task : AggregateRoot<TaskId> {
    public string Title { get; private set; }
    public string Description { get; private set; }
    public TaskStatus Status { get; private set; }
    public UserId? AssigneeId { get; private set; }
    public ProjectId ProjectId { get; private set; }
    public DateTime CreatedAt { get; private set; }
    public DateTime UpdatedAt { get; private set; }
    
    private Task() { } // EF Core
    
    public static Task Create(TaskId id, string title, string description, ProjectId projectId, UserId creatorId) {
        var task = new Task {
            Id = id,
            Title = title,
            Description = description,
            ProjectId = projectId,
            Status = TaskStatus.Backlog,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        task.AddDomainEvent(new TaskCreatedEvent(task.Id, task.Title, task.ProjectId, creatorId));
        return task;
    }
    
    public void Assign(UserId userId) {
        if (Status == TaskStatus.Done || Status == TaskStatus.Archived)
            throw new InvalidOperationException("Cannot assign completed task");
        AssigneeId = userId;
        UpdatedAt = DateTime.UtcNow;
        AddDomainEvent(new TaskAssignedEvent(Id, userId));
    }
    
    public void StartWork() {
        if (Status != TaskStatus.Backlog) throw new InvalidOperationException("Task must be in Backlog");
        Status = TaskStatus.InProgress;
        UpdatedAt = DateTime.UtcNow;
        AddDomainEvent(new TaskStatusChangedEvent(Id, TaskStatus.Backlog, TaskStatus.InProgress));
    }
    
    public void Complete() {
        if (Status != TaskStatus.InReview) throw new InvalidOperationException("Task must be in review");
        Status = TaskStatus.Done;
        UpdatedAt = DateTime.UtcNow;
        AddDomainEvent(new TaskCompletedEvent(Id));
    }
}
```

### Domain Events

```csharp
public record TaskCreatedEvent(TaskId TaskId, string Title, ProjectId ProjectId, UserId CreatorId) : IDomainEvent;
public record TaskAssignedEvent(TaskId TaskId, UserId AssigneeId) : IDomainEvent;
public record TaskStatusChangedEvent(TaskId TaskId, TaskStatus OldStatus, TaskStatus NewStatus) : IDomainEvent;
public record TaskCompletedEvent(TaskId TaskId) : IDomainEvent;
```

## 2️⃣ Application Layer — CQRS с MediatR

### Commands

```csharp
public record CreateTaskCommand(string Title, string Description, Guid ProjectId) : IRequest<TaskId>;

public class CreateTaskHandler : IRequestHandler<CreateTaskCommand, TaskId> {
    private readonly ITaskRepository _repo;
    private readonly IUnitOfWork _uow;
    private readonly ICurrentUserService _currentUser;
    
    public CreateTaskHandler(ITaskRepository repo, IUnitOfWork uow, ICurrentUserService currentUser) {
        _repo = repo; _uow = uow; _currentUser = currentUser;
    }
    
    public async Task<TaskId> Handle(CreateTaskCommand cmd, CancellationToken ct) {
        var projectId = new ProjectId(cmd.ProjectId);
        var task = Task.Create(TaskId.New(), cmd.Title, cmd.Description, projectId, _currentUser.UserId!);
        await _repo.AddAsync(task, ct);
        await _uow.SaveChangesAsync(ct);
        return task.Id;
    }
}
```

### Queries

```csharp
public record GetTaskQuery(TaskId Id) : IRequest<TaskDto?>;

public class GetTaskHandler : IRequestHandler<GetTaskQuery, TaskDto?> {
    private readonly ITaskReadRepository _repo;
    private readonly IMapper _mapper;
    
    public GetTaskHandler(ITaskReadRepository repo, IMapper mapper) {
        _repo = repo; _mapper = mapper;
    }
    
    public async Task<TaskDto?> Handle(GetTaskQuery query, CancellationToken ct) {
        var task = await _repo.GetByIdAsync(query.Id, ct);
        return task == null ? null : _mapper.Map<TaskDto>(task);
    }
}
```

### Pipeline Behaviors

```csharp
// Validation
public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> 
    where TRequest : IRequest<TResponse> {
    private readonly IEnumerable<IValidator<TRequest>> _validators;
    
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct) {
        var context = new ValidationContext<TRequest>(request);
        var failures = _validators.Select(v => v.Validate(context))
            .SelectMany(r => r.Errors).Where(e => e != null).ToList();
        if (failures.Any()) throw new ValidationException(failures);
        return await next();
    }
}

// Transaction
public class TransactionBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> {
    private readonly IUnitOfWork _uow;
    
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct) {
        if (request is ICommand) {
            await _uow.BeginTransactionAsync(ct);
            try {
                var response = await next();
                await _uow.CommitAsync(ct);
                return response;
            } catch {
                await _uow.RollbackAsync(ct);
                throw;
            }
        }
        return await next();
    }
}
```

## 3️⃣ Infrastructure — EF Core, SignalR, JWT

### DbContext

```csharp
public class AppDbContext : DbContext {
    public DbSet<Task> Tasks => Set<Task>();
    public DbSet<User> Users => Set<User>();
    public DbSet<Project> Projects => Set<Project>();
    
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
    
    protected override void OnModelCreating(ModelBuilder model) {
        model.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
        
        // Outbox pattern для Domain Events
        model.Entity<OutboxMessage>(e => {
            e.HasKey(m => m.Id);
            e.Property(m => m.Type).HasMaxLength(200);
            e.Property(m => m.Content).HasColumnType("jsonb");
        });
    }
    
    public override async Task<int> SaveChangesAsync(CancellationToken ct = default) {
        // Dispatch Domain Events -> Outbox
        var entities = ChangeTracker.Entries<IAggregateRoot>()
            .Select(e => e.Entity)
            .Where(e => e.DomainEvents.Any())
            .ToList();
        
        foreach (var entity in entities) {
            foreach (var domainEvent in entity.DomainEvents) {
                OutboxMessages.Add(new OutboxMessage {
                    Id = Guid.NewGuid(),
                    Type = domainEvent.GetType().AssemblyQualifiedName!,
                    Content = JsonSerializer.Serialize(domainEvent),
                    CreatedAt = DateTime.UtcNow
                });
            }
            entity.ClearDomainEvents();
        }
        
        return await base.SaveChangesAsync(ct);
    }
}
```

### SignalR Hub

```csharp
[Authorize]
public class TaskHub : Hub {
    public async Task JoinProject(string projectId) 
        => await Groups.AddToGroupAsync(Context.ConnectionId, $"project-{projectId}");
    
    public async Task LeaveProject(string projectId) 
        => await Groups.RemoveFromGroupAsync(Context.ConnectionId, $"project-{projectId}");
}

// Service для отправки уведомлений
public class SignalRNotificationService : INotificationService {
    private readonly IHubContext<TaskHub> _hub;
    
    public async Task NotifyTaskCreated(TaskDto task) 
        => await _hub.Clients.Group($"project-{task.ProjectId}").SendAsync("TaskCreated", task);
    
    public async Task NotifyTaskUpdated(TaskDto task) 
        => await _hub.Clients.Group($"project-{task.ProjectId}").SendAsync("TaskUpdated", task);
}
```

### JWT Authentication

```csharp
// Program.cs
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => {
        options.TokenValidationParameters = new TokenValidationParameters {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!))
        };
        options.Events = new JwtBearerEvents {
            OnMessageReceived = ctx => {
                var token = ctx.Request.Query["access_token"];
                if (!string.IsNullOrEmpty(token) && ctx.Request.Path.StartsWithSegments("/hubs"))
                    ctx.Token = token;
                return Task.CompletedTask;
            }
        };
    });

builder.Services.AddSignalR();
```

## 4️⃣ API Layer — Minimal API

```csharp
// Program.cs
var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();
app.UseRateLimiter();
app.MapHub<TaskHub>("/hubs/tasks");

var api = app.MapGroup("/api").RequireAuthorization();

api.MapGet("/tasks", async (ISender sender, Guid projectId) => 
    Results.Ok(await sender.Send(new GetTasksQuery(projectId))));

api.MapGet("/tasks/{id}", async (ISender sender, Guid id) => 
    await sender.Send(new GetTaskQuery(new TaskId(id))) is TaskDto dto ? Results.Ok(dto) : Results.NotFound());

api.MapPost("/tasks", async (ISender sender, CreateTaskCommand cmd) => 
    Results.Created($"/api/tasks/{await sender.Send(cmd)}", null));

api.MapPut("/tasks/{id}/assign", async (ISender sender, Guid id, AssignTaskCommand cmd) => {
    await sender.Send(cmd with { TaskId = new TaskId(id) });
    return Results.NoContent();
});

api.MapPost("/tasks/{id}/complete", async (ISender sender, Guid id) => {
    await sender.Send(new CompleteTaskCommand(new TaskId(id)));
    return Results.NoContent();
});

app.Run();
```

## 5️⃣ Blazor Client — Real-time UI

### SignalR Client Service

```csharp
public class TaskSignalRService {
    private HubConnection? _connection;
    private readonly ILogger<TaskSignalRService> _logger;
    
    public event Action<TaskDto>? OnTaskCreated;
    public event Action<TaskDto>? OnTaskUpdated;
    
    public async Task StartAsync(string token) {
        _connection = new HubConnectionBuilder()
            .WithUrl("https://api.taskmanager.com/hubs/tasks", options => {
                options.AccessTokenProvider = () => Task.FromResult(token)!;
            })
            .WithAutomaticReconnect()
            .Build();
        
        _connection.On<TaskDto>("TaskCreated", dto => OnTaskCreated?.Invoke(dto));
        _connection.On<TaskDto>("TaskUpdated", dto => OnTaskUpdated?.Invoke(dto));
        
        await _connection.StartAsync();
    }
    
    public async Task JoinProject(Guid projectId) 
        => await _connection?.InvokeAsync("JoinProject", projectId.ToString());
    
    public async Task StopAsync() => await _connection?.StopAsync();
}
```

### Blazor Component

```razor
@page "/projects/{ProjectId}/tasks"
@inject TaskSignalRService SignalR
@inject ITaskApiClient ApiClient
@implements IDisposable

<PageTitle>Tasks</PageTitle>

<h3>Tasks for Project @ProjectId</h3>

<TaskForm OnSubmit="CreateTask" />

<div class="task-list">
    @foreach (var task in Tasks) {
        <TaskCard Task="task" OnUpdate="UpdateTask" />
    }
</div>

@code {
    [Parameter] public Guid ProjectId { get; set; }
    private List<TaskDto> Tasks = new();
    
    protected override async Task OnInitializedAsync() {
        Tasks = await ApiClient.GetTasksAsync(ProjectId);
        SignalR.OnTaskCreated += HandleTaskCreated;
        SignalR.OnTaskUpdated += HandleTaskUpdated;
        await SignalR.JoinProject(ProjectId);
    }
    
    private void HandleTaskCreated(TaskDto task) {
        Tasks.Insert(0, task);
        StateHasChanged();
    }
    
    private void HandleTaskUpdated(TaskDto task) {
        var index = Tasks.FindIndex(t => t.Id == task.Id);
        if (index >= 0) { Tasks[index] = task; StateHasChanged(); }
    }
    
    public void Dispose() {
        SignalR.OnTaskCreated -= HandleTaskCreated;
        SignalR.OnTaskUpdated -= HandleTaskUpdated;
    }
}
```

## 6️⃣ Tests — Unit + Integration

### Unit Test (Handler)

```csharp
public class CreateTaskHandlerTests {
    private readonly Mock<ITaskRepository> _repoMock;
    private readonly Mock<IUnitOfWork> _uowMock;
    private readonly Mock<ICurrentUserService> _userMock;
    private readonly CreateTaskHandler _handler;
    
    public CreateTaskHandlerTests() {
        _repoMock = new Mock<ITaskRepository>();
        _uowMock = new Mock<IUnitOfWork>();
        _userMock = new Mock<ICurrentUserService>();
        _userMock.Setup(u => u.UserId).Returns(UserId.New());
        _handler = new CreateTaskHandler(_repoMock.Object, _uowMock.Object, _userMock.Object);
    }
    
    [Fact]
    public async Task Handle_ValidCommand_ReturnsTaskId() {
        var cmd = new CreateTaskCommand("Test Task", "Description", Guid.NewGuid());
        var result = await _handler.Handle(cmd, CancellationToken.None);
        
        result.Should().NotBeEmpty();
        _repoMock.Verify(r => r.AddAsync(It.IsAny<Task>(), It.IsAny<CancellationToken>()), Times.Once);
        _uowMock.Verify(u => u.SaveChangesAsync(It.IsAny<CancellationToken>()), Times.Once);
    }
}
```

### Integration Test (Testcontainers)

```csharp
public class TasksApiTests : IClassFixture<DatabaseFixture>, IAsyncLifetime {
    private readonly HttpClient _client;
    private readonly DatabaseFixture _fixture;
    
    public TasksApiTests(DatabaseFixture fixture) {
        _fixture = fixture;
        var factory = new WebApplicationFactory<Program>()
            .WithWebHostBuilder(builder => {
                builder.ConfigureServices(services => {
                    services.RemoveAll<DbContextOptions<AppDbContext>>();
                    services.AddDbContext<AppDbContext>(opt => 
                        opt.UseNpgsql(_fixture.ConnectionString));
                });
            });
        _client = factory.CreateClient();
    }
    
    [Fact]
    public async Task CreateTask_ReturnsCreated() {
        var token = await GetAuthTokenAsync();
        _client.DefaultRequestHeaders.Authorization = new("Bearer", token);
        
        var response = await _client.PostAsJsonAsync("/api/tasks", new {
            Title = "Integration Test Task",
            Description = "Created via test",
            ProjectId = _fixture.TestProjectId
        });
        
        response.StatusCode.Should().Be(HttpStatusCode.Created);
    }
}
```

## 7️⃣ Docker & Kubernetes

### Dockerfile (Multi-stage, Distroless)

```dockerfile
# Build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY *.sln .
COPY src/*/*.csproj ./src/
RUN dotnet restore
COPY . .
RUN dotnet publish src/TaskManager.Api/TaskManager.Api.csproj -c Release -o /app/publish --no-restore

# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0-distroless AS runtime
WORKDIR /app
USER 65532:65532
COPY --from=build --chown=65532:65532 /app/publish .
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
ENTRYPOINT ["dotnet", "TaskManager.Api.dll"]
```

### Helm Chart (values.yaml)

```yaml
replicaCount: 3
image:
  repository: ghcr.io/myorg/taskmanager
  tag: "1.0.0"
service:
  type: ClusterIP
  port: 80
ingress:
  enabled: true
  hosts:
  - host: tasks.example.com
    paths: ["/"]
  tls:
  - secretName: tasks-tls
    hosts: [tasks.example.com]
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
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
postgresql:
  enabled: true
redis:
  enabled: true
```

## 8️⃣ CI/CD — GitHub Actions + ArgoCD

### GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: taskmanager_test
        ports: [5432:5432]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
    - uses: actions/checkout@v4
    - name: Setup .NET
      uses: actions/setup-dotnet@v4
      with:
        dotnet-version: '8.0.x'
    - name: Restore
      run: dotnet restore
    - name: Build
      run: dotnet build --no-restore -c Release
    - name: Unit Tests
      run: dotnet test TaskManager.Tests.Unit --no-build -c Release --logger "trx"
    - name: Integration Tests
      run: dotnet test TaskManager.Tests.Integration --no-build -c Release --logger "trx"
    - name: Upload Coverage
      uses: codecov/codecov-action@v3

  docker:
    needs: test
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
    - name: Build and Push
      uses: docker/build-push-action@v5
      with:
        context: .
        file: src/TaskManager.Api/Dockerfile
        push: true
        tags: ghcr.io/${{ github.repository }}/api:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: docker
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - name: Update ArgoCD Application
      run: |
        kubectl set image deployment/taskmanager-api \
          taskmanager-api=ghcr.io/${{ github.repository }}/api:${{ github.sha }} \
          -n production
        kubectl rollout status deployment/taskmanager-api -n production --timeout=300s
```

### ArgoCD Application

```yaml
# argocd/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: taskmanager
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/taskmanager-config
    targetRevision: HEAD
    path: overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## 📋 Чек-лист готовности

- [ ] Clean Architecture: 4 слоя, зависимости внутрь
- [ ] Domain: Aggregates, Value Objects, Domain Events, Repository interfaces
- [ ] Application: CQRS (Commands/Queries), MediatR, Pipeline Behaviors, FluentValidation
- [ ] Infrastructure: EF Core, Repositories, Outbox Pattern, SignalR, JWT, Background Jobs
- [ ] API: Minimal API, Auth, Rate Limiting, Health Checks, SignalR Hub
- [ ] Client: Blazor WASM, SignalR Client, State Management, Components
- [ ] Tests: Unit (xUnit, Moq, FluentAssertions), Integration (Testcontainers), E2E (Playwright)
- [ ] Docker: Multi-stage, Distroless, Non-root, Health Checks, .dockerignore
- [ ] K8s: Deployment, Service, Ingress, ConfigMap, Secret, HPA, PDB
- [ ] Helm: Chart с values, dependencies (PostgreSQL, Redis)
- [ ] CI/CD: GitHub Actions (test, build, push), ArgoCD (GitOps deploy)
- [ ] Observability: Serilog + Seq, OpenTelemetry Metrics/Traces, Prometheus/Grafana

## 🎉 Поздравляете!

Вы прошли полный курс C# от основ до продакшен-уровня. Этот проект объединяет:
- **Основы**: типы, коллекции, LINQ, async/await
- **ООП/Дизайн**: SOLID, Clean Architecture, DDD, CQRS
- **Продвинутые темы**: GC, SIMD, Source Generators, Pattern Matching
- **Инфраструктура**: Docker, K8s, Helm, Service Mesh, CI/CD
- **Надежность**: Testing, Observability, Security, Resilience

**Следующие шаги**: углубитесь в темы, которые интересны: gRPC, Event Sourcing, ML.NET, NativeAOT, WebAssembly, IoT.

## 🔗 Полезные ссылки для продолжения

- .NET Docs: https://learn.microsoft.com/dotnet/
- ASP.NET Core: https://learn.microsoft.com/aspnet/core/
- EF Core: https://learn.microsoft.com/ef/core/
- Blazor: https://learn.microsoft.com/aspnet/core/blazor/
- Kubernetes: https://kubernetes.io/docs/home/
- CNCF Landscape: https://landscape.cncf.io/
"""

# Write all remaining lessons
lesson_29_data = {
    "title": "Урок 29: Observability — структурированное логирование, метрики, распределенное трассирование, профилирование",
    "slug": "lesson-29",
    "short_description": "Serilog, Seq, OpenTelemetry, метрики (Prometheus/Grafana), распределенное трассирование (Jaeger/Zipkin), профилирование",
    "goals": [
        "Настроить структурированное логирование с Serilog: sinks, enrichment, levels",
        "Экспортировать метрики в Prometheus/Grafana через OpenTelemetry",
        "Реализовать распределенное трассирование: Activity, W3C TraceContext, Jaeger/Zipkin",
        "Использовать ActivitySource и ActivityListener для кастомных spans",
        "Профилировать приложение: dotnet-trace, PerfView, BenchmarkDotNet"
    ],
    "content_md": lesson_29_md,
    "practice_tasks": [
        "Настройте Serilog: Console + Seq + File (rolling). Добавьте enrichment: ThreadId, MachineName, CorrelationId из Activity.",
        "Добавьте OpenTelemetry Metrics: Runtime, AspNetCore, HttpClient, EF Core. Экспорт в Prometheus. Создайте Grafana дашборд.",
        "Включите Distributed Tracing: Jaeger/Zipkin экспортер. Добавьте кастомный `ActivitySource` для бизнес-операций.",
        "Напишите BenchmarkDotNet тест: сравните `StringBuilder` vs `string.Concat` vs `List<string>.Join`.",
        "Профилируйте приложение под нагрузкой: `dotnet-trace collect`, анализ в PerfView / Speedscope."
    ],
    "common_errors": [
        {"mistake": "Логи не структурированы", "correct": "Используйте `{Property}` синтаксис, `@` для объектов"},
        {"mistake": "Отсутствие CorrelationId", "correct": "Добавляйте `TraceId`/`CorrelationId` в LogContext"},
        {"mistake": "Метрики без лейблов (high cardinality)", "correct": "Не добавляйте unbounded лейблы (userId, requestId)"},
        {"mistake": "Трассировка не включена для всех вызовов", "correct": "Включите instrumentation для HttpClient, EF Core, gRPC"},
        {"mistake": "Benchmark без `[MemoryDiagnoser]`", "correct": "Всегда добавляйте MemoryDiagnoser"},
        {"mistake": "`dotnet-trace` без символов", "correct": "Собирайте с `dotnet publish -c Release -p:DebugType=portable`"}
    ],
    "resources": [
        "Serilog: https://serilog.net/",
        "OpenTelemetry .NET: https://github.com/open-telemetry/opentelemetry-dotnet",
        "Prometheus: https://prometheus.io/",
        "Grafana: https://grafana.com/",
        "Jaeger: https://www.jaegertracing.io/",
        "BenchmarkDotNet: https://benchmarkdotnet.org/",
        "PerfView: https://github.com/microsoft/perfview"
    ],
    "key_takeaways": [
        "Serilog — structured logging, sinks, enrichment, @ для объектов, LogContext для correlation",
        "OpenTelemetry Metrics — Runtime, AspNetCore, HttpClient, EF Core, custom meters → Prometheus/Grafana",
        "Distributed Tracing — ActivitySource, W3C TraceContext, Jaeger/Zipkin, baggage для propagation",
        "Profiling — dotnet-trace (ETW), dotnet-counters (real-time), BenchmarkDotNet (micro), PerfView (deep)"
    ],
    "estimated_minutes": 50,
    "language_slug": "csharp",
    "lesson_order": 29,
    "name_en": "Lesson: Observability",
    "short_description_en": "Structured logging, metrics, distributed tracing, profiling with OpenTelemetry"
}

lesson_30_data = {
    "title": "Урок 30: Cloud Native — Docker, Kubernetes, Cloud Run, сервис-меш, CI/CD",
    "slug": "lesson-30",
    "short_description": "Dockerfile оптимизация, multi-stage builds, Kubernetes манифесты, Helm, Kustomize, Service Mesh (Istio/Linkerd), CI/CD pipelines",
    "goals": [
        "Писать оптимальные Dockerfile: multi-stage, layer caching, non-root, distroless",
        "Развертывать в Kubernetes: Deployments, Services, Ingress, ConfigMaps, Secrets, HPA",
        "Использовать Helm и Kustomize для управления конфигурациями",
        "Понимать Service Mesh: Istio, Linkerd — mTLS, traffic splitting, observability",
        "Настраивать CI/CD: GitHub Actions, GitLab CI, ArgoCD, Flux"
    ],
    "content_md": lesson_30_md,
    "practice_tasks": [
        "Напишите оптимальный multi-stage Dockerfile для ASP.NET Core приложения с distroless базой, non-root пользователем, health check.",
        "Создайте K8s манифесты: Deployment, Service, Ingress, ConfigMap, Secret, HPA, PDB.",
        "Создайте Helm чарт с зависимостью от PostgreSQL (Bitnami). Настройте values-prod.yaml.",
        "Настройте Kustomize: base + overlays для dev/staging/prod с разными replicaCount и ресурсами.",
        "Настройте GitHub Actions pipeline: build multi-arch image, push to GHCR, deploy через kubectl/ArgoCD."
    ],
    "common_errors": [
        {"mistake": "`latest` тег в проде", "correct": "Всегда конкретные теги: semver, git sha"},
        {"mistake": "Отсутствие `resources.requests/limits`", "correct": "Всегда ставьте requests и limits"},
        {"mistake": "Отсутствие `liveness/readiness` probes", "correct": "Добавляйте health endpoints"},
        {"mistake": "Запуск от root в контейнере", "correct": "`USER 65532:65532` в Dockerfile"},
        {"mistake": "Secrets в Git / Helm values.yaml", "correct": "Sealed Secrets, External Secrets Operator, Vault"},
        {"mistake": "Отсутствие PDB", "correct": "Добавьте PodDisruptionBudget"},
        {"mistake": "Неправильный порядок слоев в Dockerfile", "correct": "COPY csproj → restore → COPY . → publish"}
    ],
    "resources": [
        "Docker Best Practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/",
        "Kubernetes: https://kubernetes.io/docs/home/",
        "Helm: https://helm.sh/docs/",
        "Kustomize: https://kustomize.io/",
        "Istio: https://istio.io/latest/docs/",
        "Linkerd: https://linkerd.io/",
        "ArgoCD: https://argo-cd.readthedocs.io/",
        "Flux: https://fluxcd.io/"
    ],
    "key_takeaways": [
        "Docker: multi-stage, layer caching (csproj first), distroless, non-root, .dockerignore, health checks",
        "K8s: Deployment, Service, Ingress, ConfigMap/Secret, HPA, VPA, PDB, probes, resources",
        "Helm: charts, values, dependencies, template functions, release management",
        "Kustomize: base/overlays, patches, generators, нативный K8s",
        "Service Mesh: Istio/Linkerd — mTLS, traffic splitting, observability, security policies",
        "CI/CD: GitHub Actions (build/push), ArgoCD/Flux (GitOps), semver tags, security scanning"
    ],
    "estimated_minutes": 60,
    "language_slug": "csharp",
    "lesson_order": 30,
    "name_en": "Lesson: Cloud Native — Docker, K8s, Cloud",
    "short_description_en": "Dockerfile optimization, Kubernetes manifests, Helm, Kustomize, Service Mesh, CI/CD"
}

lesson_31_data = {
    "title": "Урок 31: Производительность — профилирование, бенчмарки, оптимизации, Span, ArrayPool, SIMD",
    "slug": "lesson-31",
    "short_description": "BenchmarkDotNet, профилирование (dotnet-trace, PerfView), Span/Memory, ArrayPool, SIMD, Vector<T>, PGO, NativeAOT",
    "goals": [
        "Писать правильные бенчмарки с BenchmarkDotNet: MemoryDiagnoser, DisassemblyDiagnoser",
        "Профилировать CPU и память: dotnet-trace, PerfView, dotnet-counters, EventPipe",
        "Использовать Span/Memory, ArrayPool, Stackalloc для снижения аллокаций",
        "Применять SIMD: Vector<T>, HardwareIntrinsics (AVX2, SSE), System.Numerics",
        "Понимать PGO (Profile-Guided Optimization), NativeAOT, Tiered Compilation, ReadyToRun"
    ],
    "content_md": lesson_31_md,
    "practice_tasks": [
        "Напишите BenchmarkDotNet тест: сравните `List<T>.Add` vs `ArrayPool` + `List<T>` с заранее выделенным массивом.",
        "Профилируйте приложение под нагрузкой: `dotnet-trace collect`, найдите топ-5 горячих методов в PerfView/Speedscope.",
        "Оптимизируйте парсинг CSV: замените `string.Split` на `Span<char>` парсинг без аллокаций.",
        "Реализуйте сумму массива через `Vector<T>` и `Avx2` с fallback на скалярный код.",
        "Настройте Dynamic PGO: `<TieredPGO>true</TieredPGO>`. Сравните производительность до/после."
    ],
    "common_errors": [
        {"mistake": "Бенчмарк без `[MemoryDiagnoser]`", "correct": "Всегда добавляйте"},
        {"mistake": "`DateTime.Now` в бенчмарке", "correct": "Используйте `Stopwatch`"},
        {"mistake": "JIT не прогрет", "correct": "`[GlobalSetup]` с прогревом, `IterationSetup`"},
        {"mistake": "Dead code elimination", "correct": "`return` результат, `GC.KeepAlive`"},
        {"mistake": "SIMD без fallback", "correct": "Проверяйте `Avx2.IsSupported`, `Sse.IsSupported`"},
        {"mistake": "`stackalloc` большого буфера", "correct": "Только < 1KB, иначе `ArrayPool`"},
        {"mistake": "PGO без нагрузочного теста", "correct": "Запускайте реальные сценарии"}
    ],
    "resources": [
        "BenchmarkDotNet: https://benchmarkdotnet.org/",
        "Span/Memory: https://learn.microsoft.com/dotnet/standard/memory-and-spans/",
        "SIMD: https://learn.microsoft.com/dotnet/api/system.runtime.intrinsics",
        "PGO: https://learn.microsoft.com/dotnet/core/deploying/profile-guided-optimization",
        "NativeAOT: https://learn.microsoft.com/dotnet/core/deploying/native-aot/",
        "PerfView: https://github.com/microsoft/perfview"
    ],
    "key_takeaways": [
        "BenchmarkDotNet: MemoryDiagnoser, DisassemblyDiagnoser, Params, Baseline, правильный анализ результатов",
        "Профилирование: dotnet-trace (ETW), PerfView (deep), dotnet-counters (real-time), Speedscope (визуализация)",
        "Низкие аллокации: Span/Memory, ArrayPool, stackalloc (<1KB), ObjectPool",
        "SIMD: Vector<T> (переносимо), HardwareIntrinsics (AVX2/SSE/NEON), System.Numerics",
        "Продвинутые: Dynamic PGO, NativeAOT, ReadyToRun, Tiered Compilation"
    ],
    "estimated_minutes": 55,
    "language_slug": "csharp",
    "lesson_order": 31,
    "name_en": "Lesson: Performance — Profiling, Benchmarks, SIMD",
    "short_description_en": "BenchmarkDotNet, profiling, Span/Memory, ArrayPool, SIMD, PGO, NativeAOT"
}

lesson_32_data = {
    "title": "Урок 32: Продвинутые паттерны — Функциональное программирование, Reactive (Rx.NET), Actor Model (Akka.NET/Orleans)",
    "slug": "lesson-32",
    "short_description": "Functional C#: Result, Option, Railway-oriented, Rx.NET: IObservable, operators, schedulers, Akka.NET/Orleans actors",
    "goals": [
        "Писать функциональный C#: Result<T>, Option<T>, Railway-oriented programming",
        "Работать с Rx.NET: IObservable, operators (Select, Where, Merge, CombineLatest), schedulers",
        "Понимать Actor Model: Akka.NET и Orleans — actors, persistence, clustering",
        "Применять паттерны: Circuit Breaker, Retry, Bulkhead, Saga, Event Sourcing"
    ],
    "content_md": lesson_32_md,
    "practice_tasks": [
        "Реализуйте `Result<T>` и `Option<T>` с `Map`, `Bind`, `Match`. Напишите валидацию заказа в railway-стиле.",
        "Создайте Rx.NET pipeline: генерация чисел → фильтрация чётных → батчинг по 5 → вывод среднего каждую секунду.",
        "Напишите Akka.NET актор для управления состоянием заказа с Persistence (Event Sourcing).",
        "Создайте Orleans Grain для корзины покупок с персистентным состоянием и reminders для abandoned cart.",
        "Реализуйте Circuit Breaker и Saga для распределенного заказа (Inventory → Payment → Notification)."
    ],
    "common_errors": [
        {"mistake": "Исключения для управления потоком", "correct": "Result<T>, Option<T>, Railway-oriented"},
        {"mistake": "`Subscribe` без `Dispose`", "correct": "Всегда `using subscription = obs.Subscribe(...)`"},
        {"mistake": "Blocking в Rx (`Wait`, `FirstAsync().Wait()`)", "correct": "Используйте `await observable.FirstAsync()`"},
        {"mistake": "Акторы с блокирующим кодом", "correct": "PipeTo, Ask, асинхронные методы в акторах"},
        {"mistake": "Orleans Grain делает много работы", "correct": "Декомпозиция на гранулярные grains"},
        {"mistake": "Saga без идемпотентности", "correct": "Все шаги идемпотентны (проверка по correlationId)"}
    ],
    "resources": [
        "LanguageExt: https://github.com/louthy/language-ext",
        "Rx.NET: https://github.com/dotnet/reactive",
        "Akka.NET: https://getakka.net/",
        "Orleans: https://dotnet.github.io/orleans/",
        "Enterprise Integration Patterns: https://www.enterpriseintegrationpatterns.com/"
    ],
    "key_takeaways": [
        "Functional C#: Result<T>, Option<T>, Either<L,R>, Railway-oriented — нет исключений, композиция",
        "Rx.NET: IObservable<T>, операторы (Select, Where, Merge, CombineLatest, Throttle), Schedulers, Backpressure",
        "Akka.NET: Actors, Supervision, Persistence, Clustering — классическая модель акторов",
        "Orleans: Virtual Actors (Grains), Persistence, Streams, Reminders, Clustering — проще, масштабируемее",
        "Patterns: Circuit Breaker, Retry, Bulkhead, Saga, Event Sourcing — надежность в распределенных системах"
    ],
    "estimated_minutes": 60,
    "language_slug": "csharp",
    "lesson_order": 32,
    "name_en": "Lesson: Advanced Patterns — Functional, Reactive, Actors",
    "short_description_en": "Functional C#, Result/Option, Rx.NET, Akka.NET, Orleans, Circuit Breaker, Saga"
}

lesson_33_data = {
    "title": "Урок 33: Финальный проект — Full Stack приложение: API, Blazor, SignalR, Tests, CI/CD, Deploy",
    "slug": "lesson-33",
    "short_description": "Сборка полного приложения: Clean Architecture, ASP.NET Core API, Blazor WASM, SignalR, xUnit/Integration tests, Docker, Kubernetes, GitHub Actions, ArgoCD",
    "goals": [
        "Создать Clean Architecture решение с 4 слоями",
        "Реализовать ASP.NET Core Minimal API с CQRS (MediatR), EF Core, JWT Auth",
        "Построить Blazor WebAssembly клиент с авторизацией, SignalR real-time",
        "Написать Unit тесты (xUnit, Moq, FluentAssertions) и Integration тесты (Testcontainers)",
        "Настроить Docker multi-stage, Kubernetes манифесты, Helm чарт",
        "Настроить CI/CD: GitHub Actions → Build → Test → Docker → Deploy (ArgoCD)"
    ],
    "content_md": lesson_33_md,
    "practice_tasks": [
        "Создайте Clean Architecture решение с 4 проектами. Настройте зависимости.",
        "Реализуйте Domain слой: Task aggregate, Value Objects, Domain Events.",
        "Реализуйте Application слой: CQRS команды/запросы, MediatR handlers, FluentValidation.",
        "Настройте Infrastructure: EF Core DbContext, Outbox pattern, SignalR, JWT.",
        "Постройте Minimal API endpoints с авторизацией и SignalR Hub.",
        "Создайте Blazor WASM клиент с SignalR real-time обновлениями.",
        "Напишите Unit тесты для Handlers и Domain логики (xUnit, Moq, FluentAssertions).",
        "Напишите Integration тесты с Testcontainers (PostgreSQL) и WebApplicationFactory.",
        "Создайте Multi-stage Dockerfile с distroless базой, non-root пользователем, health check.",
        "Настройте Helm чарт с зависимостями PostgreSQL и Redis. Настройте values-prod.yaml.",
        "Настройте GitHub Actions pipeline: test → build → docker push → ArgoCD deploy.",
        "Настройте Observability: Serilog + Seq, OpenTelemetry Metrics/Traces → Prometheus/Grafana."
    ],
    "common_errors": [
        {"mistake": "Нарушение Dependency Rule (Domain ссылается на Infrastructure)", "correct": "Интерфейсы в Application, реализации в Infrastructure"},
        {"mistake": "Анемичная доменная модель (логика в Handlers)", "correct": "Переносите бизнес-логику в Aggregates/Entities"},
        {"mistake": "Отсутствие Outbox Pattern для Domain Events", "correct": "Сохраняйте события в Outbox таблицу в той же транзакции"},
        {"mistake": "JWT секрет в коде / appsettings.json", "correct": "User Secrets (dev), Key Vault / Env Vars (prod)"},
        {"mistake": "Отсутствие Rate Limiting и Health Checks", "correct": "Всегда добавляйте в API"},
        {"mistake": "Dockerfile: COPY . . перед restore", "correct": "COPY csproj → restore → COPY . → publish"},
        {"mistake": "Запуск контейнера от root", "correct": "USER 65532:65532 в distroless"},
        {"mistake": "K8s без resources.requests/limits и probes", "correct": "Обязательны для production"},
        {"mistake": "Secrets в Git / Helm values.yaml", "correct": "Sealed Secrets, External Secrets Operator, Vault"},
        {"mistake": "CI/CD без тестов", "correct": "Unit + Integration тесты обязательны в pipeline"}
    ],
    "resources": [
        "Clean Architecture: https://github.com/jasontaylordev/CleanArchitecture",
        "eShopOnWeb (Microsoft reference): https://github.com/dotnet-architecture/eShopOnWeb",
        "Blazor Docs: https://learn.microsoft.com/aspnet/core/blazor/",
        "Testcontainers: https://dotnet.testcontainers.org/",
        "ArgoCD: https://argo-cd.readthedocs.io/",
        "CNCF Landscape: https://landscape.cncf.io/"
    ],
    "key_takeaways": [
        "Clean Architecture — 4 слоя, зависимости только внутрь, интерфейсы в Application",
        "DDD — Aggregates, Value Objects, Domain Events, Repository pattern",
        "CQRS + MediatR — Commands/Queries, Pipeline Behaviors (Validation, Transaction, Logging)",
        "EF Core — Outbox Pattern для надежности Domain Events, миграции",
        "SignalR — real-time уведомления, Groups для проектов, JWT в query string для WebSockets",
        "Blazor WASM — SignalR клиент, автоматическое переподключение, state management",
        "Testing — Unit (Moq), Integration (Testcontainers), E2E (Playwright)",
        "Docker — Multi-stage, Distroless, Non-root, Health Checks, Layer Caching",
        "K8s/Helm — Deployment, Service, Ingress, HPA, PDB, ConfigMap/Secret, dependencies",
        "CI/CD — GitHub Actions (test, build, push), ArgoCD (GitOps), semver tags",
        "Observability — Serilog, OpenTelemetry, Prometheus/Grafana, Jaeger/Zipkin"
    ],
    "estimated_minutes": 120,
    "language_slug": "csharp",
    "lesson_order": 33,
    "name_en": "Lesson: Final Project — Full Stack App",
    "short_description_en": "Clean Architecture, ASP.NET Core API, Blazor, SignalR, Tests, Docker, K8s, CI/CD"
}

# Write lessons 29-33
write_lesson(29, lesson_29_data)
write_lesson(30, lesson_30_data)
write_lesson(31, lesson_31_data)
write_lesson(32, lesson_32_data)
write_lesson(33, lesson_33_data)

print("Lessons 29-33 written!")