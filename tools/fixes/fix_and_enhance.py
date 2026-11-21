#!/usr/bin/env python3
"""
Fix issues from previous enhancement and re-apply properly:
- Remove duplicate context comments from code blocks
- Remove broken term definitions from text (inside HTML, tables, duplicates)
- Re-apply clean enhancements
"""

import json
import re
from pathlib import Path

def load_lesson(lesson_num):
    path = f"/Users/xiip.shk/работа/Kernify/fixtures/lessons/csharp/{lesson_num}.json"
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_lesson(lesson_num, data):
    path = f"/Users/xiip.shk/работа/Kernify/fixtures/lessons/csharp/{lesson_num}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def clean_code_block(code):
    """Remove duplicate context comments from code blocks"""
    lines = code.split('\n')
    cleaned = []
    seen_comments = set()
    
    for line in lines:
        stripped = line.strip()
        # Check if it's a context comment we added
        if stripped.startswith('// Используется:') or stripped.startswith('# Используется:'):
            if stripped in seen_comments:
                continue  # Skip duplicate
            seen_comments.add(stripped)
        cleaned.append(line)
    
    # Also fix double comments on same line
    result = '\n'.join(cleaned)
    # Remove duplicate consecutive comment lines
    result = re.sub(r'(// Используется:[^\n]*)\n\s*\1', r'\1', result)
    result = re.sub(r'(# Используется:[^\n]*)\n\s*\1', r'\1', result)
    
    return result

def clean_text_block(text):
    """Remove broken term definition injections"""
    # Remove the broken term definition pattern
    # Pattern: > 💡 **Термин:** **...**
    text = re.sub(r'\n\s*>\s*💡\s*\*\*Термин:\*\*[^\n]*\n', '\n', text)
    
    # Remove duplicates that might remain
    # Fix double injection in same sentence
    text = re.sub(r'(> 💡 \*\*Термин:\*\*[^\n]*)\n\s*\1', r'\1', text)
    
    # Clean up any leftover broken HTML from term injection
    # Fix cases where term injection broke headings like <h3>...Deferred Execution</h3>
    text = re.sub(r'(<h[0-9]>)([^<]*?)(> 💡 \*\*Термин:\*\*[^<]*</h[0-9]>)', r'\1\2\3', text)
    
    # Fix broken generic syntax like IEnumerable\n> 💡 **Термин:**...<T>
    text = re.sub(r'(IEnumerable|IQueryable|Span|Memory|ValueTask|Task|List|Dictionary|HashSet|Queue|Stack|LinkedList|ImmutableList|ImmutableDictionary|ImmutableHashSet|ImmutableArray|ImmutableQueue|ImmutableStack|ConcurrentDictionary|ConcurrentBag|ConcurrentQueue|ConcurrentStack|BlockingCollection|ArrayPool|MemoryPool|StringBuilder|StringReader|StringWriter|StreamReader|StreamWriter|FileStream|NetworkStream|PipeReader|PipeWriter|ChannelReader|ChannelWriter)\n\s*>\s*💡\s*\*\*Термин:\*\*[^<]*?(?=<|T>)', r'\1', text)
    
    # Fix broken terms in tables - remove any term definition in table rows
    lines = text.split('\n')
    cleaned = []
    in_table = False
    for line in lines:
        if '|---|' in line:
            in_table = True
        if in_table and line.strip().startswith('|'):
            # Remove term definitions from table cells
            line = re.sub(r'\s*>\s*💡\s*\*\*Термин:\*\*[^|]*', '', line)
        elif in_table and not line.strip().startswith('|'):
            in_table = False
        cleaned.append(line)
    
    return '\n'.join(cleaned)

