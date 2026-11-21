# Решение: Знак произведения
# Тема: Условные операторы (if, else, elif)

def solve():
    a, b = map(int, input().split())
    if a == 0 or b == 0:
        print("zero")
    elif (a > 0) == (b > 0):
        print("positive")
    else:
        print("negative")
