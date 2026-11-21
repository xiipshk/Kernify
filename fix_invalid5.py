import json, os

base = 'fixtures/lessons'
results = []

def check_json_file(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    try:
        json.loads(content)
        return True, content, None
    except json.JSONDecodeError as e:
        return False, content, e

# ===== FIX 1: csharp/32.json =====
path = os.path.join(base, 'csharp', '32.json')
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Line 492 (index 491): missing opening [ and closing ],
line_idx = 491
line = lines[line_idx]
stripped = line.rstrip('\n')
leading = len(stripped) - len(stripped.lstrip())
content_part = stripped[leading:]
new_line = ' ' * leading + '[' + content_part + '],\n'
lines[line_idx] = new_line
content = ''.join(lines)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
ok, _, _ = check_json_file(path)
results.append(f"csharp/32.json: {'FIXED' if ok else 'STILL BROKEN'}")

if not ok:
    # Try to find the actual error
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        lines2 = content.split('\n')
        li = e.lineno - 1
        col = e.colno
        line2 = lines2[li] if li < len(lines2) else ''
        results.append(f"  csharp/32.json error: line {e.lineno} col {col} char={repr(line2[col-1:col] if col <= len(line2) else '?')}")

# ===== FIX 2: python/02.json =====
path = os.path.join(base, 'python', '02.json')
ok, content, err = check_json_file(path)
if not ok:
    lines = content.split('\n')
    li = err.lineno - 1
    col = err.colno
    line = lines[li] if li < len(lines) else ''

    # "Expecting ',' delimiter" at col 304 means a comma is missing
    # Let's look at what's around column 304
    results.append(f"python/02.json: error at line {err.lineno} col {col}")
    results.append(f"  Line {err.lineno} length: {len(line)}")
    results.append(f"  Char at col {col}: {repr(line[col-1] if col <= len(line) else '?')}")

    # The error is "Expecting ',' delimiter" - means after a value, a comma was expected
    # Let's look at what's before the error position
    start = max(0, col - 30)
    end = min(len(line), col + 30)
    results.append(f"  Context: {repr(line[start:end])}")

    # Common fix: if there's a missing comma between two values
    # Let's check if col 304 is at a position where a comma should be
    if col <= len(line):
        ch = line[col-1]
        results.append(f"  Error char: {repr(ch)}")
else:
    results.append("python/02.json: already valid")

# ===== FIX 3: rust/02.json =====
path = os.path.join(base, 'rust', '02.json')
ok, content, err = check_json_file(path)
if not ok:
    lines = content.split('\n')
    li = err.lineno - 1
    col = err.colno
    line = lines[li] if li < len(lines) else ''
    results.append(f"rust/02.json: error at line {err.lineno} col {col}")
    results.append(f"  Line {err.lineno} length: {len(line)}")
    results.append(f"  Char at col {col}: {repr(line[col-1] if col <= len(line) else '?')}")
    start = max(0, col - 30)
    end = min(len(line), col + 30)
    results.append(f"  Context: {repr(line[start:end])}")
else:
    results.append("rust/02.json: already valid")

# Write results to file
with open('fix_results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

print("Done. Results in fix_results.txt")
