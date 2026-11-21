#!/usr/bin/env python3
"""
Enhance C# lessons 15-33 with:
- Real-world usage comments on code blocks
- Term definitions in SAFE locations (not in tables, code, headings)
- Better explanations
"""

import json
import re

TERM_DEFINITIONS = {
    "IEnumerable": "**IEnumerable** — базовый интерфейс для перечисления коллекций. Позволяет использовать foreach и LINQ. Не содержит данные — только умеет давать итератор.",
    "IQueryable": "**IQueryable** — расширяет IEnumerable, добавляя Expression Trees. Позволяет переводить LINQ в SQL (EF Core). Выполняется на сервере БД.",
    "Deferred Execution": "**Отложенное выполнение (Deferred Execution)** — LINQ запрос не выполняется при создании, а только при переборе (foreach, ToList). Позволяет строить запросы цепочкой.",
    "Materialization": "**Материализация** — принудительное выполнение отложенного запроса через ToList(), ToArray(), Count() и сохранение результата в коллекцию.",
    "Streaming": "**Streaming операторы** (Where, Select) — обрабатывают элементы по одному, память O(1). Не читают всю коллекцию сразу.",
    "Buffering": "**Buffering операторы** (OrderBy, GroupBy) — читают всю коллекцию в память O(n) для работы.",
    "Expression Tree": "**Expression Tree (Дерево выражений)** — структура данных, представляющая код как дерево. EF Core анализирует её и генерирует SQL.",
    "Closure": "**Замыкание (Closure)** — лямбда запоминает переменные из внешней области видимости. В циклах все лямбды могут ссылаться на одну переменную — нужно создавать локальную копию.",
    "ValueTask": "**ValueTask** — структура (value type), не аллоцирует память если результат уже есть (кэш). Можно await только ОДИН раз.",
    "CancellationToken": "**CancellationToken** — токен для кооперативной отмены операций. Передается во все async методы. ThrowIfCancellationRequested() бросает OperationCanceledException.",
    "ConfigureAwait": "**ConfigureAwait(false)** — продолжение после await выполняется в ThreadPool, а не в исходном контексте (UI/ASP.NET). В библиотеках — всегда false.",
    "Deadlock": "**Deadlock (взаимная блокировка)** — поток ждёт завершения задачи, а задача ждёт освобождения этого потока. В UI/.NET Framework: .Result блокирует UI поток, async ждёт UI контекст.",
    "ThreadPool": "**ThreadPool** — пул потоков .NET для выполнения работы. Не создавайте свои Thread — дорого. async/await использует пул автоматически.",
    "SynchronizationContext": "**SynchronizationContext** — контекст синхронизации (UI поток в WPF, запрос в ASP.NET classique). await по умолчанию возвращается в него.",
    "Span": "**Span<T>** — ref struct, только стек, нулевые аллокации для срезов массивов/строк. Не может быть полем класса или в async.",
    "Memory": "**Memory<T>** — как Span, но может быть на куче, поддерживает async. Memory<byte> для чтения из Stream без копирований.",
    "ArrayPool": "**ArrayPool<T>** — пул массивов для избежания аллокаций и LOH фрагментации. Rent/Return.",
    "LOH": "**Large Object Heap (LOH)** — куча для объектов ≥ 85 KB. Не компактируется (до .NET 5), фрагментируется. Избегайте больших массивов в циклах.",
    "GC": "**Garbage Collector (Сборщик мусора)** — автоматическое управление памятью. Поколенческий: Gen 0/1 (эфимерные), Gen 2 (долгоживущие).",
    "Gen 0": "**Generation 0** — новые объекты, малый размер (~256 KB), очень частые сборки (миллионы в сек).",
    "Gen 1": "**Generation 1** — объекты выжившие после Gen 0, буфер перед Gen 2.",
    "Gen 2": "**Generation 2** — долгоживущие объекты, собирается редко (Full GC).",
    "IDisposable": "**IDisposable** — интерфейс для детерминированного освобождения ресурсов. Паттерн: Dispose(bool), GC.SuppressFinalize.",
    "Finalizer": "**Финализатор (~ClassName)** — вызывается GC перед удалением. Негарантированно, может не вызвать. Только для unmanaged ресурсов БЕЗ SafeHandle.",
    "SafeHandle": "**SafeHandle** — правильный wrapper для unmanaged дескрипторов. Наследует CriticalFinalizerObject — гарантированный финализатор.",
    "WeakReference": "**WeakReference** — слабая ссылка, не удерживает объект от GC. TryGetTarget проверяет жив ли объект.",
    "ConditionalWeakTable": "**ConditionalWeakTable** — таблица с слабыми ключами (ephemeron). Значение живо пока жив ключ. Для аттачментов к чужим объектам.",
    "GCHandle": "**GCHandle** — низкоуровневая ручка для pinning (закрепления объекта в памяти для interop). Обязателен Free().",
    "Covariance": "**Ковариантность (out)** — можно использовать более конкретный тип там где ожидается общий. Только для выходных позиций (return, get). IEnumerable<out T>.",
    "Contravariance": "**Контравариантность (in)** — можно использовать более общий тип там где ожидается конкретный. Только для входных позиций (параметры, set). IComparer<in T>.",
    "Pattern Matching": "**Pattern Matching** — проверка формы данных и извлечение значений. Switch expressions, property patterns, list patterns.",
    "Record": "**Record** — immutable reference/value type с value equality, with-expressions, деконструкцией. Автоматические Equals/GetHashCode/ToString.",
    "Primary Constructor": "**Primary Constructor** — параметры конструктора становятся полями (C# 12 для class/struct).",
    "Required": "**required** — свойство ОБЯЗАТЕЛЬНО к инициализации в object initializer (C# 11). Компилятор выдаст ошибку если не задано.",
    "init": "**init** — setter только для инициализации объекта (C# 9). После — нечитаем.",
    "Source Generator": "**Source Generator** — генерация .cs файлов на этапе компиляции. Работает в NativeAOT, без рефлексии.",
    "Reflection": "**Reflection** — инспекция типов в runtime (Type, MethodInfo). Медленно — кэшируйте MemberInfo или компилируйте в делегаты.",
    "Expression.Compile": "**Expression.Compile()** — компилирует дерево выражений в делегат в runtime. Кэшируйте результат!",
    "DynamicMethod": "**DynamicMethod** — ручная генерация IL в runtime. Максимальная скорость, skipVisibility: true для private.",
    "IHttpClientFactory": "**IHttpClientFactory** — фабрика HttpClient с пулингом соединений, DNS refresh, middleware pipeline. Не создавайте new HttpClient() вручную!",
    "Polly": "**Polly** — библиотека resilience: Retry, Circuit Breaker, Timeout, Bulkhead, Fallback. Работает через PolicyWrap.",
    "Circuit Breaker": "**Circuit Breaker** — после N ошибок «переключает» цепь в открытое состояние, быстро падает без вызовов. Через время — half-open для проверки.",
    "Bulkhead": "**Bulkhead (пушковое отсек)** — ограничение параллелизма. SemaphoreSlim или Polly Bulkhead. Защита от каскадных сбоев.",
    "gRPC": "**gRPC** — высокопроизводительный RPC на HTTP/2 + Protobuf. 4 типа: Unary, Server Streaming, Client Streaming, Bidi Streaming.",
    "Protobuf": "**Protobuf** — Protocol Buffers — бинарная сериализация, схема в .proto файлах. Меньше JSON, быстрее, строгая схема.",
    "SignalR": "**SignalR** — real-time двусторонняя связь. Автоматически выбирает транспорт (WebSockets, Server-Sent Events, Long Polling). Groups, Auto-reconnect.",
    "Rate Limiting": "**Rate Limiting** — ограничение запросов. Fixed/Sliding Window, Token Bucket, Concurrency. Обязателен QueueLimit.",
    "MediatR": "**MediatR** — in-process mediator для CQRS. Commands/Queries → Handlers. Pipeline Behaviors для cross-cutting (валидация, транзакции, логирование).",
    "CQRS": "**CQRS (Command Query Responsibility Segregation)** — разделение чтения и записи. Commands (меняют состояние) / Queries (только чтение). Разные модели.",
    "Aggregate Root": "**Aggregate Root** — корень агрегата в DDD. Гарантирует инварианты внутри границ агрегата. Единственная точка входа для изменений.",
    "Value Object": "**Value Object** — объект без идентичности, равенство по значениям. Immutable. Email, Money, Address.",
    "Domain Event": "**Domain Event** — событие внутри домена (OrderPlaced). Публикуется после SaveChanges через Outbox pattern для надежности.",
    "Outbox Pattern": "**Outbox Pattern** — сохранение Domain Events в таблицу Outbox в ТОЙ ЖЕ транзакции что и бизнес-данные. Фоновый процесс публикует в брокер.",
    "Event Sourcing": "**Event Sourcing** — состояние агрегата хранится не как снэпшот, а как последовательность событий. Полный аудит, проекции для чтения.",
    "Saga": "**Saga** — распределенная транзакция через цепочку локальных транзакций с компенсацией при ошибке. Все шаги идемпотентны.",
    "Actor Model": "**Actor Model** — модель параллельности: акторы (state + behavior) общаются асинхронными сообщениями. Нет shared state.",
    "Orleans Grain": "**Orleans Grain (Virtual Actor)** — виртуальный актор с авто-активацией/деактивацией. Персистенция состояния, reminders, streams.",
    "Rx.NET": "**Rx.NET (Reactive Extensions)** — IObservable/IObserver для push-последовательностей. Операторы: Select, Where, Merge, CombineLatest, Throttle. Backpressure через Buffer/Window.",
    "IObservable": "**IObservable<T>** — «продюсер» событий. Subscribe возвращает IDisposable для отписки. Горячий/холодный.",
    "Backpressure": "**Backpressure** — контроль скорости: когда продюсер быстрее консьюмера. Buffer, Window, Throttle, или IAsyncEnumerable.",
    "Docker Multi-stage": "**Multi-stage Dockerfile** — несколько FROM. Build stage (SDK) → Runtime stage (ASP.NET runtime, distroless). Меньший образ, кэширование слоев.",
    "Distroless": "**Distroless** — минимальный образ без shell, пакетного менеджера, лишних уязвимостей. Только runtime.",
    "Kubernetes HPA": "**Horizontal Pod Autoscaler (HPA)** — автоскалинг подов по CPU, памяти или кастомным метрикам (Prometheus).",
    "Helm": "**Helm** — пакетный менеджер Kubernetes. Charts с values.yaml, зависимостями, шаблонами. Release management.",
    "Kustomize": "**Kustomize** — нативный K8s способ кастомизации манифестов. Base + overlays, patches. Без шаблонизации.",
    "Service Mesh": "**Service Mesh (Istio/Linkerd)** — инфраструктурный слой для mTLS, traffic splitting, observability, rate limiting. Sidecar proxy.",
    "mTLS": "**Mutual TLS (mTLS)** — двусторонняя аутентификация сервисов. Сертификаты выдает mesh автоматически.",
    "GitOps": "**GitOps** — desired state в Git, агент (ArgoCD/Flux) синхронизирует кластер. Аудит, rollback = git revert.",
    "NativeAOT": "**NativeAOT** — компиляция в нативный бинарь без JIT, IL. Маленький размер, быстрый старт. Ограничения: нет рефлексии, динамических сборок.",
    "PGO": "**Profile-Guided Optimization** — оптимизация на основе профиля реальной нагрузки. Dynamic PGO (TieredPGO) — просто включите в .csproj.",
    "SIMD": "**SIMD (Single Instruction Multiple Data)** — одна инструкция над вектором данных. Vector, HardwareIntrinsics (AVX2/SSE/NEON). Ускорение математики в разы.",
    "BenchmarkDotNet": "**BenchmarkDotNet** — золотой стандарт микробенчмарков. MemoryDiagnoser, DisassemblyDiagnoser, параметризация, статистика.",
    "dotnet-trace": "**dotnet-trace** — ETW профилировщик. Собирает .nettrace, конвертирует в speedscope для веб-визуализации.",
    "OpenTelemetry": "**OpenTelemetry** — стандарт observability: Metrics, Logs, Traces. Экспорт в Prometheus, Jaeger, Zipkin, Grafana.",
    "W3C TraceContext": "**W3C TraceContext** — стандарт заголовков трассировки: traceparent, tracestate, baggage. Распространение контекста между сервисами.",
}

