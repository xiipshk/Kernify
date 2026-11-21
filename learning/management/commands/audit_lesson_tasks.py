"""
Аудит задач к урокам: задачи не должны требовать того, что ещё не пройдено.

    python manage.py audit_lesson_tasks            # сводка по всем урокам
    python manage.py audit_lesson_tasks --topic python-1-1
    python manage.py audit_lesson_tasks --lesson 1-1-vvedenie-v-python --verbose
"""
from django.core.management.base import BaseCommand

from learning.models import Lesson
from practice.lesson_tasks import lesson_tasks_report
from practice.models import PracticeTask


class Command(BaseCommand):
    help = 'Проверяет, что задачи урока используют только пройденный материал.'

    def add_arguments(self, parser):
        parser.add_argument('--lesson', type=str, default='', help='slug урока')
        parser.add_argument('--topic', type=str, default='', help='slug темы')
        parser.add_argument('--verbose', action='store_true', help='Показать подробности по каждой задаче')

    def handle(self, *args, **options):
        lessons = Lesson.objects.filter(status='published').select_related('topic')
        if options['lesson']:
            lessons = lessons.filter(slug=options['lesson'])
        if options['topic']:
            lessons = lessons.filter(topic__slug=options['topic'])

        total_tasks = 0
        total_bad = 0
        lessons_with_bad = 0
        missing_counter = {}

        for lesson in lessons.order_by('topic__slug', 'order', 'id'):
            allowed, rejected = lesson_tasks_report(lesson, limit=0)
            total_tasks += len(allowed) + len(rejected)
            if rejected:
                total_bad += len(rejected)
                lessons_with_bad += 1

            if options['verbose'] or rejected:
                self.stdout.write('')
                self.stdout.write(self.style.MIGRATE_HEADING(
                    f'{lesson.topic.slug} / {lesson.name}  —  ok: {len(allowed)}, требует не пройденного: {len(rejected)}'
                ))
                for task, missing in rejected:
                    for skill in missing:
                        missing_counter[skill] = missing_counter.get(skill, 0) + 1
                    if options['verbose']:
                        self.stdout.write(f'   ✗ {task.name}: не хватает {", ".join(missing)}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Проверено задач: {total_tasks}. Нарушений: {total_bad}. Уроков с нарушениями: {lessons_with_bad}.'
        ))
        if missing_counter:
            top = sorted(missing_counter.items(), key=lambda x: -x[1])[:10]
            self.stdout.write('Чаще всего не хватает навыков: ' + ', '.join(f'{k} ({v})' for k, v in top))
