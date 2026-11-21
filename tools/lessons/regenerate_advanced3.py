#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate advanced lessons (27-33) with proper content extraction."""

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
# LESSON 27: Networking, HTTP, gRPC
# ============================================================
lesson_27_md = """## 🎯 Что вы узнаете
- HttpClient: пулинг соединений, IHttpClientFactory, жизненный цикл
- Polly: Retry, Circuit Breaker, Timeout, Bulkhead, Fallback
- gRPC: protobuf, unary/streaming, interceptors, code-first
- WebSockets: System.Net.WebSockets, SignalR
- Rate Limiting: Fixed Window, Sliding Window, Token Bucket
- Named Pipes, Unix Domain Sockets для IPC

## 🌐 HttpClient — правильное использование

### Проблема: HttpClient exhaustion

```csharp
// НЕ ДЕЛАЙТЕ ТАК — утечка сокетов (TIME_WAIT)
using var client = new HttpClient();
var result = await client.GetStringAsync(url);
```

### Правильно: IHttpClientFactory

```csharp
// Program.cs
builder.Services.AddHttpClient<GitHubClient>(client => {
    client.BaseAddress = new Uri("https://api.github.com/");
    client.DefaultRequestHeaders.UserAgent.ParseAdd("MyApp/1.0");
    client.Timeout = TimeSpan.FromSeconds(30);
});

// Использование
public class GitHubClient {
    private readonly HttpClient _client;
    public GitHubClient(HttpClient client) => _client = client;
    
    public async Task<User> GetUserAsync(string login) {
        var response = await _client.GetAsync($"users/{login}");
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<User>();
    }
}
```

### Типы регистрации

```csharp
// Typed Client (рекомендуется)
services.AddHttpClient<GitHubClient>();

// Named Client
services.AddHttpClient("github", c => c.BaseAddress = new Uri("https://api.github.com/"));

// В коде
var client = factory.CreateClient("github");

// Default Client
services.AddHttpClient(); // без имени
var client = factory.CreateClient(); // использует default
```

### HttpClientHandler настройка

```csharp
services.AddHttpClient<ApiClient>().ConfigurePrimaryHttpMessageHandler(() => 
    new HttpClientHandler {
        AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate,
        UseCookies = false,
        AllowAutoRedirect = true,
        MaxConnectionsPerServer = 100, // .NET 6+
        PooledConnectionLifetime = TimeSpan.FromMinutes(5), // DNS refresh
        ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true // только для dev!
    });
```

## 🛡 Polly — Resilience Policies

### Установка

```bash
dotnet add package Microsoft.Extensions.Http.Polly
dotnet add package Polly.Extensions.Http
```

### Основные политики

```csharp
services.AddHttpClient<ApiClient>()
    .AddPolicyHandler(GetRetryPolicy())
    .AddPolicyHandler(GetCircuitBreakerPolicy())
    .AddPolicyHandler(GetTimeoutPolicy());

// Retry с экспоненциальным backoff + jitter
static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy() 
    => HttpPolicyExtensions
        .HandleTransientHttpError() // 5xx, 408, HttpRequestException
        .OrResult(r => r.StatusCode == System.Net.HttpStatusCode.TooManyRequests) // 429
        .WaitAndRetryAsync(
            retryCount: 3,
            sleepDurationProvider: attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt)) 
                + TimeSpan.FromMilliseconds(Random.Shared.Next(0, 100)), // jitter
            onRetry: (outcome, timespan, attempt, ctx) => {
                Log.Warning("Retry {Attempt} after {Delay}: {Reason}", attempt, timespan, outcome.Exception?.Message ?? outcome.Result?.StatusCode.ToString());
            });

// Circuit Breaker — останавливает вызовы при множественных ошибках
static IAsyncPolicy<HttpResponseMessage> GetCircuitBreakerPolicy()
    => HttpPolicyExtensions
        .HandleTransientHttpError()
        .CircuitBreakerAsync(
            handledEventsAllowedBeforeBreaking: 5,
            durationOfBreak: TimeSpan.FromSeconds(30),
            onBreak: (ex, ts) => Log.Error("Circuit opened for {Duration}", ts),
            onReset: () => Log.Information("Circuit closed"),
            onHalfOpen: () => Log.Information("Circuit half-open"));

// Timeout
static IAsyncPolicy<HttpResponseMessage> GetTimeoutPolicy()
    => Policy.TimeoutAsync<HttpResponseMessage>(TimeSpan.FromSeconds(10));

// Bulkhead — ограничение параллелизма
static IAsyncPolicy<HttpResponseMessage> GetBulkheadPolicy()
    => Policy.BulkheadAsync<HttpResponseMessage>(
        maxParallelization: 10,
        maxQueuingActions: 20,
        onBulkheadRejectedAsync: ctx => {
            Log.Warning("Bulkhead rejected");
            return Task.CompletedTask;
        });

// Fallback — возврат дефолтного значения при ошибке
static IAsyncPolicy<HttpResponseMessage> GetFallbackPolicy()
    => Policy<HttpResponseMessage>
        .Handle<HttpRequestException>()
        .FallbackAsync(new HttpResponseMessage(HttpStatusCode.ServiceUnavailable) {
            Content = new StringContent("{\"error\":\"Service unavailable\"}", Encoding.UTF8, "application/json")
        });
```

### PolicyWrap — комбинирование

```csharp
// Порядок важен: Timeout → Bulkhead → CircuitBreaker → Retry → Fallback
var wrapper = Policy.WrapAsync(
    GetTimeoutPolicy(),
    GetBulkheadPolicy(),
    GetCircuitBreakerPolicy(),
    GetRetryPolicy(),
    GetFallbackPolicy()
);

services.AddHttpClient<ApiClient>().AddPolicyHandler(wrapper);
```

## 🔧 gRPC — высокопроизводительный RPC

### Protobuf определение

```protobuf
// greet.proto
syntax = "proto3";

package Greet;

service Greeter {
    rpc SayHello (HelloRequest) returns (HelloReply);           // Unary
    rpc SayHellos (HelloRequest) returns (stream HelloReply);   // Server streaming
    rpc SayHelloStream (stream HelloRequest) returns (HelloReply); // Client streaming
    rpc SayHelloBidi (stream HelloRequest) returns (stream HelloReply); // Bidi streaming
}

message HelloRequest {
    string name = 1;
}

message HelloReply {
    string message = 1;
}
```

### Server (ASP.NET Core)

```csharp
// Program.cs
builder.Services.AddGrpc();

app.MapGrpcService<GreeterService>();

// Service
public class GreeterService : Greeter.GreeterBase {
    public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context) {
        return Task.FromResult(new HelloReply { Message = $"Hello, {request.Name}!" });
    }
    
    // Server streaming
    public override async Task SayHellos(HelloRequest request, IServerStreamWriter<HelloReply> responseStream, ServerCallContext context) {
        for (int i = 0; i < 5; i++) {
            await responseStream.WriteAsync(new HelloReply { Message = $"Hello {i}, {request.Name}!" });
            await Task.Delay(100);
        }
    }
}
```

### Client

```csharp
var channel = GrpcChannel.ForAddress("https://localhost:5001");
var client = new Greeter.GreeterClient(channel);

// Unary
var reply = await client.SayHelloAsync(new HelloRequest { Name = "Alex" });

// Server streaming
using var call = client.SayHellos(new HelloRequest { Name = "Alex" });
await foreach (var msg in call.ResponseStream.ReadAllAsync()) {
    Console.WriteLine(msg.Message);
}

// Client streaming
using var call = client.SayHelloStream();
await call.RequestStream.WriteAsync(new HelloRequest { Name = "A" });
await call.RequestStream.WriteAsync(new HelloRequest { Name = "B" });
await call.RequestStream.CompleteAsync();
var reply = await call.ResponseAsync;

// Bidi streaming
using var call = client.SayHelloBidi();
var writeTask = WriteRequests(call.RequestStream);
var readTask = ReadResponses(call.ResponseStream);
await Task.WhenAll(writeTask, readTask);
```

### Code-first gRPC (без .proto)

```csharp
// .NET 7+: атрибуты вместо .proto
[ProtoContract]
public class HelloRequest {
    [ProtoMember(1)] public string Name { get; set; }
}

[ProtoContract]
public class HelloReply {
    [ProtoMember(1)] public string Message { get; set; }
}

[GrpcService]
public interface IGreeter {
    Task<HelloReply> SayHello(HelloRequest request);
}

// Реализация
public class GreeterService : IGreeter { ... }

// Регистрация
builder.Services.AddCodeFirstGrpc(options => {
    options.ResponseCompressionLevel = System.IO.Compression.CompressionLevel.Optimal;
});
```

### Interceptors — cross-cutting

```csharp
public class LoggingInterceptor : Interceptor {
    private readonly ILogger<LoggingInterceptor> _logger;
    
    public override async Task<TResponse> UnaryServerHandler<TRequest, TResponse>(
        TRequest request, ServerCallContext context, UnaryServerMethod<TRequest, TResponse> continuation) {
        _logger.LogInformation("gRPC {Method} called", context.Method);
        var stopwatch = Stopwatch.StartNew();
        try {
            return await continuation(request, context);
        } finally {
            stopwatch.Stop();
            _logger.LogInformation("gRPC {Method} completed in {Elapsed}ms", context.Method, stopwatch.ElapsedMilliseconds);
        }
    }
}

// Регистрация
builder.Services.AddGrpc(options => {
    options.Interceptors.Add<LoggingInterceptor>();
});
```

## 🔌 WebSockets и SignalR

### Низкоуровневые WebSockets

```csharp
// Server (ASP.NET Core)
app.UseWebSockets();

app.Map("/ws", async context => {
    if (!context.WebSockets.IsWebSocketRequest) {
        context.Response.StatusCode = 400;
        return;
    }
    
    using var ws = await context.WebSockets.AcceptWebSocketAsync();
    var buffer = new byte[4096];
    
    while (ws.State == WebSocketState.Open) {
        var result = await ws.ReceiveAsync(buffer, CancellationToken.None);
        if (result.MessageType == WebSocketMessageType.Close) {
            await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closed", CancellationToken.None);
            break;
        }
        
        // Echo
        await ws.SendAsync(buffer.AsMemory(0, result.Count), result.MessageType, result.EndOfMessage, CancellationToken.None);
    }
});

// Client
using var ws = new ClientWebSocket();
await ws.ConnectAsync(new Uri("wss://localhost/ws"), CancellationToken.None);
await ws.SendAsync(Encoding.UTF8.GetBytes("Hello"), WebSocketMessageType.Text, true, CancellationToken.None);
var buffer = new byte[4096];
var result = await ws.ReceiveAsync(buffer, CancellationToken.None);
```

### SignalR — абстракция над WebSockets

```bash
dotnet add package Microsoft.AspNetCore.SignalR
dotnet add package Microsoft.AspNetCore.SignalR.Client
```

```csharp
// Hub
public class ChatHub : Hub {
    public async Task SendMessage(string user, string message) {
        await Clients.All.SendAsync("ReceiveMessage", user, message);
    }
    
    public async Task SendToGroup(string group, string message) {
        await Clients.Group(group).SendAsync("ReceiveMessage", Context.UserIdentifier, message);
    }
    
    public override async Task OnConnectedAsync() {
        await Groups.AddToGroupAsync(Context.ConnectionId, "default");
        await base.OnConnectedAsync();
    }
}

// Регистрация
builder.Services.AddSignalR();
app.MapHub<ChatHub>("/chathub");

// Client (JS или C#)
var connection = new HubConnectionBuilder()
    .WithUrl("https://localhost/chathub")
    .WithAutomaticReconnect()
    .Build();

connection.On<string, string>("ReceiveMessage", (user, msg) => Console.WriteLine($"{user}: {msg}"));

await connection.StartAsync();
await connection.InvokeAsync("SendMessage", "Alex", "Hello SignalR!");
```

## 🚦 Rate Limiting — ограничение запросов

### Встроенный Rate Limiter (.NET 7+)

```csharp
builder.Services.AddRateLimiter(options => {
    // Fixed Window — простое окно
    options.AddFixedWindowLimiter("fixed", opts => {
        opts.PermitLimit = 100;
        opts.Window = TimeSpan.FromMinutes(1);
        opts.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        opts.QueueLimit = 10;
    });
    
    // Sliding Window — скользящее окно (гладче)
    options.AddSlidingWindowLimiter("sliding", opts => {
        opts.PermitLimit = 100;
        opts.Window = TimeSpan.FromMinutes(1);
        opts.SegmentsPerWindow = 10;
        opts.QueueLimit = 10;
    });
    
    // Token Bucket — для burst трафика
    options.AddTokenBucketLimiter("token", opts => {
        opts.TokenLimit = 100;
        opts.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        opts.QueueLimit = 10;
        opts.ReplenishmentPeriod = TimeSpan.FromSeconds(10);
        opts.TokensPerPeriod = 20;
    });
    
    // Concurrency — ограничение одновременных запросов
    options.AddConcurrencyLimiter("concurrency", opts => {
        opts.PermitLimit = 10;
        opts.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        opts.QueueLimit = 5;
    });
    
    // Глобальная политика отказа
    options.OnRejected = (context, token) => {
        context.HttpContext.Response.StatusCode = StatusCodes.Status429TooManyRequests;
        return ValueTask.CompletedTask;
    };
});

// Использование
app.UseRateLimiter();

app.MapGet("/api/data", () => "OK").RequireRateLimiting("sliding");

// Или через атрибут
[EnableRateLimiting("fixed")]
public class MyController : ControllerBase { }
```

### Распределенное Rate Limiting (Redis)

```csharp
// Используйте DistributedRateLimiter из Microsoft.Extensions.RateLimiting.Redis
// или реализуйте через Redis Lua скрипты для атомарности
```

## 📡 IPC: Named Pipes, Unix Domain Sockets

### Named Pipes (Windows/Linux)

```csharp
// Server
var server = new NamedPipeServerStream("mypipe", PipeDirection.InOut, 4);
await server.WaitForConnectionAsync();
using var reader = new StreamReader(server);
using var writer = new StreamWriter(server) { AutoFlush = true };

var msg = await reader.ReadLineAsync();
await writer.WriteLineAsync($"Echo: {msg}");

// Client
var client = new NamedPipeClientStream(".", "mypipe", PipeDirection.InOut);
await client.ConnectAsync(1000);
using var reader = new StreamReader(client);
using var writer = new StreamWriter(client) { AutoFlush = true };

await writer.WriteLineAsync("Hello");
var response = await reader.ReadLineAsync();
```

### Unix Domain Sockets (Linux, высокопроизводительный IPC)

```csharp
// .NET 6+
var listener = new UnixDomainSocketEndPoint("/tmp/mysocket");
var server = new Socket(AddressFamily.Unix, SocketType.Stream, ProtocolType.Unspecified);
server.Bind(listener);
server.Listen(10);

var client = await server.AcceptAsync();
// общение через SendAsync/ReceiveAsync
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| `new HttpClient()` в методе | Socket exhaustion, TIME_WAIT | `IHttpClientFactory`, `AddHttpClient` |
| Отсутствие Timeout | Зависшие запросы вечно | Всегда `Timeout` в HttpClient или Polly Timeout |
| Retry без jitter | Thundering herd при восстановлении | Добавляйте `Random.Next()` к задержке |
| Circuit Breaker не сбрасывается | Сервис не восстанавливается | Проверьте `onReset`, логируйте состояние |
| gRPC без `Grpc.Net.Client` | Не работает в браузере/HTTP/1.1 | Используйте `Grpc.Net.Client` + `Grpc.AspNetCore` |
| WebSockets без отмены | Утечки при разрыве | Всегда передавайте `CancellationToken` |
| Rate Limiter без `QueueLimit` | Неограниченная очередь = OOM | Всегда ставьте `QueueLimit` |

## 🛠 Практика

1. Настройте `IHttpClientFactory` с Typed Client, Polly Retry (3 раза, экспоненциальный backoff + jitter), Circuit Breaker, Timeout.
2. Создайте gRPC сервис с unary, server streaming, client streaming, bidi методами. Протестируйте клиент.
3. Реализуйте SignalR Hub для чата с комнатами (Groups). Напишите C# клиент.
4. Настройте Rate Limiting: Sliding Window 100 req/min, Token Bucket для burst.
5. Напишите Named Pipe сервер и клиент для IPC между двумя процессами.

## 📌 Кратко

- **HttpClient** — только через `IHttpClientFactory` (Typed/Named/Default), пулинг, DNS refresh
- **Polly** — Retry (backoff + jitter), Circuit Breaker, Timeout, Bulkhead, Fallback, PolicyWrap
- **gRPC** — protobuf, 4 типа RPC, interceptors, code-first (.NET 7+)
- **WebSockets/SignalR** — SignalR проще, авто-переподключение, Groups
- **Rate Limiting** — Fixed/Sliding Window, Token Bucket, Concurrency, всегда QueueLimit
- **IPC** — Named Pipes (cross-platform), Unix Domain Sockets (Linux, fast)

## 🔗 Ссылки

- HttpClient: https://learn.microsoft.com/dotnet/architecture/microservices/implement-resilient-applications/use-httpclientfactory-to-implement-resilient-http-requests
- Polly: https://github.com/App-vNext/Polly
- gRPC: https://learn.microsoft.com/aspnet/core/grpc/
- SignalR: https://learn.microsoft.com/aspnet/core/signalr/
- Rate Limiting: https://learn.microsoft.com/dotnet/core/extensions/rate-limiting
"""

