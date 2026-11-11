"""
Basic tests for the learning platform.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from learning.models import ProgrammingLanguage, CourseProgram, Topic, Lesson
from progress.models import UserProgress, LessonProgress, TopicProgress
from learning.services import LessonCompletionService

User = get_user_model()


@pytest.mark.django_db
class TestModels:
    """Test model creation and relationships."""

    def test_programming_language_creation(self):
        lang = ProgrammingLanguage.objects.create(
            name='Python',
            slug='python',
            icon='🐍',
            color='#3776AB',
            order=1,
            status=ProgrammingLanguage.PublishStatus.PUBLISHED,
        )
        assert lang.name == 'Python'
        assert lang.slug == 'python'
        assert str(lang) == 'Python'

    def test_course_program_creation(self):
        lang = ProgrammingLanguage.objects.create(
            name='Python', slug='python', order=1,
            status=ProgrammingLanguage.PublishStatus.PUBLISHED,
        )
        program = CourseProgram.objects.create(
            language=lang,
            name='Python Basics',
            slug='python-basics',
            target_level=CourseProgram.TargetLevel.BEGINNER,
            order=1,
            status=CourseProgram.PublishStatus.PUBLISHED,
        )
        assert program.language == lang
        assert program.target_level == 'beginner'
        assert 'Python' in str(program)

    def test_topic_creation(self):
        lang = ProgrammingLanguage.objects.create(
            name='Python', slug='python', order=1,
            status=ProgrammingLanguage.PublishStatus.PUBLISHED,
        )
        program = CourseProgram.objects.create(
            language=lang, name='Python Basics', slug='python-basics',
            target_level=CourseProgram.TargetLevel.BEGINNER, order=1,
            status=CourseProgram.PublishStatus.PUBLISHED,
        )
        topic = Topic.objects.create(
            program=program,
            name='Variables',
            slug='variables',
            order=1,
            difficulty=1,  # Topic.Difficulty.EASY
            status=Topic.PublishStatus.PUBLISHED,
        )
        assert topic.program == program
        assert topic.order == 1
        assert topic.difficulty == 1

    def test_lesson_creation(self):
        lang = ProgrammingLanguage.objects.create(
            name='Python', slug='python', order=1,
            status=ProgrammingLanguage.PublishStatus.PUBLISHED,
        )
        program = CourseProgram.objects.create(
            language=lang, name='Python Basics', slug='python-basics',
            target_level=CourseProgram.TargetLevel.BEGINNER, order=1,
            status=CourseProgram.PublishStatus.PUBLISHED,
        )
        topic = Topic.objects.create(
            program=program, name='Variables', slug='variables',
            order=1, difficulty=1, status=Topic.PublishStatus.PUBLISHED,
        )
        lesson = Lesson.objects.create(
            topic=topic,
            name='Introduction to Variables',
            slug='intro-to-variables',
            order=1,
            content=[{'type': 'text', 'content': 'Hello'}],
            status=Lesson.PublishStatus.PUBLISHED,
        )
        assert lesson.topic == topic
        assert lesson.content == [{'type': 'text', 'content': 'Hello'}]


@pytest.mark.django_db
class TestLessonCompletionService:
    """Test the lesson completion service."""

    def setup_method(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
        )
        self.lang = ProgrammingLanguage.objects.create(
            name='Python', slug='python', order=1,
            status=ProgrammingLanguage.PublishStatus.PUBLISHED,
        )
        self.program = CourseProgram.objects.create(
            language=self.lang, name='Python Basics', slug='python-basics',
            target_level=CourseProgram.TargetLevel.BEGINNER, order=1,
            status=CourseProgram.PublishStatus.PUBLISHED,
        )
        self.topic = Topic.objects.create(
            program=self.program, name='Variables', slug='variables',
            order=1, difficulty=1, status=Topic.PublishStatus.PUBLISHED,
        )
        self.lesson = Lesson.objects.create(
            topic=self.topic,
            name='Intro to Variables',
            slug='intro-to-variables',
            order=1,
            xp_reward=10,
            content=[{'type': 'text', 'content': 'Hello'}],
            status=Lesson.PublishStatus.PUBLISHED,
        )
        # Create UserProgress for the user
        from progress.models import UserProgress
        self.user_progress = UserProgress.objects.create(
            user=self.user,
            language=self.lang,
            current_program=self.program,
            current_topic=self.topic,
            current_lesson=self.lesson,
        )

    def test_complete_lesson_awards_xp(self):
        """Test that completing a lesson awards XP."""
        lesson_progress, user_progress, xp_awarded = LessonCompletionService.complete_lesson(
            self.user, self.lesson, award_xp=True
        )

        assert xp_awarded is True
        assert lesson_progress.status == LessonProgress.ProgressStatus.COMPLETED
        assert lesson_progress.score == 100

        user_progress.refresh_from_db()
        assert user_progress.total_xp == 10
        assert user_progress.lessons_completed == 1

    def test_complete_lesson_twice_no_double_xp(self):
        """Test that completing the same lesson twice doesn't award double XP."""
        # First completion
        LessonCompletionService.complete_lesson(self.user, self.lesson, award_xp=True)

        # Second completion
        lesson_progress, user_progress, xp_awarded = LessonCompletionService.complete_lesson(
            self.user, self.lesson, award_xp=True
        )

        assert xp_awarded is False  # No XP second time
        # Fetch user_progress from DB since service returns None when no XP awarded
        from progress.models import UserProgress
        user_progress = UserProgress.objects.get(user=self.user, language=self.lang)
        assert user_progress.total_xp == 10  # Still 10, not 20
        assert user_progress.lessons_completed == 1  # Still 1

    def test_start_lesson_creates_progress(self):
        """Test that starting a lesson creates LessonProgress."""
        progress = LessonCompletionService.start_lesson(self.user, self.lesson)

        assert progress.status == LessonProgress.ProgressStatus.IN_PROGRESS
        assert progress.started_at is not None

    def test_next_lesson_in_same_topic(self):
        """Test getting next lesson in same topic."""
        lesson2 = Lesson.objects.create(
            topic=self.topic, name='Lesson 2', slug='lesson-2', order=2,
            content=[], status=Lesson.PublishStatus.PUBLISHED,
        )

        next_lesson = LessonCompletionService.get_next_lesson(self.lesson)
        assert next_lesson == lesson2

    def test_next_lesson_in_next_topic(self):
        """Test getting next lesson in next topic."""
        topic2 = Topic.objects.create(
            program=self.program, name='Topic 2', slug='topic-2', order=2,
            difficulty=1, status=Topic.PublishStatus.PUBLISHED,
        )
        lesson2 = Lesson.objects.create(
            topic=topic2, name='Lesson 2', slug='lesson-2', order=1,
            content=[], status=Lesson.PublishStatus.PUBLISHED,
        )

        next_lesson = LessonCompletionService.get_next_lesson(self.lesson)
        assert next_lesson == lesson2


