"""Tests for end-of-course tests (mixed theory questions and tasks)."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from learning.models import CourseProgram, Lesson, ProgrammingLanguage, Topic
from practice.course_assessment import evaluate, latest_result, topic_marks
from practice.course_assessment_models import CourseTestQuestion, CourseTestResult


def make_course(slug='course-test', name='Course Test'):
    language, _ = ProgrammingLanguage.objects.get_or_create(
        slug='testlang', defaults={'name': 'TestLang', 'status': 'published'})
    program, _ = CourseProgram.objects.get_or_create(
        language=language,
        slug=slug,
        defaults={'name': name, 'status': 'published'},
    )
    topic, _ = Topic.objects.get_or_create(
        program=program,
        slug='course-topic',
        defaults={'name': 'Основы', 'status': 'published'},
    )
    return language, program, topic


def make_questions(program, topic):
    CourseTestQuestion.objects.create(
        program=program,
        topic=topic,
        question_type='single_choice',
        question='Что такое переменная?',
        options=[
            {'text': 'Именованная область памяти', 'correct': True},
            {'text': 'Функция', 'correct': False},
        ],
        explanation='Переменная хранит значение под именем.',
        order=1,
        status='published',
    )
    CourseTestQuestion.objects.create(
        program=program,
        topic=topic,
        question_type='multiple_choice',
        question='Выберите типы данных Python',
        options=[
            {'text': 'int', 'correct': True},
            {'text': 'str', 'correct': True},
            {'text': 'table', 'correct': False},
        ],
        order=2,
        status='published',
    )
    CourseTestQuestion.objects.create(
        program=program,
        topic=topic,
        question_type='short_answer',
        question='Сколько будет 6 * 7?',
        correct_answers=['42', 'сорок два'],
        order=3,
        status='published',
    )
    CourseTestQuestion.objects.create(
        program=program,
        topic=topic,
        question_type='code_output',
        question='Что выведет этот код?',
        code_snippet='print(2 + 2)',
        correct_answers=['4'],
        explanation='2 + 2 равно 4.',
        order=4,
        status='published',
    )


class CourseTestQuestionTests(TestCase):
    def setUp(self):
        _, self.program, self.topic = make_course()
        make_questions(self.program, self.topic)
        self.questions = list(
            CourseTestQuestion.objects.filter(program=self.program).order_by('order')
        )

    def test_single_choice_check(self):
        question = self.questions[0]
        self.assertEqual(question.check_answer('0')[0], True)
        self.assertEqual(question.check_answer('1')[0], False)

    def test_multiple_choice_check_requires_exact_set(self):
        question = self.questions[1]
        self.assertTrue(question.check_answer(['0', '1'])[0])
        self.assertFalse(question.check_answer(['0'])[0])
        self.assertFalse(question.check_answer(['0', '1', '2'])[0])

    def test_short_answer_is_case_insensitive(self):
        question = self.questions[2]
        self.assertTrue(question.check_answer(' 42 ')[0])
        self.assertTrue(question.check_answer('Сорок Два')[0])
        self.assertFalse(question.check_answer('41')[0])

    def test_code_output_keeps_line_structure(self):
        question = self.questions[3]
        self.assertTrue(question.check_answer('4\n')[0])
        self.assertFalse(question.check_answer('4 4')[0])

    def test_evaluate_builds_topic_breakdown(self):
        answers = {
            str(self.questions[0].pk): '0',
            str(self.questions[1].pk): ['0', '1'],
            str(self.questions[2].pk): '42',
            str(self.questions[3].pk): '4',
        }
        result, details = evaluate(self.program, self.questions, answers)

        self.assertEqual(result.score, 100)
        self.assertEqual(result.correct_answers, 4)
        self.assertEqual(result.total_questions, 4)
        self.assertTrue(all(item['is_correct'] for item in details))
        stats = result.topic_breakdown[str(self.topic.pk)]
        self.assertEqual(stats['correct'], 4)
        self.assertEqual(stats['total'], 4)


class CourseTestViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='course-user', email='course@test.local', password='x')
        self.client.force_login(self.user)
        _, self.program, self.topic = make_course()
        make_questions(self.program, self.topic)
        self.url = reverse('practice:course_test', kwargs={'slug': self.program.slug})

    def _post(self, payload):
        return self.client.post(self.url, payload)

    def test_page_renders_mixed_questions(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'single_choice')
        self.assertContains(response, 'multiple_choice')
        self.assertContains(response, 'short_answer')
        self.assertContains(response, 'code_output')

    def test_submit_saves_result_and_shows_breakdown(self):
        questions = list(CourseTestQuestion.objects.filter(program=self.program))
        payload = {
            f'q_{questions[0].pk}': '0',
            f'q_{questions[1].pk}': ['0', '1'],
            f'q_{questions[2].pk}': '42',
            f'q_{questions[3].pk}': '4',
        }

        response = self._post(payload)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Сильные темы')
        result = CourseTestResult.objects.get(user=self.user, program=self.program)
        self.assertEqual(result.score, 100)
        self.assertEqual(result.correct_answers, 4)
        self.assertTrue(topic_marks(self.user, self.program))

    def test_wrong_answers_are_marked_for_review(self):
        questions = list(CourseTestQuestion.objects.filter(program=self.program))
        payload = {
            f'q_{questions[0].pk}': '1',
            f'q_{questions[1].pk}': ['0'],
            f'q_{questions[2].pk}': '41',
            f'q_{questions[3].pk}': '5',
        }

        response = self._post(payload)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Темы для повторения')
        result = CourseTestResult.objects.get(user=self.user, program=self.program)
        self.assertEqual(result.score, 0)
        self.assertEqual(len(result.wrong_topics), 1)

    def test_result_detail_is_private(self):
        result = CourseTestResult.objects.create(
            user=self.user,
            program=self.program,
            total_questions=1,
            correct_answers=1,
            score=100,
            answers=[],
        )
        detail_url = reverse(
            'practice:course_test_result',
            kwargs={'slug': self.program.slug, 'pk': result.pk},
        )
        self.assertEqual(self.client.get(detail_url).status_code, 200)

        other = get_user_model().objects.create_user(
            username='other-course', email='other-course@test.local', password='x')
        self.client.force_login(other)
        self.assertEqual(self.client.get(detail_url).status_code, 404)

    def test_no_questions_page(self):
        _, empty_program, _ = make_course(slug='empty-course', name='Empty')
        response = self.client.get(
            reverse('practice:course_test', kwargs={'slug': empty_program.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'пока не готов')

    def test_program_detail_shows_course_test(self):
        response = self.client.get(
            reverse('core:program_detail', kwargs={'slug': self.program.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/course-test/')
        self.assertTrue(response.context['course_test_available'])

    @patch('learning.views.LessonCompletionService.get_next_lesson', return_value=None)
    @patch('learning.views.LessonCompletionService.complete_lesson')
    def test_finishing_course_redirects_to_test(self, mocked_complete, mocked_next):
        lesson = Lesson.objects.create(
            topic=self.topic,
            name='Последний урок',
            slug='last-lesson',
            status='published',
            order=1,
        )

        response = self.client.post(
            reverse('learning:lesson_next', kwargs={'slug': lesson.slug}))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/course-test/', response.url)
