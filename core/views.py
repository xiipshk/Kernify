"""Views for core app."""
from django.db import models
from django.db.models import Count, Prefetch
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView

from learning.models import Lesson, ProgrammingLanguage, CourseProgram, Topic


class SlugDetailMixin:
    """DetailView mixin that looks up the object by slug and raises a translated Http404 if missing."""

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        slug = self.kwargs.get(self.slug_url_kwarg)
        obj = queryset.filter(**{self.slug_field: slug}).first()
        if obj is None:
            raise Http404(_("No %(verbose_name)s found matching the query") % {
                'verbose_name': queryset.model._meta.verbose_name,
            })
        return obj


class HomeView(TemplateView):
    """Home page view."""

    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Featured languages
        context['languages'] = ProgrammingLanguage.objects.filter(status='published').order_by('order')[:6]
        # Featured programs
        context['featured_programs'] = CourseProgram.objects.filter(
            status='published'
        ).select_related('language').order_by('-created_at')[:3]
        # Stats - use aggregate to avoid multiple count() queries
        from django.db.models import Count
        stats = ProgrammingLanguage.objects.filter(status='published').aggregate(
            total_languages=Count('id')
        )
        stats.update(CourseProgram.objects.filter(status='published').aggregate(
            total_programs=Count('id')
        ))
        stats.update(Lesson.objects.filter(status='published').aggregate(
            total_lessons=Count('id')
        ))
        context.update(stats)
        return context


class LanguagesView(ListView):
    """Languages overview page."""

    model = ProgrammingLanguage
    template_name = 'core/languages.html'
    context_object_name = 'languages'
    queryset = ProgrammingLanguage.objects.filter(status='published').order_by('order')


class LanguageDetailView(SlugDetailMixin, DetailView):
    """Language detail page with programs."""

    model = ProgrammingLanguage
    template_name = 'core/language_detail.html'
    context_object_name = 'language'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset().filter(status='published')
        if self.request.user.is_authenticated:
            from progress.models import UserProgress
            queryset = queryset.prefetch_related(
                models.Prefetch(
                    'user_progress',
                    queryset=UserProgress.objects.filter(user=self.request.user),
                    to_attr='user_progress_cache'
                )
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.object
        context['programs'] = CourseProgram.objects.filter(
            language=language,
            status='published'
        ).order_by('order', 'name')
        # User's progress for this language (from prefetch)
        if self.request.user.is_authenticated:
            progress_cache = getattr(language, 'user_progress_cache', [])
            context['user_progress'] = progress_cache[0] if progress_cache else None

            # Итог последнего теста — для блока «Тест» на странице языка
            from practice.assessment import latest_result
            context['assessment_result'] = latest_result(self.request.user, language)
        return context


class ProgramDetailView(SlugDetailMixin, DetailView):
    """Course program detail page."""

    model = CourseProgram
    template_name = 'core/program_detail.html'
    context_object_name = 'program'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = CourseProgram.objects.filter(status='published').select_related('language')
        if self.request.user.is_authenticated:
            from progress.models import UserProgress
            queryset = queryset.prefetch_related(
                Prefetch(
                    'current_users',
                    queryset=UserProgress.objects.filter(user=self.request.user),
                    to_attr='user_progress_cache'
                )
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program = self.object
        context['topics'] = Topic.objects.filter(
            program=program,
            status='published'
        ).order_by('order')
        # User enrollment check (from prefetch)
        # End-of-course test availability is public; results are per-user.
        from practice.course_assessment import (
            has_questions as course_test_available,
            latest_result as latest_course_result,
            topic_marks as course_topic_marks,
        )
        context['course_test_available'] = course_test_available(program)
        context['course_test_result'] = None
        context['topic_marks'] = {}

        if self.request.user.is_authenticated:
            progress_cache = getattr(program, 'user_progress_cache', [])
            user_progress = progress_cache[0] if progress_cache else None
            context['is_enrolled'] = user_progress is not None
            context['user_progress'] = user_progress

            # Пометки тем «знаю / повторить»: сначала по тесту курса,
            # затем по общему тесту языка.
            from practice.assessment import latest_result, topic_marks
            context['course_test_result'] = latest_course_result(
                self.request.user, program
            )
            course_marks = course_topic_marks(self.request.user, program)
            context['topic_marks'] = course_marks or topic_marks(
                self.request.user, program.language
            )
            context['assessment_result'] = latest_result(self.request.user, program.language)
        return context


class TopicDetailView(SlugDetailMixin, DetailView):
    """Topic detail page."""

    model = Topic
    template_name = 'core/topic_detail.html'
    context_object_name = 'topic'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = Topic.objects.filter(status='published').select_related('program__language')
        if self.request.user.is_authenticated:
            from progress.models import LessonProgress
            queryset = queryset.prefetch_related(
                Prefetch(
                    'lessons__user_progress',
                    queryset=LessonProgress.objects.filter(user=self.request.user),
                    to_attr='user_progress_cache'
                )
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.object
        context['lessons'] = Lesson.objects.filter(
            topic=topic,
            status='published'
        ).order_by('order')

        if self.request.user.is_authenticated:
            from practice.assessment import latest_result, topic_marks
            language = topic.program.language
            context['topic_marks'] = topic_marks(self.request.user, language)
            context['assessment_result'] = latest_result(self.request.user, language)
        return context


class LessonDetailView(SlugDetailMixin, DetailView):
    """Lesson detail page."""

    model = Lesson
    template_name = 'core/lesson_detail.html'
    context_object_name = 'lesson'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = Lesson.objects.filter(
            status='published'
        ).select_related('topic__program__language')
        if self.request.user.is_authenticated:
            from progress.models import LessonProgress
            queryset = queryset.prefetch_related(
                Prefetch(
                    'user_progress',
                    queryset=LessonProgress.objects.filter(user=self.request.user),
                    to_attr='user_progress_cache'
                )
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object

        # Next/Previous lessons
        context['prev_lesson'] = Lesson.objects.filter(
            topic=lesson.topic,
            status='published',
            order__lt=lesson.order
        ).order_by('-order').first()
        context['next_lesson'] = Lesson.objects.filter(
            topic=lesson.topic,
            status='published',
            order__gt=lesson.order
        ).order_by('order').first()

        # User progress (from prefetch)
        if self.request.user.is_authenticated:
            progress_cache = getattr(lesson, 'user_progress_cache', [])
            context['user_progress'] = progress_cache[0] if progress_cache else None

        return context