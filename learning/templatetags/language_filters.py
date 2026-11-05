"""
Custom template filters for programming language display names and colors.
"""

from django import template

register = template.Library()

# Friendly display names for language slugs
LANGUAGE_NAMES = {
    'bash': 'Bash',
    'shell': 'Bash',
    'sh': 'Bash',
    'python': 'Python',
    'javascript': 'JavaScript',
    'js': 'JavaScript',
    'typescript': 'TypeScript',
    'ts': 'TypeScript',
    'cpp': 'C++',
    'c++': 'C++',
    'cxx': 'C++',
    'cc': 'C++',
    'csharp': 'C#',
    'c#': 'C#',
    'cs': 'C#',
    'rust': 'Rust',
    'rs': 'Rust',
    'css': 'CSS',
    'html': 'HTML',
    'htm': 'HTML',
    'sql': 'SQL',
    'json': 'JSON',
    'xml': 'XML',
    'yaml': 'YAML',
    'yml': 'YAML',
    'toml': 'TOML',
    'ini': 'INI',
    'text': 'Text',
    'txt': 'Text',
}

# Accent colors for each language (used for code block borders and labels)
LANGUAGE_COLORS = {
    'bash': '#4EAA25',
    'shell': '#4EAA25',
    'sh': '#4EAA25',
    'python': '#3776AB',
    'javascript': '#F7DF1E',
    'js': '#F7DF1E',
    'typescript': '#3178C6',
    'ts': '#3178C6',
    'cpp': '#00599C',
    'c++': '#00599C',
    'cxx': '#00599C',
    'cc': '#00599C',
    'csharp': '#68217A',
    'c#': '#68217A',
    'cs': '#68217A',
    'rust': '#DEA584',
    'rs': '#DEA584',
    'css': '#1572B6',
    'html': '#E34F26',
    'htm': '#E34F26',
    'sql': '#E38C00',
    'json': '#292929',
    'xml': '#0060AC',
    'yaml': '#00395E',
    'yml': '#00395E',
    'toml': '#6D8086',
    'ini': '#00395E',
}


@register.filter
def language_name(value):
    """Convert a language slug to a friendly display name."""
    if not value:
        return 'Python'
    return LANGUAGE_NAMES.get(str(value).lower(), str(value).title())


@register.filter
def language_color(value):
    """Convert a language slug to its accent color hex code."""
    if not value:
        return '#6366f1'
    return LANGUAGE_COLORS.get(str(value).lower(), '#6366f1')
