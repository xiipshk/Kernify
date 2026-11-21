"""
Сервис запуска кода через собственный Piston.

Запуск включён настройкой ``CODE_RUNNER_ENABLED`` и требует доступного
сервера Piston по адресу ``PISTON_API_URL``. Собственный Piston
поднимается через ``docker-compose.piston.yml`` и слушает только
``127.0.0.1:2000``.

Код пользователя никогда не выполняется на машине Django — он уходит
в Piston, который изолирует процесс (nsjail), ограничивает время
и память.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx
from django.conf import settings
from django.core.cache import cache

# Алиасы языков Kernify (slug из learning.ProgrammingLanguage) -> имена языков Piston.
# В собственном Piston канонические имена: node, gcc, dotnet (не javascript/c++/csharp).
PISTON_LANGUAGES = {
    'python': 'python',
    'javascript': 'node',
    'cpp': 'gcc',
    'csharp': 'dotnet',
    'rust': 'rust',
    # CSS — это не исполняемый язык, его нельзя запустить как программу.
}

# Ограничения, чтобы не залить библиотеку кода и не ждать вечно.
MAX_CODE_LENGTH = 20_000
DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_MEMORY_LIMIT_MB = 256
MAX_OUTPUT_LENGTH = 50_000
RUNTIMES_CACHE_SECONDS = 300


@dataclass
class RunResult:
    """Результат запуска кода."""

    success: bool
    output: str = ''
    error: Optional[str] = None
    exit_code: Optional[int] = None
    execution_ms: Optional[int] = None
    language: str = ''
    stdout: str = ''
    stderr: str = ''
    warnings: list = field(default_factory=list)


def is_enabled() -> bool:
    """Включён ли запуск кода в настройках."""
    return bool(getattr(settings, 'CODE_RUNNER_ENABLED', False))


def supports_language(language_slug: str) -> bool:
    """Поддерживает ли раннер этот язык."""
    return (language_slug or '').lower() in PISTON_LANGUAGES


def supported_languages() -> list:
    """Языки, которые можно запустить на сервере (для выпадающих списков)."""
    return sorted(PISTON_LANGUAGES.keys())


def validate_request(code: str, language: str) -> Optional[str]:
    """Проверяет входные данные. Возвращает текст ошибки или None."""
    if not isinstance(code, str) or not code.strip():
        return 'Code is empty.'
    if len(code) > MAX_CODE_LENGTH:
        return f'Code is too long (max {MAX_CODE_LENGTH} characters).'
    if not supports_language(language):
        return f'Language "{language}" is not supported by the code runner.'
    return None


def _piston_language_and_version(client: httpx.Client, language: str) -> Optional[tuple]:
    """Возвращает (language, version) для Piston или None, если язык недоступен."""
    api_url = settings.PISTON_API_URL

    # Кэшируем список языков на несколько минут: он меняется только при
    # установке/удалении пакетов в Piston.
    cache_key = f'runner:piston:runtimes:{api_url}'
    runtimes = cache.get(cache_key)
    if runtimes is None:
        response = client.get(f'{api_url}/runtimes')
        response.raise_for_status()
        runtimes = response.json()
        cache.set(cache_key, runtimes, RUNTIMES_CACHE_SECONDS)

    wanted = PISTON_LANGUAGES[language.lower()]

    candidates = [
        runtime
        for runtime in runtimes
        if runtime.get('language') == wanted
    ]
    if not candidates:
        return None

    # Берём самую свежую версию.
    def version_key(runtime):
        version = runtime.get('version', '0')
        parts = []
        for chunk in version.split('.'):
            parts.append(int(chunk) if chunk.isdigit() else 0)
        return parts

    chosen = max(candidates, key=version_key)
    return chosen.get('language'), chosen.get('version', '*')


def run_code(code: str, language: str, stdin: str = '') -> RunResult:
    """Запускает код через Piston API.

    Функция проверяет настройки и входные данные, но не запускает ничего,
    если раннер выключен.
    """
    language = (language or '').lower()

    if not is_enabled():
        return RunResult(
            success=False,
            language=language,
            error='Code execution is currently disabled.',
        )

    validation_error = validate_request(code, language)
    if validation_error:
        return RunResult(success=False, language=language, error=validation_error)

    timeout = getattr(settings, 'CODE_EXECUTION_TIMEOUT', DEFAULT_TIMEOUT_SECONDS)

    try:
        with httpx.Client(timeout=timeout) as client:
            target = _piston_language_and_version(client, language)
            if target is None:
                return RunResult(
                    success=False,
                    language=language,
                    error=f'Language "{language}" is not available on the runner.',
                )

            language_name, language_version = target
            payload = {
                'language': language_name,
                'version': language_version,
                'files': [{'name': _file_name(language), 'content': code}],
                'stdin': stdin or '',
                'run_timeout': timeout * 1000,
                'compile_timeout': timeout * 1000,
            }

            started = time.monotonic()
            response = client.post(f'{settings.PISTON_API_URL}/execute', json=payload)
            if response.status_code == 429:
                return RunResult(
                    success=False,
                    language=language,
                    error='Too many runs in a short time. Please wait a moment and try again.',
                )
            response.raise_for_status()
            execution_ms = int((time.monotonic() - started) * 1000)
            data = response.json()

    except httpx.TimeoutException:
        return RunResult(success=False, language=language, error='Code execution timed out.')
    except httpx.ConnectError:
        return RunResult(
            success=False,
            language=language,
            error='Code runner is unavailable. Make sure the Piston container is running.',
        )
    except httpx.HTTPError:
        return RunResult(
            success=False,
            language=language,
            error='Code runner is unavailable. Try again later.',
        )

    run = data.get('run', {}) or {}
    compile_run = data.get('compile', {}) or {}
    stdout = run.get('stdout', '') or ''
    stderr = run.get('stderr', '') or ''
    exit_code = run.get('code')
    compile_stderr = compile_run.get('stderr', '') or ''
    compile_exit = compile_run.get('code')

    warnings = []
    if data.get('message'):
        warnings.append(data['message'])

    if compile_stderr or (compile_exit not in (None, 0)):
        output = _clean_output(compile_stderr or stderr)
        return RunResult(
            success=False,
            language=language,
            output=output,
            error=output or 'Compilation failed.',
            exit_code=compile_exit,
            execution_ms=execution_ms,
            stdout=_clean_output(stdout),
            stderr=output,
            warnings=warnings,
        )

    success = exit_code == 0
    stdout = _clean_output(stdout)
    stderr = _clean_output(stderr)
    output = stdout if success else (stderr or stdout)

    return RunResult(
        success=success,
        language=language,
        output=output,
        error=None if success else (stderr or f'Process exited with code {exit_code}.'),
        exit_code=exit_code,
        execution_ms=execution_ms,
        stdout=stdout,
        stderr=stderr,
        warnings=warnings,
    )


# Piston при убийстве процесса по лимиту памяти пишет в stderr служебные
# строки cgroup — для пользователя они бессмысленны.
_CGROUP_NOISE = re.compile(r'^(?:\[?\d+\]?\s*)?(?:memory cgroup|Killed|.*cgroup.*out of memory.*)$', re.IGNORECASE)


def _clean_output(text: str) -> str:
    """Убирает служебные сообщения Piston и обрезает слишком большой вывод."""
    lines = [line for line in (text or '').splitlines() if not _CGROUP_NOISE.match(line.strip())]
    cleaned = '\n'.join(lines).strip('\n')
    if len(cleaned) > MAX_OUTPUT_LENGTH:
        cleaned = cleaned[:MAX_OUTPUT_LENGTH] + '\n… (output truncated)'
    return cleaned


def _file_name(language: str) -> str:
    """Имя файла для Piston — по расширению его иногда угадывают runtime'ы."""
    return {
        'python': 'main.py',
        'javascript': 'main.js',
        'cpp': 'main.cpp',
        'csharp': 'main.cs',
        'rust': 'main.rs',
    }.get(language, 'main.txt')
