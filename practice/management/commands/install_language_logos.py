"""
Установка настоящих логотипов языков из папки ``logo/``.

Источник на каждый язык:

    python      logo/питон.webp        (официальный логотип)
    cpp         logo/C.webp            (официальный C++)
    javascript  logo/JavaScript.png    (официальный JS)
    rust        logo/Rust.webp         (шестерёнка Rust)
    css         logo/CSS.webp          (официальный CSS3)
    csharp      logo/C.png             (C#)

Файлы приводятся к квадрату 512×512 (с прозрачными полями), чтобы логотипы
одинаково смотрелись в иконках разных размеров.

Запуск:
    python manage.py install_language_logos
"""

import io
import os

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image

from learning.models import ProgrammingLanguage

LOGOS = {
    'python': 'питон.webp',
    'cpp': 'C.webp',
    'javascript': 'JavaScript.png',
    'rust': 'Rust.webp',
    'css': 'CSS.webp',
    'csharp': 'C.png',
}

CANVAS = 512

# Монохромные логотипы — на тёмной теме показываем белыми.
MONOCHROME = {'rust'}


def prepare(source_path):
    """Квадрат 512×512 с прозрачными полями; содержимое вписано по краям."""
    image = Image.open(source_path).convert('RGBA')
    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)

    side = max(image.width, image.height)
    canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    canvas.paste(image, ((side - image.width) // 2, (side - image.height) // 2))
    canvas = canvas.resize((CANVAS, CANVAS), Image.LANCZOS)

    buffer = io.BytesIO()
    canvas.save(buffer, format='PNG', optimize=True)
    return buffer.getvalue()


class Command(BaseCommand):
    help = 'Устанавливает настоящие логотипы языков из папки logo/'

    def add_arguments(self, parser):
        parser.add_argument('--logo-dir', default='logo', help='Папка с логотипами')

    def handle(self, *args, **options):
        logo_dir = options['logo_dir']
        for slug, filename in LOGOS.items():
            source = os.path.join(logo_dir, filename)
            language = ProgrammingLanguage.all_objects.filter(slug=slug).first()
            if language is None:
                self.stdout.write(self.style.WARNING(f'Язык {slug} не найден — пропускаем'))
                continue
            if not os.path.exists(source):
                self.stdout.write(self.style.WARNING(f'Нет файла {source} — пропускаем'))
                continue

            data = prepare(source)
            if language.logo:
                language.logo.delete(save=False)
            language.logo.save(f'{slug}.png', ContentFile(data), save=True)
            language.logo_invert_on_dark = slug in MONOCHROME
            language.save(update_fields=['logo_invert_on_dark'])
            self.stdout.write(self.style.SUCCESS(f'{language.name}: {filename} → {language.logo.name}'))

        self.stdout.write(self.style.SUCCESS('Логотипы языков обновлены'))