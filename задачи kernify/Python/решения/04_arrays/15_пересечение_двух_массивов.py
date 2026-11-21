# Решение: Пересечение двух массивов
# Тема: Массивы/списки (одномерные)

def solve():
    n = int(input())
    a = set(map(int, input().split()))
    m = int(input())
    b = set(map(int, input().split()))
    inter = sorted(a & b)
    print(' '.join(map(str, inter)))
