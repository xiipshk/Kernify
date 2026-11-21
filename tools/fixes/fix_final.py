#!/usr/bin/env python3
"""
Final fix for:
1. Broken term injections in text (mid-sentence, duplicates, broken formatting)
2. Duplicate code comments
3. Clean up any remaining artifacts
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

def clean_code_block(code):
    """Remove duplicate context comments and clean up"""
    lines = code.split('\n')
    cleaned = []
    seen = set()
    
    for line in lines:
        stripped = line.strip()
        # Track context comments
        if stripped.startswith('// Используется:') or stripped.startswith('# Используется:'):
            if stripped in seen:
                continue
            seen.add(stripped)
        # Skip the "// //" double comment lines
        if stripped.startswith('// //'):
            continue
        cleaned.append(line)
    
    result = '\n'.join(cleaned)
    # Remove any remaining double-slash comments
    result = re.sub(r'\n\s*// // Используется:', '\n// Используется:', result)
    return result

def clean_text_block(text):
    """Fix broken term injections in text blocks"""
    # Fix the broken IQueryable vs IEnumerable injection
    # Pattern: "s.\n\n> 💡 **Термин:** ...\n\n> 💡 **Термин:** ..."
    text = re.sub(r's\.\s*\n\s*>\s*💡\s*\*\*Термин:\*\*[^\n]*\n\s*>\s*💡\s*\*\*Термин:\*\*[^\n]*', 's.', text)
    
    # Fix broken term definitions with duplicated content
    text = re.sub(r'(>\s*💡\s*\*\*Термин:\*\*[^\n]*)\n\s*\1', r'\1', text)
    
    # Fix broken term definitions that have garbled content
    # Pattern: > 💡 **Термин:** [content with newlines and duplicates]
    def fix_term_def(match):
        content = match.group(0)
        # Extract first sentence only
        lines = content.split('\n')
        first_line = lines[0]
        # Clean up the definition
        if 'Термин:' in first_line:
            # Keep only the first definition
            return first_line
        return content
    
    # Remove any term definitions that appear mid-sentence or have broken formatting
    # Match: > 💡 **Термин:** ... (multiline until next block or end)
    text = re.sub(r'\n\s*>\s*💡\s*\*\*Термин:\*\*[^\n]*\n\s*>\s*💡\s*\*\*Термин:\*\*[^\n]*', '\n', text)
    
    # Fix the specific broken IQueryable vs IEnumerable case
    text = re.sub(
        r'🎯 IQueryable\s*\n\s*s\.\s*\n\s*>\s*💡\s*\*\*Термин:\*\*[^<]*',
        '🎯 IQueryable vs IEnumerable',
        text
    )
    
    # Remove any remaining term definitions that are malformed
    # (appear in the middle of content, have duplicated text, etc.)
    text = re.sub(r'\n\s*>\s*💡\s*\*\*Термин:\*\*[^\n]*\n\s*>\s*💡\s*\*\*Термин:\*\*[^\n]*', '\n', text)
    
    # Clean up any term definition that has "Позволяет переводить LINQ в SQL (EF Core)." duplicated
    text = re.sub(r'(Позволяет переводить LINQ в SQL \(EF Core\)\.)\s*\1', r'\1', text)
    text = re.sub(r'(Базовый интерфейс для перечисления коллекций\.)\s*\1', r'\1', text)
    
    # Remove standalone broken term definitions that don't follow a proper term mention
    text = re.sub(r'\n\s*>\s*💡\s*\*\*Термин:\*\*[^\n]*Expression Tree[^\n]*', '', text)
    
    return text

def process_lesson(lesson_num):
    print(f"Cleaning lesson {lesson_num}...")
    data = load_lesson(lesson_num)
    
    new_blocks = []
    for block in data.get('content_blocks', []):
        if block['type'] == 'code':
            block['content'] = clean_code_block(block['content'])
        elif block['type'] == 'text':
            block['content'] = clean_text_block(block['content'])
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