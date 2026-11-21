import json, os

base = 'fixtures/lessons'
langs = ['cpp', 'csharp', 'css', 'javascript', 'python', 'rust']

invalid_files = []
resources_field_files = []
resource_block_files = []

for lang in langs:
    lang_dir = os.path.join(base, lang)
    if not os.path.isdir(lang_dir):
        continue
    files = sorted(os.listdir(lang_dir))
    for fname in files:
        path = os.path.join(lang_dir, fname)
        with open(path, encoding='utf-8') as f:
            content = f.read()
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            invalid_files.append((lang, fname, str(e)))
            continue

        # Check resources field
        if data.get('resources'):
            resources_field_files.append((lang, fname, len(data['resources'])))

        # Check for resource content blocks (heading + following list)
        blocks = data.get('content_blocks', [])
        for i, block in enumerate(blocks):
            if block.get('type') == 'heading':
                text = block.get('text', '')
                if 'ресурс' in text.lower():
                    # Check if next block is a list
                    if i + 1 < len(blocks) and blocks[i+1].get('type') == 'list':
                        resource_block_files.append((lang, fname, text[:50]))
                        break

print("=== INVALID JSON FILES ===")
for lang, fname, err in invalid_files:
    print(f"  {lang}/{fname}: {err[:80]}")
print(f"Total: {len(invalid_files)}")

print("\n=== FILES WITH resources FIELD ===")
for lang, fname, count in resources_field_files:
    print(f"  {lang}/{fname}: {count} resources")
print(f"Total: {len(resources_field_files)}")

print("\n=== FILES WITH RESOURCE CONTENT BLOCKS ===")
for lang, fname, text in resource_block_files:
    print(f"  {lang}/{fname}: {text}")
print(f"Total: {len(resource_block_files)}")
