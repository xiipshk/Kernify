# -*- coding: utf-8 -*-
"""Аудит языковых версий: ищем русский текст в EN-версии и английский в RU.

Печатает строки, которые подозрительны:
  * в EN-версии — строки с кириллицей;
  * в RU-версии — строки без кириллицы, где есть 2+ английских слова
    (исключая код, названия языков и технические термины).
"""

import html
import os
import re
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client  # noqa: E402
from accounts.models import User  # noqa: E402
from learning.models import (  # noqa: E402
    CourseProgram,
    Lesson,
    ProgrammingLanguage,
    Topic,
)

CYR = re.compile(r'[А-Яа-яЁё]')
WORD = re.compile(r'[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё\-\']{1,}')
PRE = re.compile(r'<(pre|code|script|style)[^>]*>.*?</\1>', re.S | re.I)
TAG = re.compile(r'<[^>]+>')

# Технические слова и бренды, допустимые в русской версии.
ALLOW = {
    'python', 'javascript', 'typescript', 'rust', 'css', 'html', 'cpp', 'csharp',
    'java', 'go', 'sql', 'json', 'yaml', 'toml', 'xml', 'bash', 'http', 'https',
    'api', 'url', 'uri', 'cli', 'sdk', 'ide', 'ai', 'ml', 'ui', 'ux', 'gpu', 'cpu',
    'kernify', 'github', 'git', 'docker', 'kubernetes', 'linux', 'windows', 'macos',
    'django', 'flask', 'fastapi', 'react', 'vue', 'angular', 'node', 'npm', 'pip',
    'postgresql', 'postgres', 'sqlite', 'redis', 'kafka', 'nginx', 'aws', 'gcp',
    'azure', 'openai', 'anthropic', 'chatgpt', 'telegram', 'email', 'id', 'pdf',
    'csv', 'sms', 'http2', 'http3', 'wasm', 'aot', 'jit', 'gc', 'orm', 'jwt',
    'oauth', 'csrf', 'xss', 'cors', 'csp', 'sql', 'acid', 'ddd', 'dry', 'solid',
    'sm', 'pep', 'crud', 'rest', 'graphql', 'grpc', 'protobuf', 'webhook',
    'webhooks', 'sm2', 'ok', 'vs', 'ip', 'dns', 'tls', 'ssl', 'cdn', 'dom',
    'shadow', 'flexbox', 'grid', 'scss', 'sass', 'less', 'postcss', 'eslint',
    'prettier', 'webpack', 'vite', 'babel', 'jest', 'pytest', 'unittest',
    'async', 'await', 'devops', 'ci', 'cd', 'sre', 'slo', 'sli', 'sla', 'rbac',
    'jvm', 'clr', 'il', 'linq', 'ef', 'asp', 'net', 'wl', 'tensorflow', 'pytorch',
    'numpy', 'pandas', 'sklearn', 'matplotlib', 'openapi', 'swagger', 'trpc',
    'graphql', 'apollo', 'redis', 'memcached', 'rabbitmq', 'celery', 'uvicorn',
    'gunicorn', 'pydantic', 'sqlalchemy', 'alembic', 'poetry', 'conda', 'venv',
    'py', 'js', 'ts', 'cpp', 'cs', 'rs', 'rb', 'php', 'kotlin', 'swift', 'scala',
    'haskell', 'elixir', 'erlang', 'clojure', 'lua', 'perl', 'r', 'matlab',
    'gtk', 'qt', 'wpf', 'winforms', 'blazor', 'maui', 'xamarin', 'unity',
    'unreal', 'godot', 'opengl', 'vulkan', 'directx', 'webgl', 'webgpu',
    'llvm', 'gcc', 'clang', 'msvc', 'mingw', 'cmake', 'make', 'ninja', 'conan',
    'vcpkg', 'meson', 'bazel', 'cargo', 'rustup', 'rustc', 'clippy', 'miri',
    'loom', 'criterion', 'proptest', 'quickcheck', 'mockall', 'serde', 'tokio',
    'anyhow', 'thiserror', 'bindgen', 'cxx', 'jemalloc', 'mimalloc', 'snmalloc',
    'heaptrack', 'valgrind', 'perf', 'flamegraph', 'bpftrace', 'strace', 'ltrace',
    'gdb', 'lldb', 'windbg', 'dotnet', 'nuget', 'msbuild', 'roslyn', 'xunit',
    'nunit', 'mstest', 'moq', 'nsubstitute', 'fluentassertions', 'coverlet',
    'testcontainers', 'playwright', 'selenium', 'cypress', 'vitest', 'mocha',
    'chai', 'karma', 'jasmine', 'storybook', 'figma', 'sketch', 'adobe', 'xd',
    'photoshop', 'illustrator', 'blender', 'ffmpeg', 'imagemagick', 'cuda',
    'opencl', 'rocm', 'tensorrt', 'onnx', 'huggingface', 'langchain', 'rag',
    'prompt', 'prompts', 'token', 'tokens', 'embedding', 'embeddings', 'llm',
    'llms', 'gpt', 'bert', 'transformer', 'transformers', 'attention', 'lora',
    'qlora', 'fine', 'tuning', 'agent', 'agents', 'mcp', 'rag', 'vector',
    'chroma', 'faiss', 'pinecone', 'weaviate', 'qdrant', 'milvus', 'elasticsearch',
    'kibana', 'grafana', 'prometheus', 'loki', 'jaeger', 'zipkin', 'opentelemetry',
    'sentry', 'datadog', 'newrelic', 'splunk', 'elk', 'kafka', 'zookeeper',
    'terraform', 'ansible', 'puppet', 'chef', 'vagrant', 'packer', 'helm',
    'argocd', 'argo', 'flux', 'istio', 'linkerd', 'envoy', 'consul', 'vault',
    'nomad', 'etcd', 'minio', 'ceph', 'nfs', 'smb', 'ssh', 'ftp', 'sftp', 'tcp',
    'udp', 'quic', 'ipv4', 'ipv6', 'nat', 'vpn', 'dhcp', 'bgp', 'ospf', 'vlan',
}