@pytest.mark.django_db
class TestUserProgress:
    """Test UserProgress model."""

    def setup_method(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
        )
        self.lang = ProgrammingLanguage.objects.create(
            name='Python', slug='python', order=1,
            status=ProgrammingLanguage.PublishStatus.PUBLISHED,
        )

    def test_user_progress_creation(self):
        progress = UserProgress.objects.create(
            user=self.user,
            language=self.lang,
            total_xp=100,
            lessons_completed=5,
        )
        assert progress.total_xp == 100
        assert progress.lessons_completed == 5
        assert progress.current_streak == 0

    def test_unique_user_language_constraint(self):
        """Test that user can only have one progress per language."""
        UserProgress.objects.create(user=self.user, language=self.lang)

        with pytest.raises(Exception):  # IntegrityError
            UserProgress.objects.create(user=self.user, language=self.lang)


@pytest.mark.django_db
class TestTopicProgress:
    """Test TopicProgress model."""

    def setup_method(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
        )
        self.lang = ProgrammingLanguage.objects.create(
            name='Python', slug='python', order=1,
            status=ProgrammingLanguage.PublishStatus.PUBLISHED,
        )
        self.program = CourseProgram.objects.create(
            language=self.lang, name='Python Basics', slug='python-basics',
            target_level=CourseProgram.TargetLevel.BEGINNER, order=1,
            status=CourseProgram.PublishStatus.PUBLISHED,
        )
        self.topic = Topic.objects.create(
            program=self.program, name='Variables', slug='variables', order=1,
            difficulty=1, status=Topic.PublishStatus.PUBLISHED,
        )

    def test_update_status_mastered(self):
        """Test that status becomes MASTERED with high score and completion."""
        progress = TopicProgress.objects.create(
            user=self.user, topic=self.topic,
            lessons_total=10, lessons_completed=9, test_score=80,
        )
        progress.update_status()
        assert progress.status == TopicProgress.TopicStatus.MASTERED

    def test_update_status_not_mastered(self):
        """Test that status becomes NOT_MASTERED with low score and no completion."""
        progress = TopicProgress.objects.create(
            user=self.user, topic=self.topic,
            lessons_total=10, lessons_completed=0, test_score=20,
        )
        progress.update_status()
        assert progress.status == TopicProgress.TopicStatus.NOT_MASTERED

    def test_update_status_partial(self):
        """Test that status becomes PARTIAL with some completion."""
        progress = TopicProgress.objects.create(
            user=self.user, topic=self.topic,
            lessons_total=10, lessons_completed=3, test_score=0,
        )
        progress.update_status()
        assert progress.status == TopicProgress.TopicStatus.PARTIAL


@pytest.mark.django_db
class TestErrorHistorySM2:
    """Test SM-2 algorithm in ErrorHistory."""

    def setup_method(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
        )
        self.lang = ProgrammingLanguage.objects.create(
            name='Python', slug='python', order=1,
            status=ProgrammingLanguage.PublishStatus.PUBLISHED,
        )
        self.program = CourseProgram.objects.create(
            language=self.lang, name='Python Basics', slug='python-basics',
            target_level=CourseProgram.TargetLevel.BEGINNER, order=1,
            status=CourseProgram.PublishStatus.PUBLISHED,
        )
        self.topic = Topic.objects.create(
            program=self.program, name='Variables', slug='variables', order=1,
            difficulty=1, status=Topic.PublishStatus.PUBLISHED,
        )

    def test_first_review_quality_5(self):
        """Test first review with perfect quality."""
        from progress.models import ErrorHistory
        error = ErrorHistory.objects.create(
            user=self.user, topic=self.topic,
            error_type=ErrorHistory.ErrorType.SYNTAX,
            error_description='Test error',
        )
        error.schedule_next_review(quality=5)
        assert error.count == 2
        assert error.interval_days == 1
        assert error.ease_factor >= 2.5

    def test_failed_review_resets_count(self):
        """Test that failed review (quality < 3) resets count to 1."""
        from progress.models import ErrorHistory
        error = ErrorHistory.objects.create(
            user=self.user, topic=self.topic,
            error_type=ErrorHistory.ErrorType.SYNTAX,
            error_description='Test error',
            count=3, interval_days=10, ease_factor=2.5,
        )
        error.schedule_next_review(quality=2)  # Failed
        assert error.count == 1
        assert error.interval_days == 1
        assert error.ease_factor == 2.3  # 2.5 - 0.2