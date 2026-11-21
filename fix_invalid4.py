import json, os

base = 'fixtures/lessons'

def check_json(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    try:
        json.loads(content)
        return True, content
    except json.JSONDecodeError as e:
        return False, content

# ===== Fix csharp/32.json =====
path = os.path.join(base, 'csharp', '32.json')
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Line 492 (index 491): missing opening [ and closing ],
# Current: '        "...", "..."\n'
# Should be: '        ["...", "..."],\n'
line_idx = 491
line = lines[line_idx]
# The line has 8 spaces of indentation, then content, then newline
# We need to wrap the content in [ ] and add a comma
stripped = line.rstrip('\n')
# stripped starts with spaces then "...", "..."
# Find where the content starts (after leading spaces)
leading = len(stripped) - len(stripped.lstrip())
content_part = stripped[leading:]
# content_part is: "...", "..."
# We want: ["...", "..."],
new_line = ' ' * leading + '[' + content_part + '],\n'
lines[line_idx] = new_line
content = ''.join(lines)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
ok, _ = check_json(path)
print(f"csharp/32.json: {'VALID' if ok else 'STILL INVALID'}")

# ===== Fix python/02.json =====
path = os.path.join(base, 'python', '02.json')
with open(path, encoding='utf-8') as f:
    content = f.read()
ok, _ = check_json(path)
if not ok:
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        lines = content.split('\n')
        line_idx = e.lineno - 1
        line = lines[line_idx]
        col = e.colno
        print(f"\npython/02.json: {e} at line {e.lineno} col {col}")
        print(f"  Line content (first 200 chars): {repr(line[:200])}")
        print(f"  Char at col {col}: {repr(line[col-1]) if col <= len(line) else 'OUT OF RANGE'}")
        # Show context around the error
        start = max(0, col - 20)
        end = min(len(line), col + 20)
        print(f"  Context: {repr(line[start:end])}")
else:
    print("\npython/02.json: VALID")

# ===== Fix rust/02.json =====
path = os.path.join(base, 'rust', '02.json')
with open(path, encoding='utf-8') as f:
    content = f.read()
ok, _ = check_json(path)
if not ok:
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        lines = content.split('\n')
        line_idx = e.lineno - 1
        line = lines[line_idx]
        col = e.colno
        print(f"\nrust/02.json: {e} at line {e.lineno} col {col}")
        print(f"  Line content (first 200 chars): {repr(line[:200])}")
        print(f"  Char at col {col}: {repr(line[col-1]) if col <= len(line) else 'OUT OF RANGE'}")
        start = max(0, col - 20)
        end = min(len(line), col + 20)
        print(f"  Context: {repr(line[start:end])}")
else:
    print("\nrust/02.json: VALID")
