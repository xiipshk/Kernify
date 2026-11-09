"""Remove SubTopic model and flatten Lesson.subtopic → Lesson.topic."""

import django.db.models.deletion
from django.db import migrations, models


def copy_subtopic_to_topic(apps, schema_editor):
    """Map each lesson to its subtopic's topic before dropping subtopic.
    Reassigns unique order values within each topic since the flattening
    merges lessons from multiple subtopics into one topic."""
    Lesson = apps.get_model('learning', 'Lesson')
    from django.db.models import F

    # Group lessons by topic and assign sequential unique orders
    lessons_by_topic = {}
    for lesson in Lesson.objects.all().order_by('subtopic_id', 'order', 'id'):
        topic_id = lesson.subtopic.topic_id if lesson.subtopic_id else None
        if topic_id is None:
            continue
        lessons_by_topic.setdefault(topic_id, []).append(lesson)

    for topic_id, lessons in lessons_by_topic.items():
        for new_order, lesson in enumerate(lessons, start=1):
            lesson.topic_id = topic_id
            lesson.order = new_order
            lesson.save(update_fields=['topic_id', 'order'])


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0002_lesson_difficulty_lesson_hints_lesson_lesson_type_and_more'),
    ]

    operations = [
        # 1. Add topic FK as nullable (to be filled by data migration)
        migrations.AddField(
            model_name='lesson',
            name='topic',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='lessons',
                to='learning.topic',
                verbose_name='topic',
            ),
        ),
        # 2. Remove subtopics_count from Topic
        migrations.RemoveField(
            model_name='topic',
            name='subtopics_count',
        ),
        # 3. Remove old subtopic-based constraints from Lesson
        #    (must happen before data migration so we can freely reassign order)
        migrations.RemoveConstraint(
            model_name='lesson',
            name='unique_lesson_slug_per_subtopic',
        ),
        migrations.RemoveConstraint(
            model_name='lesson',
            name='unique_lesson_order_per_subtopic',
        ),
        # 4. Data migration: copy subtopic.topic_id → topic_id
        migrations.RunPython(copy_subtopic_to_topic),
        # 5. Remove subtopic FK from Lesson
        migrations.RemoveField(
            model_name='lesson',
            name='subtopic',
        ),
        # 6. Make topic non-nullable
        migrations.AlterField(
            model_name='lesson',
            name='topic',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='lessons',
                to='learning.topic',
                verbose_name='topic',
            ),
        ),
        # 7. Add new topic-based constraints
        migrations.AddConstraint(
            model_name='lesson',
            constraint=models.UniqueConstraint(
                fields=('topic', 'slug'),
                name='unique_lesson_slug_per_topic',
            ),
        ),
        migrations.AddConstraint(
            model_name='lesson',
            constraint=models.UniqueConstraint(
                fields=('topic', 'order'),
                name='unique_lesson_order_per_topic',
            ),
        ),
        # 8. Update Lesson model ordering
        migrations.AlterModelOptions(
            name='lesson',
            options={
                'ordering': ['topic', 'order', 'name'],
                'verbose_name': 'lesson',
                'verbose_name_plural': 'lessons',
            },
        ),
        # 9. Delete SubTopic model
        migrations.DeleteModel(
            name='SubTopic',
        ),
    ]