# ============================================================
# LESSON 28: Security
# ============================================================
lesson_28_md = """## 🎯 Что вы узнаете
- Аутентификация: Cookie, JWT, OAuth2, OpenID Connect, Azure AD, IdentityServer
- Авторизация: `[Authorize]`, Policies, Requirements/Handlers, Claims, Resource-based
- Криптография: `Aes`, `RSA`, `HMACSHA256`, `Rfc2898DeriveBytes` (PBKDF2), `Argon2`
- Data Protection API: защита данных, ключи, purpose chains
- Безопасность веба: CSRF, XSS, CSP, HSTS, Anti-forgery, Secure Headers

## 🔐 Аутентификация в ASP.NET Core

### Cookie Authentication (традиционная)

```csharp
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options => {
        options.LoginPath = "/Account/Login";
        options.LogoutPath = "/Account/Logout";
        options.AccessDeniedPath = "/Account/AccessDenied";
        options.ExpireTimeSpan = TimeSpan.FromHours(8);
        options.SlidingExpiration = true;
        options.Cookie.HttpOnly = true;
        options.Cookie.SecurePolicy = CookieSecurePolicy.Always; // только HTTPS
        options.Cookie.SameSite = SameSiteMode.Strict; // CSRF защита
    });
```

### JWT Bearer (Stateless, для API)

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => {
        options.TokenValidationParameters = new TokenValidationParameters {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = "myapp",
            ValidAudience = "myapp-client",
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes("super-secret-key-min-256-bits!")),
            ClockSkew = TimeSpan.FromMinutes(1)
        };
        
        // Для SignalR / WebSockets — чтение токена из query string
        options.Events = new JwtBearerEvents {
            OnMessageReceived = context => {
                var accessToken = context.Request.Query["access_token"];
                var path = context.HttpContext.Request.Path;
                if (!string.IsNullOrEmpty(accessToken) && path.StartsWithSegments("/hubs")) {
                    context.Token = accessToken;
                }
                return Task.CompletedTask;
            }
        };
    });
```

### Генерация JWT

```csharp
public class JwtTokenService {
    private readonly IConfiguration _config;
    
    public string GenerateToken(User user, IEnumerable<string> roles) {
        var claims = new List<Claim> {
            new(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
            new(JwtRegisteredClaimNames.Email, user.Email),
            new(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new(ClaimTypes.Name, user.UserName)
        };
        claims.AddRange(roles.Select(r => new Claim(ClaimTypes.Role, r)));
        
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_config["Jwt:Key"]!));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);
        
        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddHours(1),
            signingCredentials: creds
        );
        
        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
```

### OAuth2 / OpenID Connect (Google, GitHub, Azure AD)

```csharp
builder.Services.AddAuthentication()
    .AddCookie()
    .AddGoogle(options => {
        options.ClientId = config["Google:ClientId"];
        options.ClientSecret = config["Google:ClientSecret"];
        options.Scope.Add("email");
        options.Scope.Add("profile");
    })
    .AddMicrosoftIdentityWebApp(config.GetSection("AzureAd")); // Azure AD

// Или через IdentityServer / Duende
builder.Services.AddAuthentication("Bearer")
    .AddIdentityServerAuthentication("Bearer", options => {
        options.Authority = "https://identityserver";
        options.ApiName = "myapi";
    });
```

### ASP.NET Core Identity (User Management)

```csharp
builder.Services.AddDbContext<AppDbContext>(opt => opt.UseNpgsql(connStr));
builder.Services.AddIdentity<User, Role>(options => {
    options.Password.RequireDigit = true;
    options.Password.RequiredLength = 8;
    options.Password.RequireNonAlphanumeric = true;
    options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);
    options.Lockout.MaxFailedAccessAttempts = 5;
    options.User.RequireUniqueEmail = true;
    options.SignIn.RequireConfirmedEmail = true;
})
.AddEntityFrameworkStores<AppDbContext>()
.AddDefaultTokenProviders(); // Email confirmation, password reset

// Использование
public class AccountController : ControllerBase {
    private readonly UserManager<User> _userManager;
    private readonly SignInManager<User> _signInManager;
    
    [HttpPost("register")]
    public async Task<IActionResult> Register(RegisterDto dto) {
        var user = new User { UserName = dto.Email, Email = dto.Email };
        var result = await _userManager.CreateAsync(user, dto.Password);
        if (!result.Succeeded) return BadRequest(result.Errors);
        
        await _userManager.AddToRoleAsync(user, "User");
        // Send confirmation email...
        return Ok();
    }
    
    [HttpPost("login")]
    public async Task<IActionResult> Login(LoginDto dto) {
        var result = await _signInManager.PasswordSignInAsync(dto.Email, dto.Password, dto.RememberMe, lockoutOnFailure: true);
        if (result.Succeeded) return Ok();
        if (result.IsLockedOut) return StatusCode(429, "Account locked");
        return Unauthorized();
    }
}
```

## 🛡 Авторизация — Policies и Requirements

### Простая авторизация

```csharp
[Authorize] // Требует аутентификацию
[Authorize(Roles = "Admin,Manager")] // Роли
[Authorize(Policy = "RequireAdminRole")] // Политика
```

### Политики (Policies)

```csharp
builder.Services.AddAuthorization(options => {
    // Простая политика по роли
    options.AddPolicy("RequireAdminRole", policy => 
        policy.RequireRole("Admin"));
    
    // По claim
    options.AddPolicy("CanDeleteUsers", policy =>
        policy.RequireClaim("permission", "users.delete"));
    
    // Несколько требований (И)
    options.AddPolicy("SeniorAdmin", policy =>
        policy.RequireRole("Admin")
              .RequireClaim("department", "IT")
              .RequireAssertion(ctx => ctx.User.HasClaim(c => c.Type == "security_level" && int.Parse(c.Value) >= 5)));
    
    // Кастомное требование
    options.AddPolicy("MinimumAge", policy =>
        policy.Requirements.Add(new MinimumAgeRequirement(18)));
});

// Регистрация обработчика
builder.Services.AddScoped<IAuthorizationHandler, MinimumAgeHandler>();
```

### Кастомные Requirements и Handlers

```csharp
// Требование
public class MinimumAgeRequirement : IAuthorizationRequirement {
    public int MinimumAge { get; }
    public MinimumAgeRequirement(int minimumAge) => MinimumAge = minimumAge;
}

// Обработчик
public class MinimumAgeHandler : AuthorizationHandler<MinimumAgeRequirement> {
    protected override Task HandleRequirementAsync(AuthorizationHandlerContext context, MinimumAgeRequirement requirement) {
        var dobClaim = context.User.FindFirst(ClaimTypes.DateOfBirth);
        if (dobClaim != null && DateTime.TryParse(dobClaim.Value, out var dob)) {
            var age = DateTime.Today.Year - dob.Year;
            if (dob > DateTime.Today.AddYears(-age)) age--;
            if (age >= requirement.MinimumAge) context.Succeed(requirement);
        }
        return Task.CompletedTask;
    }
}

// Resource-based authorization (на уровне объекта)
public class DocumentAuthorizationHandler : AuthorizationHandler<OperationAuthorizationRequirement, Document> {
    protected override Task HandleRequirementAsync(AuthorizationHandlerContext context, OperationAuthorizationRequirement requirement, Document resource) {
        if (requirement.Name == "Read" && resource.IsPublic) context.Succeed(requirement);
        if (requirement.Name == "Edit" && resource.OwnerId == GetUserId(context.User)) context.Succeed(requirement);
        if (requirement.Name == "Delete" && context.User.IsInRole("Admin")) context.Succeed(requirement);
        return Task.CompletedTask;
    }
}

// Использование
[HttpGet("{id}")]
public async Task<IActionResult> GetDocument(int id) {
    var doc = await _repo.GetAsync(id);
    var authResult = await _authorizationService.AuthorizeAsync(User, doc, "Read");
    if (!authResult.Succeeded) return Forbid();
    return Ok(doc);
}
```

## 🔒 Криптография — правильное использование

### Симметричное шифрование (AES-GCM) — .NET 6+

```csharp
// AES-GCM — аутентифицированное шифрование (confidentiality + integrity)
public static class AesGcmHelper {
    public static (byte[] ciphertext, byte[] nonce, byte[] tag) Encrypt(byte[] plaintext, byte[] key, byte[]? associatedData = null) {
        var nonce = RandomNumberGenerator.GetBytes(12); // 96-bit nonce для GCM
        var tag = new byte[16];
        var ciphertext = new byte[plaintext.Length];
        
        using var aes = new AesGcm(key);
        aes.Encrypt(nonce, plaintext, ciphertext, tag, associatedData);
        
        return (ciphertext, nonce, tag);
    }
    
    public static byte[] Decrypt(byte[] ciphertext, byte[] nonce, byte[] tag, byte[] key, byte[]? associatedData = null) {
        var plaintext = new byte[ciphertext.Length];
        using var aes = new AesGcm(key);
        aes.Decrypt(nonce, ciphertext, tag, plaintext, associatedData);
        return plaintext;
    }
}

// Использование
var key = RandomNumberGenerator.GetBytes(32); // 256-bit key
var (cipher, nonce, tag) = AesGcmHelper.Encrypt(Encoding.UTF8.GetBytes("secret"), key);
var plain = AesGcmHelper.Decrypt(cipher, nonce, tag, key);
```

### Асимметричное шифрование (RSA)

```csharp
// Генерация ключей
using var rsa = RSA.Create(2048);
var publicKey = rsa.ExportSubjectPublicKeyInfoPem();
var privateKey = rsa.ExportPkcs8PrivateKeyPem();

// Шифрование (малые данные, обычно hybrid: RSA для ключа + AES для данных)
public static byte[] EncryptRsa(byte[] data, string publicKeyPem) {
    using var rsa = RSA.Create();
    rsa.ImportFromPem(publicKeyPem);
    return rsa.Encrypt(data, RSAEncryptionPadding.OaepSHA256);
}

public static byte[] DecryptRsa(byte[] data, string privateKeyPem) {
    using var rsa = RSA.Create();
    rsa.ImportFromPem(privateKeyPem);
    return rsa.Decrypt(data, RSAEncryptionPadding.OaepSHA256);
}
```

### Подписание и верификация (RSA/ECDSA)

```csharp
// Подписание
public static byte[] SignData(byte[] data, string privateKeyPem) {
    using var rsa = RSA.Create();
    rsa.ImportFromPem(privateKeyPem);
    return rsa.SignData(data, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
}

// Верификация
public static bool VerifySignature(byte[] data, byte[] signature, string publicKeyPem) {
    using var rsa = RSA.Create();
    rsa.ImportFromPem(publicKeyPem);
    return rsa.VerifyData(data, signature, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
}
```

### Хеширование паролей — PBKDF2 / Argon2

```csharp
// .NET встроенный PBKDF2 (ASP.NET Core Identity использует это)
public static string HashPassword(string password) {
    // Identity использует PBKDF2 с HMACSHA256, 100000 итераций
    return new PasswordHasher<object>().HashPassword(null!, password);
}

public static bool VerifyPassword(string hashed, string password) {
    var result = new PasswordHasher<object>().VerifyHashedPassword(null!, hashed, password);
    return result == PasswordVerificationResult.Success;
}

// Argon2 (рекомендуется для новых проектов) — требует пакет Konscious.Security.Cryptography.Argon2
// dotnet add package Konscious.Security.Cryptography.Argon2
```

### HMAC — целостность и аутентичность

```csharp
public static string ComputeHmacSha256(string data, string key) {
    var keyBytes = Encoding.UTF8.GetBytes(key);
    var dataBytes = Encoding.UTF8.GetBytes(data);
    
    using var hmac = new HMACSHA256(keyBytes);
    var hash = hmac.ComputeHash(dataBytes);
    return Convert.ToBase64String(hash);
}

public static bool VerifyHmac(string data, string key, string expectedHmac) {
    var actual = ComputeHmacSha256(data, key);
    // Constant-time comparison!
    return CryptographicOperations.FixedTimeEquals(
        Encoding.UTF8.GetBytes(actual), 
        Encoding.UTF8.GetBytes(expectedHmac));
}
```

## 🛡 Data Protection API — защита данных в ASP.NET Core

### Настройка

```csharp
builder.Services.AddDataProtection()
    .PersistKeysToFileSystem(new DirectoryInfo("/app/keys")) // или Azure Blob, Redis
    .SetApplicationName("MyApp")
    .SetDefaultKeyLifetime(TimeSpan.FromDays(90))
    .ProtectKeysWithDpapi(); // Windows: DPAPI, Linux: нет (или Azure Key Vault)
```

### Использование

```csharp
public class TokenProtector {
    private readonly IDataProtector _protector;
    
    public TokenProtector(IDataProtectionProvider provider) {
        _protector = provider.CreateProtector("MyApp.Tokens.v1"); // purpose chain
    }
    
    public string Protect(string data) => _protector.Protect(data);
    public string Unprotect(string protectedData) => _protector.Unprotect(protectedData);
    
    // С ограничением по времени
    public string ProtectWithExpiry(string data, TimeSpan lifetime) 
        => _protector.ToTimeLimitedDataProtector().Protect(data, lifetime);
    
    public string UnprotectWithExpiry(string protectedData) 
        => _protector.ToTimeLimitedDataProtector().Unprotect(protectedData);
}
```

**Применения**: CSRF токены, password reset токены, email confirmation, шифрование query string параметров.

## 🌐 Веб-безопасность — заголовки и защита

### Security Headers Middleware

```csharp
app.Use(async (context, next) => {
    context.Response.Headers["X-Content-Type-Options"] = "nosniff";
    context.Response.Headers["X-Frame-Options"] = "DENY";
    context.Response.Headers["X-XSS-Protection"] = "1; mode=block";
    context.Response.Headers["Referrer-Policy"] = "strict-origin-when-cross-origin";
    context.Response.Headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()";
    context.Response.Headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'";
    context.Response.Headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload";
    await next();
});
```

### Anti-forgery (CSRF защита)

```csharp
// Автоматически для Razor Pages / MVC с Form
builder.Services.AddAntiforgery(options => {
    options.HeaderName = "X-CSRF-TOKEN";
    options.Cookie.Name = "__RequestVerificationToken";
    options.Cookie.HttpOnly = true;
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
    options.Cookie.SameSite = SameSiteMode.Strict;
});

// В контроллере
[HttpPost]
[ValidateAntiForgeryToken] // или [AutoValidateAntiforgeryToken] для всех unsafe методов
public IActionResult Submit(FormModel model) { ... }

// Для SPA (React/Vue) — чтение токена из cookie и отправка в заголовке
```

### Защита от Open Redirect

```csharp
[HttpGet("login")]
public IActionResult Login(string returnUrl) {
    if (!Url.IsLocalUrl(returnUrl)) returnUrl = "/"; // Только локальные URL!
    return View(new LoginViewModel { ReturnUrl = returnUrl });
}
```

## ⚠️ Типичные ошибки

| Ошибка | Проблема | Решение |
|---|---|---|
| Хранение паролей в открытом виде | Утечка → компромисс всех аккаунтов | Всегда `PasswordHasher` / Argon2 |
| Секретный ключ JWT в коде / Git | Компрометация токенов | User Secrets / Key Vault / Environment Variables |
| Отсутствие `ValidateLifetime` в JWT | Токены никогда не истекают | Всегда `ValidateLifetime = true`, `ClockSkew` минимальный |
| `SameSite=Lax` для auth cookie | CSRF уязвимость | `SameSite=Strict` или `Lax` + Anti-forgery |
| Отсутствие CSP | XSS уязвимости | Настройте `Content-Security-Policy` |
| Ручная криптография (AES без GCM) | Нет integrity, уязвимости padding oracle | Используйте `AesGcm` / `ChaCha20Poly1305` |
| `FixedTimeEquals` не используется | Timing attacks на HMAC/токены | Всегда `CryptographicOperations.FixedTimeEquals` |

## 🛠 Практика

1. Настройте JWT аутентификацию с Refresh Tokens (хранить в HttpOnly cookie, access token в памяти).
2. Реализуйте Policy-based авторизацию: `CanEditDocument` с Resource-based handler.
3. Зашифруйте чувствительные данные (PII) через Data Protection API с purpose chain.
4. Настройте Security Headers middleware: CSP, HSTS, X-Frame-Options, Permissions-Policy.
5. Реализуйте HMAC подпись для вебхуков (проверка `X-Signature` заголовка).

## 📌 Кратко

- **AuthN**: Cookie (web), JWT (API), OAuth2/OIDC (Google, Azure AD), Identity (user mgmt)
- **AuthZ**: `[Authorize]`, Policies (Role, Claim, Custom Requirement), Resource-based
- **Crypto**: AES-GCM (симметричное), RSA/OAEP (асимметричное), PBKDF2/Argon2 (пароли), HMAC (integrity)
- **Data Protection** — ключи, purpose chains, time-limited, для токенов/CSRF/PII
- **Web Security**: CSP, HSTS, Anti-forgery, SameSite, Secure Headers, Open Redirect protection

## 🔗 Ссылки

- ASP.NET Core Auth: https://learn.microsoft.com/aspnet/core/security/authentication/
- Authorization: https://learn.microsoft.com/aspnet/core/security/authorization/
- Data Protection: https://learn.microsoft.com/aspnet/core/security/data-protection/
- Cryptography: https://learn.microsoft.com/dotnet/standard/security/
- OWASP: https://owasp.org/www-project-top-ten/
"""

