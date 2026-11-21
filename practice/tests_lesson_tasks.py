"""Тесты: задачи к уроку используют только пройденный материал."""
from django.test import TestCase

from learning.models import CourseProgram, Lesson, ProgrammingLanguage, Topic
from learning.skill_policy import detect_skills, lesson_skills, task_skills
from practice.lesson_tasks import lesson_tasks_for, skills_before_lesson
from practice.models import PracticeTask


class SkillDetectionTests(TestCase):
    def test_detect_basic_skills(self):
        code = 'a = int(input())\nprint(a + 1)\n'
        skills = detect_skills(code)
        self.assertIn('input', skills)
        self.assertIn('int', skills)
        self.assertIn('print', skills)
        self.assertIn('variables', skills)
        self.assertIn('arithmetic', skills)

    def test_detect_loops_and_conditions(self):
        code = 'for i in range(3):\n    if i > 1:\n        print(i)\n'
        skills = detect_skills(code)
        self.assertIn('for', skills)
        self.assertIn('range', skills)
        self.assertIn('if', skills)

    def test_plain_print_has_no_input(self):
        skills = detect_skills('print("hello")\n')
        self.assertIn('print', skills)
        self.assertNotIn('input', skills)


class LessonTaskPolicyTests(TestCase):
    def setUp(self):
        self.lang = ProgrammingLanguage.objects.create(name='Py', slug='pytest-lang', status='published')
        self.program = CourseProgram.objects.create(
            language=self.lang, name='P', slug='pytest-prog', status='published')
        self.topic = Topic.objects.create(
            program=self.program, name='T1', slug='pytest-topic-1', status='published', order=1)
        self.lesson1 = Lesson.objects.create(
            topic=self.topic, name='L1', slug='pytest-l1', status='published', order=1,
            lesson_type='text',
            content=[{'type': 'code', 'content': 'print(2 + 2)'}],
        )
        self.topic2 = Topic.objects.create(
            program=self.program, name='T2', slug='pytest-topic-2', status='published', order=2)
        self.lesson2 = Lesson.objects.create(
            topic=self.topic2, name='L2', slug='pytest-l2', status='published', order=1,
            lesson_type='text',
            content=[{'type': 'code', 'content': 'a = int(input())\nprint(a)'}],
        )

        # задача, решаемая первым уроком (без ввода)
        self.easy = PracticeTask.objects.create(
            topic=self.topic, language=self.lang, name='Печать', slug='pyt-easy',
            description='d', status='published', difficulty=1,
            solution='print(2 + 2)\n', test_cases=[],
        )
        # задача, требующая ввода — только после второго урока
        self.hard = PracticeTask.objects.create(
            topic=self.topic, language=self.lang, name='Сумма', slug='pyt-hard',
            description='d', status='published', difficulty=1,
            solution='a = int(input())\nprint(a + 1)\n',
            test_cases=[{'input': '1\n', 'expected_output': '2'}],
        )

    def test_first_lesson_skills(self):
        skills = skills_before_lesson(self.lesson1)
        self.assertIn('print', skills)
        self.assertNotIn('input', skills)

    def test_task_without_tests_excluded(self):
        allowed = lesson_tasks_for(self.lesson2, limit=0)
        self.assertNotIn(self.easy, allowed)

    def test_task_requiring_input_not_before_input_lesson(self):
        allowed1 = lesson_tasks_for(self.lesson1, limit=0)
        self.assertNotIn(self.hard, allowed1)

    def test_task_allowed_after_input_lesson(self):
        allowed2 = lesson_tasks_for(self.lesson2, limit=0)
        self.assertIn(self.hard, allowed2)

    def test_no_duplicates(self):
        names = [t.name for t in lesson_tasks_for(self.lesson2, limit=0)]
        self.assertEqual(len(names), len(set(names)))


class PreviousLessonsTests(TestCase):
    """Навыки предыдущих уроков тоже доступны."""

    def setUp(self):
        self.lang = ProgrammingLanguage.objects.create(name='Py2', slug='prev-lang', status='published')
        self.program = CourseProgram.objects.create(
            language=self.lang, name='P2', slug='prev-prog', status='published')
        self.t1 = Topic.objects.create(program=self.program, name='T1', slug='prev-t1',
                                       status='published', order=1)
        self.t2 = Topic.objects.create(program=self.program, name='T2', slug='prev-t2',
                                       status='published', order=2)
        # урок 1: только print
        self.l1 = Lesson.objects.create(topic=self.t1, name='L1', slug='prev-l1', status='published',
                                        order=1, lesson_type='text',
                                        content=[{'type': 'code', 'content': 'print("hi")'}])
        # урок 2: только цикл
        self.l2 = Lesson.objects.create(topic=self.t2, name='L2', slug='prev-l2', status='published',
                                        order=1, lesson_type='text',
                                        content=[{'type': 'code', 'content': 'for i in range(2):\n    print(i)'}])

    def test_second_lesson_inherits_first(self):
        skills = skills_before_lesson(self.l2)
        self.assertIn('print', skills)   # из первого урока
        self.assertIn('for', skills)     # из второго

    def test_order_uses_track_not_just_topic(self):
        from practice.lesson_tasks import ordered_lessons

        order = ordered_lessons(self.lang)
        self.assertEqual([l.id for l in order], [self.l1.id, self.l2.id])
