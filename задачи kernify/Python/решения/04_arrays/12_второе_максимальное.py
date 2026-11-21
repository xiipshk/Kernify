# Решение: Второе максимальное
# Тема: Массивы/списки (одномерные)

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    first = second = -10**9
    for x in arr:
        if x > first:
            second = first
            first = x
        elif x > second and x != first:
            second = x
    print(second)
