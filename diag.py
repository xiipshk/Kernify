import os, sys

print("CWD:", os.getcwd())
print("Exists .:", os.path.exists('.'))
print("Is dir .:", os.path.isdir('.'))

# Try to write a test file
try:
    with open('test_diag.txt', 'w', encoding='utf-8') as f:
        f.write('hello')
    print("WRITE_OK: test_diag.txt created")
    os.remove('test_diag.txt')
    print("REMOVE_OK: test_diag.txt deleted")
except Exception as e:
    print("WRITE_ERROR:", type(e).__name__, str(e))

# Try fixtures path
try:
    with open('fixtures/lessons/csharp/32.json', 'r', encoding='utf-8') as f:
        content = f.read()
    print("READ_OK: csharp/32.json readable,", len(content), "chars")
except Exception as e:
    print("READ_ERROR:", type(e).__name__, str(e))

# Try writing to fixtures path
try:
    with open('fixtures/lessons/csharp/32.json', 'wb') as f:
        f.write(b'test')
    print("WRITE_OK: csharp/32.json writable")
except Exception as e:
    print("WRITE_ERROR:", type(e).__name__, str(e))
