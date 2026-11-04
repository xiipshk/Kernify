"""Admin configuration for accounts app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from accounts.models import User, UserProfile, UserSettings


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for custom User model."""

    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'username', 'password1', 'password2'),
            },
        ),
    )

    filter_horizontal = ('groups', 'user_permissions')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile."""

    list_display = ('user', 'daily_goal_minutes', 'preferred_difficulty', 'profile_public', 'show_progress')
    list_filter = ('preferred_difficulty', 'profile_public', 'show_progress')
    search_fields = ('user__email', 'user__username', 'bio')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    """Admin for UserSettings."""

    list_display = ('user', 'editor_theme', 'editor_font_size', 'editor_tab_size', 'spaced_repetition_enabled', 'created_at')
    list_filter = ('editor_theme', 'spaced_repetition_enabled', 'show_line_numbers')
    search_fields = ('user__email', 'user__username')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')