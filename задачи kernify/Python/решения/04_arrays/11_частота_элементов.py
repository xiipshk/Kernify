# Решение: Частота элементов
# Тема: Массивы/списки (одномерные)

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    from collections import Counter
    cnt = Counter(arr)
    for val, freq in sorted(cnt.items()):
        print(val, freq)
