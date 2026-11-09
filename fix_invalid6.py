import json, os

base = 'fixtures/lessons'
results = []

def check_json_file(path):
    try:
        with open(path, encoding='utf-8') as f:
            content = f.read()
        json.loads(content)
        return True, content, None
    except json.JSONDecodeError as e:
        try:
            with open(path, encoding='utf-8') as f:
                content = f.read()
        except:
            content = ''
        return False, content, e

def write_file(path, content):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    os.write(fd, content.encode('utf-8'))
    os.close(fd)

# ===== FIX 1: csharp/32.json =====
path = os.path.join(base, 'csharp', '32.json')
ok, content, err = check_json_file(path)
if not ok:
    lines = content.split('\n')
    # Line 492 (index 491): missing opening [ and closing ],
    line_idx = 491
    if line_idx < len(lines):
        line = lines[line_idx]
        stripped = line.rstrip('\n')
        leading = len(stripped) - len(stripped.lstrip())
        content_part = stripped[leading:]
        new_line = ' ' * leading + '[' + content_part + '],\n'
        lines[line_idx] = new_line
        new_content = '\n'.join(lines)
        write_file(path, new_content)
        ok2, _, err2 = check_json_file(path)
        results.append(f"csharp/32.json: {'FIXED' if ok2 else 'STILL BROKEN'}")
        if not ok2 and err2:
            lines2 = new_content.split('\n')
            li = err2.lineno - 1
            col = err2.colno
            l2 = lines2[li] if li < len(lines2) else ''
            ch = l2[col-1] if col <= len(l2) else '?'
            results.append(f"  Error: line {err2.lineno} col {col} char={repr(ch)}")
    else:
        results.append(f"csharp/32.json: line 492 not found")
else:
    results.append("csharp/32.json: already valid")

# ===== FIX 2: python/02.json =====
path = os.path.join(base, 'python', '02.json')
ok, content, err = check_json_file(path)
if not ok:
    results.append(f"python/02.json: error at line {err.lineno} col {err.colno}")
    lines = content.split('\n')
    li = err.lineno - 1
    col = err.colno
    line = lines[li] if li < len(lines) else ''
    if col <= len(line):
        ch = line[col-1]
        results.append(f"  Error char: {repr(ch)}")
        start = max(0, col - 40)
        end = min(len(line), col + 40)
        results.append(f"  Context: {repr(line[start:end])}")

        # Try to fix: "Expecting ',' delimiter" means a comma is missing
        # If the char at col is a quote, we might need a comma before it
        if ch == '"':
            # Insert a comma before this quote
            new_line = line[:col-1] + ',' + line[col-1:]
            lines[li] = new_line
            new_content = '\n'.join(lines)
            write_file(path, new_content)
            ok2, _, err2 = check_json_file(path)
            results.append(f"  After fix: {'FIXED' if ok2 else 'STILL BROKEN'}")
            if not ok2 and err2:
                results.append(f"  New error: line {err2.lineno} col {err2.colno}")
else:
    results.append("python/02.json: already valid")

# ===== FIX 3: rust/02.json =====
path = os.path.join(base, 'rust', '02.json')
ok, content, err = check_json_file(path)
if not ok:
    results.append(f"rust/02.json: error at line {err.lineno} col {err.colno}")
    lines = content.split('\n')
    li = err.lineno - 1
    col = err.colno
    line = lines[li] if li < len(lines) else ''
    if col <= len(line):
        ch = line[col-1]
        results.append(f"  Error char: {repr(ch)}")
        start = max(0, col - 40)
        end = min(len(line), col + 40)
        results.append(f"  Context: {repr(line[start:end])}")

        if ch == '"':
            new_line = line[:col-1] + ',' + line[col-1:]
            lines[li] = new_line
            new_content = '\n'.join(lines)
            write_file(path, new_content)
            ok2, _, err2 = check_json_file(path)
            results.append(f"  After fix: {'FIXED' if ok2 else 'STILL BROKEN'}")
            if not ok2 and err2:
                results.append(f"  New error: line {err2.lineno} col {err2.colno}")
else:
    results.append("rust/02.json: already valid")

with open('fix_results2.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

print("Done. Check fix_results2.txt")
