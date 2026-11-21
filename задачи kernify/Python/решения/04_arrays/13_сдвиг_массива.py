# Решение: Сдвиг массива
# Тема: Массивы/списки (одномерные)

def solve():
    n, k = map(int, input().split())
    arr = list(map(int, input().split()))
    k %= n
    result = arr[-k:] + arr[:-k]
    print(' '.join(map(str, result)))
