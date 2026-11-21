#!/usr/bin/env python3
"""
Лёгкий нативный раннер кода (замена Piston для локальной разработки).

Совместим по API с Piston настолько, чтобы работать с runner/code_runner.py:
  GET  /api/v2/runtimes  -> список установленных языков
  POST /api/v2/execute   -> выполнить код

Запускается внутри контейнера (Dockerfile) с установленными компиляторами.
Не является песочницей уровня nsjail: для локальной разработки этого достаточно,
но наружу такой раннер публиковать нельзя.
"""
import json
import os
import resource
import shutil
import subprocess
import tempfile
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Язык -> (команда компиляции в строку/кортеж, или None если интерпретируемый)
# Для компилируемых: первый элемент — компиляция, второй — запуск.
LANGUAGES = {
    'python': {'display': 'Python', 'run': ['python3', '{src}'], 'version_cmd': ['python3', '--version']},
    'node': {'display': 'JavaScript', 'run': ['node', '{src}'], 'version_cmd': ['node', '--version']},
    'gcc': {
        'display': 'C++',
        'compile': ['g++', '-O2', '-std=c++17', '{src}', '-o', '{bin}'],
        'run': ['{bin}'],
        'version_cmd': ['g++', '--version'],
    },
    'rust': {
        'display': 'Rust',
        'compile': ['rustc', '-O', '{src}', '-o', '{bin}'],
        'run': ['{bin}'],
        'version_cmd': ['rustc', '--version'],
    },
    'dotnet': {
        'display': 'C#',
        'compile': ['mcs', '-out:{exe}', '{src}'],
        'run': ['mono', '{exe}'],
        'version_cmd': ['mcs', '--version'],
    },
}

MEMORY_LIMIT_BYTES = 512 * 1024 * 1024  # 512 МБ


def _detect_version(command):
    try:
        out = subprocess.run(command, capture_output=True, text=True, timeout=10)
        text = (out.stdout or out.stderr or '').strip()
        # python: "Python 3.12.3", node: "v20.11.1", gcc: многострочный
        for part in text.splitlines():
            part = part.strip()
            if not part:
                continue
            if command[0] == 'node':
                return part.lstrip('v').split(' ')[0]
            tokens = part.replace('(', ' ').split()
            # ищем токен вида X.Y[.Z]
            for tok in tokens:
                digits = [c for c in tok if c.isdigit() or c == '.']
                if digits.count('.') >= 1 and len(digits) >= 3:
                    return digits.strip('.')
        return '0.0.0'
    except Exception:
        return '0.0.0'


def _available_runtimes():
    result = []
    for lang, spec in LANGUAGES.items():
        binary = spec['version_cmd'][0]
        if shutil.which(binary) is None:
            continue
        result.append({
            'language': lang,
            'version': _detect_version(spec['version_cmd']),
            'aliases': [],
            'display': spec['display'],
        })
    return result


def _limit_resources():
    try:
        resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_BYTES, MEMORY_LIMIT_BYTES))
    except Exception:
        pass
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (15, 15))
    except Exception:
        pass


def _run_command(argv, cwd, timeout_ms, stdin='', limit_memory=True):
    timeout_s = max(1, int(timeout_ms) / 1000)
    # Лимит памяти применяем только к запуску программы, но не к компилятору:
    # rustc/g++ требуют больше памяти и падают при жёстком 512 МБ.
    preexec = _limit_resources if limit_memory else None
    try:
        proc = subprocess.run(
            argv,
            cwd=cwd,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            preexec_fn=preexec,
        )
        return {
            'stdout': proc.stdout or '',
            'stderr': proc.stderr or '',
            'code': proc.returncode,
        }
    except subprocess.TimeoutExpired:
        return {'stdout': '', 'stderr': 'Process timed out.', 'code': 124}
    except Exception as exc:  # noqa: BLE001
        return {'stdout': '', 'stderr': f'Runner error: {exc}', 'code': 1}


def _execute(payload):
    language = payload.get('language', '')
    files = payload.get('files', []) or []
    stdin = payload.get('stdin', '') or ''
    run_timeout = payload.get('run_timeout', 10000)
    compile_timeout = payload.get('compile_timeout', 10000)

    if language not in LANGUAGES:
        return {
            'language': language,
            'version': '',
            'run': {'stdout': '', 'stderr': f'Language "{language}" is not supported.', 'code': 1},
        }

    if not files:
        return {
            'language': language,
            'version': '',
            'run': {'stdout': '', 'stderr': 'No files provided.', 'code': 1},
        }

    spec = LANGUAGES[language]
    source = files[0].get('content', '')
    name = files[0].get('name', 'main.txt')

    with tempfile.TemporaryDirectory() as tmp:
        src_path = os.path.join(tmp, name)
        with open(src_path, 'w') as fh:
            fh.write(source)

        bin_path = os.path.join(tmp, 'prog')
        exe_path = os.path.join(tmp, 'prog.exe')

        def _subst(tok):
            return (tok.replace('{src}', src_path)
                       .replace('{bin}', bin_path)
                       .replace('{exe}', exe_path))

        if 'compile' in spec:
            compile_argv = [_subst(tok) for tok in spec['compile']]
            compile_result = _run_command(compile_argv, tmp, compile_timeout, limit_memory=False)
            if compile_result['code'] != 0:
                return {
                    'language': language,
                    'version': '',
                    'compile': compile_result,
                    'run': {'stdout': '', 'stderr': '', 'code': None},
                }
            run_argv = [_subst(tok) for tok in spec['run']]
            run_result = _run_command(run_argv, tmp, run_timeout, stdin)
            return {
                'language': language,
                'version': '',
                'compile': {'stdout': '', 'stderr': '', 'code': 0},
                'run': run_result,
            }
        else:
            run_argv = [_subst(tok) for tok in spec['run']]
            run_result = _run_command(run_argv, tmp, run_timeout, stdin)
            return {
                'language': language,
                'version': '',
                'compile': {'stdout': '', 'stderr': '', 'code': 0},
                'run': run_result,
            }


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith('/api/v2/runtimes'):
            self._send_json(_available_runtimes())
        elif self.path == '/health' or self.path == '/health/':
            self._send_json({'status': 'ok'})
        else:
            self._send_json({'error': 'Not found'}, 404)

    def do_POST(self):
        if self.path.startswith('/api/v2/execute'):
            try:
                length = int(self.headers.get('Content-Length', 0))
                payload = json.loads(self.rfile.read(length) or b'{}')
            except Exception:
                self._send_json({'error': 'Invalid JSON'}, 400)
                return
            try:
                result = _execute(payload)
                self._send_json(result)
            except Exception:  # noqa: BLE001
                traceback.print_exc()
                self._send_json({'error': 'Internal error'}, 500)
        else:
            self._send_json({'error': 'Not found'}, 404)

    def log_message(self, fmt, *args):
        pass


def main():
    port = int(os.environ.get('RUNNER_PORT', '2000'))
    server = ThreadingHTTPServer(('0.0.0.0', port), Handler)
    print(f'Runner listening on :{port}', flush=True)
    print('Runtimes:', [r['language'] for r in _available_runtimes()], flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
