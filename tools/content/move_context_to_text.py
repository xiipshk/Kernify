#!/usr/bin/env python3
"""
Move 'where this is used' context from code comments to preceding text blocks
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

# Map of context patterns to human-readable explanations for text
CONTEXT_EXPLANATIONS = {
    # LINQ
    'LINQ to Objects (IEnumerable в памяти) или EF Core (IQueryable → SQL)': 
        'Это используется в двух сценариях: **LINQ to Objects** — когда данные уже в памяти (массивы, списки), и **LINQ to Entities (IQueryable)** — когда запрос переводится в SQL и выполняется в базе данных (Entity Framework Core).',
    
    # Async/CancellationToken
    'каждый async метод должен принимать ct для отмены по таймауту/пользователю':
        '**Важно:** каждый асинхронный метод должен принимать `CancellationToken` — это позволяет отменить операцию по таймауту (например, 30 сек) или когда пользователь закрыл страницу. Без этого долгие запросы будут висеть и съедать ресурсы.',
    
    'в библиотеках, чтобы не захватывать SynchronizationContext':
        'В библиотеках и нижних слоях приложения всегда используйте `.ConfigureAwait(false)`. Это заставляет продолжение после `await` выполняться в пуле потоков (ThreadPool), а не в исходном контексте (UI поток в WPF, запрос в старом ASP.NET). Без этого получаются дедлоки и лишние переключения контекста.',
    
    'горячие пути с кэшированием, миллионы вызовов/сек':
        '**ValueTask** вместо `Task` стоит использовать только на «горячих путях» — когда метод часто возвращает результат синхронно (из кэша) и вызывается миллионы раз в секунду. Обычный `Task` всегда аллоцирует объект, `ValueTask` — нет (если результат уже готов). Но `ValueTask` можно `await` только один раз!',
    
    'парсинг больших данных, высоконагруженные API, gRPC streaming':
        '**ArrayPool / MemoryPool** критически важны при парсинге больших файлов (CSV, JSON), в высоконагруженных API и gRPC стриминге. Вместо `new byte[100000]` в цикле (что фрагментирует LOH и вызывает Full GC) — берите буфер из пула: `ArrayPool<byte>.Shared.Rent()` и обязательно возвращайте `.Return()`.',
    
    'CQRS слой Application в Clean Architecture':
        'Это основа **CQRS** в Clean Architecture: команды (`IRequest<T>`) меняют состояние, запросы — только читают. `MediatR` диспетчерит их в хендлеры. Pipeline Behaviors (`IPipelineBehavior`) добавляют cross-cutting: валидацию (FluentValidation), транзакции, логирование — без загрязнения бизнес-логики.',
    
    'real-time уведомления, чаты, дашборды, collaboration':
        '**SignalR** — это абстракция над WebSockets / Server-Sent Events / Long Polling. Используется для real-time: чаты, уведомления, живые дашборды, коллаборативное редактирование. Автоматически выбирает транспорт, поддерживает Groups (комнаты), авто-переподключение. JWT для WebSockets передаётся в query string.',
    
    'микробенчмарки для критических путей, сравнение алгоритмов':
        '**BenchmarkDotNet** — золотой стандарт микробенчмарков. Используйте для критических путей (парсеры, сериализация, математика). Обязательно атрибуты: `[MemoryDiagnoser]` (показывает аллокации/GC), `[DisassemblyDiagnoser]` (показывает JIT-ассемблер). Запускайте в Release, без отладчика.',
    
    'математика, обработка изображений, ML, высоконагруженные вычисления':
        '**SIMD (Vector, HardwareIntrinsics)** — одна инструкция CPU обрабатывает вектор данных (4-8 чисел сразу). Используется в математике, обработке изображений, ML, финансовых расчетах. `Vector<T>` — переносимый вариант, `Avx2/Sse/AdvSimd` — прямые инструкции (проверяйте `.IsSupported`). Ускорение в 4-8 раз.',
    
    'контейнеризация для K8s, Cloud Run, Container Apps':
        '**Multi-stage Dockerfile** — разделение build и runtime. Первый этап (SDK) компилирует и публикует, второй (ASP.NET runtime, лучше distroless) — только запускает. Distroless — без shell, пакетного менеджера, минимальная поверхность атаки. `.dockerignore` критично для скорости сборки.',
    
    'автоскалинг подов в Kubernetes по метрикам':
        '**HorizontalPodAutoscaler (HPA)** автоматически меняет количество подов по CPU, памяти или кастомным метрикам (Prometheus: RPS, latency, queue length). `behavior.scaleDown.stabilizationWindowSeconds` предотвращает флаппинг.',
    
    'GitOps — desired state в Git, ArgoCD/Flux синхронизирует кластер':
        '**GitOps** — desired state хранится в Git, агент (ArgoCD/Flux) постоянно синхронизирует кластер. Деплой = `git push`, откат = `git revert`. Аудит, безопасность, декларативность. ArgoCD Application указывает на repo/path/overlay.',
    
    'декларативный язык запросов: пишем ЧТО нужно, а не КАК':
        '**LINQ** — декларативный стиль: описываем *что* нужно (фильтр, проекция, группировка), а не *как* итерировать. Компилятор строит дерево выражений. Два синтаксиса: Query Syntax (похоже на SQL) и Method Syntax (fluent API) — компилируются в один IL.',
    
    'отложенное выполнение: запрос выполняется при переборе (ToList, foreach)':
        '**Отложенное выполнение (Deferred Execution)** — LINQ запрос создаётся сразу, но выполняется ТОЛЬКО при переборе (`foreach`, `ToList()`, `ToArray()`, `Count()`). Это позволяет цепочестроить запросы и добавлять условия динамически. Материализация (`ToList()`) «замораживает» результат.',
    
    'IEnumerable — в памяти, IQueryable — в БД (переводится в SQL)':
        '**IEnumerable** — LINQ to Objects, всё в памяти. **IQueryable** — LINQ to Entities (EF Core), запрос переводится в SQL через Expression Trees и выполняется на сервере БД. Передача `Func` в `Where` у `IQueryable` загрузит ВСЮ таблицу в память!',
    
    'Immutable коллекции — потокобезопасны по дизайну, structural sharing':
        '**Immutable коллекции** (ImmutableList, ImmutableDictionary и др.) — не меняются после создания. Любое изменение возвращает НОВУЮ коллекцию, деля память со старой (structural sharing — O(log n) вместо O(n)). Потокобезопасны без локов. Для пакетных изменений используйте `.ToBuilder()`.',
    
    'Span/Memory — нулевые аллокации для срезов строк/массивов':
        '**Span<T>** (ref struct, только стек) и **Memory<T>** (может быть на куче, для async) дают нулевые аллокации при срезах: `span.Slice(1, 3)` не копирует данные, а указывает на тот же массив. `Span` — для синхронного парсинга, `Memory` — для `Stream.ReadAsync` без копирований.',
    
    'Outbox Pattern — надежная публикация Domain Events в микросервисах':
        '**Outbox Pattern** — Domain Events сохраняются в таблицу `OutboxMessages` в ТОЙ ЖЕ транзакции, что и бизнес-данные. Фоновый процесс (background job) читает outbox и публикует в message broker (Kafka/RabbitMQ). Гарантирует exactly-once доставку без распределённых транзакций.',
    
    'Circuit Breaker — после N ошибок цепь открывается':
        '**Circuit Breaker (Polly)** — после N ошибок (5xx, timeout) «размыкает цепь»: быстро падает без вызова сервиса, давая ему восстановиться. Через `durationOfBreak` переходит в half-open — пробует один запрос. Защищает от каскадных сбоев.',
    
    'Actor Model — нет shared state, сообщения вместо локов':
        '**Actor Model (Akka.NET / Orleans)** — модель параллельности без shared state. Акторы — изолированные единицы (state + behavior), общаются асинхронными сообщениями. Нет race conditions, нет локов. Orleans (Virtual Actors) проще: авто-активация, персистентность, кластеризация из коробки.',
    
    'Saga — распределённая транзакция с компенсацией':
        '**Saga** — цепочка локальных транзакций с компенсацией при ошибке. Шаг 1: Reserve Inventory → компенсация: Release. Шаг 2: Charge Payment → Refund. Все шаги идемпотентны (проверка по correlationId). Используется вместо распределённых транзакций (2PC).',
}

def extract_context_from_code(code):
    """Extract 'Используется:' comments from code block"""
    lines = code.split('\n')
    contexts = []
    cleaned = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('// Используется:') or stripped.startswith('# Используется:'):
            ctx = stripped.replace('// Используется:', '').replace('# Используется:', '').strip()
            contexts.append(ctx)
        else:
            cleaned.append(line)
    
    return '\n'.join(cleaned), contexts

def find_matching_explanation(context):
    """Find best matching explanation for a context"""
    context_lower = context.lower()
    for key, explanation in CONTEXT_EXPLANATIONS.items():
        # Check key words overlap
        key_words = set(key.lower().split())
        ctx_words = set(context_lower.split())
        if key_words & ctx_words:
            # Good enough match
            return explanation
    return None

def process_lesson(lesson_num):
    print(f"Processing lesson {lesson_num}...")
    data = load_lesson(lesson_num)
    
    new_blocks = []
    i = 0
    while i < len(data['content_blocks']):
        block = data['content_blocks'][i]
        
        if block['type'] == 'code':
            # Extract contexts from this code block
            cleaned_code, contexts = extract_context_from_code(block['content'])
            block['content'] = cleaned_code
            
            if contexts:
                # Find previous text block to append explanation
                # Look back for a text block
                for j in range(len(new_blocks) - 1, -1, -1):
                    if new_blocks[j]['type'] == 'text' and len(new_blocks[j]['content']) > 50:
                        # Append explanation to this text block
                        for ctx in contexts:
                            explanation = find_matching_explanation(ctx)
                            if explanation:
                                new_blocks[j]['content'] += f'\n\n> 💡 **Где применяется:** {explanation}'
                        break
        
        new_blocks.append(block)
        i += 1
    
    data['content_blocks'] = new_blocks
    save_lesson(lesson_num, data)
    print(f"  Processed lesson {lesson_num}")

def main():
    for lesson_num in range(15, 34):
        process_lesson(lesson_num)
    print("All lessons processed!")

if __name__ == "__main__":
    main()