# Terms that should NOT be auto-injected (too common, cause issues)
SKIP_TERMS = {
    "IEnumerable",  # appears too often
    "IQueryable",
    "Task",  # too common
    "Record",  # common word
    "Pattern",  # common word
    "Memory",  # common word
    "Span",  # common word
    "Reflection",  # common word
    "Deadlock",  # will add manually
    "CancellationToken",  # will add manually
}

def load_lesson(lesson_num):
    path = f"/Users/xiip.shk/работа/Kernify/fixtures/lessons/csharp/{lesson_num}.json"
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_lesson(lesson_num, data):
    path = f"/Users/xiip.shk/работа/Kernify/fixtures/lessons/csharp/{lesson_num}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_code_context(block):
    """Add real-world usage comments to code blocks"""
    if block['type'] != 'code':
        return block
    
    code = block.get('content', '')
    lang = block.get('language', '')
    
    # Detect patterns and add context comments
    contexts = []
    
    # C# patterns
    if lang in ['csharp', 'c#']:
        if 'IEnumerable' in code or 'IQueryable' in code:
            contexts.append("Используется: LINQ to Objects (IEnumerable в памяти) или EF Core (IQueryable → SQL)")
        if 'await' in code and 'HttpClient' in code:
            contexts.append("Используется: все внешние HTTP вызовы в ASP.NET Core, микросервисы")
        if 'CancellationToken' in code:
            contexts.append("Используется: каждый async метод должен принимать ct для отмены по таймауту/пользователю")
        if 'ConfigureAwait(false)' in code:
            contexts.append("Используется: во всех библиотеках/нижних слоях, чтобы не захватывать SynchronizationContext")
        if 'ValueTask' in code:
            contexts.append("Используется: горячие пути с кэшированием, миллионы вызовов/сек")
        if 'ArrayPool' in code or 'MemoryPool' in code:
            contexts.append("Используется: парсинг больших данных, высоконагруженные API, gRPC streaming")
        if 'record' in code.lower() and ('Record' in code or 'record ' in code):
            contexts.append("Используется: DTO, команды/запросы в MediatR, Value Objects в DDD")
        if 'MediatR' in code or 'IRequestHandler' in code or 'IPipelineBehavior' in code:
            contexts.append("Используется: CQRS слой Application в Clean Architecture")
        if 'SignalR' in code or 'HubConnection' in code or 'IHubContext' in code:
            contexts.append("Используется: real-time уведомления, чаты, дашборды, collaboration")
        if 'Benchmark' in code or 'MemoryDiagnoser' in code:
            contexts.append("Используется: микробенчмарки для критических путей, сравнение алгоритмов")
        if 'Vector<' in code or 'Avx2' in code or 'Sse' in code or 'AdvSimd' in code:
            contexts.append("Используется: математика, обработка изображений, ML, высоконагруженные вычисления")
        if 'AesGcm' in code or 'ChaCha20Poly1305' in code:
            contexts.append("Используется: симметричное шифрование с аутентификацией (confidentiality + integrity)")
        if 'RSA' in code and ('OAEP' in code or 'Pkcs1' in code):
            contexts.append("Используется: асимметричное шифрование/подпись, JWT токены, TLS")
        if 'Task.Run' in code and ('HeavyCompute' in code or 'CPU' in code or '计算' in code):
            contexts.append("Используется: вынос CPU-bound работы из UI/HTTP thread в пул потоков")
        if 'SemaphoreSlim' in code:
            contexts.append("Используется: ограничение параллелизма, rate limiting, bulkhead pattern")
        if 'Parallel.ForEachAsync' in code:
            contexts.append("Используется: параллельная обработка с контролем степени параллелизма (.NET 6+)")
        if 'IAsyncEnumerable' in code:
            contexts.append("Используется: стриминг больших данных, Server-Sent Events, gRPC streaming")
        if 'yield return' in code:
            contexts.append("Используется: ленивые последовательности, iterator паттерн, библиотеки")
        if 'FluentValidation' in code or 'IValidator' in code:
            contexts.append("Используется: валидация команд MediatR, pipeline behaviors")
        if 'OutboxMessage' in code or 'OutboxPattern' in code:
            contexts.append("Используется: надежная публикация Domain Events в микросервисах")
        if 'ActivitySource' in code or 'StartActivity' in code:
            contexts.append("Используется: distributed tracing, observability в микросервисах")
        if 'OpenTelemetry' in code or 'AddMeter' in code:
            contexts.append("Используется: метрики для Prometheus/Grafana")
        if 'Serilog' in code or 'Log.Logger' in code:
            contexts.append("Используется: структурированное логирование с enrichment, sinks")
        if 'ObjectPool' in code:
            contexts.append("Используется: пулинг дорогих объектов (StringBuilder, DbCommand, etc.)")
        if 'stackalloc' in code:
            contexts.append("Используется: малые буферы на стеке, высокая производительность, interop")
        if 'fixed (' in code and 'byte*' in code:
            contexts.append("Используется: pinning для interop, работа с нативными API")
        if 'GCHandle' in code:
            contexts.append("Используется: pinning, weak references, interop, GCHandleType.Pinned")
        if 'DynamicMethod' in code or 'ILGenerator' in code:
            contexts.append("Используется: генерация IL в runtime, максимальная скорость, AOT-совместимые библиотеки")
        if 'Expression<' in code and 'Compile' in code:
            contexts.append("Используется: динамическое построение запросов, Expression Trees")
        if 'Saga' in code and ('compensate' in code.lower() or 'Compensate' in code):
            contexts.append("Используется: распределенные транзакции с компенсацией при ошибке")
        if 'Orleans' in code or 'IGrainWithIntegerKey' in code or 'PersistentState' in code:
            contexts.append("Используется: Virtual Actors, state persistence, clustering, reminders")
        if 'Akka' in code or 'ReceiveActor' in code or 'Persist(' in code:
            contexts.append("Используется: классическая Actor Model, Event Sourcing, supervision")
    
    # Dockerfile patterns
    if lang in ['dockerfile', 'docker']:
        if 'multi-stage' in code.lower() or 'FROM.*AS build' in code:
            contexts.append("Используется: контейнеризация для K8s, Cloud Run, Container Apps — разделение build и runtime")
        if 'distroless' in code.lower():
            contexts.append("Используется: минимальный безопасный runtime образ без shell и пакетного менедже")
        if 'USER 65532' in code:
            contexts.append("Используется: non-root пользователь для безопасности контейнера")
        if 'HEALTHCHECK' in code:
            contexts.append("Используется: Kubernetes liveness/readiness probes")
    
    # YAML patterns
    if lang in ['yaml', 'yml']:
        if 'HorizontalPodAutoscaler' in code or 'autoscaling/v2' in code:
            contexts.append("Используется: автоскалинг подов в Kubernetes по метрикам")
        if 'Deployment' in code and 'replicas' in code:
            contexts.append("Используется: управление подми, rolling updates, rollback")
        if 'Service' in code and 'ClusterIP' in code:
            contexts.append("Используется: внутренняя балансировка нагрузки в K8s кластере")
        if 'Ingress' in code:
            contexts.append("Используется: внешний доступ к сервисам, TLS termination, rate limiting")
        if 'ConfigMap' in code or 'Secret' in code:
            contexts.append("Используется: конфигурация и секреты вне кода приложения")
        if 'Helm' in code or 'Chart.yaml' in code or 'values.yaml' in code:
            contexts.append("Используется: пакетный менеджер Kubernetes для production деплоя")
        if 'kustomization' in code.lower():
            contexts.append("Используется: нативный K8s способ кастомизации манифестов (base + overlays)")
        if 'istio' in code.lower() or 'VirtualService' in code or 'DestinationRule' in code:
            contexts.append("Используется: Service Mesh — mTLS, traffic splitting, observability")
    
    # Bash patterns
    if lang in ['bash', 'sh']:
        if 'dotnet publish' in code and 'DebugType=portable' in code:
            contexts.append("Используется: сборка с символами для профилирования (dotnet-trace, PerfView)")
        if 'dotnet-trace' in code:
            contexts.append("Используется: ETW профилирование CPU/memory в production")
        if 'dotnet-counters' in code:
            contexts.append("Используется: real-time метрики GC, ThreadPool, JIT, ASP.NET Core")
        if 'BenchmarkRunner' in code:
            contexts.append("Используется: запуск микробенчмарков BenchmarkDotNet")
        if 'docker build' in code and 'buildx' in code:
            contexts.append("Используется: multi-arch сборка (amd64/arm64) для K8s")
    
    # Protobuf patterns
    if lang == 'protobuf':
        if 'service' in code and 'rpc' in code:
            contexts.append("Используется: gRPC contract-first API определение")
    
    # Add comments if we found contexts
    if contexts:
        comment_prefix = "// " if lang in ['csharp', 'c#'] else "# "
        if lang in ['yaml', 'yml', 'dockerfile', 'docker', 'protobuf', 'xml']:
            comment_prefix = "# "
        
        context_comment = "\n".join([f"{comment_prefix}{c}" for c in contexts]) + "\n\n"
        
        # Check if already has this comment
        if context_comment.strip() not in code[:200]:
            block['content'] = context_comment + code
    
    return block

