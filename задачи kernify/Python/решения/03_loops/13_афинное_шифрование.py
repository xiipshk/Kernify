# Решение: Афинное шифрование
# Тема: Циклы (for, while)

def solve():
    a, b = map(int, input().split())
    text = input().strip()
    result = ''
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            x = ord(ch) - base
            y = (a * x + b) % 26
            result += chr(base + y)
        else:
            result += ch
    print(result)
