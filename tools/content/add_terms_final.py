#!/usr/bin/env python3
"""
Add clean term definitions in strategic text blocks (not in tables, headings, or code)
"""

import json
import re

def load_lesson(lesson_num):
    path = f"/Users/xiip.shk/работа/Kernify/fixtures/lessons/csharp/{lesson_num}.json"
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_lesson(lesson_num, data):
    path = f"/Users/xiip.shk/работа/Kernify/fixtures/lessons/csharp/{lesson_num}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Key terms to inject in specific lessons - one per lesson max, in appropriate text blocks
TERM_INJECTIONS = {
    15: {
        "trigger": "Отложенное выполнение",
        "term": "Deferred Execution",
        "definition": "LINQ запрос не выполняется при создании, а только при переборе (foreach, ToList). Это позволяет строить запросы цепочкой и объединять их."
    },
    16: {
        "trigger": "Immutable коллекции",
        "term": "Immutable Collections",
        "definition": "Коллекции, которые не изменяются после создания. При изменении создаётся новая коллекция, общая память со старой (structural sharing). Потокобезопасны по дизайну."
    },
    17: {
        "trigger": "CancellationToken",
        "term": "CancellationToken",
        "definition": "Токен для кооперативной отмены асинхронных операций. Передаётся во все async методы. ThrowIfCancellationRequested() бросает OperationCanceledException."
    },
    18: {
        "trigger": "Large Object Heap",
        "term": "LOH (Large Object Heap)",
        "definition": "Отдельная куча для объектов ≥ 85 KB. Не компактируется при обычном GC (до .NET 5), что приводит к фрагментации. Используйте ArrayPool для больших массивов."
    },
    19: {
        "trigger": "Testcontainers",
        "term": "Testcontainers",
        "definition": "Библиотека для запуска реальных контейнеров (PostgreSQL, Redis, Kafka и др.) в интеграционных тестах. Автоматически управляет жизненным циклом контейнеров."
    },
    20: {
        "trigger": "N+1 проблема",
        "term": "N+1 Problem",
        "definition": "Проблема в ORM: загрузка родительского объекта вызывает N дополнительных запросов для дочерних коллекций. Решение: Include(), Select(), SplitQuery()."
    },
    21: {
        "trigger": "Captive Dependency",
        "term": "Captive Dependency",
        "definition": "Ошибка DI: Singleton зависит от Scoped сервиса. Scoped «захватывается» в Singleton и живет дольше положенного. Решение: IServiceScopeFactory."
    },
    22: {
        "trigger": "Aggregate Root",
        "term": "Aggregate Root",
        "definition": "Корень агрегата в DDD — единственная точка входа для изменений внутри границ агрегата. Гарантирует инварианты. Entity с глобальной идентичностью."
    },
    23: {
        "trigger": "Covariance",
        "term": "Covariance/Contravariance",
        "definition": "Covariance (out) — более конкретный тип там где ожидается общий (выходные позиции). Contravariance (in) — более общий тип там где ожидается конкретный (входные позиции)."
    },
    24: {
        "trigger": "Source Generator",
        "term": "Source Generator",
        "definition": "Генерация .cs файлов на этапе компиляции. Работает в NativeAOT, без рефлексии, быстрее runtime генерации. IIncrementalGenerator — современный API."
    },
    25: {
        "trigger": "Pattern-based API",
        "term": "Pattern-based API",
        "definition": "Duck typing для языковых конструкций: GetEnumerator (foreach), GetAwaiter (await), Dispose (using), Deconstruct (деконструкция). Компилятор ищет методы по имени."
    },
    26: {
        "trigger": "SafeHandle",
        "term": "SafeHandle",
        "definition": "Правильный wrapper для unmanaged дескрипторов. Наследует CriticalFinalizerObject — гарантированный финализатор даже при AppDomain unload."
    },
    27: {
        "trigger": "Polly",
        "term": "Polly",
        "definition": "Библиотека resilience: Retry, Circuit Breaker, Timeout, Bulkhead, Fallback. Работает через PolicyWrap. Критично для микросервисов."
    },
    28: {
        "trigger": "JWT",
        "term": "JWT (JSON Web Token)",
        "definition": "Стандарт токенов: header.payload.signature. Stateless аутентификация. Подписывается (HS256/RS256), проверяется на сервере без БД."
    },
    29: {
        "trigger": "OpenTelemetry",
        "term": "OpenTelemetry",
        "definition": "Стандарт observability: Metrics, Logs, Traces. Экспорт в Prometheus, Jaeger, Zipkin, Grafana. Единый API для всех языков."
    },
    30: {
        "trigger": "Service Mesh",
        "term": "Service Mesh",
        "definition": "Инфраструктурный слой (sidecar proxy) для mTLS, traffic splitting, observability, rate limiting. Istio/Linkerd. Не требует изменений кода."
    },
    31: {
        "trigger": "SIMD",
        "term": "SIMD",
        "definition": "Single Instruction Multiple Data — одна инструкция обрабатывает вектор данных. Vector, HardwareIntrinsics (AVX2/SSE/NEON). Ускорение математики в разы."
    },
    32: {
        "trigger": "Actor Model",
        "term": "Actor Model",
        "definition": "Модель параллельности: акторы (state + behavior) общаются асинхронными сообщениями. Нет shared state — нет race conditions. Akka.NET / Orleans."
    },
    33: {
        "trigger": "GitOps",
        "term": "GitOps",
        "definition": "Desired state в Git, агент (ArgoCD/Flux) синхронизирует кластер. Аудит, rollback = git revert. Declarative infrastructure."
    },
}

def inject_term(text, trigger, term, definition):
    """Inject term definition after the trigger phrase in a text block"""
    # Only inject in substantial text blocks, not in tables, headings, or code
    if any(marker in text for marker in ['|---|', '<h', '<table', '```', '<code']):
        return text
    
    # Find the trigger phrase
    idx = text.find(trigger)
    if idx == -1:
        return text
    
    # Find end of sentence containing trigger
    end_pos = idx + len(trigger)
    while end_pos < len(text) and text[end_pos] not in '.!?':
        end_pos += 1
    if end_pos < len(text):
        end_pos += 1  # Include punctuation
    
    # Inject definition
    definition_html = f'\n\n> 💡 **Термин: {term}** — {definition}\n'
    return text[:end_pos] + definition_html + text[end_pos:]

def process_lesson(lesson_num):
    print(f"Adding term to lesson {lesson_num}...")
    data = load_lesson(lesson_num)
    
    if lesson_num not in TERM_INJECTIONS:
        print(f"  No term injection defined for lesson {lesson_num}")
        return
    
    injection = TERM_INJECTIONS[lesson_num]
    trigger = injection["trigger"]
    term = injection["term"]
    definition = injection["definition"]
    
    new_blocks = []
    injected = False
    for block in data.get('content_blocks', []):
        if block['type'] == 'text' and not injected:
            new_content = inject_term(block['content'], trigger, term, definition)
            if new_content != block['content']:
                block['content'] = new_content
                injected = True
                print(f"  Injected '{term}' in lesson {lesson_num}")
        new_blocks.append(block)
    
    if not injected:
        print(f"  WARNING: Could not find trigger '{trigger}' in lesson {lesson_num}")
    
    data['content_blocks'] = new_blocks
    save_lesson(lesson_num, data)

def main():
    for lesson_num in range(15, 34):
        process_lesson(lesson_num)
    print("All term injections complete!")

if __name__ == "__main__":
    main()