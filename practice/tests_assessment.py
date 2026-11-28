"""Тесты вкладки «Тест» (тест-диагностика по языку)."""
import codecs
import json
import re

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from learning.models import ProgrammingLanguage
from practice.assessment_bank import build_options, seed_questions
from practice.models import AssessmentQuestion, AssessmentResult

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='assess@example.com', username='assessuser', password='pass12345',
    )


@pytest.fixture
def language(db):
    return ProgrammingLanguage.objects.create(
        name='Python', slug='python', order=1,
        status=ProgrammingLanguage.PublishStatus.PUBLISHED,
    )


@pytest.fixture
def questions(db, language):
    result = []
    for item in seed_questions():
        if item['language_slug'] != 'python':
            continue
        result.append(AssessmentQuestion.objects.create(
            language=language,
            topic_label=item['topic_label'],
            question=item['question'],
            options=item['options'],
            explanation=item['explanation'],
            difficulty=item['difficulty'],
            order=item['order'],
            status=AssessmentQuestion.PublishStatus.PUBLISHED,
        ))
    return result


@pytest.mark.django_db
def test_bank_has_20_questions_per_language_with_one_correct():
    for item in seed_questions():
        correct = [opt for opt in item['options'] if opt['correct']]
        assert len(correct) == 1, item['question']


@pytest.mark.django_db
def test_assessment_requires_login(client, language, questions):
    response = client.get(reverse('practice:language_assessment', args=[language.slug]))
    assert response.status_code == 302
    assert 'login' in response.url


@pytest.mark.django_db
def test_assessment_page_hides_correct_answers(client, user, language, questions):
    client.force_login(user)
    response = client.get(reverse('practice:language_assessment', args=[language.slug]))
    assert response.status_code == 200
    html = response.content.decode()
    match = re.search(r"JSON\.parse\('(.*?)'\)", html, re.S)
    assert match
    assert '\\u0027' in match.group(1)
    # escapejs превращает JSON в строку с \uXXXX-экранированием
    payload = json.loads(codecs.decode(match.group(1), 'unicode_escape'))
    assert len(payload) == 20
    for question in payload:
        for option in question['options']:
            assert 'correct' not in option


@pytest.mark.django_db
def test_submit_answers_computes_score(client, user, language, questions):
    client.force_login(user)
    data = {}
    for question in questions:
        data[f'q_{question.pk}'] = str(question.correct_index)

    response = client.post(reverse('practice:language_assessment', args=[language.slug]), data)
    assert response.status_code == 200

    result = AssessmentResult.objects.get(user=user, language=language)
    assert result.score == 100
    assert result.level == AssessmentResult.Level.ADVANCED
    assert result.correct_answers == 20
    assert result.wrong_topics == []


@pytest.mark.django_db
def test_partial_answers_report_gaps(client, user, language, questions):
    client.force_login(user)
    # Отвечаем правильно только на первый вопрос, остальные — без ответа
    data = {f'q_{questions[0].pk}': str(questions[0].correct_index)}

    client.post(reverse('practice:language_assessment', args=[language.slug]), data)
    result = AssessmentResult.objects.get(user=user, language=language)
    assert result.score == 5
    assert result.level == AssessmentResult.Level.BEGINNER
    assert result.wrong_topics


@pytest.mark.django_db
def test_saved_result_view(client, user, language, questions):
    client.force_login(user)
    client.post(
        reverse('practice:language_assessment', args=[language.slug]),
        {f'q_{q.pk}': str(q.correct_index) for q in questions},
    )
    result = AssessmentResult.objects.get(user=user)
    response = client.get(reverse('practice:assessment_result', args=[language.slug, result.pk]))
    assert response.status_code == 200


