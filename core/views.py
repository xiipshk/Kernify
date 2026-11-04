"""Views for core app."""
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView

from learning.models import Lesson, ProgrammingLanguage, CourseProgram, SubTopic, Topic


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
        # Stats
        context['total_languages'] = ProgrammingLanguage.objects.filter(status='published').count()
        context['total_programs'] = CourseProgram.objects.filter(status='published').count()
        context['total_lessons'] = Lesson.objects.filter(status='published').count()
        return context


class LanguagesView(ListView):
    """Languages overview page."""

    model = ProgrammingLanguage
    template_name = 'core/languages.html'
    context_object_name = 'languages'
    queryset = ProgrammingLanguage.objects.filter(status='published').order_by('order')


class LanguageDetailView(DetailView):
    """Language detail page with programs."""

    model = ProgrammingLanguage
    template_name = 'core/language_detail.html'
    context_object_name = 'language'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language = self.object
        context['programs'] = CourseProgram.objects.filter(
            language=language,
            status='published'
        ).order_by('order', 'name')
        # User's progress for this language
        if self.request.user.is_authenticated:
            from progress.models import UserProgress
            context['user_progress'] = UserProgress.objects.filter(
                user=self.request.user,
                language=language
            ).first()
        return context


class ProgramDetailView(DetailView):
    """Course program detail page."""

    model = CourseProgram
    template_name = 'core/program_detail.html'
    context_object_name = 'program'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return CourseProgram.objects.filter(status='published').select_related('language')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        program = self.object
        context['topics'] = Topic.objects.filter(
            program=program,
            status='published'
        ).prefetch_related('subtopics').order_by('order')
        # User enrollment check
        if self.request.user.is_authenticated:
            from progress.models import UserProgress
            user_progress = UserProgress.objects.filter(
                user=self.request.user,
                current_program=program
            ).first()
            context['is_enrolled'] = user_progress is not None
            context['user_progress'] = user_progress
        return context


class TopicDetailView(DetailView):
    """Topic detail page."""

    model = Topic
    template_name = 'core/topic_detail.html'
    context_object_name = 'topic'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Topic.objects.filter(status='published').select_related('program__language')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.object
        context['subtopics'] = SubTopic.objects.filter(
            topic=topic,
            status='published'
        ).prefetch_related('lessons').order_by('order')
        return context


class SubTopicDetailView(DetailView):
    """Subtopic detail page."""

    model = SubTopic
    template_name = 'core/subtopic_detail.html'
    context_object_name = 'subtopic'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return SubTopic.objects.filter(status='published').select_related('topic__program__language')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subtopic = self.object
        context['lessons'] = Lesson.objects.filter(
            subtopic=subtopic,
            status='published',
            is_published=True
        ).order_by('order')
        return context


class LessonDetailView(DetailView):
    """Lesson detail page."""

    model = Lesson
    template_name = 'core/lesson_detail.html'
    context_object_name = 'lesson'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Lesson.objects.filter(
            status='published',
            is_published=True
        ).select_related('subtopic__topic__program__language')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        # Increment view count
        Lesson.objects.filter(pk=lesson.pk).update(views_count=models.F('views_count') + 1)
        lesson.refresh_from_db()

        # Next/Previous lessons
        context['prev_lesson'] = Lesson.objects.filter(
            subtopic=lesson.subtopic,
            status='published',
            is_published=True,
            order__lt=lesson.order
        ).order_by('-order').first()
        context['next_lesson'] = Lesson.objects.filter(
            subtopic=lesson.subtopic,
            status='published',
            is_published=True,
            order__gt=lesson.order
        ).order_by('order').first()

        # User progress
        if self.request.user.is_authenticated:
            from progress.models import LessonProgress
            context['user_progress'] = LessonProgress.objects.filter(
                user=self.request.user,
                lesson=lesson
            ).first()

        return context