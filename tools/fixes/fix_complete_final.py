#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Полное исправление уроков 12-33: извлечение кодовых блоков из текста и создание отдельных блоков кода.
"""

import json
import re
from pathlib import Path

def extract_code_blocks(text: str):
    """Извлекает кодовые блоки из текста и возвращает (очищенный_текст, список_блоков_кода)"""
    code_blocks = []
    parts = []
    last_end = 0
    
    for match in re.finditer(r'```(\w*)\n(.*?)\n```', text, flags=re.DOTALL):
        start, end = match.span()
        lang = match.group(1) or 'csharp'
        code = match.group(2).strip()
        
        # Добавляем текст перед этим кодовым блоком
        if match.start() > last_end:
            parts.append(text[last_end:match.start()])
        
        # Добавляем кодовый блок
        code_blocks.append({
            'type': 'code',
            'language': match.group(1) or 'csharp',
            'content': match.group(2).strip()
        })
        last_end = match.end()
    
    # Добавляем оставшийся текст
    if last_end < len(text):
        parts.append(text[last_end:])
    
    # Восстанавливаем текст без кодовых блоков
    clean_text = ''.join(parts)
    
    return ''.join(parts), code_blocks


def markdown_to_html(text: str) -> str:
    """Преобразует markdown-подобный текст в HTML с правильной обработкой кодовых блоков."""
    if not text:
        return text
    
    # 1. Защищаем кодовые блоки (```...```)
    code_blocks = []
    def protect_code(match):
        code_blocks.append(match.group(0))
        return f"{{{{CODE_BLOCK_{len(code_blocks)-1}}}}}"
    
    text = re.sub(r'```.*?```', lambda m: f"{{{{CODE_BLOCK_{len(code_blocks)-1}}}}}", text, flags=re.DOTALL)
    
    # Защищаем inline код (`code`)
    inline_codes = []
    def protect_inline(match):
        inline_codes.append(match.group(0))
        return f"{{{{INLINE_CODE_{len(inline_codes)-1}}}}}"
    
    text = re.sub(r'`[^`]+`', lambda m: f"{{{{INLINE_CODE_{len(inline_codes)-1}}}}}", text)
    
    # --- Применяем markdown -> HTML ---
    
    # 1. Заголовки
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Жирный
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Курсив
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    # Inline код
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Блоки кода: ```lang\ncode``` -> <pre><code class="language-lang">code</code></pre>
    def replace_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        return f'<pre><code class="language-{lang}">{code}</code></pre>'
    
    text = re.sub(r'```(\w*)\n(.*?)\n```', 
                  lambda m: f'<pre><code class="language-{m.group(1)}">{m.group(2)}</code></pre>', 
                  text, flags=re.DOTALL)
    
    # Жирный
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Курсив
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    # Списки
    text = re.sub(r'^\- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\n\1</ul>', text)
    
    # Абзацы
    text = re.sub(r'\n\n+', '</p>\n<p>', text)
    text = '<p>' + text + '</p>'
    text = re.sub(r'<p>\s*</p>', '', text)
    text = re.sub(r'<p>(<h[1-6]>)', r'\1', text)
    text = re.sub(r'</h([1-6])></p>', r'</h\1>', text)
    
    return text


def process_lesson(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lesson = json.load(f)
    
    new_blocks = []
    for block in lesson.get('content_blocks', []):
        if block.get('type') in ('text', 'heading'):
            old = block['content']
            # Сначала очищаем от HTML тегов
            clean = re.sub(r'<[^>]+>', '', block['content'])
            
            # Извлекаем кодовые блоки из текста
            clean_text, code_blocks = extract_code_blocks_and_text(block['content'])
            
            # Применяем markdown -> HTML к чистому тексту
            styled = markdown_to_html(clean)
            
            # Обновляем текстовый блок
            block['content'] = styled
            new_blocks.append(block)
            
            # Добавляем кодовые блоки после этого текстового блока
            for cb in code_blocks:
                new_blocks.append({
                    'type': 'code',
                    'language': cb['language'],
                    'content': cb['content']
                })
        else:
            new_blocks.append(block)
    
    # Заменяем content_blocks
    lesson['content_blocks'] = new_blocks
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Formatted: {filepath.name}')

if __name__ == '__main__':
    import re
    from pathlib import Path
    
    lessons_dir = Path('fixtures/lessons/csharp')
    for lesson_file in sorted(Path('fixtures/lessons/csharp').glob('*.json')):
        with open(lesson_file, 'r', encoding='utf-8') as f:
            lesson = json.load(f)
        
        new_blocks = []
        for block in lesson.get('content_blocks', []):
            if block.get('type') in ('text', 'heading'):
                old = block['content']
                # Сначала очищаем HTML
                clean = re.sub(r'<[^>]+>', '', block['content'])
                
                # Извлекаем кодовые блоки из текста
                clean_text, code_blocks = extract_code_blocks_and_text(block['content'])
                
                # Применяем markdown -> HTML
                styled = markdown_to_html(clean)
                
                # Обновляем текстовый блок
                block['content'] = styled
                new_blocks.append(block)
                
                # Добавляем кодовые блоки после этого текстового блока
                for cb in code_blocks:
                    new_blocks.append({
                        'type': 'code',
                        'language': cb['language'],
                        'content': cb['content']
                    })
            else:
                new_blocks.append(block)
        
        # Заменяем content_blocks
        lesson['content_blocks'] = new_blocks
        
        with open(lesson_file, 'w', encoding='utf-8') as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'Formatted: {lesson_file.name}')
    
    print('All lessons formatted!')