# ============================================================
# LESSON 29: Observability
# ============================================================
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

# Write lessons 27 and 28
lesson_27_data = {
    "title": "Урок 27: Сетевое программирование — HttpClient, Sockets, gRPC, WebSockets, SignalR",
    "slug": "lesson-27",
    "short_description": "HttpClient, IHttpClientFactory, Polly, Sockets, Named Pipes, gRPC, WebSockets, SignalR, Rate Limiting",
    "goals": [
        "Правильно использовать HttpClient через IHttpClientFactory",
        "Настраивать Polly политики: Retry, Circuit Breaker, Timeout, Bulkhead",
        "Работать с гRPC: protobuf, code-first, contract-first, streaming",
        "Использовать WebSockets и SignalR для real-time",
        "Применять Rate Limiting и throttling"
    ],
    "content_md": lesson_27_md,
    "practice_tasks": [
        "Настройте `IHttpClientFactory` с Typed Client, Polly Retry (3 раза, экспоненциальный backoff + jitter), Circuit Breaker, Timeout.",
        "Создайте gRPC сервис с unary, server streaming, client streaming, bidi методами. Протестируйте клиент.",
        "Реализуйте SignalR Hub для чата с комнатами (Groups). Напишите C# клиент.",
        "Настройте Rate Limiting: Sliding Window 100 req/min, Token Bucket для burst.",
        "Напишите Named Pipe сервер и клиент для IPC между двумя процессами."
    ],
    "common_errors": [
        {"mistake": "`new HttpClient()` в методе", "correct": "`IHttpClientFactory`, `AddHttpClient`"},
        {"mistake": "Отсутствие Timeout", "correct": "Всегда `Timeout` в HttpClient или Polly Timeout"},
        {"mistake": "Retry без jitter", "correct": "Добавляйте `Random.Next()` к задержке"},
        {"mistake": "Circuit Breaker не сбрасывается", "correct": "Проверьте `onReset`, логируйте состояние"},
        {"mistake": "gRPC без `Grpc.Net.Client`", "correct": "Используйте `Grpc.Net.Client` + `Grpc.AspNetCore`"},
        {"mistake": "WebSockets без отмены", "correct": "Всегда передавайте `CancellationToken`"},
        {"mistake": "Rate Limiter без `QueueLimit`", "correct": "Всегда ставьте `QueueLimit`"}
    ],
    "resources": [
        "HttpClient: https://learn.microsoft.com/dotnet/architecture/microservices/implement-resilient-applications/use-httpclientfactory-to-implement-resilient-http-requests",
        "Polly: https://github.com/App-vNext/Polly",
        "gRPC: https://learn.microsoft.com/aspnet/core/grpc/",
        "SignalR: https://learn.microsoft.com/aspnet/core/signalr/",
        "Rate Limiting: https://learn.microsoft.com/dotnet/core/extensions/rate-limiting"
    ],
    "key_takeaways": [
        "HttpClient — только через IHttpClientFactory (Typed/Named/Default), пулинг, DNS refresh",
        "Polly — Retry (backoff + jitter), Circuit Breaker, Timeout, Bulkhead, Fallback, PolicyWrap",
        "gRPC — protobuf, 4 типа RPC, interceptors, code-first (.NET 7+)",
        "WebSockets/SignalR — SignalR проще, авто-переподключение, Groups",
        "Rate Limiting — Fixed/Sliding Window, Token Bucket, Concurrency, всегда QueueLimit",
        "IPC — Named Pipes (cross-platform), Unix Domain Sockets (Linux, fast)"
    ],
    "estimated_minutes": 50,
    "language_slug": "csharp",
    "lesson_order": 27,
    "name_en": "Lesson: Networking, HTTP, gRPC",
    "short_description_en": "HttpClient, IHttpClientFactory, Polly, gRPC, WebSockets, SignalR, Rate Limiting"
}

