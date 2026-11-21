#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Очищает текст уроков: убирает markdown-разметку (*), нормализует пробелы,
делает текст более читаемым.
"""

import json
import re
from pathlib import Path


def clean_text(text: str) -> str:
    """Очищает текст от markdown-разметки и нормализует пробелы."""
    if not text:
        return text
    
    # Защищаем кодовые блоки
    code_blocks = []
    def protect_code(match):
        code_blocks.append(match.group(0))
        return f"{{{{CODE_BLOCK_{len(code_blocks)-1}}}}}"
    
    text = re.sub(r'```.*?```', protect_code, text, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', protect_code, text)
    
    # Убираем markdown bold: **text** -> text
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    # Убираем одинарные * для курсива (но не в числах типа 5*5)
    text = re.sub(r'(?<!\d)\*([^*\n]+)\*(?!\d)', r'\1', text)
    
    # Убираем заголовки markdown: ### Текст -> Текст
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Убираем markdown ссылки: [текст](url) -> текст
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Восстанавливаем кодовые блоки
    for i, block in enumerate(code_blocks):
        text = text.replace(f"{{{{CODE_BLOCK_{i}}}}}", block)
    
    # Нормализуем пробелы
    # Множественные пробелы -> один
    text = re.sub(r'[ \t]+', ' ', text)
    # Множественные переносы строк -> максимум 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Убираем пробелы в начале/конце строк
    text = '\n'.join(line.strip() for line in text.split('\n'))
    # Убираем пробелы в начале/конце
    text = text.strip()
    
    return text


def process_lesson(lesson_path: Path):
    with open(lesson_path, 'r', encoding='utf-8') as f:
        lesson = json.load(f)
    
    changed = False
    for block in lesson.get('content_blocks', []):
        if block.get('type') in ('text', 'heading'):
            old_content = block.get('content', '')
            cleaned = clean_text(block['content'])
            if cleaned != old_content:
                block['content'] = cleaned
    
    if True:  # Always save
        with open(lesson_path, 'w', encoding='utf-8') as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'Очищен: {lesson_path.name}')


if __name__ == '__main__':
    lessons_dir = Path('fixtures/lessons/csharp')
    for lesson_file in sorted(lessons_dir.glob('*.json')):
        with open(lesson_file, 'r', encoding='utf-8') as f:
            lesson = json.load(f)
        
        changed = False
        for block in lesson.get('content_blocks', []):
            if block.get('type') in ('text', 'heading'):
                old = block.get('content', '')
                cleaned = clean_text(old)
                if cleaned != old:
                    block['content'] = cleaned
        
        with open(lesson_file, 'w', encoding='utf-8') as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'Очищен: {lesson_file.name}')
    
    print('Все уроки очищены!')