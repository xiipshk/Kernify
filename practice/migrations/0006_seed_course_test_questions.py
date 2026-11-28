"""Seed course tests from the existing language-level theory questions.

Every program with published theory questions linked to its topics gets a
course test with the same single-choice questions. Intermediate/advanced
programs without questions stay empty until an editor adds mixed questions in
the admin (theory, short answer or code-output tasks).
"""
from django.db import migrations


def seed_course_questions(apps, schema_editor):
    CourseProgram = apps.get_model('learning', 'CourseProgram')
    AssessmentQuestion = apps.get_model('practice', 'AssessmentQuestion')
    CourseTestQuestion = apps.get_model('practice', 'CourseTestQuestion')
    db_alias = schema_editor.connection.alias

    for program in CourseProgram.objects.using(db_alias).all():
        if CourseTestQuestion.objects.using(db_alias).filter(program_id=program.pk).exists():
            continue

        source = (
            AssessmentQuestion.objects.using(db_alias)
            .filter(
                topic__program_id=program.pk,
                status='published',
                is_deleted=False,
            )
            .order_by('order', 'id')
        )

        for index, question in enumerate(source, start=1):
            CourseTestQuestion.objects.using(db_alias).create(
                program_id=program.pk,
                topic_id=question.topic_id,
                topic_label=question.topic_label,
                question_type='single_choice',
                question=question.question,
                question_en=question.question_en,
                options=question.options,
                correct_answers=[],
                explanation=question.explanation,
                explanation_en=question.explanation_en,
                difficulty=question.difficulty,
                skill_level=question.skill_level,
                order=index,
                status='published',
                published_at=question.published_at,
            )


def unseed_course_questions(apps, schema_editor):
    CourseTestQuestion = apps.get_model('practice', 'CourseTestQuestion')
    CourseTestQuestion.objects.using(schema_editor.connection.alias).all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('practice', '0005_coursetestquestion_coursetestresult_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_course_questions, unseed_course_questions),
    ]
