"""Проверка банка задач: запускает каждое решение через раннер и сверяет с эталоном."""
import os
import sys

import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from runner import code_runner
from practice.task_bank import EXERCISES

LANGS = ['python', 'cpp', 'javascript', 'rust']
failures = []
checked = 0

for ex in EXERCISES:
    for lang in LANGS:
        code = ex['solutions'].get(lang)
        if not code:
            continue
        # проверим на первых двух тестах
        for (inp, expected) in ex['tests'][:2]:
            checked += 1
            result = code_runner.run_code(code, lang, stdin=inp)
            got = (result.output or '').strip()
            exp = expected.strip()
            if not result.success or got != exp:
                failures.append({
                    'exercise': ex['id'],
                    'lang': lang,
                    'input': inp,
                    'expected': exp,
                    'got': got,
                    'error': (result.error or '')[:200],
                })

print(f'\nПроверено запусков: {checked}')
print(f'Провалов: {len(failures)}')
for f in failures:
    print(f"\n❌ {f['exercise']} [{f['lang']}] input={f['input']!r}")
    print(f"   expected={f['expected']!r} got={f['got']!r}")
    if f['error']:
        print(f"   error: {f['error']}")

sys.exit(1 if failures else 0)
