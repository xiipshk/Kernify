"""Remove current_subtopic from UserProgress."""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0001_initial'),
        ('learning', '0003_remove_subtopic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprogress',
            name='current_subtopic',
        ),
    ]
