# -*- coding: utf-8 -*-
"""Заполняет *_en поля в БД из уже переведённых фикстур."""

from __future__ import annotations

import json
import os
import re

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from learning.models import Lesson, Topic, CourseProgram, ProgrammingLanguage

FIXTURES = 'fixtures/lessons'

def main():
    # Загружаем все переведённые фикстуры
    lessons_by_slug = {}
    for lang_dir in os.listdir(FIXTURES):
        lang_path = os.path.join(FIXTURES, lang_dir)
        if not os.path.isdir(lang_path):
            continue
        for fname in sorted(os.listdir(lang_path)):
            if not fname.endswith('.json'):
                continue
            with open(os.path.join(lang_path, fname), encoding='utf-8') as f:
                data = json.load(f)
            slug = data.get('slug')
            if slug:
                lessons_by_slug[slug] = data

    print(f'Загружено уроков из фикстур: {len(lessons_by_slug)}')

    # Обновляем уроки
    updated = 0
    for lesson in Lesson.objects.select_related('topic__program__language'):
        data = lessons_by_slug.get(lesson.slug)
        if not data:
            # Пробуем через title
            for slug, d in lessons_by_slug.items():
                if d.get('title') == lesson.name:
                    data = d
                    break
        if not data:
            continue
        if data.get('title') and data['title'] != lesson.name_en:
            lesson.name_en = data['title']
            updated += 1
        if data.get('short_description') and data['short_description'] != lesson.short_description_en:
            lesson.short_description_en = data['short_description']
        if data.get('content_blocks') and data['content_blocks'] != lesson.content_en:
            lesson.content_en = data['content_blocks']
        lesson.save(update_fields=['name_en', 'short_description_en', 'content_en', 'updated_at'])

    print(f'Уроков обновлено: {updated}')

    # Обновляем темы
    topic_updated = 0
    for topic in Topic.objects.select_related('program__language'):
        # Собираем название темы из первого урока
        first_lesson = topic.lessons.order_by('order').first()
        if first_lesson:
            data = lessons_by_slug.get(first_lesson.slug)
            if data:
                title = data.get('title', '')
                # Извлекаем название темы
                name = title
                name = re.sub(r'^Урок\s*\d+(?:\.\d+)?\s*[:\—-]\s*', '', name, flags=re.IGNORECASE)
                name = re.sub(r'^Урок\s*\d+(?:\.\d+)?\s*', '', name, flags=re.IGNORECASE)
                if '—' in name:
                    name = name.split('—', 1)[0].strip()
                elif '-' in name:
                    name = name.split('-', 1)[0].strip()
                if name and name != topic.name_en:
                    topic.name_en = name
                    topic_updated += 1
        if topic.description and topic.description != topic.description_en:
            topic.description_en = topic.description
        topic.save(update_fields=['name_en', 'description_en', 'updated_at'])

    print(f'Тем обновлено: {topic_updated}')

    # Обновляем программы
    prog_updated = 0
    for program in CourseProgram.objects.select_related('language'):
        if program.name and program.name != program.name_en:
            program.name_en = program.name
            prog_updated += 1
        if program.description and program.description != program.description_en:
            program.description_en = program.description
        program.save(update_fields=['name_en', 'description_en', 'updated_at'])

    print(f'Программ обновлено: {prog_updated}')

    print('Done!')


if __name__ == '__main__':
    main()