"""
Ограничение задач к уроку: задача должна использовать только то,
что пройдено в этом уроке или раньше.

Идея:
  * для каждого урока вычисляем набор «навыков» (конструкций),
    которые реально встречаются в его коде/тексте;
  * навыки накапливаются по цепочке уроков (программа → порядок);
  * для каждой задачи определяем, какие навыки нужны её решению;
  * задача допускается, если все её навыки уже пройдены.

Модуль используется:
  * management-командой ``audit_lesson_tasks`` (отчёт);
  * сервисом ``practice.services.lesson_tasks_for`` (что показывать в уроке).
"""
import json
import re

# Навык -> как распознаём его в коде решения/урока
SKILL_PATTERNS = {
    # вывод (Python / JS / C# / Rust)
    'print': re.compile(
        r'\bprint\s*\(|console\.log\s*\(|Console\.Write\w*\s*\(|'
        r'\bprintln!\s*\(|\bprint!\s*\(|std::cout|\bputs\s*\('
    ),
    # ввод (Python / JS-стандартный ввод / C# / Rust / C++)
    'input': re.compile(
        r'\binput\s*\(|Console\.ReadLine\s*\(|read_to_string\s*\(|'
        r'std::cin|readline\s*\(|prompt\s*\(|fs\.readFileSync'
    ),
    'int': re.compile(r'\bint\s*\(|int\.Parse\s*\(|parseInt\s*\(|\.parse\s*::?<|\bstd::stoi|Convert\.ToInt32'),
    # объявление/инициализация переменных в других языках
    'variables': re.compile(
        r'^\s*[A-Za-z_]\w*\s*=\s*[^=]|'
        r'\b(?:let|const|var|mut)\s+\w+|'
        r'\b(?:int|double|float|long|bool|string|char|auto|size_t|f64|i32|u32|i64|u64|usize)\s+\w+\s*(?:=|;|,|\{)',
        re.MULTILINE
    ),
    'float': re.compile(r'\bfloat\s*\('),
    'str': re.compile(r'\bstr\s*\('),
    'arithmetic': re.compile(r'(?<![+\-*/=<>!])([+\-*/%])(?![=/])'),
    'compare': re.compile(r'(==|!=|<=|>=|<|>|(?<![<>=!])!(?!=))'),
    'if': re.compile(r'^\s*(if|elif|else\s+if)\s*[(:]|^\s*if\s+\w', re.MULTILINE),
    'ternary': re.compile(r'\bif\b.+\belse\b'),
    'else': re.compile(r'^\s*else\s*:', re.MULTILINE),
    'for': re.compile(r'^\s*for\s*[(\w]', re.MULTILINE),
    'while': re.compile(r'^\s*while\s*[(\w]', re.MULTILINE),
    'range': re.compile(r'\brange\s*\('),
    'def': re.compile(r'^\s*def\s+\w+|^\s*(?:public|private|static|void|int|float|double|bool|string|fn)\s+\w+\s*\(', re.MULTILINE),
    'return': re.compile(r'^\s*return\b', re.MULTILINE),
    'list': re.compile(r'\blist\s*\(|\[\s*[\'"]'),
    'index': re.compile(r'\w\s*\[\s*\w+'),
    'slice': re.compile(r'\[[^\]]*:[^\]]*\]'),
    'append': re.compile(r'\.append\s*\('),
    'split': re.compile(r'\.split\s*\('),
    'join': re.compile(r'\.join\s*\('),
    'dict': re.compile(r'\bdict\s*\(|\{\s*[\'"]'),
    'set': re.compile(r'\bset\s*\(|set\(\)'),
    'len': re.compile(r'\blen\s*\('),
    'minmax': re.compile(r'\b(min|max)\s*\('),
    'sum': re.compile(r'\bsum\s*\('),
    'sorted': re.compile(r'\bsorted\s*\(|\.sort\s*\('),
    'math': re.compile(r'^\s*(import math|from math)\b|\bmath\.\w+', re.MULTILINE),
    'import': re.compile(r'^\s*(import|from)\s', re.MULTILINE),
    'try': re.compile(r'^\s*try\s*:', re.MULTILINE),
    'class': re.compile(r'^\s*class\s+\w+', re.MULTILINE),
    'lambda': re.compile(r'\blambda\b'),
    'comprehension': re.compile(r'\[\s*[^\]]*\bfor\b[^\]]*\]'),
    'fstring': re.compile(r'f[\'"].*\{'),
}

