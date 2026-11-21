# Решение: Тип треугольника
# Тема: Условные операторы (if, else, elif)

def solve():
    a, b, c = map(int, input().split())
    if a == b == c:
        print("equilateral")
    elif a == b or b == c or a == c:
        print("isosceles")
    else:
        print("scalene")
