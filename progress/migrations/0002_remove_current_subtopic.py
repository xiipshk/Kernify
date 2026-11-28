"""Remove current_subtopic from UserProgress.

Операция сделана идемпотентной: поля current_subtopic нет в исходной схеме
(или оно уже удалено), поэтому `makemigrations`/`migrate` не падают.
"""

from django.db import migrations


def remove_current_subtopic(apps, schema_editor):
    UserProgress = apps.get_model('progress', 'UserProgress')
    if any(field.name == 'current_subtopic' for field in UserProgress._meta.get_fields()):
        schema_editor.remove_field(
            UserProgress._meta.get_field('current_subtopic')
        )


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0001_initial'),
        ('learning', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_current_subtopic, migrations.RunPython.noop),
    ]
