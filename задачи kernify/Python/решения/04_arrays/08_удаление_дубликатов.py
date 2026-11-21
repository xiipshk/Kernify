# Решение: Удаление дубликатов
# Тема: Массивы/списки (одномерные)

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    seen = set()
    result = []
    for x in arr:
        if x not in seen:
            seen.add(x)
            result.append(x)
    print(' '.join(map(str, result)))
