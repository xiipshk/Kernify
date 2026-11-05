"""Forms for accounts app."""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _

from accounts.models import User, UserProfile, UserSettings


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with email as username."""

    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email'),
            'autocomplete': 'email',
        })
    )
    username = forms.CharField(
        label=_('Username'),
        max_length=150,
        required=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Choose a username'),
            'autocomplete': 'username',
        })
    )
    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter password'),
            'autocomplete': 'new-password',
        }),
        help_text=_('Your password must contain at least 8 characters.'),
    )
    password2 = forms.CharField(
        label=_('Confirm password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm password'),
            'autocomplete': 'new-password',
        }),
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')
        field_classes = {'email': forms.EmailField}

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('A user with that email already exists.'))
        return email

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_('A user with that username already exists.'))
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form using email."""

    username_field = 'email'

    username = forms.CharField(
        label=_('Email or Username'),
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter email or username'),
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter password'),
            'autocomplete': 'current-password',
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = _('Email or Username')


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""

    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio', 'daily_goal_minutes', 'preferred_difficulty', 'notify_new_content', 'notify_reminders', 'notify_achievements', 'profile_public', 'show_progress')
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Tell us about yourself...'),
            }),
            'daily_goal_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 480,
            }),
            'preferred_difficulty': forms.Select(attrs={'class': 'form-select'}),
            'notify_new_content': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_achievements': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'profile_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_progress': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UserSettingsForm(forms.ModelForm):
    """Form for editing user settings."""

    class Meta:
        model = UserSettings
        fields = (
            'editor_theme', 'editor_font_size', 'editor_tab_size', 'editor_word_wrap',
            'auto_run_code', 'show_line_numbers', 'auto_advance', 'show_hints',
            'spaced_repetition_enabled', 'ai_provider_preference', 'ai_model_preference',
        )
        widgets = {
            'editor_theme': forms.Select(attrs={'class': 'form-select'}),
            'editor_font_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 24}),
            'editor_tab_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 2, 'max': 8}),
            'editor_word_wrap': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_run_code': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_line_numbers': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_advance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_hints': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'spaced_repetition_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ai_provider_preference': forms.Select(attrs={'class': 'form-select'}),
            'ai_model_preference': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with Bootstrap classes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})