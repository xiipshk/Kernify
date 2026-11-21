import json

path = 'fixtures/lessons/csharp/32.json'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 492 (index 491): remove trailing comma
line = lines[491]
stripped = line.rstrip('\n')
if stripped.endswith(','):
    lines[491] = stripped[:-1] + '\n'

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify
with open(path, 'r', encoding='utf-8') as f:
    json.loads(f.read())
print('csharp/32.json: VALID')