lesson_28_data = {
    "title": "Урок 28: Безопасность — Authentication, Authorization, JWT, OAuth2, OpenID Connect, Crypto, Data Protection",
    "slug": "lesson-28",
    "short_description": "ASP.NET Core Identity, JWT, OAuth2/OIDC, Policies, Claims, Crypto, Data Protection API, Anti-forgery, Rate Limiting",
    "goals": [
        "Настроить аутентификацию: Cookie, JWT, OAuth2, OpenID Connect, Azure AD, IdentityServer",
        "Реализовать авторизацию: Policies, Requirements, Handlers, Claims-based, Resource-based",
        "Работать с криптографией: AES, RSA, HMAC, Hashing, PBKDF2, Data Protection API",
        "Защитить от CSRF, XSS, Clickjacking, Open Redirect",
        "Применять Rate Limiting, IP filtering, Security Headers"
    ],
    "content_md": lesson_28_md,
    "practice_tasks": [
        "Настройте JWT аутентификацию с Refresh Tokens (хранить в HttpOnly cookie, access token в памяти).",
        "Реализуйте Policy-based авторизацию: `CanEditDocument` с Resource-based handler.",
        "Зашифруйте чувствительные данные (PII) через Data Protection API с purpose chain.",
        "Настройте Security Headers middleware: CSP, HSTS, X-Frame-Options, Permissions-Policy.",
        "Реализуйте HMAC подпись для вебхуков (проверка `X-Signature` заголовка)."
    ],
    "common_errors": [
        {"mistake": "Хранение паролей в открытом виде", "correct": "Всегда `PasswordHasher` / Argon2"},
        {"mistake": "Секретный ключ JWT в коде / Git", "correct": "User Secrets / Key Vault / Environment Variables"},
        {"mistake": "Отсутствие `ValidateLifetime` в JWT", "correct": "Всегда `ValidateLifetime = true`, `ClockSkew` минимальный"},
        {"mistake": "`SameSite=Lax` для auth cookie", "correct": "`SameSite=Strict` или `Lax` + Anti-forgery"},
        {"mistake": "Отсутствие CSP", "correct": "Настройте `Content-Security-Policy`"},
        {"mistake": "Ручная криптография (AES без GCM)", "correct": "Используйте `AesGcm` / `ChaCha20Poly1305`"},
        {"mistake": "`FixedTimeEquals` не используется", "correct": "Всегда `CryptographicOperations.FixedTimeEquals`"}
    ],
    "resources": [
        "ASP.NET Core Auth: https://learn.microsoft.com/aspnet/core/security/authentication/",
        "Authorization: https://learn.microsoft.com/aspnet/core/security/authorization/",
        "Data Protection: https://learn.microsoft.com/aspnet/core/security/data-protection/",
        "Cryptography: https://learn.microsoft.com/dotnet/standard/security/",
        "OWASP: https://owasp.org/www-project-top-ten/"
    ],
    "key_takeaways": [
        "AuthN: Cookie (web), JWT (API), OAuth2/OIDC (Google, Azure AD), Identity (user mgmt)",
        "AuthZ: [Authorize], Policies (Role, Claim, Custom Requirement), Resource-based",
        "Crypto: AES-GCM (симметричное), RSA/OAEP (асимметричное), PBKDF2/Argon2 (пароли), HMAC (integrity)",
        "Data Protection — ключи, purpose chains, time-limited, для токенов/CSRF/PII",
        "Web Security: CSP, HSTS, Anti-forgery, SameSite, Secure Headers, Open Redirect protection"
    ],
    "estimated_minutes": 55,
    "language_slug": "csharp",
    "lesson_order": 28,
    "name_en": "Lesson: Security — Auth, AuthZ, Crypto",
    "short_description_en": "Authentication, Authorization, JWT, OAuth2, OpenID Connect, Crypto, Data Protection"
}

write_lesson(27, lesson_27_data)
write_lesson(28, lesson_28_data)

print("Lessons 27-28 written!")