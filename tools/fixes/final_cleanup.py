#!/usr/bin/env python3
"""
Final comprehensive cleanup for all lessons:
- Fix garbled text in tables and headings
- Clean up code block formatting
- Ensure term definitions are properly placed
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

def clean_text(text):
    """Fix garbled text patterns"""
    # Fix the "4 типа:" duplication
    text = re.sub(r'4 типа:\s*Unary, Server/Client/Bidi Streaming\.\s*4 типа:\s*Unary, Server Streaming\s*, Client Streaming, Bidi Streaming\.\s*streaming\.', 
                  '4 типа: Unary, Server Streaming, Client Streaming, Bidi Streaming.', text)
    
    # Fix ConfigureAwait table garbling
    text = re.sub(r'\| Контекст \| ConfigureAwait\n\n, а не в исходном контексте \(UI/ASP.NET\). В библиотеках — всегда false\.\(true\) \| ConfigureAwait\(false\) \|',
                  '| Контекст | ConfigureAwait(true) | ConfigureAwait(false) |', text)
    
    # Fix ConfigureAwait rule text
    text = re.sub(r'<strong>Правило</strong>: в библиотеках <strong>всегда</strong> используйте <code>\.ConfigureAwait\n\n\n, а не в исходном контексте \(UI/ASP.NET\). В библиотеках — всегда false\.\(false\)</code>\. В UI коде — <code>true</code> \(по умолчанию\)\.',
                  '<strong>Правило</strong>: в библиотеках <strong>всегда</strong> используйте <code>.ConfigureAwait(false)</code>. В UI коде — <code>true</code> (по умолчанию).', text)
    
    # Fix ValueTask heading
    text = re.sub(r'<h2>🎯 ValueTask\n\n и IValueTaskSource — для высокой производительности</h2>',
                  '<h2>🎯 ValueTask и IValueTaskSource — для высокой производительности</h2>', text)
    
    # Fix duplicate "4 типа:" in other places
    text = re.sub(r'4 типа:\s*Unary, Server/Client/Bidi Streaming\.\s*4 типа:', '4 типа:', text)
    
    # Fix any remaining "\n\n\n." patterns
    text = re.sub(r'\n\n\n\.', '\n\n.', text)
    
    # Fix table rows with garbled content
    text = re.sub(r'\|\s*Контекст\s*\|\s*ConfigureAwait\n\n, а не в исходном контексте \(UI/ASP\.NET\)\. В библиотеках — всегда false\.\(true\)\s*\|\s*ConfigureAwait\(false\)\s*\|',
                  '| Контекст | ConfigureAwait(true) | ConfigureAwait(false) |', text)
    
    return text

def clean_code(code):
    """Clean up code blocks"""
    # Remove extra blank lines at start
    code = re.sub(r'^\s*\n+', '', code)
    # Remove trailing whitespace
    code = '\n'.join(line.rstrip() for line in code.split('\n'))
    # Ensure single blank line between comment and code
    code = re.sub(r'(// Используется:[^\n]*)\n\s*\n+(?=\w)', r'\1\n', code)
    return code

def process_lesson(lesson_num):
    print(f"Final cleaning lesson {lesson_num}...")
    data = load_lesson(lesson_num)
    
    new_blocks = []
    for block in data.get('content_blocks', []):
        if block['type'] == 'text':
            block['content'] = clean_text(block['content'])
        elif block['type'] == 'code':
            block['content'] = clean_code(block['content'])
        new_blocks.append(block)
    
    data['content_blocks'] = new_blocks
    save_lesson(lesson_num, data)
    print(f"  Final cleaned lesson {lesson_num}")

def main():
    for lesson_num in range(15, 34):
        process_lesson(lesson_num)
    print("All lessons final cleaned!")

if __name__ == "__main__":
    main()