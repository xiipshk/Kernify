# Решение: Квадратное уравнение
# Тема: Условные операторы (if, else, elif)

def solve():
    import math
    a, b, c = map(float, input().split())
    d = b*b - 4*a*c
    if d < 0:
        print("No roots")
    elif d == 0:
        x = -b / (2*a)
        print(f"{x:.6f}")
    else:
        x1 = (-b - math.sqrt(d)) / (2*a)
        x2 = (-b + math.sqrt(d)) / (2*a)
        print(f"{x1:.6f} {x2:.6f}")