@pytest.mark.django_db
def test_saved_result_is_private(client, user, language, questions):
    client.force_login(user)
    client.post(
        reverse('practice:language_assessment', args=[language.slug]),
        {f'q_{q.pk}': str(q.correct_index) for q in questions},
    )
    result = AssessmentResult.objects.get(user=user)
    other = User.objects.create_user(email='other@example.com', username='other', password='pass12345')
    client.force_login(other)
    response = client.get(reverse('practice:assessment_result', args=[language.slug, result.pk]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_language_page_has_test_tab(client, language):
    response = client.get(reverse('core:language_detail', args=[language.slug]))
    html = response.content.decode()
    assert 'tab-test' in html
    assert reverse('practice:language_assessment', args=[language.slug]) in html


@pytest.mark.django_db
def test_learning_page_has_test_tab_before_courses(client, user, language, questions):
    from learning.models import CourseProgram
    CourseProgram.objects.create(
        language=language, name='Python Basics', slug='python-basics',
        status=CourseProgram.PublishStatus.PUBLISHED,
    )
    client.force_login(user)
    response = client.get(reverse('learning:index'))
    assert response.status_code == 200
    html = response.content.decode()
    assert 'lang-python-test' in html
    assert html.index('lang-python-test') < html.index('lang-python-courses')
    # Карточка курса должна быть внутри вкладки «Курсы»
    courses = html[html.index('lang-python-courses'):]
    assert reverse('core:program_detail', args=['python-basics']) in courses


@pytest.fixture
def course(db, language):
    """Курс с двумя темами, к которым привязаны вопросы."""
    from learning.models import CourseProgram, Topic

    program = CourseProgram.objects.create(
        language=language, name='Python Basics', slug='python-basics',
        status=CourseProgram.PublishStatus.PUBLISHED,
    )
    basics = Topic.objects.create(
        program=program, name='Основы', slug='basics', order=1,
        status=Topic.PublishStatus.PUBLISHED,
    )
    functions = Topic.objects.create(
        program=program, name='Функции', slug='functions', order=2,
        status=Topic.PublishStatus.PUBLISHED,
    )
    return program, basics, functions


def make_question(language, topic, order, correct=True):
    return AssessmentQuestion.objects.create(
        language=language,
        topic=topic,
        topic_label=topic.name,
        question=f'Вопрос {order}',
        options=build_options(['верно', 'неверно'], 0),
        explanation='',
        order=order,
        status=AssessmentQuestion.PublishStatus.PUBLISHED,
    )


@pytest.mark.django_db
def test_topic_marks_follow_last_test(client, user, language, course):
    from learning.models import Topic
    from practice.assessment import topic_marks

    _, basics, functions = course
    q_basics = make_question(language, basics, 1)
    q_functions = make_question(language, functions, 2)

    client.force_login(user)
    client.post(
        reverse('practice:language_assessment', args=[language.slug]),
        {f'q_{q_basics.pk}': '0', f'q_{q_functions.pk}': '1'},
    )

    marks = topic_marks(user, language)
    assert marks[str(basics.pk)] == 'known'
    assert marks[str(functions.pk)] == 'unknown'

    # Повторный тест перезаписывает пометки
    client.post(
        reverse('practice:language_assessment', args=[language.slug]),
        {f'q_{q_basics.pk}': '1', f'q_{q_functions.pk}': '0'},
    )
    marks = topic_marks(user, language)
    assert marks[str(basics.pk)] == 'unknown'
    assert marks[str(functions.pk)] == 'known'


@pytest.mark.django_db
def test_program_page_marks_known_and_unknown_topics(client, user, language, course):
    _, basics, functions = course
    q1 = make_question(language, basics, 1)
    q2 = make_question(language, functions, 2)

    client.force_login(user)
    client.post(
        reverse('practice:language_assessment', args=[language.slug]),
        {f'q_{q1.pk}': '0', f'q_{q2.pk}': '1'},
    )

    response = client.get(reverse('core:program_detail', args=['python-basics']))
    assert response.status_code == 200
    html = response.content.decode()
    assert 'Знаю' in html
    assert 'Повторить' in html
    # Пометка стоит рядом с нужной темой
    basics_pos = html.index('Основы')
    known_pos = html.index('Знаю')
    functions_pos = html.index('Функции')
    review_pos = html.index('Повторить')
    assert basics_pos < known_pos < functions_pos < review_pos


@pytest.mark.django_db
def test_topic_page_shows_mark(client, user, language, course):
    _, basics, _ = course
    q1 = make_question(language, basics, 1)

    client.force_login(user)
    client.post(
        reverse('practice:language_assessment', args=[language.slug]),
        {f'q_{q1.pk}': '0'},
    )

    response = client.get(reverse('core:topic_detail', args=['basics']))
    assert response.status_code == 200
    assert 'Знаю' in response.content.decode()


@pytest.mark.django_db
def test_program_page_without_test_offers_to_take_it(client, user, language, course):
    client.force_login(user)
    response = client.get(reverse('core:program_detail', args=['python-basics']))
    html = response.content.decode()
    assert 'Пройдите тест, чтобы отметить темы' in html
    assert 'Знаю' not in html
