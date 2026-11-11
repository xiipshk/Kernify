"""Views for learning app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView, View

from core.views import SlugDetailMixin
from learning.models import CourseProgram, Lesson, Topic
from learning.services import LessonCompletionService


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
            'language', 'current_program', 'current_topic', 'current_lesson'
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
        first_topic = program.topics.filter(status='published').order_by('order').first()
        first_lesson = first_topic.lessons.filter(status='published').order_by('order').first() if first_topic else None

        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            language=program.language,
            defaults={
                'current_program': program,
                'current_topic': first_topic,
                'current_lesson': first_lesson,
            }
        )

        if not created:
            # Update to new program if different or if not set
            if progress.current_program != program or not progress.current_program:
                progress.current_program = program
                progress.current_topic = first_topic
                progress.current_lesson = first_lesson
                progress.save(update_fields=['current_program', 'current_topic', 'current_lesson', 'updated_at'])

        # Redirect to the user's current lesson, or the first available lesson of the program
        if progress.current_lesson:
            return redirect('learning:lesson_learn', slug=progress.current_lesson.slug)
        return redirect('learning:index')


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
        ).select_related('topic__program__language')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        user = self.request.user

        # Get or create progress (mark as in_progress if not started)
        progress = LessonCompletionService.start_lesson(user, lesson)

        # Navigation — next lesson can span across topics within the same program
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

        # If no next lesson in current topic, try first lesson of next topic in same program
        if not context['next_lesson']:
            next_topic = Topic.objects.filter(
                program=lesson.topic.program,
                status='published',
                order__gt=lesson.topic.order
            ).order_by('order').first()
            if next_topic:
                context['next_lesson'] = Lesson.objects.filter(
                    topic=next_topic,
                    status='published'
                ).order_by('order').first()

        # All lessons in topic for sidebar
        context['topic_lessons'] = Lesson.objects.filter(
            topic=lesson.topic,
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

        # Use service for atomic completion with XP awarding
        LessonCompletionService.complete_lesson(request.user, lesson, award_xp=True)

        return redirect('learning:lesson_learn', slug=slug)


class LessonNextView(LoginRequiredMixin, View):
    """Complete lesson, award XP once, and redirect to the next lesson."""

    def post(self, request, slug):
        lesson = Lesson.objects.filter(
            slug=slug, status='published'
        ).first()
        if lesson is None:
            raise Http404(_("No %(verbose_name)s found matching the query") % {
                'verbose_name': Lesson._meta.verbose_name,
            })

        # Use service for atomic completion with XP awarding
        LessonCompletionService.complete_lesson(request.user, lesson, award_xp=True)

        # Redirect to the next lesson — can span across topics within the same program
        next_lesson = LessonCompletionService.get_next_lesson(lesson)

        if next_lesson:
            return redirect('learning:lesson_learn', slug=next_lesson.slug)
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


