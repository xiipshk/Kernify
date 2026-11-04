"""Admin configuration for core app."""
from django.contrib import admin
from core.models import (
    TimeStampedModel,
    OrderedModel,
    PublishedModel,
    SoftDeleteModel,
)


# These are abstract base models, no admin registration needed
# They will be inherited by concrete models in other apps