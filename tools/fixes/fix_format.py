#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Format lessons to have beautiful HTML content.
"""

import json
import re
from pathlib import Path

def markdown_to_html(text: str) -> str:
    """Convert markdown-like text to HTML with proper code block handling."""
    if not text:
        return text
    
    # 1. Protect code blocks (```...```)
    code_blocks = []
    def protect_code(match):
        code_blocks.append(match.group(0))
        return f"{{{{CODE_BLOCK_{len(code_blocks)-1}}}}}"
    
    text = re.sub(r'```.*?```', lambda m: protect_code(m), text, flags=re.DOTALL)
    
    # Protect inline code (`code`)
    inline_codes = []
    def protect_inline(match):
        inline_codes.append(match.group(0))
        return f"{{{{INLINE_CODE_{len(inline_codes)-1}}}}}"
    
    text = re.sub(r'`[^`]+`', lambda m: f"{{{{INLINE_CODE_{len(inline_codes)}}}}}", text)
    
    # --- Apply markdown to HTML ---
    
    # 1. Code blocks: ```lang\ncode``` -> <pre><code class="language-lang">code</code></pre>
    def replace_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        return f'<pre><code class="language-{lang}">{code}</code></pre>'
    
    text = re.sub(r'```(\w*)\n(.*?)\n```', 
                  lambda m: f'<pre><code class="language-{m.group(1)}">{m.group(2)}</code></pre>', 
                  text, flags=re.DOTALL)
    
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Headers
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


def style_text(text: str) -> str:
    """Apply HTML styling to text."""
    if not text:
        return text
    
    # Remove existing HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # 1. Protect code blocks (```...```)
    code_blocks = []
    def protect_code(match):
        code_blocks.append(match.group(0))
        return f"{{{{CODE_BLOCK_{len(code_blocks)-1}}}}}"
    
    text = re.sub(r'```.*?```', lambda m: protect_code(m), text, flags=re.DOTALL)
    
    # Protect inline code (`code`)
    inline_codes = []
    def protect_inline(match):
        inline_codes.append(match.group(0))
        return f"{{{{INLINE_CODE_{len(inline_codes)-1}}}}}"
    
    text = re.sub(r'`[^`]+`', lambda m: f"{{{{INLINE_CODE_{len(inline_codes)}}}}}", text)
    
    # --- Apply styling ---
    
    # 1. Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # 2. Code blocks: ```lang\ncode``` -> <pre><code class="language-lang">code</code></pre>
    def replace_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        return f'<pre><code class="language-{lang}">{code}</code></pre>'
    
    text = re.sub(r'```(\w*)\n(.*?)\n```', 
                  lambda m: f'<pre><code class="language-{m.group(1)}">{m.group(2)}</code></pre>', 
                  text, flags=re.DOTALL)
    
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
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
            styled = markdown_to_html(clean)
            if styled != block['content']:
                block['content'] = styled
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Formatted: {filepath.name}')

def markdown_to_html(text: str) -> str:
    """Convert markdown-like text to HTML with proper code block handling."""
    if not text:
        return text
    
    # 1. Protect code blocks (```...```)
    code_blocks = []
    def protect_code(match):
        code_blocks.append(match.group(0))
        return f"{{{{CODE_BLOCK_{len(code_blocks)-1}}}}}"
    
    text = re.sub(r'```.*?```', lambda m: f"{{{{CODE_BLOCK_{len(code_blocks)}}}}}", text, flags=re.DOTALL)
    
    # Actually, let's use a simpler approach - protect code blocks first
    code_blocks = []
    def protect_code(match):
        code_blocks.append(match.group(0))
        return f"{{{{CODE_BLOCK_{len(code_blocks)-1}}}}}"
    
    text = re.sub(r'```.*?```', lambda m: f"{{{{CODE_BLOCK_{len(code_blocks)}}}}}", text, flags=re.DOTALL)
    # Need to fix the protection
    # Let's use a different approach - find all code blocks first
    code_blocks = []
    def find_code_blocks(text):
        blocks = []
        for match in re.finditer(r'```.*?```', text, flags=re.DOTALL):
            blocks.append(match.group(0))
        return blocks
    
    code_blocks = find_code_blocks(text)
    # Replace code blocks with placeholders
    for i, block in enumerate(code_blocks):
        text = text.replace(block, f"{{{{CODE_BLOCK_{i}}}}}", 1)
    
    # Protect inline code
    inline_codes = re.findall(r'`[^`]+`', text)
    for i, code in enumerate(inline_codes):
        text = text.replace(code, f"{{{{INLINE_CODE_{i}}}}}", 1)
    
    # Apply markdown transformations
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
    
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
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

def markdown_to_html(text: str) -> str:
    """Convert markdown-like text to HTML with proper code block handling."""
    if not text:
        return text
    
    # 1. Protect code blocks (```...```)
    code_blocks = []
    def protect_code(match):
        code_blocks.append(match.group(0))
        return f"{{{{CODE_BLOCK_{len(code_blocks)-1}}}}}"
    
    text = re.sub(r'```.*?```', lambda m: f"{{{{CODE_BLOCK_{len(code_blocks)}}}}}", text, flags=re.DOTALL)
    
    # Protect inline code (`code`)
    inline_codes = []
    def protect_inline(match):
        inline_codes.append(match.group(0))
        return f"{{{{INLINE_CODE_{len(inline_codes)-1}}}}}"
    
    text = re.sub(r'`[^`]+`', lambda m: f"{{{{INLINE_CODE_{len(re.findall(r'`[^`]+`', text))}}}}}", text)
    
    # --- Now apply transformations to text WITHOUT code blocks ---
    
    # 1. Code blocks: ```lang\ncode``` -> <pre><code class="language-lang">code</code></pre>
    def replace_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        return f'<pre><code class="language-{lang}">{code}</code></pre>'
    
    text = re.sub(r'```(\w*)\n(.*?)\n```', 
                  lambda m: f'<pre><code class="language-{m.group(1)}">{m.group(2)}</code></pre>', 
                  text, flags=re.DOTALL)
    
    # Inline code: `code` -> <code>code</code>
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # 2. Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Italic
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
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
                block['content'] = markdown_to_html(block['content'])
        
        with open(lesson_file, 'w', encoding='utf-8') as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'Formatted: {lesson_file.name}')
    
    print('All lessons formatted!')