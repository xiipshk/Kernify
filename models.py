"""Database models for the Telegram bot."""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean,
    JSON, BigInteger, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Language(str, PyEnum):
    """Supported programming languages."""
    PYTHON = "python"
    CPP = "cpp"
    CSHARP = "csharp"
    JAVASCRIPT = "javascript"
    RUST = "rust"
    CSS = "css"
    C = "c"


class Level(str, PyEnum):
    """Learning levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TopicStatus(str, PyEnum):
    """Topic mastery status from entrance test."""
    MASTERED = "mastered"
    PARTIAL = "partial"
    NOT_MASTERED = "not_mastered"
    UNCLEAR = "unclear"
    UNTESTED = "untested"


class User(Base):
    """Telegram user model."""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # Telegram user ID
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default="ru")
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Preferences
    preferred_language = Column(String(50), default="python")
    current_level = Column(Enum(Level), default=Level.BEGINNER)

    # Relationships
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    test_results = relationship("TestResult", back_populates="user", cascade="all, delete-orphan")
    practice_sessions = relationship("PracticeSession", back_populates="user", cascade="all, delete-orphan")
    error_repetitions = relationship("ErrorRepetition", back_populates="user", cascade="all, delete-orphan")
    ai_chats = relationship("AIChat", back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    """Programming language course."""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    language = Column(Enum(Language), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    topics = relationship("Topic", back_populates="course", cascade="all, delete-orphan")


class Topic(Base):
    """Course topic/lesson."""
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    level = Column(Enum(Level), nullable=False)
    order = Column(Integer, nullable=False)  # Order within level
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # Lesson content in markdown
    code_examples = Column(JSON, nullable=True)  # List of code examples
    prerequisites = Column(JSON, nullable=True)  # List of prerequisite topic IDs
    is_base_topic = Column(Boolean, default=False)  # Critical for dependencies
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="topics")
    test_questions = relationship("TestQuestion", back_populates="topic", cascade="all, delete-orphan")
    practice_tasks = relationship("PracticeTask", back_populates="topic", cascade="all, delete-orphan")
    user_progress = relationship("UserProgress", back_populates="topic", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('course_id', 'level', 'order', name='unique_topic_order'),
    )


class TestQuestion(Base):
    """Entrance test question for a topic."""
    __tablename__ = "test_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="understanding")  # understanding, code_reading, practical
    expected_answer = Column(Text, nullable=True)  # For auto-grading reference
    difficulty = Column(Integer, default=1)  # 1-3
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    topic = relationship("Topic", back_populates="test_questions")
    test_results = relationship("TestResult", back_populates="question")


class TestResult(Base):
    """User's answer to a test question."""
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("test_questions.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    score = Column(Integer, default=0)  # 0, 1, 2
    user_answer = Column(Text, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    status = Column(Enum(TopicStatus), default=TopicStatus.UNTESTED)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="test_results")
    question = relationship("TestQuestion", back_populates="test_results")
    topic = relationship("Topic")

    __table_args__ = (
        UniqueConstraint('user_id', 'question_id', name='unique_user_question'),
    )


class UserProgress(Base):
    """User's progress on a topic."""
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    status = Column(Enum(TopicStatus), default=TopicStatus.UNTESTED)
    score = Column(Integer, default=0)  # Last test score
    completed_at = Column(DateTime, nullable=True)
    last_reviewed_at = Column(DateTime, nullable=True)
    review_count = Column(Integer, default=0)
    error_patterns = Column(JSON, nullable=True)  # Track common errors
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="progress")
    topic = relationship("Topic", back_populates="user_progress")

    __table_args__ = (
        UniqueConstraint('user_id', 'topic_id', name='unique_user_topic'),
    )


class PracticeTask(Base):
    """Coding practice task."""
    __tablename__ = "practice_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    level = Column(Enum(Level), nullable=False)
    task_type = Column(String(50), nullable=False)  # write_code, fix_bug, explain, improve
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    starter_code = Column(Text, nullable=True)
    solution = Column(Text, nullable=True)
    test_cases = Column(JSON, nullable=False)  # Input/output test cases
    hints = Column(JSON, nullable=True)  # List of hints
    difficulty = Column(Integer, default=1)  # 1-5
    xp_reward = Column(Integer, default=10)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    topic = relationship("Topic", back_populates="practice_tasks")
    sessions = relationship("PracticeSession", back_populates="task")


class PracticeSession(Base):
    """User's practice session for a task."""
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("practice_tasks.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    submitted_code = Column(Text, nullable=True)
    language = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")  # pending, passed, failed, skipped
    test_results = Column(JSON, nullable=True)  # Results of test cases
    ai_feedback = Column(Text, nullable=True)
    hints_used = Column(Integer, default=0)
    attempts = Column(Integer, default=1)
    time_spent = Column(Integer, default=0)  # Seconds
    xp_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="practice_sessions")
    task = relationship("PracticeTask", back_populates="sessions")
    topic = relationship("Topic")


class ErrorRepetition(Base):
    """Track user errors for spaced repetition."""
    __tablename__ = "error_repetitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("practice_tasks.id"), nullable=True)
    error_type = Column(String(100), nullable=False)  # syntax, logic, concept, etc.
    error_description = Column(Text, nullable=False)
    user_code = Column(Text, nullable=True)
    correct_code = Column(Text, nullable=True)
    count = Column(Integer, default=1)
    last_seen = Column(DateTime, default=func.now())
    next_review = Column(DateTime, nullable=True)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="error_repetitions")
    topic = relationship("Topic")
    task = relationship("PracticeTask")


class AIChat(Base):
    """AI tutor chat history."""
    __tablename__ = "ai_chats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    message_role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)  # Context: level, language, etc.
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="ai_chats")
    topic = relationship("Topic")


class SearchQuery(Base):
    """Track programming topic searches."""
    __tablename__ = "search_queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    language = Column(String(50), nullable=True)
    ai_response = Column(Text, nullable=True)
    sources = Column(JSON, nullable=True)  # Web search sources
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User")