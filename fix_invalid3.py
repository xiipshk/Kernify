import json, os

base = 'fixtures/lessons'

def check_json(lang, fname):
    path = os.path.join(base, lang, fname)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    try:
        json.loads(content)
        return True, content, None
    except json.JSONDecodeError as e:
        return False, content, e

# ===== Fix csharp/32.json =====
lang, fname = 'csharp', '32.json'
path = os.path.join(base, lang, fname)
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Line 492 (index 491): missing closing bracket and comma
# Current: '        "...", "..."\n'
# Should be: '        ["...", "..."],\n'
old_492 = '        "������� ������", "���"\n'
new_492 = '        ["������� ������", "���"],\n'
if old_492 in ''.join(lines):
    idx = 491  # 0-indexed line 492
    lines[idx] = new_492
    content = ''.join(lines)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    ok, _, err = check_json(lang, fname)
    print(f"csharp/32.json: {'VALID' if ok else 'STILL INVALID: ' + str(err)}")
else:
    print(f"csharp/32.json: pattern not found at line 492")
    # Show what's there
    print(f"  Line 492: {repr(lines[491])}")

# ===== Fix python/02.json =====
lang, fname = 'python', '02.json'
path = os.path.join(base, lang, fname)
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Line 133 (index 132): error at column 304
# Let's check what's there
print(f"\npython/02.json line 133: {repr(lines[132][:350])}")

# ===== Fix rust/02.json =====
lang, fname = 'rust', '02.json'
path = os.path.join(base, lang, fname)
with open(path, encoding='utf-8') as f:
    lines = f.readlines()
ok, _, err = check_json(lang, fname)
if not ok:
    print(f"\nrust/02.json: {err} at line {err.lineno} col {err.colno}")
    for i in range(max(0, err.lineno-3), min(len(lines), err.lineno+2)):
        print(f"  Line {i+1}: {repr(lines[i][:200])}")
else:
    print("\nrust/02.json: VALID")
