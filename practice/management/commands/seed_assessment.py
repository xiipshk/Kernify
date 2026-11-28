"""Наполнение банка вопросов теста-диагностики."""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from learning.models import ProgrammingLanguage, Topic
from practice.assessment_bank import seed_questions
from practice.models import AssessmentQuestion


def resolve_topic(language, label):
    """
    Находит тему курса по названию внутри языка.

    Если название встречается в нескольких программах, берём тему из
    программы с меньшим ``order`` (обычно это базовый курс).
    """
    return (
        Topic.objects.filter(
            program__language=language,
            name=label,
            status=Topic.PublishStatus.PUBLISHED,
        )
        .select_related('program')
        .order_by('program__order', 'order')
        .first()
    )


class Command(BaseCommand):
    help = 'Заполняет вопросы теста-диагностики для всех языков'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Удалить существующие вопросы перед заполнением',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options['reset']
        languages = {lang.slug: lang for lang in ProgrammingLanguage.all_objects.all()}

        created = 0
        updated = 0
        skipped = 0
        for item in seed_questions():
            language = languages.get(item['language_slug'])
            if language is None:
                self.stdout.write(self.style.WARNING(
                    f"Язык {item['language_slug']} не найден — пропускаем"
                ))
                continue

            topic = resolve_topic(language, item['topic_label'])
            existing = AssessmentQuestion.all_objects.filter(
                language=language, order=item['order']
            ).first()

            if existing and reset:
                # У моделей мягкое удаление: instance.delete() лишь помечает
                # запись, а уникальный ключ (language, order) остаётся занятым.
                AssessmentQuestion.all_objects.filter(pk=existing.pk).delete()
                existing = None

            if existing:
                # Досвязываем тему, если её не было (например, после обновления банка)
                if existing.topic_id is None and topic is not None:
                    existing.topic = topic
                    existing.topic_label = item['topic_label']
                    existing.save(update_fields=['topic', 'topic_label'])
                    updated += 1
                else:
                    skipped += 1
                continue

            AssessmentQuestion.all_objects.create(
                language=language,
                topic=topic,
                topic_label=item['topic_label'],
                question=item['question'],
                options=item['options'],
                explanation=item['explanation'],
                difficulty=item['difficulty'],
                order=item['order'],
                status=AssessmentQuestion.PublishStatus.PUBLISHED,
                published_at=timezone.now(),
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Создано: {created}, привязано к темам: {updated}, без изменений: {skipped}'
        ))
