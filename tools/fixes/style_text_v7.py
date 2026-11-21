#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавляет HTML-стилизацию для красивого отображения текста.
Упрощенная версия без защиты HTML тегов (на входе чистый текст).
"""

import json
import re
from pathlib import Path

# Термины, которые делаем ЖИРНЫМИ (важные ключевые слова)
BOLD_TERMS = {
    "переменная", "переменную", "переменные",
    "строка", "строку", "строки", "строк",
    "целое число", "целые числа", "число", "числа",
    "дробное число", "дробные числа",
    "символ", "символы", "символ",
    "логическое", "булево", "булево значение", "true", "false",
    "null", "nullable",
    "class", "struct", "record", "interface", "enum",
    "abstract", "virtual", "override", "sealed", "static", "readonly", "const",
    "property", "свойство", "свойства", "indexer",
    "interface", "abstract class",
    "virtual", "override", "sealed", "abstract", "static", "readonly", "const",
    "generic", "дженерик", "дженерик", "where",
    "ковариантность", "контрвариантность", "out", "in",
    "async", "await", "Task", "Thread", "lock", "deadlock", "race condition", "boxing", "unboxing",
    "value type", "reference type", "boxing", "unboxing",
    "делегат", "multicast", "событие", "событие",
    "EventHandler", "EventArgs", "лямбда",
    "LINQ", "IEnumerable", "IQueryable", "yield return",
    "SOLID", "DRY", "KISS", "YAGNI", "DI", "Dependency Injection",
    "ref", "out", "in", "params", "optional parameters", "named arguments",
    "null", "nullable", "boxing", "unboxing", "value type", "reference type",
    "if", "else", "for", "while", "foreach", "break", "continue",
    "try", "catch", "finally", "throw", "return", "void",
    "class", "struct", "record", "interface", "enum", "abstract",
    "virtual", "override", "sealed", "static", "readonly", "const",
    "public", "private", "protected", "internal",
    "new", "this", "base", "override", "sealed",
    "abstract", "virtual", "static", "readonly", "const",
    "ref", "out", "in", "params", "optional", "named", "null", "nullable",
    "??", "??=", "?.", "?.", "?[]", "as", "is", "typeof", "sizeof",
    "using", "namespace", "partial", "lock",
    "int", "string", "double", "float", "bool", "char", "byte",
    "short", "long", "uint", "ushort", "ulong", "decimal",
}

# Концепции - делаем акцентом (курсив/подчеркнутый)
CONCEPT_TERMS = {
    "переменная", "переменную", "переменные",
    "строка", "строку", "строки", "строк",
    "целое число", "целые числа", "число", "числа",
    "дробное число", "дробные числа", "число", "числа",
    "символ", "символы", "символ",
    "логическое", "булево", "булево значение", "true", "false",
    "null", "nullable",
    "типизация", "статическая типизация", "динамическая типизация",
    "компилятор", "компиляция", "компилятор",
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
    "?.", "?.", "?[]", "as", "is", "as", "is", "приведение типов", "приведение",
    "приведение", "приведений", "boxing", "unboxing", "объект", "объекта",
    "объекты", "экземпляр", "экземпляры", "экземпляр", "экземпляров",
    "конструктор", "конструкторы", "конструктора", "конструктору",
    "деструктор", "деструктора", "деструкторов", "поле", "поля", "поле",
    "свойство", "свойства", "свойство", "автосвойство", "автосвойства",
    "геттер", "геттеры", "сеттер", "сеттеры", "init", "readonly", "const",
    "static", "статический", "статические", "explicit", "явная реализация",
    "неявная реализация", "default метод", "default методы", "default",
    "sealed", "abstract", "virtual", "override", "base", "this", "new",
    "sealed", "abstract", "virtual", "override", "base", "this", "new",
    "sealed", "abstract", "virtual", "override", "base", "this", "new",
}

# Концепции - исключаем уже жирные
CONCEPT_TERMS = set(CONCEPT_TERMS) - BOLD_TERMS

# Ключевые слова языка - делаем как код <code class="kw">
CODE_KEYWORDS = {
    "if", "else", "for", "while", "foreach", "break", "continue",
    "try", "catch", "finally", "throw", "return", "void",
    "class", "struct", "record", "interface", "enum", "abstract",
    "virtual", "override", "sealed", "static", "readonly", "const",
    "public", "private", "protected", "internal",
    "new", "this", "base", "override", "sealed",
    "abstract", "virtual", "static", "readonly", "const",
    "ref", "out", "in", "params", "optional", "named", "null", "nullable",
    "??", "??=", "?.", "?.", "?[]", "as", "is", "typeof", "sizeof",
    "using", "namespace", "partial", "lock",
    "int", "string", "double", "float", "bool", "char", "byte",
    "short", "long", "uint", "ushort", "ulong", "decimal",
    "true", "false", "null", "this", "base", "new", "return",
}

# Концепции - исключаем уже жирные
CONCEPT_TERMS = set(CONCEPT_TERMS) - BOLD_TERMS

def style_text(text: str) -> str:
    """Добавляет HTML-стилизацию в текст."""
    if not text:
        return text
    
    # 1. Защищаем кодовые блоки (```...```)
    code_blocks = []
    def protect_code(match):
        code_blocks.append(match.group(0))
        return f"{{{{CODE_BLOCK_{len(code_blocks)-1}}}}}"
    
    text = re.sub(r'```.*?```', lambda m: protect_code(m), text, flags=re.DOTALL)
    
    # Защищаем inline код (`code`)
    inline_codes = []
    def protect_inline(match):
        inline_codes.append(match.group(0))
        return f"{{{{INLINE_CODE_{len(inline_codes)-1}}}}}"
    
    text = re.sub(r'`[^`]+`', lambda m: f"{{{{INLINE_CODE_{len(inline_codes)}}}}}", text)
    
    # --- Теперь применяем стилизацию к тексту БЕЗ кодовых блоков ---
    
    # 1. Ключевые слова языка -> <code class="kw">...</code>
    for term in sorted(CODE_KEYWORDS, key=len, reverse=True):
        pattern = r'(?<![\w\.\$])' + re.escape(term) + r'(?![\w\.\$\<\>])'
        text = re.sub(pattern, lambda m: f'<code class="kw">{m.group(0)}</code>', text, flags=re.IGNORECASE)
    
    # 2. Жирные термины -> <strong class="keyword">
    for term in sorted(BOLD_TERMS, key=len, reverse=True):
        pattern = r'(?<![\w\.\$\<\>\-])' + re.escape(term) + r'(?![\w\.\$\<\>\-])'
        text = re.sub(pattern, lambda m: f'<strong class="keyword">{m.group(0)}</strong>', text, count=1, flags=re.IGNORECASE)
    
    # 3. Концепции -> <span class="concept">
    for term in sorted(CONCEPT_TERMS, key=len, reverse=True):
        pattern = r'(?<![\w\.\$\<\>\-])' + re.escape(term) + r'(?![\w\.\$\<\>\-])'
        text = re.sub(pattern, lambda m: f'<span class="concept">{m.group(0)}</span>', text, count=1, flags=re.IGNORECASE)
    
    # Восстанавливаем кодовые блоки
    for i, block in enumerate(code_blocks):
        text = text.replace(f"{{{{CODE_BLOCK_{i}}}}}", block)
    
    # Восстанавливаем inline код
    for i, code in enumerate(inline_codes):
        text = text.replace(f"{{{{INLINE_CODE_{i}}}}}", inline_codes[i])
    
    return text


def process_lesson(lesson_path: Path):
    with open(lesson_path, 'r', encoding='utf-8') as f:
        lesson = json.load(f)
    
    changed = False
    for block in lesson.get('content_blocks', []):
        if block.get('type') in ('text', 'heading'):
            old_content = block.get('content', '')
            styled = style_text(block['content'])
            if styled != old_content:
                block['content'] = styled
                changed = True
    
    with open(lesson_path, 'w', encoding='utf-8') as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Styled: {lesson_path.name}')


if __name__ == '__main__':
    lessons_dir = Path('fixtures/lessons/csharp')
    for lesson_file in sorted(lessons_dir.glob('*.json')):
        with open(lesson_file, 'r', encoding='utf-8') as f:
            lesson = json.load(f)
        
        for block in lesson.get('content_blocks', []):
            if block.get('type') in ('text', 'heading'):
                block['content'] = style_text(block['content'])
        
        with open(lesson_file, 'w', encoding='utf-8') as f:
            json.dump(lesson, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'Styled: {lesson_file.name}')
    
    print('Все уроки стилизованы!')