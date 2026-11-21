"""Learning signals - imported from models."""
# Signals are defined in models.py with @receiver decorators
# This module imports them to ensure they're loaded when the app is ready

# Import signals from models to register them
from learning.models import (  # noqa: F401
    update_language_counts,
    update_program_counts,
    update_topic_counts,
)

# Default app config will import this in ready()
default_app_config = 'learning.apps.LearningConfig'