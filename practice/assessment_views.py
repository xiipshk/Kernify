"""Представления теста-диагностики по языку."""
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import get_language, gettext_lazy as _
from django.views import View

from learning.models import ProgrammingLanguage
from practice.assessment import evaluate, get_questions
from practice.models import AssessmentQuestion, AssessmentResult


class AssessmentBaseMixin(LoginRequiredMixin):
    login_url = reverse_lazy('accounts:login')
    question_limit = 20

    def get_language(self):
        return get_object_or_404(
            ProgrammingLanguage,
            slug=self.kwargs['slug'],
            status=ProgrammingLanguage.PublishStatus.PUBLISHED,
        )


class LanguageAssessmentView(AssessmentBaseMixin, View):
    """Страница теста по языку + приём ответов (POST)."""

    template_name = 'practice/assessment.html'

    def get_questions(self, language):
        return get_questions(language, self.question_limit)

    def get(self, request, slug):
        language = self.get_language()
        questions = self.get_questions(language)

        if not questions:
            return render(request, 'practice/assessment.html', {
                'language': language,
                'no_questions': True,
                'history': self.get_history(request, language),
            })

        lang = get_language()
        return render(request, self.template_name, {
            'language': language,
            'questions_payload': json_for_script([q.to_payload(lang) for q in questions]),
            'question_count': len(questions),
            'history': self.get_history(request, language),
        })

    def post(self, request, slug):
        language = self.get_language()
        questions = self.get_questions(language)

        if not questions:
            return redirect('practice:language_assessment', slug=language.slug)

        answers = {}
        for question in questions:
            value = request.POST.get(f'q_{question.pk}')
            if value not in (None, ''):
                answers[str(question.pk)] = value

        result, details = evaluate(language, questions, answers)
        result.user = request.user
        result.save()

        lang = get_language()
        if (lang or '').startswith('en'):
            for detail, question in zip(details, questions):
                if question.explanation_en:
                    detail['explanation'] = question.explanation_en

        return render(request, 'practice/assessment_result.html', {
            'language': language,
            'result': result,
            'details': details,
        })

    @staticmethod
    def get_history(request, language):
        return AssessmentResult.objects.filter(
            user=request.user, language=language
        ).only('pk', 'score', 'level', 'created_at', 'total_questions', 'correct_answers')[:5]


class AssessmentResultDetailView(AssessmentBaseMixin, View):
    """Просмотр сохранённого результата."""

    def get(self, request, slug, pk):
        language = self.get_language()
        result = get_object_or_404(
            AssessmentResult, pk=pk, user=request.user, language=language
        )

        # Восстанавливаем подробный разбор для показа
        details = []
        questions = {
            q.pk: q
            for q in AssessmentQuestion.all_objects.filter(
                pk__in=[a.get('id') for a in result.answers]
            )
        }
        for answer in result.answers or []:
            question = questions.get(answer.get('id'))
            if question is None:
                continue
            options = question.get_options()
            selected = answer.get('answer')
            correct_index = answer.get('correct_index')
            details.append({
                'question': question.question,
                'topic': question.topic_label or (
                    question.topic.name if question.topic_id and question.topic else _('Общее')
                ),
                'is_correct': answer.get('correct'),
                'answered': selected is not None,
                'selected_text': (
                    AssessmentQuestion._option_text(options[selected], get_language())
                    if isinstance(selected, int) and 0 <= selected < len(options) else ''
                ),
                'correct_text': (
                    AssessmentQuestion._option_text(options[correct_index], get_language())
                    if isinstance(correct_index, int) and 0 <= correct_index < len(options) else ''
                ),
                'explanation': question.localized('explanation', get_language()),
            })

        return render(request, 'practice/assessment_result.html', {
            'language': language,
            'result': result,
            'details': details,
            'is_saved': True,
        })


def json_for_script(value):
    """
    JSON, безопасный для вставки внутрь ``<script>``.

    Экранирует ``<``, ``>`` и ``&``, чтобы строки с ``</script>`` не ломали
    разметку, и сохраняет результат валидным JSON для ``JSON.parse``.
    """
    return (
        json.dumps(value, ensure_ascii=False)
        .replace('<', '\\u003c')
        .replace('>', '\\u003e')
        .replace('&', '\\u0026')
    )
