"""
User accounts models.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from core.models import TimeStampedModel, SoftDeleteModel, ActiveManager


class User(AbstractUser, TimeStampedModel):
    """
    Custom user model extending AbstractUser.
    Uses email as the unique identifier for authentication.
    """

    # Remove username requirement, use email instead
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), unique=True)

    # Profile fields
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)

    # Programming language preference
    class Language(models.TextChoices):
        PYTHON = 'python', _('Python')
        CPP = 'cpp', _('C++')
        CSHARP = 'csharp', _('C#')
        JAVASCRIPT = 'javascript', _('JavaScript')
        RUST = 'rust', _('Rust')
        CSS = 'css', _('CSS')
        C = 'c', _('C')

    preferred_language = models.CharField(
        _('preferred language'),
        max_length=20,
        choices=Language.choices,
        default=Language.PYTHON,
    )

    class Level(models.TextChoices):
        BEGINNER = 'beginner', _('Beginner')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        ADVANCED = 'advanced', _('Advanced')

    current_level = models.CharField(
        _('current level'),
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER,
    )

    # Onboarding
    onboarding_completed = models.BooleanField(_('onboarding completed'), default=False)
    onboarding_step = models.PositiveIntegerField(_('onboarding step'), default=0)

    # Settings
    language = models.CharField(
        _('interface language'),
        max_length=10,
        choices=[('ru', _('Russian')), ('en', _('English'))],
        default='ru',
    )
    theme = models.CharField(
        _('theme'),
        max_length=20,
        choices=[('light', _('Light')), ('system', _('System'))],
        default='light',
    )

    # Email notifications
    email_notifications = models.BooleanField(_('email notifications'), default=True)

    # Telegram integration (for migration from bot)
    telegram_id = models.BigIntegerField(_('Telegram ID'), null=True, blank=True, unique=True)
    telegram_username = models.CharField(_('Telegram username'), max_length=255, blank=True)
    telegram_first_name = models.CharField(_('Telegram first name'), max_length=255, blank=True)
    telegram_last_name = models.CharField(_('Telegram last name'), max_length=255, blank=True)

    # Metadata
    last_activity_at = models.DateTimeField(_('last activity'), null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    def get_preferred_language_display(self):
        return dict(self.Language.choices).get(self.preferred_language, self.preferred_language)

    def get_current_level_display(self):
        return dict(self.Level.choices).get(self.current_level, self.current_level)


class UserProfile(TimeStampedModel):
    """
    Extended profile information for users.
    Separate from User for flexibility.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('user'),
    )

    # Bio and description
    bio = models.TextField(_('bio'), blank=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', null=True, blank=True)

    # Learning preferences
    daily_goal_minutes = models.PositiveIntegerField(_('daily goal (minutes)'), default=30)
    preferred_difficulty = models.CharField(
        _('preferred difficulty'),
        max_length=20,
        choices=User.Level.choices,
        default=User.Level.BEGINNER,
    )

    # Notification settings
    notify_new_content = models.BooleanField(_('notify new content'), default=True)
    notify_reminders = models.BooleanField(_('notify reminders'), default=True)
    notify_achievements = models.BooleanField(_('notify achievements'), default=True)

    # Bookmarked lessons
    bookmarked_lessons = models.ManyToManyField(
        'learning.Lesson',
        verbose_name=_('bookmarked lessons'),
        blank=True,
        related_name='bookmarked_by',
    )

    # Privacy
    profile_public = models.BooleanField(_('public profile'), default=False)
    show_progress = models.BooleanField(_('show progress'), default=True)

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return f"Profile of {self.user.email}"


class UserSettings(TimeStampedModel):
    """
    User-specific settings that can be extended without schema changes.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name=_('user'),
    )

    # Editor settings
    editor_theme = models.CharField(
        _('editor theme'),
        max_length=50,
        default='vs-dark',
    )
    editor_font_size = models.PositiveIntegerField(_('editor font size'), default=14)
    editor_tab_size = models.PositiveIntegerField(_('editor tab size'), default=4)
    editor_word_wrap = models.BooleanField(_('editor word wrap'), default=True)

    # Code execution settings
    auto_run_code = models.BooleanField(_('auto run code'), default=False)
    show_line_numbers = models.BooleanField(_('show line numbers'), default=True)

    # Learning settings
    auto_advance = models.BooleanField(_('auto advance to next lesson'), default=False)
    show_hints = models.BooleanField(_('show hints by default'), default=True)
    spaced_repetition_enabled = models.BooleanField(_('spaced repetition enabled'), default=True)

    # AI settings
    ai_provider_preference = models.CharField(
        _('preferred AI provider'),
        max_length=20,
        choices=[('openai', 'OpenAI'), ('anthropic', 'Anthropic'), ('auto', 'Auto')],
        default='auto',
    )
    ai_model_preference = models.CharField(_('preferred AI model'), max_length=100, blank=True)

    class Meta:
        verbose_name = _('user settings')
        verbose_name_plural = _('user settings')

    def __str__(self):
        return f"Settings of {self.user.email}"