# Term definitions - cleaner versions
TERM_DEFINITIONS = {
    "Deferred Execution": "LINQ запрос не выполняется при создании, а только при переборе (foreach, ToList). Позволяет строить запросы цепочкой.",
    "Expression Tree": "Структура данных, представляющая код как дерево. EF Core анализирует её и генерирует SQL.",
    "Streaming операторы": "Where, Select — обрабатывают элементы по одному, память O(1). Не читают всю коллекцию сразу.",
    "Buffering операторы": "OrderBy, GroupBy — читают всю коллекцию в память O(n) для работы.",
    "IEnumerable": "Базовый интерфейс для перечисления коллекций. Позволяет использовать foreach и LINQ.",
    "IQueryable": "Расширяет IEnumerable, добавляя Expression Trees. Позволяет переводить LINQ в SQL (EF Core).",
    "CancellationToken": "Токен для кооперативной отмены операций. Передается во все async методы.",
    "ConfigureAwait(false)": "Продолжение после await выполняется в ThreadPool, а не в исходном контексте. В библиотеках — всегда false.",
    "ValueTask": "Структура (value type), не аллоцирует память если результат уже есть (кэш). Можно await только ОДИН раз.",
    "ThreadPool": "Пул потоков .NET для выполнения работы. async/await использует пул автоматически.",
    "SynchronizationContext": "Контекст синхронизации (UI поток в WPF, запрос в ASP.NET classic). await возвращается в него.",
    "Span": "ref struct, только стек, нулевые аллокации для срезов массивов/строк.",
    "Memory": "Как Span, но может быть на куче, поддерживает async.",
    "ArrayPool": "Пул массивов для избежания аллокаций и LOH фрагментации. Rent/Return.",
    "LOH": "Large Object Heap — куча для объектов ≥ 85 KB. Не компактируется (до .NET 5), фрагментируется.",
    "GC": "Garbage Collector — автоматическое управление памятью. Поколенческий: Gen 0/1/2.",
    "Gen 0": "Новые объекты, малый размер (~256 KB), очень частые сборки.",
    "Gen 1": "Объекты выжившие после Gen 0, буфер перед Gen 2.",
    "Gen 2": "Долгоживущие объекты, собирается редко (Full GC).",
    "IDisposable": "Интерфейс для детерминированного освобождения ресурсов. Паттерн: Dispose(bool), GC.SuppressFinalize.",
    "SafeHandle": "Правильный wrapper для unmanaged дескрипторов. Гарантированный финализатор.",
    "WeakReference": "Слабая ссылка, не удерживает объект от GC. TryGetTarget проверяет жив ли объект.",
    "ConditionalWeakTable": "Таблица с слабыми ключами (ephemeron). Значение живо пока жив ключ.",
    "GCHandle": "Низкоуровневая ручка для pinning (закрепления объекта в памяти для interop). Обязателен Free().",
    "Covariance": "Ковариантность (out) — более конкретный тип там где ожидается общий. Только выходные позиции.",
    "Contravariance": "Контравариантность (in) — более общий тип там где ожидается конкретный. Только входные позиции.",
    "Pattern Matching": "Проверка формы данных и извлечение значений. Switch expressions, property patterns, list patterns.",
    "Record": "Immutable reference/value type с value equality, with-expressions, деконструкцией.",
    "Primary Constructor": "Параметры конструктора становятся полями (C# 12 для class/struct).",
    "Required": "Свойство ОБЯЗАТЕЛЬНО к инициализации в object initializer (C# 11).",
    "Init-only setter": "init — setter только для инициализации объекта (C# 9).",
    "Source Generator": "Генерация .cs файлов на этапе компиляции. Работает в NativeAOT, без рефлексии.",
    "Reflection": "Инспекция типов в runtime (Type, MethodInfo). Медленно — кэшируйте MemberInfo.",
    "DynamicMethod": "Ручная генерация IL в runtime. Максимальная скорость, skipVisibility: true для private.",
    "IHttpClientFactory": "Фабрика HttpClient с пулингом соединений, DNS refresh. Не создавайте new HttpClient()!",
    "Polly": "Библиотека resilience: Retry, Circuit Breaker, Timeout, Bulkhead, Fallback.",
    "Circuit Breaker": "После N ошибок «переключает» цепь в открытое состояние. Через время — half-open.",
    "Bulkhead": "Ограничение параллелизма. SemaphoreSlim или Polly Bulkhead. Защита от каскадных сбоев.",
    "gRPC": "Высокопроизводительный RPC на HTTP/2 + Protobuf. 4 типа: Unary, Server/Client/Bidi Streaming.",
    "Protobuf": "Protocol Buffers — бинарная сериализация, схема в .proto файлах. Меньше JSON, быстрее.",
    "SignalR": "Real-time двусторонняя связь. Авто-транспорт (WebSockets, SSE, Long Polling). Groups, Auto-reconnect.",
    "Rate Limiting": "Ограничение запросов. Fixed/Sliding Window, Token Bucket, Concurrency. Обязателен QueueLimit.",
    "MediatR": "In-process mediator для CQRS. Commands/Queries → Handlers. Pipeline Behaviors для cross-cutting.",
    "CQRS": "Разделение чтения и записи. Commands (меняют состояние) / Queries (только чтение).",
    "Aggregate Root": "Корень агрегата в DDD. Гарантирует инварианты. Единственная точка входа для изменений.",
    "Value Object": "Объект без идентичности, равенство по значениям. Immutable. Email, Money, Address.",
    "Domain Event": "Событие внутри домена (OrderPlaced). Публикуется после SaveChanges через Outbox pattern.",
    "Outbox Pattern": "Сохранение Domain Events в таблицу Outbox в ТОЙ ЖЕ транзакции что и бизнес-данные.",
    "Event Sourcing": "Состояние хранится как последовательность событий. Полный аудит, проекции для чтения.",
    "Saga": "Распределенная транзакция через цепочку локальных транзакций с компенсацией при ошибке.",
    "Actor Model": "Модель параллельности: акторы (state + behavior) общаются асинхронными сообщениями.",
    "Orleans Grain": "Виртуальный актор с авто-активацией/деактивацией. Персистенция, reminders, streams.",
    "Rx.NET": "IObservable/IObserver для push-последовательностей. Операторы: Select, Where, Merge, CombineLatest.",
    "IObservable": "«Продюсер» событий. Subscribe возвращает IDisposable для отписки.",
    "Backpressure": "Контроль скорости: когда продюсер быстрее консьюмера. Buffer, Window, Throttle.",
    "Docker Multi-stage": "Несколько FROM. Build stage (SDK) → Runtime stage (ASP.NET runtime, distroless).",
    "Distroless": "Минимальный образ без shell, пакетного менеджера, лишних уязвимостей. Только runtime.",
    "Kubernetes HPA": "Horizontal Pod Autoscaler — автоскалинг подов по CPU, памяти или кастомным метрикам.",
    "Helm": "Пакетный менеджер Kubernetes. Charts с values.yaml, зависимостями, шаблонами.",
    "Kustomize": "Нативный K8s способ кастомизации манифестов. Base + overlays, patches.",
    "Service Mesh": "Инфраструктурный слой для mTLS, traffic splitting, observability. Sidecar proxy.",
    "mTLS": "Mutual TLS — двусторонняя аутентификация сервисов. Сертификаты выдает mesh автоматически.",
    "GitOps": "Desired state в Git, агент (ArgoCD/Flux) синхронизирует кластер. Rollback = git revert.",
    "NativeAOT": "Компиляция в нативный бинарь без JIT, IL. Маленький размер, быстрый старт.",
    "PGO": "Profile-Guided Optimization — оптимизация на основе профиля реальной нагрузки.",
    "SIMD": "Single Instruction Multiple Data — одна инструкция над вектором данных. Vector, HardwareIntrinsics.",
    "BenchmarkDotNet": "Золотой стандарт микробенчмарков. MemoryDiagnoser, DisassemblyDiagnoser.",
    "dotnet-trace": "ETW профилировщик. Собирает .nettrace, конвертирует в speedscope.",
    "OpenTelemetry": "Стандарт observability: Metrics, Logs, Traces. Экспорт в Prometheus, Jaeger, Zipkin, Grafana.",
    "W3C TraceContext": "Стандарт заголовков трассировки: traceparent, tracestate, baggage.",
}

