"""Views for learning app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView, View

from core.views import SlugDetailMixin
from learning.models import CourseProgram, Lesson, SubTopic, Topic


class LearningIndexView(LoginRequiredMixin, TemplateView):
    """Learning index page."""

    template_name = 'learning/index.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get enrolled programs
        from progress.models import UserProgress
        enrolled = UserProgress.objects.filter(user=user).select_related('language', 'current_program')

        # Available programs
        available = CourseProgram.objects.filter(
            status='published'
        ).select_related('language').order_by('language', 'order')

        context.update({
            'enrolled_programs': enrolled,
            'available_programs': available,
        })
        return context


class MyCoursesView(LoginRequiredMixin, ListView):
    """My enrolled courses."""

    template_name = 'learning/my_courses.html'
    context_object_name = 'courses'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        from progress.models import UserProgress
        return UserProgress.objects.filter(user=self.request.user).select_related(
            'language', 'current_program', 'current_topic', 'current_subtopic', 'current_lesson'
        )


class EnrollView(LoginRequiredMixin, View):
    """Enroll in a course program."""

    def post(self, request, slug):
        program = CourseProgram.objects.filter(
            slug=slug, status='published'
        ).first()
        if program is None:
            raise Http404(_("No %(verbose_name)s found matching the query") % {
                'verbose_name': CourseProgram._meta.verbose_name,
            })

        from progress.models import UserProgress
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            language=program.language,
            defaults={
                'current_program': program,
                'current_topic': program.topics.filter(status='published').order_by('order').first(),
            }
        )

        if not created and not progress.current_program:
            progress.current_program = program
            progress.current_topic = program.topics.filter(status='published').order_by('order').first()
            progress.save()

        # Redirect to the user's current lesson, or the first available lesson of the program
        if progress.current_lesson:
            return redirect('learning:lesson_learn', slug=progress.current_lesson.slug)
        first_topic = (
            program.topics.filter(status='published')
            .order_by('order')
            .first()
        )
        if not first_topic:
            return redirect('learning:index')
        first_subtopic = (
            first_topic.subtopics.filter(status='published')
            .order_by('order')
            .first()
        )
        if not first_subtopic:
            return redirect('learning:index')
        first_lesson = (
            first_subtopic.lessons.filter(status='published')
            .order_by('order')
            .first()
        )
        if not first_lesson:
            return redirect('learning:index')
        return redirect('learning:lesson_learn', slug=first_lesson.slug)


class LessonLearnView(LoginRequiredMixin, SlugDetailMixin, DetailView):
    """Lesson learning view."""

    model = Lesson
    template_name = 'learning/lesson_learn.html'
    context_object_name = 'lesson'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return Lesson.objects.filter(
            status='published'
        ).select_related('subtopic__topic__program__language')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        user = self.request.user

        # Get or create progress
        from progress.models import LessonProgress
        progress, created = LessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={'status': 'in_progress', 'started_at': timezone.now()}
        )

        if not created and progress.status == 'not_started':
            progress.status = 'in_progress'
            progress.started_at = timezone.now()
            progress.save(update_fields=['status', 'started_at', 'updated_at'])

        # Navigation
        context['prev_lesson'] = Lesson.objects.filter(
            subtopic=lesson.subtopic,
            status='published',
            order__lt=lesson.order
        ).order_by('-order').first()
        context['next_lesson'] = Lesson.objects.filter(
            subtopic=lesson.subtopic,
            status='published',
            order__gt=lesson.order
        ).order_by('order').first()

        # All lessons in subtopic for sidebar
        context['subtopic_lessons'] = Lesson.objects.filter(
            subtopic=lesson.subtopic,
            status='published'
        ).order_by('order')

        context['progress'] = progress
        return context


class LessonCompleteView(LoginRequiredMixin, View):
    """Mark lesson as complete."""

    def post(self, request, slug):
        lesson = Lesson.objects.filter(
            slug=slug, status='published'
        ).first()
        if lesson is None:
            raise Http404(_("No %(verbose_name)s found matching the query") % {
                'verbose_name': Lesson._meta.verbose_name,
            })

        from progress.models import LessonProgress, UserProgress
        from django.utils import timezone

        progress, _ = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'status': 'completed', 'completed_at': timezone.now(), 'score': 100}
        )

        if progress.status != 'completed':
            progress.status = 'completed'
            progress.completed_at = timezone.now()
            progress.score = 100
            progress.save()

            # Update user progress (atomic increment to avoid race condition)
            UserProgress.objects.filter(
                user=request.user,
                language=lesson.subtopic.topic.program.language
            ).update(
                lessons_completed=F('lessons_completed') + 1,
                last_activity_at=timezone.now(),
            )

        return redirect('learning:lesson_learn', slug=slug)


class BookmarkLessonView(LoginRequiredMixin, View):
    """Toggle lesson bookmark."""

    def post(self, request, slug):
        lesson = Lesson.objects.filter(slug=slug).first()
        if lesson is None:
            raise Http404(_("No %(verbose_name)s found matching the query") % {
                'verbose_name': Lesson._meta.verbose_name,
            })

        from accounts.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        if lesson in profile.bookmarked_lessons.all():
            profile.bookmarked_lessons.remove(lesson)
        else:
            profile.bookmarked_lessons.add(lesson)

        return redirect('learning:lesson_learn', slug=slug)


class LessonNotesView(LoginRequiredMixin, SlugDetailMixin, DetailView):
    """Lesson notes view."""

    model = Lesson
    template_name = 'learning/lesson_notes.html'
    context_object_name = 'lesson'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return Lesson.objects.filter(status='published')

    def get_context_data(self, **kwargs):
        # Notes functionality placeholder
        context['notes'] = ''
        return context


class UserNotesView(LoginRequiredMixin, TemplateView):
    """All user notes."""

    template_name = 'learning/user_notes.html'
    login_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = []  # Placeholder
        return context


