# Решение: Реверс массива
# Тема: Массивы/списки (одномерные)

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    print(' '.join(map(str, reversed(arr))))
