"""Admin configuration for accounts app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from accounts.models import (
    User,
    UserProfile,
    UserSettings,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for User."""

    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'current_level',
        'preferred_language',
        'is_staff',
        'is_active',
        'date_joined',
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'current_level',
        'preferred_language',
        'language',
        'theme',
        'onboarding_completed',
    )
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name',
        'telegram_username',
    )
    ordering = ('-date_joined',)
    readonly_fields = (
        'last_login',
        'date_joined',
        'created_at',
        'updated_at',
        'last_activity_at',
    )

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Preferences'), {'fields': ('preferred_language', 'current_level', 'language', 'theme')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Onboarding'), {'fields': ('onboarding_completed', 'onboarding_step')}),
        (_('Telegram'), {'fields': ('telegram_id', 'telegram_username', 'telegram_first_name', 'telegram_last_name')}),
        (_('Timestamps'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at', 'last_activity_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile."""

    list_display = (
        'user',
        'daily_goal_minutes',
        'preferred_difficulty',
        'profile_public',
        'show_progress',
        'created_at',
    )
    list_filter = (
        'preferred_difficulty',
        'notify_new_content',
        'notify_reminders',
        'notify_achievements',
        'profile_public',
        'show_progress',
    )
    search_fields = (
        'user__email',
        'user__username',
        'bio',
    )
    raw_id_fields = ('user',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('bookmarked_lessons',)

    fieldsets = (
        (None, {'fields': ('user', 'bio', 'avatar')}),
        (_('Learning preferences'), {'fields': ('daily_goal_minutes', 'preferred_difficulty')}),
        (_('Notifications'), {'fields': ('notify_new_content', 'notify_reminders', 'notify_achievements')}),
        (_('Bookmarks'), {'fields': ('bookmarked_lessons',)}),
        (_('Privacy'), {'fields': ('profile_public', 'show_progress')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """Admin for UserSettings."""

    list_display = (
        'user',
        'editor_theme',
        'editor_font_size',
        'auto_run_code',
        'auto_advance',
        'spaced_repetition_enabled',
        'ai_provider_preference',
        'created_at',
    )
    list_filter = (
        'editor_theme',
        'editor_word_wrap',
        'auto_run_code',
        'show_line_numbers',
        'auto_advance',
        'show_hints',
        'spaced_repetition_enabled',
        'ai_provider_preference',
    )
    search_fields = (
        'user__email',
        'user__username',
        'ai_model_preference',
    )
    raw_id_fields = ('user',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Editor'), {'fields': ('editor_theme', 'editor_font_size', 'editor_tab_size', 'editor_word_wrap')}),
        (_('Code execution'), {'fields': ('auto_run_code', 'show_line_numbers')}),
        (_('Learning'), {'fields': ('auto_advance', 'show_hints', 'spaced_repetition_enabled')}),
        (_('AI'), {'fields': ('ai_provider_preference', 'ai_model_preference')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
