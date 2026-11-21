# Решение: Подмассив макс суммы
# Тема: Массивы/списки (одномерные)

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    max_sum = curr = arr[0]
    for x in arr[1:]:
        curr = max(x, curr + x)
        max_sum = max(max_sum, curr)
    print(max_sum)
