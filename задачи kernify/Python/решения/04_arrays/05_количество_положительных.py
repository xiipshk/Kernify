# Решение: Количество положительных
# Тема: Массивы/списки (одномерные)

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    print(sum(1 for x in arr if x > 0))
