"""
Выбор ежедневного вызова (задачи дня).

Примеры:
    python manage.py set_daily_challenge                 # задача на сегодня
    python manage.py set_daily_challenge --days 7        # на неделю вперёд
    python manage.py set_daily_challenge --force         # перевыбрать сегодняшнюю
    python manage.py set_daily_challenge --language python
    python manage.py set_daily_challenge --date 2026-12-01
"""
import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from practice.models import DailyChallenge
from practice.services import pick_daily_task


class Command(BaseCommand):
    help = 'Выбирает случайную задачу как ежедневный вызов на дату (по умолчанию — сегодня).'

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str, default='', help='Дата в формате YYYY-MM-DD (по умолчанию сегодня)')
        parser.add_argument('--days', type=int, default=1, help='Сколько дней заполнить вперёд (по умолчанию 1)')
        parser.add_argument('--force', action='store_true', help='Перевыбрать задачу, даже если на дату уже есть')
        parser.add_argument('--language', type=str, default='', help='Только задачи указанного языка (slug)')
        parser.add_argument('--dry-run', action='store_true', help='Показать выбор без сохранения')

    def handle(self, *args, **options):
        if options['date']:
            try:
                start = datetime.date.fromisoformat(options['date'])
            except ValueError:
                self.stderr.write(self.style.ERROR('Неверная дата. Формат: YYYY-MM-DD'))
                return
        else:
            start = timezone.localdate()

        days = max(1, options['days'])
        language = options['language'].strip() or None
        force = options['force']
        dry_run = options['dry_run']

        for offset in range(days):
            day = start + datetime.timedelta(days=offset)
            existing = DailyChallenge.objects.filter(date=day).select_related('task').first()

            if existing and not force:
                self.stdout.write(f'{day}: уже выбрана «{existing.task.name}» (пропуск)')
                continue

            task = pick_daily_task(day, language=language)
            if not task:
                self.stderr.write(self.style.WARNING(f'{day}: нет подходящих задач'))
                continue

            if dry_run:
                self.stdout.write(self.style.WARNING(f'{day}: (dry-run) выбрали бы «{task.name}»'))
                continue

            if existing and force:
                existing.task = task
                existing.save(update_fields=['task', 'updated_at'])
                self.stdout.write(self.style.SUCCESS(f'{day}: заменена на «{task.name}»'))
            else:
                DailyChallenge.objects.create(date=day, task=task)
                self.stdout.write(self.style.SUCCESS(f'{day}: выбрана «{task.name}»'))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY-RUN: ничего не сохранено.'))
