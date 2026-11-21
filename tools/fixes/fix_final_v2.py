#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix all lessons: extract code blocks and format properly.
"""

import json
import re
from pathlib import Path

def extract_code_blocks(text):
    """Extract code blocks from text and return (cleaned_text, code_blocks_list)"""
    code_blocks = []
    parts = []
    last_end = 0
    
    for match in re.finditer(r'```(\w*)\n(.*?)\n```', text, flags=re.DOTALL):
        start, end = match.span()
        lang = match.group(1) or 'csharp'
        code = match.group(2).strip()
        
        # Add text before this code block
        if match.start() > last_end:
            parts.append(text[last_end:match.start()])
        
        # Add code block
        code_blocks.append({
            'type': 'code',
            'language': match.group(1) or 'csharp',
            'content': match.group(2).strip()
        })
        last_end = match.end()
    
    # Add remaining text
    if last_end < len(text):
        parts.append(text[last_end:])
    
    clean_text = ''.join(parts)
    return ''.join(parts), code_blocks


def markdown_to_html(text):
    """Convert markdown-like text to HTML with proper code block handling."""
    if not text:
        return text
    
    # 1. Protect code blocks (```...```)
    code_blocks = []
    def protect_code(match):
        return f"{{{{CODE_BLOCK}}}}"
    
    text = re.sub(r'```.*?```', lambda m: f"{{{{CODE_BLOCK}}}}", text, flags=re.DOTALL)
    
    # Protect inline code (`code`)
    inline_codes = []
    def protect_inline(match):
        return f"{{{{INLINE_CODE}}}}"
    
    text = re.sub(r'`[^`]+`', r'<code>\1</code>', text)
    
    # 1. Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Italic
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Code blocks: ```lang\ncode``` -> <pre><code class="language-lang">code</code></pre>
    def replace_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        return f'<pre><code class="language-{lang}">{code}</code></pre>'
    
    text = re.sub(r'```(\w*)\n(.*?)\n```', 
                  lambda m: f'<pre><code class="language-{m.group(1)}">{m.group(2)}</code></pre>', 
                  text, flags=re.DOTALL)
    
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Italic
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    # Lists
    text = re.sub(r'^\- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\n\1</ul>', text)
    
    # Paragraphs
    text = re.sub(r'\n\n+', '</p>\n<p>', text)
    text = '<p>' + text + '</p>'
    text = re.sub(r'<p>\s*</p>', '', text)
    text = re.sub(r'<p>(<h[1-6]>)', r'\1', text)
    text = re.sub(r'</h([1-6])></p>', r'</h\1>', text)
    
    return text


def process_lesson(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lesson = json.load(f)
    
    for block in lesson.get('content_blocks', []):
        if block.get('type') in ('text', 'heading'):
            old = block['content']
            # Clean existing HTML
            clean = re.sub(r'<[^>]+>', '', block['content'])
            # Apply markdown to HTML
            styled = markdown_to_html(clean)
            if styled != block['content']:
                block['content'] = styled
    
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
        
        for block in lesson.get('content_blocks', []):
            if block.get('type') in ('text', 'heading'):
                old = block['content']
                # Clean existing HTML
                clean = re.sub(r'<[^>]+>', '', block['content'])
                # Apply markdown to HTML
                styled = markdown_to_html(clean)
                if styled != block['content']:
                    block['content'] = styled
        
        with open(lesson_file, 'w', encoding='utf-8') as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'Formatted: {lesson_file.name}')
    
    print('All lessons formatted!')