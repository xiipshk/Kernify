import json, os

base = 'fixtures/lessons'

# Fix csharp/32.json
path = os.path.join(base, 'csharp', '32.json')
with open(path, encoding='utf-8') as f:
    content = f.read()
try:
    json.loads(content)
    print("csharp/32.json: already valid")
except json.JSONDecodeError as e:
    print(f"csharp/32.json: {e} at line {e.lineno} col {e.colno}")
    lines = content.split('\n')
    if e.lineno <= len(lines):
        line = lines[e.lineno - 1]
        print(f"  Line {e.lineno}: {repr(line[:200])}")
        if e.colno <= len(line):
            print(f"  Error at char: {repr(line[e.colno-1])}")

# Fix python/02.json
path = os.path.join(base, 'python', '02.json')
with open(path, encoding='utf-8') as f:
    content = f.read()
try:
    json.loads(content)
    print("python/02.json: already valid")
except json.JSONDecodeError as e:
    print(f"python/02.json: {e} at line {e.lineno} col {e.colno}")
    lines = content.split('\n')
    if e.lineno <= len(lines):
        line = lines[e.lineno - 1]
        print(f"  Line {e.lineno}: {repr(line[:200])}")
        if e.colno <= len(line):
            print(f"  Error at char: {repr(line[e.colno-1])}")

# Fix rust/02.json
path = os.path.join(base, 'rust', '02.json')
with open(path, encoding='utf-8') as f:
    content = f.read()
try:
    json.loads(content)
    print("rust/02.json: already valid")
except json.JSONDecodeError as e:
    print(f"rust/02.json: {e} at line {e.lineno} col {e.colno}")
    lines = content.split('\n')
    if e.lineno <= len(lines):
        line = lines[e.lineno - 1]
        print(f"  Line {e.lineno}: {repr(line[:200])}")
        if e.colno <= len(line):
            print(f"  Error at char: {repr(line[e.colno-1])}")
