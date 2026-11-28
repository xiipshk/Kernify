"""
Регрессионные проверки читаемости: в CSS не должно быть правил,
которые гарантированно дают нечитаемый текст.

Проверяем два класса ошибок, которые уже случались:
  1) «black ... in dark mode» — принудительно чёрный текст в тёмной теме;
  2) белый текст без явной тёмной поверхности (bg-theme-dark / bg-dark).
"""
import re
from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase

CSS_PATH = Path(settings.BASE_DIR) / 'static' / 'css' / 'style.css'

# Цвета, которые на светлом фоне дают контраст < 2 (практически невидимы)
VERY_LIGHT = re.compile(r'#(?:fff(?:fff)?|f8fafc|f5f5f5|fafafa)\b', re.IGNORECASE)
VERY_DARK = re.compile(r'#(?:000(?:000)?|0a0f1a|131b2a)\b', re.IGNORECASE)


class CssContrastRulesTests(SimpleTestCase):
    def setUp(self):
        self.css = CSS_PATH.read_text(encoding='utf-8')

    def test_no_forced_black_text_in_dark_theme(self):
        """В .theme-dark правилах не должно быть чёрного текста без светлого фона."""
        offenders = []
        for match in re.finditer(r'([^{}]*)\{([^}]*)\}', self.css):
            selector, body = match.group(1), match.group(2)
            # учитываем селектор без комментариев
            clean_selector = re.sub(r'/\*.*?\*/', '', selector, flags=re.S).strip()
            if not clean_selector.startswith(('.theme-dark', '.theme-auto')):
                continue
            # только объявления текстового цвета (не background-color)
            decls = [d.strip() for d in body.split(';')]
            color_decls = [d for d in decls if re.match(r'^color\s*:', d)]
            if not color_decls:
                continue
            value = color_decls[0].split(':', 1)[1].strip()
            if not VERY_DARK.search(value):
                continue
            # допустимо, если правило само задаёт светлый фон (тёмный текст на светлом)
            if re.search(r'background(?:-color)?:\s*(?:#(?:f|e|fff)\w*|white|var\(--bs-light)', body, re.IGNORECASE):
                continue
            # элементы Bootstrap с собственным светлым фоном (alert-*, btn-*, badge-*)
            # задают фон отдельным компонентным правилом Bootstrap, а не этим блоком
            BOOTSTRAP_LIGHT_BG = ('alert-', 'btn-', 'badge-', 'text-bg-')
            if any(token in clean_selector for token in BOOTSTRAP_LIGHT_BG):
                continue
            # светлый фон задаётся отдельным правилом с тем же селектором ниже (например, активная вкладка)
            selector_parts = [x.strip() for x in clean_selector.split(',') if x.strip()]
            if selector_parts and any(
                re.search(re.escape(part) + r'\s*\{[^}]*background-color:\s*#f', self.css)
                for part in selector_parts
            ):
                continue
            offenders.append(f'{clean_selector[:70]} -> {value}')
        self.assertEqual(offenders, [], 'Чёрный текст в тёмной теме на тёмном фоне: '
                                        + '; '.join(offenders[:5]))

    def test_white_text_has_dark_surface(self):
        """color: #fff/#ffffff не должен задаваться внутри светлой темы без тёмного фона."""
        offenders = []
        for match in re.finditer(r'([^{}]*)\{([^}]*)\}', self.css):
            selector, body = match.group(1), match.group(2)
            if 'theme-light' not in selector:
                continue
            if 'bg-theme-dark' in selector or 'sidebar' in selector or 'bg-dark' in selector:
                continue
            decls = [d.strip() for d in body.split(';')]
            color_decls = [d for d in decls if re.match(r'^color\s*:', d)]
            for decl in color_decls:
                value = decl.split(':', 1)[1].strip()
                if VERY_LIGHT.match(value) and not any(d.startswith('background') for d in decls):
                    offenders.append(f'{selector.strip()[:80]} -> {value}')
        self.assertEqual(offenders, [], 'Белый текст без тёмного фона в светлой теме: '
                                        + '; '.join(offenders[:5]))

    def test_theme_variables_defined(self):
        """В обеих темах определены базовые переменные текста и фона."""
        for theme in ('theme-light', 'theme-dark'):
            for var in ('--text-primary', '--bg-primary', '--card-bg'):
                self.assertIn(f'{var}:', self.css, f'{theme}: не задана {var}')

    def test_badge_colors_do_not_use_translated_slugify(self):
        """Бейджи не должны получать класс bg- из переведённой метки (даёт пустой bg-)."""
        templates_dir = Path(settings.BASE_DIR) / 'templates'
        offenders = []
        for path in templates_dir.rglob('*.html'):
            text = path.read_text(encoding='utf-8')
            if re.search(r'bg-\{\{[^}]*get_\w+_display\|lower\|slugify', text):
                offenders.append(str(path.relative_to(templates_dir)))
        self.assertEqual(offenders, [], 'Шаблоны с bg-{{ ...|slugify }} (пустой класс): '
                                        + ', '.join(offenders))


