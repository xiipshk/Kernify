"""Tests for the lesson editor, rich-text rendering and URL slugs."""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from learning.models import CourseProgram, Lesson, LessonVersion, ProgrammingLanguage, Topic
from learning.templatetags.language_filters import rich_text
from learning.utils import make_url_slug


class UrlSlugTests(TestCase):
    def test_technical_characters_become_safe(self):
        self.assertEqual(make_url_slug('urok-01-введение-в-c#-и-net'), 'urok-01-введение-в-c-sharp-и-net')
        self.assertEqual(make_url_slug('urok-09-concepts-c++20'), 'urok-09-concepts-c-plus-plus20')
        self.assertEqual(make_url_slug('result,-option,-?'), 'result-option')

    def test_fallback(self):
        self.assertEqual(make_url_slug(''), 'lesson')
        self.assertEqual(make_url_slug('///', fallback='topic'), 'topic')


class RichTextTests(TestCase):
    def test_paragraphs_and_inline_markdown(self):
        html = rich_text('Первый **абзац** с `кодом`.\n\nВторой [абзац](https://example.com).')
        self.assertIn('<p>Первый <strong>абзац</strong> с <code>кодом</code>.</p>', html)
        self.assertIn('<a href="https://example.com"', html)

    def test_unknown_tags_are_shown_as_text(self):
        html = rich_text("type(x)  # <class 'int'>")
        self.assertIn("&lt;class 'int'&gt;", html)
        self.assertNotIn('<class', html)


class LessonEditorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.admin = user_model.objects.create_superuser(
            username='editor',
            email='editor@example.com',
            password='secret123',
        )
        language = ProgrammingLanguage.objects.create(name='Python', slug='python', order=1)
        program = CourseProgram.objects.create(
            language=language, name='Python basics', slug='python-basics', order=1,
        )
        topic = Topic.objects.create(program=program, name='Основы', slug='osnovy', order=1)
        cls.lesson = Lesson.objects.create(
            topic=topic,
            name='Урок 1',
            slug='urok-1',
            order=1,
            content=[{'type': 'text', 'content': 'Старый текст'}],
            status=Lesson.PublishStatus.PUBLISHED,
        )

    def setUp(self):
        self.client.force_login(self.admin)
        self.editor_url = reverse('admin:learning_lesson_editor', args=[self.lesson.pk])
        self.save_url = reverse('admin:learning_lesson_editor_save', args=[self.lesson.pk])

    def test_editor_page_renders(self):
        response = self.client.get(self.editor_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'le-payload')
        self.assertContains(response, 'lesson_editor.js')

    def test_save_updates_content_and_display(self):
        payload = {
            'meta': {
                'name': 'Урок 1: обновлён',
                'short_description': 'Коротко',
                'status': 'published',
                'difficulty': 'intermediate',
                'lesson_type': 'text',
                'xp_reward': 30,
                'estimated_minutes': 25,
            },
            'content': [
                {'type': 'heading', 'level': 2, 'content': 'Заголовок'},
                {'type': 'callout', 'style': 'warning', 'title': 'Важно', 'content': 'Текст'},
                {'type': 'unknown-widget', 'foo': 'bar'},
            ],
            'display': {'font': 'serif', 'size': 19, 'line_height': 1.8, 'width': 72},
        }
        response = self.client.post(
            self.save_url,
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['ok'])

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, 'Урок 1: обновлён')
        self.assertEqual(self.lesson.xp_reward, 30)
        self.assertEqual(len(self.lesson.content), 3)
        # Unknown blocks are preserved for forward compatibility.
        self.assertEqual(self.lesson.content[2]['type'], 'unknown-widget')
        self.assertEqual(self.lesson.display_options['font'], 'serif')
        self.assertIn('font-size: 19px', self.lesson.display_style)
        self.assertTrue(LessonVersion.objects.filter(lesson=self.lesson).exists())

    def test_save_rejects_empty_name(self):
        payload = {'meta': {'name': '   '}, 'content': [], 'display': {}}
        response = self.client.post(
            self.save_url,
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['ok'])

    def test_anonymous_user_cannot_open_editor(self):
        self.client.logout()
        response = self.client.get(self.editor_url)
        self.assertEqual(response.status_code, 302)
