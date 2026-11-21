#!/usr/bin/env python3
"""
Fix the context matching - remove wrong injections, add correct ones precisely
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

def clean_wrong_injections(text):
    """Remove all the wrong 'Где применяется' injections"""
    # Remove the wrong LINQ to Objects injections
    text = re.sub(r'\n\n> 💡 \*\*Где применяется:\*\* Это используется в двух сценариях: \*\*LINQ to Objects\*\* — когда данные уже в памяти \(массивы, списки\), и \*\*LINQ to Entities \(IQueryable\)\*\* — когда запрос переводится в SQL и выполняется в базе данных \(Entity Framework Core\)\.', '', text)
    
    # Remove duplicates of same injection
    text = re.sub(r'(\n\n> 💡 \*\*Где применяется:\*\*[^\n]*)\n\s*\1', r'\1', text)
    
    # Remove ArrayPool duplicates
    text = re.sub(r'(\n\n> 💡 \*\*Где применяется:\*\* \*\*ArrayPool / MemoryPool\*\* критически важны при парсинге больших файлов \(CSV, JSON\), в высоконагруженных API и gRPC стриминге\. Вместо `new byte\[100000\]` в цикле \(что фрагментирует LOH и вызывает Full GC\) — берите буфер из пула: `ArrayPool<byte>\.Shared\.Rent\(\)` и обязательно возвращайте `\.Return\(\)`\.)\n\s*\1', r'\1', text)
    
    # Remove ValueTask duplicates
    text = re.sub(r'(\n\n> 💡 \*\*Где применяется:\*\* \*\*ValueTask\*\* вместо `Task` стоит использовать только на «горячих путях» — когда метод часто возвращает результат синхронно \(из кэша\) и вызывается миллионы раз в секунду\. Обычный `Task` всегда аллоцирует объект, `ValueTask` — нет \(если результат уже готов\)\. Но `ValueTask` можно `await` только один раз\!\.)\n\s*\1', r'\1', text)
    
    # Remove CancellationToken duplicates
    text = re.sub(r'(\n\n> 💡 \*\*Где применяется:\*\* \*\*Важно:\*\* каждый асинхронный метод должен принимать `CancellationToken` — это позволяет отменить операцию по таймауту \(например, 30 сек\) или когда пользователь закрыл страницу\. Без этого долгие запросы будут висеть и съедать ресурсы\.)\n\s*\1', r'\1', text)
    
    # Remove ConfigureAwait duplicates
    text = re.sub(r'(\n\n> 💡 \*\*Где применяется:\*\* В библиотеках и нижних слоях приложения всегда используйте `\.ConfigureAwait\(false\)`\. Это заставляет продолжение после `await` выполняться в пуле потоков \(ThreadPool\), а не в исходном контексте \(UI поток в WPF, запрос в старом ASP\.NET\)\. Без этого получаются дедлоки и лишние переключения контекста\.)\n\s*\1', r'\1', text)
    
    # Remove Outbox Pattern duplicates
    text = re.sub(r'(\n\n> 💡 \*\*Где применяется:\*\* \*\*Outbox Pattern\*\* — Domain Events сохраняются в таблицу `OutboxMessages` в ТОЙ ЖЕ транзакции, что и бизнес-данные\. Фоновый процесс \(background job\) читает outbox и публикует в message broker \(Kafka/RabbitMQ\)\. Гарантирует exactly-once доставку без распределённых транзакций\.)\n\s*\1', r'\1', text)
    
    # Remove SignalR duplicates
    text = re.sub(r'(\n\n> 💡 \*\*Где применяется:\*\* \*\*SignalR\*\* — это абстракция над WebSockets / Server-Sent Events / Long Polling\. Используется для real-time: чаты, уведомления, живые дашборды, коллаборативное редактирование\. Автоматически выбирает транспорт, поддерживает Groups \(комнаты\), авто-переподключение\. JWT для WebSockets передаётся в query string\.)\n\s*\1', r'\1', text)
    
    # Remove GitOps duplicates
    text = re.sub(r'(\n\n> 💡 \*\*Где применяется:\*\* \*\*GitOps\*\* — desired state хранится в Git, агент \(ArgoCD/Flux\) постоянно синхронизирует кластер\. Деплой = `git push`, откат = `git revert\)\. Аудит, безопасность, декларативность\. ArgoCD Application указывает на repo/path/overlay\.)\n\s*\1', r'\1', text)
    
    # Remove Actor Model duplicates
    text = re.sub(r'(\n\n> 💡 \*\*Где применяется:\*\* \*\*Actor Model \(Akka\.NET / Orleans\)\*\* — модель параллельности без shared state\. Акторы — изолированные единицы \(state \+ behavior\), общаются асинхронными сообщениями\. Нет race conditions, нет локов\. Orleans \(Virtual Actors\) проще: авто-активация, персистентность, кластеризация из коробки\.)\n\s*\1', r'\1', text)
    
    # Remove HPA duplicates
    text = re.sub(r'(\n\n> 💡 \*\*Где применяется:\*\* \*\*HorizontalPodAutoscaler \(HPA\)\*\* автоматически меняет количество подов по CPU, памяти или кастомным метрикам \(Prometheus: RPS, latency, queue length\)\. `behavior\.scaleDown\.stabilizationWindowSeconds` предотвращает флаппинг\.)\n\s*\1', r'\1', text)
    
    # Clean up any remaining triple+ duplicates
    for _ in range(5):
        text = re.sub(r'(\n\n> 💡 \*\*Где применяется:\*\*[^\n]*)\n\s*\1', r'\1', text)
    
    return text

def process_lesson(lesson_num):
    print(f"Cleaning lesson {lesson_num}...")
    data = load_lesson(lesson_num)
    
    new_blocks = []
    for block in data.get('content_blocks', []):
        if block['type'] == 'text':
            block['content'] = clean_wrong_injections(block['content'])
        new_blocks.append(block)
    
    data['content_blocks'] = new_blocks
    save_lesson(lesson_num, data)
    print(f"  Cleaned lesson {lesson_num}")

def main():
    for lesson_num in range(15, 34):
        process_lesson(lesson_num)
    print("All lessons cleaned!")

if __name__ == "__main__":
    main()