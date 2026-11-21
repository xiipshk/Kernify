"""
Custom math template filters.
"""

from django import template

register = template.Library()


@register.filter
def divide(value, arg):
    """Divide value by arg. Returns 0 on error."""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0


@register.filter
def mul(value, arg):
    """Multiply value by arg. Returns 0 on error."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
