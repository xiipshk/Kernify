"""Create the DeepSeek provider and make it the default one."""
from django.db import migrations


def create_deepseek_provider(apps, schema_editor):
    AIProvider = apps.get_model('ai', 'AIProvider')
    db_alias = schema_editor.connection.alias
    manager = AIProvider.objects.using(db_alias)

    if manager.filter(slug='deepseek').exists():
        return

    manager.filter(is_default=True).update(is_default=False)

    manager.create(
        name='DeepSeek',
        slug='deepseek',
        provider_type='deepseek',
        api_key='',  # resolved from DEEPSEEK_API_KEY in settings
        base_url='https://api.deepseek.com',
        default_model='deepseek-chat',
        default_temperature=0.7,
        default_max_tokens=4096,
        supports_streaming=True,
        supports_functions=False,
        supports_vision=False,
        is_active=True,
        is_default=True,
        priority=10,
    )


def remove_deepseek_provider(apps, schema_editor):
    AIProvider = apps.get_model('ai', 'AIProvider')
    db_alias = schema_editor.connection.alias
    AIProvider.objects.using(db_alias).filter(slug='deepseek').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0003_alter_aiprovider_provider_type'),
    ]

    operations = [
        migrations.RunPython(create_deepseek_provider, remove_deepseek_provider),
    ]
