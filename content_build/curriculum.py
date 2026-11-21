"""Единый учебный план Kernify.

Источник — папка ``Kernify-lesson``: по одному текстовому файлу на урок.
Каждый язык делится на три программы: начинающий, средний, продвинутый.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from django.utils.text import slugify

BASE_DIR = Path(__file__).resolve().parent.parent
LESSON_ROOT = BASE_DIR.parent / "Kernify-lesson"

LANGUAGES = [
    {
        "slug": "python",
        "source_dir": "обучение питон",
        "program_counts": [11, 11, 11],
        "titles": [
            "Введение в Python",
            "Переменные и типы данных",
            "Операторы и выражения",
            "Условные конструкции",
            "Циклы",
            "Коллекции",
            "Строки и форматирование",
            "Функции",
            "Файлы и обработка ошибок",
            "Классы и объектно-ориентированное программирование",
            "Модули и первый проект",
            "Модель объектов Python",
            "Коллекции и алгоритмы",
            "Декораторы и замыкания",
            "Генераторы и итераторы",
            "Контекстные менеджеры",
            "Типизация и статический анализ",
            "Тестирование",
            "Асинхронность",
            "Работа с данными",
            "Веб-разработка",
            "Производительность и профилирование",
            "Метаклассы и дескрипторы",
            "Расширения на C и Cython",
            "Архитектура приложений",
            "Безопасность",
            "DevOps и CI/CD",
            "Микросервисы",
            "Data Science и машинное обучение",
            "Профессиональные инструменты",
            "Безопасность и надёжность",
            "Экосистема и инструменты",
            "Изучение языка и итоговый проект",
        ],
    },
    {
        "slug": "cpp",
        "source_dir": "обучение C++",
        "program_counts": [11, 11, 11],
        "titles": [
            "Введение в C++",
            "Типы и переменные",
            "Операторы",
            "Условия и циклы",
            "Функции",
            "Массивы и строки",
            "Контейнеры",
            "Указатели и ссылки",
            "Объектно-ориентированное программирование",
            "Файлы и обработка ошибок",
            "Первый проект",
            "Современный C++ и ресурсы",
            "Move semantics и перемещение",
            "Продвинутое ООП",
            "Шаблоны",
            "Стандартная библиотека STL",
            "Ошибки и исключения",
            "Сборка и CMake",
            "Тестирование",
            "Многопоточность",
            "Алгоритмы и производительность",
            "Продвинутый проект",
            "Язык и компиляция",
            "Метапрограммирование",
            "Модель объектов",
            "Семантика ресурсов",
            "Продвинутый STL",
            "Модель памяти и конкурентность",
            "Сборка и ABI",
            "Оптимизация",
            "Безопасность",
            "Архитектура крупных систем",
            "Итоговый проект",
        ],
    },
    {
        "slug": "csharp",
        "source_dir": "обучение C#",
        "program_counts": [11, 11, 11],
        "titles": [
            "Введение в C# и .NET",
            "Переменные и типы",
            "Операторы и условия",
            "Циклы",
            "Методы",
            "Массивы и строки",
            "Коллекции",
            "Классы и объекты",
            "Исключения и файлы",
            "Основы LINQ",
            "Первый проект",
            "Система типов",
            "Проектирование ООП",
            "Делегаты и события",
            "Продвинутый LINQ",
            "Коллекции и алгоритмы",
            "Async/Await",
            "Внутреннее устройство .NET",
            "Тестирование и качество",
            "Доступ к данным",
            "Разработка приложений",
            "Проект: многослойное приложение",
            "Продвинутая система типов",
            "Внутреннее устройство языка и рантайма",
            "Продвинутый C#",
            "Управление памятью",
            "Асинхронность и конкурентность",
            "Производительность",
            "Архитектура",
            "Продвинутый .NET",
            "Тестирование и надёжность",
            "Платформы и экосистема",
            "Продвинутый проект",
        ],
    },
    {
        "slug": "css",
        "source_dir": "обучение CSS",
        "program_counts": [10, 11, 11],
        "titles": [
            "Введение в CSS",
            "Селекторы и каскад",
            "Цвета и текст",
            "Блочная модель",
            "Основы раскладки",
            "Flexbox",
            "CSS Grid",
            "Фоны и эффекты",
            "Основы адаптивности",
            "Первый проект",
            "Архитектура каскада",
            "Продвинутые Flexbox и Grid",
            "Адаптивный дизайн",
            "Позиционирование и слои",
            "Визуальные эффекты",
            "Переходы и анимации",
            "Современный CSS",
            "Доступность",
            "Отладка и совместимость",
            "Архитектура CSS",
            "Проект: система компонентов",
            "Модель каскада",
            "Продвинутая раскладка",
            "Контейнерные запросы",
            "Логические селекторы",
            "Анимации и эффекты",
            "Новые возможности CSS",
            "Производительность рендеринга",
            "Дизайн-системы",
            "Доступность и интернационализация",
            "Инструменты",
            "Проект: дизайн-система",
        ],
    },
    {
        "slug": "javascript",
        "source_dir": "обучение JavaScript",
        "program_counts": [10, 11, 11],
        "titles": [
            "Введение в JavaScript",
            "Переменные и типы",
            "Операторы и условия",
            "Циклы",
            "Функции",
            "Массивы",
            "Объекты",
            "Работа с DOM",
            "Основы асинхронности",
            "Первый проект",
            "Семантика типов, приведение и равенство",
            "Область видимости, замыкания, hoisting и this",
            "Функциональный стиль: HOF, map, filter, reduce",
            "Прототипы, классы и наследование",
            "Модули и инструменты: ESM, npm, сборщики",
            "Async, Event Loop и Promises",
            "Browser API",
            "Node.js",
            "Качество кода",
            "Безопасность и производительность",
            "Проект",
            "Устройство ECMAScript и рантайма",
            "Объекты и прототипы",
            "Функции",
            "Модули и метапрограммирование",
            "Браузерная платформа",
            "Внутреннее устройство Node.js",
            "Производительность",
            "Безопасность",
            "Инженерия крупных приложений",
            "Продвинутые паттерны",
            "Итоговый проект",
        ],
    },
    {
        "slug": "rust",
        "source_dir": "обучение Rust",
        "program_counts": [11, 11, 11],
        "titles": [
            "Введение в Rust",
            "Переменные и типы",
            "Управление потоком",
            "Функции",
            "Ownership и ссылки",
            "Строки и коллекции",
            "Структуры и перечисления",
            "Обработка ошибок",
            "Модули и Cargo",
            "Трейты и дженерики",
            "Первый проект",
            "Ownership: углублённо",
            "Продвинутые типы",
            "Дженерики и трейты",
            "Итераторы и функциональный стиль",
            "Архитектура",
            "Умные указатели",
            "Тестирование",
            "Файлы, сеть и сериализация",
            "Асинхронность в Rust",
            "Конкурентность",
            "Проект",
            "Память и владение",
            "Продвинутые трейты",
            "Система типов",
            "Unsafe Rust",
            "Внутреннее устройство асинхронности",
            "Продвинутая конкурентность",
            "Макросы",
            "Системное программирование",
            "Экосистема Cargo",
            "Производительность и надёжность",
            "Итоговый проект",
        ],
    },
]

# Особые slug-и уже опубликованных уроков, чтобы не менять ссылки.
SLUG_OVERRIDES = {
    ("python", 1, 1): "1-1-vvedenie-v-python",
    ("python", 1, 2): "1-2-peremennye-i-tipy-dannyh",
}

DIFFICULTY_BY_LEVEL = {
    1: "beginner",
    2: "intermediate",
    3: "advanced",
}

TOPIC_DIFFICULTY_BY_LEVEL = {
    1: "easy",
    2: "medium",
    3: "hard",
}

MINUTES_BY_LEVEL = {
    1: 30,
    2: 35,
    3: 40,
}

XP_BY_LEVEL = {
    1: 10,
    2: 15,
    3: 20,
}


@dataclass(frozen=True)
class Slot:
    language: str
    source_path: Path
    level: int
    order: int
    title: str
    topic_name: str
    lesson_name: str
    slug: str
    difficulty: str
    topic_difficulty: str
    estimated_minutes: int
    xp_reward: int
    global_index: int


def _source_files(directory: Path) -> list[Path]:
    files = [
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}
    ]
    files.sort(key=lambda path: path.name)
    return files


def _split_by_counts(items: list[str], counts: list[int]) -> list[list[str]]:
    result: list[list[str]] = []
    offset = 0
    for count in counts:
        result.append(items[offset:offset + count])
        offset += count
    if offset != len(items):
        raise ValueError(f"Не совпадает количество уроков: {offset} != {len(items)}")
    return result


def build_slots() -> list[Slot]:
    slots: list[Slot] = []
    index = 0
    for language in LANGUAGES:
        source_dir = LESSON_ROOT / language["source_dir"]
        files = _source_files(source_dir)
        titles = language["titles"]
        if len(files) != len(titles):
            raise ValueError(
                f"{language['slug']}: файлов {len(files)}, названий {len(titles)}"
            )
        grouped_titles = _split_by_counts(titles, language["program_counts"])
        grouped_files = _split_by_counts(files, language["program_counts"])
        for level, (level_titles, level_files) in enumerate(
            zip(grouped_titles, grouped_files), start=1
        ):
            for order, (title, source_path) in enumerate(
                zip(level_titles, level_files), start=1
            ):
                slug = SLUG_OVERRIDES.get((language["slug"], level, order))
                if not slug:
                    base = slugify(title, allow_unicode=True)[:150]
                    slug = f"{language['slug']}-{level}-{order}-{base}"
                slots.append(
                    Slot(
                        language=language["slug"],
                        source_path=source_path,
                        level=level,
                        order=order,
                        title=title,
                        topic_name=title,
                        lesson_name=f"{level}.{order}. {title}",
                        slug=slug,
                        difficulty=DIFFICULTY_BY_LEVEL[level],
                        topic_difficulty=TOPIC_DIFFICULTY_BY_LEVEL[level],
                        estimated_minutes=MINUTES_BY_LEVEL[level],
                        xp_reward=XP_BY_LEVEL[level],
                        global_index=index,
                    )
                )
                index += 1
    return slots


if __name__ == "__main__":
    all_slots = build_slots()
    print(f"Всего уроков: {len(all_slots)}")
    for slot in all_slots:
        print(
            f"{slot.language:10} {slot.lesson_name:60} "
            f"{slot.source_path.name}"
        )