# Terms to skip (too common, cause issues)
SKIP_TERMS = {
    "Task", "Record", "Pattern", "Memory", "Span", "Reflection", 
    "CancellationToken", "Deadlock", "ConfigureAwait(false)", "ValueTask"
}

def inject_term_definitions(text, injected_in_lesson):
    """Inject term definitions in safe places only - after sentences in plain text"""
    # Skip if contains table, HTML tags, headings, or code-like patterns
    if any(marker in text for marker in ['|---|', '<table', '<tr>', '<th>', '<td>', '<h1', '<h2', '<h3', '<h4', '<code', '```', '`IEnumerable<', '`IQueryable<', '`Span<', '`Memory<', '`ValueTask<', '`Task<', '`List<', '`Dictionary<']):
        return text
    
    # Skip if it's a heading
    if re.match(r'^#{1,6}\s', text.strip()):
        return text
    
    # Only inject in substantial text blocks (not short labels)
    if len(text) < 100:
        return text
    
    # Find terms that appear as whole words
    for term, definition in TERM_DEFINITIONS.items():
        if term in SKIP_TERMS or term in injected_in_lesson:
            continue
        
        # Match whole word (case insensitive)
        pattern = r'\b' + re.escape(term) + r'\b'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Inject after the end of the sentence containing the term
            end_pos = match.end()
            # Find end of sentence
            while end_pos < len(text) and text[end_pos] not in '.!?':
                end_pos += 1
            if end_pos < len(text):
                end_pos += 1  # Include the punctuation
            
            # Inject definition
            definition_html = f'\n\n> 💡 **Термин:** {definition}\n'
            text = text[:end_pos] + definition_html + text[end_pos:]
            injected_in_lesson.add(term)
            
            # Only inject max 2 terms per text block
            if len(injected_in_lesson) >= 2:
                break
    
    return text

