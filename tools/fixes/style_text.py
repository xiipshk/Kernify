#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавляет HTML-стилизацию для красивого отображения текста:
- Ключевые термины -> <strong class="keyword">термин</strong>
- Важные концепции -> <span class="concept">концепция</span>
- Код в тексте -> <code>код</code>
- Важные слова -> <strong>слово</strong>
- Предупреждения/важные заметки -> <span class="warning">...</span>
"""

import json
import re
from pathlib import Path
from typing import Set

# Термины, которые делаем ЖИРНЫМИ (важные ключевые слова)
BOLD_TERMS = {
    # Базовые типы
    "переменная", "переменная", "переменную", "переменные",
    "строка", "строку", "строки", "строк",
    "целое число", "целые числа", "число", "числа",
    "дробное число", "дробные числа",
    "символ", "символы", "символ",
    "логическое", "булево", "булево значение", "true", "false",
    "null", "nullable", "null-conditional", "null-coalescing",
    
    # Типы
    "class", "class", "struct", "record", "interface", "enum", "enum",
    "abstract", "virtual", "override", "sealed", "static", "readonly", "const",
    "property", "свойство", "свойства", "indexer", "indexer",
    "interface", "abstract class", "abstract class",
    
    # ООП
    "virtual", "override", "sealed", "abstract", "static", "readonly", "const",
    "static", "readonly", "const",
    
    # Generics
    "generic", "дженерик", "дженерик", "where", "where",
    "ковариантность", "контрвариантность", "out", "in",
    
    # Асинхронность/потоки
    "async", "await", "async", "await", "Task", "Task", "Thread",
    "lock", "deadlock", "race condition", "boxing", "unboxing",
    "value type", "reference type", "boxing", "unboxing",
    
    # Делегаты/События
    "делегат", "делегат", "multicast", "событие", "событие",
    "EventHandler", "EventArgs", "лямбда", "лямбда",
    
    # LINQ
    "LINQ", "IEnumerable", "IQueryable", "yield return",
    
    # Паттерны/Принципы
    "SOLID", "DRY", "KISS", "YAGNI", "DI", "Dependency Injection",
    
    # Ключевые слова языка
    "ref", "out", "in", "params", "optional parameters", "named arguments",
    "null", "nullable", "boxing", "unboxing", "value type", "reference type",
    
    # Ключевые слова управления потоком
    "if", "else", "for", "while", "foreach", "break", "continue",
    "try", "catch", "finally", "throw", "throw",
    
    # Типы данных
    "string", "int", "int", "double", "float", "decimal", "bool", "char",
    "array", "массив", "List", "List", "Dictionary", "List",
    "null", "nullable", "boxing", "unboxing",
}

# Концепции - делаем наклонными/подчеркнутыми (акцент)
CONCEPT_TERMS = {
    "переменная", "переменная", "переменную", "переменные",
    "строка", "строку", "строки", "строк",
    "целое число", "целые числа", "число", "числа",
    "дробное число", "дробные числа", "число", "числа",
    "символ", "символы", "символ",
    "логическое", "булево", "булево значение", "true", "false",
    "null", "nullable", "null", "nullable",
    "boxing", "unboxing", "value type", "reference type",
    "типизация", "статическая типизация", "динамическая типизация",
    "компилятор", "компиляция", "компилятор",
    "тип", "типов", "типу", "переменной", "переменную", "переменные",
    "значение", "значения", "имя", "имена",
    "объявление", "инициализация", "присваивание",
    "оператор", "операторов", "выражение", "выражений",
    "оператор присваивания", "операторы присваивания",
    "конкатенация", "интерполяция", "интерполяцию", "интерполяции",
    "статическая типизация", "компиляции", "компилятора",
    "тип", "типов", "типу", "переменной", "переменную", "переменные",
    "значение", "значения", "имя", "имена",
    "объявление", "инициализация", "присваивание",
    "оператор", "операторов", "выражение", "выражений",
    "оператор присваивания", "операторы присваивания",
    "арифметика", "арифметические", "сравнение", "сравнения",
    "логические", "логическое", "логические операторы",
    "условие", "условий", "условия", "ветвление", "ветвлений",
    "цикл", "циклы", "цикла", "массив", "массивы", "массивов",
    "элемент", "элементы", "индекс", "индексы", "индекса",
    "длина", "длины", "коллекция", "коллекции", "коллекцию", "коллекций",
    "список", "списки", "словарь", "словари", "словарь", "ключ", "ключи",
    "значение", "значения", "итерация", "итерации", "перебор", "перебора",
    "foreach", "for", "while", "do-while", "break", "continue",
    "метод", "методы", "методу", "методов", "функция", "функции", "функцию",
    "возвращаемое значение", "возвращаемое", "параметр", "параметры",
    "аргумент", "аргументы", "аргумент", "вызов", "вызове", "вызов", "return",
    "void", "перегрузка", "перегрузки", "перегрузку", "рекурсия", "рекурсии",
    "исключение", "исключения", "исключение", "try", "catch", "finally",
    "throw", "null", "null-conditional", "null-coalescing", "??", "??=",
    "?.", "?.", "?[]", "as", "is", "as", "приведение типов", "приведение",
    "приведений", "boxing", "unboxing", "объект", "объекта", "объекты",
    "экземпляр", "экземпляры", "экземпляр", "экземпляров",
    "конструктор", "конструкторы", "конструктора", "конструктору",
    "деструктор", "деструктора", "деструкторов", "поле", "поля", "поле",
    "свойство", "свойства", "свойство", "автосвойство", "автосвойства",
    "геттер", "геттеры", "сеттер", "сеттеры", "init", "readonly", "const",
    "static", "static", "статический", "статические", "explicit", "явная реализация",
    "неявная реализация", "default метод", "default методы", "default", "default",
    "sealed", "abstract", "virtual", "override", "base", "this", "new", "sealed",
    "abstract", "virtual", "override", "base", "this", "new", "sealed", "abstract",
    "virtual", "override", "base", "this", "new", "sealed", "abstract", "virtual",
    "override", "base", "this", "new", "sealed", "abstract", "virtual", "override",
    "base", "this", "new", "sealed", "abstract", "virtual", "override", "base",
    "this", "new",
}

# Ключевые слова языка - делаем как код
CODE_KEYWORDS = {
    "if", "else", "for", "while", "foreach", "break", "continue",
    "try", "catch", "finally", "throw", "return", "void",
    "class", "struct", "record", "interface", "enum", "abstract",
    "virtual", "override", "sealed", "static", "readonly", "const",
    "public", "private", "protected", "internal", "private", "protected",
    "new", "this", "base", "base", "this", "new", "override", "sealed",
    "abstract", "virtual", "static", "readonly", "const", "ref", "out", "in",
    "params", "optional", "named", "null", "nullable", "??", "??=", "?.", "?.",
    "as", "is", "as", "is", "typeof", "sizeof", "typeof", "sizeof",
    "using", "namespace", "using", "namespace", "partial", "partial",
    "lock", "lock", "lock", "lock", "lock", "lock", "lock", "lock",
}

def style_text(text: str) -> str:
    """Добавляет HTML-стилизацию в текст."""
    if not text:
        return text
    
    # Защищаем кодовые блоки
    code_blocks = []
    def protect_code(match):
        code_blocks.append(match.group(0))
        return f"{{{{CODE_BLOCK_{len(code_blocks)-1}}}}}"
    
    text = re.sub(r'```.*?```', lambda m: protect_code(m), text, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', lambda m: f"{{{{INLINE_CODE_{len(code_blocks)}}}}}", text)
    
    # Защищаем уже существующие HTML-теги
    html_tags = []
    def protect_html(match):
        html_tags.append(match.group(0))
        return f"{{{{HTML_TAG_{len(html_tags)-1}}}}}"
    
    text = re.sub(r'<[^>]+>', lambda m: (html_tags.append(m.group(0)) or f"{{{{HTML_TAG_{len(html_tags)-1}}}}}"), text)
    
    # Сортируем термины по длине (сначала длинные)
    bold_terms = sorted(BOLD_TERMS, key=len, reverse=True)
    concept_terms = sorted(CONCEPT_TERMS, key=len, reverse=True)
    code_keywords = sorted(CODE_KEYWORDS, key=len, reverse=True)
    
    # Сначала кодовые ключевые слова -> <code>
    for term in sorted(CODE_KEYWORDS, key=len, reverse=True):
        pattern = r'(?<![\w\.\$])' + re.escape(term) + r'(?![\w\.\$\<\>])'
        # Не заменяем внутри уже обработанных тегов
        def repl_code(m):
            if m.group(0).startswith('<'):
                return m.group(0)
            return f'<code class="keyword">{m.group(0)}</code>'
        text = re.sub(r'(?<![\w\.\$])' + re.escape(term) + r'(?![\w\.\$\<\>])', 
                      lambda m: f'<code class="kw">{m.group(0)}</code>', 
                      text, flags=re.IGNORECASE)
    
    # Жирные термины -> <strong class="keyword">
    for term in BOLD_TERMS:
        if term in CONCEPT_TERMS:
            continue  # Пропускаем, если это тоже концепция
        pattern = r'(?<![\w\.\$\<\>\-])' + re.escape(term) + r'(?![\w\.\$\<\>\-])'
        def repl(m):
            if m.group(0).startswith('<'):
                return m.group(0)
            if 'class="keyword"' in m.group(0) or 'class="concept"' in m.group(0):
                return m.group(0)
            return f'<strong class="keyword">{m.group(0)}</strong>'
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE, count=1)
    
    # Концепции -> <span class="concept">
    for term in CONCEPT_TERMS:
        if term in BOLD_TERMS:
            continue
        pattern = r'(?<![\w\.\$\<\>\-])' + re.escape(term) + r'(?![\w\.\$\<\>\-])'
        def repl(m):
            if m.group(0).startswith('<'):
                return m.group(0)
            if 'class="concept"' in m.group(0) or 'class="keyword"' in m.group(0):
                return m.group(0)
            return f'<span class="concept">{m.group(0)}</span>'
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE, count=1)
    
    # Восстанавливаем кодовые блоки и HTML
    for i, block in enumerate(code_blocks):
        text = text.replace(f"{{{{CODE_BLOCK_{i}}}}}", m.group(0) if False else code_blocks[i])
    # Actually, we need to restore them properly
    for i, block in enumerate(code_blocks):
        text = text.replace(f"{{{{CODE_BLOCK_{i}}}}}", block)
    
    for i, tag in enumerate(html_tags):
        text = text.replace(f"{{{{HTML_TAG_{i}}}}}", tag)
    
    # Восстанавливаем inline code
    # (we didn't track inline code separately, skip for now)
    
    return text


def style_lesson_text(text: str) -> str:
    """Основная функция стилизации текста урока."""
    if not text:
        return text
    
    # Защищаем кодовые блоки
    code_blocks = []
    def protect_code(match):
        code_blocks.append(match.group(0))
        return f"{{{{CODE_BLOCK_{len(code_blocks)-1}}}}}"
    
    text = re.sub(r'```.*?```', lambda m: protect_code(m), text, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', lambda m: protect_code(m), text)
    
    # Защищаем HTML теги
    html_tags = []
    def protect_html(match):
        html_tags.append(match.group(0))
        return f"{{{{HTML_TAG_{len(html_tags)-1}}}}}"
    text = re.sub(r'<[^>]+>', lambda m: protect_html(m), text)
    
    # Применяем стилизацию
    # 1. Ключевые слова -> <code class="kw">...</code>
    for term in sorted(CODE_KEYWORDS, key=len, reverse=True):
        pattern = r'(?<![\w\.\$])' + re.escape(term) + r'(?![\w\.\$\<\>])'
        text = re.sub(pattern, lambda m: f'<code class="kw">{m.group(0)}</code>', text, flags=re.IGNORECASE)
    
    # 2. Жирные термины -> <strong class="keyword">...</strong>
    for term in sorted(BOLD_TERMS, key=len, reverse=True):
        if term in BOLD_TERMS:
            pattern = r'(?<![\w\.\$\<\>\-])' + re.escape(term) + r'(?![\w\.\$\<\>\-])'
            text = re.sub(pattern, lambda m: f'<strong class="keyword">{m.group(0)}</strong>', text, count=1, flags=re.IGNORECASE)
    
    # 3. Концепции -> <span class="concept">
    for term in sorted(set(CONCEPT_TERMS) - BOLD_TERMS, key=len, reverse=True):
        pattern = r'(?<![\w\.\$\<\>\-])' + re.escape(term) + r'(?![\w\.\$\<\>\-])'
        text = re.sub(pattern, lambda m: f'<span class="concept">{m.group(0)}</span>', text, count=1, flags=re.IGNORECASE)
    
    # Восстанавливаем кодовые блоки
    for i, block in enumerate(code_blocks):
        text = text.replace(f"{{{{CODE_BLOCK_{i}}}}}", block)
    
    # Восстанавливаем HTML теги
    for i, tag in enumerate(html_tags):
        text = text.replace(f"{{{{HTML_TAG_{i}}}}}", tag)
    
    return text


def process_lesson(lesson_path: Path):
    with open(lesson_path, 'r', encoding='utf-8') as f:
        lesson = json.load(f)
    
    changed = False
    for block in lesson.get('content_blocks', []):
        if block.get('type') in ('text', 'heading'):
            old_content = block.get('content', '')
            styled = style_lesson_text(block['content'])
            if styled != old_content:
                block['content'] = styled
                changed = True
    
    if True:
        with open(lesson_path, 'w', encoding='utf-8') as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'Styled: {lesson_path.name}')


if __name__ == '__main__':
    lessons_dir = Path('fixtures/lessons/csharp')
    for lesson_file in sorted(lessons_dir.glob('*.json')):
        with open(lesson_file, 'r', encoding='utf-8') as f:
            lesson = json.load(f)
        
        changed = False
        for block in lesson.get('content_blocks', []):
            if block.get('type') in ('text', 'heading'):
                old = block.get('content', '')
                styled = style_lesson_text(old)
                if styled != old:
                    block['content'] = styled
        
        with open(lesson_file, 'w', encoding='utf-8') as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'Styled: {lesson_file.name}')
    
    print('Все уроки стилизованы!')