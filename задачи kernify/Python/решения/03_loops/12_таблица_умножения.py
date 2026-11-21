# Решение: Таблица умножения
# Тема: Циклы (for, while)

def solve():
    n = int(input())
    for i in range(1, n + 1):
        row = [str(i * j) for j in range(1, n + 1)]
        print(' '.join(row))
