"""
Basic tests for the learning platform.
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from learning.models import ProgrammingLanguage, CourseProgram, Topic, Lesson
from progress.models import UserProgress, LessonProgress, TopicProgress
from learning.services import LessonCompletionService

User = get_user_model()


# Pytest fixtures to reduce duplication
@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123',
        first_name='Test',
    )


@pytest.fixture
def language(db):
    """Create a test programming language."""
    return ProgrammingLanguage.objects.create(
        name='Python', slug='python', order=1,
        status=ProgrammingLanguage.PublishStatus.PUBLISHED,
    )


@pytest.fixture
def program(db, language):
    """Create a test course program."""
    return CourseProgram.objects.create(
        language=language, name='Python Basics', slug='python-basics',
        target_level=CourseProgram.TargetLevel.BEGINNER, order=1,
        status=CourseProgram.PublishStatus.PUBLISHED,
    )


@pytest.fixture
def topic(db, program):
    """Create a test topic."""
    return Topic.objects.create(
        program=program, name='Variables', slug='variables', order=1,
        difficulty=1, status=Topic.PublishStatus.PUBLISHED,
    )


@pytest.fixture
def lesson(db, topic):
    """Create a test lesson."""
    return Lesson.objects.create(
        topic=topic,
        name='Intro to Variables',
        slug='intro-to-variables',
        order=1,
        xp_reward=10,
        content=[{'type': 'text', 'content': 'Hello'}],
        status=Lesson.PublishStatus.PUBLISHED,
    )


@pytest.fixture
def user_progress(db, user, language, program, topic, lesson):
    """Create user progress."""
    return UserProgress.objects.create(
        user=user,
        language=language,
        current_program=program,
        current_topic=topic,
        current_lesson=lesson,
    )


@pytest.mark.django_db
class TestModels:
    """Test model creation and relationships."""

    def test_programming_language_creation(self, language):
        assert language.name == 'Python'
        assert language.slug == 'python'
        assert str(language) == 'Python'

    def test_course_program_creation(self, program, language):
        assert program.language == language
        assert program.target_level == 'beginner'
        assert 'Python' in str(program)

    def test_topic_creation(self, topic, program):
        assert topic.program == program
        assert topic.order == 1
        assert topic.difficulty == 1

    def test_lesson_creation(self, lesson, topic):
        assert lesson.topic == topic
        assert lesson.content == [{'type': 'text', 'content': 'Hello'}]


@pytest.mark.django_db
class TestLessonCompletionService:
    """Test the lesson completion service."""

    def test_complete_lesson_awards_xp(self, user, lesson, user_progress):
        """Test that completing a lesson awards XP."""
        lesson_progress, up, xp_awarded = LessonCompletionService.complete_lesson(
            user, lesson, award_xp=True
        )

        assert xp_awarded is True
        assert lesson_progress.status == LessonProgress.ProgressStatus.COMPLETED
        assert lesson_progress.score == 100

        up.refresh_from_db()
        assert up.total_xp == 10
        assert up.lessons_completed == 1

    def test_complete_lesson_twice_no_double_xp(self, user, lesson, user_progress):
        """Test that completing the same lesson twice doesn't award double XP."""
        # First completion
        LessonCompletionService.complete_lesson(user, lesson, award_xp=True)

        # Second completion
        lesson_progress, up, xp_awarded = LessonCompletionService.complete_lesson(
            user, lesson, award_xp=True
        )

        assert xp_awarded is False  # No XP second time
        up.refresh_from_db()
        assert up.total_xp == 10  # Still 10, not 20
        assert up.lessons_completed == 1  # Still 1

    def test_start_lesson_creates_progress(self, user, lesson):
        """Test that starting a lesson creates LessonProgress."""
        progress = LessonCompletionService.start_lesson(user, lesson)

        assert progress.status == LessonProgress.ProgressStatus.IN_PROGRESS
        assert progress.started_at is not None

    def test_next_lesson_in_same_topic(self, user, topic, lesson):
        """Test getting next lesson in same topic."""
        lesson2 = Lesson.objects.create(
            topic=topic, name='Lesson 2', slug='lesson-2', order=2,
            content=[], status=Lesson.PublishStatus.PUBLISHED,
        )

        next_lesson = LessonCompletionService.get_next_lesson(lesson)
        assert next_lesson == lesson2

    def test_next_lesson_in_next_topic(self, user, program, topic, lesson):
        """Test getting next lesson in next topic."""
        topic2 = Topic.objects.create(
            program=program, name='Topic 2', slug='topic-2', order=2,
            difficulty=1, status=Topic.PublishStatus.PUBLISHED,
        )
        lesson2 = Lesson.objects.create(
            topic=topic2, name='Lesson 2', slug='lesson-2', order=1,
            content=[], status=Lesson.PublishStatus.PUBLISHED,
        )

        next_lesson = LessonCompletionService.get_next_lesson(lesson)
        assert next_lesson == lesson2