class DifficultyStarsTests(SimpleTestCase):
    """Свойства сложности звёздами у уроков/тем/программ."""

    def test_lesson_levels_map_to_stars(self):
        from learning.models import Lesson

        expected = {
            'beginner': (1, '★☆☆☆☆'),
            'intermediate': (3, '★★★☆☆'),
            'advanced': (4, '★★★★☆'),
            'expert': (5, '★★★★★'),
        }
        for value, (level, stars) in expected.items():
            lesson = Lesson(difficulty=value)
            self.assertEqual(lesson.difficulty_level, level)
            self.assertEqual(lesson.difficulty_stars, stars)
            self.assertEqual(len(lesson.difficulty_stars_filled), level)
            self.assertEqual(len(lesson.difficulty_stars_empty), 5 - level)

    def test_topic_and_program_stars(self):
        from learning.models import CourseProgram, Topic

        self.assertEqual(Topic(difficulty='easy').difficulty_stars, '★☆☆☆☆')
        self.assertEqual(Topic(difficulty='hard').difficulty_stars, '★★★★☆')
        self.assertEqual(CourseProgram(target_level='advanced').difficulty_stars, '★★★★☆')

    def test_unknown_value_defaults_to_one_star(self):
        from learning.models import Lesson

        self.assertEqual(Lesson(difficulty=None).difficulty_level, 1)

    def test_stars_css_defines_bright_colors(self):
        """Звёзды уроков должны иметь явные (яркие) цвета в обеих темах."""
        css = CSS_PATH.read_text(encoding='utf-8')
        self.assertIn('.lesson-difficulty-stars .stars-filled', css)
        self.assertIn('.theme-dark .lesson-difficulty-stars .stars-filled', css)
        self.assertRegex(css, r'\.lesson-difficulty-stars\s+\.stars-filled\s*\{[^}]*color:\s*#ff')


class LanguageLogoContrastTests(SimpleTestCase):
    """Монохромные логотипы (Rust) не должны сливаться с тёмным фоном."""

    def setUp(self):
        self.css = CSS_PATH.read_text(encoding='utf-8')

    def test_monochrome_logo_inverted_on_dark_theme(self):
        self.assertRegex(
            self.css,
            r'\.theme-dark\s+\.language-logo--invert\s*\{[^}]*filter:\s*brightness\(0\)\s+invert\(1\)',
        )

    def test_monochrome_logo_inverted_for_auto_dark(self):
        self.assertRegex(
            self.css,
            r'prefers-color-scheme:\s*dark[\s\S]*?\.theme-auto\s+\.language-logo--invert\s*\{[^}]*filter:\s*brightness\(0\)\s+invert\(1\)',
        )


class LanguageLogoRenderTests(TestCase):
    """Иконка языка добавляет класс инверсии только для монохромных логотипов."""

    def test_rust_logo_is_marked_monochrome(self):
        from learning.models import ProgrammingLanguage

        language = ProgrammingLanguage.objects.create(
            name='Rust', slug='rust', icon='🦀', order=1,
            logo='languages/rust.png', logo_invert_on_dark=True,
            status=ProgrammingLanguage.PublishStatus.PUBLISHED,
        )
        html = render_to_string('includes/language_icon.html', {'language': language})
        self.assertIn('language-logo--invert', html)

    def test_colored_logo_is_not_inverted(self):
        from learning.models import ProgrammingLanguage

        language = ProgrammingLanguage.objects.create(
            name='Python', slug='python', order=2,
            logo='languages/python.png', logo_invert_on_dark=False,
            status=ProgrammingLanguage.PublishStatus.PUBLISHED,
        )
        html = render_to_string('includes/language_icon.html', {'language': language})
        self.assertIn('language-logo', html)
        self.assertNotIn('language-logo--invert', html)