# Code context patterns
CODE_CONTEXTS = [
    # (pattern, context_comment, language)
    (r'IHttpClientFactory|AddHttpClient', 'Используется: фабрика HttpClient с пулингом, DNS refresh — не создавайте new HttpClient()!', 'csharp'),
    (r'CancellationToken', 'Используется: каждый async метод должен принимать ct для отмены по таймауту/пользователю', 'csharp'),
    (r'ConfigureAwait\(false\)', 'Используется: в библиотеках, чтобы не захватывать SynchronizationContext', 'csharp'),
    (r'ValueTask', 'Используется: горячие пути с кэшированием, миллионы вызовов/сек', 'csharp'),
    (r'ArrayPool|MemoryPool', 'Используется: парсинг больших данных, высоконагруженные API, gRPC streaming', 'csharp'),
    (r'record\s+(struct\s+)?\w+', 'Используется: DTO, команды/запросы в MediatR, Value Objects в DDD', 'csharp'),
    (r'MediatR|IRequestHandler|IPipelineBehavior', 'Используется: CQRS слой Application в Clean Architecture', 'csharp'),
    (r'SignalR|HubConnection|IHubContext', 'Используется: real-time уведомления, чаты, дашборды, collaboration', 'csharp'),
    (r'MemoryDiagnoser|BenchmarkDotNet|BenchmarkRunner', 'Используется: микробенчмарки для критических путей, сравнение алгоритмов', 'csharp'),
    (r'Vector<|Avx2|Sse|AdvSimd|HardwareIntrinsics', 'Используется: математика, обработка изображений, ML, высоконагруженные вычисления', 'csharp'),
    (r'AesGcm|ChaCha20Poly1305', 'Используется: симметричное шифрование с аутентификацией (confidentiality + integrity)', 'csharp'),
    (r'RSA.*(OAEP|Pkcs1)', 'Используется: асимметричное шифрование/подпись, JWT токены, TLS', 'csharp'),
    (r'Task\.Run.*(HeavyCompute|CPU|计算)', 'Используется: вынос CPU-bound работы из UI/HTTP thread в пул потоков', 'csharp'),
    (r'SemaphoreSlim', 'Используется: ограничение параллелизма, rate limiting, bulkhead pattern', 'csharp'),
    (r'Parallel\.ForEachAsync', 'Используется: параллельная обработка с контролем степени параллелизма (.NET 6+)', 'csharp'),
    (r'IAsyncEnumerable', 'Используется: стриминг больших данных, Server-Sent Events, gRPC streaming', 'csharp'),
    (r'yield return', 'Используется: ленивые последовательности, iterator паттерн, библиотеки', 'csharp'),
    (r'FluentValidation|IValidator', 'Используется: валидация команд MediatR, pipeline behaviors', 'csharp'),
    (r'OutboxMessage|OutboxPattern', 'Используется: надежная публикация Domain Events в микросервисах', 'csharp'),
    (r'ActivitySource|StartActivity', 'Используется: distributed tracing, observability в микросервисах', 'csharp'),
    (r'OpenTelemetry|AddMeter', 'Используется: метрики для Prometheus/Grafana', 'csharp'),
    (r'Serilog|Log\.Logger', 'Используется: структурированное логирование с enrichment, sinks', 'csharp'),
    (r'ObjectPool', 'Используется: пулинг дорогих объектов (StringBuilder, DbCommand, etc.)', 'csharp'),
    (r'stackalloc', 'Используется: малые буферы на стеке, высокая производительность, interop', 'csharp'),
    (r'fixed\s*\(.*byte\*', 'Используется: pinning для interop, работа с нативными API', 'csharp'),
    (r'GCHandle', 'Используется: pinning, weak references, interop, GCHandleType.Pinned', 'csharp'),
    (r'DynamicMethod|ILGenerator', 'Используется: генерация IL в runtime, максимальная скорость, AOT-совместимые библиотеки', 'csharp'),
    (r'Expression<.*Compile', 'Используется: динамическое построение запросов, Expression Trees', 'csharp'),
    (r'Saga.*(compensate|Compensate)', 'Используется: распределенные транзакции с компенсацией при ошибке', 'csharp'),
    (r'Orleans|IGrainWithIntegerKey|PersistentState', 'Используется: Virtual Actors, state persistence, clustering, reminders', 'csharp'),
    (r'Akka|ReceiveActor|Persist\(', 'Используется: классическая Actor Model, Event Sourcing, supervision', 'csharp'),
    (r'Dockerfile|FROM.*AS build', 'Используется: контейнеризация для K8s, Cloud Run, Container Apps — разделение build и runtime', 'dockerfile'),
    (r'distroless', 'Используется: минимальный безопасный runtime образ без shell и пакетного менеджера', 'dockerfile'),
    (r'USER 65532', 'Используется: non-root пользователь для безопасности контейнера', 'dockerfile'),
    (r'HEALTHCHECK', 'Используется: Kubernetes liveness/readiness probes', 'dockerfile'),
    (r'HorizontalPodAutoscaler|autoscaling/v2', 'Используется: автоскалинг подов в Kubernetes по метрикам', 'yaml'),
    (r'Deployment.*replicas', 'Используется: управление подми, rolling updates, rollback', 'yaml'),
    (r'Service.*ClusterIP', 'Используется: внутренняя балансировка нагрузки в K8s кластере', 'yaml'),
    (r'Ingress', 'Используется: внешний доступ к сервисам, TLS termination, rate limiting', 'yaml'),
    (r'ConfigMap|Secret', 'Используется: конфигурация и секреты вне кода приложения', 'yaml'),
    (r'Helm|Chart\.yaml|values\.yaml', 'Используется: пакетный менеджер Kubernetes для production деплоя', 'yaml'),
    (r'kustomization', 'Используется: нативный K8s способ кастомизации манифестов (base + overlays)', 'yaml'),
    (r'istio|VirtualService|DestinationRule', 'Используется: Service Mesh — mTLS, traffic splitting, observability', 'yaml'),
    (r'dotnet publish.*DebugType=portable', 'Используется: сборка с символами для профилирования (dotnet-trace, PerfView)', 'bash'),
    (r'dotnet-trace', 'Используется: ETW профилирование CPU/memory в production', 'bash'),
    (r'dotnet-counters', 'Используется: real-time метрики GC, ThreadPool, JIT, ASP.NET Core', 'bash'),
    (r'BenchmarkRunner', 'Используется: запуск микробенчмарков BenchmarkDotNet', 'bash'),
    (r'docker build.*buildx', 'Используется: multi-arch сборка (amd64/arm64) для K8s', 'bash'),
    (r'service.*rpc', 'Используется: gRPC contract-first API определение', 'protobuf'),
]

