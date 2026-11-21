#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Преобразует контент уроков в красивый HTML с правильной стилизацией.
"""

import json
import re
from pathlib import Path

def format_lesson_content(text: str) -> str:
    """Преобразует markdown-подобный текст в красивый HTML."""
    if not text:
        return text
    
    # Сначала защищаем кодовые блоки
    code_blocks = []
    def protect_code(match):
        return f"{{{{CODE_BLOCK_{len(code_blocks)}}}}}"
    
    text = re.sub(r'```(\w+)?\n(.*?)\n```', 
                  lambda m: f'{{{{CODE_BLOCK_{len(re.findall(r"```.*?```", text, re.DOTALL))}}}}}', 
                  text, flags=re.DOTALL)
    
    # Обрабатываем inline код
    text = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', text)
    
    # Заголовки markdown -> HTML
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Жирный текст **text** -> <strong>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Курсив *text* -> <em>
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    # Списки
    text = re.sub(r'^\- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+)\. (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    
    # Оборачиваем списки в <ul>/<ol>
    text = re.sub(r'(<li>.*?</li>\n)+', lambda m: '<ul>\n' + m.group(0) + '</ul>\n', text)
    text = re.sub(r'(<li>\d+\..*?</li>\n)+', lambda m: '<ol>\n' + m.group(0) + '</ol>\n', text)
    
    # Параграфы
    text = re.sub(r'\n\n+', '</p>\n<p>', text)
    text = '<p>' + text + '</p>'
    
    # Очистка пустых параграфов
    text = re.sub(r'<p>\s*</p>', '', text)
    
    return text


def format_lesson_content(text: str) -> str:
    """Форматирует контент урока в красивый HTML."""
    if not text:
        return text
    
    # Удаляем существующие HTML теги
    text = re.sub(r'<[^>]+>', '', text)
    
    # Используем упрощенный подход: markdown -> HTML
    return markdown_to_html(text)


def markdown_to_html(text: str) -> str:
    """Простой markdown -> HTML конвертер."""
    if not text:
        return text
    
    # Защищаем кодовые блоки
    code_blocks = []
    def protect_code(match):
        return f"{{{{CODE_BLOCK_{len(re.findall(r'```.*?```', text, re.DOTALL))}}}}}"
    
    text = re.sub(r'```.*?```', lambda m: f'{{{{CODE_BLOCK_{len(re.findall(r"```.*?```", text, re.DOTALL))}}}}}', text, flags=re.DOTALL)
    
    # Inline код
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Italic
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    # Code blocks
    def replace_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        return f'<pre><code class="language-{lang}">{escape_html(code)}</code></pre>'
    
    text = re.sub(r'```(\w*)\n(.*?)\n```', 
                  lambda m: f'<pre><code class="language-{m.group(1) or "text"}">{escape_html(m.group(2))}</code></pre>', 
                  text, flags=re.DOTALL)
    
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Italic
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    # Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Lists
    text = re.sub(r'^\- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\n\1</ul>', text)
    
    # Paragraphs
    text = re.sub(r'\n\n+', '</p><p>', text)
    text = '<p>' + text + '</p>'
    text = re.sub(r'<p>\s*</p>', '', text)
    text = re.sub(r'<p><h([1-6])>', r'<h\1>', text)
    text = re.sub(r'</h([1-6])></p>', r'</h\1>', text)
    
    return text


def process_lesson(lesson_path: Path):
    with open(lesson_path, 'r', encoding='utf-8') as f:
        lesson = json.load(f)
    
    changed = False
    for block in lesson.get('content_blocks', []):
        if block.get('type') in ('text', 'heading'):
            old_content = block.get('content', '')
            # Clean existing HTML tags first
            clean_content = re.sub(r'<[^>]+>', '', block['content'])
            styled = markdown_to_html(clean_content)
            if styled != block['content']:
                block['content'] = styled
    
    with open(lesson_path, 'w', encoding='utf-8') as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Formatted: {lesson_path.name}')


if __name__ == '__main__':
    import sys
    lessons_dir = Path('fixtures/lessons/csharp')
    for lesson_file in sorted(lessons_dir.glob('*.json')):
        if lesson_file.name.endswith('.json'):
            try:
                with open(lesson_file, 'r', encoding='utf-8') as f:
                    lesson = json.load(f)
                
                for block in lesson.get('content_blocks', []):
                    if block.get('type') in ('text', 'heading'):
                        old = block.get('content', '')
                        # Clean existing HTML
                        clean = re.sub(r'<[^>]+>', '', block.get('content', ''))
                        clean = re.sub(r'\{\{HTML_TAG_\d+\}\}', '', clean_content)
                        clean = re.sub(r'\{\{INLINE_CODE_\d+\}\}', '', clean_content)
                        clean = re.sub(r'\{\{CODE_BLOCK_\d+\}\}', '', clean_content)
                        # Apply markdown to HTML
                        styled = markdown_to_html(clean_content)
                        if styled != old:
                            lesson['content_blocks'][lesson['content_blocks'].index(block)]['content'] = styled
                
        with open(lesson_file, 'w', encoding='utf-8') as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'Formatted: {lesson_file.name}')
    
    print('All lessons formatted!')