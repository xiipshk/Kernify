# Решение: Степень
# Тема: Циклы (for, while)

def solve():
    a, n = map(int, input().split())
    result = 1
    for _ in range(n):
        result *= a
    print(result)