def add_code_context(block):
    """Add real-world usage comments to code blocks (avoid duplicates)"""
    if block['type'] != 'code':
        return block
    
    code = block.get('content', '')
    lang = block.get('language', '').lower()
    
    # Check if already has context comments
    if '// Используется:' in code or '# Используется:' in code:
        return block
    
    contexts = []
    for pattern, context, pattern_lang in CODE_CONTEXTS:
        if pattern_lang and pattern_lang != lang and pattern_lang != 'any':
            continue
        if re.search(pattern, code, re.IGNORECASE):
            contexts.append(context)
    
    if contexts:
        # Deduplicate
        contexts = list(dict.fromkeys(contexts))
        comment_prefix = "// " if lang in ['csharp', 'c#'] else "# "
        context_comment = "\n".join([f"{comment_prefix}{c}" for c in contexts]) + "\n\n"
        block['content'] = context_comment + code
    
    return block

def process_lesson(lesson_num):
    print(f"Processing lesson {lesson_num}...")
    data = load_lesson(lesson_num)
    
    # Track injected terms per lesson
    injected_terms = set()
    
    # Process content blocks
    new_blocks = []
    for block in data.get('content_blocks', []):
        # Clean code blocks (remove duplicates)
        if block['type'] == 'code':
            block['content'] = clean_code_block(block['content'])
        
        # Clean text blocks (remove broken injections)
        if block['type'] == 'text':
            block['content'] = clean_text_block(block['content'])
        
        # Add code context
        block = add_code_context(block)
        
        # Inject term definitions in text blocks
        if block['type'] == 'text':
            block['content'] = inject_term_definitions(block['content'], injected_terms)
        
        new_blocks.append(block)
    
    data['content_blocks'] = new_blocks
    save_lesson(lesson_num, data)
    print(f"  Saved lesson {lesson_num} (injected terms: {injected_terms})")

def main():
    for lesson_num in range(15, 34):
        process_lesson(lesson_num)
    print("All lessons fixed and enhanced!")

if __name__ == "__main__":
    main()