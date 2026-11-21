# Решение: Слияние двух отсортированных
# Тема: Массивы/списки (одномерные)

def solve():
    n = int(input())
    a = list(map(int, input().split()))
    m = int(input())
    b = list(map(int, input().split()))
    i = j = 0
    result = []
    while i < n and j < m:
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:]); result.extend(b[j:])
    print(' '.join(map(str, result)))
