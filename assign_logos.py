import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.core.files import File
from learning.models import ProgrammingLanguage

# Map language slugs to logo files
logo_mapping = {
    'python': 'logo/python.webp',  # We'll need to create or find a Python logo
    'cpp': 'logo/C.webp',
    'javascript': 'logo/JavaScript.png',
    'rust': 'logo/Rust.webp',
    'css': 'logo/CSS.webp',
    'csharp': 'logo/C.png',  # Use C.png for C#
}

for lang in ProgrammingLanguage.objects.all():
    if lang.slug in logo_mapping:
        logo_path = logo_mapping[lang.slug]
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                lang.logo.save(os.path.basename(logo_path), File(f), save=True)
                print(f"Updated {lang.name} with logo: {logo_path}")
        else:
            print(f"Logo file not found: {logo_path}")
    else:
        print(f"No logo mapping for: {lang.slug}")

print("Done!")