"""Views for end-of-course tests."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import get_language
from django.views import View

from learning.models import CourseProgram
from practice.assessment_views import json_for_script
from practice.course_assessment import evaluate, get_questions
from practice.course_assessment_models import CourseTestQuestion, CourseTestResult


class CourseTestBaseMixin(LoginRequiredMixin):
    login_url = reverse_lazy('accounts:login')
    question_limit = 20

    def get_program(self):
        return get_object_or_404(
            CourseProgram.objects.filter(status='published').select_related('language'),
            slug=self.kwargs['slug'],
        )


class CourseTestView(CourseTestBaseMixin, View):
    """End-of-course test page and answer submission."""

    template_name = 'practice/course_test.html'

    def get(self, request, slug):
        program = self.get_program()
        questions = get_questions(program, self.question_limit)

        if not questions:
            return render(request, self.template_name, {
                'program': program,
                'language': program.language,
                'no_questions': True,
                'history': self.get_history(request, program),
            })

        lang = get_language()
        return render(request, self.template_name, {
            'program': program,
            'language': program.language,
            'questions_payload': json_for_script(
                [q.to_payload(lang) for q in questions]
            ),
            'question_count': len(questions),
            'history': self.get_history(request, program),
        })

    def post(self, request, slug):
        program = self.get_program()
        questions = get_questions(program, self.question_limit)

        if not questions:
            return redirect('practice:course_test', slug=program.slug)

        answers = {}
        for question in questions:
            field = f'q_{question.pk}'
            if question.question_type == CourseTestQuestion.QuestionType.MULTIPLE_CHOICE:
                value = request.POST.getlist(field)
            else:
                value = request.POST.get(field)
            if value not in (None, '', []):
                answers[str(question.pk)] = value

        lang = get_language()
        result, details = evaluate(program, questions, answers, lang=lang)
        result.user = request.user
        result.save()

        return render(request, 'practice/course_test_result.html', {
            'program': program,
            'language': program.language,
            'result': result,
            'details': details,
        })

    @staticmethod
    def get_history(request, program):
        return CourseTestResult.objects.filter(
            user=request.user, program=program
        ).only(
            'pk', 'score', 'level', 'created_at', 'total_questions', 'correct_answers'
        )[:5]


class CourseTestResultDetailView(CourseTestBaseMixin, View):
    """Saved course test result."""

    def get(self, request, slug, pk):
        program = self.get_program()
        result = get_object_or_404(
            CourseTestResult, pk=pk, user=request.user, program=program
        )
        lang = get_language()

        questions = {
            question.pk: question
            for question in CourseTestQuestion.all_objects.filter(
                pk__in=[answer.get('id') for answer in result.answers]
            ).select_related('topic')
        }

        details = []
        for answer in result.answers or []:
            question = questions.get(answer.get('id'))
            if question is None:
                continue
            is_correct, user_display, correct_display = question.check_answer(
                answer.get('answer'), lang
            )
            raw_answer = answer.get('answer')
            if isinstance(raw_answer, (list, tuple, set)):
                answered = bool(raw_answer)
            else:
                answered = bool(str(raw_answer or '').strip())
            details.append({
                'question': question.localized('question', lang),
                'type': question.question_type,
                'topic': question.topic_label or (
                    question.topic.name
                    if question.topic_id and question.topic
                    else 'Общее'
                ),
                'is_correct': is_correct,
                'answered': answered,
                'selected_text': user_display,
                'correct_text': correct_display,
                'explanation': question.localized('explanation', lang),
            })

        return render(request, 'practice/course_test_result.html', {
            'program': program,
            'language': program.language,
            'result': result,
            'details': details,
            'is_saved': True,
        })
