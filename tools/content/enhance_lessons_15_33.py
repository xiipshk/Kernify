#!/usr/bin/env python3
"""
Enhance C# lessons 15-33 with:
- More explanations for examples
- Term definitions right after first use
- Real-world usage context
- Better structure for learning
"""

import json
import re
from pathlib import Path

# Load the lessons
def load_lesson(lesson_num):
    path = f"/Users/xiip.shk/работа/Kernify/fixtures/lessons/csharp/{lesson_num}.json"
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_lesson(lesson_num, data):
    path = f"/Users/xiip.shk/работа/Kernify/fixtures/lessons/csharp/{lesson_num}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Term definitions dictionary - will be used to inject explanations
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

def inject_term_definition(content, term):
    """Inject term definition after first mention"""
    patterns = [
        term,  # exact
        term.lower(),  # lowercase
    ]
    # For terms with angle brackets like IEnumerable<T>
    if '<' in term:
        patterns.append(term.replace('<', '<').replace('>', '>'))
    
    definition = TERM_DEFINITIONS.get(term)
    if not definition:
        return content
    
    # Find first occurrence and inject after it
    for pattern in patterns:
        # Look for the term as a whole word or in code
        idx = content.find(pattern)
        if idx != -1:
            # Find end of the word/sentence
            end_idx = idx + len(pattern)
            # Inject after the term
            inject_point = end_idx
            # Add definition as a callout
            definition_html = f'\n\n> 💡 **Термин:** {definition}\n'
            content = content[:inject_point] + definition_html + content[inject_point:]
            break
    return content

def enhance_code_explanation(content):
    """Add explanations before code blocks"""
    # Pattern: code block followed by text or text followed by code
    # We'll add comments to code and explanations
    return content

def add_real_world_context(block):
    """Add real-world usage context to content blocks"""
    content = block.get('content', '')
    if block['type'] == 'code':
        # Add comment about where this is used
        lang = block.get('language', '')
        code = content
        
        # Detect patterns and add context
        contexts = []
        if 'IEnumerable' in code or 'IQueryable' in code:
            contexts.append("Используется: LINQ to Objects (IEnumerable) или EF Core (IQueryable)")
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
        if 'Record' in code or 'record' in code.lower():
            contexts.append("Используется: DTO, команды/запросы в MediatR, Value Objects в DDD")
        if 'MediatR' in code or 'IRequestHandler' in code:
            contexts.append("Используется: CQRS слой Application в Clean Architecture")
        if 'SignalR' in code or 'HubConnection' in code:
            contexts.append("Используется: real-time уведомления, чаты, дашборды, collaboration")
        if 'Benchmark' in code or 'MemoryDiagnoser' in code:
            contexts.append("Используется: микробенчмарки для критических путей, сравнение алгоритмов")
        if 'SIMD' in code or 'Vector<' in code or 'Avx2' in code:
            contexts.append("Используется: математика, обработка изображений, ML, высоконагруженные вычисления")
        if 'Dockerfile' in code or 'FROM mcr.microsoft.com/dotnet' in code:
            contexts.append("Используется: контейнеризация для K8s, Cloud Run, Container Apps")
        if 'Helm' in code or 'kustomization' in code.lower():
            contexts.append("Используется: деплой в Kubernetes продакшн, GitOps")
        if 'OpenTelemetry' in code or 'ActivitySource' in code:
            contexts.append("Используется: observability в микросервисах, распределенная трассировка")
        
        if contexts:
            # Add as comment at top of code
            comment_prefix = "// " if lang in ['csharp', 'csharp'] else "# "
            context_comment = comment_prefix + "\n".join([comment_prefix + c for c in contexts]) + "\n\n"
            block['content'] = context_comment + code
    
    return block

def process_lesson(lesson_num):
    print(f"Processing lesson {lesson_num}...")
    data = load_lesson(lesson_num)
    
    # Process content blocks
    new_blocks = []
    for block in data.get('content_blocks', []):
        # Add real-world context to code blocks
        block = add_real_world_context(block)
        
        # Inject term definitions in text blocks
        if block['type'] == 'text':
            content = block['content']
            # Find terms mentioned and inject definitions
            # Simple approach: check for known terms
            for term, definition in TERM_DEFINITIONS.items():
                # Only inject if term appears and definition not already there
                pattern = term.replace('<', '<').replace('>', '>')
                if pattern in content and definition[:50] not in content:
                    # Inject after first occurrence
                    idx = content.find(pattern)
                    if idx != -1:
                        end_idx = idx + len(pattern)
                        # Only inject once per lesson per term
                        definition_html = f'\n\n> 💡 **Термин:** {definition}\n'
                        content = content[:end_idx] + definition_html + content[end_idx:]
                        # Mark as injected by removing from tracking
            
            block['content'] = content
        
        # Add learning objectives before major sections
        if block['type'] == 'heading' and block.get('level') == 2:
            # Could add context about why this section matters
            pass
        
        new_blocks.append(block)
    
    data['content_blocks'] = new_blocks
    
    # Also enhance practice tasks with more detail
    for i, task in enumerate(data.get('practice_tasks', [])):
        # Tasks already have good detail, but we could add "Why this matters"
        pass
    
    save_lesson(lesson_num, data)
    print(f"  Saved lesson {lesson_num}")

def main():
    for lesson_num in range(15, 34):
        process_lesson(lesson_num)
    print("All lessons enhanced!")

if __name__ == "__main__":
    main()