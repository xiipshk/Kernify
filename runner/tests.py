"""Tests for the code runner service and endpoint."""
from unittest.mock import patch

import httpx
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from runner import code_runner


class RunnerServiceTests(TestCase):
    """Unit tests for runner.code_runner."""

    @override_settings(CODE_RUNNER_ENABLED=False)
    def test_disabled_by_default_returns_error(self):
        result = code_runner.run_code('print(1)', 'python')
        self.assertFalse(result.success)
        self.assertIn('disabled', result.error.lower())

    @override_settings(CODE_RUNNER_ENABLED=True)
    def test_empty_code_is_rejected(self):
        result = code_runner.run_code('   ', 'python')
        self.assertFalse(result.success)
        self.assertIn('empty', result.error.lower())

    @override_settings(CODE_RUNNER_ENABLED=True)
    def test_unsupported_language_is_rejected(self):
        result = code_runner.run_code('body { color: red; }', 'css')
        self.assertFalse(result.success)
        self.assertIn('not supported', result.error.lower())

    @override_settings(CODE_RUNNER_ENABLED=True)
    def test_too_long_code_is_rejected(self):
        result = code_runner.run_code('x' * (code_runner.MAX_CODE_LENGTH + 1), 'python')
        self.assertFalse(result.success)
        self.assertIn('too long', result.error.lower())

    def test_supports_language(self):
        self.assertTrue(code_runner.supports_language('python'))
        self.assertTrue(code_runner.supports_language('cpp'))
        self.assertFalse(code_runner.supports_language('css'))

    @override_settings(CODE_RUNNER_ENABLED=True)
    def test_successful_run_is_parsed(self):
        code_runner.cache.clear()
        runtimes = [{'language': 'python', 'version': '3.10.0', 'aliases': ['py']}]
        executed = {
            'language': 'python',
            'version': '3.10.0',
            'run': {'stdout': 'hello\n', 'stderr': '', 'code': 0},
        }

        class FakeResponse:
            status_code = 200

            def __init__(self, payload):
                self._payload = payload

            def raise_for_status(self):
                return None

            def json(self):
                return self._payload

        class FakeClient:
            def __init__(self, *a, **kw):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def get(self, url):
                return FakeResponse(runtimes)

            def post(self, url, json=None):
                return FakeResponse(executed)

        with patch('runner.code_runner.httpx.Client', FakeClient):
            result = code_runner.run_code('print("hello")', 'python')

        self.assertTrue(result.success)
        self.assertEqual(result.output, 'hello')
        self.assertEqual(result.exit_code, 0)

    @override_settings(CODE_RUNNER_ENABLED=True)
    def test_timeout_is_reported(self):
        code_runner.cache.clear()
        runtimes = [{'language': 'python', 'version': '3.10.0'}]

        class FakeResponse:
            status_code = 200

            def __init__(self, payload):
                self._payload = payload

            def raise_for_status(self):
                return None

            def json(self):
                return self._payload

        class TimeoutClient:
            def __init__(self, *a, **kw):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def get(self, url):
                return FakeResponse(runtimes)

            def post(self, url, json=None):
                raise httpx.TimeoutException('boom')

        with patch('runner.code_runner.httpx.Client', TimeoutClient):
            result = code_runner.run_code('print(1)', 'python')

        self.assertFalse(result.success)
        self.assertIn('timed out', result.error.lower())


class RunCodeEndpointTests(TestCase):
    """Integration tests for POST /api/code/run/."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='runner_test', password='test-pass-123'
        )
        self.url = reverse('runner:code_run')

    @override_settings(CODE_RUNNER_ENABLED=False)
    def test_requires_login(self):
        response = self.client.post(
            self.url,
            data='{"code": "print(1)", "language": "python"}',
            content_type='application/json',
        )
        self.assertIn(response.status_code, (302, 403))

    @override_settings(CODE_RUNNER_ENABLED=False)
    def test_disabled_returns_403_and_runs_nothing(self):
        self.client.force_login(self.user)
        with patch('runner.code_runner.httpx.Client') as client_cls:
            response = self.client.post(
                self.url,
                data='{"code": "print(1)", "language": "python"}',
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.json()['disabled'])
        client_cls.assert_not_called()

    @override_settings(CODE_RUNNER_ENABLED=False)
    def test_get_not_allowed(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    @override_settings(CODE_RUNNER_ENABLED=False)
    def test_invalid_json(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data='not json', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    @override_settings(CODE_RUNNER_ENABLED=True)
    def test_enabled_runs_and_returns_output(self):
        self.client.force_login(self.user)
        with patch('runner.views.code_runner.run_code') as run_code:
            run_code.return_value = code_runner.RunResult(
                success=True, language='python', output='42\n', exit_code=0, stdout='42\n',
            )
            response = self.client.post(
                self.url,
                data='{"code": "print(42)", "language": "python"}',
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['output'], '42\n')

    @override_settings(CODE_RUNNER_ENABLED=True)
    def test_enabled_returns_runtime_error(self):
        self.client.force_login(self.user)
        with patch('runner.views.code_runner.run_code') as run_code:
            run_code.return_value = code_runner.RunResult(
                success=False, language='python', error='NameError: x', exit_code=1, stderr='NameError: x',
            )
            response = self.client.post(
                self.url,
                data='{"code": "x", "language": "python"}',
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn('NameError', response.json()['error'])

    @override_settings(CODE_RUNNER_ENABLED=True)
    def test_enabled_rejects_css_language(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            data='{"code": "body{}", "language": "css"}',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('not supported', response.json()['error'].lower())