@pytest.mark.django_db
class TestUserProgress:
    """Test UserProgress model."""

    def test_user_progress_creation(self, user, language):
        progress = UserProgress.objects.create(
            user=user,
            language=language,
            total_xp=100,
            lessons_completed=5,
        )
        assert progress.total_xp == 100
        assert progress.lessons_completed == 5
        assert progress.current_streak == 0

    def test_unique_user_language_constraint(self, user, language):
        """Test that user can only have one progress per language."""
        UserProgress.objects.create(user=user, language=language)

        with pytest.raises(Exception):  # IntegrityError
            UserProgress.objects.create(user=user, language=language)


@pytest.mark.django_db
class TestTopicProgress:
    """Test TopicProgress model."""

    def test_update_status_mastered(self, user, topic):
        """Test that status becomes MASTERED with high score and completion."""
        progress = TopicProgress.objects.create(
            user=user, topic=topic,
            lessons_total=10, lessons_completed=9, test_score=80,
        )
        progress.update_status()
        assert progress.status == TopicProgress.TopicStatus.MASTERED

    def test_update_status_not_mastered(self, user, topic):
        """Test that status becomes NOT_MASTERED with low score."""
        progress = TopicProgress.objects.create(
            user=user, topic=topic,
            lessons_total=10, lessons_completed=0, test_score=20,
        )
        progress.update_status()
        assert progress.status == TopicProgress.TopicStatus.NOT_MASTERED

    def test_update_status_partial(self, user, topic):
        """Test that status becomes PARTIAL with some completion."""
        progress = TopicProgress.objects.create(
            user=user, topic=topic,
            lessons_total=10, lessons_completed=3, test_score=0,
        )
        progress.update_status()
        assert progress.status == TopicProgress.TopicStatus.PARTIAL


@pytest.mark.django_db
class TestErrorHistorySM2:
    """Test SM-2 algorithm in ErrorHistory."""

    def test_first_review_quality_5(self, user, topic):
        """Test first review with perfect quality."""
        from progress.models import ErrorHistory
        error = ErrorHistory.objects.create(
            user=user, topic=topic,
            error_type=ErrorHistory.ErrorType.SYNTAX,
            error_description='Test error',
        )
        error.schedule_next_review(quality=5)
        assert error.count == 2
        assert error.interval_days == 1
        assert error.ease_factor >= 2.5

    def test_failed_review_resets_count(self, user, topic):
        """Test that failed review (quality < 3) resets count to 1."""
        from progress.models import ErrorHistory
        error = ErrorHistory.objects.create(
            user=user, topic=topic,
            error_type=ErrorHistory.ErrorType.SYNTAX,
            error_description='Test error',
            count=3, interval_days=10, ease_factor=2.5,
        )
        error.schedule_next_review(quality=2)  # Failed
        assert error.count == 1
        assert error.interval_days == 1
        assert error.ease_factor == 2.3  # 2.5 - 0.2