def visible_lines(body):
    body = PRE.sub(' ', body)
    body = TAG.sub('\n', body)
    text = html.unescape(body)
    return [x.strip() for x in text.split('\n') if x.strip()]


def english_offenders(lines):
    out = []
    for ln in lines:
        if CYR.search(ln):
            continue
        words = [w for w in WORD.findall(ln)]
        en = [w for w in words if w.lower() not in ALLOW and not re.fullmatch(r'[A-Z0-9\-]+', w)]
        if len(en) >= 2:
            out.append(ln)
    return out


def main():
    user = User.objects.first()
    client = Client(HTTP_HOST='localhost')
    if user:
        client.force_login(user)

    lang = ProgrammingLanguage.objects.first()
    program = CourseProgram.objects.first()
    topic = Topic.objects.first()
    lesson = Lesson.objects.first()
    task = None
    try:
        from practice.models import PracticeTask
        task = PracticeTask.objects.first()
    except Exception:
        pass

    paths = [
        '/', '/about/', '/contact/', '/languages/',
        f'/languages/{lang.slug}/' if lang else None,
        f'/programs/{program.slug}/' if program else None,
        f'/topics/{topic.slug}/' if topic else None,
        f'/lessons/{lesson.slug}/' if lesson else None,
        '/learning/', '/learning/my-courses/',
        f'/learning/lessons/{lesson.slug}/learn/' if lesson else None,
        '/learning/notes/',
        '/practice/', '/practice/tasks/', '/practice/history/', '/practice/daily/',
        f'/practice/tasks/{task.slug}/' if task else None,
        '/progress/', '/progress/achievements/', '/progress/stats/',
        '/progress/errors/', '/progress/heatmap/',
        '/accounts/dashboard/', '/accounts/profile/', '/accounts/profile/edit/',
        '/accounts/profile/settings/', '/accounts/password/change/',
        '/accounts/email/verify/',
        '/ai/chat/', '/ai/assistant/', '/ai/code-review/', '/ai/explain/',
        '/ai/generate-exercise/', '/ai/usage/',
    ]
    paths = [p for p in paths if p]

    out = []
    for path in paths:
        for lg in ('en', 'ru'):
            resp = client.get(f'/{lg}{path}')
            body = resp.content.decode('utf-8', 'ignore')
            lines = visible_lines(body)
            if resp.status_code != 200:
                out.append(f'### {lg} {path} -> HTTP {resp.status_code}')
                continue
            if lg == 'en':
                bad = [ln for ln in lines if CYR.search(ln)]
                label = 'РУССКИЙ ТЕКСТ В EN'
            else:
                bad = english_offenders(lines)
                label = 'АНГЛИЙСКИЙ ТЕКСТ В RU'
            if bad:
                out.append(f'### {lg} {path} | {label} ({len(bad)})')
                for ln in bad[:15]:
                    out.append('    ' + ln[:200])
                if len(bad) > 15:
                    out.append(f'    ... ещё {len(bad) - 15}')

    report = '\n'.join(out)
    target = '/private/var/folders/xw/9cpnw6912l3d0zdpcntn158w0000gn/T/opencode/lang_audit.txt'
    with open(target, 'w', encoding='utf-8') as fh:
        fh.write(report + '\n')
    print(report or 'Нарушений не найдено.')
    print(f'\nОтчёт: {target}')

    from django.contrib.sessions.models import Session
    Session.objects.all().delete()


if __name__ == '__main__':
    main()
