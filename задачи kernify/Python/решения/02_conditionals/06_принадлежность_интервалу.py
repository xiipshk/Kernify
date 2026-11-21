# Решение: Принадлежность интервалу
# Тема: Условные операторы (if, else, elif)

def solve():
    a, b, x = map(int, input().split())
    print("YES" if a < x < b else "NO")
