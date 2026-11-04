"""Views for learning app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView, View

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
        program = get_object_or_404(CourseProgram, slug=slug, status='published')

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

        return redirect('learning:lesson_learn', slug=progress.current_lesson.slug if progress.current_lesson else program.topics.filter(status='published').order_by('order').first().subtopics.filter(status='published').order_by('order').first().lessons.filter(status='published', is_published=True).order_by('order').first().slug)


class LessonLearnView(LoginRequiredMixin, DetailView):
    """Lesson learning view."""

    model = Lesson
    template_name = 'learning/lesson_learn.html'
    context_object_name = 'lesson'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return Lesson.objects.filter(
            status='published',
            is_published=True
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
            defaults={'status': 'in_progress', 'first_viewed_at': timezone.now()}
        )

        if created or progress.status == 'not_started':
            progress.status = 'in_progress'
            progress.first_viewed_at = timezone.now()
            progress.save()

        # Navigation
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

        # All lessons in subtopic for sidebar
        context['subtopic_lessons'] = Lesson.objects.filter(
            subtopic=lesson.subtopic,
            status='published',
            is_published=True
        ).order_by('order')

        context['progress'] = progress
        return context


class LessonCompleteView(LoginRequiredMixin, View):
    """Mark lesson as complete."""

    def post(self, request, slug):
        lesson = get_object_or_404(Lesson, slug=slug, status='published', is_published=True)

        from progress.models import LessonProgress, UserProgress
        from django.utils import timezone

        progress, _ = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'status': 'completed', 'completed_at': timezone.now(), 'score': 100, 'xp_earned': lesson.xp_reward}
        )

        if progress.status != 'completed':
            progress.status = 'completed'
            progress.completed_at = timezone.now()
            progress.score = 100
            progress.xp_earned = lesson.xp_reward
            progress.save()

            # Update user progress
            user_progress, _ = UserProgress.objects.get_or_create(
                user=request.user,
                language=lesson.subtopic.topic.program.language
            )
            user_progress.total_xp += lesson.xp_reward
            user_progress.lessons_completed += 1
            user_progress.last_activity_date = timezone.now().date()
            user_progress.save()

        return redirect('learning:lesson_learn', slug=slug)


class BookmarkLessonView(LoginRequiredMixin, View):
    """Toggle lesson bookmark."""

    def post(self, request, slug):
        lesson = get_object_or_404(Lesson, slug=slug)

        from accounts.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        if lesson in profile.bookmarked_lessons.all():
            profile.bookmarked_lessons.remove(lesson)
        else:
            profile.bookmarked_lessons.add(lesson)

        return redirect('learning:lesson_learn', slug=slug)


class LessonNotesView(LoginRequiredMixin, DetailView):
    """Lesson notes view."""

    model = Lesson
    template_name = 'learning/lesson_notes.html'
    context_object_name = 'lesson'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    login_url = reverse_lazy('accounts:login')

    def get_queryset(self):
        return Lesson.objects.filter(status='published', is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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


# Import timezone
from django.utils import timezone