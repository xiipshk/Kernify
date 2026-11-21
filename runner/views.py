"""Views for the code runner app."""
import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.http import require_POST

from runner import code_runner

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
@method_decorator(require_POST, name='dispatch')
class RunCodeView(View):
    """POST /api/code/run/ — выполняет код пользователя.

    Код уходит в собственный Piston (см. ``PISTON_API_URL``). Если запуск
    выключен в настройках (``CODE_RUNNER_ENABLED = False``), эндпоинт
    отвечает 403 и ничего не выполняет.
    """

    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except (ValueError, UnicodeDecodeError):
            return JsonResponse({'error': _('Invalid request body.')}, status=400)

        code = payload.get('code', '')
        language = (payload.get('language') or '').lower()
        stdin = payload.get('stdin', '') or ''

        if not isinstance(code, str) or not isinstance(stdin, str):
            return JsonResponse({'error': _('Invalid request body.')}, status=400)

        if not code_runner.is_enabled():
            # Запуск кода пока отключён на уровне проекта.
            return JsonResponse(
                {
                    'error': _('Code execution is currently disabled.'),
                    'disabled': True,
                },
                status=403,
            )

        validation_error = code_runner.validate_request(code, language)
        if validation_error:
            return JsonResponse({'error': validation_error}, status=400)

        result = code_runner.run_code(code, language, stdin=stdin)

        if result.success:
            return JsonResponse({
                'output': result.output,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.exit_code,
                'execution_ms': result.execution_ms,
                'language': result.language,
                'warnings': result.warnings,
            })

        # Сервер запуска недоступен — 503; ошибка в коде пользователя — 200.
        status = 503 if result.error and 'unavailable' in result.error else 200
        return JsonResponse(
            {
                'error': result.error,
                'output': result.output,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.exit_code,
                'execution_ms': result.execution_ms,
                'language': result.language,
                'warnings': result.warnings,
            },
            status=status,
        )
