# Решение: Среднее значение
# Тема: Массивы/списки (одномерные)

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    print(sum(arr) / n)
