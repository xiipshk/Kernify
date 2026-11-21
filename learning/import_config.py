"""
Shared configuration for lesson import and alignment scripts.
"""
from learning.models import CourseProgram

# Lesson order range -> (target_level, level_display_name)
LEVEL_RANGES = [
    (1, 11, CourseProgram.TargetLevel.BEGINNER, 'Новичок'),
    (12, 22, CourseProgram.TargetLevel.INTERMEDIATE, 'Средний уровень'),
    (23, 33, CourseProgram.TargetLevel.ADVANCED, 'Углубленный уровень'),
]

LEVEL_PROGRAM_ORDER = {
    CourseProgram.TargetLevel.BEGINNER: 1,
    CourseProgram.TargetLevel.INTERMEDIATE: 2,
    CourseProgram.TargetLevel.ADVANCED: 3,
}

# Per-language metadata
LANGUAGE_META = {
    'python': {'name': 'Python', 'icon': '🐍', 'color': '#3776AB', 'order': 1},
    'cpp': {'name': 'C++', 'icon': '⚡', 'color': '#00599C', 'order': 2},
    'javascript': {'name': 'JavaScript', 'icon': '🟨', 'color': '#F7DF1E', 'order': 3},
    'rust': {'name': 'Rust', 'icon': '🦀', 'color': '#000000', 'order': 4},
    'css': {'name': 'CSS', 'icon': '🎨', 'color': '#1572B6', 'order': 5},
    'csharp': {'name': 'C#', 'icon': '🔷', 'color': '#68217A', 'order': 6},
}

# Language mapping: lang_slug -> reference file name
LANG_FILES = {
    'csharp': 'CSharp.md',
    'cpp': 'C++.md',
    'python': 'Python.md',
    'javascript': 'JavaScript.md',
    'css': 'CSS.md',
    'rust': 'Rust.md',
}

LEVEL_ORDER = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
LEVEL_NAME_RU = {
    'beginner': 'Новичок',
    'intermediate': 'Средний уровень',
    'advanced': 'Углубленный уровень',
}

# Number of topics per level per language (from reference files)
TOPIC_COUNTS = {
    'csharp': {'beginner': 11, 'intermediate': 11, 'advanced': 11},
    'cpp': {'beginner': 11, 'intermediate': 11, 'advanced': 11},
    'python': {'beginner': 11, 'intermediate': 11, 'advanced': 11},
    'javascript': {'beginner': 10, 'intermediate': 11, 'advanced': 11},
    'css': {'beginner': 10, 'intermediate': 11, 'advanced': 11},
    'rust': {'beginner': 11, 'intermediate': 11, 'advanced': 11},
}

# Lesson order -> topic order mapping per language/level
LESSON_ORDER_MAP = {
    'csharp': {
        'beginner': list(range(1, 12)),
        'intermediate': list(range(12, 23)),
        'advanced': list(range(23, 34)),
    },
    'cpp': {
        'beginner': list(range(1, 12)),
        'intermediate': list(range(12, 23)),
        'advanced': list(range(23, 34)),
    },
    'python': {
        'beginner': list(range(1, 12)),
        'intermediate': list(range(12, 23)),
        'advanced': list(range(23, 34)),
    },
    'rust': {
        'beginner': list(range(1, 12)),
        'intermediate': list(range(12, 23)),
        'advanced': list(range(23, 34)),
    },
    'javascript': {
        'beginner': list(range(1, 11)),
        'intermediate': list(range(11, 22)),
        'advanced': list(range(25, 33)),
    },
    'css': {
        'beginner': list(range(1, 11)),
        'intermediate': list(range(11, 22)),
        'advanced': list(range(22, 33)),
    },
}