def inject_term_definitions_safely(text, injected_terms):
    """Inject term definitions only in safe places - after sentences, not in tables/code/HTML"""
    # Skip if text contains table markdown or HTML tables
    if '|---|' in text or '<table' in text.lower() or '<tr>' in text.lower():
        return text
    
    # Skip headings
    if text.strip().startswith('#') or text.strip().startswith('<h') or re.match(r'^#+ ', text.strip()):
        return text
    
    # For each term not yet injected in this text
    for term, definition in TERM_DEFINITIONS.items():
        if term in SKIP_TERMS:
            continue
        if term in injected_terms:
            continue
        
        # Find term as whole word
        pattern = r'\b' + re.term_regex_escape(term) + r'\b'
        # But also handle terms with angle brackets
        if '<' in term:
            pattern = re.term_regex_escape(term)
        
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Check it's not inside HTML tag
            pos = match.start()
            before = text[max(0, pos-10):pos]
            after = text[pos:pos+20]
            if '<' in before and '>' not in before:
                continue  # inside HTML tag
            
            # Find end of sentence/phrase
            end_pos = match.end()
            # Extend to end of sentence or comma
            while end_pos < len(text) and text[end_pos] not in '.!?,\n':
                end_pos += 1
            
            # Inject definition
            definition_html = f'\n\n> 💡 **Термин:** {definition}\n'
            text = text[:end_pos] + definition_html + text[end_pos:]
            injected_terms.add(term)
            # Only inject 2 terms per text block to avoid clutter
            if len(injected_terms) >= 2:
                break
    
    return text

class term_regex_escape:
    @staticmethod
    def escape(s):
        return re.escape(s)

# Monkey patch
import re as _re
_re.term_regex_escape = _re.escape

def process_lesson(lesson_num):
    print(f"Processing lesson {lesson_num}...")
    data = load_lesson(lesson_num)
    
    # Process content blocks
    new_blocks = []
    terms_injected_in_lesson = set()
    
    for block in data.get('content_blocks', []):
        # Add real-world context to code blocks
        block = add_code_context(block)
        
        # Inject term definitions in text blocks
        if block['type'] == 'text':
            content = block['content']
            content = inject_term_definitions_safely(content, terms_injected_in_lesson)
            block['content'] = content
        
        new_blocks.append(block)
    
    data['content_blocks'] = new_blocks
    
    save_lesson(lesson_num, data)
    print(f"  Saved lesson {lesson_num} (injected terms: {terms_injected_in_lesson})")

def main():
    for lesson_num in range(15, 34):
        process_lesson(lesson_num)
    print("All lessons enhanced!")

if __name__ == "__main__":
    main()