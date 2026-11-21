#!/usr/bin/env python3
"""
Fix failed term injections with correct triggers
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

# Corrected triggers based on actual content
FIXED_INJECTIONS = {
    16: {
        "trigger": "Immutable коллекции",
        "term": "Immutable Collections",
        "definition": "Коллекции, которые не изменяются после создания. При изменении создаётся новая коллекция, общая память со старой (structural sharing). Потокобезопасны по дизайну."
    },
    20: {
        "trigger": "N+1 проблема в EF Core",
        "term": "N+1 Problem",
        "definition": "Проблема в ORM: загрузка родительского объекта вызывает N дополнительных запросов для дочерних коллекций. Решение: Include(), Select(), SplitQuery()."
    },
    21: {
        "trigger": "Captive Dependency",
        "term": "Captive Dependency",
        "definition": "Ошибка DI: Singleton зависит от Scoped сервиса. Scoped «захватывается» в Singleton и живет дольше положенного. Решение: IServiceScopeFactory."
    },
    26: {
        "trigger": "SafeHandle — правильный способ",
        "term": "SafeHandle",
        "definition": "Правильный wrapper для unmanaged дескрипторов. Наследует CriticalFinalizerObject — гарантированный финализатор даже при AppDomain unload."
    },
    32: {
        "trigger": "Actor Model — Akka.NET и Orleans",
        "term": "Actor Model",
        "definition": "Модель параллельности: акторы (state + behavior) общаются асинхронными сообщениями. Нет shared state — нет race conditions. Akka.NET / Orleans."
    },
}

def inject_term(text, trigger, term, definition):
    """Inject term definition after the trigger phrase in a text block"""
    # Skip if already has this term definition
    if f"Термин: {term}" in text:
        return text
    
    # Skip if in tables, headings, code
    if any(marker in text for marker in ['|---|', '<h', '<table', '```', '<code']):
        return text
    
    # Find the trigger phrase (case insensitive)
    idx = text.lower().find(trigger.lower())
    if idx == -1:
        return text
    
    # Find end of sentence containing trigger
    end_pos = idx + len(trigger)
    while end_pos < len(text) and text[end_pos] not in '.!?':
        end_pos += 1
    if end_pos < len(text):
        end_pos += 1
    
    # Inject definition
    definition_html = f'\n\n> 💡 **Термин: {term}** — {definition}\n'
    return text[:end_pos] + definition_html + text[end_pos:]

def process_lesson(lesson_num):
    print(f"Fixing injection for lesson {lesson_num}...")
    data = load_lesson(lesson_num)
    
    if lesson_num not in FIXED_INJECTIONS:
        return
    
    injection = FIXED_INJECTIONS[lesson_num]
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
    for lesson_num in FIXED_INJECTIONS.keys():
        process_lesson(lesson_num)
    print("All fixed injections complete!")

if __name__ == "__main__":
    main()