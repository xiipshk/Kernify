import json

path = 'fixtures/lessons/csharp/32.json'
with open(path, 'rb') as f:
    raw = f.read()

# Decode and fix
content = raw.decode('utf-8')
lines = content.split('\n')

# Line 492 (index 491): remove trailing comma
line = lines[491]
if line.rstrip().endswith(','):
    lines[491] = line.rstrip()[:-1] + '\n'

new_content = '\n'.join(lines)

# Write in binary mode
with open(path, 'wb') as f:
    f.write(new_content.encode('utf-8'))

# Verify
with open(path, 'r', encoding='utf-8') as f:
    json.loads(f.read())
print('csharp/32.json: VALID')
