#!/usr/bin/env python3
"""
Fix specific remaining garbled text patterns
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

def fix_text(text):
    """Fix specific garbled patterns"""
    
    # Fix "4 типа:" duplication with extra newlines
    text = text.replace(
        "<strong>Когда использовать</strong>: стриминг больших данных, чанки из БД, Server-Sent Events, gRPC\n\n.\n\n 4 типа: Unary, Server Streaming, Client Streaming, Bidi Streaming.",
        "<strong>Когда использовать</strong>: стриминг больших данных, чанки из БД, Server-Sent Events, gRPC. 4 типа: Unary, Server Streaming, Client Streaming, Bidi Streaming."
    )
    
    # Fix ConfigureAwait table header
    text = text.replace(
        "| Контекст | ConfigureAwait\n\n, а не в исходном контексте (UI/ASP.NET). В библиотеках — всегда false.\n(true) | ConfigureAwait(false) |",
        "| Контекст | ConfigureAwait(true) | ConfigureAwait(false) |"
    )
    
    # Fix ConfigureAwait rule
    text = text.replace(
        "<strong>Правило</strong>: в библиотеках <strong>всегда</strong> используйте <code>.ConfigureAwait\n\n\n, а не в исходном контексте (UI/ASP.NET). В библиотеках — всегда false.\n(false)</code>. В UI коде — <code>true</code> (по умолчанию).",
        "<strong>Правило</strong>: в библиотеках <strong>всегда</strong> используйте <code>.ConfigureAwait(false)</code>. В UI коде — <code>true</code> (по умолчанию)."
    )
    
    # Fix ValueTask heading
    text = text.replace(
        "<h2>🎯 ValueTask\n\n и IValueTaskSource — для высокой производительности</h2>",
        "<h2>🎯 ValueTask и IValueTaskSource — для высокой производительности</h2>"
    )
    
    # Fix any remaining "\n\n\n." patterns
    text = re.sub(r'\n\n\n\.', '\n\n.', text)
    
    # Fix table with garbled header
    text = text.replace(
        "| Контекст | ConfigureAwait\n\n, а не в исходном контексте (UI/ASP.NET). В библиотеках — всегда false.\n(true) | ConfigureAwait(false) |",
        "| Контекст | ConfigureAwait(true) | ConfigureAwait(false) |"
    )
    
    return text

def process_lesson(lesson_num):
    print(f"Fixing lesson {lesson_num}...")
    data = load_lesson(lesson_num)
    
    new_blocks = []
    for block in data.get('content_blocks', []):
        if block['type'] == 'text':
            block['content'] = fix_text(block['content'])
        new_blocks.append(block)
    
    data['content_blocks'] = new_blocks
    save_lesson(lesson_num, data)
    print(f"  Fixed lesson {lesson_num}")

def main():
    for lesson_num in range(15, 34):
        process_lesson(lesson_num)
    print("All specific fixes applied!")

if __name__ == "__main__":
    main()