# Более «продвинутые» навыки: задача не должна применяться раньше урока,
# где они реально встречаются.
BASIC_SKILLS = {'print', 'variables', 'arithmetic', 'int', 'str', 'float', 'input'}


def _blocks(lesson):
    content = lesson.content
    if isinstance(content, str):
        try:
            return json.loads(content)
        except (ValueError, TypeError):
            return []
    return content or []


def lesson_source(lesson):
    """Весь текст и код урока одной строкой (для анализа)."""
    parts = []
    for block in _blocks(lesson):
        if isinstance(block, dict):
            for key in ('content',):
                value = block.get(key)
                if isinstance(value, str):
                    parts.append(value)
            for key in ('items',):
                value = block.get(key)
                if isinstance(value, list):
                    parts.extend(str(x) for x in value)
            rows = block.get('rows')
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, list):
                        parts.extend(str(x) for x in row)
    if lesson.starter_code:
        parts.append(lesson.starter_code)
    return '\n'.join(parts)


# Конструкции, которые язык требует всегда (обёртка программы),
# но которым не нужно отдельно учить ради задач.
ALWAYS_AVAILABLE = {'class', 'return', 'def'}


def detect_skills(source, include_basic=True):
    """Навыки, которые встречаются в коде/тексте."""
    found = set()
    text = source or ''
    # код в блоках важнее текста; текст иногда упоминает слова, поэтому
    # анализируем только фрагменты, похожие на код
    for skill, pattern in SKILL_PATTERNS.items():
        if pattern.search(text):
            found.add(skill)
    found -= ALWAYS_AVAILABLE
    if not include_basic:
        found -= BASIC_SKILLS
    return found


def code_blocks_source(lesson):
    """Только код урока (без прозаического текста)."""
    return '\n'.join(
        b.get('content', '') for b in _blocks(lesson)
        if isinstance(b, dict) and b.get('type') == 'code'
    )


def lesson_skills(lesson):
    """Навыки, которые урок действительно показывает в примерах кода."""
    src = code_blocks_source(lesson)
    if lesson.starter_code:
        src += '\n' + lesson.starter_code
    skills = detect_skills(src)
    # «print» и «переменные» из текста тоже считаем пройденными,
    # если урок их объясняет словами
    prose = lesson_source(lesson).lower()
    if 'print' in prose:
        skills.add('print')
    return skills


def task_skills(task):
    """Навыки, необходимые для решения задачи (по эталонному решению)."""
    source = task.solution or task.starter_code or ''
    skills = detect_skills(source)
    # Тесты могут требовать ввода, даже если в решении иное
    if task.test_cases:
        skills.add('input')
    return skills


def cumulative_skills_for_topic(topic, upto_lesson=None):
    """Накопленные навыки по урокам темы в порядке ``order``."""
    from learning.models import Lesson

    lessons = Lesson.objects.filter(topic=topic, status='published').order_by('order', 'id')
    accumulated = set()
    for lesson in lessons:
        accumulated |= lesson_skills(lesson)
        if upto_lesson is not None and lesson.id == upto_lesson.id:
            break
    return accumulated


def filter_tasks_for_lesson(lesson, tasks):
    """Возвращает (разрешённые, отклонённые_с_причинами)."""
    allowed_skills = cumulative_skills_for_topic(lesson.topic, upto_lesson=lesson)
    allowed, rejected = [], []
    for task in tasks:
        needed = task_skills(task)
        missing = needed - allowed_skills
        # «input» требует умения читать ввод — он должен быть пройден
        if missing:
            rejected.append((task, sorted(missing)))
        else:
            allowed.append(task)
    return allowed, rejected
