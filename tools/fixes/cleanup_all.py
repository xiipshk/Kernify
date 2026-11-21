#!/usr/bin/env python3
"""
Remove ALL 'Где применяется' injections - they're causing more harm than good.
Keep only the 'Термин:' definitions which were correctly added.
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

def remove_all_gde_primenyaetsya(text):
    """Remove ALL 'Где применяется' blocks"""
    # Remove all "Где применяется" blocks
    text = re.sub(r'\n\n> 💡 \*\*Где применяется:\*\*[^\n]*', '', text)
    # Clean up any leftover newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def process_lesson(lesson_num):
    print(f"Cleaning lesson {lesson_num}...")
    data = load_lesson(lesson_num)
    
    new_blocks = []
    for block in data.get('content_blocks', []):
        if block['type'] == 'text':
            block['content'] = remove_all_gde_primenyaetsya(block['content'])
        new_blocks.append(block)
    
    data['content_blocks'] = new_blocks
    save_lesson(lesson_num, data)
    print(f"  Cleaned lesson {lesson_num}")

def main():
    for lesson_num in range(15, 34):
        process_lesson(lesson_num)
    print("All 'Где применяется' removed!")

if __name__ == "__main__":
    main()