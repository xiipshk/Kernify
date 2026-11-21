import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from learning.models import ProgrammingLanguage
with open('langs_output.txt', 'w', encoding='utf-8') as f:
    for lang in ProgrammingLanguage.objects.all():
        logo = str(lang.logo) if lang.logo else 'None'
        icon = str(lang.icon) if lang.icon else 'None'
        f.write(f'{lang.slug}: {lang.name}, icon={icon}, logo={logo}\n')
print('Done')