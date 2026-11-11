"""
Learning services: Business logic for lesson completion, XP awarding, etc.
Extracted from views to avoid duplication and enable atomic operations.
"""
from django.db import transaction
from django.db.models import F, Count
from django.utils import timezone

from progress.models import LessonProgress, UserProgress, TopicProgress
from learning.models import Lesson, Topic


class LessonCompletionService:
    """
    Service for handling lesson completion atomically.
    Prevents race conditions when awarding XP.
    """

    @staticmethod
    @transaction.atomic
    def complete_lesson(user, lesson, award_xp=True):
        """
        Mark lesson as completed and optionally award XP.
        Uses select_for_update to prevent race conditions.
        Also updates current position and topic progress.

        Returns:
            tuple: (lesson_progress, user_progress, xp_awarded)
                - lesson_progress: LessonProgress instance
                - user_progress: UserProgress instance (or None)
                - xp_awarded: bool, whether XP was actually awarded
        """
        # Lock the lesson progress row for this user+lesson
        lesson_progress = LessonProgress.objects.select_for_update().filter(
            user=user,
            lesson=lesson
        ).first()

        if lesson_progress is None:
            lesson_progress = LessonProgress.objects.create(
                user=user,
                lesson=lesson,
                status=LessonProgress.ProgressStatus.COMPLETED,
                completed_at=timezone.now(),
                score=100,
            )
            xp_awarded = True
        elif lesson_progress.status != LessonProgress.ProgressStatus.COMPLETED:
            lesson_progress.status = LessonProgress.ProgressStatus.COMPLETED
            lesson_progress.completed_at = timezone.now()
            lesson_progress.score = 100
            lesson_progress.save(update_fields=['status', 'completed_at', 'score', 'updated_at'])
            xp_awarded = True
        else:
            # Already completed, no XP award
            xp_awarded = False

        user_progress = None
        if xp_awarded and award_xp:
            # Lock the user progress row for this user+language
            user_progress = UserProgress.objects.select_for_update().filter(
                user=user,
                language=lesson.topic.program.language
            ).first()

            if user_progress:
                # Get next lesson to update current position
                next_lesson = LessonCompletionService.get_next_lesson(lesson)

                # Atomic increment using F() expressions
                update_fields = {
                    'total_xp': F('total_xp') + lesson.xp_reward,
                    'lessons_completed': F('lessons_completed') + 1,
                    'last_activity_at': timezone.now(),
                }

                # Update current position to next lesson (or keep current if no next)
                if next_lesson:
                    update_fields['current_lesson'] = next_lesson
                    update_fields['current_topic'] = next_lesson.topic
                    update_fields['current_program'] = next_lesson.topic.program
                # If no next lesson, we keep current position (user finished the program)

                UserProgress.objects.filter(pk=user_progress.pk).update(**update_fields)
                # Refresh to get updated values
                user_progress.refresh_from_db()

                # Update or create TopicProgress for the completed lesson's topic
                LessonCompletionService._update_topic_progress(user, lesson.topic)

                # Check if topic is now fully completed
                LessonCompletionService._check_topic_completion(user_progress, lesson.topic)

        return lesson_progress, user_progress, xp_awarded

    @staticmethod
    def _update_topic_progress(user, topic):
        """Update or create TopicProgress when a lesson in the topic is completed."""
        topic_progress, created = TopicProgress.objects.get_or_create(
            user=user,
            topic=topic,
            defaults={
                'lessons_total': topic.lessons.filter(status='published').count(),
                'lessons_completed': 0,
                'status': TopicProgress.TopicStatus.UNTESTED,
            }
        )

        # Recalculate completed lessons in this topic
        completed_count = LessonProgress.objects.filter(
            user=user,
            lesson__topic=topic,
            status=LessonProgress.ProgressStatus.COMPLETED
        ).count()

        topic_progress.lessons_completed = completed_count
        topic_progress.lessons_total = topic.lessons.filter(status='published').count()

        # Update status based on completion
        topic_progress.update_status()

        if topic_progress.status == TopicProgress.TopicStatus.MASTERED and not topic_progress.completed_at:
            topic_progress.completed_at = timezone.now()

        topic_progress.save(update_fields=[
            'lessons_completed', 'lessons_total', 'status', 'completed_at', 'updated_at'
        ])

        return topic_progress

    @staticmethod
    def _check_topic_completion(user_progress, completed_topic):
        """
        Check if the completed topic was the last in the current program.
        If so, increment topics_completed.
        """
        # Count completed topics in the current program
        program = user_progress.current_program
        if not program:
            return

        completed_topics_count = TopicProgress.objects.filter(
            user=user_progress.user,
            topic__program=program,
            status__in=[TopicProgress.TopicStatus.MASTERED, TopicProgress.TopicStatus.PARTIAL]
        ).count()

        # Update topics_completed atomically
        UserProgress.objects.filter(pk=user_progress.pk).update(
            topics_completed=completed_topics_count
        )

    @staticmethod
    @transaction.atomic
    def start_lesson(user, lesson):
        """
        Mark lesson as in_progress if not started.
        Also updates UserProgress current position.
        Returns LessonProgress instance.
        """
        lesson_progress, created = LessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={
                'status': LessonProgress.ProgressStatus.IN_PROGRESS,
                'started_at': timezone.now(),
            }
        )

        if not created and lesson_progress.status == LessonProgress.ProgressStatus.NOT_STARTED:
            lesson_progress.status = LessonProgress.ProgressStatus.IN_PROGRESS
            lesson_progress.started_at = timezone.now()
            lesson_progress.save(update_fields=['status', 'started_at', 'updated_at'])

        # Update UserProgress current position
        UserProgress.objects.filter(
            user=user,
            language=lesson.topic.program.language
        ).update(
            current_lesson=lesson,
            current_topic=lesson.topic,
            current_program=lesson.topic.program,
            last_activity_at=timezone.now(),
        )

        return lesson_progress

    @staticmethod
    def get_next_lesson(current_lesson):
        """
        Get the next lesson in the learning sequence.
        Can span across topics within the same program.
        """
        from learning.models import Lesson, Topic

        # Try next lesson in same topic
        next_lesson = Lesson.objects.filter(
            topic=current_lesson.topic,
            status='published',
            order__gt=current_lesson.order
        ).order_by('order').first()

        if next_lesson:
            return next_lesson

        # Try first lesson of next topic in same program
        next_topic = Topic.objects.filter(
            program=current_lesson.topic.program,
            status='published',
            order__gt=current_lesson.topic.order
        ).order_by('order').first()

        if next_topic:
            return Lesson.objects.filter(
                topic=next_topic,
                status='published'
            ).order_by('order').first()

        return None